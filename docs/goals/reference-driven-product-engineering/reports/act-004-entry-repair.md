# ACT-004 入口修复报告

- Goal ID：GOAL-REFERENCE-DRIVEN-PRODUCT-ENGINEERING
- 执行时间：2026-07-30T19:55:00+08:00
- 授权：用户批准 ACT-004
- 结论：实施最小入口修复候选，不新增万能 Skill

## 修改范围

- `skills_manifest.json`：增强既有 `product-delivery` 协作 workflow，使“参考驱动产品工程 / 成熟可用稳定的 B2B 工单协作产品 / 主动寻找参考 / 产品契约 / 多 Agent 分工 / 独立评委和可执行检查器验收”等复合目标能进入协作候选。
- `evals/capability-collaboration.json`：新增一条复合 B2B 工单产品目标回归用例，期望仍走既有 `product-delivery` workflow。

## 设计取舍

- 不新增第 28 个 Skill。
- 不新增大型万能 workflow。
- 不改路由算法。
- 不安装、不部署、不提交。
- 只让已有产品交付链在需要时显式包含 `research-and-sourcing`，再进入 `product-sense`、`requirement-analysis`、`system-design`、`coding-discipline` 和 `reality-auditor`。

## 预期验证

先前失败的唯一探针应从 `selected=[]` 且 `collaboration_candidates=[]`，变成至少返回 `product-delivery` 协作候选。该结果只证明入口候选被修复，不证明成熟产品已可自动构建。

## 实际验证

- 复测命令：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/explain_route.py --json --limit 8 reference-driven-b2b-ticket-product-prompt`
- 退出码：0
- 结果：`lifecycle_state=collaboration_candidate`，`collaboration_candidates[0].id=product-delivery`，`score=200.0`
- 命中触发：`成熟可用稳定的 B2B 工单协作产品`、`主动寻找合适参考`、`形成产品契约`、`组织多 Agent 分工`、`独立评委和可执行检查器验收`
- 阶段链：`research-and-sourcing` -> `product-sense` / `requirement-analysis` -> `system-design` -> `coding-discipline` / `code-minimalism` / `frontend-expert` / `taste-aesthetics` -> `reality-auditor` -> `documentation` / `human-voice`

## 边界

- 这次修复证明“复合产品目标能进入受控协作候选入口”。
- 这次修复不证明“一个简单提示词即可稳定产出成熟生产级产品”。
- ACT-004 执行阶段没有执行 ACT-005，因此当时未暂存、未提交、未推送、未发布。
