"""Shared agent dependency types.

GovernanceDeps uses Protocol-typed repos — no AsyncSession leak.
Constructed by get_governance_deps() in dependencies.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ideanance.modules.design.protocols import DesignRepo
from ideanance.modules.evaluation.protocols import EvaluationRepo
from ideanance.modules.governance.protocols import GovernancePolicyRepo


@dataclass
class RouterDeps:
    """Dependencies for the Query Router."""

    workspace_id: str
    project_id: str
    available_agents: list[str]


@dataclass
class GovernanceDeps:
    """Shared dependency type for governance-aware domain agents.

    No AsyncSession — agent tools use Protocol-typed repos.
    """

    workspace_id: str
    project_id: str
    active_frameworks: list[str]
    active_policies: list[dict[str, Any]]
    agent_specs: list[dict[str, Any]]
    policy_repo: GovernancePolicyRepo
    design_repo: DesignRepo
    eval_repo: EvaluationRepo
    embedding_client: Any | None = None
