#!/usr/bin/env python3
"""Lab 08: ADK Fundamentals & Multi-Agent Latency Math (Objectives 3.1 & 3.3)."""

from __future__ import annotations

import asyncio
import sys
import warnings
from dataclasses import dataclass

from common import DEFAULT_AGENT_MODEL, DEFAULT_FAST_MODEL, load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, step, table
from google.adk.agents import (
    LlmAgent,
    LoopAgent,
    ParallelAgent,
    SequentialAgent,
)
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, exit_loop
from google.adk.workflow import Edge, FunctionNode, JoinNode, START, Workflow
from pydantic import BaseModel, Field


class ReviewOutput(BaseModel):
    is_approved: bool = Field(description="Whether the architecture design is approved")
    comments: str = Field(description="Concise actionable review feedback")


class TicketEntities(BaseModel):
    order_id: str = Field(description="Extracted order identifier")
    issue_type: str = Field(description="Normalized issue category")


class AppState(BaseModel):
    entities: TicketEntities | None = None
    review: ReviewOutput | None = None
    order_ctx: str | None = None
    billing_ctx: str | None = None
    shipping_ctx: str | None = None


@dataclass(frozen=True)
class TopologyMetrics:
    """Latency and LLM-hop comparison across ADK multi-agent patterns."""

    pattern: str
    total_latency_ms: int
    llm_calls: int


def compute_support_fanout_comparison(
    branch_latencies_ms: list[int],
    synthesis_ms: int,
) -> dict[str, int]:
    """Compare Sequential sum(T_i) vs Parallel/JoinNode max(T_i) + synthesis."""
    return {
        "sequential_ms": sum(branch_latencies_ms) + synthesis_ms,
        "parallel_ms": (max(branch_latencies_ms) if branch_latencies_ms else 0) + synthesis_ms,
    }


def compute_delegation_hops(
    router_ms: int,
    specialist_ms: int,
    parent_synthesis_ms: int,
) -> dict[str, TopologyMetrics]:
    """Compare deterministic Workflow vs transfer_to_agent vs AgentTool hops."""
    return {
        "workflow_edge": TopologyMetrics(
            pattern="Workflow / SequentialAgent (0 LLM routing hops)",
            total_latency_ms=specialist_ms,
            llm_calls=1,
        ),
        "transfer_to_agent": TopologyMetrics(
            pattern="LlmAgent sub_agents + transfer_to_agent (direct handoff)",
            total_latency_ms=router_ms + specialist_ms,
            llm_calls=2,
        ),
        "agent_tool_default": TopologyMetrics(
            pattern="AgentTool(skip_summarization=False) (parent synthesis)",
            total_latency_ms=router_ms + specialist_ms + parent_synthesis_ms,
            llm_calls=3,
        ),
        "agent_tool_skip_summary": TopologyMetrics(
            pattern="AgentTool(skip_summarization=True)",
            total_latency_ms=router_ms + specialist_ms,
            llm_calls=2,
        ),
    }


