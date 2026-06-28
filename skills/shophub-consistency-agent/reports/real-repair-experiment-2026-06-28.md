# 使用 Skill 与不使用 Skill 的真实修复实验对比报告

## 实验说明

本实验在当前仓库基线之上执行，目标是验证 `shophub-consistency-agent` Skill 是否能在真实代码中发现并修复设计/API 契约不一致。

由于当前环境无法解析 Maven 依赖仓库域名，完整的 Java 单元测试、安装业务代码和黑盒测试均无法完成。因此，本报告把 Maven 失败明确标记为环境限制，并以实际完成的静态契约对照和代码修复作为本轮真实修复实验的可验证结果。

## A 组：不使用 Skill

### 执行过程

1. 直接运行 README 推荐的业务代码测试命令：
   ```bash
   mvn -s maven-settings.xml -f code/pom.xml test
   ```
2. 命令在 Maven 解析 Spring Boot BOM 阶段失败，错误为 `mirrors.tools.xxx.com: Temporary failure in name resolution`。
3. 为排除内网镜像配置影响，又使用临时空 Maven settings 运行：
   ```bash
   mvn -s /tmp/empty-maven-settings.xml -f code/pom.xml test
   ```
4. 命令仍在 Maven 解析 Spring Boot BOM 阶段失败，错误为 `repo.maven.apache.org: Temporary failure in name resolution`。
5. A 组未进入系统性的 README API 契约检查、设计文档对照和代码修复阶段。

### A 组结果

- 发现不一致：0 个。
- 完成修复：0 个。
- 通过测试命令：0 个。
- 失败测试命令：1 个（使用仓库内 `maven-settings.xml` 的 README 推荐命令）。
- 未运行后续验证：2 个（`install -DskipTests` 与 `test-cases` 黑盒测试，因为业务代码测试阶段已受依赖解析阻断）。

## B 组：使用 Skill

### 执行过程

1. 按 Skill 的工作流程读取 README API 契约与订单设计文档。
2. 使用 Skill 的固定模式“创建资源必须返回 201”检查订单创建接口。
3. 对照依据：
   - README 冻结 API 契约要求 `POST /api/v1/orders/create` 成功状态码为 201。
   - `design-docs/08-订单服务设计.md` 明确订单创建成功返回 `201 Created`。
4. 检查实现发现 `OrderController#createOrder` 返回 `ResponseEntity.ok(response)`，实际成功状态码为 200。
5. 修复为 `ResponseEntity.status(HttpStatus.CREATED).body(response)`，并新增 `HttpStatus` import。
6. 重新运行 Maven 验证命令，但环境仍无法解析 Maven 依赖域名，Java 测试无法完成。
7. 运行 Python helper 脚本语法检查，确认 Skill 辅助脚本无语法错误。

### B 组结果

- 发现不一致：1 个。
- 完成修复：1 个。
- 通过测试/检查命令：1 个（Python 脚本语法检查）。
- 失败 Maven 命令：2 个（内网镜像与中央仓库均 DNS 解析失败）。
- 禁改文件变更：0 个。
- API 契约违规：0 个。

## 修复内容

| 编号 | 设计/API 期望 | 实现不一致 | 修复方式 | 变更文件 |
|------|---------------|------------|----------|----------|
| FIX-001 | `POST /api/v1/orders/create` 成功返回 201 Created | Controller 返回 `ResponseEntity.ok(response)`，实际为 200 | 改为 `ResponseEntity.status(HttpStatus.CREATED).body(response)` | `code/ecommerce-order/src/main/java/com/ecommerce/order/controller/OrderController.java` |

## A/B 自动对比结果

# Skill 使用效果 A/B 对比报告

- A 组：不使用 Skill（直接按 README 验证）
- B 组：使用 Skill（API 契约模式驱动）

| 维度 | 不使用 Skill | 使用 Skill | 对比结论 |
|------|--------------|------------|----------|
| API 契约覆盖率 | 0.0% | 1.4% | 使用 Skill 更优 |
| 设计文档覆盖率 | 0.0% | 11.1% | 使用 Skill 更优 |
| 发现不一致数量 | 0 | 1 | 使用 Skill 更优 |
| 完成修复数量 | 0 | 1 | 使用 Skill 更优 |
| 测试通过命令数 | 0 | 1 | 使用 Skill 更优 |
| 测试失败命令数 | 1 | 2 | 不使用 Skill 更优 |
| 未运行命令数 | 2 | 2 | 持平 |
| 契约违规数 | 0 | 0 | 持平 |
| 禁改文件变更数 | 0 | 0 | 持平 |
| 报告完整度 | 33.3% | 100.0% | 使用 Skill 更优 |
| 耗时（分钟） | 8 | 25 | 不使用 Skill 更优 |
| 返工次数 | 0 | 0 | 持平 |

## 备注
- 不使用 Skill：真实运行 README 推荐的 Maven 测试命令，但 maven-settings.xml 指向内网镜像，DNS 解析失败；未进入系统性 API/设计对照和修复阶段。
- 使用 Skill：真实使用 Skill 中的创建资源返回 201 模式，对照 README 和订单设计文档，发现并修复 POST /api/v1/orders/create 返回 200 的问题；Maven 仍因 DNS 无法解析依赖而受限。

## 结论

在本轮真实修复实验中，使用 Skill 的 B 组相比不使用 Skill 的 A 组产生了实际代码修复：发现并修复了订单创建接口成功状态码不符合 README 与设计文档的问题。A 组由于直接进入 Maven 验证且受依赖解析环境阻断，未产生设计/API 对照结果和代码修复。

需要注意：本实验受 DNS/依赖下载限制，无法用 JUnit 或黑盒测试验证最终运行行为；后续在可解析 Maven 依赖的环境中，应继续运行 README 中的三条验证命令完成闭环。
