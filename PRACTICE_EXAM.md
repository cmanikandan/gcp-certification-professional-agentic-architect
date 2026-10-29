# Google Cloud Certified Professional Agentic Architect — 80-Question Practice Exam

> [!IMPORTANT]
> **Personal, unofficial repository.** This is a personal study project. It is **not
> affiliated with, endorsed by, or maintained by Google or Google Cloud**. These questions
> were written by the repository author — they are **not real exam questions** and are not
> drawn from the live exam. For official guidance — exam objectives, registration, policies,
> and the current exam guide — refer to
> **[cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect)**.
> See [`DISCLAIMER.md`](DISCLAIMER.md) for the full disclaimer.

> [!NOTE]
> **Exam Format, Mid-November GA Launch & Test-Taking UI**:
> - **Beta vs. GA Question Count**: This practice exam contains **80 multiple-choice and multiple-select questions**, matching the **~80-question Beta exam** format (3-hour window). **The Generally Available (GA) exam launches in mid-November and will have a lesser number of questions** (standard ~50–60 questions, 2-hour window).
> - **Delivery**: Available **online-proctored** or **onsite-proctored** (testing center).
> - **UI Strategy**: The live test interface provides **Mark for Review** and **Strike-through**. Practice mentally striking through distractors that violate least-privilege IAM (`roles/owner`, `roles/editor`, static JSON SA keys), sandbox safety (`UnsafeLocalCodeExecutor`), or protocol boundaries (using MCP for agent-to-agent delegation).
> - **Beta Calibration**: Across the 5 official domains (**13% / 17% / 33% / 22% / 15%**), roughly **30–35% of questions** weave in **IAM roles, least-privilege permissions, Agent Identity, Principal Access Boundaries (PAB), Connector Auth, and cross-project access**, alongside heavy **customer support** and **HIPAA / regulated industry** scenarios.

<details><summary><b>How to use this exam</b></summary>
Answers are collapsed by default. Read the scenario, mentally strike through invalid distractors, choose your answer, and expand the details block to check it. Aim for <b>≥80% (64 / 80)</b> overall and ≥80% in every domain.
</details>

---

## Domain 1: Building Agents Using Low-Code Tools (~13% · Questions 1–10)

### Question 1
**Scenario**: Your retail organization is deploying an omnichannel customer support agent using **Customer Experience Agent Studio (`GECX` / CX Agent Studio)**. The agent must guide customers through a regulated 3-step order refund workflow (`Verify Identity -> Validate Return Reason -> Issue Refund`). Compliance rules require that every step execute in exact sequence, missing ZIP or order numbers be repeatedly prompted until provided, and two consecutive invalid tracking numbers deterministically escalate the session to a human support agent with full context preserved.

**Which configuration in CX Agent Studio (`GECX`) meets these requirements?**
- **A)** Configure a **Deterministic Flow** with dedicated **Pages** for each stage, mark Order ID and ZIP as **Required Form parameters** with reprompt messages, use **Condition Transition Routes** (`$session.params.verified == true`), and attach a **`sys.no-match-2` Event Handler** transitioning to a Live Agent Handoff page.
- **B)** Create a single probabilistic Generative Playbook in Agent Designer and instruct the LLM in system instructions to count invalid tracking numbers and refuse to skip steps.
- **C)** Upload the refund policy PDF to Agent Search and set model temperature to `0.0` so zero-shot generation follows the 3 steps automatically.
- **D)** Write an inline webhook using static Service Account JSON keys to track retry counts in a global Python dictionary.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In **CX Agent Studio (`GECX`)**, regulated step-by-step customer support processes require **Deterministic Flows**: **Pages** represent states, **Required Form parameters** handle slot-filling loops, **Transition Routes** enforce deterministic state branching, and **`sys.no-match-2` Event Handlers** guarantee escalation after exactly two invalid inputs while preserving session parameters. → Lab 02 — CX Agent Studio State.
- **Why B and C are incorrect**: Generative Playbooks and `temperature=0.0` remain probabilistic; LLMs can miscount retries or skip mandatory verification steps under adversarial input.
- **Why D is incorrect**: Static JSON keys and in-memory webhook counters violate both declarative state management and IAM security best practices.
</details>

---

### Question 2
**Scenario**: A telecommunications company is redesigning its customer support virtual agent in **CX Agent Studio (`GECX`)**. Customers start conversations with open-ended, unstructured troubleshooting questions (e.g., *"My fiber router blinks orange whenever it rains"*), which require synthesizing troubleshooting articles. However, if the customer asks to **upgrade their billing plan or process an equipment replacement**, compliance mandates a strict identity check and PCI-compliant confirmation flow.

**Which GECX architectural pattern should you choose?**
- **A)** A pure Deterministic Flow creating hundreds of rigid Intent Pages for every possible router LED blinking pattern.
- **B)** A pure Probabilistic Generative Playbook handling both router troubleshooting and PCI billing upgrades via natural-language prompt instructions.
- **C)** A **Hybrid Flow architecture**: use a **Probabilistic Generative Playbook** grounded on **Agent Search** for open-ended troubleshooting and triage, which deterministically transitions into a **GECX Deterministic Flow Page** whenever a billing upgrade or replacement action is triggered.
- **D)** Deploy two disconnected chatbots with separate web URLs and ask customers to copy-paste their chat transcript between windows.

<details><summary>Show answer</summary>

**Correct Answer: C**
**Explanation**:
- **Why C is correct**: **GECX Hybrid Flows** combine the flexibility of **Generative Playbooks** (handling open-ended troubleshooting grounded in Agent Search) with the auditability of **Deterministic Flows** (Pages, Form parameters, and deterministic Transition Routes) for regulated financial or account-mutating steps, sharing a single session state. → Lab 01 & Lab 02.
- **Why A is incorrect**: Enumerating every open-ended troubleshooting permutation in static intents causes state explosion and high maintenance overhead.
- **Why B is incorrect**: Executing regulated PCI plan changes purely via probabilistic prompt instructions lacks deterministic slot and state enforcement.
- **Why D is incorrect**: Breaks conversational continuity and session state.
</details>

---

### Question 3
**Scenario**: You are rolling out **Gemini Enterprise (`GEApp`)** as the unified assistant workspace for 25,000 employees. You must connect two enterprise systems:
1. **Confluence & Google Drive** (5 million documents) so employees can run fast semantic searches while strictly seeing **only** documents their corporate identity has ACL permission to view.
2. **Jira** so an employee can tell the assistant *"Create a P1 incident ticket assigned to my team"*, and Jira records the **specific logged-in employee** (not a shared bot account) as the ticket reporter.

**Which dual connector authentication design should you configure?**
- **A)** Configure **ACL-aware ingestion sync** using a dedicated Connector Service Account + **Workforce Identity Federation** for Confluence/Drive in **Agent Search**, and configure **real-time 3-legged OAuth 2.0 (3LO)** via **Auth Manager** (`IAMConnectorCredentialsServiceClient`) for Jira action execution.
- **B)** Configure a single Jira Administrator API token shared by all 25,000 employees and disable ACL sync on Confluence.
- **C)** Download a Service Account JSON key with `roles/owner` and embed it inside an Agent Designer prompt template.
- **D)** Force all 5 million Confluence pages through 3LO per-file user consent popups on every search query without indexing.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Enterprise connectors in **Gemini Enterprise (`GEApp`)** separate **read/search indexing** (Connector Service Account + Workforce Identity Federation syncing Document-Level ACLs into **Agent Search**) from **transactional write actions** (**Auth Manager** + `IAMConnectorCredentialsServiceClient` executing 3-legged OAuth 2.0 consent so mutations run under the human user's identity and audit trail). → Lab 03 — Enterprise Data and Multimodal.
- **Why B and C are incorrect**: Shared admin tokens, `roles/owner`, and static JSON keys cause cross-user data leakage and destroy per-user audit attribution.
- **Why D is incorrect**: Real-time unindexed crawling cannot search 5M documents at interactive latency.
</details>

---

### Question 4
**Scenario**: An insurance carrier is building a claims triage agent in **Gemini Enterprise Agent Designer**. Claimants upload a PDF repair estimate, smartphone photos of bumper damage, and a 4-minute MP4 video walkthrough with spoken narration into a Cloud Storage bucket (`gs://claims-intake-prod/`). The agent must cross-check whether the spoken narration, visual damage, and PDF line items agree, while following **least-privilege IAM** on the bucket and Vertex AI.

**Which ingestion design and IAM role binding should you implement?**
- **A)** Pass the `gs://` URIs for the PDF, photos, and MP4 video directly in a single multimodal request to **`gemini-3.7-flash`**, and grant the agent's identity **`roles/storage.objectViewer`** (scoped to `claims-intake-prod`) plus **`roles/aiplatform.user`**.
- **B)** Split the files across Speech-to-Text, Vision OCR, and Document AI, concatenate the text into `gemini-2.5-flash-lite`, and grant `roles/storage.admin` + `roles/owner`.
- **C)** Strip the audio track with `ffmpeg` and pass frames to `gemma-4-31b-it` using a downloaded Service Account JSON key.
- **D)** Load the raw MP4 bytes into `gemini-embedding-2` (8,192-token text embedding model) to generate a written claim summary.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `gemini-3.7-flash` (1M token window) natively reasons across PDFs, images, audio, and MP4 video simultaneously via `gs://` URIs, preserving temporal/visual alignment. Scoping `roles/storage.objectViewer` to the specific bucket and `roles/aiplatform.user` to the project enforces strict least privilege. → Lab 03 — Enterprise Data and Multimodal.
- **Why B is incorrect**: Separate APIs lose cross-modal synchronization and `roles/storage.admin` + `roles/owner` severely over-privilege the agent.
- **Why C is incorrect**: Stripping audio loses spoken narration, and static JSON keys are an IAM anti-pattern.
- **Why D is incorrect**: `gemini-embedding-2` produces embeddings, not generative cross-modal reasoning.
</details>

---

### Question 5
**Scenario**: A hospital network subject to **HIPAA** is building a low-code **patient support agent** in **CX Agent Studio (`GECX`)** and **Gemini Enterprise (`GEApp`)** to answer post-discharge care questions from approved clinical leaflets and schedule follow-up appointments.

**Which low-code architecture satisfies HIPAA compliance and least privilege?**
- **A)** Deploy inside a **BAA-covered** Google Cloud project protected by **VPC Service Controls** and **CMEK**, screen patient inputs/outputs with **Model Armor + Sensitive Data Protection (`SdpAdvancedConfig`)**, ground clinical FAQs exclusively on an **Agent Search** data store (`roles/discoveryengine.viewer`), and handle appointment booking via a **Deterministic GECX Flow** with zero raw PHI logging.
- **B)** Use an ungrounded zero-shot prompt in a personal Gmail consumer account and log full patient chat transcripts to a public Cloud Storage bucket for debugging.
- **C)** Paste 800 pages of patient EHR records into the Agent Designer system instructions so every patient session shares the same prompt cache.
- **D)** Grant `allAuthenticatedUsers` `roles/discoveryengine.admin` on the clinical data store so patients can query leaflets without authentication.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Regulated **HIPAA customer support agents** require BAA-eligible services inside VPC-SC + CMEK, **Model Armor + SDP** to redact unintended PHI, grounded retrieval (`roles/discoveryengine.viewer`) to prevent clinical fabrication, and **Deterministic GECX Flows** for scheduling mutations without capturing PHI in telemetry logs. → Lab 01, Lab 02 & Lab 03.
- **Why B, C, and D are incorrect**: Consumer accounts lack a HIPAA BAA, pasting EHR data into shared system instructions leaks PHI across patients, and `allAuthenticatedUsers` exposes data to every Google account on Earth!
</details>

---

### Question 6
**Scenario**: Your IT helpdesk team uses **Gemini Enterprise Agent Designer** to triage laptop tickets. Users write messy messages containing serial numbers in inconsistent formats, and the agent frequently extracts malformed asset tags. The helpdesk team has zero Python coding experience and cannot change models.

**What is the most effective low-code improvement in Agent Designer?**
- **A)** Add structured **few-shot examples** (diverse messy user inputs paired with exact extracted asset-tag outputs) and explicit **chain-of-thought** formatting steps inside the in-console prompt template.
- **B)** Deploy a custom GKE cluster with `GkeCodeExecutor` to compile regexes dynamically.
- **C)** Increase model temperature to `1.5` to encourage creative tag extraction.
- **D)** Grant the agent `roles/iam.securityAdmin` so it can look up IAM bindings instead.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 1.1 explicitly tests *"Creating system instructions and in-console prompt templates (e.g., few-shot and chain-of-thought) to guide agent behavior"*. Few-shot examples teach exact entity formatting in low-code without custom webhooks or code. → Lab 01 — Agent Designer Workflows.
- **Why B is incorrect**: Violates the no-code requirement.
- **Why C and D are incorrect**: High temperature increases formatting variance, and IAM admin roles are unrelated and unsafe.
</details>

---

### Question 7
**Scenario**: A runtime customer support agent deployed in Project `support-runtime-prod` needs **read-only search access** to an **Agent Search** (Discovery Engine) enterprise knowledge data store hosted in Project `knowledge-hub-prod`. It must **never** be able to delete documents, modify schemas, or reconfigure connectors.

**Which predefined IAM role should you grant to the support agent's identity on `knowledge-hub-prod`?**
- **A)** `roles/discoveryengine.viewer`
- **B)** `roles/discoveryengine.admin`
- **C)** `roles/discoveryengine.editor`
- **D)** `roles/editor`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `roles/discoveryengine.viewer` grants least-privilege read/query (`servingConfigs.search` / `answer`) access to Agent Search / Gemini Enterprise data stores without allowing document ingestion, deletion, or connector administration. → Lab 03 — Enterprise Data and Multimodal.
- **Why B, C, and D are incorrect**: `editor` and `admin` roles allow mutating or deleting indexed enterprise data stores, violating least privilege.
</details>

---

### Question 8
**Scenario**: While testing a **Gemini Enterprise (`GEApp`)** action connector backed by `google.cloud.iamconnectorcredentials_v1alpha.IAMConnectorCredentialsServiceClient`, your agent calls `RetrieveCredentialsRequest(connector=..., user_id="alice@corp.com", scopes=["jira:write"], continue_uri="https://app.corp.com/callback")`. Because Alice has never used the Jira connector before, no OAuth refresh token exists yet.

**How does the Connector Credentials service respond so the agent can complete authorization safely?**
- **A)** It returns metadata indicating **`uri_consent_required` / `consent_pending`** with an authorization consent URL so the UI prompts Alice to complete the **3-legged OAuth 2.0** flow before retrying the tool call.
- **B)** It automatically falls back to the organization's root Google Cloud Organization Admin credential.
- **C)** It scrapes Alice's plaintext password from Active Directory logs.
- **D)** It permanently bans `alice@corp.com` via a Principal Access Boundary.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `IAMConnectorCredentialsServiceClient` (`RetrieveCredentialsRequest`) manages per-user 3LO credentials cleanly: when a user has not yet granted OAuth scopes, the response signals `uri_consent_required` / `consent_pending` so the client surfaces a consent link (`continue_uri`) and finalizes the user-scoped token via `FinalizeCredentialsRequest`. → Lab 03 & Lab 16.
- **Why B, C, and D are incorrect**: Falling back to admin credentials or scraping passwords breaks user-scoped OAuth security, and PAB does not ban users on missing OAuth tokens.
</details>

---

### Question 9
**Scenario**: A retail bank builds a low-code loan-inquiry assistant in **Agent Designer**. Regulatory policy forbids the assistant from giving credit-score repair advice and requires it to redirect any credit-score question to the bank's dedicated credit portal.

**What is the most direct first-line control in Agent Designer, and when must you add CX Agent Studio or Model Armor alongside it?**
- **A)** Add explicit negative constraints and fallback phrasing in Agent Designer's **System Instructions** for routine topical redirection, and layer **Model Armor** (`ModelArmorConfig`) if adversarial jailbreak resistance is required.
- **B)** Train a new foundation model from scratch without the word "credit" in its vocabulary.
- **C)** Replace Agent Designer with Cloud CDN rules.
- **D)** Set `max_output_tokens=5` so the agent cannot form complete sentences.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: System Instructions establish polite topical scope in Agent Designer, while **Model Armor** provides deterministic safety/jailbreak enforcement outside the prompt context when adversarial compliance guarantees are required. → Lab 01 & Lab 17.
- **Why B, C, and D are incorrect**: Pre-training from scratch is prohibitive, Cloud CDN is an HTTP asset cache, and truncating output breaks all legitimate loan answers.
</details>

