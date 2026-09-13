import os
import shutil
import tempfile
from common import load_config, require_live

from google.adk.skills import load_skills_from_dir, Skill, Frontmatter

def create_mock_skill(base_dir: str):
    """
    Creates a skill structure on disk mimicking an enterprise custom skill.
    """
    skill_dir = os.path.join(base_dir, "enterprise-security-auditor")
    os.makedirs(skill_dir, exist_ok=True)
    
    # Writing the SKILL.md with Frontmatter (L1) and Instructions (L2)
    skill_content = """---
name: enterprise-security-auditor
description: Audits code against enterprise zero-trust standards.
license: Apache-2.0
compatibility: gemini-3.7-flash
allowed_tools: code_executor, mcp_jira_server, gcp_iam_analyzer
metadata:
  approval_gate: required
---
# Security Auditor Instructions
You are an enterprise security auditor.
1. Run static analysis using the code_executor.
2. Check IAM bindings using gcp_iam_analyzer.
3. If violations are found, file a ticket using mcp_jira_server.
"""
    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)
    
    return skill_dir

def run_offline():
    print("--- Enterprise Coding Agent Customization (Offline) ---")
    
    # 1. Create a workspace with a custom skill
    workspace = tempfile.mkdtemp()
    create_mock_skill(workspace)
    print(f"Provisioned local skill directory at {workspace}")
    
    # 2. Parse the skill using the official ADK API
    skills = load_skills_from_dir(workspace)
    if not skills:
        print("Failed to load skills.")
        return
        
    skill = skills[0]
    fm = skill.frontmatter
    
    print("\n--- Parsed Skill Frontmatter (Governance Metadata) ---")
    print(f"Name:          {fm.name}")
    print(f"Description:   {fm.description}")
    print(f"Compatibility: {fm.compatibility}")
    print(f"Allowed Tools: {fm.allowed_tools}")
    print(f"Metadata:      {fm.metadata}")
    
    # 3. Governance check demonstration
    print("\n--- Simulating Governance / Tool Binding ---")
    allowed_tools_list = [t.strip() for t in fm.allowed_tools.split(",")] if fm.allowed_tools else []
    print(f"The ADK agent will only be granted access to: {allowed_tools_list}")
    
    if fm.metadata.get("approval_gate") == "required":
        print("GOVERNANCE: This skill requires a Human-In-The-Loop (HITL) approval gate.")
        
    print("\nOffline execution successful: Instantiated and verified custom ADK skills.")
    
    # Cleanup
    shutil.rmtree(workspace)

def run_live(config):
    # This lab focuses on local/portable customization, so live just runs offline.
    print("Live mode: This lab uses local ADK parsing and does not require GCP services.")
    run_offline()

def main():
    config = load_config()
    if require_live(config):
        run_live(config)
    else:
        run_offline()

if __name__ == "__main__":
    main()
