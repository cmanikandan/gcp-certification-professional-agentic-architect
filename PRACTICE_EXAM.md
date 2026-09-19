# Google Cloud Certified Professional Agentic Architect — High-Yield Practice Exam

> [!IMPORTANT]
> **Personal, unofficial repository.** This is a personal study project. It is **not
> affiliated with, endorsed by, or maintained by Google or Google Cloud**. These questions
> were written by the repository author — they are **not real exam questions** and are not
> drawn from the live exam. For official guidance — exam objectives, registration, policies,
> and the current exam guide — refer to
> **[cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect)**.
> See [`DISCLAIMER.md`](DISCLAIMER.md) for the full disclaimer.

This unofficial practice set uses the objectives and domain weights in the official exam guide. It is a study aid, not a claim about the live exam's exact wording, length, or difficulty. A score of ≥80% across all domains indicates strong readiness for the live exam.

<details><summary><b>How to use this exam</b></summary>
Answers are collapsed by default. Read the scenario, choose your answer, and expand the details block to check it. Every question explains why the correct answer is right and why the distractors are wrong in the context of the scenario.
</details>

---

## Domain 1: Building Agents Using Low-Code Tools (~13%)

### Question 1
**Scenario**: Your retail organization wants to deploy an AI customer service agent using Gemini Enterprise low-code tools. The agent must guide customers through a 3-step order return process (Select Order -> Validate Reason -> Generate Return Label). If the customer provides an invalid tracking number twice, the agent must escalate the conversation to a human tier without crashing or losing session context.

**Which architectural configuration should you implement in CX Agent Studio?**
- **A)** Create a single Page with an inline Python cloud function that maintains a retry counter in memory and triggers a webhook transition.
- **B)** Configure dedicated Pages for each return stage, configure Transition Routes with parameter conditions, and implement an Event Handler for `sys.no-match-2` that transitions to an Agent Handoff page.
- **C)** Use a single generative prompt template in Agent Designer and instruct the LLM in system instructions to count retries internally before generating an escalation message.
- **D)** Configure an Agent Search data store linked to return policies and allow zero-shot intent classification to handle return routing dynamically.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: In CX Agent Studio (formerly Dialogflow CX), state-based multi-step workflows are modeled using **Pages** and **Transition Routes**. Built-in **Event Handlers** (like `sys.no-match-2` or `sys.no-input-2`) automatically manage error counts and trigger deterministic transitions to an escalation/handoff page while preserving all session parameters. → Lab 02 — CX Agent Studio State.
- **Why A is incorrect**: Maintaining retry counters in custom webhook memory introduces unnecessary complexity and breaks the declarative state machine paradigm of CX Agent Studio.
- **Why C is incorrect**: Relying solely on LLM system instructions to count retries is non-deterministic and prone to hallucinations and reasoning loops.
- **Why D is incorrect**: Agent Search is designed for RAG over unstructured documents, not for managing stateful multi-step business transactions.
</details>

---

### Question 2
**Scenario**: An insurance company needs an agent in Gemini Enterprise that can ingest user-uploaded claims consisting of a PDF repair estimate, photos of vehicle damage, and a voice recording of the accident description. The agent must summarize the incident and verify if the damage photos match the written description.

**How should you configure the multimodal data ingestion pipeline?**
- **A)** Convert the audio recording using Speech-to-Text API, run Vision API on the photos for OCR, extract text from the PDF using Document AI, and pass combined text strings into a Gemini 2.5 Flash-Lite model.
- **B)** Upload the PDF, damage photos, and audio files directly into Cloud Storage, and provide their GCS URIs in a single multimodal prompt payload to Gemini 3.7 Flash within Gemini Enterprise Agent Designer.
- **C)** Embed the audio and images into a Vector Search index and use text search to retrieve the nearest matching insurance policy clauses.
- **D)** Ingest the data into BigQuery using BigQuery ML, and train a supervised classification model to evaluate the insurance claim.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Gemini 3.7 Flash natively supports multimodal reasoning across audio, high-resolution images, video, and PDF documents within a single context window. Referencing Cloud Storage URIs (`gs://...`) directly in the multimodal prompt eliminates complex multi-pipeline preprocessing and preserves rich cross-modal relationships. → Lab 03 — Enterprise Data and Multimodal.
- **Why A is incorrect**: Splitting the workflow into disparate APIs strips cross-modal nuance and increases latency and cost.
- **Why C is incorrect**: Vector embedding alone cannot perform multi-modal comparative reasoning across image damage and text repair quotes.
- **Why D is incorrect**: Training a custom BigQuery ML model requires labeled training datasets and does not provide generative reasoning.
</details>

---

### Question 3
**Scenario**: A healthcare provider wants to build a symptom-checking agent using Agent Designer. The agent must strictly follow a decision tree based on clinical guidelines, ensuring it never hallucinates a diagnosis or skips mandatory triage questions. 

**Which approach provides the strongest guarantee of adherence to the decision tree in a low-code environment?**
- **A)** Use a zero-shot prompt in Agent Designer with a long list of clinical rules and constraints.
- **B)** Configure a workflow in CX Agent Studio using explicit Pages, state parameters, and Transition Routes for each branch of the clinical decision tree.
- **C)** Upload the clinical guidelines PDF to Agent Search and rely on semantic retrieval to guide the LLM's responses.
- **D)** Use Gemini 2.5 Pro with a temperature of 0.0 and a custom few-shot prompt template outlining the tree.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: CX Agent Studio's state machine (Pages, Parameters, Transition Routes) enforces deterministic workflows. When absolute adherence to a business or clinical process is required, state-based routing is mandatory over generative approaches. → Lab 02 — CX Agent Studio State.
- **Why A is incorrect**: LLMs, even with long system instructions, are probabilistic and can skip steps or hallucinate, which is unacceptable for strict clinical triage.
- **Why C is incorrect**: Agent Search provides grounding for knowledge retrieval but does not enforce a step-by-step conversational state machine.
- **Why D is incorrect**: Temperature 0.0 reduces variance but does not guarantee the LLM will reliably navigate a complex multi-step decision tree without skipping or looping.
</details>

---

### Question 4
**Scenario**: You are using Gemini Enterprise Agent Designer to prototype an IT helpdesk agent. The agent frequently fails to extract the correct device MAC address format from user messages. You want to improve its extraction accuracy without migrating to a custom code solution or changing the underlying model.

**What is the most effective low-code mechanism to improve this behavior?**
- **A)** Add several few-shot examples (user messages and expected MAC address outputs) into the in-console prompt template.
- **B)** Switch the agent's model to Gemini 2.5 Flash-Lite to reduce token parsing latency.
- **C)** Upload a CSV of all employee MAC addresses to Agent Search.
- **D)** Configure a webhook to call an external Python script that uses regex to find the MAC address.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In-console prompt templates support few-shot prompting, which is highly effective for teaching the model specific data extraction patterns (like MAC addresses) without writing custom code or external regex. → Lab 01 — Agent Designer Workflows.
- **Why B is incorrect**: Switching to a Flash-Lite model prioritizes speed over reasoning capability and is likely to decrease extraction accuracy further.
- **Why C is incorrect**: Uploading a CSV to Agent Search provides grounding data but does not teach the LLM the pattern-matching skill required to extract the entity from the user's utterance.
- **Why D is incorrect**: While effective, creating and maintaining an external Python webhook violates the constraint of improving behavior "without migrating to a custom code solution".
</details>

---

### Question 5
**Scenario**: Your marketing team uses Gemini Enterprise to build an agent that generates ad copy. They want the agent to automatically reference the company's 200-page brand guidelines PDF so it consistently uses the correct tone and vocabulary. The marketing team has no coding experience.

**How should you integrate the brand guidelines?**
- **A)** Instruct the team to paste the 200-page PDF text directly into the system instructions.
- **B)** Configure an Agent Search data store, upload the brand guidelines PDF, and connect the data store to the agent in the console.
- **C)** Convert the PDF into a JSON schema and upload it as a parameter constraint in CX Agent Studio.
- **D)** Write a Python script using the ADK to parse the PDF and inject it into the memory bank.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Connecting an Agent Search (formerly Vertex AI Search) data store provides out-of-the-box, low-code Retrieval-Augmented Generation (RAG). The agent automatically queries the index and grounds its responses in the uploaded PDF. → Lab 03 — Enterprise Data and Multimodal.
- **Why A is incorrect**: Pasting 200 pages into system instructions consumes massive amounts of the context window, increases per-turn latency, and makes the prompt unmanageable.
- **Why C is incorrect**: A JSON schema defines data structures, not semantic tone and vocabulary rules.
- **Why D is incorrect**: Writing a custom ADK Python script violates the requirement that the solution accommodate a team with no coding experience.
</details>

---

### Question 6
**Scenario**: You are testing a low-code agent in CX Agent Studio that collects a user's address for shipping. Users often provide incomplete addresses (e.g., missing the ZIP code). 

**How do you configure the agent to repeatedly prompt the user until a complete address is collected, without writing code?**
- **A)** Set the LLM temperature to 1.0 so it creatively asks for the ZIP code in different ways.
- **B)** Define a Form parameter for the ZIP code on the Page, mark it as Required, and configure parameter-level prompt messages to ask for the missing information.
- **C)** Create a new Page for every possible combination of missing address fields.
- **D)** Enable Agent Search to look up the user's ZIP code based on their street name.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: CX Agent Studio uses **Form parameters** to handle slot-filling. By marking a parameter as Required and providing prompt messages, the agent will automatically loop and ask the user for the specific missing data until the form is complete. → Lab 02 — CX Agent Studio State.
- **Why A is incorrect**: Increasing temperature only increases randomness in generation; it does not enforce a structured data collection loop.
- **Why C is incorrect**: Creating a Page for every combination of missing fields leads to an explosion of states and an unmaintainable graph.
- **Why D is incorrect**: Agent Search retrieves documents; it cannot definitively geolocate a user based solely on an incomplete street address without a City/State.
</details>

---

### Question 7
**Scenario**: A media company wants to build a video summarization agent using Gemini Enterprise. Users will upload MP4 video files up to 30 minutes long. The agent must describe the visual events and transcribe key spoken quotes simultaneously.

**Which model and ingestion method is best suited for this low-code workflow?**
- **A)** Gemini 3.5 Transcribe to convert the audio, and Vision API to extract frames every 5 seconds.
- **B)** Gemini 3.7 Flash passing the MP4 file URI directly in the prompt for native multimodal processing.
- **C)** Gemini Omni Flash Preview, stripping the audio with ffmpeg before sending to the API.
- **D)** Gemma 4 31B IT running in a self-hosted environment to ensure the video remains private.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Gemini 3.7 Flash natively supports video ingestion directly via a Cloud Storage URI. It processes both the visual frames and the audio track concurrently within the same context window, making it perfect for describing visual events and transcribing quotes without custom preprocessing pipelines. → Lab 03 — Enterprise Data and Multimodal.
- **Why A is incorrect**: Splitting the video into separate audio transcription and frame extraction APIs destroys the temporal synchronization between what is seen and what is said.
- **Why C is incorrect**: Stripping the audio with ffmpeg would prevent the agent from transcribing key spoken quotes, failing the requirements.
- **Why D is incorrect**: Gemma models are text-in/text-out (or image-in/text-out for multimodal variants), but they do not natively process 30-minute MP4 video files with audio.
</details>

---

### Question 8
**Scenario**: A regional bank is using Agent Designer to prototype a loan assistant. The agent needs to politely decline any queries about credit scores, as the bank uses a separate system for that. 

**What is the most direct way to enforce this boundary in the low-code Agent Designer?**
- **A)** Implement an A2A protocol handoff to a separate Credit Score Agent.
- **B)** Add explicit negative constraints to the System Instructions (e.g., "Do not answer questions about credit scores. Instead, say 'Please visit the credit portal.'").
- **C)** Deploy Model Armor and configure a custom regex filter for "credit score".
- **D)** Use CX Agent Studio to build a state machine with a transition route triggered by a "credit_score" intent.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: In Agent Designer, the System Instructions are the primary mechanism for setting behavioral boundaries. Explicit negative constraints (telling the model what *not* to do and what to do instead) are highly effective for simple topical boundaries. → Lab 01 — Agent Designer Workflows.
- **Why A is incorrect**: A2A is a complex developer protocol for custom coded agents, not a feature of the low-code Agent Designer.
- **Why C is incorrect**: While Model Armor can block topics, using System Instructions is the more direct and appropriate first line of defense for conversational routing, rather than triggering a security block.
- **Why D is incorrect**: While CX Agent Studio is powerful, the question specifically asks for the most direct way *in Agent Designer*.
</details>

## Domain 2: Using Coding Agents for Application Development (~17%)

### Question 9
**Scenario**: Your engineering team is adopting Google Antigravity to build autonomous coding agents that refactor legacy Java services into Python Cloud Run microservices. The agent needs to execute shell commands, run test suites, and install dependencies, but enterprise security policy strictly prohibits agents from making unvetted outbound internet connections or accessing corporate secrets on the host machine.

**How should you configure the Antigravity execution environment?**
- **A)** Run Antigravity in Standard Sandbox Mode with GKE Sandbox (gVisor container runtime) and workspace directory boundaries.
- **B)** Grant Antigravity `BypassSandbox: true` and configure OS-level firewall iptables rules on the developer's laptop.
- **C)** Run Antigravity inside a local Docker container with root privileges and mount the entire `/Users/` directory.
- **D)** Restrict the Antigravity agent to read-only tools and manually copy-paste code suggestions into the IDE.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Standard Sandbox Mode in Antigravity enforces workspace directory confinement and disables arbitrary network calls. Combining this with GKE Sandbox (using gVisor kernel isolation) provides enterprise-grade isolation for untrusted code execution and automated testing. → Lab 05 — Secure Sandboxes.
- **Why B is incorrect**: `BypassSandbox: true` disables sandbox isolation and requires manual approval for every command, which is risky and degrades developer velocity.
- **Why C is incorrect**: Mounting `/Users/` with root privileges violates the principle of least privilege and exposes personal credentials.
- **Why D is incorrect**: Read-only mode prevents the agent from running automated refactoring and test suites autonomously.
</details>

