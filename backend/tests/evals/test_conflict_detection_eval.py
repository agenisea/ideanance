"""Conflict detection eval against golden dataset — PLAN40."""

from pathlib import Path

import pytest
import yaml

from ideanance.modules.governance.conflict_detection import ConflictDetector
from ideanance.modules.governance.cross_mapping import CrossFrameworkMapper
from ideanance.modules.governance.loader import load_framework_policies

GOLDEN_DATASET = (
    Path(__file__).parent / "golden_datasets" / "conflict_detection.yml"
)
CROSS_MAPPINGS_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "cross_mappings"
)
NIST_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "nist-ai-rmf"
)
EU_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "eu-ai-act"
)


def _load_golden_cases() -> list:
    with open(GOLDEN_DATASET) as f:
        return yaml.safe_load(f)["cases"]


def _get_all_policies():
    nist = load_framework_policies(NIST_DIR)
    eu = load_framework_policies(EU_DIR)
    return {p.id: p for p in nist + eu}


@pytest.fixture(scope="module")
def all_policies():
    return _get_all_policies()


@pytest.fixture(scope="module")
def detector():
    mapper = CrossFrameworkMapper.from_yaml_dir(CROSS_MAPPINGS_DIR)
    return ConflictDetector(mapper=mapper)


@pytest.mark.parametrize("case", _load_golden_cases(), ids=lambda c: c["name"])
def test_conflict_detection_golden(case, detector, all_policies):
    policy_ids = case.get("policies", [])
    policies = [all_policies[pid] for pid in policy_ids if pid in all_policies]

    conflicts = detector.detect(policies)
    min_expected = case.get("expected_conflicts_min", 0)

    assert len(conflicts) >= min_expected, (
        f"Expected at least {min_expected} conflicts, got {len(conflicts)}"
    )
