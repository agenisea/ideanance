"""Model registry with governance quality ratings.

Static configuration — not a service, no injection needed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelCapability:
    """Capabilities and governance quality for a model."""

    model_id: str
    provider: str
    governance_quality: str
    # "validated" (>=95%) | "recommended" (>=90%)
    # "experimental" (>=80%) | "not_recommended" (<80%)
    max_output_tokens: int
    supports_streaming: bool
    cost_per_1k_input: float
    cost_per_1k_output: float


# Quality thresholds for governance citation fidelity
QUALITY_VALIDATED = 0.95
QUALITY_RECOMMENDED = 0.90
QUALITY_EXPERIMENTAL = 0.80


def quality_rating(score: float) -> str:
    """Map citation fidelity score to quality rating."""
    if score >= QUALITY_VALIDATED:
        return "validated"
    if score >= QUALITY_RECOMMENDED:
        return "recommended"
    if score >= QUALITY_EXPERIMENTAL:
        return "experimental"
    return "not_recommended"


MODEL_REGISTRY: dict[str, ModelCapability] = {
    "anthropic:claude-sonnet-4-6": ModelCapability(
        model_id="anthropic:claude-sonnet-4-6",
        provider="anthropic",
        governance_quality="validated",
        max_output_tokens=8192,
        supports_streaming=True,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    "anthropic:claude-haiku-4-5": ModelCapability(
        model_id="anthropic:claude-haiku-4-5",
        provider="anthropic",
        governance_quality="recommended",
        max_output_tokens=8192,
        supports_streaming=True,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.005,
    ),
    "openai:gpt-4o": ModelCapability(
        model_id="openai:gpt-4o",
        provider="openai",
        governance_quality="recommended",
        max_output_tokens=4096,
        supports_streaming=True,
        cost_per_1k_input=0.0025,
        cost_per_1k_output=0.01,
    ),
}


def get_model(model_id: str) -> ModelCapability | None:
    """Look up model capabilities."""
    return MODEL_REGISTRY.get(model_id)


def list_models(
    min_quality: str = "experimental",
) -> list[ModelCapability]:
    """List models meeting minimum quality threshold."""
    order = [
        "not_recommended",
        "experimental",
        "recommended",
        "validated",
    ]
    min_idx = order.index(min_quality)
    return [
        m
        for m in MODEL_REGISTRY.values()
        if order.index(m.governance_quality) >= min_idx
    ]


def estimate_cost_per_query(
    model_id: str,
    input_tokens: int = 3000,
    output_tokens: int = 1500,
) -> float:
    """Estimate cost for a single governance query."""
    model = MODEL_REGISTRY.get(model_id)
    if model is None:
        return 0.0
    return (
        (input_tokens / 1000) * model.cost_per_1k_input
        + (output_tokens / 1000) * model.cost_per_1k_output
    )
