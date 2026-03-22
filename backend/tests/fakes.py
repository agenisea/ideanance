"""In-memory fake repository implementations for unit testing.

Each fake stores data in a dict keyed by id, and implements all methods
from the corresponding Protocol interface. No database required.

SQLAlchemy mapped classes need proper __init__ (via DeclarativeBase),
so we construct them using keyword arguments and let SQLAlchemy's
generated __init__ handle attribute initialization.
"""

from __future__ import annotations

from uuid import uuid4

from ideanance.modules.design.models import Design
from ideanance.modules.evaluation.models import EvalCriterion, Evaluation
from ideanance.modules.governance.models import (
    GovernanceCheck,
    GovernanceEvalWiring,
    GovernancePolicy,
)
from ideanance.modules.workspace.models import Project, Workspace

# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------


class FakeWorkspaceRepository:
    """In-memory WorkspaceRepository."""

    def __init__(self) -> None:
        self._store: dict[str, Workspace] = {}

    async def create(self, **kwargs: object) -> Workspace:
        ws = Workspace(id=str(uuid4()), **kwargs)  # type: ignore[arg-type]
        self._store[ws.id] = ws
        return ws

    async def get_by_id(self, workspace_id: str) -> Workspace | None:
        return self._store.get(workspace_id)

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> list[Workspace]:
        items = list(self._store.values())
        return items[offset : offset + limit]


class FakeProjectRepository:
    """In-memory ProjectRepository."""

    def __init__(self) -> None:
        self._store: dict[str, Project] = {}

    async def create(
        self, workspace_id: str, **kwargs: object
    ) -> Project:
        proj = Project(id=str(uuid4()), workspace_id=workspace_id, **kwargs)  # type: ignore[arg-type]
        self._store[proj.id] = proj
        return proj

    async def get_by_id(self, project_id: str) -> Project | None:
        return self._store.get(project_id)

    async def list_by_workspace(
        self, workspace_id: str, limit: int = 100
    ) -> list[Project]:
        return [
            p
            for p in self._store.values()
            if p.workspace_id == workspace_id
        ][:limit]


# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------


class FakeGovernancePolicyRepo:
    """In-memory GovernancePolicyRepo."""

    def __init__(self) -> None:
        self._store: dict[str, GovernancePolicy] = {}

    async def create(
        self, project_id: str, **kwargs: object
    ) -> GovernancePolicy:
        policy = GovernancePolicy(id=str(uuid4()), project_id=project_id, **kwargs)  # type: ignore[arg-type]
        self._store[policy.id] = policy
        return policy

    async def get_by_id(
        self, policy_id: str
    ) -> GovernancePolicy | None:
        return self._store.get(policy_id)

    async def list_by_project(
        self, project_id: str, enabled_only: bool = True
    ) -> list[GovernancePolicy]:
        return [
            p
            for p in self._store.values()
            if p.project_id == project_id
            and (not enabled_only or p.enabled)
        ]

    async def find_by_policy_id(
        self, project_id: str, policy_id: str
    ) -> GovernancePolicy | None:
        for p in self._store.values():
            if p.project_id == project_id and p.policy_id == policy_id:
                return p
        return None


class FakeGovernanceEvalWiringRepo:
    """In-memory GovernanceEvalWiringRepo."""

    def __init__(self) -> None:
        self._store: dict[str, GovernanceEvalWiring] = {}

    async def create(
        self, project_id: str, **kwargs: object
    ) -> GovernanceEvalWiring:
        wiring = GovernanceEvalWiring(id=str(uuid4()), project_id=project_id, **kwargs)  # type: ignore[arg-type]
        self._store[wiring.id] = wiring
        return wiring

    async def list_by_project(
        self, project_id: str
    ) -> list[GovernanceEvalWiring]:
        return [
            w
            for w in self._store.values()
            if w.project_id == project_id
        ]

    async def count_by_project(self, project_id: str) -> int:
        return len(await self.list_by_project(project_id))

    async def delete(self, wiring_id: str) -> bool:
        if wiring_id in self._store:
            del self._store[wiring_id]
            return True
        return False


class FakeGovernanceCheckRepo:
    """In-memory GovernanceCheckRepo."""

    def __init__(self) -> None:
        self._store: dict[str, GovernanceCheck] = {}

    async def create(self, **kwargs: object) -> GovernanceCheck:
        check = GovernanceCheck(id=str(uuid4()), **kwargs)  # type: ignore[arg-type]
        self._store[check.id] = check
        return check


# ---------------------------------------------------------------------------
# Design
# ---------------------------------------------------------------------------


class FakeDesignRepo:
    """In-memory DesignRepo."""

    def __init__(self) -> None:
        self._store: dict[str, Design] = {}

    async def create(
        self, project_id: str, **kwargs: object
    ) -> Design:
        design = Design(id=str(uuid4()), project_id=project_id, **kwargs)  # type: ignore[arg-type]
        self._store[design.id] = design
        return design

    async def get_by_id(self, design_id: str) -> Design | None:
        return self._store.get(design_id)

    async def list_by_project(
        self, project_id: str, limit: int = 100
    ) -> list[Design]:
        return [
            d
            for d in self._store.values()
            if d.project_id == project_id
        ][:limit]

    async def update(
        self, design_id: str, **kwargs: object
    ) -> Design | None:
        design = self._store.get(design_id)
        if design is None:
            return None
        for k, v in kwargs.items():
            setattr(design, k, v)
        return design


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


class FakeEvaluationRepo:
    """In-memory EvaluationRepo."""

    def __init__(self) -> None:
        self._store: dict[str, Evaluation] = {}

    async def create(
        self, project_id: str, **kwargs: object
    ) -> Evaluation:
        ev = Evaluation(id=str(uuid4()), project_id=project_id, **kwargs)  # type: ignore[arg-type]
        self._store[ev.id] = ev
        return ev

    async def get_by_id(
        self, evaluation_id: str
    ) -> Evaluation | None:
        return self._store.get(evaluation_id)

    async def list_by_project(
        self, project_id: str, limit: int = 100
    ) -> list[Evaluation]:
        return [
            e
            for e in self._store.values()
            if e.project_id == project_id
        ][:limit]


class FakeEvalCriterionRepo:
    """In-memory EvalCriterionRepo."""

    def __init__(self) -> None:
        self._store: dict[str, EvalCriterion] = {}

    async def create(
        self, evaluation_id: str, **kwargs: object
    ) -> EvalCriterion:
        crit = EvalCriterion(id=str(uuid4()), evaluation_id=evaluation_id, **kwargs)  # type: ignore[arg-type]
        self._store[crit.id] = crit
        return crit

    async def get_by_id(
        self, criterion_id: str
    ) -> EvalCriterion | None:
        return self._store.get(criterion_id)

    async def list_by_evaluation(
        self, evaluation_id: str
    ) -> list[EvalCriterion]:
        return [
            c
            for c in self._store.values()
            if c.evaluation_id == evaluation_id
        ]
