# Quickstart Live Replay Output

Date: 2026-07-01
Type: live_run
Runtime: Codex CLI, read-only sandbox
Workspace: `<repo-root>`

This file records real quickstart replay output for Guyue. It is intentionally not a polished marketing transcript. Deviations are kept because they show where the skill suite needs tighter product boundaries.

## Replay Method

Command pattern:

```bash
codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-replay-root.md "<prompt>"
```

Prompts were run with explicit "do not edit files" constraints. The goal was to verify routing, restraint, and boundary-setting in a real agent session.

## Runtime Notes

- Earlier live replay reported that the local `AGENTS.md` pointed to `RTK.md` while the repository did not contain `RTK.md`.
- 2026-07-01 follow-up work added `AGENTS.md` and `RTK.md` as lightweight coding-agent adapters. `SKILL.md` remains the public Skill entrypoint.
- The global skill environment emitted unrelated third-party skill load errors.
- The runtime also warned that the skills context budget was exceeded, so many external skill descriptions were omitted.

These are productization findings, not failures of the replay itself. They show that the public install path should stay lightweight and that noisy global skill roots can reduce reliability.

Runtime-entrypoint regression:

- Date: 2026-07-01
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-runtime-entrypoint-replay.md "<prompt>"`
- Result: pass
- Observed behavior: Codex read `RTK.md`, then loaded `SKILL.md`, `GUYUE_PRINCIPLES.md`, `skills_manifest.json`, and the relevant `requirement-analysis` child skill. The run did not report `RTK.md missing`.
- Remaining environment noise: unrelated global skill load errors and skills context budget warnings still appeared.

## Replay 1: Points Mall, "Write All Code Now"

Prompt:

```text
使用古月的思路评估这个需求：我们要新加一个积分商城功能，你直接帮我把前后端代码写好。只输出最终答复，不要编辑文件。
```

Observed trace:

```text
[Trace: Guyue/ProductSense] 这个需求不能直接进入“把前后端代码写好”。积分商城涉及资产、兑换、库存、风控、订单一致性和权限边界，不是普通展示页。
[Trace: Guyue/RequirementAnalysis] 当前输入缺少关键业务契约：积分来源、积分是否等价货币、兑换对象、库存扣减规则、退款/撤销、权限、审计、并发防刷。
[Trace: Guyue/SystemDesign] 建议先做单体内的 MVP，不上微服务、不引入消息队列、不做复杂营销玩法；用数据库事务和唯一约束守住资产一致性。
```

Result: pass

Why it passes:

- Refused to jump directly into full-stack implementation.
- Identified asset, inventory, audit, transaction, and authorization boundaries.
- Proposed an MVP and explicitly listed non-goals.
- Asked for confirmation before code.

Representative conclusion:

```text
确认后再进入代码阶段才合理。否则“直接写好前后端”看起来快，实际上是在没有业务契约的资产系统上堆代码，后续返工成本会很高。
```

## Replay 2: 500 Error, "Wrap It With Retry"

Prompt:

```text
使用古月的排障心法处理：线上接口挂了，报了500，是不是数据库超时了？帮我写一段重试代码包一下。只输出最终答复，不要编辑文件。
```

Observed trace:

```text
[Trace: Guyue/DebuggingMindset] 不能先假设“500 = 数据库超时”。重试只能包已确认可安全重试的瞬时错误，否则可能把接口打得更挂，或者重复写入数据。
```

Result: partial_pass

What worked:

- Rejected the assumption that every HTTP 500 means database timeout.
- Asked for application stack traces, database metrics, and request shape.
- Warned against retrying a whole request handler.
- Limited retry guidance to idempotent or read-only operations.

Deviation:

- The answer still included a concrete TypeScript retry helper before seeing logs or proving a transient, idempotent failure.

Follow-up fix:

- Tighten `debugging-mindset` so that, before raw logs or metrics are provided, it should only give an evidence checklist and safe containment options. Concrete retry code should wait until the failure type and idempotency boundary are known.

Boundary update:

- 2026-07-01 follow-up work added an explicit evidence gate to `debugging-mindset`: before raw logs, error codes, metrics, and idempotency boundaries are available, the agent must output `[等待日志/证据]` and must not provide concrete retry helper code or configuration patches.

Regression replay:

- Date: 2026-07-01
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-debug-boundary-after.md "<prompt>"`
- Result: pass
- Observed behavior: the live answer refused to assume database timeout, refused to write retry code, listed application logs, database metrics, request idempotency, impact scope, an RCA matrix, and ended with `[等待日志/证据]`.

Representative trace:

```text
[Trace: Guyue/DebuggingMindset] 触发证据闸门：当前只有“线上接口 500”这个症状，缺少原始错误栈、trace id、数据库指标、请求类型和幂等性边界，因此不能先假设是数据库超时，也不能直接写 retry 代码包住。
```

## Replay 3: Five-Level Referral Growth

Prompt:

```text
使用古月的产品感评估：我想做一个带 5 级分销裂变拉新功能的积分商城。只输出最终答复，不要编辑文件。
```

Observed trace:

```text
[Trace: Guyue/ProductSense] 启动商业直觉洞察，对齐 ROI、合规红线与真实增长假设。
```

Result: pass

Why it passes:

- Did not treat the request as a pure feature build.
- Flagged multi-level referral design as high risk.
- Recommended a safer MVP: points mall plus single-level invite task system.
- Asked to validate conversion, retention, and reward cost against LTV.

Representative conclusion:

```text
建议方案：做“积分商城 + 单级邀请任务系统”，不要做 5 级分销。
```

Source-quality note:

- The live answer referenced a general encyclopedia-style source for multi-level marketing. Future compliance-sensitive live runs should prefer official laws, regulations, platform rules, or legal/compliance review notes.

## Productization Follow-Ups

1. Keep public install instructions small and avoid loading every external skill into the same runtime context.
2. Add a stricter debugging live replay after updating `debugging-mindset`.
3. Prefer official or primary sources for compliance-sensitive product judgments.
4. Keep this evidence page updated with real replay results before release tags.
