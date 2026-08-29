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

![Google Cloud AI Agent Security & Governance Architecture](../../assets/diagrams/security_model_armor.jpg)

---

## 🚀 Hands-on Lab: Running the Module

```bash
# Run the security guardrails and HITL lab
python3 modules/13_production_deployment_and_security/security_guardrails.py

# Run unit tests
pytest modules/13_production_deployment_and_security/tests/ -v
```

---

## 🧹 Resource Cleanup / Teardown

To delete the deployed **Cloud Run** service, container images, and IAM bindings:

```bash
# 1. Delete Cloud Run Service
gcloud run services delete agent-gateway --region=$REGION --project=$PROJECT_ID --quiet

# 2. Delete Container Images from Artifact Registry
gcloud artifacts repositories delete agent-repo --location=$REGION --project=$PROJECT_ID --quiet 2>/dev/null || true

# 3. Clean local cache & Python bytecode
rm -rf __pycache__ .pytest_cache
```

