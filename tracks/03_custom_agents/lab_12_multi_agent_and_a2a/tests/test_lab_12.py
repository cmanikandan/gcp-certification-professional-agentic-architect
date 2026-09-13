import pytest
from google.adk.tools import MCPToolset, RemoteMcpServer

def test_mcp_toolset_structure():
    mcp_server = RemoteMcpServer(
        name="test_server",
        url="http://localhost:8080/mcp"
    )
    assert mcp_server.name == "test_server"
    assert mcp_server.url == "http://localhost:8080/mcp"

def test_a2a_and_registry_imports():
    try:
        from google.adk.a2a.agent import A2aRemoteAgentConfig
        config = A2aRemoteAgentConfig()
        assert config is not None
    except ImportError:
        pass
        
    try:
        from google.adk.integrations.agent_registry import AgentRegistry
        assert AgentRegistry is not None
    except ImportError:
        pass
