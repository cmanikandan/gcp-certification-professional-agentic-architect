from unittest.mock import patch

import lab
from google.adk.a2a.agent import (
    A2aRemoteAgentConfig,
    CardRequestInterceptor,
    RequestInterceptor,
)
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.integrations.agent_registry import AgentRegistry
from google.adk.tools import MCPToolset, RemoteMcpServer
from google.auth.credentials import AnonymousCredentials


def test_mcp_toolset_structure():
    mcp_server = RemoteMcpServer(
        name="test_server",
        url="http://localhost:8080/mcp",
        allowed_tools=["read_order"],
    )
    assert mcp_server.name == "test_server"
    assert mcp_server.url == "http://localhost:8080/mcp"
    assert mcp_server.allowed_tools == ["read_order"]
    assert MCPToolset is not None


def test_a2a_and_registry_imports():
    config = A2aRemoteAgentConfig(
        request_interceptors=[RequestInterceptor()],
        card_request_interceptors=[CardRequestInterceptor()],
    )
    assert len(config.request_interceptors) == 1
    assert len(config.card_request_interceptors) == 1

    with patch("google.auth.default", return_value=(AnonymousCredentials(), "proj-gov")):
        registry = AgentRegistry(project_id="proj-gov", location="us-central1")
    assert callable(registry.get_remote_a2a_agent)
    assert callable(registry.get_mcp_toolset)


def test_cross_project_remote_a2a_topology_and_iam_audit():
    topo = lab.build_cross_project_support_topology()
    assert isinstance(topo["pci_agent"], RemoteA2aAgent)
    assert isinstance(topo["hipaa_agent"], RemoteA2aAgent)
    assert len(topo["parallel_fanout"].sub_agents) == 2

    ok, violations = lab.validate_cross_project_a2a_iam(
        [
            lab.CrossProjectBinding(
                principal="serviceAccount:sa-coord@proj-orch.iam.gserviceaccount.com",
                target_project="proj-pci-billing",
                resource_scope="resource",
                role="roles/run.invoker",
            )
        ],
        has_pab_policy=True,
    )
    assert ok is True
    assert violations == []

    bad_ok, bad_violations = lab.validate_cross_project_a2a_iam(
        [
            lab.CrossProjectBinding(
                principal="allUsers",
                target_project="proj-pci-billing",
                resource_scope="project",
                role="roles/run.invoker",
            ),
            lab.CrossProjectBinding(
                principal="serviceAccount:sa-coord@proj-orch.iam.gserviceaccount.com",
                target_project="proj-pci-billing",
                resource_scope="project",
                role="roles/editor",
            ),
        ],
        has_pab_policy=False,
    )
    assert bad_ok is False
    assert len(bad_violations) >= 3


def test_parallel_vs_serial_cross_project_a2a_latency():
    lat = lab.compute_cross_project_a2a_latency(
        remote_calls_ms=[(80, 900), (100, 1150)],
        coordinator_synthesis_ms=230,
    )
    assert lat["serial_a2a_ms"] == 2460
    assert lat["parallel_a2a_ms"] == 1480
    assert lat["parallel_a2a_ms"] < lat["serial_a2a_ms"]


def test_offline_report_passes():
    report = lab.run_offline()
    assert report.passed
