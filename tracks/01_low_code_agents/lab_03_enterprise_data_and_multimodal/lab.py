#!/usr/bin/env python3
"""Lab 03: Enterprise Data Connectors, Agent Identity & Multimodal Ingestion."""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from unittest.mock import patch

from google.adk.integrations.agent_identity import (
    GcpAuthProvider,
    GcpAuthProviderScheme,
)
from google.adk.tools import DiscoveryEngineSearchTool, VertexAiSearchTool
from google.cloud import iamconnectorcredentials_v1alpha
from google.genai import types

from common import load_config, require_live
from common.labkit import (
    LabReport,
    banner,
    detail,
    exam_note,
    section,
    step,
    table,
)
from common.models import DEFAULT_AGENT_MODEL, get_profile

# ---------------------------------------------------------------------------
# 1. Mode 1 Connector: ACL-Sync Indexing + Workforce Identity Propagation
# ---------------------------------------------------------------------------


class MockDatastore:
    """Simulates Agent Search enforcing synced Document-Level ACLs BEFORE LLM generation."""

    def __init__(self) -> None:
        self.documents = [
            {
                "id": "doc-public-01",
                "title": "Outpatient Clinic Visiting Hours & Parking",
                "acl": ["*"],
                "source": "SharePoint",
            },
            {
                "id": "doc-clin-02",
                "title": "HIPAA Oncology Lab Escalation Protocol",
                "acl": ["group:clinicians", "dr.alice@hospital.org"],
                "source": "Confluence",
            },
            {
                "id": "doc-bill-03",
                "title": "Enterprise Billing Refund Ceiling ($250 SOP)",
                "acl": ["group:billing-support", "rep.sam@hospital.org"],
                "source": "GoogleDrive",
            },
            {
                "id": "doc-exec-04",
                "title": "Confidential M&A Hospital Acquisition Targets",
                "acl": ["group:executives"],
                "source": "SharePoint",
            },
        ]

    def search(
        self,
        query: str,
        user_email: str,
        workforce_groups: list[str],
    ) -> list[dict]:
        """Filter indexed chunks against federated user/group ACLs at retrieval time."""
        _ = query
        authorized: list[dict] = []
        principals = {"*", user_email, *[f"group:{g}" for g in workforce_groups]}
        for doc in self.documents:
            if principals.intersection(doc["acl"]):
                authorized.append(doc)
        return authorized


# ---------------------------------------------------------------------------
# 2. Mode 2 Connector: 3LO Per-User Action Connector via Auth Manager
#    (google.cloud.iamconnectorcredentials_v1alpha + GcpAuthProviderScheme)
# ---------------------------------------------------------------------------


@dataclass
class ConnectorAuthResult:
    """Structured result from the offline 3LO connector broker."""

    request: iamconnectorcredentials_v1alpha.RetrieveCredentialsRequest
    status: str  # "CONSENT_REQUIRED" | "TOKEN_READY"
    response: iamconnectorcredentials_v1alpha.RetrieveCredentialsResponse | None = None
    metadata: iamconnectorcredentials_v1alpha.RetrieveCredentialsMetadata | None = None


class GeActionConnectorAuthBroker:
    """Simulates IAMConnectorCredentialsServiceClient 3-Legged OAuth (3LO) flow."""

    def __init__(self, secret_manager_ref: str) -> None:
        if not secret_manager_ref.startswith("projects/"):
            raise ValueError(
                "OAuth client secrets must be referenced from Secret Manager "
                "(projects/<proj>/secrets/<name>/versions/latest), never hardcoded."
            )
        self.secret_manager_ref = secret_manager_ref
        self._consented_users: dict[tuple[str, str], set[str]] = {}

    def build_adk_auth_scheme(
        self,
        connector_name: str,
        scopes: list[str],
        continue_uri: str,
    ) -> tuple[GcpAuthProviderScheme, GcpAuthProvider]:
        """Construct verified ADK agent-identity scheme and provider objects."""
        scheme = GcpAuthProviderScheme(
            name=connector_name,
            scopes=scopes,
            continueUri=continue_uri,
        )
        provider = GcpAuthProvider()
        return scheme, provider

    def grant_user_3lo_consent(
        self,
        connector_name: str,
        user_id: str,
        scopes: list[str],
    ) -> None:
        """Record interactive user approval on the 3LO consent screen."""
        self._consented_users[(connector_name, user_id)] = set(scopes)

    def retrieve_user_credentials(
        self,
        *,
        connector_name: str,
        user_id: str,
        scopes: list[str],
        continue_uri: str,
    ) -> ConnectorAuthResult:
        """Build real RetrieveCredentialsRequest and simulate LRO metadata vs token."""
        req = iamconnectorcredentials_v1alpha.RetrieveCredentialsRequest(
            connector=connector_name,
            user_id=user_id,
            scopes=scopes,
            continue_uri=continue_uri,
        )
        granted = self._consented_users.get((connector_name, user_id), set())
        if not set(scopes).issubset(granted):
            meta = iamconnectorcredentials_v1alpha.RetrieveCredentialsMetadata(
                uri_consent_required=(
                    iamconnectorcredentials_v1alpha.RetrieveCredentialsMetadata.UriConsentRequired(
                        authorization_uri=(
                            f"https://auth.cloud.google/authorize?connector={connector_name}"
                            f"&user={user_id}"
                        ),
                        consent_nonce="nonce-3lo-hipaa-001",
                    )
                )
            )
            return ConnectorAuthResult(
                request=req,
                status="CONSENT_REQUIRED",
                metadata=meta,
            )

        resp = iamconnectorcredentials_v1alpha.RetrieveCredentialsResponse(
            token=f"ya29.3lo-scoped-{user_id.split('@')[0]}",
            header="Authorization",
            scopes=scopes,
        )
        return ConnectorAuthResult(
            request=req,
            status="TOKEN_READY",
            response=resp,
        )