---

### Question 10
**Scenario**: In **CX Agent Studio (`GECX`)**, a customer is mid-way through filling out a 4-parameter `ScheduleAppointment` Page (`date`, `time`, `clinic_location`, `insurance_plan`). After providing `date` and `time`, the customer suddenly asks an off-script question: *"By the way, is parking free at the downtown clinic?"*

**How should you configure GECX so the agent answers the parking question accurately from hospital documents AND seamlessly resumes collecting `clinic_location` and `insurance_plan`?**
- **A)** Enable a **Knowledge / Agent Search Data Store handler** (or generative fallback) on the Page/Flow with session state preserved, so the agent answers the grounded FAQ and automatically re-prompts for the next missing **Required Form parameter** (`clinic_location`).
- **B)** Trigger `sys.no-match-default` to wipe `$session.params` and terminate the phone call.
- **C)** Force the user to restart from the beginning whenever an intent does not match a date string.
- **D)** Disable Required Form parameters and hope the user remembers to mention their insurance plan later.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Linking **Agent Search** data stores to a **GECX Page/Flow** enables grounded FAQ digressions while the Page's **Form** state machine retains already-collected `$session.params` (`date`, `time`) and automatically resumes prompting for the remaining required slots (`clinic_location`, `insurance_plan`). → Lab 02 & Lab 03.
- **Why B, C, and D are incorrect**: Wiping session state frustrates customers, and removing required form slots breaks deterministic appointment booking.
</details>

---

## Domain 2: Using Coding Agents for Application Development (~17% · Questions 11–24)

### Question 11
**Scenario**: Your security engineering team wants **deterministic, non-bypassable enforcement** in **Antigravity** across a monorepo so that:
1. Any attempt by the coding agent to execute `rm -rf`, `gcloud projects delete`, or `terraform destroy` via `run_command` is **hard-blocked** before execution with an explanation returned to the model.
2. Whenever the agent edits a Python file, `ruff check` runs automatically afterward.
3. The agent is **prevented from ending its turn** if the unit test suite (`pytest -q`) is currently failing.

**Which Antigravity customization file and lifecycle events should you configure?**
- **A)** Configure **`.agents/hooks.json`** with a **`PreToolUse`** hook (`matcher: "run_command"`, returning camelCase JSON `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`), a **`PostToolUse`** hook (`matcher: "write_to_file|replace_file_content"`) running `ruff`, and a **`Stop`** hook returning `{"decision": "block", "reason": "pytest failed"}` when tests fail.
- **B)** Write *"Please never run destructive commands and always run pytest"* inside `GEMINI.md` and trust the LLM with 100% compliance.
- **C)** Add a `description` field to `skills.json` without any hooks or policies.
- **D)** Set `temperature=0.0` in `mcp_config.json`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In Antigravity, **`.agents/hooks.json`** executes deterministic shell gates outside the LLM's probabilistic reasoning: **`PreToolUse`** inspects camelCase `toolInput` on `stdin` and enforces `"deny"` / `"force_ask"` / `"overwrite"`, **`PostToolUse`** runs linters after file edits, and **`Stop`** (`"decision": "block"`) prevents premature task completion until tests pass. → Lab 06 — Antigravity Customization.
- **Why B and C are incorrect**: `GEMINI.md` and `SKILL.md` are prompt-level instructions, not deterministic execution gates.
- **Why D is incorrect**: `mcp_config.json` configures MCP servers, not model temperature or command hooks.
</details>

---

### Question 12
**Scenario**: Your platform team is authoring Antigravity customizations for a 400-engineer polyglot repository containing Go services, React frontends, Terraform (`**/*.tf`), and complex database-migration runbooks (with helper Python scripts). You want to **minimize context-window token usage** on every turn while keeping repo-wide architecture overview always visible.

**How should you partition instructions across `GEMINI.md` (`AGENTS.md`), `.agents/rules/*.md`, and `.agents/skills/*/SKILL.md`?**
- **A)** Keep **`GEMINI.md` / `AGENTS.md`** concise for repo-wide always-on context; put language/IaC-specific standards in **`.agents/rules/*.md`** with `trigger: glob` (e.g., `**/*.tf`) or `trigger: model_decision`; and package multi-step migration workflows + `scripts/` into **`.agents/skills/<name>/SKILL.md`** (indexed via `skills.json`) for **L1 → L2 → L3 progressive disclosure**.
- **B)** Paste all 80 pages of Go, React, Terraform, and migration scripts into the root `GEMINI.md` so every turn pays 120,000 input tokens.
- **C)** Put YAML `trigger: glob` frontmatter at the top of `GEMINI.md` (which ignores frontmatter and loads unconditionally).
- **D)** Store coding guidelines inside `.evalset.json` files.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Antigravity separates **always-on hierarchical context** (`GEMINI.md` / `AGENTS.md`, plain Markdown with no frontmatter) from **conditionally triggered rules** (`.agents/rules/*.md` using `trigger: glob | model_decision | manual`) and **3-level progressive-disclosure skills** (`SKILL.md` frontmatter L1 → Markdown instructions L2 → `scripts/` & `references/` L3). → Lab 06 — Antigravity Customization.
- **Why B and C are incorrect**: Bloating `GEMINI.md` wastes tokens and degrades attention; `GEMINI.md` does not support `glob` frontmatter triggers.
- **Why D is incorrect**: `.evalset.json` stores ADK evaluation test cases, not coding-agent rules.
</details>

---

### Question 13
**Scenario**: You want to distribute a standardized **"GCP FinOps & Security Kit"** across 30 engineering teams using Antigravity. The kit must bundle 4 custom skills (`skills/`), 2 read-only auditor subagents (`agents/`), mandatory `PreToolUse` guardrails (`hooks/hooks.json`), and a team ruleset (`rules/`) as a single versioned unit.

**Which Antigravity manifest and directory structure packages all of these customizations together?**
- **A)** An **Antigravity Plugin** defined by **`plugin.json`** inside `.agents/plugins/<plugin-name>/` (or `~/.gemini/config/plugins/<plugin-name>/`) containing `skills/` (and `skills.json`), `agents/`, `hooks/hooks.json`, and `rules/`.
- **B)** A single `Dockerfile` placed in `/tmp`.
- **C)** A CX Agent Studio Transition Route export.
- **D)** A BigQuery scheduled query.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 2.2 explicitly covers *"Creating skills, plugins, extensions hooks, rules, and subagents using Antigravity"*. An Antigravity **Plugin** (`plugin.json`) is the distributable bundle that groups `skills/`, `agents/`, `hooks/hooks.json`, and `rules/` for team-wide installation. → Lab 06 — Antigravity Customization.
- **Why B, C, and D are incorrect**: None of these package Antigravity IDE/CLI customizations.
</details>

---

### Question 14
**Scenario**: An Antigravity coding agent is invoking the **Agents CLI (`adk` / `agents-cli`)** inside an automated pipeline to evaluate (`adk eval`), prompt-optimize (`adk optimize`), and deploy (`adk deploy cloud_run`) an enterprise support agent. On its first attempt, the coding agent hangs indefinitely waiting for an interactive `[y/N]` confirmation prompt and misparses ANSI terminal spinner characters.

**How should you configure the Agents CLI invocation for coding-agent automation?**
- **A)** Run the CLI in **Agent Mode** (headless, non-interactive flags, structured JSON output, and deterministic exit codes) rather than interactive **Human Mode** TTY spinners/prompts, and gate production deploys via explicit CI/CD or `PreToolUse` approval policies.
- **B)** Use `adk web` and instruct the coding agent to take screenshots of localhost every 100ms.
- **C)** Pipe `yes | rm -rf` before every CLI command with `UnsafeLocalCodeExecutor`.
- **D)** Rewrite the entire `google-adk` CLI in assembly.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objectives 2.2 and 3.1 test *"Augmenting Antigravity with Agents CLI to build, scale, govern, and optimize deployed agents"* and *"agent vs. human mode"*. **Human Mode** (`adk web`, interactive `adk run`) uses TTY prompts and ANSI formatting for humans, whereas **Agent Mode** disables interactive stdin blocks and emits machine-parseable JSON + exit codes so Antigravity can orchestrate `adk eval`, `adk optimize` (GEPA), and `adk deploy` reliably. → Lab 06 & Lab 10.
- **Why B, C, and D are incorrect**: Screenshot loops and `UnsafeLocalCodeExecutor` are brittle and unsafe workarounds.
</details>

---

### Question 15
**Scenario**: A healthcare fintech enterprise wants human software engineers to use **Claude Code on Google Cloud** and **Antigravity** to refactor HIPAA-regulated microservices. Security policy mandates:
1. **Zero source code or credentials** may ever reside on developers' local laptops.
2. All LLM coding calls must stay inside the company's **VPC Service Controls (VPC-SC)** perimeter using Google Cloud IAM — **no external third-party API keys**.
3. Developers must use **least-privilege IAM** without static JSON Service Account keys.

**Which developer sandbox and authentication architecture meets every requirement?**
- **A)** Provision **Cloud Workstations** inside the VPC-SC perimeter (persistent browser/SSH remote IDE with zero local disk sync), configure Claude Code and Antigravity to call Vertex AI endpoints via keyless **Application Default Credentials (ADC)** attached to a dedicated workstation Service Account granted **`roles/aiplatform.user`**, and enforce `iam.disableServiceAccountKeyCreation`.
- **B)** Give every engineer an external `ANTHROPIC_API_KEY` on their personal MacBook and clone the HIPAA repo to `~/Desktop`.
- **C)** Grant all engineers `roles/owner` and export static Service Account JSON keys into `.agents/mcp_config.json` committed to Git.
- **D)** Run developers' IDEs inside `VertexAiMemoryBankService`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **Cloud Workstations** (Objective 2.1) provides managed, VPC-SC-confined remote development environments so proprietary code never touches endpoints. Pairing **Claude Code on Vertex AI** and **Antigravity** with keyless ADC + least-privilege `roles/aiplatform.user` eliminates external API keys and static JSON keys. → Lab 04 & Lab 05.
- **Why B and C are incorrect**: External API keys bypass VPC-SC/BAA boundaries, local clones violate zero-laptop source policy, and committed JSON keys / `roles/owner` are severe IAM violations.
- **Why D is incorrect**: Memory Bank is an agent memory store, not a developer workstation runtime.
</details>

---

### Question 16
**Scenario**: Your application security team receives nightly SAST/fuzzing crash reports on C++ and Python services. They want an autonomous workflow that localizes the root cause in the repository, synthesizes a minimal security patch, compiles and runs exploit reproduction + fuzzers + regression suites inside a **kernel-isolated sandbox**, and opens a verified pull request for human sign-off.

**Which tool and execution sandbox combination is purpose-built for this requirement?**
- **A)** **Code Mender** paired with **GKE Agent Sandbox (`GkeCodeExecutor` configured with `executor_type="sandbox"`, gVisor `runsc`, and default-deny egress `NetworkPolicy`)**.
- **B)** CX Agent Studio Transition Routes paired with `UnsafeLocalCodeExecutor` on the production database VM.
- **C)** `GkeCodeExecutor(executor_type="job")` running in privileged root containers (`--privileged`) sharing the host Linux kernel.
- **D)** Agent Designer zero-shot prompt templates with no test execution.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **Code Mender** (Objective 2.1 *"patch application-layer vulnerabilities"*) autonomously performs root-cause analysis, patch synthesis, and fuzz/regression verification. Running verification inside **`GkeCodeExecutor(executor_type="sandbox")`** uses **GKE Sandbox (`gVisor` `runsc`)** to intercept Linux syscalls in user space, protecting the host kernel from untrusted exploit reproduction payloads. → Lab 05 — Secure Sandboxes.
- **Why B, C, and D are incorrect**: `UnsafeLocalCodeExecutor` and standard `executor_type="job"` (which shares the host kernel) expose infrastructure during exploit reproduction, and zero-shot prompts without sandbox testing cannot verify patches.
</details>

---

### Question 17
**Scenario**: You are configuring **`.agents/mcp_config.json`** in Antigravity to connect a coding agent to two Model Context Protocol (MCP) servers:
1. A local repository AST analyzer binary running as a child process on the same Cloud Workstation.
2. A shared enterprise Cloud SQL schema-inspection MCP server hosted centrally on **Cloud Run** (`--no-allow-unauthenticated`) in another team's project, exposing **85 tools** (though developers typically use only 2 tools per session).

**How should you configure transports, authentication, and context-window efficiency?**
- **A)** Use **Stdio transport** (`command`, `args`) for the local AST analyzer; use **SSE / Streamable HTTP transport** (`serverUrl` + short-lived OIDC ID token header, granting the caller **`roles/run.invoker`** on the Cloud Run MCP service) for the remote server; and enable **lazy tool-schema loading** so the 85 tool JSON schemas do not bloat every prompt turn.
- **B)** Expose the Cloud Run MCP server publicly with `--allow-unauthenticated` (`allUsers`) and eagerly inject all 85 full JSON schemas into `GEMINI.md`.
- **C)** Hardcode the Cloud SQL `postgres` superuser password in plaintext inside `mcp_config.json` and commit it to Git.
- **D)** Use the A2A `RemoteA2aAgent` protocol instead of MCP to run SQL schema queries.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Local process MCP servers use **Stdio**, while remote Cloud Run MCP servers use **SSE / Streamable HTTP** secured by Cloud Run IAM (`roles/run.invoker` + OIDC token). **Lazy loading** MCP tool schemas prevents dozens of unused tool definitions from consuming thousands of prompt tokens on every turn. → Lab 04 — MCP and Tooling.
- **Why B and C are incorrect**: Public unauthenticated internal database servers and committed plaintext passwords violate security fundamentals; eager injection of 85 schemas bloats context cost.
- **Why D is incorrect**: MCP connects agents to tools/databases; A2A connects agents to peer reasoning agents.
</details>

---

### Question 18
**Scenario**: Using the **Antigravity Python SDK (`policy` module)**, you configure programmatic safety rules for an autonomous refactoring agent:
- A workspace policy sets `ALLOW` on `run_command` for `git *`.
- A higher-priority session policy sets `DENY` on `run_command` matching `git push --force*`.
- A custom `when=` Python predicate checking branch names raises a `KeyError` bug at runtime.

**According to Antigravity SDK `policy` evaluation rules, what happens when the agent attempts `git push --force` AND when the `when=` predicate throws `KeyError`?**
- **A)** Both actions are **blocked (`DENY`)**: higher-priority `session_policies` override `workspace` policies (and within the same level `DENY > ASK > ALLOW`), and any unhandled exception inside a `when=` predicate **fails closed (`DENY`)**.
- **B)** Both actions are allowed (`ALLOW`) because `ALLOW` takes precedence over `DENY` and exceptions fail open to maximize developer velocity.
- **C)** Antigravity disables sandboxing (`enable_sandbox=False`) automatically whenever a `KeyError` occurs.
- **D)** `GEMINI.md` overrides programmatic `session_policies`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In the Antigravity SDK 9-level policy hierarchy (`session_policies` → ... → `workspace` → ... → `system_defaults`), higher-priority levels win, **`DENY > ASK > ALLOW`** resolves same-level ties, and any exception raised by a custom `when=` predicate deterministically **fails closed (`DENY`)**. → Lab 06 — Antigravity Customization.
- **Why B, C, and D are incorrect**: Failing open or allowing `GEMINI.md` text to override SDK security policies would create trivial security bypasses.
</details>

---

### Question 19
**Scenario**: You want your primary Antigravity coding agent to delegate security reviews of generated Terraform files to a specialized **`security-critic` subagent** defined in `.agents/agents/security-critic.md`. You must ensure the `security-critic` subagent: (1) cannot modify files or run shell commands, (2) does not pollute the parent coding agent's 100K-token coding context with verbose audit checklists, and (3) cannot recursively spawn infinite subagents.

