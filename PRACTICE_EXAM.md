# Google Cloud Certified Professional Agentic Architect — High-Yield Practice Exam

This unofficial practice set uses the objectives and domain weights in the official exam guide. It is a study aid, not a claim about the live exam's exact wording, length, or difficulty.

---

## Domain 1: Building Agents Using Low-Code Tools (~13%)

### Question 1
**Scenario**: Your retail organization wants to deploy an AI customer service agent using Gemini Enterprise low-code tools. The agent must guide customers through a 3-step order return process (Select Order -> Validate Reason -> Generate Return Label). If the customer provides an invalid tracking number twice, the agent must escalate the conversation to a human tier without crashing or losing session context.

**Which architectural configuration should you implement in CX Agent Studio?**
- **A)** Create a single Page with an inline Python cloud function that maintains a retry counter in memory and triggers a webhook transition.
- **B)** Configure dedicated Pages for each return stage, configure Transition Routes with parameter conditions, and implement an Event Handler for `sys.no-match-2` that transitions to an Agent Handoff page.
- **C)** Use a single generative prompt template in Agent Designer and instruct the LLM in system instructions to count retries internally before generating an escalation message.
- **D)** Configure an Agent Search data store linked to return policies and allow zero-shot intent classification to handle return routing dynamically.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: In CX Agent Studio (formerly Dialogflow CX), state-based multi-step workflows are modeled using **Pages** and **Transition Routes**. Built-in **Event Handlers** (like `sys.no-match-2` or `sys.no-input-2`) automatically manage error counts and trigger deterministic transitions to an escalation/handoff page while preserving all session parameters.
> - **Why A is incorrect**: Maintaining retry counters in custom webhook memory introduces unnecessary complexity and breaks the declarative state machine paradigm of CX Agent Studio.
> - **Why C is incorrect**: Relying solely on LLM system instructions to count retries is non-deterministic and prone to hallucinations and reasoning loops.
> - **Why D is incorrect**: Agent Search is designed for RAG over unstructured documents, not for managing stateful multi-step business transactions.

---

### Question 2
**Scenario**: An insurance company needs an agent in Gemini Enterprise that can ingest user-uploaded claims consisting of a PDF repair estimate, photos of vehicle damage, and a voice recording of the accident description. The agent must summarize the incident and verify if the damage photos match the written description.

**How should you configure the multimodal data ingestion pipeline?**
- **A)** Convert the audio recording using Speech-to-Text API, run Vision API on the photos for OCR, extract text from the PDF using Document AI, and pass combined text strings into a Gemini 2.5 Flash-Lite model.
- **B)** Upload the PDF, damage photos, and audio files directly into Cloud Storage, and provide their GCS URIs in a single multimodal prompt payload to Gemini 3.7 Flash within Gemini Enterprise Agent Designer.
- **C)** Embed the audio and images into a Vector Search index and use text search to retrieve the nearest matching insurance policy clauses.
- **D)** Ingest the data into BigQuery using BigQuery ML, and train a supervised classification model to evaluate the insurance claim.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: Gemini 3.7 Flash natively supports native multimodal reasoning across audio, high-resolution images, video, and PDF documents within a single context window. Referencing Cloud Storage URIs (`gs://...`) directly in the multimodal prompt eliminates complex multi-pipeline preprocessing (Speech-to-Text, Vision OCR, Document AI) and preserves rich cross-modal relationships.
> - **Why A is incorrect**: Splitting the workflow into disparate APIs strips cross-modal nuance (e.g., correlating specific dents in the image with specific voice emphasis in the audio) and increases latency and cost.
> - **Why C is incorrect**: Vector embedding alone cannot perform multi-modal comparative reasoning across image damage and text repair quotes.
> - **Why D is incorrect**: Training a custom BigQuery ML model requires labeled training datasets and does not provide generative reasoning.

---

## Domain 2: Using Coding Agents for Application Development (~17%)

### Question 3
**Scenario**: Your engineering team is adopting Google Antigravity to build autonomous coding agents that refactor legacy Java services into Python Cloud Run microservices. The agent needs to execute shell commands, run test suites, and install dependencies, but enterprise security policy strictly prohibits agents from making unvetted outbound internet connections or accessing corporate secrets on the host machine.

