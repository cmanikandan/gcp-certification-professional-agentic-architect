# Hands-on Lab Runbook

Every module has the same contract:

- `run_lab.sh` runs the demonstration and that module's tests.
- The default path is deterministic, offline, and non-billable.
- `cleanup.sh` removes only that module's local generated artifacts and is safe to run repeatedly.
- Optional live-cloud work is explicitly labeled and requires exact project/resource identifiers. The default lab never creates cloud resources.

## One-time setup

```bash
./scripts/setup_environment.sh
```

Do not put credentials in source files or command history. Use Application Default Credentials or a local ignored `.env` only for an explicitly chosen live exercise.

## Run one module

```bash
./modules/09_enterprise_rag_and_vector_search/run_lab.sh
./modules/09_enterprise_rag_and_vector_search/cleanup.sh
```

The wrappers resolve the repository path themselves, so they work from any current directory. Set `PYTHON_BIN=/path/to/python` only if you do not want to use the repository `.venv`.

## Verify all modules

```bash
./scripts/verify_labs.sh
```

This executes and cleans every module independently. It is also used in CI so a missing entry point, cleanup script, import, or dependency fails the build.

## Live API exercise

Module 05 is offline by default even when `GEMINI_API_KEY` exists. A billable call requires explicit opt-in:

```bash
python3 modules/05_agent_development_kit_adk/custom_adk_agent.py --live
```

The live call creates no persistent infrastructure, but it can incur model usage charges. Run the module cleanup afterward to clear local test artifacts.

## Lab debrief

After each lab, answer these four prompts without looking at the README:

1. Which official objective did this lab exercise?
2. What requirement caused the selected Google Cloud service or pattern to win?
3. Which two plausible alternatives would appear as distractors, and why are they wrong here?
4. What identity, data, safety, evaluation, cost, and cleanup controls are still required in production?
