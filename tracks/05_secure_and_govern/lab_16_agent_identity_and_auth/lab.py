import sys
import os

# Ensure we can import from the common module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from common.config import load_config, require_live
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG
# The exam requires understanding how to configure Agent Identity auth
from google.adk.auth import AuthConfig
try:
    from google.adk.integrations.agent_identity import GcpAuthProviderScheme, GcpAuthProvider
    HAS_AGENT_IDENTITY = True
except ImportError:
    HAS_AGENT_IDENTITY = False

# The model to use
MODEL = DEFAULT_AGENT_MODEL

def run_offline():
    """Deterministic, free, network-less execution of the lab."""
    print("=== Lab 16: Agent Identity and Auth (Offline Mode) ===")
    
    if not HAS_AGENT_IDENTITY:
        print("[!] ERROR: google.adk.integrations.agent_identity not found.")
        print("    Did you install google-adk[agent-identity]?")
        sys.exit(1)
        
    print("\n1. Constructing a GcpAuthProviderScheme...")
    scheme = GcpAuthProviderScheme(
        name="projects/my-project/locations/us-central1/connectors/my-connector",
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
        continue_uri="https://myapp.example.com/oauth2callback"
    )
    
    print(f"Scheme Name: {scheme.name}")
    print(f"Scheme Scopes: {scheme.scopes}")
    print(f"Scheme Type: {scheme.type_}")
    
    print("\n2. Configuring Tool Auth...")
    auth_config = AuthConfig(auth_scheme=scheme)
    print(f"Configured AuthConfig with scheme: {auth_config.auth_scheme.__class__.__name__}")
    
    print("\n3. Principal Access Boundary (PAB) Policy Design...")
    print("PABs restrict what resources an agent's service account can access.")
    print("Even if the SA has roles/editor globally, a PAB can restrict it to ONE project.")
    
    pab_command = """
gcloud iam principal-access-boundary-policies create restrict-to-sandbox \\
  --organization=123456789 \\
  --location=global \\
  --details-rules="description=Sandbox Only,effect=ALLOW,resources=//cloudresourcemanager.googleapis.com/projects/my-sandbox-project"
"""
    print("Equivalent CLI command to create the PAB:")
    print(pab_command.strip())
    
    print("\nLab 16 offline execution complete.")

def run_live(config):
    """Execution that touches Google Cloud (requires active credentials)."""
    print("=== Lab 16: Agent Identity and Auth (Live Mode) ===")
    print("Live mode for this lab requires organization-level IAM permissions to create PAB policies.")
    print("Since most learners test in a standalone project without an organization,")
    print("we fallback to the offline demonstration for safety.")
    run_offline()

if __name__ == "__main__":
    config = load_config()
    if "--live" in sys.argv and require_live(config):
        run_live(config)
    else:
        run_offline()
