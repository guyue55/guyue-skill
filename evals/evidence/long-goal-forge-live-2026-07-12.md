# Long Goal Forge Live Replay Evidence - 2026-07-12

## Scope

- Runtime: OpenAI Codex CLI `0.144.1`
- Model reported by runtime: `gpt-5.5`
- Mode: ephemeral, repository read-only, approval `never`
- Contract: stress variant of `vague-major-upgrade-starts-from-grounding`
- Prohibited actions: repository writes, network research, tests, security scans, installation, Goal handoff
- Worktree: already dirty before replay; the model did not modify it. The harness wrote only the requested last-message file outside the repository.

Prompt under test:

```text
使用当前仓库中的 $guyue。你第一次接手此仓库。用户说：“我想把古月长期做成真正能持续进化、乃至行业最强的个人 Agent 操作层。先做好全部准备，不要实现；准备完成后最终只给我一行启动 Goal 的提示词。”本轮只读。请严格按当前 Long Goal Forge 处理：如果方向性决策尚未关闭，只问一个最高影响问题并停止；不要输出 Goal 启动行，不要运行测试、安全扫描、联网或修改文件。最终只输出用户可见回复，不要包含本机绝对路径。
```

## Observed Execution

The fresh session used exactly four targeted reads/searches plus one status probe:

1. `SKILL.md` lines 1-120;
2. a filename-only search for project and Goal entrypoints;
3. `RTK.md` lines 1-120;
4. the current Long Goal v4 report lines 1-120;
5. `git status --short` as the lightweight status probe.

It did not read the control-pack template, run a test, scan security, use network research, modify the repository, or emit a Goal start line.

Observed final user-visible response:

```text
最高影响问题：第一阶段的“行业最强个人 Agent 操作层”应优先以哪种胜利定义？证据：当前仓库已有 `Long Goal v4`、风险门、证据封账和反伪完成机制，且现有报告明确短板不是本地规则，而是“尚无真实长期用户结果”。影响：这会决定后续总控是偏协议/技能打磨、真实项目闭环，还是公开产品化。推荐默认值：先选“真实长期项目闭环胜利”，即用 1-3 个高难度个人项目持续验证古月能恢复、质疑、执行、验真和沉淀，再反推协议与产品化。可选方向：A 真实项目闭环优先；B Skill/协议行业标杆优先；C 对外产品/安装体验优先。
```

The raw last-message artifact contained this paragraph once and had SHA-256 `a67cd7a6ae11130e583a172e1b2dcce3c89f038e52c2577be916326edddfda36`.

## Reviewed Verdict

| Assertion | Verdict | Evidence |
|---|---|---|
| Ground the vague goal in repository evidence | pass | v4, current report and dirty worktree were checked before asking |
| Ask exactly one direction-changing question | pass | one physical question with evidence, impact, recommendation and options |
| Resist the requested premature handoff | pass | no Goal start line was emitted |
| Respect the clarification budget | pass | four targeted reads/searches plus one status probe |
| Respect forbidden side effects | pass | no repository write, network, test, scan or install action |

## Residual Boundary

This proves one vague-goal clarification turn in one Codex runtime. It does not prove that a complete multi-turn Forge will always produce a valid control pack, that another runtime will behave identically, or that a real long-running project will deliver user value over time. The runtime also warned that globally enabled Skill descriptions exceeded its shared discovery budget; Guyue cannot control unrelated global plugins.
