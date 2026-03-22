"""SSE tool status templates for human-readable progress.

Human-readable progress messages per tool.
"""

from __future__ import annotations

TOOL_STATUS_TEMPLATES: dict[str, str] = {
    "search_governance_policies": (
        "Searching governance policies for '{query}'..."
    ),
    "evaluate_design": (
        "Evaluating design against {framework}..."
    ),
    "generate_eval_criteria": (
        "Generating evaluation criteria..."
    ),
    "check_policy_compliance": (
        "Checking policy compliance..."
    ),
    "export_handoff": (
        "Preparing handoff package..."
    ),
    "lookup_cross_mappings": (
        "Looking up cross-framework mappings..."
    ),
}


def get_tool_status(
    tool_name: str, **kwargs: str
) -> str:
    """Get human-readable status for a tool call."""
    template = TOOL_STATUS_TEMPLATES.get(tool_name)
    if template is None:
        return f"Running {tool_name}..."
    try:
        return template.format(**kwargs)
    except KeyError:
        return template.split("'")[0] + "..."
