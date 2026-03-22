"""Tests for custom governance framework authoring — PLAN34."""

import pytest

from ideanance.modules.governance.custom_framework import (
    CustomFrameworkService,
    YamlValidationError,
)
from ideanance.modules.governance.engine import GovernanceEngine

VALID_POLICY_YAML = """\
policy:
  id: "custom-data-retention"
  framework: "Internal Policy"
  category: "data"
  name: "Data Retention Policy"
  description: "Data must be retained for minimum period"
  severity: "required"
  applies_to: ["agent"]
  rules:
    - check: "field_present"
      target: "design.data_retention_policy"
      message: "Must define a data retention policy"
    - check: "field_min_length"
      target: "design.data_retention_policy"
      min_length: 20
      message: "Data retention policy must be substantive"
  remediation:
    guidance: "Define data retention periods and procedures"
  eval_suggestions:
    - criterion: "Data retention policy present"
      metric: "data_retention_present"
      threshold: "boolean: true"
"""

MINIMAL_POLICY_YAML = """\
policy:
  id: "custom-minimal"
  framework: "Internal Policy"
  category: "general"
  name: "Minimal Policy"
  rules:
    - check: "field_present"
      target: "design.name"
      message: "Must have a name"
"""


def test_create_framework():
    svc = CustomFrameworkService()
    fw = svc.create_framework(
        project_id="proj-1",
        framework_id="internal-policy",
        name="Internal AI Policy",
        version="1.0.0",
        categories=["data", "security"],
    )
    assert fw.id == "internal-policy"
    assert fw.name == "Internal AI Policy"
    assert len(fw.policies) == 0


def test_create_duplicate_framework_raises():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "dup-fw", "Duplicate")
    with pytest.raises(ValueError, match="already exists"):
        svc.create_framework("proj-1", "dup-fw", "Duplicate Again")


def test_add_policy_from_valid_yaml():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "internal-policy", "Internal")
    policy = svc.add_policy_from_yaml("internal-policy", VALID_POLICY_YAML)

    assert policy.id == "custom-data-retention"
    assert policy.framework == "Internal Policy"
    assert len(policy.rules) == 2
    assert policy.rules[0].check == "field_present"
    assert len(policy.eval_suggestions) == 1


def test_add_minimal_policy():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "internal-policy", "Internal")
    policy = svc.add_policy_from_yaml("internal-policy", MINIMAL_POLICY_YAML)
    assert policy.id == "custom-minimal"
    assert len(policy.rules) == 1


def test_invalid_yaml_syntax():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    with pytest.raises(YamlValidationError, match="Invalid YAML"):
        svc.add_policy_from_yaml("fw", "{{invalid yaml")


def test_missing_policy_key():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    with pytest.raises(YamlValidationError, match="top-level 'policy'"):
        svc.add_policy_from_yaml("fw", "not_a_policy: true")


def test_missing_required_fields():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    yaml_content = """\
policy:
  id: "incomplete"
  name: "Missing fields"
"""
    with pytest.raises(YamlValidationError, match="Missing required"):
        svc.add_policy_from_yaml("fw", yaml_content)


def test_unknown_check_type():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    yaml_content = """\
policy:
  id: "bad-check"
  framework: "FW"
  category: "test"
  name: "Bad Check"
  rules:
    - check: "nonexistent_check"
      target: "design.x"
      message: "bad"
"""
    with pytest.raises(YamlValidationError, match="Unknown check type"):
        svc.add_policy_from_yaml("fw", yaml_content)


def test_no_rules_rejected():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    yaml_content = """\
policy:
  id: "no-rules"
  framework: "FW"
  category: "test"
  name: "No Rules"
  rules: []
"""
    with pytest.raises(YamlValidationError, match="at least one rule"):
        svc.add_policy_from_yaml("fw", yaml_content)


def test_duplicate_policy_id():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    svc.add_policy_from_yaml("fw", MINIMAL_POLICY_YAML)
    with pytest.raises(YamlValidationError, match="already exists"):
        svc.add_policy_from_yaml("fw", MINIMAL_POLICY_YAML)


def test_validate_framework_valid():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    svc.add_policy_from_yaml("fw", VALID_POLICY_YAML)
    result = svc.validate_framework("fw")
    assert result.valid is True
    assert result.policy_count == 1
    assert result.rule_count == 2
    assert len(result.errors) == 0


def test_validate_framework_empty():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    result = svc.validate_framework("fw")
    assert result.valid is False
    assert "no policies" in result.errors[0].lower()


def test_validate_framework_warnings():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    svc.add_policy_from_yaml("fw", MINIMAL_POLICY_YAML)
    result = svc.validate_framework("fw")
    assert result.valid is True
    assert len(result.warnings) >= 1  # Missing remediation, few rules


def test_export_framework():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW", description="Test FW")
    svc.add_policy_from_yaml("fw", VALID_POLICY_YAML)
    yaml_output = svc.export_framework_yaml("fw")
    assert "FW" in yaml_output
    assert "total_policies: 1" in yaml_output


def test_list_frameworks():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw1", "FW1")
    svc.create_framework("proj-1", "fw2", "FW2")
    svc.create_framework("proj-2", "fw3", "FW3")
    frameworks = svc.list_frameworks("proj-1")
    assert len(frameworks) == 2


def test_delete_framework():
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    svc.delete_framework("fw")
    assert svc.get_framework("fw") is None


def test_delete_nonexistent_raises():
    svc = CustomFrameworkService()
    with pytest.raises(ValueError, match="not found"):
        svc.delete_framework("nonexistent")


def test_custom_policy_evaluates_with_engine():
    """Custom policies evaluate identically to built-in ones."""
    svc = CustomFrameworkService()
    svc.create_framework("proj-1", "fw", "FW")
    policy = svc.add_policy_from_yaml("fw", VALID_POLICY_YAML)

    engine = GovernanceEngine()

    # Test passing design
    passing_design = {
        "design": {
            "data_retention_policy": (
                "Retain all data for 7 years per regulation"
            )
        }
    }
    results = engine.evaluate(passing_design, policy.rules)
    assert all(r.status == "pass" for r in results)

    # Test failing design
    failing_design = {"design": {}}
    results = engine.evaluate(failing_design, policy.rules)
    assert any(r.status == "fail" for r in results)


def test_framework_not_found_raises():
    svc = CustomFrameworkService()
    with pytest.raises(ValueError, match="not found"):
        svc.add_policy_from_yaml("nonexistent", VALID_POLICY_YAML)
