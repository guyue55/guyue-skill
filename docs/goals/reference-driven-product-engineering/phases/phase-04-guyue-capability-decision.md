# PHASE-04 古月能力裁决

- Goal ID：GOAL-REFERENCE-DRIVEN-PRODUCT-ENGINEERING
- 阶段 ID：PHASE-04
- 状态：就绪待执行
- 阶段目标：将当前经验、固定模拟、唯一探针、成本和失败映射回 Guyue 当前能力，裁决是否值得投入完整产品验证
- 稳定输入：PHASE-01 至 PHASE-03 的来源、报告、审查、探针、耗时和失败记录
- 依赖：PHASE-03 完成或诚实阻塞
- 本阶段改动边界：本 Goal reports、reviews、evidence、总控和账本；只形成候选改造摘要
- 本阶段不做：不修改根控制面；不新增万能 Skill；不把模拟或探针外推为成熟产品能力
- 定向检查：承诺矩阵、来源、实验假设、协作收益、上下文成本、反证和三路线比较
- 主线门禁：每个“已有、缺失、应修现有、可能新增”结论都有对应证据和可推翻条件
- 活体验收：未参与模拟的审查者能复算推荐路线，并指出仍未知的能力边界
- 失败处理：证据不足则保持 `DIRECTION_UNPROVEN`，只给下一个最小真实证明
- 回滚方式：删除未批准候选补丁；保留裁决、反证和失败产物
- 人工检查点：用户决定停止、投入完整产品回放，或批准绑定具体版本的最小改造
- 阶段完成条件：REQ-005、RISK-001、RISK-003、全部 NREQ 有证据；结论没有越过本 Goal 证明层级
- 下一入口：等待用户对完整产品验证或具体 Guyue 改造作版本化授权

## 工作项
- TASK-401：将 GATE-001 各环节映射到现有 Guyue Skill、工作流和合同
- TASK-402：比较保持现状、修好现有入口、新增机制三条路线及其反证
- TASK-403：生成下一个最小真实证明或候选补丁摘要，不应用
- TASK-404：独立复核能力裁决、证据边界和完成口径；报告路径为 `docs/goals/reference-driven-product-engineering/reviews/capability-decision-review-404.md`，基线为 PHASE-01 至 PHASE-04 全部 FINAL/ATTEMPT 证据，预算为 1 个 Agent turn 且最多 25 分钟

## 副作用与重放
| 任务 ID | 副作用 | 重放类别 | 核验或补偿 |
|---|---|---|---|
| TASK-401 | 只读仓库与报告写入 | replay_safe | 先核对当前 Guyue 版本 |
| TASK-402 | 报告写入 | replay_safe | 新证据出现时追加，不删除反证 |
| TASK-403 | 候选摘要写入 | verify_before_repeat | 确认 ACT-004 未批准，不应用 |
| TASK-404 | 只读独立复核与报告写入；后续用户决策交互 | human_required | 先完成只读复核，不修改裁决；再绑定精确范围、成本、摘要和失效条件 |
