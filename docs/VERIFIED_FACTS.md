# VERIFIED FACTS — ground truth for the repo rewrite

> **Personal study repo — not affiliated with Google Cloud.** Official guidance: [cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect) · [Disclaimer](../DISCLAIMER.md)

> [!IMPORTANT]
> Every fact here was verified by **direct machine inspection**, not by recall or web summary.
> Verification methods: `L` = live Gemini API `ListModels`, `P` = PyPI JSON API,
> `I` = Python introspection of the installed package, `D` = official docs URL.
> Anything not verified is explicitly marked **UNVERIFIED**.
>
> Authoring rule: **if it is not in this file, do not write it as fact.**

Captured: 2026-09-13

---

## 1. Package versions (P)

| Package | Version | Install |
| :--- | :--- | :--- |
| `google-adk` | **2.9.0** | `pip install google-adk==2.9.0` |
| `google-genai` | **2.23.0** | `pip install google-genai` |
| `a2a-sdk` | **1.1.2** | `pip install a2a-sdk` |
| `mcp` | **2.2.0** | `pip install mcp` |

`google-adk` requires **Python >= 3.10**.

### ADK extras — these gate the exam-relevant integrations (I)

| Extra | Unlocks |
| :--- | :--- |
| `google-adk[agent-identity]` | `integrations.agent_identity`, `integrations.agent_registry` |
| `google-adk[gcp]` | Model Armor (`google-cloud-modelarmor`) |
| `google-adk[a2a]` | A2A support (`a2a-sdk`) |
| `google-adk[extensions]` | `GkeCodeExecutor` |

> [!TIP]
> Exam-relevant: attempting to import these without the extra raises a **precise `ImportError` naming the extra**. That is a plausible troubleshooting question.

---

## 2. Gemini models — confirmed present in the live API (L)

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

## 3. ADK 2.9.0 API surface (I)

### Top level

```python
from google.adk import Agent, Runner, Workflow, Context, Event
```

### `google.adk.agents`

```
Agent, BaseAgent, BaseAgentConfig, Context, InvocationContext,
LiveRequest, LiveRequestQueue, LlmAgent, LlmAgentConfig,
LoopAgent, LoopAgentConfig, ManagedAgent, McpInstructionProvider,
ParallelAgent, ParallelAgentConfig, RunConfig,
SequentialAgent, SequentialAgentConfig
```

> [!IMPORTANT]
> `SequentialAgent` / `ParallelAgent` / `LoopAgent` **still exist and still work in 2.9.0**, but they
> are **formally deprecated**. Constructing one emits, verbatim:
>
> ```
> DeprecationWarning: SequentialAgent is deprecated in favor of Workflow and will be
> removed in a future version. Workflow cannot yet be used as an LlmAgent sub-agent.
> ```
>
> Read that second sentence carefully — it is the reason the deprecated classes are still
> necessary. `Workflow` **cannot yet be nested as a sub-agent of an `LlmAgent`**, so a
> hierarchical design still needs the workflow agents today. This nuance is exactly the kind
> of thing a beta exam asks about: the answer is neither "they're gone" nor "nothing changed".
>
> Their MRO is now `-> BaseAgent -> BaseNode -> BaseModel`, i.e. they sit on the graph engine.
> `Agent` is an alias of `LlmAgent` (identical MRO and fields).
>
> Pinned by a regression test in `tracks/03_custom_agents/lab_08_adk_fundamentals/tests/`.

**`LlmAgent` fields (selected, exact):**
`name, description, model, instruction, global_instruction, static_instruction, tools, sub_agents, parent_agent, input_schema, output_schema, state_schema, output_key, planner, code_executor, generate_content_config, include_contents, mode ('chat'|'task'|'single_turn'), parallel_worker, disallow_transfer_to_parent, disallow_transfer_to_peers, before_agent_callback, after_agent_callback, before_model_callback, retry_config, timeout, rerun_on_resume, wait_for_output`

**`LoopAgent`** adds `max_iterations`.

**`ManagedAgent`** — backed by the Managed Agents API (`interactions.create`); fields include `agent_id`, `environment`, `agent_config`, `mode='single_turn'`. Only server-side tools supported.

