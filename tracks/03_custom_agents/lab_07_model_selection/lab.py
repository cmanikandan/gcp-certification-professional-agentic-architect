#!/usr/bin/env python3
"""Lab 07: Model Selection & Multi-Tier Agent Routing (Objective 3.1)."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from common import (
    DEFAULT_AGENT_MODEL,
    DEFAULT_FAST_MODEL,
    DEFAULT_JUDGE_MODEL,
    DEFAULT_OSS_MODEL,
    DEFAULT_REASONING_MODEL,
    load_config,
    require_live,
)
from common.labkit import LabReport, banner, exam_note, section, step, table
from common.models import (
    DEFAULT_OSS_MOE_MODEL,
    FLOATING_ALIASES,
    MODEL_CATALOG,
    Hosting,
    Licensing,
    Tier,
    estimate_cost_ratio,
    get_profile,
    select_model,
)
from google.adk.agents import LlmAgent
from google.adk.models import (
    ApigeeLlm,
    Claude,
    FallbackModel,
    Gemini,
    Gemma,
    Gemma3Ollama,
    LiteLlm,
)


@dataclass(frozen=True)
class TieredRoutingEstimate:
    """Ordinal cost comparison between single-tier Pro and multi-tier routing."""

    all_pro_cost_units: float
    tiered_cost_units: float
    savings_pct: float


def compute_tiered_routing_savings(
    simple_fraction: float = 0.90,
    total_requests: int = 1_000,
) -> TieredRoutingEstimate:
    """Compare sending 100% of traffic to GA Pro vs Lite router + Pro escalation.

    In a tiered topology:
    - 100% of requests hit the fast Lite router/triage model.
    - ``simple_fraction`` are resolved directly by a Standard/Lite path without Pro.
    - ``(1 - simple_fraction)`` escalate to the GA Pro reasoning specialist.
    """
    if not 0.0 <= simple_fraction <= 1.0:
        raise ValueError("simple_fraction must be between 0.0 and 1.0")

    ga_pro_id, _ = select_model(needs_deep_reasoning=True, requires_ga_only=True)
    pro_weight = estimate_cost_ratio(ga_pro_id)
    lite_weight = estimate_cost_ratio(DEFAULT_FAST_MODEL)

    all_pro_units = total_requests * pro_weight
    escalated_fraction = 1.0 - simple_fraction
    tiered_units = total_requests * (lite_weight + escalated_fraction * pro_weight)
    savings_pct = ((all_pro_units - tiered_units) / all_pro_units) * 100.0
    return TieredRoutingEstimate(
        all_pro_cost_units=all_pro_units,
        tiered_cost_units=tiered_units,
        savings_pct=round(savings_pct, 2),
    )


def validate_production_model_pinning(model_id: str) -> tuple[bool, str]:
    """Reject floating aliases and unverified IDs in production configs."""
    if model_id in FLOATING_ALIASES:
        return (
            False,
            f"Floating alias {model_id!r} can shift weights silently; pin an explicit version.",
        )
    if model_id not in MODEL_CATALOG:
        return False, f"Unverified model ID {model_id!r} is not in MODEL_CATALOG."
    return True, f"Pinned verified model {model_id!r}."


def build_enterprise_model_suite() -> dict[str, object]:
    """Instantiate all ADK BaseLlm classes used across Exam Objective 3.1."""
    fast_router = Gemini(model=DEFAULT_FAST_MODEL)
    standard_specialist = Gemini(model=DEFAULT_AGENT_MODEL)
    distinct_judge = Gemini(model=DEFAULT_JUDGE_MODEL)
    dense_oss = Gemma(model=DEFAULT_OSS_MODEL)
    moe_oss = Gemma(model=DEFAULT_OSS_MOE_MODEL)
    litellm_oss = LiteLlm(model=f"vertex_ai/{DEFAULT_OSS_MODEL}")
    local_ollama = Gemma3Ollama()
    partner_claude = Claude()
    governed_apigee = ApigeeLlm(
        model=f"apigee/{DEFAULT_AGENT_MODEL}",
        proxy_url="https://apigee.corp.example/v1",
        custom_headers={"X-Cost-Center": "cc-customer-support"},
    )
    ha_fallback = FallbackModel(
        models=[standard_specialist, distinct_judge],
    )
    return {
        "fast_router": fast_router,
        "standard_specialist": standard_specialist,
        "distinct_judge": distinct_judge,
        "dense_oss": dense_oss,
        "moe_oss": moe_oss,
        "litellm_oss": litellm_oss,
        "local_ollama": local_ollama,
        "partner_claude": partner_claude,
        "governed_apigee": governed_apigee,
        "ha_fallback": ha_fallback,
    }


def run_offline() -> LabReport:
    banner(
        "Lab 07 — Model Selection & Multi-Tier Agent Routing",
        "Objective 3.1: LLM vs SLM, Self-Hosted vs SaaS, OSS vs Proprietary (Offline)",
    )
    report = LabReport("Lab 07 — Model Selection")

    section("1. Constraint-Driven Architectural Selection")
    scenarios = [
        ("Air-gapped / Sovereign VPC", dict(data_cannot_leave_premises=True)),
        ("50k RPM Ticket Triage Router", dict(high_volume_simple_task=True)),
        ("Clinical Claim Reasoning (GA-Only)", dict(needs_deep_reasoning=True, requires_ga_only=True)),
        ("Greenfield Architecture Design", dict(needs_deep_reasoning=True, requires_ga_only=False)),
        ("Balanced Tool-Calling Specialist", dict()),
    ]
    rows: list[list[object]] = []
    for label, kwargs in scenarios:
        model_id, _rationale = select_model(**kwargs)
        profile = get_profile(model_id)
        rows.append(
            [
                label,
                model_id,
                profile.tier.value,
                profile.hosting.value,
                profile.licensing.value,
                "preview" if profile.preview else "GA",
            ]
        )
    table(["Scenario", "Selected Model", "Tier", "Hosting", "Licensing", "Release"], rows)

    airgap_id, _ = select_model(data_cannot_leave_premises=True)
    ga_pro_id, _ = select_model(needs_deep_reasoning=True, requires_ga_only=True)
    report.check(
        "Air-gapped workload selects self-hosted open-weights model",
        get_profile(airgap_id).hosting is Hosting.SELF_HOSTED
        and get_profile(airgap_id).licensing is Licensing.OPEN_WEIGHTS,
        airgap_id,
    )
    report.check(
        "GA-only deep reasoning selects non-preview Pro tier",
        get_profile(ga_pro_id).tier is Tier.PRO and not get_profile(ga_pro_id).preview,
        ga_pro_id,
    )
    report.check(
        "Preview Pro reasoning model is flagged preview=True",
        get_profile(DEFAULT_REASONING_MODEL).preview is True,
        DEFAULT_REASONING_MODEL,
    )

    section("2. Dense vs MoE Open-Weights Self-Hosting (GKE / Model Garden)")
    dense_prof = get_profile(DEFAULT_OSS_MODEL)
    moe_prof = get_profile(DEFAULT_OSS_MOE_MODEL)
    step(1, f"Dense OSS: {dense_prof.model_id} (ctx={dense_prof.input_token_limit:,})")
    step(2, f"MoE OSS:   {moe_prof.model_id} (ctx={moe_prof.input_token_limit:,}, 4B active params)")
    exam_note(
        "Self-hosted Gemma models have $0 per-token API charge (cost_ratio=0.0) "
        "because you pay for dedicated GKE/Model Garden GPU node hours instead."
    )
    report.check(
        "Both Dense and MoE Gemma models are catalogued for self-hosting",
        estimate_cost_ratio(DEFAULT_OSS_MODEL) == 0.0
        and estimate_cost_ratio(DEFAULT_OSS_MOE_MODEL) == 0.0,
    )

    section("3. ADK BaseLlm Model Wrappers & High-Availability Failover")
    suite = build_enterprise_model_suite()
    fallback: FallbackModel = suite["ha_fallback"]  # type: ignore[assignment]
    apigee: ApigeeLlm = suite["governed_apigee"]  # type: ignore[assignment]

    resilient_agent = LlmAgent(
        name="ResilientSupportAgent",
        model=fallback,
        instruction="Assist customers reliably across regional quota spikes.",
    )
    step(3, f"Bound {type(fallback).__name__} to LlmAgent '{resilient_agent.name}'.")
    step(4, f"Retriable HTTP codes: {sorted(fallback.retriable_status_codes)}")
    step(5, f"Apigee governed proxy model: {apigee.model}")

    report.check(
        "All 7 ADK model wrapper classes instantiate cleanly offline",
        len(suite) == 10 and isinstance(suite["litellm_oss"], LiteLlm) and isinstance(suite["local_ollama"], Gemma3Ollama) and isinstance(suite["partner_claude"], Claude),
    )
    report.check(
        "FallbackModel fails over on 429 and 5xx status codes",
        {429, 500, 502, 503, 504}.issubset(fallback.retriable_status_codes),
    )
    report.check(
        "Judge model differs from primary agent model to avoid self-preference bias",
        DEFAULT_JUDGE_MODEL != DEFAULT_AGENT_MODEL,
        f"agent={DEFAULT_AGENT_MODEL}, judge={DEFAULT_JUDGE_MODEL}",
    )

    section("4. Multi-Tier Routing Cost Math & Production Version Pinning")
    estimate = compute_tiered_routing_savings(simple_fraction=0.90, total_requests=1_000)
    step(
        6,
        f"1,000 turns: All-Pro={estimate.all_pro_cost_units:.0f} units vs "
        f"90%-Lite/10%-Pro={estimate.tiered_cost_units:.0f} units "
        f"({estimate.savings_pct:.1f}% cost reduction).",
    )
    report.check(
        "Tiered Lite->Pro routing saves >80% ordinal token cost at 90% simple volume",
        estimate.savings_pct > 80.0,
        f"{estimate.savings_pct:.1f}% saved",
    )

    alias_ok, alias_msg = validate_production_model_pinning(FLOATING_ALIASES[0])
    pinned_ok, _ = validate_production_model_pinning(DEFAULT_AGENT_MODEL)
    report.check(
        "Production pinning audit rejects floating aliases and accepts pinned versions",
        (not alias_ok) and pinned_ok,
        alias_msg,
    )

    report.summary()
    return report


def run_live(config) -> None:
    banner("Lab 07 — Model Selection (Live)", f"Project: {config.project_id}")
    run_offline()
    section("Live Verification")
    from google import genai

    client = genai.Client(api_key=config.gemini_api_key)
    resp = client.models.generate_content(
        model=DEFAULT_FAST_MODEL,
        contents="Classify intent in one word (billing or technical): My invoice shows a duplicate charge.",
    )
    step(1, f"Live {DEFAULT_FAST_MODEL} router response: {(resp.text or '').strip()}")


if __name__ == "__main__":
    cfg = load_config(sys.argv[1:])
    if require_live(cfg):
        run_live(cfg)
    else:
        result = run_offline()
        sys.exit(0 if result.passed else 1)
