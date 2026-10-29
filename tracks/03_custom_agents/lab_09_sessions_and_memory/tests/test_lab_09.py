import asyncio
from pydantic import BaseModel

import lab
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG
from google.adk.agents import LlmAgent
from google.adk.integrations.redis import (
    RedisSessionService,
    RedisSessionServiceConfig,
)
from google.adk.memory import (
    InMemoryMemoryService,
    VertexAiMemoryBankService,
    VertexAiRagMemoryService,
)
from google.adk.sessions import (
    DatabaseSessionService,
    InMemorySessionService,
    VertexAiSessionService,
)
from google.adk.tools import load_memory, preload_memory


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
        key_prefix="test",
    )
    assert config.host == "localhost"
    assert config.key_prefix == "test"
    assert config.ttl_seconds == 120


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
        output_key="val",
    )
    assert agent.output_key == "val"
    assert agent.state_schema == AppState


def test_agent_runtime_managed_pair_and_recall_tradeoffs():
    v_sess, v_mem = lab.build_agent_runtime_managed_pair(
        project_id="proj-support",
        location="us-central1",
        agent_engine_id="ae-999",
    )
    assert isinstance(v_sess, VertexAiSessionService)
    assert isinstance(v_mem, VertexAiMemoryBankService)

    tradeoffs = lab.compare_memory_recall_modes(memory_needed_rate=0.2, injected_memory_tokens=300)
    assert tradeoffs["preload_memory"].llm_round_trips_when_needed == 1
    assert tradeoffs["load_memory"].llm_round_trips_when_needed == 2
    assert tradeoffs["load_memory"].avg_memory_tokens_per_turn < tradeoffs["preload_memory"].avg_memory_tokens_per_turn


def test_per_user_id_session_and_memory_isolation():
    iso = asyncio.run(lab.verify_tenant_isolation_and_retention())
    assert iso["owner_session_accessible"] is True
    assert iso["cross_tenant_session_blocked"] is True
    assert iso["owner_memory_recalled"] is True
    assert iso["cross_tenant_memory_isolated"] is True


def test_offline_report_passes():
    report = lab.run_offline()
    assert report.passed
