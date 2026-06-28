# ShopHub Consistency Repair Agent Skill

Use this skill when working on the ShopHub software-contest task: compare `design-docs/`, the frozen REST API contract in `README.md`, and the Java Spring Boot multi-module implementation under `code/`, then repair implementation inconsistencies without changing design documents or the frozen API contract.

## Goal

Deliver code changes that make ShopHub match the design documents and keep the project buildable. Finish every run with an execution report that records inspected documents, inconsistencies found, code changes made, and validation results.

## Non-negotiable rules

- Treat `design-docs/` as the acceptance baseline.
- Do not modify `design-docs/`, `test-cases/`, or frozen API URLs/methods/request fields/response fields/status codes from `README.md`.
- Do not hard-code logic for specific public tests.
- Do not expose database reset or bootstrap endpoints.
- Keep `/api/v1/` unchanged.
- Preserve Java 17 and Spring Boot 3.2.6 compatibility.

## Workflow

1. **Load contest context**
   - Read `README.md` sections 3, 5, 6, 7, 8, and 9.
   - Read all relevant files in `design-docs/`; for a focused fix, read at least the module design document plus common specs:
     - `03-通用规范与非功能设计.md`
     - `附录A-API接口参考.md`
     - `附录B-配置参考.md`
     - `附录C-数据模型.md`
     - `附录D-本地事件契约.md`
   - Use `references/module-map.md` to map business domains to Maven modules and design documents.

2. **Build an API and behavior checklist**
   - Use `scripts/extract_api_contract.py` to extract the frozen API baseline from `README.md` into a Markdown checklist.
   - Compare controllers, DTOs, HTTP status codes, error codes, and auth requirements against that checklist.
   - For business behavior, use `references/common-patterns.md` as a defect-pattern catalog.

3. **Inspect implementation**
   - Search with `rg`, not recursive grep.
   - Check controllers first, then services/domain models/repositories/configuration.
   - Verify module boundaries and shared classes in `ecommerce-common` before adding duplicate code.

4. **Repair code only**
   - Prefer minimal, design-driven patches.
   - Add or update DTOs, services, configuration, events, and tests only when they support the design.
   - Keep API response shapes stable; if a controller returns `ResponseEntity`, explicitly set the README success status.
   - Use design-defined error codes and HTTP status mappings.

5. **Validate**
   - Run the narrowest relevant tests first.
   - Before finalizing, run when feasible:
     ```bash
     mvn -s maven-settings.xml -f code/pom.xml test
     mvn -s maven-settings.xml -f code/pom.xml install -DskipTests
     mvn -s maven-settings.xml -f test-cases/pom.xml test
     ```
   - If network or mirror access prevents dependency resolution, record it as an environment limitation in the report.

6. **Report**
   - Generate an execution report using `scripts/generate_report.py` or write the same sections manually.
   - Include: scope, inspected evidence, inconsistencies, fixes, validations, residual risks.

## Output report template

```markdown
# ShopHub Consistency Execution Report

## Scope
- Modules/features inspected:
- Design documents used:
- README contract sections used:

## Findings and Fixes
| ID | Design/API expectation | Implementation mismatch | Fix | Files changed |
|----|------------------------|-------------------------|-----|---------------|

## Validation
| Command | Result | Notes |
|---------|--------|-------|

## Residual Risks
- 
```

## Reference files

- `references/module-map.md` — domain-to-module/document mapping.
- `references/common-patterns.md` — recurring mismatch and repair patterns.
- `references/report-checklist.md` — final review checklist.

## Helper scripts

- `scripts/extract_api_contract.py` — parses README API tables and emits a checklist.
- `scripts/generate_report.py` — creates a report scaffold from JSON or command-line fields.
