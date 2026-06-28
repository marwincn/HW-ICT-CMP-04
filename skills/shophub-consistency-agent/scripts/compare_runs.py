#!/usr/bin/env python3
"""对比“不使用 Skill”和“使用 Skill”两次执行结果。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("name", path.stem)
    return data


def ratio(data: dict[str, Any], numerator: str, denominator: str) -> float:
    total = float(data.get(denominator, 0) or 0)
    if total <= 0:
        return 0.0
    return float(data.get(numerator, 0) or 0) / total


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def value(data: dict[str, Any], key: str) -> Any:
    return data.get(key, 0)


def better_for_metric(metric: str, no_skill: dict[str, Any], with_skill: dict[str, Any]) -> str:
    higher_is_better = {
        "api_coverage",
        "design_doc_coverage",
        "findings",
        "fixes",
        "tests_passed",
        "report_completeness",
    }
    lower_is_better = {
        "tests_failed",
        "tests_not_run",
        "contract_violations",
        "modified_forbidden_files",
        "duration_minutes",
        "rework_count",
    }
    if metric == "api_coverage":
        a = ratio(no_skill, "api_checked", "api_total")
        b = ratio(with_skill, "api_checked", "api_total")
    elif metric == "design_doc_coverage":
        a = ratio(no_skill, "design_docs_checked", "design_docs_total")
        b = ratio(with_skill, "design_docs_checked", "design_docs_total")
    elif metric == "report_completeness":
        a = ratio(no_skill, "report_sections_present", "report_sections_total")
        b = ratio(with_skill, "report_sections_present", "report_sections_total")
    else:
        a = float(value(no_skill, metric) or 0)
        b = float(value(with_skill, metric) or 0)

    if a == b:
        return "持平"
    if metric in higher_is_better:
        return "使用 Skill 更优" if b > a else "不使用 Skill 更优"
    if metric in lower_is_better:
        return "使用 Skill 更优" if b < a else "不使用 Skill 更优"
    return "需人工判断"


def render(no_skill: dict[str, Any], with_skill: dict[str, Any]) -> str:
    rows = [
        ("API 契约覆盖率", "api_coverage", percent(ratio(no_skill, "api_checked", "api_total")), percent(ratio(with_skill, "api_checked", "api_total"))),
        ("设计文档覆盖率", "design_doc_coverage", percent(ratio(no_skill, "design_docs_checked", "design_docs_total")), percent(ratio(with_skill, "design_docs_checked", "design_docs_total"))),
        ("发现不一致数量", "findings", value(no_skill, "findings"), value(with_skill, "findings")),
        ("完成修复数量", "fixes", value(no_skill, "fixes"), value(with_skill, "fixes")),
        ("测试通过命令数", "tests_passed", value(no_skill, "tests_passed"), value(with_skill, "tests_passed")),
        ("测试失败命令数", "tests_failed", value(no_skill, "tests_failed"), value(with_skill, "tests_failed")),
        ("未运行命令数", "tests_not_run", value(no_skill, "tests_not_run"), value(with_skill, "tests_not_run")),
        ("契约违规数", "contract_violations", value(no_skill, "contract_violations"), value(with_skill, "contract_violations")),
        ("禁改文件变更数", "modified_forbidden_files", value(no_skill, "modified_forbidden_files"), value(with_skill, "modified_forbidden_files")),
        ("报告完整度", "report_completeness", percent(ratio(no_skill, "report_sections_present", "report_sections_total")), percent(ratio(with_skill, "report_sections_present", "report_sections_total"))),
        ("耗时（分钟）", "duration_minutes", value(no_skill, "duration_minutes"), value(with_skill, "duration_minutes")),
        ("返工次数", "rework_count", value(no_skill, "rework_count"), value(with_skill, "rework_count")),
    ]

    lines = [
        "# Skill 使用效果 A/B 对比报告",
        "",
        f"- A 组：{no_skill.get('name', '不使用 Skill')}",
        f"- B 组：{with_skill.get('name', '使用 Skill')}",
        "",
        "| 维度 | 不使用 Skill | 使用 Skill | 对比结论 |",
        "|------|--------------|------------|----------|",
    ]
    for label, metric, a, b in rows:
        lines.append(f"| {label} | {a} | {b} | {better_for_metric(metric, no_skill, with_skill)} |")

    lines.extend([
        "",
        "## 备注",
        f"- 不使用 Skill：{no_skill.get('notes', '无')}",
        f"- 使用 Skill：{with_skill.get('notes', '无')}",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("no_skill", type=Path, help="不使用 Skill 的执行结果 JSON")
    parser.add_argument("with_skill", type=Path, help="使用 Skill 的执行结果 JSON")
    parser.add_argument("-o", "--output", type=Path, help="可选的 Markdown 输出文件")
    args = parser.parse_args()

    report = render(load(args.no_skill), load(args.with_skill))
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
