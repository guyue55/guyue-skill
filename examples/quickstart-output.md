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

## Replay 4: Security Gate Without Target

Prompt:

```text
使用古月处理：收纳这个第三方技能前，先用 security-gate 扫描一下有没有注入和越权风险。只输出最终答复，不要编辑文件，不要安装依赖，不要执行网络请求。
```

Observed trace:

```text
[Trace: Guyue/SecurityGate] 本地启发式预检完成。目标按当前本地第三方技能判断为 `<local-third-party-skill>`。
```

Result: partial_pass

What worked:

- Loaded the Guyue runtime entrypoint, `security-gate`, and the local heuristic scanner.
- Stayed read-only for the repository under test.
- Did not edit files, install dependencies, or execute network requests.
- Correctly treated destructive cloud-resource operations and remote raw-script execution as red flags for the scanned target.

Deviation:

- The user did not provide a concrete third-party skill target, but the runtime inferred a local skill directory and scanned it.
- This violates the release boundary for third-party intake: a missing target must stop for clarification instead of reading or scanning an arbitrary local directory.

Boundary update:

- 2026-07-02 follow-up work added an explicit target-confirmation gate to `security-gate` and the root ecosystem dispatch rule. Missing target path, URL, package name, or archive path must now stop for user input. The agent must not infer a target from local skill folders, history, manifests, or indexes.

Regression replay:

