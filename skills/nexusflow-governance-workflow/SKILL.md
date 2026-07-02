---
name: nexusflow-governance-workflow
description: Project-specific workflow skill for NexusFlow permission, tenant governance, platform visibility, dashboard, GCP import, audit-log, and role-management work. Use when working in a NexusFlow checkout or when the user mentions NexusFlow, "权限管理", "后端控制权限，前端控制体现", tenant governance, platform scope, permissionSnapshot, approval flows, dashboard reality checks, GCP resource discovery, or Chinese conventional commits for this project.
---

# nexusflow-governance-workflow

## Core Job

Execute NexusFlow governance work without losing the security boundary:

- backend authorization is the truth source
- frontend permission state is UX expression only
- user-facing governance UX must stay Chinese-first, low-friction, and business-friendly
- work must be implemented in small validated slices

## Entry Checklist

Run this before planning or editing:

1. Read project instructions in order:
   - `AGENTS.md`
   - `RTK.md`
   - `docs/plans/README.md`
2. Run `git status --short --branch`.
3. Identify unrelated dirty files and keep them out of the task.
4. Locate the relevant truth source:
   - authorization kernel: `backend/app/authorization/`
   - GraphQL/REST resolver or route
   - service layer
   - frontend page/component
   - tests that assert the contract

If any file is missing, adapt to the current checkout and state the gap.

## Governance Principles

1. Backend controls permission.
   - Use `AuthorizationService.can()` / `can_many()` or established service wrappers.
   - Avoid scattered checks against role display names, JWT role strings, `isAdmin`, or direct membership rows.
2. Frontend controls expression.
   - Use `permissionSnapshot`, `PermissionGate`, and local permission-state helpers for visibility, disabled states, tooltips, and explanatory copy.
   - Never claim frontend hiding is a security boundary.
3. Tenant autonomy is the default.
   - Tenant owner/admin can govern internal tenant actions.
   - Platform approval is reserved for platform-owned or tenant-destructive actions.
4. UX must be operator-friendly.
   - Prefer concise Chinese labels, icon actions with tooltips, modal batch flows, progressive loading, and clear empty/error states.
   - Do not expose raw technical contracts unless the user actually needs them.

## Implementation Flow

1. Map the contract.
   - Actor, scope, action, resource, and expected audit trail.
   - Current UI affordance and backend permission path.
2. Write a narrow plan.
   - Backend contract
   - Frontend expression
   - Tests
   - Verification and commit boundary
3. Implement backend first when permission behavior changes.
   - Resolver/route/service
   - Authorization check
   - Audit evidence
   - Migration when needed
4. Implement frontend expression.
   - Read backend capability
   - Bind disabled/visible state to snapshot or permission helper
   - Keep Chinese copy and business-language explanations
5. Add or update targeted tests.
6. Run validation commands appropriate to the touched layer.

## Repeated Validation Set

Choose the smallest set that proves the contract:

```bash
PYTHONPATH=backend backend/venv/bin/python -m pytest backend/tests/authorization -q
PYTHONPATH=backend backend/venv/bin/python -m pytest backend/tests/test_dashboard_permissions.py
cd frontend && npx vitest run <targeted-test>
cd frontend && npm run typecheck
cd frontend && npm run lint
cd frontend && npm run build
python3 scripts/permissions/scan_legacy_call_sites.py --check
git diff --check
```

If a command is not available in the current checkout, record the exact blocker.

## Reality Checks

Before calling the work done, verify:

- every filter reaches GraphQL/resolver/service/SQL or the equivalent backend path
- dashboard aggregates come from backend aggregation, not page-size-limited list queries
- completion metrics use completion timestamps, not only current status
- risk lists obey selected filters
- platform visibility traces through live token/session/snapshot state
- UI error states surface API failures
- tests cover the behavioral contract, not only string changes

Use `reality-auditor` for a separate review pass after nontrivial implementation.

## Git Discipline

- Stage only task files.
- Use Chinese conventional commits when the user asks for commits:

```text
fix(权限): 修正审批取消权限边界
feat(仪表盘): 支持自定义时间范围
```

- If migrations are ignored, verify with `git status --short --ignored` and add intentionally with `git add -f`.

## Anti-Patterns

- Do not redesign backend authorization to fix frontend session freshness.
- Do not hide platform/tenant entries with hardcoded frontend roles.
- Do not treat same display name as the same identity.
- Do not use full-fetch scans for large GCP resource lists; prefer official pagination/search plus frontend lazy loading.
- Do not commit unrelated dirty work.

## Cross-Skill Invocation

- Need independent post-implementation review -> `reality-auditor`.
- Need source-backed external API research -> `research-and-sourcing`.
- Need frontend interaction polish -> `frontend-expert`.
- Need root-cause analysis for failing auth/session behavior -> `debugging-mindset`.
