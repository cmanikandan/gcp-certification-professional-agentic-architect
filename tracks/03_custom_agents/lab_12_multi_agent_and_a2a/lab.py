#!/usr/bin/env python3
"""Lab 12: Multi-Agent and A2A."""
import sys
from common import load_config, require_live

try:
    from google.adk.integrations.agent_registry import AgentRegistry
    has_registry = True
except ImportError:
    has_registry = False

try:
    from google.adk.a2a.agent import A2aRemoteAgentConfig
    has_a2a = True
except ImportError:
    has_a2a = False

from google.adk.tools import MCPToolset, RemoteMcpServer

def run_offline():
    print("Running Lab 12 OFFLINE: Multi-Agent and A2A")
    
    # 1. MCP Toolset (Agent-to-Tool)
    print("\n--- MCP (Agent-to-Tool) ---")
    mcp_server = RemoteMcpServer(
        name="weather_server",
        url="http://localhost:8080/mcp"
    )
    print(f"Defined {mcp_server.__class__.__name__} configuration.")
    print("MCP is used when an agent needs to invoke remote capabilities (tools) securely.")
    print("In ADK, an McpToolset connects to these remote servers.")

    # 2. A2A (Agent-to-Agent)
    print("\n--- A2A (Agent-to-Agent) ---")
    if has_a2a:
        a2a_config = A2aRemoteAgentConfig()
        print(f"Created {a2a_config.__class__.__name__}.")
        print("A2A is used when an agent needs to delegate reasoning to another intelligent agent.")
    else:
        print("google.adk.a2a is not installed. Needs google-adk[a2a] extra.")

    # 3. Agent Registry (Discovery)
    print("\n--- Agent Registry (Discovery) ---")
    if has_registry:
        # In a real setup, you'd pass project_id and location.
        # registry = AgentRegistry(project_id="my-project", location="us-central1")
        # a2a_agent = registry.get_remote_a2a_agent(agent_id="security-reviewer")
        # mcp_tools = registry.get_mcp_toolset(server_id="internal-db-mcp")
        print("AgentRegistry module is available.")
        print("You would use AgentRegistry.get_remote_a2a_agent(...) to find agents,")
        print("and AgentRegistry.get_mcp_toolset(...) to find tools without hardcoding endpoints.")
    else:
        print("AgentRegistry module is NOT available. Needs google-adk[agent-identity] extra.")


def run_live(config):
    print("Running Lab 12 LIVE")
    run_offline()


if __name__ == "__main__":
    config = load_config(sys.argv[1:])
    if require_live(config):
        run_live(config)
    else:
        run_offline()
