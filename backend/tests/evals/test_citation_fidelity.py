"""Citation fidelity tests (deterministic).

Verifies that all section IDs referenced in golden datasets
actually exist in the loaded NIST AI RMF policy set.
"""

from pathlib import Path

import pytest
import yaml

from modules.governance.loader import load_all_policies

GOLDEN_PATH = Path(__file__).parent / "golden_datasets" / "citation_fidelity.yml"


@pytest.fixture
def valid_section_ids():
    policies = load_all_policies()
    return {p.id for p in policies}


def _load_citation_cases():
    data = yaml.safe_load(GOLDEN_PATH.read_text())
    return data["cases"]


@pytest.mark.parametrize("case", _load_citation_cases(), ids=lambda c: c["name"])
def test_expected_sections_exist(case, valid_section_ids):
    """All expected sections in golden dataset must exist in policy set."""
    for section_id in case["expected_sections"]:
        assert section_id in valid_section_ids, (
            f"Expected section {section_id} not found in loaded policies. "
            f"Available: {sorted(valid_section_ids)}"
        )


@pytest.mark.parametrize("case", _load_citation_cases(), ids=lambda c: c["name"])
def test_invalid_sections_do_not_exist(case, valid_section_ids):
    """Invalid sections in golden dataset must NOT exist in policy set."""
    for section_id in case.get("invalid_sections", []):
        assert section_id not in valid_section_ids, (
            f"Section {section_id} should not exist but was found"
        )
