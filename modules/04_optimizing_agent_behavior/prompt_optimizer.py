"""
Module 04: Optimizing Agent Behavior
Demonstrates:
1. System Instruction & Few-Shot Prompt Template Builder
2. Concise decision-rationale examples without exposing private reasoning traces
3. Real-Time Tool Loop / Cycle Detection Interceptor
"""

import os
from typing import Dict, List, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class PromptTemplateBuilder:
    """Constructs structured, production-grade system prompts with Few-Shot examples and guardrails."""

    def __init__(self, agent_role: str, enterprise_context: str):
        self.agent_role = agent_role
        self.enterprise_context = enterprise_context
        self.guardrails: List[str] = []
        self.few_shot_examples: List[Dict[str, str]] = []

    def add_guardrail(self, guardrail: str) -> "PromptTemplateBuilder":
        self.guardrails.append(guardrail)
        return self

    def add_few_shot_example(self, user_input: str, expected_thought: str, expected_action: str) -> "PromptTemplateBuilder":
        """Add an observable decision example.

        ``expected_thought`` is retained for API compatibility, but it must be a
        short decision basis, not a hidden chain-of-thought transcript.
        """
        self.few_shot_examples.append({
            "input": user_input,
            "decision_basis": expected_thought,
            "action": expected_action
        })
        return self

    def build_system_instruction(self) -> str:
        guardrails_str = "\n".join([f"- {g}" for g in self.guardrails])
        examples_str = ""
        if self.few_shot_examples:
            examples_str = "\n### FEW-SHOT DEMONSTRATIONS:\n"
            for i, ex in enumerate(self.few_shot_examples, 1):
                examples_str += (
                    f"Example {i}:\n"
                    f"User: {ex['input']}\n"
                    f"Decision basis: {ex['decision_basis']}\n"
                    f"Action: {ex['action']}\n\n"
                )

        return (
            f"You are {self.agent_role}.\n"
            f"Enterprise Context: {self.enterprise_context}\n\n"
            f"### MANDATORY GUARDRAILS:\n{guardrails_str}\n"
            f"{examples_str}"
            "Keep private reasoning private. Return only the selected action and a concise, "
            "auditable decision rationale; never emit hidden scratchpad or <thought> tags."
        )

class ReasoningLoopDetector:
    """Detects repetitive tool invocations or cyclic reasoning loops in agent execution."""

    def __init__(self, max_consecutive_duplicates: int = 2, max_total_turns: int = 5):
        self.max_consecutive_duplicates = max_consecutive_duplicates
        self.max_total_turns = max_total_turns
        self.history: List[Dict[str, Any]] = []

    def record_action(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Records an action and checks for loop conditions."""
        current_action = {"tool": tool_name, "args": arguments}
        self.history.append(current_action)

        if len(self.history) >= self.max_total_turns:
            return {
                "loop_detected": True,
                "reason": "MAX_TURNS_EXCEEDED",
                "recommendation": "HALT_AND_ESCALATE"
            }

        # Check consecutive duplicate tool calls with same parameters
        if len(self.history) >= self.max_consecutive_duplicates:
            recent = self.history[-self.max_consecutive_duplicates:]
            if all(r == current_action for r in recent):
                return {
                    "loop_detected": True,
                    "reason": "REPETITIVE_TOOL_CALL_DETECTED",
                    "recommendation": "INJECT_REFLECTION_PROMPT"
                }

        return {"loop_detected": False, "reason": None, "recommendation": "CONTINUE"}

def main():
    print("====================================================================")
    print("Module 04: Optimizing Agent Behavior & Loop Prevention")
    print("====================================================================\n")

    # 1. Build Production Prompt
    print("--- 1. Generating Optimized System Prompt ---")
    builder = PromptTemplateBuilder(
        agent_role="Google Cloud Database Migration Specialist Agent",
        enterprise_context="Migrating on-premises PostgreSQL instances to Cloud SQL / AlloyDB."
    )
    builder.add_guardrail("Never execute DROP TABLE or destructive DDL without explicit human confirmation.")
    builder.add_guardrail("Always compute index fragmentation before recommending instance scaling.")
    builder.add_few_shot_example(
        user_input="Analyze table orders on prod db",
        expected_thought="Need to check table size and index statistics using inspect_table_stats tool.",
        expected_action="CALL tool: inspect_table_stats(table='orders', schema='public')"
    )
    system_prompt = builder.build_system_instruction()
    print(system_prompt)

    # 2. Test Loop Detection Interceptor
    print("\n--- 2. Simulating Agent Loop Interceptor ---")
    detector = ReasoningLoopDetector(max_consecutive_duplicates=2, max_total_turns=4)

    # Turn 1
    t1 = detector.record_action("search_docs", {"query": "alloydb limits"})
    print("Turn 1 (First search) ->", t1)

    # Turn 2 (Duplicate tool & argument)
    t2 = detector.record_action("search_docs", {"query": "alloydb limits"})
    print("Turn 2 (Duplicate search) ->", t2)

    # Turn 3
    t3 = detector.record_action("search_docs", {"query": "alloydb limits"})
    print("Turn 3 (Duplicate search) ->", t3)

if __name__ == "__main__":
    main()
