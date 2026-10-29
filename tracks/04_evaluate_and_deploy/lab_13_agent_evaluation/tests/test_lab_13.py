"""Tests for Lab 13 — ADK Eval Metrics vs. Rubrics & Gen AI Evaluation Service."""

from __future__ import annotations

import importlib
import json
import os
import sys

from google.adk.evaluation.eval_metrics import ToolTrajectoryCriterion
from vertexai.evaluation import CustomMetric, EvalTask, PairwiseMetric, PointwiseMetric

from common.models import DEFAULT_AGENT_MODEL, DEFAULT_JUDGE_MODEL, MODEL_CATALOG

LAB_DIR = os.path.dirname(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(LAB_DIR, "../../.."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

agent = importlib.import_module("tracks.04_evaluate_and_deploy.lab_13_agent_evaluation.agent")
lab = importlib.import_module("tracks.04_evaluate_and_deploy.lab_13_agent_evaluation.lab")


def test_uses_only_verified_models_and_distinct_judge() -> None:
    assert agent.AGENT_MODEL in MODEL_CATALOG
    assert lab.AGENT_MODEL == DEFAULT_AGENT_MODEL
    assert lab.JUDGE_MODEL == DEFAULT_JUDGE_MODEL
    assert lab.JUDGE_MODEL in MODEL_CATALOG
    assert lab.JUDGE_MODEL != lab.AGENT_MODEL


def test_config_json_schema_combines_metrics_and_rubrics() -> None:
    config_path = os.path.join(LAB_DIR, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    assert "criteria" in config
    assert "tool_trajectory_avg_score" in config["criteria"]
    assert "rubric_based_final_response_quality_v1" in config["criteria"]
    assert "rubric_based_tool_use_quality_v1" in config["criteria"]
    assert "hallucinations_v1" in config["criteria"]

    traj = config["criteria"]["tool_trajectory_avg_score"]
    assert traj["match_type"] == "IN_ORDER"

    crit = config["criteria"]["rubric_based_final_response_quality_v1"]
    assert "threshold" in crit
    assert "judge_model_options" in crit
    assert len(crit["rubrics"]) >= 2

    judge_model = crit["judge_model_options"].get("judge_model")
    assert judge_model in MODEL_CATALOG


def test_evalset_json_validates_against_adk_pydantic_schema() -> None:
    evalset = lab.load_lab_eval_set()
    assert evalset.eval_set_id == "hipaa_pharmacy_support_golden_v1"
    assert len(evalset.eval_cases) == 2

    first_case = evalset.eval_cases[0]
    assert first_case.eval_id == "case_01_verified_hipaa_order_lookup"
    assert first_case.conversation is not None
    assert len(first_case.conversation) == 1
    assert first_case.conversation[0].intermediate_data is not None
    tool_names = [t.name for t in first_case.conversation[0].intermediate_data.tool_uses]
    assert tool_names == ["verify_patient_identity", "lookup_prescription_order"]

    # Case 2 proves reference-free rubric evaluation (no fixed final_response required!)
    second_case = evalset.eval_cases[1]
    assert second_case.conversation is not None
    assert second_case.conversation[0].final_response is None
    assert second_case.conversation[0].rubrics is not None
    assert len(second_case.conversation[0].rubrics) >= 1


def test_trajectory_match_types_exact_vs_in_order_vs_any_order() -> None:
    criteria = lab.build_trajectory_criteria()
    assert criteria["EXACT"].match_type == ToolTrajectoryCriterion.MatchType.EXACT
    assert criteria["IN_ORDER"].match_type == ToolTrajectoryCriterion.MatchType.IN_ORDER
    assert criteria["ANY_ORDER"].match_type == ToolTrajectoryCriterion.MatchType.ANY_ORDER

    expected = ["verify_patient_identity", "lookup_prescription_order"]
    with_helper = [
        "verify_patient_identity",
        "check_weather_advisory",
        "lookup_prescription_order",
    ]
    violated_order = ["lookup_prescription_order", "verify_patient_identity"]

    assert lab.score_tool_trajectory(expected, with_helper, ToolTrajectoryCriterion.MatchType.EXACT) == 0.0
    assert lab.score_tool_trajectory(expected, with_helper, ToolTrajectoryCriterion.MatchType.IN_ORDER) == 1.0
    assert lab.score_tool_trajectory(expected, violated_order, ToolTrajectoryCriterion.MatchType.IN_ORDER) == 0.0
    assert lab.score_tool_trajectory(expected, violated_order, ToolTrajectoryCriterion.MatchType.ANY_ORDER) == 1.0


def test_rubric_criterion_and_genai_eval_service_classes() -> None:
    rubric_crit = lab.build_hipaa_rubrics_criterion()
    assert rubric_crit.threshold == 0.8
    assert rubric_crit.judge_model_options.judge_model == DEFAULT_JUDGE_MODEL
    assert len(rubric_crit.rubrics) == 2

    suite = lab.build_genai_eval_service_suite()
    assert isinstance(suite["eval_task"], EvalTask)
    assert isinstance(suite["pointwise_metric"], PointwiseMetric)
    assert isinstance(suite["pairwise_metric"], PairwiseMetric)
    assert isinstance(suite["custom_metric"], CustomMetric)


def test_evaluation_tooling_decision_matrix() -> None:
    ci_choice, _ = lab.select_evaluation_tooling(
        is_ci_pr_regression_gate=True,
        has_fixed_golden_reference=True,
    )
    assert ci_choice == "adk_deterministic_metric"

    rubric_choice, _ = lab.select_evaluation_tooling(
        evaluates_open_ended_policy_or_tone=True,
        has_fixed_golden_reference=False,
    )
    assert rubric_choice == "adk_rubric_evaluator"

    pairwise_choice, _ = lab.select_evaluation_tooling(
        compares_two_models_pairwise_at_scale=True,
    )
    assert pairwise_choice == "genai_eval_service_pairwise"

    prod_choice, _ = lab.select_evaluation_tooling(
        samples_production_bigquery_traces=True,
    )
    assert prod_choice == "genai_eval_service_adaptive_rubrics"
