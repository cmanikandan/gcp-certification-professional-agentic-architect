"""Tests for Lab 14 — Deployment Runtimes, Managed Sessions & Memory Bank."""

from __future__ import annotations

import importlib
import os
import sys

from google.adk.memory import VertexAiMemoryBankService
from google.adk.sessions import InMemorySessionService, VertexAiSessionService

from common.models import MODEL_CATALOG

LAB_DIR = os.path.dirname(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(LAB_DIR, "../../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

agent = importlib.import_module("tracks.04_evaluate_and_deploy.lab_14_deployment_runtimes.agent")
lab = importlib.import_module("tracks.04_evaluate_and_deploy.lab_14_deployment_runtimes.lab")


def test_uses_only_verified_models() -> None:
    assert agent.AGENT_MODEL in MODEL_CATALOG


def test_dockerfile_exists() -> None:
    dockerfile_path = os.path.join(LAB_DIR, "Dockerfile")
    assert os.path.exists(dockerfile_path)
    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "adk" in content
    assert "api_server" in content


def test_agent_runtime_managed_sessions_memory_and_vpc_sc_worker_pool() -> None:
    sess_svc, mem_svc, ae_sbx = lab.build_agent_runtime_state_services()
    assert isinstance(sess_svc, VertexAiSessionService)
    assert isinstance(mem_svc, VertexAiMemoryBankService)
    assert ae_sbx.timeout_seconds == 60

    bp = lab.select_deployment_blueprint(
        needs_managed_sessions_and_memory_bank=True,
        vpc_sc_perimeter=True,
    )
    assert bp.deploy_target == "agent_engine"
    assert "--worker_pool=" in bp.cli_command
    assert bp.session_backend == "VertexAiSessionService"
    assert bp.memory_backend == "VertexAiMemoryBankService"


def test_cloud_run_vs_gke_blueprint_selection() -> None:
    cr_bp = lab.select_deployment_blueprint(needs_scale_to_zero_eventarc=True)
    assert cr_bp.deploy_target == "cloud_run"
    assert "--session_service_uri=redis://" in cr_bp.cli_command

    gke_bp = lab.select_deployment_blueprint(
        needs_self_hosted_open_weight_gpus_or_gvisor=True
    )
    assert gke_bp.deploy_target == "gke"
    assert "--cluster_name=" in gke_bp.cli_command

    redis_cfg, cr_sbx = lab.build_cloud_run_stateless_safe_config()
    assert redis_cfg.ssl is True
    assert cr_sbx.allow_egress is False


def test_runtime_identity_and_state_auditor_catches_exam_antipatterns() -> None:
    ok_bad, findings_bad = lab.validate_runtime_identity_and_state(
        deploy_target="agent_engine",
        service_account_email="998877665544-compute@developer.gserviceaccount.com",
        session_service_name=InMemorySessionService.__name__,
        vpc_sc_enforced=True,
        worker_pool=None,
    )
    assert ok_bad is False
    assert len(findings_bad) == 3
    assert any("DEFAULT_COMPUTE_SA_FORBIDDEN" in f for f in findings_bad)
    assert any("EPHEMERAL_SESSION_LOSS" in f for f in findings_bad)
    assert any("VPC_SC_MISSING_WORKER_POOL" in f for f in findings_bad)

    ok_good, findings_good = lab.validate_runtime_identity_and_state(
        deploy_target="agent_engine",
        service_account_email="support-runtime-sa@my-proj.iam.gserviceaccount.com",
        session_service_name=VertexAiSessionService.__name__,
        vpc_sc_enforced=True,
        worker_pool="projects/my-proj/locations/us-central1/workerPools/vpc-pool",
    )
    assert ok_good is True
    assert findings_good == []
