"""
Unit Tests for Module 06: Agent Memory, State & Sessions
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from memory_bank_manager import (
    ManagedSession,
    AgentPlatformMemoryBank
)

def test_managed_session_pruning():
    session = ManagedSession(session_id="test_sess", max_messages=3)
    session.add_message("user", "Msg 1")
    session.add_message("model", "Msg 2")
    session.add_message("user", "Msg 3")
    assert len(session.messages) == 3

    session.add_message("model", "Msg 4")
    assert len(session.messages) == 3
    active = session.get_active_context()
    assert active[0]["content"] == "Msg 2"
    assert active[-1]["content"] == "Msg 4"

def test_session_variables():
    session = ManagedSession("test_var_sess")
    session.set_variable("order_id", "ORD-123")
    assert session.get_variable("order_id") == "ORD-123"
    assert session.get_variable("missing_key", "default_val") == "default_val"

def test_memory_bank_extraction_and_recall():
    bank = AgentPlatformMemoryBank()
    user_id = "user_test_99"
    dialogue = "I prefer Python and our deployment region is us-central1 with a budget: $500."

    facts = bank.extract_and_store_facts(user_id, dialogue)
    assert len(facts) >= 2

    recalled = bank.recall_memories(user_id, "How should I structure the Python script?")
    assert len(recalled) >= 1
    assert any("Python" in r for r in recalled)
