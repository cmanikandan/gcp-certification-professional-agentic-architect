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

The lab now exercises the complete request chain: versioned Agent Registry entry, OAuth audience/scope validation, Agent Gateway capability policy, Model Armor inspection, Agent Identity resource ceiling through PAB, runtime selection, and HITL approval.

The optional Cloud Run deployment is private by default (`--no-allow-unauthenticated`) and relies on workload identity/Application Default Credentials. Do not pass long-lived model API keys as plain environment variables; use identity-based access or Secret Manager when a secret is unavoidable.

---

## 🛡️ Enterprise Security & Governance Architecture

![Google Cloud AI Agent Security & Governance Architecture](../../assets/diagrams/security_model_armor.jpg)

---

## High-yield exam checkpoint

Layer the controls: Registry inventories and versions, Identity names the workload, OAuth delegates scoped access, IAM grants, PAB caps reachable resources, Gateway enforces traffic policy, Model Armor inspects content, and HITL gates high-impact actions. PAB and VPC Service Controls are not the same control.

---

## 🚀 Hands-on Lab: Running the Module

The supported entrypoint runs both the demonstration and this module's tests from any current directory:

```bash
./modules/13_production_deployment_and_security/run_lab.sh
```

Equivalent manual commands:

```bash
# Run the security guardrails and HITL lab
python3 modules/13_production_deployment_and_security/security_guardrails.py

# Run unit tests
pytest modules/13_production_deployment_and_security/tests/ -v
```

---

## 🧹 Resource Cleanup / Teardown

Always finish with the idempotent module cleanup:

```bash
./modules/13_production_deployment_and_security/cleanup.sh
```

To delete the deployed **Cloud Run** service, container images, and IAM bindings:

```bash
# 1. Delete Cloud Run Service
gcloud run services delete agent-gateway --region=$REGION --project=$PROJECT_ID --quiet

# 2. Delete Container Images from Artifact Registry
gcloud artifacts repositories delete agent-repo --location=$REGION --project=$PROJECT_ID --quiet 2>/dev/null || true

# 3. Clean local cache & Python bytecode
rm -rf __pycache__ .pytest_cache
```