# ---------------------------------------------------------------------------
# 3. Cross-Project Least-Privilege IAM Validator
# ---------------------------------------------------------------------------

FORBIDDEN_BROAD_ROLES = {
    "roles/owner",
    "roles/editor",
    "roles/discoveryengine.admin",
    "roles/discoveryengine.editor",
    "roles/storage.admin",
    "roles/secretmanager.admin",
    "roles/aiplatform.admin",
}

REQUIRED_CROSS_PROJECT_BINDINGS: dict[tuple[str, str], str] = {
    ("proj-enterprise-search", "agent_search_datastore"): "roles/discoveryengine.viewer",
    ("proj-media-lake", "bucket:gs://proj-media-lake-intake"): "roles/storage.objectViewer",
    ("proj-cx-prod", "secret:jira-3lo-client-secret"): "roles/secretmanager.secretAccessor",
    ("proj-cx-prod", "vertex_ai_models"): "roles/aiplatform.user",
}


def validate_cross_project_iam(
    bindings: list[dict[str, str]],
) -> tuple[bool, list[str]]:
    """Verify cross-project Agent Identity bindings follow strict least privilege."""
    violations: list[str] = []
    seen_targets: dict[tuple[str, str], str] = {}

    for entry in bindings:
        project = entry["project"]
        resource = entry["resource"]
        role = entry["role"]
        principal = entry["principal"]

        if not principal.startswith("principal://") and not principal.endswith(
            ".gserviceaccount.com"
        ):
            violations.append(f"Invalid workload/agent principal format: {principal}")

        if role in FORBIDDEN_BROAD_ROLES:
            violations.append(
                f"Over-privileged role '{role}' on {project}/{resource} violates least privilege."
            )

        expected = REQUIRED_CROSS_PROJECT_BINDINGS.get((project, resource))
        if expected and role != expected:
            violations.append(
                f"Expected '{expected}' on {project}/{resource}, got '{role}'."
            )
        seen_targets[(project, resource)] = role

    for target, required_role in REQUIRED_CROSS_PROJECT_BINDINGS.items():
        if seen_targets.get(target) != required_role:
            violations.append(
                f"Missing required binding '{required_role}' on {target[0]}/{target[1]}."
            )

    return len(violations) == 0, violations


# ---------------------------------------------------------------------------
# 4. Multimodal Ingestion Helpers (gs:// Native URI vs Preprocessing Pipeline)
# ---------------------------------------------------------------------------


def build_multimodal_gcs_part(gcs_uri: str, mime_type: str) -> types.Part:
    """Create a verified google.genai Part pointing directly at a GCS URI."""
    if not gcs_uri.startswith("gs://"):
        raise ValueError("Multimodal Cloud Storage reference must use a gs:// URI.")
    return types.Part.from_uri(file_uri=gcs_uri, mime_type=mime_type)


