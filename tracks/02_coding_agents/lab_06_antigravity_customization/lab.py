"""Lab 06 — Antigravity Customization, Enterprise Governance & Agents CLI.

Covers Section 2.2 (and 3.1 CLI modes):
  - Progressive-disclosure Skills (`skills/<name>/SKILL.md`, `list_skills_in_dir`
    L1 vs `load_skills_from_dir` L2/L3, and `GCPSkillRegistry`).
  - Workspace & directory Rules (`GEMINI.md` / `AGENTS.md` walk-up with no YAML
    frontmatter vs `rules/*.md` triggers: `always_on`, `model_decision`, `glob`,
    `manual`, plus path deduplication).
  - Lifecycle Hooks (`hooks.json`: `PreToolUse` `allow`/`deny`/`ask`/`force_ask`
    + shallow `overwrite`, `PostToolUse`, `PreInvocation`, `PostInvocation`, and
    `Stop` `"continue"` gate).
  - Shareable Plugins (`plugin.json`), JSON config inheritance (`skills.json`
    `inherits` / `entries` with `include_only` / `exclude`), and Subagent depth
    controls (`max_subagent_depth`, `allowed_subagents`, `commandExecutionPolicy`).
  - Antigravity SDK 9-level policy precedence (`Specific Deny` -> `Global Allow`)
    and fail-closed `when=` argument predicates.
  - Augmenting Antigravity with Agents CLI (`adk`): `eval`, `optimize` (GEPA),
    `deploy`, and Agent Mode vs. Human Mode.
"""

from __future__ import annotations

import copy
import fnmatch
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml
from google.adk.integrations.skill_registry import GCPSkillRegistry
from google.adk.skills import (
    Frontmatter,
    Skill,
    list_skills_in_dir,
    load_skill_from_dir,
    load_skills_from_dir,
)

from common import DEFAULT_AGENT_MODEL, LabConfig, load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, table


# ---------------------------------------------------------------------------
# 1. ADK Skills & Progressive Disclosure (L1 -> L2 -> L3)
# ---------------------------------------------------------------------------


