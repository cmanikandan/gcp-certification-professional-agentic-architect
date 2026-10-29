#!/usr/bin/env python3
"""Lab 12: Multi-Agent Orchestration & Cross-Project A2A (Objective 3.3)."""

from __future__ import annotations

import sys
import warnings
from dataclasses import dataclass
from unittest.mock import patch

from common import DEFAULT_AGENT_MODEL, DEFAULT_FAST_MODEL, load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, step, table
from google.adk.a2a.agent import (
    A2aRemoteAgentConfig,
    CardRequestInterceptor,
    RequestInterceptor,
)
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.integrations.agent_registry import AgentRegistry
from google.adk.models import Gemini
from google.adk.tools import MCPToolset, RemoteMcpServer
from google.auth.credentials import AnonymousCredentials


@dataclass(frozen=True)
class CrossProjectBinding:
    """Represents a cross-project IAM binding granted to a caller agent."""

    principal: str
    target_project: str
    resource_scope: str  # "resource" or "project"
    role: str


BANNED_BROAD_ROLES = frozenset(
    {
        "roles/owner",
        "roles/editor",
        "roles/run.admin",
        "roles/aiplatform.admin",
        "roles/bigquery.admin",
        "roles/bigquery.dataViewer",
        "roles/storage.objectViewer",
    }
)


def validate_cross_project_a2a_iam(
    bindings: list[CrossProjectBinding],
    *,
    has_pab_policy: bool,
) -> tuple[bool, list[str]]:
    """Audit cross-project A2A IAM bindings against zero-trust exam rules.

    Enforces:
    1. No unauthenticated public access (`allUsers` / `allAuthenticatedUsers`).
    2. No broad primitive/admin roles or direct cross-project data roles granted to
       the remote caller (data access stays encapsulated inside the specialist project).
    3. Invoker permissions (`roles/run.invoker`, `roles/aiplatform.user`) must be
       resource-scoped rather than broad project-wide grants where possible.
    4. Principal Access Boundary (PAB) policy must be attached to cap blast radius.
    """
    violations: list[str] = []
    if not has_pab_policy:
        violations.append("Missing Principal Access Boundary (PAB) policy on orchestrator identity.")

    for b in bindings:
        if b.principal in {"allUsers", "allAuthenticatedUsers"}:
            violations.append(f"Public principal {b.principal!r} forbidden on {b.target_project}.")
        if b.role in BANNED_BROAD_ROLES:
            violations.append(
                f"Over-privileged or direct data role {b.role!r} granted across projects on {b.target_project}."
            )
        if b.role == "roles/run.invoker" and b.resource_scope != "resource":
            violations.append(
                "roles/run.invoker must be bound at Cloud Run 'resource' scope, not entire project."
            )

    return len(violations) == 0, violations


def compute_cross_project_a2a_latency(
    remote_calls_ms: list[tuple[int, int]],
    coordinator_synthesis_ms: int,
) -> dict[str, int]:
    """Compare serial vs ParallelAgent cross-project A2A execution.

    Each tuple in ``remote_calls_ms`` is ``(network_plus_oidc_ms, remote_agent_ms)``.
    """
    branch_totals = [net + remote for net, remote in remote_calls_ms]
    return {
        "serial_a2a_ms": sum(branch_totals) + coordinator_synthesis_ms,
        "parallel_a2a_ms": (max(branch_totals) if branch_totals else 0) + coordinator_synthesis_ms,
    }


