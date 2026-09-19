# Exam readiness map

> [!IMPORTANT]
> **Personal, unofficial repository.** This is a personal study project. It is **not
> affiliated with, endorsed by, or maintained by Google or Google Cloud**. For official
> guidance — exam objectives, registration, policies, and the current exam guide — refer to
> **[cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect)**.
> Where anything here disagrees with the official source, **the official source is correct**.
> See [`DISCLAIMER.md`](DISCLAIMER.md) for the full disclaimer.

A self-assessment instrument, not a reading list. Every row is a **capability**, phrased as
something you can do *without looking it up*, and mapped to the lab that proves it.

Based on the official
[Professional Agentic Architect exam guide](https://services.google.com/fh/files/misc/professional_agentic_architect_exam_guide_english.pdf).
This is a **beta** exam — product names and policies move. Re-check the guide before you book.

> [!IMPORTANT]
> The guide weights the sections **13% / 17% / 33% / 22% / 15%**. Allocate practice time in roughly
> the same ratio. The common failure mode is spending half your preparation on the visually
> interesting multi-agent material and neglecting evaluation, deployment and governance — which
> together are **37%** of the paper.

---

## Section 1 — Building agents using low-code tools · 13%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Choose between zero-shot, few-shot and chain-of-thought prompting, and say what each costs | [Lab 01](tracks/01_low_code_agents/lab_01_agent_designer_workflows) |
| ☐ | Explain pages, intents, transition routes and event handlers, and which one handles a retry limit | [Lab 02](tracks/01_low_code_agents/lab_02_cx_agent_studio_state) |
| ☐ | Connect enterprise data to Gemini Enterprise App (`GEApp`), distinguish `GEApp` from the `Gemini Enterprise` umbrella and `Agent Platform (GEAP)`, and say when Agent Search is the right answer | [Lab 03](tracks/01_low_code_agents/lab_03_enterprise_data_and_multimodal) |
| ☐ | Decide when a low-code tool is *sufficient* and when the requirement forces custom code | [Track 1](tracks/01_low_code_agents/) |

## Section 2 — Using coding agents for application development · 17%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Explain what MCP is, and wire an agent to an MCP server with a toolset | [Lab 04](tracks/02_coding_agents/lab_04_mcp_and_tooling) |
| ☐ | Rank the code executors by isolation strength, and explain why GKE `job` and `sandbox` (gVisor `runsc`) differ | [Lab 05](tracks/02_coding_agents/lab_05_secure_sandboxes) |
| ☐ | Explain how **Code Mender** automates vulnerability root-cause analysis, fuzzing, and sandboxed patch verification | [Lab 05](tracks/02_coding_agents/lab_05_secure_sandboxes) |
| ☐ | Say why `UnsafeLocalCodeExecutor` must never reach production, in one sentence | [Lab 05](tracks/02_coding_agents/lab_05_secure_sandboxes) |
| ☐ | Govern a coding agent with rules, skills and an `allowed_tools` allowlist | [Lab 06](tracks/02_coding_agents/lab_06_antigravity_customization) |

## Section 3 — Developing custom agents · 33% ⭐

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Pick between Pro, Flash and Lite from a latency/cost/reasoning requirement | [Lab 07](tracks/03_custom_agents/lab_07_model_selection) |
| ☐ | Say when open-weights (Gemma 4 on GKE GPUs) beats a hosted model, and what it costs you operationally | [Lab 07](tracks/03_custom_agents/lab_07_model_selection), [Lab 19](tracks/04_evaluate_and_deploy/lab_19_gke_inference_gateway_and_gpus) |
| ☐ | Write an `LlmAgent` from a blank file — instruction, tools, `output_schema`, `output_key` | [Lab 08](tracks/03_custom_agents/lab_08_adk_fundamentals) |
| ☐ | Choose between a workflow agent and the graph `Workflow`, and state the deprecation nuance | [Lab 08](tracks/03_custom_agents/lab_08_adk_fundamentals) |
| ☐ | Distinguish **session state** from **memory**, and say which survives a restart | [Lab 09](tracks/03_custom_agents/lab_09_sessions_and_memory) |
| ☐ | Choose between Memory Bank and RAG memory, and justify it | [Lab 09](tracks/03_custom_agents/lab_09_sessions_and_memory) |
| ☐ | Distinguish a **tool** from a **skill**, and explain what a Skill Registry adds | [Lab 10](tracks/03_custom_agents/lab_10_tools_and_skills) |
| ☐ | Implement a human-in-the-loop pause with a long-running tool | [Lab 10](tracks/03_custom_agents/lab_10_tools_and_skills) |
| ☐ | Choose between Agent Search, RAG Engine, a vector store, and long-context stuffing | [Lab 11](tracks/03_custom_agents/lab_11_rag_and_retrieval) |
| ☐ | Explain chunking, embedding choice, re-ranking and citation checking as hallucination controls | [Lab 11](tracks/03_custom_agents/lab_11_rag_and_retrieval) |
| ☐ | Say when **A2A** beats in-process `sub_agents` — and it is not "when there are many agents" | [Lab 12](tracks/03_custom_agents/lab_12_multi_agent_and_a2a) |
| ☐ | Describe the A2A task handshake and what an Agent Card advertises | [Lab 12](tracks/03_custom_agents/lab_12_multi_agent_and_a2a) |
| ☐ | Explain how Agent Registry ties discovery, MCP (`get_mcp_toolset`) and A2A (`get_remote_a2a_agent`) together | [Lab 12](tracks/03_custom_agents/lab_12_multi_agent_and_a2a) |

## Section 4 — Evaluating and deploying agentic workflows · 22%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Distinguish **trajectory** evaluation (`trajectory_evaluator`) from **final-response** and **hallucination** evaluation (`hallucinations_v1`), and say when each fails | [Lab 13](tracks/04_evaluate_and_deploy/lab_13_agent_evaluation) |
| ☐ | Build an eval set and run `adk eval`; explain why the judge should out-rank the agent | [Lab 13](tracks/04_evaluate_and_deploy/lab_13_agent_evaluation) |
| ☐ | State the exact **limitations of Agent Runtime** (`adk deploy agent_engine`) and when you **must choose GKE** instead | [Lab 14](tracks/04_evaluate_and_deploy/lab_14_deployment_runtimes), [Lab 19](tracks/04_evaluate_and_deploy/lab_19_gke_inference_gateway_and_gpus) |
| ☐ | Name the `adk deploy` targets and what changes about session persistence on each | [Lab 14](tracks/04_evaluate_and_deploy/lab_14_deployment_runtimes) |
| ☐ | Configure **GKE Inference Gateway** (`InferencePool`, `InferenceModel`) for KV-cache/prefix-cache affinity, LoRA multiplexing, and criticality load-shedding on GPU pools | [Lab 19](tracks/04_evaluate_and_deploy/lab_19_gke_inference_gateway_and_gpus) |
| ☐ | Attribute latency between model (`trace_call_llm`) and tool (`trace_tool_call`) in Cloud Trace, and spot a runaway loop | [Lab 15](tracks/04_evaluate_and_deploy/lab_15_observability_and_troubleshooting) |
| ☐ | Say what to alert on for an agent that generic APM would miss, and configure `ContentCapturingMode` safely | [Lab 15](tracks/04_evaluate_and_deploy/lab_15_observability_and_troubleshooting) |
| ☐ | Explain conformance replay (`adk conformance record` / `test`) as regression testing | [Lab 15](tracks/04_evaluate_and_deploy/lab_15_observability_and_troubleshooting) |

## Section 5 — Securing and governing agentic workflows · 15%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Explain Agent Identity, and why a Principal Access Boundary (PAB) caps blast radius (`IAM Allow ∩ PAB`) | [Lab 16](tracks/05_secure_and_govern/lab_16_agent_identity_and_auth), [Lab 20](tracks/05_secure_and_govern/lab_20_e2e_ai_threat_defense) |
| ☐ | Describe identity propagation, and what breaks when an agent acts as itself instead of the user | [Lab 16](tracks/05_secure_and_govern/lab_16_agent_identity_and_auth) |
| ☐ | Configure Model Armor fail-closed vs fail-open, and name the flag (`block_on_screening_failure`) that does it | [Lab 17](tracks/05_secure_and_govern/lab_17_model_armor_and_hitl) |
| ☐ | Explain why prompt injection is not solved by prompt engineering | [Lab 17](tracks/05_secure_and_govern/lab_17_model_armor_and_hitl) |
| ☐ | Wire the end-to-end AI Threat Defense path: **Agent Identity (PAB) → Agent Gateway → Agent Registry → Model Armor → Agent → GKE Sandbox** | [Lab 18](tracks/05_secure_and_govern/lab_18_governance_gateway_registry), [Lab 20](tracks/05_secure_and_govern/lab_20_e2e_ai_threat_defense) |
| ☐ | Explain what an Agent Registry gives you that a list of URLs does not | [Lab 18](tracks/05_secure_and_govern/lab_18_governance_gateway_registry) |

---

## Score yourself

Count the ticks per section, then weight them. A section you have half-learned is more dangerous
than one you have not started, because you will not know to revise it.

| Section | Ticks | Out of | % | Exam weight |
| :--- | ---: | ---: | ---: | ---: |
| 1. Low-code tools | | 4 | | 13% |
| 2. Coding agents | | 5 | | 17% |
| 3. Custom agents | | 13 | | 33% |
| 4. Evaluate & deploy | | 8 | | 22% |
| 5. Secure & govern | | 6 | | 15% |
| **Total** | | **36** | | **100%** |

| Overall | Verdict |
| :--- | :--- |
| **32–36** | Ready. Spend the remaining time on your lowest-scoring *section*, not your lowest-scoring total. |
| **26–31** | Nearly. Identify the weakest section and redo those labs on the live path, not just offline. |
| **18–25** | Not yet. Work Tracks 3 and 4 first — 55% of the exam — then reassess. |
| **0–17** | Do not book yet. Complete every lab once, then take the practice exam cold. |

Then take [`PRACTICE_EXAM.md`](PRACTICE_EXAM.md) (75 questions, matching the 3-hour live exam length) under timed conditions. **≥80% is the target.**
Score it per section: a 75-question paper weighted like the real one will expose an imbalance that
a single overall percentage hides.

---

## You are not ready if...

These are hard blockers. Any one of them will cost you multiple questions.

- You cannot state the difference between **MCP** (connecting an agent to *tools*) and **A2A**
  (connecting an agent to *other agents*).
- You think **more agents** is the trigger for adopting A2A. The trigger is a **boundary** —
  process, network, team or organisation.
- You believe an IAM grant is equivalent to a **Principal Access Boundary**. One says what an
  identity *may* do; the other caps what it can *ever* do.
- You cannot draw the request path: **identity → gateway → Model Armor → agent → tool → sandbox**.
- You think prompt engineering mitigates **prompt injection**.
- You would run `UnsafeLocalCodeExecutor` anywhere near production.
- You cannot explain what **session state** holds that **memory** does not.
- You evaluate only the final answer and never the **trajectory**.
- You pin production to a floating alias such as `gemini-flash-latest` and cannot explain the risk.
- You use the term *Agent Engine* in an answer where the guide says **Agent Runtime**.

---

## Final week

| When | Focus | Why |
| :--- | :--- | :--- |
| **Day 7–5** | Track 3 (33%) — rebuild labs 08–12 from scratch, not by reading | Recognition is not recall; the exam tests recall under a scenario |
| **Day 4–3** | Track 4 (22%) — run `adk eval`, walk the deployment decision tree aloud | These two tracks are 55% of the paper |
| **Day 2** | Track 5 (15%), then Tracks 1–2 (30%) | Governance is small but heavily trapped |
| **Day 1** | Practice exam cold and timed. Score per section. Revisit only the weakest | Do not learn anything new today |

## The day before

- Re-read the decision trees and the "most likely tested distinctions" table in
  [`STUDY_GUIDE.md`](STUDY_GUIDE.md).
- Re-read the renamed-products glossary: **Agent Runtime**, **Agent Search**, **Agent Registry**,
  **Agent Gateway**. Using the old name in your head is how you misread a question stem.
- Skim [`docs/VERIFIED_FACTS.md`](docs/VERIFIED_FACTS.md) for the model catalog.
- Do not start a new lab. Sleep.
