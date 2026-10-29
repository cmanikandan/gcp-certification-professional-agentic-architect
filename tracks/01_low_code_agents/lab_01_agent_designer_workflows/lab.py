#!/usr/bin/env python3
"""Lab 01: Agent Designer Workflows — Prompt Templates, HIPAA Triage & IAM."""

from __future__ import annotations

import asyncio
import sys
from textwrap import dedent

from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from common import load_config, require_live
from common.labkit import (
    LabReport,
    banner,
    detail,
    exam_note,
    kv_table,
    section,
    step,
    table,
)
from common.models import (
    DEFAULT_AGENT_MODEL,
    DEFAULT_FAST_MODEL,
    DEFAULT_REASONING_MODEL,
    estimate_cost_ratio,
)

# ---------------------------------------------------------------------------
# In-Console Prompt Templates (Healthcare & Customer Support Triage)
# ---------------------------------------------------------------------------

ZERO_SHOT_PROMPT = """\
You are a patient and billing support triage assistant for Meridian Health.
Rules:
1. NEVER fabricate clinical lab results or diagnose symptoms.
2. NEVER echo raw Protected Health Information (PHI) such as SSNs or MRNs; replace them with [REDACTED-PHI].
3. Classify the inquiry urgency as ROUTINE, PRIORITY, or URGENT_CLINICAL.
"""

FEW_SHOT_PROMPT = """\
You are a healthcare and billing ticket router for Meridian Health.
Classify each message into exactly one QUEUE and flag whether PHI is present.

Allowed QUEUE values:
- HIPAA_CLINICAL_ESCALATION (lab results, symptoms, prescriptions, clinical records)
- BILLING_REFUND_REVIEW (co-pay disputes, duplicate charges, invoice refunds)
- STANDARD_FACILITY_FAQ (clinic hours, parking, general insurance accepted)

Examples:
Inquiry: What time does the downtown clinic open on Saturdays?
QUEUE: STANDARD_FACILITY_FAQ
PHI_DETECTED: NO

Inquiry: I was charged twice ($85 each) on invoice INV-9042 for my visit.
QUEUE: BILLING_REFUND_REVIEW
PHI_DETECTED: NO

Inquiry: My MRN is 449-88-1020 and I need my blood panel results from Tuesday, plus I was billed $40 extra.
QUEUE: HIPAA_CLINICAL_ESCALATION
PHI_DETECTED: YES
"""

CHAIN_OF_THOUGHT_PROMPT = """\
You are a compliance-aware customer support policy evaluator for Meridian Health.
Evaluate refund and records requests against these mandatory policies:
- Policy A (HIPAA Gate): Any clinical record or lab status request requires verified_hipaa_consent=true BEFORE disclosure.
- Policy B (Refund Ceiling): Duplicate billing refunds <= $250 may be auto-approved if invoice_verified=true; refunds > $250 require SUPERVISOR_ESCALATION.

Before outputting the final decision, think step-by-step:
1. Check whether the inquiry requests clinical/PHI data and verify verified_hipaa_consent.
2. Identify any requested refund dollar amount and compare it against the $250 ceiling.
3. Determine whether Sensitive Data Protection (SDP) redaction is required before logging.
4. Emit the final ACTION.

Format:
Reasoning: <step-by-step policy evaluation>
ACTION: <AUTO_APPROVE_REFUND | REQUIRE_HIPAA_CONSENT | SUPERVISOR_ESCALATION | ANSWER_FAQ>
"""

TEST_INQUIRY = (
    "Hi, my MRN is 771-20-9941. I was double-charged $310 on my radiology "
    "bill and I also want to see my MRI report right now. verified_hipaa_consent=false"
)

# ---------------------------------------------------------------------------
# Architectural Decision & IAM Helpers (Tested Deterministically Offline)
# ---------------------------------------------------------------------------

LEAST_PRIVILEGE_IAM_MAP: dict[str, tuple[str, str, str]] = {
    "cx_runtime_caller": (
        "roles/dialogflow.client",
        "roles/dialogflow.admin",
        "Grants detectIntent session execution only; cannot modify or delete flows.",
    ),
    "cx_flow_author": (
        "roles/dialogflow.flowEditor",
        "roles/owner",
        "Allows console editing of Pages, Transition Routes, and Playbooks without project IAM control.",
    ),
    "vertex_model_invoker": (
        "roles/aiplatform.user",
        "roles/aiplatform.admin",
        "Allows agent service account to invoke Vertex AI prediction/generation endpoints.",
    ),
    "agent_search_reader": (
        "roles/discoveryengine.viewer",
        "roles/discoveryengine.admin",
        "Grants read-only search queries against Agent Search datastores.",
    ),
    "phi_redaction_caller": (
        "roles/dlp.user",
        "roles/dlp.admin",
        "Allows Sensitive Data Protection inspect/de-identify API calls before persistence.",
    ),
}


