"""Tests for governance audit trail — PLAN53."""

from sqlalchemy.ext.asyncio import AsyncSession

from modules.governance.audit import (
    GovernanceAuditEntry,
    GovernanceAuditService,
)


async def test_record_check(db: AsyncSession):
    svc = GovernanceAuditService(db)
    entry = await svc.record_check(
        project_id="proj-1",
        workspace_id="ws-1",
        verdict="proceed",
        confidence=0.95,
        finding_count=5,
    )
    assert entry.project_id == "proj-1"
    assert entry.verdict == "proceed"
    assert entry.confidence == 0.95


async def test_list_by_project(db: AsyncSession):
    svc = GovernanceAuditService(db)
    await svc.record_check(
        project_id="proj-2",
        workspace_id="ws-1",
        verdict="blocked",
        confidence=0.8,
        finding_count=3,
    )
    await svc.record_check(
        project_id="proj-2",
        workspace_id="ws-1",
        verdict="proceed",
        confidence=0.95,
        finding_count=0,
    )
    entries = await svc.list_by_project("proj-2")
    assert len(entries) == 2


async def test_list_empty_project(db: AsyncSession):
    svc = GovernanceAuditService(db)
    entries = await svc.list_by_project("nonexistent")
    assert len(entries) == 0


async def test_audit_entry_model(db: AsyncSession):
    entry = GovernanceAuditEntry(
        project_id="p",
        workspace_id="w",
        action="check",
        verdict="escalate",
    )
    db.add(entry)
    await db.flush()
    assert entry.id is not None
