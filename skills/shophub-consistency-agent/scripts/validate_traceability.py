#!/usr/bin/env python3
"""校验 ShopHub 规格到测试的追踪完整性和黑盒测试基本有效性。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALID_COVERAGE_TYPES = {"blackbox", "unit", "architecture", "routing"}
HTTP_MARKERS = ("apiClient", "TestRestTemplate", ".exchange(", ".getForEntity(", ".postForEntity(")
ASSERT_MARKERS = ("assert", "Assertions.", "assertThat")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_test(root: Path, reference: str) -> tuple[Path, str]:
    file_name, separator, method = reference.partition("#")
    path = Path(file_name)
    if path.parts and path.parts[0] == root.name:
        path = Path(*path.parts[1:])
    return root / path, method if separator else ""


def method_body(content: str, method: str) -> str:
    """返回简单 Java 测试方法的声明和方法体。"""
    if not method:
        return ""
    marker = content.find(method + "(")
    if marker < 0:
        return ""
    start = content.find("{", marker)
    if start < 0:
        return ""
    depth = 0
    for index in range(start, len(content)):
        if content[index] == "{":
            depth += 1
        elif content[index] == "}":
            depth -= 1
            if depth == 0:
                return content[marker:index + 1]
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-contract", required=True, type=Path)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--specs", required=True, type=Path)
    parser.add_argument("--traceability", required=True, type=Path)
    parser.add_argument("--tests-root", required=True, type=Path)
    args = parser.parse_args()

    api = load_json(args.api_contract)
    candidates = load_json(args.candidates)
    specs = load_json(args.specs)
    traceability = load_json(args.traceability)
    errors: list[str] = []

    api_items = {item["id"]: item for item in api.get("endpoints", [])}
    api_ids = set(api_items)
    candidate_items = {item["id"]: item for item in candidates.get("requirements", [])}
    reviewed_items = {item["id"]: item for item in specs.get("requirements", [])}
    missing_reviews = set(candidate_items) - set(reviewed_items)
    extra_reviews = set(reviewed_items) - set(candidate_items)
    for requirement_id in sorted(missing_reviews):
        errors.append(f"设计候选未进入审核清单：{requirement_id}")
    for requirement_id in sorted(extra_reviews):
        errors.append(f"审核清单包含未知设计候选：{requirement_id}")
    for requirement_id, item in reviewed_items.items():
        status = item.get("status")
        if status not in {"required", "informational"}:
            errors.append(f"设计候选尚未完成审核：{requirement_id} ({status})")
        if status == "informational" and not str(item.get("reason", "")).strip():
            errors.append(f"informational 规格缺少理由：{requirement_id}")
    spec_ids = {
        item["id"]
        for item in reviewed_items.values()
        if item.get("status") == "required"
    }
    required_ids = api_ids | spec_ids

    mappings_by_id: dict[str, list[dict[str, Any]]] = {}
    for mapping in traceability.get("mappings", []):
        requirement_id = mapping.get("requirement_id", "")
        mappings_by_id.setdefault(requirement_id, []).append(mapping)

    unknown = set(mappings_by_id) - required_ids
    for requirement_id in sorted(unknown):
        errors.append(f"追踪项引用未知或非 required 规格：{requirement_id}")

    for requirement_id in sorted(required_ids):
        mappings = mappings_by_id.get(requirement_id, [])
        if not mappings:
            errors.append(f"缺少规格映射：{requirement_id}")
            continue
        if requirement_id in api_ids and not any(
            mapping.get("coverage_type") == "blackbox" for mapping in mappings
        ):
            errors.append(f"REST 契约必须具有 blackbox 覆盖：{requirement_id}")

        for mapping in mappings:
            coverage_type = mapping.get("coverage_type")
            if coverage_type not in VALID_COVERAGE_TYPES:
                errors.append(f"{requirement_id} 使用非法覆盖类型：{coverage_type}")
                continue
            tests = mapping.get("tests", [])
            evidence = mapping.get("evidence", [])
            if coverage_type != "routing" and not evidence:
                errors.append(f"{requirement_id} 没有规格专属 evidence")
            if not tests:
                errors.append(f"{requirement_id} 没有测试引用")
                continue
            for reference in tests:
                test_path, method = resolve_test(args.tests_root, reference)
                if not test_path.is_file():
                    errors.append(f"测试文件不存在：{reference}")
                    continue
                content = test_path.read_text(encoding="utf-8")
                body = method_body(content, method)
                if method and not body:
                    errors.append(f"测试方法不存在：{reference}")
                    continue
                if requirement_id not in body:
                    errors.append(f"测试方法体未引用规格 ID {requirement_id}：{reference}")
                for marker in evidence:
                    if str(marker) not in body:
                        errors.append(f"测试方法体缺少 evidence `{marker}`：{reference}")
                if coverage_type == "blackbox":
                    declaration_prefix = content[max(0, content.rfind("\n", 0, content.find(method)) - 200):content.find(method)]
                    if "@Test" not in declaration_prefix and "@ParameterizedTest" not in declaration_prefix:
                        errors.append(f"黑盒文件没有测试入口：{reference}")
                    if not any(marker in body for marker in HTTP_MARKERS):
                        errors.append(f"黑盒测试未识别到真实 HTTP 调用：{reference}")
                    if not any(marker in body for marker in ASSERT_MARKERS):
                        errors.append(f"黑盒测试未识别到断言：{reference}")
                    if requirement_id in api_ids:
                        expected = api_items[requirement_id]["success_status"]
                        if mapping.get("expected_status") != expected:
                            errors.append(
                                f"REST 契约成功状态码未精确映射：{requirement_id}，应为 {expected}"
                            )
                        if api_items[requirement_id]["path"] not in [str(item) for item in evidence]:
                            errors.append(f"REST 契约 evidence 缺少具体路径：{requirement_id}")

    covered = len(required_ids) - len(
        {error.split("：", 1)[1] for error in errors if error.startswith("缺少规格映射：")}
    )
    print(f"冻结 REST 契约：{len(api_ids)}")
    print(f"必验设计规格：{len(spec_ids)}")
    print(f"已建立映射：{covered}/{len(required_ids)}")
    if errors:
        print(f"校验失败，共 {len(errors)} 项：")
        for error in errors:
            print(f"- {error}")
        return 1
    print("追踪校验通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