def select_authoring_surface(
    *,
    needs_regulated_state_machine: bool = False,
    needs_custom_python_or_cicd: bool = False,
) -> dict[str, str]:
    """Select between Agent Designer, CX Agent Studio (GECX), and Code-First ADK."""
    if needs_custom_python_or_cicd:
        return {
            "surface": "ADK (Code-First)",
            "rationale": (
                "Custom cyclic graph nodes, gVisor/GKE sandboxes, and GitOps CI/CD "
                "require code-first orchestration in google-adk."
            ),
        }
    if needs_regulated_state_machine:
        return {
            "surface": "CX Agent Studio",
            "rationale": (
                "Regulated customer/patient journeys require deterministic Pages, "
                "Form Parameters, Transition Routes, and Event Handlers paired with Playbooks."
            ),
        }
    return {
        "surface": "Agent Designer",
        "rationale": (
            "Internal employee assistants grounded in enterprise search are fastest "
            "to prototype and maintain via low-code Agent Designer templates."
        ),
    }


def evaluate_prompt_strategy(
    *,
    task_complexity: str,
    strict_sub_250ms_latency: bool = False,
) -> dict[str, object]:
    """Return the recommended prompt template strategy and verified model tier."""
    if strict_sub_250ms_latency:
        return {
            "strategy": "few_shot",
            "model": DEFAULT_FAST_MODEL,
            "increases_output_latency": False,
            "cost_ratio": estimate_cost_ratio(DEFAULT_FAST_MODEL),
            "reason": (
                "Strict latency budgets forbid Chain-of-Thought output token generation; "
                "use Few-Shot examples on the Lite model tier."
            ),
        }
    if task_complexity == "multi_policy_compliance_math":
        return {
            "strategy": "chain_of_thought",
            "model": DEFAULT_REASONING_MODEL,
            "increases_output_latency": True,
            "cost_ratio": estimate_cost_ratio(DEFAULT_REASONING_MODEL),
            "reason": (
                "Multi-step SLA math and HIPAA/refund policy checks require intermediate "
                "reasoning steps, accepting higher output tokens and latency."
            ),
        }
    if task_complexity == "custom_taxonomy_routing":
        return {
            "strategy": "few_shot",
            "model": DEFAULT_AGENT_MODEL,
            "increases_output_latency": False,
            "cost_ratio": estimate_cost_ratio(DEFAULT_AGENT_MODEL),
            "reason": (
                "Concrete input/output examples anchor custom enterprise queue names "
                "and edge-case precedence rules."
            ),
        }
    return {
        "strategy": "zero_shot",
        "model": DEFAULT_FAST_MODEL,
        "increases_output_latency": False,
        "cost_ratio": estimate_cost_ratio(DEFAULT_FAST_MODEL),
        "reason": "Simple unambiguous tasks succeed with direct system instructions.",
    }


def recommend_least_privilege_iam(actor_key: str) -> dict[str, str]:
    """Return least-privilege IAM role vs over-privileged exam distractor."""
    role, distractor, why = LEAST_PRIVILEGE_IAM_MAP[actor_key]
    return {
        "actor": actor_key,
        "recommended_role": role,
        "overprivileged_trap": distractor,
        "rationale": why,
    }


