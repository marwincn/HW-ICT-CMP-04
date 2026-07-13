---
name: shophub-consistency-agent
description: 审查并修复 ShopHub 软件大赛代码，使 Java 17 与 Spring Boot 3.2.6 实现符合 design-docs/ 的设计规格和 README.md 的冻结 REST API 契约。用于从规格建立可追踪清单和设计侧契约、只读分析 test-cases/、在 test-case-new/ 生成真实 HTTP 黑盒验收、检查状态机、公式、权限、事件和模块边界，并以失败用例驱动源代码及 UT 修复直至全部验收通过。
---

# ShopHub 设计实现一致性验收

把设计规格转化为可追踪、可执行的验收标准，再用失败证据修复实现。不得从当前实现反推期望。

## 保护验收基准

- 不得修改 `design-docs/`、`README.md` 或 `test-cases/`。
- 只能在 `test-case-new/` 创建新增黑盒、契约和追踪产物。
- 不得改变冻结的 URL、HTTP 方法、请求/响应字段、字段类型、成功状态码及 `/api/v1/` 前缀。
- 不得为公开用例硬编码行为，不得新增数据库重置或初始化接口。
- 保持 Java 17、Spring Boot 3.2.6 兼容，并保留无关用户改动。

开始前记录 `git status --short`，并计算受保护文件摘要：

```bash
git ls-files -z -- README.md design-docs test-cases | sort -z | xargs -0 shasum -a 256
```

将输出再整体计算一次 SHA-256 并留存。结束前重复执行；摘要变化时不得交付。只校验 Git 跟踪文件，避免 `target/` 等运行产物造成假差异。

## 一、建立设计侧事实源

1. 阅读 `README.md` 第 3、5、6、7、8、9 节和全部 `design-docs/`。聚焦单一业务域时，仍需阅读通用规范及附录 A-D。
2. 阅读 [references/module-map.md](references/module-map.md)，确认规格、模块和跨模块协作边界。
3. 生成冻结 REST 契约：

   ```bash
   python3 skills/shophub-consistency-agent/scripts/extract_api_contract.py README.md --format json -o /tmp/shophub-api.json
   python3 skills/shophub-consistency-agent/scripts/extract_api_contract.py README.md --format openapi -o test-case-new/spec/openapi.json
   ```

4. 生成设计规格候选：

   ```bash
   python3 skills/shophub-consistency-agent/scripts/extract_design_specs.py design-docs -o test-case-new/spec/spec-candidates.json
   ```

5. 将全部候选复制到 `spec-inventory.json` 后逐项审核：把可由代码、UT、架构测试或黑盒观察的规则标为 `required`；把纯背景说明标为 `informational` 并写明具体理由。不得删除候选、只保留高风险样本，或因当前实现缺失而降低为说明项。高风险只决定执行顺序，不决定是否验收。

按以下优先级解决冲突：README 冻结契约、业务设计文档、通用规范与附录、当前实现。无法消除的真实冲突必须报告，不得自造期望。

## 二、只读探索原始黑盒

1. 阅读 `test-cases/pom.xml`、测试基类、认证辅助、数据构造和全部测试方法。
2. 记录原始用例覆盖的接口、正向路径、异常路径和断言点。
3. 将原始覆盖映射到规格 ID，形成缺口；不得把测试方法数量当作规格覆盖率。
4. 只学习其 Maven 结构、启动方式和测试风格，不复制或修改原始源码。

## 三、生成新增验收

阅读 [references/blackbox-generation.md](references/blackbox-generation.md)，在 `test-case-new/` 中创建：

- `spec/openapi.json`：从设计和 README 生成的契约，不得从 Controller 生成期望；
- `spec/spec-candidates.json`：脚本生成且不得删项的原始候选；
- `spec/spec-inventory.json`：审核后的设计规则；
- `spec/traceability.json`：规格 ID 到测试方法的映射；
- JUnit 黑盒工程：通过真实 HTTP 调用完整应用。

每个冻结接口至少有一个真实 HTTP 契约测试。规则密集业务还必须覆盖：

