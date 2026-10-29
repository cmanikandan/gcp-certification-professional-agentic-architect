from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import sys
from pathlib import Path

from google.adk import Agent
from google.adk.integrations.agent_registry import AgentRegistry
from google.adk.models import Claude
from google.adk.tools import McpToolset, RemoteMcpServer
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseConnectionParams,
    StdioConnectionParams,
)
from mcp.client.stdio import StdioServerParameters

from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG

LAB_DIR = Path(__file__).resolve().parent.parent


def _load_lab_module():
    spec = importlib.util.spec_from_file_location("lab_04_module", LAB_DIR / "lab.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lab_04_module"] = mod
    spec.loader.exec_module(mod)
    return mod


lab = _load_lab_module()


def test_mcp_config_parses_stdio_and_remote_sse() -> None:
    """Verify Antigravity / Claude Code mcp_config.json schema validation."""
    cfg = {
        "mcpServers": {
            "sqlite-local": {
                "command": "python3",
                "args": ["mcp_server.py"],
                "env": {"MCP_READONLY": "true"},
            },
            "cloudrun-remote": {
                "serverUrl": "https://mcp-gateway-uc.a.run.app/sse",
            },
        }
    }
    servers, errors = lab.parse_and_validate_mcp_config(cfg)
    assert errors == []
    assert len(servers) == 2
    assert servers[0].transport == "stdio"
    assert servers[0].env_keys == ("MCP_READONLY",)
    assert servers[1].transport == "sse"
    assert servers[1].uses_tls is True


def test_mcp_config_rejects_ambiguous_or_insecure_remote_urls() -> None:
    """Remote SSE endpoints must use HTTPS and cannot mix stdio + SSE keys."""
    bad_cfg = {
        "mcpServers": {
            "insecure": {"serverUrl": "http://mcp.internal.corp/sse"},
            "mixed": {
                "command": "node",
                "serverUrl": "https://mcp.internal.corp/sse",
            },
        }
    }
    servers, errors = lab.parse_and_validate_mcp_config(bad_cfg)
    assert servers == []
    assert len(errors) == 2
    assert any("HTTPS" in err for err in errors)
    assert any("not both" in err for err in errors)


def test_mcp_toolset_stdio_and_sse_conversion() -> None:
    """Verify ADK McpToolset and RemoteMcpServer encapsulate both transports."""
    cfg = {
        "mcpServers": {
            "local": {"command": sys.executable, "args": ["mcp_server.py"]},
            "remote": {"serverUrl": "https://cloudrun-mcp.a.run.app/sse"},
        }
    }
    servers, _ = lab.parse_and_validate_mcp_config(cfg)
    stdio_ts = lab.build_adk_toolset_from_server(servers[0])
    sse_ts = lab.build_adk_toolset_from_server(
        servers[1], headers={"Authorization": "Bearer token"}
    )

    assert isinstance(stdio_ts, McpToolset)
    assert isinstance(stdio_ts.connection_params, StdioConnectionParams)
    assert isinstance(stdio_ts.connection_params.server_params, StdioServerParameters)
    assert isinstance(sse_ts.connection_params, SseConnectionParams)
    assert sse_ts.connection_params.url == "https://cloudrun-mcp.a.run.app/sse"

    remote = RemoteMcpServer(
        name="gcp_cloudrun_mcp",
        url="https://cloudrun-mcp.a.run.app/sse",
        allowed_tools=["list_services"],
    )
    agent = Agent(
        name="mcp_agent", model=DEFAULT_AGENT_MODEL, tools=[stdio_ts, sse_ts]
    )
    assert len(agent.tools) == 2
    assert remote.allowed_tools == ["list_services"]


def test_stdio_stdout_pollution_detector_and_live_local_roundtrip() -> None:
    """stdio MCP servers must never write logs to stdout; verify real round-trip."""
    server_source = (LAB_DIR / "mcp_server.py").read_text(encoding="utf-8")
    assert lab.detect_stdio_stdout_pollution(server_source) == []

    polluted = 'import sys\nprint("debug banner")\nprint("safe", file=sys.stderr)\n'
    assert lab.detect_stdio_stdout_pollution(polluted) == [2]

    tools, digest, _ = asyncio.run(lab.execute_local_mcp_roundtrip("AgenticArchitect"))
    assert "calculate_checksum" in tools
    assert "server_security_mode" in tools
    assert digest == hashlib.sha256(b"AgenticArchitect").hexdigest()


def test_claude_code_and_antigravity_gcp_iam_posture() -> None:
    """Verify Vertex AI ADC + roles/aiplatform.user + VPC-SC + Cloud Run IAM checks."""
    ok = lab.evaluate_coding_agent_gcp_posture(
        agent_client="claude_code",
        uses_vertex_ai_adc=True,
        granted_iam_roles={"roles/aiplatform.user"},
        inside_vpc_sc_perimeter=True,
        raw_external_api_key_present=False,
        remote_mcp_allow_unauthenticated=False,
        remote_mcp_caller_roles={
            "roles/run.invoker",
            "roles/iap.httpsResourceAccessor",
        },
        uses_iap_for_human_users=True,
    )
    assert ok.compliant is True
    assert "roles/aiplatform.user" in ok.required_iam_roles
    assert "roles/run.invoker" in ok.required_iam_roles

    bad = lab.evaluate_coding_agent_gcp_posture(
        agent_client="claude_code",
        uses_vertex_ai_adc=False,
        granted_iam_roles={"roles/owner"},
        inside_vpc_sc_perimeter=False,
        raw_external_api_key_present=True,
        remote_mcp_allow_unauthenticated=True,
        remote_mcp_caller_roles=set(),
        uses_iap_for_human_users=True,
    )
    assert bad.compliant is False
    assert any("VPC Service Controls" in v for v in bad.violations)
    assert any("roles/aiplatform.user" in v for v in bad.violations)
    assert any("roles/run.invoker" in v for v in bad.violations)


def test_agent_registry_and_verified_models() -> None:
    """Contract test: AgentRegistry exposes MCP governance and models are verified."""
    from unittest.mock import patch as mock_patch
    from google.auth.credentials import AnonymousCredentials

    with mock_patch(
        "google.auth.default", return_value=(AnonymousCredentials(), "test-proj")
    ):
        registry = AgentRegistry(project_id="test-proj", location="us-central1")
    assert hasattr(registry, "list_mcp_servers")
    assert hasattr(registry, "get_mcp_toolset")
    assert isinstance(Claude(), Claude)
    assert DEFAULT_AGENT_MODEL in MODEL_CATALOG