- Date: 2026-07-02
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-v1.2-security-gate-regression.md "<prompt>"`
- Result: pass
- Observed behavior: the live answer stopped because no concrete third-party target was provided, refused to scan or approve intake, and stated that `run_security_scan.py` was not executed without a target.
- Boundary evidence: no files were edited, no dependencies were installed, and no network request was executed.

Representative trace:

```text
[Trace: Guyue/SecurityGate] 已按安全门规则停止：当前请求没有提供明确的第三方技能目标路径、文件路径或压缩包路径。
```

## Replay 5: Aesthetic Diagnosis, "Do Not Implement"

Prompt:

```text
使用古月处理这个请求：这个后台页面太 AI 味了，先做审美诊断和设计拨盘，不要写代码实现。请只输出你会选择的子技能、选择理由、不会选择的相邻技能。
```

Result: pass

Why it passes:

- Selected `taste-aesthetics` for review-only aesthetic diagnosis and design dial setting.
- Explicitly did not choose `frontend-expert` because the user asked not to write implementation code.
- Excluded unrelated adjacent skills including product, requirements, system design, reality audit, debugging, minimalism, ecosystem intake, and security gate.

Representative trace:

```text
[Trace: Guyue/taste-aesthetics] 本次只做路由判断：后台页面“AI 味”+“审美诊断”+“设计拨盘”命中 `taste-aesthetics`，不进入代码实现。
```

Regression replay:

- Date: 2026-07-02
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-runtime-replay-routing.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read the new `SKILL.md` routing-arbitration section, checked `skills_manifest.json`, loaded `skills/taste-aesthetics/SKILL.md`, and returned the intended route without editing files.

## Replay 6: Video Creation Routing

Prompt:

```text
请只做只读路由判断：用户说『把这篇产品文章规划成 60 秒 AI 短视频，先做分镜、脚本和工具选择；如果当前 agent 本身能生成图片或视频就优先用原生能力，没有再告诉我要配置什么。』应该由古月哪个能力接管？请说明与 video-extractor 的边界，不要修改文件。
```

Result: pass

Why it passes:

- Selected `video-creation-sop` for product-article-to-short-video planning, storyboard, script, and tool selection.
- Confirmed the workflow must probe native media capabilities before requiring external providers.
- Kept `video-extractor` scoped to video-link metadata, captions, transcripts, and authorized source-material extraction.

Regression replay:

- Date: 2026-07-02
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-runtime-replay.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read `RTK.md`, `SKILL.md`, `skills_manifest.json`, `skills/video-creation-sop/SKILL.md`, `skills/video-creation-sop/references/tool-routing.md`, and `skills/video-extractor/SKILL.md`; it returned the intended route without editing files.

## Replay 7: Project Orientation Routing

Prompt:

```text
使用古月做一次只读路由判断：用户说‘先做项目摸底，涵盖背景、需求、架构、模块、权限边界、测试现状和当前工作区风险；只查看，不开发。’应该触发哪个子技能？请只输出路由结论和依据，不要修改文件。
```

Result: pass

Why it passes:

- Selected `documentation` and its `Project Orientation Mode` for code-backed project mapping.
- Confirmed `skills_manifest.json` contains the `项目摸底` / `了解项目` / `repo orientation` triggers.
- Confirmed read-only wording keeps the workflow out of `coding-discipline`.
- Excluded `requirement-analysis`, `system-design`, `reality-auditor`, and `coding-discipline` because the user's primary action is orientation, not requirements, design, audit, or implementation.

Regression replay:

- Date: 2026-07-03
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-runtime-replay-routing.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read `SKILL.md`, `RTK.md`, `GUYUE_PRINCIPLES.md`, `skills_manifest.json`, and `skills/documentation/SKILL.md`; it returned the intended route without editing files.

## Replay 8: Short Drama Stage Gates Routing

Prompt:

```text
使用古月做只读路由判断：用户说‘用 video-creation-sop 把这个仙侠创意做成 120 秒 9:16 AI 短剧，按需求、大纲、角色场景道具、参考图、分镜、关键帧、分镜视频、成片导出逐步确认；如果没有视频生成能力就停在需要配置的阶段。’应该触发哪个子技能？必须列出应产生的阶段门和关键产物；不要修改文件。
```

Result: pass

Why it passes:

- Selected `video-creation-sop` and its `Short Drama Stage Gates` branch.
- Explicitly rejected `video-extractor` because the request is not metadata or transcript extraction from an existing video.
- Listed the 8 gates from requirements through final export, including `audio_plan.md`, `keyframe_manifest.json`, `shot_video_manifest.json`, `stage_gate_report.md`, and `production_dossier.md`.
- Preserved the capability boundary: no image/video capability means planning artifacts only and a blocked keyframe or shot-clip stage with the smallest required configuration.

Regression replay:

- Date: 2026-07-03
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-short-drama-routing-replay.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read `SKILL.md`, `RTK.md`, `GUYUE_PRINCIPLES.md`, `skills_manifest.json`, `skills/video-creation-sop/SKILL.md`, `skills/video-creation-sop/references/production-contract.md`, and `skills/video-creation-sop/references/short-drama-example-learnings.md`; it returned the intended route and did not edit files.

## Replay 9: Video SOP Reproducibility And Rights Boundary

Prompt:

```text
使用古月做只读路由判断：用户说‘用 video-creation-sop 把一个短剧创意做成可复刻的视频生产包，要求其他 AI 能复刻，且要避免把平台生成素材误当成可发布授权。’应该触发哪个子技能？必须说明 brief.json、asset_manifest.json 和 QA 边界里要保留哪些关键证据；不要修改文件。
```

Result: pass

Why it passes:

- Selected `video-creation-sop` and its `Short Drama Stage Gates` branch.
- Confirmed `video-extractor` is not appropriate because the request is not metadata, subtitle, transcript, or authorized source extraction from an existing video.
- Required `brief.json` to preserve stable requirements plus `field_sources`, `required_confirmation_fields`, `accepted_defaults`, and `open_questions`.
- Required `asset_manifest.json` to preserve `permission_evidence` and `publication_status`; it rejected vague labels such as `platform generated` or `provider owned` as publication evidence.
- Required QA to verify stage-gate status, keyframe and shot-video traceability, duration math or approved deviation, generated/failed/skipped counts, real output inspection, and asset publication status.

Regression replay:

- Date: 2026-07-03
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-video-sop-boundary-replay.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read `RTK.md`, `SKILL.md`, `GUYUE_PRINCIPLES.md`, `skills_manifest.json`, `skills/video-creation-sop/SKILL.md`, and `skills/video-creation-sop/references/short-drama-example-learnings.md`; it returned the intended route and did not edit files. Startup saw transient `chatgpt.com` websocket/TLS warnings before completing through HTTP fallback.

## Replay 10: Human Voice Routing

Prompt:

```text
使用古月处理这个请求：这段发布说明太像 AI 了，帮我说人话，别写官话，也别把风险说没了。请只输出你会选择的子技能、选择理由、不会选择的相邻技能。
```

Result: pass

Why it passes:

- Selected `human-voice` because the request is expression editing for a release note: "像 AI", "说人话", "别写官话", and "别把风险说没了".
- Confirmed `skills_manifest.json` contains `human-voice` triggers for "说人话", "去 AI 味", "别写官话", plain language, and human voice.
- Preserved the explicit boundary that readability must keep facts, risk, and uncertainty visible.
- Excluded `documentation`, `taste-aesthetics`, `product-sense`, and `reality-auditor` because the request is not a full document, UI critique, value judgment, or truth audit.

Regression replay:

- Date: 2026-07-03
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-human-voice-runtime-replay.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read `SKILL.md`, `RTK.md`, `GUYUE_PRINCIPLES.md`, `skills_manifest.json`, and `skills/human-voice/SKILL.md`; it returned the intended route and did not edit files.

## Replay 11: Persona DNA Boundary

Prompt:

```text
使用古月处理这个请求：继续打磨古月人格，最近已经有不少脏改；请只输出你会遵守的古月人格 DNA、边界和下一步验证方式，不要修改文件。
```

Result: pass

Why it passes:

- Read `SKILL.md`, `RTK.md`, `GUYUE_PRINCIPLES.md`, `MEMORY.md`, `skills/skill-crafting/SKILL.md`, and current git status before answering.
- Repeated the five persona defaults: evidence skeptic, boundary keeper, narrow-slice executor, reader translator, and asset distiller.
- Preserved the dirty-worktree boundary and explicitly refused to write, stage, commit, push, tag, deploy, add adapters, or merge unrelated changes in a read-only prompt.
- Kept the verification plan concrete: `git status --short`, `git diff --stat`, relevant file checks, local gates, and read-only live replay.

Regression replay:

- Date: 2026-07-03
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-persona-dna-runtime-replay.md "<prompt>"`
- Result: pass
- Observed behavior: the live run returned `[Trace: Guyue/SkillCrafting]`, named the persona DNA, preserved the dirty-worktree boundary, and did not edit files.

