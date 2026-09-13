import pytest
from pydantic import BaseModel
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models import Gemini
from google.adk.workflow import Workflow, FunctionNode, START
from common.models import DEFAULT_AGENT_MODEL

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
        include_contents="default"
    )
    assert agent.name == "TestAgent"
    assert agent.output_key == "test_result"
    assert agent.output_schema == DummySchema
    assert agent.include_contents == "default"
    
def test_sequential_agent_structure():
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    agent1 = LlmAgent(name="A1", model=model)
    agent2 = LlmAgent(name="A2", model=model)
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


def test_workflow_structure():
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    agent = LlmAgent(name="A1", model=model)
    from google.adk.workflow import Edge

    wf = Workflow(
        name="TestWF",
        state_schema=DummySchema,
        edges=[Edge(from_node=START, to_node=agent)],
    )

    # The graph stores nodes, not the agent objects you passed in, so compare by
    # name rather than identity.
    node_names = [node.name for node in wf.graph.nodes]
    assert "A1" in node_names
    assert any("START" in name for name in node_names), node_names

