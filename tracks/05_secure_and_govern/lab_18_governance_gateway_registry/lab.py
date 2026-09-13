import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from common.config import load_config, require_live
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG

try:
    from google.adk.integrations.agent_registry import AgentRegistry
    HAS_REGISTRY = True
except ImportError:
    HAS_REGISTRY = False

MODEL = DEFAULT_AGENT_MODEL

def run_offline():
    """Deterministic, free, network-less execution of the lab."""
    print("=== Lab 18: Agent Governance, Gateways, and Registries (Offline Mode) ===")
    
    if not HAS_REGISTRY:
        print("[!] ERROR: google.adk.integrations.agent_registry not found.")
        print("    Did you install google-adk[agent-identity] and mcp?")
        sys.exit(1)
        
    print("\n1. Agent Registry Introspection...")
    print("The AgentRegistry is the discovery and governance plane.")
    
    # We won't instantiate it because it requires GCP credentials, 
    # but we will inspect its available methods to prove the API surface.
    registry_methods = [m for m in dir(AgentRegistry) if not m.startswith('_')]
    
    print("Available methods on AgentRegistry:")
    for method in sorted(registry_methods):
        print(f"  - {method}()")
        
    print("\nNote specifically: get_mcp_toolset() and get_remote_a2a_agent().")
    print("This shows the Registry's role in distributing MCP and A2A capabilities.")
    
    print("\n2. Agent Gateway Architecture (Simulation)...")
    print("An Agent Gateway is a chokepoint for policy enforcement and identity propagation.")
    
    def mock_agent_gateway(user_request, user_token):
        print(f"[Gateway] Intercepted request: {user_request}")
        print("[Gateway] Enforcing rate limits and logging...")
        
        # Identity Propagation
        print(f"[Gateway] Propagating user identity: {user_token}")
        mock_agent_execution(user_request, propagated_identity=user_token)
        
    def mock_agent_execution(request, propagated_identity):
        print("[Agent] Received request from Gateway.")
        print("[Agent] Calling Vertex AI Search tool...")
        print(f"[Tool] Performing ACL-Aware Search using identity: {propagated_identity}")
        print("[Tool] Results filtered to match user's permissions.")
        
    mock_agent_gateway("Summarize the Q3 financials", user_token="OAuth2:User_JaneDoe")
    
    print("\nLab 18 offline execution complete.")

def run_live(config):
    """Execution that touches Google Cloud (requires active credentials)."""
    print("=== Lab 18: Agent Governance, Gateways, and Registries (Live Mode) ===")
    print("Live mode requires a provisioned Agent Registry and Agent Gateway.")
    print("As Agent Gateway is a pattern often implemented via Apigee, we fallback to offline.")
    run_offline()

if __name__ == "__main__":
    config = load_config()
    if "--live" in sys.argv and require_live(config):
        run_live(config)
    else:
        run_offline()
