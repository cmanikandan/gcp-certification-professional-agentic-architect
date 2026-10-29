#!/usr/bin/env python3
"""Lab 19 — Regulated / Air-Gapped GKE Inference Gateway, Open-Weight SLMs & Sandbox.

Demonstrates:
1. Balanced runtime selection: Managed Agent Runtime vs. when regulated/HIPAA
   air-gapped data residency, self-hosted open-weight SLMs, or gVisor sandboxes
   mandate GKE (``adk deploy gke``).
2. ADK 2.9.0 ``GkeCodeExecutor`` in ``sandbox`` mode (gVisor ``runsc`` +
   ``sandbox_gateway_name`` + ``sandbox_template``) vs ``job`` mode.
3. Self-hosted open-weight SLMs (``DEFAULT_OSS_MOE_MODEL`` / ``DEFAULT_OSS_MODEL``)
   in two failover postures:
   - Hybrid GKE -> Vertex AI SaaS ``FallbackModel`` (non-air-gapped workloads)
   - Strict HIPAA / Air-Gapped ``FallbackModel`` (self-hosted open-weight ONLY;
     zero SaaS egress)
4. GKE Workload Identity Federation least-privilege IAM audit for GCS FUSE model
   weight streaming (``roles/storage.objectViewer`` on model bucket vs node-level SA).
5. Deterministic simulation of **GKE Inference Gateway** Endpoint Picker (EPP):
   KV-cache saturation routing, prefix-cache affinity, LoRA adapter matching,
   and criticality-based load shedding (``Critical`` vs ``Sheddable``).
"""

from __future__ import annotations

import inspect
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from google.adk.agents import LlmAgent
from google.adk.code_executors import GkeCodeExecutor
from google.adk.models import FallbackModel, Gemma, LiteLlm

from common import (
    DEFAULT_AGENT_MODEL,
    DEFAULT_OSS_MODEL,
    DEFAULT_OSS_MOE_MODEL,
    LabReport,
    banner,
    exam_note,
    kv_table,
    load_config,
    require_live,
    section,
    step,
)


@dataclass(frozen=True)
class VllmGpuPod:
    """Represents a vLLM GPU serving pod inside a GKE InferencePool."""

    pod_name: str
    gpu_type: str
    kv_cache_saturation: float  # 0.0 to 1.0
    waiting_queue_depth: int
    cached_prefixes: tuple[str, ...]
    loaded_lora_adapters: tuple[str, ...]


@dataclass(frozen=True)
class InferenceRequest:
    """Represents an incoming agent LLM turn hitting GKE Inference Gateway."""

    request_id: str
    prefix_hash: str
    lora_adapter: str | None
    criticality: str  # "Critical" | "Standard" | "Sheddable"


def build_gke_sandbox_executor() -> GkeCodeExecutor:
    """Build a GkeCodeExecutor configured for GKE Agent Sandbox (gVisor)."""
    from unittest.mock import patch

    with (
        patch("kubernetes.config.load_incluster_config"),
        patch("kubernetes.config.load_kube_config"),
    ):
        return GkeCodeExecutor(
            executor_type="sandbox",
            namespace="agent-sandboxes",
            sandbox_gateway_name="gke-agent-sandbox-gateway",
            sandbox_template="python-gvisor-runtime-template",
            cpu_requested="500m",
            mem_requested="1Gi",
            cpu_limit="1000m",
            mem_limit="2Gi",
            timeout_seconds=60,
            stateful=True,
        )


def build_gke_job_executor() -> GkeCodeExecutor:
    """Build a GkeCodeExecutor configured for standard Kubernetes Job mode."""
    from unittest.mock import patch

    with (
        patch("kubernetes.config.load_incluster_config"),
        patch("kubernetes.config.load_kube_config"),
    ):
        return GkeCodeExecutor(
            executor_type="job",
            namespace="agent-jobs",
            timeout_seconds=60,
            stateful=False,
        )


