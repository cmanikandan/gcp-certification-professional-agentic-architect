# Module 12: AgentOps: Evaluation & Observability

## Overview
This module explores enterprise AgentOps on Google Cloud. You will learn to build automated evaluation pipelines using **ADK evalset**, create golden datasets, deploy **LLM-as-a-Judge Autoraters (Gemini 3.7 Flash)**, and instrument distributed tracing with **Google Cloud Trace** and **Cloud Logging**.

---

## 🎯 Exam Objectives Covered
- **4.1 Evaluating agents in development and in production**
  - Creating golden evaluation test sets (prompts, edge cases, expected tools).
  - Continuous evaluation pipelines using ADK `evalset` and custom autoraters.
  - Computing quantitative evaluation metrics: Tool Precision, Retrieval Faithfulness, Answer Relevance.
- **4.2 Deploying and scaling production workloads**
  - Distributed tracing and latency bottleneck profiling using Cloud Trace and Cloud Logging.

---

## 📊 Evaluation & Tracing Architecture

![Google Cloud AgentOps Architecture](../../assets/diagrams/agentops_eval_tracing.jpg)

---

## 🚀 Hands-on Lab: Running the Module

```bash
# Run the agent evaluation and tracing lab
python3 modules/12_agentops_evaluation_and_monitoring/agent_evaluator.py

# Run unit tests
pytest modules/12_agentops_evaluation_and_monitoring/tests/ -v
```

---

## 🧹 Resource Cleanup / Teardown

If you configured live **Google Cloud Logging** sinks or **Cloud Trace** log exports:

```bash
# 1. Delete custom log sinks
gcloud logging sinks delete agentops-eval-sink --project=$PROJECT_ID --quiet 2>/dev/null || true

# 2. Clean local cache & Python bytecode
rm -rf __pycache__ .pytest_cache *.log
```

