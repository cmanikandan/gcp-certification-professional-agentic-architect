import sys
import os
import pytest
import importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from common.models import MODEL_CATALOG
lab = importlib.import_module("tracks.05_secure_and_govern.lab_17_model_armor_and_hitl.lab")

def test_uses_only_verified_models():
    assert lab.MODEL in MODEL_CATALOG

def test_has_model_armor():
    assert lab.HAS_GCP_EXTRA, "The google-adk[gcp] extra must be installed"

def test_model_armor_config():
    if not lab.HAS_GCP_EXTRA:
        pytest.skip("GCP extra not installed")
        
    from google.adk.integrations.model_armor import ModelArmorConfig
    
    config = ModelArmorConfig(
        prompt_template_name="projects/test/locations/us-central1/templates/test",
        block_on_screening_failure=True
    )
    
    assert config.prompt_template_name == "projects/test/locations/us-central1/templates/test"
    assert config.block_on_screening_failure is True
