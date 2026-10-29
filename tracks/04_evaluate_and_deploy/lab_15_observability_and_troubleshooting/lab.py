#!/usr/bin/env python3
"""Lab 15 — Observability, Loop Guardrails & HIPAA-Safe Telemetry.

Demonstrates:
1. OpenTelemetry span attribution in ADK 2.9.0 (``trace_call_llm``,
   ``trace_tool_call``, ``trace_merged_tool_calls``) to distinguish slow backend
   tool APIs from slow LLM generation or infinite reasoning loops.
2. Three layered loop-prevention controls:
   - ``RunConfig(max_llm_calls=...)`` hard invocation ceiling
   - ``LoopAgent(..., max_iterations=...)`` bounded workflow iterations
   - ``ReflectAndRetryToolPlugin(max_retries=...)`` bounded tool self-correction
3. HIPAA / Regulated PII protection in production logs & traces via
   ``TelemetryConfig(capture_message_content=ContentCapturingMode.NO_CONTENT)``.
4. Continuous optimization & regression tooling (``adk optimize`` GEPA prompt
   optimizer + ``adk conformance record/test``) and least-privilege telemetry IAM
   (``roles/cloudtrace.agent``, ``roles/logging.logWriter``, ``roles/monitoring.metricWriter``).
"""

from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from google.adk.agents import LoopAgent, RunConfig
from google.adk.optimization import gepa_root_agent_prompt_optimizer
from google.adk.plugins import ReflectAndRetryToolPlugin
from google.adk.telemetry import (
    ContentCapturingMode,
    TelemetryConfig,
    trace_call_llm,
    trace_merged_tool_calls,
    trace_send_data,
    trace_tool_call,
)

import importlib.util
from common import (
    LabReport,
    banner,
    exam_note,
    kv_table,
    load_config,
    require_live,
    section,
    step,
)
from common.labkit import detail, table

_AGENT_PATH = Path(__file__).resolve().parent / "agent.py"
_agent_spec = importlib.util.spec_from_file_location("lab15_agent", _AGENT_PATH)
assert _agent_spec and _agent_spec.loader
agent = importlib.util.module_from_spec(_agent_spec)
_agent_spec.loader.exec_module(agent)

REQUIRED_OBSERVABILITY_ROLES: frozenset[str] = frozenset(
    {
        "roles/cloudtrace.agent",
        "roles/logging.logWriter",
        "roles/monitoring.metricWriter",
    }
)

FORBIDDEN_OVERPRIVILEGED_ROLES: frozenset[str] = frozenset(
    {
        "roles/owner",
        "roles/editor",
        "roles/logging.admin",
        "roles/monitoring.admin",
    }
)


@dataclass(frozen=True)
class TraceSpanSample:
    """Simplified OpenTelemetry span summary for latency & loop diagnosis."""

    span_name: str  # e.g., "trace_call_llm", "trace_tool_call", "trace_merged_tool_calls"
    duration_ms: float
    status: Literal["OK", "ERROR"] = "OK"
    input_tokens: int = 0
    output_tokens: int = 0


def diagnose_trace_bottleneck(
    spans: list[TraceSpanSample],
) -> tuple[
    Literal["agent_reasoning_loop", "tool_invocation_latency", "llm_generation_latency", "healthy"],
    str,
]:
    """Classify an ADK OpenTelemetry trace into the exact exam root cause."""
    tool_error_spans = [
        s for s in spans if s.span_name in ("trace_tool_call", "trace_merged_tool_calls") and s.status == "ERROR"
    ]
    llm_spans = [s for s in spans if s.span_name == "trace_call_llm"]
    tool_spans = [s for s in spans if s.span_name in ("trace_tool_call", "trace_merged_tool_calls")]

    if len(tool_error_spans) >= 3 and len(llm_spans) >= 3:
        return (
            "agent_reasoning_loop",
            f"Detected {len(tool_error_spans)} failing tool spans alternating with "
            f"{len(llm_spans)} LLM calls. Cap with `RunConfig.max_llm_calls`, "
            "`LoopAgent.max_iterations`, and `ReflectAndRetryToolPlugin(max_retries=...)`.",
        )

    total_llm_ms = sum(s.duration_ms for s in llm_spans)
    total_tool_ms = sum(s.duration_ms for s in tool_spans)

    if total_tool_ms > 2000 and total_tool_ms > (total_llm_ms * 2.0):
        return (
            "tool_invocation_latency",
            f"Tool execution consumed {total_tool_ms:.0f}ms vs {total_llm_ms:.0f}ms in LLM calls. "
            "Optimize downstream API timeouts, cache lookups, or batch independent calls into "
            "`trace_merged_tool_calls`.",
        )

    if total_llm_ms > 2000 and total_llm_ms >= (total_tool_ms * 2.0):
        return (
            "llm_generation_latency",
            f"LLM generation consumed {total_llm_ms:.0f}ms vs {total_tool_ms:.0f}ms in tools. "
            "Enable `events_compaction_config` / `context_cache_config`, or route simple steps "
            "to the Flash-Lite tier.",
        )

    return "healthy", "Turn latency is within normal operating bounds."


