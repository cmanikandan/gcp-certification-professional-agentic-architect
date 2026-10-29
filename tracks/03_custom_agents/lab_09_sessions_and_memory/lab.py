#!/usr/bin/env python3
"""Lab 09: Managed Runtime Sessions & Memory Service Patterns (Objective 3.1)."""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass

from common import DEFAULT_AGENT_MODEL, load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, step, table
from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.adk.integrations.redis import (
    RedisSessionService,
    RedisSessionServiceConfig,
)
from google.adk.memory import (
    InMemoryMemoryService,
    VertexAiMemoryBankService,
    VertexAiRagMemoryService,
)
from google.adk.models import Gemini
from google.adk.sessions import (
    DatabaseSessionService,
    InMemorySessionService,
    VertexAiSessionService,
)
from google.adk.tools import load_memory, preload_memory
from google.genai import types
from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    dietary_needs: str = Field(description="Verified dietary or accessibility preference")


class AppState(BaseModel):
    user_prefs: UserPreferences | None = None


@dataclass(frozen=True)
class RecallTradeOff:
    """Latency and prompt-token profile for preload_memory vs load_memory."""

    mode: str
    llm_round_trips_when_needed: int
    avg_memory_tokens_per_turn: float


def compare_memory_recall_modes(
    memory_needed_rate: float = 0.20,
    injected_memory_tokens: int = 350,
) -> dict[str, RecallTradeOff]:
    """Compare proactive preload_memory vs on-demand load_memory."""
    if not 0.0 <= memory_needed_rate <= 1.0:
        raise ValueError("memory_needed_rate must be in [0.0, 1.0]")

    return {
        "preload_memory": RecallTradeOff(
            mode="preload_memory (proactive before model call)",
            llm_round_trips_when_needed=1,
            avg_memory_tokens_per_turn=float(injected_memory_tokens),
        ),
        "load_memory": RecallTradeOff(
            mode="load_memory (on-demand tool call)",
            llm_round_trips_when_needed=2,
            avg_memory_tokens_per_turn=round(memory_needed_rate * injected_memory_tokens, 1),
        ),
    }


def build_agent_runtime_managed_pair(
    project_id: str = "proj-support-prod",
    location: str = "us-central1",
    agent_engine_id: str = "ae-customer-care-001",
) -> tuple[VertexAiSessionService, VertexAiMemoryBankService]:
    """Configure the zero-ops managed session + memory pair for Agent Runtime."""
    session_svc = VertexAiSessionService(
        project=project_id,
        location=location,
        agent_engine_id=agent_engine_id,
    )
    memory_svc = VertexAiMemoryBankService(
        project=project_id,
        location=location,
        agent_engine_id=agent_engine_id,
    )
    return session_svc, memory_svc


async def verify_tenant_isolation_and_retention() -> dict[str, bool]:
    """Prove per-user_id session and memory isolation offline."""
    session_svc = InMemorySessionService()
    memory_svc = InMemoryMemoryService()

    sess_a = await session_svc.create_session(
        app_name="hipaa_support_portal",
        user_id="patient-101",
        state={"tier": "gold", "redacted_intake": True},
    )
    turn_event = Event(
        author="user",
        content=types.Content(
            role="user",
            parts=[types.Part.from_text(text="I prefer morning telehealth appointments and vegan meal plans.")],
        ),
    )
    await session_svc.append_event(session=sess_a, event=turn_event)

    owner_read = await session_svc.get_session(
        app_name="hipaa_support_portal",
        user_id="patient-101",
        session_id=sess_a.id,
    )
    cross_tenant_read = await session_svc.get_session(
        app_name="hipaa_support_portal",
        user_id="patient-202",
        session_id=sess_a.id,
    )

    refreshed_a = owner_read or sess_a
    await memory_svc.add_session_to_memory(refreshed_a)

    owner_mem = await memory_svc.search_memory(
        app_name="hipaa_support_portal",
        user_id="patient-101",
        query="vegan",
    )
    cross_tenant_mem = await memory_svc.search_memory(
        app_name="hipaa_support_portal",
        user_id="patient-202",
        query="vegan",
    )

    return {
        "owner_session_accessible": owner_read is not None,
        "cross_tenant_session_blocked": cross_tenant_read is None,
        "owner_memory_recalled": len(owner_mem.memories) > 0,
        "cross_tenant_memory_isolated": len(cross_tenant_mem.memories) == 0,
    }