### `google.adk.workflow` — graph orchestration

```
Workflow, Node, BaseNode, Edge, FunctionNode, JoinNode,
START, DEFAULT_ROUTE, RetryConfig, NodeTimeoutError, node
```

`Workflow` fields: `name, description, edges, max_concurrency, graph, input_schema, output_schema, state_schema, retry_config, timeout`.
`Node` fields add `parallel_worker`, `max_parallel_workers`.

> Maps directly to the exam phrase **"graph workflow"** in objective 3.3.

### `google.adk.sessions`

```
BaseSessionService, InMemorySessionService, DatabaseSessionService,
VertexAiSessionService, Session, State, StateSchemaError
```

### `google.adk.memory`

```
BaseMemoryService, InMemoryMemoryService,
VertexAiMemoryBankService, VertexAiRagMemoryService
```

### `google.adk.artifacts`

```
BaseArtifactService, InMemoryArtifactService,
FileArtifactService, GcsArtifactService
```

### `google.adk.tools`

```
APIHubToolset, AgentTool, ApiRegistry, AuthToolArguments, BaseTool,
DiscoveryEngineSearchTool, ExampleTool, FunctionTool,
LongRunningFunctionTool, MCPToolset, McpToolset, RemoteMcpServer,
SearchResultMode, ToolContext, TransferToAgentTool,
VertexAiLoadProfilesTool, VertexAiSearchTool,
enterprise_web_search, exit_loop, get_user_choice,
google_maps_grounding, google_search, load_artifacts,
load_memory, preload_memory, request_input,
transfer_to_agent, url_context
```

> [!TIP]
> `request_input` and `get_user_choice` are the **built-in HITL primitives** (Section 5.2).
> `load_memory` / `preload_memory` are the memory-recall tools (Section 3.1).
> `exit_loop` terminates a `LoopAgent` (Section 3.3).

### `google.adk.tools.bigquery`

```
BigQueryToolset, BigQueryCredentialsConfig, get_bigquery_skill
```

### `google.adk.models`

```
BaseLlm, Gemini, Gemma, Claude, LiteLlm, ApigeeLlm, Gemma3Ollama,
FallbackModel, LLMRegistry, LlmCapabilities, AnthropicGenerateContentConfig
```

> `FallbackModel` = model failover. `LiteLlm` = third-party/OSS. `Gemma3Ollama` = local self-hosted.
> Directly supports objective 3.1 "LLM vs SLM, self-hosted vs SaaS, OSS vs proprietary".

### `google.adk.code_executors` — Section 2 sandboxing

```
BaseCodeExecutor, BuiltInCodeExecutor, ContainerCodeExecutor,
GkeCodeExecutor, VertexAiCodeExecutor, AgentEngineSandboxCodeExecutor,
UnsafeLocalCodeExecutor, CodeExecutorContext
```

Plus `google.adk.integrations.cloud_run.CloudRunSandboxCodeExecutor`
(runs Python via the `sandbox` CLI **inside** a Cloud Run container; fields include
`sandbox_bin`, `allow_egress`, `stateful`, `timeout_seconds`, `error_retry_attempts`).

> `GkeCodeExecutor` requires `google-adk[extensions]`.
> `UnsafeLocalCodeExecutor` is the explicitly-unsafe one — a likely exam distractor.

### `google.adk.plugins`

```
BasePlugin, PluginManager, LoggingPlugin, DebugLoggingPlugin,
ReflectAndRetryModelPlugin, ReflectAndRetryToolPlugin
```

### `google.adk.skills` — **this is the Skill Registry surface**

```
Skill, SkillRegistry, Frontmatter, Resources, Script,
DEFAULT_SKILL_SYSTEM_INSTRUCTION,
load_skill_from_dir, load_skill_from_dir_async,
load_skills_from_dir, load_skills_from_dir_async,
load_skill_from_gcs_dir, load_skill_from_gcs_dir_async,
list_skills_in_dir, list_skills_in_dir_async,
list_skills_in_gcs_dir, list_skills_in_gcs_dir_async
```