**How should you configure the Antigravity execution environment?**
- **A)** Run Antigravity in Standard Sandbox Mode with GKE Sandbox (gVisor container runtime) and workspace directory boundaries.
- **B)** Grant Antigravity `BypassSandbox: true` and configure OS-level firewall iptables rules on the developer's laptop.
- **C)** Run Antigravity inside a local Docker container with root privileges and mount the entire `/Users/` directory.
- **D)** Restrict the Antigravity agent to read-only tools and manually copy-paste code suggestions into the IDE.

> **Correct Answer: A**
> **Explanation**:
> - **Why A is correct**: Standard Sandbox Mode in Antigravity enforces workspace directory confinement and disables arbitrary network calls. Combining this with GKE Sandbox (using gVisor kernel isolation) provides enterprise-grade isolation for untrusted code execution and automated testing.
> - **Why B is incorrect**: `BypassSandbox: true` disables sandbox isolation and requires manual approval for every command, which is risky and degrades developer velocity.
> - **Why C is incorrect**: Mounting `/Users/` with root privileges violates the principle of least privilege and exposes personal credentials.
> - **Why D is incorrect**: Read-only mode prevents the agent from running automated refactoring and test suites autonomously.

---

### Question 4
**Scenario**: You are developing an enterprise Antigravity plugin for your cloud operations team. You want the coding agent to automatically follow Google Cloud security best practices whenever a developer opens a Terraform file (`*.tf`), but you want the Terraform linting instructions loaded into the context window *only* when Terraform files are being edited to conserve prompt tokens.

**Which customization mechanism in Antigravity should you implement?**
- **A)** Add global system instructions in `~/.gemini/config/GEMINI.md` with `always_on: true`.
- **B)** Create a custom skill in `.agents/skills/terraform-lint/SKILL.md` and define an agent rule with `trigger: model_decision` or directory pattern matching.
- **C)** Write a bash script that runs `terraform fmt` in a cron schedule using the schedule tool.
- **D)** Hardcode Terraform rules into the agent's Python SDK client configuration before each conversation turn.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: Antigravity uses progressive disclosure for **Skills** and **Rules**. By creating a skill with a YAML frontmatter and scoping rules to file triggers/model decisions, Antigravity injects the full skill instructions only when relevant files are touched, preserving context window tokens and minimizing costs.
> - **Why A is incorrect**: Setting `always_on: true` in global configuration injects the rules into every turn regardless of file type, bloating token usage.
> - **Why C is incorrect**: A cron schedule does not guide the agent's contextual generation during code authoring.
> - **Why D is incorrect**: Hardcoding rules into client code prevents modular sharing across team repositories.

---

## Domain 3: Developing Custom Agents (~33%)

### Question 5
**Scenario**: You are architecting a real-time financial trading assistant using the Agent Development Kit (ADK). The agent must analyze market feeds, detect trading signals, and propose calls to an internal REST API. The system requires low latency and machine-validated API parameter shapes; application code will independently enforce business rules, authorization, and human approval.

**Which model and parameter configuration should you select?**
- **A)** Gemini 2.5 Pro with a static thinking budget of 32,000 tokens and zero temperature.
- **B)** Gemini 3.7 Flash configured with dynamic thinking budget (1,024 to 2,048 tokens) and strict Pydantic structured output schemas (`response_schema`).
- **C)** Gemma 2 2B deployed on an edge Cloud Run instance without function calling tools.
- **D)** Gemini 2.5 Flash-Lite with thinking mode disabled and unstructured natural language output.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: A latency-oriented tool-capable model with a bounded thinking budget and a Pydantic `response_schema` is the best fit among these choices. The schema validates structure and types; it does not guarantee factual correctness or authorize a trade.
> - **Why A is incorrect**: Gemini 2.5 Pro with a 32K thinking budget will incur multi-second latencies, violating the 1.5-second SLA.
> - **Why C is incorrect**: Gemma 2 2B lacks the complex multi-step reasoning and function calling reliability required for financial trading operations.
> - **Why D is incorrect**: Disabling thinking and using unstructured text will lead to hallucinated parameters and unreliable tool execution.

---

### Question 6
**Scenario**: An autonomous customer support agent built with the ADK interacts with enterprise users over multiple weeks. The agent needs to recall user preferences (e.g., preferred billing currency, communication language, past ticket resolutions) across completely different chat sessions, but recent chat turns must not be cluttered with thousands of irrelevant past messages.

