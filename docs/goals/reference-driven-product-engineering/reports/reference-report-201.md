# TASK-201 参考研究报告

- Goal ID：GOAL-REFERENCE-DRIVEN-PRODUCT-ENGINEERING
- 阶段：PHASE-02
- 生成时间：2026-07-30T18:35:00+08:00
- 材料数量：6
- 结论：DONE

## 材料清单

| ID | 来源 | 类型 | 访问日 | 本 Goal 用途 |
|---|---|---|---|---|
| M1 | https://github.com/mshumer/Claude-of-Duty/blob/main/prompt.md | 原始 prompt 仓库 | 2026-07-30 | 提取挑战循环的组织机制与夸张边界 |
| M2 | https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more | Anthropic 官方博客 | 2026-07-30 | 判断 Skills、subagents、hooks、规则的适用层级和上下文成本 |
| M3 | https://code.claude.com/docs/en/sub-agents | Claude Code 官方文档 | 2026-07-30 | 判断 subagents 的隔离、权限、模型和并行边界 |
| M4 | https://linear.app/docs/configuring-workflows | Linear 官方文档 | 2026-07-30 | 建立工单/Issue 状态流参考 |
| M5 | https://www.atlassian.com/software/jira/service-management/product-guide/getting-started/service-request-management 与 https://support.atlassian.com/jira-cloud-administration/docs/add-statuses-to-a-jira-workflow/ | Atlassian 官方文档 | 2026-07-30 | 建立服务请求、门户、表单字段、工作流权限与状态配置参考 |
| M6 | https://www.intercom.com/help/en/articles/9730130-how-ticket-states-work 与 https://support.zendesk.com/hc/en-us/articles/8263915942938-About-the-ticket-lifecycle-and-ticket-statuses | Intercom/Zendesk 官方帮助 | 2026-07-30 | 建立客户可见状态、内部等待、重开、关闭和 SLA 参考 |

## 对挑战循环的真实判断

挑战循环的有效部分不是“夸大目标就会自动做出 AAA 产品”，而是四个工程机制：

1. 主控把模糊愿景拆成可交付切片。
2. 专业 Agent 分开处理相对独立的子问题，降低主上下文污染。
3. 独立评审使用外部参照和明确标准，不允许只凭自我满意停止。
4. 循环必须有成本、权限、证据和停止条件，否则会变成昂贵的无界返工。

M1 的 prompt 故意使用极限目标和“不要停止”等措辞。本 Goal 不能照搬这部分，因为古月的目标是成熟产品工程能力验证，不是用夸张话术诱导模型无限消耗。

## Agent 编排经验

M2 把 CLAUDE.md、Rules、Skills、Subagents、Hooks 等方法按加载时机、压缩行为、上下文成本和适用场景区分。对古月的启发是：长期稳定规则不应塞进单个万能 prompt；过程型能力应进入 Skill；并行或隔离侧任务适合 subagents；确定性自动检查适合脚本或 hook。

M3 说明 subagents 有自己的上下文、工具和权限边界，适合隔离深搜、日志分析、依赖审计等侧任务。它同时给出限制：subagent 结果回主线程的是摘要，运行多个 subagents 会消耗上下文，权限模式需要显式控制。对古月的启发是：多 Agent 不能替代主控集成，也不能让评委与生产者共享同一标准漂移。

## 工单产品参考矩阵

| 机制 | Linear | Jira Service Management / Jira | Intercom / Zendesk | 固定产品契约 |
|---|---|---|---|---|
| 状态流 | 团队级 Issue 状态，默认 Backlog、Todo、In Progress、Done、Canceled | 工作流由状态、转换、权限和审批构成；服务请求覆盖请求入口到履约全生命周期 | 提交、处理中、等待客户、已解决；Zendesk 还区分 New/Open/Pending/On-hold/Solved/Closed 和重开/跟进 | 首版状态：新建、待分派、处理中、等待客户、内部等待、已解决、已关闭；允许重开 |
| 创建入口 | Issue 创建与模板 | 门户、邮件请求、请求类型和表单字段 | Messenger/Inbox/Customer ticket/Back-office ticket | 首版支持内部创建；将外部门户、邮件和 IM 接入作为后续扩展 |
| 权限 | 团队归属与 Issue 操作 | 管理员权限影响 workflow/status 配置；不同空间/项目有权限边界 | 客户可见状态与内部状态区分 | 后端必须控制角色权限；前端只做体现。角色：管理员、主管、处理人、观察者、客户 |
| 优先级/SLA | 视图与排序可支撑团队执行 | 请求管理强调统一入口和履约；JSM 可按团队配置服务流程 | SLA/优先级用于排序和响应承诺 | 首版实现优先级、到期时间、SLA 风险标识和列表排序；不实现复杂 SLA 引擎 |
| 协作 | 评论、分派、关系 | 表单、审批、转换规则和通知 | 客户沟通、内部等待、自动化和重开 | 首版实现公开评论、内部备注、负责人、关注人、审计事件 |
| 复杂度控制 | 团队可配置但默认流程简单 | 工作流可复杂配置，但变更影响范围大 | 客户可见状态强调清晰预期 | 首版固定配置优先；自定义状态和自动化作为后续版本 |

## 必要问题与默认假设

本 Goal 不再向用户追问，原因是用户已批准用中等复杂度 B2B 工单样本模拟。为保持可执行，采用以下默认：

- 客户规模：20-200 人的 B2B 服务或运营团队。
- 使用场景：内部团队处理客户请求，不做公开 SaaS 多租户商业化。
- 首版重点：稳定工单生命周期、协作、权限、筛选和验收，不做 AI 自动回复或复杂自动化。
- 技术风险重点：权限边界、状态机一致性、列表筛选真实查询、审计记录、失败/重开流程。

## 反抄袭边界

- 允许学习：状态类别、列表/详情/评论/权限/SLA 的通用产品结构；Agent 编排的隔离、权限和评审机制。
- 禁止复制：品牌名称、图标、配色、页面布局细节、宣传语、截图、专有素材、非公开行为、外部产品代码。
- 模拟产物必须使用通用业务命名，例如“工单”“客户”“处理人”“SLA 风险”，不使用 Linear/Jira/Intercom/Zendesk 的品牌表达作为产品身份。

## PHASE-02 结论

参考研究支持进入 PHASE-03。固定产品不是“照着某一个产品抄”，而是抽取 B2B 工单协作的共同机制，并用 Agent 工程材料约束古月的多智能体工作方式。
