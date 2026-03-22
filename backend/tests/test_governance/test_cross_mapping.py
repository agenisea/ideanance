"""Tests for cross-framework mapping — PLAN33."""

from pathlib import Path

from ideanance.modules.governance.constants import (
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_NIST_AI_RMF,
)
from ideanance.modules.governance.cross_mapping import CrossFrameworkMapper

CROSS_MAPPINGS_DIR = (
    Path(__file__).resolve().parents[3] / "governance-policies" / "cross_mappings"
)


def test_load_cross_mappings_from_yaml():
    mapper = CrossFrameworkMapper.from_yaml_dir(CROSS_MAPPINGS_DIR)
    assert mapper.mapping_count >= 5


def test_get_mappings_between_nist_and_eu():
    mapper = CrossFrameworkMapper.from_yaml_dir(CROSS_MAPPINGS_DIR)
    mappings = mapper.get_mappings(FRAMEWORK_NIST_AI_RMF, FRAMEWORK_EU_AI_ACT)
    assert len(mappings) >= 5
    # All mappings should be between these frameworks
    for m in mappings:
        assert {m.source_framework, m.target_framework} == {
            FRAMEWORK_NIST_AI_RMF,
            FRAMEWORK_EU_AI_ACT,
        }


def test_get_mappings_bidirectional():
    mapper = CrossFrameworkMapper.from_yaml_dir(CROSS_MAPPINGS_DIR)
    # Should work regardless of argument order
    ab = mapper.get_mappings(FRAMEWORK_NIST_AI_RMF, FRAMEWORK_EU_AI_ACT)
    ba = mapper.get_mappings(FRAMEWORK_EU_AI_ACT, FRAMEWORK_NIST_AI_RMF)
    assert len(ab) == len(ba)


def test_get_mappings_unknown_frameworks():
    mapper = CrossFrameworkMapper.from_yaml_dir(CROSS_MAPPINGS_DIR)
    mappings = mapper.get_mappings("Unknown A", "Unknown B")
    assert len(mappings) == 0


def test_cross_mappings_have_relationships():
    mapper = CrossFrameworkMapper.from_yaml_dir(CROSS_MAPPINGS_DIR)
    all_mappings = mapper.get_all_mappings()
    for m in all_mappings:
        assert m.relationship in ("overlap", "equivalent", "subset", "partial")


def test_empty_mapper():
    mapper = CrossFrameworkMapper()
    assert mapper.mapping_count == 0
    assert mapper.get_mappings("A", "B") == []


def test_missing_directory():
    mapper = CrossFrameworkMapper.from_yaml_dir(Path("/nonexistent"))
    assert mapper.mapping_count == 0
