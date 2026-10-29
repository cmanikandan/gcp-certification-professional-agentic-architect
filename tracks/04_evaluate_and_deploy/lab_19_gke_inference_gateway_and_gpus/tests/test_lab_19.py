"""Tests for Lab 19 — Regulated GKE Inference Gateway, Open-Weight SLMs & Sandbox."""

from __future__ import annotations

import lab
from common.models import (
    DEFAULT_AGENT_MODEL,
    DEFAULT_OSS_MODEL,
    DEFAULT_OSS_MOE_MODEL,
    MODEL_CATALOG,
)


def test_verified_models_in_catalog() -> None:
    assert DEFAULT_AGENT_MODEL in MODEL_CATALOG
    assert DEFAULT_OSS_MODEL in MODEL_CATALOG
    assert DEFAULT_OSS_MOE_MODEL in MODEL_CATALOG


def test_gke_sandbox_vs_job_executor_isolation() -> None:
    sandbox_exec = lab.build_gke_sandbox_executor()
    job_exec = lab.build_gke_job_executor()

    assert sandbox_exec.executor_type == "sandbox"
    assert sandbox_exec.sandbox_gateway_name == "gke-agent-sandbox-gateway"
    assert sandbox_exec.sandbox_template == "python-gvisor-runtime-template"
    assert sandbox_exec.stateful is True

    assert job_exec.executor_type == "job"
    assert job_exec.stateful is False


def test_runtime_decision_chooses_gke_for_airgapped_slms_and_agent_runtime_by_default() -> None:
    target, rationale = lab.evaluate_runtime_choice(
        requires_open_weight_gpus=True,
        requires_gvisor_agent_sandbox=False,
        requires_inference_gateway_kv_routing=False,
    )
    assert target == "gke"
    assert "Agent Runtime" in rationale

    target_airgap, _ = lab.evaluate_runtime_choice(
        strict_airgapped_no_saas_residency=True,
    )
    assert target_airgap == "gke"

    target_igw, _ = lab.evaluate_runtime_choice(
        requires_inference_gateway_kv_routing=True,
    )
    assert target_igw == "gke"

    target_default, _ = lab.evaluate_runtime_choice()
    assert target_default == "agent_engine"


def test_airgapped_hipaa_fallback_excludes_saas_and_workload_identity_iam() -> None:
    _, hybrid_chain = lab.build_hybrid_gke_agent()
    airgap_chain = lab.build_airgapped_hipaa_fallback_chain()

    assert len(hybrid_chain.models) == 3
    assert DEFAULT_AGENT_MODEL in hybrid_chain.models

    assert len(airgap_chain.models) == 2
    assert DEFAULT_AGENT_MODEL not in airgap_chain.models

    ok, issues = lab.audit_gke_workload_identity_iam(
        ksa_annotation_gsa="vllm-loader@hipaa-gke.iam.gserviceaccount.com",
        granted_bucket_roles={"roles/storage.objectViewer"},
        uses_node_default_compute_sa=False,
    )
    assert ok is True
    assert issues == []

    bad_ok, bad_issues = lab.audit_gke_workload_identity_iam(
        ksa_annotation_gsa="112233-compute@developer.gserviceaccount.com",
        granted_bucket_roles={"roles/storage.admin"},
        uses_node_default_compute_sa=True,
    )
    assert bad_ok is False
    assert len(bad_issues) >= 3


def test_inference_gateway_prefers_prefix_cache_and_sheds_batch_under_load() -> None:
    pods = [
        lab.VllmGpuPod(
            pod_name="pod-busy-no-prefix",
            gpu_type="nvidia-l4",
            kv_cache_saturation=0.88,
            waiting_queue_depth=10,
            cached_prefixes=(),
            loaded_lora_adapters=(),
        ),
        lab.VllmGpuPod(
            pod_name="pod-prefix-hit",
            gpu_type="nvidia-l4",
            kv_cache_saturation=0.40,
            waiting_queue_depth=1,
            cached_prefixes=("shared-agent-prefix",),
            loaded_lora_adapters=("risk-lora",),
        ),
    ]
    req = lab.InferenceRequest(
        request_id="r1",
        prefix_hash="shared-agent-prefix",
        lora_adapter="risk-lora",
        criticality="Critical",
    )
    chosen, reason = lab.select_inference_pool_pod(pods, req)
    assert chosen == "pod-prefix-hit"
    assert "prefix_hit=True" in reason
    assert "lora_hit=True" in reason

    saturated = [
        lab.VllmGpuPod("p0", "nvidia-l4", 0.90, 5, (), ()),
        lab.VllmGpuPod("p1", "nvidia-l4", 0.90, 5, (), ()),
    ]
    shed_req = lab.InferenceRequest("r2", "p", None, criticality="Sheddable")
    shed_chosen, shed_reason = lab.select_inference_pool_pod(saturated, shed_req)
    assert shed_chosen is None
    assert "SHED" in shed_reason
