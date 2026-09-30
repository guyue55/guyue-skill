# 参考驱动多智能体产品工程能力验证执行账本

## 当前指针
- 控制包版本：4
- 当前控制修订：REV-0001
- Goal ID：GOAL-REFERENCE-DRIVEN-PRODUCT-ENGINEERING
- 当前状态：终局候选
- 当前阶段 ID：PHASE-04
- 当前入口：ACT-004 已实施并通过定向验证；等待用户决定是否进入 ACT-005 暂存/提交封账或继续扩展产品契约模板
- 最近有效提交：eeb417359d8b53b12b95db9b3d48bf100c56cf86
- 最近新鲜证据：EVID-015
- 当前阻塞：无执行阻塞；ACT-005 未授权，因此不得暂存、提交、推送或发布
- 停止原因：ACT-004 最小入口修复已验证，等待用户下一步授权
- 完成判定：未完成

## 状态转换
- RUN-0001：铸造中 -> 铸造中；依据：方向与样本已批准，但独立审查推翻精确预算和动作已获批准的表述
- RUN-0002：铸造中 -> 就绪待执行；依据：用户批准 180 分钟、最多 6 份材料、3 个生产 Agent、1 个独立审查 turn、35 分钟唯一探针及无安装/提交/部署边界
- RUN-0003：就绪待执行 -> 终局候选；依据：PHASE-01 至 PHASE-04 完成候选证据，唯一活体探针失败并进入三路线裁决
- RUN-0004：终局候选 -> 终局候选；依据：用户批准 ACT-004，最小入口修复后同一类复合 B2B 工单提示进入 `product-delivery` 协作候选，但 ACT-005 未授权且不满足完成封账条件

## 设计门失败记录
| 尝试 ID | 控制修订 ID | 风险门 ID | 假设 ID | 实验 ID | 差异说明 | 失败证据 ID | 结论 |
|---|---|---|---|---|---|---|---|

## 阶段记录

### RUN-0001 · 2026-07-30T14:44:05+08:00 · Forge 收口
- 本轮输入：用户批准的参考驱动、必要澄清、多 Agent 协作方向、B2B 工单样本及低成本验证决定
- 本轮范围：只创建控制包并验证就绪；采用联网经验、预设模拟和最多一个最小活体探针，不开始完整产品实现
- 实际改动：新增总控、账本、四个阶段计划和证据索引
- 失败命令：无
- 修复动作：无
- 定向检查：待运行 ready 检查器
- 主线门禁：ready 机器检查曾通过；独立语义审查失败，见 `reviews/ready-review-001.md`
- 活体证据：待生成
- 证据新鲜度：控制包基线绑定 eeb417359d8b53b12b95db9b3d48bf100c56cf86
- 人工判断：用户已批准方向和样本；当时将“最多 8 份材料”等精确边界写成已批准的口径被独立审查推翻，后续以 RUN-0002 为准
- 提交记录：未提交
- 残余风险：模拟和单一探针不能证明成熟产品能力；真实运行时、模型能力与跨领域通用性仍未知
- 状态结论：铸造中；必须关闭预算授权及审查 P1 后才能重新进入 ready
- 下一入口：`docs/goals/reference-driven-product-engineering/phases/phase-01-baseline-and-experiment-contract.md`

### RUN-0002 · 2026-07-30T18:04:33+08:00 · 预算授权收口
- 本轮输入：用户确认批准修正版预算与动作边界
- 本轮范围：只修正 Forge 控制包，不开始 PHASE-02 联网研究，不运行正文活体探针
- 实际改动：统一墙钟 180 分钟与 PHASE-01/02/03/04 的 20/60/75/25 分钟预算；外部材料上限改为 6；唯一探针改为 35 分钟且失败不重试；新增 TASK-404 委派包；修正 NREQ-004 与 A/B/C 封账冲突；拆分 EVID-004 的 FINAL 审计与 EVID-014 的 ATTEMPT 探针结果
- 失败命令：无
- 修复动作：按 ready-review-001 的 P0/P1/P2 修正控制文本
- 定向检查：待重新运行 ready 检查器、安全扫描和独立只读复核
- 主线门禁：未通过前不得进入正文执行
- 活体证据：本轮仅更新 DEC-001 决定边界；正文探针尚未运行
- 证据新鲜度：EVID-006 晚于用户当前批准
- 人工判断：用户批准本 Goal 文件写入、只读联网、现有本地检查、一次 35 分钟内最小探针、最多 3 个生产 Agent 与 1 个独立审查 turn；未批准安装、付费、凭证、部署、外部写入、核心改造、Git 暂存、提交、合并、推送或发布
- 提交记录：未提交
- 残余风险：当前 ready 只证明控制包可执行；不证明 Guyue 已具备成熟产品构建能力
- 状态结论：就绪待执行；从 PHASE-01 开始，先重探工作树与运行时
- 下一入口：`docs/goals/reference-driven-product-engineering/phases/phase-01-baseline-and-experiment-contract.md`

