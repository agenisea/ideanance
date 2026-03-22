"""Tests for promptfoo exporter — PLAN37."""

import yaml

from modules.export.promptfoo_exporter import (
    ASSERTION_TYPE_MAP,
    EvalCriterionInput,
    PromptfooExporter,
)


def _make_criteria() -> list[EvalCriterionInput]:
    return [
        EvalCriterionInput(
            criterion_id="eval-purpose-001",
            description="Purpose statement is present",
            metric="field_present",
            threshold="boolean: true",
            governance_wiring="nist-govern-1.1",
            framework="NIST AI RMF",
        ),
        EvalCriterionInput(
            criterion_id="eval-risk-001",
            description="Risk assessment documented",
            metric="governance_accuracy",
            threshold="",
            governance_wiring="nist-map-1.5",
            framework="NIST AI RMF",
        ),
        EvalCriterionInput(
            criterion_id="eval-format-001",
            description="Output is valid JSON",
            metric="json_valid",
            threshold="",
        ),
    ]


def test_export_generates_valid_yaml():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Test Project", _make_criteria())
    config = yaml.safe_load(config_str)
    assert config is not None
    assert "tests" in config
    assert "providers" in config


def test_export_includes_all_criteria():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Test Project", _make_criteria())
    config = yaml.safe_load(config_str)
    assert len(config["tests"]) == 3


def test_export_includes_governance_provenance():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Test Project", _make_criteria())
    config = yaml.safe_load(config_str)
    test = config["tests"][0]
    assert test["metadata"]["ideanance_criterion_id"] == "eval-purpose-001"
    assert test["metadata"]["governance_wiring"] == "nist-govern-1.1"


def test_export_description_includes_wiring():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Test Project", _make_criteria())
    config = yaml.safe_load(config_str)
    assert "[nist-govern-1.1]" in config["tests"][0]["description"]


def test_export_maps_field_present_to_contains():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Test Project", _make_criteria())
    config = yaml.safe_load(config_str)
    assert config["tests"][0]["assert"][0]["type"] == "contains"


def test_export_maps_accuracy_to_llm_rubric():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Test Project", _make_criteria())
    config = yaml.safe_load(config_str)
    assert config["tests"][1]["assert"][0]["type"] == "llm-rubric"


def test_export_maps_json_valid_to_is_json():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Test Project", _make_criteria())
    config = yaml.safe_load(config_str)
    assert config["tests"][2]["assert"][0]["type"] == "is-json"


def test_export_uses_custom_provider():
    exporter = PromptfooExporter()
    config_str = exporter.export_config(
        "Test Project",
        _make_criteria(),
        provider="openai:gpt-4o",
    )
    config = yaml.safe_load(config_str)
    assert config["providers"][0]["id"] == "openai:gpt-4o"


def test_export_empty_criteria():
    exporter = PromptfooExporter()
    config_str = exporter.export_config("Empty Project", [])
    config = yaml.safe_load(config_str)
    assert config["tests"] == []


def test_assertion_type_map_coverage():
    """All mapped types should produce valid promptfoo assertions."""
    expected_types = {
        "contains", "llm-rubric", "not-contains",
        "javascript", "is-json",
    }
    actual_types = set(ASSERTION_TYPE_MAP.values())
    assert actual_types.issubset(expected_types)