`Skill` = `frontmatter: Frontmatter` + `instructions: str` + `resources: Resources`.
Documented as three levels: **L1 frontmatter for discovery**, then instructions, then resources.

`Frontmatter` fields (exact): `name`, `description`, `license`, `compatibility`, `allowed_tools`, `metadata`.

`SkillRegistry` interface methods: `get_skill`, `search_skills`, `search_tool_description`.

### `google.adk.integrations` — maps almost 1:1 to the exam tool list

```
agent_identity, agent_registry, api_registry, bigquery, cloud_run,
crewai, daytona, e2b, eventarc, firestore, gcs, langchain, livekit,
model_armor, oci, parameter_manager, redis, secret_manager,
skill_registry, slack, vmaas
```

| Integration | Verified exports |
| :--- | :--- |
| `agent_identity` | `GcpAuthProvider`, `GcpAuthProviderScheme` |
| `agent_registry` | `AgentRegistry` |
| `api_registry` | `ApiRegistry` |
| `skill_registry` | `GCPSkillRegistry(project_id, location, credentials)` — "GCP implementation of SkillRegistry using GCP Skill Registry API"; methods `get_skill`, `search_skills`, `search_tool_description` |
| `model_armor` | `ModelArmorPlugin`, `ModelArmorConfig` |
| `redis` | `RedisSessionService`, `RedisSessionServiceConfig(uri, host, port, password, ssl, db, ttl_seconds, key_prefix)` |
| `cloud_run` | `CloudRunSandboxCodeExecutor` |
| `bigquery` | `BigQueryToolset`, `BigQueryCredentialsConfig`, `get_bigquery_skill` |
| `gcs` | `GCSToolset`, `GCSAdminToolset`, `GCSCredentialsConfig` |
| `eventarc` | `EventarcToolset`, `EventarcToolConfig`, `EventarcCredentialsConfig`, `CloudEventAttributesBinding`, `AgentProvided` |
| `secret_manager` | `SecretManagerClient` |

> `agent_registry` and `api_registry` additionally require the `mcp` package to be installed.

#### `AgentRegistry` — verified signature (exam Section 5.1 / 5.2, and 3.2)

Docstring: *"Client for interacting with the Google Cloud Agent Registry service."*

```python
from google.adk.integrations.agent_registry import AgentRegistry

registry = AgentRegistry(
    project_id="my-project",
    location="us-central1",
    header_provider=None,   # Callable[[ReadonlyContext], Dict[str, str]] | None
)
```

Verified methods:

| Method | Purpose |
| :--- | :--- |
| `list_agents()` / `search_agents()` | Discover registered agents |
| `get_agent_info()` | Fetch a registered agent's metadata |
| `get_endpoint()` / `list_endpoints()` | Resolve agent endpoints |
| `get_remote_a2a_agent()` | Build an A2A remote agent from the registry |
| `list_mcp_servers()` / `search_mcp_servers()` / `get_mcp_server()` | Discover registered MCP servers |
| `get_mcp_toolset()` | Build an `MCPToolset` from a registered MCP server |
| `get_model_name()` | Resolve the governed model name |

> [!IMPORTANT]
> This is the concrete link between **Agent Registry**, **A2A**, and **MCP**: the
> registry is the discovery/governance plane that hands you a ready-made
> `MCPToolset` or remote A2A agent. That is an excellent exam talking point.

#### `ModelArmorPlugin` — verified signature (exam Section 5.1 / 5.2)

```python
from google.adk.integrations.model_armor import ModelArmorPlugin, ModelArmorConfig

plugin = ModelArmorPlugin(
    config=ModelArmorConfig(
        prompt_template_name=...,          # str | None
        response_template_name=...,        # str | None
        input_blocked_message=...,         # str
        output_blocked_message=...,        # str
        block_on_screening_failure=...,    # bool  <- fail-closed vs fail-open
    ),
    name="model_armor_plugin",
    client=None,        # Optional[modelarmor_v1.ModelArmorAsyncClient]
    credentials=None,
)
```

Implements the full plugin callback surface: `before_run_callback`, `on_user_message_callback`,
`before_agent_callback`, `before_model_callback`, `after_model_callback`, `before_tool_callback`,
`after_tool_callback`, `after_agent_callback`, `after_run_callback`, `on_event_callback`,
and the `on_*_error_callback` family.

