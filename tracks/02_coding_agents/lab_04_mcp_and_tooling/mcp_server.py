#!/usr/bin/env python3
"""Local stdio MCP server for Lab 04 (MCP 2.x).

CRITICAL EXAM RULE:
When an MCP server uses ``stdio`` transport, ``stdout`` carries raw JSON-RPC 2.0
frames. Every diagnostic message or log line MUST be written to ``sys.stderr``.
"""

from __future__ import annotations

import hashlib
import os
import sys

from mcp.server import MCPServer

mcp = MCPServer("enterprise-crypto-server")


@mcp.tool(description="Calculates the SHA-256 hex digest of UTF-8 text.")
def calculate_checksum(text: str) -> str:
    """Return deterministic SHA-256 hex digest for ``text``."""
    print(f"[audit] hashing {len(text)} chars", file=sys.stderr)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@mcp.tool(description="Returns whether the server is running in read-only mode.")
def server_security_mode() -> dict[str, str]:
    """Return environment-scoped execution posture passed via mcp_config.json env."""
    readonly = os.getenv("MCP_READONLY", "true").lower()
    print(f"[audit] queried server_security_mode={readonly}", file=sys.stderr)
    return {
        "server": "enterprise-crypto-server",
        "transport": "stdio",
        "readonly": readonly,
    }


def main() -> None:
    print("Starting enterprise-crypto-server over stdio...", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
