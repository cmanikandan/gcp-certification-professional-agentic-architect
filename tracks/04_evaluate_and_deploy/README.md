# Track 4 — Evaluating and deploying agentic workflows

This track covers approximately 22% of the Google Cloud Certified Professional Agentic Architect (beta) exam.

It is broken down into three labs:

* **Lab 13: Agent Evaluation** (Objective 4.1): Creating test sets, golden data, and continuous evaluation pipelines using the ADK `AgentEvaluator` and `.evalset.json` tooling. Also compares LLM-as-judge autoraters vs programmatic rubrics.
* **Lab 14: Deployment Runtimes** (Objective 4.2): Selecting the optimal deployment runtime (Agent Runtime vs Cloud Run vs GKE) based on cost, operational burden, and use case requirements.
* **Lab 15: Observability and Troubleshooting** (Objective 4.2): Monitoring agent loops, tool invocation latency, and hallucinations using OpenTelemetry, Cloud Trace, and ADK telemetry controls (`RunConfig.max_llm_calls`, `LoopAgent.max_iterations`).
