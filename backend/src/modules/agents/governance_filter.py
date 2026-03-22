"""Deterministic governance filter — post-processing on ALL agent output.

No LLM calls. Budget: <100ms execution time.
Validates citations, checks schema completeness, applies conflict resolution,
annotates output with governance metadata.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from modules.agents.base import AgentRunMetadata
from modules.governance.constants import (
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARN,
)

# Policy ID for schema completeness checks
POLICY_ID_SCHEMA_CHECK = "schema"


class GovernanceCheckResult(BaseModel):
    """Result of a single governance policy check."""

    policy_id: str
    status: str = Field(description="pass | warn | fail")
    message: str


class GovernanceFilterOutput(BaseModel):
    """Annotation applied to every agent output before delivery."""

    check_results: list[GovernanceCheckResult]
    compliance_score: float = Field(ge=0.0, le=1.0)
    warnings: list[str]
    passed: bool
    invalid_citations: list[str]


class GovernanceFilter:
    """Deterministic governance filter — no LLM calls.

    Applied as post-processing on all domain agent output.
    """

    def __init__(
        self,
        active_policies: list[dict],
        framework_sections: set[str] | None = None,
    ) -> None:
        self.active_policies = active_policies
        self.framework_sections = framework_sections or set()

    def check(self, agent_output: BaseModel) -> GovernanceFilterOutput:
        """Run governance checks against agent output."""
        results: list[GovernanceCheckResult] = []
        warnings: list[str] = []
        invalid_citations: list[str] = []

        # Validate citations if output has them
        citations = self._extract_citations(agent_output)
        if citations:
            invalid = self.validate_citations(citations)
            invalid_citations.extend(invalid)
            if invalid:
                warnings.append(
                    f"Invalid citations: {', '.join(invalid)}"
                )

        # Check schema completeness
        missing = self.check_schema_completeness(agent_output)
        for field_name in missing:
            results.append(
                GovernanceCheckResult(
                    policy_id=POLICY_ID_SCHEMA_CHECK,
                    status=STATUS_WARN,
                    message=f"Field '{field_name}' is empty or missing",
                )
            )
            warnings.append(f"Incomplete field: {field_name}")

        # Compute score
        total = len(results) if results else 1
        passed_count = sum(
            1 for r in results if r.status == STATUS_PASS
        )
        score = passed_count / total if results else 1.0

        return GovernanceFilterOutput(
            check_results=results,
            compliance_score=round(score, 2),
            warnings=warnings,
            passed=len(invalid_citations) == 0 and all(
                r.status != STATUS_FAIL for r in results
            ),
            invalid_citations=invalid_citations,
        )

    def validate_citations(
        self, citations: list[dict]
    ) -> list[str]:
        """Verify cited sections exist in loaded framework data."""
        if not self.framework_sections:
            return []
        invalid = []
        for citation in citations:
            section_id = citation.get("section_id", "")
            if section_id and section_id not in self.framework_sections:
                invalid.append(section_id)
        return invalid

    def check_schema_completeness(
        self, output: BaseModel
    ) -> list[str]:
        """Return field names that are empty or missing."""
        missing = []
        for field_name, value in output.model_dump().items():
            is_empty = (
                (isinstance(value, str) and value == "")
                or (isinstance(value, list) and len(value) == 0)
            )
            if is_empty:
                missing.append(field_name)
        return missing

    def add_degradation_warning(
        self, metadata: AgentRunMetadata
    ) -> str | None:
        """If agent ran on fallback model, return warning text."""
        if metadata.from_fallback:
            return (
                "Running in simplified mode — governance analysis "
                "may be less thorough."
            )
        return None

    def _extract_citations(
        self, output: BaseModel
    ) -> list[dict]:
        """Extract citation-like objects from agent output."""
        citations = []
        data = output.model_dump()
        for key, value in data.items():
            if "citation" in key.lower() or "reference" in key.lower():
                if isinstance(value, list):
                    citations.extend(
                        v for v in value if isinstance(v, dict)
                    )
                elif isinstance(value, dict):
                    citations.append(value)
        return citations