---

### Question 10
**Scenario**: You are developing an enterprise Antigravity plugin for your cloud operations team. You want the coding agent to automatically follow Google Cloud security best practices whenever a developer opens a Terraform file (`*.tf`), but you want the Terraform linting instructions loaded into the context window *only* when Terraform files are being edited to conserve prompt tokens.

**Which customization mechanism in Antigravity should you implement?**
- **A)** Add global system instructions in `~/.gemini/config/GEMINI.md` with `always_on: true`.
- **B)** Create a custom skill in `.agents/skills/terraform-lint/SKILL.md` and define an agent rule with `trigger: model_decision` or directory pattern matching.
- **C)** Write a bash script that runs `terraform fmt` in a cron schedule using the schedule tool.
- **D)** Hardcode Terraform rules into the agent's Python SDK client configuration before each conversation turn.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Antigravity uses progressive disclosure for **Skills** and **Rules**. By creating a skill with a YAML frontmatter and scoping rules to file triggers/model decisions, Antigravity injects the full skill instructions only when relevant files are touched, preserving context window tokens and minimizing costs. → Lab 06 — Antigravity Customization.
- **Why A is incorrect**: Setting `always_on: true` in global configuration injects the rules into every turn regardless of file type, bloating token usage.
- **Why C is incorrect**: A cron schedule does not guide the agent's contextual generation during code authoring.
- **Why D is incorrect**: Hardcoding rules into client code prevents modular sharing across team repositories.
</details>

---

### Question 11
**Scenario**: A developer uses a coding agent powered by Antigravity to patch a recently discovered SQL injection vulnerability in a Go web application. The developer wants the agent to dynamically query the live staging database schema to ensure the new parameterized queries match the table structure before writing the fix. 

**How should the agent access the staging database?**
- **A)** Pass the database password in the chat window so the agent can write a temporary Go script to print the schema.
- **B)** Configure a Model Context Protocol (MCP) server for PostgreSQL and authorize the coding agent to connect to it.
- **C)** Grant the agent IAM Organization Administrator privileges so it can read all Cloud SQL instances via the Resource Manager API.
- **D)** Run the agent in `UnsafeLocalCodeExecutor` mode and allow it to download a SQL client binary from the internet.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Model Context Protocol (MCP) servers safely expose external resources (like database schemas) and tools to coding agents. It provides a standardized, permission-scoped interface without hardcoding credentials in prompts or running untrusted binaries. → Lab 04 — MCP and Tooling.
- **Why A is incorrect**: Pasting passwords into chat windows risks logging them in telemetry and prompt histories.
- **Why C is incorrect**: Organization Administrator is a massive over-permissioning violation of least privilege.
- **Why D is incorrect**: `UnsafeLocalCodeExecutor` provides zero isolation and allows arbitrary untrusted binary execution, posing a severe security risk.
</details>

---

### Question 12
**Scenario**: Your platform team is standardizing on the Agents CLI to manage custom subagents for different microservices. You have created a specialized subagent that writes unit tests for frontend React components. You want to make this subagent available to the primary coding agent.

**How do you integrate this subagent using Antigravity and the Agents CLI?**
- **A)** Register the subagent in the Agent Registry and configure the primary agent to use the Agent2Agent (A2A) protocol for handoffs.
- **B)** Place the subagent configuration in the `.agents/agents/` directory of the workspace and rely on the local Antigravity orchestrator to discover it.
- **C)** Merge the React subagent's prompt directly into the primary agent's global system prompt.
- **D)** Deploy the subagent to Cloud Run and instruct the primary agent to use `curl` to send HTTP requests to it.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: In Antigravity (a local coding agent environment), local subagents are discovered automatically by placing their configuration in the `.agents/agents/` directory. The primary agent can then dynamically invoke them as tools when needed. → Lab 06 — Antigravity Customization.
- **Why A is incorrect**: While A2A and Agent Registry are correct for cloud-deployed custom ADK agents (Section 3.3), Antigravity coding agents orchestrate local subagents via workspace directory discovery.
- **Why C is incorrect**: Merging prompts degrades performance through token bloat and violates the principle of separation of concerns (specialized subagents).
- **Why D is incorrect**: Using `curl` is a brittle, unstructured workaround compared to native subagent invocation.
</details>

---

### Question 13
**Scenario**: A developer asks the coding agent to optimize a complex Python data processing script. The script currently takes 10 minutes to run. The agent rewrites the code to use multiprocessing, but when the developer tests it, the new script crashes due to a race condition.

**What is the most effective workflow to resolve this using the coding agent?**
- **A)** Delete the conversation history, paste the crash stack trace, and ask the agent to write the script from scratch again.
- **B)** Provide the stack trace in the current conversation, ask the agent to explain the race condition, and instruct it to use the `GkeCodeExecutor` to run a test suite in an isolated sandbox.
- **C)** Switch to a weaker model like Gemini 2.5 Flash-Lite so it avoids writing overly complex multiprocessing code.
- **D)** Use the `run_command` tool to force the agent to run the script repeatedly until it works.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Coding agents excel at debugging when provided with exact stack traces in the context of the ongoing conversation. Using a secure execution sandbox (like `GkeCodeExecutor` in `job` or `sandbox` mode) allows the agent to safely run tests and iteratively verify its race-condition fix without crashing the developer's local machine. → Lab 05 — Secure Sandboxes.
- **Why A is incorrect**: Deleting conversation history destroys the context of *why* the code was written that way, making it harder for the agent to debug the specific optimization.
- **Why C is incorrect**: Multiprocessing race conditions are complex; switching to a smaller/weaker model decreases the likelihood of a correct fix.
- **Why D is incorrect**: Blindly repeating a failing script will not fix a race condition and wastes compute resources.
</details>

---

### Question 14
**Scenario**: You are configuring a fleet of coding agents for a large enterprise. The agents must have access to a proprietary internal tool that provisions cloud development environments. The tool's API changes frequently, and you want to manage the tool logic centrally rather than updating every developer's local agent configuration.

**Which technology should you use to expose this tool to the coding agents?**
- **A)** Write a bash script that curls the API, and distribute the script via Git to every developer's machine.
- **B)** Implement the tool as a Model Context Protocol (MCP) server deployed on Cloud Run, and provide the MCP server URL to the agents.
- **C)** Embed the API's OpenAPI specification directly into the Gemini model's fine-tuning dataset.
- **D)** Create an Agent Retrieval vector database containing the tool's documentation.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: MCP servers decouple tool implementation from the agent client. By deploying the tool as an MCP server on Cloud Run, the platform team manages the API integration centrally. The agents simply connect to the MCP server to dynamically discover and use the tool. → Lab 04 — MCP and Tooling.
- **Why A is incorrect**: Distributing local bash scripts is difficult to maintain, audit, and version control across a large fleet.
- **Why C is incorrect**: Fine-tuning teaches style and syntax, not dynamic tool execution. Furthermore, fine-tuning requires retraining every time the API changes.
- **Why D is incorrect**: A vector database provides documentation, but does not give the agent the actual execution capability to call the API.
</details>

---

### Question 15
**Scenario**: Your Antigravity coding agent needs to refactor an application to use the newly released Google Cloud Spanner features. The agent is hallucinating outdated Spanner syntax because the features were released after the model's training cutoff.

**How can you provide the agent with the necessary up-to-date knowledge?**
- **A)** Tell the agent to guess the new syntax based on similar database technologies.
- **B)** Provide the URL to the new Spanner documentation and use the web search or `read_url_content` tool to let the agent read the updated specs before coding.
- **C)** Wait for Google to release a new base model with an updated training cutoff.
- **D)** Switch to a localized SLM like Gemma 4 26B IT, which updates faster.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Coding agents have access to tools that allow them to overcome training cutoffs. Directing the agent to read specific, up-to-date documentation via a URL reader or web search tool grounds its generation in current facts. → Lab 06 — Antigravity Customization.
- **Why A is incorrect**: Guessing syntax leads to broken code and hallucinations.
- **Why C is incorrect**: Waiting for a new base model is impractical for day-to-day development tasks.
- **Why D is incorrect**: SLMs do not intrinsically have more recent training data than frontier SaaS models, and they generally have weaker coding capabilities.
</details>

---

### Question 16
**Scenario**: A developer is using a coding agent to parse a large 500MB JSON log file to find a specific error pattern. 

**Which approach represents the most effective use of the coding agent?**
- **A)** Instruct the agent to read the entire 500MB file into its context window and summarize the errors.
- **B)** Have the agent write a short Python script using `json` and `grep` logic to parse the file locally, run it, and analyze the output.
- **C)** Upload the 500MB file to Agent Platform Memory Bank for long-term semantic retrieval.
- **D)** Configure a Cloud Logging sink to export the logs to BigQuery and use BigQuery ML.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Coding agents are most effective when they write code to solve computational problems rather than trying to process massive datasets entirely within their prompt context. Writing a script to parse the file is fast, accurate, and cost-effective. → Lab 04 — MCP and Tooling.
- **Why A is incorrect**: A 500MB JSON file is roughly 150-200 million tokens, which vastly exceeds the 1M or 2M token limit of even the largest context windows (like Gemini 3.7 Flash).
- **Why C is incorrect**: Memory Bank is for long-term conversational memory and semantic facts, not bulk structured log analysis.
- **Why D is incorrect**: While BQ is good for logs, setting up a sink and using BQ ML is overkill for a developer trying to quickly find a pattern in a local file.
</details>

---

### Question 17
**Scenario**: You are designing a CI/CD pipeline where a coding agent automatically reviews pull requests. The agent needs to execute the PR's code to run the test suite. 

**Which ADK CodeExecutor provides the strongest isolation for executing untrusted PR code?**
- **A)** `BuiltInCodeExecutor` running on the CI/CD runner.
- **B)** `UnsafeLocalCodeExecutor` running as a background task.
- **C)** `GkeCodeExecutor` running in `sandbox` mode with gVisor.
- **D)** `ContainerCodeExecutor` using standard Docker containers.

<details><summary>Show answer</summary>

**Correct Answer: C**
**Explanation**:
- **Why C is correct**: The `GkeCodeExecutor` in `sandbox` mode provisions pods using GKE Sandbox (gVisor). gVisor intercepts syscalls to the host kernel, providing a strong security boundary ideal for untrusted, potentially malicious PR code. → Lab 05 — Secure Sandboxes.
- **Why A is incorrect**: `BuiltInCodeExecutor` runs in the same process/environment as the agent, providing no isolation and risking CI/CD runner compromise.
- **Why B is incorrect**: `UnsafeLocalCodeExecutor` explicitly provides no isolation.
- **Why D is incorrect**: Standard Docker containers share the host kernel and are vulnerable to container escape exploits from untrusted code.
</details>

---

### Question 18
**Scenario**: Your team is building a complex application with multiple inter-dependent components. You want the coding agent to plan its approach before writing code, ensuring it doesn't get stuck in a dead-end implementation.

**How should you configure the agent's behavior?**
- **A)** Limit the `max_tokens` output to force the agent to write shorter, simpler code.
- **B)** Instruct the agent to create a markdown artifact (e.g., `design_doc.md`) outlining the architecture and steps before implementing any code.
- **C)** Disable all tools so the agent focuses entirely on writing code.
- **D)** Use a `LoopAgent` to continuously rewrite the code until it compiles.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Forcing the agent to write a plan or design document artifact first leverages Chain-of-Thought reasoning. It allows the agent (and the human user) to review the architectural approach before committing tokens and time to implementation. → Lab 06 — Antigravity Customization.
- **Why A is incorrect**: Limiting tokens just truncates the output; it doesn't improve planning.
- **Why C is incorrect**: Disabling tools removes the agent's ability to read existing files or test its code.
- **Why D is incorrect**: A `LoopAgent` rewriting code blindly without a plan will quickly exhaust resources and likely fail.
</details>

## Domain 3: Developing Custom Agents (~33%)

### Question 19
**Scenario**: You are architecting a real-time financial trading assistant using the Agent Development Kit (ADK). The agent must analyze market feeds, detect trading signals, and propose calls to an internal REST API. The system requires low latency and machine-validated API parameter shapes; application code will independently enforce business rules, authorization, and human approval.

**Which model and parameter configuration should you select?**
- **A)** Gemini 2.5 Pro with a static thinking budget of 32,000 tokens and zero temperature.
- **B)** Gemini 3.7 Flash configured with dynamic thinking budget (1,024 to 2,048 tokens) and strict Pydantic structured output schemas (`response_schema`).
- **C)** Gemma 4 26B IT deployed on an edge Cloud Run instance without function calling tools.
- **D)** Gemini 3.5 Flash-Lite with thinking mode disabled and unstructured natural language output.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: A latency-oriented tool-capable model with a bounded thinking budget and a Pydantic `response_schema` is the best fit among these choices. The schema validates structure and types; it does not guarantee factual correctness or authorize a trade. → Lab 07 — Model Selection.
- **Why A is incorrect**: Gemini 2.5 Pro with a 32K thinking budget will incur multi-second latencies, violating the 1.5-second SLA.
- **Why C is incorrect**: Gemma models lack the complex multi-step reasoning and function calling reliability required for financial trading operations compared to Gemini Flash.
- **Why D is incorrect**: Disabling thinking and using unstructured text will lead to hallucinated parameters and unreliable tool execution.
</details>

---

### Question 20
**Scenario**: An autonomous customer support agent built with the ADK interacts with enterprise users over multiple weeks. The agent needs to recall user preferences (e.g., preferred billing currency, communication language, past ticket resolutions) across completely different chat sessions, but recent chat turns must not be cluttered with thousands of irrelevant past messages.

