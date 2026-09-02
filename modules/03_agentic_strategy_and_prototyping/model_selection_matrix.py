"""
Module 03: Agentic Strategy & Model Selection
Demonstrates:
1. Automated Model Selection Rule Engine based on task requirements (Latency, Cost, Reasoning)
2. Dynamic Thinking Budget Calibrator for Gemini 3.7 Flash
3. Illustrative Cost & Latency Estimation Pipeline (not a live price catalog)
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class ModelProfile:
    name: str
    input_cost_per_m: float
    output_cost_per_m: float
    context_window: int
    supports_thinking: bool
    typical_latency_ms: int
    best_use_case: str

# Model Registry
MODEL_CATALOG: Dict[str, ModelProfile] = {
    "gemini-3.7-flash": ModelProfile(
        name="gemini-3.7-flash",
        input_cost_per_m=0.10,
        output_cost_per_m=0.40,
        context_window=1_000_000,
        supports_thinking=True,
        typical_latency_ms=450,
        best_use_case="Core Enterprise Agentic Workflows, Multi-Tool Orchestration & Coding"
    ),
    "gemini-2.5-pro": ModelProfile(
        name="gemini-2.5-pro",
        input_cost_per_m=1.25,
        output_cost_per_m=5.00,
        context_window=2_000_000,
        supports_thinking=True,
        typical_latency_ms=1800,
        best_use_case="Deep Multi-Document Synthesis, Extreme Analytical Proofs & Complex Audits"
    ),
    "gemini-2.5-flash-lite": ModelProfile(
        name="gemini-2.5-flash-lite",
        input_cost_per_m=0.0375,
        output_cost_per_m=0.15,
        context_window=1_000_000,
        supports_thinking=False,
        typical_latency_ms=180,
        best_use_case="High-Throughput Intent Classification, Triage & Fast Extraction"
    ),
    "gemma-2-9b": ModelProfile(
        name="gemma-2-9b",
        input_cost_per_m=0.0,
        output_cost_per_m=0.0,
        context_window=8_192,
        supports_thinking=False,
        typical_latency_ms=120,
        best_use_case="On-Device / Air-Gapped Edge Gateways & Self-Hosted Compute"
    )
}

class AgenticModelSelector:
    """Evaluates task constraints and selects the optimal Google Cloud model."""

    def select_optimal_model(
        self,
        task_type: str,
        requires_tools: bool = True,
        max_acceptable_latency_ms: int = 2000,
        is_air_gapped: bool = False,
        requires_deep_reasoning: bool = False
    ) -> Dict[str, Any]:
        if is_air_gapped:
            selected = MODEL_CATALOG["gemma-2-9b"]
            reason = "Air-gapped on-device environment requires self-hosted SLM (Gemma 2)."
            thinking_budget = 0
        elif task_type in ["classification", "intent_routing", "simple_extraction"] and not requires_deep_reasoning:
            selected = MODEL_CATALOG["gemini-2.5-flash-lite"]
            reason = "High-throughput deterministic task suited for low-latency Flash-Lite."
            thinking_budget = 0
        elif task_type in ["deep_audit", "legal_compliance_audit"] and max_acceptable_latency_ms > 2000:
            selected = MODEL_CATALOG["gemini-2.5-pro"]
            reason = "Complex multi-document synthesis requiring Gemini 2.5 Pro."
            thinking_budget = 4096
        else:
            # Default Enterprise Agent Workhorse: Gemini 3.7 Flash
            selected = MODEL_CATALOG["gemini-3.7-flash"]
            reason = "Gemini 3.7 Flash provides the optimal balance of reasoning, tool accuracy, speed, and cost."
            thinking_budget = self.calculate_thinking_budget(task_type, requires_tools)

        return {
            "selected_model": selected.name,
            "profile": selected,
            "thinking_budget": thinking_budget,
            "selection_rationale": reason
        }

    def calculate_thinking_budget(self, task_type: str, requires_tools: bool) -> int:
        """Dynamically computes the thinking budget for Gemini 3.7 Flash."""
        if task_type in ["code_refactoring", "multi_step_tool_planning", "financial_arbitrage"]:
            return 2048
        elif task_type in ["complex_workflow_orchestration"]:
            return 4096
        elif requires_tools:
            return 1024
        return 512

    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int, thinking_tokens: int = 0) -> Dict[str, float]:
        profile = MODEL_CATALOG.get(model_name, MODEL_CATALOG["gemini-3.7-flash"])
        total_output = output_tokens + thinking_tokens
        input_cost = (input_tokens / 1_000_000) * profile.input_cost_per_m
        output_cost = (total_output / 1_000_000) * profile.output_cost_per_m
        return {
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(input_cost + output_cost, 6)
        }

def main():
    print("====================================================================")
    print("Module 03: Agentic Strategy & Model Selection Decision Matrix")
    print("====================================================================\n")
    print("NOTE: Catalog prices/latencies are illustrative lab inputs; verify current product documentation before a real design.\n")

    selector = AgenticModelSelector()

    scenarios = [
        {"name": "Real-Time Customer Service Agent", "task": "multi_step_tool_planning", "tools": True, "latency": 800, "air_gapped": False},
        {"name": "Fast Intent Classifier", "task": "classification", "tools": False, "latency": 250, "air_gapped": False},
        {"name": "Multi-Million Token Legal Compliance Audit", "task": "deep_audit", "tools": False, "latency": 5000, "air_gapped": False},
        {"name": "Edge Warehouse Device (Offline)", "task": "inventory_scan", "tools": False, "latency": 500, "air_gapped": True}
    ]

    for s in scenarios:
        res = selector.select_optimal_model(
            task_type=s["task"],
            requires_tools=s["tools"],
            max_acceptable_latency_ms=s["latency"],
            is_air_gapped=s["air_gapped"]
        )
        cost = selector.estimate_cost(res["selected_model"], input_tokens=15000, output_tokens=800, thinking_tokens=res["thinking_budget"])
        print(f"Scenario: {s['name']}")
        print(f"  -> Selected Model  : {res['selected_model']}")
        print(f"  -> Thinking Budget : {res['thinking_budget']} tokens")
        print(f"  -> Illustrative Cost: ${cost['total_cost_usd']} / 15k input tokens")
        print(f"  -> Rationale       : {res['selection_rationale']}\n")

if __name__ == "__main__":
    main()
