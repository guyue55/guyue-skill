# PHASE-01 基线与实验合同报告

- Goal ID：GOAL-REFERENCE-DRIVEN-PRODUCT-ENGINEERING
- 阶段：PHASE-01
- 生成时间：2026-07-30T18:20:00+08:00
- 控制修订：REV-0001
- 结论：DONE_WITH_CONCERNS

## 已确认基线

- 当前正式版本口径：README 声明 v1.7.2，当前开发清单含 26 个子 Skill、113 个路由用例、65 个行为合同、10 个协作用例、214 个近邻负例和 10 个工作流。
- 证据边界：README 明确这些证据只证明指定运行时、给定提示词和合成任务，不证明跨运行时、任意输入质量、真实用户价值或长期效果。
- Long Goal 能力：README 与当前检查器支持 Long Goal v4 的修订、风险门、委派收束、FINAL/ATTEMPT 证据和 A/B/C 封账。
- 当前工作树：执行前 `git status --short --branch` 显示 dirty，且存在本 Goal 之外的既有修改；本 Goal 执行不得改动或清理这些无关文件。
- 仓库根规则：任务上下文引用 `@RTK.md`，但仓库根下未发现 `AGENTS.md` 或 `RTK.md` 文件；本 Goal 以系统消息中的仓库规则和 Guyue 总控为准。

## 活体/本地检查

| 检查 | 命令 | 退出码 | 结论 |
|---|---|---:|---|
| Long Goal ready | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_long_goal_pack.py --repo-root repo-root --mode ready docs/goals/reference-driven-product-engineering/goal-master.md` | 0 | 控制包结构通过 |
| 安全扫描 | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/security_scanner.py` | 0 | 无泄漏阻断 |
| 30 秒验货 | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/try_guyue.py` | 1 | 因工作树有未发布修改，包体检查失败；不能继承 Forge 初始 clean 口径 |
| 复合目标路由 | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/explain_route.py "B2B 工单协作产品目标..."` | 0 | 无直接 Skill 命中，只给出弱相关候选；后续应把“跨 Skill 编排入口”列为核心待验证点 |

## 固定实验输入

- 代表产品情境：中等复杂度 B2B 工单协作产品。
- 用户目标：低门槛自然语言启动复杂产品工作；古月主动找参考、补问必要信息、组织多 Agent、主控集成，并用独立评审与真实检查收口。
- 本轮不做：完整产品实现、品牌资产复制、安装/下载外部代码、凭证/付费/部署/外部写入、修改 Guyue 根控制面、Git 暂存/提交/推送/发布。
- 成本边界：总墙钟 180 分钟；PHASE-01/02/03/04 为 20/60/75/25；最多 6 份外部原始材料；最多 3 个生产 Agent 各 1 turn，另加 1 个独立审查 turn；唯一活体探针 35 分钟内且失败不重试。

## PHASE-01 判断

PHASE-01 可进入 PHASE-02，但带两个关注项：

1. 现有确定性路由对“参考研究 + 需求澄清 + 多 Agent + 独立验收”的复合目标没有直接入口命中，后续模拟不能默认已有编排能力，需要具体映射。
2. 当前 dirty 工作树会使发布级载荷检查失败，后续证据必须使用 `dirty@...` 或未提交候选口径，不能声明 release-ready 或 clean 封账。
