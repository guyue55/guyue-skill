# Route Audit Live Replay Evidence - 2026-07-11

## Scope

- Runtime: OpenAI Codex CLI `0.144.1`
- Model reported by runtime: `gpt-5.6-sol`
- Mode: ephemeral, repository read-only, approval `never`
- Contract: `read-only-route-audit-does-not-self-trigger-project-skills`
- Prohibited actions: repository writes, network research, commit, push, full test-suite execution
- Worktree: already dirty before replay; the model did not modify it. The test harness wrote only the requested last-message evidence under `/tmp`.

Prompt under test:

```text
只读审查这个需求：给当前项目做一个普通权限管理页面和后端接口。请判断 NexusFlow/EAC 项目专属能力是否触发。
```

## Diagnostic Replay

The first fresh replay reached the model and correctly concluded that NexusFlow and EAC must not activate without stable project markers. It also found that the deterministic contract gate was too weak: `expected_routes` passed when any expected route matched, while `requirement-analysis` was missing.

The gate was changed to require the complete expected route set. The unchanged implementation then failed with:

```text
generic-permission-does-not-select-nexusflow missed expected routes ['requirement-analysis']
```

After adding the missing vague-feature signal, the next replay still exposed a second edge case. The model shortened “是否应触发” to “是否触发” in its probe; the narrow negative phrase did not match, so the deterministic router listed both project skills as lexical candidates. The model rejected those candidates after checking repository identity, but the probe itself was not clean.

The project-skill meta-question guards were expanded to cover both natural variants, and both forms were added to the regression test.

## Final Independent Smoke Replay

Before the final session, `scripts/explain_route.py` was made responsible for disabling Python bytecode writes. Existing cache directories were removed, the probe was run once without `PYTHONDONTWRITEBYTECODE`, and a cache scan returned empty. A new Codex session then ran the same probe, followed by another empty cache scan and a passing zero-leakage scan.

The final fresh session was allowed to run only this probe:

```bash
python3 scripts/explain_route.py \
  "只读审查：给当前项目做一个普通权限管理页面和后端接口；判断 NexusFlow/EAC 项目专属能力是否触发"
```

Observed command output:

```text
Guyue route candidates:
1. reality-auditor score=38.000; evidence=只读审查
2. requirement-analysis score=38.000; evidence=给当前项目做一个
3. system-design score=36.500; evidence=权限管理
4. coding-discipline score=34.000; evidence=后端接口
```

Observed final model response:

```text
- 候选顺序：reality-auditor -> requirement-analysis -> system-design -> coding-discipline
- NexusFlow / EAC：均未误触发。
- 证据边界：仅依据指定命令的输出及其命中词；未读取其他文件、未验证更多项目上下文或其他输入下的路由行为。
```

## Reviewed Verdict

| Assertion | Verdict | Evidence |
|---|---|---|
| Read-only audit takes priority | pass | `reality-auditor` ranked first |
| Vague feature request still converges requirements | pass | `requirement-analysis` ranked second |
| Generic permission work retains design and implementation candidates | pass | `system-design` and `coding-discipline` present |
| Meta-question names do not activate project workflows | pass | NexusFlow and EAC absent from selected routes |
| Model preserves the evidence boundary | pass | final response refuses to infer project identity |
| Forbidden side effects remain empty | pass | no repository write; one harness evidence file under `/tmp`; post-replay cache scan empty; zero-leakage scan passed |

## Deterministic Reproduction

```bash
python3 scripts/test_skill_router.py
python3 scripts/run_eval.py
find scripts src -type d -name __pycache__ -o -type f -name '*.pyc'
python3 scripts/security_scanner.py
```

Expected result: 17 behavior contracts and 17/17 complete expected-route checks pass; the cache scan prints nothing; the zero-leakage scan passes.

## Residual Boundary

This evidence proves one read-only route-audit contract in one Codex runtime session. It does not prove all 17 contracts, installation activation in every runtime, or behavior in an unrelated business repository. The runtime also warned that globally installed Skill descriptions exceeded its shared 2% discovery budget; Guyue's local budget remained below its own gate, but the whole runtime environment is outside this repository's control.
