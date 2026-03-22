"""Custom governance framework service.

Enables users to create, validate, and manage custom governance frameworks
that evaluate alongside built-in ones (NIST AI RMF, EU AI Act).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml

from core.events import EventBus
from core.security.input_validation import (
    MAX_POLICY_YAML_SIZE,
)
from modules.governance.engine import GovernanceEngine, PolicyRule
from modules.governance.loader import EvalSuggestion, LoadedPolicy
from modules.templates.constants import DEFAULT_SCHEMA_VERSION

# YAML nesting depth limit (bomb defense)
MAX_YAML_DEPTH = 10

# Event types for custom framework lifecycle
EVENT_CUSTOM_FRAMEWORK_CREATED = "governance.custom_framework.created"
EVENT_CUSTOM_POLICY_ADDED = "governance.custom_framework.policy_added"

# Valid rule check types (must match GovernanceEngine.RULE_EVALUATORS)
VALID_CHECK_TYPES = frozenset(GovernanceEngine.RULE_EVALUATORS.keys())

# Required policy YAML fields
REQUIRED_POLICY_FIELDS = {"id", "framework", "category", "name", "rules"}


def _check_yaml_depth(
    obj: object, depth: int = 0, max_depth: int = MAX_YAML_DEPTH
) -> None:
    """Reject deeply nested YAML (bomb defense)."""
    if depth > max_depth:
        raise YamlValidationError(
            "YAML nesting exceeds maximum depth"
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _check_yaml_depth(v, depth + 1, max_depth)
    elif isinstance(obj, list):
        for v in obj:
            _check_yaml_depth(v, depth + 1, max_depth)


@dataclass
class CustomFramework:
    """A user-created governance framework."""

    id: str
    project_id: str
    name: str
    version: str = DEFAULT_SCHEMA_VERSION
    description: str = ""
    categories: list[str] = field(default_factory=list)
    policies: list[LoadedPolicy] = field(default_factory=list)


@dataclass
class FrameworkValidation:
    """Result of validating a custom framework."""

    valid: bool
    errors: list[str]
    warnings: list[str]
    policy_count: int
    rule_count: int


class YamlValidationError(ValueError):
    """Raised when custom YAML fails validation."""


class CustomFrameworkService:
    """Manages user-created governance frameworks.

    Validates YAML policies, manages framework lifecycle,
    and exports frameworks as shareable YAML.
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
    ) -> None:
        self._event_bus = event_bus
        self._frameworks: dict[str, CustomFramework] = {}

    def create_framework(
        self,
        project_id: str,
        framework_id: str,
        name: str,
        version: str = DEFAULT_SCHEMA_VERSION,
        description: str = "",
        categories: list[str] | None = None,
    ) -> CustomFramework:
        """Create a new custom governance framework."""
        if framework_id in self._frameworks:
            raise ValueError(f"Framework already exists: {framework_id}")

        framework = CustomFramework(
            id=framework_id,
            project_id=project_id,
            name=name,
            version=version,
            description=description,
            categories=categories or [],
        )
        self._frameworks[framework_id] = framework
        return framework

    def add_policy_from_yaml(
        self, framework_id: str, yaml_content: str
    ) -> LoadedPolicy:
        """Parse, validate, and add a policy from YAML content."""
        framework = self._get_framework(framework_id)

        # Size check
        if len(yaml_content.encode("utf-8")) > MAX_POLICY_YAML_SIZE:
            raise YamlValidationError(
                f"YAML exceeds {MAX_POLICY_YAML_SIZE} byte limit"
            )

        # Parse YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise YamlValidationError(
                f"Invalid YAML syntax: {e}"
            ) from e

        # Depth check (YAML bomb defense)
        _check_yaml_depth(data)

        if not isinstance(data, dict) or "policy" not in data:
            raise YamlValidationError(
                "YAML must contain a top-level 'policy' key"
            )

        policy_data = data["policy"]

        # Validate required fields
        missing = REQUIRED_POLICY_FIELDS - set(policy_data.keys())
        if missing:
            raise YamlValidationError(
                f"Missing required fields: {', '.join(sorted(missing))}"
            )

        # Validate rules use registered check types
        rules = []
        for rule_data in policy_data.get("rules", []):
            if "check" not in rule_data:
                raise YamlValidationError(
                    "Each rule must have a 'check' field"
                )
            if rule_data["check"] not in VALID_CHECK_TYPES:
                raise YamlValidationError(
                    f"Unknown check type: '{rule_data['check']}'. "
                    f"Valid types: {', '.join(sorted(VALID_CHECK_TYPES))}"
                )
            if "target" not in rule_data:
                raise YamlValidationError(
                    "Each rule must have a 'target' field"
                )
            if "message" not in rule_data:
                raise YamlValidationError(
                    "Each rule must have a 'message' field"
                )
            params = {
                k: v
                for k, v in rule_data.items()
                if k not in ("check", "target", "message")
            }
            rules.append(
                PolicyRule(
                    check=rule_data["check"],
                    target=rule_data["target"],
                    message=rule_data["message"],
                    params=params if params else None,
                )
            )

        if not rules:
            raise YamlValidationError("Policy must have at least one rule")

        # Parse eval suggestions
        eval_suggestions = [
            EvalSuggestion(
                criterion=s.get("criterion", ""),
                metric=s.get("metric", ""),
                threshold=s.get("threshold", ""),
            )
            for s in policy_data.get("eval_suggestions", [])
        ]

        policy = LoadedPolicy(
            id=policy_data["id"],
            framework=policy_data["framework"],
            category=policy_data["category"].lower(),
            subcategory=policy_data.get("subcategory", ""),
            name=policy_data["name"],
            description=policy_data.get("description", ""),
            severity=policy_data.get("severity", "warning"),
            applies_to=policy_data.get("applies_to", []),
            rules=rules,
            remediation=policy_data.get("remediation", {}),
            eval_suggestions=eval_suggestions,
        )

        # Check for duplicate policy ID
        if any(p.id == policy.id for p in framework.policies):
            raise YamlValidationError(
                f"Policy ID already exists: {policy.id}"
            )

        framework.policies.append(policy)
        return policy

    def validate_framework(
        self, framework_id: str
    ) -> FrameworkValidation:
        """Validate framework has sufficient policies and rules."""
        framework = self._get_framework(framework_id)

        errors: list[str] = []
        warnings: list[str] = []
        rule_count = 0

        if not framework.policies:
            errors.append("Framework has no policies")

        for policy in framework.policies:
            rule_count += len(policy.rules)
            if len(policy.rules) < 2:
                warnings.append(
                    f"Policy '{policy.id}' has fewer than 2 rules"
                )
            if not policy.remediation.get("guidance"):
                warnings.append(
                    f"Policy '{policy.id}' has no remediation guidance"
                )

        return FrameworkValidation(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            policy_count=len(framework.policies),
            rule_count=rule_count,
        )

    def export_framework_yaml(self, framework_id: str) -> str:
        """Export framework as YAML string."""
        framework = self._get_framework(framework_id)

        output: dict[str, Any] = {
            "framework": {
                "id": framework.id,
                "name": framework.name,
                "version": framework.version,
                "description": framework.description,
                "categories": framework.categories,
                "total_policies": len(framework.policies),
            }
        }
        return yaml.dump(output, default_flow_style=False, sort_keys=False)

    def get_framework(self, framework_id: str) -> CustomFramework | None:
        """Get a framework by ID."""
        return self._frameworks.get(framework_id)

    def list_frameworks(self, project_id: str) -> list[CustomFramework]:
        """List all custom frameworks for a project."""
        return [
            fw
            for fw in self._frameworks.values()
            if fw.project_id == project_id
        ]

    def delete_framework(self, framework_id: str) -> None:
        """Delete a custom framework."""
        self._get_framework(framework_id)  # Raises if not found
        del self._frameworks[framework_id]

    def _get_framework(self, framework_id: str) -> CustomFramework:
        framework = self._frameworks.get(framework_id)
        if framework is None:
            raise ValueError(f"Framework not found: {framework_id}")
        return framework
