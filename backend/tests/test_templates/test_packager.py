"""Tests for TemplatePackager: export, import, round-trip, validation."""

from __future__ import annotations

import io
import zipfile

import pytest
import yaml

from ideanance.modules.governance.engine import PolicyRule
from ideanance.modules.governance.loader import (
    EvalSuggestion,
    LoadedPolicy,
)
from ideanance.modules.templates.packager import (
    MAX_ZIP_SIZE,
    TemplatePackageError,
    TemplatePackager,
)


def _make_policy(
    policy_id: str = "test-policy-1",
    framework: str = "test-framework",
) -> LoadedPolicy:
    """Create a minimal LoadedPolicy for testing."""
    return LoadedPolicy(
        id=policy_id,
        framework=framework,
        category="govern",
        subcategory="1.1",
        name="Test Policy",
        description="A test governance policy",
        severity="warning",
        applies_to=["agent_design"],
        rules=[
            PolicyRule(
                check="field_present",
                target="design.purpose",
                message="Must include purpose",
                params=None,
            ),
            PolicyRule(
                check="field_min_length",
                target="design.risk_assessment",
                message="Risk assessment must be substantive",
                params={"min_length": 50},
            ),
        ],
        remediation={
            "guidance": "Add documentation."
        },
        eval_suggestions=[
            EvalSuggestion(
                criterion="Purpose present",
                metric="purpose_present",
                threshold="boolean: true",
            ),
        ],
    )


class TestExportZip:
    """Test ZIP export functionality."""

    def test_export_creates_valid_zip(self) -> None:
        packager = TemplatePackager()
        policies = [_make_policy()]

        result = packager.export_zip(
            framework_name="Test Framework",
            policies=policies,
            version="2.0.0",
            description="Test desc",
            author="tester",
            tags=["test"],
        )

        assert isinstance(result, bytes)
        buf = io.BytesIO(result)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()
            assert "manifest.yml" in names
            assert "policies/test-policy-1.yml" in names

    def test_export_manifest_content(self) -> None:
        packager = TemplatePackager()
        policies = [_make_policy()]

        result = packager.export_zip(
            framework_name="My Framework",
            policies=policies,
            version="1.2.3",
            author="author",
            description="desc",
            tags=["a", "b"],
        )

        buf = io.BytesIO(result)
        with zipfile.ZipFile(buf, "r") as zf:
            manifest = yaml.safe_load(
                zf.read("manifest.yml")
            )

        m = manifest["manifest"]
        assert m["name"] == "My Framework"
        assert m["version"] == "1.2.3"
        assert m["author"] == "author"
        assert m["description"] == "desc"
        assert m["tags"] == ["a", "b"]
        assert m["policy_count"] == 1

    def test_export_policy_content(self) -> None:
        packager = TemplatePackager()
        policy = _make_policy()

        result = packager.export_zip(
            framework_name="FW",
            policies=[policy],
        )

        buf = io.BytesIO(result)
        with zipfile.ZipFile(buf, "r") as zf:
            data = yaml.safe_load(
                zf.read("policies/test-policy-1.yml")
            )

        p = data["policy"]
        assert p["id"] == "test-policy-1"
        assert p["framework"] == "test-framework"
        assert p["category"] == "govern"
        assert len(p["rules"]) == 2
        assert p["rules"][0]["check"] == "field_present"
        assert p["remediation"]["guidance"] == (
            "Add documentation."
        )
        assert len(p["eval_suggestions"]) == 1

    def test_export_multiple_policies(self) -> None:
        packager = TemplatePackager()
        policies = [
            _make_policy("policy-a"),
            _make_policy("policy-b"),
        ]

        result = packager.export_zip(
            framework_name="FW", policies=policies
        )

        buf = io.BytesIO(result)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()
        assert "policies/policy-a.yml" in names
        assert "policies/policy-b.yml" in names


