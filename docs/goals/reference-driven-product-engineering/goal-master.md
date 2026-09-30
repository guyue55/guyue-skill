# 参考驱动多智能体产品工程能力验证总控

## 控制信息
- 控制包版本：4
- 当前控制修订：REV-0001
- Goal ID：GOAL-REFERENCE-DRIVEN-PRODUCT-ENGINEERING
- 状态：终局候选
- 唯一总控：本文件
- 执行账本：docs/goals/reference-driven-product-engineering/execution-ledger.md
- 阶段计划目录：docs/goals/reference-driven-product-engineering/phases
- 活体证据索引：docs/goals/reference-driven-product-engineering/evidence/index.md
- 基线提交或版本：eeb417359d8b53b12b95db9b3d48bf100c56cf86
- 最后审查时间：2026-07-30T20:05:00+08:00

## 状态机
- 正向：铸造中 -> 就绪待执行 -> 执行中 -> 终局候选 -> 完成
- 恢复：执行中 -> 阻塞 -> 执行中
- 设计复核：执行中 -> BLOCKED_DESIGN_REVIEW_REQUIRED；只有用户批准新修订后，BLOCKED_DESIGN_REVIEW_REQUIRED -> 执行中
- 规则：状态变化必须写入账本；`停止原因`只说明本轮为何停止，`完成判定`只有全部完成定义满足时才能写“通过”。

## 控制权与三层时间尺度
- 权威顺序：用户已确认目标与版本化授权 > 仓库规则 > 本总控 > 阶段验收契约 > 阶段计划 > 执行账本
- 当前控制基线：提交 `eeb417359d8b53b12b95db9b3d48bf100c56cf86` 上的 Guyue v1.7.2 能力声明、Forge 时点工作树快照，以及用户最终批准的“联网经验 + 预设模拟 + 最小活体探针”范围
- 替代或继承：无旧控制包；Forge 中未通过 ready 门的完整产品草案已被成本决定替换，不具有执行权
- 历史完成权：撤销任何“真实产品构建能力已完成”的旧口径；保留现有 26/26 活体激活、合成产出与 Long Goal 检查结果作为有限能力基线
- 控制完整性边界：检查器通过只证明控制结构完整，不证明产品完成
- 终极愿景：古月能让普通用户以低门槛自然语言启动复杂产品工作，由系统主动寻找合适参考、澄清必要信息、组织多智能体协作并以真实产品证据迭代收口
- 本 Goal 交付：在 180 分钟总墙钟主动执行上限内，通过当前一手经验、固定 B2B 工单产品情境、多智能体模拟和最多一个最小活体探针，判断现有古月是否具备该能力骨架、真实缺口和是否值得进入完整产品验证
- 时间型结果：成熟稳定产品、跨领域复现、跨模型收益、真实用户采用和长期生产效率均不在本 Goal 内宣称完成
- 活跃控制文档上限：7
- 控制包推翻条件：模拟无法代表用户目标到验收链路；现有运行时不能执行最小活体探针；外部材料或 Guyue 当前实现推翻关键前提；预算不足以区分三条路线。触发后暂停并请求新修订，不扩大成本

## 控制修订记录
| 修订 ID | 前序修订 | 控制基线 | 批准动作 ID | 触发风险门 | 状态 | 变更原因 |
|---|---|---|---|---|---|---|
| REV-0001 | 无（首次建立） | eeb417359d8b53b12b95db9b3d48bf100c56cf86 | 无（首次建立） | 无（首次建立） | ACTIVE | 用户批准参考驱动、必要交互、多 Agent 协作方向、B2B 工单样本、180 分钟总墙钟、最多 6 份材料、最多 3 个生产 Agent、1 个独立审查 turn、一次 35 分钟内最小探针及无安装/提交/部署边界 |

## 活跃控制文档清单
| 文档角色 | 仓库相对路径 |
|---|---|
| MASTER | docs/goals/reference-driven-product-engineering/goal-master.md |
| LEDGER | docs/goals/reference-driven-product-engineering/execution-ledger.md |
| PHASE | docs/goals/reference-driven-product-engineering/phases/phase-01-baseline-and-experiment-contract.md |
| PHASE | docs/goals/reference-driven-product-engineering/phases/phase-02-reference-research-and-product-contract.md |
| PHASE | docs/goals/reference-driven-product-engineering/phases/phase-03-simulation-and-live-probe.md |
| PHASE | docs/goals/reference-driven-product-engineering/phases/phase-04-guyue-capability-decision.md |
| EVIDENCE_INDEX | docs/goals/reference-driven-product-engineering/evidence/index.md |

