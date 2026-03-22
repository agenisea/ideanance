"""Canonical model identifiers and pricing — single source of truth."""

from dataclasses import dataclass
from enum import StrEnum


class ModelId(StrEnum):
    CLAUDE_SONNET = "anthropic:claude-sonnet-4-6"
    CLAUDE_HAIKU = "anthropic:claude-haiku-4-5"
    CLAUDE_OPUS = "anthropic:claude-opus-4-6"
    GPT_4O = "openai:gpt-4o"
    EMBEDDING_SMALL = "openai:text-embedding-3-small"


@dataclass(frozen=True)
class ModelPricing:
    prompt_per_1k: float
    completion_per_1k: float


MODEL_PRICING: dict[str, ModelPricing] = {
    ModelId.CLAUDE_SONNET: ModelPricing(0.003, 0.015),
    ModelId.CLAUDE_HAIKU: ModelPricing(0.001, 0.005),
    ModelId.CLAUDE_OPUS: ModelPricing(0.005, 0.025),
    ModelId.GPT_4O: ModelPricing(0.0025, 0.01),
    ModelId.EMBEDDING_SMALL: ModelPricing(0.00002, 0.0),
}
