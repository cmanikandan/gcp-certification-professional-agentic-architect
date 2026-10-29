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
[Professional Agentic Architect exam guide](https://services.google.com/fh/files/misc/professional_agentic_architect_exam_guide_english.pdf)
and calibrated with **Beta exam** feedback.

> [!NOTE]
> **Exam Format & Timeline Reminder**:
> - **Beta Exam**: **~80 multiple-choice / multiple-select questions** (3 hours).
> - **GA Exam (launches mid-November)**: **Question count will be lesser** (standard ~50–60 questions, 2 hours).
> - **Delivery & UI**: Online-proctored or onsite-proctored; includes **Mark for Review** and **Strike-through**.
> - **Weighting**: Official domain weights are **13% / 17% / 33% / 22% / 15%**, with **~30–35% of questions overall** testing **IAM roles, least-privilege permissions, credential provisioning, and identity boundaries** inside those five sections.

---

## Section 1 — Building agents using low-code tools · 13%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Choose between zero-shot, few-shot, and chain-of-thought prompt templates in Agent Designer, and enforce customer support / HIPAA topical guardrails | [Lab 01](tracks/01_low_code_agents/lab_01_agent_designer_workflows) |
| ☐ | Distinguish **GECX (CX Agent Studio) Deterministic Flows** (`Pages`, required `Form` parameters, `Transition Routes`, `sys.no-match-2` Event Handlers) from **Probabilistic Playbooks** and **Hybrid** support flows | [Lab 02](tracks/01_low_code_agents/lab_02_cx_agent_studio_state) |
| ☐ | Configure **Gemini Enterprise (`GEApp`) connector auth**: ACL-sync Service Account + Workforce Identity Federation for search vs. **3-legged OAuth 2.0 (3LO)** via Auth Manager (`IAMConnectorCredentialsServiceClient`) for user actions | [Lab 03](tracks/01_low_code_agents/lab_03_enterprise_data_and_multimodal) |
| ☐ | Ingest multimodal `gs://` assets (PDF, audio, image, MP4 video) natively into `gemini-3.7-flash` with least-privilege `roles/storage.objectViewer` & `roles/discoveryengine.viewer` | [Lab 03](tracks/01_low_code_agents/lab_03_enterprise_data_and_multimodal) |

## Section 2 — Using coding agents for application development · 17%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Configure local Stdio vs. remote SSE MCP servers (`mcp_config.json`), lazy tool loading, and **Claude Code on Google Cloud** using Vertex AI ADC (`roles/aiplatform.user`) | [Lab 04](tracks/02_coding_agents/lab_04_mcp_and_tooling) |
| ☐ | Rank execution sandboxes by isolation: **GKE Agent Sandbox (`executor_type="sandbox"`, gVisor `runsc`)** vs. `job` mode vs. **Cloud Workstations** (VPC-SC IDE) vs. `CloudRunSandboxCodeExecutor` vs. `UnsafeLocalCodeExecutor` | [Lab 05](tracks/02_coding_agents/lab_05_secure_sandboxes) |
| ☐ | Explain how **Code Mender** localizes CVEs, synthesizes patches, and runs fuzz/regression verification inside a GKE Agent Sandbox | [Lab 05](tracks/02_coding_agents/lab_05_secure_sandboxes) |
| ☐ | Distinguish Antigravity's **`GEMINI.md` / `AGENTS.md`** (always-on walk-up), **`.agents/rules/*.md`** (`glob` / `model_decision`), **`SKILL.md` + `skills.json`** (L1/L2/L3), **`plugin.json`**, and **`hooks.json`** (`PreToolUse`, `PostToolUse`, `Stop`) | [Lab 06](tracks/02_coding_agents/lab_06_antigravity_customization) |
| ☐ | State Antigravity SDK `policy` precedence (`DENY > ASK > ALLOW`, fail-closed `when=`) and **Agents CLI (`adk`)** headless **Agent Mode** vs. interactive **Human Mode** (`adk optimize`) | [Lab 06](tracks/02_coding_agents/lab_06_antigravity_customization) |

## Section 3 — Developing custom agents · 33% ⭐

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Select between `gemini-3.7-flash`, `gemini-2.5-pro`, `gemini-3.5-flash-lite`, `FallbackModel`, and self-hosted `gemma-4-26b-a4b-it` / `gemma-4-31b-it` on GKE GPUs (including HIPAA/VPC-SC trade-offs) | [Lab 07](tracks/03_custom_agents/lab_07_model_selection), [Lab 19](tracks/04_evaluate_and_deploy/lab_19_gke_inference_gateway_and_gpus) |
| ☐ | Compare multi-agent **latency & token math** across `Workflow` (0ms routing), `SequentialAgent` ($\sum T_i$), `ParallelAgent` ($\max T_i$), `LoopAgent` + `exit_loop`, `transfer_to_agent` (1 hop), and `AgentTool` (2 parent hops), plus `include_contents='none'` + `output_key` | [Lab 08](tracks/03_custom_agents/lab_08_adk_fundamentals), [Lab 12](tracks/03_custom_agents/lab_12_multi_agent_and_a2a) |
| ☐ | State the exact ADK 2.9.0 `SequentialAgent` deprecation nuance (*`Workflow` cannot yet be nested inside `LlmAgent.sub_agents`*) | [Lab 08](tracks/03_custom_agents/lab_08_adk_fundamentals) |
| ☐ | Configure **Managed Sessions (`VertexAiSessionService`)** vs. `RedisSessionService` (`ttl_seconds`) / `DatabaseSessionService`, and **Memory Bank (`VertexAiMemoryBankService`)** `preload_memory` vs. `load_memory` | [Lab 09](tracks/03_custom_agents/lab_09_sessions_and_memory) |
| ☐ | Wire `BigQueryToolset`, `MCPToolset`, HITL (`request_input` / `get_user_choice`), and `GCPSkillRegistry` with exact least-privilege IAM (`roles/bigquery.jobUser` + `roles/bigquery.dataViewer`, `roles/secretmanager.secretAccessor`) | [Lab 10](tracks/03_custom_agents/lab_10_tools_and_skills) |
| ☐ | Design a two-stage RAG pipeline using **RAG Engine** (`RagCorpus`, `LayoutParserConfig`, `HybridSearch`, `gemini-embedding-2`) + **Discovery Engine Ranking API (`RankServiceClient`)**, and contrast with **Agent Search** and **Vector Search 1.0** | [Lab 11](tracks/03_custom_agents/lab_11_rag_and_retrieval) |
| ☐ | Architect **cross-project A2A** delegation using `RemoteA2aAgent`, `A2aRemoteAgentConfig`, Agent Cards, `AgentRegistry.get_remote_a2a_agent`, OIDC tokens, and service-level `roles/run.invoker` | [Lab 12](tracks/03_custom_agents/lab_12_multi_agent_and_a2a) |

## Section 4 — Evaluating and deploying agentic workflows · 22%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Distinguish **Metrics** (`ToolTrajectoryCriterion` / `trajectory_evaluator`, `final_response_match_v2`, `Rouge`) from reference-free **Rubrics** (`Rubric` + `RubricsBasedCriterion`, `rubric_based_final_response_quality_v1`, `hallucinations_v1`) | [Lab 13](tracks/04_evaluate_and_deploy/lab_13_agent_evaluation) |
| ☐ | Choose between local **`adk eval` (`evalset`)** / **`adk conformance`** for CI gating and cloud **Agent Platform Gen AI Evaluation Service** (`vertexai.evaluation.EvalTask`, `PairwiseMetric`, continuous drift monitoring) | [Lab 13](tracks/04_evaluate_and_deploy/lab_13_agent_evaluation), [Lab 15](tracks/04_evaluate_and_deploy/lab_15_observability_and_troubleshooting) |
| ☐ | State the exact boundaries of **Agent Runtime** (`adk deploy agent_engine`) vs. **Cloud Run** vs. **GKE**, and separate CI deployer IAM from runtime agent IAM (`roles/aiplatform.user`) | [Lab 14](tracks/04_evaluate_and_deploy/lab_14_deployment_runtimes) |
| ☐ | Configure **GKE Inference Gateway** (`InferencePool`, `InferenceModel`) for KV-cache/prefix-cache affinity, LoRA multiplexing, criticality load-shedding, and separate GPU vs. gVisor node pools | [Lab 19](tracks/04_evaluate_and_deploy/lab_19_gke_inference_gateway_and_gpus) |
| ☐ | Attribute latency across `trace_call_llm`, `trace_tool_call`, and `trace_merged_tool_calls` using `roles/cloudtrace.agent`, while disabling raw PHI/PII payload capture via **`ContentCapturingMode`** | [Lab 15](tracks/04_evaluate_and_deploy/lab_15_observability_and_troubleshooting) |

## Section 5 — Securing and governing agentic workflows · 15%

| ✓ | I can... without looking it up | Proven by |
| :--- | :--- | :--- |
| ☐ | Provision keyless credentials via **Agent Identity** (`GcpAuthProvider`, `AuthProviderCredentialsServiceClient`) and cap blast radius with a **Principal Access Boundary (PAB)** (`IAM Allow ∩ PAB`) | [Lab 16](tracks/05_secure_and_govern/lab_16_agent_identity_and_auth) |
| ☐ | Configure **Model Armor with Sensitive Data Protection (`SdpAdvancedConfig` `inspect_template` + `deidentify_template`)** and fail-closed `ModelArmorPlugin(block_on_screening_failure=True)` (`roles/modelarmor.user`) | [Lab 17](tracks/05_secure_and_govern/lab_17_model_armor_and_hitl) |
| ☐ | Contrast centralized **Agent Gateway + Model Armor** perimeter screening/OAuth propagation with in-agent `ModelArmorPlugin` mid-loop tool-output screening and **Agent Registry** allowlisting | [Lab 18](tracks/05_secure_and_govern/lab_18_governance_gateway_registry), [Lab 20](tracks/05_secure_and_govern/lab_20_e2e_ai_threat_defense) |
| ☐ | Design an end-to-end **HIPAA-compliant customer support agent** (BAA, VPC-SC, CMEK, SDP PHI de-identification, zero-capture `ContentCapturingMode`, PAB, and HITL gates) | [Lab 20](tracks/05_secure_and_govern/lab_20_e2e_ai_threat_defense) |

---

## Score yourself

| Section | Ticks | Out of | % | Official Exam Weight |
| :--- | ---: | ---: | ---: | ---: |
| 1. Low-code tools & GECX | | 4 | | 13% |
| 2. Coding agents & Antigravity | | 5 | | 17% |
| 3. Custom agents, RAG & A2A | | 7 | | 33% |
| 4. Evaluate, Runtime & GKE | | 5 | | 22% |
| 5. IAM, SDP, Gateway & Govern | | 4 | | 15% |
| **Total** | | **25** | | **100%** |

| Overall | Verdict |
| :--- | :--- |
| **22–25** | Ready. Take [`PRACTICE_EXAM.md`](PRACTICE_EXAM.md) timed (80 questions matching the Beta exam length; GA in mid-November has fewer questions) and aim for **≥80%**. |
| **18–21** | Nearly ready. Drill your lowest-scoring domain and review the Least-Privilege IAM Matrix in [`STUDY_GUIDE.md`](STUDY_GUIDE.md). |
| **12–17** | Not yet. Master Tracks 3, 4, and the IAM/Security patterns in Track 5 first. |
| **0–11** | Do not book yet. Work through all 20 labs sequentially, then take the practice exam cold. |

---

## Hard blockers — do not sit the exam if any of these are unclear

- You grant `roles/editor`, `roles/owner`, or static Service Account JSON keys instead of **least-privilege predefined roles + Agent Identity + PAB**.
- You forget that querying BigQuery requires **both** `roles/bigquery.jobUser` (to run the job) **and** `roles/bigquery.dataViewer` (on the dataset).
- You confuse **GECX Deterministic Flows** (`Pages` + `Transition Routes` + `sys.no-match-2`) with **Probabilistic Generative Playbooks**.
- You confuse Antigravity's **`GEMINI.md`** (always-on Markdown), **`rules/*.md`** (`glob`/`model_decision`), **`SKILL.md`** (L1/L2/L3 task bundle), and **`hooks.json`** (deterministic shell `PreToolUse` / `Stop` gates).
- You cannot explain **Rubric (`RubricsBasedCriterion`)** vs. **Metric (`ToolTrajectoryCriterion`)**, or **RAG Engine + Discovery Engine Ranking API (`RankServiceClient`)**.
- You confuse **Cloud Armor** (L7 HTTP/DDoS WAF) with **Model Armor + Sensitive Data Protection (`SdpAdvancedConfig`)** (LLM prompt injection & semantic PHI/PII de-identification).