## 认知与实验台账
| 认知 ID | 类型 | 命题 | 当前证据 | 证伪或通过标准 | 关联项 | 失败或删除路径 |
|---|---|---|---|---|---|---|
| FACT-001 | VERIFIED_FACT | Guyue v1.7.2 已有 26 个窄 Skill、Long Goal v4、协作合同、活体回放和独立审查，但 README 明确不把合成任务扩大为真实用户价值 | README.md；docs/guyue-long-goal-meta-control-polish-2026-07-11.md | 出现当前版本、真实产品、完整端到端且可复算的既有证据 | FDEC-001 | 重开“是否需要后续完整验证”决定 |
| FACT-002 | VERIFIED_FACT | Forge 初始调查时工作树无未提交改动，dev 分支比 origin/dev 领先 1 个提交；当前执行前必须重新探测工作树，因为后续出现本 Goal 文件和其他既有改动 | `git status --short --branch` 于 2026-07-30；RUN-0002 记录 | 当前工作树或基线提交影响本 Goal 执行路径 | FDEC-002 | PHASE-01 执行前重建基线，不继承旧 clean 口径 |
| FDEC-001 | FROZEN_DECISION | 首个代表情境为中等复杂度 B2B 工单协作产品，并允许必要用户澄清、主动参考研究和多 Agent 协作 | 用户明确批准 | 只有用户批准的新 REV 可改变 | FACT-001 | 暂停并追加控制修订 |
| FDEC-002 | FROZEN_DECISION | 本轮采用低成本验证，总墙钟主动执行不超过 180 分钟；PHASE-01/02/03/04 分别不超过 20/60/75/25 分钟；不完整实现产品，不修改古月核心 | 用户在 Forge ready 前作出的精确成本决定 | 只有用户批准的新 REV 可改变 | FACT-002 | 到预算即停止并保留当前证据 |
| HYP-001 | HYPOTHESIS | 现有 Guyue 的窄 Skill 与 Long Goal 已能组成参考驱动、必要澄清、多 Agent 和独立验收的能力骨架 | 现有组件与行为合同提供候选依据 | EXP-001 的固定情境模拟能从目标贯穿到验收，且每一步都有现有入口、稳定产物和停止条件 | EXP-001 | 失败后定位缺口，不新增万能 Skill |
| EXP-001 | EXPERIMENT | 用冻结的工单产品快照模拟参考研究、需求澄清、任务编排、主控集成、评委回炉和恢复 | PHASE-01 固定输入 | 模拟链路完整、承诺可追踪、无越权、无无界循环；任一缺口均记录而不脑补 | HYP-001 | 记录 ATTEMPT 并进入能力裁决 |
| HYP-002 | HYPOTHESIS | 最小活体探针能发现纯文档模拟无法暴露的路由、上下文或协作问题 | README 明确区分合成证据与真实运行 | EXP-002 至少推翻或确认一个关键链路假设，且成本不超过 35 分钟 | EXP-002 | 若无可测关键点则跳过并明确证据降级 |
| EXP-002 | EXPERIMENT | 只对模拟中最高不确定环节运行一次现有 Guyue 活体入口或最小 Agent 回放 | EXP-001 的最大证据缺口 | 有真实命令、退出码、输出、时间和独立复核；不要求完成产品 | HYP-002 | 失败即保留 ATTEMPT，不续跑第二探针 |

## 风险门与先纵切后扩张
- 扩张规则：先纵切后扩张；GATE-001 只允许从研究和模拟进入一个最小活体探针，通过前后均不得扩张为完整产品、批量 Agent、依赖或基础设施建设。
- 设计复核规则：本 Goal 不做三轮产品实现；模拟或唯一探针失败后直接进入能力裁决。若未来完整验证同一门完成 3 次差异化实验仍失败，必须进入 `BLOCKED_DESIGN_REVIEW_REQUIRED`。

