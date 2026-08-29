# Module 03: Agentic Strategy & Model Selection

## Overview
This module covers strategic model selection for enterprise agent architectures on Google Cloud. You will learn how to evaluate LLMs vs SLMs, calibrate dynamic thinking budgets for **Gemini 3.7 Flash**, and optimize cost-latency-accuracy trade-offs across diverse agentic workloads.

---

## 🎯 Exam Objectives Covered
- **3.1 Designing and building agentic workflows in code**
  - Selecting and configuring the appropriate language model (LLM vs SLM, self-hosted vs SaaS, OSS vs proprietary).
  - Configuring **Gemini 3.7 Flash** with thinking budgets (`thinking_config`) for complex multi-step reasoning.
  - Analyzing trade-offs between cost, context window limits, TTFT latency, and tool proficiency.

---

## 📊 Model Selection Decision Matrix

```mermaid
graph TD
    Start[Agent Task Ingestion] --> Question{Task Complexity?}
    Question -->|High: Multi-Step Tool Reasoning & Coding| G37[Gemini 3.7 Flash (Dynamic Thinking: 1024-4096)]
    Question -->|Extreme: Deep Mathematical Proofs / 1M+ Docs Audit| G25P[Gemini 2.5 Pro]
    Question -->|Simple: Classification, Intent Routing, Extraction| G25FL[Gemini 2.5 Flash-Lite]
    Question -->|Edge / Air-Gapped / Zero Cloud Cost| Gemma[Gemma 2 9B via LiteRT / Model Garden]
```

---

## 💰 Cost & Latency Benchmark Table

| Model Tier | Cost per 1M Input Tokens | Cost per 1M Output Tokens | Reasoning / Thinking Support | Recommended Agent Role |
| :--- | :---: | :---: | :---: | :--- |
| **Gemini 3.7 Flash** | **$0.075 - $0.15** | **$0.30 - $0.60** | ✅ Dynamic (128 – 64k tokens) | **Default Core Agent Engine**: Multi-tool, multi-turn, code generation |
| **Gemini 2.5 Pro** | $1.25 - $2.50 | $5.00 - $10.00 | ✅ Deep built-in reasoning | Complex compliance audits, legal analysis, massive multi-doc synthesis |
| **Gemini 2.5 Flash-Lite** | $0.0375 | $0.15 | ❌ Fast deterministic | Intent classification, message routing, basic JSON extraction |
| **Gemma 2 (2B / 9B / 27B)** | Infrastructure compute only | Infrastructure compute only | ❌ Fine-tunable SLM | On-device, edge gateways, offline air-gapped environments |

---

## 🚀 Hands-on Lab: Running the Module

```bash
# Run the model selection matrix and thinking budget estimator
python3 modules/03_agentic_strategy_and_prototyping/model_selection_matrix.py

# Run unit tests
pytest modules/03_agentic_strategy_and_prototyping/tests/ -v
```

---

## 🧹 Resource Cleanup / Teardown

This module calculates cost and latency matrices in memory and does not leave persistent cloud infrastructure.

```bash
# Clean local cache & Python bytecode
rm -rf __pycache__ .pytest_cache
```