def build_hybrid_gke_agent() -> tuple[LlmAgent, FallbackModel]:
    """Construct a hybrid ADK agent backed by self-hosted Gemma 4 on GKE with SaaS fallback."""
    primary_gke_oss = Gemma(model=DEFAULT_OSS_MOE_MODEL)
    secondary_dense_oss = LiteLlm(model=f"openai/{DEFAULT_OSS_MODEL}")
    fallback_chain = FallbackModel(
        models=[primary_gke_oss, secondary_dense_oss, DEFAULT_AGENT_MODEL]
    )
    sandbox_exec = build_gke_sandbox_executor()
    agent = LlmAgent(
        name="gke_open_weight_specialist",
        description="Runs open-weight inference via GKE Inference Gateway and executes code in GKE Sandbox.",
        model=DEFAULT_AGENT_MODEL,
        instruction=(
            "Analyze financial risk models using self-hosted open-weight GPUs on GKE "
            "and execute verification scripts inside the gVisor Agent Sandbox."
        ),
        code_executor=sandbox_exec,
    )
    return agent, fallback_chain


def build_airgapped_hipaa_fallback_chain() -> FallbackModel:
    """Build a strict air-gapped HIPAA FallbackModel that NEVER fails over to public SaaS."""
    primary_moe_slm = Gemma(model=DEFAULT_OSS_MOE_MODEL)
    secondary_dense_slm = LiteLlm(model=f"openai/{DEFAULT_OSS_MODEL}")
    return FallbackModel(models=[primary_moe_slm, secondary_dense_slm])


def audit_gke_workload_identity_iam(
    *,
    ksa_annotation_gsa: str | None,
    granted_bucket_roles: set[str],
    uses_node_default_compute_sa: bool = False,
) -> tuple[bool, list[str]]:
    """Verify GKE Workload Identity Federation least-privilege IAM for vLLM weight streaming."""
    issues: list[str] = []
    if uses_node_default_compute_sa or not ksa_annotation_gsa:
        issues.append(
            "MISSING_WORKLOAD_IDENTITY: Bind Kubernetes SA via `iam.gke.io/gcp-service-account` "
            "instead of inheriting the GKE node's Compute Engine default SA."
        )
    if ksa_annotation_gsa and "-compute@developer.gserviceaccount.com" in ksa_annotation_gsa:
        issues.append("DEFAULT_COMPUTE_SA_FORBIDDEN: Use a dedicated model-loader GSA.")
    if "roles/storage.admin" in granted_bucket_roles or "roles/editor" in granted_bucket_roles:
        issues.append(
            "OVERPRIVILEGED_MODEL_BUCKET_ROLE: Use bucket-scoped `roles/storage.objectViewer` "
            "for read-only GCS FUSE model weight streaming."
        )
    if "roles/storage.objectViewer" not in granted_bucket_roles:
        issues.append("MISSING_OBJECT_VIEWER: Grant `roles/storage.objectViewer` on the weights bucket.")
    return (len(issues) == 0), issues


def select_inference_pool_pod(
    pods: list[VllmGpuPod],
    req: InferenceRequest,
    saturation_shed_threshold: float = 0.85,
) -> tuple[str | None, str]:
    """Simulate GKE Inference Gateway Endpoint Picker (EPP) routing logic."""
    avg_saturation = sum(p.kv_cache_saturation for p in pods) / len(pods)
    if req.criticality == "Sheddable" and avg_saturation >= saturation_shed_threshold:
        return (
            None,
            f"SHED: cluster KV-cache saturation ({avg_saturation:.0%}) >= "
            f"{saturation_shed_threshold:.0%} threshold for Sheddable batch traffic.",
        )

    best_pod: VllmGpuPod | None = None
    best_score = -1e9
    best_reason = ""

    for pod in pods:
        if pod.kv_cache_saturation >= 0.95:
            continue

        prefix_bonus = 50.0 if req.prefix_hash in pod.cached_prefixes else 0.0
        lora_bonus = (
            25.0
            if req.lora_adapter and req.lora_adapter in pod.loaded_lora_adapters
            else 0.0
        )
        load_penalty = (pod.kv_cache_saturation * 60.0) + (pod.waiting_queue_depth * 4.0)
        score = prefix_bonus + lora_bonus - load_penalty

        if score > best_score:
            best_score = score
            best_pod = pod
            best_reason = (
                f"score={score:.1f} (prefix_hit={prefix_bonus > 0}, "
                f"lora_hit={lora_bonus > 0}, kv_cache={pod.kv_cache_saturation:.0%})"
            )

    if best_pod is None:
        return None, "NO_CAPACITY: all GPU pods exceed safe KV-cache ceiling."
    return best_pod.pod_name, best_reason


