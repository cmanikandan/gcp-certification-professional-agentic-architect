"""
Unit Tests for Module 08: Custom Agent Skills & Hooks
"""

import sys
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from skills_and_hooks_manager import (
    AntigravityCustomizationManager,
    AgentSkill
)

def test_skill_parsing_and_precedence():
    manager = AntigravityCustomizationManager()
    global_skill = """---
name: lint-skill
description: Global linting.
---
Run global lint.
"""
    workspace_skill = """---
name: lint-skill
description: Workspace customized linting.
---
Run custom workspace lint.
"""
    # Parse global first, then workspace
    manager.parse_skill_file(global_skill, source_location="global")
    assert manager.skills["lint-skill"].source_location == "global"

    manager.parse_skill_file(workspace_skill, source_location="workspace")
    # Workspace should override global due to higher priority (rank 1 < rank 3)
    assert manager.skills["lint-skill"].source_location == "workspace"
    assert "Workspace" in manager.skills["lint-skill"].description

def test_progressive_disclosure():
    manager = AntigravityCustomizationManager()
    skill_text = """---
name: deploy-agent
description: Cloud Run deployer.
---
Instructions for deploying to Cloud Run.
"""
    manager.parse_skill_file(skill_text, source_location="workspace")

    # Inactive
    ctx1 = manager.get_progressive_disclosure_context(active_skills=[])
    assert "deploy-agent: Cloud Run deployer" in ctx1["available_skills_overview"]
    assert ctx1["injected_skill_instructions"] == ""

    # Active
    ctx2 = manager.get_progressive_disclosure_context(active_skills=["deploy-agent"])
    assert "Instructions for deploying to Cloud Run." in ctx2["injected_skill_instructions"]

def test_lifecycle_hooks():
    manager = AntigravityCustomizationManager()
    manager.register_pre_turn_hook(lambda p: p.upper())

    results = []
    manager.register_post_tool_hook(lambda t, a, r: results.append(t))

    prompt = manager.execute_pre_turn("hello agent")
    assert prompt == "HELLO AGENT"

    manager.execute_post_tool("query_db", {}, {})
    assert results == ["query_db"]
