#!/usr/bin/env python3
"""Extract the frozen ShopHub REST API contract from README.md.

The script scans README API baseline tables and emits a Markdown checklist that
is convenient for controller-by-controller consistency review.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

API_ROW = re.compile(
    r"^\|\s*(GET|POST|PUT|DELETE|PATCH)\s*\|\s*(`[^`]+`)\s*\|\s*([^|]+?)\s*\|\s*(\d{3})\s*(?:\|.*)?$"
)
SECTION = re.compile(r"^###\s+6\.\d+\s+(.+)$")


def extract(readme: Path) -> list[dict[str, str]]:
    current_section = "API"
    rows: list[dict[str, str]] = []
    for raw_line in readme.read_text(encoding="utf-8").splitlines():
        section_match = SECTION.match(raw_line.strip())
        if section_match:
            current_section = section_match.group(1).strip()
            continue
        row_match = API_ROW.match(raw_line.strip())
        if not row_match:
            continue
        method, url, auth, status = row_match.groups()
        rows.append(
            {
                "section": current_section,
                "method": method,
                "url": url.strip("`"),
                "auth": auth.strip(),
                "status": status,
            }
        )
    return rows


def render_markdown(rows: list[dict[str, str]]) -> str:
    lines = ["# Frozen API Contract Checklist", ""]
    last_section = None
    for row in rows:
        if row["section"] != last_section:
            last_section = row["section"]
            lines.extend([f"## {last_section}", ""])
        lines.append(
            f"- [ ] `{row['method']}` `{row['url']}` — auth: {row['auth']}; success: {row['status']}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", nargs="?", default="README.md", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="Optional output Markdown file")
    args = parser.parse_args()

    rows = extract(args.readme)
    output = render_markdown(rows)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