**Which memory architecture on Google Cloud should you deploy?**
- **A)** Store all raw message histories in a single Firestore document and append the entire history to the system prompt on every turn.
- **B)** Deploy **Agent Platform Memory Bank** to automatically extract semantic memories and facts, combined with a **Managed Session** store for short-term working context pruning.
- **C)** Keep conversation history in local Python process memory using a global dictionary.
- **D)** Configure a Redis cache that purges all keys every 24 hours using TTL expiration.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: **Agent Platform Memory Bank** (`VertexAiMemoryBankService`) provides long-term associative memory. It analyzes past turns, extracts salient facts/preferences, indexes them into a semantic store, and injects only relevant memories when queried. Managed Sessions (`VertexAiSessionService`) handle short-term conversational context with automatic sliding-window pruning. → Lab 09 — Sessions and Memory.
- **Why A is incorrect**: Appending raw history to the system prompt will rapidly exceed context token limits, increase latency, and inflate costs.
- **Why C is incorrect**: In-memory global state is lost on process restarts and fails when scaling horizontally across multiple container instances.
- **Why D is incorrect**: Purging Redis keys after 24 hours destroys long-term user preferences across multi-week interactions.
</details>

---

### Question 21
**Scenario**: You need to connect an ADK-based agent to enterprise BigQuery analytics and Cloud SQL PostgreSQL databases. The agent must discover available schemas dynamically, generate valid SQL queries, execute them safely, and handle query syntax errors automatically without writing custom integration code for every database.

**Which approach should you use?**
- **A)** Hardcode database connection strings in the agent's system prompt and instruct the LLM to output bash commands using `psql` and `bq`.
- **B)** Deploy **Google Cloud MCP Toolbox for Databases** as Model Context Protocol (MCP) servers and register them in the agent's MCP client configuration using `MCPToolset`.
- **C)** Export all database tables to static CSV files in Cloud Storage every hour and query them using Agent Search.
- **D)** Write custom Python functions for every SQL query variation and register them as static `FunctionTool` objects.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: **Google Cloud MCP Servers** expose supported databases to agents through MCP with reusable tool definitions and database integration patterns. Using `MCPToolset` in the ADK seamlessly integrates these external tools. → Lab 10 — Tools and Skills.
- **Why A is incorrect**: Exposing connection strings and running raw shell commands is a severe security vulnerability.
- **Why C is incorrect**: Static CSV exports provide stale data and do not support dynamic real-time querying.
- **Why D is incorrect**: Authoring custom functions for every query variation is unmaintainable and prevents dynamic query generation.
</details>

---

### Question 22
**Scenario**: You are designing a complex multi-agent system for a logistics company using the ADK. The system consists of an Order Ingestion Agent, a Route Optimization Agent, and a Fleet Dispatch Agent. When an order arrives, the Route Optimization Agent and Fleet Dispatch Agent must collaborate, negotiate constraints across multiple turns, and hand off execution state statefully across different Kubernetes clusters.

**Which multi-agent protocol and orchestration pattern should you select?**
- **A)** Implement the **Agent2Agent (A2A)** protocol managed via Agent Registry and Agent Identity.
- **B)** Chain the agents into a rigid linear bash script that passes JSON files via local filesystem storage.
- **C)** Use a single ADK `SequentialAgent` to run all three prompts in a deterministic order in one process.
- **D)** Use Google Cloud Pub/Sub with broadcast fan-out where all agents execute independently without state handoffs or coordination.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: The **Agent2Agent (A2A)** protocol enables decentralized autonomous agents to discover capabilities, exchange messages, and hand off execution state across network boundaries. It is designed precisely for multi-turn negotiation between independently deployed agents. → Lab 12 — Multi-agent and A2A.
- **Why B is incorrect**: Bash scripts passing local files cannot scale across distributed cloud environments or support dynamic multi-turn agent negotiations.
- **Why C is incorrect**: A `SequentialAgent` runs in a single process and enforces a rigid, deterministic order. It cannot handle multi-turn negotiation or cross-cluster deployment.
- **Why D is incorrect**: Uncoordinated Pub/Sub broadcasting lacks stateful handoff and negotiation semantics.
</details>

---

### Question 23
**Scenario**: You are building an internal HR agent that answers policy questions. The company wants to run the agent entirely within their Virtual Private Cloud (VPC) with zero data leaving the network, even to Google APIs. Cost is highly constrained, and the agent only needs to answer simple factual questions from an internal wiki.

**Which model architecture should you select?**
- **A)** Gemini 3.8 Flash accessed via the Vertex AI API over the public internet.
- **B)** A self-hosted **Gemma 4 31B IT** model deployed on a GKE cluster within the VPC using vLLM or Ollama.
- **C)** Gemini 2.5 Pro fine-tuned using Model Garden.
- **D)** An ADK `FallbackModel` configured to route all traffic to a third-party SaaS provider.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Deploying a self-hosted open model like Gemma 4 ensures zero data egress from the VPC, meeting the strict data residency and network isolation requirement. For simple factual RAG tasks, Gemma 4 is highly capable and avoids SaaS API costs. → Lab 07 — Model Selection.
- **Why A is incorrect**: Calling Vertex AI APIs requires data to leave the VPC to hit the Google control plane (even with Private Service Connect, data is processed by Google's SaaS).
- **Why C is incorrect**: Gemini 2.5 Pro is a SaaS model; fine-tuning it does not bring the model weights inside the VPC.
- **Why D is incorrect**: Routing traffic to a third-party SaaS provider violates the strict "zero data leaving the network" requirement.
</details>

---

### Question 24
**Scenario**: You are developing an ADK workflow for a data extraction pipeline. Step 1 extracts text from a PDF. Step 2 translates it. Step 3 summarizes it. These steps must happen in an exact, guaranteed order every time, without relying on the LLM to decide which tool to call next.

**Which ADK orchestration component should you use?**
- **A)** A single `LlmAgent` with all three tools provided in the `tools` list.
- **B)** An ADK **graph `Workflow`** defining `Node` instances for each step and deterministic `Edge` connections between them.
- **C)** The Agent2Agent (A2A) protocol with a broadcast message.
- **D)** A `LoopAgent` with a `max_iterations` of 3.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: An ADK graph `Workflow` (or `SequentialAgent`) executes nodes in a rigid, deterministic order defined by edges. It explicitly removes control flow decisions from the LLM, guaranteeing the pipeline runs Step 1 -> Step 2 -> Step 3. → Lab 12 — Multi-agent and A2A.
- **Why A is incorrect**: Giving an `LlmAgent` tools relies on the model to decide the order (agentic routing), which is probabilistic and not guaranteed.
- **Why C is incorrect**: A2A is for decentralized agent communication, not for enforcing strict in-process deterministic pipelines.
- **Why D is incorrect**: A `LoopAgent` iterates a single agent's reasoning loop; it does not enforce a three-step sequential pipeline of different tasks.
</details>

---

### Question 25
**Scenario**: You are configuring a RAG pipeline for an ADK agent using `VertexAiRagMemoryService`. The agent needs to search a massive corpus of 10 million legal documents. Initial testing shows the retrieval system is returning documents that share keywords but are semantically unrelated to the legal concepts in the user's query.

**Which configuration change to the vector retrieval system will best solve this?**
- **A)** Switch the embedding model from `gemini-embedding-2` to `gemini-embedding-001`.
- **B)** Increase the top-K retrieval limit from 10 to 1,000 to give the LLM more context.
- **C)** Implement a **reranker** (like Vertex AI Ranking) to re-score the top vector matches based on deep semantic relevance before passing them to the agent.
- **D)** Replace Vector Search with a standard SQL `LIKE` query on a Cloud SQL database.

<details><summary>Show answer</summary>

**Correct Answer: C**
**Explanation**:
- **Why C is correct**: A common RAG failure is that fast vector similarity (like dot product) captures broad similarity but misses nuanced semantic relevance. A reranker takes the top-K fast results and scores them with a heavier, more precise cross-encoder model, drastically improving the quality of the final context. → Lab 11 — RAG and Retrieval.
- **Why A is incorrect**: `gemini-embedding-001` is a legacy model with a smaller input limit and worse performance than `gemini-embedding-2`.
- **Why B is incorrect**: Passing 1,000 documents into the LLM context window will cause massive latency, high token costs, and likely trigger "lost in the middle" hallucinations.
- **Why D is incorrect**: Standard SQL `LIKE` queries only do exact keyword matching, which is even worse at semantic concept matching than vector search.
</details>

---

### Question 26
**Scenario**: You want to share a custom capability—querying a proprietary internal ticketing system—across several different ADK agents built by different teams. You want teams to discover this capability dynamically and understand its expected inputs and outputs without reading source code.

**Which Google Cloud component should you use to publish this capability?**
- **A)** Save a Python script to a shared Google Drive folder.
- **B)** Package it using `Frontmatter` and publish it to the **Skill Registry** (`GCPSkillRegistry`).
- **C)** Hardcode the tool logic into an ADK `BasePlugin` and require all teams to import it.
- **D)** Deploy it to Cloud Run and share the IP address in a Slack channel.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The **Skill Registry** (accessed via `GCPSkillRegistry` in the ADK) is the discovery and governance plane for agent capabilities. By packaging the tool with `Frontmatter` (name, description, schema), other agents can use `search_skills()` or `search_tool_description()` to dynamically discover and integrate it. → Lab 10 — Tools and Skills.
- **Why A is incorrect**: A shared Drive folder provides no programmatic API for dynamic discovery or schema validation.
- **Why C is incorrect**: Hardcoding into a plugin requires code duplication and tight coupling, defeating dynamic discovery.
- **Why D is incorrect**: Sharing an IP in Slack is an unmanaged, un-discoverable anti-pattern for enterprise capability sharing.
</details>

### Question 27
**Scenario**: An ADK agent needs to interact with an external API that is known to be flaky, frequently returning HTTP 503 errors. If the tool call fails, the agent usually apologizes and gives up immediately, frustrating users.

**How can you configure the ADK to handle these transient tool failures automatically without changing the agent's core instructions?**
- **A)** Add a `while True:` loop inside the agent's system prompt.
- **B)** Wrap the tool in a `LongRunningFunctionTool`.
- **C)** Apply the `ReflectAndRetryToolPlugin` to the agent, which automatically catches errors and prompts the model to retry the tool call.
- **D)** Switch to a model with a larger thinking budget.

<details><summary>Show answer</summary>

**Correct Answer: C**
**Explanation**:
- **Why C is correct**: The `ReflectAndRetryToolPlugin` is a built-in ADK mechanism that intercepts tool execution errors. Instead of failing immediately, it feeds the error back to the LLM (reflection) and allows it to retry the tool call, perfect for handling flaky APIs or syntax errors. → Lab 08 — ADK Fundamentals.
- **Why A is incorrect**: System prompts cannot execute code loops; the LLM cannot enforce a `while True` behavior reliably.
- **Why B is incorrect**: `LongRunningFunctionTool` is for asynchronous background tasks, not for automatically retrying failed synchronous API calls.
- **Why D is incorrect**: A larger thinking budget helps with complex reasoning, but does not intercept tool execution exceptions in the ADK runtime.
</details>

---

### Question 28
**Scenario**: You are deploying a multi-agent system where a customer-facing `GreeterAgent` collects user requirements and then transfers control to a `BookingAgent`. Both agents are deployed within the same Python application using the ADK.

**What is the simplest way to implement this handoff in the ADK?**
- **A)** Use the Agent2Agent (A2A) gRPC protocol.
- **B)** Provide the `BookingAgent` in the `sub_agents` list of the `GreeterAgent`, allowing it to use the `transfer_to_agent` tool automatically.
- **C)** Setup a Pub/Sub topic and have the `GreeterAgent` publish a message that the `BookingAgent` subscribes to.
- **D)** Write the `GreeterAgent` state to a Cloud SQL database and run a cron job to wake up the `BookingAgent`.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: For agents running in the *same process*, simply adding the target agent to the `sub_agents` list of the parent `LlmAgent` automatically provisions the `transfer_to_agent` tool. This is the simplest and most native way to handle in-process agent handoffs. → Lab 12 — Multi-agent and A2A.
- **Why A is incorrect**: A2A is a complex protocol designed for cross-network, decentralized agent communication. It is overkill for agents running in the same Python application.
- **Why C is incorrect**: Pub/Sub introduces unnecessary asynchronous infrastructure for a simple in-process synchronous handoff.
- **Why D is incorrect**: Cron jobs and database polling are massive anti-patterns for real-time conversational agent handoffs.
</details>

---

### Question 29
**Scenario**: You are building an agent that needs to authenticate to a third-party SaaS provider (e.g., Salesforce) on behalf of the specific human user interacting with the agent. The agent should only be able to access data the human user has permission to see in Salesforce.

**Which authentication mechanism should you implement in the ADK?**
- **A)** Hardcode a Salesforce Admin API key in the ADK `ToolContext`.
- **B)** Use the **Auth Manager (OAuth 2.0)** module (`OAuth2Auth`) to perform a 3-legged OAuth flow, capturing the user's specific access token to pass to the tool.
- **C)** Use Agent Identity to issue a Google Cloud Service Account credential to the agent.
- **D)** Use a `GcpAuthProvider` to assert a Principal Access Boundary.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: When an agent must act on behalf of a *specific human user* in a third-party system, 3-legged OAuth 2.0 is required. The ADK's Auth Manager handles token exchange and refresh, ensuring the agent's tool calls are executed with the human's exact permission scope. → Lab 16 — Agent Identity and Auth.
- **Why A is incorrect**: Hardcoding an Admin API key grants the agent global access, violating least privilege and bypassing user-specific authorization.
- **Why C is incorrect**: A Google Cloud Service Account identifies the *agent* to Google Cloud resources, not the human user to a third-party SaaS provider.
- **Why D is incorrect**: A PAB restricts Google Cloud resource access; it does not authenticate users to Salesforce.
</details>

---

### Question 30
**Scenario**: You are designing a RAG system using `gemini-embedding-2`. The documents you are embedding are 50-page technical manuals. You decide to embed each entire 50-page manual as a single vector. During testing, the agent fails to answer specific technical questions accurately.

