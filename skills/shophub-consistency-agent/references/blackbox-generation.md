# `test-case-new` 黑盒验收生成指南

把设计事实转化为可执行验收，不从实现行为推导期望。原始 `test-cases/` 只能只读参考。

## 必需产物

```text
test-case-new/
├── pom.xml
├── spec/
│   ├── openapi.json
│   ├── spec-candidates.json
│   ├── spec-inventory.json
│   └── traceability.json
└── src/test/java/
    └── ...
        ├── support/
        ├── contract/
        ├── state/
        ├── calculation/
        └── architecture/
```

`openapi.json` 是设计侧契约。实现生成的 OpenAPI 只能作为实际快照参与差异检查，不能覆盖它。

## 规格追踪格式

`spec-inventory.json`：

```json
{
  "requirements": [
    {
      "id": "D08-S2-R001",
      "source": "design-docs/08-订单服务设计.md#2",
      "category": "state-machine",
      "description": "已支付订单不能再次发起支付",
      "status": "required",
      "reason": "可通过支付接口和查询接口观察"
    }
  ]
}
```

`traceability.json`：

```json
{
  "mappings": [
    {
      "requirement_id": "D08-S2-R001",
      "coverage_type": "blackbox",
      "evidence": ["D08-S2-R001", "PAYMENT_ALREADY_COMPLETED", "assertEquals"],
      "tests": [
        "src/test/java/com/ecommerce/blackbox/state/OrderStateTest.java#paidOrderCannotPayAgain"
      ]
    }
  ]
}
```

覆盖类型使用 `blackbox`、`unit`、`architecture` 或 `routing`。`routing` 仅表示方法和路径可达，不计入规格验收。REST 契约 ID 必须另有 `blackbox` 映射，填写与设计一致的 `expected_status`，并在 `evidence` 中列出规格 ID、具体路径、精确状态码和关键断言标记。

`spec-candidates.json` 中的每一项都必须出现在 `spec-inventory.json`，状态只能是 `required` 或 `informational`。不得用删除候选的方式提高覆盖率。

## 真实覆盖标准

黑盒测试必须同时具备：

- `@Test` 或参数化测试入口；
- 真实 HTTP 客户端调用；
- 对状态码、响应字段、错误码或后续可观察状态的断言；
- 测试源码中出现对应规格 ID。

以下内容不能单独计为覆盖：

- 在 Java 列表中枚举全部端点并断言数量；
- 对全部接口只断言“不是 405/5xx”；
- 只检查 Controller 注解；
- 只断言响应非空或状态为 2xx；
- 把多个不相关规格 ID 写进注释，却没有对应输入和断言；
- 直接调用 Service/Repository 后声称是黑盒；
- 复制原始公开用例但不增加规格断言。

## 用例设计

### REST 契约

逐端点验证方法、路径、认证、成功状态码、关键请求字段、响应字段和错误结构。创建、删除和回调接口必须检查精确状态码及副作用。

### 状态机

从设计转换表生成矩阵：每条合法边至少一次，每种禁止跳转至少一个代表用例，每个终态至少检查一次重复命令。状态依赖必须通过公开 API 构造。

### 公式与守恒

对金额、库存、积分和优惠覆盖典型值、零值、阈值前后、最大值、舍入和组合顺序。优先断言精确数值，并验证拆分前后总额、预占释放前后库存等守恒关系。

### 权限和副作用

分别覆盖未认证、角色不足、跨用户资源和冻结状态。失败请求后重新查询，确认没有写入或状态改变。

### 事件与可测试性

通过故障注入、事件失败记录、通知记录、运行时配置和测试时钟观察结果。非关键监听器失败不得回滚主事务。

## 失败分流

1. 编译或上下文失败：修复新增测试工程。
2. 前置数据失败：确认使用合法公开 API 和隔离数据。
3. 规格明确且断言失败：修复实现及根因 UT。
4. 规格冲突：保留失败证据并报告，不自行选择有利于当前实现的解释。

禁止删除失败测试、降低断言、增加条件跳过或从当前响应复制期望。