def build_cross_project_support_topology() -> dict[str, object]:
    """Build Coordinator in proj-support-orchestrator calling PCI & HIPAA RemoteA2aAgents."""
    pci_auth = GcpAuthProviderScheme(
        name="projects/proj-support-orchestrator/locations/us-central1/authProviders/pci-run-oidc",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    hipaa_auth = GcpAuthProviderScheme(
        name="projects/proj-support-orchestrator/locations/us-central1/authProviders/hipaa-runtime-oauth",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    a2a_config = A2aRemoteAgentConfig(
        request_interceptors=[RequestInterceptor()],
        card_request_interceptors=[CardRequestInterceptor()],
    )

    pci_billing_agent = RemoteA2aAgent(
        name="pci_billing_specialist",
        description="Autonomous PCI billing dispute & refund agent in proj-pci-billing (Cloud Run).",
        agent_card="https://pci-billing-agent-uc.a.run.app/.well-known/agent-card.json",
        auth_scheme=pci_auth,
        config=a2a_config,
        timeout=30.0,
    )

    hipaa_claims_agent = RemoteA2aAgent(
        name="hipaa_claims_specialist",
        description="Autonomous HIPAA claims adjudication agent in proj-hipaa-claims (Agent Runtime).",
        agent_card="https://us-central1-aiplatform.googleapis.com/v1/projects/proj-hipaa-claims/locations/us-central1/reasoningEngines/claims-01/.well-known/agent-card.json",
        auth_scheme=hipaa_auth,
        config=a2a_config,
        timeout=30.0,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        parallel_remote_fanout = ParallelAgent(
            name="CrossProjectParallelFanOut",
            sub_agents=[pci_billing_agent, hipaa_claims_agent],
        )

    shipping_mcp = RemoteMcpServer(
        name="shipping_policy_mcp",
        url="https://shipping-mcp-internal.a.run.app/mcp",
        allowed_tools=["lookup_carrier_sla"],
    )

    coordinator = LlmAgent(
        name="SupportCoordinator",
        model=Gemini(model=DEFAULT_AGENT_MODEL),
        instruction=(
            "Coordinate cross-project PCI billing and HIPAA claims inquiries via A2A "
            "without ever requesting raw PAN or unredacted PHI."
        ),
        sub_agents=[parallel_remote_fanout],
        disallow_transfer_to_peers=True,
    )

    with patch("google.auth.default", return_value=(AnonymousCredentials(), "proj-shared-governance")):
        registry = AgentRegistry(
            project_id="proj-shared-governance",
            location="us-central1",
        )

    return {
        "coordinator": coordinator,
        "parallel_fanout": parallel_remote_fanout,
        "pci_agent": pci_billing_agent,
        "hipaa_agent": hipaa_claims_agent,
        "a2a_config": a2a_config,
        "shipping_mcp": shipping_mcp,
        "registry": registry,
    }


def run_offline() -> LabReport:
    banner(
        "Lab 12 — Multi-Agent Orchestration & Cross-Project A2A",
        "Objective 3.3: RemoteA2aAgent, AgentRegistry, Least-Privilege IAM & Parallel A2A Latency (Offline)",
    )
    report = LabReport("Lab 12 — Multi-Agent & Cross-Project A2A")

    section("1. Cross-Project A2A Topology & Agent Registry Discovery Plane")
    topo = build_cross_project_support_topology()
    coordinator: LlmAgent = topo["coordinator"]  # type: ignore[assignment]
    pci_agent: RemoteA2aAgent = topo["pci_agent"]  # type: ignore[assignment]
    hipaa_agent: RemoteA2aAgent = topo["hipaa_agent"]  # type: ignore[assignment]
    a2a_cfg: A2aRemoteAgentConfig = topo["a2a_config"]  # type: ignore[assignment]
    shipping_mcp: RemoteMcpServer = topo["shipping_mcp"]  # type: ignore[assignment]
    registry: AgentRegistry = topo["registry"]  # type: ignore[assignment]

    step(1, f"Coordinator '{coordinator.name}' -> parallel A2A peers: {[pci_agent.name, hipaa_agent.name]}")
    step(
        2,
        f"A2aRemoteAgentConfig interceptors: "
        f"request={len(a2a_cfg.request_interceptors or [])}, "
        f"card={len(a2a_cfg.card_request_interceptors or [])}",
    )
    step(3, f"MCP vertical tool server: {shipping_mcp.name} ({MCPToolset.__name__})")
    step(
        4,
        f"AgentRegistry discovery methods verified: "
        f"get_remote_a2a_agent={callable(registry.get_remote_a2a_agent)}, "
        f"get_mcp_toolset={callable(registry.get_mcp_toolset)}",
    )
    report.check(
        "RemoteA2aAgent, A2aRemoteAgentConfig interceptors, and AgentRegistry instantiate offline",
        isinstance(pci_agent, RemoteA2aAgent)
        and isinstance(hipaa_agent, RemoteA2aAgent)
        and callable(registry.get_remote_a2a_agent)
        and callable(registry.get_mcp_toolset),
    )

    section("2. Cross-Project Least-Privilege IAM & PAB Policy Audit")
    compliant_bindings = [
        CrossProjectBinding(
            principal="serviceAccount:sa-support-coord@proj-support-orchestrator.iam.gserviceaccount.com",
            target_project="proj-pci-billing",
            resource_scope="resource",
            role="roles/run.invoker",
        ),
        CrossProjectBinding(
            principal="serviceAccount:sa-support-coord@proj-support-orchestrator.iam.gserviceaccount.com",
            target_project="proj-hipaa-claims",
            resource_scope="resource",
            role="roles/aiplatform.user",
        ),
    ]
    overprivileged_bindings = [
        CrossProjectBinding(
            principal="allUsers",
            target_project="proj-pci-billing",
            resource_scope="project",
            role="roles/run.invoker",
        ),
        CrossProjectBinding(
            principal="serviceAccount:sa-support-coord@proj-support-orchestrator.iam.gserviceaccount.com",
            target_project="proj-pci-billing",
            resource_scope="project",
            role="roles/bigquery.dataViewer",
        ),
    ]
    good_ok, good_violations = validate_cross_project_a2a_iam(compliant_bindings, has_pab_policy=True)
    bad_ok, bad_violations = validate_cross_project_a2a_iam(overprivileged_bindings, has_pab_policy=False)

    step(5, f"Compliant resource-scoped IAM + PAB audit passed: {good_ok}")
    step(6, f"Over-privileged config caught {len(bad_violations)} violations: {bad_violations[0]}")
    exam_note(
        "Cross-project A2A callers get ONLY resource-level roles/run.invoker (or scoped "
        "roles/aiplatform.user) + PAB — NEVER direct roles/bigquery.dataViewer on PCI/HIPAA stores."
    )
    report.check(
        "Cross-project IAM validator approves least-privilege + PAB and blocks allUsers / direct DB roles",
        good_ok and len(good_violations) == 0 and (not bad_ok) and len(bad_violations) >= 3,
    )

    section("3. Cross-Project A2A Latency Math: Serial vs Parallel Fan-Out")
    # PCI Cloud Run A2A: (80ms mTLS/OIDC + 900ms LLM) = 980ms
    # HIPAA Agent Runtime A2A: (100ms OAuth/Gateway + 1150ms LLM) = 1250ms
    # Coordinator synthesis: 230ms (using DEFAULT_FAST_MODEL / DEFAULT_AGENT_MODEL)
    lat = compute_cross_project_a2a_latency(
        remote_calls_ms=[(80, 900), (100, 1150)],
        coordinator_synthesis_ms=230,
    )
    table(
        ["Cross-Project Orchestration Mode", "Total End-to-End Latency (ms)", "Meets 2,000ms SLA?"],
        [
            ["Serial A2A Handoffs (Sum of Net + Remote Turns)", lat["serial_a2a_ms"], lat["serial_a2a_ms"] <= 2000],
            ["ParallelAgent / JoinNode A2A Fan-Out (Max Branch)", lat["parallel_a2a_ms"], lat["parallel_a2a_ms"] <= 2000],
        ],
    )
    report.check(
        "Parallel RemoteA2aAgent fan-out cuts cross-project latency from 2460ms to 1480ms (<2s SLA)",
        lat["serial_a2a_ms"] == 2460
        and lat["parallel_a2a_ms"] == 1480
        and DEFAULT_FAST_MODEL != DEFAULT_AGENT_MODEL,
    )

    report.summary()
    return report


def run_live(config) -> None:
    banner("Lab 12 — Multi-Agent & Cross-Project A2A (Live)", f"Project: {config.project_id}")
    run_offline()
    section("Least-Privilege Cross-Project CLI Reference")
    step(
        1,
        "gcloud run services add-iam-policy-binding pci-billing-agent "
        "--project=proj-pci-billing --region=us-central1 "
        "--member='serviceAccount:sa-support-coord@proj-support-orchestrator.iam.gserviceaccount.com' "
        "--role='roles/run.invoker'",
    )


if __name__ == "__main__":
    cfg = load_config(sys.argv[1:])
    if require_live(cfg):
        run_live(cfg)
    else:
        result = run_offline()
        sys.exit(0 if result.passed else 1)
