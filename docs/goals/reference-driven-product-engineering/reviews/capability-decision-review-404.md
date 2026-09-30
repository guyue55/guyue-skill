# TASK-404 独立复核：PHASE-04 能力裁决

- Goal ID：GOAL-REFERENCE-DRIVEN-PRODUCT-ENGINEERING
- 阶段：PHASE-04
- 复核时间：2026-07-30T19:40:00+08:00
- 复核者：独立复核 Agent，未参与 PHASE-04 裁决产出
- 范围：只读复核指定输入；只写本报告；未联网；未安装；未修改古月核心；未修改裁决报告；未提交
- 结论：READY

## 1. 输入完整性

已读取并用于本复核：

1. `docs/goals/reference-driven-product-engineering/goal-master.md`
2. `docs/goals/reference-driven-product-engineering/execution-ledger.md`
3. `docs/goals/reference-driven-product-engineering/evidence/index.md`
4. `docs/goals/reference-driven-product-engineering/reports/guyue-capability-decision.md`
5. `docs/goals/reference-driven-product-engineering/evidence/artifacts/minimal-live-probe-result.json`
6. `docs/goals/reference-driven-product-engineering/reviews/independent-review-303.md`

补充只读核对：

1. `docs/goals/reference-driven-product-engineering/evidence/artifacts/external-side-effect-audit.json`
2. `docs/goals/reference-driven-product-engineering/evidence/artifacts/root-control-non-change.json`
3. `docs/goals/reference-driven-product-engineering/evidence/artifacts/maturity-claim-boundary.json`
4. `git status --short`

注意：任务上下文要求 `@RTK.md`，但当前仓库根目录未发现 `RTK.md` 或 `AGENTS.md`；本复核沿用上级显式任务边界、系统规则和 Goal 总控。

## 2. 裁决是否被证据支持

判断：支持。

PHASE-04 的核心裁决是：

- 古月具备“参考驱动、多角色拆解、证据门控、边界收束”的能力骨架；
- 当前不具备“普通用户一句复合产品目标就稳定自动进入参考研究、必要澄清、多 Agent 协作、主控集成、独立验收”的产品化入口；
- 推荐路线是 B：修复现有入口，而不是保持现状或新增万能 Skill；
- 未获 ACT-005 时只能停在“终局候选”，不得 complete。

该裁决与证据链一致：

| 复核点 | 证据 | 结论 |
|---|---|---|
| 能力骨架存在 | PHASE-01/02/03 产物经 EVID-001 至 EVID-003 登记为 FINAL；TASK-303 认可 GATE-001 的结构链路覆盖 | 支持“骨架存在”，但仅是研究与模拟等级 |
| 产品化入口不足 | `minimal-live-probe-result.json` 记录 `selected_count=0`、`collaboration_candidates_count=0`，且核心 Skill 被判为 `insufficient_signal` | 支持“入口层强负证据” |
| 三路线裁决 | PHASE-04 明确 A 不建议、B 建议、C 暂不建议 | 与探针失败和既有窄 Skill 可承载的判断一致 |
| 终局候选边界 | 总控、账本和裁决均写明 ACT-005 未授权，不得 complete | 支持停在终局候选 |

## 3. 唯一探针失败处理

判断：处理正确。

TASK-303 指定的唯一探针判据要求：退出码为 0 且至少有直接 `selected` 路由或明确 `collaboration_candidates`，并覆盖参考研究、需求澄清、产品契约、多 Agent、主控、现实审计等关键链路中的至少 4 类。

实际结果：

- 命令退出码：0
- `selected_count`：0
- `collaboration_candidates_count`：0
- 本地候选偏离主链：`understand`、GCP、GSAP、notebook、PDB、workshop 等
- 核心候选被拒：`research-and-sourcing`、`requirement-analysis`、`system-design`、`coding-discipline`、`reality-auditor`、`product-sense`、`context-compressor`
- 证据等级：`LIVE_ATTEMPT_HIGH_NEGATIVE`
- 重试状态：`not_allowed`

PHASE-04 没有把退出码 0 误判为通过，而是把“输出可解析但路由失败”作为入口层强负证据；也没有追加第二探针、扩张为实现或把失败掩盖为模型能力问题。因此处理符合总控的“唯一探针失败后直接进入能力裁决”规则。

## 4. 是否越界宣称成熟产品或简单提示词稳定构建产品

判断：未越界。

PHASE-04 明确禁止以下口径：

- 普通用户一句话就能稳定得到成熟 SaaS；
- 多 Agent 越多越好；
- 同模型评委满意等于独立验收；
- 模拟报告或路由检查通过等于真实产品可用；
- 强模型可以替代权限、状态机、真实数据、测试、部署、运维和用户反馈。

PHASE-04 的正向表达也被限定为“部分能力骨架”“强模型和明确总控协助下的纵向验证”“可验证纵向切片和投资决策证据”，没有宣称已经构建成熟、可用、稳定产品。

## 5. 是否违反未授权动作

判断：未见违反。

依据：

- `external-side-effect-audit.json` 记录未执行安装、下载外部代码或资产、凭证使用、付费、部署、外部写入、Git 暂存、Git 提交、Git 推送、发布。
- `root-control-non-change.json` 记录未修改 Guyue 根 `SKILL.md`、`skills_manifest.json`、公共行为合同或运行时控制面；候选修复只写入 Goal 报告。
- `git status --short` 显示工作树存在既有修改与 `docs/goals/` 未跟踪文件，但本复核没有看到 PHASE-04 把这些修改宣称为已提交或已发布。

保留说明：工作树当前 dirty，且 `git status --short` 显示 `skills_manifest.json` 等根控制相关文件已有修改；本复核只能确认裁决与审计文件没有把这些修改归因为已授权核心改造或已提交结果。若后续要进入 ACT-004/ACT-005，必须先做精确 diff 归因。

## 6. 是否正确停在终局候选而不是 complete

判断：正确。

总控最终完成定义写明：无 ACT-005 时只能停在未提交终局候选，不得标记 complete。执行账本当前指针也写明：

- 当前状态：终局候选
- 当前阻塞：无执行阻塞；ACT-005 未授权，因此不得标记 complete 或提交封账
- 完成判定：未完成

PHASE-04 裁决报告同样写明“终局候选；不得标记 complete，因为 ACT-005 未授权 Git 封账”。该口径与总控一致。

## 7. 非阻塞风险

以下风险不阻止 READY，但必须在交付用户时保留：

1. 唯一活体探针是强负证据：当前复合目标入口未能路由到参考、需求、系统设计、编码纪律和现实审计主链。
2. 正向证据主要来自研究、固定情境模拟和独立评审，不是完整真实产品构建。
3. TASK-303 指出的主控集成产物、评委回炉闭环、参考到验收的结构化可检查性仍不足。
4. 当前工作树 dirty，不能导出 release-ready、clean 封账或发布级结论。
5. 后续修复现有入口需要 ACT-004；任何 Git 暂存、提交、合并、推送或发布需要 ACT-005。

## 8. 最终状态

READY
