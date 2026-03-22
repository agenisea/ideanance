"""Generate promptfoo YAML config from Ideanance eval criteria.

Bidirectional integration: Ideanance eval criteria → promptfoo config.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog
import yaml

log = structlog.get_logger()

# Mapping from Ideanance metric types to promptfoo assertion types
ASSERTION_TYPE_MAP: dict[str, str] = {
    "field_present": "contains",
    "governance_accuracy": "llm-rubric",
    "citation_fidelity": "not-contains",
    "score_threshold": "javascript",
    "json_valid": "is-json",
    "length_check": "javascript",
    "presence": "contains",
    "accuracy": "llm-rubric",
    "format": "is-json",
    "threshold": "javascript",
}

DEFAULT_PROVIDER = "anthropic:messages:claude-sonnet-4-6"


@dataclass
class PromptfooTest:
    """A single promptfoo test case."""

    description: str
    vars: dict[str, str] = field(default_factory=dict)
    assertions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class EvalCriterionInput:
    """Input eval criterion for export."""

    criterion_id: str
    description: str
    metric: str
    threshold: str
    governance_wiring: str = ""
    framework: str = ""


class PromptfooExporter:
    """Generate promptfoo YAML config from eval criteria.

    Stateless — operates on provided criteria, no DB dependency.
    """

    def export_config(
        self,
        project_name: str,
        criteria: list[EvalCriterionInput],
        provider: str = DEFAULT_PROVIDER,
    ) -> str:
        """Generate a complete promptfooconfig.yaml."""
        log.info(
            "promptfoo.exporting",
            project=project_name,
            criteria_count=len(criteria),
        )
        tests = []
        for criterion in criteria:
            test = self._criterion_to_test(criterion)
            tests.append(test)

        config: dict[str, Any] = {
            "description": f"Governance eval criteria — {project_name}",
            "providers": [
                {
                    "id": provider,
                    "config": {"temperature": 0},
                }
            ],
            "tests": [
                {
                    "description": t.description,
                    **({"vars": t.vars} if t.vars else {}),
                    "assert": t.assertions,
                    "metadata": t.metadata,
                }
                for t in tests
            ],
        }

        return yaml.dump(
            config, default_flow_style=False, sort_keys=False
        )

    def _criterion_to_test(
        self, criterion: EvalCriterionInput
    ) -> PromptfooTest:
        """Convert an Ideanance eval criterion to a promptfoo test."""
        assertion = self._map_assertion(criterion)
        description = criterion.description
        if criterion.governance_wiring:
            description = f"[{criterion.governance_wiring}] {description}"

        return PromptfooTest(
            description=description,
            vars={"design": "{{design_content}}"},
            assertions=[assertion],
            metadata={
                "ideanance_criterion_id": criterion.criterion_id,
                **(
                    {"governance_wiring": criterion.governance_wiring}
                    if criterion.governance_wiring
                    else {}
                ),
            },
        )

    def _map_assertion(
        self, criterion: EvalCriterionInput
    ) -> dict[str, Any]:
        """Map Ideanance metric to promptfoo assertion type."""
        assertion_type = ASSERTION_TYPE_MAP.get(
            criterion.metric, "llm-rubric"
        )

        if assertion_type == "contains":
            return {
                "type": "contains",
                "value": criterion.description.lower().split()[0]
                if criterion.description
                else "",
            }
        elif assertion_type == "llm-rubric":
            return {
                "type": "llm-rubric",
                "value": criterion.description,
            }
        elif assertion_type == "javascript":
            return {
                "type": "javascript",
                "value": f"output.length >= {criterion.threshold}"
                if criterion.threshold.isdigit()
                else f'output.includes("{criterion.threshold}")',
            }
        elif assertion_type == "is-json":
            return {"type": "is-json"}
        elif assertion_type == "not-contains":
            return {
                "type": "not-contains",
                "value": "fabricated",
            }
        else:
            return {
                "type": "llm-rubric",
                "value": criterion.description,
            }