**What is the architectural flaw in this RAG design?**
- **A)** The embedding model does not support technical jargon.
- **B)** `gemini-embedding-2` has an input limit of 8,192 tokens; a 50-page manual exceeds this, causing truncation and loss of information.
- **C)** You should have used `gemini-embedding-001` instead.
- **D)** The agent needs a larger `response_schema` to hold the answer.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: `gemini-embedding-2` has a maximum input limit of 8,192 tokens. A 50-page manual is roughly 25,000+ tokens. The embedding API will truncate the text, meaning everything past the first few pages is completely ignored and unsearchable. You must implement a **chunking strategy** (e.g., semantic chunking or fixed-size overlapping chunks). → Lab 11 — RAG and Retrieval.
- **Why A is incorrect**: Embedding models handle technical jargon well; the issue is the input length limit.
- **Why C is incorrect**: `gemini-embedding-001` is a stale model identifier and does not solve the fundamental lack of a chunking strategy.
- **Why D is incorrect**: The `response_schema` dictates the output format, not the retrieval quality or embedding limits.
</details>

---

### Question 31
**Scenario**: You need to integrate an open-source LangChain tool into your ADK workflow. You don't want to rewrite the tool from scratch using ADK's `FunctionTool`.

**How does the ADK support this requirement?**
- **A)** You cannot use LangChain tools in ADK; you must rewrite them.
- **B)** Use the `google.adk.integrations.langchain` module to wrap the LangChain tool so it conforms to the ADK `BaseTool` interface.
- **C)** Run the LangChain tool in a separate Docker container and use A2A to communicate with it.
- **D)** Inject the LangChain Python source code directly into the LLM's system prompt.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The ADK provides built-in integration modules (`integrations.langchain`, `integrations.crewai`) that act as adapters, allowing you to seamlessly use tools developed for other popular open-source frameworks within an ADK agent. → Lab 10 — Tools and Skills.
- **Why A is incorrect**: The ADK explicitly provides integration adapters; rewriting is not necessary.
- **Why C is incorrect**: Running it in a separate container with A2A is massively over-engineered for a simple tool integration.
- **Why D is incorrect**: Injecting source code does not execute the tool; it just wastes context tokens.
</details>

---

### Question 32
**Scenario**: You are configuring a fallback mechanism for an ADK agent that normally relies on Gemini 3.7 Flash. If the Google Cloud API experiences a regional outage, the agent must automatically degrade gracefully and use a local SLM (Gemma 3 Ollama) to answer the user, albeit with lower quality.

**Which ADK class provides this functionality?**
- **A)** `ReflectAndRetryModelPlugin`
- **B)** `FallbackModel`
- **C)** `LlmCapabilities`
- **D)** `ManagedAgent`

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The `FallbackModel` class in `google.adk.models` allows you to define a primary model (Gemini) and one or more secondary models (e.g., local Gemma). If the primary model raises an exception (like an API outage or rate limit), the ADK automatically routes the request to the fallback model. → Lab 07 — Model Selection.
- **Why A is incorrect**: `ReflectAndRetryModelPlugin` asks the *same* model to try generating again; it does not route traffic to a *different* model during an outage.
- **Why C is incorrect**: `LlmCapabilities` is a metadata class describing what a model can do (e.g., function calling), not a routing mechanism.
- **Why D is incorrect**: `ManagedAgent` interacts with the server-side Managed Agents API, not local model failover logic.
</details>

---

### Question 33
**Scenario**: You want your ADK agent to perform a Google Search to answer a user's question about recent news, but you want to ensure the agent's response is explicitly grounded in the search results with citations provided by Google's backend.

**Which ADK tool should you provision to the agent?**
- **A)** `google_search` tool
- **B)** `google_maps_grounding` tool
- **C)** `enterprise_web_search` tool
- **D)** Write a custom web scraper using BeautifulSoup.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: The built-in `google_search` tool connects to Google's Grounding service. It performs the search and provides the LLM with verified facts and citation metadata, ensuring the response is grounded in real-time web results. → Lab 10 — Tools and Skills.
- **Why B is incorrect**: `google_maps_grounding` is for location and places data, not general news.
- **Why C is incorrect**: `enterprise_web_search` is for searching internal company intranets (Vertex AI Search for Web), not the public Google Search index for recent news.
- **Why D is incorrect**: A custom scraper does not provide native citation grounding and is brittle compared to the managed Google Search tool.
</details>

---

### Question 34
**Scenario**: You are developing an agent that handles highly sensitive data. You want to capture telemetry (traces and spans) to monitor latency and tool execution using `google.adk.telemetry`, but you must ensure that no user prompts or LLM generated text are ever sent to Cloud Trace.

**How do you configure the ADK Telemetry module?**
- **A)** Disable telemetry entirely using `adk telemetry disable`.
- **B)** Set `ContentCapturingMode` to a mode that excludes payloads (e.g., metadata only) in the `TelemetryConfig`.
- **C)** Run a regex replace on the Cloud Trace dashboard to mask the data after it is uploaded.
- **D)** Use `UnsafeLocalCodeExecutor` to bypass telemetry hooks.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The ADK `TelemetryConfig` uses `ContentCapturingMode` to control exactly what is recorded in spans. By setting it to exclude content/payloads, you retain structural metrics (latency, tool invocation counts, routing) without leaking sensitive prompt/response data to the observability backend. → Lab 15 — Observability and Troubleshooting.
- **Why A is incorrect**: Disabling telemetry entirely blinds you to performance bottlenecks and system failures, which is unacceptable for production monitoring.
- **Why C is incorrect**: Masking data on the dashboard means the sensitive data was already transmitted and stored in Cloud Trace, which is a compliance violation.
- **Why D is incorrect**: `UnsafeLocalCodeExecutor` is for code execution sandboxing, not telemetry configuration.
</details>

---

### Question 35
**Scenario**: A custom agent built with ADK needs to plan a 5-day vacation itinerary. It needs to search for flights, then search for hotels based on the flight dates, and finally suggest activities. 

**Which agent architecture is most appropriate for handling this multi-step interdependent task?**
- **A)** A single `LlmAgent` with a `BuiltInPlanner` or `PlanReActPlanner` configured.
- **B)** A `ParallelAgent` that runs the flight, hotel, and activity searches simultaneously.
- **C)** An Agent Registry search query.
- **D)** A `FallbackModel` implementation.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: The ADK provides Planners (`BuiltInPlanner`, `PlanReActPlanner`) that force an agent to decompose a complex goal into a sequence of dependent steps, execute them one by one, and adjust the plan if a step fails. This is ideal for a task where step 2 (hotels) strictly depends on the output of step 1 (flights). → Lab 08 — ADK Fundamentals.
- **Why B is incorrect**: A `ParallelAgent` executes tasks concurrently. You cannot search for hotels based on flight dates if you haven't booked the flights yet; they are interdependent, not parallelizable.
- **Why C is incorrect**: Agent Registry is for discovering capabilities, not executing reasoning plans.
- **Why D is incorrect**: `FallbackModel` is for high availability API routing, not task planning.
</details>

---

### Question 36
**Scenario**: You want to deploy an ADK agent that receives asynchronous events from a Cloud Storage bucket whenever a new PDF is uploaded, processes the PDF, and sends an email. The agent does not need a synchronous chat interface.

**Which ADK integration is designed for this event-driven architecture?**
- **A)** `google.adk.integrations.redis`
- **B)** `google.adk.integrations.eventarc` (using `EventarcToolset` and `CloudEventAttributesBinding`)
- **C)** `google.adk.sessions.VertexAiSessionService`
- **D)** `google.adk.integrations.model_armor`

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The `eventarc` integration allows ADK agents to consume standard CloudEvents. An `EventarcToolset` can map incoming asynchronous triggers (like a GCS file upload) directly to agent invocations, enabling fully event-driven, background agent workflows. → Lab 12 — Multi-agent and A2A.
- **Why A is incorrect**: Redis is a state store for sessions, not an event-triggering bus.
- **Why C is incorrect**: Managed sessions are for multi-turn conversational memory, not event routing.
- **Why D is incorrect**: Model Armor is a security scanning service for prompt injection and DLP, not an event trigger.
</details>

### Question 37
**Scenario**: You are using ADK to build an agent that analyzes PDF invoices and cross-references them with unstructured vendor emails.

**Which model provides the highest context window (over 1M tokens) combined with native multimodal processing capabilities?**
- **A)** Gemini 2.5 Pro
- **B)** Gemini 3.8 Flash
- **C)** Gemma 4 31B IT
- **D)** `gemini-embedding-2`

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Gemini 3.8 Flash (and 3.7 Flash) supports a massive 1,048,576 token context window and natively processes PDFs and images (multimodal). → Lab 07 — Model Selection.
- **Why A is incorrect**: While Gemini 2.5 Pro has a large context window, Gemini 3.8 Flash represents the latest generation verified available for high-capacity multimodal tasks in this environment.
- **Why C is incorrect**: Gemma models are open-weights with smaller context windows (e.g., 262k) and are generally text-focused.
- **Why D is incorrect**: This is an embedding model, not a generative model.
</details>

---

### Question 38
**Scenario**: You want to execute a Python script dynamically generated by an ADK agent using `CloudRunSandboxCodeExecutor`. 

**Which parameter must be configured to ensure the container is stateless and cleans up after each turn?**
- **A)** Set `stateful=False`.
- **B)** Define `timeout_seconds=0`.
- **C)** Disable `allow_egress`.
- **D)** Use `AgentEngineSandboxCodeExecutor` instead.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: The `CloudRunSandboxCodeExecutor` provides a `stateful` boolean parameter. Setting `stateful=False` ensures the execution environment is destroyed/reset between runs, maintaining a clean slate. → Lab 14 — Deployment Runtimes.
- **Why B is incorrect**: Setting a timeout to 0 would immediately kill the execution.
- **Why C is incorrect**: Egress controls network access, not statefulness.
- **Why D is incorrect**: This is a completely different executor meant for the Agent Runtime, not Cloud Run.
</details>

## Domain 4: Evaluating and Deploying Agentic Workflows (~22%)

### Question 39
**Scenario**: Before promoting a new customer service agent to production, your team needs to evaluate its performance against 500 historical customer interactions. The evaluation must verify: (1) Did the agent select the right refund tool? (2) Were the generated refund parameters exact? (3) Was the agent's explanation faithful to company policy?

**What is the recommended evaluation architecture on Google Cloud?**
- **A)** Have senior customer support agents manually read all 500 conversation transcripts in Google Cloud Logging.
- **B)** Use **ADK evaluation tooling (`AgentEvaluator`)** with a curated **Eval Set** and deploy an **Agent Platform Gen AI Autorater (e.g., using Gemini 3.7 Flash)** to score tool precision and answer faithfulness automatically.
- **C)** Compute traditional BLEU and ROUGE scores against human reference responses.
- **D)** Run simple Python unit tests verifying that the agent returns HTTP 200 OK status codes.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: ADK `AgentEvaluator` combined with Eval Sets and LLM-as-a-judge autoraters provides multi-dimensional, automated evaluation. It measures tool selection accuracy (`multi_turn_tool_use_quality_evaluator`), trajectory quality, and factual faithfulness against ground truth. → Lab 13 — Agent Evaluation.
- **Why A is incorrect**: Manual review of 500 multi-turn transcripts is slow, expensive, and cannot be integrated into automated CI/CD pipelines.
- **Why C is incorrect**: BLEU and ROUGE measure n-gram lexical overlap, which fails completely for evaluating tool calls, multi-turn reasoning, or semantic correctness.
- **Why D is incorrect**: HTTP 200 OK only verifies server availability, not agent reasoning accuracy or tool correctness.
</details>

---

### Question 40
**Scenario**: In production, your monitoring dashboard alerts you that an autonomous research agent is occasionally getting trapped in an infinite reasoning loop, making 40+ consecutive web search tool calls with slightly varied keywords when researching obscure topics, leading to high latency and cost spikes.

**Which set of mitigations should you implement?**
- **A)** Disable the web search tool entirely and rely solely on the LLM's internal pre-trained weights.
- **B)** Configure a strict `max_iterations` execution budget (if using a LoopAgent) and implement a `before_tool_callback` interceptor hook in the ADK agent to detect duplicate queries and inject a reflection prompt.
- **C)** Increase the Cloud Run container memory and CPU limits to allow the agent to execute indefinitely.
- **D)** Switch the model to Gemini 2.5 Flash-Lite to reduce token costs during the infinite loops.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Preventing agent reasoning loops requires multi-layer defense: setting a hard turn limit (`max_iterations`) and implementing lifecycle hooks (`before_tool_callback`) to detect repetitive/stagnant tool calls, dynamically steering the agent to summarize findings or ask for clarification. → Lab 15 — Observability and Troubleshooting.
- **Why A is incorrect**: Disabling search removes the core research capability of the agent.
- **Why C is incorrect**: Increasing compute limits worsens cost spikes and does not solve the algorithmic logic loop.
- **Why D is incorrect**: Switching models does not solve the loop condition and degrades research quality.
</details>

---

### Question 41
**Scenario**: You are deploying a simple, stateless Q&A agent built with the ADK. The workload expects highly variable traffic (from 0 requests at night to 10,000 requests per minute during a marketing push). The team has limited DevOps experience and wants to minimize infrastructure management and costs during idle periods.

**Which deployment runtime should you select?**
- **A)** Google Kubernetes Engine (GKE) standard cluster with manual node provisioning.
- **B)** Cloud Run, deployed via `adk deploy cloud_run`.
- **C)** Compute Engine virtual machines with static IP addresses.
- **D)** Agent Runtime.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Cloud Run is a fully managed serverless platform that scales to zero during idle periods (saving costs) and scales up rapidly to handle traffic spikes. It is ideal for stateless workloads and requires minimal DevOps expertise. The `adk deploy cloud_run` command makes this trivial. → Lab 14 — Deployment Runtimes.
- **Why A is incorrect**: GKE standard requires managing nodes, control planes, and networking, which demands high DevOps expertise and incurs baseline costs even at zero traffic.
- **Why C is incorrect**: Static VMs do not scale dynamically and charge for 24/7 uptime regardless of traffic.
- **Why D is incorrect**: While Agent Runtime (`adk deploy agent_engine`) is an option, Cloud Run is explicitly the most established choice for stateless, scale-to-zero HTTP web application deployments with minimal overhead.
</details>

---

### Question 42
**Scenario**: You are using `adk eval` to test a new version of your agent. The test suite uses the `rubric_based_final_response_quality_v1` metric. The agent scores highly on the final response, but production users complain that the agent takes too long to answer.

