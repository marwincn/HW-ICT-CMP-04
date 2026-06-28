# ShopHub Module Map

| Domain | Maven module | Primary design document | Key API areas |
|--------|--------------|-------------------------|---------------|
| Application assembly/config | `code/ecommerce-app` | `02-系统架构.md`, `03-通用规范与非功能设计.md` | Spring Boot startup, security, scheduling, test profile |
| Common infrastructure | `code/ecommerce-common` | `03-通用规范与非功能设计.md`, appendices B-D | error responses, auth/JWT, clock, events, configs, fault injection |
| User | `code/ecommerce-user` | `04-用户服务设计.md` | registration, activation, login, profile, addresses, freeze/unfreeze |
| Product | `code/ecommerce-product` | `05-商品服务设计.md` | SPU/SKU management, shelf status, product query/search, categories |
| Inventory | `code/ecommerce-inventory` | `06-库存服务设计.md` | warehouses, inbound/outbound, availability, adjustments, warnings |
| Cart | `code/ecommerce-cart` | `07-购物车服务设计.md` | cart items, cart estimate, stock/sale validation |
| Order | `code/ecommerce-order` | `08-订单服务设计.md` | order creation, cancellation, batch, purchase verification, sales stats |
| Payment/refund/invoice/settlement | `code/ecommerce-payment` | `09-支付服务设计.md`, `14-发票与结算设计.md` | pay, callback, refunds, invoices, settlement batches |
| Promotion | `code/ecommerce-promotion` | `10-促销服务设计.md` | coupons, full reductions, seckill, calculation |
| Logistics | `code/ecommerce-logistics` | `11-物流服务设计.md` | shipment query and state transitions, callbacks, freight templates |
| Loyalty | `code/ecommerce-loyalty` | `12-积分与会员服务设计.md` | points balance/history, level, expiration, redeem estimate |
| Review | `code/ecommerce-review` | `13-评价服务设计.md` | review create/append/query/moderation |
| Public black-box tests | `test-cases` | README section 8 | Do not modify; use to validate behavior |

## Investigation order

1. Match endpoint declaration in controller.
2. Match DTO field names and JSON types.
3. Match success HTTP status.
4. Match authentication/authorization and domain ownership checks.
5. Match service behavior, state transitions, calculations, and event side effects.
6. Match persistence defaults and test profile isolation.