### RUN-0003 · 2026-07-30T19:25:00+08:00 · 四阶段执行候选收束
- 本轮输入：PHASE-01 基线、PHASE-02 参考矩阵、TASK-301/302 生产模拟、TASK-303 独立评审、唯一最小活体探针
- 本轮范围：完成低成本研究、模拟、一次探针和能力裁决；不实现完整产品，不修改古月核心
- 实际改动：新增 PHASE-01/02/03/04 报告、固定产品契约、证据 artifacts，并更新证据索引
- 失败命令：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/try_guyue.py` 退出码 1，原因是工作树有未发布修改；唯一探针 `scripts/explain_route.py --json --limit 8 compound-b2b-product-engineering-goal` 退出码 0 但按判据失败，因 `selected=[]` 且 `collaboration_candidates=[]`
- 修复动作：无；探针按授权不得重试，失败进入 PHASE-04 裁决
- 定向检查：ready 检查器与安全扫描待最终复跑；TASK-404 待独立复核
- 主线门禁：GATE-001 结构链路由模拟覆盖，但活体入口被探针证伪，不能声明成熟能力
- 活体证据：EVID-014 为失败 ATTEMPT；EVID-004 只证明探针执行审计合规
- 证据新鲜度：EVID-001 至 EVID-014 已更新或保留，PHASE-04 裁决晚于探针
- 人工判断：建议优先修复现有入口，不新增万能 Skill；需要 ACT-004 才能实施修复
- 提交记录：未提交，ACT-005 未授权
- 残余风险：低成本模拟不能证明真实产品构建；当前路由入口负证据强；强模型可提高主对话表现但不能替代控制层入口
- 状态结论：终局候选；不得标记 complete
- 下一入口：`docs/goals/reference-driven-product-engineering/reviews/capability-decision-review-404.md` 独立复核

### RUN-0004 · 2026-07-30T20:05:00+08:00 · ACT-004 入口修复
- 本轮输入：用户批准 ACT-004
- 本轮范围：修复现有入口、Manifest、公共合同或运行时控制面的最小候选；不新增万能 Skill，不安装、不部署、不提交
- 实际改动：增强 `skills_manifest.json` 中既有 `product-delivery` workflow 的参考驱动产品触发、`research-and-sourcing` 入口和独立验收完成门；在 `evals/capability-collaboration.json` 增加复合 B2B 工单产品回归用例；新增 ACT-004 报告和 EVID-015
- 失败命令：无
- 修复动作：将原本 `selected=[]` 且 `collaboration_candidates=[]` 的复合产品提示转为 `product-delivery` 协作候选
- 定向检查：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/explain_route.py --json --limit 8 reference-driven-b2b-ticket-product-prompt` 退出码 0，返回 `lifecycle_state=collaboration_candidate` 和 `collaboration_candidates[0].id=product-delivery`
- 主线门禁：待最终回归检查完成后交付；当前不得声明 release-ready
- 活体证据：EVID-015
- 证据新鲜度：EVID-015 晚于用户 ACT-004 授权和入口修复
- 人工判断：本轮只证明入口协作候选恢复，不证明 Guyue 可凭一句提示稳定构建成熟生产级产品
- 提交记录：未提交，ACT-005 未授权
- 残余风险：能力链仍依赖 host 正确激活各 Skill；多 Agent 实作质量、长期成本、真实产品稳定性仍需后续分阶段验证
- 状态结论：终局候选；ACT-004 修复候选已验证，但不得标记 complete
- 下一入口：等待用户授权 ACT-005 或继续补产品契约模板与检查器
