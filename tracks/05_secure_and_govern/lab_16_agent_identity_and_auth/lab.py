#!/usr/bin/env python3
"""Lab 16 — IAM Least-Privilege, Agent Identity, Connector Auth & PAB Master Lab.

Demonstrates the 4 IAM & Identity pillars heavily tested (~30-35% cross-cutting):
1. Safe Credential Provisioning via Agent Identity:
   - ``GcpAuthProvider``, ``GcpAuthProviderScheme``, and
     ``google.cloud.agentidentitycredentials_v1`` (``AuthProviderCredentialsServiceClient``,
     ``RetrieveCredentialsRequest``) — eliminating static SA JSON keys & plaintext env vars.
2. Auth Manager OAuth 2.0 & Gemini Enterprise Connector Auth:
   - ``OAuth2Auth``, ``AuthConfig``, and ``google.cloud.iamconnectorcredentials_v1alpha``
     (``IAMConnectorCredentialsServiceClient``, ``RetrieveCredentialsRequest``) for
     3-legged OAuth (3LO) user-delegated consent vs. Service Account workload identity.
3. Cross-Project Least-Privilege IAM Auditor:
   - Exact predefined roles across Host, RAG, Data Warehouse, and Tool projects
     (``roles/aiplatform.user``, ``roles/discoveryengine.viewer``, ``roles/modelarmor.user``,
     ``roles/run.invoker``, host-project ``roles/bigquery.jobUser`` + dataset-level
     ``roles/bigquery.dataViewer``, secret-level ``roles/secretmanager.secretAccessor``)
     while rejecting ``roles/owner``, ``roles/editor``, ``roles/bigquery.admin``, and
     ``roles/storage.admin``.
4. Principal Access Boundary (PAB) Blast-Radius Containment:
   - ``Effective Access = IAM Allow ∩ PAB Eligible Resources``.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Literal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from google.adk.auth import AuthConfig, OAuth2Auth
from google.cloud import agentidentitycredentials_v1, iamconnectorcredentials_v1alpha

from common import (
    DEFAULT_AGENT_MODEL,
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
from common.models import MODEL_CATALOG

try:
    from google.adk.integrations.agent_identity import (
        GcpAuthProvider,
        GcpAuthProviderScheme,
    )

    HAS_AGENT_IDENTITY = True
except ImportError:
    HAS_AGENT_IDENTITY = False

MODEL = DEFAULT_AGENT_MODEL

FORBIDDEN_IAM_ROLES: frozenset[str] = frozenset(
    {
        "roles/owner",
        "roles/editor",
        "roles/viewer",
        "roles/bigquery.admin",
        "roles/storage.admin",
        "roles/aiplatform.admin",
        "roles/secretmanager.admin",
        "roles/run.admin",
    }
)

APPROVED_LEAST_PRIVILEGE_ROLES: dict[str, str] = {
    "roles/aiplatform.user": "Invoke Vertex AI Gemini models, Reasoning Engine, and Memory Bank",
    "roles/discoveryengine.viewer": "Query Agent Search / Discovery Engine data stores read-only",
    "roles/modelarmor.user": "Call Model Armor SanitizeUserPrompt / SanitizeModelResponse templates",
    "roles/run.invoker": "Invoke private Cloud Run MCP tool servers or A2A peers",
    "roles/bigquery.jobUser": "Submit BigQuery query jobs billed to the agent's host project",
    "roles/bigquery.dataViewer": "Read rows from a specific authorized BigQuery dataset/table ONLY",
    "roles/secretmanager.secretAccessor": "Read a specific third-party secret payload at runtime",
}


@dataclass(frozen=True)
class IamBindingSpec:
    """Represents a single IAM role grant on a specific GCP resource scope."""

    project_id: str
    resource_scope: Literal["project", "dataset", "secret", "cloud_run_service"]
    resource_name: str
    role: str


def build_agent_identity_and_connector_requests(
    project_id: str = "argolis-agent-host",
    location: str = "us-central1",
) -> dict[str, object]:
    """Instantiate real Agent Identity, Auth Manager OAuth2, and Connector Auth objects."""
    if not HAS_AGENT_IDENTITY:
        raise RuntimeError("google-adk[agent-identity] extra is required")

    scheme = GcpAuthProviderScheme(
        name=f"projects/{project_id}/locations/{location}/authProviders/salesforce-crm-oauth",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
        continue_uri="https://agent-gateway.example.com/oauth2callback",
    )
    auth_provider = GcpAuthProvider()
    tool_auth_config = AuthConfig(auth_scheme=scheme)

    oauth2_user_flow = OAuth2Auth(
        client_id="enterprise-support-oauth-client",
        auth_uri="https://accounts.google.com/o/oauth2/v2/auth",
        redirect_uri="https://agent-gateway.example.com/oauth2callback",
        code_challenge_method="S256",
    )

    aic_retrieve_req = agentidentitycredentials_v1.RetrieveCredentialsRequest(
        auth_provider=scheme.name,
        user_id="clinician-dr-patel@hospital.example",
        scopes=list(scheme.scopes or []),
        continue_uri=scheme.continue_uri or "",
    )

    connector_retrieve_req = iamconnectorcredentials_v1alpha.RetrieveCredentialsRequest(
        connector=f"projects/{project_id}/locations/{location}/connectors/servicenow-hipaa-connector",
        user_id="clinician-dr-patel@hospital.example",
        scopes=["useraccount", "incident.read"],
        continue_uri="https://gemini-enterprise.example.com/connector/callback",
    )

    return {
        "scheme": scheme,
        "auth_provider": auth_provider,
        "tool_auth_config": tool_auth_config,
        "oauth2_user_flow": oauth2_user_flow,
        "aic_client_cls": agentidentitycredentials_v1.AuthProviderCredentialsServiceClient,
        "aic_retrieve_req": aic_retrieve_req,
        "connector_client_cls": iamconnectorcredentials_v1alpha.IAMConnectorCredentialsServiceClient,
        "connector_retrieve_req": connector_retrieve_req,
    }


def select_auth_mechanism(
    *,
    acts_on_behalf_of_human_user: bool = False,
    uses_gemini_enterprise_managed_connector: bool = False,
    calls_internal_cloud_run_mcp_service: bool = False,
) -> tuple[
    Literal[
        "iam_connector_credentials_3lo",
        "adk_agent_identity_oauth2_3lo",
        "workload_agent_identity_oidc",
    ],
    str,
]:
    """Choose the right authentication flow between 3LO user consent and workload identity."""
    if acts_on_behalf_of_human_user and uses_gemini_enterprise_managed_connector:
        return (
            "iam_connector_credentials_3lo",
            "Use Gemini Enterprise Connector Auth (`IAMConnectorCredentialsServiceClient` / "
            "`RetrieveCredentialsRequest`) to run 3LO user consent (`continue_uri`) and cache "
            "per-user scoped OAuth tokens so downstream SaaS tools enforce the caller's ACLs.",
        )
    if acts_on_behalf_of_human_user:
        return (
            "adk_agent_identity_oauth2_3lo",
            "Use ADK `GcpAuthProviderScheme` / `OAuth2Auth` (`AuthProviderCredentialsServiceClient`) "
            "for 3-legged OAuth 2.0 user delegation — never a shared Service Account that would "
            "bypass per-user document/record permissions.",
        )
    if calls_internal_cloud_run_mcp_service:
        return (
            "workload_agent_identity_oidc",
            "Use short-lived Workload / Agent Identity OIDC ID tokens paired with service-level "
            "`roles/run.invoker` on the target Cloud Run MCP server (zero static keys).",
        )
    return (
        "workload_agent_identity_oidc",
        "Use short-lived Agent Identity / Workload Identity tokens with resource-scoped IAM.",
    )


def audit_credential_provisioning(
    *,
    uses_static_sa_json_key: bool = False,
    stores_api_key_in_plaintext_env: bool = False,
    uses_default_compute_sa: bool = False,
) -> tuple[bool, list[str]]:
    """Flag credential provisioning anti-patterns tested heavily on the exam."""
    violations: list[str] = []
    if uses_static_sa_json_key:
        violations.append(
            "STATIC_SA_KEY_FORBIDDEN: Exported Service Account JSON keys do not auto-rotate "
            "and risk exfiltration; use Agent Identity / Workload Identity Federation."
        )
    if stores_api_key_in_plaintext_env:
        violations.append(
            "PLAINTEXT_ENV_SECRET_FORBIDDEN: Never bake API keys into container env vars or "
            "source control; fetch via `GcpAuthProvider` or Secret Manager (`roles/secretmanager.secretAccessor`)."
        )
    if uses_default_compute_sa:
        violations.append(
            "DEFAULT_COMPUTE_SA_FORBIDDEN: Provision a dedicated per-agent identity instead "
            "of sharing `<project-number>-compute@developer.gserviceaccount.com`."
        )
    return (len(violations) == 0), violations


def audit_cross_project_iam_bindings(
    bindings: list[IamBindingSpec],
    *,
    agent_host_project: str,
) -> tuple[bool, list[str]]:
    """Deterministically validate cross-project least-privilege IAM bindings."""
    violations: list[str] = []
    has_host_bq_job_user = False

    for b in bindings:
        if b.role in FORBIDDEN_IAM_ROLES:
            violations.append(
                f"OVERPRIVILEGED_ROLE ({b.role} on {b.project_id}/{b.resource_name}): "
                "Replace basic/admin roles with least-privilege predefined roles."
            )
            continue

        if b.role not in APPROVED_LEAST_PRIVILEGE_ROLES:
            violations.append(f"UNRECOGNIZED_ROLE ({b.role}): Not in least-privilege catalog.")
            continue

        if b.role == "roles/bigquery.dataViewer" and b.resource_scope == "project":
            violations.append(
                f"BROAD_BQ_DATA_VIEWER ({b.project_id}): Grant `roles/bigquery.dataViewer` "
                "at the specific DATASET/TABLE level, never across the entire data project."
            )

        if b.role == "roles/bigquery.jobUser":
            if b.project_id == agent_host_project:
                has_host_bq_job_user = True
            else:
                violations.append(
                    f"CROSS_PROJECT_BQ_JOB_USER ({b.project_id}): Grant `roles/bigquery.jobUser` "
                    f"on the agent's host project (`{agent_host_project}`), not the remote data project."
                )

        if b.role == "roles/secretmanager.secretAccessor" and b.resource_scope == "project":
            violations.append(
                f"BROAD_SECRET_ACCESSOR ({b.project_id}): Scope `roles/secretmanager.secretAccessor` "
                "to the individual secret resource, not the entire project."
            )

        if b.role == "roles/run.invoker" and b.resource_scope == "project":
            violations.append(
                f"BROAD_RUN_INVOKER ({b.project_id}): Scope `roles/run.invoker` to the specific "
                "approved Cloud Run MCP service, not all services in the project."
            )

    uses_remote_bq = any(b.role == "roles/bigquery.dataViewer" for b in bindings)
    if uses_remote_bq and not has_host_bq_job_user:
        violations.append(
            f"MISSING_HOST_BQ_JOB_USER: Cross-project BigQuery queries require "
            f"`roles/bigquery.jobUser` on `{agent_host_project}` paired with dataset-level "
            "`roles/bigquery.dataViewer` on the target data project."
        )

    return (len(violations) == 0), violations


def evaluate_pab_effective_access(
    iam_allowed_resources: set[str],
    pab_eligible_resources: set[str],
) -> set[str]:
    """Compute Effective Access = IAM Allow ∩ PAB Eligible Resources."""
    return iam_allowed_resources & pab_eligible_resources


def build_compliant_cross_project_bindings() -> list[IamBindingSpec]:
    """Return the canonical exam-compliant cross-project IAM binding blueprint."""
    return [
        IamBindingSpec("proj-agent-host", "project", "proj-agent-host", "roles/aiplatform.user"),
        IamBindingSpec("proj-agent-host", "project", "proj-agent-host", "roles/modelarmor.user"),
        IamBindingSpec("proj-agent-host", "project", "proj-agent-host", "roles/bigquery.jobUser"),
        IamBindingSpec("proj-agent-host", "secret", "secrets/erp-webhook-hmac", "roles/secretmanager.secretAccessor"),
        IamBindingSpec("proj-enterprise-rag", "project", "proj-enterprise-rag", "roles/discoveryengine.viewer"),
        IamBindingSpec("proj-hipaa-warehouse", "dataset", "datasets/claims_deidentified", "roles/bigquery.dataViewer"),
        IamBindingSpec("proj-mcp-tools", "cloud_run_service", "services/pharmacy-order-mcp", "roles/run.invoker"),
    ]


def run_offline() -> LabReport:
    """Deterministic, credential-free execution of the IAM & Identity Master Lab."""
    report = LabReport(
        title="Lab 16 — IAM Least-Privilege, Agent Identity, Connector Auth & PAB"
    )
    banner(
        "Lab 16 — Agent Identity, Connector Auth, Cross-Project IAM & PAB (Offline)",
        "Addressing the ~30-35% Cross-Cutting IAM & Security Exam Weight",
    )

    if not HAS_AGENT_IDENTITY:
        raise RuntimeError("Missing google-adk[agent-identity] extra.")

    section("1. Agent Identity & Gemini Enterprise Connector 3LO Auth")
    objs = build_agent_identity_and_connector_requests()
    scheme: GcpAuthProviderScheme = objs["scheme"]  # type: ignore[assignment]
    aic_req = objs["aic_retrieve_req"]
    conn_req = objs["connector_retrieve_req"]

    kv_table(
        {
            "ADK Scheme Class & type_": f"{type(scheme).__name__} ({scheme.type_})",
            "Agent Identity Client": objs["aic_client_cls"].__name__,  # type: ignore[attr-defined]
            "AIC RetrieveCredentialsRequest": aic_req.auth_provider,  # type: ignore[attr-defined]
            "Connector Auth Client": objs["connector_client_cls"].__name__,  # type: ignore[attr-defined]
            "Connector 3LO Target": conn_req.connector,  # type: ignore[attr-defined]
            "PKCE Challenge Method": objs["oauth2_user_flow"].code_challenge_method,  # type: ignore[attr-defined]
        }
    )
    cred_ok, _ = audit_credential_provisioning()
    cred_bad, cred_issues = audit_credential_provisioning(
        uses_static_sa_json_key=True,
        stores_api_key_in_plaintext_env=True,
    )
    report.check(
        "Agent Identity & Connector Auth instantiate cleanly and block static SA keys",
        scheme.type_ == "gcpAuthProviderScheme"
        and cred_ok is True
        and cred_bad is False
        and len(cred_issues) == 2,
    )

    section("2. Cross-Project Least-Privilege IAM Auditor")
    good_bindings = build_compliant_cross_project_bindings()
    good_iam_ok, good_iam_issues = audit_cross_project_iam_bindings(
        good_bindings, agent_host_project="proj-agent-host"
    )

    bad_bindings = [
        IamBindingSpec("proj-agent-host", "project", "proj-agent-host", "roles/editor"),
        IamBindingSpec("proj-hipaa-warehouse", "project", "proj-hipaa-warehouse", "roles/bigquery.admin"),
        IamBindingSpec("proj-hipaa-warehouse", "project", "proj-hipaa-warehouse", "roles/bigquery.dataViewer"),
        IamBindingSpec("proj-agent-host", "project", "proj-agent-host", "roles/secretmanager.secretAccessor"),
    ]
    bad_iam_ok, bad_iam_issues = audit_cross_project_iam_bindings(
        bad_bindings, agent_host_project="proj-agent-host"
    )

    table(
        ["Project", "Scope", "Resource", "Least-Privilege Role"],
        [[b.project_id, b.resource_scope, b.resource_name, b.role] for b in good_bindings],
    )
    step(1, f"Compliant cross-project blueprint passed={good_iam_ok} (issues={len(good_iam_issues)})")
    step(2, f"Over-privileged anti-pattern rejected={not bad_iam_ok} ({len(bad_iam_issues)} violations caught)")
    report.check(
        "Cross-project IAM auditor enforces dataset/service/secret scoping & rejects admin/editor roles",
        good_iam_ok is True and bad_iam_ok is False and len(bad_iam_issues) >= 4,
    )

    section("3. Principal Access Boundary (PAB) Ceiling (IAM Allow ∩ PAB)")
    iam_granted = {
        "//cloudresourcemanager.googleapis.com/projects/proj-agent-host",
        "//cloudresourcemanager.googleapis.com/projects/proj-hipaa-warehouse",
        "//cloudresourcemanager.googleapis.com/projects/proj-prod-payroll-restricted",
    }
    pab_eligible = {
        "//cloudresourcemanager.googleapis.com/projects/proj-agent-host",
        "//cloudresourcemanager.googleapis.com/projects/proj-hipaa-warehouse",
    }
    effective = evaluate_pab_effective_access(iam_granted, pab_eligible)
    step(
        3,
        f"PAB blocked accidental payroll grant -> effective projects count={len(effective)} (expected 2)",
    )
    report.check(
        "PAB restricts effective access to intersection (IAM Allow ∩ PAB)",
        "//cloudresourcemanager.googleapis.com/projects/proj-prod-payroll-restricted" not in effective
        and len(effective) == 2
        and MODEL in MODEL_CATALOG,
    )

    exam_note(
        "Cross-Project BigQuery Rule: Grant `roles/bigquery.jobUser` on the AGENT'S HOST project "
        "(where query compute runs) and dataset-scoped `roles/bigquery.dataViewer` on the specific "
        "dataset in the DATA project. Pair with a Principal Access Boundary (PAB) to cap maximum "
        "eligible projects, and use 3LO Connector Auth / `OAuth2Auth` whenever acting as a human user."
    )
    report.summary()
    return report


def run_live(config) -> LabReport:
    """Live mode note: PAB creation requires Organization-level IAM permissions."""
    banner("Lab 16 — Agent Identity, Connector Auth & PAB (Live Mode)")
    step(1, f"Project: {config.project_id} | Location: {config.location}")
    step(2, "Running deterministic IAM & PAB verification without mutating org policies.")
    return run_offline()


if __name__ == "__main__":
    cfg = load_config()
    if "--live" in sys.argv and require_live(cfg):
        run_live(cfg)
    else:
        run_offline()
