"""Emergency kill switches for cost and error thresholds."""

from __future__ import annotations

import structlog

log = structlog.get_logger()


class KillSwitches:
    """Manages global and per-agent kill switches."""

    def __init__(self) -> None:
        self._global_disabled = False
        self._disabled_agents: set[str] = set()

    def disable_all_agents(self, reason: str) -> None:
        self._global_disabled = True
        log.critical("kill_switch.global_disable", reason=reason)

    def disable_agent(self, agent_id: str, reason: str) -> None:
        self._disabled_agents.add(agent_id)
        log.warning(
            "kill_switch.agent_disable",
            agent_id=agent_id,
            reason=reason,
        )

    def is_agent_enabled(self, agent_id: str) -> bool:
        if self._global_disabled:
            return False
        return agent_id not in self._disabled_agents

    def enable_all(self) -> None:
        self._global_disabled = False
        self._disabled_agents.clear()
        log.info("kill_switch.all_enabled")
