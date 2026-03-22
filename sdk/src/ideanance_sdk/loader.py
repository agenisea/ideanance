"""YAML governance policy loader with anti-corruption layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ideanance_sdk.engine import PolicyRule


@dataclass
class LoadedPolicy:
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


def translate_policy(raw: dict[str, Any]) -> LoadedPolicy:
    """Anti-corruption layer — shields domain from YAML format.

    If the YAML policy schema changes, only this function
    changes. Domain objects remain untouched.
    """
    policy = raw.get("policy", raw)

    rules = []
    for rd in policy.get("rules", []):
        params = {
            k: v
            for k, v in rd.items()
            if k not in ("check", "target", "message")
        }
        rules.append(
            PolicyRule(
                check=rd["check"],
                target=rd["target"],
                message=rd["message"],
                params=params if params else None,
            )
        )

    return LoadedPolicy(
        id=policy["id"],
        framework=policy["framework"],
        category=policy["category"].lower(),
        subcategory=policy.get("subcategory", ""),
        name=policy["name"],
        description=policy.get("description", ""),
        severity=policy.get("severity", "warning"),
        applies_to=policy.get("applies_to", []),
        rules=rules,
        remediation=policy.get("remediation", {}),
    )


def load_policy_file(path: Path) -> LoadedPolicy:
    """Load a policy from YAML with error handling."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        return translate_policy(data)
    except KeyError as e:
        raise ValueError(
            f"Missing required field {e} in {path}"
        ) from e
    except yaml.YAMLError as e:
        raise ValueError(
            f"Invalid YAML in {path}: {e}"
        ) from e


def load_framework_policies(
    directory: Path,
) -> list[LoadedPolicy]:
    policies = []
    for path in sorted(directory.rglob("*.yml")):
        if path.name.startswith("_"):
            continue
        policies.append(load_policy_file(path))
    return policies
