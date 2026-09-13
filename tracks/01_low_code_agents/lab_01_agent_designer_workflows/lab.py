#!/usr/bin/env python3
"""Lab 1: Agent Designer Workflows (Prompt Templates)"""

import asyncio
from textwrap import dedent

from google.adk import Agent
from google.adk.models import Gemini
from common import load_config, require_live
from common.labkit import LabReport, banner, section, step, kv_table, detail
from common.models import DEFAULT_AGENT_MODEL

# ---------------------------------------------------------------------------
# The three prompt templates we are teaching.
# ---------------------------------------------------------------------------

ZERO_SHOT_PROMPT = "Extract the sentiment from this review. Reply ONLY with POSITIVE, NEGATIVE, or NEUTRAL."

FEW_SHOT_PROMPT = """\
Extract the sentiment from this review. Reply ONLY with POSITIVE, NEGATIVE, or NEUTRAL.

Examples:
Review: I loved the new features!
Sentiment: POSITIVE

Review: It broke on the first day.
Sentiment: NEGATIVE

Review: It is a phone. It makes calls.
Sentiment: NEUTRAL
"""

CHAIN_OF_THOUGHT_PROMPT = """\
Extract the sentiment from this review. Reply ONLY with POSITIVE, NEGATIVE, or NEUTRAL.

Before answering, think step-by-step:
1. Identify the core entity being reviewed.
2. List words that carry emotional weight.
3. Weigh the positive vs negative words.
4. Output your final classification.

Format:
Reasoning: <your step by step thought process>
Sentiment: <POSITIVE/NEGATIVE/NEUTRAL>
"""

# The query we will test.
TEST_REVIEW = "The battery life is amazing, but the screen scratches easily and customer support was rude. Overall, I regret buying it."


async def run_offline():
    """Offline deterministic path."""
    banner("Lab 1: Agent Designer Workflows", "Prompt Templates and System Instructions")
    
    section("1. Zero-Shot Agent")
    agent_zero = Agent(
        name="ZeroShotAgent",
        model=DEFAULT_AGENT_MODEL,
        instruction=ZERO_SHOT_PROMPT,
    )
    step("1", f"Created agent '{agent_zero.name}'")
    detail("Zero-shot relies entirely on the model's pre-trained knowledge.")
    kv_table({"Model": agent_zero.model, "Instruction length": len(agent_zero.instruction)})

    section("2. Few-Shot Agent")
    agent_few = Agent(
        name="FewShotAgent",
        model=DEFAULT_AGENT_MODEL,
        instruction=FEW_SHOT_PROMPT,
    )
    step("2", f"Created agent '{agent_few.name}'")
    detail("Few-shot constrains output formatting by providing concrete examples.")
    kv_table({"Model": agent_few.model, "Instruction length": len(agent_few.instruction)})
    
    section("3. Chain-of-Thought Agent")
    agent_cot = Agent(
        name="ChainOfThoughtAgent",
        model=DEFAULT_AGENT_MODEL,
        instruction=CHAIN_OF_THOUGHT_PROMPT,
    )
    step("3", f"Created agent '{agent_cot.name}'")
    detail("Chain-of-thought forces intermediate reasoning, reducing hallucinations on complex text.")
    kv_table({"Model": agent_cot.model, "Instruction length": len(agent_cot.instruction)})
    
    # Assertions
    report = LabReport("Prompt Templates")
    report.check("Zero-shot instruction configured", agent_zero.instruction == ZERO_SHOT_PROMPT)
    report.check("Few-shot includes examples", "Examples:" in agent_few.instruction)
    report.check("CoT includes reasoning request", "step-by-step" in agent_cot.instruction)
    report.summary()


async def run_live(config):
    """Live Google Cloud path."""
    banner("Lab 1: Agent Designer Workflows (LIVE)", "Testing Prompt Templates")
    
    model = Gemini(model=DEFAULT_AGENT_MODEL)
    
    for name, prompt in [
        ("Zero-Shot", ZERO_SHOT_PROMPT),
        ("Few-Shot", FEW_SHOT_PROMPT),
        ("Chain-of-Thought", CHAIN_OF_THOUGHT_PROMPT)
    ]:
        section(f"Testing {name} Template")
        agent = Agent(name=name.replace("-", ""), model=DEFAULT_AGENT_MODEL, instruction=prompt)
        
        step("Input", TEST_REVIEW)
        response = await agent.run(TEST_REVIEW)
        step("Output", f"\n{dedent(response.text)}")


def main():
    config = load_config()
    if require_live(config):
        asyncio.run(run_live(config))
    else:
        asyncio.run(run_offline())

if __name__ == "__main__":
    main()
