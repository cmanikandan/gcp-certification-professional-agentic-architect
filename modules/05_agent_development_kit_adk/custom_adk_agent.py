"""
Module 05: Engineer AI Agents with Agent Development Kit (ADK)
Demonstrates:
1. Production ADK Agent Architecture with Google GenAI SDK & Gemini 3.7 Flash
2. Pydantic Structured Output Validation (response_schema)
3. Dynamic Thinking Budget Configuration
4. Live API & Offline Mock Fallback Engine
"""

import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# 1. Pydantic Structured Schema
# ==============================================================================

class ArchitecturalRecommendation(BaseModel):
    service_name: str = Field(description="Google Cloud target service (e.g., Cloud Run, GKE, BigQuery)")
    sizing_tier: str = Field(description="Recommended sizing tier or machine configuration")
    monthly_cost_estimate_usd: float = Field(description="Estimated monthly cost in USD")
    rationale: str = Field(description="Architectural decision justification")

class CloudArchitecturePlan(BaseModel):
    project_name: str = Field(description="Name of the cloud architecture project")
    primary_workload_type: str = Field(description="Category of workload (e.g., High-Throughput Agentic API)")
    recommendations: List[ArchitecturalRecommendation] = Field(description="List of service recommendations")
    total_estimated_cost_usd: float = Field(description="Sum of all service monthly costs")
    governance_guardrails: List[str] = Field(description="Enforced security and compliance boundaries")

# ==============================================================================
# 2. ADK Agent Implementation
# ==============================================================================

class ADKEnterpriseAgent:
    """Enterprise Agent built using Google GenAI SDK and ADK patterns."""

    def __init__(self, model_name: str = "gemini-3.7-flash", thinking_budget: int = 2048):
        self.model_name = os.getenv("GEMINI_MODEL", model_name)
        self.thinking_budget = int(os.getenv("GEMINI_THINKING_BUDGET", str(thinking_budget)))
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None

    def generate_architecture_plan(self, workload_description: str) -> CloudArchitecturePlan:
        """Generates a structured cloud architecture plan using Gemini 3.7 Flash."""
        # Check if live client is available
        if self.client:
            try:
                from google.genai import types
                prompt = (
                    f"You are a Google Cloud Certified Professional Agentic Architect.\n"
                    f"Design an optimal cloud architecture plan for the following workload:\n"
                    f"'{workload_description}'\n"
                    f"Ensure you configure low-latency runtimes, secure databases, and Model Armor guardrails."
                )
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CloudArchitecturePlan,
                        thinking_config=types.ThinkingConfig(thinking_budget=self.thinking_budget) if hasattr(types, "ThinkingConfig") else None
                    )
                )
                parsed_json = json.loads(response.text)
                return CloudArchitecturePlan(**parsed_json)
            except Exception as e:
                # Fallback to mock if API quota / network issue occurs
                return self._mock_architecture_plan(workload_description)
        else:
            return self._mock_architecture_plan(workload_description)

    def _mock_architecture_plan(self, workload_description: str) -> CloudArchitecturePlan:
        """Deterministic mock engine simulating Gemini 3.7 Flash structured output."""
        return CloudArchitecturePlan(
            project_name="Enterprise Agentic Gateway",
            primary_workload_type="High-Throughput Multi-Agent Orchestration",
            recommendations=[
                ArchitecturalRecommendation(
                    service_name="Cloud Run",
                    sizing_tier="4 vCPU, 8 GB RAM, min-instances=2",
                    monthly_cost_estimate_usd=145.50,
                    rationale="Serverless container hosting with rapid scaling and zero-idle cost for Agent Runtime APIs."
                ),
                ArchitecturalRecommendation(
                    service_name="Memorystore for Redis",
                    sizing_tier="Standard Tier 5GB with Multi-AZ Replication",
                    monthly_cost_estimate_usd=85.00,
                    rationale="Sub-millisecond session state persistence and short-term working context caching."
                ),
                ArchitecturalRecommendation(
                    service_name="Vertex AI Vector Search 1.0",
                    sizing_tier="Standard 1-replica index endpoint with ScaNN",
                    monthly_cost_estimate_usd=120.00,
                    rationale="High-performance approximate nearest neighbor retrieval for enterprise RAG."
                )
            ],
            total_estimated_cost_usd=350.50,
            governance_guardrails=[
                "Model Armor inline prompt injection inspection on Agent Gateway",
                "Agent Identity Principal Access Boundary (PAB) scoping IAM to VPC-SC perimeter",
                "Sensitive Data Protection (Cloud DLP) automated PII masking on agent responses"
            ]
        )

def main():
    print("====================================================================")
    print("Module 05: Engineer AI Agents with Agent Development Kit (ADK)")
    print("====================================================================\n")

    agent = ADKEnterpriseAgent()
    print(f"Agent Model        : {agent.model_name}")
    print(f"Thinking Budget    : {agent.thinking_budget} tokens")
    print(f"Live Client Active : {agent.client is not None}\n")

    workload = "High-throughput autonomous customer service platform needing low-latency RAG and Redis session state"
    print(f"Input Workload: '{workload}'\n")
    print("Generating Cloud Architecture Plan...\n")

    plan = agent.generate_architecture_plan(workload)
    print(json.dumps(plan.model_dump(), indent=2))

if __name__ == "__main__":
    main()
