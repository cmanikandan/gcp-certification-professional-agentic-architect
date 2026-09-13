import pytest
from common.models import EMBEDDING_MODELS, DEFAULT_EMBEDDING_MODEL

def test_uses_only_verified_models():
    assert DEFAULT_EMBEDDING_MODEL in EMBEDDING_MODELS
    assert EMBEDDING_MODELS[DEFAULT_EMBEDDING_MODEL] == 8192

def test_adk_memory_imports():
    from google.adk.memory import VertexAiRagMemoryService
    svc = VertexAiRagMemoryService(rag_corpus="abc")
    assert hasattr(svc, "add_memory")
    assert hasattr(svc, "search_memory")

def test_cosine_similarity():
    import importlib
    lab = importlib.import_module("tracks.03_custom_agents.lab_11_rag_and_retrieval.lab")
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert lab.cosine_similarity(v1, v2) == 1.0
    assert lab.cosine_similarity(v1, v3) == 0.0