- 状态机：合法转换、非法跳转、终态重复命令和跨接口序列；
- 公式：典型值、零值、阈值两侧、舍入、上下界和守恒关系；
- 安全：匿名、未认证、角色不足、资源不归属及失败后无副作用；
- 事件：主事务结果、非关键监听失败、失败记录和重试/幂等；
- 配置与时间：运行时覆盖、故障注入、测试时钟和测试隔离。

只列出全部接口的集合、只排除 405/5xx 或仅断言列表大小，只能记为 `routing` 探测，不能算契约验收。每个冻结接口必须在合法认证和前置数据下发出 HTTP 请求，断言设计规定的精确成功状态码及关键响应字段或可观察副作用。

不得把多个互不相关的公式、状态或权限规格仅以注释方式映射到同一测试。每条映射都要列出规格专属 `evidence` 标记，并且这些标记和对应断言必须出现在所引用的测试方法体内。

## 四、选择一致性检查方法

阅读 [references/consistency-methods.md](references/consistency-methods.md)，按规则选择最小有效方法：

- REST 形态和认证：设计侧 OpenAPI/契约清单加 HTTP 黑盒；
- 状态转换：JUnit 转换矩阵；仅在路径组合明显膨胀时引入模型测试工具；
- 金额、库存、优惠、退款、积分：示例黑盒加属性测试或参数化 UT；
- 模块依赖、Repository 越界、分层：ArchUnit；无法增加依赖时使用独立静态检查并记录降级；
- 测试是否真正识别关键错误：对核心计算和状态判断定向运行 PIT；不以全仓库变异率作为硬门槛。

外部工具不可用时使用 JUnit 等价实现，不得跳过对应规则。

## 五、校验追踪并运行新增黑盒

先检查追踪完整性：

```bash
python3 skills/shophub-consistency-agent/scripts/validate_traceability.py \
  --api-contract /tmp/shophub-api.json \
  --candidates test-case-new/spec/spec-candidates.json \
  --specs test-case-new/spec/spec-inventory.json \
  --traceability test-case-new/spec/traceability.json \
  --tests-root test-case-new
```

再运行：

```bash
mvn -s maven-settings.xml -f test-case-new/pom.xml test
```

测试工程无法编译或启动时先修测试基础设施；期望来自明确规格且断言失败时进入实现修复。禁止通过删除用例、放宽断言或改写规格来获得绿色结果。

## 六、定位并修复根因

1. 从失败接口追踪 Controller、DTO、Service、领域模型、Repository、事件和配置。
2. 检查路径、方法、认证、字段、状态码、错误码、资源归属、状态转换、公式、事务和副作用。
3. 使用 [references/common-patterns.md](references/common-patterns.md) 排查 ShopHub 已知高风险模式。
4. 实施恢复规格的最小补丁；不得扩大为无关重写。
5. 每修复一个黑盒失败，同时新增或更新根因所在模块的 UT；跨模块边界问题补充架构测试。

## 七、循环验收

按“失败证据 → 根因修复 → UT → 相关黑盒 → 全量回归”循环，直至追踪校验和所有测试通过：

```bash
mvn -s maven-settings.xml -f code/pom.xml test
mvn -s maven-settings.xml -f code/pom.xml install -DskipTests
mvn -s maven-settings.xml -f test-cases/pom.xml test
mvn -s maven-settings.xml -f test-case-new/pom.xml test
```

不得把未执行、超时或环境受阻记为通过。完成后使用 [references/report-checklist.md](references/report-checklist.md) 自检。

## 八、报告

报告以下内容：

- 已读取的设计和契约来源；
- 冻结接口、可验证规格、原始覆盖、新增覆盖和缺口数量；
- 状态机、公式、权限、事件和架构检查结果；
- 每项不一致的规格 ID、失败证据、根因、修复及 UT；
- 每条验证命令的实际结果；
- 受保护文件摘要复核、环境限制和残余风险。

需要 Markdown 产物时使用 `scripts/generate_report.py`。
