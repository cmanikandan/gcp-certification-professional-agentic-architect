"""Offline deterministic tests for Lab 03 (Enterprise Data Connectors & Multimodal)."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys

import pytest

LAB_PATH = Path(__file__).resolve().parent.parent / "lab.py"
_SPEC = importlib.util.spec_from_file_location("track01_lab03", LAB_PATH)
assert _SPEC and _SPEC.loader
lab = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = lab
_SPEC.loader.exec_module(lab)


def test_acl_sync_pre_llm_filtering() -> None:
    """Verify Workforce Identity group and user ACL filtering before LLM context."""
    datastore = lab.MockDatastore()

    clinician_docs = datastore.search(
        "lab", "dr.alice@hospital.org", ["clinicians"]
    )
    assert {d["id"] for d in clinician_docs} == {"doc-public-01", "doc-clin-02"}

    contractor_docs = datastore.search(
        "layoff", "contractor.lee@ext.org", []
    )
    assert [d["id"] for d in contractor_docs] == ["doc-public-01"]


def test_3lo_action_connector_auth_and_secret_manager_guard() -> None:
    """Verify RetrieveCredentialsRequest consent handshake and Secret Manager check."""
    with pytest.raises(ValueError, match="Secret Manager"):
        lab.GeActionConnectorAuthBroker(secret_manager_ref="hardcoded-client-secret")

    broker = lab.GeActionConnectorAuthBroker(
        secret_manager_ref="projects/proj-cx-prod/secrets/oauth-client/versions/latest"
    )
    connector = "projects/proj-cx-prod/locations/global/connectors/jira-prod"

    scheme, _provider = broker.build_adk_auth_scheme(
        connector_name=connector,
        scopes=["jira:write"],
        continue_uri="https://geapp.example/cb",
    )
    assert scheme.name == connector
    assert scheme.scopes == ["jira:write"]

    pending = broker.retrieve_user_credentials(
        connector_name=connector,
        user_id="rep.sam@hospital.org",
        scopes=["jira:write"],
        continue_uri="https://geapp.example/cb",
    )
    assert pending.status == "CONSENT_REQUIRED"
    assert pending.metadata is not None
    assert "authorize" in pending.metadata.uri_consent_required.authorization_uri
    assert pending.metadata.uri_consent_required.consent_nonce == "nonce-3lo-hipaa-001"
    assert pending.request.user_id == "rep.sam@hospital.org"

    broker.grant_user_3lo_consent(connector, "rep.sam@hospital.org", ["jira:write"])
    ready = broker.retrieve_user_credentials(
        connector_name=connector,
        user_id="rep.sam@hospital.org",
        scopes=["jira:write"],
        continue_uri="https://geapp.example/cb",
    )
    assert ready.status == "TOKEN_READY"
    assert ready.response is not None
    assert ready.response.header == "Authorization"
    assert list(ready.response.scopes) == ["jira:write"]


def test_cross_project_least_privilege_iam_rejects_broad_roles() -> None:
    """Over-privileged roles like discoveryengine.admin or editor must fail validation."""
    principal = "principal://agents.global.org-1.system.id.goog/resources/agents/cx"
    bad_bindings = [
        {
            "principal": principal,
            "project": "proj-enterprise-search",
            "resource": "agent_search_datastore",
            "role": "roles/discoveryengine.admin",
        },
        {
            "principal": principal,
            "project": "proj-media-lake",
            "resource": "bucket:gs://proj-media-lake-intake",
            "role": "roles/editor",
        },
    ]
    valid, errors = lab.validate_cross_project_iam(bad_bindings)
    assert valid is False
    assert any("Over-privileged role 'roles/discoveryengine.admin'" in e for e in errors)
    assert any("Over-privileged role 'roles/editor'" in e for e in errors)


def test_multimodal_gcs_part_and_strategy_selection() -> None:
    """Verify gs:// Part construction and native vs preprocessing decision rules."""
    with pytest.raises(ValueError, match="gs://"):
        lab.build_multimodal_gcs_part("https://example.com/video.mp4", "video/mp4")

    part = lab.build_multimodal_gcs_part(
        "gs://proj-media-lake-intake/claims/photo1.png",
        "image/png",
    )
    assert part.file_data is not None
    assert part.file_data.mime_type == "image/png"

    native = lab.select_multimodal_ingestion_strategy(
        hours_of_media=0.02,
        requires_cross_modal_visual_audio_reasoning=True,
    )
    assert native["pattern"] == "NATIVE_MULTIMODAL_GCS_URI"

    hipaa_pipeline = lab.select_multimodal_ingestion_strategy(
        hours_of_media=500.0,
        requires_cross_modal_visual_audio_reasoning=True,
        requires_pre_llm_hipaa_phi_scrubbing=True,
    )
    assert hipaa_pipeline["pattern"] == "PREPROCESSING_PIPELINE_WITH_SDP"


def test_offline_run_passes_all_checks(capsys) -> None:
    """Offline execution must complete cleanly with zero network calls."""
    report = asyncio.run(lab.run_offline())
    captured = capsys.readouterr()
    assert report.passed
    assert "All 6 checks passed." in captured.out
