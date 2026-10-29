---
name: my-custom-skill
description: >-
  Audits Google Cloud IAM bindings and Terraform plans for least-privilege
  compliance before deployment. Use when reviewing IAM roles or running
  pre-deployment security checks.
license: Apache-2.0
compatibility: gemini-3.7-flash
allowed_tools: "view_file, run_command"
metadata:
  author: "Agentic Architect Study Repo"
  approval_gate: "required"
---
# Skill: Enterprise IAM & Pre-Deployment Auditor

Use this skill whenever the user asks to validate IAM roles or run pre-flight security checks.

## Workflow
1. Read the least-privilege role table in `references/iam_runbook.md` only if IAM bindings are modified.
2. Execute `scripts/validate.py` via `run_command` to verify policy conformance.
3. Require Human-in-the-Loop (HITL) approval before applying changes.
