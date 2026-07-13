#!/usr/bin/env python3
"""从 README.md 提取 ShopHub 冻结 REST 契约。

支持输出 Markdown 检查清单、JSON 规格清单或设计侧 OpenAPI JSON。
输出只依赖 README，不读取 Controller 或运行时接口。
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

API_ROW = re.compile(
    r"^\|\s*(GET|POST|PUT|DELETE|PATCH)\s*\|\s*(`[^`]+`)\s*\|\s*([^|]+?)\s*\|\s*(\d{3})\s*(?:\|.*)?$"
)
SUPPORT_API_ROW = re.compile(
    r"^\|\s*(GET|POST|PUT|DELETE|PATCH)\s*\|\s*(`[^`]+`)\s*\|\s*(\d{3})\s*\|\s*([^|]+?)\s*\|$"
)
SECTION = re.compile(r"^###\s+(6\.\d+)\s+(.+)$")


def extract(readme: Path) -> list[dict[str, Any]]:
    section_number = "6"
    section_name = "API"
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(readme.read_text(encoding="utf-8").splitlines(), 1):
        stripped = raw_line.strip()
        section_match = SECTION.match(stripped)
        if section_match:
            section_number, section_name = section_match.groups()
            section_name = section_name.strip()
            continue
        row_match = API_ROW.match(stripped)
        support_match = SUPPORT_API_ROW.match(stripped)
        if not row_match and not support_match:
            continue
        if row_match:
            method, url, auth, status = row_match.groups()
        else:
            method, url, status, _description = support_match.groups()
            auth = "ADMIN"
        rows.append(
            {
                "id": f"API-{len(rows) + 1:03d}",
                "section": section_name,
                "section_number": section_number,
                "method": method,
                "path": url.strip("`"),
                "auth": auth.strip(),
                "success_status": int(status),
                "source": f"{readme.as_posix()}#L{line_number}",
            }
        )
    return rows


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = ["# 冻结 API 契约检查清单", ""]
    last_section = None
    for row in rows:
        if row["section"] != last_section:
            last_section = row["section"]
            lines.extend([f"## {last_section}", ""])
        lines.append(
            f"- [ ] `{row['id']}` `{row['method']}` `{row['path']}` — "
            f"认证：{row['auth']}；成功状态码：{row['success_status']}"
        )
    lines.extend(["", f"共 {len(rows)} 个冻结接口。", ""])
    return "\n".join(lines)


def render_json(rows: list[dict[str, Any]], readme: Path) -> str:
    payload = {
        "source": readme.as_posix(),
        "endpoint_count": len(rows),
        "endpoints": rows,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def security_for(auth: str) -> list[dict[str, list[str]]]:
    if auth == "匿名":
        return []
    if auth == "签名":
        # README 只冻结“签名”认证，未为所有回调统一冻结头名称。
        # 不虚构头部；由附录和具体设计审核后补全。
        return []
    return [{"bearerAuth": []}]


def render_openapi(rows: list[dict[str, Any]]) -> str:
    paths: dict[str, Any] = {}
    for row in rows:
        operation: dict[str, Any] = {
            "operationId": row["id"].lower().replace("-", "_"),
            "summary": f"{row['section']}：{row['method']} {row['path']}",
            "tags": [row["section"]],
            "security": security_for(row["auth"]),
            "responses": {
                str(row["success_status"]): {
                    "description": f"设计规定的成功响应 {row['success_status']}"
                }
            },
            "x-shophub-spec-id": row["id"],
            "x-shophub-auth": row["auth"],
            "x-shophub-source": row["source"],
        }
        paths.setdefault(row["path"], {})[row["method"].lower()] = operation

    document = {
        "openapi": "3.1.0",
        "info": {
            "title": "ShopHub 设计侧冻结 REST 契约",
            "version": "1.0.0",
            "description": "由 README 冻结契约生成；请求和响应结构需继续依据设计附录 A 审核补全。",
        },
        "paths": paths,
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            }
        },
    }
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", nargs="?", default="README.md", type=Path)
    parser.add_argument(
        "--format",
        choices=("markdown", "json", "openapi"),
        default="markdown",
        help="输出格式，默认 markdown",
    )
    parser.add_argument("-o", "--output", type=Path, help="输出文件；省略时写到标准输出")
    args = parser.parse_args()

    rows = extract(args.readme)
    if not rows:
        parser.error(f"未在 {args.readme} 中找到冻结 API 契约")

    if args.format == "json":
        output = render_json(rows, args.readme)
    elif args.format == "openapi":
        output = render_openapi(rows)
    else:
        output = render_markdown(rows)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