**How should you configure the subagent?**
- **A)** Define `security-critic` in `.agents/agents/` with **write/command tools disabled (`enable_write_tools: false`)** so it operates in an **isolated read-only subagent context window**, and set **`max_subagent_depth` / `allowed_subagents`** recursion bounds.
- **B)** Paste the entire security checklist into the parent agent's conversation every turn and grant `BypassSandbox: true`.
- **C)** Give `security-critic` `roles/owner` and unrestricted `run_command` access.
- **D)** Deploy `security-critic` as a Cloud SQL stored procedure.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Antigravity subagents run in **isolated context windows** (returning only a concise audit report to the parent), enforce tool-group separation (`enable_write_tools: false` guarantees read-only auditing), and prevent runaway fan-out via `max_subagent_depth` and `allowed_subagents`. → Lab 06 — Antigravity Customization.
- **Why B, C, and D are incorrect**: Polluting parent context wastes tokens, granting write/owner privileges violates read-only critic separation, and SQL procedures are unrelated.
</details>

---

### Question 20
**Scenario**: A developer asks an Antigravity coding agent to diagnose why a **600 MB NDJSON production error log** stored on their Cloud Workstation exhibits spike patterns every Tuesday at 02:00 UTC.

**What is the fastest, cheapest, and most accurate coding-agent pattern?**
- **A)** Instruct the coding agent to write and run a streaming Python script inside its local workspace sandbox to aggregate timestamps and error codes, then inspect only the compact summary output.
- **B)** Read all 600 MB (~180M tokens) raw into the LLM context window.
- **C)** Upload all 600 MB into `VertexAiMemoryBankService` as conversational user preferences.
- **D)** Embed every JSON line with `gemini-embedding-2` before counting timestamps.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: 600 MB (~180M tokens) vastly exceeds the 1,048,576-token window of Gemini models, and exact timestamp aggregation is a deterministic computational task best solved by having the coding agent write and run a small streaming Python analyzer. → Lab 04 & Lab 05.
- **Why B, C, and D are incorrect**: Exceeds context limits, misuses conversational memory, and wastes money doing approximate vector math for exact aggregation.
</details>

---

### Question 21
**Scenario**: A serverless team runs an ADK coding/data-analysis helper on **Cloud Run** (without a GKE cluster) that occasionally needs to execute short, untrusted 5-second Python calculation snippets with **zero outbound internet access** and **clean state reset** after every snippet.

**Which code executor configuration should they select?**
- **A)** `CloudRunSandboxCodeExecutor(allow_egress=False, stateful=False, timeout_seconds=10)` from `google.adk.integrations.cloud_run`
- **B)** `UnsafeLocalCodeExecutor()` inside the main web server process
- **C)** `CloudRunSandboxCodeExecutor(allow_egress=True, stateful=True)`
- **D)** `BuiltInCodeExecutor` with `roles/owner` attached to the Cloud Run service account

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `CloudRunSandboxCodeExecutor` runs snippets inside a sandboxed subprocess (`sandbox_bin`) within Cloud Run; setting `allow_egress=False` blocks outbound data exfiltration and `stateful=False` resets state cleanly between runs without requiring a GKE cluster. → Lab 05 & Lab 14.
- **Why B, C, and D are incorrect**: `UnsafeLocalCodeExecutor` has zero isolation, `allow_egress=True, stateful=True` violates both network and statelessness constraints, and `roles/owner` violates least privilege.
</details>

---

### Question 22
**Scenario**: Your coding agent uses **`adk optimize`** (from `google.adk.optimization`, powered by **GEPA** — `gepa_root_agent_prompt_optimizer`) to improve a customer-support triage agent whose tool-routing accuracy on edge cases is only 68%.

**What inputs does `adk optimize` require, and what artifact does it update?**
- **A)** It evaluates candidate system instructions against a local **Eval Set (`local_eval_sampler` / `.evalset.json`)** using evaluation metrics, iteratively mutating and selecting **root agent prompt instructions** without modifying base LLM weights.
- **B)** It runs GPU LoRA backpropagation on `gemini-3.7-flash` weights without needing an eval set.
- **C)** It modifies Principal Access Boundary (PAB) IAM policies automatically.
- **D)** It rewrites `hooks.json` into C++ kernel modules.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `adk optimize` (`gepa_root_agent_prompt_optimizer`) performs automated prompt/instruction optimization over a golden `.evalset.json` (`local_eval_sampler`), proposing instruction refinements and keeping candidates that raise empirical eval scores—no weight fine-tuning required. → Lab 06 & Lab 13.
- **Why B, C, and D are incorrect**: GEPA optimizes instructions rather than model weights, IAM boundaries, or C++ binaries.
</details>

---

### Question 23
**Scenario**: An Antigravity coding agent is refactoring a legacy payment service to integrate a **newly released Google Cloud API** published last week (after the LLM's pre-training knowledge cutoff), causing the agent to hallucinate deprecated method signatures.

**Which two mechanisms ground the coding agent in exact, current API signatures? (Select TWO)**
- **A)** Connect an authoritative **documentation MCP server** (or inspect the installed SDK package directly in `.venv` via introspection/read tools) before generating code.
- **B)** Package verified usage patterns and reference docs inside a workspace **Skill (`.agents/skills/<api>/SKILL.md` + `references/`)**.
- **C)** Increase `temperature` to `2.0` so the model guesses newer method names randomly.
- **D)** Disable all read and MCP tools so the model relies strictly on pre-training memory.
- **E)** Switch from `gemini-3.7-flash` to `gemini-embedding-2` for code generation.

<details><summary>Show answer</summary>

**Correct Answers: A and B**
**Explanation**:
- **Why A and B are correct**: Objective 2.1 tests configuring coding agents with **MCP servers** (e.g., live SDK/API doc lookup or local package introspection) and **custom skills (`SKILL.md` + `references/`)** to eliminate post-cutoff API hallucinations deterministically. → Lab 04 & Lab 06.
- **Why C, D, and E are incorrect**: Higher temperature increases hallucinations, disabling tools traps the model in stale pre-training weights, and `gemini-embedding-2` cannot generate code.
</details>

---

### Question 24
**Scenario**: In Antigravity, you configure a **`PreToolUse`** hook in `.agents/hooks.json` targeting `write_to_file` so that whenever the coding agent writes a Kubernetes manifest missing the mandatory corporate label `cost-center: ai-platform`, the hook **injects the missing label automatically** and lets the write proceed seamlessly without failing the turn.

**Which `permissionDecision` value and payload field in the hook's camelCase JSON stdout accomplishes this?**
- **A)** `"permissionDecision": "overwrite"` paired with `"updatedInput"` containing the modified `CodeContent`.
- **B)** `"permissionDecision": "deny"` with exit code `137`.
- **C)** `"permissionDecision": "crash_session"`.
- **D)** Writing snake_case `allow_multiple_edits=true` to `/dev/null`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Antigravity `PreToolUse` hooks support five `permissionDecision` actions (`"allow"`, `"deny"`, `"ask"`, `"force_ask"`, and **`"overwrite"`**). Returning `"overwrite"` with `"updatedInput"` rewrites the tool arguments deterministically before execution. → Lab 06 — Antigravity Customization.
- **Why B, C, and D are incorrect**: `"deny"` aborts the tool call instead of rewriting the input, and the remaining options are invalid schemas.
</details>

---

## Domain 3: Developing Custom Agents (~33% · Questions 25–50)

### Question 25
**Scenario**: You are building a real-time **customer support triage agent** in ADK 2.9.0. For every incoming ticket, the system must query **four independent backends** before drafting a response: (1) Order Status API (~900 ms), (2) Shipping Carrier API (~1,100 ms), (3) Loyalty Tier Lookup (~600 ms), and (4) Return Policy RAG (~800 ms). Currently, a `SequentialAgent` runs four specialist sub-agents in series, passing the full 40,000-token chat transcript to each one, resulting in **>6.5 seconds** p95 latency.

**Which ADK refactoring delivers the largest latency and token reduction while keeping results deterministic?**
- **A)** Replace `SequentialAgent` with **`ParallelAgent`** for the four independent specialist lookups (cutting lookup wall-time from $\sum T_i \approx 3.4\text{s}$ to $\max T_i \approx 1.1\text{s}$), set **`include_contents='none'`** on each worker so they don't re-prefill the 40K transcript, write compact JSON outputs via **`output_key`**, and feed those keys into a downstream synthesizer agent.
- **B)** Wrap all four agents in a `LoopAgent(max_iterations=10)` so they run 40 times sequentially.
- **C)** Convert every local Python function into a cross-region A2A network call over public internet without concurrency.
- **D)** Switch all four simple lookups to `gemini-2.5-pro` with a 32,768-token thinking budget.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Independent I/O and specialist lookups belong in a **`ParallelAgent`** (latency drops from $\sum T_i$ to $\max(T_i)$), and setting **`include_contents='none'`** + passing scoped state via **`{output_key}`** eliminates redundant 40K-token prompt prefills across all four parallel LLM calls! → Lab 08 & Lab 12.
- **Why B, C, and D are incorrect**: Each multiplies latency and token cost rather than reducing critical-path execution time.
</details>

---

### Question 26
**Scenario**: Compare two ways a `CustomerSupportSupervisor` (`LlmAgent`) can invoke a `BillingSpecialist` (`LlmAgent`) inside the same ADK process:
- **Pattern 1**: Add `BillingSpecialist` to `CustomerSupportSupervisor(sub_agents=[BillingSpecialist])` using **`transfer_to_agent`**.
- **Pattern 2**: Wrap `BillingSpecialist` inside **`AgentTool(agent=BillingSpecialist)`** in `CustomerSupportSupervisor(tools=[...])`.

**Which statement accurately contrasts their latency and control-flow trade-offs?**
- **A)** **`transfer_to_agent`** performs a **1-hop handoff** where `BillingSpecialist` takes over the conversation and streams directly to the user ($T_{\text{router}} + T_{\text{specialist}}$), whereas **`AgentTool`** treats `BillingSpecialist` like a synchronous function call and requires a **second parent LLM synthesis hop** ($T_{\text{sup1}} + T_{\text{specialist}} + T_{\text{sup2}}$) so `CustomerSupportSupervisor` retains final response control.
- **B)** `AgentTool` has zero LLM calls, whereas `transfer_to_agent` requires GKE Sandbox (`gVisor`).
- **C)** `transfer_to_agent` only works across separate GCP organizations via A2A, whereas `AgentTool` requires BigQuery.
- **D)** Both patterns execute identically with zero difference in LLM invocations or ownership.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Understanding **handoff (`transfer_to_agent`) vs. agent-as-a-tool (`AgentTool`)** is a classic ADK architecture trade-off: `transfer_to_agent` saves an entire supervisor re-synthesis LLM call (lower latency, direct specialist streaming), while `AgentTool` adds a second supervisor LLM pass so the parent can combine outputs from multiple specialists under one unified persona. → Lab 08 & Lab 12.
- **Why B, C, and D are incorrect**: Misstate ADK's in-process delegation mechanics.
</details>

---

### Question 27
**Scenario**: In ADK 2.9.0, you are building a hierarchical customer-support system. A top-level `LlmAgent` (`SupportRouter`) dynamically routes either to `LiveTroubleshootingAgent` (`LlmAgent`) or to a strict 3-step `HipaaRecordsReleasePipeline` (`VerifyConsent -> RedactNotes -> GenerateSummary`). You notice `SequentialAgent` emits a `DeprecationWarning` recommending `google.adk.workflow.Workflow`, yet passing a `Workflow` directly inside `SupportRouter(sub_agents=[...])` fails validation.

**What is the verified ADK 2.9.0 architectural solution?**
- **A)** Keep **`SequentialAgent`** inside `SupportRouter.sub_agents` (or wrap `Workflow` inside an `AgentTool`), because ADK 2.9.0's deprecation message explicitly states: *"Workflow cannot yet be used as an LlmAgent sub-agent."*
- **B)** Replace `SequentialAgent` with `ParallelAgent` so `GenerateSummary` runs before `VerifyConsent`.
- **C)** Remove `SupportRouter` and require patients to call three separate REST endpoints manually.
- **D)** Pass `UnsafeLocalCodeExecutor` into `sub_agents` to bypass validation.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Verified directly against ADK 2.9.0 (`docs/VERIFIED_FACTS.md`): `Workflow` provides 0ms deterministic edge routing at the top level, **but cannot yet be nested inside `LlmAgent.sub_agents`**, which is why `SequentialAgent` / `ParallelAgent` / `LoopAgent` remain supported in 2.9.0 for hierarchical sub-agent trees. → Lab 08 — ADK Fundamentals.
- **Why B, C, and D are incorrect**: Running `GenerateSummary` before `VerifyConsent` violates HIPAA, and manual client orchestration or code executors do not solve sub-agent nesting.
</details>

---

### Question 28
**Scenario**: Your retail customer support orchestrator runs on **Agent Runtime** in GCP Project `proj-support-front` (`service-account: sa-front@proj-support-front.iam.gserviceaccount.com`). It must delegate complex fraud disputes via the **Agent2Agent (A2A)** protocol to a `FraudInvestigatorAgent` hosted as a **private Cloud Run service** (`--no-allow-unauthenticated`) in **a separate GCP project**, `proj-risk-core`. Security forbids hardcoded URLs, public endpoints, and static Service Account JSON keys.

**Which cross-project architecture and IAM configuration should you implement?**
- **A)** Register `FraudInvestigatorAgent` and its Agent Card in **`AgentRegistry`**, resolve it dynamically via `registry.get_remote_a2a_agent()` (`RemoteA2aAgent` + `A2aRemoteAgentConfig` with a `RequestInterceptor` minting a keyless Google-signed **OIDC ID token** whose `audience` is the target Cloud Run URL), and grant **`roles/run.invoker`** on the `FraudInvestigatorAgent` Cloud Run service in `proj-risk-core` to `sa-front@proj-support-front.iam.gserviceaccount.com`.
- **B)** Export a JSON key for `proj-risk-core`'s default Compute Engine service account (`roles/editor`) and commit it into `proj-support-front`'s container image.
- **C)** Set `--allow-unauthenticated` (`allUsers`) on `FraudInvestigatorAgent` and pass a shared secret in the system prompt.
- **D)** Use `MCPToolset` instead of A2A and grant `roles/owner` across both projects.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Cross-project A2A between `proj-support-front` and private Cloud Run in `proj-risk-core` requires: (1) dynamic discovery via **`AgentRegistry.get_remote_a2a_agent()`** (`RemoteA2aAgent`), (2) keyless OIDC ID token injection via `A2aRemoteAgentConfig(request_interceptors=[...])`, and (3) resource-scoped **`roles/run.invoker`** granted on the specific Cloud Run service in `proj-risk-core` to the caller's principal. → Lab 12 & Lab 16.
- **Why B, C, and D are incorrect**: Static JSON keys, `allUsers` exposure, `roles/owner`, and misusing `MCPToolset` for agent-to-agent delegation are all major exam anti-patterns.
</details>

---

### Question 29
**Scenario**: An ADK healthcare support agent uses **`BigQueryToolset`** (`google.adk.tools.bigquery`) under its own runtime identity (`sa-claims-agent@proj-agent-app.iam.gserviceaccount.com`) to run **read-only analytical `SELECT` queries** against a curated claims table stored in `proj-data-lake.curated_claims.denials`. When you grant `sa-claims-agent` **only** `roles/bigquery.dataViewer` on the `curated_claims` dataset, every tool call fails with `403 Access Denied: User does not have bigquery.jobs.create`.

**What is the exact least-privilege IAM fix?**
- **A)** Keep **`roles/bigquery.dataViewer`** scoped exclusively to the `proj-data-lake.curated_claims` dataset (or table), and additionally grant **`roles/bigquery.jobUser`** on `proj-agent-app` (the billing/execution project where query jobs are created).
- **B)** Grant `roles/bigquery.admin` at the Organization root so all permission errors disappear.
- **C)** Grant `roles/bigquery.dataOwner` on all datasets in `proj-data-lake` so the agent can also `DROP` tables.
- **D)** Export a personal Data Engineer user OAuth refresh token and hardcode it in `BigQueryCredentialsConfig`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: BigQuery separates **data read authorization** (`roles/bigquery.dataViewer` on the target dataset/table in `proj-data-lake`) from **compute job creation** (`roles/bigquery.jobUser` on the project executing/billed for the SQL job, `proj-agent-app`). Granting both narrow roles solves the `403 bigquery.jobs.create` error with zero write or admin access! → Lab 10 & Lab 16.
- **Why B, C, and D are incorrect**: Over-privilege the agent with destructive table permissions or leak personal credentials.
</details>

