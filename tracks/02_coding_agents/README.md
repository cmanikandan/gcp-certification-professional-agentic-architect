# Track 2 — Using coding agents for application development

> **Personal study repo — not affiliated with Google Cloud.** Official guidance: [cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect) · [Disclaimer](../../DISCLAIMER.md)

**Exam Section:** 2 (~17% of the exam)

This track covers how to harness autonomous coding agents inside Google Cloud to build applications, while securing their access boundaries and execution environments. A core principle of the GCP Agentic Architect exam is that agents write and run code—but they must be strictly governed and cleanly integrated.

## Objectives Covered
*   **2.1 Using coding agents effectively**
    *   Configuring coding agents with Model Context Protocol (MCP) servers, custom skills, and access to tools (e.g., Antigravity and Claude Code on Google Cloud).
    *   Using coding agents in secure sandboxes (e.g., GKE, Cloud Workstations, and Antigravity).
    *   Using coding agents to refactor source code, optimize execution runtimes, and patch application-layer vulnerabilities.
*   **2.2 Customizing coding agents for enterprise workflows**
    *   Creating skills, plugins, extensions hooks, rules, and subagents using Antigravity.
    *   Augmenting Antigravity with Agents CLI to build, scale, govern, and optimize deployed agents.

## Labs in this Track

| Lab | Title | Focus |
| :--- | :--- | :--- |
| **Lab 04** | [MCP and Tooling](lab_04_mcp_and_tooling/README.md) | Standardizing tool integration using the Model Context Protocol (MCP) (vs custom plugins), and exposing Google Cloud resources safely via the `google.adk.tools` and `mcp` APIs. |
| **Lab 05** | [Secure Sandboxes](lab_05_secure_sandboxes/README.md) | The architectural decisions behind safe code execution. Evaluates `GkeCodeExecutor`, `CloudRunSandboxCodeExecutor`, and other ADK implementations to understand runtime isolation, networking limits, and when to use which. |
| **Lab 06** | [Antigravity Customization](lab_06_antigravity_customization/README.md) | The anatomy of Antigravity customization: creating skills, rules, and plugins. Using the real ADK `SkillRegistry` API to parse and execute agent instructions. |
