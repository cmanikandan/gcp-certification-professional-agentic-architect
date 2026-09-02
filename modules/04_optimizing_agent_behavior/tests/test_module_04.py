"""
Unit Tests for Module 04: Optimizing Agent Behavior
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from prompt_optimizer import (
    PromptTemplateBuilder,
    ReasoningLoopDetector
)

def test_prompt_builder():
    builder = PromptTemplateBuilder("Test Agent", "Enterprise Testing")
    builder.add_guardrail("Safety Rule 1")
    builder.add_few_shot_example("Input 1", "Thought 1", "Action 1")
    prompt = builder.build_system_instruction()

    assert "Test Agent" in prompt
    assert "Safety Rule 1" in prompt
    assert "FEW-SHOT DEMONSTRATIONS" in prompt
    assert "Decision basis" in prompt
    assert "never emit hidden scratchpad" in prompt
    assert "<thought>...</thought>" not in prompt

def test_loop_detector_repetitive_calls():
    detector = ReasoningLoopDetector(max_consecutive_duplicates=2, max_total_turns=5)
    r1 = detector.record_action("tool_a", {"k": "v"})
    assert r1["loop_detected"] is False

    r2 = detector.record_action("tool_a", {"k": "v"})
    assert r2["loop_detected"] is True
    assert r2["reason"] == "REPETITIVE_TOOL_CALL_DETECTED"
    assert r2["recommendation"] == "INJECT_REFLECTION_PROMPT"

def test_loop_detector_max_turns():
    detector = ReasoningLoopDetector(max_consecutive_duplicates=5, max_total_turns=3)
    detector.record_action("tool_1", {"i": 1})
    detector.record_action("tool_2", {"i": 2})
    r3 = detector.record_action("tool_3", {"i": 3})

    assert r3["loop_detected"] is True
    assert r3["reason"] == "MAX_TURNS_EXCEEDED"
    assert r3["recommendation"] == "HALT_AND_ESCALATE"
