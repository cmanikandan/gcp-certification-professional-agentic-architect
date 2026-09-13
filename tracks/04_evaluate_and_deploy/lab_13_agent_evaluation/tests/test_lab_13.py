import json
import os
from common.models import MODEL_CATALOG
import sys; import os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__))); import agent

LAB_DIR = os.path.dirname(os.path.dirname(__file__))

def test_uses_only_verified_models():
    assert agent.AGENT_MODEL in MODEL_CATALOG

def test_config_json_schema():
    config_path = os.path.join(LAB_DIR, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Assert on metric names matching ADK 2.9.0 available metrics
    assert "criteria" in config
    assert "rubric_based_final_response_quality_v1" in config["criteria"]
    
    crit = config["criteria"]["rubric_based_final_response_quality_v1"]
    assert "threshold" in crit
    assert "judge_model_options" in crit
    
    judge_model = crit["judge_model_options"].get("judge_model")
    assert judge_model in MODEL_CATALOG

def test_evalset_json_schema():
    evalset_path = os.path.join(LAB_DIR, ".evalset.json")
    with open(evalset_path, "r") as f:
        evalset = json.load(f)
        
    assert "eval_set_id" in evalset
    assert "eval_cases" in evalset
    assert len(evalset["eval_cases"]) > 0
    
    case = evalset["eval_cases"][0]
    assert "eval_id" in case
    # In StaticConversation, there's a list of Invocations
    assert "conversation" in case