**Which memory architecture on Google Cloud should you deploy?**
- **A)** Store all raw message histories in a single Firestore document and append the entire history to the system prompt on every turn.
- **B)** Deploy **Agent Platform Memory Bank** to automatically extract semantic memories and facts, combined with a **Managed Session** store for short-term working context pruning.
- **C)** Keep conversation history in local Python process memory using a global dictionary.
- **D)** Configure a Redis cache that purges all keys every 24 hours using TTL expiration.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: **Agent Platform Memory Bank** provides long-term associative memory. It analyzes past turns, extracts salient facts/preferences, indexes them into a semantic store, and injects only relevant memories when queried. Managed Sessions handle short-term conversational context with automatic sliding-window pruning.
> - **Why A is incorrect**: Appending raw history to the system prompt will rapidly exceed context token limits, increase latency, and inflate costs.
> - **Why C is incorrect**: In-memory global state is lost on process restarts and fails when scaling horizontally across multiple container instances.
> - **Why D is incorrect**: Purging Redis keys after 24 hours destroys long-term user preferences across multi-week interactions.

---

### Question 7
**Scenario**: You need to connect an ADK-based agent to enterprise BigQuery analytics and Cloud SQL PostgreSQL databases. The agent must discover available schemas dynamically, generate valid SQL queries, execute them safely, and handle query syntax errors automatically without writing custom integration code for every database.

**Which approach should you use?**
- **A)** Hardcode database connection strings in the agent's system prompt and instruct the LLM to output bash commands using `psql` and `bq`.
- **B)** Deploy **Google Cloud MCP Toolbox for Databases** as Model Context Protocol (MCP) servers and register them in the agent's MCP client configuration.
- **C)** Export all database tables to static CSV files in Cloud Storage every hour and query them using Vertex AI Search.
- **D)** Write custom Python functions for every SQL query variation and register them as static function calling tools.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: **Google Cloud MCP Toolbox for Databases** exposes supported databases to agents through MCP with reusable tool definitions and database integration patterns. You must still configure identity, least privilege, query policy, timeouts, and auditing.
> - **Why A is incorrect**: Exposing connection strings and running raw shell commands is a severe security vulnerability.
> - **Why C is incorrect**: Static CSV exports provide stale data and do not support dynamic real-time querying.
> - **Why D is incorrect**: Authoring custom functions for every query variation is unmaintainable and prevents dynamic query generation.

---

### Question 8
**Scenario**: You are designing a complex multi-agent system for a logistics company. The system consists of an Order Ingestion Agent, a Route Optimization Agent, and a Fleet Dispatch Agent. When an order arrives, the Route Optimization Agent and Fleet Dispatch Agent must collaborate, negotiate constraints, and hand off execution state statefully.

**Which multi-agent protocol and orchestration pattern should you select?**
- **A)** Implement the **Agent2Agent (A2A)** protocol with a **Hierarchical Supervisor** pattern managed via Agent Registry and Agent Identity.
- **B)** Chain the agents into a rigid linear bash script that passes JSON files via local filesystem storage.
- **C)** Consolidate all three agent roles into a single monolithic LLM prompt with 50 tools.
- **D)** Use Google Cloud Pub/Sub with broadcast fan-out where all agents execute independently without state handoffs or coordination.

> **Correct Answer: A**
> **Explanation**:
> - **Why A is correct**: The **Agent2Agent (A2A)** protocol enables decentralized autonomous agents to discover capabilities, exchange messages, and hand off execution state. A **Hierarchical Supervisor** provides centralized coordination and routing while enforcing IAM boundaries through Agent Identity and Agent Registry.
> - **Why B is incorrect**: Bash scripts passing local files cannot scale across distributed cloud environments or support dynamic multi-turn agent negotiations.
> - **Why C is incorrect**: Monolithic prompts with excessive tools suffer from tool selection confusion, high latency, and degraded reasoning quality.
> - **Why D is incorrect**: Uncoordinated Pub/Sub broadcasting lacks stateful handoff and negotiation semantics.

---

## Domain 4: Evaluating and Deploying Agentic Workflows (~22%)

### Question 9
**Scenario**: Before promoting a new customer service agent to production, your team needs to evaluate its performance against 500 historical customer interactions. The evaluation must verify: (1) Did the agent select the right refund tool? (2) Were the generated refund parameters exact? (3) Was the agent's explanation faithful to company policy?

