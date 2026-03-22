"""Tests for CLI entry point."""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

POLICIES_DIR = str(
    Path(__file__).resolve().parents[2] / "governance-policies"
)


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ideanance_sdk.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[1]),
        env={
            "PATH": "",
            "PYTHONPATH": str(
                Path(__file__).resolve().parents[1] / "src"
            ),
        },
    )


def test_cli_check_json():
    with tempfile.NamedTemporaryFile(
        suffix=".yml", mode="w", delete=False
    ) as f:
        yaml.dump(
            {"design": {"purpose": "Test AI"}}, f
        )
        f.flush()

        result = _run_cli(
            "check",
            f.name,
            "--framework",
            "nist-ai-rmf",
            "--policies-dir",
            POLICIES_DIR,
            "--format",
            "json",
        )
        assert "overall_score" in result.stdout


def test_cli_check_ci_mode():
    with tempfile.NamedTemporaryFile(
        suffix=".yml", mode="w", delete=False
    ) as f:
        yaml.dump(
            {"design": {"purpose": "Test AI"}}, f
        )
        f.flush()

        result = _run_cli(
            "check",
            f.name,
            "--framework",
            "nist-ai-rmf",
            "--policies-dir",
            POLICIES_DIR,
            "--ci",
        )
        assert "policies passed" in result.stdout