| 风险门 ID | 用户结果 | 纵向切片 | 失败判据 | 放行证据 | 扩张权限 |
|---|---|---|---|---|---|
| GATE-001 | 用户给出产品目标后，古月能找到参考、补问必要信息、组织协作并以外部标准验收，而不是随意生成 | 固定目标与产品快照贯穿参考矩阵、需求决定、委派包、主控集成、评委问题、返工和停止 | 任一步无现有入口；同模型自评分冒充独立证据；缺少用户决策点、成本门或恢复状态 | EVID-006 | 仅允许进入一次最小活体探针和 PHASE-04 能力裁决 |

## 阶段计划清单
- `docs/goals/reference-driven-product-engineering/phases/phase-01-baseline-and-experiment-contract.md`
- `docs/goals/reference-driven-product-engineering/phases/phase-02-reference-research-and-product-contract.md`
- `docs/goals/reference-driven-product-engineering/phases/phase-03-simulation-and-live-probe.md`
- `docs/goals/reference-driven-product-engineering/phases/phase-04-guyue-capability-decision.md`

## 愿景与真实需求
- 真实用户：能描述业务目标并回答必要问题，但不应被要求自己完成竞品研究、完整 PRD、架构设计、多角色协调和验收工程的产品发起者
- 核心场景：古月主动寻找适合的产品、案例与标准，向用户补问不可推断的信息，组织专业 Agent 设计、开发和验收
- 当前替代方式：用户反复写长提示词、手工安排 Agent、自己寻找参考并追踪阶段缺口
- 不做的后果：古月虽有子能力，却仍可能把专业编排成本转嫁给用户
- 最终目标：以较低成本得到一份可复算的能力地图，决定是否值得投入完整真实产品验证

