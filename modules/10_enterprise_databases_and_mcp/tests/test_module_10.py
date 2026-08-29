"""
Unit Tests for Module 10: Enterprise Databases & MCP
"""

import sys
import json
from pathlib import Path
import pytest

module_dir = Path(__file__).resolve().parent.parent
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))

from mcp_database_server import (
    GoogleCloudMCPDatabaseServer,
    MCPAgentClient
)

def test_mcp_list_tools():
    server = GoogleCloudMCPDatabaseServer()
    client = MCPAgentClient(server)
    tools = client.discover_tools()
    names = [t["name"] for t in tools]

    assert "bigquery_list_tables" in names
    assert "bigquery_execute_query" in names
    assert "cloudsql_get_order_details" in names

def test_mcp_execute_bigquery():
    server = GoogleCloudMCPDatabaseServer()
    client = MCPAgentClient(server)
    res = client.execute_tool("bigquery_execute_query", {"query": "SELECT customer_id FROM dataset"})

    assert "result" in res
    content = json.loads(res["result"]["content"][0]["text"])
    assert len(content) == 2
    assert content[0]["customer_id"] == "C-901"

def test_mcp_security_block_drop():
    server = GoogleCloudMCPDatabaseServer()
    client = MCPAgentClient(server)
    res = client.execute_tool("bigquery_execute_query", {"query": "DROP TABLE dataset.table"})

    assert "result" in res
    assert res["result"].get("isError") is True
    assert "Security Error" in res["result"]["content"][0]["text"]
