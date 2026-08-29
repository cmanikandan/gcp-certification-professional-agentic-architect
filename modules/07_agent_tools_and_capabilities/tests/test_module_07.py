"""
Unit Tests for Module 07: Dynamic Agent Tools
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from tool_orchestrator import (
    ToolRegistry,
    get_bucket_metrics,
    restart_cloud_run_service
)

def test_tool_registration_and_schemas():
    test_reg = ToolRegistry()

    @test_reg.register(description="Calculate tax")
    def calculate_tax(amount: float, rate: float = 0.08) -> float:
        return amount * rate

    schemas = test_reg.get_function_declarations()
    assert len(schemas) == 1
    assert schemas[0]["name"] == "calculate_tax"
    assert "amount" in schemas[0]["parameters"]["properties"]
    assert "amount" in schemas[0]["parameters"]["required"]

def test_tool_execution_success():
    test_reg = ToolRegistry()

    @test_reg.register()
    def multiply(a: int, b: int) -> int:
        return a * b

    res = test_reg.execute("multiply", {"a": 5, "b": 10})
    assert res["status"] == "success"
    assert res["output"] == 50

def test_tool_type_coercion():
    test_reg = ToolRegistry()

    @test_reg.register()
    def toggle(flag: bool) -> bool:
        return not flag

    res = test_reg.execute("toggle", {"flag": "true"})
    assert res["status"] == "success"
    assert res["output"] is False

def test_tool_not_found():
    test_reg = ToolRegistry()
    res = test_reg.execute("non_existent_tool", {})
    assert res["status"] == "error"
    assert res["error_code"] == "TOOL_NOT_FOUND"