def create_enterprise_skill(
    skills_root: str | Path,
    skill_name: str = "enterprise-security-auditor",
) -> Path:
    """Create a realistic enterprise skill with L1 frontmatter, L2 body, and L3 files."""
    skill_dir = Path(skills_root) / skill_name
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)

    skill_md = (
        "---\n"
        f"name: {skill_name}\n"
        "description: Audits Terraform and IAM bindings against zero-trust policies.\n"
        "license: Apache-2.0\n"
        f"compatibility: {DEFAULT_AGENT_MODEL}\n"
        "allowed_tools: view_file, run_command, mcp_iam_analyzer\n"
        "metadata:\n"
        "  approval_gate: required\n"
        "  owner_team: cloud-security\n"
        "---\n"
        "# Security Auditor Workflow (L2 Instructions)\n\n"
        "1. Read `references/least_privilege_matrix.md` when IAM roles change.\n"
        "2. Run `scripts/check_iam.py` before proposing approval.\n"
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (skill_dir / "references" / "least_privilege_matrix.md").write_text(
        "Prefer roles/aiplatform.user, roles/workstations.user, roles/run.invoker.\n",
        encoding="utf-8",
    )
    (skill_dir / "scripts" / "check_iam.py").write_text(
        "#!/usr/bin/env python3\nprint('IAM check ok')\n",
        encoding="utf-8",
    )
    return skill_dir


# ---------------------------------------------------------------------------
# 2. Rules Discovery: GEMINI.md / AGENTS.md vs rules/*.md Triggers
# ---------------------------------------------------------------------------

VALID_RULE_TRIGGERS = ("always_on", "model_decision", "glob", "manual")


@dataclass(frozen=True)
class LoadedRule:
    """Resolved rule metadata after hierarchical discovery and trigger filtering."""

    resolved_path: Path
    kind: str  # "directory_rule" | "triggered_rule"
    trigger: str
    active_immediately: bool
    listed_for_model_decision: bool
    body: str


def _split_frontmatter(markdown_text: str) -> tuple[dict[str, Any] | None, str]:
    """Split optional YAML frontmatter from Markdown body."""
    if not markdown_text.startswith("---\n"):
        return None, markdown_text
    end_idx = markdown_text.find("\n---\n", 4)
    if end_idx == -1:
        return None, markdown_text
    raw_yaml = markdown_text[4:end_idx]
    body = markdown_text[end_idx + 5 :]
    parsed = yaml.safe_load(raw_yaml) or {}
    if not isinstance(parsed, dict):
        raise ValueError("Rule frontmatter must parse to a YAML mapping.")
    return parsed, body


def discover_and_resolve_rules(
    *,
    cwd: Path,
    repo_root: Path,
    open_files: list[str] | None = None,
    mentioned_rules: set[str] | None = None,
    extra_rule_dirs: list[Path] | None = None,
) -> tuple[list[LoadedRule], list[str]]:
    """Simulate Antigravity rule discovery, trigger evaluation, and deduplication.

    Verified Antigravity behavior:
      - Standalone ``GEMINI.md`` and ``AGENTS.md`` files sit directly in any
        directory, do **not** support YAML frontmatter, and are loaded by walking
        up from ``cwd`` to ``repo_root``.
      - Markdown files inside ``_agents/rules/`` or ``~/.gemini/config/rules/``
        support YAML frontmatter ``trigger``:
          * ``always_on``: always injected into context.
          * ``model_decision``: **requires** ``description``; only description is
            listed until the model chooses to read it.
          * ``glob``: **requires** ``globs`` (or ``glob``); activates when any
            open/edited file matches one of the comma-separated patterns.
          * ``manual``: activates only when ``@<rule-stem>`` is mentioned by user.
      - Rules are deduplicated by ``Path.resolve()``.
    """
    open_files = open_files or []
    mentioned_rules = mentioned_rules or set()
    extra_rule_dirs = extra_rule_dirs or []

    cwd_res = cwd.resolve()
    root_res = repo_root.resolve()
    seen_paths: set[Path] = set()
    loaded: list[LoadedRule] = []
    errors: list[str] = []

    # 1. Walk up from cwd -> repo_root for GEMINI.md / AGENTS.md
    cur = cwd_res
    walk_dirs: list[Path] = []
    while True:
        walk_dirs.append(cur)
        if cur == root_res or cur.parent == cur:
            break
        cur = cur.parent

    for directory in walk_dirs:
        for child in sorted(directory.iterdir()) if directory.is_dir() else []:
            if not child.is_file():
                continue
            if child.name.upper() not in {"GEMINI.MD", "AGENTS.MD"}:
                continue
            resolved = child.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            text = resolved.read_text(encoding="utf-8")
            fm, _ = _split_frontmatter(text)
            if fm is not None:
                errors.append(
                    f"{resolved.name}: standalone GEMINI.md / AGENTS.md files do not support YAML frontmatter."
                )
                continue
            loaded.append(
                LoadedRule(
                    resolved_path=resolved,
                    kind="directory_rule",
                    trigger="always_on",
                    active_immediately=True,
                    listed_for_model_decision=False,
                    body=text.strip(),
                )
            )

    # 2. Scan _agents/rules/*.md + extra_rule_dirs (e.g. ~/.gemini/config/rules)
    rule_dirs = [root_res / "_agents" / "rules", *extra_rule_dirs]
    for rdir in rule_dirs:
        if not rdir.is_dir():
            continue
        for rule_file in sorted(rdir.glob("*.md")):
            resolved = rule_file.resolve()
            if resolved in seen_paths:
                continue
            seen_paths.add(resolved)
            text = resolved.read_text(encoding="utf-8")
            fm, body = _split_frontmatter(text)
            if fm is None:
                loaded.append(
                    LoadedRule(
                        resolved_path=resolved,
                        kind="triggered_rule",
                        trigger="always_on",
                        active_immediately=True,
                        listed_for_model_decision=False,
                        body=text.strip(),
                    )
                )
                continue

            trigger = fm.get("trigger", "always_on")
            if trigger not in VALID_RULE_TRIGGERS:
                errors.append(
                    f"{resolved.name}: invalid trigger {trigger!r}; expected {VALID_RULE_TRIGGERS}."
                )
                continue

            if trigger == "always_on":
                loaded.append(
                    LoadedRule(
                        resolved_path=resolved,
                        kind="triggered_rule",
                        trigger="always_on",
                        active_immediately=True,
                        listed_for_model_decision=False,
                        body=body.strip(),
                    )
                )
            elif trigger == "model_decision":
                desc = fm.get("description")
                if not isinstance(desc, str) or not desc.strip():
                    errors.append(
                        f"{resolved.name}: trigger 'model_decision' requires a non-empty 'description' field."
                    )
                    continue
                loaded.append(
                    LoadedRule(
                        resolved_path=resolved,
                        kind="triggered_rule",
                        trigger="model_decision",
                        active_immediately=False,
                        listed_for_model_decision=True,
                        body=body.strip(),
                    )
                )
            elif trigger == "glob":
                raw_globs = fm.get("globs") or fm.get("glob")
                if not isinstance(raw_globs, str) or not raw_globs.strip():
                    errors.append(
                        f"{resolved.name}: trigger 'glob' requires a comma-separated 'globs' field."
                    )
                    continue
                patterns = [p.strip() for p in raw_globs.split(",") if p.strip()]
                matched = any(
                    fnmatch.fnmatch(os.path.basename(f), pat) or fnmatch.fnmatch(f, pat)
                    for f in open_files
                    for pat in patterns
                )
                loaded.append(
                    LoadedRule(
                        resolved_path=resolved,
                        kind="triggered_rule",
                        trigger="glob",
                        active_immediately=matched,
                        listed_for_model_decision=False,
                        body=body.strip(),
                    )
                )
            elif trigger == "manual":
                stem = resolved.stem
                matched = stem in mentioned_rules or resolved.name in mentioned_rules
                loaded.append(
                    LoadedRule(
                        resolved_path=resolved,
                        kind="triggered_rule",
                        trigger="manual",
                        active_immediately=matched,
                        listed_for_model_decision=False,
                        body=body.strip(),
                    )
                )

    return loaded, errors


# ---------------------------------------------------------------------------
# 3. Lifecycle Hooks (hooks.json) Validator & Simulator
# ---------------------------------------------------------------------------

GROUPED_HOOK_EVENTS = ("PreToolUse", "PostToolUse")
FLAT_HOOK_EVENTS = ("PreInvocation", "PostInvocation", "Stop")
ALL_HOOK_EVENTS = GROUPED_HOOK_EVENTS + FLAT_HOOK_EVENTS
PRE_TOOL_DECISIONS = ("allow", "deny", "ask", "force_ask")


def validate_hooks_json(hooks_doc: dict[str, Any]) -> list[str]:
    """Validate an Antigravity ``hooks.json`` configuration document."""
    errors: list[str] = []
    if not isinstance(hooks_doc, dict) or not hooks_doc:
        return ["hooks.json must be a non-empty JSON object keyed by hook name."]

    for hook_name, spec in hooks_doc.items():
        if not isinstance(spec, dict):
            errors.append(f"{hook_name}: hook spec must be an object.")
            continue
        if "enabled" in spec and not isinstance(spec["enabled"], bool):
            errors.append(f"{hook_name}: 'enabled' must be a boolean.")

        for key, val in spec.items():
            if key == "enabled":
                continue
            if key not in ALL_HOOK_EVENTS:
                errors.append(
                    f"{hook_name}: unknown event {key!r}; valid events are {ALL_HOOK_EVENTS}."
                )
                continue
            if not isinstance(val, list):
                errors.append(f"{hook_name}.{key}: must be a JSON array.")
                continue

            if key in GROUPED_HOOK_EVENTS:
                for idx, group in enumerate(val):
                    if not isinstance(group, dict) or "hooks" not in group:
                        errors.append(
                            f"{hook_name}.{key}[{idx}]: tool events must use grouped {{'matcher': ..., 'hooks': [...]}} format."
                        )
                        continue
                    for h_idx, handler in enumerate(group["hooks"]):
                        errors.extend(
                            _validate_hook_handler(f"{hook_name}.{key}[{idx}].hooks[{h_idx}]", handler)
                        )
            else:
                for h_idx, handler in enumerate(val):
                    if isinstance(handler, dict) and "hooks" in handler:
                        errors.append(
                            f"{hook_name}.{key}[{h_idx}]: {key} uses a flat handler array, not a 'matcher'/'hooks' wrapper."
                        )
                        continue
                    errors.extend(
                        _validate_hook_handler(f"{hook_name}.{key}[{h_idx}]", handler)
                    )
    return errors


def _validate_hook_handler(path_label: str, handler: Any) -> list[str]:
    errs: list[str] = []
    if not isinstance(handler, dict):
        return [f"{path_label}: handler must be an object."]
    h_type = handler.get("type", "command")
    if h_type != "command":
        errs.append(f"{path_label}: unsupported hook type {h_type!r}; only 'command' is supported.")
    cmd = handler.get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        errs.append(f"{path_label}: 'command' is required and must be a non-empty string.")
    timeout = handler.get("timeout", 30)
    if not isinstance(timeout, int) or timeout <= 0:
        errs.append(f"{path_label}: 'timeout' must be a positive integer (seconds).")
    return errs


def apply_pre_tool_use_response(
    stdin_payload: dict[str, Any],
    stdout_response: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Apply a ``PreToolUse`` hook stdout payload to a camelCase stdin toolCall.

    Exam nuance from hooks.md:
      - ``stdin`` keys are camelCase: ``conversationId``, ``workspacePaths``,
        ``toolCall`` (``name``, ``args``), ``stepIdx``.
      - ``decision`` must be one of ``allow``, ``deny``, ``ask``, ``force_ask``.
      - ``overwrite`` performs a **shallow, top-level** key replacement on
        ``toolCall.args`` (nested dictionaries are replaced wholesale, NOT
        deep-merged).
    """
    required_camel_keys = {"conversationId", "workspacePaths", "toolCall", "stepIdx"}
    missing = required_camel_keys - set(stdin_payload.keys())
    if missing:
        raise ValueError(f"PreToolUse stdin payload missing camelCase keys: {sorted(missing)}")

    decision = stdout_response.get("decision")
    if decision not in PRE_TOOL_DECISIONS:
        raise ValueError(f"Invalid PreToolUse decision {decision!r}; expected {PRE_TOOL_DECISIONS}")

    effective_args = copy.deepcopy(stdin_payload["toolCall"].get("args", {}))
    overwrite = stdout_response.get("overwrite")
    if overwrite is not None:
        if not isinstance(overwrite, dict):
            raise ValueError("'overwrite' must be a JSON object.")
        # Shallow top-level replacement (nested dicts replaced wholesale!)
        for key, new_val in overwrite.items():
            effective_args[key] = copy.deepcopy(new_val)

    return decision, effective_args


def evaluate_stop_hook(
    stop_stdin: dict[str, Any],
    *,
    tests_passing: bool,
) -> dict[str, str]:
    """Simulate a ``Stop`` hook that prevents premature model exit until tests pass."""
    if stop_stdin.get("terminationReason") == "model_stop" and not tests_passing:
        return {
            "decision": "continue",
            "reason": "Unit test suite has not passed yet. Run pytest and fix failures before stopping.",
        }
    return {"decision": "allow_stop"}


# ---------------------------------------------------------------------------
# 4. Plugins (plugin.json), Custom Subagents & JSON Config Inheritance
# ---------------------------------------------------------------------------


def resolve_customization_names(
    config_doc: dict[str, Any],
    available_by_path: dict[str, list[str]],
    inherited_docs: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Resolve ``skills.json`` / ``plugins.json`` / ``agents.json`` entries.

    Supports ``inherits`` (processed first in listed order) and ``entries``,
    applying ``include_only`` and ``exclude`` regex filters to directory names.
    """
    inherited_docs = inherited_docs or {}
    resolved: list[str] = []

    def _filter_names(names: list[str], entry: dict[str, Any]) -> list[str]:
        inc = [re.compile(p) for p in entry.get("include_only", [])]
        exc = [re.compile(p) for p in entry.get("exclude", [])]
        out: list[str] = []
        for n in names:
            if inc and not any(r.search(n) for r in inc):
                continue
            if exc and any(r.search(n) for r in exc):
                continue
            out.append(n)
        return out

    for inh in config_doc.get("inherits", []):
        inh_path = inh["path"]
        parent_doc = inherited_docs.get(inh_path, {})
        parent_names = resolve_customization_names(
            parent_doc, available_by_path, inherited_docs
        )
        for name in _filter_names(parent_names, inh):
            if name not in resolved:
                resolved.append(name)

    for entry in config_doc.get("entries", []):
        candidates = available_by_path.get(entry["path"], [])
        for name in _filter_names(candidates, entry):
            if name not in resolved:
                resolved.append(name)

    return resolved


def validate_plugin_and_subagent_bundle(
    *,
    plugin_json: dict[str, Any],
    subagent_frontmatter: dict[str, Any],
    max_subagent_depth: int,
    root_allowed_subagents: list[str],
) -> list[str]:
    """Validate an Antigravity plugin manifest, Markdown subagent, and depth ceiling."""
    errors: list[str] = []
    if not isinstance(plugin_json, dict):
        errors.append("plugin.json must be a JSON object.")
    if "name" in plugin_json and (
        not isinstance(plugin_json["name"], str) or not plugin_json["name"].strip()
    ):
        errors.append("plugin.json 'name', when present, must be a non-empty string.")

    for req in ("name", "description"):
        if not subagent_frontmatter.get(req):
            errors.append(f"Markdown agent frontmatter missing required field {req!r}.")

    cmd_policy = subagent_frontmatter.get("commandExecutionPolicy", "auto")
    if cmd_policy not in {"off", "auto", "eager"}:
        errors.append(
            f"Invalid commandExecutionPolicy {cmd_policy!r}; expected 'off', 'auto', or 'eager'."
        )

    if max_subagent_depth < 1 or max_subagent_depth > 5:
        errors.append(
            f"max_subagent_depth={max_subagent_depth} outside recommended enterprise bounds (1..5)."
        )
    if not root_allowed_subagents:
        errors.append("root_allowed_subagents should explicitly scope delegated subagents.")

    return errors


# ---------------------------------------------------------------------------
# 5. Antigravity SDK 9-Level Policy Precedence & Fail-Closed Predicates
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SdkPolicyRule:
    """Models a ``google.antigravity.hooks.policy`` rule."""

    action: str  # "deny" | "ask_user" | "allow"
    target: str  # e.g. "run_command", "cloudrun/*", "*"
    when: Callable[[dict[str, Any]], bool] | None = None
    name: str = ""

    @property
    def priority_rank(self) -> int:
        """Return 1..9 matching Antigravity SDK's exact 9-level resolution order."""
        if self.target == "*":
            scope_offset = 6  # Global Wildcard: 7, 8, 9
        elif self.target.endswith("/*"):
            scope_offset = 3  # Prefix Wildcard: 4, 5, 6
        else:
            scope_offset = 0  # Specific Tool:   1, 2, 3

        action_rank = {"deny": 1, "ask_user": 2, "allow": 3}[self.action]
        return scope_offset + action_rank


def default_confirm_run_command_policies(*, interactive: bool = False) -> list[SdkPolicyRule]:
    """Return Antigravity SDK's default ``policy.confirm_run_command()`` ruleset.

    Headless ``LocalAgentConfig`` denies ``run_command`` and allows other tools;
    ``run_interactive_loop()`` upgrades ``run_command`` to ``ask_user``.
    """
    return [
        SdkPolicyRule(
            action="ask_user" if interactive else "deny",
            target="run_command",
            name="confirm_run_command_gate",
        ),
        SdkPolicyRule(action="allow", target="*", name="confirm_run_command_default_allow"),
    ]


def evaluate_antigravity_policies(
    policies: list[SdkPolicyRule],
    tool_name: str,
    tool_args: dict[str, Any] | None = None,
) -> tuple[str, int, str]:
    """Evaluate policies using Antigravity SDK's 9-level precedence + fail-closed predicates.

    Returns:
        ``(decision_action, winning_priority_level, winning_rule_name)``
    """
    tool_args = tool_args or {}

    # Stable sort by priority_rank (1..9) so first-match-wins within each tier!
    ordered = sorted(policies, key=lambda r: r.priority_rank)

    for rule in ordered:
        if rule.target == "*":
            target_matches = True
        elif rule.target.endswith("/*"):
            prefix = rule.target[:-1]  # keep trailing "/"
            target_matches = tool_name.startswith(prefix)
        else:
            target_matches = tool_name == rule.target

        if not target_matches:
            continue

        if rule.when is not None:
            try:
                predicate_matched = bool(rule.when(tool_args))
            except Exception:
                # CRITICAL EXAM RULE (safety_policies.md):
                # If a predicate raises an exception, the policy FAILS CLOSED and
                # treats the predicate as a match so the rule's decision applies!
                predicate_matched = True
            if not predicate_matched:
                continue

        return rule.action, rule.priority_rank, rule.name or f"{rule.action}({rule.target})"

    return "deny", 0, "implicit_default_deny"


# ---------------------------------------------------------------------------
# 6. Agents CLI (`adk`) — Agent Mode vs. Human Mode
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AgentsCliCommandSpec:
    """Constructed CLI invocation and environment for Agent Mode vs Human Mode."""

    argv: tuple[str, ...]
    env_overrides: dict[str, str]
    expects_structured_output: bool
    interactive_tty: bool


def build_agents_cli_invocation(
    subcommand: str,
    target_dir: str,
    *,
    agent_mode: bool,
    eval_set_path: str | None = None,
    deploy_target: str = "cloud_run",
) -> AgentsCliCommandSpec:
    """Build an ``adk`` / Agents CLI command tailored for Agent Mode or Human Mode.

    Exam distinction (Objectives 2.2 & 3.1):
      - **Agent Mode** (invoked by Antigravity or CI/CD): non-interactive,
        ``NO_COLOR=1``, deterministic exit codes, machine-readable JSON artifacts
        for ``eval``, ``optimize`` (GEPA prompt optimizer), ``test``, ``deploy``.
      - **Human Mode** (invoked by an engineer at a terminal): interactive REPL
        (``adk run`` without query) or browser Dev UI (``adk web``), ANSI colors,
        interactive confirmation prompts.
    """
    valid_deploy_targets = {"agent_engine", "cloud_run", "gke", "docker"}
    if subcommand == "deploy" and deploy_target not in valid_deploy_targets:
        raise ValueError(f"Unsupported adk deploy target: {deploy_target!r}")

    env = {"NO_COLOR": "1", "CI": "true"} if agent_mode else {}

    if subcommand == "eval":
        argv = ["adk", "eval", target_dir]
        if eval_set_path:
            argv.append(eval_set_path)
        if agent_mode:
            argv.append("--print_detailed_results")
    elif subcommand == "optimize":
        # GEPA root-agent instruction optimizer
        argv = ["adk", "optimize", target_dir]
    elif subcommand == "deploy":
        argv = ["adk", "deploy", deploy_target, target_dir]
    elif subcommand == "run":
        argv = (
            ["adk", "run", target_dir, "--replay", "ci_input.json"]
            if agent_mode
            else ["adk", "run", target_dir]
        )
    elif subcommand == "web":
        if agent_mode:
            raise ValueError(
                "'adk web' launches an interactive human browser UI; use 'adk eval' or 'adk test' in Agent Mode."
            )
        argv = ["adk", "web", target_dir]
    else:
        raise ValueError(f"Unknown CLI subcommand: {subcommand!r}")

    return AgentsCliCommandSpec(
        argv=tuple(argv),
        env_overrides=env,
        expects_structured_output=agent_mode,
        interactive_tty=not agent_mode,
    )


# ---------------------------------------------------------------------------
# Offline & Live Runners
# ---------------------------------------------------------------------------


def run_offline() -> LabReport:
    banner(
        "Lab 06 — Antigravity Customization, Governance & Agents CLI",
        "Skills (L1/L2/L3), GEMINI.md & Rules, hooks.json, Plugins, 9-Level Policy & Agents CLI",
    )
    report = LabReport("Lab 06 — Antigravity Customization")
    workspace = Path(tempfile.mkdtemp(prefix="lab06_agy_"))

    try:
        # 1. ADK Skills L1 vs L2/L3 Progressive Disclosure + GCPSkillRegistry
        section("1. Progressive Disclosure Skills (L1 Frontmatter vs L2/L3 Load)")
        skills_dir = workspace / "_agents" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        create_enterprise_skill(skills_dir, "enterprise-security-auditor")

        # Also verify the bundled lab skill on disk
        bundled_lab_dir = Path(__file__).resolve().parent
        bundled_skill = load_skill_from_dir(bundled_lab_dir / "my-custom-skill")

        l1_catalog: dict[str, Frontmatter] = list_skills_in_dir(skills_dir)
        full_skills: list[Skill] = load_skills_from_dir(skills_dir)
        auditor = full_skills[0]
        gcp_skill_reg = GCPSkillRegistry(
            project_id="enterprise-agent-gov", location="us-central1"
        )

        report.check(
            "L1 list_skills_in_dir loads Frontmatter only; load_skills_from_dir loads L2 + L3",
            "enterprise-security-auditor" in l1_catalog
            and l1_catalog["enterprise-security-auditor"].metadata.get("approval_gate")
            == "required"
            and "least_privilege_matrix.md" in auditor.resources.references
            and "check_iam.py" in auditor.resources.scripts
            and "iam_runbook.md" in bundled_skill.resources.references
            and hasattr(gcp_skill_reg, "search_skills"),
            f"L1_compatibility={auditor.frontmatter.compatibility}, L3_refs={list(auditor.resources.references)}",
        )

        # 2. Rules Hierarchy (GEMINI.md walk-up + rules/*.md triggers + deduplication)
        section("2. Workspace Rules (GEMINI.md Walk-Up, Triggers & Deduplication)")
        sub_pkg = workspace / "services" / "payments"
        sub_pkg.mkdir(parents=True, exist_ok=True)
        (workspace / "GEMINI.md").write_text(
            "# Repo Root Rule\nAlways use Google Cloud least-privilege IAM roles.\n",
            encoding="utf-8",
        )
        (sub_pkg / "AGENTS.md").write_text(
            "# Payments Directory Rule\nNever log PAN or CVV fields.\n",
            encoding="utf-8",
        )
        rules_dir = workspace / "_agents" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / "terraform_guard.md").write_text(
            '---\ntrigger: glob\nglobs: "*.tf,*.tfvars"\n---\nRequire CMEK on all Cloud SQL & GCS resources.\n',
            encoding="utf-8",
        )
        (rules_dir / "arch_review.md").write_text(
            '---\ntrigger: model_decision\ndescription: "Load when reviewing VPC Service Controls topology."\n---\nEnforce private Google access.\n',
            encoding="utf-8",
        )
        (rules_dir / "incident_override.md").write_text(
            "---\ntrigger: manual\n---\nBreak-glass runbook steps.\n",
            encoding="utf-8",
        )

        # Pass rules_dir twice to verify Path.resolve() deduplication!
        resolved_rules, rule_errors = discover_and_resolve_rules(
            cwd=sub_pkg,
            repo_root=workspace,
            open_files=["infra/main.tf"],
            mentioned_rules=set(),
            extra_rule_dirs=[rules_dir],
        )
        active_names = [r.resolved_path.name for r in resolved_rules if r.active_immediately]
        model_dec_names = [
            r.resolved_path.name for r in resolved_rules if r.listed_for_model_decision
        ]
        table(
            ["Rule File", "Kind", "Trigger", "Active Now?", "Model-Decision Listed?"],
            [
                [
                    r.resolved_path.name,
                    r.kind,
                    r.trigger,
                    r.active_immediately,
                    r.listed_for_model_decision,
                ]
                for r in resolved_rules
            ],
        )
        report.check(
            "GEMINI.md/AGENTS.md walk up without frontmatter; glob/model_decision/manual triggers & dedup work",
            rule_errors == []
            and len(resolved_rules) == 5
            and set(active_names) == {"AGENTS.md", "GEMINI.md", "terraform_guard.md"}
            and model_dec_names == ["arch_review.md"],
            f"active={active_names}, model_decision={model_dec_names}",
        )

        # 3. Lifecycle Hooks (hooks.json PreToolUse shallow overwrite + Stop continue)
        section("3. Lifecycle Hooks (hooks.json PreToolUse & Stop Gate)")
        hooks_config = {
            "command-sanitizer": {
                "enabled": True,
                "PreToolUse": [
                    {
                        "matcher": "run_command",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "./scripts/sanitize_cmd.py",
                                "timeout": 15,
                            }
                        ],
                    }
                ],
            },
            "ci-test-gate": {
                "Stop": [
                    {
                        "type": "command",
                        "command": "./scripts/verify_pytest_green.py",
                        "timeout": 30,
                    }
                ]
            },
        }
        hook_errors = validate_hooks_json(hooks_config)
        decision, updated_args = apply_pre_tool_use_response(
            stdin_payload={
                "conversationId": "conv-001",
                "workspacePaths": [str(workspace)],
                "stepIdx": 4,
                "toolCall": {
                    "name": "run_command",
                    "args": {
                        "CommandLine": "pytest",
                        "NestedEnv": {"DEBUG": "1", "KEEP_ME": "will_be_replaced"},
                    },
                },
            },
            stdout_response={
                "decision": "force_ask",
                "reason": "Confirm test runner flags",
                "overwrite": {
                    "CommandLine": "pytest -q --maxfail=1",
                    "NestedEnv": {"SAFE": "1"},
                },
            },
        )
        stop_out = evaluate_stop_hook(
            {"executionNum": 1, "terminationReason": "model_stop", "fullyIdle": True},
            tests_passing=False,
        )
        report.check(
            "hooks.json validates; PreToolUse shallow overwrite & Stop 'continue' gate work",
            hook_errors == []
            and decision == "force_ask"
            and updated_args["CommandLine"] == "pytest -q --maxfail=1"
            and updated_args["NestedEnv"] == {"SAFE": "1"}
            and stop_out["decision"] == "continue",
            f"decision={decision}, stop_gate={stop_out['decision']}",
        )
        exam_note(
            "PreToolUse 'overwrite' is a SHALLOW top-level replacement; Stop returning "
            "{'decision': 'continue'} prevents premature exit when tests are failing."
        )

        # 4. Plugins, Subagents & skills.json Inheritance
        section("4. Plugins (plugin.json), Subagent Depth & skills.json Inheritance")
        inherited_skills = resolve_customization_names(
            config_doc={
                "inherits": [
                    {
                        "path": "/shared/platform/skills.json",
                        "exclude": ["deprecated-.*"],
                    }
                ],
                "entries": [
                    {
                        "path": "team/skills",
                        "include_only": ["sec-.*", "iam-.*"],
                    }
                ],
            },
            available_by_path={
                "shared/dir": ["core-linter", "deprecated-v1"],
                "team/skills": ["sec-scanner", "iam-auditor", "experimental-toy"],
            },
            inherited_docs={
                "/shared/platform/skills.json": {
                    "entries": [{"path": "shared/dir"}]
                }
            },
        )
        bundle_errors = validate_plugin_and_subagent_bundle(
            plugin_json={"name": "enterprise-platform-kit"},
            subagent_frontmatter={
                "name": "security-reviewer",
                "description": "Audits Terraform diffs before apply.",
                "tools": ["view_file", "grep_search"],
                "mainAgent": False,
                "subagent": True,
                "commandExecutionPolicy": "off",
            },
            max_subagent_depth=2,
            root_allowed_subagents=["security-reviewer"],
        )
        report.check(
            "plugin.json + subagent depth + skills.json inherits/include_only/exclude verified",
            bundle_errors == []
            and inherited_skills == ["core-linter", "sec-scanner", "iam-auditor"],
            f"resolved_skills={inherited_skills}",
        )

        # 5. Antigravity SDK 9-Level Policy Precedence & Fail-Closed Predicates
        section("5. Antigravity SDK 9-Level Policy Precedence & Fail-Closed Predicates")
        policies = [
            SdkPolicyRule(action="allow", target="*", name="global_allow"),
            SdkPolicyRule(action="allow", target="cloudrun/*", name="mcp_prefix_allow"),
            SdkPolicyRule(action="deny", target="cloudrun/*", name="mcp_prefix_deny"),
            SdkPolicyRule(action="allow", target="run_command", name="specific_allow_cmd"),
            SdkPolicyRule(
                action="deny",
                target="run_command",
                when=lambda args: "rm -rf" in args["CommandLine"],
                name="specific_deny_rm_or_buggy_args",
            ),
        ]
        # Specific Deny (rank 1) beats Specific Allow (rank 3) and Global Allow (rank 9)
        act1, rank1, _ = evaluate_antigravity_policies(
            policies, "run_command", {"CommandLine": "rm -rf /tmp/build"}
        )
        # Missing 'CommandLine' raises KeyError inside predicate -> MUST FAIL CLOSED (match deny)!
        act_fail_closed, rank_fc, _ = evaluate_antigravity_policies(
            policies, "run_command", {}
        )
        # Prefix Wildcard Deny (rank 4) beats Prefix Wildcard Allow (rank 6)
        act_prefix, rank_prefix, _ = evaluate_antigravity_policies(
            policies, "cloudrun/delete_service", {}
        )
        # Default confirm_run_command(): headless='deny', interactive='ask_user'
        headless_act, _, _ = evaluate_antigravity_policies(
            default_confirm_run_command_policies(interactive=False), "run_command"
        )
        interactive_act, _, _ = evaluate_antigravity_policies(
            default_confirm_run_command_policies(interactive=True), "run_command"
        )
        report.check(
            "9-level policy precedence (Specific Deny > Specific Allow > Prefix > Global) + fail-closed predicate",
            (act1, rank1) == ("deny", 1)
            and (act_fail_closed, rank_fc) == ("deny", 1)
            and (act_prefix, rank_prefix) == ("deny", 4)
            and headless_act == "deny"
            and interactive_act == "ask_user",
            f"rm_rank={rank1}, fail_closed={act_fail_closed}, headless={headless_act}, interactive={interactive_act}",
        )

        # 6. Agents CLI (`adk`) Agent Mode vs Human Mode
        section("6. Agents CLI (adk) — Agent Mode vs. Human Mode")
        agent_eval = build_agents_cli_invocation(
            "eval", "./my_agent", agent_mode=True, eval_set_path="golden_evalset.json"
        )
        agent_opt = build_agents_cli_invocation(
            "optimize", "./my_agent", agent_mode=True
        )
        human_web = build_agents_cli_invocation("web", "./my_agent", agent_mode=False)
        report.check(
            "Agents CLI distinguishes non-interactive Agent Mode (eval, GEPA optimize) from Human Mode (web/REPL)",
            agent_eval.expects_structured_output is True
            and agent_eval.env_overrides.get("NO_COLOR") == "1"
            and agent_opt.argv[:2] == ("adk", "optimize")
            and human_web.interactive_tty is True,
            f"eval_cmd={' '.join(agent_eval.argv)}, optimize_cmd={' '.join(agent_opt.argv)}",
        )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    report.summary()
    return report


def run_live(config: LabConfig) -> None:
    banner(
        "Lab 06 — Enterprise Customization & Governance Verification",
        f"Project: {config.project_id} | Location: {config.location}",
    )
    report = run_offline()
    if not report.passed:
        sys.exit(1)


def main() -> None:
    config = load_config()
    if require_live(config):
        run_live(config)
    else:
        report = run_offline()
        if not report.passed:
            sys.exit(1)


if __name__ == "__main__":
    main()
