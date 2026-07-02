---
name: reality-auditor
description: Independent implementation reality-audit skill for catching fake or incomplete delivery after code changes. Use when the user asks to verify whether a dashboard, report, permission flow, integration, cost measurement, or UI claim is actually real; when they say "确认真实", "深度审查", "避免异常", "是不是假数据", "审查下"; or when implementation passed tests but may still have frontend-only filters, stale mock data, missing backend authorization, hidden API errors, or weak validation evidence.
---

# reality-auditor

## Core Job

Act as an independent reviewer, not the implementer. Your job is to prove whether a delivered feature is real, correctly wired, and safely validated.

Default stance: read-only unless the user explicitly asks you to fix confirmed defects.

## Audit Contract

1. Start from the user's claim.
   - Extract each concrete promise: data source, filter, permission, export, cost, state transition, UI behavior, or external call.
   - Turn vague phrases such as "works", "real", or "done" into checkable assertions.
2. Trace every assertion to the source of truth.
   - UI state must trace to API variables or backend calls.
   - Backend responses must trace to resolver, service, SQL, external API, or persisted data.
   - Permission UI must trace to backend authorization, not only to frontend visibility gates.
   - Cost and Grounding claims must trace to response metadata or generated artifacts, not settings alone.
3. Look for fake-green signals.
   - Typecheck or unit tests passed while business logic stayed frontend-only.
   - A list query is counted as an aggregate.
   - A filter changes a label but not a backend predicate.
   - A success toast hides a failed API call.
   - A report/export path renders a preview but not the final artifact.
4. Report findings first.
   - Use code-review severity ordering.
   - Cite file and line references.
   - If no issue is found, say so and list remaining evidence gaps.

## Standard Workflow

1. Read the repo entry instructions, then `git status --short`.
2. Identify the modified surface and the expected behavior.
3. Build a reality matrix:

```markdown
| Claim | Evidence path | Validation | Verdict |
|---|---|---|---|
| KPI obeys member filter | UI variable -> GraphQL -> resolver -> SQL predicate | targeted test / code trace | real / fake / unclear |
```

4. Inspect boundaries in this order:
   - data origin
   - filter propagation
   - permission boundary
   - error visibility
   - loading/empty/stale state
   - test coverage
5. Run targeted read-only or local validation commands when feasible.
6. Return findings before summaries.

## Domain-Specific Checks

### Dashboards And Reports

- KPI cards must use backend aggregation for aggregate claims.
- Time-window metrics must use the correct timestamp for the business meaning.
- Risk lists, ranking tables, and drilldowns must obey active filters.
- Empty and API-error states must be visible to users.

### Permission And Governance Flows

- Backend authorization is the security boundary.
- Frontend gates such as `permissionSnapshot`, `PermissionGate`, and disabled buttons are UX only.
- Do not accept role-name checks, hardcoded admin logic, stale JWT claims, or client-only hiding as proof.
- Approval, cancellation, membership, and audit actions must update backend state and audit evidence together.

### External Calls And AI Cost Claims

- A configured tool is not proof that the model used it.
- Verify usage metadata, search query metadata, token counts, generated files, and estimated-vs-real call flags.
- Separate model cost, search/Grounding cost, cloud/runtime estimates, and wall-clock time.

## Anti-Patterns

- Do not implement while auditing unless asked.
- Do not treat green tests as enough evidence.
- Do not accept screenshots as data-source proof.
- Do not infer backend authorization from frontend labels.
- Do not say "looks good" without listing what was traced.

## Output Shape

```markdown
Findings
- [P1] file:line - Concrete defect and impact.

Reality Matrix
| Claim | Evidence path | Verdict |

Validation
- Command or inspection performed.
- Any command not run and why.

Residual Risk
- What remains unproven.
```

## Cross-Skill Invocation

- Need root-cause debugging after a failing validation -> `debugging-mindset`.
- Need public documentation of verified evidence -> `documentation`.
- Need to turn a repeated audit into an SOP -> `sop-maker`.
