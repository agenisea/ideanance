"""Tests for model registry — PLAN47."""

from modules.agents.model_registry import (
    MODEL_REGISTRY,
    estimate_cost_per_query,
    get_model,
    list_models,
    quality_rating,
)


def test_registry_has_three_models():
    assert len(MODEL_REGISTRY) == 3


def test_sonnet_is_validated():
    m = get_model("anthropic:claude-sonnet-4-6")
    assert m is not None
    assert m.governance_quality == "validated"


def test_haiku_is_recommended():
    m = get_model("anthropic:claude-haiku-4-5")
    assert m is not None
    assert m.governance_quality == "recommended"


def test_gpt4o_is_recommended():
    m = get_model("openai:gpt-4o")
    assert m is not None
    assert m.governance_quality == "recommended"


def test_unknown_model_returns_none():
    assert get_model("unknown:model") is None


def test_list_models_all():
    models = list_models(min_quality="experimental")
    assert len(models) == 3


def test_list_models_validated_only():
    models = list_models(min_quality="validated")
    assert len(models) == 1
    assert models[0].model_id == "anthropic:claude-sonnet-4-6"


def test_quality_rating_thresholds():
    assert quality_rating(0.96) == "validated"
    assert quality_rating(0.92) == "recommended"
    assert quality_rating(0.85) == "experimental"
    assert quality_rating(0.70) == "not_recommended"


def test_estimate_cost():
    cost = estimate_cost_per_query(
        "anthropic:claude-sonnet-4-6",
        input_tokens=3000,
        output_tokens=1500,
    )
    # 3000/1000 * 0.003 + 1500/1000 * 0.015 = 0.009 + 0.0225
    assert abs(cost - 0.0315) < 0.001


def test_estimate_cost_unknown():
    assert estimate_cost_per_query("unknown") == 0.0
