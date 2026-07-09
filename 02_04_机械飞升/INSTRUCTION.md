# ShopHub 设计实现一致性修复 Skill 运行入口

本作品提交的是一个 Codex Skill：`shophub-consistency-agent`。平台加载本文件后，请按以下步骤验证作品可用性。

## 1. 加载 Skill

将 `work/skills/shophub-consistency-agent/` 作为 Skill 目录加载，入口文件为：

```text
work/skills/shophub-consistency-agent/SKILL.md
```

## 2. 适用任务

当任务要求检查并修复 ShopHub 电商系统中 `design-docs/`、`README.md` 冻结 REST API 契约与 `code/` Java Spring Boot 多模块实现之间的不一致时，启用该 Skill。

## 3. 推荐执行流程

1. 阅读 `work/skills/shophub-consistency-agent/SKILL.md`。
2. 按 Skill 中的工作流程读取比赛上下文、建立 API 与行为检查清单、检查实现并只修复代码实现。
3. 需要抽取 API 契约时运行：

   ```bash
   python3 work/skills/shophub-consistency-agent/scripts/extract_api_contract.py README.md
   ```

4. 需要生成执行报告脚手架时运行：

   ```bash
   python3 work/skills/shophub-consistency-agent/scripts/generate_report.py --help
   ```

5. 完成修复后，优先运行 Skill 建议的验证命令：

   ```bash
   mvn -s maven-settings.xml -f code/pom.xml test
   mvn -s maven-settings.xml -f code/pom.xml install -DskipTests
   mvn -s maven-settings.xml -f test-cases/pom.xml test
   ```

## 4. 输出要求

执行结束时按 Skill 的执行报告模板输出报告，至少包含：范围、检查依据、发现的不一致、修复内容、验证结果与残余风险。
