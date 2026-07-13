#!/usr/bin/env python3
"""从 ShopHub 设计文档提取可审核的规格候选清单。"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

HEADING = re.compile(r"^(#{2,4})\s+(.+)$")
SECTION_NUMBER = re.compile(r"^(\d+(?:\.\d+)*)[.、\s]")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]\s+|\d+[.、]\s*)(.+)$")
TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
TABLE_SEPARATOR = re.compile(r"^\s*:?-{3,}:?\s*$")

CATEGORY_KEYWORDS = {
    "state-machine": ("状态", "流转", "转换", "终态"),
    "calculation": ("公式", "金额", "库存", "优惠", "积分", "运费", "税率", "舍入"),
    "authorization": ("认证", "权限", "角色", "归属", "冻结"),
    "event": ("事件", "监听", "通知", "失败记录", "重试"),
    "architecture": ("模块", "依赖", "Repository", "事务边界", "DTO"),
    "configuration": ("配置", "时钟", "故障注入", "限流", "TTL"),
    "persistence": ("数据", "字段", "表", "持久化", "唯一"),
    "rest-contract": ("REST", "API", "/api/v1/", "HTTP"),
}


def document_code(path: Path) -> str:
    number = re.match(r"(\d+)", path.name)
    if number:
        return f"D{int(number.group(1)):02d}"
    appendix = re.match(r"附录([A-Za-z])", path.name)
    if appendix:
        return f"APP{appendix.group(1).upper()}"
    return "DOC"


def section_code(title: str, fallback: int) -> str:
    match = SECTION_NUMBER.match(title)
    if match:
        return "S" + match.group(1).replace(".", "_")
    return f"S{fallback}"


def classify(text: str) -> str:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category
    return "business-rule"


def clean_table_row(line: str) -> str | None:
    match = TABLE_ROW.match(line)
    if not match:
        return None
    cells = [cell.strip().strip("`") for cell in match.group(1).split("|")]
    if not cells or all(not cell for cell in cells):
        return None
    if all(TABLE_SEPARATOR.match(cell) for cell in cells if cell):
        return None
    return "；".join(cell for cell in cells if cell)


def extract_file(path: Path, root: Path) -> list[dict[str, Any]]:
    document = document_code(path)
    section = "S0"
    section_title = "文档说明"
    section_index = 0
    ordinals: defaultdict[str, int] = defaultdict(int)
    requirements: list[dict[str, Any]] = []

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        heading = HEADING.match(raw_line.strip())
        if heading:
            section_index += 1
            section_title = heading.group(2).strip()
            section = section_code(section_title, section_index)
            continue

        list_match = LIST_ITEM.match(raw_line)
        description = list_match.group(1).strip() if list_match else clean_table_row(raw_line)
        if not description or len(description) < 4:
            continue

        ordinals[section] += 1
        requirement_id = f"{document}-{section}-R{ordinals[section]:03d}"
        requirements.append(
            {
                "id": requirement_id,
                "source": f"{root.name}/{path.relative_to(root).as_posix()}#L{line_number}",
                "section": section_title,
                "category": classify(section_title + " " + description),
                "description": description,
                "status": "candidate",
                "reason": "待依据可观察性和验收边界审核",
            }
        )
    return requirements


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design_docs", nargs="?", default="design-docs", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="输出 JSON 文件；省略时写标准输出")
    args = parser.parse_args()

    paths = sorted(args.design_docs.glob("*.md"))
    if not paths:
        parser.error(f"{args.design_docs} 下没有设计文档")
    requirements: list[dict[str, Any]] = []
    for path in paths:
        requirements.extend(extract_file(path, args.design_docs))

    payload = {
        "source": args.design_docs.as_posix(),
        "candidate_count": len(requirements),
        "requirements": requirements,
    }
    output = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
