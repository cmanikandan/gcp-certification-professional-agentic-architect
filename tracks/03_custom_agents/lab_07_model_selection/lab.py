#!/usr/bin/env python3
"""Lab 07: Model Selection using ADK and common constraints."""
import sys
from common import DEFAULT_AGENT_MODEL, DEFAULT_JUDGE_MODEL, load_config, require_live
from common.models import select_model, get_profile, MODEL_CATALOG

# The ADK classes for modeling
from google.adk.models import (
    Gemini,
    Gemma,
    FallbackModel,
)


def run_offline():
    print("Running Lab 07 OFFLINE: Model Selection")
    
    print("\n--- Scenario 1: Air-gapped / Strict Data Residency ---")
    model_id, rationale = select_model(data_cannot_leave_premises=True)
    profile = get_profile(model_id)
    print(f"Selected: {model_id} (Hosting: {profile.hosting.value})")
    print(f"Rationale: {rationale}")
    # ADK Instantiation
    model_instance = Gemma(model=model_id)
    print(f"ADK Class: {model_instance.__class__.__name__}")
    
    print("\n--- Scenario 2: High-Volume Routing ---")
    model_id, rationale = select_model(high_volume_simple_task=True)
    profile = get_profile(model_id)
    print(f"Selected: {model_id} (Tier: {profile.tier.value})")
    print(f"Rationale: {rationale}")
    model_instance = Gemini(model=model_id)
    print(f"ADK Class: {model_instance.__class__.__name__}")
    
    print("\n--- Scenario 3: Complex Architectural Planning (GA Only) ---")
    model_id, rationale = select_model(needs_deep_reasoning=True, requires_ga_only=True)
    profile = get_profile(model_id)
    print(f"Selected: {model_id} (Tier: {profile.tier.value}, Preview: {profile.preview})")
    print(f"Rationale: {rationale}")
    
    print("\n--- Fallback Strategy ---")
    primary = Gemini(model=DEFAULT_AGENT_MODEL)
    secondary = Gemini(model=DEFAULT_JUDGE_MODEL)
    fallback = FallbackModel(models=[primary, secondary])
    print(f"Created a {fallback.__class__.__name__} to failover from {primary.model} to {secondary.model}.")


def run_live(config):
    print("Running Lab 07 LIVE: Model Selection")
    # For a live run, we might instantiate the ADK models with api_keys, but since ADK models
    # often take the key from environment or project default, we can just invoke them.
    # We will keep it simple here.
    run_offline()
    print("Live execution complete (used offline path for demonstrations).")


if __name__ == "__main__":
    config = load_config(sys.argv[1:])
    if require_live(config):
        run_live(config)
    else:
        run_offline()
