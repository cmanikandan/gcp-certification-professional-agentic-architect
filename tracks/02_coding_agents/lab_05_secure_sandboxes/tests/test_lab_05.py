from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

patch("kubernetes.config.load_incluster_config").start()
patch("kubernetes.config.load_kube_config").start()

from google.adk.code_executors import (
    AgentEngineSandboxCodeExecutor,
    GkeCodeExecutor,
    UnsafeLocalCodeExecutor,
)
from google.adk.integrations.cloud_run import CloudRunSandboxCodeExecutor
from google.adk.integrations.daytona import DaytonaEnvironment
from google.adk.integrations.e2b import E2BEnvironment

LAB_DIR = Path(__file__).resolve().parent.parent


def _load_lab_module():
    spec = importlib.util.spec_from_file_location("lab_05_module", LAB_DIR / "lab.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lab_05_module"] = mod
    spec.loader.exec_module(mod)
    return mod


lab = _load_lab_module()


def test_cloud_workstations_and_antigravity_os_sandbox_selection() -> None:
    """Verify Cloud Workstations (VPC IDE) and Antigravity OS Sandbox recommendations."""
    cw = lab.select_sandbox_architecture(interactive_human_ide_in_vpc=True)
    assert cw.surface == "Cloud Workstations"
    assert "roles/workstations.user" in cw.required_iam_roles
    assert "roles/workstations.admin" not in cw.required_iam_roles

    agy = lab.select_sandbox_architecture(antigravity_local_cli_command=True)
    assert agy.executor_instance == {
        "enable_sandbox": True,
        "policy": "confirm_run_command",
    }
    assert "enable_sandbox" in agy.adk_or_sdk_primitive


def test_gke_executor_isolation_modes_and_selector() -> None:
    """Verify GkeCodeExecutor differentiates gVisor sandbox vs standard K8s job."""
    rec = lab.select_sandbox_architecture(untrusted_exploit_or_fuzzing=True)
    prod_executor = rec.executor_instance
    assert isinstance(prod_executor, GkeCodeExecutor)
    assert prod_executor.executor_type == "sandbox"
    assert prod_executor.sandbox_gateway_name == "agent-sandbox-gateway"
    assert "roles/iam.workloadIdentityUser" in rec.required_iam_roles
    assert "roles/artifactregistry.reader" in rec.required_iam_roles

    dev_executor = GkeCodeExecutor(
        executor_type="job",
        namespace="test",
        image="python:3.14-slim",
    )
    assert dev_executor.executor_type == "job"
    assert prod_executor.executor_type != dev_executor.executor_type


def test_cloudrun_agent_engine_third_party_and_unsafe_block() -> None:
    """Verify Cloud Run, Agent Engine, E2B/Daytona, and default UnsafeLocal block."""
    cr = lab.select_sandbox_architecture(running_inside_cloud_run_container=True)
    assert isinstance(cr.executor_instance, CloudRunSandboxCodeExecutor)
    assert cr.executor_instance.allow_egress is False

    ae = lab.select_sandbox_architecture(deployed_on_agent_engine=True)
    assert isinstance(ae.executor_instance, AgentEngineSandboxCodeExecutor)

    assert isinstance(
        lab.select_sandbox_architecture(third_party_provider="e2b").executor_instance,
        E2BEnvironment,
    )
    assert isinstance(
        lab.select_sandbox_architecture(third_party_provider="daytona").executor_instance,
        DaytonaEnvironment,
    )

    with pytest.raises(PermissionError):
        lab.select_sandbox_architecture()

    unsafe = lab.select_sandbox_architecture(allow_unsafe_local_dev=True)
    assert isinstance(unsafe.executor_instance, UnsafeLocalCodeExecutor)


def test_code_mender_remediation_requires_gvisor_sandbox_and_human_pr_gate() -> None:
    """Verify Code Mender blocks SQLi, requires gVisor sandbox, and enforces HITL PR review."""
    vuln = 'def get_customer_orders(db, user_id):\n    return db.execute(f"SELECT * FROM orders WHERE user_id = \'{user_id}\'")\n'
    patch_sql = 'def get_customer_orders(db, user_id):\n    return db.execute("SELECT * FROM orders WHERE user_id = :user_id", {"user_id": user_id})\n'

    gvisor_exec = GkeCodeExecutor(
        executor_type="sandbox",
        namespace="agent-sandbox",
        image="python:3.14-slim",
        sandbox_gateway_name="default",
        sandbox_template="default",
    )
    res = lab.run_code_mender_remediation_workflow(
        cve_id="CVE-2026-41092",
        vulnerable_sql_builder=vuln,
        proposed_parameterized_patch=patch_sql,
        executor=gvisor_exec,
    )
    assert res.exploit_blocked_after_patch is True
    assert res.regression_suite_passed is True
    assert res.ready_for_human_pr_review is True
    assert res.auto_merged_to_main is False

    job_exec = GkeCodeExecutor(
        executor_type="job", namespace="default", image="python:3.14-slim"
    )
    with pytest.raises(PermissionError):
        lab.run_code_mender_remediation_workflow(
            cve_id="CVE-2026-41092",
            vulnerable_sql_builder=vuln,
            proposed_parameterized_patch=patch_sql,
            executor=job_exec,
        )


def test_sandbox_iam_least_privilege_validator() -> None:
    """Verify Cloud Workstations user vs admin, Workload Identity, and Artifact Registry reader."""
    assert (
        lab.validate_sandbox_iam_bindings(
            developer_roles={"roles/workstations.user"},
            gke_pod_uses_workload_identity=True,
            gke_pod_mounts_json_sa_key=False,
            node_pull_roles={"roles/artifactregistry.reader"},
        )
        == []
    )
    findings = lab.validate_sandbox_iam_bindings(
        developer_roles={"roles/workstations.admin"},
        gke_pod_uses_workload_identity=False,
        gke_pod_mounts_json_sa_key=True,
        node_pull_roles={"roles/artifactregistry.writer"},
    )
    assert len(findings) == 5