def build_hipaa_production_run_config(
    *,
    hipaa_regulated: bool = True,
    max_llm_calls: int = 8,
) -> tuple[RunConfig, ReflectAndRetryToolPlugin, LoopAgent]:
    """Build HIPAA-safe telemetry + loop-bounded RunConfig, Plugin, and LoopAgent."""
    capture_mode = (
        ContentCapturingMode.NO_CONTENT
        if hipaa_regulated
        else ContentCapturingMode.SPAN_AND_EVENT
    )
    telemetry_cfg = TelemetryConfig(capture_message_content=capture_mode)
    run_cfg = RunConfig(
        max_llm_calls=max_llm_calls,
        telemetry=telemetry_cfg,
    )
    retry_plugin = ReflectAndRetryToolPlugin(
        max_retries=2,
        throw_exception_if_retry_exceeded=True,
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        bounded_loop = LoopAgent(
            name="bounded_verification_loop",
            max_iterations=3,
            sub_agents=[],
        )
    return run_cfg, retry_plugin, bounded_loop


def audit_observability_iam_roles(granted_roles: set[str]) -> tuple[bool, list[str]]:
    """Verify least-privilege telemetry IAM roles for Cloud Trace, Logging, and Monitoring."""
    issues: list[str] = []
    overprivileged = sorted(granted_roles & FORBIDDEN_OVERPRIVILEGED_ROLES)
    if overprivileged:
        issues.append(
            f"OVERPRIVILEGED_ROLES: Remove {overprivileged}; never grant basic/admin roles for telemetry."
        )
    missing = sorted(REQUIRED_OBSERVABILITY_ROLES - granted_roles)
    if missing:
        issues.append(f"MISSING_TELEMETRY_ROLES: Grant {missing} on the runtime service account.")
    return (len(issues) == 0), issues


def run_offline() -> LabReport:
    report = LabReport(
        title="Lab 15 — Observability, Loop Guardrails & HIPAA-Safe Telemetry"
    )
    banner(
        "Lab 15 — Observability & Troubleshooting (Offline)",
        "Span Attribution · Reasoning Loop Caps · HIPAA Zero-Content Telemetry · GEPA",
    )

    section("1. Diagnosing Tool Latency vs. LLM Latency vs. Reasoning Loops")
    verified_tracers = [
        fn.__name__
        for fn in (
            trace_call_llm,
            trace_tool_call,
            trace_merged_tool_calls,
            trace_send_data,
        )
    ]
    step(1, f"Verified ADK OpenTelemetry span emitters: {', '.join(verified_tracers)}")

    try:
        agent.mock_flaky_tool("make it fail")
        flaky_failed = False
    except ValueError:
        flaky_failed = True

    loop_trace = [
        TraceSpanSample("trace_call_llm", 420, "OK", 300, 45),
        TraceSpanSample("trace_tool_call", 180, "ERROR"),
        TraceSpanSample("trace_call_llm", 450, "OK", 420, 40),
        TraceSpanSample("trace_tool_call", 190, "ERROR"),
        TraceSpanSample("trace_call_llm", 480, "OK", 540, 42),
        TraceSpanSample("trace_tool_call", 175, "ERROR"),
    ]
    slow_tool_trace = [
        TraceSpanSample("trace_call_llm", 550, "OK", 250, 35),
        TraceSpanSample("trace_tool_call", 6400, "OK"),
        TraceSpanSample("trace_call_llm", 510, "OK", 480, 90),
    ]
    slow_llm_trace = [
        TraceSpanSample("trace_call_llm", 5800, "OK", 280_000, 1200),
        TraceSpanSample("trace_merged_tool_calls", 320, "OK"),
    ]

    diag_loop, note_loop = diagnose_trace_bottleneck(loop_trace)
    diag_tool, note_tool = diagnose_trace_bottleneck(slow_tool_trace)
    diag_llm, note_llm = diagnose_trace_bottleneck(slow_llm_trace)

    table(
        ["Scenario", "Diagnosed Root Cause", "Architectural Remediation"],
        [
            ["3x Failing Tool Retries", diag_loop, note_loop[:68] + "..."],
            ["6.4s External API Span", diag_tool, note_tool[:68] + "..."],
            ["280k Token Context Span", diag_llm, note_llm[:68] + "..."],
        ],
    )
    report.check(
        "Flaky tool simulated and trace bottleneck classifier separates all 3 failure modes",
        flaky_failed
        and diag_loop == "agent_reasoning_loop"
        and diag_tool == "tool_invocation_latency"
        and diag_llm == "llm_generation_latency",
    )

    section("2. Loop Guardrails & HIPAA Zero-PHI Telemetry Configuration")
    hipaa_run_cfg, retry_plugin, loop_agent = build_hipaa_production_run_config(
        hipaa_regulated=True,
        max_llm_calls=8,
    )
    kv_table(
        {
            "RunConfig.max_llm_calls": str(hipaa_run_cfg.max_llm_calls),
            "LoopAgent.max_iterations": str(loop_agent.max_iterations),
            "ReflectAndRetryToolPlugin.max_retries": str(retry_plugin.max_retries),
            "HIPAA Telemetry Capture Mode": str(
                hipaa_run_cfg.telemetry.capture_message_content  # type: ignore[union-attr]
            ),
            "GEPA Prompt Optimizer Module": gepa_root_agent_prompt_optimizer.__name__.split(".")[-1],
        }
    )
    report.check(
        "HIPAA RunConfig disables raw prompt/PHI capture (ContentCapturingMode.NO_CONTENT)",
        hipaa_run_cfg.telemetry is not None
        and hipaa_run_cfg.telemetry.capture_message_content == ContentCapturingMode.NO_CONTENT
        and hipaa_run_cfg.max_llm_calls == 8
        and loop_agent.max_iterations == 3
        and retry_plugin.max_retries == 2,
    )

    section("3. Least-Privilege Observability IAM Audit & Conformance CLI")
    least_priv_ok, issues = audit_observability_iam_roles(set(REQUIRED_OBSERVABILITY_ROLES))
    bad_priv_ok, _ = audit_observability_iam_roles({"roles/editor", "roles/cloudtrace.agent"})
    detail("adk optimize . --eval_set_path=.evalset.json  # GEPA instruction optimization")
    detail("adk conformance record tests/core && adk conformance test --mode=replay tests/core")
    report.check(
        "Observability IAM auditor enforces trace/log/metric writer roles and blocks roles/editor",
        least_priv_ok is True and issues == [] and bad_priv_ok is False,
    )

    exam_note(
        "In HIPAA / regulated workloads, enable OpenTelemetry structure (`--otel_to_cloud` + "
        "`roles/cloudtrace.agent`, `roles/logging.logWriter`, `roles/monitoring.metricWriter`) "
        "while setting `ContentCapturingMode.NO_CONTENT` so span latencies and loop counts are "
        "captured WITHOUT leaking raw PHI prompts or tool outputs into Cloud Logging."
    )
    report.summary()
    return report


def run_live(config) -> LabReport:
    banner("Lab 15 — Observability & Troubleshooting (Live Mode)")
    step(1, f"Project: {config.project_id} | Location: {config.location}")
    detail("Run `adk telemetry status` or deploy with `--otel_to_cloud` to inspect live spans.")
    return run_offline()


if __name__ == "__main__":
    cfg = load_config()
    if cfg.live and require_live(cfg):
        run_live(cfg)
    else:
        run_offline()
