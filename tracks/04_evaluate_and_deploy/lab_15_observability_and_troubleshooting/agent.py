import logging
from google.adk import Agent
from common.models import MODEL_CATALOG, DEFAULT_AGENT_MODEL

logger = logging.getLogger(__name__)

def mock_flaky_tool(query: str) -> str:
    """A tool that simulates failure to demonstrate tracing and loop detection."""
    logger.info(f"Executing mock_flaky_tool with query: {query}")
    if "fail" in query:
        raise ValueError("Simulated tool failure: The backend API returned a 500 error.")
    return "Tool execution succeeded."

root_agent = Agent(
    name="troubleshooting_agent",
    model=DEFAULT_AGENT_MODEL,
    instruction="You are an agent being monitored for observability. Use tools if necessary.",
    tools=[mock_flaky_tool]
)
