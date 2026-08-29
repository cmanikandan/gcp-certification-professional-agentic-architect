# Module 08: Build Custom Agent Skills, Plugins & Hooks

## Overview
This module explores enterprise extensibility in Google Antigravity and Agents CLI. You will learn to construct modular agent skills (`SKILL.md`), manage progressive disclosure, package plugins, configure contextual rules (`GEMINI.md`), and execute lifecycle interceptor hooks.

---

## 🎯 Exam Objectives Covered
- **2.2 Customizing coding agents for enterprise workflows**
  - Creating custom skills, plugins, extension hooks, rules, and subagents using Antigravity.
  - Understanding skill discovery precedence: Workspace Project (`.agents/`) > Declared (`skills.json`) > Global (`~/.gemini/config/`) > Built-in.
  - Implementing lifecycle hooks for pre-tool validation and post-execution telemetry.

---

## 🧩 Antigravity Customization Hierarchy

```mermaid
graph TD
    UserTurn[Developer Turn / File Opened] --> PrecedenceRouter[Precedence Router]
    PrecedenceRouter --> Priority1[1. Workspace Project: .agents/skills/ & rules/]
    Priority1 --> Priority2[2. Declared Config: skills.json / plugins.json]
    Priority2 --> Priority3[3. Global Config: ~/.gemini/config/]
    Priority3 --> Priority4[4. Built-in Skills]
    PrecedenceRouter --> HookPre[Pre-Turn Lifecycle Hook]
    HookPre --> SkillActivation{Progressive Disclosure: Activate Skill?}
    SkillActivation -->|Relevant| InjectFullSKILL[Inject Full SKILL.md Context]
    SkillActivation -->|Not Needed| NameOnly[Inject Name & Description Only]
    InjectFullSKILL --> ModelReasoning[Agent Reasoning]
    ModelReasoning --> HookPost[Post-Tool Lifecycle Hook]
```

---

## 🚀 Hands-on Lab: Running the Module

```bash
# Run the skills and hooks manager lab
python3 modules/08_custom_skills_plugins_and_hooks/skills_and_hooks_manager.py

# Run unit tests
pytest modules/08_custom_skills_plugins_and_hooks/tests/ -v
```
