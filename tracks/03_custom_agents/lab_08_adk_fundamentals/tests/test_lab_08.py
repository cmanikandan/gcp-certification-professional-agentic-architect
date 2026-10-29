import warnings
import pytest
from pydantic import BaseModel, ValidationError

import lab
from common.models import DEFAULT_AGENT_MODEL
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models import Gemini
from google.adk.tools import exit_loop
from google.adk.workflow import Edge, START, Workflow


class DummySchema(BaseModel):
    name: str


def test_llm_agent_structure():
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    agent = LlmAgent(
        name="TestAgent",
        model=model,
        instruction="You are a test agent.",
        output_schema=DummySchema,
        output_key="test_result",
        include_contents="default",
    )
    assert agent.name == "TestAgent"
    assert agent.output_key == "test_result"
    assert agent.output_schema == DummySchema
    assert agent.include_contents == "default"


def test_sequential_agent_structure():
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    agent1 = LlmAgent(name="A1", model=model)
    agent2 = LlmAgent(name="A2", model=model)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        seq = SequentialAgent(name="Seq", sub_agents=[agent1, agent2])
    assert len(seq.sub_agents) == 2
    assert seq.sub_agents[0].name == "A1"


def test_sequential_agent_is_superseded_but_still_functional():
    """Exam-relevant: the workflow agents still work, but ADK now steers you to Workflow.

    Knowing which of the two a question is really about matters, so pin the
    actual behaviour rather than trusting either 'removed' or 'unchanged'.
    """
    model = Gemini(model=DEFAULT_AGENT_MODEL)

    with pytest.warns(DeprecationWarning, match="Workflow"):
        seq = SequentialAgent(
            name="Seq",
            sub_agents=[LlmAgent(name="A1", model=model)],
        )

    # Deprecated, but emphatically not gone: it still builds and still runs.
    assert seq.name == "Seq"
    assert len(seq.sub_agents) == 1

    # Verify the second half of the deprecation nuance: Workflow cannot yet be nested in sub_agents.
    wf = Workflow(
        name="NestedWF",
        edges=[Edge(from_node=START, to_node=LlmAgent(name="Leaf", model=model))],
    )
    with pytest.raises(ValidationError):
        LlmAgent(name="Parent", model=model, sub_agents=[wf])  # type: ignore[list-item]


def test_workflow_structure():
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    agent = LlmAgent(name="A1", model=model)

    wf = Workflow(
        name="TestWF",
        state_schema=DummySchema,
        edges=[Edge(from_node=START, to_node=agent)],
    )

    node_names = [node.name for node in wf.graph.nodes]
    assert "A1" in node_names
    assert any("START" in name for name in node_names), node_names


def test_token_hygiene_and_parallel_join_latency_math():
    pipeline = lab.build_token_hygiene_pipeline()
    assert pipeline.sub_agents[0].output_key == "entities"
    assert pipeline.sub_agents[1].include_contents == "none"

    wf = lab.build_parallel_support_workflow()
    names = {n.name for n in wf.graph.nodes}
    assert {"OrderStatusWorker", "BillingHistoryWorker", "ShippingPolicyWorker", "SupportContextBarrier", "ResolutionDrafter", "ApprovalGate"}.issubset(names)

    lat = lab.compute_support_fanout_comparison([420, 510, 380], synthesis_ms=450)
    assert lat["parallel_ms"] == 960
    assert lat["sequential_ms"] == 1760

    loop = lab.build_bounded_refinement_loop(max_iterations=3)
    assert loop.max_iterations == 3
    assert exit_loop in loop.sub_agents[0].tools

    hops = lab.compute_delegation_hops(router_ms=200, specialist_ms=500, parent_synthesis_ms=300)
    assert hops["workflow_edge"].llm_calls == 1
    assert hops["transfer_to_agent"].llm_calls == 2
    assert hops["agent_tool_default"].llm_calls == 3
    assert hops["agent_tool_default"].total_latency_ms > hops["transfer_to_agent"].total_latency_ms


def test_offline_report_passes():
    report = lab.run_offline()
    assert report.passed