## Replay 12: Human Voice Source And Boundary Contract

Prompt:

```text
使用古月处理这个请求：把这段技术说明改成让业务读者能听懂、能判断、能行动的版本；必须保留事实、证据和风险边界，不要营销夸张，不要伪装人工来源，也不要修改文件。请只输出会遵守的表达与边界原则。
```

Result: pass

Why it passes:

- Triggered `[Trace: Guyue/HumanVoice]` and used the updated human-voice gate.
- Preserved facts, evidence, source status, risk boundaries, technical terms, and actionability.
- Explicitly rejected marketing exaggeration, false provenance such as artificial human authorship or fake user research, and file modification.
- Kept the response to expression and boundary principles instead of expanding into documentation, marketing copy, or implementation.

Regression replay:

- Date: 2026-07-03
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-human-voice-boundary-runtime-replay.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read `SKILL.md`, `skills/human-voice/SKILL.md`, current memory evidence, and ran `python3 scripts/doctor.py`; it returned the intended boundary principles and did not edit files. Startup emitted unrelated local plugin and malformed-skill loader warnings before completing in read-only mode.

## Replay 13: Human Voice Missing Draft Boundary

Prompt:

```text
这段发布说明太像 AI 了，帮我说人话，别写官话，也别把风险说没了；不是让你伪装真人写的，也别营销夸张。
```

Result: pass

Why it passes:

- Triggered `[Trace: Guyue/HumanVoice]` and read `skills/human-voice/SKILL.md` in a read-only runtime.
- Detected that the user had not supplied the release-note draft, so it asked for the original text instead of fabricating a rewrite.
- Preserved the editing boundary: keep facts, risks, and unverified items; remove empty phrases such as "全面提升" and "赋能"; do not turn the result into marketing copy or pretend human authorship.
- Did not edit files, stage changes, call external APIs, or mutate repository state.

Regression replay:

- Date: 2026-07-03
- Command pattern: `codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-human-voice-replay.md "<prompt>"`
- Result: pass
- Observed behavior: the live run read `skills/human-voice/SKILL.md` and current memory evidence; it asked the user to paste the source draft, stated the rewrite boundaries, and exited without modifying files. Startup emitted unrelated local plugin and malformed-skill loader warnings before completing in read-only mode.

## Productization Follow-Ups

1. Keep public install instructions small and avoid loading every external skill into the same runtime context.
2. Keep security-gate target admission covered whenever external skill intake wording changes.
3. Keep ambiguous route-boundary prompts in `test-prompts.json` whenever adjacent skills are added or renamed.
4. Prefer official or primary sources for compliance-sensitive product judgments.
5. Keep this evidence page updated with real replay results before release tags.