**What is the recommended evaluation architecture on Google Cloud?**
- **A)** Have senior customer support agents manually read all 500 conversation transcripts in Google Cloud Logging.
- **B)** Use **ADK evaluation tooling (`evalset`)** with a curated **Golden Dataset** and deploy an **Agent Platform Gen AI Autorater (using Gemini 3.7 Flash)** to score tool precision and answer faithfulness automatically.
- **C)** Compute traditional BLEU and ROUGE scores against human reference responses.
- **D)** Run simple Python unit tests verifying that the agent returns HTTP 200 OK status codes.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: ADK `evalset` combined with Golden Datasets and LLM-as-a-judge autoraters (powered by Gemini 3.7 Flash) provides multi-dimensional, automated evaluation. It measures tool selection accuracy, argument exactness, and factual faithfulness against ground truth.
> - **Why A is incorrect**: Manual review of 500 multi-turn transcripts is slow, expensive, and cannot be integrated into automated CI/CD pipelines.
> - **Why C is incorrect**: BLEU and ROUGE measure n-gram lexical overlap, which fails completely for evaluating tool calls, multi-turn reasoning, or semantic correctness.
> - **Why D is incorrect**: HTTP 200 OK only verifies server availability, not agent reasoning accuracy or tool correctness.

---

### Question 10
**Scenario**: In production, your monitoring dashboard alerts you that an autonomous research agent is occasionally getting trapped in an infinite reasoning loop, making 40+ consecutive web search tool calls with slightly varied keywords when researching obscure topics, leading to high latency and cost spikes.

**Which set of mitigations should you implement?**
- **A)** Disable the web search tool entirely and rely solely on the LLM's internal pre-trained weights.
- **B)** Configure a strict `max_turns` execution budget, implement a cycle-detection interceptor hook in the ADK agent runtime, and inject a reflection prompt when duplicate queries are detected.
- **C)** Increase the Cloud Run container memory and CPU limits to allow the agent to execute indefinitely.
- **D)** Switch the model to Gemini 2.5 Flash-Lite to reduce token costs during the infinite loops.

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: Preventing agent reasoning loops requires multi-layer defense: setting a hard turn limit (`max_turns=5` or `10`), implementing lifecycle hooks to detect repetitive/stagnant tool calls, and dynamically steering the agent with a reflection prompt to summarize findings or ask for clarification.
> - **Why A is incorrect**: Disabling search removes the core research capability of the agent.
> - **Why C is incorrect**: Increasing compute limits worsens cost spikes and does not solve the algorithmic logic loop.
> - **Why D is incorrect**: Switching models does not solve the loop condition and degrades research quality.

---

## Domain 5: Securing and Governing Agentic Workflows (~15%)

### Question 11
**Scenario**: An enterprise financial services firm is deploying an autonomous agent that can query account balances and initiate wire transfers up to $10,000. Corporate risk policies dictate that: (1) The agent must never initiate transfers over $1,000 without verified manager sign-off. (2) Prompt injection attacks must be inspected. (3) The agent identity must have a resource ceiling that excludes all unapproved projects and tools.

**Which security architecture fulfills all compliance requirements?**
- **A)** Implement **Agent Gateway** with **Model Armor** for prompt injection inspection, enforce a **Principal Access Boundary (PAB)** on the agent's **Agent Identity**, and add a **Human-In-The-Loop (HITL)** approval gate for transactions > $1,000.
- **B)** Place the agent on a public Cloud Run URL and write regex filters in Python to check for words like "wire" and "transfer".
- **C)** Give the agent admin Service Account permissions and require the user to enter their personal password in the chat prompt.
- **D)** Run the agent on a private VM with no IAM roles and disable external API authentication.

> **Correct Answer: A**
> **Explanation**:
> - **Why A is correct**:
>   - **Model Armor** on **Agent Gateway** intercepts prompt injection and jailbreak attempts before LLM processing.
>   - **Agent Identity** with a **Principal Access Boundary (PAB)** caps the resources the principal can reach; normal IAM grants are still required. VPC Service Controls is a separate perimeter control.
>   - **Human-In-The-Loop (HITL)** deterministic gates pause execution and require authenticated human approval for high-risk tool operations.
> - **Why B is incorrect**: Python regex filters are easily bypassed with prompt obfuscation and do not provide enterprise IAM scoping or HITL governance.
> - **Why C is incorrect**: Admin service accounts violate least privilege, and asking users for passwords in chat prompts is a critical security vulnerability.
> - **Why D is incorrect**: Disabling authentication prevents auditing and violates cloud security policies.