---

### Question 30
**Scenario**: You are building a medical-policy RAG pipeline using **RAG Engine (`vertexai.preview.rag`)** over 50,000 complex clinical PDF guidelines containing **multi-column tables**, **exact ICD-10 / CPT procedure codes**, and nuanced exclusion clauses. Initial bi-encoder vector search (`gemini-embedding-2` alone) misses exact CPT codes and ranks superficially similar paragraphs above the true clinical exclusion rule.

**Which RAG Engine + Reranking configuration fixes table parsing, exact code recall, AND semantic precision?**
- **A)** Configure `RagCorpus` ingestion with Document AI **`LayoutParserConfig`** (preserving table/section boundaries in `TransformationConfig`), enable **`HybridSearch`** (combining dense `gemini-embedding-2` vectors with sparse keyword matching for exact ICD-10/CPT codes) retrieving `top_k=40` candidates, and configure **Stage-2 Cross-Encoder Reranking** via **Discovery Engine Ranking API** (`rag.Ranking(rank_service=rag.RankService(model_name="semantic-ranker-default@latest"))` / `RankServiceClient`) down to `top_n=5`.
- **B)** Embed each entire 80-page PDF as a single vector in `gemini-embedding-2` without chunking or reranking.
- **C)** Pass `top_k=500` unranked chunks into every prompt turn.
- **D)** Replace `gemini-embedding-2` with legacy `gemini-embedding-001` (2,048-token limit) and disable layout parsing.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Every piece addresses a specific failure mode: **`LayoutParserConfig`** keeps PDF tables intact across chunk boundaries, **`HybridSearch`** blends dense semantic embeddings (`gemini-embedding-2`) with lexical sparse matching for exact CPT/ICD-10 codes, and **Discovery Engine Ranking API (`RankService` / `RankServiceClient`)** applies cross-encoder joint query-document attention to rank the top 5 truly relevant clinical clauses at the top. → Lab 11 — RAG and Retrieval.
- **Why B, C, and D are incorrect**: Exceed `gemini-embedding-2`'s 8,192-token limit, trigger "lost-in-the-middle" latency/cost bloat, or downgrade embedding quality.
</details>

---

### Question 31
**Scenario**: Your custom retrieval service queries **Vector Search 1.0** (fetching 50 candidate chunks in 6 ms) and also fetches 20 candidate rows from a PostgreSQL full-text index. Before injecting the top 5 merged records into `gemini-3.7-flash`, you want a **standalone, low-latency Google Cloud cross-encoder reranking API call** in Python without spinning up an `RagCorpus` or paying the multi-second latency of a generative LLM ranker.

**Which SDK client and request objects should you invoke, and with what least-privilege IAM role?**
- **A)** Use **`google.cloud.discoveryengine_v1.RankServiceClient`** calling `client.rank(request=RankRequest(ranking_config=..., model="semantic-ranker-default@latest", top_n=5, query=..., records=[RankingRecord(id=..., title=..., content=...)]))` with **`roles/discoveryengine.viewer`**.
- **B)** Use `rag.LlmRanker` with `gemini-2.5-pro` thinking budget 32K and `roles/owner`.
- **C)** Sort the 70 strings alphabetically in Python.
- **D)** Use `ModelArmorClient.sanitize_user_prompt()` as a document relevance ranker.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`discoveryengine_v1.RankServiceClient`** (`RankRequest` + `RankingRecord`) is Google Cloud's standalone cross-encoder **Ranking / Reranking API**, scoring arbitrary candidate lists from any vector DB (Vector Search 1.0, pgvector, BigQuery) in tens of milliseconds under least-privilege `roles/discoveryengine.viewer`. → Lab 11 — RAG and Retrieval.
- **Why B, C, and D are incorrect**: `LlmRanker` with Pro incurs multi-second generative latency, alphabetical sort destroys relevance, and Model Armor is a safety scanner.
</details>

---

### Question 32
**Scenario**: Compare the three retrieval products in the official Exam Guide: **Agent Search**, **RAG Engine**, and **Vector Search 1.0**. You must match three different departmental workloads to the optimal service:
1. **HR Portal**: Out-of-the-box connectors to SharePoint, Google Drive, and Jira with automatic per-user Document-Level ACL inheritance and zero custom chunking code.
2. **Custom Legal ADK Agent**: Custom PDF chunking (`ChunkingConfig` / `LayoutParserConfig`) over Cloud Storage files with managed corpus lifecycle and integrated `RankService` reranking.
3. **E-Commerce Recommendations Engine**: 800 million custom multimodal product embeddings requiring <8 ms p99 ANN HNSW/ScaNN lookup with high-QPS numeric/categorical metadata filtering.

**Which 1 → 2 → 3 mapping is optimal?**
- **A)** (1) **Agent Search** → (2) **RAG Engine** → (3) **Vector Search 1.0**
- **B)** (1) Vector Search 1.0 → (2) Agent Search → (3) InMemoryMemoryService
- **C)** (1) RAG Engine → (2) Cloud SQL → (3) `GEMINI.md`
- **D)** Use long-context prompt stuffing (1M tokens) for all 800 million products on every turn.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **Agent Search** wins whenever turn-key SaaS connectors + Document-Level ACLs are required; **RAG Engine** (`RagCorpus`) wins for developer-controlled chunking/parsing + reranking pipelines in ADK; **Vector Search 1.0** wins for raw hundred-million/billion-scale low-latency ANN indexes with custom embeddings. → Lab 11 — RAG and Retrieval.
- **Why B, C, and D are incorrect**: Mismatch managed connectors, memory types, and impossible context sizes.
</details>

---

### Question 33
**Scenario**: You are deploying a customer-support ADK agent onto **Agent Runtime** (`adk deploy agent_engine`). You need two distinct state layers:
1. **Within the active chat session**: Track the current support ticket ID, verified authentication flag (`session.state["verified"]`), and temporary scratchpad calculation (`temp:draft_calc` discarded after the current invocation).
2. **Across separate chat sessions weeks apart**: Remember that a returning VIP customer prefers concise bulleted updates and metric units, automatically injected on **every** turn without costing an extra LLM tool-call round-trip.

**Which session service, memory service, and recall tool should you configure?**
- **A)** **`VertexAiSessionService`** (using plain session keys + `temp:` prefix) paired with **`VertexAiMemoryBankService`** and the **`preload_memory`** tool (authorized via `roles/aiplatform.user`).
- **B)** `InMemorySessionService` paired with `load_memory` and `UnsafeLocalCodeExecutor`.
- **C)** Store temporary per-turn scratchpad data inside `app:` global state so all customers overwrite each other's ticket IDs.
- **D)** `RedisSessionService` with `ttl_seconds=60` as the sole long-term multi-week memory bank.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: On **Agent Runtime**, **`VertexAiSessionService`** provides managed session state (`temp:` auto-clears after the invocation), while **`VertexAiMemoryBankService`** extracts durable cross-session user preferences. Using **`preload_memory`** (instead of reactive `load_memory`) eagerly injects relevant user memories before every LLM turn with zero extra tool-call latency! → Lab 09 — Sessions and Memory.
- **Why B, C, and D are incorrect**: `InMemorySessionService` loses state across replicas/restarts, `app:` leaks state across users, and 60-second Redis TTL deletes multi-week memories.
</details>

---

### Question 34
**Scenario**: Conversely, suppose you build a **high-volume technical documentation Q&A agent** (50,000 turns/hour) deployed on **Cloud Run** where **95% of turns are anonymous, stateless one-off technical questions**, and only **5% of turns** explicitly ask *"Based on my past architecture discussions last month, what did we decide?"*

**To minimize Cloud Run session latency AND avoid wasting Memory Bank retrieval/token cost on the 95% of turns that don't need past history, which pairing is best?**
- **A)** Use **`RedisSessionService`** (Memorystore for Redis with `ttl_seconds`) for sub-millisecond horizontal Cloud Run session state, and attach **`VertexAiMemoryBankService`** with the reactive **`load_memory`** tool so the LLM invokes memory lookup *only* on the 5% of turns where past context is requested.
- **B)** Use `preload_memory` on 100% of anonymous turns and `InMemorySessionService` across 50 Cloud Run instances.
- **C)** Dump raw Redis memory into `GCPSkillRegistry`.
- **D)** Force every anonymous user through a 60-second cold-start GKE StatefulSet pod.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Stateless Cloud Run containers require external shared session storage (**`RedisSessionService`** delivers sub-ms latency and automatic `ttl_seconds` cleanup), while reactive **`load_memory`** ensures Memory Bank queries and extra prompt tokens are only paid on the 5% of turns that actually reference prior sessions. → Lab 09 — Sessions and Memory.
- **Why B, C, and D are incorrect**: `InMemorySessionService` breaks when Cloud Run load-balances turns across multiple instances, and `preload_memory` wastes calls on 95% anonymous queries.
</details>

---

### Question 35
**Scenario**: You are selecting models (`common/models.py`) for a 3-tier enterprise customer support system:
- **Tier 1 (High-Throughput Router — 5,000 req/min)**: Classify incoming user intent into 12 categories in <300 ms at minimal cost.
- **Tier 2 (Core Support Agent)**: Multi-step tool orchestration across CRM, Order MCP, and Policy RAG with strong accuracy/latency balance.
- **Tier 3 (Offline Escalation Auditor / LLM Judge)**: Deep multi-document dispute synthesis and rubric grading of Tier 2 transcripts.

**Which pinned model assignment is optimal?**
- **A)** Tier 1: **`gemini-3.5-flash-lite`** · Tier 2: **`gemini-3.7-flash`** (or `gemini-3.8-flash`) · Tier 3: **`gemini-2.5-pro`**
- **B)** Tier 1: `gemini-2.5-pro` · Tier 2: `gemini-embedding-2` · Tier 3: `gemini-3.5-flash-lite`
- **C)** Use floating alias `gemini-flash-latest` everywhere without version pinning so silent model shifts happen unannounced in production.
- **D)** Use `veo-3.1-generate-preview` for text intent routing.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Matches capability to cost/latency shape: **`gemini-3.5-flash-lite`** handles cheap ultra-fast classification, **`gemini-3.7-flash`** is the pinned enterprise agentic workhorse, and **`gemini-2.5-pro`** provides maximum reasoning depth for complex audits and out-ranked LLM-as-a-judge evaluation. → Lab 07 & Lab 13.
- **Why B, C, and D are incorrect**: Misassign embedding/video models, invert judge superiority, or rely on unpinned floating aliases.
</details>

---

### Question 36
**Scenario**: A defense-contracting division must run an internal engineering support agent inside an **air-gapped VPC** with **zero outbound calls to multi-tenant SaaS LLM APIs**. Each GKE node has only a single 24 GB NVIDIA L4 GPU, and you need a verified open-weight model with a **262,144-token context window** and maximum tokens-per-second throughput.

**Which verified model ID should you deploy via Model Garden / vLLM on GKE?**
- **A)** `gemma-4-26b-a4b-it`
- **B)** `gemma-4-31b-it`
- **C)** `gemini-2.5-pro`
- **D)** `gemini-3.7-flash`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`gemma-4-26b-a4b-it`** is the Gemma 4 Mixture-of-Experts (MoE) open-weight model (26B total parameters, **~4B active parameters per token**, 262K input / 32K output). Activating only ~4B parameters per forward pass yields dramatically higher throughput and lower memory-bandwidth pressure on a single L4 GPU than the dense 31B variant while staying 100% self-hosted inside the VPC. → Lab 07 & Lab 19.
- **Why B is incorrect**: `gemma-4-31b-it` activates all 31B parameters on every token, making it heavier and slower on a constrained single-L4 budget.
- **Why C and D are incorrect**: Proprietary cloud SaaS models cannot be self-hosted inside an air-gapped VPC.
</details>

---

### Question 37
**Scenario**: Across 12 engineering squads building ADK agents, teams want to publish and dynamically discover reusable domain procedures (e.g., `hipaa-claim-appeal-SOP`, `bigquery-cost-audit`) consisting of lightweight discovery metadata (`name`, `description`, `allowed_tools`), detailed Markdown instructions, and helper scripts stored in Google Cloud—without hardcoding all 200 SOPs into every agent's system prompt.

**Which ADK / Google Cloud service and loading pattern solves this?**
- **A)** Package each SOP as an ADK **`Skill`** (`Frontmatter` + `instructions` + `Resources`) published to **`GCPSkillRegistry`** (`google.adk.integrations.skill_registry`), using **L1 (`Frontmatter`) → L2 (`instructions`) → L3 (`Resources`) progressive disclosure** via `search_skills()` and `get_skill()`.
- **B)** Register Markdown SOPs as A2A `RemoteA2aAgent` endpoints in Cloud DNS.
- **C)** Paste all 200 SOPs into `global_instruction` on every agent.
- **D)** Store SOP instructions inside `PrincipalAccessBoundary` IAM rules.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`SkillRegistry` / `GCPSkillRegistry`** (Tool #28 in the Exam Guide) governs reusable **`Skill`** bundles (`Frontmatter` fields: `name`, `description`, `license`, `compatibility`, `allowed_tools`, `metadata`), keeping token budgets lean through L1/L2/L3 progressive disclosure. → Lab 10 — Tools and Skills.
- **Why B, C, and D are incorrect**: Confuse A2A live agents, token-bloated prompts, and IAM policies with skill discovery.
</details>

---

### Question 38
**Scenario**: An ADK customer-support agent calls a third-party shipping REST API via a `FunctionTool`. Occasionally, the LLM formats the `country_code` as `"United States"` instead of ISO-2 `"US"`, causing the tool to raise a `ValueError("Expected 2-letter ISO code")`, or the API returns a transient `503`. You want the agent to automatically inspect the error and retry with fixed arguments up to a bounded limit.

**Which built-in ADK plugin provides this self-healing tool retry behavior?**
- **A)** `ReflectAndRetryToolPlugin` (from `google.adk.plugins`)
- **B)** `ModelArmorPlugin`
- **C)** `DebugLoggingPlugin`
- **D)** `GcsArtifactService`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`ReflectAndRetryToolPlugin`** (`google.adk.plugins`) intercepts tool exceptions, feeds structured error diagnostics back to the model for reflection (so it corrects `"United States"` → `"US"` or retries transient failures), and bounds retry attempts cleanly. → Lab 08 & Lab 10.
- **Why B, C, and D are incorrect**: Screen content safety, log debug events, or store binary artifacts rather than reflecting/retrying failed tool calls.
</details>

---

### Question 39
**Scenario**: In ADK, an iterative `PolicyDraftingAgent` writes a customer refund email (`output_key="draft_email"`) and a `ComplianceCriticAgent` checks whether mandatory legal disclosures are present. You want them to iterate until `ComplianceCriticAgent` approves the draft, **capped strictly at 3 iterations** so a stubborn edge case never causes a runaway billing loop.

**Which orchestration class and termination tool should you combine?**
- **A)** `LoopAgent(name="DraftReviewLoop", max_iterations=3, sub_agents=[PolicyDraftingAgent, ComplianceCriticAgent])` with the built-in **`exit_loop`** tool (`from google.adk.tools import exit_loop`) attached to `ComplianceCriticAgent`.
- **B)** `ParallelAgent` with `disallow_transfer_to_parent=True`.
- **C)** A `while True:` loop inside the prompt without `max_iterations`.
- **D)** `FallbackModel` wrapping `ComplianceCriticAgent`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`LoopAgent`** enforces a deterministic ceiling via `max_iterations=3`, while invoking **`exit_loop`** allows `ComplianceCriticAgent` to terminate the loop immediately on iteration 1 or 2 once disclosures pass. → Lab 08 & Lab 12.
- **Why B, C, and D are incorrect**: `ParallelAgent` runs concurrently once, prompt loops have no hard cap, and `FallbackModel` handles model outages.
</details>

---

### Question 40
**Scenario**: An ADK enterprise billing agent needs to connect to both **Cloud SQL for PostgreSQL** and **BigQuery** through a centrally governed **MCP Toolbox for Databases** server hosted on Cloud Run, authenticating to Cloud SQL **without** database passwords and reading a Slack webhook secret **without** broad project-level secret access.

