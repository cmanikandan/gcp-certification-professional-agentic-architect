#!/usr/bin/env python3
"""Lab 08: ADK Fundamentals."""
import sys
from pydantic import BaseModel, Field
from common import DEFAULT_AGENT_MODEL, load_config, require_live

from google.adk.agents import (
    LlmAgent,
    SequentialAgent,
    ParallelAgent,
    LoopAgent,
)
from google.adk.models import Gemini
from google.adk.workflow import Workflow, FunctionNode, Edge, START
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import InMemoryRunner


class ReviewOutput(BaseModel):
    is_approved: bool = Field(description="Whether the design is approved")
    comments: str = Field(description="Review comments")

class AppState(BaseModel):
    review: ReviewOutput | None = None


def run_offline():
    print("Running Lab 08 OFFLINE: ADK Fundamentals")
    
    # 1. Core LlmAgent
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    
    reviewer_agent = LlmAgent(
        name="Reviewer",
        model=model,
        instruction="Review the architecture design.",
        output_schema=ReviewOutput,
        output_key="review",
        include_contents="default",
    )
    print(f"\nCreated {reviewer_agent.__class__.__name__} '{reviewer_agent.name}'")
    print(f"Output schema bound to key: '{reviewer_agent.output_key}'")

    # 2. Workflow Agents
    generator_agent = LlmAgent(
        name="Generator",
        model=model,
        instruction="Generate an architecture design.",
    )
    
    pipeline = SequentialAgent(
        name="Pipeline",
        sub_agents=[generator_agent, reviewer_agent],
    )
    print(f"\nCreated a declarative {pipeline.__class__.__name__} with {len(pipeline.sub_agents)} agents.")
    
    reviewer_2 = LlmAgent(name="Reviewer2", model=model, instruction="...")
    reviewer_3 = LlmAgent(name="Reviewer3", model=model, instruction="...")
    parallel = ParallelAgent(
        name="FanOut",
        sub_agents=[reviewer_2, reviewer_3],
    )
    print(f"Created a {parallel.__class__.__name__} to fan-out tasks.")

    reviewer_4 = LlmAgent(name="Reviewer4", model=model, instruction="...")
    loop = LoopAgent(
        name="ReviewLoop",
        sub_agents=[reviewer_4],
        max_iterations=3,
    )
    print(f"Created a {loop.__class__.__name__} with max_iterations={loop.max_iterations}.")

    wf_generator = LlmAgent(name="WFGenerator", model=model, instruction="...")
    wf_reviewer = LlmAgent(name="WFReviewer", model=model, instruction="...")
    
    # FunctionNode for custom logic
    def check_approval(review: ReviewOutput | None = None) -> str:
        if review and review.is_approved:
            return "approved"
        return "rejected"

    router_node = FunctionNode(name="Router", func=check_approval)
    
    # 3. Graph Workflow
    workflow = Workflow(
        name="ComplexReviewWorkflow",
        state_schema=AppState,
        edges=[
            Edge(from_node=START, to_node=wf_generator),
            Edge(from_node=wf_generator, to_node=wf_reviewer),
            Edge(from_node=wf_reviewer, to_node=router_node)
        ]
    )
    
    print(f"\nCreated a Graph {workflow.__class__.__name__} with nodes: {workflow.graph.nodes}")


def run_live(config):
    print("Running Lab 08 LIVE")
    run_offline()
    # In a fully fleshed out live run, we'd use the InMemoryRunner
    # runner = InMemoryRunner(
    #     session_service=InMemorySessionService(),
    #     memory_service=InMemoryMemoryService(),
    # )
    # runner.run(...)


if __name__ == "__main__":
    config = load_config(sys.argv[1:])
    if require_live(config):
        run_live(config)
    else:
        run_offline()
