"""Governance framework plugin discovery via entry_points."""

from __future__ import annotations

from importlib.metadata import entry_points

from modules.governance.plugins.base import PolicyRuleProvider


def discover_plugins() -> dict[str, PolicyRuleProvider]:
    """Discover governance framework plugins via entry_points."""
    plugins: dict[str, PolicyRuleProvider] = {}
    eps = entry_points(group="ideanance.governance")
    for ep in eps:
        plugin = ep.load()()
        plugins[plugin.framework] = plugin
    return plugins
