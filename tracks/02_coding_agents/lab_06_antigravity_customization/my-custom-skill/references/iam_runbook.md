# Enterprise Coding-Agent IAM Runbook (L3 Reference)

- **Vertex AI model invocation:** `roles/aiplatform.user`
- **Cloud Workstations developer launch:** `roles/workstations.user`
- **Remote Cloud Run MCP server invocation:** `roles/run.invoker` (+ `roles/iap.httpsResourceAccessor` for IAP)
- **GKE Sandbox image pull:** `roles/artifactregistry.reader` + Workload Identity (`roles/iam.workloadIdentityUser`)
