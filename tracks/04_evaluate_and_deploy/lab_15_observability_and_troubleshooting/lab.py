import sys
import time
import logging
from common.config import load_config, require_live
from common.labkit import banner, section, step, detail, LabReport
import agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_offline():
    banner("Lab 15: Observability and Troubleshooting", "Simulating traces and metrics offline")
    
    report = LabReport("Observability Tests")
    
    section("Simulating an Agent Trace")
    step(1, "Starting agent turn...")
    start_time = time.time()
    
    # Simulate LLM call
    step(2, "Simulating LLM call (span: trace_call_llm)")
    llm_start = time.time()
    time.sleep(0.1) # Simulate network latency
    llm_latency = time.time() - llm_start
    input_tokens = 150
    output_tokens = 50
    detail(f"LLM Latency: {llm_latency:.3f}s | Input Tokens: {input_tokens} | Output Tokens: {output_tokens}")
    
    # Simulate tool call (failure)
    step(3, "Simulating Tool call (span: trace_tool_call)")
    tool_start = time.time()
    try:
        agent.mock_flaky_tool("make it fail")
    except Exception as e:
        tool_latency = time.time() - tool_start
        detail(f"Tool Latency: {tool_latency:.3f}s | Result: ERROR - {str(e)}")
        report.check("Tool Failure Detected", True, "Successfully simulated and caught tool error.")
    
    # Simulate LLM retry (loop detection)
    step(4, "Simulating LLM retry after tool failure (Loop Detection)")
    llm_retry_start = time.time()
    time.sleep(0.1)
    llm_retry_latency = time.time() - llm_retry_start
    input_tokens += 250
    output_tokens += 10
    detail(f"LLM Latency: {llm_retry_latency:.3f}s | Total Input Tokens: {input_tokens} | Total Output Tokens: {output_tokens}")
    
    total_latency = time.time() - start_time
    detail(f"Total Turn Latency: {total_latency:.3f}s")
    
    report.check("Latency Attribution", total_latency > llm_latency, "Total latency accounts for both LLM and tools.")
    report.check("Token Accounting", input_tokens == 400, "Successfully aggregated token metrics across reasoning loops.")
    
    section("Evaluation and Conformance (Offline)")
    step(5, "Simulating ADK CLI commands for conformance")
    detail("adk conformance record tests/core")
    detail("adk conformance test --mode=replay tests/core")
    report.check("CLI Introspection", True, "adk conformance commands documented.")
    
    report.summary()

def run_live(config):
    banner("Lab 15: Observability and Troubleshooting", "Live mode")
    print("In a fully live environment, you would run:")
    print("  adk telemetry enable")
    print("Then run your agent to push traces to Google Cloud Operations Suite.")
    print("To view logs:")
    print("  gcloud logging read 'resource.type=\"cloud_run_revision\" AND textPayload:\"Tool execution failed\"' --limit=10")

if __name__ == "__main__":
    config = load_config()
    if config.live and require_live(config):
        run_live(config)
    else:
        run_offline()
