# ShopHub 模块映射

| 业务域 | Maven 模块 | 主要设计文档 | 重点 API/能力 |
|--------|------------|--------------|---------------|
| 应用组装与配置 | `code/ecommerce-app` | `02-系统架构.md`、`03-通用规范与非功能设计.md` | Spring Boot 启动、安全配置、调度、测试 profile |
| 公共基础设施 | `code/ecommerce-common` | `03-通用规范与非功能设计.md`、附录 B-D | 错误响应、认证/JWT、测试时钟、事件、运行时配置、故障注入 |
| 用户 | `code/ecommerce-user` | `04-用户服务设计.md` | 注册、激活、登录、个人信息、地址、冻结/解冻 |
| 商品 | `code/ecommerce-product` | `05-商品服务设计.md` | SPU/SKU 管理、上下架、商品查询/搜索、类目树 |
| 库存 | `code/ecommerce-inventory` | `06-库存服务设计.md` | 仓库、入库、出库、可用库存、库存调整、库存预警 |
| 购物车 | `code/ecommerce-cart` | `07-购物车服务设计.md` | 购物车项、价格预估、库存与可售校验 |
| 订单 | `code/ecommerce-order` | `08-订单服务设计.md` | 创建订单、取消、批量下单、购买校验、销售统计 |
| 支付/退款/发票/结算 | `code/ecommerce-payment` | `09-支付服务设计.md`、`14-发票与结算设计.md` | 支付、回调、退款、发票、结算批次 |
| 促销 | `code/ecommerce-promotion` | `10-促销服务设计.md` | 优惠券、满减、秒杀、促销计算 |
| 物流 | `code/ecommerce-logistics` | `11-物流服务设计.md` | 物流查询、状态流转、回调、运费模板 |
| 积分与会员 | `code/ecommerce-loyalty` | `12-积分与会员服务设计.md` | 积分余额/历史、会员等级、积分过期、积分抵扣预估 |
| 评价 | `code/ecommerce-review` | `13-评价服务设计.md` | 发布评价、追评、查询、审核 |
| 原始公开黑盒测试 | `test-cases` | README 第 8 节 | 不得修改；仅用于探索测试结构与回归验证 |
| 新增黑盒验收测试 | `test-case-new` | README 第 6-8 节、全部相关设计文档 | 保存设计侧契约、规格追踪和真实 HTTP 验收；可生成和修改 |

## 排查顺序

1. 对照 Controller 中的端点声明。
2. 对照 DTO 字段名与 JSON 类型。
3. 对照成功 HTTP 状态码。
4. 对照认证、授权和资源归属校验。
5. 对照 Service 行为、状态机、金额/库存计算和事件副作用。
6. 对照持久化默认值、测试 profile 隔离和静态状态清理。
7. 校验设计规格 ID、契约、真实测试和实现证据之间的追踪关系。
8. 对照 `test-case-new` 的新增黑盒失败，定位实现或 UT 缺口。
