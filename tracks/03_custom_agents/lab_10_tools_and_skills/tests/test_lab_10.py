import pytest
from google.adk.tools import (
    FunctionTool,
    LongRunningFunctionTool,
    request_input,
    get_user_choice,
    exit_loop,
    transfer_to_agent,
    MCPToolset,
)
from google.adk.skills import (
    Skill,
    Frontmatter,
    SkillRegistry,
    load_skills_from_dir,
    load_skill_from_gcs_dir,
)
from google.adk.integrations.skill_registry import GCPSkillRegistry
from google.adk.agents import LlmAgent
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG


def test_tools_exist():
    assert FunctionTool
    assert LongRunningFunctionTool
    assert request_input.name
    assert get_user_choice.name
    assert exit_loop.__name__
    assert transfer_to_agent.__name__
    assert MCPToolset

def test_skills_exist():
    assert Skill
    assert Frontmatter
    assert SkillRegistry
    assert callable(load_skills_from_dir)
    assert callable(load_skill_from_gcs_dir)

def test_gcp_skill_registry():
    registry = GCPSkillRegistry(
        project_id="test",
        location="us-central1",
        credentials=None
    )
    assert isinstance(registry, SkillRegistry)
    assert registry.project_id == "test"

def test_frontmatter_fields():
    fm = Frontmatter(
        name="test-skill",
        description="test",
        allowed_tools="tool1"
    )
    assert fm.allowed_tools == "tool1"

def test_agent_tools_binding():
    def my_tool():
        pass
    
    agent = LlmAgent(
        name="Test",
        model=DEFAULT_AGENT_MODEL,
        instruction="test",
        tools=[FunctionTool(func=my_tool), request_input]
    )
    assert len(agent.tools) == 2
    names = [t.name for t in agent.tools]
    assert "my_tool" in names
    assert request_input.name in names

def test_uses_only_verified_models():
    assert DEFAULT_AGENT_MODEL in MODEL_CATALOG
