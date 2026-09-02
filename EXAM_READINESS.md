# Exam Readiness Map

This map is based on the official Professional Agentic Architect exam guide downloaded on 2 September 2026. Product names and exam policies can change, so re-check the [official exam guide](https://services.google.com/fh/files/misc/professional_agentic_architect_exam_guide_english.pdf) before booking.

The guide weights the domains at 13% / 17% / 33% / 22% / 15%. Allocate practice time in approximately the same ratio; do not spend half your preparation on the visually interesting multi-agent material while neglecting evaluation and governance.

## Objective-to-lab coverage

| Official objective | What you must be able to explain or do | Lab evidence |
| --- | --- | --- |
| 1.1 Low-code workflows | Model pages, transition routes, event handlers, system instructions, prompt templates, few-shot examples, and deterministic escalation | Module 01 state machine; Module 04 prompt and loop lab |
| 1.2 Enterprise data | Choose secure connectors and an ingestion/grounding path for proprietary text, image, audio, video, and PDF sources | Module 01 multimodal connection planner; Module 09 grounding lab |
| 2.1 Coding agents | Configure tools/MCP/skills, enforce a sandbox boundary, refactor code, patch vulnerabilities, and verify the result | Module 02 sandbox and remediation lab; Modules 07 and 10 |
| 2.2 Enterprise customization | Explain skills, plugins, hooks, rules, subagents, Agents CLI modes, versioning, and Skill Registry governance | Module 08 skill registry and execution-mode lab |
| 3.1 Custom agents | Select LLM/SLM and hosted/self-hosted options; build structured agents; manage sessions/memory; configure skills | Modules 03, 05, 06, and 08 |
| 3.2 Domain knowledge | Build RAG, select embeddings/similarity/reranking, enforce Agent Identity permissions, and integrate databases/SaaS through MCP | Modules 09, 10, and 13 |
| 3.3 Orchestration | Distinguish MCP from A2A and select sequential, parallel, supervisor, or graph coordination with governed handoffs | Module 11; Module 13 registry/identity policy chain |
| 4.1 Evaluation | Create golden and edge-case sets, score tool use and retrieval/response quality, and gate releases continuously | Module 12 continuous evaluation gate |
| 4.2 Deployment | Choose Agent Runtime, Cloud Run, or GKE; diagnose drift, latency, loops, and system failures; trace cost/reliability | Modules 04, 12, and 13 runtime selector |
| 5.1 Governance | Apply OAuth 2.0, Agent Identity PAB, Agent Gateway, Agent Registry, and Model Armor as distinct layers | Module 13 end-to-end policy chain |
| 5.2 Secure behavior | Combine guardrails, secure identity/data propagation, and HITL for consequential actions | Module 13 Model Armor and approval gate |

## High-yield distinctions

- MCP connects an agent or model-facing client to tools and context. A2A coordinates work and handoffs between independently addressable agents.
- IAM allow policy grants access. A Principal Access Boundary sets the maximum resource boundary for a principal; it does not grant access. VPC Service Controls is a separate data-exfiltration perimeter.
- Agent Registry is inventory, version, ownership, and policy metadata. Agent Gateway is the traffic enforcement and observability point. Agent Identity is the workload principal.
- Agent Runtime is the managed agent-specific choice. Cloud Run is the portable serverless container choice. GKE is for Kubernetes-level control, specialized networking, or custom scheduling.
- Sessions preserve an active interaction. Memory Bank supports durable, cross-session recall. A cache is an optimization, not authoritative conversational memory.
- Retrieval quality and response quality are separate. Evaluate retrieval relevance/groundedness as well as task completion, tool choice, tool arguments, safety, latency, and cost.
- Model Armor inspects content; OAuth authenticates/delegates; IAM/PAB authorizes and bounds resources; HITL controls consequential actions. No single layer replaces the others.
- The exam guide includes chain-of-thought prompting as a concept. In production, do not require or log private model scratchpads; ask for concise, auditable decisions and tool traces.

## Readiness gates

You are ready to schedule only when all of these are true:

1. `./scripts/verify_labs.sh` passes from a clean clone.
2. You can complete each lab without reading its implementation first, then explain why the alternative services are weaker for that scenario.
3. You score at least 85% twice on scenario questions, including multiple-select questions, with at least 75% in every domain.
4. For every missed question, you can name the misleading distractor and the requirement that eliminates it.
5. You can draw the identity-to-gateway-to-tool authorization path and the prompt-to-retrieval-to-evaluation path from memory.

These gates improve preparation but cannot guarantee an exam result.
