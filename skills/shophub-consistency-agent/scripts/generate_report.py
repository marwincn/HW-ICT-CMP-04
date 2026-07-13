#!/usr/bin/env python3
"""生成 ShopHub 规格驱动黑盒验收与一致性修复报告脚手架。"""

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
    return "\n".join(f"- {item}" for item in items) if items else "- 未记录"


def render(data: dict[str, Any]) -> str:
    findings = data.get("findings", [])
    validations = data.get("validations", [])

    lines = [
        "# ShopHub 规格驱动黑盒验收与一致性修复报告",
        "",
        "## 范围",
        "- 已检查模块/功能：",
        bullet(data.get("modules", [])),
        "- 使用的设计文档：",
        bullet(data.get("docs", [])),
        "- 使用的 README 契约章节：",
        bullet(data.get("readme_sections", [])),
        "",
        "## 原始黑盒探索",
        "- 已探索的原始用例：",
        bullet(data.get("original_blackbox_cases", [])),
        "- 发现的覆盖缺口：",
        bullet(data.get("coverage_gaps", [])),
        "",
        "## test-case-new 新增验收覆盖",
        "| 指标 | 数量 |",
        "|------|------|",
        f"| 冻结 REST 接口 | {data.get('frozen_api_count', '未记录')} |",
        f"| 可验证设计规格 | {data.get('required_spec_count', '未记录')} |",
        f"| 原始黑盒已覆盖规格 | {data.get('original_covered_count', '未记录')} |",
        f"| 新增黑盒已覆盖规格 | {data.get('new_covered_count', '未记录')} |",
        f"| 仍缺少验收的规格 | {data.get('uncovered_count', '未记录')} |",
        "",
        "- 新增黑盒用例：",
        bullet(data.get("new_blackbox_cases", [])),
        "- 覆盖的规格与契约：",
        bullet(data.get("new_blackbox_contracts", [])),
        "",
        "## 发现与修复",
        "| 编号 | 设计/API 期望 | 实现不一致 | 修复方式 | 变更文件 |",
        "|------|---------------|------------|----------|----------|",
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
        "## 验证",
        "| 命令 | 结果 | 说明 |",
        "|------|------|------|",
    ])
    if validations:
        for item in validations:
            lines.append(
                f"| `{item.get('command', '')}` | {item.get('result', '')} | {item.get('notes', '')} |"
            )
    else:
        lines.append("| TBD | TBD | TBD |")

    lines.extend(["", "## 残余风险", bullet(data.get("risks", [])), ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="JSON file with report fields")
    parser.add_argument("--modules", help="逗号分隔的模块/功能")
    parser.add_argument("--docs", help="逗号分隔的设计文档")
    parser.add_argument("--readme-sections", help="逗号分隔的 README 章节")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    if args.json:
        data = json.loads(args.json.read_text(encoding="utf-8"))
    else:
        data = {
            "modules": as_list(args.modules),
            "docs": as_list(args.docs),
            "readme_sections": as_list(args.readme_sections),
            "original_blackbox_cases": [],
            "coverage_gaps": [],
            "new_blackbox_cases": [],
            "new_blackbox_contracts": [],
            "frozen_api_count": "未记录",
            "required_spec_count": "未记录",
            "original_covered_count": "未记录",
            "new_covered_count": "未记录",
            "uncovered_count": "未记录",
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
