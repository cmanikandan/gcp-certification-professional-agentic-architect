# Track 1 — Building agents using low-code tools

> **Personal study repo — not affiliated with Google Cloud.** Official guidance: [cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect) · [Disclaimer](../../DISCLAIMER.md)

**Exam weight:** ~13%
**Key products:** Gemini Enterprise, Agent Designer, CX Agent Studio

This track covers Section 1 of the GCP Professional Agentic Architect exam. The focus here is on **configuration over code**.

The tools covered in this track (Agent Designer, CX Agent Studio) are **console products** with no native ADK (Python SDK) surface. Because the exam tests your architectural judgement, the hands-on labs in this track implement a *simulator* in Python. This lets you run deterministic experiments and see the state-machine transitions that power the console products.

## The Labs

### [Lab 1: Agent Designer Workflows](./lab_01_agent_designer_workflows/)
Covers objective 1.1 (prompt templates, system instructions).
Learn how to define an agent's persona and tools using low-code paradigms. Explores the critical architectural decision of **low-code vs code-first** and demonstrates prompt-template patterns (few-shot vs chain-of-thought) deterministically.

### [Lab 2: CX Agent Studio State](./lab_02_cx_agent_studio_state/)
Covers objective 1.1 (state-based workflows).
This is the **key lab** for Section 1. It teaches the state-machine primitives: pages, transition routes, and event handlers. Crucially, it covers the exam favourite: **deterministic state machine vs generative playbook**. 

### [Lab 3: Enterprise Data & Multimodal](./lab_03_enterprise_data_and_multimodal/)
Covers objective 1.2 (Agent Search, unstructured multimodal data).
Learn how to securely connect enterprise data stores, focusing on **ACL-aware search and identity propagation**. It also covers the trade-offs between **native multimodal prompting vs pre-processing pipelines**.

---

> [!WARNING]
> **Pre-GA / naming note.** The exam guide refers to *Gemini Enterprise Agent Designer* and *CX Agent Studio*. These are console-centric configuration interfaces. The labs simulate their behaviour using Python to give you a concrete, testable understanding of how they work under the hood.
