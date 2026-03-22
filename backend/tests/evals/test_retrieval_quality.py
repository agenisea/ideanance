"""Structural validation of the retrieval quality golden dataset.

Similar to test_boundary.py — validates that the golden dataset YAML
is well-formed and references valid policy section IDs. No LLM calls.
"""

from pathlib import Path

import yaml

from ideanance.modules.governance.constants import (
    NIST_GOVERN_1_1,
    NIST_GOVERN_1_2,
    NIST_GOVERN_1_3,
    NIST_GOVERN_1_4,
    NIST_MANAGE_2_1,
    NIST_MAP_1_1,
    NIST_MAP_1_5,
    NIST_MEASURE_2_5,
)

GOLDEN_PATH = (
    Path(__file__).parent / "golden_datasets" / "retrieval_quality.yml"
)

# All known NIST AI RMF section IDs from constants
VALID_NIST_SECTIONS = {
    NIST_GOVERN_1_1,
    NIST_GOVERN_1_2,
    NIST_GOVERN_1_3,
    NIST_GOVERN_1_4,
    NIST_MAP_1_1,
    NIST_MAP_1_5,
    NIST_MANAGE_2_1,
    NIST_MEASURE_2_5,
}


def _load_cases() -> list[dict]:
    data = yaml.safe_load(GOLDEN_PATH.read_text())
    return data["cases"]


def test_all_cases_have_required_fields():
    """Every case needs name, query, frameworks, expected_relevant_sections."""
    cases = _load_cases()
    for case in cases:
        assert "name" in case, f"Case missing 'name': {case}"
        assert "query" in case, f"Case {case['name']} missing 'query'"
        assert "frameworks" in case, (
            f"Case {case['name']} missing 'frameworks'"
        )
        assert "expected_relevant_sections" in case, (
            f"Case {case['name']} missing 'expected_relevant_sections'"
        )


def test_frameworks_are_lists():
    """Frameworks must be a list of strings."""
    cases = _load_cases()
    for case in cases:
        assert isinstance(case["frameworks"], list), (
            f"Case {case['name']}: 'frameworks' must be a list"
        )
        for fw in case["frameworks"]:
            assert isinstance(fw, str), (
                f"Case {case['name']}: framework entry must be a string"
            )


def test_expected_sections_reference_valid_ids():
    """All expected_relevant_sections must be known NIST policy IDs."""
    cases = _load_cases()
    for case in cases:
        for section_id in case["expected_relevant_sections"]:
            assert section_id in VALID_NIST_SECTIONS, (
                f"Case {case['name']}: unknown section '{section_id}'. "
                f"Valid: {sorted(VALID_NIST_SECTIONS)}"
            )


def test_at_least_three_retrieval_cases():
    """Golden dataset should have reasonable coverage."""
    cases = _load_cases()
    assert len(cases) >= 3


def test_each_case_has_at_least_one_expected_section():
    """Each case should expect at least one relevant section."""
    cases = _load_cases()
    for case in cases:
        assert len(case["expected_relevant_sections"]) >= 1, (
            f"Case {case['name']}: must expect at least one section"
        )
