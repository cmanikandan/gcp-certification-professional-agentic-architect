"""
Unit Tests for Module 01: Understand Google Cloud Agents & Architecture
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from agent_architecture_demo import (
    DeterministicStateMachine,
    AutonomousAgentSimulator,
    EnterpriseDataSource,
    EnterpriseDataConnectionPlanner,
)

def test_state_machine_happy_path():
    sm = DeterministicStateMachine()
    assert sm.current_page == "START"

    r1 = sm.process_event("intent:track_order")
    assert r1["action"] == "TRANSITION_SUCCESS"
    assert sm.current_page == "ORDER_LOOKUP"

    r2 = sm.process_event("param:order_valid")
    assert r2["action"] == "TRANSITION_SUCCESS"
    assert sm.current_page == "ORDER_STATUS"

def test_state_machine_escalation():
    sm = DeterministicStateMachine()
    r1 = sm.process_event("invalid_trigger_1")
    assert r1["action"] == "EVENT_HANDLER_TRIGGERED"
    assert sm.current_page == "FALLBACK_1"

    r2 = sm.process_event("invalid_trigger_2")
    assert r2["action"] == "EVENT_HANDLER_TRIGGERED"
    assert sm.current_page == "ESCALATION"

def test_autonomous_agent_returnable():
    agent = AutonomousAgentSimulator()
    result = agent.execute_goal("Return item", "ORD-991")
    assert result["status"] == "completed"
    assert len(result["steps"]) == 4
    assert "123.49" in result["final_response"] or "refund" in result["final_response"].lower()

def test_autonomous_agent_not_found():
    agent = AutonomousAgentSimulator()
    result = agent.execute_goal("Return item", "NON_EXISTENT")
    assert result["status"] == "completed"
    assert "could not locate" in result["final_response"].lower()


def test_enterprise_multimodal_connection_plan():
    plan = EnterpriseDataConnectionPlanner().plan([
        EnterpriseDataSource("Claims", "pdf", "Cloud Storage", True),
        EnterpriseDataSource("Damage photos", "image", "Cloud Storage", True),
    ])
    assert plan["ingestion_target"] == "Gemini Enterprise / Agent Search"
    assert plan["modalities"] == ["image", "pdf"]
    assert "Access-filtered retrieval" in plan["security_controls"]
