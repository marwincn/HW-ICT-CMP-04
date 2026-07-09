# 作品自验证输出

## 交付件检查

- 已按要求创建 `INSTRUCTION.md` 作为作品运行入口。
- 已将 Skill 放入 `work/skills/shophub-consistency-agent/`，并保留 `SKILL.md`、`references/`、`scripts/`、`reports/` 等完整内容。
- 已创建 `result/`、`logs/`、`logs/trace/` 等必选目录。
- `logs/interaction.md` 已创建；本次打包过程无人工交互干预。

## 运行成功信息

作品可通过加载 `work/skills/shophub-consistency-agent/SKILL.md` 使用。该 Skill 会指导 Agent 对 ShopHub 设计文档、README 冻结 API 契约与 Java 实现进行一致性检查和修复，并在结束时生成执行报告。
