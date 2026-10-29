"""Tests for Lab 17 — Model Armor w/ SDP, Gateway Pattern & HITL Guardrails."""

from __future__ import annotations

import importlib
import os
import sys

import pytest
from google.cloud import modelarmor_v1

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from common.models import MODEL_CATALOG

lab = importlib.import_module("tracks.05_secure_and_govern.lab_17_model_armor_and_hitl.lab")


def test_uses_only_verified_models() -> None:
    assert lab.MODEL in MODEL_CATALOG


def test_has_model_armor() -> None:
    assert lab.HAS_GCP_EXTRA, "The google-adk[gcp] extra must be installed"


def test_model_armor_config_and_plugin_fail_closed() -> None:
    if not lab.HAS_GCP_EXTRA:
        pytest.skip("GCP extra not installed")

    config, plugin = lab.build_fail_closed_model_armor_plugin(
        project_id="test", location="us-central1"
    )
    assert "templates/hipaa-sdp-prompt-shield" in (config.prompt_template_name or "")
    assert config.block_on_screening_failure is True
    assert plugin.name == "hipaa_model_armor_plugin"


def test_model_armor_v1_sdp_basic_vs_sdp_advanced_templates() -> None:
    basic_cfg, adv_cfg = lab.build_sdp_basic_vs_advanced_filters(
        project_id="hipaa-proj", location="us-central1"
    )

    assert (
        basic_cfg.pi_and_jailbreak_filter_settings.filter_enforcement
        == modelarmor_v1.PiAndJailbreakFilterSettings.PiAndJailbreakFilterEnforcement.ENABLED
    )
    assert (
        basic_cfg.malicious_uri_filter_settings.filter_enforcement
        == modelarmor_v1.MaliciousUriFilterSettings.MaliciousUriFilterEnforcement.ENABLED
    )
    assert (
        basic_cfg.sdp_settings.basic_config.filter_enforcement
        == modelarmor_v1.SdpBasicConfig.SdpBasicConfigEnforcement.ENABLED
    )

    assert "inspectTemplates/hipaa-phi-inspect" in adv_cfg.sdp_settings.advanced_config.inspect_template
    assert "deidentifyTemplates/hipaa-phi-redact" in adv_cfg.sdp_settings.advanced_config.deidentify_template

    sample = "Caller MRN-998877 SSN 999-11-2222 requests refill."
    basic_allowed, _ = lab.simulate_sdp_basic_vs_advanced(sample, mode="basic_block")
    adv_allowed, sanitized = lab.simulate_sdp_basic_vs_advanced(
        sample, mode="advanced_deidentify"
    )
    assert basic_allowed is False
    assert adv_allowed is True
    assert "[REDACTED_HIPAA_MRN]" in sanitized
    assert "[REDACTED_US_SSN]" in sanitized
    assert "998877" not in sanitized


def test_gateway_vs_in_agent_plugin_and_hitl_gates() -> None:
    gw_only, _ = lab.select_model_armor_enforcement_pattern(
        governs_heterogeneous_agents_at_org_perimeter=True,
        screens_internal_mcp_tool_outputs_before_llm=False,
    )
    assert gw_only == "centralized_agent_gateway_pattern"

    both, _ = lab.select_model_armor_enforcement_pattern(
        governs_heterogeneous_agents_at_org_perimeter=True,
        screens_internal_mcp_tool_outputs_before_llm=True,
    )
    assert both == "gateway_plus_plugin_defense_in_depth"

    ok_low, _ = lab.evaluate_hitl_customer_support_gate(
        tool_name="issue_customer_refund", refund_amount_usd=25.0
    )
    assert ok_low is True

    ok_high_pending, _ = lab.evaluate_hitl_customer_support_gate(
        tool_name="issue_customer_refund", refund_amount_usd=950.0
    )
    assert ok_high_pending is False

    ok_clinical_denied, _ = lab.evaluate_hitl_customer_support_gate(
        tool_name="cancel_clinical_prescription",
        modifies_clinical_prescription=True,
        human_supervisor_decision="deny",
    )
    assert ok_clinical_denied is False