**Which least-privilege IAM configuration should you apply?**
- **A)** Configure Cloud SQL **IAM Database Authentication** granting the MCP server's Service Account **`roles/cloudsql.client` + `roles/cloudsql.instanceUser`**, grant **`roles/secretmanager.secretAccessor` bound strictly on the single Slack webhook secret resource**, and grant the ADK agent **`roles/run.invoker`** on the MCP Cloud Run service.
- **B)** Grant `roles/cloudsql.admin` and project-wide `roles/secretmanager.admin` to all containers, and store the PostgreSQL `postgres` root password in `GEMINI.md`.
- **C)** Make the Cloud SQL instance public (`0.0.0.0/0`) with trust authentication.
- **D)** Export CSV dumps to a public GCS bucket every night.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Enforces defense-in-depth least privilege at every hop: `roles/run.invoker` gates MCP transport access, `roles/cloudsql.client` + `roles/cloudsql.instanceUser` enables keyless IAM DB authentication, and resource-level `roles/secretmanager.secretAccessor` prevents reading any other secret in the project. → Lab 10 & Lab 16.
- **Why B, C, and D are incorrect**: Expose admin roles, plaintext root credentials, or public network/storage surfaces.
</details>

---

### Question 41
**Scenario**: An ADK customer-support agent handles high-value warranty replacements. Whenever replacement value exceeds **$500**, the agent must **pause mid-execution**, present structured `[Approve Replacement / Reject / Request Receipt]` options to a human supervisor, and resume the exact paused session once the supervisor responds hours later.

**Which built-in ADK primitives support durable Human-in-the-Loop (HITL) pauses and resumptions?**
- **A)** Built-in HITL tools **`get_user_choice` / `request_input`** or **`LongRunningFunctionTool`** (from `google.adk.tools`) paired with **`ResumabilityConfig`** (`google.adk.apps.App`) and a persistent `SessionService` (`VertexAiSessionService` or `DatabaseSessionService`).
- **B)** `time.sleep(28800)` inside a synchronous `FunctionTool` blocking a Cloud Run worker thread for 8 hours.
- **C)** Asking the LLM in its system prompt to *"pretend a manager approved it if the customer sounds polite"*.
- **D)** Using `InMemorySessionService` on scale-to-zero Cloud Run instances.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: ADK provides native HITL primitives (`get_user_choice`, `request_input`, and `LongRunningFunctionTool`) that yield control cleanly without holding compute threads open, while `ResumabilityConfig` + persistent `VertexAiSessionService` / `DatabaseSessionService` allows resuming hours later even after container scale-down. → Lab 10 & Lab 17.
- **Why B, C, and D are incorrect**: `sleep()` exceeds Cloud Run request timeouts and wastes compute, prompt-based approval is easily bypassed, and `InMemorySessionService` loses paused state on scale-to-zero.
</details>

---

### Question 42
**Scenario**: In a multi-agent hierarchy (`RootTriageAgent` → `BillingAgent`, `TechSupportAgent`, `ReturnsAgent`), production traces show `BillingAgent` unexpectedly transferring customers sideways to `ReturnsAgent`, which transfers back to `BillingAgent` in a 9-turn lateral ping-pong loop. You want only `RootTriageAgent` to orchestrate handoffs; leaf specialists must complete their task and never transfer laterally to peers.

**Which exact `LlmAgent` configuration fields stop lateral ping-pong transfers deterministically?**
- **A)** Set **`disallow_transfer_to_peers=True`** (and optionally `disallow_transfer_to_parent=True` when terminal) on the specialist `LlmAgent` definitions.
- **B)** Set `parallel_worker=True` on `VertexAiMemoryBankService`.
- **C)** Add `"Please do not transfer to ReturnsAgent"` in `BillingAgent`'s system prompt while leaving peer transfer tools enabled.
- **D)** Switch from `LlmAgent` to `UnsafeLocalCodeExecutor`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `LlmAgent` exposes **`disallow_transfer_to_peers`** and **`disallow_transfer_to_parent`** (`docs/VERIFIED_FACTS.md`), which deterministically prune invalid target agents from `TransferToAgentTool`'s schema so the LLM physically cannot emit lateral peer transfers. → Lab 08 & Lab 12.
- **Why B, C, and D are incorrect**: Prompt nudges remain probabilistic when peer targets are still exposed in the tool schema, and the other fields do not exist on those classes.
</details>

---

### Question 43
**Scenario**: Your ADK customer-support agent relies on `gemini-3.7-flash` in `us-central1`. Business continuity rules require that if Vertex AI returns `429 RESOURCE_EXHAUSTED` or a transient regional `503`, the agent automatically fails over to a secondary model endpoint without crashing the user's conversation.

**Which ADK model wrapper class implements this failover?**
- **A)** `FallbackModel` (from `google.adk.models`)
- **B)** `ReflectAndRetryToolPlugin`
- **C)** `LlmCapabilities`
- **D)** `ManagedAgent`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`FallbackModel`** (`google.adk.models`) wraps a primary `BaseLlm` and an ordered list of backup models (e.g., cross-region Gemini or self-hosted `Gemma`), failing over automatically on model API errors. → Lab 07 — Model Selection.
- **Why B, C, and D are incorrect**: `ReflectAndRetryToolPlugin` retries tool exceptions on the *same* model; `LlmCapabilities` is a capability descriptor; `ManagedAgent` wraps server-side managed interactions.
</details>

---

### Question 44
**Scenario**: Two departmental agents communicate via the **Agent2Agent (A2A)** protocol. Before creating a task, the calling orchestrator must inspect what skills, input/output MIME types, and authentication schemes (`OAuth2`, `OIDC`) the remote agent supports, and then inject a signed authorization header into every outgoing A2A request.

**Which A2A artifact and ADK configuration classes handle capability discovery and header injection?**
- **A)** The remote agent publishes an **Agent Card** (`/.well-known/agent.json`), and the caller configures **`RemoteA2aAgent` / `A2aRemoteAgentConfig`** with **`request_interceptors` (`RequestInterceptor`)** and **`card_request_interceptors` (`CardRequestInterceptor`)**.
- **B)** The remote agent publishes a `hooks.json` file over FTP and the caller uses `BigQueryToolset`.
- **C)** Both agents share a local SQLite span exporter file (`sqlite_span_exporter`).
- **D)** The caller uses `VertexAiRagMemoryService` to guess the remote URL from embeddings.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In A2A (`google.adk.a2a.agent` + `RemoteA2aAgent`), peer capabilities and auth requirements are advertised via an **Agent Card**, while `A2aRemoteAgentConfig` provides `request_interceptors` and `card_request_interceptors` to attach OAuth/OIDC tokens and trace headers cleanly. → Lab 12 — Multi-Agent and A2A.
- **Why B, C, and D are incorrect**: Confuse coding hooks, local telemetry exporters, and RAG memory with A2A protocol negotiation.
</details>

---

### Question 45
**Scenario**: You are building a top-level insurance claims settlement pipeline in ADK 2.9.0 (`ParseClaim -> CheckCoverage -> ComputePayout -> JoinAudit`). Every transition must follow explicit Python edge conditions with **0 ms LLM routing overhead**, bounded node retries (`RetryConfig`), and per-node SLAs (`NodeTimeoutError`). It does **not** need to be nested as a `sub_agent` inside an `LlmAgent`.

**Which ADK 2.9.0 orchestration engine is purpose-built for this top-level deterministic DAG?**
- **A)** `google.adk.workflow.Workflow` (`Node`, `FunctionNode`, `JoinNode`, `Edge`, `START`)
- **B)** A single `LlmAgent` with 15 tools and temperature `1.0` hoping it calls them in DAG order
- **C)** `InMemoryArtifactService`
- **D)** `Gemma3Ollama` without any workflow edges

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 3.3 explicitly tests **"graph workflow"**, implemented in ADK 2.9.0 by **`google.adk.workflow.Workflow`** (`Node`, `FunctionNode`, `JoinNode`, `Edge`, `RetryConfig`, `NodeTimeoutError`), delivering zero-millisecond deterministic edge routing for top-level pipelines. → Lab 08 & Lab 12.
- **Why B, C, and D are incorrect**: Probabilistic tool routing cannot guarantee strict financial settlement DAG execution.
</details>

---

### Question 46
**Scenario**: Whenever a hospital partner uploads an HL7/PDF referral package into a Cloud Storage bucket, a headless ADK agent should wake up asynchronously—without any interactive chat UI—extract structured referral fields, and post an event downstream.

**Which ADK integration module and security binding should trigger this workflow?**
- **A)** `google.adk.integrations.eventarc` (`EventarcToolset` + `CloudEventAttributesBinding`), granting **`roles/run.invoker`** on the agent's Cloud Run service exclusively to the dedicated Eventarc trigger Service Account.
- **B)** Polling `gsutil ls` every 0.5 seconds inside `UnsafeLocalCodeExecutor`.
- **C)** Exposing `adk web` publicly to `0.0.0.0/0` without authentication.
- **D)** Using `VertexAiLoadProfilesTool` as a cron scheduler.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `EventarcToolset` (`CloudEventAttributesBinding`) binds standard GCS CloudEvents directly into headless ADK runs, while scoping `roles/run.invoker` to the dedicated Eventarc trigger SA prevents unauthorized direct invocations. → Lab 12 & Lab 16.
- **Why B, C, and D are incorrect**: Polling loops, public unauthenticated dev UIs, and profile loaders are anti-patterns for event-driven pipelines.
</details>

---

### Question 47
**Scenario**: Compare `google_search` and `enterprise_web_search` in `google.adk.tools`. A regulated pharmaceutical support agent needs to ground answers on public FDA drug-recall announcements with verifiable web citations, **without** building custom web scrapers.

**Which built-in ADK tool should you attach?**
- **A)** `google_search` (for public web grounding with citations; whereas `enterprise_web_search` targets internal/enterprise web indexes)
- **B)** `google_maps_grounding`
- **C)** Custom `BeautifulSoup` scraping inside `UnsafeLocalCodeExecutor`
- **D)** `exit_loop`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `google_search` connects ADK agents to managed Google Search grounding with structured citation metadata for public web facts, whereas `enterprise_web_search` grounds over indexed enterprise web domains. → Lab 10 — Tools and Skills.
- **Why B, C, and D are incorrect**: Target geospatial places, fragile ungrounded scraping, or loop termination.
</details>

---

### Question 48
**Scenario**: Your enterprise already maintains 15 battle-tested Python tools written for **LangChain** (e.g., custom ERP normalizers), and your team is migrating the orchestration layer to **ADK 2.9.0** on tight deadlines without rewriting validated tool logic.

**How should you adopt those tools in ADK?**
- **A)** Wrap them via **`google.adk.integrations.langchain`** so they conform natively to ADK's `BaseTool` interface.
- **B)** Deploy 15 separate GKE clusters and call each Python function over A2A.
- **C)** Paste the LangChain Python source files into the agent's `static_instruction` string.
- **D)** Rewrite all 15 tools in bash inside `hooks.json`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `google.adk.integrations.langchain` (alongside `integrations.crewai`) adapts existing third-party ecosystem tools directly into ADK's `BaseTool` contract with zero rewrite. → Lab 10 — Tools and Skills.
- **Why B, C, and D are incorrect**: Over-engineer network hops or fail to execute Python logic safely.
</details>

---

### Question 49
**Scenario**: A banking customer-support ADK agent deployed on **GKE** requires **ACID transactional durability** and SQL audit queryability for its multi-turn `Session` records (so compliance auditors can join session events with relational customer tables in **Cloud SQL**), rather than in-memory cache volatility.

**Which ADK session service should you configure?**
- **A)** `DatabaseSessionService` (`google.adk.sessions.DatabaseSessionService`) backed by **Cloud SQL** using IAM Database Authentication (`roles/cloudsql.client` + `roles/cloudsql.instanceUser`).
- **B)** `InMemorySessionService` inside ephemeral GKE pods.
- **C)** `GcsArtifactService` storing raw pickle files in a public bucket.
- **D)** `RedisSessionService` with `ttl_seconds=5` and persistence disabled.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`DatabaseSessionService`** persists ADK `Session` and `Event` state in relational databases like **Cloud SQL** (Tool #15 in the Exam Guide) with full ACID transactions and IAM DB Auth. → Lab 09 & Lab 14.
- **Why B, C, and D are incorrect**: Lose session records on pod restarts/TTL expiry or lack relational ACID semantics.
</details>

---

### Question 50
**Scenario**: Your enterprise uses **Gemini Enterprise App (`GEApp`)** as the unified employee portal (searching SharePoint and Google Drive with Document-Level ACLs), while a specialized custom Python ADK supply-chain agent runs on **GKE** (`Agent Platform / GEAP`) to solve linear-programming inventory models in gVisor sandboxes. Leadership asks you to *"surface the custom supply-chain agent inside Gemini Enterprise so supply-chain planners can invoke it from their central assistant."*

**How should you integrate `GEApp` and your custom GKE ADK agent?**
- **A)** Expose the GKE ADK agent via **A2A** with an attested **Agent Card**, register it in **`AgentRegistry`**, and connect it into **Gemini Enterprise App (`GEApp`)** with **OAuth 2.0 user identity propagation** via Agent Gateway / Auth Manager.
- **B)** Rewrite the Python linear-programming solver as a zero-shot prompt inside Agent Designer.
- **C)** Disable Document-Level ACLs in `GEApp` and share a single admin login across all planners.
- **D)** Move SharePoint indexing out of Agent Search into `UnsafeLocalCodeExecutor`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Demonstrates how the **Gemini Enterprise** ecosystem fits together: **`GEApp`** serves as the turn-key ACL-aware employee front door, delegating specialized tasks over **A2A** (governed by **`AgentRegistry`**) to custom code-first agents running on **GKE / Cloud Run / Agent Runtime (`GEAP`)** with end-to-end OAuth identity propagation. → Lab 03 & Lab 12.
- **Why B, C, and D are incorrect**: LLMs cannot replace exact numerical optimization solvers via prompts alone, and disabling ACLs or sandboxes violates security.
</details>

---

## Domain 4: Evaluating and Deploying Agentic Workflows (~22% · Questions 51–68)

### Question 51
**Scenario**: You are designing the evaluation suite (`google.adk.evaluation`) for a healthcare **customer support agent**. You have two very different evaluation goals:
1. **Goal 1 (Deterministic Action Audit)**: Verify that on every prescription-refill request, the agent **always** calls `verify_patient_dob` *before* `submit_refill_request` with exact expected parameters against a golden `.evalset.json`.
2. **Goal 2 (Open-Ended Tone & Policy Quality)**: Grade whether the agent's free-form explanation of insurance prior-authorization delays is empathetic, avoids medical diagnosis, and cites clinic hours—where hundreds of differently worded answers are equally valid and **no single golden reference string exists**.

**How should you combine ADK Evaluation Metrics vs. Rubrics?**
- **A)** Use a deterministic **Metric** (`ToolTrajectoryCriterion` / `trajectory_evaluator` with `in_order_match` or `exact_match`) for Goal 1, and use a reference-free autorater **Rubric** (`Rubric` + `RubricsBasedCriterion` / `rubric_based_final_response_quality_v1` judged by `gemini-2.5-pro`) for Goal 2.
- **B)** Use `Rouge` lexical n-gram overlap for both Goal 1 and Goal 2.
- **C)** Use `RubricsBasedCriterion` alone without checking tool trajectories, assuming polite prose implies `verify_patient_dob` was called.
- **D)** Check only `HTTP 200 OK` status codes in pytest.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Separates **Metrics vs. Rubrics** cleanly: **Metrics** (`ToolTrajectoryCriterion` / `trajectory_evaluator`, `final_response_match_v2`, `Rouge`) compare against deterministic golden trajectories/strings, whereas **Rubrics** (`Rubric` + `RubricsBasedCriterion`, `rubric_based_final_response_quality_v1`) use an out-ranked LLM judge (`gemini-2.5-pro`) to grade open-ended multi-criteria behavioral quality without brittle reference strings! → Lab 13 — Agent Evaluation.
- **Why B, C, and D are incorrect**: `Rouge` fails on valid paraphrases and ignores tool calls; skipping trajectory metrics misses skipped security/consent tools.
</details>