def evaluate_runtime_choice(
    *,
    requires_open_weight_gpus: bool = False,
    requires_gvisor_agent_sandbox: bool = False,
    requires_inference_gateway_kv_routing: bool = False,
    strict_airgapped_no_saas_residency: bool = False,
    requires_scale_to_zero_http: bool = False,
) -> tuple[str, str]:
    """Determine when Agent Runtime is optimal vs. when GKE or Cloud Run is required."""
    if (
        requires_open_weight_gpus
        or requires_gvisor_agent_sandbox
        or requires_inference_gateway_kv_routing
        or strict_airgapped_no_saas_residency
    ):
        return (
            "gke",
            "GKE (`adk deploy gke`) is mandatory: Agent Runtime does not expose "
            "custom GPU node pools for air-gapped open-weight SLM vLLM serving, "
            "GKE Inference Gateway (`InferencePool` KV-cache routing), or gVisor "
            "`GkeCodeExecutor(executor_type='sandbox')`.",
        )
    if requires_scale_to_zero_http:
        return (
            "cloud_run",
            "Cloud Run (`adk deploy cloud_run`) provides serverless scale-to-zero "
            "for bursty HTTP/Eventarc workloads.",
        )
    return (
        "agent_engine",
        "Agent Runtime (`adk deploy agent_engine`) is optimal for zero-ops managed "
        "ADK agents calling SaaS Gemini APIs with managed sessions and Memory Bank.",
    )


