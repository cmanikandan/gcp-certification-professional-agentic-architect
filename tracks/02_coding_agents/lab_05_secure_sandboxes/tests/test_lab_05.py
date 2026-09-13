import os, sys
from unittest.mock import patch
patch("kubernetes.config.load_incluster_config").start()
patch("kubernetes.config.load_kube_config").start()

from google.adk.code_executors import (
    GkeCodeExecutor,
    UnsafeLocalCodeExecutor,
    AgentEngineSandboxCodeExecutor
)
from google.adk.integrations.cloud_run import CloudRunSandboxCodeExecutor
from google.adk.integrations.e2b import E2BEnvironment
from google.adk.integrations.daytona import DaytonaEnvironment

def test_gke_executor_isolation_modes():
    """Verify that GkeCodeExecutor differentiates between job and sandbox modes."""
    prod_executor = GkeCodeExecutor(
        executor_type="sandbox",
        namespace="test",
        image="python:3.14-slim",
        cpu_requested="500m",
        mem_requested="512Mi",
        cpu_limit="1000m",
        mem_limit="1024Mi",
        sandbox_gateway_name="default",
        sandbox_template="default",
        stateful=False
    )
    assert prod_executor.executor_type == "sandbox"
    assert prod_executor.cpu_requested == "500m"
    
    dev_executor = GkeCodeExecutor(
        executor_type="job",
        namespace="test",
        image="python:3.14-slim"
    )
    assert dev_executor.executor_type == "job"
    assert prod_executor.executor_type != dev_executor.executor_type

def test_cloudrun_sandbox_egress():
    """Verify CloudRunSandboxCodeExecutor allows toggling network egress."""
    executor = CloudRunSandboxCodeExecutor(
        sandbox_bin="/usr/local/bin/sandbox",
        allow_egress=False,
        stateful=False,
        timeout_seconds=30
    )
    assert executor.allow_egress is False
    assert executor.stateful is False
    assert executor.timeout_seconds == 30

def test_third_party_environments():
    """Verify E2B and Daytona configurations."""
    e2b = E2BEnvironment(image="base", timeout=300)
    assert e2b is not None
    
    daytona = DaytonaEnvironment(image="base", timeout=300)
    assert daytona is not None

def test_unsafe_local_executor():
    """Verify UnsafeLocalCodeExecutor can be instantiated."""
    executor = UnsafeLocalCodeExecutor()
    assert executor is not None
