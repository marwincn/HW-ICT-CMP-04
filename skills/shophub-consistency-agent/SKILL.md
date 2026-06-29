# ShopHub 设计实现一致性修复 Agent Skill

当任务是处理 ShopHub 软件大赛题目时使用本 Skill：对比 `design-docs/`、`README.md` 中冻结的 REST API 契约，以及 `code/` 下 Java Spring Boot 多模块实现，发现设计与实现的不一致，并只修复代码实现，不反向修改设计文档或冻结 API 契约。

## 目标

交付一组代码修改，使 ShopHub 的实现与设计文档保持一致，并保证项目可编译、可验证。每次执行结束时都应输出执行报告，说明读取了哪些文档、发现了哪些不一致、修复了哪些文件、运行了哪些验证命令，以及仍然存在的风险。

## 不可违反的规则

- `design-docs/` 是最终验收基准。
- 不得修改 `design-docs/`、`test-cases/`，也不得修改 `README.md` 冻结的 API URL、HTTP Method、请求字段、响应字段、字段类型和成功状态码。
- 不得为某个公开测试用例写硬编码逻辑。
- 不得暴露数据库 reset/bootstrap 接口。
- 不得修改 `/api/v1/` 前缀。
- 保持 Java 17 与 Spring Boot 3.2.6 兼容。

## 工作流程

1. **读取比赛上下文**
   - 阅读 `README.md` 第 3、5、6、7、8、9 节。
   - 阅读 `design-docs/` 中与任务相关的设计文档；如果是聚焦某个模块的修复，至少同时阅读该模块设计文档和以下通用文档：
     - `03-通用规范与非功能设计.md`
     - `附录A-API接口参考.md`
     - `附录B-配置参考.md`
     - `附录C-数据模型.md`
     - `附录D-本地事件契约.md`
   - 使用 `references/module-map.md` 将业务域映射到 Maven 模块和设计文档。

2. **先学习并扩展黑盒验收用例**
   - 在学习 `code/` 之前，先阅读 `test-cases/` 中已有公开黑盒测试，理解 fixture、认证、随机 `testRunId`、H2 隔离和只通过 REST API 构造/观察结果的方式。
   - 复制 `test-cases/` 为 `test-cases-new/`，不得修改原始 `test-cases/`。
   - 使用 `scripts/extract_api_contract.py` 从 `README.md` 抽取包含 6.8 管理接口在内的完整 REST API 基线，生成 Markdown 检查清单。
   - 以 `design-docs/` 全部规格和 README REST API 契约为准，在 `test-cases-new/` 中补齐全量黑盒测试用例；新增用例必须继续只通过 REST API 创建前置条件和观察结果。
   - `test-cases-new/` 是最终结果验收标准，最终交付前必须以 `mvn -s maven-settings.xml -f test-cases-new/pom.xml test` 全部通过为目标。

3. **建立 API 与行为检查清单**
   - 将 `test-cases-new/` 中的用例覆盖矩阵、Controller、DTO、HTTP 成功状态码、错误码和认证要求逐项对照 README 检查清单。
   - 对业务行为使用 `references/common-patterns.md` 中沉淀的常见缺陷模式进行排查。

4. **检查实现**
   - 使用 `rg` 搜索代码，不使用递归 `grep`。
   - 先检查 Controller，再检查 Service、领域模型、Repository 和配置。
   - 新增公共能力前，先检查 `ecommerce-common` 是否已有共享类，避免重复实现。

5. **只修复代码实现**
   - 优先做最小、设计驱动的补丁。
   - 只有在服务于设计一致性时，才新增或更新 DTO、Service、配置、事件和测试。
   - 保持 API 响应结构稳定；如果 Controller 返回 `ResponseEntity`，必须显式设置 `README.md` 中约定的成功状态码。
   - 使用设计文档和 README 中定义的错误码与 HTTP 状态映射。

6. **验证**
   - 先运行最小范围的相关测试。
   - 最终提交前，在可行时运行：
     ```bash
     mvn -s maven-settings.xml -f code/pom.xml test
     mvn -s maven-settings.xml -f code/pom.xml install -DskipTests
     mvn -s maven-settings.xml -f test-cases/pom.xml test
     mvn -s maven-settings.xml -f test-cases-new/pom.xml test
     ```
   - 如果网络、Maven 镜像或依赖下载导致命令无法完成，需要在报告中标记为环境限制。

7. **输出报告**
   - 使用 `scripts/generate_report.py` 生成执行报告，或按同样结构手写报告。
   - 报告必须包含：范围、检查依据、发现的不一致、修复内容、验证结果、残余风险。

## 执行报告模板

```markdown
# ShopHub 设计实现一致性执行报告

## 范围
- 已检查模块/功能：
- 使用的设计文档：
- 使用的 README 契约章节：

## 发现与修复
| 编号 | 设计/API 期望 | 实现不一致 | 修复方式 | 变更文件 |
|------|---------------|------------|----------|----------|

## 验证
| 命令 | 结果 | 说明 |
|------|------|------|

## 残余风险
- 
```

## Reference 文件

- `references/module-map.md`：业务域、代码模块和设计文档映射。
- `references/common-patterns.md`：常见不一致模式和修复方向。
- `references/report-checklist.md`：最终报告前的自检清单。

## 辅助脚本

- `scripts/extract_api_contract.py`：解析 README API 表格（含 6.8 管理接口）并生成检查清单。
- `scripts/generate_report.py`：根据 JSON 或命令行字段生成报告脚手架。

## Skill 效果对比评估

当需要证明本 Skill 的价值时，使用 `references/ab-evaluation.md` 中的 A/B 对比方案：

1. 在两个干净分支或工作区中执行同一批比赛任务，A 组不加载本 Skill，B 组严格按本 Skill 执行。
2. 两组都必须记录相同格式的执行报告，包括检查范围、发现数量、修复数量、验证命令、失败原因和残余风险。
3. 使用 `scripts/compare_runs.py` 汇总两份 JSON 结果，从 API 契约覆盖率、设计文档覆盖率、缺陷发现率、修复有效性、测试通过情况、违规风险、报告完整度和耗时等维度对比。
4. 对比结论应以测试结果和报告证据为准，不用主观印象替代数据。
