"""
Module 08: Build Custom Agent Skills, Plugins & Hooks
Demonstrates:
1. Skill Discovery & Progressive Disclosure Manager (YAML frontmatter parsing)
2. Antigravity Loading Precedence Engine
3. Agent Lifecycle Hooks (Pre-turn interceptor, Post-tool execution telemetry)
"""

import os
import re
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class AgentSkill:
    name: str
    description: str
    content: str
    source_location: str  # workspace, declared, global, builtin
    priority_rank: int


@dataclass(frozen=True)
class RegisteredSkillVersion:
    name: str
    version: str
    digest: str
    approved_by: str


class SkillRegistrySimulator:
    """Versions and approves skills before Agents CLI can consume them."""

    def __init__(self):
        self.versions: Dict[str, Dict[str, RegisteredSkillVersion]] = {}

    def publish(self, skill: AgentSkill, version: str, approved_by: str) -> RegisteredSkillVersion:
        if not approved_by.strip():
            raise ValueError("A governed skill version requires an approver")
        digest = hashlib.sha256(skill.content.encode("utf-8")).hexdigest()[:12]
        registered = RegisteredSkillVersion(skill.name, version, digest, approved_by)
        self.versions.setdefault(skill.name, {})[version] = registered
        return registered

    def resolve(self, name: str, version: str) -> Optional[RegisteredSkillVersion]:
        return self.versions.get(name, {}).get(version)


class AgentsCLIModePolicy:
    """Separates autonomous agent permissions from interactive human permissions."""

    def __init__(self, agent_mode_tools: List[str], human_mode_tools: List[str]):
        self.allowed = {
            "agent": set(agent_mode_tools),
            "human": set(human_mode_tools),
        }

    def can_invoke(self, mode: str, tool_name: str) -> bool:
        if mode not in self.allowed:
            raise ValueError("mode must be 'agent' or 'human'")
        return tool_name in self.allowed[mode]

class AntigravityCustomizationManager:
    """Manages skill discovery, progressive disclosure, and lifecycle hooks."""

    PRIORITY_MAP = {
        "workspace": 1,  # Highest priority
        "declared": 2,
        "global": 3,
        "builtin": 4     # Lowest priority
    }

    def __init__(self):
        self.skills: Dict[str, AgentSkill] = {}
        self.pre_turn_hooks: List[Callable[[str], str]] = []
        self.post_tool_hooks: List[Callable[[str, Dict[str, Any], Any], None]] = []

    def parse_skill_file(self, file_content: str, source_location: str = "workspace") -> Optional[AgentSkill]:
        """Extracts YAML frontmatter (name, description) and body."""
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", file_content, re.DOTALL)
        if not match:
            return None

        frontmatter, body = match.groups()
        name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)

        if not name_match or not desc_match:
            return None

        name = name_match.group(1).strip()
        description = desc_match.group(1).strip()
        rank = self.PRIORITY_MAP.get(source_location, 5)

        skill = AgentSkill(
            name=name,
            description=description,
            content=body.strip(),
            source_location=source_location,
            priority_rank=rank
        )

        # Apply precedence (lower rank integer = higher precedence)
        if name not in self.skills or rank < self.skills[name].priority_rank:
            self.skills[name] = skill

        return skill

    def get_progressive_disclosure_context(self, active_skills: List[str] = None) -> Dict[str, Any]:
        """Implements progressive disclosure: summaries for all, full bodies for active only."""
        active_skills = active_skills or []
        summary_list = []
        injected_instructions = []

        for name, skill in self.skills.items():
            summary_list.append(f"- {skill.name}: {skill.description} [Origin: {skill.source_location}]")
            if name in active_skills:
                injected_instructions.append(f"### ACTIVE SKILL: {skill.name}\n{skill.content}")

        return {
            "available_skills_overview": "\n".join(summary_list),
            "injected_skill_instructions": "\n\n".join(injected_instructions)
        }

    def register_pre_turn_hook(self, hook: Callable[[str], str]):
        self.pre_turn_hooks.append(hook)

    def register_post_tool_hook(self, hook: Callable[[str, Dict[str, Any], Any], None]):
        self.post_tool_hooks.append(hook)

    def execute_pre_turn(self, user_prompt: str) -> str:
        current_prompt = user_prompt
        for hook in self.pre_turn_hooks:
            current_prompt = hook(current_prompt)
        return current_prompt

    def execute_post_tool(self, tool_name: str, args: Dict[str, Any], result: Any):
        for hook in self.post_tool_hooks:
            hook(tool_name, args, result)

def main():
    print("====================================================================")
    print("Module 08: Custom Agent Skills, Plugins & Lifecycle Hooks")
    print("====================================================================\n")

    manager = AntigravityCustomizationManager()

    # 1. Register Built-in vs Workspace Custom Skill (Precedence Test)
    builtin_raw = """---
name: gcp-ops-skill
description: Default built-in Cloud Run ops tool.
---
# Built-in Instructions
Run standard gcloud command.
"""
    workspace_raw = """---
name: gcp-ops-skill
description: Enterprise-hardened Cloud Run ops tool with PAB verification.
---
# Enterprise Workspace Instructions
1. Run gcloud with strict PAB identity.
2. Verify /healthz endpoint.
"""
    manager.parse_skill_file(builtin_raw, source_location="builtin")
    manager.parse_skill_file(workspace_raw, source_location="workspace")

    print("--- 1. Skill Discovery & Precedence Resolution ---")
    active_skill = manager.skills["gcp-ops-skill"]
    print(f"Skill Name        : {active_skill.name}")
    print(f"Resolved Origin   : {active_skill.source_location} (Priority {active_skill.priority_rank})")
    print(f"Description       : {active_skill.description}")

    # 2. Test Progressive Disclosure
    print("\n--- 2. Progressive Disclosure (Only Active Skills Injected) ---")
    overview = manager.get_progressive_disclosure_context(active_skills=["gcp-ops-skill"])
    print("Available Skills Injected to System Prompt:\n", overview["available_skills_overview"])
    print("\nInjected Full Body:\n", overview["injected_skill_instructions"])

    # 3. Lifecycle Hooks
    print("\n--- 3. Testing Lifecycle Hooks ---")
    # Pre-turn hook sanitizes prompt
    manager.register_pre_turn_hook(lambda p: f"[AUDITED-TURN]: {p.strip()}")
    # Post-tool hook records telemetry
    telemetry_log = []
    manager.register_post_tool_hook(lambda t, a, r: telemetry_log.append(f"Tool {t} executed with {a} -> Status {r.get('status')}"))

    sanitized = manager.execute_pre_turn("Deploy service auth-gateway")
    print("Sanitized Prompt:", sanitized)

    manager.execute_post_tool("deploy_service", {"name": "auth-gateway"}, {"status": "SUCCESS"})
    print("Telemetry Log   :", telemetry_log)

    # 4. Govern a versioned skill and enforce Agents CLI execution modes
    print("\n--- 4. Testing Skill Registry & Agents CLI Modes ---")
    registry = SkillRegistrySimulator()
    version = registry.publish(active_skill, version="1.0.0", approved_by="platform-admin")
    print(f"Published Skill : {version.name}@{version.version} ({version.digest})")
    modes = AgentsCLIModePolicy(
        agent_mode_tools=["inspect_service"],
        human_mode_tools=["inspect_service", "deploy_service"],
    )
    print("Agent mode can deploy:", modes.can_invoke("agent", "deploy_service"))
    print("Human mode can deploy:", modes.can_invoke("human", "deploy_service"))

if __name__ == "__main__":
    main()
