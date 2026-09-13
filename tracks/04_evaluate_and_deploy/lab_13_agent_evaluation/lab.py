import os
from google.adk import Agent
from google.adk.agents import RunConfig
from google.adk.apps import App
from google.adk.evaluation import AgentEvaluator
from google.adk.evaluation.eval_metrics import EvalMetric
from common.models import DEFAULT_AGENT_MODEL, DEFAULT_JUDGE_MODEL, MODEL_CATALOG
from common.config import load_config, require_live

# We use the default test model, but an LLM-as-judge evaluator should typically use a distinct model.
AGENT_MODEL = DEFAULT_AGENT_MODEL
JUDGE_MODEL = DEFAULT_JUDGE_MODEL # In a real scenario, use gemini-3.5-pro or a stronger model.

# 1. Define a simple agent for the evaluation target
math_agent = Agent(
    name="math_agent",
    model=AGENT_MODEL,
    instruction="You are a helpful math agent. Answer math questions clearly."
)

app = App(
    name="math_eval_app",
    root_agent=math_agent
)

def run_offline():
    print("Running offline evaluation simulation (mock).")
    print(f"Creating an AgentEvaluator with judge model {JUDGE_MODEL}.")
    print("Metrics configured: rubric_based_final_response_quality_v1, llm_as_judge")
    print("Loaded eval set from lab_13_agent_evaluation/.evalset.json")
    print("Offline run completed successfully. See the tests for exact class assertions.")

def run_live(config):
    print("Running live evaluation against real LLMs...")
    # 2. Configure the Evaluator
    evaluator = AgentEvaluator(
        app=app,
        eval_metrics=[
            EvalMetric(name="rubric_based_final_response_quality_v1")
        ],
        judge_model_config={"model": JUDGE_MODEL}
    )

    # 3. Load the evaluation set and run
    # Note: We rely on the local file .evalset.json
    eval_set_id = "123"
    results = evaluator.evaluate(eval_set_path=".evalset.json")
    print("Evaluation Results:", results)

if __name__ == "__main__":
    import sys
    config = load_config()
    if "--live" in sys.argv and require_live(config):
        run_live(config)
    else:
        run_offline()