> `block_on_screening_failure` is the **fail-closed vs fail-open** control — a
> classic security exam distinction.

#### `GkeCodeExecutor` — verified fields (exam Section 2.1 sandboxing)

Docstring: *"Executes Python code in a dedicated Pod on GKE. This executor supports two modes of execution: 'job' and 'sandbox', which do not provide the same isolation."*

Fields: `executor_type: Literal['job', 'sandbox']`, `namespace`, `image`,
`cpu_requested`, `mem_requested`, `cpu_limit`, `mem_limit`,
`kubeconfig_path`, `kubeconfig_context`, `sandbox_gateway_name`, `sandbox_template`,
`timeout_seconds`, `stateful`, `error_retry_attempts`.

> The docstring explicitly warns the two modes **do not provide the same isolation**.
> That is exactly the kind of nuance the exam probes.

#### `A2aRemoteAgentConfig` — verified fields

`a2a_message_converter`, `a2a_task_converter`, `a2a_status_update_converter`,
`a2a_artifact_update_converter`, `a2a_part_converter`, `request_interceptors`,
`card_request_interceptors`. Built on `a2a_pb2` protobuf types.


### `google.adk.auth` — maps to "Auth Manager (OAuth 2.0)"

```
AuthConfig, AuthCredential, AuthCredentialTypes, AuthScheme, AuthSchemeType,
BaseAuthProvider, OAuth2Auth, OpenIdConnectWithConfig
```
Submodules: `credential_manager`, `credential_service`, `exchanger`, `refresher`,
`oauth2_credential_util`, `oauth2_discovery`, `auth_preprocessor`, `auth_handler`.

### `google.adk.evaluation`

Public: `AgentEvaluator`.

Evaluator modules present (these are the **real metric names**):
`final_response_match_v1`, `final_response_match_v2`, `hallucinations_v1`,
`safety_evaluator`, `trajectory_evaluator`, `response_evaluator`,
`rubric_based_final_response_quality_v1`, `rubric_based_tool_use_quality_v1`,
`rubric_based_multi_turn_trajectory_evaluator`,
`multi_turn_task_success_evaluator`, `multi_turn_tool_use_quality_evaluator`,
`multi_turn_trajectory_quality_evaluator`, `llm_as_judge`,
`custom_metric_evaluator`, `metric_evaluator_registry`.

Managers: `local_eval_sets_manager`, `gcs_eval_sets_manager`, `in_memory_eval_sets_manager`,
`local_eval_set_results_manager`, `gcs_eval_set_results_manager`.
Services: `local_eval_service`, `base_eval_service`, `vertex_ai_eval_facade`,
`_vertex_ai_scenario_generation_facade`, `simulation` (pkg).

### `google.adk.planners`

```
BasePlanner, BuiltInPlanner, PlanReActPlanner
```

### `google.adk.telemetry`

```
TelemetryConfig, ContentCapturingMode, tracer,
trace_call_llm, trace_tool_call, trace_merged_tool_calls, trace_send_data
```
Submodules include `google_cloud`, `_agent_engine_metric_exporter`, `_hallucination`,
`_token_usage`, `sqlite_span_exporter`, `node_tracing`.

### `google.adk.apps`

```
App(name, root_agent, plugins, events_compaction_config,
    context_cache_config, resumability_config)
ResumabilityConfig
```

### `google.adk.a2a`

Subpackages: `agent`, `converters`, `executor`, `logs`, `utils`, `experimental`, `_compat`.
`google.adk.a2a.agent` exports:
`A2aRemoteAgentConfig`, `A2aCardRequestConfig`, `ParametersConfig`,
`RequestInterceptor`, `CardRequestInterceptor`.
Requires `google-adk[a2a]`.

### `google.adk.optimization`

GEPA-based prompt/agent optimizers: `agent_optimizer`, `gepa_root_agent_optimizer`,
`gepa_root_agent_prompt_optimizer`, `simple_prompt_optimizer`, `local_eval_sampler`.
Exposed via the `adk optimize` CLI command.

---

