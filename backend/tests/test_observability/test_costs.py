"""Tests for cost aggregation."""

from core.observability.costs import (
    DAILY_COST_LIMIT,
    CostAggregator,
    TokenUsage,
    calculate_cost,
)


def test_calculate_cost_sonnet():
    usage = TokenUsage(
        prompt_tokens=1000,
        completion_tokens=500,
        model="claude-sonnet-4-6",
    )
    cost = calculate_cost(usage)
    # 1K * 0.003 + 0.5K * 0.015 = 0.003 + 0.0075 = 0.0105
    assert abs(cost - 0.0105) < 0.0001


def test_calculate_cost_unknown_model():
    usage = TokenUsage(
        prompt_tokens=1000,
        completion_tokens=500,
        model="unknown-model",
    )
    assert calculate_cost(usage) == 0.0


def test_aggregator_tracks_daily():
    agg = CostAggregator()
    usage = TokenUsage(
        prompt_tokens=1000,
        completion_tokens=500,
        model="claude-sonnet-4-6",
    )
    agg.add_usage("req-1", usage)
    assert agg.get_daily_total() > 0
    assert not agg.is_over_daily_limit()


def test_aggregator_detects_limit():
    agg = CostAggregator()
    # Force over limit
    agg._daily_total = DAILY_COST_LIMIT + 1.0
    assert agg.is_over_daily_limit()


def test_aggregator_reset():
    agg = CostAggregator()
    agg._daily_total = 5.0
    agg.reset_daily()
    assert agg.get_daily_total() == 0.0
