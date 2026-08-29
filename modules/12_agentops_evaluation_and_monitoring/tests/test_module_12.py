"""
Unit Tests for Module 12: AgentOps Evaluation & Observability
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from agent_evaluator import (
    AgentOpsEvaluator,
    SAMPLE_GOLDEN_DATASET,
    mock_agent_runner,
    CloudTraceSimulator
)

def test_cloud_trace_simulator():
    tracer = CloudTraceSimulator("trace_123")
    tracer.log_span("LLM_Inference", 150.0, {"tokens": 400})
    assert len(tracer.spans) == 1
    assert tracer.spans[0]["span_name"] == "LLM_Inference"
    assert tracer.spans[0]["duration_ms"] == 150.0

def test_evalset_golden_evaluation():
    evaluator = AgentOpsEvaluator()
    scorecard = evaluator.evaluate_test_suite(SAMPLE_GOLDEN_DATASET, mock_agent_runner)

    assert scorecard.total_tests == 2
    assert scorecard.tool_accuracy_pct == 100.0
    assert scorecard.argument_precision_pct == 100.0
    assert scorecard.faithfulness_score == 1.0
    assert scorecard.average_latency_ms >= 0.0
