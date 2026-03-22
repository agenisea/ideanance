"""Unit tests for GovernanceService using fake repositories and a real EventBus."""

from __future__ import annotations

import asyncio

import pytest

from ideanance.core.events import EventBus
from ideanance.modules.governance.engine import GovernanceEngine
from ideanance.modules.governance.schemas import GovernanceEvalWiringCreate
from ideanance.modules.governance.service import GovernanceService
from tests.fakes import (
    FakeEvalCriterionRepo,
    FakeGovernanceCheckRepo,
    FakeGovernanceEvalWiringRepo,
    FakeGovernancePolicyRepo,
)


async def _seed_policy_and_criterion(
    policy_repo: FakeGovernancePolicyRepo,
    criterion_repo: FakeEvalCriterionRepo,
    project_id: str,
) -> tuple[str, str]:
    """Create a policy and a criterion, return (policy.id, criterion.id)."""
    policy = await policy_repo.create(
        project_id=project_id,
        framework="NIST AI RMF",
        policy_id="nist-govern-1.1",
        name="Legal Requirements",
        category="govern",
    )
    criterion = await criterion_repo.create(
        evaluation_id="eval-1",
        criterion_id="crit-1",
        description="Check legal compliance",
        metric="compliance_score",
        threshold=">0.8",
    )
    return policy.id, criterion.id


def _build_service(
    event_bus: EventBus | None = None,
) -> tuple[
    GovernanceService,
    FakeGovernancePolicyRepo,
    FakeEvalCriterionRepo,
]:
    policy_repo = FakeGovernancePolicyRepo()
    wiring_repo = FakeGovernanceEvalWiringRepo()
    check_repo = FakeGovernanceCheckRepo()
    criterion_repo = FakeEvalCriterionRepo()
    engine = GovernanceEngine()
    svc = GovernanceService(
        policy_repo=policy_repo,
        wiring_repo=wiring_repo,
        check_repo=check_repo,
        engine=engine,
        criterion_repo=criterion_repo,
        event_bus=event_bus,
    )
    return svc, policy_repo, criterion_repo


async def test_wire_policy_to_criterion_happy_path():
    svc, policy_repo, criterion_repo = _build_service()
    project_id = "proj-1"
    policy_id, criterion_id = await _seed_policy_and_criterion(
        policy_repo, criterion_repo, project_id
    )

    wiring = await svc.wire_policy_to_criterion(
        project_id,
        GovernanceEvalWiringCreate(
            policy_id=policy_id, criterion_id=criterion_id
        ),
    )
    assert wiring.policy_id == policy_id
    assert wiring.criterion_id == criterion_id

    # Should appear in list
    wirings = await svc.list_wirings(project_id)
    assert len(wirings) == 1


async def test_wire_policy_not_found_raises():
    svc, _policy_repo, criterion_repo = _build_service()
    # Create a criterion but no policy
    criterion = await criterion_repo.create(
        evaluation_id="eval-1",
        criterion_id="crit-1",
        description="Desc",
        metric="m",
        threshold="t",
    )
    with pytest.raises(ValueError, match="Policy not found"):
        await svc.wire_policy_to_criterion(
            "proj-1",
            GovernanceEvalWiringCreate(
                policy_id="nonexistent", criterion_id=criterion.id
            ),
        )


async def test_wire_criterion_not_found_raises():
    svc, policy_repo, _criterion_repo = _build_service()
    policy = await policy_repo.create(
        project_id="proj-1",
        framework="NIST AI RMF",
        policy_id="nist-govern-1.1",
        name="Legal Requirements",
        category="govern",
    )
    with pytest.raises(ValueError, match="Eval criterion not found"):
        await svc.wire_policy_to_criterion(
            "proj-1",
            GovernanceEvalWiringCreate(
                policy_id=policy.id, criterion_id="nonexistent"
            ),
        )


async def test_wire_publishes_event():
    event_bus = EventBus()
    svc, policy_repo, criterion_repo = _build_service(
        event_bus=event_bus
    )
    project_id = "proj-1"
    policy_id, criterion_id = await _seed_policy_and_criterion(
        policy_repo, criterion_repo, project_id
    )

    # Subscribe before the wiring event
    queue = event_bus.subscribe("")  # workspace_id is "" in the service

    await svc.wire_policy_to_criterion(
        project_id,
        GovernanceEvalWiringCreate(
            policy_id=policy_id, criterion_id=criterion_id
        ),
    )

    # Should receive the event without blocking
    event = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert event.type == "governance.wiring.created"
    assert event.payload["policy_id"] == policy_id
    assert event.payload["criterion_id"] == criterion_id
