from google.adk import Agent
from common.models import DEFAULT_AGENT_MODEL, MODEL_CATALOG

AGENT_MODEL = DEFAULT_AGENT_MODEL

root_agent = Agent(
    name="math_agent",
    model=AGENT_MODEL,
    instruction="You are a helpful math agent. Answer math questions clearly."
)
