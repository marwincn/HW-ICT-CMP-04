# Report Checklist

Before producing the final execution report, confirm:

- [ ] No files under `design-docs/` were modified.
- [ ] No files under `test-cases/` were modified unless the human explicitly allowed it for local experimentation; never include such changes in final contest fixes.
- [ ] Frozen API paths, methods, field names, field types, status codes, and `/api/v1/` prefix are unchanged.
- [ ] Every changed behavior cites a design document or README contract expectation.
- [ ] Error codes and HTTP statuses match README section 7.
- [ ] Module tests or relevant black-box tests were run, or environment limitations are documented.
- [ ] Residual risks list unverified modules or commands that could not be run.
