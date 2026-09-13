import pytest
from google.adk.sessions import (
    InMemorySessionService,
    VertexAiSessionService,
    DatabaseSessionService,
)
from google.adk.memory import (
    InMemoryMemoryService,
    VertexAiMemoryBankService,
    VertexAiRagMemoryService,
)
from google.adk.integrations.redis import (
    RedisSessionService,
    RedisSessionServiceConfig,
)
from google.adk.tools import load_memory, preload_memory
from google.adk.agents import LlmAgent
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG


def test_session_services_exist():
    assert InMemorySessionService
    assert VertexAiSessionService
    assert DatabaseSessionService(db_url="sqlite+aiosqlite:///:memory:")
    assert RedisSessionService
    
def test_redis_config_fields():
    config = RedisSessionServiceConfig(
        uri="redis://localhost",
        host="localhost",
        port=6379,
        password="pass",
        ssl=False,
        db=1,
        ttl_seconds=120,
        key_prefix="test"
    )
    assert config.host == "localhost"
    assert config.key_prefix == "test"

def test_memory_services_exist():
    assert InMemoryMemoryService
    assert VertexAiMemoryBankService
    assert VertexAiRagMemoryService

def test_memory_tools_exist():
    assert load_memory.name
    assert preload_memory.name

def test_uses_only_verified_models():
    assert DEFAULT_AGENT_MODEL in MODEL_CATALOG

def test_agent_state_schema_binding():
    from pydantic import BaseModel
    class AppState(BaseModel):
        val: str | None = None
        
    class OutState(BaseModel):
        val: str
        
    agent = LlmAgent(
        name="Test",
        model=DEFAULT_AGENT_MODEL,
        instruction="test",
        state_schema=AppState,
        output_schema=OutState,
        output_key="val"
    )
    assert agent.output_key == "val"
    assert agent.state_schema == AppState
