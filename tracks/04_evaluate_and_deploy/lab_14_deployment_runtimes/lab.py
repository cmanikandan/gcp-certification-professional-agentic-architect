import sys
from common.config import load_config, require_live

def run_offline():
    print("Offline deployment simulation.")
    print("To deploy this agent to Cloud Run:")
    print("  adk deploy cloud_run . --project=MY_PROJECT --region=us-central1 --memory_service_uri=rag://12345")
    print("\nTo deploy this agent to Agent Runtime (Agent Engine):")
    print("  adk deploy agent_engine . --project=MY_PROJECT --region=us-central1")
    print("\nTo deploy this agent to GKE:")
    print("  adk deploy gke . --project=MY_PROJECT --region=us-central1 --cluster_name=my-cluster")
    print("\nNote: The exam refers to 'Agent Engine' as 'Agent Runtime'.")

def run_live(config, target="cloud_run"):
    print(f"Deploying to {target} is skipped in the automated live run to avoid provisioning delays and costs.")
    print(f"If this were a real deployment, we would execute: adk deploy {target} .")

if __name__ == "__main__":
    config = load_config()
    if "--live" in sys.argv and require_live(config):
        target = "cloud_run"
        if "agent_engine" in sys.argv:
            target = "agent_engine"
        run_live(config, target)
    else:
        run_offline()