---

### Question 52
**Scenario**: Compare **ADK local evaluation tooling (`adk eval` with `.evalset.json`)** against the managed **Agent Platform Gen AI Evaluation Service (`vertexai.evaluation.EvalTask`)**. Your org needs:
1. Fast pull-request regression checks on 30 golden edge-case trajectories inside developer Cloud Workstations and CI.
2. Weekly side-by-side **Pairwise A/B comparison** (`PairwiseMetric`) of `gemini-3.7-flash` vs. a candidate prompt/model upgrade across 10,000 sampled production customer-support turns stored in Cloud Storage / BigQuery, with managed experiment tracking and **Adaptive Rubrics**.

**Which tooling split is architecturally sound?**
- **A)** Use **`adk eval` (`AgentEvaluator` + `.evalset.json`)** for fast developer/PR regression gating, and use **Agent Platform Gen AI Evaluation Service** (`vertexai.evaluation.EvalTask` with `PairwiseMetric`, `PointwiseMetric`, and `vertex_ai_eval_facade`, using `roles/aiplatform.user` + `roles/bigquery.dataViewer`) for large-scale cloud A/B and continuous production evaluation.
- **B)** Have human QA engineers read all 10,000 transcripts manually in Notepad every Friday.
- **C)** Run 10,000 pairwise LLM judge calls synchronously inside a blocking git pre-commit hook on developer laptops.
- **D)** Replace both tools with `adk migrate session`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 4.1 explicitly tests *"Determining the appropriate evaluation framework and tooling (ADK evaluation tooling (evalset), Agent Platform Gen AI evaluation service, custom autoraters)"*. Local `adk eval` excels at fast PR gating on `.evalset.json`, while **Agent Platform Gen AI Evaluation Service** (`EvalTask`, `PairwiseMetric`, `PointwiseMetric`, Adaptive Rubrics) scales to thousands of cloud evaluations and A/B comparisons. → Lab 13 — Agent Evaluation.
- **Why B, C, and D are incorrect**: Manual review doesn't scale, 10K synchronous pre-commit calls stall engineering, and `adk migrate session` is unrelated.
</details>

---

### Question 53
**Scenario**: A healthcare scheduling agent scores 96% on `final_response_match_v2` against a 200-case golden dataset. However, clinical QA uncovers two severe production bugs:
1. On 12% of turns, the agent skips calling `check_insurance_eligibility` yet still outputs a fluent appointment confirmation.
2. On 6% of turns, the agent invents a `$15 copay` figure that never appeared in the EHR tool output.

**Which two evaluators from `google.adk.evaluation` must you add to catch both bugs deterministically? (Select TWO)**
- **A)** `trajectory_evaluator` (`ToolTrajectoryCriterion`) to enforce mandatory tool invocation order and precision
- **B)** `hallucinations_v1` (`HallucinationsCriterion`) to verify every factual claim in the response is grounded in retrieved tool/RAG outputs
- **C)** `final_response_match_v1`
- **D)** `SimplePromptOptimizer`
- **E)** `RedisSessionService`

<details><summary>Show answer</summary>

**Correct Answers: A and B**
**Explanation**:
- **Why A and B are correct**: `final_response_match_v2` only compares surface text. **`trajectory_evaluator`** catches skipped mandatory tools (`check_insurance_eligibility`), and **`hallucinations_v1`** catches ungrounded fabricated numbers (`$15 copay`) not backed by tool/RAG context. → Lab 13 — Agent Evaluation.
- **Why C, D, and E are incorrect**: Do not inspect tool call trajectories or groundedness against tool context.
</details>

---

### Question 54
**Scenario**: You want every Git pull request in Cloud Build to verify that Python refactors to your ADK workflow state schemas and tool wiring have not broken known-good execution paths—**without** paying token costs or suffering non-deterministic LLM variance on 400 test cases per commit.

**Which verified `adk` CLI command pair records staging interactions and replays them deterministically in CI?**
- **A)** `adk conformance record` and `adk conformance test`
- **B)** `adk optimize` and `adk web`
- **C)** `adk deploy gke` and `adk telemetry disable`
- **D)** `adk create` and `adk migrate session`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`adk conformance record`** captures deterministic interaction traces and **`adk conformance test`** replays them offline in CI/CD to catch state-schema and wiring regressions with zero live LLM cost or randomness. → Lab 15 — Observability and Troubleshooting.
- **Why B, C, and D are incorrect**: Handle prompt optimization, UI serving, deployment, or schema migration rather than deterministic replay testing.
</details>

---

### Question 55
**Scenario**: Your data-governance team writes a custom deterministic evaluator in Python (`SqlLimitClauseEvaluator`) that parses every generated BigQuery SQL tool argument and fails if `LIMIT` is missing or exceeds `10000`. You want `adk eval` to invoke this custom evaluator alongside built-in metrics.

**Which ADK evaluation registry must you register your custom evaluator with?**
- **A)** `metric_evaluator_registry` (in `google.adk.evaluation`)
- **B)** `AgentRegistry`
- **C)** `GCPSkillRegistry`
- **D)** `LLMRegistry`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Custom evaluators in `google.adk.evaluation` register into **`metric_evaluator_registry`** (`custom_metric_evaluator`) so `AgentEvaluator` and `adk eval` can resolve and execute them by metric name. → Lab 13 — Agent Evaluation.
- **Why B, C, and D are incorrect**: Register live A2A/MCP endpoints, skills, or LLM model adapters.
</details>

---

### Question 56
**Scenario**: You run `RubricsBasedCriterion` using **`gemini-3.5-flash-lite`** as the autorater judge to grade complex multi-document legal-compliance answers generated by **`gemini-2.5-pro`**. Engineers notice the autorater frequently marks nuanced, accurate legal citations as wrong while giving high scores to superficial, confident-sounding hallucinations.

**What is the root cause and architectural fix?**
- **A)** The judge model is weaker than the generator ("judge under-ranking"). Configure `judge_model_options` so the autorater uses a **stronger or equal high-reasoning model** (such as **`gemini-2.5-pro`**) with explicit rubric criteria and `hallucinations_v1`, calibrated against human-labeled golden examples.
- **B)** Downgrade the legal agent to `gemini-embedding-001` so both models fail equally.
- **C)** Remove all evaluation rubrics and deploy directly to production.
- **D)** Increase judge `temperature` to `2.0` so scores average out randomly.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In LLM-as-a-Judge architectures, the judge must possess reasoning capacity **greater than or equal to** the agent being evaluated (`gemini-2.5-pro` judging `gemini-3.7-flash` or `gemini-2.5-pro` with rubric calibration); a lightweight classifier (`flash-lite`) lacks the reasoning depth to verify complex multi-document synthesis. → Lab 13 — Agent Evaluation.
- **Why B, C, and D are incorrect**: Degrade accuracy, eliminate quality gates, or inject scoring noise.
</details>

---

### Question 57
**Scenario**: Your team initially deployed a Python ADK multi-agent assistant onto **Agent Runtime** (`adk deploy agent_engine`) for zero-ops convenience. Six months later, architecture requirements change:
1. One specialist agent must serve open-weight **`gemma-4-26b-a4b-it`** with custom LoRA adapters on dedicated NVIDIA L4 GPUs inside your VPC.
2. Multi-turn requests to those GPU pods must use **KV-cache / prefix-cache affinity routing**.
3. Untrusted user-submitted data-cleaning scripts must run inside **gVisor (`runsc`)** kernel-isolated pods (`GkeCodeExecutor(executor_type="sandbox")`).

**Why must you migrate or deploy these components onto GKE (`adk deploy gke`) instead of Agent Runtime?**
- **A)** **Agent Runtime** is a serverless managed Python runtime that does not expose custom GPU node pools for self-hosted `vLLM` models, cannot deploy **GKE Inference Gateway** (`InferencePool`), and cannot schedule custom **GKE Agent Sandbox (`gVisor`)** pod templates.
- **B)** Agent Runtime cannot run Python `google-adk` code or connect to `VertexAiMemoryBankService`.
- **C)** Agent Runtime only supports Windows Server containers.
- **D)** Agent Runtime blocks outbound calls to Vertex AI Gemini models.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Knowing **Agent Runtime's sweet spot** (zero-ops Python ADK + native `VertexAiSessionService` & `VertexAiMemoryBankService`) vs. its **hard architectural boundaries** (no custom GPU node pools, no GKE Inference Gateway `InferencePool`, no node-level gVisor `GkeCodeExecutor`) is a core Section 4.2 exam distinction. → Lab 14 & Lab 19.
- **Why B, C, and D are incorrect**: Agent Runtime natively runs Python ADK, integrates with Memory Bank, and calls Gemini on Vertex AI.
</details>

---

### Question 58
**Scenario**: A stateless webhook-style ADK order-notification agent receives 0 requests overnight and bursts to 8,000 requests/minute during flash sales. Each invocation calls a legacy ERP API that takes **55 seconds** to respond, plus ~4 seconds of `gemini-3.7-flash` generation. Your team wants scale-to-zero cost efficiency and minimal ops overhead, but initial **Cloud Run** deployments occasionally fail with `504 Gateway Timeout` or drop session state across turns.

**Which Cloud Run architecture fixes both issues cleanly?**
- **A)** Deploy via `adk deploy cloud_run`, explicitly configure **both** the ADK tool/agent timeout AND the **Cloud Run request `timeout`** above 60 seconds (e.g., 120s) to accommodate the 55s ERP call + retries, and back multi-turn state with **`RedisSessionService`** (or `DatabaseSessionService`).
- **B)** Put Cloud CDN in front of the dynamic POST endpoint and keep `InMemorySessionService`.
- **C)** Provision 100 static Compute Engine VMs running 24/7 idle overnight.
- **D)** Set Cloud Run `timeout=5s` to force the 55-second ERP database to run faster.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **Cloud Run** (`adk deploy cloud_run`) is optimal for bursty scale-to-zero stateless HTTP workloads, provided infrastructure request timeouts exceed total LLM + slow-tool duration and any multi-turn state lives in external `RedisSessionService` / `DatabaseSessionService`. → Lab 14 — Deployment Runtimes.
- **Why B, C, and D are incorrect**: CDN doesn't accelerate uncached ERP mutations, static VMs waste idle spend, and a 5s timeout kills every 55s call.
</details>

---

### Question 59
**Scenario**: Your security architect audits the CI/CD pipeline deploying ADK agents to **Agent Runtime** (`adk deploy agent_engine`). Currently, a single Service Account (`sa-everything@proj-prod.iam.gserviceaccount.com`) with `roles/owner` both runs Cloud Build deployments AND serves live customer traffic at runtime.

**How should you refactor IAM roles to enforce strict least-privilege separation of duties?**
- **A)** Create **two separate Service Accounts**:
  1. **CI/CD Deployer SA**: Granted deployment permissions (`roles/aiplatform.admin` or custom Reasoning Engine deploy role, `roles/storage.objectAdmin` on the staging bucket, and `roles/iam.serviceAccountUser` **scoped only to the Runtime SA**).
  2. **Agent Runtime Execution SA**: Granted **only runtime permissions** (`roles/aiplatform.user`, `roles/modelarmor.user`, `roles/cloudtrace.agent`, `roles/logging.logWriter`, plus scoped tool roles) and capped by a **Principal Access Boundary (PAB)**.
- **B)** Keep a single SA with `roles/editor` and export a JSON key into GitHub Actions secrets without Workload Identity Federation.
- **C)** Grant the Runtime Execution SA `roles/iam.securityAdmin` so the agent can grant itself new roles when a tool fails with `403`.
- **D)** Remove all IAM roles from both accounts and disable authentication.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Separating **CI/CD control-plane deploy identity** (needs `iam.serviceAccountUser` on the runtime SA + staging/deploy rights) from the **live data-plane Agent Identity** (needs only `roles/aiplatform.user` + narrow tool/telemetry roles + PAB ceiling) prevents a prompt-injected runtime agent from deploying rogue agents or modifying infrastructure! → Lab 14 & Lab 16.
- **Why B, C, and D are incorrect**: `roles/editor`, static JSON keys, and self-escalating `securityAdmin` agents are catastrophic security anti-patterns.
</details>

---

### Question 60
**Scenario**: You self-host `gemma-4-31b-it` using `vLLM` across 8 NVIDIA A100 GPU pods on GKE for an interactive customer-support agent that sends a **28,000-token system prompt + tool catalog** on every turn. Behind a standard round-robin L7 HTTP Load Balancer, consecutive turns hit different GPU pods—recomputing the 28K prefill from scratch, spiking Time-To-First-Token (TTFT), and causing KV-cache OOMs whenever nightly batch evaluations run concurrently.

**Which GKE architecture resolves both TTFT prefill waste and batch starvation?**
- **A)** Deploy **GKE Inference Gateway** with an **`InferencePool`** (using the Endpoint Picker extension for **KV-cache / prefix-cache hit affinity** and GPU HBM saturation routing) and **`InferenceModel`** criticality tiers (`Critical` for live customer support, `Sheddable` for nightly batch evaluations).
- **B)** Switch to an L4 TCP Load Balancer with client-IP affinity and scale HPA on CPU utilization >80%.
- **C)** Move the 8 A100 vLLM pods to Cloud Run Functions without GPUs.
- **D)** Delete the 28,000-token tool catalog so the agent guesses tool schemas blindly.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **GKE Inference Gateway** (`InferencePool` + `InferenceModel`) scrapes real-time `vLLM` KV-cache and queue metrics via its Endpoint Picker (EPP), routing multi-turn prompts to the GPU pod already holding the 28K prefix in HBM KV-cache while shedding `Sheddable` batch evals during traffic spikes to protect `Critical` live turns. → Lab 19 — GKE Inference Gateway and GPUs.
- **Why B, C, and D are incorrect**: Proxy traffic shares one client IP, CPU % does not track GPU KV-cache HBM saturation, and removing schemas breaks tool calls.
</details>

---

### Question 61
**Scenario**: On a single **GKE** cluster, you must run both:
1. `InferencePool` `vLLM` pods requiring **NVIDIA L4 GPUs** (`--accelerator type=nvidia-l4`), and
2. `GkeCodeExecutor(executor_type="sandbox")` pods requiring **GKE Sandbox (`--sandbox type=gvisor`)**.
Attempting to create one GKE node pool with both flags fails validation.

**What is the correct GKE topology?**
- **A)** Provision **two distinct node pools in the same GKE cluster**—a **GPU node pool** (`g2-standard` + L4 GPUs) for `InferencePool` pods and a **CPU gVisor node pool** (`--sandbox="type=gvisor"`) for `GkeCodeExecutor(executor_type="sandbox")` pods—using Kubernetes taints/tolerations and `runtimeClassName: gvisor` to schedule each workload onto its matching pool.
- **B)** Switch `GkeCodeExecutor` to `UnsafeLocalCodeExecutor` inside the GPU pod.
- **C)** Switch `GkeCodeExecutor` to `executor_type="job"` on GPU nodes assuming `job` mode provides gVisor `runsc` syscall interception.
- **D)** Create two separate Google Cloud Organizations.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: GKE does not combine hardware GPU passthrough and gVisor (`runsc`) on the same VM node pool; separating GPU serving nodes and gVisor sandbox CPU nodes inside one cluster via node selectors/taints is the standard production topology. → Lab 05 & Lab 19.
- **Why B, C, and D are incorrect**: `UnsafeLocalCodeExecutor` and `executor_type="job"` lack gVisor syscall isolation, and separate Orgs are unnecessary.
</details>

---

### Question 62
**Scenario**: A multi-agent support workflow exhibits p99 latency spikes of 16 seconds. On each turn, the root agent calls Gemini, fans out to three MCP tools concurrently, and summarizes the result. You need to pinpoint whether the 16-second bottleneck is LLM prefill/generation, one slow MCP server, or parallel fan-in stragglers, using **least-privilege observability IAM**.

