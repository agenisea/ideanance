"""Tests for the export handoff package service."""

import json
import zipfile
from io import BytesIO

import pytest
import yaml

from modules.design.repository import SqlDesignRepository
from modules.evaluation.repository import (
    SqlEvalCriterionRepository,
    SqlEvaluationRepository,
)
from modules.export.service import ExportService
from modules.governance.constants import (
    CATEGORY_GOVERN,
    CATEGORY_MAP,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
    NIST_MAP_1_5,
    SEVERITY_REQUIRED,
)
from modules.governance.repository import (
    SqlGovernanceEvalWiringRepository,
    SqlGovernancePolicyRepository,
)
from modules.workspace.repository import (
    SqlProjectRepository,
    SqlWorkspaceRepository,
)


@pytest.fixture
async def export_service(db):
    return ExportService(
        project_repo=SqlProjectRepository(db),
        design_repo=SqlDesignRepository(db),
        policy_repo=SqlGovernancePolicyRepository(db),
        wiring_repo=SqlGovernanceEvalWiringRepository(db),
        eval_repo=SqlEvaluationRepository(db),
        criterion_repo=SqlEvalCriterionRepository(db),
    )


@pytest.fixture
async def seeded_project(db):
    """Create a project with policies, wirings, designs, and evals."""
    ws_repo = SqlWorkspaceRepository(db)
    proj_repo = SqlProjectRepository(db)
    policy_repo = SqlGovernancePolicyRepository(db)
    wiring_repo = SqlGovernanceEvalWiringRepository(db)
    design_repo = SqlDesignRepository(db)
    eval_repo = SqlEvaluationRepository(db)
    criterion_repo = SqlEvalCriterionRepository(db)

    ws = await ws_repo.create(name="Test Workspace")
    proj = await proj_repo.create(ws.id, name="Test Agent")
    await db.flush()

    # Add policies
    p1 = await policy_repo.create(
        proj.id,
        framework=FRAMEWORK_NIST_AI_RMF,
        policy_id=NIST_GOVERN_1_1,
        name="Legal Requirements",
        category=CATEGORY_GOVERN,
        severity=SEVERITY_REQUIRED,
        rules={"checks": [{"field": "purpose", "operator": "exists"}]},
        enabled=True,
    )
    await policy_repo.create(
        proj.id,
        framework=FRAMEWORK_NIST_AI_RMF,
        policy_id=NIST_MAP_1_5,
        name="Risk Assessment",
        category=CATEGORY_MAP,
        severity=SEVERITY_REQUIRED,
        rules={"checks": [{"field": "risk_assessment", "operator": "exists"}]},
        enabled=True,
    )
    await db.flush()

    # Add design
    await design_repo.create(
        proj.id,
        name="Support Agent",
        design_type="agent",
        content={"purpose": "Help customers"},
    )
    await db.flush()

    # Add evaluation + criterion
    evaluation = await eval_repo.create(proj.id, name="Governance Eval")
    await db.flush()

    criterion = await criterion_repo.create(
        evaluation.id,
        criterion_id="eval-purpose-001",
        description="Agent must state its purpose",
        metric="purpose_statement_present",
        threshold="100%",
        priority=SEVERITY_REQUIRED,
    )
    await db.flush()

    # Wire one policy to criterion
    await wiring_repo.create(
        proj.id,
        policy_id=p1.policy_id,
        criterion_id=criterion.criterion_id,
        wiring_type="auto",
        confidence=0.9,
        rationale="GOVERN-1.1 requires stated purpose",
    )
    await db.flush()

    return proj


@pytest.mark.asyncio
async def test_preview_returns_metadata(export_service, seeded_project):
    preview = await export_service.preview(seeded_project.id)
    assert preview.project_name == "Test Agent"
    assert preview.active_policy_count == 2
    assert preview.wiring_count == 1
    assert preview.governance_score == 0.5  # 1 wiring / 2 policies
    assert "ai-context.yml" in preview.artifact_filenames
    assert "_provenance.json" in preview.artifact_filenames


@pytest.mark.asyncio
async def test_preview_ai_context_is_valid_yaml(export_service, seeded_project):
    preview = await export_service.preview(seeded_project.id)
    data = yaml.safe_load(preview.ai_context_yml)
    assert data["_meta"]["generated_by"] == "ideanance"
    assert data["project"]["name"] == "Test Agent"
    assert data["governance"]["active_policies"] == 2


@pytest.mark.asyncio
async def test_generate_package_has_all_artifacts(
    export_service, seeded_project
):
    package = await export_service.generate_package(seeded_project.id)
    filenames = {a.filename for a in package.artifacts}
    assert "governance/active-policies.yml" in filenames
    assert "governance/wiring-map.json" in filenames
    assert "governance/governance-report.md" in filenames
    assert "evaluations/eval-criteria.yml" in filenames
    assert "agents/agent-specs.yml" in filenames
    assert "CLAUDE.md" in filenames
    assert "README.md" in filenames


@pytest.mark.asyncio
async def test_generate_package_provenance(export_service, seeded_project):
    package = await export_service.generate_package(seeded_project.id)
    provenance = json.loads(package.provenance_json)
    assert provenance["project_id"] == seeded_project.id
    assert provenance["project_name"] == "Test Agent"
    assert FRAMEWORK_NIST_AI_RMF in provenance["governance_frameworks"]
    assert provenance["governance_score_at_export"] == 0.5


@pytest.mark.asyncio
async def test_wiring_map_contains_wirings(export_service, seeded_project):
    package = await export_service.generate_package(seeded_project.id)
    wiring_artifact = next(
        a for a in package.artifacts if a.filename == "governance/wiring-map.json"
    )
    wiring_data = json.loads(wiring_artifact.content)
    assert wiring_data["total_wirings"] == 1
    assert wiring_data["wirings"][0]["policy_id"] == NIST_GOVERN_1_1
    assert wiring_data["wirings"][0]["confidence"] == 0.9


@pytest.mark.asyncio
async def test_artifacts_have_checksums(export_service, seeded_project):
    package = await export_service.generate_package(seeded_project.id)
    for artifact in package.artifacts:
        assert artifact.checksum.startswith("sha256:")


@pytest.mark.asyncio
async def test_governance_report_lists_gaps(export_service, seeded_project):
    package = await export_service.generate_package(seeded_project.id)
    report = next(
        a
        for a in package.artifacts
        if a.filename == "governance/governance-report.md"
    )
    assert NIST_GOVERN_1_1 in report.content
    assert NIST_MAP_1_5 in report.content
    assert "[Gap]" in report.content
    assert "[Wired]" in report.content


@pytest.mark.asyncio
async def test_download_zip_is_valid(export_service, seeded_project):
    zip_bytes = await export_service.download_zip(seeded_project.id)
    assert len(zip_bytes) > 0

    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        names = zf.namelist()
        assert any("ai-context.yml" in n for n in names)
        assert any("_provenance.json" in n for n in names)
        assert any("wiring-map.json" in n for n in names)
        assert any("CLAUDE.md" in n for n in names)


@pytest.mark.asyncio
async def test_preview_not_found(export_service):
    with pytest.raises(ValueError, match="not found"):
        await export_service.preview("nonexistent-id")


@pytest.mark.asyncio
async def test_ai_context_shows_gaps(export_service, seeded_project):
    preview = await export_service.preview(seeded_project.id)
    data = yaml.safe_load(preview.ai_context_yml)
    assert data["governance"]["status"] == "partial"
    gaps = data["governance"]["gaps"]
    gap_policies = [g["policy"] for g in gaps]
    assert NIST_MAP_1_5 in gap_policies
