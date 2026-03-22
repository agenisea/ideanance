"""Boundary tests (deterministic).

Validates the golden dataset structure and ensures boundary
test cases are well-formed. The actual rejection/redirection
behavior is tested at the agent level with TestModel.
"""

from pathlib import Path

import yaml

GOLDEN_PATH = Path(__file__).parent / "golden_datasets" / "boundary_testing.yml"

VALID_BEHAVIORS = {"reject", "redirect", "answer"}


def _load_boundary_cases():
    data = yaml.safe_load(GOLDEN_PATH.read_text())
    return data["cases"]


def test_all_cases_have_required_fields():
    """Every boundary case must have name, prompt, and expected_behavior."""
    cases = _load_boundary_cases()
    for case in cases:
        assert "name" in case, f"Case missing 'name': {case}"
        assert "prompt" in case, f"Case {case['name']} missing 'prompt'"
        assert "expected_behavior" in case, (
            f"Case {case['name']} missing 'expected_behavior'"
        )


def test_all_behaviors_are_valid():
    """expected_behavior must be one of: reject, redirect, answer."""
    cases = _load_boundary_cases()
    for case in cases:
        assert case["expected_behavior"] in VALID_BEHAVIORS, (
            f"Case {case['name']}: invalid behavior '{case['expected_behavior']}'"
        )


def test_at_least_five_boundary_cases():
    """Golden dataset should have comprehensive coverage."""
    cases = _load_boundary_cases()
    assert len(cases) >= 5


def test_has_rejection_cases():
    """Must include at least one rejection case."""
    cases = _load_boundary_cases()
    rejects = [c for c in cases if c["expected_behavior"] == "reject"]
    assert len(rejects) >= 1


def test_has_normal_case():
    """Must include at least one normal (answer) case for balance."""
    cases = _load_boundary_cases()
    answers = [c for c in cases if c["expected_behavior"] == "answer"]
    assert len(answers) >= 1
