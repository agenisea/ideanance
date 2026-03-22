"""THE CRITICAL TEST: Full governance-eval wiring loop.

Proves the Milestone 1 success criteria from ACTION_ROADMAP:
- Create a project, attach a governance policy, create eval criteria, wire them
- Bidirectional traversal: policy -> criteria AND criteria -> policy
- North Star metric: project is Governance-Wired when wiring count > 0
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ideanance.modules.evaluation.models import EvalCriterion, Evaluation
from ideanance.modules.governance.constants import (
    CATEGORY_GOVERN,
    FRAMEWORK_NIST_AI_RMF,
    NIST_GOVERN_1_1,
)
from ideanance.modules.governance.models import (
    GovernanceEvalWiring,
    GovernancePolicy,
)
from ideanance.modules.workspace.models import Project, Workspace


async def _create_wired_project(db: AsyncSession):
    """Helper: create a full Governance-Wired Project."""
    ws = Workspace(name="Test Workspace")
    db.add(ws)
    await db.flush()

    proj = Project(workspace_id=ws.id, name="AI Agent Project")
    db.add(proj)
    await db.flush()

    policy = GovernancePolicy(
        project_id=proj.id,
        framework=FRAMEWORK_NIST_AI_RMF,
        policy_id=NIST_GOVERN_1_1,
        name="Legal Requirements",
        category=CATEGORY_GOVERN,
        severity="error",
    )
    db.add(policy)
    await db.flush()

    ev = Evaluation(project_id=proj.id, name="Compliance Evals")
    db.add(ev)
    await db.flush()

    crit = EvalCriterion(
        evaluation_id=ev.id,
        criterion_id="eval-001",
        description="Purpose statement present",
        metric="purpose_present",
        threshold="true",
        priority="critical",
    )
    db.add(crit)
    await db.flush()

    wiring = GovernanceEvalWiring(
        project_id=proj.id,
        policy_id=policy.id,
        criterion_id=crit.id,
        wiring_type="manual",
        confidence=1.0,
        rationale="GOVERN-1.1 requires stated purpose",
    )
    db.add(wiring)
    await db.flush()

    return ws, proj, policy, ev, crit, wiring


async def test_full_governance_eval_wiring_loop(db: AsyncSession):
    """The atomic test: full wiring from workspace to eval criterion."""
    ws, proj, policy, ev, crit, wiring = await _create_wired_project(db)

    assert wiring.id is not None
    assert wiring.policy_id == policy.id
    assert wiring.criterion_id == crit.id
    assert wiring.project_id == proj.id


async def test_bidirectional_traversal_policy_to_criteria(db: AsyncSession):
    """Given a policy, retrieve all linked eval criteria."""
    _, _, policy, _, crit, _ = await _create_wired_project(db)

    result = await db.execute(
        select(GovernancePolicy)
        .options(selectinload(GovernancePolicy.eval_criteria))
        .where(GovernancePolicy.id == policy.id)
    )
    loaded = result.scalar_one()
    assert len(loaded.eval_criteria) == 1
    assert loaded.eval_criteria[0].id == crit.id


async def test_bidirectional_traversal_criterion_to_policies(db: AsyncSession):
    """Given a criterion, retrieve all linked policies."""
    _, _, policy, _, crit, _ = await _create_wired_project(db)

    result = await db.execute(
        select(EvalCriterion)
        .options(selectinload(EvalCriterion.governance_policies))
        .where(EvalCriterion.id == crit.id)
    )
    loaded = result.scalar_one()
    assert len(loaded.governance_policies) == 1
    assert loaded.governance_policies[0].id == policy.id


async def test_project_governance_wired_metric(db: AsyncSession):
    """North Star: count of governance-wired projects."""
    _, proj, _, _, _, _ = await _create_wired_project(db)

    # Create a second project WITHOUT wiring
    ws2 = Workspace(name="WS2")
    db.add(ws2)
    await db.flush()
    proj2 = Project(workspace_id=ws2.id, name="Unwired Project")
    db.add(proj2)
    await db.flush()

    # Count wired projects
    result = await db.execute(
        select(func.count(func.distinct(GovernanceEvalWiring.project_id)))
    )
    wired_count = result.scalar_one()
    assert wired_count == 1


async def test_multiple_wirings_per_policy(db: AsyncSession):
    """A single policy can wire to multiple criteria."""
    _, proj, policy, ev, crit1, _ = await _create_wired_project(db)

    crit2 = EvalCriterion(
        evaluation_id=ev.id,
        criterion_id="eval-002",
        description="Users documented",
        metric="users_listed",
        threshold="count >= 1",
    )
    db.add(crit2)
    await db.flush()

    wiring2 = GovernanceEvalWiring(
        project_id=proj.id,
        policy_id=policy.id,
        criterion_id=crit2.id,
        wiring_type="manual",
        confidence=1.0,
        rationale="GOVERN-1.1 also requires user identification",
    )
    db.add(wiring2)
    await db.flush()

    result = await db.execute(
        select(GovernancePolicy)
        .options(selectinload(GovernancePolicy.eval_criteria))
        .where(GovernancePolicy.id == policy.id)
    )
    loaded = result.scalar_one()
    assert len(loaded.eval_criteria) == 2