async def run_offline() -> LabReport:
    """Offline deterministic execution path."""
    banner(
        "Lab 01: Agent Designer Workflows",
        "System Instructions, HIPAA/Support Prompt Templates & Least-Privilege IAM",
    )

    section("1. Low-Code Prompt Template Configurations")
    agent_zero = Agent(
        name="ZeroShotSupportAgent",
        model=DEFAULT_FAST_MODEL,
        instruction=ZERO_SHOT_PROMPT,
    )
    step("1", f"Configured {agent_zero.name} ({agent_zero.model})")
    detail("Enforces persona and [REDACTED-PHI] boundary with minimal token overhead.")

    agent_few = Agent(
        name="FewShotTriageAgent",
        model=DEFAULT_AGENT_MODEL,
        instruction=FEW_SHOT_PROMPT,
    )
    step("2", f"Configured {agent_few.name} ({agent_few.model})")
    detail("Uses concrete Examples: to map multi-intent clinical + billing messages consistently.")

    agent_cot = Agent(
        name="ChainOfThoughtPolicyAgent",
        model=DEFAULT_REASONING_MODEL,
        instruction=CHAIN_OF_THOUGHT_PROMPT,
    )
    step("3", f"Configured {agent_cot.name} ({agent_cot.model})")
    detail("Forces step-by-step evaluation of HIPAA consent gates and $250 refund ceilings.")

    kv_table(
        {
            "Zero-Shot chars": len(agent_zero.instruction),
            "Few-Shot chars": len(agent_few.instruction),
            "Chain-of-Thought chars": len(agent_cot.instruction),
        }
    )

    section("2. Authoring Surface & Latency Trade-Off Matrix")
    hipaa_surface = select_authoring_surface(needs_regulated_state_machine=True)
    internal_surface = select_authoring_surface()
    cicd_surface = select_authoring_surface(needs_custom_python_or_cicd=True)

    fast_choice = evaluate_prompt_strategy(
        task_complexity="custom_taxonomy_routing",
        strict_sub_250ms_latency=True,
    )
    cot_choice = evaluate_prompt_strategy(
        task_complexity="multi_policy_compliance_math",
        strict_sub_250ms_latency=False,
    )

    table(
        ["Scenario", "Selected Surface / Strategy", "Model / Note"],
        [
            ["Internal HR/IT Search Bot", internal_surface["surface"], "No-code console speed"],
            ["HIPAA / Refund Customer CX", hipaa_surface["surface"], "Deterministic Pages + Playbooks"],
            ["Cyclic Graph + GitOps CI/CD", cicd_surface["surface"], "Full Python ADK control"],
            ["Sub-250ms Ticket Classifier", str(fast_choice["strategy"]), str(fast_choice["model"])],
            ["Multi-Rule SLA & HIPAA Policy", str(cot_choice["strategy"]), str(cot_choice["model"])],
        ],
    )
    exam_note("CoT improves multi-step accuracy but INCREASES output latency and token cost.")

    section("3. Least-Privilege IAM Audit (~30-35% of Exam)")
    iam_rows = []
    for key in LEAST_PRIVILEGE_IAM_MAP:
        rec = recommend_least_privilege_iam(key)
        iam_rows.append(
            [rec["actor"], rec["recommended_role"], f"Avoid {rec['overprivileged_trap']}"]
        )
    table(["Workload Principal", "Minimum Role", "Exam Trap"], iam_rows)

    report = LabReport("Lab 01 — Agent Designer & Prompt Templates")
    report.check(
        "Zero-shot enforces PHI guardrail boundary",
        "[REDACTED-PHI]" in agent_zero.instruction,
    )
    report.check(
        "Few-shot template embeds canonical Examples:",
        "Examples:" in agent_few.instruction
        and "HIPAA_CLINICAL_ESCALATION" in agent_few.instruction,
    )
    report.check(
        "Chain-of-thought template enforces step-by-step policy checks",
        "step-by-step" in agent_cot.instruction and "$250" in agent_cot.instruction,
    )
    report.check(
        "Latency-critical routing avoids Chain-of-Thought",
        fast_choice["strategy"] == "few_shot"
        and fast_choice["increases_output_latency"] is False,
    )
    report.check(
        "Regulated customer CX selects CX Agent Studio over plain Agent Designer",
        hipaa_surface["surface"] == "CX Agent Studio",
    )
    report.check(
        "Runtime CX caller uses least-privilege roles/dialogflow.client",
        recommend_least_privilege_iam("cx_runtime_caller")["recommended_role"]
        == "roles/dialogflow.client",
    )
    report.summary()
    return report


async def run_live(config) -> None:
    """Opt-in live execution path using ADK InMemoryRunner."""
    banner("Lab 01: Agent Designer Workflows (LIVE)", f"Project: {config.project_id}")

    for label, prompt in [
        ("ZeroShotSupport", ZERO_SHOT_PROMPT),
        ("FewShotTriage", FEW_SHOT_PROMPT),
        ("ChainOfThoughtPolicy", CHAIN_OF_THOUGHT_PROMPT),
    ]:
        section(f"Live Run — {label}")
        agent = Agent(name=label, model=DEFAULT_AGENT_MODEL, instruction=prompt)
        runner = InMemoryRunner(agent=agent, app_name="lab01_live")
        session = await runner.session_service.create_session(
            app_name="lab01_live", user_id="exam_student"
        )
        step("Input", TEST_INQUIRY)
        chunks: list[str] = []
        async for event in runner.run_async(
            user_id="exam_student",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part.from_text(text=TEST_INQUIRY)]
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        chunks.append(part.text)
        step("Output", "\n" + dedent("".join(chunks)).strip())


def main() -> None:
    config = load_config(sys.argv[1:])
    if require_live(config):
        asyncio.run(run_live(config))
    else:
        asyncio.run(run_offline())


if __name__ == "__main__":
    main()
