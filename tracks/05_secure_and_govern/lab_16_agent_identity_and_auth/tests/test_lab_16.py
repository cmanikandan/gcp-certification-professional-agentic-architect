"""Tests for Lab 16 — IAM Least-Privilege, Agent Identity, Connector Auth & PAB."""

from __future__ import annotations

import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from common.models import MODEL_CATALOG

lab = importlib.import_module("tracks.05_secure_and_govern.lab_16_agent_identity_and_auth.lab")


def test_uses_only_verified_models() -> None:
    assert lab.MODEL in MODEL_CATALOG


def test_has_agent_identity() -> None:
    assert lab.HAS_AGENT_IDENTITY, "The google-adk[agent-identity] extra must be installed"


def test_gcp_auth_provider_scheme_and_connector_credentials_instantiation() -> None:
    if not lab.HAS_AGENT_IDENTITY:
        pytest.skip("Agent Identity not installed")

    from google.adk.integrations.agent_identity import GcpAuthProviderScheme

    scheme = GcpAuthProviderScheme(
        name="projects/test/locations/us-central1/connectors/test",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    assert scheme.type_ == "gcpAuthProviderScheme"
    assert scheme.name == "projects/test/locations/us-central1/connectors/test"
    assert "https://www.googleapis.com/auth/cloud-platform" in scheme.scopes

    objs = lab.build_agent_identity_and_connector_requests()
    assert objs["aic_retrieve_req"].user_id == "clinician-dr-patel@hospital.example"
    assert "servicenow-hipaa-connector" in objs["connector_retrieve_req"].connector
    assert objs["oauth2_user_flow"].code_challenge_method == "S256"


def test_auth_mechanism_selection_3lo_vs_workload_identity() -> None:
    conn_choice, _ = lab.select_auth_mechanism(
        acts_on_behalf_of_human_user=True,
        uses_gemini_enterprise_managed_connector=True,
    )
    assert conn_choice == "iam_connector_credentials_3lo"

    user_oauth_choice, _ = lab.select_auth_mechanism(
        acts_on_behalf_of_human_user=True,
        uses_gemini_enterprise_managed_connector=False,
    )
    assert user_oauth_choice == "adk_agent_identity_oauth2_3lo"

    m2m_choice, _ = lab.select_auth_mechanism(
        calls_internal_cloud_run_mcp_service=True,
    )
    assert m2m_choice == "workload_agent_identity_oidc"


def test_credential_provisioning_rejects_static_keys_and_env_secrets() -> None:
    ok_clean, issues_clean = lab.audit_credential_provisioning()
    assert ok_clean is True
    assert issues_clean == []

    ok_bad, issues_bad = lab.audit_credential_provisioning(
        uses_static_sa_json_key=True,
        stores_api_key_in_plaintext_env=True,
        uses_default_compute_sa=True,
    )
    assert ok_bad is False
    assert len(issues_bad) == 3


def test_cross_project_least_privilege_iam_auditor() -> None:
    good = lab.build_compliant_cross_project_bindings()
    ok, issues = lab.audit_cross_project_iam_bindings(
        good, agent_host_project="proj-agent-host"
    )
    assert ok is True, f"Expected compliant blueprint to pass, got: {issues}"

    bad = [
        lab.IamBindingSpec("proj-agent-host", "project", "proj-agent-host", "roles/owner"),
        lab.IamBindingSpec("proj-data", "project", "proj-data", "roles/bigquery.dataViewer"),
        lab.IamBindingSpec("proj-data", "project", "proj-data", "roles/bigquery.jobUser"),
        lab.IamBindingSpec("proj-mcp", "project", "proj-mcp", "roles/run.invoker"),
        lab.IamBindingSpec("proj-agent-host", "project", "proj-agent-host", "roles/secretmanager.secretAccessor"),
    ]
    bad_ok, bad_issues = lab.audit_cross_project_iam_bindings(
        bad, agent_host_project="proj-agent-host"
    )
    assert bad_ok is False
    assert any("OVERPRIVILEGED_ROLE" in i for i in bad_issues)
    assert any("BROAD_BQ_DATA_VIEWER" in i for i in bad_issues)
    assert any("CROSS_PROJECT_BQ_JOB_USER" in i for i in bad_issues)
    assert any("BROAD_RUN_INVOKER" in i for i in bad_issues)
    assert any("BROAD_SECRET_ACCESSOR" in i for i in bad_issues)


def test_pab_effective_access_intersection() -> None:
    iam_allow = {"proj-a", "proj-b", "proj-secret-vault"}
    pab_eligible = {"proj-a", "proj-b"}
    effective = lab.evaluate_pab_effective_access(iam_allow, pab_eligible)
    assert effective == {"proj-a", "proj-b"}
    assert "proj-secret-vault" not in effective
