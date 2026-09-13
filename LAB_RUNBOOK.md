# Hands-on Lab Runbook

Every lab follows a strict authoring contract:
- `run_lab.sh` executes the lab code and its test suite.
- The default execution path is deterministic, offline, and non-billable. Only a `--live` flag touches Google Cloud.
- `cleanup.sh` cleanly removes all local and remote resources created by the lab.

## Environment Setup

The repository uses a pre-built virtual environment (`.venv-adk`). If you need to rebuild it or run locally:

```bash
python3.10 -m venv .venv-adk
source .venv-adk/bin/activate
pip install -r requirements.txt
```

### Why ADK Extras Matter
The `google-adk` package requires specific extras to unlock exam-relevant integrations. If you miss them, you will see a precise `ImportError` naming the extra. This maps directly to troubleshooting scenarios on the exam.

- `google-adk[agent-identity]`: Unlocks `integrations.agent_identity` and `integrations.agent_registry`.
- `google-adk[gcp]`: Unlocks Model Armor (`google-cloud-modelarmor`).
- `google-adk[a2a]`: Unlocks A2A support (`a2a-sdk`).
- `google-adk[extensions]`: Unlocks `GkeCodeExecutor`.

## Offline vs. Live Contract

By default, running a lab exercises the real ADK class structures without hitting network endpoints. The model inference calls are stubbed to keep execution fast and free.

To run a live exercise against Google Cloud, use the `--live` flag.
For live paths, you must verify your active identity and quota project using Application Default Credentials (ADC):
```bash
gcloud auth list
gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
```

You can optionally define environment variables in a local `.env` file (copy `.env.example` to `.env`).

## Running the Labs

### Run One Lab
```bash
cd tracks/03_custom_agents/lab_08_adk_fundamentals
./run_lab.sh
./cleanup.sh
```

### Verify All Labs
```bash
./scripts/verify_labs.sh
```
This executes every test suite and cleanup script across all tracks to guarantee the repository is green.

## Cost Control

- Labs run offline by default and incur **$0**.
- Running with `--live` will hit real endpoints. Most labs use minimal tokens (under $0.05), but long-running multi-agent loops can accumulate charges.
- Ensure you run `./cleanup.sh` after every `--live` execution, as it deletes any active cloud resources.

## Troubleshooting

| Failure Mode | Symptom | Fix |
| :--- | :--- | :--- |
| **Missing ADK Extras** | `ImportError` when importing `GkeCodeExecutor` or A2A modules | Run `pip install google-adk[extensions]` or the specific missing extra. |
| **Missing ADC** | Default credentials not found / 401 Unauthorized | Run `gcloud auth application-default login` |
| **Quota Project Mismatch** | 403 Forbidden on Vertex AI | Run `gcloud auth application-default set-quota-project <PROJECT_ID>` |
| **Stale Virtualenv** | Module not found errors | `rm -rf .venv-adk` and re-run setup |
| **Region Availability** | 400 Unsupported region | Set your region to `us-central1` |