def build_token_hygiene_pipeline() -> SequentialAgent:
    """Build a SequentialAgent using output_schema + output_key + include_contents='none'."""
    fast_model = Gemini(model=DEFAULT_FAST_MODEL)
    std_model = Gemini(model=DEFAULT_AGENT_MODEL)

    extractor = LlmAgent(
        name="TicketExtractor",
        model=fast_model,
        instruction="Extract structured order_id and issue_type from the customer message.",
        output_schema=TicketEntities,
        output_key="entities",
    )
    reviewer = LlmAgent(
        name="CompactPolicyReviewer",
        model=std_model,
        instruction="Evaluate resolution policy for extracted state: {entities}.",
        output_schema=ReviewOutput,
        output_key="review",
        include_contents="none",
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return SequentialAgent(
            name="TokenHygienePipeline",
            sub_agents=[extractor, reviewer],
        )


def build_parallel_support_workflow() -> Workflow:
    """Build a modern ADK 2.9.0 fan-out/fan-in Graph Workflow with JoinNode."""
    fast_model = Gemini(model=DEFAULT_FAST_MODEL)
    std_model = Gemini(model=DEFAULT_AGENT_MODEL)

    order_agent = LlmAgent(
        name="OrderStatusWorker",
        model=fast_model,
        instruction="Fetch order status.",
        output_key="order_ctx",
        include_contents="none",
    )
    billing_agent = LlmAgent(
        name="BillingHistoryWorker",
        model=fast_model,
        instruction="Fetch billing ledger.",
        output_key="billing_ctx",
        include_contents="none",
    )
    shipping_agent = LlmAgent(
        name="ShippingPolicyWorker",
        model=fast_model,
        instruction="Fetch carrier SLA policy.",
        output_key="shipping_ctx",
        include_contents="none",
    )
    join_barrier = JoinNode(name="SupportContextBarrier")
    drafter = LlmAgent(
        name="ResolutionDrafter",
        model=std_model,
        instruction="Synthesize resolution from {order_ctx}, {billing_ctx}, and {shipping_ctx}.",
        output_schema=ReviewOutput,
        output_key="review",
        include_contents="none",
    )

    def route_review(review: ReviewOutput | None = None) -> str:
        return "approved" if (review and review.is_approved) else "escalate"

    gate_node = FunctionNode(name="ApprovalGate", func=route_review)

    return Workflow(
        name="CustomerSupportFanOutGraph",
        state_schema=AppState,
        edges=[
            Edge(from_node=START, to_node=order_agent),
            Edge(from_node=START, to_node=billing_agent),
            Edge(from_node=START, to_node=shipping_agent),
            Edge(from_node=order_agent, to_node=join_barrier),
            Edge(from_node=billing_agent, to_node=join_barrier),
            Edge(from_node=shipping_agent, to_node=join_barrier),
            Edge(from_node=join_barrier, to_node=drafter),
            Edge(from_node=drafter, to_node=gate_node),
        ],
    )


def build_bounded_refinement_loop(max_iterations: int = 3) -> LoopAgent:
    """Build a bounded LoopAgent equipped with exit_loop to avoid tail-latency traps."""
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    critic = LlmAgent(
        name="BoundedCritic",
        model=model,
        instruction="Validate the draft; call exit_loop immediately once compliant.",
        tools=[exit_loop],
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return LoopAgent(
            name="BoundedRefinementLoop",
            sub_agents=[critic],
            max_iterations=max_iterations,
        )


def build_delegation_variants() -> tuple[LlmAgent, LlmAgent]:
    """Return (handoff_coordinator, agent_tool_coordinator) for comparison."""
    router_model = Gemini(model=DEFAULT_FAST_MODEL)
    spec_model = Gemini(model=DEFAULT_AGENT_MODEL)

    handoff_specialist = LlmAgent(
        name="BillingHandoffSpecialist",
        description="Handles billing disputes directly with the customer.",
        model=spec_model,
        instruction="Resolve the billing dispute.",
        disallow_transfer_to_peers=True,
    )
    handoff_coordinator = LlmAgent(
        name="DirectHandoffCoordinator",
        model=router_model,
        instruction="Transfer billing disputes to BillingHandoffSpecialist.",
        sub_agents=[handoff_specialist],
    )

    tool_specialist = LlmAgent(
        name="BillingToolSpecialist",
        description="Computes refund eligibility JSON for a supervisor.",
        model=spec_model,
        instruction="Return refund eligibility details.",
    )
    agent_tool_coordinator = LlmAgent(
        name="AgentToolSupervisor",
        model=spec_model,
        instruction="Invoke BillingToolSpecialist and synthesize an executive answer.",
        tools=[AgentTool(agent=tool_specialist, skip_summarization=False)],
    )
    return handoff_coordinator, agent_tool_coordinator


def run_offline() -> LabReport:
    banner(
        "Lab 08 — ADK Fundamentals & Multi-Agent Latency Math",
        "Objectives 3.1 & 3.3: LlmAgent, Workflow, JoinNode, LoopAgent & Delegation Hops (Offline)",
    )
    report = LabReport("Lab 08 — ADK Fundamentals & Latency Trade-Offs")

    section("1. Token Hygiene: output_schema + output_key + include_contents='none'")
    pipeline = build_token_hygiene_pipeline()
    extractor, reviewer = pipeline.sub_agents[0], pipeline.sub_agents[1]
    step(1, f"Stage 1 '{extractor.name}' -> output_key='{extractor.output_key}'")
    step(2, f"Stage 2 '{reviewer.name}' -> include_contents='{reviewer.include_contents}'")
    report.check(
        "Downstream sequential stage strips raw chat history via include_contents='none'",
        extractor.output_key == "entities" and reviewer.include_contents == "none",
    )

    section("2. Parallel Fan-Out Graph Workflow (JoinNode) vs Sequential Latency")
    wf = build_parallel_support_workflow()
    node_names = [n.name for n in wf.graph.nodes]
    step(3, f"Built Workflow '{wf.name}' with nodes: {node_names}")

    lat = compute_support_fanout_comparison(
        branch_latencies_ms=[420, 510, 380],
        synthesis_ms=450,
    )
    step(
        4,
        f"Support lookup latency (420/510/380ms + 450ms synthesis): "
        f"Sequential={lat['sequential_ms']}ms vs Parallel/JoinNode={lat['parallel_ms']}ms",
    )
    report.check(
        "Parallel JoinNode fan-out bounds branch latency at max(T_i) instead of sum(T_i)",
        lat["parallel_ms"] == 960 and lat["sequential_ms"] == 1760,
        f"{lat['parallel_ms']}ms vs {lat['sequential_ms']}ms",
    )
    report.check(
        "Workflow graph contains SupportContextBarrier JoinNode and ApprovalGate FunctionNode",
        "SupportContextBarrier" in node_names and "ApprovalGate" in node_names,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        par_agent = ParallelAgent(
            name="SupportParallelAgent",
            sub_agents=[
                LlmAgent(name="P1", model=DEFAULT_FAST_MODEL, output_key="order_ctx"),
                LlmAgent(name="P2", model=DEFAULT_FAST_MODEL, output_key="billing_ctx"),
            ],
        )
    report.check(
        "ParallelAgent workers write to distinct output_key slots",
        par_agent.sub_agents[0].output_key != par_agent.sub_agents[1].output_key,
    )

    section("3. Bounded LoopAgent & ADK 2.9.0 Workflow Nesting Nuance")
    loop = build_bounded_refinement_loop(max_iterations=3)
    step(5, f"LoopAgent '{loop.name}' capped at max_iterations={loop.max_iterations} with exit_loop tool.")
    report.check(
        "LoopAgent enforces max_iterations=3 and binds exit_loop tool",
        loop.max_iterations == 3 and exit_loop in loop.sub_agents[0].tools,
    )

    nesting_blocked = False
    try:
        LlmAgent(name="InvalidParent", model=DEFAULT_AGENT_MODEL, sub_agents=[wf])  # type: ignore[list-item]
    except Exception:
        nesting_blocked = True
    exam_note(
        "Workflow cannot yet be passed into LlmAgent.sub_agents (raises ValidationError), "
        "which is why SequentialAgent / ParallelAgent / LoopAgent remain necessary when nested."
    )
    report.check(
        "ADK 2.9.0 blocks nesting Workflow directly inside LlmAgent.sub_agents",
        nesting_blocked,
    )

    section("4. Delegation Latency Math: Workflow vs transfer_to_agent vs AgentTool")
    handoff_coord, tool_coord = build_delegation_variants()
    hops = compute_delegation_hops(router_ms=220, specialist_ms=600, parent_synthesis_ms=380)
    table(
        ["Pattern", "LLM Calls", "Total Latency (ms)"],
        [[m.pattern, m.llm_calls, m.total_latency_ms] for m in hops.values()],
    )
    report.check(
        "transfer_to_agent saves 1 LLM synthesis round-trip compared to default AgentTool",
        hops["transfer_to_agent"].llm_calls == 2
        and hops["agent_tool_default"].llm_calls == 3
        and hops["workflow_edge"].llm_calls == 1
        and len(handoff_coord.sub_agents) == 1
        and len(tool_coord.tools) == 1,
    )

    report.summary()
    return report


def run_live(config) -> None:
    banner("Lab 08 — ADK Fundamentals (Live)", f"Project: {config.project_id}")
    run_offline()
    section("Live InMemoryRunner Execution")
    from google.genai import types

    agent = LlmAgent(
        name="LiveExtractor",
        model=Gemini(model=DEFAULT_FAST_MODEL),
        instruction="Extract order_id and issue_type.",
        output_schema=TicketEntities,
        output_key="entities",
    )
    runner = InMemoryRunner(agent=agent, app_name="lab08_live")

    async def _exec() -> None:
        sess = await runner.session_service.create_session(app_name="lab08_live", user_id="u1")
        msg = types.Content(
            role="user",
            parts=[types.Part.from_text(text="Order ORD-9921 arrived with a cracked screen.")],
        )
        async for event in runner.run_async(user_id="u1", session_id=sess.id, new_message=msg):
            if event.is_final_response() and event.content and event.content.parts:
                step(1, f"Structured output: {event.content.parts[0].text}")

    asyncio.run(_exec())


if __name__ == "__main__":
    cfg = load_config(sys.argv[1:])
    if require_live(cfg):
        run_live(cfg)
    else:
        result = run_offline()
        sys.exit(0 if result.passed else 1)