---

### Question 12
**Scenario**: A healthcare agent processes patient medical records. You must ensure that Personal Identifiable Information (PII) and Protected Health Information (PHI) like Social Security Numbers and medical condition codes are masked both before the prompt reaches Gemini and when the agent outputs responses to external APIs.

**Which Google Cloud security service should be integrated into the Agent Gateway?**
- **A)** Cloud Armor Web Application Firewall (WAF)
- **B)** **Sensitive Data Protection (Cloud DLP)** integrated with **Model Armor** sanitization filters
- **C)** Secret Manager
- **D)** Cloud Key Management Service (Cloud KMS)

> **Correct Answer: B**
> **Explanation**:
> - **Why B is correct**: **Sensitive Data Protection (Cloud DLP)** combined with **Model Armor** provides automated real-time inspection, de-identification, masking, and redaction of PII/PHI (SSNs, medical record numbers, names) in both prompt inputs and agent outputs.
> - **Why A is incorrect**: Cloud Armor protects against DDoS and Layer 7 web attacks (SQLi, XSS), but does not inspect or redact unstructured semantic PII in LLM payloads.
> - **Why C is incorrect**: Secret Manager stores API keys and database credentials, not real-time payload sanitization.
> - **Why D is incorrect**: Cloud KMS handles cryptographic key encryption at rest/transit, not contextual data de-identification.

---

## Additional Cross-Domain Scenarios

### Question 13 - Select two

**Scenario**: A team is promoting a RAG agent after it passes response-style reviews. In production, users report that answers are fluent but cite irrelevant documents. Which two changes most directly address the release failure?

- **A)** Add retrieval relevance/groundedness cases to a golden dataset and gate releases on them.
- **B)** Increase Cloud Run CPU so the model can write longer answers.
- **C)** Trace retrieval candidates, similarity scores, reranking, citations, and end-to-end latency.
- **D)** Replace all human-authored questions with synthetic easy questions.
- **E)** Disable citations because users find them distracting.

> **Correct Answers: A and C**
> **Explanation**: The failure is retrieval quality, not prose style or compute. A representative golden set makes it testable; traces identify whether candidate generation, filters, reranking, or latency caused the miss.

### Question 14

**Scenario**: An agent needs managed sessions, long-term memory, agent-specific evaluation integration, and the least operational overhead. It does not require custom Kubernetes scheduling.

- **A)** GKE Autopilot
- **B)** Agent Runtime
- **C)** A Compute Engine managed instance group
- **D)** Cloud Run jobs

> **Correct Answer: B**
> **Explanation**: Agent Runtime is the agent-specific managed choice. Cloud Run is a strong portable HTTP/container option when managed agent features are not the deciding requirement; GKE is justified by Kubernetes-level control.

### Question 15 - Select two

**Scenario**: A registered billing agent presents a valid OAuth token to Agent Gateway but requests an unapproved `delete_invoice` tool. Which two statements are correct?

- **A)** The valid token requires the gateway to allow the request.
- **B)** Agent Gateway should deny the tool through capability policy and audit the decision.
- **C)** Agent Registry metadata can define the approved agent version, identity, owner, and capabilities used by the gateway.
- **D)** Model Armor should grant the missing tool permission after inspecting the prompt.
- **E)** A PAB grants `delete_invoice` because it is narrower than project admin.

> **Correct Answers: B and C**
> **Explanation**: Authentication is not authorization. Registry supplies governed inventory/capability metadata, while Gateway enforces traffic policy. Model Armor inspects content; PAB caps resources and does not grant a permission.

### Question 16

**Scenario**: A supervisor agent needs to delegate a route-planning task to a separately deployed specialist. The specialist itself needs access to a map database tool. Which protocol mapping is correct?

- **A)** Use MCP for the supervisor-to-specialist handoff and A2A for the specialist-to-database call.
- **B)** Use A2A for the supervisor-to-specialist handoff and MCP for specialist tool/database access.
- **C)** Use OAuth for both message semantics and database schema discovery.
- **D)** Use Agent Registry as the message transport for both calls.

> **Correct Answer: B**
> **Explanation**: A2A handles agent-to-agent delegation and handoff. MCP exposes tools/context to an agent-facing client. OAuth can authenticate calls, and Registry can describe agents, but neither replaces the interaction protocol.
