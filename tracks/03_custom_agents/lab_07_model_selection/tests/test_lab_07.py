import lab
from common.models import (
    DEFAULT_AGENT_MODEL,
    DEFAULT_FAST_MODEL,
    DEFAULT_JUDGE_MODEL,
    DEFAULT_OSS_MODEL,
    DEFAULT_OSS_MOE_MODEL,
    FLOATING_ALIASES,
    MODEL_CATALOG,
    Hosting,
    Licensing,
    Tier,
    estimate_cost_ratio,
    get_profile,
    select_model,
)
from google.adk.models import (
    ApigeeLlm,
    Claude,
    FallbackModel,
    Gemini,
    Gemma,
    Gemma3Ollama,
    LiteLlm,
)


def test_uses_only_verified_models():
    models_to_test = [
        select_model(data_cannot_leave_premises=True)[0],
        select_model(high_volume_simple_task=True)[0],
        select_model(needs_deep_reasoning=True, requires_ga_only=True)[0],
        select_model(needs_deep_reasoning=True, requires_ga_only=False)[0],
        select_model()[0],
    ]
    for model_id in models_to_test:
        assert model_id in MODEL_CATALOG


def test_adk_model_instantiation():
    gemma_model = Gemma(model=DEFAULT_OSS_MODEL)
    assert gemma_model.model == DEFAULT_OSS_MODEL

    gemini_model = Gemini(model=DEFAULT_AGENT_MODEL)
    assert gemini_model.model == DEFAULT_AGENT_MODEL

    fallback = FallbackModel(models=[gemini_model, gemma_model])
    assert fallback.models[0] == gemini_model
    assert fallback.models[1] == gemma_model
    assert {429, 500, 502, 503, 504}.issubset(fallback.retriable_status_codes)


def test_enterprise_model_suite_covers_all_hosting_patterns():
    suite = lab.build_enterprise_model_suite()
    assert isinstance(suite["dense_oss"], Gemma)
    assert isinstance(suite["moe_oss"], Gemma)
    assert suite["moe_oss"].model == DEFAULT_OSS_MOE_MODEL
    assert isinstance(suite["litellm_oss"], LiteLlm)
    assert isinstance(suite["local_ollama"], Gemma3Ollama)
    assert isinstance(suite["partner_claude"], Claude)
    assert isinstance(suite["governed_apigee"], ApigeeLlm)

    moe_profile = get_profile(DEFAULT_OSS_MOE_MODEL)
    assert moe_profile.hosting is Hosting.SELF_HOSTED
    assert moe_profile.licensing is Licensing.OPEN_WEIGHTS
    assert estimate_cost_ratio(DEFAULT_OSS_MOE_MODEL) == 0.0


def test_multi_tier_routing_cost_and_pinning_checks():
    estimate = lab.compute_tiered_routing_savings(simple_fraction=0.90, total_requests=1_000)
    assert estimate.tiered_cost_units < estimate.all_pro_cost_units
    assert estimate.savings_pct > 80.0

    ga_pro_id, _ = select_model(needs_deep_reasoning=True, requires_ga_only=True)
    assert get_profile(ga_pro_id).tier is Tier.PRO
    assert get_profile(ga_pro_id).preview is False

    ok_alias, _ = lab.validate_production_model_pinning(FLOATING_ALIASES[0])
    ok_pinned, _ = lab.validate_production_model_pinning(DEFAULT_FAST_MODEL)
    assert not ok_alias
    assert ok_pinned
    assert DEFAULT_JUDGE_MODEL != DEFAULT_AGENT_MODEL


def test_offline_report_passes():
    report = lab.run_offline()
    assert report.passed
