#!/usr/bin/env python3
"""从 README.md 抽取 ShopHub 冻结 REST API 契约。

脚本会扫描 README 的 API 基线表格，并输出便于逐个 Controller
核对的一份 Markdown 检查清单。
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

API_ROW_WITH_AUTH = re.compile(
    r"^\|\s*(GET|POST|PUT|DELETE|PATCH)\s*\|\s*(`[^`]+`)\s*\|\s*([^|]+?)\s*\|\s*(\d{3})\s*(?:\|.*)?$"
)
API_ROW_WITHOUT_AUTH = re.compile(
    r"^\|\s*(GET|POST|PUT|DELETE|PATCH)\s*\|\s*(`[^`]+`)\s*\|\s*(\d{3})\s*\|.*$"
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
        row_match = API_ROW_WITH_AUTH.match(raw_line.strip())
        if row_match:
            method, url, auth, status = row_match.groups()
        else:
            row_match = API_ROW_WITHOUT_AUTH.match(raw_line.strip())
            if not row_match:
                continue
            method, url, status = row_match.groups()
            auth = "ADMIN" if "管理接口" in current_section else "未标注"
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
    lines = ["# 冻结 API 契约检查清单", ""]
    last_section = None
    for row in rows:
        if row["section"] != last_section:
            last_section = row["section"]
            lines.extend([f"## {last_section}", ""])
        lines.append(
            f"- [ ] `{row['method']}` `{row['url']}` — 认证：{row['auth']}；成功状态码：{row['status']}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", nargs="?", default="README.md", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="可选的 Markdown 输出文件")
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
