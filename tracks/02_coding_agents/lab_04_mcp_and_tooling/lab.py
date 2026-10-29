"""Lab 04 — MCP, Claude Code on Google Cloud, and Enterprise Tooling.

Covers Section 2.1:
  - Configuring coding agents with Model Context Protocol (MCP) servers via
    ``mcp_config.json`` (local ``stdio`` vs remote HTTP ``SSE``) and ADK
    ``McpToolset`` / ``RemoteMcpServer``.
  - Authenticating Antigravity and Claude Code on Google Cloud via Vertex AI
    Application Default Credentials (ADC), least-privilege ``roles/aiplatform.user``,
    VPC Service Controls (VPC-SC), and zero-data-retention governance.
  - Securing centralized Cloud Run MCP servers with ``roles/run.invoker`` and IAP,
    discovering governed MCP servers via ``AgentRegistry``, and avoiding ``stdout``
    JSON-RPC stream corruption in ``stdio`` servers.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import os
import sys
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from google.adk import Agent
from google.adk.integrations.agent_registry import AgentRegistry
from google.adk.models import Claude
from google.adk.runners import InMemoryRunner
from google.adk.tools import McpToolset, RemoteMcpServer
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseConnectionParams,
    StdioConnectionParams,
)
from google.genai import types as genai_types
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from common import DEFAULT_AGENT_MODEL, LabConfig, load_config, require_live
from common.labkit import LabReport, banner, exam_note, section, table


@dataclass(frozen=True)
class ParsedMcpServer:
    """Normalized MCP server entry parsed from ``mcp_config.json``."""

    name: str
    transport: str  # "stdio" | "sse"
    target: str
    args: tuple[str, ...] = ()
    env_keys: tuple[str, ...] = ()
    uses_tls: bool = True


def parse_and_validate_mcp_config(
    raw_config: dict[str, Any],
) -> tuple[list[ParsedMcpServer], list[str]]:
    """Validate an Antigravity / Claude Code ``mcp_config.json`` document.

    Supported schemas in ``mcp_config.json``:
      1. Local Stdio: ``{"command": "...", "args": [...], "env": {...}}``
      2. Remote SSE:  ``{"serverUrl": "https://.../sse"}``

    Returns:
        ``(parsed_servers, errors)`` where ``errors`` lists schema or transport
        security violations (such as unencrypted remote HTTP).
    """
    errors: list[str] = []
    parsed: list[ParsedMcpServer] = []

    servers = raw_config.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        return [], ["Top-level 'mcpServers' object is required and must be non-empty."]

    for name, spec in servers.items():
        if not isinstance(spec, dict):
            errors.append(f"{name}: server spec must be a JSON object.")
            continue

        has_command = "command" in spec
        has_url = "serverUrl" in spec
        if has_command and has_url:
            errors.append(
                f"{name}: specify either 'command' (stdio) or 'serverUrl' (SSE), not both."
            )
            continue
        if not has_command and not has_url:
            errors.append(
                f"{name}: missing transport field ('command' for stdio or 'serverUrl' for SSE)."
            )
            continue

        if has_command:
            cmd = spec.get("command")
            args = spec.get("args", [])
            env = spec.get("env", {})
            if not isinstance(cmd, str) or not cmd.strip():
                errors.append(f"{name}: 'command' must be a non-empty string.")
                continue
            if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
                errors.append(f"{name}: 'args' must be a list of strings.")
                continue
            if not isinstance(env, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in env.items()
            ):
                errors.append(f"{name}: 'env' must map string keys to string values.")
                continue
            parsed.append(
                ParsedMcpServer(
                    name=name,
                    transport="stdio",
                    target=cmd,
                    args=tuple(args),
                    env_keys=tuple(sorted(env.keys())),
                    uses_tls=True,
                )
            )
        else:
            url = spec.get("serverUrl", "")
            if not isinstance(url, str) or not url.strip():
                errors.append(f"{name}: 'serverUrl' must be a non-empty URL string.")
                continue
            parsed_url = urlparse(url)
            is_localhost = parsed_url.hostname in {"localhost", "127.0.0.1"}
            uses_tls = parsed_url.scheme == "https" or (
                parsed_url.scheme == "http" and is_localhost
            )
            if not uses_tls:
                errors.append(
                    f"{name}: remote SSE endpoint '{url}' must use HTTPS (TLS) for Cloud Run / IAP."
                )
                continue
            parsed.append(
                ParsedMcpServer(
                    name=name,
                    transport="sse",
                    target=url,
                    uses_tls=uses_tls,
                )
            )

    return parsed, errors


def build_adk_toolset_from_server(
    server: ParsedMcpServer,
    env: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> McpToolset:
    """Convert a parsed ``mcp_config.json`` entry into an ADK ``McpToolset``."""
    if server.transport == "stdio":
        return McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=server.target,
                    args=list(server.args),
                    env=env,
                )
            )
        )
    if server.transport == "sse":
        return McpToolset(
            connection_params=SseConnectionParams(
                url=server.target,
                headers=headers or {},
            )
        )
    raise ValueError(f"Unsupported transport: {server.transport}")


def detect_stdio_stdout_pollution(python_source: str) -> list[int]:
    """Return 1-indexed line numbers where ``print(...)`` writes to ``stdout``.

    In an MCP ``stdio`` server, ``stdout`` is reserved exclusively for JSON-RPC
    messages. Bare ``print("debug")`` calls corrupt framing and break tool discovery.
    """
    tree = ast.parse(python_source)
    bad_lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            writes_to_stderr = False
            for kw in node.keywords:
                if kw.arg == "file":
                    if (
                        isinstance(kw.value, ast.Attribute)
                        and kw.value.attr == "stderr"
                    ) or (
                        isinstance(kw.value, ast.Name)
                        and kw.value.id == "stderr"
                    ):
                        writes_to_stderr = True
            if not writes_to_stderr:
                bad_lines.append(node.lineno)
    return sorted(bad_lines)


@dataclass(frozen=True)
class CodingAgentGcpPosture:
    """Enterprise security evaluation for Antigravity or Claude Code on GCP."""

    compliant: bool
    required_iam_roles: tuple[str, ...]
    violations: tuple[str, ...]


def evaluate_coding_agent_gcp_posture(
    *,
    agent_client: str,  # "claude_code" | "antigravity"
    uses_vertex_ai_adc: bool,
    granted_iam_roles: set[str],
    inside_vpc_sc_perimeter: bool,
    raw_external_api_key_present: bool,
    remote_mcp_allow_unauthenticated: bool = False,
    remote_mcp_caller_roles: set[str] | None = None,
    uses_iap_for_human_users: bool = True,
) -> CodingAgentGcpPosture:
    """Audit enterprise governance for Claude Code on GCP or Antigravity.

    Exam principles (Section 2.1 + IAM):
      1. Both Antigravity (Vertex Standard Mode) and Claude Code on Google Cloud
         authenticate via ADC to Vertex AI endpoints using ``roles/aiplatform.user``
         (never ``roles/aiplatform.admin`` or ``roles/owner``).
      2. Routing through Vertex AI keeps prompts/code inside VPC Service Controls
         (``aiplatform.googleapis.com``) with Cloud Audit Logs and zero data
         retention, whereas direct external vendor API keys bypass VPC-SC.
      3. Remote Cloud Run MCP servers must disable ``allUsers`` unauthenticated
         ingress and enforce ``roles/run.invoker`` (plus ``roles/iap.httpsResourceAccessor``
         when human developers authenticate through Identity-Aware Proxy).
    """
    violations: list[str] = []
    required_roles = ["roles/aiplatform.user"]

    if agent_client not in {"claude_code", "antigravity"}:
        violations.append(f"Unsupported coding agent client: {agent_client}")

    if raw_external_api_key_present or not uses_vertex_ai_adc:
        violations.append(
            "Must authenticate to Vertex AI via Application Default Credentials (ADC); "
            "external SaaS API keys bypass VPC Service Controls and Cloud Audit Logs."
        )

    if "roles/aiplatform.user" not in granted_iam_roles:
        violations.append(
            "Missing least-privilege IAM role 'roles/aiplatform.user' for Vertex AI model invocation."
        )

    overprivileged = granted_iam_roles & {
        "roles/owner",
        "roles/editor",
        "roles/aiplatform.admin",
    }
    if overprivileged:
        violations.append(
            f"Over-privileged IAM role(s) detected ({sorted(overprivileged)}); "
            "scope developer/agent identity down to 'roles/aiplatform.user'."
        )

    if not inside_vpc_sc_perimeter:
        violations.append(
            "Workload is outside a VPC Service Controls perimeter protecting 'aiplatform.googleapis.com'."
        )

    if remote_mcp_allow_unauthenticated:
        violations.append(
            "Remote Cloud Run MCP server allows unauthenticated ('allUsers') access; "
            "require IAM 'roles/run.invoker'."
        )

    if remote_mcp_caller_roles is not None:
        required_roles.append("roles/run.invoker")
        if "roles/run.invoker" not in remote_mcp_caller_roles:
            violations.append(
                "Caller lacks 'roles/run.invoker' on the remote Cloud Run MCP service."
            )
        if uses_iap_for_human_users:
            required_roles.append("roles/iap.httpsResourceAccessor")
            if "roles/iap.httpsResourceAccessor" not in remote_mcp_caller_roles:
                violations.append(
                    "Human OAuth flow via IAP requires 'roles/iap.httpsResourceAccessor'."
                )

    return CodingAgentGcpPosture(
        compliant=not violations,
        required_iam_roles=tuple(required_roles),
        violations=tuple(violations),
    )


async def execute_local_mcp_roundtrip(text: str) -> tuple[list[str], str, dict[str, str]]:
    """Spawn ``mcp_server.py`` over ``stdio`` and execute real JSON-RPC calls."""
    server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        env={**os.environ, "MCP_READONLY": "true"},
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_resp = await session.list_tools()
            tool_names = [t.name for t in tools_resp.tools]
            checksum_resp = await session.call_tool("calculate_checksum", {"text": text})
            mode_resp = await session.call_tool("server_security_mode", {})
            digest = checksum_resp.content[0].text
            mode_info = {"raw": mode_resp.content[0].text}
            return tool_names, digest, mode_info


async def run_offline() -> LabReport:
    banner(
        "Lab 04 — MCP, Claude Code on GCP, and Enterprise Tooling",
        "Offline verification: mcp_config.json, stdio JSON-RPC, Vertex AI ADC & Cloud Run MCP IAM",
    )
    report = LabReport("Lab 04 — MCP and Tooling")

    # 1. Validate mcp_config.json (Stdio vs Remote SSE)
    section("1. Validating Antigravity / Claude Code mcp_config.json")
    server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    sample_mcp_config = {
        "mcpServers": {
            "local-crypto": {
                "command": sys.executable,
                "args": [server_script],
                "env": {"MCP_READONLY": "true"},
            },
            "cloudrun-jira-gateway": {
                "serverUrl": "https://jira-mcp-gateway-uc.a.run.app/sse",
            },
        }
    }
    parsed_servers, errors = parse_and_validate_mcp_config(sample_mcp_config)
    table(
        ["Server Name", "Transport", "Endpoint / Command", "TLS / Env Keys"],
        [
            [
                s.name,
                s.transport,
                os.path.basename(s.target) if s.transport == "stdio" else s.target,
                ",".join(s.env_keys) if s.env_keys else f"TLS={s.uses_tls}",
            ]
            for s in parsed_servers
        ],
    )
    report.check(
        "mcp_config.json parses stdio + remote HTTPS SSE servers cleanly",
        not errors and len(parsed_servers) == 2,
        f"transports={[s.transport for s in parsed_servers]}",
    )

    _, insecure_errors = parse_and_validate_mcp_config(
        {"mcpServers": {"bad-sse": {"serverUrl": "http://insecure-mcp.corp.example.com/sse"}}}
    )
    report.check(
        "Validator rejects non-TLS HTTP remote SSE MCP server",
        len(insecure_errors) == 1 and "HTTPS" in insecure_errors[0],
        insecure_errors[0] if insecure_errors else "",
    )

    # 2. Real stdio JSON-RPC round-trip + stdout pollution check
    section("2. Local stdio MCP Server Round-Trip & stdout Hygiene")
    with open(server_script, encoding="utf-8") as fh:
        server_src = fh.read()
    polluted_lines = detect_stdio_stdout_pollution(server_src)
    broken_snippet = 'import sys\nprint("Connecting to DB...")\nprint("ok", file=sys.stderr)\n'
    broken_lines = detect_stdio_stdout_pollution(broken_snippet)

    tool_names, digest, _ = await execute_local_mcp_roundtrip("GoogleCloud")
    expected_digest = hashlib.sha256(b"GoogleCloud").hexdigest()
    report.check(
        "mcp_server.py writes zero logs to stdout (stderr only)",
        polluted_lines == [] and broken_lines == [2],
        f"mcp_server_bad_lines={polluted_lines}, detector_caught_line={broken_lines}",
    )
    report.check(
        "Real stdio JSON-RPC tool discovery & execution succeeded",
        "calculate_checksum" in tool_names and digest == expected_digest,
        f"tools={tool_names}, sha256={digest[:16]}...",
    )
    exam_note(
        "In MCP stdio transport, stdout is strictly reserved for JSON-RPC frames; "
        "any print() to stdout breaks protocol framing."
    )

    # 3. ADK McpToolset, RemoteMcpServer, Claude on Vertex AI, and AgentRegistry
    section("3. ADK McpToolset, Claude on Vertex AI & AgentRegistry Discovery")
    stdio_toolset = build_adk_toolset_from_server(
        parsed_servers[0], env={"MCP_READONLY": "true"}
    )
    sse_toolset = build_adk_toolset_from_server(
        parsed_servers[1], headers={"Authorization": "Bearer <id-token>"}
    )
    remote_mcp = RemoteMcpServer(
        name="cloudrun_mcp",
        url="https://cloudrun-mcp-uc.a.run.app/sse",
        allowed_tools=["list_services", "get_service_log"],
    )
    agent = Agent(
        name="enterprise_coding_assistant",
        model=DEFAULT_AGENT_MODEL,
        instruction="Use governed MCP tools to inspect services and compute digests.",
        tools=[stdio_toolset, sse_toolset],
    )
    from unittest.mock import patch as mock_patch
    from google.auth.credentials import AnonymousCredentials

    claude_vertex = Claude()
    with mock_patch(
        "google.auth.default", return_value=(AnonymousCredentials(), "demo-enterprise-proj")
    ):
        registry = AgentRegistry(
            project_id="demo-enterprise-proj", location="us-central1"
        )
    report.check(
        "ADK Agent binds both Stdio and SSE McpToolsets; AgentRegistry exposes MCP governance",
        len(agent.tools) == 2
        and remote_mcp.allowed_tools == ["list_services", "get_service_log"]
        and hasattr(registry, "get_mcp_toolset")
        and isinstance(claude_vertex, Claude),
        f"agent_model={agent.model}, claude_adapter={type(claude_vertex).__name__}",
    )

    # 4. Enterprise IAM & VPC-SC posture for Claude Code on GCP & Cloud Run MCP
    section("4. Enterprise IAM & VPC-SC Audit (Claude Code on GCP + Cloud Run MCP)")
    compliant_posture = evaluate_coding_agent_gcp_posture(
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
    risky_posture = evaluate_coding_agent_gcp_posture(
        agent_client="claude_code",
        uses_vertex_ai_adc=False,
        granted_iam_roles={"roles/aiplatform.admin"},
        inside_vpc_sc_perimeter=False,
        raw_external_api_key_present=True,
        remote_mcp_allow_unauthenticated=True,
        remote_mcp_caller_roles=set(),
        uses_iap_for_human_users=True,
    )
    report.check(
        "Claude Code on GCP passes with ADC + roles/aiplatform.user + VPC-SC + roles/run.invoker",
        compliant_posture.compliant and not risky_posture.compliant and len(risky_posture.violations) >= 4,
        f"required_roles={list(compliant_posture.required_iam_roles)}",
    )
    exam_note(
        "Claude Code on Google Cloud uses Vertex AI ADC + roles/aiplatform.user inside "
        "VPC-SC; remote Cloud Run MCP servers require roles/run.invoker (+ IAP for users)."
    )

    report.summary()
    return report


async def run_live(config: LabConfig) -> None:
    banner(
        "Lab 04 — Live Gemini + Local MCP Server Execution",
        f"Project: {config.project_id} | Location: {config.location} | Model: {DEFAULT_AGENT_MODEL}",
    )
    server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[server_script],
                env={**os.environ, "MCP_READONLY": "true"},
            )
        )
    )
    agent = Agent(
        name="crypto_agent",
        model=DEFAULT_AGENT_MODEL,
        tools=[mcp_toolset],
        instruction=(
            "Calculate the SHA-256 checksum for the text 'AgenticArchitect' "
            "using calculate_checksum and return only the hex digest."
        ),
    )
    runner = InMemoryRunner(agent=agent, app_name="lab_04_mcp")
    session = await runner.session_service.create_session(
        app_name="lab_04_mcp", user_id="architect"
    )
    msg = genai_types.Content(
        role="user",
        parts=[genai_types.Part.from_text(text="Hash 'AgenticArchitect'.")],
    )
    async for event in runner.run_async(
        user_id="architect", session_id=session.id, new_message=msg
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print("\nLive Agent Final Response:", event.content.parts[0].text)


def main() -> None:
    config = load_config()
    if require_live(config):
        asyncio.run(run_live(config))
    else:
        report = asyncio.run(run_offline())
        if not report.passed:
            sys.exit(1)


if __name__ == "__main__":
    main()
