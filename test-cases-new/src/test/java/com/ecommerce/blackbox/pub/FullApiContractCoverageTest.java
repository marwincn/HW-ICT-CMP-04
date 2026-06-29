package com.ecommerce.blackbox.pub;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * README REST API contract coverage matrix for the expanded acceptance module.
 *
 * <p>This meta-test makes the intended full blackbox coverage explicit: every
 * frozen endpoint in README section 6, including the section 6.8 support/admin
 * endpoints, must have a row in this matrix before implementation-specific
 * request/response assertions are considered complete.</p>
 */
@DisplayName("Full REST API Contract Coverage Matrix")
class FullApiContractCoverageTest {

    private static final int README_SECTION_6_ENDPOINT_COUNT = 81;

    @Test
    @DisplayName("README section 6 frozen REST APIs are represented in test-cases-new")
    void readmeSection6ApiContractIsFullyRepresented() {
        List<EndpointContract> contracts = contracts();

        assertEquals(README_SECTION_6_ENDPOINT_COUNT, contracts.size(),
                "README section 6 currently defines 81 frozen REST endpoints including 6.8 admin support APIs");

        Set<String> uniqueKeys = new HashSet<>();
        for (EndpointContract contract : contracts) {
            assertTrue(uniqueKeys.add(contract.method() + " " + contract.url()),
                    "duplicate API contract row: " + contract.method() + " " + contract.url());
            assertTrue(contract.successStatus() >= 200 && contract.successStatus() < 300,
                    "success status must be 2xx for " + contract.method() + " " + contract.url());
            assertTrue(!contract.module().isBlank(), "module must be recorded");
            assertTrue(!contract.auth().isBlank(), "auth requirement must be recorded");
        }
    }

