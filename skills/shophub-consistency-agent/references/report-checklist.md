# 报告自检清单

输出最终执行报告前，确认以下事项：

- [ ] 没有修改 `design-docs/` 下的任何文件。
- [ ] 没有修改 `test-cases/`；即使为本地实验临时修改，也不得把这些改动纳入最终补丁。
- [ ] 冻结 API 的路径、HTTP Method、字段名、字段类型、成功状态码和 `/api/v1/` 前缀均未改变。
- [ ] 每一项行为变更都能追溯到设计文档或 README API 契约。
- [ ] 错误码和 HTTP 状态码与 README 第 7 节一致。
- [ ] 已运行模块测试或相关黑盒测试；若因环境限制无法运行，已在报告中说明。
- [ ] 残余风险列出了尚未验证的模块或无法运行的命令。
- [ ] 已在学习 `code/` 前阅读原始 `test-cases/` 的测试组织、fixture 和断言风格。
- [ ] 已创建或更新 `test-cases-new/`，并且没有修改原始 `test-cases/`。
- [ ] `test-cases-new/` 覆盖 README 全量 REST API 契约（含 6.8 管理接口）和设计文档关键规格。
- [ ] 最终验收以 `mvn -s maven-settings.xml -f test-cases-new/pom.xml test` 全部通过为准；若环境无法运行，报告中必须标记为阻断风险。
