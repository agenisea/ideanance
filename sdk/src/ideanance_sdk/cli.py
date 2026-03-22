"""CLI entry point: ideanance check design.yml --framework nist-ai-rmf"""

from __future__ import annotations

import argparse
import sys

import yaml

from ideanance_sdk.checker import check_governance


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ideanance",
        description="Governance-as-Code checks",
    )
    sub = parser.add_subparsers(dest="command")

    check = sub.add_parser(
        "check", help="Check a design against governance"
    )
    check.add_argument(
        "design_file", help="Path to design YAML"
    )
    check.add_argument(
        "--framework",
        action="append",
        required=True,
        help="Framework ID (repeatable)",
    )
    check.add_argument(
        "--policies-dir",
        default="./governance-policies",
        help="Path to policies directory",
    )
    check.add_argument(
        "--format",
        choices=["json", "yaml", "markdown"],
        default="json",
        help="Output format",
    )
    check.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: one-line summary + exit code",
    )
    check.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures (exit 1)",
    )

    args = parser.parse_args()

    if args.command != "check":
        parser.print_help()
        sys.exit(0)

    # Load design
    try:
        with open(args.design_file) as f:
            design = yaml.safe_load(f)
    except FileNotFoundError:
        print(
            f"Error: File not found: {args.design_file}",
            file=sys.stderr,
        )
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML: {e}", file=sys.stderr)
        sys.exit(1)

    report = check_governance(
        design=design,
        frameworks=args.framework,
        policies_dir=args.policies_dir,
    )

    if args.ci:
        print(report.as_ci())
    elif args.format == "json":
        print(report.as_json())
    elif args.format == "yaml":
        print(report.as_yaml())
    elif args.format == "markdown":
        print(report.as_markdown())

    if args.strict:
        sys.exit(0 if report.is_strict_pass() else 1)
    else:
        sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