**What is the likely cause of this discrepancy, and which evaluation metric should you add?**
- **A)** The model is hallucinating; you should add `hallucinations_v1`.
- **B)** The agent is executing an inefficient sequence of tool calls before reaching the right answer; you should add `trajectory_evaluator` or `multi_turn_tool_use_quality_evaluator` to analyze the intermediate steps.
- **C)** The deployment runtime is under-provisioned; you should add a security evaluator.
- **D)** The users are asking too many questions; you should add `multi_turn_task_success_evaluator`.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Final-response scoring only checks if the final answer is correct. It ignores *how* the agent got there. If an agent makes 10 confused, failed tool calls before finally getting the answer on the 11th try, the final response gets an A+, but latency is terrible. Trajectory and tool-use evaluators analyze the efficiency and correctness of the intermediate steps. → Lab 13 — Agent Evaluation.
- **Why A is incorrect**: The prompt says the agent scores highly on response quality, meaning it is likely not hallucinating the final answer.
- **Why C is incorrect**: Under-provisioning is an infrastructure issue, not something solved by a security LLM evaluator.
- **Why D is incorrect**: Task success still measures the final outcome, not the latency-inducing inefficient path taken to get there.
</details>

---

### Question 43
**Scenario**: A team is promoting a RAG agent after it passes response-style reviews. In production, users report that answers are fluent but cite irrelevant documents. 

**Which two changes most directly address the release failure? (Select TWO)**
- **A)** Add retrieval relevance/groundedness cases to a golden dataset and gate releases on them.
- **B)** Increase Cloud Run CPU so the model can write longer answers.
- **C)** Trace retrieval candidates, similarity scores, reranking, citations, and end-to-end latency using `adk telemetry`.
- **D)** Replace all human-authored questions in the test set with synthetic easy questions.
- **E)** Disable citations because users find them distracting.

<details><summary>Show answer</summary>

**Correct Answers: A and C**
**Explanation**: 
- **Why A and C are correct**: The failure is retrieval quality, not prose style or compute. A representative golden set makes it testable (`A`); telemetry traces (`C`) identify whether candidate generation, filters, reranking, or latency caused the miss. → Lab 15 — Observability and Troubleshooting.
- **Why B is incorrect**: CPU limits do not affect the semantic relevance of vector retrieval.
- **Why D is incorrect**: Synthetic easy questions will artificially inflate test scores and hide the production failure.
- **Why E is incorrect**: Disabling citations hides the symptom but doesn't fix the underlying retrieval failure.
</details>

---

### Question 44
**Scenario**: An enterprise needs to deploy an ADK agent that orchestrates highly sensitive proprietary workloads. The deployment environment must support custom Kubernetes networking policies, sidecar proxies for mutual TLS (mTLS), and dedicated node pools equipped with specific GPU hardware accelerators.

**Which deployment runtime must you select?**
- **A)** Cloud Run
- **B)** Google Kubernetes Engine (GKE) via `adk deploy gke`
- **C)** Agent Runtime
- **D)** App Engine Standard

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: GKE provides total control over the Kubernetes control plane. It is required when you need custom network policies (Calico), Istio/Envoy sidecars for mTLS, and custom hardware scheduling (specific GPU node pools). → Lab 14 — Deployment Runtimes.
- **Why A is incorrect**: Cloud Run abstracts away the network and node layers; you cannot deploy custom sidecars for mTLS or specify node pool topologies.
- **Why C is incorrect**: Agent Runtime is a managed service that does not expose underlying Kubernetes cluster configurations to the user.
- **Why D is incorrect**: App Engine Standard runs in a highly restricted sandbox and does not support custom Kubernetes networking or GPUs.
</details>

---

### Question 45
**Scenario**: You are using the GEPA optimizer (`adk optimize`) to improve the system instructions of an agent that frequently fails to extract JSON from unstructured text. 

**How does the `gepa_root_agent_prompt_optimizer` function?**
- **A)** It uses gradient descent to adjust the internal weights of the Gemini model.
- **B)** It iteratively proposes changes to the agent's system prompt, evaluates the new prompt against a provided local eval set, and keeps the prompt that yields the highest score.
- **C)** It automatically upgrades your subscription to a more expensive API tier.
- **D)** It converts Python code into optimized C++ binaries.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: DSPy/GEPA optimizers work at the prompt level. They use a "teacher" LLM to propose variations of the system instructions, test those variations against an evaluation dataset (`local_eval_sampler`), and algorithmically select the prompt that maximizes the evaluation metric. → Lab 13 — Agent Evaluation.
- **Why A is incorrect**: This describes fine-tuning or pre-training, not prompt optimization. ADK optimizes the prompt text, not the model weights.
- **Why C is incorrect**: Optimizers do not alter billing or API tiers.
- **Why D is incorrect**: It optimizes LLM instructions, not compiled code.
</details>

---

### Question 46
**Scenario**: Your ADK agent uses the `BigQueryToolset` to run analytical queries. Users are complaining about unpredictable latency: sometimes answers take 2 seconds, sometimes 30 seconds. 

**How should you use Google Cloud Observability to troubleshoot this issue?**
- **A)** Check the Cloud Run CPU utilization graph.
- **B)** Enable ADK telemetry (`adk telemetry enable`) and use **Cloud Trace** to examine the distributed spans. You can pinpoint exactly whether the latency is in the LLM generation phase (`trace_call_llm`), the tool invocation phase (`trace_tool_call`), or the BigQuery execution backend.
- **C)** Review IAM audit logs to see if permissions are changing dynamically.
- **D)** SSH into the container and read the `/var/log/syslog` file.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Cloud Trace provides distributed tracing. The ADK telemetry module natively emits spans for LLM calls, tool execution, and orchestration. Viewing these spans in a waterfall chart immediately reveals the bottleneck (e.g., if `trace_tool_call` for BigQuery takes 28 seconds, the database query is slow, not the LLM). → Lab 15 — Observability and Troubleshooting.
- **Why A is incorrect**: CPU utilization tells you the container is busy or idle, but not *what* phase of the agentic workflow is blocking.
- **Why C is incorrect**: IAM logs track access, not execution latency of individual tool calls.
- **Why D is incorrect**: Serverless containers (like Cloud Run) do not allow SSH, and syslog does not provide structured distributed tracing.
</details>

---

### Question 47
**Scenario**: An agent is deployed to Cloud Run. It requires a 60-second timeout for the LLM to perform deep reasoning, but requests are failing after exactly 10 seconds with a "Gateway Timeout" error.

**What is the most likely cause of this system failure?**
- **A)** The Gemini API has a hard 10-second limit.
- **B)** The Cloud Run container configuration has a `timeout_seconds` limit set too low (e.g., 10 seconds) for the expected LLM execution duration.
- **C)** The agent is stuck in an infinite reasoning loop.
- **D)** The BigQuery tool is returning too much data.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: When deploying agents, the infrastructure timeout (Cloud Run) must be greater than or equal to the application-level timeout (ADK LLM timeout). If Cloud Run is configured to terminate requests after 10 seconds, it will kill the process before the LLM finishes its 60-second reasoning task. → Lab 14 — Deployment Runtimes.
- **Why A is incorrect**: Gemini APIs can process requests for much longer than 10 seconds.
- **Why C is incorrect**: An infinite loop would run until it hits the infrastructure timeout, but the *cause* of the 10-second failure is the infrastructure configuration, not the loop itself.
- **Why D is incorrect**: Data volume issues cause memory exhaustion (OOM), not immediate Gateway Timeouts.
</details>

### Question 48
**Scenario**: Your ADK agent uses the Agent Platform Gen AI evaluation service. You have run `adk eval` on a golden dataset and the `multi_turn_task_success_evaluator` scores an average of 45%. 

**What is the most likely actionable insight from this result?**
- **A)** The model is generating harmful content.
- **B)** The agent is failing to accomplish the user's end goal across multiple turns (e.g., failing to successfully book a flight after 5 messages).
- **C)** The deployment environment (GKE) is failing to scale.
- **D)** The RAG retrieval latency is too high.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The `multi_turn_task_success_evaluator` measures whether the agent successfully completes the complex, multi-step goal presented by the user over the entire conversational trajectory. A low score means the agent is getting stuck, confused, or failing the objective. → Lab 13 — Agent Evaluation.
- **Why A is incorrect**: Harmful content is measured by the `safety_evaluator`.
- **Why C is incorrect**: Evaluation services test agent logic and quality, not Kubernetes infrastructure scaling.
- **Why D is incorrect**: Latency is measured by telemetry (Cloud Trace), not LLM-as-a-judge task success metrics.
</details>

---

### Question 49
**Scenario**: You are analyzing the performance of a newly deployed ADK workflow. You notice in Cloud Logging that the `LlmAgent` is raising `NodeTimeoutError` exceptions.

**What part of the ADK architecture generates this specific exception?**
- **A)** The LLM API connection (e.g., Vertex AI API timeout).
- **B)** The `google.adk.workflow` graph orchestration engine timing out on a specific node.
- **C)** The `GkeCodeExecutor` taking too long to provision a pod.
- **D)** The Agent Platform Memory Bank taking too long to semantic search.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: `NodeTimeoutError` is explicitly exported by `google.adk.workflow`. It indicates that a node in the graph workflow (or a `SequentialAgent`/`LoopAgent` which builds on the workflow engine) exceeded its configured `timeout`. → Lab 15 — Observability and Troubleshooting.
- **Why A, C, and D are incorrect**: While these can cause timeouts, they throw different exceptions (e.g., standard HTTP timeouts, or code executor timeouts). The specific `NodeTimeoutError` is tied to the workflow graph execution bounds.
</details>

---

### Question 50
**Scenario**: Your team wants to implement continuous evaluation (autorating) in a CI/CD pipeline. The pipeline should run automatically every time a developer merges changes to the agent's system prompt.

**Which ADK command should the CI/CD pipeline execute?**
- **A)** `adk deploy agent_engine`
- **B)** `adk test`
- **C)** `adk eval`
- **D)** `adk optimize`

<details><summary>Show answer</summary>

**Correct Answer: C**
**Explanation**:
- **Why C is correct**: The `adk eval` command executes the evaluation pipeline against the defined Eval Sets and evaluators. It is designed to be run in CI/CD to prevent regressions in agent quality when prompts or tool definitions change. → Lab 13 — Agent Evaluation.
- **Why A is incorrect**: This deploys the agent; it does not evaluate it.
- **Why B is incorrect**: `adk test` runs pytest on agent test JSON files (traditional unit testing), while `eval` runs the LLM-based autorater framework.
- **Why D is incorrect**: `optimize` uses GEPA to iteratively rewrite prompts; it is a development tool, not a CI/CD gating check.
</details>

---

### Question 51
**Scenario**: An agentic workflow involves calling a third-party legacy API that takes exactly 55 seconds to return data. 

**If deploying to Cloud Run, what infrastructure configuration must be adjusted to prevent the agent from failing this tool call?**
- **A)** Enable Cloud CDN.
- **B)** Increase the `timeout_seconds` configuration on the Cloud Run service beyond the default.
- **C)** Switch to a `ContainerCodeExecutor`.
- **D)** Use a smaller LLM model to compensate for the time.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Cloud Run has a default request timeout (often 5 minutes or less depending on configuration, but configurable up to 60 minutes). However, if the tool takes 55 seconds, plus LLM generation time, you must ensure both the application-level ADK timeout and the infrastructure-level Cloud Run timeout are explicitly high enough. → Lab 14 — Deployment Runtimes.
- **Why A is incorrect**: A CDN caches static web assets, which does not help a dynamic 55-second API call.
- **Why C is incorrect**: `ContainerCodeExecutor` is for code execution sandboxing, not for managing HTTP request timeouts to an external API.
- **Why D is incorrect**: Using a faster model saves a few seconds of generation time, but the 55-second tool bottleneck remains.
</details>

## Domain 5: Securing and Governing Agentic Workflows (~15%)

### Question 52
**Scenario**: An enterprise financial services firm is deploying an autonomous agent that can query account balances and initiate wire transfers up to $10,000. Corporate risk policies dictate that: (1) The agent must never initiate transfers over $1,000 without verified manager sign-off. (2) Prompt injection attacks must be inspected. (3) The agent identity must have a resource ceiling that excludes all unapproved projects and tools.

**Which security architecture fulfills all compliance requirements?**
- **A)** Implement **Agent Gateway** with **Model Armor** for prompt injection inspection, enforce a **Principal Access Boundary (PAB)** on the agent's **Agent Identity**, and add a **Human-In-The-Loop (HITL)** approval gate (`get_user_choice`) for transactions > $1,000.
- **B)** Place the agent on a public Cloud Run URL and write regex filters in Python to check for words like "wire" and "transfer".
- **C)** Give the agent admin Service Account permissions and require the user to enter their personal password in the chat prompt.
- **D)** Run the agent on a private VM with no IAM roles and disable external API authentication.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**:
  - **Model Armor** on **Agent Gateway** intercepts prompt injection and jailbreak attempts.
  - **Agent Identity** with a **Principal Access Boundary (PAB)** caps the resources the principal can reach (defense-in-depth).
  - **Human-In-The-Loop (HITL)** deterministic tools (like `request_input` or `get_user_choice`) pause execution and require authenticated human approval for high-risk operations. → Lab 17 — Model Armor and HITL.
- **Why B is incorrect**: Python regex filters are easily bypassed with prompt obfuscation and do not provide enterprise IAM scoping or HITL governance.
- **Why C is incorrect**: Admin service accounts violate least privilege, and asking users for passwords in chat prompts is a critical security vulnerability.
- **Why D is incorrect**: Disabling authentication prevents auditing and violates cloud security policies.
</details>

---

### Question 53
**Scenario**: A healthcare agent processes patient medical records. You must ensure that Personal Identifiable Information (PII) and Protected Health Information (PHI) like Social Security Numbers and medical condition codes are masked both before the prompt reaches Gemini and when the agent outputs responses to external APIs.

