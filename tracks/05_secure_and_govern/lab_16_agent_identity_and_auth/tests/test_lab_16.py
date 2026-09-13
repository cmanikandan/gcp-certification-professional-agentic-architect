import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from common.models import MODEL_CATALOG
import importlib
lab = importlib.import_module("tracks.05_secure_and_govern.lab_16_agent_identity_and_auth.lab")

def test_uses_only_verified_models():
    assert lab.MODEL in MODEL_CATALOG

def test_has_agent_identity():
    assert lab.HAS_AGENT_IDENTITY, "The google-adk[agent-identity] extra must be installed"

def test_gcp_auth_provider_scheme_instantiation():
    if not lab.HAS_AGENT_IDENTITY:
        pytest.skip("Agent Identity not installed")
        
    from google.adk.integrations.agent_identity import GcpAuthProviderScheme
    
    scheme = GcpAuthProviderScheme(
        name="projects/test/locations/us-central1/connectors/test",
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    
    assert scheme.type_ == "gcpAuthProviderScheme"
    assert scheme.name == "projects/test/locations/us-central1/connectors/test"
    assert "https://www.googleapis.com/auth/cloud-platform" in scheme.scopes
