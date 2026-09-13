import pytest
from common.models import DEFAULT_AGENT_MODEL, DEFAULT_OSS_MODEL, MODEL_CATALOG, select_model
from google.adk.models import Gemini, Gemma, FallbackModel

def test_uses_only_verified_models():
    # Assert that all scenarios return models in our verified catalog
    models_to_test = [
        select_model(data_cannot_leave_premises=True)[0],
        select_model(high_volume_simple_task=True)[0],
        select_model(needs_deep_reasoning=True, requires_ga_only=True)[0]
    ]
    for model_id in models_to_test:
        assert model_id in MODEL_CATALOG

def test_adk_model_instantiation():
    # Verify the ADK model classes exist and initialize correctly
    gemma_model = Gemma(model=DEFAULT_OSS_MODEL)
    assert gemma_model.model == DEFAULT_OSS_MODEL
    
    gemini_model = Gemini(model=DEFAULT_AGENT_MODEL)
    assert gemini_model.model == DEFAULT_AGENT_MODEL
    
    fallback = FallbackModel(models=[gemini_model, gemma_model])
    assert fallback.models[0] == gemini_model
    assert fallback.models[1] == gemma_model
