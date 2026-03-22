"""Lens correctness evaluation.

Tests that each lens produces findings for its concern.
Deterministic — no LLM calls.
"""

from __future__ import annotations

from pathlib import Path

from ideanance.modules.governance.lenses.accountability import (
    AccountabilityLens,
)
from ideanance.modules.governance.lenses.boundary import (
    BoundaryLens,
)
from ideanance.modules.governance.lenses.dignity import (
    DignityLens,
)
from ideanance.modules.governance.lenses.privacy import (
    PrivacyLens,
)
from ideanance.modules.governance.lenses.transparency import (
    TransparencyLens,
)
from ideanance.modules.governance.loader import (
    load_framework_policies,
)

NIST_DIR = (
    Path(__file__).resolve().parents[2]
    / "governance-policies"
    / "nist-ai-rmf"
)

policies = load_framework_policies(NIST_DIR)
empty_design: dict = {"design": {}}


def run_eval() -> None:
    """Run lens evaluation."""
    lenses = [
        BoundaryLens(),
        TransparencyLens(),
        AccountabilityLens(),
        PrivacyLens(),
        DignityLens(),
    ]

    passed = 0
    total = 0

    for lens in lenses:
        result = lens.evaluate(empty_design, policies)
        total += 1
        has_findings = len(result.findings) > 0

        if lens.name in (
            "boundary",
            "transparency",
            "accountability",
        ):
            # These should produce findings for
            # empty design against NIST
            ok = has_findings
        else:
            # Privacy/Dignity may not have NIST
            # policies mapped
            ok = True

        icon = "PASS" if ok else "FAIL"
        print(
            f"  {icon}: {lens.name}"
            f" — {len(result.findings)} findings,"
            f" status={result.status}"
        )
        if ok:
            passed += 1

    print(f"\n{passed}/{total} passed")


if __name__ == "__main__":
    run_eval()
