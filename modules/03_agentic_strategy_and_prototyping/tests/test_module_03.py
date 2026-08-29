"""
Unit Tests for Module 03: Agentic Strategy & Model Selection
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from model_selection_matrix import (
    AgenticModelSelector,
    MODEL_CATALOG
)

def test_model_catalog_keys():
    assert "gemini-3.7-flash" in MODEL_CATALOG
    assert "gemini-2.5-pro" in MODEL_CATALOG
    assert "gemini-2.5-flash-lite" in MODEL_CATALOG
    assert "gemma-2-9b" in MODEL_CATALOG

def test_select_air_gapped():
    selector = AgenticModelSelector()
    res = selector.select_optimal_model("any_task", is_air_gapped=True)
    assert res["selected_model"] == "gemma-2-9b"
    assert res["thinking_budget"] == 0

def test_select_classification():
    selector = AgenticModelSelector()
    res = selector.select_optimal_model("classification", requires_tools=False)
    assert res["selected_model"] == "gemini-2.5-flash-lite"
    assert res["thinking_budget"] == 0

def test_select_core_enterprise_agent():
    selector = AgenticModelSelector()
    res = selector.select_optimal_model("multi_step_tool_planning", requires_tools=True)
    assert res["selected_model"] == "gemini-3.7-flash"
    assert res["thinking_budget"] == 2048

def test_cost_estimation():
    selector = AgenticModelSelector()
    cost = selector.estimate_cost("gemini-3.7-flash", input_tokens=1_000_000, output_tokens=1_000_000)
    assert cost["input_cost_usd"] == 0.10
    assert cost["output_cost_usd"] == 0.40
    assert cost["total_cost_usd"] == 0.50
