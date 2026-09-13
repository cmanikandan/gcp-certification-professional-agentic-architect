import sys
import os
import pytest
import importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from common.models import MODEL_CATALOG
lab = importlib.import_module("tracks.05_secure_and_govern.lab_18_governance_gateway_registry.lab")

def test_uses_only_verified_models():
    assert lab.MODEL in MODEL_CATALOG

def test_has_agent_registry():
    assert lab.HAS_REGISTRY, "The google-adk[agent-identity] extra must be installed"

def test_agent_registry_methods():
    if not lab.HAS_REGISTRY:
        pytest.skip("Registry not installed")
        
    from google.adk.integrations.agent_registry import AgentRegistry
    
    methods = dir(AgentRegistry)
    assert "list_agents" in methods
    assert "get_mcp_toolset" in methods
    assert "get_remote_a2a_agent" in methods
    assert "list_endpoints" in methods
