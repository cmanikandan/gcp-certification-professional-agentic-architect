import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from common.config import load_config, require_live
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG

from google.adk import Agent
from google.adk.tools import get_user_choice, request_input
try:
    from google.adk.integrations.model_armor import ModelArmorPlugin, ModelArmorConfig
    HAS_GCP_EXTRA = True
except ImportError:
    HAS_GCP_EXTRA = False

MODEL = DEFAULT_AGENT_MODEL

def run_offline():
    """Deterministic, free, network-less execution of the lab."""
    print("=== Lab 17: Model Armor and HITL (Offline Mode) ===")
    
    if not HAS_GCP_EXTRA:
        print("[!] ERROR: google.adk.integrations.model_armor not found.")
        print("    Did you install google-adk[gcp]?")
        sys.exit(1)
        
    print("\n1. Configuring Model Armor Plugin...")
    config = ModelArmorConfig(
        prompt_template_name="projects/my-project/locations/us-central1/templates/my-prompt-template",
        response_template_name="projects/my-project/locations/us-central1/templates/my-response-template",
        input_blocked_message="Your input was blocked due to a policy violation.",
        output_blocked_message="The generated response was blocked due to a policy violation.",
        block_on_screening_failure=True # Fail-closed
    )
    
    plugin = ModelArmorPlugin(config=config, name="model_armor_plugin")
    
    print(f"Configured Plugin: {plugin.name}")
    print(f"Prompt Template: {config.prompt_template_name}")
    print(f"Response Template: {config.response_template_name}")
    print(f"Fail-Closed (block_on_screening_failure): {config.block_on_screening_failure}")
    
    print("\n2. Human-in-the-Loop (HITL) Guardrails...")
    print("The ADK provides `request_input` and `get_user_choice` for built-in HITL.")
    print("Agents can pause execution and wait for human confirmation.")
    
    # Mocking a HITL scenario conceptually
    print("\nExample Tool Callback for HITL:")
    print('''
async def require_approval(callback_context, llm_request):
    if "delete_database" in llm_request.content.parts[0].text:
        # Pause and ask the human
        choice = get_user_choice(
            prompt="Agent wants to delete the database. Approve?", 
            choices=["yes", "no"]
        )
        if choice == "no":
            raise PermissionError("Human denied execution.")
    ''')
    
    print("\nLab 17 offline execution complete.")

def run_live(config):
    """Execution that touches Google Cloud (requires active credentials)."""
    print("=== Lab 17: Model Armor and HITL (Live Mode) ===")
    print("Live mode requires a provisioned Model Armor template.")
    print("Falling back to offline mode for safety.")
    run_offline()

if __name__ == "__main__":
    config = load_config()
    if "--live" in sys.argv and require_live(config):
        run_live(config)
    else:
        run_offline()
