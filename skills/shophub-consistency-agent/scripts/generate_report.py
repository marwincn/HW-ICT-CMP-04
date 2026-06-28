#!/usr/bin/env python3
"""Generate a ShopHub consistency execution report scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def as_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- Not recorded"


def render(data: dict[str, Any]) -> str:
    findings = data.get("findings", [])
    validations = data.get("validations", [])

    lines = [
        "# ShopHub Consistency Execution Report",
        "",
        "## Scope",
        "- Modules/features inspected:",
        bullet(data.get("modules", [])),
        "- Design documents used:",
        bullet(data.get("docs", [])),
        "- README contract sections used:",
        bullet(data.get("readme_sections", [])),
        "",
        "## Findings and Fixes",
        "| ID | Design/API expectation | Implementation mismatch | Fix | Files changed |",
        "|----|------------------------|-------------------------|-----|---------------|",
    ]
    if findings:
        for item in findings:
            lines.append(
                "| {id} | {expectation} | {mismatch} | {fix} | {files} |".format(
                    id=item.get("id", ""),
                    expectation=item.get("expectation", ""),
                    mismatch=item.get("mismatch", ""),
                    fix=item.get("fix", ""),
                    files=", ".join(item.get("files", [])),
                )
            )
    else:
        lines.append("| TBD | TBD | TBD | TBD | TBD |")

    lines.extend([
        "",
        "## Validation",
        "| Command | Result | Notes |",
        "|---------|--------|-------|",
    ])
    if validations:
        for item in validations:
            lines.append(
                f"| `{item.get('command', '')}` | {item.get('result', '')} | {item.get('notes', '')} |"
            )
    else:
        lines.append("| TBD | TBD | TBD |")

    lines.extend(["", "## Residual Risks", bullet(data.get("risks", [])), ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="JSON file with report fields")
    parser.add_argument("--modules", help="Comma-separated modules/features")
    parser.add_argument("--docs", help="Comma-separated design documents")
    parser.add_argument("--readme-sections", help="Comma-separated README sections")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    if args.json:
        data = json.loads(args.json.read_text(encoding="utf-8"))
    else:
        data = {
            "modules": as_list(args.modules),
            "docs": as_list(args.docs),
            "readme_sections": as_list(args.readme_sections),
            "findings": [],
            "validations": [],
            "risks": [],
        }

    report = render(data)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
