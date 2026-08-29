"""
Module 12: AgentOps: Evaluation & Observability
Demonstrates:
1. Golden Dataset Test Suite & ADK evalset Engine
2. LLM-as-a-Judge Autorater Rubrics (Tool Selection Accuracy, Argument Precision, Faithfulness)
3. Distributed Tracing Simulation (Cloud Trace Spans & Latency Profiling)
"""

import os
import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class GoldenTestCase:
    test_id: str
    user_prompt: str
    expected_tool: str
    expected_args: Dict[str, Any]
    ground_truth_fact: str

@dataclass
class EvaluationScorecard:
    total_tests: int
    tool_accuracy_pct: float
    argument_precision_pct: float
    faithfulness_score: float
    average_latency_ms: float
    detailed_results: List[Dict[str, Any]]

class CloudTraceSimulator:
    """Simulates Google Cloud Trace spans for agent perception, reasoning, and tool execution."""

    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.spans: List[Dict[str, Any]] = []

    def log_span(self, span_name: str, duration_ms: float, attributes: Optional[Dict[str, Any]] = None):
        self.spans.append({
            "trace_id": self.trace_id,
            "span_name": span_name,
            "duration_ms": duration_ms,
            "attributes": attributes or {}
        })

class AgentOpsEvaluator:
    """Automated evaluation suite using ADK evalset concepts and LLM autoraters."""

    def __init__(self, autorater_model: str = "gemini-3.7-flash"):
        self.autorater_model = os.getenv("GEMINI_MODEL", autorater_model)

    def evaluate_test_suite(self, golden_dataset: List[GoldenTestCase], agent_runner_fn) -> EvaluationScorecard:
        results = []
        correct_tools = 0
        correct_args = 0
        faithfulness_total = 0.0
        latencies = []

        for test in golden_dataset:
            tracer = CloudTraceSimulator(trace_id=f"eval_{test.test_id}")
            start = time.time()

            # Execute agent under test
            agent_output = agent_runner_fn(test.user_prompt, tracer)
            duration_ms = round((time.time() - start) * 1000, 2)
            latencies.append(duration_ms)

            # Metric 1: Tool Selection Accuracy
            actual_tool = agent_output.get("tool_called")
            tool_match = actual_tool == test.expected_tool
            if tool_match:
                correct_tools += 1

            # Metric 2: Argument Precision
            actual_args = agent_output.get("tool_args", {})
            arg_match = all(actual_args.get(k) == v for k, v in test.expected_args.items())
            if arg_match:
                correct_args += 1

            # Metric 3: Faithfulness / Groundedness Score (0.0 to 1.0)
            final_text = agent_output.get("final_response", "")
            faithfulness = 1.0 if test.ground_truth_fact.lower() in final_text.lower() else 0.5
            faithfulness_total += faithfulness

            results.append({
                "test_id": test.test_id,
                "tool_match": tool_match,
                "arg_match": arg_match,
                "faithfulness": faithfulness,
                "latency_ms": duration_ms,
                "spans": tracer.spans
            })

        total = len(golden_dataset)
        return EvaluationScorecard(
            total_tests=total,
            tool_accuracy_pct=round((correct_tools / total) * 100, 2) if total else 0.0,
            argument_precision_pct=round((correct_args / total) * 100, 2) if total else 0.0,
            faithfulness_score=round(faithfulness_total / total, 2) if total else 0.0,
            average_latency_ms=round(sum(latencies) / total, 2) if total else 0.0,
            detailed_results=results
        )

# Sample Golden Dataset
SAMPLE_GOLDEN_DATASET = [
    GoldenTestCase(
        test_id="TC_01",
        user_prompt="Check storage utilization for bucket gs://finance-prod-2026 in us-central1",
        expected_tool="get_bucket_metrics",
        expected_args={"bucket_name": "gs://finance-prod-2026", "region": "us-central1"},
        ground_truth_fact="328.45"
    ),
    GoldenTestCase(
        test_id="TC_02",
        user_prompt="Restart the agent-gateway-api on project gcp-prod-arch-2026 immediately",
        expected_tool="restart_cloud_run_service",
        expected_args={"service_name": "agent-gateway-api", "project_id": "gcp-prod-arch-2026", "force": True},
        ground_truth_fact="RESTARTED"
    )
]

def mock_agent_runner(prompt: str, tracer: CloudTraceSimulator) -> Dict[str, Any]:
    """Simulates agent execution under evaluation."""
    tracer.log_span("Gemini3.7Flash_Reasoning", 240.5, {"model": "gemini-3.7-flash", "thinking_budget": 2048})

    if "storage" in prompt.lower() or "bucket" in prompt.lower():
        tracer.log_span("ToolExecution_get_bucket_metrics", 45.2)
        return {
            "tool_called": "get_bucket_metrics",
            "tool_args": {"bucket_name": "gs://finance-prod-2026", "region": "us-central1"},
            "final_response": "Bucket gs://finance-prod-2026 utilization is currently 328.45 GB."
        }
    else:
        tracer.log_span("ToolExecution_restart_cloud_run", 88.0)
        return {
            "tool_called": "restart_cloud_run_service",
            "tool_args": {"service_name": "agent-gateway-api", "project_id": "gcp-prod-arch-2026", "force": True},
            "final_response": "Service agent-gateway-api status is RESTARTED successfully."
        }

def main():
    print("====================================================================")
    print("Module 12: AgentOps: Evaluation, Golden Datasets & Observability")
    print("====================================================================\n")

    evaluator = AgentOpsEvaluator()
    print("--- 1. Running ADK evalset Against Golden Dataset ---")
    scorecard = evaluator.evaluate_test_suite(SAMPLE_GOLDEN_DATASET, mock_agent_runner)

    print(f"Total Test Cases Evaluated : {scorecard.total_tests}")
    print(f"Tool Selection Accuracy     : {scorecard.tool_accuracy_pct}%")
    print(f"Argument Precision          : {scorecard.argument_precision_pct}%")
    print(f"Retrieval Faithfulness      : {scorecard.faithfulness_score} / 1.0")
    print(f"Average Agent Latency       : {scorecard.average_latency_ms} ms\n")

    print("--- 2. Sample Distributed Trace Spans (Cloud Trace) ---")
    print(json.dumps(scorecard.detailed_results[0]["spans"], indent=2))

if __name__ == "__main__":
    main()