    private static List<EndpointContract> contracts() {
        return List.of(
            endpoint("用户模块", "POST", "/api/v1/users/register", "匿名", 201),
            endpoint("用户模块", "POST", "/api/v1/users/activate", "匿名", 200),
            endpoint("用户模块", "POST", "/api/v1/users/login", "匿名", 200),
            endpoint("用户模块", "GET", "/api/v1/users/me", "USER", 200),
            endpoint("用户模块", "POST", "/api/v1/users/addresses", "USER", 201),
            endpoint("用户模块", "GET", "/api/v1/users/addresses", "USER", 200),
            endpoint("用户模块", "PUT", "/api/v1/users/addresses/{addressId}", "USER", 200),
            endpoint("用户模块", "DELETE", "/api/v1/users/addresses/{addressId}", "USER", 204),
            endpoint("用户模块", "POST", "/api/v1/admin/users/{userId}/freeze", "ADMIN", 200),
            endpoint("用户模块", "POST", "/api/v1/admin/users/{userId}/unfreeze", "ADMIN", 200),
            endpoint("商品模块", "POST", "/api/v1/admin/products/spu", "ADMIN", 201),
            endpoint("商品模块", "POST", "/api/v1/admin/products/sku", "ADMIN", 201),
            endpoint("商品模块", "POST", "/api/v1/admin/products/sku/{skuId}/on-shelf", "ADMIN", 200),
            endpoint("商品模块", "POST", "/api/v1/admin/products/sku/{skuId}/off-shelf", "ADMIN", 200),
            endpoint("商品模块", "GET", "/api/v1/products", "匿名", 200),
            endpoint("商品模块", "GET", "/api/v1/products/search", "匿名", 200),
            endpoint("商品模块", "GET", "/api/v1/products/{skuId}", "匿名", 200),
            endpoint("商品模块", "GET", "/api/v1/categories/tree", "匿名", 200),
            endpoint("库存模块", "POST", "/api/v1/admin/warehouses", "ADMIN", 201),
            endpoint("库存模块", "POST", "/api/v1/admin/inventory/inbound", "ADMIN", 201),
            endpoint("库存模块", "POST", "/api/v1/admin/inventory/outbound", "ADMIN", 201),
            endpoint("库存模块", "GET", "/api/v1/inventory/sku/{skuId}", "匿名", 200),
            endpoint("库存模块", "POST", "/api/v1/inventory/check", "匿名", 200),
            endpoint("库存模块", "POST", "/api/v1/admin/inventory/adjustments", "ADMIN", 201),
            endpoint("库存模块", "GET", "/api/v1/admin/inventory/warnings", "ADMIN", 200),
            endpoint("购物车模块", "POST", "/api/v1/cart/items", "USER", 201),
            endpoint("购物车模块", "GET", "/api/v1/cart", "USER", 200),
            endpoint("购物车模块", "PUT", "/api/v1/cart/items/{skuId}", "USER", 200),
            endpoint("购物车模块", "DELETE", "/api/v1/cart/items/{skuId}", "USER", 204),
            endpoint("购物车模块", "DELETE", "/api/v1/cart", "USER", 204),
            endpoint("购物车模块", "POST", "/api/v1/cart/estimate", "USER", 200),
            endpoint("订单模块", "POST", "/api/v1/orders/create", "USER", 201),
            endpoint("订单模块", "GET", "/api/v1/orders/{orderId}", "USER", 200),
            endpoint("订单模块", "GET", "/api/v1/orders", "USER", 200),
            endpoint("订单模块", "POST", "/api/v1/orders/{orderId}/cancel", "USER", 200),
            endpoint("订单模块", "POST", "/api/v1/admin/orders/{orderId}/cancel-review", "ADMIN", 200),
            endpoint("订单模块", "POST", "/api/v1/orders/batch", "USER", 200),
            endpoint("订单模块", "GET", "/api/v1/orders/verify-purchase", "USER/ADMIN", 200),
            endpoint("订单模块", "GET", "/api/v1/admin/orders/statistics/sales", "ADMIN", 200),
            endpoint("支付、退款、发票", "POST", "/api/v1/payment/pay", "USER", 201),
            endpoint("支付、退款、发票", "POST", "/api/v1/payment/callback", "签名", 200),
            endpoint("支付、退款、发票", "GET", "/api/v1/payment/{paymentNo}", "USER", 200),
            endpoint("支付、退款、发票", "POST", "/api/v1/refunds/apply", "USER", 201),
            endpoint("支付、退款、发票", "POST", "/api/v1/admin/refunds/{refundId}/review", "ADMIN", 200),
            endpoint("支付、退款、发票", "POST", "/api/v1/admin/refunds/{refundId}/warehouse-accept", "ADMIN", 200),
            endpoint("支付、退款、发票", "GET", "/api/v1/refunds/{refundId}", "USER", 200),
            endpoint("支付、退款、发票", "POST", "/api/v1/invoices", "USER", 201),
            endpoint("支付、退款、发票", "GET", "/api/v1/invoices/order/{orderId}", "USER", 200),
            endpoint("支付、退款、发票", "POST", "/api/v1/admin/settlements/batches", "ADMIN", 201),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/promotions/coupons", "ADMIN", 201),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/promotions/coupons/claim", "USER", 201),
            endpoint("促销、物流、积分、评价", "GET", "/api/v1/promotions/coupons/my", "USER", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/promotions/calculate", "USER", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/promotions/full-reductions", "ADMIN", 201),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/promotions/seckill", "ADMIN", 201),
            endpoint("促销、物流、积分、评价", "GET", "/api/v1/logistics/order/{orderId}", "USER", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/logistics/shipments/{shipmentId}/pick", "ADMIN", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/logistics/shipments/{shipmentId}/print-label", "ADMIN", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/logistics/shipments/{shipmentId}/outbound", "ADMIN", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/logistics/callback", "签名", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/logistics/freight-templates", "ADMIN", 201),
            endpoint("促销、物流、积分、评价", "GET", "/api/v1/loyalty/points", "USER", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/loyalty/points/estimate-redeem", "USER", 200),
            endpoint("促销、物流、积分、评价", "GET", "/api/v1/loyalty/points/history", "USER", 200),
            endpoint("促销、物流、积分、评价", "GET", "/api/v1/loyalty/member-level", "USER", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/loyalty/points/expire", "ADMIN", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/reviews", "USER", 201),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/reviews/{reviewId}/append", "USER", 201),
            endpoint("促销、物流、积分、评价", "GET", "/api/v1/reviews/product/{productId}", "匿名", 200),
            endpoint("促销、物流、积分、评价", "GET", "/api/v1/reviews/my", "USER", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/reviews/{reviewId}/approve", "ADMIN", 200),
            endpoint("促销、物流、积分、评价", "POST", "/api/v1/admin/reviews/{reviewId}/reject", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "PUT", "/api/v1/admin/system/configs/{key}", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "GET", "/api/v1/admin/system/configs/{key}", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "POST", "/api/v1/admin/ops/fault-injections", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "DELETE", "/api/v1/admin/ops/fault-injections", "ADMIN", 204),
            endpoint("黑盒测试支撑管理接口", "GET", "/api/v1/admin/events/failures", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "GET", "/api/v1/admin/notifications", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "PUT", "/api/v1/admin/system/clock", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "DELETE", "/api/v1/admin/system/clock", "ADMIN", 200),
            endpoint("黑盒测试支撑管理接口", "POST", "/api/v1/admin/orders/timeout-cancel", "ADMIN", 200)
        );
    }

    private static EndpointContract endpoint(String module, String method, String url, String auth, int successStatus) {
        return new EndpointContract(module, method, url, auth, successStatus);
    }

    private record EndpointContract(String module, String method, String url, String auth, int successStatus) {
    }
}
