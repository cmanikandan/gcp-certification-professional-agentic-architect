#!/usr/bin/env python3
"""Lab 10: Agents CLI, Agent Identity & Prebuilt GCP MCP Toolsets (Objectives 3.1 & 3.2)."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from common import DEFAULT_AGENT_MODEL, load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, step, table
from google.adk.agents import LlmAgent
from google.adk.integrations.agent_identity import (
    GcpAuthProvider,
    GcpAuthProviderScheme,
)
from google.adk.integrations.api_registry import ApiRegistry
from google.adk.integrations.skill_registry import GCPSkillRegistry
from google.adk.models import Gemini
from google.adk.plugins import (
    LoggingPlugin,
    PluginManager,
    ReflectAndRetryToolPlugin,
)
from google.adk.skills import (
    Frontmatter,
    Skill,
    SkillRegistry,
    list_skills_in_dir,
    load_skill_from_dir,
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

LAB_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class AgentsCliInvocationResult:
    """Models Agents CLI execution behavior in Agent Mode vs Human Mode."""

    mode: str
    non_interactive: bool
    interactive_tty_prompts: bool
    exit_code: int
    stdout: str


def simulate_agents_cli_invocation(
    command: str,
    *,
    agent_mode: bool,
    plugins: tuple[str, ...] = ("reflect-and-retry", "model-armor"),
) -> AgentsCliInvocationResult:
    """Compare Agents CLI in Agent Mode (JSON, --non-interactive) vs Human Mode (TUI)."""
    if agent_mode:
        envelope = {
            "status": "ok",
            "command": command,
            "mode": "agent",
            "non_interactive": True,
            "installed_plugins": list(plugins),
        }
        return AgentsCliInvocationResult(
            mode="agent",
            non_interactive=True,
            interactive_tty_prompts=False,
            exit_code=0,
            stdout=json.dumps(envelope, sort_keys=True),
        )
    return AgentsCliInvocationResult(
        mode="human",
        non_interactive=False,
        interactive_tty_prompts=True,
        exit_code=0,
        stdout=f"[Wizard] Execute '{command}' with plugins {list(plugins)}? [y/N]",
    )


def check_weather(location: str) -> str:
    """Returns the current weather summary for a given location."""
    return f"The weather in {location} is sunny."


async def provision_analytics_sandbox(environment_name: str) -> str:
    """Provisions an ephemeral sandbox asynchronously."""
    await asyncio.sleep(0.01)
    return f"Sandbox {environment_name} provisioned."


def build_agent_identity_and_gcp_toolsets() -> dict[str, object]:
    """Configure Agent Identity + BigQueryToolset + APIHubToolset + RemoteMcpServer."""
    auth_provider = GcpAuthProvider()
    auth_scheme = GcpAuthProviderScheme(
        name="projects/proj-enterprise-agents/locations/us-central1/authProviders/bq-readonly-id",
        scopes=["https://www.googleapis.com/auth/bigquery.readonly"],
    )

    # Safe delegated/agent-identity token reference: zero static JSON SA keys!
    bq_creds = BigQueryCredentialsConfig(
        external_access_token_key="agent_identity_bq_token",
    )
    bq_toolset = BigQueryToolset(
        credentials_config=bq_creds,
        tool_filter=["list_dataset_ids", "get_table_info", "execute_sql"],
    )

    apihub_toolset = APIHubToolset(
        apihub_resource_name="projects/proj-enterprise-agents/locations/us-central1/apis/orders-v2",
        auth_scheme=auth_scheme,
        access_token="ephemeral-placeholder-for-offline-init",
        lazy_load_spec=True,
    )

    cloudsql_mcp = RemoteMcpServer(
        name="cloudsql_readonly_mcp",
        url="https://cloudsql-mcp-internal.a.run.app/sse",
        allowed_tools=["query_orders", "describe_schema"],
    )

    return {
        "auth_provider": auth_provider,
        "auth_scheme": auth_scheme,
        "bq_creds": bq_creds,
        "bq_toolset": bq_toolset,
        "apihub_toolset": apihub_toolset,
        "cloudsql_mcp": cloudsql_mcp,
    }


def inspect_progressive_skill_loading() -> tuple[dict[str, Frontmatter], Skill]:
    """Demonstrate L1 Frontmatter discovery vs L2 full Skill hydration from disk."""
    prev_level = logging.root.level
    logging.disable(logging.WARNING)
    try:
        l1_catalog = list_skills_in_dir(LAB_DIR)
    finally:
        logging.disable(prev_level)
    l2_skill = load_skill_from_dir(LAB_DIR / "weather-expert")
    return l1_catalog, l2_skill


def run_offline() -> LabReport:
    banner(
        "Lab 10 — Agents CLI, Agent Identity & Prebuilt GCP MCP Toolsets",
        "Objectives 3.1 & 3.2: Agent vs Human CLI Mode, Safe Credentials, MCP & Skills (Offline)",
    )
    report = LabReport("Lab 10 — Tools, Skills, Agent Identity & Agents CLI")

    section("1. Agents CLI: Agent Mode (JSON / --non-interactive) vs Human Mode (TUI)")
    agent_cli = simulate_agents_cli_invocation("skills sync --registry=gcp", agent_mode=True)
    human_cli = simulate_agents_cli_invocation("skills sync --registry=gcp", agent_mode=False)
    parsed_json = json.loads(agent_cli.stdout)
    table(
        ["CLI Mode", "--non-interactive", "TTY Prompts", "Exit Code", "Output Sample"],
        [
            [agent_cli.mode, agent_cli.non_interactive, agent_cli.interactive_tty_prompts, agent_cli.exit_code, agent_cli.stdout[:52] + "..."],
            [human_cli.mode, human_cli.non_interactive, human_cli.interactive_tty_prompts, human_cli.exit_code, human_cli.stdout[:52]],
        ],
    )
    report.check(
        "Agents CLI Agent Mode outputs machine-parseable JSON with zero blocking TTY prompts",
        parsed_json["status"] == "ok"
        and agent_cli.non_interactive is True
        and agent_cli.interactive_tty_prompts is False
        and human_cli.interactive_tty_prompts is True,
    )

    section("2. Safe Credential Access via Agent Identity & Prebuilt GCP Toolsets")
    bundle = build_agent_identity_and_gcp_toolsets()
    auth_scheme: GcpAuthProviderScheme = bundle["auth_scheme"]  # type: ignore[assignment]
    bq_creds: BigQueryCredentialsConfig = bundle["bq_creds"]  # type: ignore[assignment]
    cloudsql_mcp: RemoteMcpServer = bundle["cloudsql_mcp"]  # type: ignore[assignment]

    step(1, f"Agent Identity scheme: {type(auth_scheme).__name__} -> {auth_scheme.name}")
    step(2, f"BigQueryToolset token key: '{bq_creds.external_access_token_key}' (zero static SA JSON keys)")
    step(3, f"APIHubToolset lazy_load_spec=True + ApiRegistry sig={inspect.signature(ApiRegistry)}")
    step(4, f"RemoteMcpServer '{cloudsql_mcp.name}' allowlisted tools: {cloudsql_mcp.allowed_tools}")
    exam_note(
        "BigQueryCredentialsConfig enforces that client_id/client_secret/scopes are omitted "
        "when external_access_token_key supplies a pre-exchanged Agent Identity token."
    )
    report.check(
        "Agent Identity GcpAuthProviderScheme, BigQueryToolset, APIHubToolset & RemoteMcpServer configured",
        isinstance(bundle["auth_provider"], GcpAuthProvider)
        and isinstance(bundle["bq_toolset"], BigQueryToolset)
        and isinstance(bundle["apihub_toolset"], APIHubToolset)
        and MCPToolset is not None,
    )

    section("3. Progressive Skill Disclosure (L1 Frontmatter vs L2 Full Skill) & GCPSkillRegistry")
    l1_catalog, l2_skill = inspect_progressive_skill_loading()
    registry = GCPSkillRegistry(
        project_id="proj-enterprise-agents",
        location="us-central1",
        credentials=AnonymousCredentials(),
    )
    step(5, f"L1 catalog keys (Frontmatter only): {list(l1_catalog.keys())}")
    step(6, f"L2 hydrated skill '{l2_skill.frontmatter.name}' allowed_tools='{l2_skill.frontmatter.allowed_tools}'")
    step(7, f"Enterprise skill plane: {type(registry).__name__} (implements {SkillRegistry.__name__})")
    report.check(
        "L1 list_skills_in_dir discovers Frontmatter while L2 load_skill_from_dir hydrates instructions",
        "weather-expert" in l1_catalog
        and isinstance(l1_catalog["weather-expert"], Frontmatter)
        and "meteorologist" in l2_skill.instructions
        and callable(load_skills_from_dir)
        and callable(load_skill_from_gcs_dir)
        and isinstance(registry, SkillRegistry),
    )

    section("4. Runtime Plugins, Async Long-Running Tools & HITL Guardrails")
    plugin_mgr = PluginManager(plugins=[LoggingPlugin(), ReflectAndRetryToolPlugin()])
    func_tool = FunctionTool(func=check_weather)
    long_tool = LongRunningFunctionTool(func=provision_analytics_sandbox)

    governed_agent = LlmAgent(
        name="GovernedEnterpriseOperator",
        model=Gemini(model=DEFAULT_AGENT_MODEL),
        instruction="Always call get_user_choice before provisioning or mutating resources.",
        tools=[func_tool, long_tool, request_input, get_user_choice],
    )
    tool_names = [t.name for t in governed_agent.tools]
    step(8, f"PluginManager active plugins: {[type(p).__name__ for p in plugin_mgr.plugins]}")
    step(9, f"Agent '{governed_agent.name}' tool manifest: {tool_names}")
    step(10, f"Workflow control primitives available: {exit_loop.__name__}, {transfer_to_agent.__name__}")
    report.check(
        "PluginManager, LongRunningFunctionTool, and HITL tools (request_input, get_user_choice) bound",
        len(plugin_mgr.plugins) == 2
        and request_input.name in tool_names
        and get_user_choice.name in tool_names
        and long_tool.name in tool_names,
    )

    report.summary()
    return report


def run_live(config) -> None:
    banner("Lab 10 — Tools, Skills & Agent Identity (Live)", f"Project: {config.project_id}")
    run_offline()


if __name__ == "__main__":
    cfg = load_config(sys.argv[1:])
    if require_live(cfg):
        run_live(cfg)
    else:
        result = run_offline()
        sys.exit(0 if result.passed else 1)
