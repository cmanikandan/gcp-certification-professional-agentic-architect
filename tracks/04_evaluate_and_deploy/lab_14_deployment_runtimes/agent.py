from google.adk import Agent
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG

AGENT_MODEL = DEFAULT_AGENT_MODEL

root_agent = Agent(
    name="simple_agent",
    model=AGENT_MODEL,
    instruction="You are a simple agent ready for deployment."
)