## 项目现场
- 已确认事实：README 声明 26 个 Skill、10 个工作流、65 个行为合同及活体与合成证据边界；Long Goal v4 已能管理修订、风险门、委派收束与封账
- 合理推断：`research-and-sourcing`、`requirement-analysis`、`system-design`、`coding-discipline`、`reality-auditor` 和 Long Goal 可组成候选主链，但组合质量尚未被真实产品证明
- 已关闭冲突：目标不是“模糊输入零交互生成”；完整产品回放成本过高，本轮改用联网经验、预设模拟和最小活体探针
- 事实源：SKILL.md、README.md、skills/*/SKILL.md、skills_manifest.json、docs/long-goal-protocol.md、外部一手材料和本 Goal 生成的可复算产物
- 当前基线：控制与合成证据较强；参考驱动端到端产品工程和真实用户价值未证明

## 范围契约
- 必须完成：冻结基线和模拟输入；研究当前经验与产品参考；模拟完整多 Agent 挑战链；至多运行一个最小活体探针；形成三路线裁决
- 明确不做：不完整实现 B2B 产品；不复制品牌和资产；不把模拟冒充成熟产品；除用户已批准的 ACT-004 最小入口修复外，不修改根 Skill、Manifest 或公共合同
- 必须保持：默认中文；来源可追踪；必要用户问题可见；并行任务所有权隔离；主控负责耦合集成；结论与证据层级一致
- 时间与成本边界：总主动执行墙钟不超过 180 分钟；PHASE-01 20 分钟，PHASE-02 60 分钟且最多 6 份外部原始材料，PHASE-03 75 分钟且唯一活体探针最多 35 分钟，PHASE-04 25 分钟
- 计量口径：一份材料指一个可独立访问的一手、官方或产品原始页面/文档，重复镜像只计一次；最多 3 个并行生产 Agent 各 1 个 turn，另加 1 个独立审查 turn；墙钟是硬上限，模型 turn 数单独记账但不能扩张墙钟
- 工具与权限边界：允许本地只读检查、本 Goal 文件写入、现有测试/回放工具和只读联网；安装、外部写入、凭证、付费、部署、提交和核心改造均不在授权内

## 方案与取舍
| 方案 | 用户价值 | 主要工作 | 成本与风险 | 结论 |
|---|---|---|---|---|
| 直接完整构建真实产品 | 证据最强 | 真实全栈、多 Agent、两轮加固 | 8–16 小时以上，Token 高 | 本轮放弃 |
| 只做联网与纸面分析 | 成本最低 | 资料总结和架构推演 | 无法暴露运行时问题 | 放弃 |
| 联网经验 + 固定情境模拟 + 一个最小活体探针 | 在成本与真实性间平衡 | 有界研究、完整链路模拟、最高不确定点实测 | 不能证明成熟产品，但足以决定是否继续投资 | 采用 |

### 推荐方案
- 总体方案：先用当前一手材料建立参考与控制基线，再在固定产品快照上模拟现有 Guyue 的端到端编排，最后只对最大证据缺口运行一个活体探针
- 架构边界：所有产物落在本 Goal 的 reports、reviews、evidence；不创建完整产品目录；不改根控制面
- 复用入口：现有 research、requirement、system-design、coding、reality-auditor、Long Goal 和活体评测入口
- 异常与兜底：外部材料不足则停止于未知；子任务无进展则回退主控；探针不可运行则输出证据降级，不用更多模拟伪装

## 阶段路线
| 阶段 ID | 目标 | 稳定输入 | 交付物 | 依赖 | 定向检查 | 活体验收 | 人工检查点 |
|---|---|---|---|---|---|---|---|
| PHASE-01 | 冻结基线、固定情境和成本合同 | REV-0001、eeb4173 | 基线报告、模拟夹具和量表 | 无 | 路径、预算、权限检查 | 可从空白上下文复述实验 | 模拟是否代表真实问题 |
| PHASE-02 | 建立当前经验与产品参考矩阵 | PHASE-01、最多 6 份原始材料 | 来源报告、参考矩阵和必要问题 | PHASE-01 | 来源日期与机制对账 | 参考可转为验收标准且不照搬 | 关键产品取舍 |
| PHASE-03 | 完成端到端模拟并运行最多一个探针 | 冻结参考与固定产品快照 | 模拟报告、委派报告、评委复核、活体 ATTEMPT/FINAL | PHASE-02 | 承诺、所有权、停止门、命令退出码 | 最高不确定环节有真实运行证据 | 模拟与真实差距 |
| PHASE-04 | 对 Guyue 能力作三路线裁决 | 全部研究、模拟、探针和成本证据 | 能力地图、缺口、最小下一证明 | PHASE-03 | 双向证据复算 | 独立审查能推翻或复述结论 | 是否投入完整产品验证 |

## 承诺覆盖矩阵
| 承诺 ID | 承诺或否定项 | 阶段 ID | 验证证据 |
|---|---|---|---|
| REQ-001 | 当前外部经验与代表产品参考有来源、日期和适用边界 | PHASE-02 | EVID-001 |
| REQ-002 | 固定产品目标能转为必要澄清、参考矩阵和产品契约 | PHASE-03 | EVID-002 |
| REQ-003 | 多 Agent 模拟有稳定输入、独占所有权、主控集成和独立评审 | PHASE-03 | EVID-003 |
| REQ-004 | 最大证据缺口由一次 35 分钟内的探针执行审计验证；探针真实结果另以 EVID-014 的 ATTEMPT 记录且失败不重试 | PHASE-03 | EVID-004 |
| REQ-005 | 形成结合 Guyue 当前实现的保持、修复、新增三路线裁决 | PHASE-04 | EVID-005 |
| DEC-001 | 用户批准修正版方向、B2B 样本和 180 分钟低成本验证边界 | PHASE-01 | EVID-006 |
| DEC-002 | 用户批准 ACT-004，并完成最小入口修复候选验证 | PHASE-04 | EVID-015 |
| RISK-001 | 模拟、同模型评委和检查器不得冒充成熟产品或真实用户价值 | PHASE-04 | EVID-007 |
| RISK-002 | Agent 并行不得越过所有权、重复调查或用无进展冒充协作 | PHASE-03 | EVID-008 |
| RISK-003 | 研究、循环、子任务和探针必须在冻结预算内停止 | PHASE-04 | EVID-009 |
| NREQ-001 | 不修改 Guyue 根控制面或新增万能 Skill | PHASE-04 | EVID-010 |
| NREQ-002 | 不复制参考产品品牌、文字、图片或专有资产 | PHASE-02 | EVID-011 |
| NREQ-003 | 不宣称已构建成熟、可用、稳定产品 | PHASE-04 | EVID-012 |
| NREQ-004 | 不安装、付费、部署、发布、使用凭证或外部写入；未经 ACT-005 精确授权不得 Git 暂存、提交、合并或推送 | PHASE-04 | EVID-013 |

## 循环与预算
- 最大修复轮数：研究与模拟各 1 轮生产、1 轮独立复核；最小活体探针不自动重试
- 单阶段时间上限：PHASE-01 20 分钟；PHASE-02 60 分钟；PHASE-03 75 分钟；PHASE-04 25 分钟；合计 180 分钟
- Token 或上下文预算：最多 3 个并行生产子任务；每项 1 个完整 Agent turn；另加 1 个独立审查 turn；剩余额度为硬上限
- 子任务数量上限：全 Goal 最多 4 个委派任务，同时最多 3 个生产任务
- 工具范围：本地只读、Goal 产物写入、现有检查器/回放、只读联网
- 缺证据熔断：连续两次无新证据、参考无法复核、同模型自评无外部约束或探针无法运行即停止
- 重复运行要求：先核对报告、时间、工作树与运行时；不自动重试外部请求或模型额度

## 委派与收束
- 委派判定：参考候选、固定情境的独立专业分析和只读评审可委派；产品方向、最终集成和裁决由主控持有
- 最大并发子任务：3
- 单任务时间上限：生产任务 30 分钟或一个完整 Agent turn；独立审查 25 分钟或一个完整 Agent turn
- 委派包：每项绑定 Brief、所有权与可改范围、明确不做、基线版本、报告路径和审查包
- 返回状态：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
- 心跳与收束：每个 Agent turn 后检查；连续两次无新证据、重复调查或越界立即停止
- 独立审查：未参与产出的上下文按冻结输入、报告、外部来源和探针证据复核

| 任务 ID | Brief | 所有权与可改范围 | 明确不做 | 基线版本 | 报告路径 | 审查包 | 收束预算 |
|---|---|---|---|---|---|---|---|
| TASK-201 | 收集并比较当前 Agent 工程经验与工单/协作产品参考 | 只写 PHASE-02 参考报告 | 不复制资产、不决定 Guyue 改造 | PHASE-01 基线 | docs/goals/reference-driven-product-engineering/reports/reference-report-201.md | 来源、日期、机制、反证 | 1 轮，最多 6 份材料 |
| TASK-301 | 从产品与体验视角完成固定情境模拟 | 只写 TASK-301 报告 | 不改仓库核心、不读取其他模拟产出 | PHASE-02 冻结输入 | docs/goals/reference-driven-product-engineering/reports/product-simulation-301.md | 目标、参考、必要问题、验收 | 1 个 Agent turn |
| TASK-302 | 从架构与实现视角完成固定情境模拟 | 只写 TASK-302 报告 | 不改仓库核心、不读取其他模拟产出 | PHASE-02 冻结输入 | docs/goals/reference-driven-product-engineering/reports/engineering-simulation-302.md | 架构、权限、任务拓扑、检查器 | 1 个 Agent turn |
| TASK-303 | 独立评审组合模拟并确定唯一活体探针 | 只写 review 报告 | 不修改模拟、不降低标准 | TASK-301/302 输出 | docs/goals/reference-driven-product-engineering/reviews/independent-review-303.md | 固定输入、两份报告、反例清单 | 1 个 Agent turn |
| TASK-404 | 独立复核 PHASE-04 能力裁决和完成边界 | 只写 read-only 复核报告 | 不修改裁决、不请求新工具、不执行外部动作 | PHASE-01 至 PHASE-04 全部 FINAL/ATTEMPT 证据 | docs/goals/reference-driven-product-engineering/reviews/capability-decision-review-404.md | 三路线裁决、证据双向引用、预算账本、否定清单、ACT-004/005 状态 | 1 个 Agent turn，最多 25 分钟 |

## 主线验证门
- 静态检查：控制包和新增报告格式可解析，无未替换模板字段
- 测试：ready 检查器、涉及到的现有路由/行为合同定向测试和唯一活体探针命令退出码
- 构建或导出：不构建完整产品；若探针产生可运行产物，只验证该最小产物
- 安全与隐私：定向扫描本 Goal 新文件与探针输入，不包含凭证、私有数据和外部资产
- 真实运行：最多一个当前 Guyue 活体入口或最小 Agent 回放，不以模拟替代
- 证据新鲜度：报告、探针输出和裁决晚于对应输入；终局证据从授权后的 A 候选基线才可转 FINAL；若未获 ACT-005 提交授权，A/B/C 只作为未提交候选链复算，不得标记 complete

## 最终完成定义
- 正向条件：四个阶段完成；研究、模拟、独立评审和最多一个探针均在预算内；全部承诺有新鲜 FINAL 或明确允许的 ATTEMPT 边界；三路线裁决有反证和下一最小证明；无 ACT-005 时只能停在终局候选
- 否定清单：完整产品完成宣称、品牌资产复制、无界循环、重复委派、同模型自评冒充独立事实、模拟冒充运行、核心 Guyue 未授权改动、安装、部署、提交、发布或外部写入
- 完成边界：仅本 Goal 的投资决策证据与 ACT-004 最小入口修复候选就绪；不得外推为终极愿景、时间型结果、成熟产品能力、跨模型能力或长期用户价值完成
- 独立验收：Long Goal 检查器、未参与模拟的审查上下文、来源复核和探针产物复算
- 人工体验：本 Goal 不评价成品体验；人工只判断模拟是否代表真实产品工程问题、结论是否值得继续投资
- 完成口径：研究完成不等于能力完成；模拟通过不等于产品可用；探针通过不等于完整链路稳定；Goal complete 仅表示投资决策证据就绪

## 风险、授权与停止条件
| 动作 ID | 风险或动作 | 版本或摘要哈希 | 有效期或失效条件 | 是否需要人工授权 | 授权状态 | 授权证据 |
|---|---|---|---|---|---|---|
| ACT-001 | 在本仓库创建控制、模拟、报告与证据文件，运行本地检查和一次 35 分钟内的最小活体探针 | REV-0001 | 样本、预算、依赖、目录或影响面变化即失效 | 是 | APPROVED | DEC-001 |
| ACT-002 | 最多 6 份外部原始材料的有界只读联网研究 | REV-0001 / PHASE-02 | 材料上限、写入行为、登录或付费要求变化即失效 | 是 | APPROVED | DEC-001 |
| ACT-003 | 安装、下载外部代码/资产、使用凭证、付费、部署或外部写入 | 待形成精确清单 | 参数、目标或成本变化即失效 | 是 | PENDING | 待授权 |
| ACT-004 | 修改 Guyue 根 Skill、Manifest、公共合同或运行时控制面 | `product-delivery` 参考驱动入口最小修复 | 任一新增文件、机制或影响面变化即失效 | 是 | APPROVED | DEC-002 |
| ACT-005 | Git 暂存、提交、合并、推送或发布 | 待形成精确 diff 与目标 | diff、分支、远端或目标变化即失效 | 是 | PENDING | 待授权 |

## 恢复协议
1. 读取本总控的范围、阶段路线、最终完成定义和停止条件。
2. 读取执行账本最后一条记录、失败命令、残余风险和下一入口。
3. 对账当前工作树、最近提交、运行时、联网材料数和已用主动时间。
4. 读取当前阶段计划，只从账本记录的下一入口继续。
5. 按重放类别处理；只读研究先查缓存，活体探针不可自动重复，用户交互重新绑定当前问题。
6. 发现输入、报告或代码晚于证据时，先标记过期再判断状态。

## 终局封账顺序
- 实现提交：待生成
- 证据提交：待生成
- 封账定位：待生成

1. A 候选包含控制包、冻结来源元数据、固定模拟夹具、模拟报告、探针产物和非终局工作输出；只有取得 ACT-005 精确授权才可提交为 A，并在 clean 工作树上记录候选对象。
2. B 候选只使用 A 候选中的冻结本地输入和已经捕获的探针产物复算新鲜证据，不重新联网、不重跑模型生产、不扩大预算；必须经过独立验证，且只有 ACT-005 精确授权才可提交 evidence、reports、reviews 及证据索引为 B。
3. C 候选只更新总控与账本为完成，以 `derived@master+ledger` 定位；只有 ACT-005 精确授权才可提交 C，并由账本记录封账状态。
4. 未获提交授权时保持未提交终局候选，不得标记 complete。
