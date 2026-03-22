"""Package governance frameworks as ZIP archives for sharing.

Uses yaml.safe_load() exclusively. Validates imports for size,
secret leaks, and YAML depth bombs.
"""

from __future__ import annotations

import io
import zipfile
from typing import Any

import yaml

from ideanance.core.security.input_validation import (
    MAX_POLICY_YAML_SIZE,
)
from ideanance.core.security.secret_detection import has_secrets
from ideanance.modules.governance.engine import PolicyRule
from ideanance.modules.governance.loader import (
    EvalSuggestion,
    LoadedPolicy,
)

# Maximum total ZIP size (5 MB)
MAX_ZIP_SIZE = 5_000_000

# Maximum number of files inside the archive
MAX_ZIP_ENTRIES = 100

# YAML nesting depth limit (bomb defense)
MAX_YAML_DEPTH = 10


class TemplatePackageError(ValueError):
    """Raised when a template package is invalid."""


def _check_yaml_depth(
    obj: object,
    depth: int = 0,
    max_depth: int = MAX_YAML_DEPTH,
) -> None:
    """Reject deeply nested YAML (bomb defense)."""
    if depth > max_depth:
        raise TemplatePackageError(
            "YAML nesting exceeds maximum depth"
        )
    if isinstance(obj, dict):
        for v in obj.values():
            _check_yaml_depth(v, depth + 1, max_depth)
    elif isinstance(obj, list):
        for v in obj:
            _check_yaml_depth(v, depth + 1, max_depth)


def _policy_to_dict(policy: LoadedPolicy) -> dict[str, Any]:
    """Serialize a LoadedPolicy to a YAML-ready dict."""
    rules_out = []
    for rule in policy.rules:
        entry: dict[str, Any] = {
            "check": rule.check,
            "target": rule.target,
            "message": rule.message,
        }
        if rule.params:
            entry.update(rule.params)
        rules_out.append(entry)

    result: dict[str, Any] = {
        "policy": {
            "id": policy.id,
            "framework": policy.framework,
            "category": policy.category,
            "subcategory": policy.subcategory,
            "name": policy.name,
            "description": policy.description,
            "severity": policy.severity,
            "applies_to": policy.applies_to,
            "rules": rules_out,
        }
    }

    if policy.remediation:
        result["policy"]["remediation"] = policy.remediation

    if policy.eval_suggestions:
        result["policy"]["eval_suggestions"] = [
            {
                "criterion": s.criterion,
                "metric": s.metric,
                "threshold": s.threshold,
            }
            for s in policy.eval_suggestions
        ]

    return result


def _parse_policy(data: dict[str, Any]) -> LoadedPolicy:
    """Parse a policy dict into a LoadedPolicy."""
    if "policy" not in data:
        raise TemplatePackageError(
            "YAML must contain a top-level 'policy' key"
        )

    policy = data["policy"]
    required = {"id", "framework", "category", "name", "rules"}
    missing = required - set(policy.keys())
    if missing:
        raise TemplatePackageError(
            f"Missing required fields: "
            f"{', '.join(sorted(missing))}"
        )

    rules = []
    for rule_data in policy.get("rules", []):
        params = {
            k: v
            for k, v in rule_data.items()
            if k not in ("check", "target", "message")
        }
        rules.append(
            PolicyRule(
                check=rule_data["check"],
                target=rule_data["target"],
                message=rule_data["message"],
                params=params if params else None,
            )
        )

    eval_suggestions = [
        EvalSuggestion(
            criterion=s.get("criterion", ""),
            metric=s.get("metric", ""),
            threshold=s.get("threshold", ""),
        )
        for s in policy.get("eval_suggestions", [])
    ]

    return LoadedPolicy(
        id=policy["id"],
        framework=policy["framework"],
        category=policy["category"].lower(),
        subcategory=policy.get("subcategory", ""),
        name=policy["name"],
        description=policy.get("description", ""),
        severity=policy.get("severity", "warning"),
        applies_to=policy.get("applies_to", []),
        rules=rules,
        remediation=policy.get("remediation", {}),
        eval_suggestions=eval_suggestions,
    )


