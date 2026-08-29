---
name: gcp-ops-skill
description: Automated runbook for deploying and verifying Google Cloud Run agent services and IAM Principal Access Boundaries.
---

# Google Cloud Operations Skill

Use this skill when deploying, restarting, or auditing Cloud Run agent services.

## Operational Workflow
1. Verify GCP project ID and region: `gcloud config get-value project`
2. Audit service IAM policies to verify Principal Access Boundary (PAB).
3. Validate container health endpoint `/healthz` returning HTTP 200.
4. Check Cloud Trace logs for latency spikes or reasoning bottlenecks.