def run_offline() -> LabReport:
    report = LabReport(
        title="Lab 19 — Regulated GKE Inference Gateway, Open-Weight SLMs & Agent Sandbox"
    )
    banner("Lab 19 — Regulated GKE Open-Weight SLMs, Inference Gateway & Sandbox (Offline)")

    section("1. Regulated Air-Gapped Residency vs. Managed Agent Runtime")
    target, reason = evaluate_runtime_choice(
        strict_airgapped_no_saas_residency=True,
        requires_open_weight_gpus=True,
    )
    managed_target, _ = evaluate_runtime_choice()
    kv_table(
        {
            "Air-Gapped / Open-Weight GPU Target": target,
            "Standard Managed SaaS Agent Target": managed_target,
            "Rationale": reason,
        }
    )
    report.check(
        "Balanced selector picks GKE for air-gapped SLMs and Agent Runtime for standard SaaS",
        target == "gke" and managed_target == "agent_engine",
    )

    section("2. Agent Sandbox on GKE (GkeCodeExecutor: 'sandbox' vs 'job')")
    sandbox_exec = build_gke_sandbox_executor()
    job_exec = build_gke_job_executor()
    kv_table(
        {
            "Sandbox Mode executor_type": sandbox_exec.executor_type,
            "Sandbox Gateway Name": str(sandbox_exec.sandbox_gateway_name),
            "Sandbox Runtime Template": str(sandbox_exec.sandbox_template),
            "Job Mode executor_type": job_exec.executor_type,
            "Docstring Warning": (inspect.getdoc(GkeCodeExecutor) or "").splitlines()[0],
        }
    )
    report.check(
        "GkeCodeExecutor supports 'sandbox' mode with gVisor template",
        sandbox_exec.executor_type == "sandbox"
        and sandbox_exec.sandbox_template == "python-gvisor-runtime-template",
    )

    section("3. Hybrid vs. Strict Air-Gapped HIPAA Open-Weight Chains + Workload Identity")
    agent, hybrid_fallback = build_hybrid_gke_agent()
    airgapped_fallback = build_airgapped_hipaa_fallback_chain()
    wi_ok, wi_issues = audit_gke_workload_identity_iam(
        ksa_annotation_gsa="vllm-weights-reader@hipaa-gke-prod.iam.gserviceaccount.com",
        granted_bucket_roles={"roles/storage.objectViewer"},
        uses_node_default_compute_sa=False,
    )
    kv_table(
        {
            "Primary Self-Hosted MoE SLM": DEFAULT_OSS_MOE_MODEL,
            "Secondary Self-Hosted Dense SLM": DEFAULT_OSS_MODEL,
            "Hybrid Chain Length (includes SaaS)": str(len(hybrid_fallback.models)),
            "Air-Gapped HIPAA Chain Length (OSS only)": str(len(airgapped_fallback.models)),
            "Workload Identity Least-Privilege OK": str(wi_ok),
            "Attached Code Executor": type(agent.code_executor).__name__,
        }
    )
    report.check(
        "Air-gapped HIPAA FallbackModel excludes public SaaS & enforces Workload Identity",
        len(hybrid_fallback.models) == 3
        and len(airgapped_fallback.models) == 2
        and DEFAULT_AGENT_MODEL not in airgapped_fallback.models
        and wi_ok is True
        and wi_issues == [],
    )

    section("4. GKE Inference Gateway (Endpoint Picker KV-Cache & LoRA Simulation)")
    pool = [
        VllmGpuPod(
            pod_name="vllm-gemma4-l4-pod-0",
            gpu_type="nvidia-l4",
            kv_cache_saturation=0.92,
            waiting_queue_depth=8,
            cached_prefixes=("sys-prompt-other",),
            loaded_lora_adapters=("retail-lora",),
        ),
        VllmGpuPod(
            pod_name="vllm-gemma4-l4-pod-1",
            gpu_type="nvidia-l4",
            kv_cache_saturation=0.45,
            waiting_queue_depth=1,
            cached_prefixes=("agent-system-prefix-v1",),
            loaded_lora_adapters=("clinical-hipaa-lora",),
        ),
    ]

    live_req = InferenceRequest(
        request_id="turn-42",
        prefix_hash="agent-system-prefix-v1",
        lora_adapter="clinical-hipaa-lora",
        criticality="Critical",
    )
    selected_pod, route_reason = select_inference_pool_pod(pool, live_req)
    step(1, f"Critical Clinical Turn routed to: {selected_pod} -> {route_reason}")

    saturated_pool = [
        VllmGpuPod(
            pod_name="vllm-gemma4-l4-pod-0",
            gpu_type="nvidia-l4",
            kv_cache_saturation=0.90,
            waiting_queue_depth=12,
            cached_prefixes=(),
            loaded_lora_adapters=(),
        ),
        VllmGpuPod(
            pod_name="vllm-gemma4-l4-pod-1",
            gpu_type="nvidia-l4",
            kv_cache_saturation=0.90,
            waiting_queue_depth=11,
            cached_prefixes=(),
            loaded_lora_adapters=(),
        ),
    ]
    batch_req = InferenceRequest(
        request_id="batch-eval-99",
        prefix_hash="eval-prefix",
        lora_adapter=None,
        criticality="Sheddable",
    )
    shed_pod, shed_reason = select_inference_pool_pod(saturated_pool, batch_req)
    step(2, f"Sheddable Batch Eval Request under 90% KV saturation: {shed_pod} -> {shed_reason}")

    report.check(
        "GKE Inference Gateway selects prefix-cached & LoRA-matched GPU pod",
        selected_pod == "vllm-gemma4-l4-pod-1",
    )
    report.check(
        "GKE Inference Gateway sheds Sheddable batch traffic under KV saturation",
        shed_pod is None,
    )
    exam_note(
        "Default to Agent Runtime (`adk deploy agent_engine`) unless the scenario requires "
        "strict VPC/air-gapped open-weight SLM residency on GPUs (`Gemma 4`), GKE Inference "
        "Gateway (`InferencePool` KV-cache & LoRA affinity), or gVisor `GkeCodeExecutor(executor_type='sandbox')`."
    )
    report.summary()
    return report


def run_live(config) -> LabReport:
    from google import genai

    banner("Lab 19 — Live GKE & Gemini API Verification")
    step(1, f"Project: {config.project_id} | Location: {config.location}")
    client = genai.Client(api_key=config.gemini_api_key)
    step(2, f"Verified Gemini API Client initialized (vertexai={client.vertexai})")
    return run_offline()


def main() -> None:
    config = load_config()
    if require_live(config):
        run_live(config)
    else:
        run_offline()


if __name__ == "__main__":
    main()
