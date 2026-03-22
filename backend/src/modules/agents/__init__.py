"""Agent constants: IDs, model names, token budgets, timeouts."""

from core.handoff.limits import (
    EXPORT_HANDOFF_TIMEOUT_MS,
    HANDOFF_TIMEOUT_MS,
    ROUTER_TIMEOUT_MS,
)
from core.model_catalog import ModelId

AGENT_IDS = {
    "QUERY_ROUTER": "query_router",
    "DESIGN_ADVISOR": "design_advisor",
    "POLICY_INTERPRETER": "policy_interpreter",
    "EVAL_GENERATOR": "eval_generator",
    "EXPORT_FORMATTER": "export_formatter",
}

MODELS = {
    "ROUTING": ModelId.CLAUDE_HAIKU,
    "DOMAIN": ModelId.CLAUDE_SONNET,
    "FALLBACK": ModelId.GPT_4O,
    "DEGRADED": ModelId.CLAUDE_HAIKU,
    "EMBEDDING": ModelId.EMBEDDING_SMALL,
}

TOKEN_BUDGETS = {
    "query_router": {"in": 500, "out": 200},
    "design_advisor": {"in": 3000, "out": 2000},
    "policy_interpreter": {"in": 4000, "out": 1500},
    "eval_generator": {"in": 3000, "out": 2000},
    "export_formatter": {"in": 4000, "out": 3000},
}

POLICY_SEARCH_LIMIT = 5  # Max policy results returned by agent tools

TIMEOUTS_MS = {
    "query_router": ROUTER_TIMEOUT_MS,
    "design_advisor": HANDOFF_TIMEOUT_MS,
    "policy_interpreter": HANDOFF_TIMEOUT_MS,
    "eval_generator": HANDOFF_TIMEOUT_MS,
    "export_formatter": EXPORT_HANDOFF_TIMEOUT_MS,
    "GOVERNANCE_FILTER": 100,
}