**Which configuration of `google.adk.telemetry` and IAM roles should you deploy?**
- **A)** Enable OpenTelemetry export (`adk telemetry enable` / `google.adk.telemetry.google_cloud`) to inspect **`trace_call_llm`**, **`trace_tool_call`**, and **`trace_merged_tool_calls`** waterfall spans in **Cloud Trace**, granting the runtime Service Account **`roles/cloudtrace.agent`**, **`roles/logging.logWriter`**, and **`roles/monitoring.metricWriter`**.
- **B)** Grant the agent `roles/logging.admin` and SSH into serverless containers to run `top`.
- **C)** Disable telemetry (`adk telemetry disable`) to save 2 ms and guess which MCP server is slow from monthly billing CSVs.
- **D)** Check IAM Policy Analyzer logs to measure SQL query latency.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: ADK natively emits `trace_call_llm`, `trace_tool_call`, and `trace_merged_tool_calls` spans to **Cloud Trace**, immediately exposing straggler MCP calls in a waterfall view, while `roles/cloudtrace.agent` + `roles/logging.logWriter` + `roles/monitoring.metricWriter` provide write-only telemetry least privilege. → Lab 15 — Observability and Troubleshooting.
- **Why B, C, and D are incorrect**: Over-privilege the agent or fail to attribute per-phase distributed latency.
</details>

---

### Question 63
**Scenario**: Building on Question 62, your hospital's **HIPAA Privacy Officer** approves exporting span latencies, HTTP status codes, and token-usage counters to Cloud Trace and Cloud Logging, **provided zero raw patient prompts, EHR tool outputs, or LLM responses are ever written into trace span attributes**.

**Which ADK telemetry setting enforces this requirement?**
- **A)** Configure **`TelemetryConfig`** with **`ContentCapturingMode`** set to disable/omit payload content capture in production while keeping span timing and `_token_usage` telemetry active.
- **B)** Capture full raw PHI payloads into Cloud Trace and ask engineers not to click on spans.
- **C)** Run `adk telemetry disable` so all latency and error visibility is lost.
- **D)** Store raw patient prompts in public GitHub Issues instead.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **`ContentCapturingMode`** in `google.adk.telemetry.TelemetryConfig` controls whether prompt/response/tool strings are attached to OpenTelemetry spans. Disabling content capture in production preserves full SLO latency and token accounting with zero PHI leakage into observability storage! → Lab 15 & Lab 20.
- **Why B, C, and D are incorrect**: Either violate HIPAA by persisting raw PHI in trace sinks or blind SRE operations completely.
</details>

---

### Question 64
**Scenario**: In Cloud Logging, your production pipeline raises `google.adk.workflow.NodeTimeoutError` on 3% of runs during peak hours.

**What specifically caused `NodeTimeoutError`, and how should you remediate it?**
- **A)** A `Node` inside a **`google.adk.workflow.Workflow`** graph (or workflow-backed agent) exceeded its configured node `timeout`; inspect `node_tracing` spans in Cloud Trace to identify whether a downstream tool/LLM call inside that node needs caching, parallelization, or a tuned `RetryConfig` / `timeout`.
- **B)** GKE failed to pull a container image from Docker Hub.
- **C)** Principal Access Boundary (PAB) rejected an OAuth scope.
- **D)** `gemini-embedding-2` exceeded 8,192 dimensions.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `NodeTimeoutError` is raised specifically by `google.adk.workflow` when an orchestrated graph `Node` breaches its execution `timeout` budget. → Lab 08 & Lab 15.
- **Why B, C, and D are incorrect**: Produce Kubernetes `ImagePullBackOff`, IAM `403 PERMISSION_DENIED`, or invalid-argument errors, not `NodeTimeoutError`.
</details>

---

### Question 65
**Scenario**: Production token-cost alerts fire because an autonomous support research `LlmAgent` occasionally enters a **runaway reasoning loop**, calling `search_ticket_archive` 45 times in a row with nearly identical query strings when an obscure product SKU does not exist.

**Which two code-level guardrails stop runaway tool loops cleanly? (Select TWO)**
- **A)** Bound iterative loops with **`max_iterations`** (on `LoopAgent` / `RunConfig`) so execution cannot spin indefinitely.
- **B)** Implement a **`before_tool_callback`** hook (or stateful plugin) that hashes `(tool_name, normalized_args)` in `session.state` and blocks duplicate repeated queries, returning a deterministic instruction to synthesize findings or state "SKU not found".
- **C)** Double the Cloud Run memory limit from 2 GiB to 4 GiB.
- **D)** Remove all search tools so the agent hallucinates SKU specs from memory.
- **E)** Grant `roles/bigquery.admin` to speed up loop iterations.

<details><summary>Show answer</summary>

**Correct Answers: A and B**
**Explanation**:
- **Why A and B are correct**: Objective 4.2 explicitly tests troubleshooting **"agent reasoning loops"**. Combining hard iteration caps (`max_iterations`) with a deduplicating **`before_tool_callback`** breaks stagnant search cycles gracefully without removing search capability. → Lab 15 — Observability and Troubleshooting.
- **Why C, D, and E are incorrect**: More RAM lets loops burn even more tokens, removing search causes hallucinations, and IAM admin roles are irrelevant.
</details>

---

### Question 66
**Scenario**: Four months after launching a telecom customer-support agent with 92% task success, you have **not** changed a single line of agent code or pinned model ID (`gemini-3.7-flash`). Yet continuous production evaluation (`EvalTask` over sampled traces) shows `rubric_based_tool_use_quality_v1` dropping steadily from 0.92 to 0.71 after the company launched three new 5G plan tiers and updated CRM status codes.

**What operational phenomenon is occurring, and what is the correct closed-loop response?**
- **A)** **Concept / Data & Environment Drift**: customer vocabulary and upstream CRM domain values shifted relative to your static prompt examples, RAG corpus, and golden `.evalset.json`. Re-index updated 5G plan docs in RAG/Agent Search, harvest failing production traces (redacted via SDP) into `.evalset.json` via `adk eval_set add_eval_case`, and run `adk optimize` + `adk eval` before redeploying.
- **B)** Weights of the pinned `gemini-3.7-flash` checkpoint randomly decayed on disk.
- **C)** Principal Access Boundary policies gradually expire 5% per month.
- **D)** GKE gVisor converted Python integers into floats.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Even with a pinned model ID, **agent drift** (Objective 4.2) occurs when external enterprise schemas, product catalogs, and user intents evolve. Continuous evaluation catches the drop, and feeding redacted failure cases back into `.evalset.json` + RAG + `adk optimize` closes the loop. → Lab 13 & Lab 15.
- **Why B, C, and D are incorrect**: Pinned checkpoints, PAB rules, and gVisor syscalls do not decay over time.
</details>

---

### Question 67
**Scenario**: Your customer-support ADK `App` (`google.adk.apps.App`) loads a static 45,000-token compliance handbook + 30 MCP tool definitions on every turn, and VIP troubleshooting chats often run for 60+ turns—causing growing input-token costs and rising prefill latency by turn 40.

**Which two built-in `google.adk.apps.App` configurations directly optimize cost and multi-turn latency? (Select TWO)**
- **A)** Configure **`context_cache_config`** on `App` (combined with `static_instruction`) to cache the invariant 45,000-token handbook and tool schemas across turns.
- **B)** Configure **`events_compaction_config`** on `App` to periodically summarize/compact older conversational event turns instead of resending all 60 raw turns verbatim.
- **C)** Set `block_on_screening_failure=False` on `ModelArmorConfig`.
- **D)** Switch session storage from `RedisSessionService` to `UnsafeLocalCodeExecutor`.
- **E)** Paste the 45,000-token handbook a second time inside every user message.

<details><summary>Show answer</summary>

**Correct Answers: A and B**
**Explanation**:
- **Why A and B are correct**: Verified on `google.adk.apps.App(name, root_agent, plugins, events_compaction_config, context_cache_config, resumability_config)`: **`context_cache_config`** cuts token cost and TTFT on large static instructions/schemas, while **`events_compaction_config`** bounds multi-turn history growth! → Lab 08, Lab 09 & Lab 15.
- **Why C, D, and E are incorrect**: Weaken security, misuse code executors, or double token waste.
</details>

---

### Question 68
**Scenario**: During an evaluation audit of a multi-turn technical-support agent, `trajectory_evaluator` reports 95% (it calls the right diagnostic tools), `hallucinations_v1` reports 99% (no fabricated facts), yet **`multi_turn_task_success_evaluator`** scores only **48%** because the agent stops after printing raw diagnostic JSON without ever executing the final router-reboot step the user originally asked for.

**Why was `multi_turn_task_success_evaluator` essential here?**
- **A)** Individual tool calls can be valid and grounded (`trajectory` / `hallucinations`), yet the agent still fails to **complete the user's end-to-end multi-turn goal**—which `multi_turn_task_success_evaluator` specifically measures across the full conversation.
- **B)** `multi_turn_task_success_evaluator` measures Kubernetes pod CPU throttling.
- **C)** `hallucinations_v1` only works on audio files.
- **D)** `trajectory_evaluator` deletes the final turn of every session.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Each ADK evaluator covers an orthogonal failure axis: tool sequence (`trajectory_evaluator`), factual grounding (`hallucinations_v1`), response rubric quality (`rubric_based_final_response_quality_v1`), and **end-to-end goal completion across turns** (`multi_turn_task_success_evaluator`). → Lab 13 — Agent Evaluation.
- **Why B, C, and D are incorrect**: Misdescribe ADK's built-in evaluation modules.
</details>

---

## Domain 5: Securing and Governing Agentic Workflows (~15% · Questions 69–80)

### Question 69
**Scenario**: A development team deploying an ADK customer-support agent to GKE asks you to generate a downloadable **Service Account JSON key file**, base64-encode it into a Kubernetes Secret, and mount it into the agent pod so the agent can call Vertex AI, BigQuery, and third-party OAuth APIs.

**Why must you reject this design, and what is the Google Cloud-recommended credential architecture?**
- **A)** Static JSON keys are long-lived, exfiltratable bearer secrets (blocked by Org Policy `constraints/iam.disableServiceAccountKeyCreation`). Instead, use **Agent Identity** (`google.adk.integrations.agent_identity` — `GcpAuthProvider` / `GcpAuthProviderScheme` + GKE Workload Identity Federation) to mint **short-lived, auto-rotated OIDC/OAuth tokens** managed via `AuthProviderCredentialsServiceClient`, governed by a **Principal Access Boundary (PAB)**.
- **B)** Base64-encoding JSON keys is fine as long as you also paste a backup copy into `GEMINI.md`.
- **C)** Replace the Service Account JSON key with a personal Google Workspace Super Admin refresh token.
- **D)** Disable TLS and authentication on all internal APIs inside the VPC.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Safe credential provisioning for agents (Sections 3.2 & 5.1) mandates **zero static Service Account JSON keys**: **Agent Identity** (`GcpAuthProvider` + `AuthProviderCredentialsServiceClient`) and Workload Identity Federation issue short-lived tokens bound to the agent's cryptographic workload identity and capped by a **PAB**. → Lab 16 — Agent Identity and Auth.
- **Why B, C, and D are incorrect**: Expose long-lived or super-admin credentials or strip zero-trust authentication.
</details>

---

### Question 70
**Scenario**: An IAM administrator accidentally grants `roles/bigquery.admin` and `roles/storage.admin` at the **Google Cloud Organization root** to the **Agent Identity** of an experimental marketing-analytics agent. Fortunately, your security team previously bound a **Principal Access Boundary (PAB)** policy to that Agent Identity listing **only** `//cloudresourcemanager.googleapis.com/projects/marketing-sandbox-dev` in its `eligible_resources`.

When a prompt-injection payload tricks the marketing agent into querying `projects/hr-compensation-prod.payroll.executive_bonuses`, what happens?
- **A)** The request fails deterministically with **`403 PERMISSION_DENIED`**, because $\text{Effective Access} = \text{IAM Allow} \cap \text{PAB}$. Since `hr-compensation-prod` is outside the PAB's eligible resources ceiling, even an Organization-root IAM Allow grant is neutralized.
- **B)** The query succeeds because Organization-level `roles/bigquery.admin` overrides PAB policies.
- **C)** The query succeeds unless `ModelArmorPlugin` recognizes the table name via regex.
- **D)** PAB only restricts human Workspace users, not Agent Identities.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 5.1 tests *"Configuring principal access boundary (PAB) policies using Agent Identity"*. A PAB sets a hard identity-centric blast-radius ceiling ($\text{IAM Allow} \cap \text{PAB}$): it never grants permissions by itself, and no IAM Allow binding anywhere in the hierarchy can grant access outside the PAB's eligible resources. → Lab 16 & Lab 20.
- **Why B, C, and D are incorrect**: IAM Allow never overrides PAB, enforcement occurs at the IAM plane independent of Model Armor, and PAB natively binds to Agent Identities.
</details>

---

### Question 71
**Scenario**: A **HIPAA-regulated patient support agent** receives free-text chat messages in which patients frequently type their **Social Security Number (SSN)**, **Medical Record Number (MRN)**, and **phone number**. Compliance requires that:
1. SSNs, MRNs, and phone numbers be **masked/redacted into `[REDACTED_SSN]` / cryptographic tokens in-flight** *before* the prompt reaches Gemini AND *before* any model output returns to downstream ticketing tools.
2. Prompt injection and malicious phishing URLs are blocked simultaneously.
3. Both the runtime agent and the security services operate under **least-privilege IAM**.

**Which Model Armor + Sensitive Data Protection (SDP) configuration and IAM setup should you deploy?**
- **A)** Configure a **Model Armor template (`google.cloud.modelarmor_v1.FilterConfig`)** enabling `PiAndJailbreakFilterSettings`, `MaliciousUriFilterSettings`, and **`SdpFilterSettings` with `SdpAdvancedConfig(inspect_template=..., deidentify_template=...)`**; attach **`ModelArmorPlugin(block_on_screening_failure=True)`**; grant the runtime agent **`roles/modelarmor.user`**; and grant the Model Armor service agent **`roles/dlp.user` + `roles/dlp.inspectTemplatesReader` + `roles/dlp.deidentifyTemplatesReader`**.
- **B)** Deploy **Cloud Armor** L7 WAF OWASP SQLi rules in front of Cloud Run without Model Armor or SDP.
- **C)** Use `SdpBasicConfig` expecting custom cryptographic surrogate tokenization without any `deidentify_template`, and grant the runtime agent `roles/modelarmor.admin`.
- **D)** Ask patients nicely in the welcome message not to type SSNs, with no technical redaction.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Verified directly in `google.cloud.modelarmor_v1`: **`SdpAdvancedConfig`** links Cloud **Sensitive Data Protection (`inspect_template` + `deidentify_template`)** directly into Model Armor's `FilterConfig`, redacting/tokenizing PHI in-flight alongside prompt-injection (`PiAndJailbreakFilterSettings`) and URL (`MaliciousUriFilterSettings`) screening—while keeping runtime agents strictly on least-privilege **`roles/modelarmor.user`**. → Lab 17 & Lab 20.
- **Why B is incorrect**: **Cloud Armor** is an HTTP/DDoS L7 WAF; it does **not** perform semantic PHI de-identification or LLM jailbreak detection!
- **Why C and D are incorrect**: `SdpBasicConfig` only inspects/blocks rather than applying custom `deidentify_template` transformations, `roles/modelarmor.admin` lets the agent weaken its own guardrails, and UI warnings are not HIPAA technical safeguards.
</details>

---

### Question 72
**Scenario**: Your security team already enforces **Model Armor** centrally on **Agent Gateway** at the ingress/egress perimeter of your multi-agent platform. An application architect asks: *"Since Agent Gateway already screens the user's incoming HTTP prompt and final outgoing response with Model Armor, why do we ALSO attach `ModelArmorPlugin` inside our ADK customer-support agent?"*

**What critical attack vector does the in-agent `ModelArmorPlugin` catch that perimeter-only user-prompt screening misses?**
- **A)** **Indirect Prompt Injection inside mid-loop tool / MCP / RAG outputs**: when the ADK agent fetches an untrusted external email, Jira comment, or web page mid-turn via an MCP tool, `ModelArmorPlugin` (`after_tool_callback` / `before_model_callback`) screens that tool payload *before* feeding it into the LLM—whereas an ingress-only gateway check only saw the user's clean initial prompt!
- **B)** `ModelArmorPlugin` replaces Kubernetes Horizontal Pod Autoscaling.
- **C)** Agent Gateway cannot validate OAuth 2.0 tokens unless `ModelArmorPlugin` is disabled.
- **D)** `ModelArmorPlugin` compiles Python into Rust binaries.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Explains the **Gateway + Plugin defense-in-depth** architecture: **Agent Gateway + Model Armor** guarantees org-wide perimeter governance (no unscreened ingress/egress even for non-ADK agents), while in-process **`ModelArmorPlugin`** intercepts **internal mid-loop tool/MCP responses** (`before_model_callback` / `after_tool_callback`) where **indirect prompt injections** hide inside retrieved third-party data! → Lab 17, Lab 18 & Lab 20.
- **Why B, C, and D are incorrect**: Unrelated to prompt-injection screening layers.
</details>