def select_multimodal_ingestion_strategy(
    *,
    hours_of_media: float,
    requires_cross_modal_visual_audio_reasoning: bool,
    requires_pre_llm_hipaa_phi_scrubbing: bool = False,
    needs_keyword_index_in_agent_search: bool = False,
) -> dict[str, str]:
    """Choose between Native Multimodal gs:// prompting and a Preprocessing Pipeline."""
    if requires_pre_llm_hipaa_phi_scrubbing:
        return {
            "pattern": "PREPROCESSING_PIPELINE_WITH_SDP",
            "services": "Speech-to-Text / Document AI -> Sensitive Data Protection -> Gemini",
            "rationale": (
                "Raw PHI must be transcribed/parsed and scrubbed via Sensitive Data Protection "
                "before entering the LLM context window."
            ),
        }
    if hours_of_media >= 100.0 or needs_keyword_index_in_agent_search:
        return {
            "pattern": "PREPROCESSING_PIPELINE",
            "services": "Speech-to-Text / Document AI -> BigQuery or Agent Search",
            "rationale": (
                "High-volume batch extraction or full-text search indexing is cheaper and "
                "faster with dedicated ASR/OCR pipelines than raw multimodal token streaming."
            ),
        }
    if requires_cross_modal_visual_audio_reasoning:
        return {
            "pattern": "NATIVE_MULTIMODAL_GCS_URI",
            "services": f"types.Part.from_uri(gs://...) -> {DEFAULT_AGENT_MODEL}",
            "rationale": (
                "Joint visual + audio temporal reasoning preserves screen state, alarm LEDs, "
                "and vocal tone in a single model pass."
            ),
        }
    return {
        "pattern": "PREPROCESSING_PIPELINE",
        "services": "Document AI / Speech-to-Text",
        "rationale": "Structured text extraction suffices when cross-modal cues are unneeded.",
    }


