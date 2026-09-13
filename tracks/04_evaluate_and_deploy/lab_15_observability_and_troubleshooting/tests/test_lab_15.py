import sys
import os
from common.models import MODEL_CATALOG

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import agent

def test_uses_only_verified_models():
    assert agent.root_agent.model in MODEL_CATALOG

def test_agent_tools_exist():
    assert len(agent.root_agent.tools) > 0
    assert agent.root_agent.tools[0].__name__ == "mock_flaky_tool"

def test_mock_tool_fails():
    import pytest
    with pytest.raises(ValueError, match="Simulated tool failure"):
        agent.mock_flaky_tool("make it fail")
