"""YAML governance policy loader. Uses yaml.safe_load() exclusively."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from modules.governance.engine import PolicyRule


@dataclass
class EvalSuggestion:
    """A suggested eval criterion from a governance policy."""

    criterion: str
    metric: str
    threshold: str


@dataclass
class LoadedPolicy:
    """A parsed governance policy from YAML."""

    id: str
    framework: str
    category: str
    subcategory: str
    name: str
    description: str
    severity: str
    applies_to: list[str]
    rules: list[PolicyRule]
    remediation: dict = field(default_factory=dict)
    eval_suggestions: list[EvalSuggestion] = field(default_factory=list)


def load_policy_file(path: Path) -> LoadedPolicy:
    """Load a single governance policy from a YAML file.

    Delegates to GovernancePolicyTranslator (anti-corruption
    layer) to shield domain from external YAML changes.
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    from modules.ingestion.translators import (
        translator,
    )

    return translator.translate(data)


def load_framework_policies(directory: Path) -> list[LoadedPolicy]:
    """Load all policy YAML files from a directory, recursing subdirectories."""
    policies = []
    for path in sorted(directory.rglob("*.yml")):
        if path.name.startswith("_"):
            continue  # Skip metadata files
        policies.append(load_policy_file(path))
    return policies


# Root of governance-policies relative to this file
_GOVERNANCE_ROOT = (
    Path(__file__).parent.parent.parent.parent.parent
    / "governance-policies"
)


def load_all_policies() -> list[LoadedPolicy]:
    """Load all governance policies from the governance-policies directory."""
    policies: list[LoadedPolicy] = []
    if _GOVERNANCE_ROOT.exists():
        for framework_dir in sorted(_GOVERNANCE_ROOT.iterdir()):
            if framework_dir.is_dir() and not framework_dir.name.startswith("_"):
                if framework_dir.name in ("templates", "cross_mappings"):
                    continue
                policies.extend(load_framework_policies(framework_dir))
    return policies
