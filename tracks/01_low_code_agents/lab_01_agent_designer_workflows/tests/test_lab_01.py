"""Offline deterministic tests for Lab 01 (Agent Designer Workflows)."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys

from common.models import MODEL_CATALOG

LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_SPEC = importlib.util.spec_from_file_location("track01_lab01", LAB_PATH)
assert _SPEC and _SPEC.loader
lab = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = lab
_SPEC.loader.exec_module(lab)


def test_uses_only_verified_models() -> None:
    """Every model constant imported by Lab 01 must exist in MODEL_CATALOG."""
    assert lab.DEFAULT_AGENT_MODEL in MODEL_CATALOG
    assert lab.DEFAULT_FAST_MODEL in MODEL_CATALOG
    assert lab.DEFAULT_REASONING_MODEL in MODEL_CATALOG


def test_prompt_templates_include_hipaa_and_structural_markers() -> None:
    """Verify Zero-Shot, Few-Shot, and CoT structural & compliance markers."""
    assert "[REDACTED-PHI]" in lab.ZERO_SHOT_PROMPT
    assert "Examples:" in lab.FEW_SHOT_PROMPT
    assert "HIPAA_CLINICAL_ESCALATION" in lab.FEW_SHOT_PROMPT
    assert "BILLING_REFUND_REVIEW" in lab.FEW_SHOT_PROMPT
    assert "step-by-step" in lab.CHAIN_OF_THOUGHT_PROMPT
    assert "verified_hipaa_consent" in lab.CHAIN_OF_THOUGHT_PROMPT


def test_authoring_surface_decision_matrix() -> None:
    """Verify low-code vs GECX state-machine vs code-first ADK selection."""
    assert lab.select_authoring_surface()["surface"] == "Agent Designer"
    assert (
        lab.select_authoring_surface(needs_regulated_state_machine=True)["surface"]
        == "CX Agent Studio"
    )
    assert (
        lab.select_authoring_surface(
            needs_regulated_state_machine=True,
            needs_custom_python_or_cicd=True,
        )["surface"]
        == "ADK (Code-First)"
    )


def test_cot_vs_latency_budget_tradeoff() -> None:
    """Strict latency budgets must avoid CoT; multi-policy compliance uses CoT."""
    low_latency = lab.evaluate_prompt_strategy(
        task_complexity="multi_policy_compliance_math",
        strict_sub_250ms_latency=True,
    )
    assert low_latency["strategy"] == "few_shot"
    assert low_latency["increases_output_latency"] is False

    deep_policy = lab.evaluate_prompt_strategy(
        task_complexity="multi_policy_compliance_math",
        strict_sub_250ms_latency=False,
    )
    assert deep_policy["strategy"] == "chain_of_thought"
    assert deep_policy["increases_output_latency"] is True


def test_least_privilege_iam_recommendations() -> None:
    """Verify minimum IAM roles and rejection of admin/owner distractors."""
    cx_client = lab.recommend_least_privilege_iam("cx_runtime_caller")
    assert cx_client["recommended_role"] == "roles/dialogflow.client"
    assert cx_client["overprivileged_trap"] == "roles/dialogflow.admin"

    flow_editor = lab.recommend_least_privilege_iam("cx_flow_author")
    assert flow_editor["recommended_role"] == "roles/dialogflow.flowEditor"

    search_viewer = lab.recommend_least_privilege_iam("agent_search_reader")
    assert search_viewer["recommended_role"] == "roles/discoveryengine.viewer"


def test_offline_run_passes_all_checks(capsys) -> None:
    """The offline lab must complete with zero network calls and pass all checks."""
    report = asyncio.run(lab.run_offline())
    captured = capsys.readouterr()
    assert report.passed
    assert "All 6 checks passed." in captured.out
