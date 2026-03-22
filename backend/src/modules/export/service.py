"""Export service: generates structured handoff packages with governance provenance."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import UTC, datetime

import yaml

from modules.design.protocols import DesignRepo
from modules.evaluation.protocols import (
    EvalCriterionRepo,
    EvaluationRepo,
)
from modules.export.constants import EXPORT_GENERATOR, IDEANANCE_VERSION
from modules.export.schemas import (
    ExportArtifact,
    ExportPreview,
    HandoffPackage,
    ProvenanceMetadata,
)
from modules.governance.protocols import (
    GovernanceEvalWiringRepo,
    GovernancePolicyRepo,
)
from modules.workspace.protocols import ProjectRepository


class ExportService:
    def __init__(
        self,
        project_repo: ProjectRepository,
        design_repo: DesignRepo,
        policy_repo: GovernancePolicyRepo,
        wiring_repo: GovernanceEvalWiringRepo,
        eval_repo: EvaluationRepo,
        criterion_repo: EvalCriterionRepo,
    ) -> None:
        self.project_repo = project_repo
        self.design_repo = design_repo
        self.policy_repo = policy_repo
        self.wiring_repo = wiring_repo
        self.eval_repo = eval_repo
        self.criterion_repo = criterion_repo

    async def preview(self, project_id: str) -> ExportPreview:
        """Preview the handoff package without generating full content."""
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")

        policies = await self.policy_repo.list_by_project(
            project_id, enabled_only=True
        )
        wirings = await self.wiring_repo.list_by_project(project_id)
        score = len(wirings) / max(len(policies), 1)

        filenames = [
            "ai-context.yml",
            "CLAUDE.md",
            "README.md",
            "governance/active-policies.yml",
            "governance/wiring-map.json",
            "governance/governance-report.md",
            "evaluations/eval-criteria.yml",
            "_provenance.json",
        ]

        # Build ai-context.yml for preview
        ai_context = self._build_ai_context(
            project_name=project.name,
            project_id=project_id,
            score=score,
            policies=policies,
            wirings=wirings,
        )

        return ExportPreview(
            project_name=project.name,
            governance_score=round(score, 2),
            active_policy_count=len(policies),
            wiring_count=len(wirings),
            artifact_filenames=filenames,
            ai_context_yml=ai_context,
        )

    async def generate_package(self, project_id: str) -> HandoffPackage:
        """Generate the full handoff package with all artifacts."""
        project = await self.project_repo.get_by_id(project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")

        policies = await self.policy_repo.list_by_project(
            project_id, enabled_only=True
        )
        wirings = await self.wiring_repo.list_by_project(project_id)
        designs = await self.design_repo.list_by_project(project_id)
        evaluations = await self.eval_repo.list_by_project(project_id)

        # Collect criteria from all evaluations
        all_criteria = []
        for evaluation in evaluations:
            criteria = await self.criterion_repo.list_by_evaluation(
                evaluation.id
            )
            all_criteria.extend(criteria)

        score = len(wirings) / max(len(policies), 1)
        frameworks = list({p.framework for p in policies})
        now = datetime.now(UTC).isoformat()

        # Build ai-context.yml
        ai_context = self._build_ai_context(
            project_name=project.name,
            project_id=project_id,
            score=score,
            policies=policies,
            wirings=wirings,
        )

        # Build artifacts
        artifacts: list[ExportArtifact] = []

        # Active policies YAML
        policies_data = [
            {
                "policy_id": p.policy_id,
                "framework": p.framework,
                "name": p.name,
                "category": p.category,
                "severity": p.severity,
            }
            for p in policies
        ]
        policies_yml = yaml.dump(
            {"policies": policies_data}, default_flow_style=False
        )
        artifacts.append(
            ExportArtifact(
                filename="governance/active-policies.yml",
                content=policies_yml,
                checksum=self._checksum(policies_yml),
                governance_provenance=[p.policy_id for p in policies],
            )
        )

        # Wiring map JSON
        wiring_data = {
            "project_id": project_id,
            "total_wirings": len(wirings),
            "wirings": [
                {
                    "policy_id": w.policy_id,
                    "criterion_id": w.criterion_id,
                    "wiring_type": w.wiring_type,
                    "confidence": w.confidence,
                    "rationale": w.rationale,
                }
                for w in wirings
            ],
        }
        wiring_json = json.dumps(wiring_data, indent=2)
        artifacts.append(
            ExportArtifact(
                filename="governance/wiring-map.json",
                content=wiring_json,
                checksum=self._checksum(wiring_json),
                governance_provenance=[w.policy_id for w in wirings],
            )
        )

        # Governance report MD
        report = self._build_governance_report(
            project.name, score, policies, wirings
        )
        artifacts.append(
            ExportArtifact(
                filename="governance/governance-report.md",
                content=report,
                checksum=self._checksum(report),
            )
        )

        # Eval criteria YAML
        criteria_data = [
            {
                "criterion_id": c.criterion_id,
                "description": c.description,
                "metric": c.metric,
                "threshold": c.threshold,
                "priority": c.priority,
                "test_cases": c.test_cases,
            }
            for c in all_criteria
        ]
        criteria_yml = yaml.dump(
            {"criteria": criteria_data}, default_flow_style=False
        )
        artifacts.append(
            ExportArtifact(
                filename="evaluations/eval-criteria.yml",
                content=criteria_yml,
                checksum=self._checksum(criteria_yml),
            )
        )

        # Agent specs YAML
        agent_specs = [
            {
                "name": d.name,
                "design_type": d.design_type,
                "content": d.content,
            }
            for d in designs
        ]
        agents_yml = yaml.dump(
            {"agents": agent_specs}, default_flow_style=False
        )
        artifacts.append(
            ExportArtifact(
                filename="agents/agent-specs.yml",
                content=agents_yml,
                checksum=self._checksum(agents_yml),
            )
        )

        # Generated CLAUDE.md
        claude_md = self._build_claude_md(project.name, frameworks, score)
        artifacts.append(
            ExportArtifact(
                filename="CLAUDE.md",
                content=claude_md,
                checksum=self._checksum(claude_md),
            )
        )

        # README.md
        readme = self._build_readme(project.name, frameworks, score)
        artifacts.append(
            ExportArtifact(
                filename="README.md",
                content=readme,
                checksum=self._checksum(readme),
            )
        )

        # Provenance
        provenance = ProvenanceMetadata(
            exported_at=now,
            project_id=project_id,
            project_name=project.name,
            governance_frameworks=frameworks,
            governance_score_at_export=round(score, 2),
            artifact_count=len(artifacts) + 2,  # +ai-context +provenance
        )
        provenance_json = provenance.model_dump_json(indent=2)

        return HandoffPackage(
            project_name=project.name,
            project_id=project_id,
            ai_context_yml=ai_context,
            provenance_json=provenance_json,
            artifacts=artifacts,
        )

    async def download_zip(self, project_id: str) -> bytes:
        """Generate and return the handoff package as a ZIP file."""
        package = await self.generate_package(project_id)
        return self._create_zip(package)

    def _create_zip(self, package: HandoffPackage) -> bytes:
        buffer = io.BytesIO()
        prefix = f"ideanance-export-{package.project_name.lower().replace(' ', '-')}"
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{prefix}/ai-context.yml", package.ai_context_yml)
            zf.writestr(
                f"{prefix}/_provenance.json", package.provenance_json
            )
            for artifact in package.artifacts:
                zf.writestr(
                    f"{prefix}/{artifact.filename}", artifact.content
                )
        return buffer.getvalue()

    def _build_ai_context(
        self,
        project_name: str,
        project_id: str,
        score: float,
        policies: list,
        wirings: list,
    ) -> str:
        gaps = []
        wired_policy_ids = {w.policy_id for w in wirings}
        for p in policies:
            if p.policy_id not in wired_policy_ids:
                gaps.append(
                    {
                        "policy": p.policy_id,
                        "severity": "warning",
                        "message": f"{p.name} not wired to eval criteria",
                    }
                )

        data = {
            "_meta": {
                "generated_by": EXPORT_GENERATOR,
                "version": IDEANANCE_VERSION,
                "exported_at": datetime.now(UTC).isoformat(),
                "project_id": project_id,
            },
            "project": {
                "name": project_name,
                "governance_score": round(score, 2),
                "frameworks": list({p.framework for p in policies}),
            },
            "governance": {
                "status": "full" if not gaps else "partial",
                "score": round(score, 2),
                "active_policies": len(policies),
                "gaps": gaps,
                "report": "governance/governance-report.md",
            },
            "evaluations": {
                "wired_count": len(wirings),
                "coverage": round(score, 2),
                "spec": "evaluations/eval-criteria.yml",
            },
            "instructions": [
                "Read governance/governance-report.md for compliance requirements",
                "All agents must cite governance policies when making design decisions",
                "Run eval criteria from evaluations/eval-criteria.yml before deploying",
                "Address governance gaps listed above before production",
            ],
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def _build_governance_report(
        self,
        project_name: str,
        score: float,
        policies: list,
        wirings: list,
    ) -> str:
        pct = round(score * 100)
        wired_ids = {w.policy_id for w in wirings}
        lines = [
            f"# Governance Report: {project_name}",
            "",
            f"**Overall Score**: {pct}%",
            f"**Active Policies**: {len(policies)}",
            f"**Wired to Evals**: {len(wirings)}",
            "",
            "## Policy Status",
            "",
        ]
        for p in policies:
            status = "Wired" if p.policy_id in wired_ids else "Gap"
            lines.append(f"- [{status}] {p.framework} {p.policy_id}: {p.name}")

        return "\n".join(lines) + "\n"

    def _build_claude_md(
        self, project_name: str, frameworks: list[str], score: float
    ) -> str:
        return "\n".join(
            [
                f"# {project_name}",
                "",
                "## Governance Requirements",
                "",
                f"This project has governance coverage of {round(score * 100)}%.",
                f"Frameworks: {', '.join(frameworks)}",
                "",
                "Before making changes, review:",
                "- `governance/governance-report.md` for compliance status",
                "- `governance/wiring-map.json` for policy-eval mappings",
                "- `evaluations/eval-criteria.yml` for test criteria",
                "",
                "## Rules",
                "",
                "- All agent responses must cite governance policies",
                "- Run eval criteria before deploying",
                "- Address governance gaps before production",
                "",
            ]
        )

    def _build_readme(
        self, project_name: str, frameworks: list[str], score: float
    ) -> str:
        return "\n".join(
            [
                f"# {project_name} — Ideanance Handoff Package",
                "",
                "This package was generated by [Ideanance](https://github.com/ideanance/ideanance),",
                "a governance-first design workspace for agentic applications.",
                "",
                f"**Governance Score**: {round(score * 100)}%",
                f"**Frameworks**: {', '.join(frameworks)}",
                "",
                "## Using with Claude Code",
                "",
                "1. Copy this directory into your project",
                "2. Claude Code will automatically read `ai-context.yml`",
                '3. Ask Claude Code: "Review the governance requirements"',
                "4. Run eval criteria before deploying:",
                "   ```bash",
                "   npx promptfoo@latest eval -c evaluations/eval-criteria.yml",
                "   ```",
                "",
            ]
        )

    @staticmethod
    def _checksum(content: str) -> str:
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
