import os
import shutil
import tempfile
from google.adk.skills import load_skills_from_dir
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG

def create_mock_skill(base_dir: str):
    skill_dir = os.path.join(base_dir, "test-skill")
    os.makedirs(skill_dir, exist_ok=True)
    skill_content = """---
name: test-skill
description: A test skill.
allowed_tools: search, read_file
---
# Test Instructions
Do test things.
"""
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)
    return skill_dir

def test_load_skills_from_dir():
    workspace = tempfile.mkdtemp()
    try:
        create_mock_skill(workspace)
        skills = load_skills_from_dir(workspace)
        
        assert len(skills) == 1
        skill = skills[0]
        assert skill.frontmatter.name == "test-skill"
        assert skill.frontmatter.description == "A test skill."
        assert skill.frontmatter.allowed_tools == "search, read_file"
    finally:
        shutil.rmtree(workspace)

def test_uses_only_verified_models():
    # Model used in lab context (if any) should be verified.
    # In this lab we are referencing 'gemini-3.7-flash' in compatibility.
    assert DEFAULT_AGENT_MODEL in MODEL_CATALOG
