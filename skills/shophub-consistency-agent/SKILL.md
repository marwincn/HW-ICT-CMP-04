---
name: shophub-consistency-agent
description: 审查并修复 ShopHub 软件大赛代码，使 Java 17 与 Spring Boot 3.2.6 实现符合 design-docs/ 中的设计规格、README.md 中冻结的 REST API 契约，以及基于这些规格生成到 test-case-new/ 的新增黑盒验收用例。当 Codex 需要从设计和接口契约推导黑盒测试、保护原始 test-cases/ 不被修改、定位或修复契约、DTO、状态码、认证、业务规则、持久化、事件、配置或测试隔离问题时使用。
---

# ShopHub 规格驱动黑盒验收与一致性修复

先从 `design-docs/` 和 `README.md` 建立规格与 REST 契约基线，再参考原始 `test-cases/` 的测试风格生成新的 `test-case-new/` 黑盒验收用例，最后以 `test-case-new/` 作为最终验收标准驱动 `code/` 下实现和实现侧单元测试修复。

## 保护不可变约束

- 不得修改 `design-docs/` 或 `test-cases/`。
- 可以创建和修改 `test-case-new/`，但不得从 `test-cases/` 直接移动、覆盖或改写原始比赛用例。
- 不得修改 `README.md` 中冻结的 API URL、HTTP 方法、请求或响应字段、字段类型、成功状态码及 `/api/v1/` 前缀。
- 不得为单个公开测试硬编码行为。
- 不得暴露数据库重置或初始化接口。
- 保持 Java 17 与 Spring Boot 3.2.6 兼容。
- 保留工作树中与任务无关的用户改动。

编辑前检查 `git status --short`。编辑后检查差异；如果本次修复改动了受保护文件，则停止交付并撤销相应改动。`test-case-new/` 是本 Skill 生成的验收资产，不属于禁改目录。

## 阶段一：建立规格与接口契约基线

1. 阅读 `README.md` 第 3、5、6、7、8 和 9 节。
2. 阅读 `design-docs/` 下与目标业务域相关的设计文档；全量验收时覆盖所有业务域设计文档。
3. 同时阅读适用的通用文档：
   - `03-通用规范与非功能设计.md`
   - `附录A-API接口参考.md`
   - `附录B-配置参考.md`
   - `附录C-数据模型.md`
   - `附录D-本地事件契约.md`
4. 阅读 [references/module-map.md](references/module-map.md)，将业务域映射到 Maven 模块和设计文档。
5. 运行 `scripts/extract_api_contract.py README.md` 生成冻结接口检查清单。除非用户要求保留产物，否则将输出写入临时路径。

按以下优先级消除歧义：README 中明确冻结的 API 契约、相关业务设计文档、通用设计附录、当前实现。遇到真实矛盾时如实报告，不得自行虚构契约。

基线产出必须能回答：

- 每个公开 REST 端点的路径、方法、认证、请求字段、响应字段、成功状态码和错误码；
- 每个业务域的核心状态机、金额/库存公式、权限边界、事件副作用和可测试配置；
- 哪些行为已被原始 `test-cases/` 覆盖，哪些设计规格和契约仍缺少黑盒覆盖。

## 阶段二：探索原始黑盒用例

只读探索 `test-cases/`，目的是学习测试工程结构和已有覆盖，不得修改其文件。

1. 识别 `test-cases/pom.xml`、测试启动类、基础测试工具、认证辅助、数据构造方式和断言风格。
2. 列出每个原始黑盒用例覆盖的 REST 端点、业务场景、正向路径、异常路径和断言点。
3. 将覆盖情况与阶段一的规格与契约清单对齐，形成缺口清单。
4. 保留原始用例作为兼容性回归验证，但不把它作为新增测试资产的编辑目标。

## 阶段三：生成 `test-case-new` 黑盒验收用例

阅读 [references/blackbox-generation.md](references/blackbox-generation.md)，然后创建或更新 `test-case-new/`。

生成规则：

- 参考 `test-cases/` 的 Maven 结构、Spring Boot 黑盒启动方式、数据隔离方式和断言风格。
- 从阶段一的设计规格与 REST 契约推导测试，不从当前实现反推期望。
- 覆盖所有公开 REST 契约；对复杂业务域至少覆盖一个正向场景、一个权限或状态冲突场景、一个关键边界场景。
- 对设计文档中的金额公式、库存公式、状态机、事件失败记录、运行时配置、故障注入和测试时钟生成明确断言。
- 每个测试类顶部或测试方法名应能体现对应规格来源；避免把规格解释藏在实现细节里。
- 不复制 `test-cases/` 的整段源码；可以复用公开测试工程的依赖、启动参数、辅助模式和断言习惯。

生成后先运行 `mvn -s maven-settings.xml -f test-case-new/pom.xml test`。如果新增用例本身无法编译或启动，优先修复 `test-case-new/` 的测试工程问题；如果用例失败反映实现不符合规格，则进入阶段四。

## 阶段四：审查并修复实现

使用 `rg` 搜索，并按以下顺序审查：

1. 将接口映射到 Controller，对比路径、方法、认证、DTO 字段、JSON 类型和成功状态码。
2. 从每个受影响的 Controller 追踪到 Service、领域模型、Repository、事件和配置。
3. 检查资源归属、授权、状态流转、计算逻辑、持久化默认值、事务边界和异常映射。
4. 新增共享行为前先检查 `ecommerce-common`。
5. 阅读 [references/common-patterns.md](references/common-patterns.md)，排查与目标业务域相关的 ShopHub 特有缺陷模式。

不得将聚焦修复扩大为全仓库重写。除非无关问题阻塞目标行为，否则将其记录为残余风险。

## 阶段五：实施修复与 UT 同步

- 实施能够恢复契约的最小设计驱动补丁。
- 仅在契约要求时新增或更新 DTO、Service、配置、事件和实现侧测试。
- 返回 `ResponseEntity` 时显式设置成功状态码。
- 使用文档定义的业务错误码和 HTTP 映射。
- 修复无效状态的根因，不得用补偿逻辑掩盖问题。
- 存在合适的实现侧测试模块时添加回归测试；不得编辑公开黑盒测试。
- 每修复一个黑盒失败，都同步补充或更新对应模块的 UT，确保单元层能锁定根因。

## 阶段六：反复验收

按“新增黑盒失败 → 修复源代码 → 同步 UT → 重新运行相关测试”的循环推进，直到 `test-case-new/` 黑盒用例全部通过。先运行范围最小的相关测试。在条件允许时，再运行以下命令：

```bash
mvn -s maven-settings.xml -f code/pom.xml test
mvn -s maven-settings.xml -f code/pom.xml install -DskipTests
mvn -s maven-settings.xml -f test-cases/pom.xml test
mvn -s maven-settings.xml -f test-case-new/pom.xml test
```

最终验收标准是 `test-case-new/` 全部通过，同时原始 `test-cases/` 不回退。将依赖、网络或 Maven 镜像失败记录为环境限制。不得将未执行或受阻的命令报告为通过。结束前重新检查 `git diff --name-only`，并使用 [references/report-checklist.md](references/report-checklist.md) 完成自检。

## 报告结果

报告必须包含：

- 检查范围和已读取的契约来源；
- 原始 `test-cases/` 覆盖探索结论；
- `test-case-new/` 新增黑盒用例覆盖的设计规格和 REST 契约；
- 每项不一致、期望行为、修复方式和变更文件；
- 每条验证命令及其实际结果；
- 剩余风险和环境限制。

用户要求生成可复用的 Markdown 产物时，使用 `scripts/generate_report.py`；否则直接在最终回复中提供同等信息。