## 4. `adk` CLI — verified command tree (I)

```
adk create           Creates a new app in the current folder with prepopulated agent template
adk run              Runs an agent. If no query is provided, enters interactive mode
adk web              Starts a FastAPI server with Web UI for agents
adk api_server       Starts a FastAPI server for agents
adk eval             Evaluates an agent given the eval sets
adk eval_set         Manage Eval Sets
   ├─ create
   ├─ add_eval_case
   └─ generate_eval_cases
adk test             Runs pytest on agent test JSON files under the specified folder
adk deploy           Deploys agent to hosted environments
   ├─ agent_engine
   ├─ cloud_run
   ├─ docker
   └─ gke
adk optimize         Optimizes the root agent instructions using the GEPA optimizer
adk telemetry        Manage telemetry settings
   ├─ enable
   ├─ disable
   └─ status
adk conformance      Conformance testing tools for ADK
   ├─ record
   └─ test
adk migrate
   └─ session
```

> [!IMPORTANT]
> `adk deploy` has **four** targets: `agent_engine`, `cloud_run`, `docker`, `gke`.
> Objective 4.2 ("selecting optimal deployment runtime") maps onto exactly this.

---

## 5. Official exam guide — extracted verbatim (D)

Source: <https://services.google.com/fh/files/misc/professional_agentic_architect_exam_guide_english.pdf>

| Section | Title | Weight |
| :--- | :--- | :---: |
| 1 | Building agents using low-code tools | ~13% |
| 2 | Using coding agents for application development | ~17% |
| 3 | Developing custom agents | ~33% |
| 4 | Evaluating and deploying agentic workflows | ~22% |
| 5 | Securing and governing agentic workflows | ~15% |

**Role definition (verbatim):** *"A Google Cloud Certified Professional Agentic Architect is a technical practitioner who designs and manages autonomous, AI-driven agentic workflows in Google Cloud. This individual is an experienced developer or architect who builds agentic solutions while considering reliability, performance, cost, security, and scalability."*

### Objectives (verbatim bullets)

**1.1** Configuring agentic workflows and behavior using low-code tools
- Configuring state-based workflows (pages, transition routes, and event handlers) using Gemini Enterprise tools (e.g., Gemini Enterprise Agent Designer and Customer Experience Agent Studio [CX Agent Studio])
- Creating system instructions and in-console prompt templates (e.g., few-shot and chain-of-thought) to guide agent behavior

**1.2** Connecting enterprise data to Gemini Enterprise
- Configuring agents to securely connect and query enterprise proprietary data sources (e.g., Gemini Enterprise and Agent Search)
- Ingesting and processing unstructured multimodal data (e.g., videos, audio, and images) into the agentic workflow

**2.1** Using coding agents effectively
- Configuring coding agents with Model Context Protocol (MCP) servers, custom skills, and access to tools (e.g., Antigravity and Claude Code on Google Cloud)
- Using coding agents in secure sandboxes (e.g., GKE, Cloud Workstations, and Antigravity)
- Using coding agents to refactor source code, optimize execution runtimes, and patch application-layer vulnerabilities

**2.2** Customizing coding agents for enterprise workflows
- Creating skills, plugins, extensions hooks, rules, and subagents using Antigravity
- Augmenting Antigravity with Agents CLI to build, scale, govern, and optimize deployed agents

**3.1** Designing and building agentic workflows in code
- Selecting and configuring the appropriate language model (LLM vs. SLM, self-hosted vs. SaaS, OSS vs. proprietary) considering cost, security, and agent architecture
- Building custom agents using open-source libraries (e.g., ADK)
- Configuring sessions and memory (e.g., Agent Platform Memory Bank and managed sessions)
- Configuring skills using Agents CLI (e.g., plugins and agent vs. human mode)

**3.2** Integrating enterprise domain knowledge
- Designing, configuring, and managing RAG pipelines and vector retrieval systems (embedding models, similarity scoring, reranking) using services such as vector databases (e.g., Vector Search and Agent Retrieval)
- Configuring agent permissions (e.g., Agent Identity)
- Using Google Cloud tools (e.g., Agent Registry, Google Cloud MCP Servers) to configure prebuilt and custom capabilities

