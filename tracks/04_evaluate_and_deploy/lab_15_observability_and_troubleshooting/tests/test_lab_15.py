"""Tests for Lab 15 — Observability, Loop Guardrails & HIPAA-Safe Telemetry."""

from __future__ import annotations

import importlib
import os
import sys

import pytest
from google.adk.telemetry import ContentCapturingMode

from common.models import MODEL_CATALOG

LAB_DIR = os.path.dirname(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(LAB_DIR, "../../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

agent = importlib.import_module(
    "tracks.04_evaluate_and_deploy.lab_15_observability_and_troubleshooting.agent"
)
lab = importlib.import_module(
    "tracks.04_evaluate_and_deploy.lab_15_observability_and_troubleshooting.lab"
)


def test_uses_only_verified_models() -> None:
    assert agent.root_agent.model in MODEL_CATALOG


def test_agent_tools_exist() -> None:
    assert len(agent.root_agent.tools) > 0
    assert agent.root_agent.tools[0].__name__ == "mock_flaky_tool"


def test_mock_tool_fails() -> None:
    with pytest.raises(ValueError, match="Simulated tool failure"):
        agent.mock_flaky_tool("make it fail")


def test_trace_bottleneck_diagnosis_distinguishes_tool_llm_and_loops() -> None:
    loop_spans = [
        lab.TraceSpanSample("trace_call_llm", 300, "OK"),
        lab.TraceSpanSample("trace_tool_call", 120, "ERROR"),
        lab.TraceSpanSample("trace_call_llm", 310, "OK"),
        lab.TraceSpanSample("trace_tool_call", 130, "ERROR"),
        lab.TraceSpanSample("trace_call_llm", 320, "OK"),
        lab.TraceSpanSample("trace_tool_call", 110, "ERROR"),
    ]
    kind_loop, _ = lab.diagnose_trace_bottleneck(loop_spans)
    assert kind_loop == "agent_reasoning_loop"

    tool_spans = [
        lab.TraceSpanSample("trace_call_llm", 400, "OK"),
        lab.TraceSpanSample("trace_tool_call", 5200, "OK"),
    ]
    kind_tool, _ = lab.diagnose_trace_bottleneck(tool_spans)
    assert kind_tool == "tool_invocation_latency"

    llm_spans = [
        lab.TraceSpanSample("trace_call_llm", 6100, "OK", input_tokens=300_000),
        lab.TraceSpanSample("trace_merged_tool_calls", 250, "OK"),
    ]
    kind_llm, _ = lab.diagnose_trace_bottleneck(llm_spans)
    assert kind_llm == "llm_generation_latency"


def test_hipaa_telemetry_no_content_and_loop_guardrails() -> None:
    hipaa_cfg, retry_plugin, bounded_loop = lab.build_hipaa_production_run_config(
        hipaa_regulated=True,
        max_llm_calls=6,
    )
    assert hipaa_cfg.max_llm_calls == 6
    assert hipaa_cfg.telemetry is not None
    assert hipaa_cfg.telemetry.capture_message_content == ContentCapturingMode.NO_CONTENT
    assert retry_plugin.max_retries == 2
    assert retry_plugin.throw_exception_if_retry_exceeded is True
    assert bounded_loop.max_iterations == 3

    dev_cfg, _, _ = lab.build_hipaa_production_run_config(hipaa_regulated=False)
    assert dev_cfg.telemetry is not None
    assert dev_cfg.telemetry.capture_message_content == ContentCapturingMode.SPAN_AND_EVENT


def test_observability_least_privilege_iam_auditor() -> None:
    ok, issues = lab.audit_observability_iam_roles(
        {
            "roles/cloudtrace.agent",
            "roles/logging.logWriter",
            "roles/monitoring.metricWriter",
        }
    )
    assert ok is True
    assert issues == []

    bad_ok, bad_issues = lab.audit_observability_iam_roles(
        {"roles/editor", "roles/cloudtrace.agent"}
    )
    assert bad_ok is False
    assert any("OVERPRIVILEGED_ROLES" in i for i in bad_issues)
    assert any("MISSING_TELEMETRY_ROLES" in i for i in bad_issues)
