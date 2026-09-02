# Google Cloud Certified Professional Agentic Architect — Exam Blueprint & Syllabus

> [!IMPORTANT]
> **Unofficial Blueprint Notice**:
> This blueprint is an **unofficial** educational overview. For official beta registration and authoritative syllabus updates, please visit the [Google Cloud Certification Portal](https://cloud.google.com/certification) and [Google Cloud Skills Boost](https://www.cloudskillsboost.google/).

## Overview
The **Google Cloud Certified Professional Agentic Architect** certification validates the expertise required to design, develop, deploy, secure, and govern enterprise-grade autonomous AI agents and multi-agent systems on Google Cloud.

- **Exam logistics**: The exam guide used for this repository does not specify duration, question count, delivery format, or a passing score. Confirm current logistics on the official registration page rather than relying on unofficial figures.
- **Prerequisites**: Deep understanding of LLM architectures, Google Cloud compute/data/security services, Agent Development Kit (ADK), Antigravity, Model Context Protocol (MCP), and Agent2Agent (A2A) orchestration.

---

## Domain Weighting & Module Cross-Reference

| Domain | Exam Weight | Description | Covered Modules |
| :--- | :---: | :--- | :--- |
| **Section 1: Building agents using low-code tools** | **13%** | Gemini Enterprise Agent Designer, Customer Experience Agent Studio (CX Agent Studio), state machines, prompt templates, enterprise multimodal ingestion. | **Module 01, Module 04** |
| **Section 2: Using coding agents for application development** | **17%** | Antigravity CLI/IDE/SDK, Claude Code on GCP, MCP servers, custom skills, sandboxed environments (GKE, Cloud Workstations), runtime refactoring, vulnerability patching. | **Module 02, Module 08** |
| **Section 3: Developing custom agents** | **33%** | Custom agent development with ADK, model selection (LLM vs SLM, Gemini 3.7 Flash), memory banks & sessions, enterprise RAG, Vector Search 1.0, MCP Toolbox, Agent2Agent (A2A) multi-agent orchestration. | **Module 03, Module 05, Module 06, Module 07, Module 09, Module 10, Module 11** |
| **Section 4: Evaluating and deploying agentic workflows** | **22%** | Golden test sets, ADK evalset tooling, autoraters, continuous evaluation, deployment runtimes (Agent Runtime, Cloud Run, GKE), troubleshooting drift & reasoning loops, Cloud Logging/Trace. | **Module 12, Module 13** |
| **Section 5: Securing and governing agentic workflows** | **15%** | OAuth 2.0 Auth Manager, Principal Access Boundary (PAB) via Agent Identity, Agent Gateway, Model Armor guardrails, Agent Registry, Human-In-The-Loop (HITL). | **Module 13** |

---

## Detailed Exam Objectives Breakdown

### Section 1: Building agents using low-code tools (~13%)
- **1.1 Configuring agentic workflows and behavior using low-code tools**:
  - Configuring state-based workflows: pages, transition routes, and event handlers in Gemini Enterprise Agent Designer and Customer Experience Agent Studio (CX Agent Studio).
  - Designing system instructions and in-console prompt templates: zero-shot, few-shot, and chain-of-thought (CoT) patterns to steer agent behavior. For production telemetry, retain concise decisions and tool traces rather than private scratchpad text.
  - Defining fallback handlers, intent classification, and entity extraction in low-code builders.
- **1.2 Connecting enterprise data to Gemini Enterprise**:
  - Securely connecting proprietary data stores (BigQuery, Cloud Storage, Google Drive, Third-party SaaS).
  - Ingesting and processing unstructured multimodal data (videos, high-res images, audio recordings, PDFs) into agentic reasoning flows.
  - Leveraging Agent Search (formerly Vertex AI Search) for zero-code grounding and citations.

---

### Section 2: Using coding agents for application development (~17%)
- **2.1 Using coding agents effectively**:
  - Configuring coding agents with Model Context Protocol (MCP) servers, custom skills, and environment tools (Antigravity and Claude Code on Google Cloud).
  - Executing coding agents inside isolated and secure sandboxes (Google Kubernetes Engine [GKE], Cloud Workstations, and Antigravity sandboxes).
  - Leveraging coding agents for automated source code refactoring, runtime performance optimization, and application-layer security vulnerability remediation.
- **2.2 Customizing coding agents for enterprise workflows**:
  - Creating custom skills (`SKILL.md`), plugins, extensions hooks, rules (`GEMINI.md`/`AGENTS.md`), and subagents in Antigravity.
  - Utilizing Agents CLI to build, test, version, govern, and optimize deployed developer agents.

---

### Section 3: Developing custom agents (~33%)
- **3.1 Designing and building agentic workflows in code**:
  - Selecting language models: LLM (Gemini 3.7 Flash / Gemini 2.5 Pro) vs. SLM (Gemma 2 2B/9B/27B via LiteRT / Vertex Model Garden), SaaS vs self-hosted OSS, balancing cost, latency, thinking token budgets, and security.
  - Building custom autonomous agents using open-source libraries: Agent Development Kit (ADK) and Google GenAI SDK.
  - Configuring session persistence and memory: Agent Platform Memory Bank, managed sessions, short-term context pruning vs long-term semantic retrieval.
  - Managing skills via Agents CLI (plugins, agent vs human mode).
- **3.2 Integrating enterprise domain knowledge**:
  - Designing end-to-end RAG pipelines and vector retrieval: embedding generation (`text-embedding-005`, `multimodalembedding`), similarity scoring (Cosine, Dot Product, Euclidean), and cross-encoder reranking.
  - Implementing vector databases with Vector Search 1.0, Agent Retrieval, and Vertex RAG Engine.
  - Configuring agent permissions and IAM boundaries with Agent Identity.
  - Integrating Google Cloud MCP Servers / MCP Toolbox for Databases (BigQuery, Cloud SQL, AlloyDB, Spanner) and SaaS API integrations.
- **3.3 Orchestrating and coordinating agentic workflows**:
  - Implementing agentic protocols: Model Context Protocol (MCP) and Agent2Agent (A2A).
  - Multi-agent coordination patterns: Sequential pipelines, parallel execution, hierarchical supervisors, and state-graph workflows.
  - Managing handoffs, contextual memory sharing, and dynamic routing using Agent Identity, Agent Registry, Agent Runtime, and agent policies.

---

### Section 4: Evaluating and deploying agentic workflows (~22%)
- **4.1 Evaluating agents in development and in production**:
  - Constructing golden evaluation datasets (curated prompts, edge cases, multi-turn dialogues, adversarial inputs).
  - Continuous evaluation pipelines using ADK evaluation tooling (`evalset`), Agent Platform Gen AI evaluation service, and LLM-as-a-judge autoraters.
  - Measuring quantitative agent metrics: tool selection accuracy, argument precision, retrieval faithfulness, answer relevance, and task completion rate.
- **4.2 Deploying and scaling production workloads**:
  - Selecting optimal execution runtimes: Agent Runtime (formerly Agent Engine), Cloud Run (serverless containerized), and GKE (high-scale custom clusters).
  - Troubleshooting agent failures: semantic drift, tool invocation latency, infinite reasoning loops, context window overflow, and API rate limits.
  - Observability and monitoring: Cloud Logging, Cloud Trace, OpenTelemetry spans, latency bottleneck profiling, and hallucination mitigation.

---

### Section 5: Securing and governing agentic workflows (~15%)
- **5.1 Configuring agent security and governance**:
  - Authentication and authorization: Agent-to-tool API security using OAuth 2.0 and Google Auth Manager.
  - Configuring Principal Access Boundary (PAB) policies via Agent Identity to enforce strict least-privilege scoping.
  - Deploying Agent Gateway for centralized traffic routing, agent telemetry, and policy enforcement.
  - Registering and auditing agents in Agent Registry with Model Armor content inspection.
- **5.2 Implementing secure agent behavior and execution**:
  - Implementing multi-layer safety guardrails: Model Armor (prompt injection defense, jailbreak detection, PII redacting via Cloud DLP / Sensitive Data Protection).
  - Integrating Human-in-the-Loop (HITL) approval gates for high-stakes tool execution (financial transactions, data deletion, production deployments).
  - Ensuring secure identity propagation across distributed multi-agent handoffs.

---

## Official Tools in Scope

```
- Agent Development Kit (ADK)           - Gemini Enterprise
- Agent Evaluation (evalset)            - Gemini LLMs (Gemini 3.7 Flash, Gemini 2.5 Pro)
- Agent Gateway                         - Google Cloud Observability (Cloud Logging, Trace)
- Agent Identity (PAB)                  - Google Kubernetes Engine (GKE)
- Agent Registry                        - Memorystore for Redis
- Agent Retrieval & Vector Search 1.0   - Model Armor
- Agent Runtime (formerly Agent Engine) - Model Context Protocol (MCP) servers & Toolbox
- Agent Search (Vertex AI Search)       - Model Garden (Gemma 2, Llama 3)
- Agentic Protocols (A2A, MCP)          - RAG Engine
- Agents CLI in Agent Platform          - Sensitive Data Protection (Cloud DLP)
- Antigravity (CLI, SDK, IDE, App)      - Skill Registry
- Auth Manager (OAuth 2.0)              - Cloud Run / Cloud Functions
- BigQuery                              - Cloud Storage
- Cloud SQL                             - Firestore
```
