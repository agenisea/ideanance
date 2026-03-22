"""Tests for promptfoo result importer — PLAN37."""

from modules.evaluation.result_importer import (
    PromptfooResultImporter,
)


def _make_results_json(pass_count: int = 8, fail_count: int = 2) -> dict:
    results = []
    for i in range(pass_count):
        results.append({
            "success": True,
            "score": 1.0,
            "metadata": {
                "ideanance_criterion_id": f"eval-{i:03d}",
                "governance_wiring": f"nist-govern-{i}",
            },
        })
    for i in range(fail_count):
        results.append({
            "success": False,
            "score": 0.0,
            "error": f"Assertion failed for criterion {i}",
            "metadata": {
                "ideanance_criterion_id": f"eval-fail-{i:03d}",
            },
        })
    return {"results": results}


def test_import_computes_pass_rate():
    importer = PromptfooResultImporter()
    result = importer.import_results(_make_results_json(8, 2))
    assert result.total_tests == 10
    assert result.passed == 8
    assert result.failed == 2
    assert result.pass_rate == 0.8


def test_import_detects_threshold_breach():
    importer = PromptfooResultImporter(pass_threshold=0.90)
    result = importer.import_results(_make_results_json(8, 2))
    assert result.threshold_breached is True  # 0.8 < 0.9


def test_import_no_threshold_breach():
    importer = PromptfooResultImporter(pass_threshold=0.90)
    result = importer.import_results(_make_results_json(10, 0))
    assert result.threshold_breached is False
    assert result.pass_rate == 1.0


def test_import_preserves_criterion_ids():
    importer = PromptfooResultImporter()
    result = importer.import_results(_make_results_json(3, 1))
    ids = [r.criterion_id for r in result.criterion_results]
    assert "eval-000" in ids
    assert "eval-fail-000" in ids


def test_import_preserves_governance_wiring():
    importer = PromptfooResultImporter()
    result = importer.import_results(_make_results_json(2, 0))
    assert result.criterion_results[0].governance_wiring == "nist-govern-0"


def test_import_empty_results():
    importer = PromptfooResultImporter()
    result = importer.import_results({"results": []})
    assert result.total_tests == 0
    assert result.pass_rate == 0.0


def test_import_all_failing():
    importer = PromptfooResultImporter()
    result = importer.import_results(_make_results_json(0, 5))
    assert result.passed == 0
    assert result.failed == 5
    assert result.pass_rate == 0.0
    assert result.threshold_breached is True


def test_import_source_is_promptfoo():
    importer = PromptfooResultImporter()
    result = importer.import_results(_make_results_json(1, 0))
    assert result.source == "promptfoo"


def test_import_nested_metadata():
    """Test with metadata nested under testCase (promptfoo v2 format)."""
    results_json = {
        "results": [
            {
                "success": True,
                "score": 1.0,
                "testCase": {
                    "metadata": {
                        "ideanance_criterion_id": "eval-nested",
                        "governance_wiring": "eu-art9",
                    },
                },
            },
        ]
    }
    importer = PromptfooResultImporter()
    result = importer.import_results(results_json)
    assert result.criterion_results[0].criterion_id == "eval-nested"
    assert result.criterion_results[0].governance_wiring == "eu-art9"
