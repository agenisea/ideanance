"""Tests for kill switches."""

from core.observability.kill_switches import (
    KillSwitches,
)
from modules.agents import AGENT_IDS


def test_kill_switches():
    ks = KillSwitches()
    assert (
        ks.is_agent_enabled(AGENT_IDS["DESIGN_ADVISOR"])
        is True
    )

    ks.disable_agent(
        AGENT_IDS["DESIGN_ADVISOR"], "testing"
    )
    assert (
        ks.is_agent_enabled(AGENT_IDS["DESIGN_ADVISOR"])
        is False
    )
    assert (
        ks.is_agent_enabled(AGENT_IDS["QUERY_ROUTER"])
        is True
    )

    ks.disable_all_agents("cost spike")
    assert (
        ks.is_agent_enabled(AGENT_IDS["QUERY_ROUTER"])
        is False
    )

    ks.enable_all()
    assert (
        ks.is_agent_enabled(AGENT_IDS["DESIGN_ADVISOR"])
        is True
    )
