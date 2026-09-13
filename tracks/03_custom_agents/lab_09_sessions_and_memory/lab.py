#!/usr/bin/env python3
"""Lab 09: Sessions and Memory."""
import sys
from pydantic import BaseModel, Field
from common import DEFAULT_AGENT_MODEL, load_config, require_live

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
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


class UserPreferences(BaseModel):
    dietary_needs: str = Field(description="Dietary requirements")

class AppState(BaseModel):
    user_prefs: UserPreferences | None = None


def run_offline():
    print("Running Lab 09 OFFLINE: Sessions and Memory")
    
    # 1. Session State (Short-term)
    print("\n--- Session Services ---")
    in_memory_session = InMemorySessionService()
    print(f"Created {in_memory_session.__class__.__name__} for local dev.")
    
    vertex_session = VertexAiSessionService()
    print(f"Created {vertex_session.__class__.__name__} for managed history.")

    db_session = DatabaseSessionService(db_url="sqlite+aiosqlite:///:memory:")
    print(f"Created {db_session.__class__.__name__} for durable, multi-region SQL storage.")

    redis_config = RedisSessionServiceConfig(
        uri="redis://10.0.0.5:6379",
        host="10.0.0.5",
        port=6379,
        password="dummy",
        ssl=True,
        db=0,
        ttl_seconds=3600,
        key_prefix="agent_session"
    )
    print(f"Configured Redis: host={redis_config.host}, prefix={redis_config.key_prefix}")
    
    # Demonstrate output_key and state_schema binding
    agent = LlmAgent(
        name="PrefExtractor",
        model=Gemini(model=DEFAULT_AGENT_MODEL),
        instruction="Extract dietary preferences.",
        output_schema=UserPreferences,
        output_key="user_prefs", # Binds to AppState.user_prefs in a workflow
        state_schema=AppState,
    )
    print(f"\nAgent '{agent.name}' will write to state key '{agent.output_key}'.")

    # 2. Memory Banks (Long-term)
    print("\n--- Memory Services ---")
    in_memory_bank = InMemoryMemoryService()
    print(f"Created {in_memory_bank.__class__.__name__} for local testing.")

    vertex_memory = VertexAiMemoryBankService(agent_engine_id="my-agent")
    print(f"Created {vertex_memory.__class__.__name__} for structured long-term facts.")

    rag_memory = VertexAiRagMemoryService()
    print(f"Created {rag_memory.__class__.__name__} for large semantic vector recall.")

    # 3. Tools
    print("\n--- Memory Tools ---")
    print(f"On-demand recall tool: {load_memory.name}")
    print(f"Proactive context injection tool: {preload_memory.name}")
    print("\nReminder: Use `adk migrate session` CLI command to move data between session backends.")


def run_live(config):
    print("Running Lab 09 LIVE")
    run_offline()


if __name__ == "__main__":
    config = load_config(sys.argv[1:])
    if require_live(config):
        run_live(config)
    else:
        run_offline()
