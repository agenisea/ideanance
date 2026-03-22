"""Tests for security pipeline + PII detection — PLAN53."""

from core.security.pii_detection import (
    PIIDetector,
)
from core.security.pipeline import (
    SecurityCheckResult,
    SecurityPipeline,
    SecurityPipelineResult,
)

# --- Mock guards ---


class PassGuard:
    def check(self, content, context):
        return SecurityCheckResult(
            passed=True, guard="pass_guard"
        )


class BlockGuard:
    def check(self, content, context):
        return SecurityCheckResult(
            passed=False,
            guard="block_guard",
            reason="blocked",
            severity="block",
        )


class WarnGuard:
    def check(self, content, context):
        return SecurityCheckResult(
            passed=False,
            guard="warn_guard",
            reason="warned",
            severity="warning",
        )


# --- Pipeline tests ---


def test_pipeline_all_pass():
    pipeline = SecurityPipeline([PassGuard()])
    result = pipeline.run("safe content")
    assert result.passed is True
    assert len(result.checks) == 1


def test_pipeline_block_stops_chain():
    pipeline = SecurityPipeline(
        [PassGuard(), BlockGuard(), PassGuard()]
    )
    result = pipeline.run("bad content")
    assert result.passed is False
    # Should stop at block guard — 2 checks, not 3
    assert len(result.checks) == 2


def test_pipeline_warn_does_not_stop():
    pipeline = SecurityPipeline(
        [WarnGuard(), PassGuard()]
    )
    result = pipeline.run("content")
    assert result.passed is False  # warn fails
    assert len(result.checks) == 2  # continues


def test_pipeline_empty_guards():
    pipeline = SecurityPipeline([])
    result = pipeline.run("anything")
    assert result.passed is True


def test_pipeline_result_is_dataclass():
    result = SecurityPipelineResult(
        passed=True, checks=[]
    )
    assert result.passed is True


# --- PII Detection tests ---


def test_pii_detects_email():
    d = PIIDetector()
    findings = d.detect("Contact john@example.com")
    assert len(findings) == 1
    assert findings[0].pii_type == "Email Address"


def test_pii_detects_ssn():
    d = PIIDetector()
    findings = d.detect("SSN: 123-45-6789")
    assert len(findings) >= 1
    assert any(f.pii_type == "SSN" for f in findings)


def test_pii_detects_credit_card():
    d = PIIDetector()
    findings = d.detect("Card: 4111 1111 1111 1111")
    assert any(
        f.pii_type == "Credit Card" for f in findings
    )


def test_pii_clean_content():
    d = PIIDetector()
    findings = d.detect(
        "This is a governance policy with no PII."
    )
    assert len(findings) == 0


def test_pii_allowlist_suppresses_governance_ids():
    """EU regulation numbers should not trigger Gov ID."""
    d = PIIDetector()
    content = "See EU AI Act regulation EU202401689"
    findings = d.detect(content)
    # Should be suppressed by allowlist
    gov_ids = [
        f for f in findings if f.pii_type == "Government ID"
    ]
    assert len(gov_ids) == 0


def test_pii_allowlist_suppresses_nist_refs():
    d = PIIDetector()
    content = "Per nist-govern-1.1 requirements"
    findings = d.detect(content)
    assert len(findings) == 0


def test_pii_has_pii_convenience():
    d = PIIDetector()
    assert d.has_pii("Email: test@test.com") is True
    assert d.has_pii("No PII here") is False
