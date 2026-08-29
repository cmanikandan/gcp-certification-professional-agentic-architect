"""
Unit Tests for Module 05: Agent Development Kit (ADK)
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from custom_adk_agent import (
    ADKEnterpriseAgent,
    CloudArchitecturePlan,
    ArchitecturalRecommendation
)

def test_pydantic_schema_validation():
    rec = ArchitecturalRecommendation(
        service_name="Cloud Run",
        sizing_tier="2 vCPU, 4GB",
        monthly_cost_estimate_usd=50.0,
        rationale="Cost-effective serverless execution"
    )
    assert rec.service_name == "Cloud Run"
    assert rec.monthly_cost_estimate_usd == 50.0

    plan = CloudArchitecturePlan(
        project_name="Test Project",
        primary_workload_type="Batch RAG",
        recommendations=[rec],
        total_estimated_cost_usd=50.0,
        governance_guardrails=["PAB Policy"]
    )
    assert plan.project_name == "Test Project"
    assert len(plan.recommendations) == 1
    assert plan.total_estimated_cost_usd == 50.0

def test_agent_plan_generation():
    agent = ADKEnterpriseAgent()
    plan = agent.generate_architecture_plan("Build an enterprise multi-agent system")
    assert isinstance(plan, CloudArchitecturePlan)
    assert len(plan.recommendations) >= 3
    assert plan.total_estimated_cost_usd > 0
    assert len(plan.governance_guardrails) >= 2
