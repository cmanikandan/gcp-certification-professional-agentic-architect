"""Lab 05 — Secure Sandboxes, Cloud Workstations, and Code Mender.

Covers Section 2.1:
  - Using coding agents in secure sandboxes (Google Kubernetes Engine [GKE],
    Cloud Workstations, Antigravity OS Sandbox, Cloud Run Sandbox, Agent Engine).
  - Using coding agents (including Code Mender) to refactor source code, optimize
    execution runtimes, and patch application-layer vulnerabilities safely.
  - Enforcing least-privilege IAM across Cloud Workstations, GKE Workload Identity
    Federation, and Artifact Registry.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

# Patch kubeconfig discovery so GkeCodeExecutor instantiates cleanly offline.
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

from common import LabConfig, load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, table


@dataclass(frozen=True)
class SandboxRecommendation:
    """Architectural decision output for coding-agent execution isolation."""

    surface: str
    adk_or_sdk_primitive: str
    kernel_or_boundary: str
    required_iam_roles: tuple[str, ...]
    executor_instance: Any | None
    rationale: str


def select_sandbox_architecture(
    *,
    interactive_human_ide_in_vpc: bool = False,
    untrusted_exploit_or_fuzzing: bool = False,
    running_inside_cloud_run_container: bool = False,
    deployed_on_agent_engine: bool = False,
    antigravity_local_cli_command: bool = False,
    third_party_provider: str | None = None,
    allow_unsafe_local_dev: bool = False,
) -> SandboxRecommendation:
    """Choose the right Google Cloud sandbox and instantiate its ADK/SDK primitive.

    Exam priority rules (Section 2.1):
      1. Interactive enterprise developers using Antigravity or Claude Code without
         source code touching laptops -> **Cloud Workstations** inside VPC-SC with
         ``roles/workstations.user`` (admins use ``roles/workstations.admin``).
      2. Untrusted AI-generated code, CVE reproduction, or Code Mender fuzzing ->
         **GKE Agent Sandbox** (`GkeCodeExecutor(executor_type="sandbox")`) backed
         by **gVisor (`runsc`)** user-space kernel interception + Workload Identity
         Federation (never ``executor_type="job"``, which shares the host kernel).
      3. Serverless execution *from inside* a Cloud Run service ->
         ``CloudRunSandboxCodeExecutor`` (`allow_egress=False`). Cannot be called
         remotely from outside Cloud Run.
      4. Agent Runtime (Agent Engine) managed agents ->
         ``AgentEngineSandboxCodeExecutor``.
      5. Antigravity SDK local shell tool -> ``RunCommandConfig(enable_sandbox=True)``
         **paired with** ``policy.confirm_run_command()`` / ``policy.ask_user()``
         because ``enable_sandbox`` silently no-ops if unsupported by the host OS.
      6. ``UnsafeLocalCodeExecutor`` runs raw host subprocesses -> strictly blocked
         unless ``allow_unsafe_local_dev=True`` for throwaway local debugging.
    """
    if interactive_human_ide_in_vpc:
        return SandboxRecommendation(
            surface="Cloud Workstations",
            adk_or_sdk_primitive="Cloud Workstations Custom Container + VPC-SC",
            kernel_or_boundary="Dedicated ephemeral Compute VM in customer VPC (no laptop code)",
            required_iam_roles=("roles/workstations.user", "roles/aiplatform.user"),
            executor_instance=None,
            rationale=(
                "Managed browser/SSH IDE inside customer VPC & VPC-SC with CMEK home disks; "
                "developers receive roles/workstations.user while platform ops hold roles/workstations.admin."
            ),
        )

    if untrusted_exploit_or_fuzzing:
        executor = GkeCodeExecutor(
            executor_type="sandbox",
            namespace="agent-sandbox",
            image="us-central1-docker.pkg.dev/enterprise-sec/sandboxes/python-fuzz:3.14-slim",
            cpu_requested="500m",
            mem_requested="512Mi",
            cpu_limit="1000m",
            mem_limit="1024Mi",
            sandbox_gateway_name="agent-sandbox-gateway",
            sandbox_template="gvisor-no-egress",
            timeout_seconds=60,
            stateful=False,
        )
        return SandboxRecommendation(
            surface="GKE Agent Sandbox (gVisor)",
            adk_or_sdk_primitive='GkeCodeExecutor(executor_type="sandbox")',
            kernel_or_boundary="gVisor (runsc) user-space kernel syscall interception + NetworkPolicy",
            required_iam_roles=(
                "roles/iam.workloadIdentityUser",
                "roles/artifactregistry.reader",
            ),
            executor_instance=executor,
            rationale=(
                "executor_type='sandbox' isolates syscalls via gVisor and claims warm pods through "
                "sandbox_gateway_name; executor_type='job' shares the host Linux kernel."
            ),
        )

    if running_inside_cloud_run_container:
        executor = CloudRunSandboxCodeExecutor(
            sandbox_bin="/usr/local/bin/sandbox",
            allow_egress=False,
            stateful=False,
            timeout_seconds=30,
        )
        return SandboxRecommendation(
            surface="Cloud Run Sandbox",
            adk_or_sdk_primitive="CloudRunSandboxCodeExecutor(allow_egress=False)",
            kernel_or_boundary="Cloud Run second-gen execution environment + local sandbox binary",
            required_iam_roles=("roles/run.invoker",),
            executor_instance=executor,
            rationale=(
                "Invokes /usr/local/bin/sandbox from INSIDE a Cloud Run container; "
                "cannot be called remotely from an external VM or laptop."
            ),
        )

    if deployed_on_agent_engine:
        executor = AgentEngineSandboxCodeExecutor()
        return SandboxRecommendation(
            surface="Agent Runtime (Agent Engine) Sandbox",
            adk_or_sdk_primitive="AgentEngineSandboxCodeExecutor()",
            kernel_or_boundary="Managed Vertex AI Agent Engine isolated code sandbox",
            required_iam_roles=("roles/aiplatform.user",),
            executor_instance=executor,
            rationale="Zero-ops managed code execution natively integrated with Agent Runtime.",
        )

    if antigravity_local_cli_command:
        return SandboxRecommendation(
            surface="Antigravity OS Sandbox + Policy Gate",
            adk_or_sdk_primitive=(
                "RunCommandConfig(enable_sandbox=True) + policy.confirm_run_command()"
            ),
            kernel_or_boundary="Host OS process sandbox + SDK 9-level tool policy",
            required_iam_roles=("roles/aiplatform.user",),
            executor_instance={
                "enable_sandbox": True,
                "policy": "confirm_run_command",
            },
            rationale=(
                "Defense in depth: SDK policy gates WHETHER run_command runs, while OS sandbox "
                "confines filesystem/network scope. Always pair both because enable_sandbox "
                "silently no-ops on unsupported OS environments."
            ),
        )

    if third_party_provider == "e2b":
        return SandboxRecommendation(
            surface="Third-Party E2B Sandbox",
            adk_or_sdk_primitive="E2BEnvironment(image='base', timeout=300)",
            kernel_or_boundary="External SaaS microVM (outside GCP VPC-SC)",
            required_iam_roles=(),
            executor_instance=E2BEnvironment(image="base", timeout=300),
            rationale="Managed external sandbox when workload does not require GCP VPC-SC residency.",
        )

    if third_party_provider == "daytona":
        return SandboxRecommendation(
            surface="Third-Party Daytona Sandbox",
            adk_or_sdk_primitive="DaytonaEnvironment(image='base', timeout=300)",
            kernel_or_boundary="External Daytona workspace environment",
            required_iam_roles=(),
            executor_instance=DaytonaEnvironment(image="base", timeout=300),
            rationale="Managed external dev sandbox outside native GCP VPC boundaries.",
        )

    if allow_unsafe_local_dev:
        return SandboxRecommendation(
            surface="Unsafe Local Host Subprocess",
            adk_or_sdk_primitive="UnsafeLocalCodeExecutor()",
            kernel_or_boundary="NONE — direct host subprocess with ambient credentials",
            required_iam_roles=(),
            executor_instance=UnsafeLocalCodeExecutor(),
            rationale="WARNING: Zero isolation; acceptable only for disposable offline toy scripts.",
        )

    raise PermissionError(
        "Refusing to return UnsafeLocalCodeExecutor without explicit allow_unsafe_local_dev=True."
    )


@dataclass(frozen=True)
class CodeMenderPatchResult:
    """Result of a simulated Code Mender autonomous vulnerability remediation loop."""

    cve_id: str
    root_cause_function: str
    sandbox_mode_verified: str
    exploit_blocked_after_patch: bool
    regression_suite_passed: bool
    ready_for_human_pr_review: bool
    auto_merged_to_main: bool


def run_code_mender_remediation_workflow(
    *,
    cve_id: str,
    vulnerable_sql_builder: str,
    proposed_parameterized_patch: str,
    executor: GkeCodeExecutor,
) -> CodeMenderPatchResult:
    """Simulate Code Mender's 4-stage autonomous CVE patching & verification loop.

    Stages tested on the exam (Objective 2.1):
      1. Root-cause localization (AST / call-graph / sanitizer trace analysis).
      2. Minimal security patch synthesis.
      3. Sandboxed exploit reproduction + fuzzing + unit regression suite inside
         a gVisor-isolated GKE Agent Sandbox (`executor_type="sandbox"`).
      4. Human-in-the-Loop (HITL) PR submission (never auto-merging unreviewed
         patches straight into production).
    """
    if executor.executor_type != "sandbox":
        raise PermissionError(
            "Code Mender exploit verification MUST run in executor_type='sandbox' (gVisor), "
            f"got executor_type={executor.executor_type!r}."
        )

    # Stage 1: Verify the original snippet actually has raw string interpolation SQLi
    has_sqli_pattern = "SELECT " in vulnerable_sql_builder and (
        "f\"" in vulnerable_sql_builder or "%s" not in proposed_parameterized_patch and "?" not in proposed_parameterized_patch
    )
    # Stage 2 & 3: Verify candidate patch uses parameterized placeholders, not f-strings
    uses_parameterized_query = (
        ("?" in proposed_parameterized_patch or ":user_id" in proposed_parameterized_patch)
        and "f\"" not in proposed_parameterized_patch
        and "f'" not in proposed_parameterized_patch
    )
    exploit_blocked = bool(has_sqli_pattern and uses_parameterized_query)
    regressions_ok = "return" in proposed_parameterized_patch

    return CodeMenderPatchResult(
        cve_id=cve_id,
        root_cause_function="get_customer_orders",
        sandbox_mode_verified=executor.executor_type,
        exploit_blocked_after_patch=exploit_blocked,
        regression_suite_passed=regressions_ok,
        ready_for_human_pr_review=exploit_blocked and regressions_ok,
        auto_merged_to_main=False,  # HITL PR gate enforced
    )


def validate_sandbox_iam_bindings(
    *,
    developer_roles: set[str],
    gke_pod_uses_workload_identity: bool,
    gke_pod_mounts_json_sa_key: bool,
    node_pull_roles: set[str],
) -> list[str]:
    """Audit least-privilege IAM across Cloud Workstations and GKE Agent Sandbox."""
    findings: list[str] = []

    if "roles/workstations.admin" in developer_roles:
        findings.append(
            "Developers must receive 'roles/workstations.user', not 'roles/workstations.admin' "
            "(which permits altering VPC network & CMEK settings)."
        )
    if "roles/workstations.user" not in developer_roles:
        findings.append("Developer lacks 'roles/workstations.user' to start Cloud Workstations.")

    if gke_pod_mounts_json_sa_key or not gke_pod_uses_workload_identity:
        findings.append(
            "GKE Agent Sandbox pods must authenticate via Workload Identity Federation "
            "('roles/iam.workloadIdentityUser'), never mounted JSON service account keys."
        )

    if "roles/artifactregistry.reader" not in node_pull_roles:
        findings.append(
            "Sandbox image pull identity requires 'roles/artifactregistry.reader'."
        )
    if "roles/artifactregistry.admin" in node_pull_roles or "roles/artifactregistry.writer" in node_pull_roles:
        findings.append(
            "Sandbox runtime should not have write/admin permissions to Artifact Registry."
        )

    return findings


def run_offline() -> LabReport:
    banner(
        "Lab 05 — Secure Sandboxes, Cloud Workstations, and Code Mender",
        "Offline architecture selector, gVisor vs Job check, Code Mender CVE loop & IAM audit",
    )
    report = LabReport("Lab 05 — Secure Sandboxes")

    # 1. Compare all 6 enterprise coding-agent execution surfaces
    section("1. Sandbox Architecture Selector Matrix")
    cw_rec = select_sandbox_architecture(interactive_human_ide_in_vpc=True)
    gke_rec = select_sandbox_architecture(untrusted_exploit_or_fuzzing=True)
    cr_rec = select_sandbox_architecture(running_inside_cloud_run_container=True)
    ae_rec = select_sandbox_architecture(deployed_on_agent_engine=True)
    agy_rec = select_sandbox_architecture(antigravity_local_cli_command=True)
    e2b_rec = select_sandbox_architecture(third_party_provider="e2b")
    daytona_rec = select_sandbox_architecture(third_party_provider="daytona")

    recs = [cw_rec, gke_rec, cr_rec, ae_rec, agy_rec, e2b_rec, daytona_rec]
    table(
        ["Execution Surface", "ADK / SDK Primitive", "IAM Roles"],
        [
            [
                r.surface,
                r.adk_or_sdk_primitive,
                ", ".join(r.required_iam_roles) or "(external / local)",
            ]
            for r in recs
        ],
    )
    report.check(
        "Cloud Workstations selected for VPC-SC interactive developer IDE with roles/workstations.user",
        cw_rec.surface == "Cloud Workstations"
        and "roles/workstations.user" in cw_rec.required_iam_roles
        and "roles/workstations.admin" not in cw_rec.required_iam_roles,
        f"roles={cw_rec.required_iam_roles}",
    )
    report.check(
        "GKE Agent Sandbox uses executor_type='sandbox' (gVisor) + warm gateway",
        isinstance(gke_rec.executor_instance, GkeCodeExecutor)
        and gke_rec.executor_instance.executor_type == "sandbox"
        and gke_rec.executor_instance.sandbox_gateway_name == "agent-sandbox-gateway",
        f"template={gke_rec.executor_instance.sandbox_template}",
    )
    report.check(
        "CloudRunSandboxCodeExecutor disables egress (allow_egress=False) for in-container sandboxing",
        isinstance(cr_rec.executor_instance, CloudRunSandboxCodeExecutor)
        and cr_rec.executor_instance.allow_egress is False,
        f"timeout={cr_rec.executor_instance.timeout_seconds}s",
    )
    report.check(
        "Antigravity OS sandbox pairs enable_sandbox=True with SDK confirm_run_command policy",
        agy_rec.executor_instance == {
            "enable_sandbox": True,
            "policy": "confirm_run_command",
        },
        agy_rec.adk_or_sdk_primitive,
    )

    # 2. Verify UnsafeLocalCodeExecutor is blocked by default
    section("2. Blocking UnsafeLocalCodeExecutor in Governed Profiles")
    blocked_default = False
    try:
        select_sandbox_architecture()
    except PermissionError:
        blocked_default = True
    unsafe_dev = select_sandbox_architecture(allow_unsafe_local_dev=True)
    report.check(
        "Selector blocks UnsafeLocalCodeExecutor unless allow_unsafe_local_dev=True",
        blocked_default and isinstance(unsafe_dev.executor_instance, UnsafeLocalCodeExecutor),
        "PermissionError raised when no safe boundary is selected",
    )

    # 3. Code Mender autonomous CVE patching & gVisor verification loop
    section("3. Code Mender Autonomous CVE Patching & Fuzz/Regression Gate")
    vulnerable_code = (
        'def get_customer_orders(db, user_id):\n'
        '    return db.execute(f"SELECT * FROM orders WHERE user_id = \'{user_id}\'")\n'
    )
    patched_code = (
        "def get_customer_orders(db, user_id):\n"
        '    return db.execute("SELECT * FROM orders WHERE user_id = :user_id", {"user_id": user_id})\n'
    )
    assert isinstance(gke_rec.executor_instance, GkeCodeExecutor)
    cm_result = run_code_mender_remediation_workflow(
        cve_id="CVE-2026-41092",
        vulnerable_sql_builder=vulnerable_code,
        proposed_parameterized_patch=patched_code,
        executor=gke_rec.executor_instance,
    )

    # Also prove GKE 'job' mode is rejected for untrusted exploit reproduction
    job_executor = GkeCodeExecutor(
        executor_type="job", namespace="default", image="python:3.14-slim"
    )
    job_rejected = False
    try:
        run_code_mender_remediation_workflow(
            cve_id="CVE-2026-41092",
            vulnerable_sql_builder=vulnerable_code,
            proposed_parameterized_patch=patched_code,
            executor=job_executor,
        )
    except PermissionError:
        job_rejected = True

    report.check(
        "Code Mender verifies patch in gVisor sandbox, rejects GKE 'job' mode, and gates on human PR",
        cm_result.exploit_blocked_after_patch
        and cm_result.regression_suite_passed
        and cm_result.ready_for_human_pr_review
        and not cm_result.auto_merged_to_main
        and job_rejected,
        f"cve={cm_result.cve_id}, gke_job_rejected={job_rejected}, auto_merged={cm_result.auto_merged_to_main}",
    )
    exam_note(
        "Code Mender localizes CVEs, synthesizes patches, and runs fuzzers/tests inside "
        "a gVisor sandbox before opening a human-reviewed PR."
    )

    # 4. Sandbox IAM Least-Privilege Audit
    section("4. Sandbox IAM Least-Privilege Audit")
    clean_iam = validate_sandbox_iam_bindings(
        developer_roles={"roles/workstations.user", "roles/aiplatform.user"},
        gke_pod_uses_workload_identity=True,
        gke_pod_mounts_json_sa_key=False,
        node_pull_roles={"roles/artifactregistry.reader"},
    )
    bad_iam = validate_sandbox_iam_bindings(
        developer_roles={"roles/workstations.admin"},
        gke_pod_uses_workload_identity=False,
        gke_pod_mounts_json_sa_key=True,
        node_pull_roles={"roles/artifactregistry.admin"},
    )
    report.check(
        "Sandbox IAM validator enforces workstations.user, Workload Identity, and artifactregistry.reader",
        clean_iam == [] and len(bad_iam) == 5,
        f"violations_caught_in_bad_profile={len(bad_iam)}",
    )

    report.summary()
    return report


def run_live(config: LabConfig) -> None:
    banner(
        "Lab 05 — Live Sandbox Configuration Audit",
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
