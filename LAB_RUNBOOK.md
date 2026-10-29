# Hands-on Lab Runbook

> [!IMPORTANT]
> **Personal, unofficial repository.** This is a personal study project. It is **not
> affiliated with, endorsed by, or maintained by Google or Google Cloud**. For official
> guidance — exam objectives, registration, policies, and the current exam guide — refer to
> **[cloud.google.com/learn/certification/agentic-architect](https://cloud.google.com/learn/certification/agentic-architect)**.
> Any Google Cloud charges incurred by running the `--live` path are your own.
> See [`DISCLAIMER.md`](DISCLAIMER.md) for the full disclaimer.

Every one of the **20 labs** follows a strict authoring contract:
- `run_lab.sh` executes the lab code and its `pytest` verification suite.
- The default execution path is **100% deterministic, offline, and free ($0)**. Only passing `--live` touches Google Cloud APIs.
- `cleanup.sh` idempotently removes any local scratch state and remote resources created by the lab.

## Environment Setup

The repository uses a virtual environment (`.venv-adk`, Python >= 3.10). To build or refresh it locally:

```bash
python3 -m venv .venv-adk
source .venv-adk/bin/activate
pip install -r requirements.txt
```

### Why ADK Extras & Cloud Packages Matter (Exam Troubleshooting!)
The `google-adk` package gates enterprise integrations behind optional extras. Importing an integration without its extra raises an explicit `ImportError` naming the missing extra — a realistic exam troubleshooting stem:

- `google-adk[agent-identity]`: Unlocks `integrations.agent_identity` (`GcpAuthProvider`) and `integrations.agent_registry` (`AgentRegistry`).
- `google-adk[gcp]`: Unlocks Model Armor (`ModelArmorPlugin`, `google-cloud-modelarmor`).
- `google-adk[a2a]`: Unlocks A2A protocol support (`a2a-sdk`, `RemoteA2aAgent`, `A2aRemoteAgentConfig`).
- `google-adk[extensions]`: Unlocks `GkeCodeExecutor` (`sandbox` gVisor vs `job` modes).
- Companion Cloud SDKs installed in `.venv-adk`: `google-cloud-modelarmor` (`SdpAdvancedConfig`), `google-cloud-discoveryengine` (`RankServiceClient`), `google-cloud-agentidentitycredentials`, and `google-cloud-iamconnectorcredentials`.

## Offline vs. Live Contract & Least-Privilege ADC Setup

By default, running any lab exercises real ADK 2.9.0 and Google Cloud SDK classes offline without making billable network calls.

To run a live exercise against a sandbox Google Cloud project, pass `--live`. Verify your active `gcloud` identity, Application Default Credentials (ADC) quota alignment, and **least-privilege IAM roles** first (never create static JSON Service Account keys!):

```bash
gcloud auth list
gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
```

Minimum roles typically needed on your sandbox test project for `--live` runs:
- `roles/aiplatform.user` (Gemini, RAG Engine, Memory Bank, Managed Sessions)
- `roles/discoveryengine.viewer` (Agent Search & Ranking API)
- `roles/modelarmor.user` (Model Armor prompt/response screening)
- `roles/cloudtrace.agent` and `roles/logging.logWriter` (OpenTelemetry export)

## Running & Verifying Labs

### Run One Lab
```bash
./tracks/03_custom_agents/lab_08_adk_fundamentals/run_lab.sh
./tracks/03_custom_agents/lab_08_adk_fundamentals/cleanup.sh
```

### Run via Interactive CLI (`cli.py`)
```bash
./.venv-adk/bin/python cli.py --all        # Run all 20 lab test suites
./.venv-adk/bin/python cli.py --cleanup    # Run all 20 cleanup scripts
```

### Run Full Repository Contract & Lab Suite
```bash
./scripts/verify_labs.sh
```
This runs repository-wide contract checks (`tests/test_lab_contract.py`, `tests/test_diagrams.py`, `tests/test_no_stale_facts.py`) plus every lab test suite across all 5 tracks.

## Troubleshooting

| Failure Mode | Symptom | Fix |
| :--- | :--- | :--- |
| **Missing ADK Extras** | `ImportError` importing `GkeCodeExecutor`, `ModelArmorPlugin`, or `RemoteA2aAgent` | Run `pip install "google-adk[agent-identity,gcp,a2a,extensions]"` |
| **Missing ADC** | `DefaultCredentialsError` / `401 UNAUTHENTICATED` on `--live` | Run `gcloud auth application-default login` (never download JSON keys) |
| **Quota Project Mismatch** | `403 PERMISSION_DENIED` (`CONSUMER_INVALID` or quota project missing) | Run `gcloud auth application-default set-quota-project <PROJECT_ID>` |
| **Missing BigQuery Job Role** | `403 Access Denied: Project ...: User does not have bigquery.jobs.create` | Grant `roles/bigquery.jobUser` on the execution project in addition to dataset `roles/bigquery.dataViewer` |
| **Region Availability** | `400 Unsupported region` on preview endpoints | Set `GOOGLE_CLOUD_LOCATION=us-central1` in `.env` |
