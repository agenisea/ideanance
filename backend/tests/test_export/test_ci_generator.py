"""Tests for CI workflow generator — PLAN38."""

from ideanance.modules.export.ci_generator import CIWorkflowGenerator


def test_generates_valid_yaml():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test Project")
    assert "name: Governance Check" in workflow
    assert "on:" in workflow
    assert "pull_request:" in workflow


def test_includes_project_name():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Customer Support Agent")
    assert "Customer Support Agent" in workflow


def test_includes_framework_label():
    gen = CIWorkflowGenerator()
    workflow = gen.generate(
        "Test", frameworks=["NIST AI RMF", "EU AI Act"]
    )
    assert "NIST AI RMF" in workflow
    assert "EU AI Act" in workflow


def test_includes_checkout_step():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test")
    assert "actions/checkout@v4" in workflow


def test_includes_node_setup():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test")
    assert "actions/setup-node@v4" in workflow


def test_includes_promptfoo_eval():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test")
    assert "npx promptfoo@latest eval" in workflow


def test_includes_api_key_secret():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test")
    assert "ANTHROPIC_API_KEY" in workflow


def test_custom_eval_criteria_path():
    gen = CIWorkflowGenerator()
    workflow = gen.generate(
        "Test", eval_criteria_path="custom/path.yml"
    )
    assert "custom/path.yml" in workflow


def test_custom_pass_threshold():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test", pass_threshold=95)
    assert "95" in workflow


def test_default_pass_threshold():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test")
    assert "90" in workflow


def test_runs_on_ubuntu():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test")
    assert "ubuntu-latest" in workflow


def test_governance_check_step():
    gen = CIWorkflowGenerator()
    workflow = gen.generate("Test")
    assert "Check governance pass rate" in workflow
