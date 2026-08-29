"""
Module 10: Build AI Agents with Enterprise Databases & MCP
Demonstrates:
1. Model Context Protocol (MCP) Server Implementation exposing BigQuery & Cloud SQL tools
2. MCP JSON-RPC 2.0 Request/Response Protocol Handler
3. MCP Agent Client Executing Parameterized Database Introspection & Safe Querying
"""

import os
import json
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class GoogleCloudMCPDatabaseServer:
    """Simulates an MCP Server providing standardized database tools to agents."""

    def __init__(self, project_id: str = "gcp-prod-arch-2026"):
        self.project_id = os.getenv("GCP_PROJECT_ID", project_id)
        # Mock database schemas
        self.bigquery_tables = {
            "analytics.customer_churn": [
                {"name": "customer_id", "type": "STRING"},
                {"name": "tenure_months", "type": "INTEGER"},
                {"name": "monthly_charges", "type": "FLOAT"},
                {"name": "churn_probability", "type": "FLOAT"}
            ]
        }
        self.cloudsql_tables = {
            "public.orders": [
                {"name": "order_id", "type": "VARCHAR(64)"},
                {"name": "status", "type": "VARCHAR(32)"},
                {"name": "total_amount", "type": "NUMERIC(10,2)"}
            ]
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """MCP Protocol: Returns tool schemas."""
        return [
            {
                "name": "bigquery_list_tables",
                "description": "Lists all BigQuery tables and dataset schemas in the project.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {"type": "string", "description": "BigQuery dataset ID"}
                    },
                    "required": ["dataset_id"]
                }
            },
            {
                "name": "bigquery_execute_query",
                "description": "Executes a read-only SQL query against Google Cloud BigQuery.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Standard SQL query string"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "cloudsql_get_order_details",
                "description": "Retrieves transactional order record from Cloud SQL PostgreSQL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "Unique Order ID"}
                    },
                    "required": ["order_id"]
                }
            }
        ]

    def handle_jsonrpc_request(self, request_json: Dict[str, Any]) -> Dict[str, Any]:
        """Handles MCP JSON-RPC 2.0 protocol messages."""
        req_id = request_json.get("id", 1)
        method = request_json.get("method")
        params = request_json.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.list_tools()}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = self._call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found."}
        }

    def _call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "bigquery_list_tables":
            dataset = args.get("dataset_id", "analytics")
            return {"dataset": dataset, "tables": list(self.bigquery_tables.keys())}

        elif name == "bigquery_execute_query":
            query = args.get("query", "").upper()
            if any(forbidden in query for forbidden in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
                return {"isError": True, "content": [{"type": "text", "text": "Security Error: Only SELECT queries are permitted."}]}

            # Mock query result
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps([
                        {"customer_id": "C-901", "tenure_months": 24, "churn_probability": 0.04},
                        {"customer_id": "C-902", "tenure_months": 3, "churn_probability": 0.78}
                    ])
                }]
            }

        elif name == "cloudsql_get_order_details":
            order_id = args.get("order_id")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({"order_id": order_id, "status": "SHIPPED", "total_amount": 349.99})
                }]
            }

        return {"isError": True, "content": [{"type": "text", "text": f"Tool '{name}' not recognized."}]}

class MCPAgentClient:
    """Agent client that negotiates MCP protocol with the database server."""

    def __init__(self, server: GoogleCloudMCPDatabaseServer):
        self.server = server

    def discover_tools(self) -> List[Dict[str, Any]]:
        req = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        res = self.server.handle_jsonrpc_request(req)
        return res["result"]["tools"]

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": args}
        }
        return self.server.handle_jsonrpc_request(req)

def main():
    print("====================================================================")
    print("Module 10: Build AI Agents with Enterprise Databases & MCP")
    print("====================================================================\n")

    server = GoogleCloudMCPDatabaseServer()
    client = MCPAgentClient(server)

    # 1. Discover Tools via MCP
    print("--- 1. Agent Discovering MCP Tools ---")
    tools = client.discover_tools()
    for t in tools:
        print(f"  🔧 Tool: {t['name']} -> {t['description']}")

    # 2. Execute BigQuery Query via MCP
    print("\n--- 2. Executing BigQuery Query via MCP Tool ---")
    bq_res = client.execute_tool(
        "bigquery_execute_query",
        {"query": "SELECT customer_id, churn_probability FROM analytics.customer_churn WHERE churn_probability > 0.5"}
    )
    print("BigQuery MCP Response:\n", json.dumps(bq_res, indent=2))

    # 3. Test Security Guardrail (Block Non-SELECT Query)
    print("\n--- 3. Testing MCP Security Policy on Destructive Query ---")
    bad_res = client.execute_tool("bigquery_execute_query", {"query": "DROP TABLE analytics.customer_churn"})
    print("Destructive Query Result:\n", json.dumps(bad_res, indent=2))

if __name__ == "__main__":
    main()
