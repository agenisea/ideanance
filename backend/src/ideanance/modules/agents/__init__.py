"""Agent constants: IDs, model names, token budgets, timeouts."""

AGENT_IDS = {
    "QUERY_ROUTER": "query_router",
    "DESIGN_ADVISOR": "design_advisor",
    "POLICY_INTERPRETER": "policy_interpreter",
    "EVAL_GENERATOR": "eval_generator",
    "EXPORT_FORMATTER": "export_formatter",
}

MODELS = {
    "ROUTING": "anthropic:claude-haiku-4-5",
    "DOMAIN": "anthropic:claude-sonnet-4-6",
    "FALLBACK": "openai:gpt-4o",
    "DEGRADED": "anthropic:claude-haiku-4-5",
    "EMBEDDING": "text-embedding-3-small",
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
    "query_router": 500,
    "design_advisor": 5000,
    "policy_interpreter": 5000,
    "eval_generator": 5000,
    "export_formatter": 8000,
    "GOVERNANCE_FILTER": 100,
}
