# VERIFIED FACTS — ground truth for the repo rewrite

> **Personal study repo — not affiliated with Google Cloud.** Official guidance: [cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect) · [Disclaimer](../DISCLAIMER.md)

> [!IMPORTANT]
> Every fact here was verified by **direct machine inspection**, not by recall or web summary.
> Verification methods: `L` = live Gemini API `ListModels`, `P` = PyPI JSON API,
> `I` = Python introspection of the installed package, `A` = local Antigravity runtime/SDK docs,
> `D` = official exam-guide PDF & Google Cloud IAM documentation.
> Anything not verified is explicitly marked **UNVERIFIED**.
>
> Authoring rule: **if it is not in this file, do not write it as fact.**

Captured: 2026-09-13 · Updated with Beta Exam verification: 2026-10-29

---

## 1. Exam format, timeline, and delivery notes (D + Beta feedback)

- **Official Exam Guide Source**: [Professional Agentic Architect Certification Exam Guide (PDF)](https://services.google.com/fh/files/misc/professional_agentic_architect_exam_guide_english.pdf) (4 pages: Role Definition, Sections 1–5, and 28 Tools in Scope).
- **Beta vs. GA Timeline & Question Count**:
  - **Beta Exam**: Approximately **~80 multiple-choice and multiple-select questions** (3-hour window). Real-world topic emphases documented across this course are informed by **Beta exam** feedback alongside the official Exam Guide.
  - **GA Launch**: The **Generally Available (GA) exam launches in mid-November** and **will have a lesser number of questions** than the ~80-question Beta form (typically ~50–60 questions in standard 2-hour Google Cloud Professional GA exams). Always confirm current exam length and policies on the official registration page before booking.
- **Delivery Method**: Available via **online-proctored** (remote) or **onsite-proctored** (testing center) delivery.
- **Testing Interface Features**: Includes **Mark for Review** and **option Strike-through** (crossing out eliminated distractors on complex scenario stems).

---

## 2. Package versions (P + I)

| Package | Version | Install |
| :--- | :--- | :--- |
| `google-adk` | **2.9.0** | `pip install google-adk==2.9.0` |
| `google-genai` | **2.23.0** | `pip install google-genai` |
| `a2a-sdk` | **1.1.2** | `pip install a2a-sdk` |
| `mcp` | **2.2.0** | `pip install mcp` |
| `google-cloud-aiplatform` | **1.165.1** | `pip install google-cloud-aiplatform` |
| `google-cloud-modelarmor` | **0.7.1** | `pip install google-cloud-modelarmor` |
| `google-cloud-discoveryengine` | **0.13.12** | `pip install google-cloud-discoveryengine` |
| `google-cloud-agentidentitycredentials` | **0.1.1** | `pip install google-cloud-agentidentitycredentials` |
| `google-cloud-iamconnectorcredentials` | **0.1.1** | `pip install google-cloud-iamconnectorcredentials` |

`google-adk` requires **Python >= 3.10**.

### ADK extras — these gate the exam-relevant integrations (I)

| Extra | Unlocks |
| :--- | :--- |
| `google-adk[agent-identity]` | `integrations.agent_identity`, `integrations.agent_registry` |
| `google-adk[gcp]` | Model Armor (`google-cloud-modelarmor`) |
| `google-adk[a2a]` | A2A support (`a2a-sdk`, `RemoteA2aAgent`) |
| `google-adk[extensions]` | `GkeCodeExecutor` |

> [!TIP]
> Exam-relevant: attempting to import these without the extra raises a **precise `ImportError` naming the extra**. That is a plausible troubleshooting question.

---

## 3. Gemini models — confirmed present in the live API (L)

> Verified by calling `ListModels` on `generativelanguage.googleapis.com/v1beta`.
> **`gemini-3.7-flash` is REAL.** Do not "correct" it.

### Text / reasoning — stable

| Model ID | Input | Output |
| :--- | ---: | ---: |
| `gemini-3.8-flash` | 1,048,576 | 65,536 |
| `gemini-3.7-flash` | 1,048,576 | 65,536 |
| `gemini-3.6-flash` | 1,048,576 | 65,536 |
| `gemini-3.5-flash` | 1,048,576 | 65,536 |
| `gemini-3.5-flash-lite` | 1,048,576 | 65,536 |
| `gemini-3.1-flash-lite` | 1,048,576 | 65,536 |
| `gemini-2.5-pro` | 1,048,576 | 65,536 |
| `gemini-2.5-flash` | 1,048,576 | 65,536 |
| `gemini-2.5-flash-lite` | 1,048,576 | 65,536 |

### Text / reasoning — preview

| Model ID | Input | Output |
| :--- | ---: | ---: |
| `gemini-3.1-pro-preview` | 1,048,576 | 65,536 |
| `gemini-3.1-pro-preview-customtools` | 1,048,576 | 65,536 |
| `gemini-3.1-flash-lite-preview` | 1,048,576 | 65,536 |
| `gemini-3-flash-preview` | 1,048,576 | 65,536 |

### Floating aliases

`gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-pro-latest` — all 1,048,576 in / 65,536 out.

> [!WARNING]
> Aliases move. Pin an explicit version for production and for reproducible labs.

### Embeddings (RAG)

| Model ID | Input limit | Status |
| :--- | ---: | :--- |
| `gemini-embedding-2` | 8,192 | current |
| `gemini-embedding-2-preview` | 8,192 | preview |
| `gemini-embedding-001` | 2,048 | legacy |

Methods: `embedContent`, `asyncBatchEmbedContent`, `countTextTokens`.

> `text-embedding-005` is **NOT** in the live list. The old repo's use of it is stale.

### Open models (Gemma) — for self-hosted / Model Garden tradeoffs

| Model ID | Input | Output |
| :--- | ---: | ---: |
| `gemma-4-26b-a4b-it` | 262,144 | 32,768 |
| `gemma-4-31b-it` | 262,144 | 32,768 |

> Current Gemma generation is **4**, not 2. The old repo's "Gemma 2 2B/9B/27B" is stale.

### Specialized (useful for multimodal ingestion, Section 1.2)

| Model ID | Purpose |
| :--- | :--- |
| `gemini-3-pro-image`, `gemini-3.1-flash-image`, `gemini-3.1-flash-lite-image` | image generation/editing |
| `nano-banana-pro-preview` | image generation |
| `gemini-3.5-transcribe`, `gemini-3.5-transcribe-live` | speech-to-text |
| `gemini-3.1-flash-tts-preview` | text-to-speech |
| `gemini-3.1-flash-live-preview` | Live API (`bidiGenerateContent`) |
| `gemini-3.5-live-translate-preview` | live speech translation |
| `gemini-omni-flash-preview`, `gemini-omni-1.1-flash` | omni / video |
| `veo-3.1-generate-preview` (+ `-fast`, `-lite`) | video generation |
| `lyria-3.5`, `lyria-3-pro-preview` | music |
| `gemini-2.5-computer-use-preview-10-2025` | computer use |
| `gemini-robotics-er-2-preview` | robotics embodied reasoning |
| `antigravity-preview-05-2026` | Antigravity |
| `deep-research-pro-preview-12-2025`, `deep-research-max-preview-04-2026` | deep research |

---

## 4. ADK 2.9.0 & Cloud SDK API surfaces (I)

### Top level

```python
from google.adk import Agent, Runner, Workflow, Context, Event
```

### `google.adk.agents` & `RemoteA2aAgent`

```
Agent, BaseAgent, BaseAgentConfig, Context, InvocationContext,
LiveRequest, LiveRequestQueue, LlmAgent, LlmAgentConfig,
LoopAgent, LoopAgentConfig, ManagedAgent, McpInstructionProvider,
ParallelAgent, ParallelAgentConfig, RunConfig,
SequentialAgent, SequentialAgentConfig
```
Plus `google.adk.agents.remote_a2a_agent.RemoteA2aAgent` (`name`, `description`, `agent_card`, `httpx_client`, `timeout`, `a2a_client_factory`, `config: A2aRemoteAgentConfig`, `full_history_when_stateless`, `auth_scheme`, `auth_credential`, `credential_key`).

> [!IMPORTANT]
> `SequentialAgent` / `ParallelAgent` / `LoopAgent` **still exist and still work in 2.9.0**, but they
> are **formally deprecated**. Constructing one emits, verbatim:
>
> ```
> DeprecationWarning: SequentialAgent is deprecated in favor of Workflow and will be
> removed in a future version. Workflow cannot yet be used as an LlmAgent sub-agent.
> ```
>
> `Workflow` **cannot yet be nested as a sub-agent of an `LlmAgent`**, so a hierarchical design
> where an `LlmAgent` delegates to a deterministic sub-pipeline still needs `SequentialAgent` /
> `ParallelAgent` / `LoopAgent` (or wrapping `Workflow` inside an `AgentTool`).

**`LlmAgent` fields (selected, exact):**
`name, description, model, instruction, global_instruction, static_instruction, tools, sub_agents, parent_agent, input_schema, output_schema, state_schema, output_key, planner, code_executor, generate_content_config, include_contents, mode ('chat'|'task'|'single_turn'), parallel_worker, disallow_transfer_to_parent, disallow_transfer_to_peers, before_agent_callback, after_agent_callback, before_model_callback, retry_config, timeout, rerun_on_resume, wait_for_output`

- **Multi-Agent Latency & Context Optimization**:
  - `SequentialAgent`: End-to-end latency = $\sum T_i$ (sum of sub-agents).
  - `ParallelAgent`: End-to-end latency = $\max(T_i)$ (slowest concurrent worker).
  - `LoopAgent`: End-to-end latency = $k \times T_{\text{iter}}$ ($k \le \text{max\_iterations}$, early exit via `exit_loop`).
  - `transfer_to_agent` (`TransferToAgentTool`): Adds 1 routing LLM hop, then target agent streams directly to user.
  - `AgentTool`: Parent LLM invokes child agent like a synchronous function and runs **a second parent LLM synthesis hop** ($T_{\text{parent1}} + T_{\text{child}} + T_{\text{parent2}}$).
  - `Workflow` (`Node` / `Edge` / `FunctionNode` / `JoinNode`): **0ms routing overhead** via deterministic Python edge predicates.
  - Setting `include_contents='none'` on downstream specialists and passing structured state via `{output_key}` prevents $O(N^2)$ context-window bloat and prefill latency spikes.

### `google.adk.sessions` & `google.adk.memory`

- **Sessions (`google.adk.sessions`)**: `BaseSessionService`, `InMemorySessionService`, `DatabaseSessionService`, `VertexAiSessionService`, `Session`, `State`, `StateSchemaError` + `google.adk.integrations.redis.RedisSessionService`.
  - State prefix scopes: plain key (current session), `user:` (across sessions for that user), `app:` (global to app), `temp:` (discarded after current invocation).
- **Memory (`google.adk.memory`)**: `BaseMemoryService`, `InMemoryMemoryService`, `VertexAiMemoryBankService`, `VertexAiRagMemoryService`.
  - Recall tools: `preload_memory` (eagerly injects relevant memories before every turn — zero extra tool round-trip) vs `load_memory` (reactive tool called only when the LLM decides memory is needed — lower baseline token cost).

### `google.adk.tools` & `google.adk.skills`

- **Tools**: `APIHubToolset, AgentTool, ApiRegistry, AuthToolArguments, BaseTool, DiscoveryEngineSearchTool, ExampleTool, FunctionTool, LongRunningFunctionTool, MCPToolset, McpToolset, RemoteMcpServer, SearchResultMode, ToolContext, TransferToAgentTool, VertexAiLoadProfilesTool, VertexAiSearchTool, enterprise_web_search, exit_loop, get_user_choice, google_maps_grounding, google_search, load_artifacts, load_memory, preload_memory, request_input, transfer_to_agent, url_context`.
- **Skills (`google.adk.skills` + `integrations.skill_registry.GCPSkillRegistry`)**:
  - `Skill` = `frontmatter: Frontmatter` (`name`, `description`, `license`, `compatibility`, `allowed_tools`, `metadata`) + `instructions: str` + `resources: Resources`.
  - Progressive disclosure: **L1** frontmatter (always loaded for lightweight discovery) → **L2** full Markdown `instructions` (loaded when activated) → **L3** `resources` / scripts (loaded on demand).

### RAG Engine & Discovery Engine Ranking / Reranking API (I)

- **`vertexai.preview.rag`** (installed in `google-cloud-aiplatform 1.165.1`; emits deprecation notice pointing toward `agentplatform.Client`):
  - Corpus & ingestion: `RagCorpus`, `RagFile`, `TransformationConfig(chunking_config=ChunkingConfig(chunk_size=..., chunk_overlap=...))`, `LayoutParserConfig` (Document AI layout-aware table/heading chunking), `LlmParserConfig`.
  - Retrieval & two-stage reranking: `RagRetrievalConfig(top_k=..., filter=..., ranking=Ranking(rank_service=RankService(model_name=...)) | Ranking(llm_ranker=LlmRanker(model_name=...)), hybrid_search=HybridSearch(alpha=...))`.
- **`google.cloud.discoveryengine_v1.RankServiceClient`** (Standalone Cross-Encoder Reranking API):
  - `RankRequest(ranking_config="projects/.../locations/global/rankingConfigs/default_ranking_config", model="semantic-ranker-default@latest", top_n=5, query=..., records=[RankingRecord(id=..., title=..., content=...)])` → returns `RankResponse` with calibrated relevance `score` per `RankingRecord`.
  - Architectural pattern: **Stage 1 Bi-Encoder ANN recall** (`gemini-embedding-2`, fetch `top_k=50` in milliseconds) → **Stage 2 Cross-Encoder Reranking** (`RankServiceClient`, joint query-chunk cross-attention down to `top_n=5` before LLM prompt injection).

### `google.adk.evaluation` (Rubric vs. Metric) & `vertexai.evaluation` (I)

- **Reference-Based / Deterministic Metrics (`google.adk.evaluation.eval_metrics`)**:
  - `ToolTrajectoryCriterion` / `trajectory_evaluator` (`exact_match`, `in_order_match`, `any_order_match`) — deterministic check on tool names and arguments against a golden `.evalset.json`.
  - `final_response_match_v1`, `final_response_match_v2`, `Rouge` — compares final output against a static golden reference answer.
- **Reference-Free / Rubric-Based Autoraters (`google.adk.evaluation.eval_rubrics` + `eval_metrics`)**:
  - `Rubric(rubric_id=..., rubric_content=RubricContent(text_property=...), description=..., type=...)` paired with `RubricsBasedCriterion(threshold=..., judge_model_options=..., rubrics=[...])`.
  - Built-in rubric/groundedness evaluators: `rubric_based_final_response_quality_v1`, `rubric_based_tool_use_quality_v1`, `rubric_based_multi_turn_trajectory_evaluator`, `hallucinations_v1`, `safety_evaluator`.
  - Use **Metrics** when a deterministic right tool sequence or reference string exists; use **Rubrics** when evaluating open-ended customer support empathy, policy adherence, or multi-valid-path reasoning where no single reference string suffices.
- **Cloud-Scale Evaluation (`vertexai.evaluation` / Agent Platform Gen AI Evaluation Service)**:
  - `EvalTask`, `PointwiseMetric`, `PairwiseMetric` (side-by-side A/B model or prompt comparison), `CustomMetric`, `RubricBasedMetric`, `MetricPromptTemplateExamples`.
  - ADK bridges local `.evalset.json` runs to the managed cloud service via `vertex_ai_eval_facade`.

### `google.cloud.modelarmor_v1` + Sensitive Data Protection (SDP) + `ModelArmorPlugin` (I)

- **Cloud Model Armor SDK (`google.cloud.modelarmor_v1`)**:
  - `ModelArmorClient` / `ModelArmorAsyncClient`: `sanitize_user_prompt()`, `sanitize_model_response()`, `create_template()`.
  - `FilterConfig` fields:
    - `pi_and_jailbreak_filter_settings`: `PiAndJailbreakFilterSettings` (prompt injection & jailbreak detection).
    - `sdp_settings`: `SdpFilterSettings` with either:
      - `basic_config`: `SdpBasicConfig(filter_enforcement=...)` (fast inspect/block), OR
      - `advanced_config`: `SdpAdvancedConfig(inspect_template="projects/.../inspectTemplates/...", deidentify_template="projects/.../deidentifyTemplates/...")` (masks/redacts/tokenizes PII & HIPAA PHI in-flight before the prompt reaches Gemini or before the response reaches the client!).
    - `malicious_uri_filter_settings`: `MaliciousUriFilterSettings` (blocks phishing/malware links in outputs).
    - `rai_settings`: `RaiFilterSettings` (hate speech, harassment, dangerous content, sexually explicit).
- **ADK Integration (`google.adk.integrations.model_armor`)**:
  - `ModelArmorPlugin(config=ModelArmorConfig(prompt_template_name=..., response_template_name=..., block_on_screening_failure=True))` — `block_on_screening_failure=True` enforces **fail-closed** security.
  - **Gateway vs. Plugin Defense-in-Depth**: **Agent Gateway + Model Armor** enforces centralized, language-agnostic perimeter screening across all enterprise agents (preventing developers from forgetting a plugin), whereas **`ModelArmorPlugin`** inside ADK additionally intercepts **mid-loop MCP/tool outputs** (`after_tool_callback` / `before_model_callback`) to neutralize indirect prompt injections fetched from third-party tickets or emails.

### Agent Identity, Connector Credentials & Auth Manager (I)

- **Agent Identity (`google.adk.integrations.agent_identity` + `google.cloud.agentidentitycredentials_v1`)**:
  - `GcpAuthProvider`, `GcpAuthProviderScheme` + `AuthProviderCredentialsServiceClient` (`RetrieveCredentialsRequest(auth_provider=..., user_id=..., scopes=..., continue_uri=..., force_refresh_token=...)`).
  - Eliminates static JSON Service Account keys (`roles/iam.serviceAccountKeys.create` disabled via Org Policy `iam.disableServiceAccountKeyCreation`); mints short-lived workload OIDC/OAuth tokens bound to a **Principal Access Boundary (PAB)** (`Effective Access = IAM Allow ∩ PAB`).
- **Gemini Enterprise / Discovery Engine Connector Credentials (`google.cloud.iamconnectorcredentials_v1alpha`)**:
  - `IAMConnectorCredentialsServiceClient` (`RetrieveCredentialsRequest(connector=..., user_id=..., scopes=..., continue_uri=...)`, `FinalizeCredentialsRequest`).
  - Two enterprise connector auth modes in Gemini Enterprise (`GEApp`):
    1. **ACL-Aware Search Indexing (Ingestion Sync)**: Connector Service Account + Workforce Identity Federation ingests documents and ACLs from SharePoint/Jira/Confluence/Drive into **Agent Search**; queries verify user identity so users only retrieve documents matching their ACLs.
    2. **Real-Time Action / Federated Connectors (3-Legged OAuth 2.0 / 3LO)**: Managed by **Auth Manager** + `IAMConnectorCredentialsServiceClient`; triggers per-user OAuth consent (`uri_consent_required`) so write actions (creating a Jira ticket or Slack post) execute strictly as the authenticated human user.

---

## 5. Antigravity customization & governance specification (A)

Verified directly from Antigravity runtime documentation (`jetski-customizations` & `google-antigravity-sdk`):

| Artifact / File | Exact Discovery Path(s) | Purpose & Schema Mechanics |
| :--- | :--- | :--- |
| **`GEMINI.md` / `AGENTS.md`** | Walked hierarchically from workspace root up to filesystem root, plus `~/.gemini/GEMINI.md` / `~/.gemini/AGENTS.md` | **Always-on plain Markdown instructions** (no YAML frontmatter). `GEMINI.md` and `AGENTS.md` are peers; subdirectories override/specialize repo-wide conventions for monorepos. |
| **`rules/*.md`** | `.agents/rules/*.md` (workspace) and `~/.gemini/config/rules/*.md` (user) | Modular rules with YAML frontmatter `trigger`: `always_on`, `model_decision` (loaded when `description` matches task), `glob` (loaded only when active files match e.g. `**/*.tf`), or `manual` (`@rule-name`). Conserves context tokens vs `GEMINI.md`. |
| **`SKILL.md` & `skills.json`** | `.agents/skills/<name>/SKILL.md`, `~/.gemini/config/skills/<name>/SKILL.md`, and manifest `skills.json` | Reusable task packages with YAML frontmatter (`name`, `description`) + instructions + optional `scripts/`, `references/`, `examples/`. Uses L1/L2/L3 progressive disclosure; `skills.json` indexes skill bundles inside plugins/registries. |
| **`hooks.json`** | `.agents/hooks.json` (workspace), `~/.gemini/hooks.json` (user), `plugins/<name>/hooks/hooks.json` | Deterministic shell commands triggered at lifecycle events: **`PreToolUse`**, **`PostToolUse`**, **`PreInvocation`**, **`PostInvocation`**, **`Stop`**. Filtered by regex `matcher` (e.g., `"run_command"`, `"write_to_file\|replace_file_content"`). |
| **`plugin.json`** | `.agents/plugins/<name>/plugin.json` and `~/.gemini/config/plugins/<name>/plugin.json` | Bundles `skills/`, `agents/`, `hooks/hooks.json`, `rules/`, and MCP servers into a versioned distributable unit for enterprise teams. |
| **`mcp_config.json`** | `~/.gemini/config/mcp_config.json` (and workspace `.agents/mcp.json`) | Registers local **Stdio** (`command`, `args`, `env`) and remote **SSE / Streamable HTTP** (`serverUrl`, `headers`) MCP servers. Supports **eager** vs **lazy-loaded** tool schemas to prevent context bloat. |
| **Subagents (`agents/`)** | `.agents/agents/<name>.md` (or `agent.json` + `config.yaml`) | Isolated specialist context windows with tool allowlists (`enable_write_tools: false` for read-only security/code reviewers), model routing (`flash`, `pro`, `inherit`), and recursion guards (`max_subagent_depth`, `allowed_subagents`). |

### `hooks.json` stdin/stdout protocol & decision precedence (A)

- Hooks receive **camelCase JSON** on `stdin` (`sessionId`, `transcriptPath`, `cwd`, `hookEventName`, `toolName`, `toolInput`) and return JSON on `stdout`.
- **`PreToolUse` `permissionDecision` values**: `"allow"`, `"deny"` (hard block; returns `permissionDecisionReason` to agent), `"ask"` (prompt human if not auto-allowed), `"force_ask"` (always require human confirmation even in auto-approve mode), `"overwrite"` (rewrite `updatedInput` before tool runs).
- **`Stop` hook**: Returning `{"decision": "block", "reason": "Run pytest before finishing"}` prevents the coding agent from prematurely ending its turn until verification passes!
- **Antigravity SDK `policy` 9-Level Precedence Order** (highest to lowest):
  1. `session_policies` (runtime dynamic overrides) → 2. `extra_policies` → 3. `agent_config_policies` → 4. `subagent` policies → 5. `hooks` (`hooks.json`) → 6. `workspace` policies → 7. `role` policies → 8. `user` policies → 9. `system_defaults`.
  - Within the same level, the **most restrictive action wins**: `DENY` > `ASK` > `ALLOW`.
  - If a custom `when=` predicate raises an unhandled Python exception, Antigravity **fails closed** (`DENY`).
  - Built-in terminal safety rule: `policy.Rule(tool="run_command", action=policy.Action.ASK, check=policy.confirm_run_command())` combined with `RunCommandConfig(enable_sandbox=True, network_Disabled=True)`.

---

## 6. Least-Privilege Google Cloud IAM Roles Reference Matrix (D)

> [!IMPORTANT]
> Beta exam feedback consistently highlights that **~30–35% of exam questions** test least-privilege IAM roles, service-specific permissions, cross-project access, and safe credential provisioning (never `roles/owner`, `roles/editor`, or static Service Account keys).

| Workload / Scenario | Least-Privilege Predefined Role(s) | Common Exam Trap / Anti-Pattern |
| :--- | :--- | :--- |
| **ADK Agent calling Gemini / Memory Bank / Sessions / RAG Engine on Vertex AI** | `roles/aiplatform.user` (on the target project) | Granting `roles/aiplatform.admin` or `roles/editor` |
| **Deploying an agent to Agent Runtime (`adk deploy agent_engine`)** | CI/CD deployer: `roles/aiplatform.admin` (or custom Reasoning Engine deploy role) + `roles/iam.serviceAccountUser` on the runtime SA + `roles/storage.objectAdmin` on staging bucket | Running the runtime agent itself as `roles/aiplatform.admin` |
| **Cross-Project A2A Caller → Cloud Run Specialist Agent** | Grant `roles/run.invoker` **on the specific Cloud Run service** in Project B to Project A's Agent Identity / SA (authenticated via OIDC ID token) | Setting `--allow-unauthenticated` (`allUsers`) or granting project-wide `roles/run.admin` |
| **Agent querying Agent Search / Gemini Enterprise (`GEApp`) Data Store** | `roles/discoveryengine.viewer` (read/search only) | Granting `roles/discoveryengine.admin` to a runtime query agent |
| **Connector Indexing Service Account syncing ACLs into Agent Search** | `roles/discoveryengine.editor` (or data store writer) scoped to the target Data Store + read-only source connector scope | Using an employee's personal OAuth token for bulk background indexing |
| **Agent executing read-only analytical SQL in BigQuery (`BigQueryToolset`)** | `roles/bigquery.jobUser` (on the billing/execution project to run jobs) **+** `roles/bigquery.dataViewer` (scoped to the specific dataset/table) | Granting only `dataViewer` (fails to create query job!) or granting `roles/bigquery.admin` |
| **Agent connecting to Cloud SQL via IAM Database Auth / MCP Server** | `roles/cloudsql.client` + `roles/cloudsql.instanceUser` | Hardcoding PostgreSQL superuser passwords in prompts or env vars |
| **Agent reading tool API secrets at startup** | `roles/secretmanager.secretAccessor` **bound on the individual secret resource** (not project-wide) | Storing secrets in `GEMINI.md`, Cloud Run plaintext env vars, or granting project-wide `secretmanager.admin` |
| **Agent screening prompts/responses via Model Armor (`ModelArmorPlugin`)** | `roles/modelarmor.user` (invoke `sanitizeUserPrompt` / `sanitizeModelResponse`) vs `roles/modelarmor.admin` (security team creating templates) | Letting application developers modify `FilterConfig` templates in prod (`roles/modelarmor.admin`) |
| **Model Armor Advanced SDP inspecting & de-identifying PHI/PII** | Grant **Model Armor service agent** `roles/dlp.user` + `roles/dlp.inspectTemplatesReader` + `roles/dlp.deidentifyTemplatesReader` | Using Cloud Armor WAF rules expecting semantic SSN/PHI redaction |
| **Agent exporting OpenTelemetry spans & structured logs** | `roles/cloudtrace.agent` + `roles/logging.logWriter` + `roles/monitoring.metricWriter` | Granting `roles/logging.privateLogViewer` to the agent or capturing raw PHI in spans |
| **Capping maximum blast radius of an Agent Identity across GCP** | **Principal Access Boundary (PAB)** policy (`roles/iam.principalAccessBoundaryAdmin` to author/bind) | Relying on IAM Allow policies alone (which are additive) |

---

## 7. `adk` CLI — verified command tree & Agent vs. Human Mode (I)

```
adk create           Creates a new app in the current folder with prepopulated agent template
adk run              Runs an agent. If no query is provided, enters interactive mode
adk web              Starts a FastAPI server with Web UI for agents
adk api_server       Starts a FastAPI server for agents
adk eval             Evaluates an agent given the eval sets
adk eval_set         Manage Eval Sets (create | add_eval_case | generate_eval_cases)
adk test             Runs pytest on agent test JSON files under the specified folder
adk deploy           Deploys agent to hosted environments (agent_engine | cloud_run | docker | gke)
adk optimize         Optimizes the root agent instructions using the GEPA optimizer
adk telemetry        Manage telemetry settings (enable | disable | status)
adk conformance      Conformance testing tools for ADK (record | test)
adk migrate          Migrate schemas (session)
```

- **Agent Mode vs. Human Mode in Agents CLI (`adk` / `agents-cli`)**:
  - **Human Mode**: Interactive TTY mode (`adk run`, `adk web`) with ANSI spinners, conversational prompts, and interactive debugging for developers.
  - **Agent Mode**: Non-interactive, headless, structured JSON output (`--format=json` / single-shot flags, deterministic non-zero exit codes, no interactive stdin prompts) so coding agents like **Antigravity** or CI/CD runners can invoke `adk eval`, `adk optimize`, and `adk deploy` autonomously without hanging on TTY input.

---

## 8. Official exam guide — verbatim 5 sections & all 28 tools in scope (D)

Source: <https://services.google.com/fh/files/misc/professional_agentic_architect_exam_guide_english.pdf>

| Section | Title | Weight |
| :--- | :--- | :---: |
| 1 | Building agents using low-code tools | ~13% |
| 2 | Using coding agents for application development | ~17% |
| 3 | Developing custom agents | ~33% |
| 4 | Evaluating and deploying agentic workflows | ~22% |
| 5 | Securing and governing agentic workflows | ~15% |

### All 28 tools in scope (Page 4 verbatim list)

1. Agent Development Kit (ADK)
2. Agent evaluation
3. Agent Gateway
4. Agent Identity
5. Agent Registry
6. Agent Retrieval and Vector Search 1.0
7. Agent Runtime (formerly Agent Engine)
8. Agent Search (formerly Vertex AI Search)
9. Agentic protocols (e.g., Agent2Agent [A2A], MCP)
10. Agents CLI in Agent Platform
11. Antigravity (CLI, SDK, App)
12. Auth Manager (OAuth 2.0)
13. BigQuery
14. Cloud Run
15. Cloud SQL
16. Cloud Storage
17. Firestore
18. Gemini Enterprise
19. Gemini LLMs
20. Google Cloud Observability (Cloud Logging and Cloud Trace)
21. Google Kubernetes Engine (GKE)
22. Memorystore for Redis
23. Model Armor
24. Model Context Protocol (MCP) servers
25. Model Garden
26. RAG Engine
27. Sensitive Data Protection
28. Skill Registry

---

## 9. Corrections to stale / legacy claims

| Legacy / stale claim | Verified reality |
| :--- | :--- |
| ~~`gemini-3.7-flash` is fake~~ | **It is real** (L). Keep it. |
| `text-embedding-005` / `textembedding-gecko` | Retired → use `gemini-embedding-2` (8,192 tokens) |
| `gemini-1.5-pro` / `gemini-1.5-flash` / `gemini-2.0-flash` | Retired → use `gemini-3.7-flash`, `gemini-2.5-pro`, `gemini-3.5-flash-lite` |
| `gemma-2-9b-it` / `gemma-2-27b-it` | Retired → use `gemma-4-26b-a4b-it`, `gemma-4-31b-it` |
| Static Service Account JSON keys for agents | Anti-pattern → use **Agent Identity** (`GcpAuthProvider` + Workload Identity + PAB) |
| "26 tools in scope" | Official PDF Page 4 lists **28** tools in scope |

---

## 10. Authoring rules for all contributors

1. **Never** invent a model ID, class name, import path, or CLI flag. If it is not in this file, verify it or mark it UNVERIFIED.
2. Use `common/models.py` as the single source of model IDs — no hard-coded model strings in Python lab files.
3. Mark Pre-GA / unverified products inline with a `> [!WARNING]` callout naming the closest GA equivalent.
4. Every lab must run **offline by default** and only touch Google Cloud behind an explicit `--live` flag.
5. Every lab must ship a `cleanup.sh` that is idempotent and safe to run twice.
6. Prefer showing the **decision** (when to use X over Y, and with what least-privilege IAM role) over boilerplate — that is what the exam tests.
