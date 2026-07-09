# Skill A/B 效果对比方案

本方案用于分别评估“不使用 Skill”和“使用本 Skill”执行 ShopHub 比赛任务的最终效果，确保结论可复现、可量化、可审计。

## 实验目标

比较两种执行方式在以下维度上的差异：

| 维度 | 含义 | 推荐度量 |
|------|------|----------|
| API 契约覆盖率 | 是否系统性检查 README 冻结 API | 已检查端点数 / README 端点总数 |
| 设计文档覆盖率 | 是否读取并引用相关设计文档 | 已检查设计文档数、关键附录覆盖情况 |
| 缺陷发现能力 | 是否发现设计与实现不一致 | 发现的不一致数量、按模块分布 |
| 修复有效性 | 修复是否真实改善行为 | 已修复问题数、修复后通过的测试数 |
| 契约违规风险 | 是否误改设计、测试或冻结 API | 违规文件数、API 形态变更数 |
| 验证充分性 | 是否按 README 推荐命令验证 | 成功/失败/未运行命令数 |
| 报告完整度 | 是否输出可审计执行报告 | 范围、依据、发现、修复、验证、风险是否齐全 |
| 执行效率 | 是否减少遗漏与返工 | 总耗时、返工次数、无效搜索次数 |

## 实验准备

1. 从同一个基线 commit 创建两个干净工作区：
   - A 组：不使用 Skill，只依据用户原始要求和仓库文件完成任务。
   - B 组：加载 `skills/shophub-consistency-agent/SKILL.md`，并按其工作流程完成任务。
2. 两组使用相同的环境变量、JDK、Maven、网络和时间预算。
3. 两组不得互相查看对方的中间结果。
4. 两组都不得修改 `design-docs/` 和 `test-cases/`。

## 执行步骤

### A 组：不使用 Skill

1. 阅读用户任务和仓库文档，自行决定检查顺序。
2. 修复发现的问题。
3. 运行可行的 Maven 验证命令。
4. 输出 JSON 格式的执行摘要，字段见“结果 JSON 格式”。

### B 组：使用 Skill

1. 阅读 `SKILL.md` 的不可违反规则和工作流程。
2. 使用 `extract_api_contract.py` 生成 README API 检查清单。
3. 结合 `module-map.md`、`common-patterns.md` 和 `report-checklist.md` 排查并修复问题。
4. 运行同样的 Maven 验证命令。
5. 输出同一 JSON 格式的执行摘要。

## 结果 JSON 格式

```json
{
  "name": "使用 Skill",
  "duration_minutes": 120,
  "api_total": 72,
  "api_checked": 72,
  "design_docs_total": 18,
  "design_docs_checked": 18,
  "findings": 15,
  "fixes": 13,
  "tests_passed": 3,
  "tests_failed": 0,
  "tests_not_run": 0,
  "contract_violations": 0,
  "modified_forbidden_files": 0,
  "report_sections_present": 6,
  "report_sections_total": 6,
  "rework_count": 1,
  "notes": "示例"
}
```

## 对比命令

```bash
python3 skills/shophub-consistency-agent/scripts/compare_runs.py no_skill.json with_skill.json
```

## 结论判定建议

- 如果 B 组 API 契约覆盖率、设计文档覆盖率、报告完整度更高，且契约违规风险不高于 A 组，说明 Skill 对规范性和审计性有明显帮助。
- 如果 B 组测试通过数更多、失败数更少，说明 Skill 对修复有效性有帮助。
- 如果 B 组耗时略高但遗漏更少，应在结论中说明这是“前期结构化检查换取后期返工减少”。
- 如果 B 组耗时更低且质量更高，说明 Skill 的模块映射、固定模式和脚本显著减少了探索成本。
