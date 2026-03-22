"""Tests for TemplateService: delegation and built-in framework export."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ideanance.modules.governance.engine import PolicyRule
from ideanance.modules.governance.loader import (
    LoadedPolicy,
)
from ideanance.modules.templates.packager import (
    TemplatePackager,
)
from ideanance.modules.templates.service import (
    BUILTIN_FRAMEWORKS,
    TemplateService,
)


def _make_policy(
    policy_id: str = "svc-test-1",
) -> LoadedPolicy:
    return LoadedPolicy(
        id=policy_id,
        framework="svc-framework",
        category="govern",
        subcategory="1.1",
        name="Service Test Policy",
        description="Test",
        severity="warning",
        applies_to=["agent_design"],
        rules=[
            PolicyRule(
                check="field_present",
                target="design.purpose",
                message="Must include purpose",
                params=None,
            ),
        ],
    )


class TestExportFramework:
    """Test TemplateService.export_framework delegates."""

    def test_delegates_to_packager(self) -> None:
        mock_packager = MagicMock(spec=TemplatePackager)
        mock_packager.export_zip.return_value = (
            b"zip-bytes"
        )
        svc = TemplateService(packager=mock_packager)

        policies = [_make_policy()]
        result = svc.export_framework(
            framework_name="Test FW",
            policies=policies,
            version="2.0",
            description="desc",
            author="auth",
            tags=["t"],
        )

        assert result == b"zip-bytes"
        mock_packager.export_zip.assert_called_once_with(
            framework_name="Test FW",
            policies=policies,
            version="2.0",
            description="desc",
            author="auth",
            tags=["t"],
        )


class TestImportFramework:
    """Test TemplateService.import_framework delegates."""

    def test_delegates_to_packager(self) -> None:
        mock_packager = MagicMock(spec=TemplatePackager)
        expected = ({"name": "imported"}, [_make_policy()])
        mock_packager.import_zip.return_value = expected
        svc = TemplateService(packager=mock_packager)

        result = svc.import_framework(b"zip-data")

        assert result == expected
        mock_packager.import_zip.assert_called_once_with(
            b"zip-data"
        )


class TestExportBuiltin:
    """Test built-in framework export."""

    def test_unknown_framework_raises(self) -> None:
        svc = TemplateService()
        with pytest.raises(
            ValueError, match="Unknown built-in"
        ):
            svc.export_builtin("nonexistent-framework")

    def test_export_nist_returns_zip(self) -> None:
        svc = TemplateService()
        result = svc.export_builtin("nist-ai-rmf")
        assert isinstance(result, bytes)
        # ZIP magic bytes
        assert result[:4] == b"PK\x03\x04"

    def test_export_eu_ai_act_returns_zip(self) -> None:
        svc = TemplateService()
        result = svc.export_builtin("eu-ai-act")
        assert isinstance(result, bytes)
        assert result[:4] == b"PK\x03\x04"


class TestListBuiltinFrameworks:
    """Test listing available built-in frameworks."""

    def test_returns_known_frameworks(self) -> None:
        svc = TemplateService()
        frameworks = svc.list_builtin_frameworks()
        ids = {fw["id"] for fw in frameworks}
        assert ids == set(BUILTIN_FRAMEWORKS.keys())
        for fw in frameworks:
            assert "id" in fw
            assert "name" in fw
