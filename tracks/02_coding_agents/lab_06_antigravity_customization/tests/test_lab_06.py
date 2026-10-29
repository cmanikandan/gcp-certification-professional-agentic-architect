from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
from google.adk.integrations.skill_registry import GCPSkillRegistry
from google.adk.skills import (
    Frontmatter,
    Skill,
    list_skills_in_dir,
    load_skill_from_dir,
    load_skills_from_dir,
)

from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG

LAB_DIR = Path(__file__).resolve().parent.parent


def _load_lab_module():
    spec = importlib.util.spec_from_file_location("lab_06_module", LAB_DIR / "lab.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lab_06_module"] = mod
    spec.loader.exec_module(mod)
    return mod


lab = _load_lab_module()


def test_adk_skills_progressive_disclosure_and_name_match_validation() -> None:
    """Verify L1 list_skills_in_dir vs L2/L3 load_skills_from_dir and folder name check."""
    workspace = Path(tempfile.mkdtemp())
    try:
        lab.create_enterprise_skill(workspace, "enterprise-security-auditor")

        # L1 progressive disclosure: Frontmatter only
        l1 = list_skills_in_dir(workspace)
        assert "enterprise-security-auditor" in l1
        fm = l1["enterprise-security-auditor"]
        assert isinstance(fm, Frontmatter)
        assert fm.compatibility == DEFAULT_AGENT_MODEL
        assert fm.metadata.get("approval_gate") == "required"

        # L2 + L3 activation: full instructions + references + scripts
        skills = load_skills_from_dir(workspace)
        assert len(skills) == 1
        skill = skills[0]
        assert isinstance(skill, Skill)
        assert "Security Auditor Workflow" in skill.instructions
        assert "least_privilege_matrix.md" in skill.resources.references
        assert "check_iam.py" in skill.resources.scripts

        # Verify ADK raises ValueError when SKILL.md 'name' != folder name
        mismatch_dir = workspace / "wrong-folder-name"
        mismatch_dir.mkdir()
        (mismatch_dir / "SKILL.md").write_text(
            "---\nname: different-skill-name\ndescription: mismatch\n---\nBody\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="does not match directory"):
            load_skill_from_dir(mismatch_dir)

        # Verify bundled on-disk lab skill and GCPSkillRegistry
        bundled = load_skill_from_dir(LAB_DIR / "my-custom-skill")
        assert bundled.frontmatter.name == "my-custom-skill"
        assert "iam_runbook.md" in bundled.resources.references
        reg = GCPSkillRegistry(project_id="test-proj", location="us-central1")
        assert hasattr(reg, "get_skill") and hasattr(reg, "search_skills")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_rules_walk_up_frontmatter_ban_triggers_and_deduplication() -> None:
    """Verify GEMINI.md/AGENTS.md walk-up (no frontmatter) and rules/*.md triggers."""
    root = Path(tempfile.mkdtemp())
    try:
        leaf = root / "pkg" / "billing"
        leaf.mkdir(parents=True)
        (root / "GEMINI.md").write_text("Root coding guideline.\n", encoding="utf-8")
        (leaf / "AGENTS.md").write_text("Billing local guideline.\n", encoding="utf-8")

        rules_dir = root / "_agents" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "always.md").write_text(
            "---\ntrigger: always_on\n---\nAlways active.\n", encoding="utf-8"
        )
        (rules_dir / "py_only.md").write_text(
            '---\ntrigger: glob\nglobs: "*.py"\n---\nPython rule.\n', encoding="utf-8"
        )
        (rules_dir / "vpc_guide.md").write_text(
            '---\ntrigger: model_decision\ndescription: "VPC rules"\n---\nVPC body.\n',
            encoding="utf-8",
        )
        (rules_dir / "on_demand.md").write_text(
            "---\ntrigger: manual\n---\nManual body.\n", encoding="utf-8"
        )

        # Open a .tf file first -> py_only.md is inactive; manual is not @-mentioned
        rules, errs = lab.discover_and_resolve_rules(
            cwd=leaf,
            repo_root=root,
            open_files=["main.tf"],
            mentioned_rules=set(),
            extra_rule_dirs=[rules_dir],  # duplicate path tests deduplication
        )
        assert errs == []
        assert len(rules) == 6
        active = {r.resolved_path.name for r in rules if r.active_immediately}
        assert active == {"GEMINI.md", "AGENTS.md", "always.md"}

        # Now open app.py and @-mention on_demand -> both activate!
        rules2, _ = lab.discover_and_resolve_rules(
            cwd=leaf,
            repo_root=root,
            open_files=["app.py"],
            mentioned_rules={"on_demand"},
        )
        active2 = {r.resolved_path.name for r in rules2 if r.active_immediately}
        assert "py_only.md" in active2 and "on_demand.md" in active2

        # Putting YAML frontmatter inside GEMINI.md must be flagged as invalid
        (root / "GEMINI.md").write_text(
            "---\ntrigger: always_on\n---\nInvalid frontmatter in GEMINI.md\n",
            encoding="utf-8",
        )
        _, fm_errs = lab.discover_and_resolve_rules(cwd=leaf, repo_root=root)
        assert len(fm_errs) == 1 and "do not support YAML frontmatter" in fm_errs[0]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_hooks_json_validation_shallow_overwrite_and_stop_continue() -> None:
    """Verify hooks.json grouped vs flat events, shallow overwrite, and Stop 'continue'."""
    valid_hooks = {
        "gate": {
            "enabled": True,
            "PreToolUse": [
                {
                    "matcher": "run_command",
                    "hooks": [{"type": "command", "command": "./check.sh", "timeout": 10}],
                }
            ],
            "Stop": [{"command": "./verify_done.sh"}],
        }
    }
    assert lab.validate_hooks_json(valid_hooks) == []

    # Flat Stop event erroneously wrapped in matcher/hooks must fail validation
    bad_hooks = {
        "broken": {
            "Stop": [{"matcher": "*", "hooks": [{"command": "./x.sh"}]}]
        }
    }
    assert len(lab.validate_hooks_json(bad_hooks)) == 1

    # Shallow top-level overwrite replaces nested dicts wholesale
    decision, new_args = lab.apply_pre_tool_use_response(
        stdin_payload={
            "conversationId": "c1",
            "workspacePaths": ["/ws"],
            "stepIdx": 1,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "rm -rf /", "Env": {"A": "1", "B": "2"}},
            },
        },
        stdout_response={
            "decision": "ask",
            "overwrite": {"CommandLine": "ls -la", "Env": {"A": "safe"}},
        },
    )
    assert decision == "ask"
    assert new_args == {"CommandLine": "ls -la", "Env": {"A": "safe"}}

    # Stop hook blocks premature termination until tests pass
    assert (
        lab.evaluate_stop_hook(
            {"terminationReason": "model_stop"}, tests_passing=False
        )["decision"]
        == "continue"
    )
    assert (
        lab.evaluate_stop_hook(
            {"terminationReason": "model_stop"}, tests_passing=True
        )["decision"]
        == "allow_stop"
    )