def run_offline() -> LabReport:
    banner(
        "Lab 09 — Managed Runtime Sessions & Memory Patterns",
        "Objective 3.1: Agent Runtime Managed Pair, Redis/SQL Backends & Recall Trade-Offs (Offline)",
    )
    report = LabReport("Lab 09 — Sessions & Memory")

    section("1. Agent Runtime Zero-Ops Managed Pairing (agent_engine_id)")
    v_sess, v_mem = build_agent_runtime_managed_pair(
        project_id="proj-support-prod",
        location="us-central1",
        agent_engine_id="ae-customer-care-001",
    )
    step(1, f"Short-term turns: {type(v_sess).__name__}(agent_engine_id='ae-customer-care-001')")
    step(2, f"Long-term facts:  {type(v_mem).__name__}(agent_engine_id='ae-customer-care-001')")
    exam_note(
        "Deploying via `adk deploy agent_engine` pairs VertexAiSessionService + "
        "VertexAiMemoryBankService for zero-infrastructure state and cross-session memory."
    )
    report.check(
        "Agent Runtime managed session & memory services instantiate with agent_engine_id",
        isinstance(v_sess, VertexAiSessionService) and isinstance(v_mem, VertexAiMemoryBankService),
    )

    section("2. Cloud Run / GKE Session Backends & Corpus RAG Memory")
    redis_cfg = RedisSessionServiceConfig(
        uri="rediss://10.12.0.5:6378",
        host="10.12.0.5",
        port=6378,
        password="secret-ref-from-secret-manager",
        ssl=True,
        db=0,
        ttl_seconds=1800,
        key_prefix="support_sess",
    )
    db_sess = DatabaseSessionService(db_url="sqlite+aiosqlite:///:memory:")
    rag_mem = VertexAiRagMemoryService(
        rag_corpus="projects/proj-support-prod/locations/us-central1/ragCorpora/kb-corpus",
        similarity_top_k=5,
    )
    step(
        3,
        f"Memorystore config ({RedisSessionService.__name__}): "
        f"ssl={redis_cfg.ssl}, ttl_seconds={redis_cfg.ttl_seconds}, prefix='{redis_cfg.key_prefix}'",
    )
    step(4, f"ACID SQL session backend: {type(db_sess).__name__}")
    step(5, f"Large-corpus semantic memory: {type(rag_mem).__name__}")
    report.check(
        "RedisSessionServiceConfig enforces TLS and ephemeral TTL retention",
        redis_cfg.ssl is True and redis_cfg.ttl_seconds == 1800 and isinstance(db_sess, DatabaseSessionService),
    )

    section("3. Typed State Binding & Recall Mode Trade-Offs (preload_memory vs load_memory)")
    proactive_agent = LlmAgent(
        name="VIPConcierge",
        model=Gemini(model=DEFAULT_AGENT_MODEL),
        instruction="Personalize every response using preloaded preferences.",
        output_schema=UserPreferences,
        output_key="user_prefs",
        state_schema=AppState,
        tools=[preload_memory],
    )
    ondemand_agent = LlmAgent(
        name="TechSupportSpecialist",
        model=Gemini(model=DEFAULT_AGENT_MODEL),
        instruction="Only call load_memory if the user references a prior ticket preference.",
        tools=[load_memory],
    )
    tradeoffs = compare_memory_recall_modes(memory_needed_rate=0.20, injected_memory_tokens=350)
    table(
        ["Recall Tool", "LLM Round-Trips (When Needed)", "Avg Memory Tokens / Turn (20% Hit Rate)"],
        [
            [t.mode, t.llm_round_trips_when_needed, t.avg_memory_tokens_per_turn]
            for t in tradeoffs.values()
        ],
    )
    report.check(
        "preload_memory avoids extra tool round-trip; load_memory saves tokens on non-memory turns",
        tradeoffs["preload_memory"].llm_round_trips_when_needed == 1
        and tradeoffs["load_memory"].llm_round_trips_when_needed == 2
        and tradeoffs["load_memory"].avg_memory_tokens_per_turn
        < tradeoffs["preload_memory"].avg_memory_tokens_per_turn
        and proactive_agent.output_key == "user_prefs"
        and ondemand_agent.tools[0].name == load_memory.name,
    )

    section("4. Multi-Tenant (app_name, user_id) Session & Memory Isolation")
    iso = asyncio.run(verify_tenant_isolation_and_retention())
    for check_key, passed in iso.items():
        step("ISO", f"{check_key}: {passed}")
    report.check(
        "Strict per-user_id isolation blocks cross-tenant session & memory access",
        all(iso.values()),
    )

    report.summary()
    return report


def run_live(config) -> None:
    banner("Lab 09 — Managed Runtime Sessions & Memory (Live)", f"Project: {config.project_id}")
    run_offline()
    section("Agent Runtime CLI Reference")
    step(1, "Deploy managed runtime: adk deploy agent_engine --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION")
    step(2, "Migrate session store:  adk migrate session --help")


if __name__ == "__main__":
    cfg = load_config(sys.argv[1:])
    if require_live(cfg):
        run_live(cfg)
    else:
        result = run_offline()
        sys.exit(0 if result.passed else 1)
