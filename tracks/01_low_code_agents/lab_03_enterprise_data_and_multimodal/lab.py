#!/usr/bin/env python3
"""Lab 3: Enterprise Data & Multimodal"""

import asyncio
from typing import Optional
from unittest.mock import patch

from google.adk import Agent
from google.adk.tools import VertexAiSearchTool, DiscoveryEngineSearchTool

from common import load_config, require_live
from common.labkit import LabReport, banner, section, step, detail
from common.models import DEFAULT_AGENT_MODEL, get_profile


# ---------------------------------------------------------------------------
# Simulator for ACL-Aware Search (Identity Propagation)
#
# The exam asks about "securely connecting... enterprise proprietary data".
# The key architectural concept is Identity Propagation: the agent must not
# surface documents the calling user is not allowed to see.
# ---------------------------------------------------------------------------

class MockDatastore:
    def __init__(self):
        self.documents = [
            {"id": "doc1", "title": "Public Holiday Policy", "acl": ["*"]},
            {"id": "doc2", "title": "Project X Architecture", "acl": ["engineering", "alice@example.com"]},
            {"id": "doc3", "title": "Q3 Layoff Plans", "acl": ["executives", "bob@example.com"]},
        ]

    def search(self, query: str, user_email: str, user_groups: list[str]) -> list[dict]:
        """Simulate an ACL-aware search query."""
        results = []
        for doc in self.documents:
            # Check if user has permission to view this document
            allowed = False
            if "*" in doc["acl"] or user_email in doc["acl"]:
                allowed = True
            else:
                for group in user_groups:
                    if group in doc["acl"]:
                        allowed = True
            
            if allowed:
                results.append(doc)
        return results


async def run_offline():
    banner("Lab 3: Enterprise Data & Multimodal", "Agent Search ACLs and Multimodal Models")

    section("1. Identity Propagation in Agent Search")
    step("1", "Simulating Datastore Search with ACLs")
    datastore = MockDatastore()
    
    # Alice is an engineer
    alice_results = datastore.search("policy", user_email="alice@example.com", user_groups=["engineering"])
    detail(f"Alice (Engineer) sees: {[d['title'] for d in alice_results]}")
    
    # Charlie is a contractor (no groups)
    charlie_results = datastore.search("policy", user_email="charlie@example.com", user_groups=[])
    detail(f"Charlie (Contractor) sees: {[d['title'] for d in charlie_results]}")
    
    # Bob is an executive
    bob_results = datastore.search("policy", user_email="bob@example.com", user_groups=["executives"])
    detail(f"Bob (Executive) sees: {[d['title'] for d in bob_results]}")

    section("2. ADK Search Tools")
    step("2", "Instantiating real ADK Search Tools")
    
    # In ADK, you use VertexAiSearchTool or DiscoveryEngineSearchTool
    # Patch credentials since we are offline
    with patch("google.auth.default", return_value=(None, "dummy-project")):
        tool = DiscoveryEngineSearchTool(
            location="global",
            data_store_id="my-datastore"
        )
        detail(f"Instantiated: {type(tool).__name__}")
    
    section("3. Multimodal Model Selection")
    step("3", "Checking verified modalities")
    
    flash_profile = get_profile(DEFAULT_AGENT_MODEL)
    detail(f"{DEFAULT_AGENT_MODEL} native modalities: {flash_profile.modalities}")
    detail("Native models process video/audio/images without intermediate extraction pipelines.")

    report = LabReport("Enterprise Data")
    report.check("Identity Propagation hides sensitive data", len(charlie_results) == 1 and len(bob_results) == 2)
    report.check("ADK Tool instantiated", type(tool).__name__ == "DiscoveryEngineSearchTool")
    report.check("Gemini natively supports audio/video", "video" in flash_profile.modalities)
    report.summary()


async def run_live(config):
    """Live Google Cloud path."""
    banner("Lab 3: Enterprise Data & Multimodal (LIVE)")
    detail("Live execution requires an active Vertex AI Search Datastore.")
    detail("Since datastores take hours to index, this lab falls back to offline.")
    await run_offline()


def main():
    config = load_config()
    if require_live(config):
        asyncio.run(run_live(config))
    else:
        asyncio.run(run_offline())

if __name__ == "__main__":
    main()
