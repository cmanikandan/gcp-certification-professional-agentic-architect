# Module 01: Understand Google Cloud Agents & Architecture

## Overview
This module establishes the foundational architectural principles of Google Cloud AI agents, covering the spectrum from low-code state machines to autonomous generative agents.

---

## 🎯 Exam Objectives Covered
- **1.1 Configuring agentic workflows and behavior using low-code tools**
  - Distinguishing deterministic state-based workflows (pages, transition routes, event handlers) from autonomous agentic loops.
  - Selecting between Gemini Enterprise Agent Designer, Customer Experience Agent Studio (CX Agent Studio), and Custom Code.
- **Scope & Terminology**:
  - **Deterministic Workflow**: Predefined, graph-based execution paths with hardcoded transition conditions.
  - **Autonomous Agent**: Goal-oriented LLM loops utilizing perception, internal chain-of-thought reasoning, dynamic tool selection, and reflection.

---

## 🏗️ Architecture Comparison

```mermaid
graph TD
    subgraph Deterministic ["Low-Code Deterministic State Machine (CX Agent Studio)"]
        D_Start[Start Page] -->|Intent Match: Return Item| D_Page1[Page: Return Policy Validation]
        D_Page1 -->|Condition: Receipt Provided| D_Page2[Page: Issue Refund]
        D_Page1 -->|Event: No Match| D_Fallback[Event Handler: Fallback Page]
    end

    subgraph Autonomous ["Autonomous Custom Agent (Gemini 3.7 Flash)"]
        A_User[User Goal: Process complex return] --> A_Reason[Perception & Thinking Mode]
        A_Reason -->|Select Tool| A_Tool[Dynamic Tool: Query Policy DB]
        A_Tool --> A_Observe[Observe Tool Output]
        A_Observe --> A_Reflect{Goal Complete?}
        A_Reflect -->|No| A_Reason
        A_Reflect -->|Yes| A_Response[Final Grounded Response]
    end
```

---

## 💡 Key Architectural Trade-Offs

| Dimension | CX Agent Studio / Agent Designer | Custom ADK Agent (Code) |
| :--- | :--- | :--- |
| **Developer Persona** | Business analysts, support engineers, low-code builders | Software engineers, AI architects |
| **Control & Determinism** | 100% deterministic state transitions and guardrails | Dynamic reasoning, non-linear goal execution |
| **Tool Flexibility** | Preconfigured webhooks and Agent Search connectors | Arbitrary Python/gRPC/MCP tools and distributed services |
| **Deployment Model** | Fully managed Google Cloud console platform | Agent Runtime, Cloud Run, or GKE containers |

---

## 🚀 Hands-on Lab: Running the Module

### 1. Run the Standalone Demo
```bash
python3 modules/01_understand_agents_and_architecture/agent_architecture_demo.py
```

### 2. Run the Unit Tests
```bash
pytest modules/01_understand_agents_and_architecture/tests/ -v
```