**3.3** Orchestrating and coordinating agentic workflows
- Orchestrating agents using agentic protocols (e.g., MCP and A2A)
- Selecting and coordinating multiagent handoffs and workflows (parallel, sequential, graph workflow) using Google Cloud tools (Agent Identity, Agent Registry, Agent Runtime, agent policies)

**4.1** Evaluating agents in development and in production
- Creating test sets for agent evaluation (golden data, prompts, edge cases)
- Creating continuous evaluation pipelines to assess an agent's tool execution against success criteria
- Determining the appropriate evaluation framework and tooling (ADK evaluation tooling (evalset), Agent Platform Gen AI evaluation service, custom autoraters)
- Evaluating an agentic system against a golden dataset to assess response and retrieval quality

**4.2** Deploying and scaling production workloads
- Selecting optimal deployment runtime based on use case, requirements, and cost (Agent Runtime, Cloud Run, GKE)
- Troubleshooting agent issues (drift, tool invocation latency, agent reasoning loops, system failures)
- Monitoring and optimizing agents for performance, reliability, and cost

**5.1** Configuring agent security and governance
- Implementing authentication and secure tool execution (agent-to-tool API calls using OAuth 2.0)
- Configuring principal access boundary (PAB) policies using Agent Identity
- Configuring Agent Gateway to monitor traffic and track agents
- Designing and configuring agentic governance and policy enforcement (Agent Registry and Model Armor)

**5.2** Implementing secure agent behavior and execution
- Designing appropriate safety frameworks and guardrails (Agent Gateway, Model Armor, HITL)
- Configuring secure access to data and identity propagation (Agent Gateway and Agent Registry)

### Tools in scope (verbatim list)

Agent Development Kit (ADK) · Agent evaluation · Agent Gateway · Agent Identity · Agent Registry ·
Agent Retrieval and Vector Search 1.0 · Agent Runtime (formerly Agent Engine) ·
Agent Search (formerly Vertex AI Search) · Agentic protocols (A2A, MCP) · Agents CLI in Agent Platform ·
Antigravity (CLI, SDK, App) · Auth Manager (OAuth 2.0) · BigQuery · Cloud Run · Cloud SQL ·
Cloud Storage · Firestore · Gemini Enterprise · Gemini LLMs ·
Google Cloud Observability (Cloud Logging and Cloud Trace) · GKE · Memorystore for Redis ·
Model Armor · MCP servers · Model Garden · RAG Engine · Sensitive Data Protection · Skill Registry

---

## 6. Exam-tool → verified-implementation map

This is the highest-value table in the repo: it turns exam vocabulary into runnable code.