class TestImportZip:
    """Test ZIP import functionality."""

    def test_import_valid_zip(self) -> None:
        packager = TemplatePackager()
        policies = [_make_policy()]
        zip_bytes = packager.export_zip(
            framework_name="Test",
            policies=policies,
        )

        manifest, imported = packager.import_zip(zip_bytes)

        assert manifest["name"] == "Test"
        assert len(imported) == 1
        assert imported[0].id == "test-policy-1"

    def test_import_rejects_oversized_zip(self) -> None:
        packager = TemplatePackager()
        big_data = b"\x00" * (MAX_ZIP_SIZE + 1)

        with pytest.raises(
            TemplatePackageError, match="byte limit"
        ):
            packager.import_zip(big_data)

    def test_import_rejects_bad_zip(self) -> None:
        packager = TemplatePackager()

        with pytest.raises(
            TemplatePackageError, match="Invalid ZIP"
        ):
            packager.import_zip(b"not a zip file")

    def test_import_rejects_missing_manifest(self) -> None:
        packager = TemplatePackager()

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("readme.txt", "hello")

        with pytest.raises(
            TemplatePackageError, match="manifest.yml"
        ):
            packager.import_zip(buf.getvalue())

    def test_import_rejects_secrets(self) -> None:
        packager = TemplatePackager()

        manifest_content = yaml.dump(
            {
                "manifest": {
                    "name": "bad",
                    "version": "1.0",
                }
            }
        )
        policy_content = (
            "policy:\n"
            "  id: leaked\n"
            "  framework: test\n"
            "  category: govern\n"
            "  name: Leaked\n"
            "  rules:\n"
            "    - check: field_present\n"
            "      target: design.purpose\n"
            "      message: sk-ant-AAAAAAAAAAAAAAAAAAAAAA\n"
        )

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("manifest.yml", manifest_content)
            zf.writestr(
                "policies/leaked.yml", policy_content
            )

        with pytest.raises(
            TemplatePackageError, match="secrets"
        ):
            packager.import_zip(buf.getvalue())

    def test_import_rejects_deep_yaml(self) -> None:
        packager = TemplatePackager()

        # Build deeply nested YAML
        nested: dict = {"a": None}
        current = nested
        for _ in range(15):
            child: dict = {"a": None}
            current["a"] = child
            current = child

        manifest_content = yaml.dump(
            {
                "manifest": {
                    "name": "deep",
                    "version": "1.0",
                }
            }
        )
        deep_content = yaml.dump({"policy": nested})

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("manifest.yml", manifest_content)
            zf.writestr("policies/deep.yml", deep_content)

        with pytest.raises(
            TemplatePackageError, match="depth"
        ):
            packager.import_zip(buf.getvalue())


class TestRoundTrip:
    """Test export -> import round-trip preserves data."""

    def test_round_trip_preserves_policy_data(
        self,
    ) -> None:
        packager = TemplatePackager()
        original = _make_policy()

        zip_bytes = packager.export_zip(
            framework_name="Round Trip FW",
            policies=[original],
            version="3.0.0",
            author="rt-tester",
        )

        manifest, policies = packager.import_zip(
            zip_bytes
        )

        assert manifest["name"] == "Round Trip FW"
        assert manifest["version"] == "3.0.0"
        assert manifest["author"] == "rt-tester"

        assert len(policies) == 1
        p = policies[0]
        assert p.id == original.id
        assert p.framework == original.framework
        assert p.category == original.category
        assert p.subcategory == original.subcategory
        assert p.name == original.name
        assert p.description == original.description
        assert p.severity == original.severity
        assert p.applies_to == original.applies_to
        assert len(p.rules) == len(original.rules)

        # Check rule details
        for imported_rule, orig_rule in zip(
            p.rules, original.rules, strict=True
        ):
            assert imported_rule.check == orig_rule.check
            assert (
                imported_rule.target == orig_rule.target
            )
            assert (
                imported_rule.message == orig_rule.message
            )
            assert (
                imported_rule.params == orig_rule.params
            )

        # Check eval suggestions
        assert len(p.eval_suggestions) == len(
            original.eval_suggestions
        )
        assert (
            p.eval_suggestions[0].criterion
            == original.eval_suggestions[0].criterion
        )

        # Check remediation
        assert p.remediation == original.remediation