**Which Google Cloud security service should be integrated into the Agent Gateway or ADK?**
- **A)** Cloud Armor Web Application Firewall (WAF)
- **B)** **Sensitive Data Protection (Cloud DLP)** integrated with **Model Armor** (`ModelArmorPlugin`) sanitization filters.
- **C)** Secret Manager
- **D)** Cloud Key Management Service (Cloud KMS)

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: **Sensitive Data Protection (Cloud DLP)** combined with **Model Armor** provides automated real-time inspection, de-identification, masking, and redaction of PII/PHI (SSNs, medical record numbers, names) in both prompt inputs and agent outputs. The `ModelArmorPlugin` in ADK applies this seamlessly. → Lab 17 — Model Armor and HITL.
- **Why A is incorrect**: Cloud Armor protects against DDoS and Layer 7 web attacks (SQLi, XSS), but does not inspect or redact unstructured semantic PII in LLM payloads.
- **Why C is incorrect**: Secret Manager stores API keys and database credentials, not real-time payload sanitization.
- **Why D is incorrect**: Cloud KMS handles cryptographic key encryption at rest/transit, not contextual data de-identification.
</details>

---

### Question 54
**Scenario**: A registered billing agent presents a valid OAuth token to Agent Gateway but requests an unapproved `delete_invoice` tool. 

**Which two statements regarding governance and access control are correct? (Select TWO)**
- **A)** The valid OAuth token requires the gateway to allow the request.
- **B)** Agent Gateway should deny the tool through capability policy mapping and audit the decision.
- **C)** Agent Registry (`AgentRegistry` metadata) defines the approved agent version, identity, owner, and capabilities that the Gateway uses to make routing and policy decisions.
- **D)** Model Armor should grant the missing tool permission after inspecting the prompt.
- **E)** A PAB grants `delete_invoice` because it is narrower than project admin.

<details><summary>Show answer</summary>

**Correct Answers: B and C**
**Explanation**: 
- **Why B and C are correct**: Authentication (who you are) is not authorization (what you can do). A valid OAuth token simply proves identity. The **Agent Registry** supplies governed inventory/capability metadata (which tools are allowed). The **Agent Gateway** enforces traffic policy by checking the request against the Registry metadata and denying unapproved tool executions. → Lab 18 — Governance, Gateway, Registry.
- **Why A is incorrect**: Authentication does not imply universal authorization.
- **Why D is incorrect**: Model Armor inspects content for safety and PII; it does not manage IAM or tool execution grants.
- **Why E is incorrect**: A Principal Access Boundary (PAB) is a restrictive ceiling; it *caps* resources. It does not *grant* permissions.
</details>

---

### Question 55
**Scenario**: You are implementing a Model Armor plugin in your ADK workflow. You need to decide how the system should behave if the Model Armor API itself becomes briefly unreachable or times out during a screening request.

**Which configuration parameter controls the fail-closed vs. fail-open behavior?**
- **A)** `max_iterations`
- **B)** `block_on_screening_failure` in the `ModelArmorConfig`
- **C)** `timeout_seconds` in the `GkeCodeExecutor`
- **D)** `ContentCapturingMode` in `TelemetryConfig`

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The `block_on_screening_failure` boolean in the `ModelArmorConfig` determines the failure mode. Setting it to `True` means "fail-closed" (if the safety check cannot complete, block the request to ensure security). Setting it to `False` means "fail-open" (prioritize availability over guaranteed screening). This is a classic security architectural decision. → Lab 17 — Model Armor and HITL.
- **Why A is incorrect**: Controls reasoning loops, not safety screening failures.
- **Why C is incorrect**: Controls code execution timeouts, not Model Armor behavior.
- **Why D is incorrect**: Controls observability data, not security enforcement.
</details>

---

### Question 56
**Scenario**: You want to monitor traffic, enforce rate limits, and track API usage specifically for a fleet of decentralized A2A agents interacting across different departments in your organization.

**Which Google Cloud component acts as the central control plane for this agentic traffic?**
- **A)** Cloud SQL
- **B)** **Agent Gateway**
- **C)** Secret Manager
- **D)** Agent Platform Memory Bank

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: **Agent Gateway** acts as the API gateway and control plane specifically designed for agentic workflows. It monitors traffic, tracks agent interactions, enforces rate limits, and integrates with the Registry to apply governance policies centrally. → Lab 18 — Governance, Gateway, Registry.
- **Why A is incorrect**: Cloud SQL is a relational database, not a traffic gateway.
- **Why C is incorrect**: Secret Manager stores credentials, not traffic routing logic.
- **Why D is incorrect**: Memory Bank stores conversation history and semantic facts, not API traffic metrics.
</details>

### Question 57
**Scenario**: You are tasked with implementing identity propagation for a multi-agent system. The initial Web UI agent receives a user's OAuth 2.0 token. It must pass this token to a backend Specialist Agent, which in turn uses it to query a secure Database MCP server.

**How is identity propagation securely managed in this Google Cloud architecture?**
- **A)** The Web UI agent extracts the username from the token and passes it as a plaintext string in the prompt to the Specialist Agent.
- **B)** The **Agent Gateway** intercepts the incoming user request, validates the OAuth token, and injects it into the trusted headers of the A2A protocol payload sent to the Specialist Agent.
- **C)** The Web UI agent writes the token to a public Cloud Storage bucket for the Specialist Agent to read.
- **D)** The Specialist Agent uses `UnsafeLocalCodeExecutor` to run a script that steals the token from the Web UI agent's memory.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: Agent Gateway acts as the trusted perimeter. It validates external authentication (OAuth) and propagates that identity securely into internal agent-to-agent (A2A) and agent-to-tool (MCP) calls via trusted header injection, ensuring downstream systems can enforce user-level authorization. → Lab 18 — Governance, Gateway, Registry.
- **Why A is incorrect**: Passing identity in plaintext prompts strips the cryptographic signature, making it impossible for the database to verify the token.
- **Why C is incorrect**: Writing active bearer tokens to storage is a massive security breach.
- **Why D is incorrect**: Running unsafe code to steal memory is a malware pattern, not an enterprise identity propagation architecture.
</details>

---

### Question 58
**Scenario**: An ADK agent relies on an `EventarcToolset` to process sensitive internal HR documents uploaded to a Cloud Storage bucket. You must ensure that only the specific Cloud Storage bucket can trigger the agent, and the agent cannot be invoked directly by unauthorized internal users.

**How should you configure the security boundary?**
- **A)** Configure a Principal Access Boundary (PAB) on the Eventarc service account.
- **B)** Grant the `roles/run.invoker` (or equivalent invocation role) exclusively to the specific Eventarc trigger's Service Account, denying all other users and services.
- **C)** Use Model Armor to screen the contents of the HR document for unauthorized users.
- **D)** Set the `allow_egress` flag to `False` on the Cloud Run container.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: IAM invocation control (e.g., `roles/run.invoker` for Cloud Run) enforces who or what can trigger the agent. By granting it exclusively to the Eventarc trigger's service account, you ensure the agent is strictly event-driven and blocks unauthorized synchronous invocations. → Lab 16 — Agent Identity and Auth.
- **Why A is incorrect**: A PAB limits what resources a principal can *access*; it does not prevent a principal from being *invoked*.
- **Why C is incorrect**: Model Armor scans payloads for safety and DLP; it is not an IAM access control mechanism.
- **Why D is incorrect**: Disabling egress prevents the agent from calling out; it does not prevent unauthorized calls *in* to the agent.
</details>

---

### Question 59
**Scenario**: Your organization uses the `AgentRegistry` to manage hundreds of custom agents. A critical zero-day vulnerability is discovered in a specific LangChain tool used by "Agent v1.0". You deploy "Agent v1.1" with the patched tool.

**How do you ensure all incoming enterprise traffic immediately shifts to the patched agent without changing the client applications?**
- **A)** Email all developers to update their client code to point to the v1.1 endpoint.
- **B)** Update the `AgentRegistry` metadata to deprecate v1.0 and mark v1.1 as the active production endpoint. The Agent Gateway will automatically route new traffic to v1.1 based on the registry.
- **C)** Delete the GCP project containing v1.0.
- **D)** Modify the system prompt of v1.0 to tell the LLM to refuse all requests.

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: The Agent Registry acts as the central directory for agent endpoints and metadata. By updating the registry, the Agent Gateway (which relies on registry metadata for routing) dynamically shifts traffic to the new version without any client-side code changes. This is standard agentic governance. → Lab 18 — Governance, Gateway, Registry.
- **Why A is incorrect**: Relying on developers to update client code is slow and leaves the vulnerable agent exposed in the meantime.
- **Why C is incorrect**: Deleting the project is destructive, breaks running sessions abruptly, and is terrible operational practice.
- **Why D is incorrect**: Prompt instructions can be bypassed (jailbroken) and do not physically prevent the vulnerable tool from being loaded in the agent process.
</details>

---

### Question 60
**Scenario**: You are developing a custom metric evaluator in `google.adk.evaluation` to check if an agent's SQL queries comply with internal data governance policies (e.g., always including a `LIMIT` clause). 

**Which ADK registry must you integrate your custom evaluator with so it can be used by `adk eval`?**
- **A)** `SkillRegistry`
- **B)** `metric_evaluator_registry`
- **C)** `AgentRegistry`
- **D)** `LLMRegistry`

<details><summary>Show answer</summary>

**Correct Answer: B**
**Explanation**:
- **Why B is correct**: To make a custom evaluation metric available to the ADK's evaluation tooling (`adk eval`), it must be registered with the internal `metric_evaluator_registry`. → Lab 13 — Agent Evaluation.
- **Why A is incorrect**: `SkillRegistry` is for discovering tools and agent capabilities, not evaluation metrics.
- **Why C is incorrect**: `AgentRegistry` is for discovering and routing agent endpoints.
- **Why D is incorrect**: `LLMRegistry` maps model IDs to their implementing provider classes.
</details>

---

### Question 61
**Scenario**: Your enterprise architecture team is standardizing terminology and platform boundaries across two initiatives:
1. Giving 50,000 non-technical employees a unified web interface to search SharePoint, Google Drive, and Jira with automatic Document-Level ACL enforcement and out-of-the-box assistant capabilities.
2. Building a custom Python ADK multi-agent system that runs code inside GKE gVisor sandboxes and queries VPC-internal Cloud SQL databases via MCP.

In exam scenarios and architectural blueprints, the prompt states: *"Connect your custom ADK specialist agent to Gemini Enterprise so employees can invoke it from their central search workspace."*

**How should you interpret "Gemini Enterprise" in this architecture and integrate the two environments?**
- **A)** "Gemini Enterprise" is now the umbrella brand, and in this context specifically refers to the **Gemini Enterprise App (`GEApp`)** employee web experience. You deploy the custom ADK agent on **GKE** or **Agent Runtime** (part of **Agent Platform / `GEAP`**), register it in **Agent Registry** with an A2A Agent Card, and surface it inside **Gemini Enterprise App (`GEApp`)** with OAuth 2.0 identity propagation.
- **B)** Rewrite the GKE custom agent entirely as a zero-shot prompt template inside CX Agent Studio, because Gemini Enterprise App cannot invoke external GKE or Cloud Run agents.
- **C)** Deploy the SharePoint and Drive connectors directly inside a GKE `GkeCodeExecutor` pod without using Agent Search.
- **D)** Disable Document-Level ACLs in Agent Search and rely on a single shared Service Account for all 50,000 employees.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **Gemini Enterprise** is the overarching umbrella brand, while **Gemini Enterprise App (`GEApp`, formerly Google Agentspace)** is the turn-key employee search & assistant web application. Real-world enterprise agentic architectures are hybrid: `GEApp` handles turn-key enterprise search (`Agent Search` with ACL inheritance) and acts as the front door, while complex custom agents run on **GKE**, **Cloud Run**, or **Agent Runtime** (`GEAP`) and integrate via **A2A** and **Agent Registry**. → Lab 03 — Enterprise Data and Multimodal & Lab 12 — Multi-Agent and A2A.
- **Why B is incorrect**: CX Agent Studio / Agent Designer cannot replace custom GKE gVisor code execution or VPC-private MCP workloads.
- **Why C is incorrect**: Building custom connectors inside a code-execution sandbox violates separation of concerns and loses managed Agent Search ACL indexing.
- **Why D is incorrect**: Using a single shared Service Account without identity propagation leaks confidential documents across employees.
</details>

---

### Question 62
**Scenario**: An application security engineering team wants to automate the remediation of C/C++ and Python application-layer vulnerabilities (CVEs and sanitizer crashes) discovered in their CI pipeline. The solution must autonomously localize the root cause in the repository, synthesize a code patch, reproduce the exploit in an isolated sandbox, and run regression and fuzz tests to prove the patch eliminates the vulnerability before opening a pull request.

**Which Google Cloud coding agent capability and execution environment is purpose-built for this workflow?**
- **A)** **Code Mender** paired with **GKE Agent Sandbox (`GkeCodeExecutor` with `executor_type="sandbox"`)**
- **B)** Agent Designer in-console prompt templates with `UnsafeLocalCodeExecutor`
- **C)** CX Agent Studio Transition Routes with `VertexAiSearchTool`
- **D)** `VertexAiMemoryBankService` with floating model alias `gemini-flash-latest`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Objective 2.1 explicitly covers *"Using coding agents to refactor source code, optimize execution runtimes, and patch application-layer vulnerabilities"*. **Code Mender** is Google's autonomous vulnerability-patching coding agent that combines root-cause analysis, patch synthesis, and automated fuzz/regression verification inside a kernel-isolated sandbox (**GKE Agent Sandbox / gVisor**). → Lab 05 — Secure Sandboxes.
- **Why B is incorrect**: `UnsafeLocalCodeExecutor` runs untrusted exploit and fuzzing payloads directly on the host OS, creating a severe security risk.
- **Why C is incorrect**: CX Agent Studio is a conversational state machine for customer experience flows, not an autonomous vulnerability-patching agent.
- **Why D is incorrect**: Memory Bank stores conversational memories across sessions and does not localize or patch code vulnerabilities.
</details>

---