class TemplatePackager:
    """Package and unpackage governance framework ZIP archives."""

    def export_zip(
        self,
        framework_name: str,
        policies: list[LoadedPolicy],
        *,
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        tags: list[str] | None = None,
    ) -> bytes:
        """Package framework + policies as ZIP bytes.

        Creates a ZIP with:
          manifest.yml — name, version, author, description, tags
          policies/*.yml — one file per policy
        """
        manifest: dict[str, Any] = {
            "manifest": {
                "name": framework_name,
                "version": version,
                "author": author,
                "description": description,
                "tags": tags or [],
                "policy_count": len(policies),
            }
        }

        buf = io.BytesIO()
        with zipfile.ZipFile(
            buf, "w", zipfile.ZIP_DEFLATED
        ) as zf:
            zf.writestr(
                "manifest.yml",
                yaml.dump(
                    manifest,
                    default_flow_style=False,
                    sort_keys=False,
                ),
            )
            for policy in policies:
                filename = f"policies/{policy.id}.yml"
                content = yaml.dump(
                    _policy_to_dict(policy),
                    default_flow_style=False,
                    sort_keys=False,
                )
                zf.writestr(filename, content)

        return buf.getvalue()

    def import_zip(
        self, zip_bytes: bytes
    ) -> tuple[dict[str, Any], list[LoadedPolicy]]:
        """Unpackage ZIP. Returns (manifest, policies).

        Validates:
          - Total ZIP size
          - Entry count limit
          - Per-file YAML size
          - Secret scanning
          - YAML depth check
        """
        # Size gate
        if len(zip_bytes) > MAX_ZIP_SIZE:
            raise TemplatePackageError(
                f"ZIP exceeds {MAX_ZIP_SIZE} byte limit"
            )

        try:
            buf = io.BytesIO(zip_bytes)
            zf = zipfile.ZipFile(buf, "r")
        except zipfile.BadZipFile as e:
            raise TemplatePackageError(
                f"Invalid ZIP file: {e}"
            ) from e

        with zf:
            names = zf.namelist()

            # Entry count gate
            if len(names) > MAX_ZIP_ENTRIES:
                raise TemplatePackageError(
                    f"ZIP has too many entries "
                    f"(max {MAX_ZIP_ENTRIES})"
                )

            # Must contain manifest
            if "manifest.yml" not in names:
                raise TemplatePackageError(
                    "ZIP missing manifest.yml"
                )

            # Parse manifest
            manifest_bytes = zf.read("manifest.yml")
            manifest_str = manifest_bytes.decode("utf-8")
            self._validate_yaml_content(manifest_str)
            manifest_data = yaml.safe_load(manifest_str)
            _check_yaml_depth(manifest_data)

            if (
                not isinstance(manifest_data, dict)
                or "manifest" not in manifest_data
            ):
                raise TemplatePackageError(
                    "manifest.yml must contain a "
                    "'manifest' key"
                )

            manifest = manifest_data["manifest"]

            # Parse policies
            policies: list[LoadedPolicy] = []
            for name in sorted(names):
                if not name.startswith("policies/"):
                    continue
                if not name.endswith(".yml"):
                    continue

                raw = zf.read(name)
                content = raw.decode("utf-8")
                self._validate_yaml_content(content)

                data = yaml.safe_load(content)
                _check_yaml_depth(data)
                policies.append(_parse_policy(data))

        return manifest, policies

    def _validate_yaml_content(self, content: str) -> None:
        """Run size + secret checks on YAML content."""
        size = len(content.encode("utf-8"))
        if size > MAX_POLICY_YAML_SIZE:
            raise TemplatePackageError(
                f"YAML file exceeds "
                f"{MAX_POLICY_YAML_SIZE} byte limit"
            )
        if has_secrets(content):
            raise TemplatePackageError(
                "YAML file contains potential secrets"
            )
