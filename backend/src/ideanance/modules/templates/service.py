"""Template export/import service.

Delegates to TemplatePackager for ZIP packaging and to
load_framework_policies for loading built-in framework files.
"""

from __future__ import annotations

from pathlib import Path

from ideanance.modules.governance.constants import (
    FRAMEWORK_EU_AI_ACT,
    FRAMEWORK_ID_EU_AI_ACT,
    FRAMEWORK_ID_NIST_AI_RMF,
    FRAMEWORK_NIST_AI_RMF,
)
from ideanance.modules.governance.loader import (
    LoadedPolicy,
    load_framework_policies,
)
from ideanance.modules.templates.packager import (
    TemplatePackager,
)

# Root of governance-policies relative to this file
_GOVERNANCE_ROOT = (
    Path(__file__).resolve().parents[5]
    / "governance-policies"
)

# Built-in framework directories
BUILTIN_FRAMEWORKS: dict[str, str] = {
    FRAMEWORK_ID_NIST_AI_RMF: FRAMEWORK_NIST_AI_RMF,
    FRAMEWORK_ID_EU_AI_ACT: FRAMEWORK_EU_AI_ACT,
}


class TemplateService:
    """Orchestrates governance framework export/import."""

    def __init__(
        self, packager: TemplatePackager | None = None
    ) -> None:
        self._packager = packager or TemplatePackager()

    def export_framework(
        self,
        framework_name: str,
        policies: list[LoadedPolicy],
        *,
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        tags: list[str] | None = None,
    ) -> bytes:
        """Export policies as a shareable ZIP package."""
        return self._packager.export_zip(
            framework_name=framework_name,
            policies=policies,
            version=version,
            description=description,
            author=author,
            tags=tags,
        )

    def import_framework(
        self, zip_bytes: bytes
    ) -> tuple[dict, list[LoadedPolicy]]:
        """Import a ZIP package. Returns (manifest, policies).

        The caller is responsible for persisting the imported
        policies into the project via CustomFrameworkService.
        """
        return self._packager.import_zip(zip_bytes)

    def export_builtin(self, framework_id: str) -> bytes:
        """Export a built-in framework as a ZIP package."""
        if framework_id not in BUILTIN_FRAMEWORKS:
            raise ValueError(
                f"Unknown built-in framework: "
                f"{framework_id}. "
                f"Available: "
                f"{', '.join(sorted(BUILTIN_FRAMEWORKS))}"
            )

        fw_dir = _GOVERNANCE_ROOT / framework_id
        if not fw_dir.exists():
            raise ValueError(
                f"Framework directory not found: {fw_dir}"
            )

        policies = load_framework_policies(fw_dir)
        name = BUILTIN_FRAMEWORKS[framework_id]

        return self._packager.export_zip(
            framework_name=name,
            policies=policies,
            version="1.0.0",
            description=(
                f"Built-in {name} governance policies"
            ),
            author="ideanance",
            tags=[framework_id, "built-in"],
        )

    def list_builtin_frameworks(
        self,
    ) -> list[dict[str, str]]:
        """List available built-in frameworks for export."""
        return [
            {"id": fid, "name": fname}
            for fid, fname in BUILTIN_FRAMEWORKS.items()
        ]