### Question 63
**Scenario**: You are deploying a custom ADK multi-agent system. Initially, the team planned to deploy all agents to **Agent Runtime** (`adk deploy agent_engine`) to minimize operational overhead. However, the updated security and model architecture introduces three new requirements:
1. One specialist agent must run an open-weight `gemma-4-26b-a4b-it` model with custom LoRA adapters on dedicated NVIDIA L4 GPUs inside your VPC.
2. Multi-turn requests to the self-hosted model must route based on live GPU KV-cache utilization and prefix-cache affinity.
3. Untrusted Python scripts generated by the agent must execute in gVisor kernel-isolated pods (`runtimeClassName: gvisor`).

**Why must you choose GKE (`adk deploy gke`) over Agent Runtime for this workload?**
- **A)** Agent Runtime is a managed serverless environment that does not allow attaching custom GPU node pools for self-hosted vLLM serving, does not support **GKE Inference Gateway** (`InferencePool` KV-cache routing), and cannot schedule custom **GKE Agent Sandbox (`gVisor`)** pod templates.
- **B)** Agent Runtime does not support the Python `google-adk` SDK or `VertexAiMemoryBankService`.
- **C)** Agent Runtime cannot make outbound HTTPS calls to Gemini SaaS models.
- **D)** Agent Runtime only supports Java and Go containers, whereas GKE supports Python.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: While **Agent Runtime** (`adk deploy agent_engine`) is ideal for zero-ops Python ADK agents calling managed Gemini APIs, its key architectural limitations are that you cannot provision custom GPU node pools for self-hosted open-weight models (`Gemma 4`), cannot deploy **GKE Inference Gateway** (`InferencePool` / `InferenceModel`) for KV-cache and LoRA routing, and cannot customize node-level **gVisor (`GkeCodeExecutor` `sandbox` mode)** or DaemonSet networking. Those requirements mandate **GKE**. → Lab 14 — Deployment Runtimes & Lab 19 — GKE Inference Gateway and GPUs.
- **Why B is incorrect**: Agent Runtime natively supports Python `google-adk` and `VertexAiMemoryBankService`.
- **Why C is incorrect**: Agent Runtime natively calls Gemini models on Vertex AI.
- **Why D is incorrect**: Agent Runtime is specifically built for Python ADK/agent deployments.
</details>

---

### Question 64
**Scenario**: You are hosting `gemma-4-31b-it` using vLLM across a pool of 8 NVIDIA A100 GPU pods on GKE to power a multi-turn financial research agent. Because the agent sends a 32,000-token system prompt and tool specification on every turn, your standard Kubernetes L7 HTTP Load Balancer routes consecutive turns of the same conversation to different GPU pods. This forces every pod to recompute the 32,000-token prefill from scratch, spiking Time-To-First-Token (TTFT) and saturating GPU KV-caches. Additionally, nightly batch evaluation jobs frequently starve live user conversations.

**Which architecture should you deploy on GKE to solve both problems?**
- **A)** Deploy **GKE Inference Gateway** with an **`InferencePool`** (using the Endpoint Picker extension for KV-cache and prefix-cache affinity routing) and configure **`InferenceModel`** criticality tiers (`Critical` for interactive agent turns, `Sheddable` for batch evaluation jobs).
- **B)** Replace the L7 HTTP Load Balancer with a L4 TCP Network Load Balancer and enable client IP session affinity.
- **C)** Configure Horizontal Pod Autoscaler (HPA) to scale the vLLM pods based on container CPU utilization above 80%.
- **D)** Move the vLLM GPU pods from GKE to Cloud Functions Gen 2.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: **GKE Inference Gateway** (`InferencePool` + `InferenceModel`) uses an Endpoint Picker (EPP) that scrapes real-time vLLM GPU metrics. It routes multi-turn agent requests to the GPU pod that already holds the matching prompt prefix in its KV-cache (eliminating redundant prefill computation and slashing TTFT), routes LoRA requests to pods with the adapter loaded in VRAM, and sheds `Sheddable` batch traffic when KV-cache saturation spikes to protect `Critical` interactive agent turns. → Lab 19 — GKE Inference Gateway and GPUs.
- **Why B is incorrect**: L4 TCP client-IP affinity fails when requests arrive through a shared Agent Gateway or web backend proxy (all traffic shares the proxy's IP) and has zero awareness of GPU KV-cache memory saturation.
- **Why C is incorrect**: LLM inference on GPUs is bottlenecked by GPU HBM KV-cache saturation and request queue depth (`vllm:gpu_cache_usage_perc`), not host CPU percentage.
- **Why D is incorrect**: Cloud Functions does not support multi-A100 GPU pools or stateful vLLM KV-cache pools.
</details>

---

### Question 65
**Scenario**: You are designing a GKE cluster that must simultaneously host:
1. Self-hosted `gemma-4-26b-a4b-it` inference pods requiring NVIDIA L4 GPUs.
2. ADK `GkeCodeExecutor(executor_type="sandbox")` pods requiring **GKE Sandbox (`gVisor`)** to run untrusted Python scripts generated by coding agents.

When your DevOps engineer attempts to create a single GKE node pool with both `--accelerator type=nvidia-l4` and `--sandbox type=gvisor`, the `gcloud container node-pools create` command fails.

**What is the correct GKE architectural configuration?**
- **A)** Create **two separate node pools** within the same GKE cluster: a **GPU node pool** (`g2-standard` with NVIDIA L4 GPUs) for the `InferencePool` vLLM pods, and a dedicated **CPU node pool with GKE Sandbox (`--sandbox="type=gvisor"`)** for the `GkeCodeExecutor(executor_type="sandbox")` pods, using Kubernetes node selectors/taints to schedule each workload onto its matching pool.
- **B)** Change `GkeCodeExecutor` to `UnsafeLocalCodeExecutor` so all code runs inside the GPU container without gVisor.
- **C)** Deploy two completely separate GCP organizations because GKE cannot support GPUs and sandboxes in the same cluster.
- **D)** Switch `GkeCodeExecutor` to `executor_type="job"` on the GPU nodes, because `job` mode provides the exact same gVisor kernel syscall interception as `sandbox` mode.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In GKE, a single node pool cannot combine hardware GPU accelerators with GKE Sandbox (`gVisor` `runsc`) on the same VM nodes. The standard enterprise pattern is a multi-node-pool GKE cluster: a GPU node pool serves the open-weight `InferencePool`, and a separate `--sandbox="type=gvisor"` CPU node pool runs `GkeCodeExecutor(executor_type="sandbox", sandbox_gateway_name=..., sandbox_template=...)`. → Lab 19 — GKE Inference Gateway and GPUs.
- **Why B is incorrect**: `UnsafeLocalCodeExecutor` removes all isolation and exposes the GPU host and credentials to arbitrary code execution.
- **Why C is incorrect**: A single GKE cluster natively supports multiple heterogeneous node pools.
- **Why D is incorrect**: `executor_type="job"` runs standard containers sharing the host Linux kernel and does **not** provide gVisor isolation (explicitly warned in `GkeCodeExecutor`'s docstring).
</details>

---

### Question 66
**Scenario**: In ADK 2.9.0, you are building a hierarchical multi-agent system. A top-level `LlmAgent` named `ChiefOrchestrator` needs to dynamically route user requests either to an interactive `SupportAgent` (`LlmAgent`) or to a deterministic 3-step compliance pipeline (`Ingest -> Audit -> Archive`) that must execute in strict sequence as a `sub_agent` of `ChiefOrchestrator`.

When you inspect ADK 2.9.0, you notice `SequentialAgent` emits a `DeprecationWarning` recommending `google.adk.workflow.Workflow`. However, passing a `Workflow` instance inside `ChiefOrchestrator(sub_agents=[...])` raises a validation error.

**How should you architect this in ADK 2.9.0?**
- **A)** Use `SequentialAgent` for the 3-step compliance sub-pipeline inside `ChiefOrchestrator.sub_agents` (or wrap the `Workflow` inside an `AgentTool`), because ADK 2.9.0's `DeprecationWarning` explicitly states: *"Workflow cannot yet be used as an LlmAgent sub-agent."*
- **B)** Delete `ChiefOrchestrator` and force all users to call three separate HTTP endpoints manually in order.
- **C)** Put all three compliance agents inside `ParallelAgent` so they run simultaneously.
- **D)** Pass `disallow_transfer_to_peers=True` on `Workflow` to bypass the Pydantic type check.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: As verified in ADK 2.9.0 (`docs/VERIFIED_FACTS.md`), `SequentialAgent` emits: `DeprecationWarning: SequentialAgent is deprecated in favor of Workflow and will be removed in a future version. Workflow cannot yet be used as an LlmAgent sub-agent.` Therefore, when nesting a deterministic sequential pipeline directly inside `LlmAgent.sub_agents` (or wrapping it as a callable `AgentTool`), `SequentialAgent` remains necessary today. → Lab 08 — ADK Fundamentals & Lab 12 — Multi-Agent and A2A.
- **Why B is incorrect**: Breaks autonomous orchestration by pushing orchestration logic onto the client.
- **Why C is incorrect**: `ParallelAgent` runs all steps concurrently rather than in the required strict `Ingest -> Audit -> Archive` order.
- **Why D is incorrect**: `disallow_transfer_to_peers` is an `LlmAgent` field, not a `Workflow` field.
</details>

---

### Question 67
**Scenario**: Your organization operates a decentralized multi-agent ecosystem across three Google Cloud projects:
- An **Order Triage Agent** running on **Agent Runtime** (`project-retail`).
- A **Fraud Scoring Agent** running on **GKE** (`project-risk`) exposed via the **Agent2Agent (A2A)** protocol.
- A **Ledger MCP Server** running on **Cloud Run** (`project-finance`) exposing BigQuery and Cloud SQL tools via **Model Context Protocol (MCP)**.

Security policy forbids hardcoding service URLs in agent source code and requires that agents only communicate with centrally vetted A2A peers and MCP servers.

**How should the Order Triage Agent discover and bind to both the Fraud Scoring Agent and the Ledger MCP Server in ADK 2.9.0?**
- **A)** Instantiate `AgentRegistry(project_id=..., location=...)` from `google.adk.integrations.agent_registry` and call `registry.get_remote_a2a_agent(...)` to bind the A2A Fraud Scoring Agent and `registry.get_mcp_toolset(...)` to bind the governed Ledger `MCPToolset`.
- **B)** Use `MCPToolset` to connect to the Fraud Scoring Agent and `A2aRemoteAgentConfig` to query the Cloud SQL database directly.
- **C)** Store hardcoded IP addresses in a public GitHub repository and fetch them using `UnsafeLocalCodeExecutor`.
- **D)** Use `GCPSkillRegistry` (`get_skill`) to establish network sockets to remote A2A agents.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `AgentRegistry` (`google.adk.integrations.agent_registry.AgentRegistry`) is the central discovery and governance plane that ties **A2A** and **MCP** together. It provides `get_remote_a2a_agent()` (which resolves the remote agent's endpoint and Agent Card from the registry) and `get_mcp_toolset()` (which returns a ready-to-use `MCPToolset` for a registered MCP server). → Lab 12 — Multi-Agent and A2A & Lab 20 — E2E AI Threat Defense.
- **Why B is incorrect**: Reverses the protocols: **A2A** is for agent-to-agent negotiation, while **MCP** is for agent-to-tool/database connections.
- **Why C is incorrect**: Hardcoding IPs and running `UnsafeLocalCodeExecutor` violates both dynamic governance and sandbox security.
- **Why D is incorrect**: `GCPSkillRegistry` manages reusable skill instructions/frontmatter (`L1/L2/L3`), not live A2A agent endpoints or MCP server discovery.
</details>

---

### Question 68
**Scenario**: You are designing an iterative code-review architecture in ADK where a `GeneratorAgent` writes a SQL migration script and stores it in `session.state["draft_sql"]` via `output_key="draft_sql"`. A `CriticAgent` then validates the SQL against schema rules. This `Generator -> Critic` cycle must repeat until `CriticAgent` approves the SQL, or stop after at most 4 iterations to prevent an infinite billing loop.

**Which ADK orchestration pattern and termination mechanism should you configure?**
- **A)** Wrap `GeneratorAgent` and `CriticAgent` inside a `LoopAgent(max_iterations=4, sub_agents=[GeneratorAgent, CriticAgent])` and equip `CriticAgent` with the built-in `exit_loop` tool from `google.adk.tools` to terminate early when the SQL passes validation.
- **B)** Use `ParallelAgent` with `max_concurrency=4` and call `transfer_to_agent` inside a prompt.
- **C)** Set `block_on_screening_failure=True` on `ModelArmorConfig` to stop the loop after 4 turns.
- **D)** Rely on the LLM to count to 4 in its system prompt without `max_iterations`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `LoopAgent` enforces a hard deterministic cap via `max_iterations=4` (preventing runaway token loops), while the built-in `exit_loop` tool (`from google.adk.tools import exit_loop`) allows `CriticAgent` to break out of the loop immediately once the quality criteria are met. → Lab 08 — ADK Fundamentals & Lab 12 — Multi-Agent and A2A.
- **Why B is incorrect**: `ParallelAgent` executes sub-agents concurrently in a single pass, not iteratively in a generator-critic feedback cycle.
- **Why C is incorrect**: `ModelArmorConfig` screens for prompt injection/safety violations, not iterative convergence.
- **Why D is incorrect**: Prompt-based counting is probabilistic and cannot guarantee protection against runaway reasoning loops.
</details>

---

### Question 69
**Scenario**: Your medical-device company must deploy an on-premise/edge-compatible open-weight model on a GKE cluster with a tight GPU budget (single NVIDIA L4 24 GB GPU per node). You need a model from the Gemma 4 family with a 262,144-token context window that maximizes tokens-per-second throughput and minimizes active-parameter memory bandwidth per generated token.

