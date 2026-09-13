import sys
import os
from common.models import MODEL_CATALOG

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import agent

def test_uses_only_verified_models():
    assert agent.AGENT_MODEL in MODEL_CATALOG

def test_dockerfile_exists():
    dockerfile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Dockerfile")
    assert os.path.exists(dockerfile_path)
    with open(dockerfile_path, "r") as f:
        content = f.read()
    assert "adk" in content
    assert "api_server" in content
