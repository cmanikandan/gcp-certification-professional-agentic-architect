#!/usr/bin/env python3
"""Lab 17 — Model Armor with Sensitive Data Protection (SDP), Gateway Pattern & HITL.

Demonstrates the exact Beta exam guardrails:
1. Real ``google.cloud.modelarmor_v1`` template filter configuration:
   - ``FilterConfig``, ``PiAndJailbreakFilterSettings``, ``MaliciousUriFilterSettings``
   - ``SdpFilterSettings`` contrasting ``SdpBasicConfig`` (detect & block) vs.
     ``SdpAdvancedConfig(inspect_template=..., deidentify_template=...)`` (custom
     Cloud SDP HIPAA PHI redaction / masking / cryptographic tokenization BEFORE
     prompts reach the LLM or observability logs).
2. ADK ``ModelArmorPlugin`` & ``ModelArmorConfig(block_on_screening_failure=True)``
   fail-closed posture.
3. Architectural comparison: **Model Armor at the Agent Gateway (Centralized
   Perimeter Pattern)** vs. **In-Agent ``ModelArmorPlugin``** (internal tool-output
   indirect prompt injection defense).
4. Human-in-the-Loop (HITL) guardrails (``request_input``, ``get_user_choice``) for
   high-stakes customer refunds and HIPAA clinical actions.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Literal
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from google.adk import Agent
from google.adk.tools import get_user_choice, request_input
from google.cloud import modelarmor_v1

from common import (
    DEFAULT_AGENT_MODEL,
    LabReport,
    banner,
    exam_note,
    kv_table,
    load_config,
    require_live,
    section,
    step,
)
from common.labkit import table
from common.models import MODEL_CATALOG

try:
    from google.adk.integrations.model_armor import ModelArmorConfig, ModelArmorPlugin

    HAS_GCP_EXTRA = True
except ImportError:
    HAS_GCP_EXTRA = False

MODEL = DEFAULT_AGENT_MODEL

MRN_RE = re.compile(r"\bMRN-\d{5,8}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def build_sdp_basic_vs_advanced_filters(
    project_id: str = "argolis-hipaa-support",
    location: str = "us-central1",
) -> tuple[modelarmor_v1.FilterConfig, modelarmor_v1.FilterConfig]:
    """Build Model Armor FilterConfigs contrasting SdpBasicConfig vs SdpAdvancedConfig."""
    pi_jb = modelarmor_v1.PiAndJailbreakFilterSettings(
        filter_enforcement=modelarmor_v1.PiAndJailbreakFilterSettings.PiAndJailbreakFilterEnforcement.ENABLED,
        confidence_level=modelarmor_v1.DetectionConfidenceLevel.MEDIUM_AND_ABOVE,
    )
    malicious_uri = modelarmor_v1.MaliciousUriFilterSettings(
        filter_enforcement=modelarmor_v1.MaliciousUriFilterSettings.MaliciousUriFilterEnforcement.ENABLED,
    )

    basic_filter_cfg = modelarmor_v1.FilterConfig(
        pi_and_jailbreak_filter_settings=pi_jb,
        malicious_uri_filter_settings=malicious_uri,
        sdp_settings=modelarmor_v1.SdpFilterSettings(
            basic_config=modelarmor_v1.SdpBasicConfig(
                filter_enforcement=modelarmor_v1.SdpBasicConfig.SdpBasicConfigEnforcement.ENABLED,
            )
        ),
    )

    advanced_hipaa_filter_cfg = modelarmor_v1.FilterConfig(
        pi_and_jailbreak_filter_settings=pi_jb,
        malicious_uri_filter_settings=malicious_uri,
        sdp_settings=modelarmor_v1.SdpFilterSettings(
            advanced_config=modelarmor_v1.SdpAdvancedConfig(
                inspect_template=(
                    f"projects/{project_id}/locations/{location}/inspectTemplates/hipaa-phi-inspect"
                ),
                deidentify_template=(
                    f"projects/{project_id}/locations/{location}/deidentifyTemplates/hipaa-phi-redact"
                ),
            )
        ),
    )
    return basic_filter_cfg, advanced_hipaa_filter_cfg


def build_fail_closed_model_armor_plugin(
    project_id: str = "argolis-hipaa-support",
    location: str = "us-central1",
) -> tuple[ModelArmorConfig, ModelArmorPlugin]:
    """Instantiate ADK ModelArmorConfig + ModelArmorPlugin in fail-closed mode."""
    if not HAS_GCP_EXTRA:
        raise RuntimeError("google-adk[gcp] extra is required")

    config = ModelArmorConfig(
        prompt_template_name=(
            f"projects/{project_id}/locations/{location}/templates/hipaa-sdp-prompt-shield"
        ),
        response_template_name=(
            f"projects/{project_id}/locations/{location}/templates/hipaa-sdp-response-shield"
        ),
        input_blocked_message="Prompt blocked by Model Armor policy (injection or unsafe URI).",
        output_blocked_message="Response blocked by Model Armor HIPAA SDP guardrail.",
        block_on_screening_failure=True,
    )
    plugin = ModelArmorPlugin(
        config=config,
        name="hipaa_model_armor_plugin",
        client=MagicMock(),
    )
    return config, plugin


def simulate_sdp_basic_vs_advanced(
    prompt: str,
    *,
    mode: Literal["basic_block", "advanced_deidentify"],
) -> tuple[bool, str]:
    """Simulate how SdpBasicConfig blocks PHI whereas SdpAdvancedConfig redacts PHI inline."""
    has_phi = bool(MRN_RE.search(prompt) or SSN_RE.search(prompt))
    if mode == "basic_block":
        if has_phi:
            return False, "SDP_BASIC_BLOCKED: Sensitive PHI detected; entire turn rejected."
        return True, prompt

    sanitized = MRN_RE.sub("[REDACTED_HIPAA_MRN]", prompt)
    sanitized = SSN_RE.sub("[REDACTED_US_SSN]", sanitized)
    return True, sanitized


def select_model_armor_enforcement_pattern(
    *,
    governs_heterogeneous_agents_at_org_perimeter: bool = False,
    screens_internal_mcp_tool_outputs_before_llm: bool = False,
) -> tuple[
    Literal[
        "gateway_plus_plugin_defense_in_depth",
        "centralized_agent_gateway_pattern",
        "in_agent_model_armor_plugin",
    ],
    str,
]:
    """Contrast Centralized Agent Gateway Model Armor vs. In-Agent ModelArmorPlugin."""
    if governs_heterogeneous_agents_at_org_perimeter and screens_internal_mcp_tool_outputs_before_llm:
        return (
            "gateway_plus_plugin_defense_in_depth",
            "Combine Centralized Agent Gateway + Model Armor w/ SDP at the ingress/egress "
            "perimeter AND In-Agent `ModelArmorPlugin` (`after_tool_callback` / "
            "`before_model_callback`) to catch indirect prompt injections from internal tools.",
        )
    if governs_heterogeneous_agents_at_org_perimeter:
        return (
            "centralized_agent_gateway_pattern",
            "Enforce Model Armor w/ SDP at the centralized Agent Gateway so every prompt and "
            "response across polyglot agents is screened and de-identified before reaching "
            "individual agent codebases.",
        )
    return (
        "in_agent_model_armor_plugin",
        "Attach `ModelArmorPlugin` inside the ADK `App` to screen internal `after_tool_callback` "
        "results and `before_model_callback` turns.",
    )


def evaluate_hitl_customer_support_gate(
    *,
    tool_name: str,
    refund_amount_usd: float = 0.0,
    modifies_clinical_prescription: bool = False,
    human_supervisor_decision: Literal["approve", "deny"] | None = None,
) -> tuple[bool, str]:
    """Enforce HITL approval (get_user_choice / request_input) for high-risk actions."""
    requires_hitl = (
        modifies_clinical_prescription
        or tool_name in ("cancel_clinical_prescription", "delete_patient_record")
        or (tool_name == "issue_customer_refund" and refund_amount_usd > 500.0)
    )
    if not requires_hitl:
        return True, "AUTO_APPROVED: Low-risk operation within autonomous threshold."

    if human_supervisor_decision != "approve":
        choice_tool_name = getattr(get_user_choice, "name", "get_user_choice")
        input_tool_name = getattr(request_input, "name", "request_input")
        return (
            False,
            f"HITL_PAUSED_OR_DENIED: Tool `{tool_name}` requires human approval via "
            f"`{choice_tool_name}` / `{input_tool_name}`.",
        )
    return True, f"HITL_APPROVED: Human supervisor approved `{tool_name}`."


def run_offline() -> LabReport:
    """Deterministic, credential-free verification of Model Armor w/ SDP, Gateway & HITL."""
    report = LabReport(
        title="Lab 17 — Model Armor w/ SDP, Gateway Pattern & HITL Guardrails"
    )
    banner(
        "Lab 17 — Model Armor w/ SDP, Gateway Pattern & HITL (Offline)",
        "HIPAA PHI De-identification (SdpAdvancedConfig) · Fail-Closed · HITL Gates",
    )

    if not HAS_GCP_EXTRA:
        raise RuntimeError("Missing google-adk[gcp] extra.")

    section("1. Model Armor FilterConfig: SdpBasicConfig vs. SdpAdvancedConfig (HIPAA)")
    basic_cfg, adv_cfg = build_sdp_basic_vs_advanced_filters()
    ma_config, ma_plugin = build_fail_closed_model_armor_plugin()

    hipaa_prompt = (
        "Patient Jane Roe (MRN-482910, SSN 123-45-6789) asks when her insulin refill ships."
    )
    basic_ok, basic_out = simulate_sdp_basic_vs_advanced(hipaa_prompt, mode="basic_block")
    adv_ok, adv_out = simulate_sdp_basic_vs_advanced(hipaa_prompt, mode="advanced_deidentify")

    kv_table(
        {
            "Plugin Class & Name": f"{type(ma_plugin).__name__} ({ma_plugin.name})",
            "Fail-Closed (block_on_screening_failure)": str(ma_config.block_on_screening_failure),
            "SDP Basic Enforcement": str(basic_cfg.sdp_settings.basic_config.filter_enforcement),
            "SDP Advanced Inspect Template": adv_cfg.sdp_settings.advanced_config.inspect_template,
            "SDP Advanced De-ID Template": adv_cfg.sdp_settings.advanced_config.deidentify_template,
            "SDP Basic Result on HIPAA Turn": f"allowed={basic_ok} ({basic_out})",
            "SDP Advanced Result on HIPAA Turn": f"allowed={adv_ok} -> {adv_out}",
        }
    )
    report.check(
        "SdpAdvancedConfig wires inspect_template + deidentify_template and redacts MRN/SSN inline",
        basic_ok is False
        and adv_ok is True
        and "[REDACTED_HIPAA_MRN]" in adv_out
        and "[REDACTED_US_SSN]" in adv_out
        and "482910" not in adv_out,
    )

    section("2. Gateway Perimeter Pattern vs. In-Agent ModelArmorPlugin")
    pattern, rationale = select_model_armor_enforcement_pattern(
        governs_heterogeneous_agents_at_org_perimeter=True,
        screens_internal_mcp_tool_outputs_before_llm=True,
    )
    step(1, f"Selected Regulated Pattern: {pattern}")
    step(2, f"Rationale: {rationale}")
    report.check(
        "Defense-in-depth pairs Gateway Model Armor w/ SDP and In-Agent ModelArmorPlugin",
        pattern == "gateway_plus_plugin_defense_in_depth",
    )

    section("3. Human-in-the-Loop (HITL) Customer Support & Clinical Guardrails")
    small_refund_ok, _ = evaluate_hitl_customer_support_gate(
        tool_name="issue_customer_refund", refund_amount_usd=45.0
    )
    large_refund_unapproved, _ = evaluate_hitl_customer_support_gate(
        tool_name="issue_customer_refund",
        refund_amount_usd=1200.0,
        human_supervisor_decision=None,
    )
    clinical_approved, _ = evaluate_hitl_customer_support_gate(
        tool_name="cancel_clinical_prescription",
        modifies_clinical_prescription=True,
        human_supervisor_decision="approve",
    )
    support_agent = Agent(
        name="hipaa_customer_care_agent",
        model=MODEL,
        instruction="Assist patients safely using SDP-sanitized inputs and HITL approvals.",
        tools=[get_user_choice, request_input],
    )
    table(
        ["Action", "Amount / Risk", "Supervisor Decision", "Execution Permitted?"],
        [
            ["issue_customer_refund", "$45 (<= $500)", "Not required", str(small_refund_ok)],
            ["issue_customer_refund", "$1,200 (> $500)", "Pending / None", str(large_refund_unapproved)],
            ["cancel_clinical_prescription", "HIPAA Clinical", "Approved", str(clinical_approved)],
        ],
    )
    report.check(
        "HITL gate auto-allows $45 refund, pauses $1,200 refund, and verifies clinical approval",
        small_refund_ok is True
        and large_refund_unapproved is False
        and clinical_approved is True
        and len(support_agent.tools) == 2
        and MODEL in MODEL_CATALOG,
    )

    exam_note(
        "Model Armor SDP Basic vs. Advanced: `SdpBasicConfig` simply blocks detected sensitive "
        "strings (breaking legitimate healthcare support chats where patients type their MRN), "
        "whereas `SdpAdvancedConfig` attaches Cloud SDP `inspect_template` + `deidentify_template` "
        "to mask/tokenize PHI BEFORE prompts hit the LLM or logs! Enforce at the Agent Gateway "
        "for org-wide coverage AND via `ModelArmorPlugin` (`after_tool_callback`) for tool outputs."
    )
    report.summary()
    return report


def run_live(config) -> LabReport:
    """Live mode note: executes deterministic verification unless a template URI is supplied."""
    banner("Lab 17 — Model Armor w/ SDP & HITL (Live Mode)")
    step(1, f"Project: {config.project_id} | Location: {config.location}")
    return run_offline()


if __name__ == "__main__":
    cfg = load_config()
    if "--live" in sys.argv and require_live(cfg):
        run_live(cfg)
    else:
        run_offline()
