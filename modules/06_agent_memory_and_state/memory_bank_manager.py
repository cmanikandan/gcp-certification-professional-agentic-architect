"""
Module 06: Manage Agent Memory, State & Sessions
Demonstrates:
1. Managed Session Controller with Sliding-Window Token/Turn Pruning
2. Agent Platform Memory Bank Simulator (Associative Long-Term Semantic Fact Extraction & Recall)
3. Multi-Session User Personalization Flow
"""

import os
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class Message:
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)

class ManagedSession:
    """Manages short-term conversational context with sliding-window pruning."""

    def __init__(self, session_id: str, max_messages: int = 4):
        self.session_id = session_id
        self.max_messages = max_messages
        self.messages: List[Message] = []
        self.variables: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
        self._prune_context()

    def _prune_context(self):
        """Maintains active context within max_messages sliding window."""
        if len(self.messages) > self.max_messages:
            # Preserve system instruction if any, prune older turns
            overflow_count = len(self.messages) - self.max_messages
            self.messages = self.messages[overflow_count:]

    def set_variable(self, key: str, value: Any):
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def get_active_context(self) -> List[Dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

@dataclass
class MemoryFact:
    fact_id: str
    user_id: str
    category: str
    fact_text: str
    created_at: float = field(default_factory=time.time)

class AgentPlatformMemoryBank:
    """Simulates Google Cloud Agent Platform Memory Bank for long-term associative memory."""

    def __init__(self):
        # In-memory fact store keyed by user_id
        self.fact_store: Dict[str, List[MemoryFact]] = {}

    def extract_and_store_facts(self, user_id: str, conversation_text: str) -> List[MemoryFact]:
        """Analyzes dialogue and extracts persistent user preferences/facts."""
        extracted = []
        lower_text = conversation_text.lower()

        if "prefer python" in lower_text or "python developer" in lower_text:
            fact = MemoryFact(
                fact_id=f"fact_{len(extracted)+1}",
                user_id=user_id,
                category="technical_preference",
                fact_text="User specializes in Python and prefers Python code examples."
            )
            extracted.append(fact)

        if "us-central1" in lower_text or "iowa region" in lower_text:
            fact = MemoryFact(
                fact_id=f"fact_{len(extracted)+1}",
                user_id=user_id,
                category="infrastructure_preference",
                fact_text="User's primary production deployment region is us-central1 (Iowa)."
            )
            extracted.append(fact)

        if "budget under $500" in lower_text or "budget: $500" in lower_text:
            fact = MemoryFact(
                fact_id=f"fact_{len(extracted)+1}",
                user_id=user_id,
                category="financial_constraint",
                fact_text="Monthly cloud infrastructure budget cap is $500 USD."
            )
            extracted.append(fact)

        if user_id not in self.fact_store:
            self.fact_store[user_id] = []
        self.fact_store[user_id].extend(extracted)
        return extracted

    def recall_memories(self, user_id: str, query: str) -> List[str]:
        """Semantically retrieves relevant long-term memories for a user query."""
        user_facts = self.fact_store.get(user_id, [])
        if not user_facts:
            return []

        # Simple semantic filter simulation
        query_words = set(query.lower().split())
        matched_facts = []
        for fact in user_facts:
            fact_words = set(fact.fact_text.lower().split())
            if query_words.intersection(fact_words) or any(w in fact.category for w in query_words):
                matched_facts.append(fact.fact_text)

        # Fallback to returning all salient facts if general query
        if not matched_facts:
            matched_facts = [f.fact_text for f in user_facts]

        return matched_facts

def main():
    print("====================================================================")
    print("Module 06: Manage Agent Memory, State & Sessions")
    print("====================================================================\n")

    user_id = "usr_architect_408"

    # 1. Short-Term Managed Session with Pruning
    print("--- 1. Testing Managed Session (Sliding Window Context) ---")
    session = ManagedSession(session_id="sess_1001", max_messages=4)
    session.add_message("user", "Hello, I am setting up our GCP environment.")
    session.add_message("model", "Hello! Which region do you plan to use?")
    session.add_message("user", "We will deploy in us-central1 and prefer Python.")
    session.add_message("model", "Got it. Will remember us-central1 and Python.")
    session.add_message("user", "Can you also make sure our budget is under $500?")
    session.add_message("model", "Noted, budget is capped at $500.")

    print(f"Total messages added: 6. Active context window (max 4):")
    for m in session.get_active_context():
        print(f"  [{m['role'].upper()}]: {m['content']}")

    # 2. Extract Facts into Agent Platform Memory Bank
    print("\n--- 2. Extracting Facts into Agent Platform Memory Bank ---")
    memory_bank = AgentPlatformMemoryBank()
    full_text = " ".join([m.content for m in session.messages])
    facts = memory_bank.extract_and_store_facts(user_id, full_text)
    for f in facts:
        print(f"  🧠 Extracted Memory Fact [{f.category}]: {f.fact_text}")

    # 3. New Session 3 Weeks Later: Long-Term Recall
    print("\n--- 3. Starting New Session Weeks Later: Memory Bank Recall ---")
    new_query = "Please generate a deployment script for our database."
    recalled = memory_bank.recall_memories(user_id, new_query)
    print(f"User Query: '{new_query}'")
    print("Recalled Long-Term Memories for Context Augmentation:")
    for mem in recalled:
        print(f"  * {mem}")

if __name__ == "__main__":
    main()
