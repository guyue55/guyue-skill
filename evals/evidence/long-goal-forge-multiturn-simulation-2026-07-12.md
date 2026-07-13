# Long Goal Forge Multi-Turn Simulation - 2026-07-12

## Scope

- Product fixture: a local Python Decision Ledger prototype with `add/list`, plain JSON storage, no tests, and known corruption risk
- Forge model for clarification: `gpt-5.6-luna`
- Final independent reviewer: `gpt-5.6-luna`
- Target boundary: disposable local project; no network, dependency installation, product implementation, push, tag, or release
- Guyue checker: installed separately from the target project and invoked with explicit `--repo-root`

## Multi-Turn Clarification

The fresh Forge session asked exactly one direction-changing question per turn:

1. **First user result**: daily record/review loop, data recovery, or decision-quality structure.
   - User chose the record/review loop.
   - The suggested 14-day usage target was corrected into a time-only outcome, explicitly excluded from Goal completion.
2. **Data semantics**: minimal record, structured outcome tracking, or immutable event ledger.
   - User chose stable ID, UTC creation time, decision, reason, optional result, and stable creation order.
3. **Minimum safety contract**: atomic local safety, happy-path only, or full backup/recovery system.
   - User chose atomic replacement, no overwrite after failed writes, preserved corrupt input, and actionable errors.

The session did not implement the product or emit a premature Goal handoff during these turns.

## Interruption And Recovery

After the third answer, the original Agent produced no file changes for more than two minutes and did not respond to a heartbeat interrupt. Two fresh write workers also produced no files in bounded waits. They were stopped rather than allowed to run indefinitely.

The three closed decisions were persisted to a durable decision packet before recovery. A fresh executor used that packet instead of chat memory and did not reopen the decisions.

Decision packet SHA-256:

```text
ab47fb298096a8788249ca134e738d053955b533b5444a33a7a22451f6e1767c
```

## External-Project Ready Pack

The recovered Forge produced a v4 master, execution ledger, phase plan, evidence index, and minimal evidence artifacts in the disposable target project. The first external CLI validation failed on:

- completion-boundary wording that was not machine-readable;
- an invalid replay class;
- no recognized replay classification.

After repair, structural ready validation passed. Independent semantic review then returned `FAIL` because baseline gaps were mislabeled as passing FINAL evidence, the risk gate pointed at the wrong evidence, a dirty Forge worktree claimed `clean@`, and the three decisions lacked an auditable file reference.

The pack and checker were repaired together:

- ready gaps use failing `ATTEMPT` evidence with `dirty@forge-ready`;
- complete `FINAL` evidence still requires `clean@A`;
- the risk gate points to the risk attempt;
- the frozen decision references the durable decision packet;
- two counterexamples freeze dirty ATTEMPT acceptance and dirty FINAL rejection.

The external target command then passed:

```bash
python3 <guyue-root>/scripts/check_long_goal_pack.py \
  --repo-root <target-repo> \
  --mode ready \
  docs/goals/decision-ledger-first-goal/goal-master.md
```

Final control-file SHA-256 values:

```text
goal-master.md                  9ef7e791305e6361d5e722ac14c833bf5ce2509fcbf79e95d44609697f259f96
execution-ledger.md             1cf143652b3d1aa3ddf330066f0ef2c88b03c9a2619d9122525051769d6d7925
phase-01-vertical-slice.md      1f096fab5acad0825f8061e3580342ba6cd23ce947dd817791e5273e9d42aeef
evidence/index.md               37271e9d9fba7158970a26640f36c0189645d2c3cf5e05f24433c99e9c21eff1
```

## Final Independent Handoff

The same reviewer that returned `FAIL` rechecked the repairs and returned exactly one physical line:

```text
以 docs/goals/decision-ledger-first-goal/goal-master.md 为唯一总控，先读取其执行账本并从下一入口开始；上下文恢复先读账本，失败或新事实证伪时暂停并按控制修订协议处理，未经用户批准不得改向；只有全部阶段完成、终局 FINAL 证据新鲜通过，且 A（实现）→B（证据）→C（仅更新总控与账本）封账链独立复算通过后，才可标记 Goal complete。
```

## Verdict

`PASS_WITH_REAL_FAILURES_PRESERVED`

This simulation proves multi-turn one-question clarification, time-horizon separation, durable decision recovery after an interrupted Agent, an external-project ready pack, checker-driven repair, independent semantic rejection, and one-line handoff after repair. It does not prove product implementation, fourteen days of use, public-network installation, or real-user value.
