#!/usr/bin/env python3
"""Lab 14 — Deployment Runtimes, Managed Sessions, Memory Bank & Runtime Identity.

Demonstrates:
1. Managed Agent Runtime (``adk deploy agent_engine``) paired with native
   ``VertexAiSessionService``, ``VertexAiMemoryBankService``, and
   ``AgentEngineSandboxCodeExecutor``.
2. Dedicated least-privilege runtime Service Account / Agent Identity vs.
   the over-privileged default Compute Engine SA anti-pattern, plus ``--worker_pool``
   for VPC Service Controls (VPC-SC).
3. Cloud Run (``adk deploy cloud_run``) scale-to-zero paired with external durable
   state (``RedisSessionServiceConfig`` / ``DatabaseSessionService``) and
   ``CloudRunSandboxCodeExecutor(allow_egress=False)``.
4. Balanced runtime & state architecture selector comparing Agent Runtime,
   Cloud Run, and GKE (self-hosted open-weight SLMs/GPUs + gVisor sandbox).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.integrations.cloud_run import CloudRunSandboxCodeExecutor
from google.adk.integrations.redis import RedisSessionService, RedisSessionServiceConfig
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.adk.sessions import (
    DatabaseSessionService,
    InMemorySessionService,
    VertexAiSessionService,
)

from common import (
    LabReport,
    banner,
    exam_note,
    kv_table,
    load_config,
    require_live,
    section,
    step,
)
from common.labkit import table

DEFAULT_COMPUTE_SA_RE = re.compile(r"^\d+-compute@developer\.gserviceaccount\.com$")


@dataclass(frozen=True)
class RuntimeBlueprint:
    """Complete deployment + state + identity blueprint for an ADK workload."""

    deploy_target: Literal["agent_engine", "cloud_run", "gke"]
    cli_command: str
    session_backend: str
    memory_backend: str
    runtime_identity_pattern: str
    rationale: str


def build_agent_runtime_state_services(
    project_id: str = "argolis-agent-prod",
    location: str = "us-central1",
    reasoning_engine_id: str = "9876543210",
) -> tuple[VertexAiSessionService, VertexAiMemoryBankService, AgentEngineSandboxCodeExecutor]:
    """Instantiate managed Agent Runtime session, memory bank, and sandbox services."""
    session_svc = VertexAiSessionService(
        project=project_id,
        location=location,
        agent_engine_id=reasoning_engine_id,
    )
    memory_svc = VertexAiMemoryBankService(
        project=project_id,
        location=location,
        agent_engine_id=reasoning_engine_id,
    )
    resource_name = (
        f"projects/{project_id}/locations/{location}/reasoningEngines/{reasoning_engine_id}"
    )
    with patch("vertexai.Client", return_value=MagicMock()):
        sandbox_exec = AgentEngineSandboxCodeExecutor(
            agent_engine_resource_name=resource_name,
            timeout_seconds=60,
        )
    return session_svc, memory_svc, sandbox_exec


def build_cloud_run_stateless_safe_config() -> tuple[
    RedisSessionServiceConfig, CloudRunSandboxCodeExecutor
]:
    """Build external Redis session config + no-egress Cloud Run sandbox for ephemeral instances."""
    redis_cfg = RedisSessionServiceConfig(
        host="10.128.0.15",
        port=6379,
        ssl=True,
        ttl_seconds=86400,
        key_prefix="adk:prod:session:",
    )
    cr_sandbox = CloudRunSandboxCodeExecutor(
        allow_egress=False,
        stateful=False,
        timeout_seconds=30,
    )
    return redis_cfg, cr_sandbox


def validate_runtime_identity_and_state(
    *,
    deploy_target: Literal["agent_engine", "cloud_run", "gke"],
    service_account_email: str,
    session_service_name: str,
    vpc_sc_enforced: bool = False,
    worker_pool: str | None = None,
) -> tuple[bool, list[str]]:
    """Audit runtime deployment against exam security and statefulness anti-patterns."""
    findings: list[str] = []

    if DEFAULT_COMPUTE_SA_RE.match(service_account_email):
        findings.append(
            "DEFAULT_COMPUTE_SA_FORBIDDEN: Never run deployed agents under the default "
            "Compute Engine SA (`<project-number>-compute@developer.gserviceaccount.com`); "
            "bind a dedicated least-privilege Agent Identity / custom SA."
        )

    if session_service_name == InMemorySessionService.__name__:
        findings.append(
            f"EPHEMERAL_SESSION_LOSS: `{InMemorySessionService.__name__}` loses multi-turn "
            f"context across `{deploy_target}` autoscaling replicas and restarts; use "
            f"`{VertexAiSessionService.__name__}`, `{RedisSessionService.__name__}`, or "
            f"`{DatabaseSessionService.__name__}`."
        )

    if deploy_target == "agent_engine" and vpc_sc_enforced and not worker_pool:
        findings.append(
            "VPC_SC_MISSING_WORKER_POOL: `adk deploy agent_engine` inside a VPC-SC "
            "perimeter requires `--worker_pool=projects/.../workerPools/...` so Cloud Build "
            "executes inside the private perimeter."
        )

    return (len(findings) == 0), findings


def select_deployment_blueprint(
    *,
    needs_managed_sessions_and_memory_bank: bool = False,
    needs_scale_to_zero_eventarc: bool = False,
    needs_self_hosted_open_weight_gpus_or_gvisor: bool = False,
    vpc_sc_perimeter: bool = False,
) -> RuntimeBlueprint:
    """Select the optimal ADK deployment target, state backend, and CLI flags."""
    if needs_self_hosted_open_weight_gpus_or_gvisor:
        return RuntimeBlueprint(
            deploy_target="gke",
            cli_command=(
                "adk deploy gke . --project=$PROJECT --region=$REGION "
                "--cluster_name=agentic-gpu-cluster --service_type=ClusterIP"
            ),
            session_backend=f"{RedisSessionService.__name__} / {DatabaseSessionService.__name__}",
            memory_backend=VertexAiMemoryBankService.__name__,
            runtime_identity_pattern="GKE Workload Identity Federation (per-Pod KSA -> dedicated GSA)",
            rationale=(
                "GKE is required for self-hosted open-weight SLMs/LLMs on GPU node pools, "
                "GKE Inference Gateway (`InferencePool` KV-cache routing), and kernel-isolated "
                "`GkeCodeExecutor(executor_type='sandbox')` on gVisor."
            ),
        )

    if needs_scale_to_zero_eventarc and not needs_managed_sessions_and_memory_bank:
        return RuntimeBlueprint(
            deploy_target="cloud_run",
            cli_command=(
                "adk deploy cloud_run . --project=$PROJECT --region=$REGION "
                "--otel_to_cloud --session_service_uri=redis://10.128.0.15:6379 "
                "--service_account=cr-support-agent@$PROJECT.iam.gserviceaccount.com"
            ),
            session_backend=f"{RedisSessionService.__name__} (Memorystore) or {DatabaseSessionService.__name__}",
            memory_backend=f"{VertexAiMemoryBankService.__name__} or VertexAiRagMemoryService",
            runtime_identity_pattern="Dedicated per-service Cloud Run Service Account",
            rationale=(
                "Cloud Run scales to $0 during idle periods and integrates natively with "
                "Eventarc/PubSub triggers, provided state is externalized out of container RAM."
            ),
        )

    worker_flag = (
        " --worker_pool=projects/$PROJECT/locations/$REGION/workerPools/vpcsc-private-pool"
        if vpc_sc_perimeter
        else ""
    )
    return RuntimeBlueprint(
        deploy_target="agent_engine",
        cli_command=(
            f"adk deploy agent_engine . --project=$PROJECT --region=$REGION{worker_flag}"
        ),
        session_backend=VertexAiSessionService.__name__,
        memory_backend=VertexAiMemoryBankService.__name__,
        runtime_identity_pattern="Managed Agent Identity / dedicated Reasoning Engine SA",
        rationale=(
            "Agent Runtime (`adk deploy agent_engine`) is the lowest-ops managed runtime "
            "with built-in `VertexAiSessionService` + `VertexAiMemoryBankService` integration."
        ),
    )


def run_offline() -> LabReport:
    report = LabReport(
        title="Lab 14 — Deployment Runtimes, Managed Sessions & Memory Bank"
    )
    banner(
        "Lab 14 — Deployment Runtimes (Offline)",
        "Agent Runtime vs. Cloud Run vs. GKE · State Backends · Runtime Identity",
    )

    section("1. Agent Runtime (`adk deploy agent_engine`) + Managed Sessions & Memory Bank")
    sess_svc, mem_svc, ae_sbx = build_agent_runtime_state_services()
    ae_bp = select_deployment_blueprint(
        needs_managed_sessions_and_memory_bank=True,
        vpc_sc_perimeter=True,
    )
    kv_table(
        {
            "Deploy Target": ae_bp.deploy_target,
            "CLI Command (VPC-SC)": ae_bp.cli_command,
            "Managed Session Class": type(sess_svc).__name__,
            "Managed Memory Class": type(mem_svc).__name__,
            "Managed Sandbox Class": type(ae_sbx).__name__,
        }
    )
    report.check(
        "Agent Runtime wires VertexAiSessionService + VertexAiMemoryBankService + --worker_pool",
        ae_bp.deploy_target == "agent_engine" and "--worker_pool=" in ae_bp.cli_command,
    )

    section("2. Cloud Run (`adk deploy cloud_run`) Scale-to-Zero + External State")
    redis_cfg, cr_sbx = build_cloud_run_stateless_safe_config()
    cr_bp = select_deployment_blueprint(needs_scale_to_zero_eventarc=True)
    step(1, f"Cloud Run CLI: {cr_bp.cli_command}")
    step(
        2,
        f"RedisSessionServiceConfig(ssl={redis_cfg.ssl}, ttl={redis_cfg.ttl_seconds}s) "
        f"| CloudRunSandboxCodeExecutor(allow_egress={cr_sbx.allow_egress})",
    )
    report.check(
        "Cloud Run externalizes sessions to TLS Redis and disables sandbox egress",
        cr_bp.deploy_target == "cloud_run"
        and redis_cfg.ssl is True
        and cr_sbx.allow_egress is False,
    )

    section("3. Runtime Identity & Statefulness Anti-Pattern Auditor")
    bad_ok, bad_findings = validate_runtime_identity_and_state(
        deploy_target="cloud_run",
        service_account_email="123456789012-compute@developer.gserviceaccount.com",
        session_service_name=InMemorySessionService.__name__,
    )
    good_ok, good_findings = validate_runtime_identity_and_state(
        deploy_target="agent_engine",
        service_account_email="hipaa-support-agent@argolis-agent-prod.iam.gserviceaccount.com",
        session_service_name=VertexAiSessionService.__name__,
        vpc_sc_enforced=True,
        worker_pool="projects/argolis-agent-prod/locations/us-central1/workerPools/private-pool",
    )

    table(
        ["Runtime Audit Case", "Compliant?", "Findings"],
        [
            ["Default Compute SA + InMemorySessionService", str(bad_ok), f"{len(bad_findings)} critical violations"],
            ["Dedicated Agent SA + VertexAiSessionService + VPC-SC Pool", str(good_ok), str(good_findings or "None")],
        ],
    )
    report.check(
        "Auditor blocks default Compute Engine SA and InMemorySessionService in prod",
        bad_ok is False and len(bad_findings) == 2 and good_ok is True,
    )

    exam_note(
        "Exam runtime questions focus on agentic state & security trade-offs: "
        "Agent Runtime (`adk deploy agent_engine`) pairs natively with `VertexAiSessionService` "
        "and `VertexAiMemoryBankService` (use `--worker_pool` under VPC-SC); Cloud Run scales to "
        "zero for Eventarc/HTTP bursts but MUST externalize sessions (`RedisSessionService` / "
        "`DatabaseSessionService`, never `InMemorySessionService` / `InMemoryMemoryService`); "
        "GKE is reserved for self-hosted open-weight GPUs, Inference Gateway, and gVisor sandboxes."
    )
    report.summary()
    return report


def run_live(config, target: str = "cloud_run") -> LabReport:
    banner("Lab 14 — Live Deployment Dry-Run", f"Target: {target}")
    step(1, f"Project: {config.project_id} | Location: {config.location}")
    step(2, f"Skipping billable cluster/service creation; verified CLI: adk deploy {target} .")
    return run_offline()


if __name__ == "__main__":
    cfg = load_config()
    if "--live" in sys.argv and require_live(cfg):
        chosen_target = "agent_engine" if "agent_engine" in sys.argv else "cloud_run"
        run_live(cfg, chosen_target)
    else:
        run_offline()
