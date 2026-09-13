#!/usr/bin/env python3
import sys
import hashlib
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# 1. Initialize the MCP Server
app = Server("enterprise-crypto-server")

async def handle_list_tools(request) -> types.ListToolsResult:
    """Expose available tools to the MCP client."""
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="calculate_checksum",
                description="Calculates SHA-256 checksum of text.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to hash"}
                    },
                    "required": ["text"],
                }
            )
        ]
    )

async def handle_call_tool(request: types.CallToolRequest) -> types.CallToolResult:
    """Handle tool execution requests."""
    name = request.params.name
    arguments = request.params.arguments or {}
    if name == "calculate_checksum":
        text = arguments.get("text", "")
        checksum = hashlib.sha256(str(text).encode()).hexdigest()
        return types.CallToolResult(content=[types.TextContent(type="text", text=checksum)])
    raise ValueError(f"Unknown tool: {name}")

app.add_request_handler(types.ListToolsRequest.model_fields['method'].default, types.ListToolsRequest, handle_list_tools)
app.add_request_handler(types.CallToolRequest.model_fields['method'].default, types.CallToolRequest, handle_call_tool)

async def main():
    # 2. Run over stdio transport
    # CRITICAL EXAM POINT: stdio transport requires reading from stdin and writing to stdout.
    # Therefore, ALL application logging MUST go to stderr.
    print("Starting enterprise-crypto-server...", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
