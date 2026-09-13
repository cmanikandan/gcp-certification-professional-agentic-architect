# Track 3 — Developing Custom Agents

**Exam Section:** 3. Developing custom agents (~33% of the exam)

This is the single largest and most critical section of the Professional Agentic Architect exam. It covers the core coding primitives used to construct, coordinate, and scale agentic applications.

In this track, we build entirely in code using the **Agent Development Kit (ADK)** (`google-adk`). We move away from the low-code consoles of Track 1 and the CLI-driven sandboxes of Track 2, focusing instead on Python-based agent architectures.

## Labs in this track

- **[Lab 07 — Model Selection](lab_07_model_selection/README.md)**: Objective 3.1. Choosing the right engine for the agent (LLM vs. SLM, OSS vs. proprietary) and understanding the ADK model classes (`Gemini`, `Gemma`, `LiteLlm`, `Gemma3Ollama`, `Claude`, `FallbackModel`).
- **[Lab 08 — ADK Fundamentals](lab_08_adk_fundamentals/README.md)**: Objective 3.1. The foundational mechanics of the ADK: `LlmAgent`, instructions, schemas, routing, and the `adk` CLI. We cover both workflow agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`) and the graph-based `Workflow` engine.
- **[Lab 09 — Sessions and Memory](lab_09_sessions_and_memory/README.md)**: Objective 3.1. Distinguishing short-term session state from long-term memory across conversations, and implementing the managed services (Memorystore, Vertex AI Session Service, Agent Platform Memory Bank).
- **[Lab 10 — Tools and Skills](lab_10_tools_and_skills/README.md)**: Objectives 3.1 & 3.2. Equipping agents with functions, MCP tools, and external knowledge via the Skill Registry (`Skill`, `Frontmatter`).
- **[Lab 11 — RAG and Retrieval](lab_11_rag_and_retrieval/README.md)**: Objective 3.2. Designing RAG pipelines, choosing embedding models, and understanding the retrieval services (Agent Search, RAG Engine).
- **[Lab 12 — Multi-Agent and A2A](lab_12_multi_agent_and_a2a/README.md)**: Objective 3.3. Coordinating multi-agent systems via direct delegation, graph workflows, and standardized agent-to-agent (A2A) protocols.
