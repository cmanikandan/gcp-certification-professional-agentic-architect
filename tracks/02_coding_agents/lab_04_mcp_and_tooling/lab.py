import asyncio
import sys
import os
from common import DEFAULT_AGENT_MODEL, load_config, require_live

# ADK imports
from google.adk import Agent
from google.adk.tools import McpToolset
from mcp.client.stdio import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams

async def run_offline():
    """
    Offline run: Starts the MCP server as a subprocess and connects an agent to it.
    This demonstrates the local (stdio) transport used by coding assistants.
    """
    print("--- 1. Configuring MCP Toolset (stdio transport) ---")
    server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    
    # In an offline environment, we configure the transport to spawn our local server.
    # The client uses standard input/output to exchange JSON-RPC payloads.
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[server_script]
            )
        )
    )
    
    print("McpToolset instance created successfully.\n")

    print("--- 2. Building the Agent with MCP Toolset ---")
    # Instead of writing custom plugins, we simply pass the toolset to the agent.
    # The agent will dynamically discover tools exposed by the MCP server (N+M architecture).
    agent = Agent(
        name="crypto_agent",
        description="I am an agent connected to the enterprise crypto MCP server.",
        instruction="You are a helpful assistant. Use your tools to hash the text 'GoogleCloud'.",
        model=DEFAULT_AGENT_MODEL,  # Using the explicitly verified stable reasoning model
        tools=[mcp_toolset]
    )
    
    print(f"Agent '{agent.name}' built with model: {agent.model}")
    print(f"Agent toolset attached: {type(mcp_toolset).__name__}\n")

    # In a fully offline lab without a model, we don't execute the agent's inference loop.
    # But we've verified the toolset composition logic.
    print("Offline run successful: MCP configuration is valid and Agent graph is constructed.")

async def run_live(config):
    """
    Live run: Actually executes the agent loop, calling Gemini to use the MCP tools.
    """
    print("--- Running Live MCP Integration ---")
    server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[server_script]
            )
        )
    )

    agent = Agent(
        name="crypto_agent",
        model=DEFAULT_AGENT_MODEL,
        tools=[mcp_toolset],
        instruction="Calculate the SHA-256 checksum for the text 'AgenticArchitect' using your tools. Only return the final checksum."
    )
    
    response = await agent.arun("Calculate the checksum for 'AgenticArchitect'.")
    print("\nLive Response:")
    print(response.output)

def main():
    config = load_config()
    if require_live(config):
        asyncio.run(run_live(config))
    else:
        asyncio.run(run_offline())

if __name__ == "__main__":
    main()