| Exam tool name | Verified implementation | Confidence |
| :--- | :--- | :--- |
| Agent Development Kit (ADK) | `google-adk` 2.9.0 | ✅ verified |
| Skill Registry | `google.adk.skills.SkillRegistry` + `integrations.skill_registry.GCPSkillRegistry` | ✅ verified |
| Agent Identity | `google.adk.integrations.agent_identity` → `GcpAuthProvider`, `GcpAuthProviderScheme` | ✅ verified |
| Agent Registry | `google.adk.integrations.agent_registry.AgentRegistry` | ✅ verified |
| Model Armor | `google.adk.integrations.model_armor.ModelArmorPlugin` | ✅ verified |
| Auth Manager (OAuth 2.0) | `google.adk.auth` (`OAuth2Auth`, exchanger, refresher, credential_service) | ✅ verified |
| Agent Runtime (formerly Agent Engine) | `adk deploy agent_engine`; `AgentEngineSandboxCodeExecutor` | ✅ CLI verified |
| Agent Platform Memory Bank | `google.adk.memory.VertexAiMemoryBankService` | ✅ verified |
| Managed sessions | `google.adk.sessions.VertexAiSessionService` | ✅ verified |
| Memorystore for Redis | `google.adk.integrations.redis.RedisSessionService` | ✅ verified |
| Agent Search (formerly Vertex AI Search) | `google.adk.tools.VertexAiSearchTool`, `DiscoveryEngineSearchTool` | ✅ verified |
| Agent Retrieval / Vector Search | `google.adk.memory.VertexAiRagMemoryService` + RAG Engine | 🟡 partial |
| MCP servers | `google.adk.tools.MCPToolset`, `RemoteMcpServer`, `McpInstructionProvider` | ✅ verified |
| A2A | `google.adk.a2a` (needs `[a2a]` extra); `a2a-sdk` 1.1.2 | ✅ verified |
| Agent evaluation | `google.adk.evaluation.AgentEvaluator`; `adk eval` / `adk eval_set` | ✅ verified |
| GKE (sandbox) | `google.adk.code_executors.GkeCodeExecutor` (needs `[extensions]`) | ✅ verified |
| Cloud Run (sandbox) | `integrations.cloud_run.CloudRunSandboxCodeExecutor`; `adk deploy cloud_run` | ✅ verified |
| BigQuery | `google.adk.tools.bigquery.BigQueryToolset` | ✅ verified |
| Cloud Logging / Cloud Trace | `google.adk.telemetry` (+ `google_cloud` exporter); `adk telemetry` | ✅ verified |
| Model Garden (OSS/SLM) | `google.adk.models.Gemma`, `LiteLlm`, `Gemma3Ollama`, `FallbackModel` | ✅ verified |
| HITL | `google.adk.tools.request_input`, `get_user_choice`, `LongRunningFunctionTool` | ✅ verified |
| **Agent Gateway** | policy-enforcing ingress/egress proxy for agentic MCP & A2A traffic (no local ADK class; enforced at gateway layer) | 🟡 architectural / gateway plane |
| **Agents CLI in Agent Platform** | distinct from `adk` CLI? not confirmed | ❓ **UNVERIFIED** |
| **Gemini Enterprise vs. Gemini Enterprise App (`GEApp`) vs. Agent Platform (`GEAP`)** | **Gemini Enterprise** is the overarching umbrella brand. **Gemini Enterprise App (`GEApp`)** is the turn-key enterprise search & assistant web application (console product), whereas **Agent Platform (`GEAP`)** is the developer platform (`adk`, Agent Runtime, Agent Registry, Memory Bank). | ✅ architectural taxonomy |
| **Code Mender** | Autonomous AI security & vulnerability-patching coding agent (maps to Objective 2.1 *"patch application-layer vulnerabilities"* using static/dynamic analysis, fuzzing, and sandboxed verification). | ✅ architectural tool (Section 2.1) |
| **GKE Inference Gateway** | Kubernetes Gateway API extension (`InferencePool`, `InferenceModel`) for KV-cache & prefix-cache aware routing, LoRA multiplexing, and criticality load-shedding on GKE GPU pools. | ✅ GKE AI infrastructure |
| **Sensitive Data Protection** | no ADK integration module | 🟡 use `google-cloud-dlp` (or via Model Armor SDP templates) |

---

## 7. Corrections to the old repo

| Old repo claim | Reality |
| :--- | :--- |
| ~~`gemini-3.7-flash` is fake~~ | **It is real** (L). Keep it. |
| `text-embedding-005` | Stale → `gemini-embedding-2` |
| `Gemma 2 (2B/9B/27B)` | Stale → `gemma-4-26b-a4b-it`, `gemma-4-31b-it` |
| "ADK module" using only `google-genai` | Must use real `google-adk` |
| `mcp>=1.3.0` | Current is `2.2.0` |
| No `google-adk` dependency | Must add, with extras |
| No `a2a-sdk` | Must add for Section 3.3 |

---

## 8. Authoring rules for all contributors

1. **Never** invent a model ID, class name, import path, or CLI flag. If it is not in this file, verify it or mark it UNVERIFIED.
2. Use `common/models.py` as the single source of model IDs — no hard-coded strings in labs.
3. Mark Pre-GA / unverified products inline with a `> [!WARNING]` callout naming the closest GA equivalent.
4. Every lab must run **offline by default** and only touch Google Cloud behind an explicit `--live` flag.
5. Every lab must ship a `cleanup.sh` that is idempotent and safe to run twice.
6. Prefer showing the **decision** (when to use X over Y) over showing more code — that is what the exam tests.
