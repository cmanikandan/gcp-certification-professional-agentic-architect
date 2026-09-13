import os
import sys
from unittest.mock import patch, AsyncMock
from google.adk import Agent
from google.adk.tools import McpToolset
from mcp.client.stdio import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from common.models import DEFAULT_AGENT_MODEL

def test_mcp_toolset_initialization():
    """Verify that ADK's McpToolset correctly encapsulates stdio parameters."""
    server_script = "fake_server.py"
    params = StdioConnectionParams(
        server_params=StdioServerParameters(command="python", args=[server_script])
    )
    toolset = McpToolset(connection_params=params)
    
    assert isinstance(toolset, McpToolset)
    assert toolset.connection_params.server_params.command == "python"
    assert server_script in toolset.connection_params.server_params.args

def test_agent_with_mcp_toolset():
    """Verify that an Agent accepts the McpToolset correctly in its tools list."""
    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(command="echo", args=["{}"])
        )
    )
    agent = Agent(name="test_agent", model=DEFAULT_AGENT_MODEL, tools=[toolset])
    
    assert agent.name == "test_agent"
    assert toolset in agent.tools

def test_uses_only_verified_models():
    """Contract test: must only use verified models."""
    from common.models import MODEL_CATALOG
    
    agent = Agent(name="test_agent", model=DEFAULT_AGENT_MODEL)
    assert agent.model in MODEL_CATALOG