**Which verified model ID from the Gemini/Gemma catalog should you select?**
- **A)** `gemma-4-26b-a4b-it`
- **B)** `gemma-4-31b-it`
- **C)** `gemini-2.5-pro`
- **D)** `gemini-embedding-2`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `gemma-4-26b-a4b-it` is the open-weights Mixture-of-Experts (MoE) variant in the Gemma 4 family (26B total parameters, ~4B active parameters per token, 262K input / 32K output context). Because only ~4B parameters are activated per forward pass, it delivers substantially higher tokens/sec and lower compute latency on constrained GPUs like NVIDIA L4 compared to the dense 31B model (`gemma-4-31b-it`). → Lab 07 — Model Selection & Lab 19 — GKE Inference Gateway and GPUs.
- **Why B is incorrect**: `gemma-4-31b-it` is a dense 31B model that activates all 31B parameters on every token, requiring more GPU memory bandwidth and higher latency than the `a4b` MoE variant.
- **Why C is incorrect**: `gemini-2.5-pro` is a proprietary cloud SaaS model and cannot be self-hosted on edge/GKE GPU nodes.
- **Why D is incorrect**: `gemini-embedding-2` generates vector embeddings (8,192 input limit) and cannot generate text responses.
</details>

---

### Question 70
**Scenario**: When two remote agents communicate across organizational departments using the **Agent2Agent (A2A)** protocol, the calling orchestrator must first inspect what capabilities, input/output MIME types (`application/json`, `text/plain`), and authentication schemes (`OAuth2`, `OIDC`) the remote specialist agent supports before creating an A2A Task. Furthermore, the orchestrator must attach a signed OAuth 2.0 trace/auth header to every outgoing A2A request.

**Which A2A artifacts and ADK classes handle capability advertisement and header injection?**
- **A)** The remote agent publishes an **Agent Card** (`/.well-known/agent.json`), and the calling ADK agent configures `A2aRemoteAgentConfig` with `request_interceptors` (`RequestInterceptor`) and `card_request_interceptors` (`CardRequestInterceptor`).
- **B)** The remote agent publishes a `SKILL.md` frontmatter file over FTP, and the caller uses `BigQueryToolset`.
- **C)** Both agents share a local SQLite database file using `sqlite_span_exporter`.
- **D)** The caller uses `VertexAiRagMemoryService` to guess the remote agent's URL from vector embeddings.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: In the **A2A** specification and `google.adk.a2a.agent`, remote agents advertise their skills, supported modalities, endpoint URL, and required auth schemes via an **Agent Card**. On the client side, `A2aRemoteAgentConfig` exposes `request_interceptors` and `card_request_interceptors` (`RequestInterceptor` / `CardRequestInterceptor`) to inject OAuth 2.0 bearer tokens and distributed trace headers into A2A handshakes. → Lab 12 — Multi-Agent and A2A.
- **Why B is incorrect**: `SKILL.md` is used for local/GCS `SkillRegistry` instructions, not A2A network protocol negotiation.
- **Why C is incorrect**: `sqlite_span_exporter` is a local OpenTelemetry trace exporter, not an inter-agent protocol.
- **Why D is incorrect**: RAG memory stores semantic facts, not cryptographic A2A capability contracts.
</details>

---

### Question 71
**Scenario**: A healthcare agent passes all `final_response_match_v2` tests on a golden dataset of 200 patient scheduling scenarios. However, in staging, an audit reveals two critical defects:
1. For 15% of prompts, the agent skips calling the mandatory `verify_insurance_eligibility` tool and still fabricates a polite confirmation message that matches the expected text pattern.
2. For 5% of prompts, the agent invents a copay dollar amount that does not appear anywhere in the tool output returned by the EHR system.

**Which two evaluation modules from `google.adk.evaluation` should you add to your continuous `adk eval` pipeline to catch both defects deterministically?**
- **A)** `trajectory_evaluator` (to enforce `in_order_match` / `exact_match` on tool invocations) and `hallucinations_v1` (to verify that every claim in the final response is grounded in retrieved tool context)
- **B)** `final_response_match_v1` and `SimplePromptOptimizer`
- **C)** `GkeCodeExecutor` and `RedisSessionService`
- **D)** `TransferToAgentTool` and `preload_memory`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: Final-response similarity (`final_response_match_v2`) only checks *what* the agent said, not *how* it got there or whether the facts came from tool outputs. Adding `trajectory_evaluator` verifies the exact tool-call trajectory (catching the skipped `verify_insurance_eligibility` call), while `hallucinations_v1` scores groundedness against the actual tool/RAG context (catching the fabricated copay amount). → Lab 13 — Agent Evaluation.
- **Why B is incorrect**: `final_response_match_v1` is an older surface-level response comparator that still ignores tool trajectories and ungrounded claims.
- **Why C is incorrect**: These are execution and session components, not evaluation metrics.
- **Why D is incorrect**: These are agent routing and memory tools, not evaluation modules.
</details>

---

### Question 72
**Scenario**: You want to run regression tests on your multi-agent ADK workflow on every Git pull request in Cloud Build. However, calling live Gemini models on 500 multi-turn test cases on every commit is too slow, non-deterministic, and expensive. You want to record a known-good interaction trace (including LLM tool-call decisions and tool outputs) in staging and replay it deterministically during CI checks to verify that code refactors have not broken agent state transitions or schema contracts.

**Which verified `adk` CLI command pair supports this workflow?**
- **A)** `adk conformance record` and `adk conformance test`
- **B)** `adk optimize` and `adk migrate session`
- **C)** `adk create` and `adk web`
- **D)** `adk deploy docker` and `adk telemetry disable`

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: The `adk conformance` command group (`adk conformance record` and `adk conformance test`) captures deterministic execution recordings and replays them in CI/CD pipelines to detect regressions in agent graph wiring, state schemas, and tool contracts without paying for or waiting on live LLM inference. → Lab 15 — Observability and Troubleshooting.
- **Why B is incorrect**: `adk optimize` runs the GEPA prompt optimizer, and `adk migrate session` migrates session storage schemas.
- **Why C is incorrect**: `adk create` scaffolds a project template, and `adk web` launches the interactive local UI.
- **Why D is incorrect**: `adk deploy docker` builds a container image, and `adk telemetry disable` turns off OpenTelemetry export.
</details>

---

### Question 73
**Scenario**: A multi-agent customer support system on Google Cloud is experiencing p99 latency spikes of 14 seconds. On a single user turn, the root `LlmAgent` invokes three independent MCP tools in parallel and delegates a sub-task to a remote A2A agent. At the same time, your compliance officer mandates that **Cloud Trace** spans must record tool execution latency, token counts, and parallel tool-merge timings, but **must never capture raw customer PII or prompt text** inside trace attributes in production.

**How should you configure `google.adk.telemetry` to meet both the latency-attribution and privacy requirements?**
- **A)** Enable OpenTelemetry export to Cloud Trace (`trace_call_llm`, `trace_tool_call`, `trace_merged_tool_calls`) and configure `TelemetryConfig` with `ContentCapturingMode` set to disable/redact prompt and response content capture in production while preserving span durations, status codes, and token usage metrics.
- **B)** Run `adk telemetry disable` in production so no spans are sent to Cloud Trace, and rely on billing invoices to debug latency.
- **C)** Set `ContentCapturingMode` to capture full raw payloads and grant `roles/cloudtrace.user` to all employees.
- **D)** Disable parallel tool execution so every tool runs sequentially without `trace_merged_tool_calls`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: `google.adk.telemetry` instruments LLM calls (`trace_call_llm`), individual tool executions (`trace_tool_call`), and concurrent tool fan-out/fan-in (`trace_merged_tool_calls`), exporting waterfall spans and token counters (`_token_usage`) to Cloud Trace. Setting `ContentCapturingMode` in `TelemetryConfig` to redact/omit payload contents ensures zero PII is written to trace storage while keeping full latency and token observability. → Lab 15 — Observability and Troubleshooting.
- **Why B is incorrect**: Disabling telemetry removes the ability to attribute latency between `trace_call_llm` and `trace_tool_call`.
- **Why C is incorrect**: Capturing full raw prompts containing PII in Cloud Trace violates the compliance mandate.
- **Why D is incorrect**: Forcing sequential tool execution degrades p99 latency even further.
</details>

---

### Question 74
**Scenario**: A junior IAM administrator accidentally grants `roles/bigquery.admin` and `roles/storage.admin` at the **Google Cloud Organization root** to the workload identity (`Agent Identity`) of an experimental marketing agent. Fortunately, the security architect had previously bound a **Principal Access Boundary (PAB)** policy to that Agent Identity whose `eligible_resources` rule only lists `//cloudresourcemanager.googleapis.com/projects/marketing-sandbox-dev`.

During a prompt-injection attack, the marketing agent attempts to query `projects/corp-payroll-prod.hr_dataset.salaries`.

**What is the outcome of the query, and why?**
- **A)** The query fails with `403 PERMISSION_DENIED`. Effective access is the **intersection** of IAM Allow policies and the Principal Access Boundary (`Effective Access = IAM Allow ∩ PAB`). Because `projects/corp-payroll-prod` is outside the PAB's eligible resources ceiling, the Organization-level IAM grant is neutralized.
- **B)** The query succeeds because an Organization-level IAM Allow policy (`roles/bigquery.admin`) overrides a Principal Access Boundary policy.
- **C)** The query succeeds unless `ModelArmorPlugin` blocks the SQL syntax.
- **D)** The query fails only if the agent runs on GKE, because PAB policies do not apply to Agent Runtime or Cloud Run.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: A **Principal Access Boundary (PAB)** policy defines the maximum set of resources a principal can *ever* access across Google Cloud (`Effective Access = IAM Allow ∩ PAB Eligible Resources`). A PAB never grants permissions on its own, and no IAM Allow role—even at the Organization root—can grant access to a resource excluded by the principal's PAB. → Lab 16 — Agent Identity and Auth & Lab 20 — E2E AI Threat Defense.
- **Why B is incorrect**: IAM Allow policies never override a PAB ceiling; both must allow the target resource.
- **Why C is incorrect**: IAM + PAB enforcement happens deterministically at the Google Cloud IAM control plane regardless of Model Armor.
- **Why D is incorrect**: PAB is bound to the **Agent Identity** (principal) and applies universally across all Google Cloud runtimes (Agent Runtime, Cloud Run, GKE, GCE).
</details>

---

### Question 75
**Scenario**: You are designing an end-to-end **AI Threat Defense** architecture for a regulated banking multi-agent system. The architecture must simultaneously defend against four distinct threats:
1. Unauthenticated or rate-abusive traffic hitting your A2A and MCP endpoints, plus loss of end-user OAuth 2.0 identity during downstream RAG queries.
2. Developers or compromised agents attempting to invoke unvetted "shadow" MCP servers or rogue A2A agents.
3. Indirect prompt injections hidden inside third-party emails fetched by an MCP tool, as well as fail-safe blocking if the content screening API experiences a transient outage.
4. Lateral movement to non-sandbox GCP projects if an agent's identity is granted overly broad IAM roles.

**Which combination of four Google Cloud security controls maps 1:1 to these four threat vectors?**
- **A)** (1) **Agent Gateway** for ingress policy, rate limiting, and OAuth identity propagation; (2) **Agent Registry** (`AgentRegistry`) for attested A2A/MCP endpoint allowlisting; (3) **Model Armor** (`ModelArmorPlugin` with `block_on_screening_failure=True`) for pre-model/post-tool screening; and (4) **Agent Identity with a Principal Access Boundary (PAB)** for blast-radius containment.
- **B)** (1) Cloud DNS; (2) `GCPSkillRegistry`; (3) `UnsafeLocalCodeExecutor`; and (4) `InMemorySessionService`.
- **C)** (1) GKE Inference Gateway; (2) `FallbackModel`; (3) `ModelArmorConfig(block_on_screening_failure=False)`; and (4) `roles/owner`.
- **D)** (1) System prompt rules ("do not get hacked"); (2) `temperature=0.0`; (3) `SequentialAgent`; and (4) `VertexAiMemoryBankService`.

<details><summary>Show answer</summary>

**Correct Answer: A**
**Explanation**:
- **Why A is correct**: This is the complete 4-layer Google Cloud **AI Threat Defense** reference architecture:
  1. **Agent Gateway** enforces authentication, quotas, audit logging, and user OAuth 2.0 identity propagation.
  2. **Agent Registry** governs discovery of cryptographically attested A2A Agent Cards (`get_remote_a2a_agent`) and approved MCP servers (`get_mcp_toolset`).
  3. **Model Armor** (`ModelArmorPlugin` with `block_on_screening_failure=True`) screens user prompts and tool outputs (`before_model_callback` / `after_tool_callback`) for indirect prompt injection and PII leaks while failing closed on outages.
  4. **Agent Identity + Principal Access Boundary (PAB)** enforces an identity-centric blast-radius ceiling (`IAM Allow ∩ PAB`). → Lab 20 — E2E AI Threat Defense.
- **Why B, C, and D are incorrect**: None of these provide the 4-layer security control plane; setting `block_on_screening_failure=False` fails open during an outage, and prompt engineering (`D`) cannot enforce network, catalog, or IAM boundaries.
</details>

---


## Scoring and Diagnosis

Count your correct answers across all 75 questions (matching the 3-hour, 75-question live exam format) and use this table to plan your final review:

| Score | Meaning | Recommended Action |
| :---: | :--- | :--- |
| **0–44** | **Foundational gaps.** | Do not take the exam yet. Re-run Tracks 3, 4, and 5 end-to-end. |
| **45–59** | **Close, but risky.** | You understand the concepts but miss the trade-offs. Review `STUDY_GUIDE.md` and `docs/VERIFIED_FACTS.md`. |
| **60–75 (≥80%)** | **Ready to test.** | You have mastered the multi-agent architectures, runtime trade-offs, security boundaries, and ADK 2.9.0 API surfaces. |

### Domain Breakdown Tracker

Find your weakest domain to focus your study time efficiently:

| Domain | Your Score | Target (80%) |
| :--- | :---: | :---: |
| 1. Low-Code Tools (~13%) | ___ / 9 | 8 |
| 2. Coding Agents (~17%) | ___ / 12 | 10 |
| 3. Custom Agents (~33%) | ___ / 25 | 20 |
| 4. Evaluating & Deploying (~22%) | ___ / 17 | 14 |
| 5. Securing & Governing (~15%) | ___ / 12 | 10 |
| **Total** | **___ / 75** | **60** |

