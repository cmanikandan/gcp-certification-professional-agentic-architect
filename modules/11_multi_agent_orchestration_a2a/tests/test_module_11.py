"""
Unit Tests for Module 11: Multi-Agent Systems & A2A
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from multi_agent_system import (
    SupervisorAgent,
    SecurityAuditAgent,
    FinOpsOptimizationAgent,
    A2AHandoffToken
)

def test_specialist_security_agent():
    agent = SecurityAuditAgent()
    token = A2AHandoffToken(
        token_id="tok_1",
        initiator_agent="sup",
        target_agent="agent-security-auditor",
        task_payload={"resource": "Public Cloud Run API"},
        session_context={}
    )
    res = agent.execute_a2a_handoff(token)
    assert res["status"] == "COMPLETED"
    assert "CRITICAL: Public internet exposure" in res["findings"][0]
    assert res["security_score"] > 0

def test_supervisor_orchestration():
    supervisor = SupervisorAgent()
    plan = supervisor.orchestrate_workflow({
        "service_name": "Internal Billing Agent",
        "workload_type": "Batch"
    })

    assert plan["overall_status"] == "APPROVED"
    assert "finops_recommendations" in plan
    assert len(plan["a2a_execution_trace"]) == 2
    assert "32.0%" in plan["finops_savings_potential"]
