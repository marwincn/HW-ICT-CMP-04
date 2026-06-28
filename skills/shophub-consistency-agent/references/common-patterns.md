# Common ShopHub Consistency Patterns

Use these patterns as a checklist while comparing design documents and implementation.

## API contract patterns

- **Created resources must return 201**: register, address create, product/SPU/SKU create, warehouse/inbound/outbound/adjustment, order create, payment create, refund apply, invoice create, coupon claim, review create/append, freight/full-reduction/seckill creation.
- **Deletes that remove state return 204 with an empty body**: address delete, cart item delete, cart clear, clearing fault injections.
- **Frozen URL shapes are exact**: do not rename segments such as `/orders/create`, `/admin/orders/{orderId}/cancel-review`, `/reviews/product/{productId}`, or `/admin/system/clock`.
- **Error response consistency**: map business exceptions to README error codes and HTTP statuses; avoid leaking validation stack traces as 500.
- **Anonymous endpoints must stay anonymous**: product browsing, inventory checks, registration/activation/login, payment/logistics signed callbacks.

## User and auth patterns

- Registration creates a pending user; activation moves the user to active.
- Login must reject inactive users with `USER_NOT_ACTIVE` and frozen users with `USER_FROZEN` where the design requires it.
- USER endpoints must use the authenticated user rather than request-supplied user IDs.
- ADMIN endpoints must require admin authorization.

## Product/inventory/cart patterns

- Only `ON_SHELF` SKUs are saleable and searchable to public users.
- Inventory availability usually equals on-hand minus locked/reserved stock; inbound should increase both on-hand and available stock when no lock exists.
- Cart add commonly accumulates quantity for the same SKU; cart update replaces quantity.
- Cart estimate should expose item total, discount, shipping, packaging, points deduction, and payable amount according to design formulas.

## Order/payment/logistics patterns

- Order creation validates user status, SKU sale status, stock, amount formula, risk controls, address, and promotions before persisting.
- High-risk orders should fail with `ORDER_RISK_REJECTED`, not a generic validation error.
- Payment callback success should not roll back when downstream notification/event/logistics actions fail; record failures for admin query.
- Logistics must follow the designed state machine: pick before print label before outbound; reject skipped transitions with a status-conflict error.
- Timeout cancellation should use the controllable test clock when present.

## Promotion/loyalty/review/invoice patterns

- Percentage coupons often store discount rate; an 8-fold coupon means customer pays 80%, so discount is `price * (1 - 0.8)`.
- Payable amount formula should include shipping/packaging and subtract discounts/points exactly once.
- Purchase verification for reviews should accept paid/fulfilled states as defined by design, and reject non-purchases with `REVIEW_PURCHASE_REQUIRED`.
- Invoice amount cannot exceed remaining invoiceable paid amount; use `INVOICE_AMOUNT_EXCEEDED`.
- Points history pagination should be deterministic and scoped to the current user.

## Configuration and testability patterns

- Runtime config overrides under admin system APIs should affect subsequent service calculations without restart.
- Fault injection should be scoped, queryable through event failure records where designed, and clearable.
- Tests create isolated H2 contexts; avoid static mutable state that survives context shutdown unless explicitly reset by Spring lifecycle.
