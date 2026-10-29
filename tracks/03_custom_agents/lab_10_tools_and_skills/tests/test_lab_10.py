import json
import pytest
from pydantic import ValidationError

import lab
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG
from google.adk.agents import LlmAgent
from google.adk.integrations.agent_identity import (
    GcpAuthProvider,
    GcpAuthProviderScheme,
)
from google.adk.integrations.skill_registry import GCPSkillRegistry
from google.adk.skills import (
    Frontmatter,
    Skill,
    SkillRegistry,
    load_skill_from_gcs_dir,
    load_skills_from_dir,
)
from google.adk.tools import (
    APIHubToolset,
    FunctionTool,
    LongRunningFunctionTool,
    MCPToolset,
    RemoteMcpServer,
    exit_loop,
    get_user_choice,
    request_input,
    transfer_to_agent,
)
from google.adk.integrations.bigquery import (
    BigQueryCredentialsConfig,
    BigQueryToolset,
)
from google.auth.credentials import AnonymousCredentials


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
        credentials=AnonymousCredentials(),
    )
    assert isinstance(registry, SkillRegistry)
    assert registry.project_id == "test"


def test_frontmatter_fields():
    fm = Frontmatter(
        name="test-skill",
        description="test",
        allowed_tools="tool1",
    )
    assert fm.allowed_tools == "tool1"


def test_agent_tools_binding():
    def my_tool():
        pass

    agent = LlmAgent(
        name="Test",
        model=DEFAULT_AGENT_MODEL,
        instruction="test",
        tools=[FunctionTool(func=my_tool), request_input],
    )
    assert len(agent.tools) == 2
    names = [t.name for t in agent.tools]
    assert "my_tool" in names
    assert request_input.name in names


def test_uses_only_verified_models():
    assert DEFAULT_AGENT_MODEL in MODEL_CATALOG


def test_agents_cli_agent_vs_human_mode():
    agent_res = lab.simulate_agents_cli_invocation("eval run", agent_mode=True)
    human_res = lab.simulate_agents_cli_invocation("eval run", agent_mode=False)

    payload = json.loads(agent_res.stdout)
    assert payload["mode"] == "agent"
    assert payload["non_interactive"] is True
    assert agent_res.interactive_tty_prompts is False
    assert human_res.interactive_tty_prompts is True


def test_agent_identity_and_bigquery_credentials_validation():
    bundle = lab.build_agent_identity_and_gcp_toolsets()
    assert isinstance(bundle["auth_provider"], GcpAuthProvider)
    assert isinstance(bundle["auth_scheme"], GcpAuthProviderScheme)
    assert isinstance(bundle["bq_toolset"], BigQueryToolset)
    assert isinstance(bundle["apihub_toolset"], APIHubToolset)
    assert isinstance(bundle["cloudsql_mcp"], RemoteMcpServer)

    # Pin ADK validation rule: external_access_token_key cannot be mixed with scopes/client_secret.
    with pytest.raises(ValidationError):
        BigQueryCredentialsConfig(
            external_access_token_key="delegated_tok",
            scopes=["https://www.googleapis.com/auth/bigquery.readonly"],
        )


def test_l1_vs_l2_progressive_skill_loading():
    l1_catalog, l2_skill = lab.inspect_progressive_skill_loading()
    assert "weather-expert" in l1_catalog
    assert isinstance(l1_catalog["weather-expert"], Frontmatter)
    assert isinstance(l2_skill, Skill)
    assert "meteorologist" in l2_skill.instructions


def test_offline_report_passes():
    report = lab.run_offline()
    assert report.passed
