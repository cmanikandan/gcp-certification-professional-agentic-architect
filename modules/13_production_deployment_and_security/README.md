# Module 13: Production Deployment, Security & Governance

## Overview
This module covers enterprise production deployment and multi-layered security governance on Google Cloud. You will learn to containerize agents for **Cloud Run** and **Agent Runtime**, enforce **Model Armor** prompt injection defenses, scope IAM permissions via **Agent Identity Principal Access Boundaries (PAB)**, and implement **Human-in-the-Loop (HITL)** approval gates.

---

## 🎯 Exam Objectives Covered
- **4.2 Deploying and scaling production workloads**
  - Selecting optimal deployment runtimes (Agent Runtime, Cloud Run, GKE).
  - Production containerization, health checks (`/healthz`), and autoscaling.
- **5.1 Configuring agent security and governance**
  - Authentication and secure tool execution using OAuth 2.0 and Auth Manager.
  - Configuring Principal Access Boundary (PAB) policies using **Agent Identity**.
  - Deploying **Agent Gateway** for traffic inspection, rate limiting, and Model Armor guardrails.
- **5.2 Implementing secure agent behavior and execution**
  - Designing safety guardrails against prompt injection, jailbreaks, and PII leakage (Sensitive Data Protection).
  - Integrating deterministic **Human-in-the-Loop (HITL)** gates for high-risk operations.

---

## 🛡️ Enterprise Security & Governance Architecture

```mermaid
graph TD
    Client[End User / External API] --> Gateway[Agent Gateway (OAuth 2.0 Auth Manager)]
    Gateway --> ModelArmor[Model Armor: Prompt Injection & Jailbreak Filter]
    ModelArmor -->|Sanitized Prompt| Identity[Agent Identity with Principal Access Boundary PAB]
    Identity --> AgentCore[Agent Runtime on Cloud Run (Gemini 3.7 Flash)]
    AgentCore --> ToolEvaluation{High-Risk Action? e.g. Wire Transfer > $1,000}
    ToolEvaluation -->|Yes| HITL[Human-In-The-Loop (HITL) Gate: Approval Required]
    ToolEvaluation -->|No| Execute[Direct Tool Execution]
    HITL -->|Manager Approved| Execute
    Execute --> DLP[Sensitive Data Protection DLP: PII Masking]
    DLP --> Response[Final Clean Response to Client]
```

---

## 🚀 Hands-on Lab: Running the Module

```bash
# Run the security guardrails and HITL lab
python3 modules/13_production_deployment_and_security/security_guardrails.py

# Run unit tests
pytest modules/13_production_deployment_and_security/tests/ -v
```