async def run_offline() -> LabReport:
    """Execute all four Objective 1.2 simulations deterministically offline."""
    banner(
        "Lab 03: Enterprise Data Connectors & Multimodal",
        "GEApp ACL-Sync vs 3LO Auth, Cross-Project IAM & Multimodal Ingestion",
    )

    section("1. Mode 1 Connector: Agent Search ACL-Sync + Workforce Identity")
    datastore = MockDatastore()
    alice_docs = datastore.search(
        "protocol",
        user_email="dr.alice@hospital.org",
        workforce_groups=["clinicians"],
    )
    sam_docs = datastore.search(
        "refund",
        user_email="rep.sam@hospital.org",
        workforce_groups=["billing-support"],
    )
    contractor_docs = datastore.search(
        "acquisition",
        user_email="contractor.lee@ext.org",
        workforce_groups=[],
    )
    step("1", f"Dr. Alice (clinicians) retrieved: {[d['id'] for d in alice_docs]}")
    step("2", f"Sam (billing-support) retrieved: {[d['id'] for d in sam_docs]}")
    step("3", f"Contractor (no groups) retrieved: {[d['id'] for d in contractor_docs]}")

    section("2. Mode 2 Connector: 3LO Per-User Auth (iamconnectorcredentials_v1alpha)")
    connector_path = (
        "projects/proj-cx-prod/locations/global/connectors/jira-enterprise-action"
    )
    broker = GeActionConnectorAuthBroker(
        secret_manager_ref=(
            "projects/proj-cx-prod/secrets/jira-3lo-client-secret/versions/latest"
        )
    )
    scheme, _provider = broker.build_adk_auth_scheme(
        connector_name=connector_path,
        scopes=["jira:ticket:create", "jira:ticket:read"],
        continue_uri="https://geapp.corp.example/auth/callback",
    )
    first_try = broker.retrieve_user_credentials(
        connector_name=connector_path,
        user_id="dr.alice@hospital.org",
        scopes=["jira:ticket:create"],
        continue_uri="https://geapp.corp.example/auth/callback",
    )
    step(
        "1",
        f"Unconsented call -> status={first_try.status}, "
        f"redirect={first_try.metadata.uri_consent_required.authorization_uri if first_try.metadata else ''}",
    )

    broker.grant_user_3lo_consent(
        connector_name=connector_path,
        user_id="dr.alice@hospital.org",
        scopes=["jira:ticket:create", "jira:ticket:read"],
    )
    second_try = broker.retrieve_user_credentials(
        connector_name=connector_path,
        user_id="dr.alice@hospital.org",
        scopes=["jira:ticket:create"],
        continue_uri="https://geapp.corp.example/auth/callback",
    )
    step(
        "2",
        f"Post-consent call -> status={second_try.status}, "
        f"header={second_try.response.header if second_try.response else ''}, "
        f"scopes={list(second_try.response.scopes) if second_try.response else []}",
    )

    section("3. ADK Search Tools & Cross-Project Least-Privilege IAM")
    cross_project_datastore = (
        "projects/proj-enterprise-search/locations/global/collections/"
        "default_collection/dataStores/hipaa-support-kb"
    )
    with patch("google.auth.default", return_value=(None, "proj-cx-prod")):
        de_tool = DiscoveryEngineSearchTool(data_store_id=cross_project_datastore)
        vais_tool = VertexAiSearchTool(data_store_id=cross_project_datastore)

    agent_principal = (
        "principal://agents.global.org-12345.system.id.goog/resources/agents/cx-support-agent"
    )
    least_priv_bindings = [
        {
            "principal": agent_principal,
            "project": "proj-enterprise-search",
            "resource": "agent_search_datastore",
            "role": "roles/discoveryengine.viewer",
        },
        {
            "principal": agent_principal,
            "project": "proj-media-lake",
            "resource": "bucket:gs://proj-media-lake-intake",
            "role": "roles/storage.objectViewer",
        },
        {
            "principal": agent_principal,
            "project": "proj-cx-prod",
            "resource": "secret:jira-3lo-client-secret",
            "role": "roles/secretmanager.secretAccessor",
        },
        {
            "principal": agent_principal,
            "project": "proj-cx-prod",
            "resource": "vertex_ai_models",
            "role": "roles/aiplatform.user",
        },
    ]
    iam_valid, iam_errors = validate_cross_project_iam(least_priv_bindings)
    table(
        ["Target Project", "Resource", "Least-Privilege Role"],
        [[b["project"], b["resource"], b["role"]] for b in least_priv_bindings],
    )

    section("4. Multimodal Unstructured Data Ingestion (gs:// vs Preprocessing)")
    video_part = build_multimodal_gcs_part(
        "gs://proj-media-lake-intake/device-clips/pump_alarm_20s.mp4",
        "video/mp4",
    )
    profile = get_profile(DEFAULT_AGENT_MODEL)
    clip_strategy = select_multimodal_ingestion_strategy(
        hours_of_media=0.01,
        requires_cross_modal_visual_audio_reasoning=True,
    )
    hipaa_batch_strategy = select_multimodal_ingestion_strategy(
        hours_of_media=10_000.0,
        requires_cross_modal_visual_audio_reasoning=False,
        requires_pre_llm_hipaa_phi_scrubbing=True,
    )
    detail(f"Verified model {DEFAULT_AGENT_MODEL} modalities: {profile.modalities}")
    detail(f"20s device video clip -> {clip_strategy['pattern']}")
    detail(f"10,000h HIPAA audio batch -> {hipaa_batch_strategy['pattern']}")
    exam_note(
        "Filter ACLs in Agent Search BEFORE LLM context; use 3LO Auth Manager for user write actions."
    )

    report = LabReport("Lab 03 — Enterprise Connectors, Identity & Multimodal")
    report.check(
        "ACL-Sync filters executive & clinical docs before LLM prompt assembly",
        len(contractor_docs) == 1
        and len(alice_docs) == 2
        and all(d["id"] != "doc-exec-04" for d in alice_docs),
    )
    report.check(
        "3LO RetrieveCredentialsRequest enforces consent before minting user token",
        first_try.status == "CONSENT_REQUIRED"
        and second_try.status == "TOKEN_READY"
        and scheme.name == connector_path,
    )
    report.check(
        "ADK DiscoveryEngineSearchTool & VertexAiSearchTool configured cross-project",
        type(de_tool).__name__ == "DiscoveryEngineSearchTool"
        and vais_tool.data_store_id == cross_project_datastore,
    )
    report.check(
        "Cross-project IAM audit passes least-privilege viewer/objectViewer/secretAccessor",
        iam_valid and not iam_errors,
    )
    report.check(
        "Multimodal gs:// Part built and verified against model catalog modalities",
        video_part.file_data is not None
        and video_part.file_data.file_uri.startswith("gs://proj-media-lake-intake/")
        and "video" in profile.modalities
        and "audio" in profile.modalities,
    )
    report.check(
        "Strategy selector routes cross-modal clips to gs:// URI and HIPAA batches to SDP pipeline",
        clip_strategy["pattern"] == "NATIVE_MULTIMODAL_GCS_URI"
        and hipaa_batch_strategy["pattern"] == "PREPROCESSING_PIPELINE_WITH_SDP",
    )
    report.summary()
    return report


async def run_live(config) -> None:
    """Opt-in live gate acknowledging project setup while keeping datastore runs free."""
    banner("Lab 03: Enterprise Data & Multimodal (LIVE)", f"Project: {config.project_id}")
    detail(
        "Enterprise Agent Search connector crawls and Workforce Identity Pools are "
        "organization-provisioned; executing full verification suite."
    )
    await run_offline()


def main() -> None:
    config = load_config(sys.argv[1:])
    if require_live(config):
        asyncio.run(run_live(config))
    else:
        asyncio.run(run_offline())


if __name__ == "__main__":
    main()