def test_plugin_bundle_and_skills_json_inheritance() -> None:
    """Verify skills.json inherits + include_only/exclude and subagent frontmatter."""
    names = lab.resolve_customization_names(
        config_doc={
            "inherits": [{"path": "/org/skills.json", "include_only": ["org-sec-.*"]}],
            "entries": [{"path": "local/skills", "exclude": ["draft-.*"]}],
        },
        available_by_path={
            "org/shared": ["org-sec-iam", "org-misc"],
            "local/skills": ["prod-deploy", "draft-experiment"],
        },
        inherited_docs={"/org/skills.json": {"entries": [{"path": "org/shared"}]}},
    )
    assert names == ["org-sec-iam", "prod-deploy"]

    errs = lab.validate_plugin_and_subagent_bundle(
        plugin_json={"name": "sec-bundle"},
        subagent_frontmatter={
            "name": "critic",
            "description": "Read-only critic",
            "commandExecutionPolicy": "off",
        },
        max_subagent_depth=3,
        root_allowed_subagents=["critic"],
    )
    assert errs == []


def test_antigravity_9_level_policy_precedence_and_fail_closed_predicate() -> None:
    """Verify Specific Deny > Specific Ask > Specific Allow > Prefix > Global & fail-closed."""
    rules = [
        lab.SdkPolicyRule(action="allow", target="*", name="lvl9_global_allow"),
        lab.SdkPolicyRule(action="deny", target="*", name="lvl7_global_deny"),
        lab.SdkPolicyRule(action="allow", target="mcp_db/*", name="lvl6_prefix_allow"),
        lab.SdkPolicyRule(action="ask_user", target="mcp_db/*", name="lvl5_prefix_ask"),
        lab.SdkPolicyRule(action="allow", target="run_command", name="lvl3_spec_allow"),
        lab.SdkPolicyRule(action="ask_user", target="run_command", name="lvl2_spec_ask"),
        lab.SdkPolicyRule(
            action="deny",
            target="run_command",
            when=lambda a: "DROP TABLE" in a["sql"],  # raises KeyError if 'sql' absent!
            name="lvl1_spec_deny",
        ),
    ]
    assert [r.priority_rank for r in sorted(rules, key=lambda x: x.priority_rank)] == [
        1,
        2,
        3,
        5,
        6,
        7,
        9,
    ]
    # Missing 'sql' key triggers KeyError in predicate -> fails closed to Specific Deny (rank 1)!
    act, rank, name = lab.evaluate_antigravity_policies(
        rules, "run_command", {"CommandLine": "echo hi"}
    )
    assert (act, rank, name) == ("deny", 1, "lvl1_spec_deny")

    # When 'sql' is safe (no exception, returns False), falls through to Specific Ask (rank 2)
    act2, rank2, _ = lab.evaluate_antigravity_policies(
        rules, "run_command", {"sql": "SELECT 1"}
    )
    assert (act2, rank2) == ("ask_user", 2)

    # Prefix Ask (rank 5) beats Prefix Allow (rank 6) and Global Deny (rank 7)
    act3, rank3, _ = lab.evaluate_antigravity_policies(rules, "mcp_db/query", {})
    assert (act3, rank3) == ("ask_user", 5)


def test_agents_cli_agent_mode_vs_human_mode_and_verified_models() -> None:
    """Verify Agents CLI (adk) non-interactive Agent Mode vs interactive Human Mode."""
    eval_spec = lab.build_agents_cli_invocation("eval", "./agent", agent_mode=True)
    assert eval_spec.expects_structured_output is True
    assert eval_spec.interactive_tty is False
    assert eval_spec.env_overrides["NO_COLOR"] == "1"

    opt_spec = lab.build_agents_cli_invocation("optimize", "./agent", agent_mode=True)
    assert opt_spec.argv == ("adk", "optimize", "./agent")

    for target in ("agent_engine", "cloud_run", "gke", "docker"):
        dep = lab.build_agents_cli_invocation(
            "deploy", "./agent", agent_mode=True, deploy_target=target
        )
        assert target in dep.argv

    with pytest.raises(ValueError):
        lab.build_agents_cli_invocation("web", "./agent", agent_mode=True)

    assert DEFAULT_AGENT_MODEL in MODEL_CATALOG