---

### Question 73
**Scenario**: For a regulated financial wire-transfer agent using `ModelArmorPlugin`, compliance requires that if the Model Armor API experiences a transient regional network timeout, the agent **must immediately block the turn** rather than letting an unscreened prompt reach the LLM.

**Which exact boolean field on `ModelArmorConfig` enforces this fail-closed behavior?**
- **A)** `block_on_screening_failure=True`
- **B)** `block_on_screening_failure=False`
- **C)** `allow_egress=True`
- **D)** `disallow_transfer_to_peers=False`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In `google.adk.integrations.model_armor.ModelArmorConfig`, **`block_on_screening_failure=True`** enforces **fail-closed** security (blocking execution whenever screening errors or times out), whereas `False` fails open for availability-first non-regulated bots. → Lab 17 — Model Armor and HITL.
- **Why B, C, and D are incorrect**: `False` fails open, and the other flags belong to `CloudRunSandboxCodeExecutor` and `LlmAgent`.
</details>

---

### Question 74
**Scenario**: A customer logs into your banking web portal (issuing a user-scoped OAuth 2.0 access token), talks to a `FrontDoorAgent`, which delegates via **A2A** to a `PortfolioAgent`, which queries a `HoldingsMcpServer`. When Bob (`user_id=bob`) asks *"Show my account holdings"*, you must guarantee `HoldingsMcpServer` cryptographically verifies **Bob's** identity and cannot be tricked by prompt injection into returning Alice's holdings.

**How should identity propagation be architected across these hops?**
- **A)** Validate Bob's OAuth 2.0 token at **Agent Gateway** and propagate a cryptographically verifiable user credential/assertion (or OBO exchanged token via **Auth Manager**) through **trusted A2A & MCP protocol headers**—never via LLM-generated prompt text or tool arguments—so `HoldingsMcpServer` enforces row-level authorization on the verified token claim (`sub == bob`).
- **B)** Pass `"user_id": "bob"` as an LLM-generated string parameter in `get_holdings(user_id: str)` and trust whatever string the LLM outputs.
- **C)** Run `HoldingsMcpServer` with a single shared database superuser account and filter rows in the system prompt.
- **D)** Write Bob's bearer token into a world-readable GCS bucket.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 5.2 explicitly tests *"Configuring secure access to data and identity propagation (Agent Gateway and Agent Registry)"*. Letting an LLM choose `user_id` as a tool parameter creates an immediate **Confused Deputy** vulnerability under prompt injection; propagating verified OAuth/JWT claims out-of-band in trusted **Agent Gateway / A2A / MCP headers** guarantees row-level security at the data tier. → Lab 16, Lab 18 & Lab 20.
- **Why B, C, and D are incorrect**: Classic Confused Deputy and credential-exposure vulnerabilities.
</details>

---

### Question 75
**Scenario**: A registered `BillingSupportAgent` presents a valid Agent Identity credential to **Agent Gateway**, but due to a prompt injection it attempts to invoke `delete_customer_ledger` on a Finance MCP server—a destructive capability NOT listed in its approved metadata.

**Which two statements accurately describe how Agent Registry and Agent Gateway govern this request? (Select TWO)**
- **A)** **Agent Registry** maintains the authoritative inventory of attested agent versions, owners, Agent Cards, and **approved tool/MCP capability allowlists**.
- **B)** **Agent Gateway** acts as the runtime Policy Enforcement Point (PEP), evaluating the authenticated call against **Agent Registry** policy metadata, **denying** `delete_customer_ledger` with `403`, and emitting an immutable audit log.
- **C)** Because the OAuth/OIDC token is cryptographically valid, Agent Gateway must allow any tool on the MCP server.
- **D)** A Principal Access Boundary (PAB) automatically grants `delete_customer_ledger` if it is narrower than `roles/owner`.
- **E)** Model Armor dynamically grants IAM roles when prompts are polite.

<details><summary>Show answer</summary>

**Correct Answers: A and B**
**Explanation**:
- **Why A and B are correct**: Authentication (*who is calling*) ≠ authorization (*which capabilities are governed*). **Agent Registry** serves as the governance source of truth, and **Agent Gateway** enforces capability-level authorization, quotas, and audit logging in real time. → Lab 18 & Lab 20.
- **Why C, D, and E are incorrect**: Valid authn never implies blanket authz, PAB only restricts (never grants), and Model Armor never grants IAM permissions.
</details>

---

### Question 76
**Scenario**: Your SOC discovers a critical zero-day vulnerability in a PDF-parsing library bundled inside `ClaimsAgent v2.1`. Your team builds and registers patched `ClaimsAgent v2.2`, and needs **100% of enterprise A2A traffic from 40 upstream callers** to cut over immediately with **zero code redeployments** on the 40 caller apps and instant revocation of `v2.1`.

**Which governance mechanism accomplishes this?**
- **A)** Update **`AgentRegistry`** to mark `ClaimsAgent v2.2` as the active attested production endpoint and deprecate/quarantine `v2.1`, so **Agent Gateway** and dynamic `registry.get_remote_a2a_agent()` callers route all new traffic to `v2.2` and reject `v2.1` immediately.
- **B)** Email 40 application teams asking them to edit hardcoded IP addresses next sprint.
- **C)** Delete the entire GCP Organization.
- **D)** Append `"Please ignore CVE exploits"` to `v2.1`'s system prompt.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Decoupling logical agent identity in **`AgentRegistry`** from physical runtime URLs allows **Agent Gateway** and registry-resolved clients to perform instant version cutovers and emergency quarantine revocations across the enterprise. → Lab 18 — Governance, Gateway, Registry.
- **Why B, C, and D are incorrect**: Leave vulnerable endpoints reachable, cause catastrophic outages, or rely on ineffective prompt text.
</details>

---

### Question 77
**Scenario**: Which IAM role distinction enforces **separation of duties** for **Model Armor** so that central Security Operations engineers can create/update corporate `FilterConfig` templates (`SdpAdvancedConfig`, jailbreak thresholds), while 50 application-team ADK agents can **invoke** `sanitizeUserPrompt` / `sanitizeModelResponse` at runtime **without** being able to weaken or delete those templates?

- **A)** Grant Security Operations **`roles/modelarmor.admin`** (in a dedicated central security project) and grant the 50 runtime Agent Identities **`roles/modelarmor.user`** on those templates.
- **B)** Grant all 50 runtime Agent Identities `roles/modelarmor.admin`.
- **C)** Grant all developers `roles/owner` on the security project.
- **D)** Disable IAM and share a single API key across SecOps and runtime pods.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Hosting Model Armor templates in a central security project administered via **`roles/modelarmor.admin`** while granting cross-project runtime agents **`roles/modelarmor.user`** guarantees that neither application developers nor compromised agents can tamper with safety/SDP templates! → Lab 17 & Lab 20.
- **Why B, C, and D are incorrect**: Violate separation of duties and least privilege.
</details>

---

### Question 78
**Scenario**: A retail customer-support agent can:
1. Check order tracking status ($0 risk, read-only),
2. Issue store-credit goodwill coupons up to $25 (low risk, reversible), and
3. Process wire/card chargeback reversals over **$250** (high financial & fraud risk, irreversible).

**How should you tier guardrails across these three actions?**
- **A)** Allow (1) autonomously under read-only IAM (`roles/bigquery.dataViewer` / `roles/discoveryengine.viewer`), enforce deterministic schema + rate/amount bounds in code + Model Armor on (2), and enforce a **mandatory deterministic Human-in-the-Loop (HITL) approval gate** (`get_user_choice` / `request_input` / `LongRunningFunctionTool`) before executing (3).
- **B)** Require a VP to manually approve every read-only tracking-number lookup, and let wire reversals run autonomously with zero checks.
- **C)** Rely solely on system instructions (*"Never refund more than $250 unless sure"*) while giving the tool unrestricted Stripe Admin API permissions.
- **D)** Block all three actions permanently with `ModelArmorPlugin`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 5.2 tests *"Designing appropriate safety frameworks and guardrails (Agent Gateway, Model Armor, HITL)"*. Risk-tiered autonomy keeps read-only paths fast while placing deterministic code checks and **HITL approval gates** squarely in front of high-impact, irreversible mutations. → Lab 10 & Lab 17.
- **Why B, C, and D are incorrect**: Invert risk tiers, rely on jailbreakable prompt text for financial caps, or break business utility.
</details>

---

### Question 79
**Scenario**: You are conducting a final HIPAA compliance & security review for a multi-agent **patient customer-support platform** on Google Cloud. Which **complete** set of controls is required before handling live Protected Health Information (PHI)?

- **A)** Executed Google Cloud **BAA**; all in-scope services (Vertex AI / Agent Runtime / GKE, Agent Search, Cloud Storage, Cloud SQL, Model Armor, SDP, Cloud Logging/Trace) inside a **VPC Service Controls (VPC-SC)** perimeter encrypted with **CMEK**; **Model Armor + `SdpAdvancedConfig`** (`inspect_template` + `deidentify_template`) masking unnecessary PHI in-flight; **`ContentCapturingMode`** configured to omit raw prompt/PHI payloads from traces; **Agent Gateway** propagating patient OAuth 2.0 identity; **Agent Identity** with **zero static SA keys** + **Principal Access Boundary (PAB)**; and **deterministic GECX Flows / HITL** for clinical or billing mutations.
- **B)** Public Cloud Run URLs (`allUsers`), `ContentCapturingMode` logging full raw SSNs/diagnoses to Cloud Trace, static SA JSON keys with `roles/editor`, and Cloud Armor WAF alone without SDP or BAA.
- **C)** Storing patient PHI in `InMemorySessionService` on shared developer laptops outside VPC-SC.
- **D)** Using `gemini-flash-latest` over public internet with prompt instructions *"Be HIPAA compliant"*.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Synthesizes every layer tested on regulated healthcare/HIPAA scenarios: **BAA + VPC-SC + CMEK** (data residency & perimeter), **Model Armor + SDP `SdpAdvancedConfig`** (in-flight PHI de-identification), **zero-capture `ContentCapturingMode`** (observability privacy), **Agent Gateway OAuth propagation + Agent Identity + PAB** (zero-trust least-privilege IAM), and **deterministic GECX/HITL gates** (clinical/financial safety). → Lab 03, Lab 15, Lab 17 & Lab 20.
- **Why B, C, and D are incorrect**: Violate multiple mandatory HIPAA technical and administrative safeguards.
</details>

---

### Question 80
**Scenario**: In an end-to-end **AI Threat Defense** architecture review for a multi-project enterprise customer-support mesh, map the **four core security threats** to their exact Google Cloud control planes:
1. Unauthenticated / rate-abusive A2A & MCP traffic and loss of end-user OAuth 2.0 identity across agent hops.
2. Compromised or shadow agents invoking unapproved rogue MCP servers or unattested peer agents.
3. Direct user jailbreaks AND indirect prompt injections / PII leaks inside mid-loop MCP tool outputs, including safe behavior during scanner outages.
4. Over-privileged IAM role grants enabling lateral access to unrelated GCP projects if an agent is hijacked.

**Which 4-control mapping is 100% accurate?**
- **A)** (1) **Agent Gateway** · (2) **Agent Registry (`AgentRegistry`)** · (3) **Model Armor (`FilterConfig` + `SdpAdvancedConfig` + `ModelArmorPlugin(block_on_screening_failure=True)`)** · (4) **Agent Identity + Principal Access Boundary (PAB)**
- **B)** (1) Cloud DNS · (2) `GCPSkillRegistry` · (3) `UnsafeLocalCodeExecutor` · (4) `roles/owner`
- **C)** (1) GKE Inference Gateway · (2) `FallbackModel` · (3) `ModelArmorConfig(block_on_screening_failure=False)` · (4) static Service Account JSON keys
- **D)** (1) `GEMINI.md` · (2) `temperature=0.0` · (3) `Rouge` · (4) `InMemoryMemoryService`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: This is the complete 4-pillar Google Cloud **AI Threat Defense** architecture:
  1. **Agent Gateway** enforces authentication, quotas, audit logging, and user OAuth 2.0 identity propagation.
  2. **Agent Registry** governs discovery of attested A2A Agent Cards (`get_remote_a2a_agent`) and approved MCP servers (`get_mcp_toolset`).
  3. **Model Armor + SDP** enforces fail-closed (`block_on_screening_failure=True`) prompt-injection, malicious-URI, and PHI/PII sanitization at both perimeter and mid-loop plugin callbacks.
  4. **Agent Identity + Principal Access Boundary (PAB)** enforces keyless credentials and an unbreakable resource ceiling ($\text{IAM Allow} \cap \text{PAB}$). → Lab 20 — E2E AI Threat Defense.
- **Why B, C, and D are incorrect**: Confuse GPU inference routing (`GKE Inference Gateway`), fail-open configs, static keys, or non-security components with the 4-layer security plane.
</details>

---

## Scoring and Diagnosis

> [!TIP]
> **Beta vs. Mid-November GA Calibration**:
> - This 80-question practice exam mirrors the **~80-question, 3-hour Beta exam** length.
> - **The GA exam launches in mid-November and will have a lesser question count** (typically ~50–60 questions in 2 hours), using the **exact same percentage weights** below.

| Score (out of 80) | Meaning | Recommended Action |
| :---: | :--- | :--- |
| **0–47 (<60%)** | **Foundational gaps.** | Do not book yet. Work through Tracks 3, 4, and 5 plus the Least-Privilege IAM Matrix in [`STUDY_GUIDE.md`](STUDY_GUIDE.md). |
| **48–63 (60–79%)** | **Close, but risky.** | Audit every missed question below by domain—especially IAM roles, Antigravity customization files, GECX flows, Reranking API, and Rubric vs. Metric distinctions. |
| **64–80 (≥80%)** | **Exam ready.** | You have strong command of the official 28-tool scope, ADK 2.9.0, IAM/PAB least privilege, HIPAA/support patterns, and multi-agent trade-offs. |

### Domain Breakdown Tracker (Exact Official Weights)

| Official Exam Domain | Question Range | Weight | Your Score | Target (≥80%) |
| :--- | :---: | :---: | :---: | :---: |
| **1. Building Agents Using Low-Code Tools** (`GECX`, `GEApp`, Connectors, Multimodal) | Q1 – Q10 | ~13% (12.5%) | ___ / 10 | **8 / 10** |
| **2. Using Coding Agents for Application Development** (`Antigravity`, `hooks.json`, `SKILL.md`, `Agents CLI`, `Code Mender`, Sandboxes) | Q11 – Q24 | ~17% (17.5%) | ___ / 14 | **12 / 14** |
| **3. Developing Custom Agents** (`ADK`, Latency Math, Sessions/Memory Bank, `RAG Engine` + Ranking API, Cross-Project `A2A` & `MCP`) | Q25 – Q50 | ~33% (32.5%) | ___ / 26 | **21 / 26** |
| **4. Evaluating and Deploying Agentic Workflows** (Rubric vs. Metric, Gen AI Eval Service, `Agent Runtime` vs `GKE`, Inference Gateway, Trace/HIPAA) | Q51 – Q68 | ~22% (22.5%) | ___ / 18 | **15 / 18** |
| **5. Securing and Governing Agentic Workflows** (`Agent Identity`, `PAB`, `Model Armor` + `SDP`, `Agent Gateway`, `Agent Registry`, `HITL`, `HIPAA`) | Q69 – Q80 | ~15% (15.0%) | ___ / 12 | **10 / 12** |
| **Total** *(with ~32.5% cross-cutting IAM & Identity questions across Domains 1–5)* | **Q1 – Q80** | **100%** | **___ / 80** | **64 / 80** |

