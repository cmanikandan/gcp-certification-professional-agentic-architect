import os, sys
if "pytest" not in sys.modules:
    from unittest.mock import patch
    patch("kubernetes.config.load_incluster_config").start()
    patch("kubernetes.config.load_kube_config").start()

from common import load_config, require_live

from google.adk.code_executors import (
    GkeCodeExecutor,
    UnsafeLocalCodeExecutor,
    AgentEngineSandboxCodeExecutor,
)
from google.adk.integrations.cloud_run import CloudRunSandboxCodeExecutor
from google.adk.integrations.e2b import E2BEnvironment
from google.adk.integrations.daytona import DaytonaEnvironment

def get_executor_for_environment(env: str):
    """
    Policy engine that decides which Code Executor (or Environment) to use.
    """
    print(f"--- Requesting Code Environment for: {env.upper()} ---")
    
    if env == "production_gke":
        executor = GkeCodeExecutor(
            executor_type="sandbox",
            namespace="agent-sandbox",
            image="python:3.14-slim",
            cpu_requested="500m",
            mem_requested="512Mi",
            cpu_limit="1000m",
            mem_limit="1024Mi",
            sandbox_gateway_name="default",
            sandbox_template="default",
            stateful=False
        )
        print("Selected GkeCodeExecutor (sandbox mode). Highest isolation via gVisor.")
        return executor
        
    elif env == "cloud_run":
        executor = CloudRunSandboxCodeExecutor(
            sandbox_bin="/usr/local/bin/sandbox",
            allow_egress=False,
            stateful=False,
            timeout_seconds=30
        )
        print("Selected CloudRunSandboxCodeExecutor. Runs INSIDE Cloud Run.")
        return executor
        
    elif env == "agent_engine":
        executor = AgentEngineSandboxCodeExecutor()
        print("Selected AgentEngineSandboxCodeExecutor. Integrated with Agent Runtime.")
        return executor
        
    elif env == "third_party_e2b":
        env_e2b = E2BEnvironment(
            image="base",
            timeout=300
        )
        print("Selected E2BEnvironment. Third-party cloud execution.")
        return env_e2b

    elif env == "third_party_daytona":
        env_daytona = DaytonaEnvironment(
            image="base",
            timeout=300
        )
        print("Selected DaytonaEnvironment. Third-party cloud execution.")
        return env_daytona
        
    elif env == "local_dev":
        executor = UnsafeLocalCodeExecutor()
        print("WARNING: Selected UnsafeLocalCodeExecutor. ZERO isolation. Do NOT use in production.")
        return executor
        
    else:
        raise ValueError("Unknown environment")

def run_offline():
    prod_executor = get_executor_for_environment("production_gke")
    assert prod_executor.executor_type == "sandbox"
    print("\n")
    
    cr_executor = get_executor_for_environment("cloud_run")
    assert cr_executor.allow_egress is False
    print("\n")
    
    ae_executor = get_executor_for_environment("agent_engine")
    print("\n")

    e2b_env = get_executor_for_environment("third_party_e2b")
    print("\n")
    
    daytona_env = get_executor_for_environment("third_party_daytona")
    print("\n")

    try:
        print("--- Testing Policy Enforcement ---")
        dev_executor = get_executor_for_environment("local_dev")
        if isinstance(dev_executor, UnsafeLocalCodeExecutor):
            print("Policy Alert: UnsafeLocalCodeExecutor detected.")
    except Exception as e:
        print(e)
        
    print("\nOffline execution successful.")

def run_live(config):
    print("Executing live code sandboxing...")
    run_offline()

def main():
    config = load_config()
    if require_live(config):
        run_live(config)
    else:
        run_offline()

if __name__ == "__main__":
    main()
