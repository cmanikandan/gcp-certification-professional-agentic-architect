#!/usr/bin/env python3
"""Lab 10: Tools and Skills."""
import sys
import asyncio
from common import DEFAULT_AGENT_MODEL, load_config, require_live

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
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
    load_skills_from_dir,
    load_skill_from_gcs_dir,
    SkillRegistry,
)
from google.adk.integrations.skill_registry import GCPSkillRegistry


# 1. Plain Python Function Tool
def check_weather(location: str) -> str:
    """Returns the weather for a given location."""
    return f"The weather in {location} is sunny."


# 2. LongRunningFunctionTool
async def provision_server(hostname: str) -> str:
    """Provisions a server in the background."""
    await asyncio.sleep(0.1) # simulate work
    return f"Server {hostname} provisioned."

long_running_tool = LongRunningFunctionTool(
    func=provision_server
)


def run_offline():
    print("Running Lab 10 OFFLINE: Tools and Skills")

    # --- TOOLS ---
    print("\n--- Tool Taxonomy ---")
    
    print("1. Standard Function Tool:")
    func_tool = FunctionTool(func=check_weather)
    print(f"   Created {func_tool.__class__.__name__} from python func: {func_tool.name}")
    
    print("\n2. Long Running Tool:")
    print(f"   Created {long_running_tool.__class__.__name__} for async work.")
    
    print("\n3. HITL (Human-In-The-Loop) Primitives:")
    print(f"   - {request_input.name}: Ask human for open-text input.")
    print(f"   - {get_user_choice.name}: Ask human to select from options.")
    
    print("\n4. Built-in workflow tools:")
    print(f"   - {exit_loop.__name__}: Terminate a LoopAgent.")
    print(f"   - {transfer_to_agent.__name__}: Agent-as-a-tool handoff.")
    
    # We could theoretically instantiate MCPToolset here, but it takes actual client configurations
    print("\n5. MCP Toolsets: MCPToolset and RemoteMcpServer are available.")

    # Let's attach some of these to a real LlmAgent
    agent = LlmAgent(
        name="SysAdmin",
        model=Gemini(model=DEFAULT_AGENT_MODEL),
        instruction="You are a helpful admin.",
        tools=[func_tool, long_running_tool, request_input, get_user_choice]
    )
    
    print(f"\n--- Agent Manifest ---")
    print(f"Agent '{agent.name}' resolved tool manifest:")
    for t in agent.tools:
        print(f" - {t.name}")


    # --- SKILLS ---
    print("\n--- Skill Registry ---")
    
    # A skill is a governed bundle
    fm = Frontmatter(
        name="networking-basics",
        description="Standard networking tools",
        allowed_tools="ping, traceroute"
    )
    skill = Skill(frontmatter=fm, instructions="You are a network expert.")
    
    print(f"Created a {skill.__class__.__name__} object with allowed_tools: {skill.frontmatter.allowed_tools}")
    
    print(f"Functions available to load skills dynamically:")
    print(f" - load_skills_from_dir")
    print(f" - load_skill_from_gcs_dir")
    
    # GCPSkillRegistry implementation
    registry = GCPSkillRegistry(
        project_id="dummy-project",
        location="us-central1",
        credentials=None
    )
    print(f"Instantiated {registry.__class__.__name__} (implements {SkillRegistry.__name__})")
    print(f"   project_id: {registry.project_id}")
    

def run_live(config):
    print("Running Lab 10 LIVE")
    run_offline()


if __name__ == "__main__":
    config = load_config(sys.argv[1:])
    if require_live(config):
        run_live(config)
    else:
        run_offline()
