# 2026 Q2 Agent Skill、插件与提示词生态逐仓研究账本

## 研究边界

- 冻结时间：2026-07-10 15:59:10Z。
- 时间窗：最近三个月内仍活跃，或在最近八周安装榜、主流运行时官方生态中持续可见的项目。
- 纳入条件：与 Skill 规范、插件分发、提示词工程、上下文、记忆、长任务、编码 Agent、安全或评测直接相关；来源可定位；机制能被本仓库验证。
- “全部”的口径：不是声称穷尽整个互联网，而是完整下载并逐仓阅读所有通过上述筛选条件的 52 个项目。每仓至少检查根说明、项目状态和与本轮问题直接相关的规范、Skill、评测或工作流文件。
- 下载方式：浅克隆、部分对象、固定 HEAD 到临时目录 `/tmp/guyue-ecosystem-2026-07-10`。全部 52 仓成功，0 失败；没有安装依赖、执行第三方脚本或把源码复制进古月。
- 热度只用于发现，不等于质量。Skills.sh 的八周趋势和匿名聚合安装量不能代替源码、维护状态、许可与实测审查。

## 总结

跨项目真正重复的机制只有八组：渐进披露、正负路由、无 Skill 基线与留出回放、持久任务包、稳定 ID、委派所有权与独立审查、停滞/预算收束、证据绑定当前产物。古月已用现有 26 个 Skill、轻量 Python 检查器和 Markdown 控制包吸收这些机制，没有新增第 27 个业务 Skill，也没有引入 Agent 框架、数据库或外部观测服务。

本轮明确拒绝三类诱惑：用热门榜替代质量判断、复制泄露或来历不清的系统提示词、为了“自治”引入无法证明收益的多 Agent 运行时。项目标为“借鉴”的，只吸收可验证机制；标为“拒绝依赖”的，不代表项目差，而是当前仓库的收益不足以覆盖生命周期成本。

## 逐仓账本

| 项目与冻结提交 | 读取重点 | 对古月的决定 |
|---|---|---|
| [Aider](https://github.com/Aider-AI/aider) `5dc9490bb35f9729ef2c95d00a19ccd30c26339c` | Git 感知编辑、检查与提交循环 | 借鉴小步验证；拒绝运行时依赖 |
| [Ponytail](https://github.com/DietrichGebert/ponytail) `14a0d79548d4de8fc2de95c1b94bb0de63a739d3` | 简单优先、纠正膨胀基线 | 已吸收到 `code-minimalism`；安全、验证、可访问性不随简化删除 |
| [Caveman](https://github.com/JuliusBrussee/caveman) `0d95a81d35a9f2d123a5e9430d1cfc43d55f1bb0` | 最少抽象与直接实现 | 借鉴反过度设计；不把“简单”绝对化 |
| [SkillSpector](https://github.com/NVIDIA/SkillSpector) `c2d09df019e358d3dc12d980b82c798b87cb9f56` | Skill 静态分析、安全与质量信号 | 保留为精确提交的可选审查源；本地主门禁不依赖它 |
| [OpenHands](https://github.com/OpenHands/OpenHands) `73b72a223d0325ab049af2b6a37b1adc13006d79` | 事件流、工作区与执行隔离 | 借鉴状态与边界；拒绝引入平台依赖 |
| [planning-with-files](https://github.com/OthmanAdi/planning-with-files) `bdef0e0aa0c5dcd385e7387d19b755b567dd6d98` | 磁盘计划、恢复、完成门 | 吸收到 Long Goal 账本；拒绝全局 Hook 注入 |
| [Claude Code system prompt history](https://github.com/Piebald-AI/claude-code-system-prompts) `4778f4cc99afa1b172c0ba1eecba461156ff1591` | 版本差异、压缩摘要保留错误与承诺 | 仅作行为观察；不复制系统提示词 |
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) `1132b3e80a45487ce8423f75d0e180874bf84caa` | Agent/环境接口与轨迹 | 借鉴轨迹证据；项目状态变化使其不适合作为新依赖 |
| [Addy Osmani agent-skills](https://github.com/addyosmani/agent-skills) `6bcfeb9dae52b11eaad23511acc165109746dbc3` | 结构、确定性路由碰撞、行为轨迹三层评测 | 已落地 16 条正负路由契约与解释器 |
| [Everything Claude Code](https://github.com/affaan-m/ECC) `40927950c49f6e742d341e20ff7b9b7e1e7bfff5` | 大型 Agent/Hook/Skill 套件 | 用作臃肿对照；不复制全套编排 |
| [Agent Skills specification](https://github.com/agentskills/agentskills) `38a2ff82958afee88dadf4831509e6f7e9d8ef4e` | 发现、激活、执行的渐进披露 | 继续作为公共兼容基线 |
| [Claude Code](https://github.com/anthropics/claude-code) `15a21e1b4e240e2da6a4953d5f148a806c9c9bb2` | 运行时能力、插件与子 Agent 表面 | 只按官方可验证能力适配，不臆测加载行为 |
| [Anthropic prompt tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial) `0d277542e927652da25b0014c9b346723af55881` | 示例驱动的提示词迭代 | 借鉴最小案例；不增加教程型 Skill |
| [Anthropic Skills](https://github.com/anthropics/skills) `9d2f1ae187231d8199c64b5b762e1bdf2244733d` | skill-creator、真实用例、无 Skill 基线、盲评 | 吸收到 `skill-crafting` 与评测文档 |
| [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) `49069b8b5276afd21402bc3b978b69ad78a7d2ef` | 新装、升级、旧文件清理与运行时验真 | 吸收到安装收据和发布检查；拒绝角色海洋 |
| [DeepEval](https://github.com/confident-ai/deepeval) `c917669c728fb1101d8d9ad6ae711a94202f94f7` | Trace、工具正确性与断言评测 | 借鉴断言模型；当前不引入依赖 |
| [Marketing Skills](https://github.com/coreyhaines31/marketingskills) `f04556d923e076a29564559101e5ca33698422f5` | 窄领域 Skill 与可行动输出 | 借鉴窄职责；不扩营销能力目录 |
| [Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) `57673726396dd94acb23bdb1e67f27c78ee85a8e` | 提示模式与研究索引 | 作为参考材料，不当运行时规则 |
| [prompts.chat](https://github.com/f/prompts.chat) `01a18249fff1645f38f1e116acd50819f67d88d8` | 大规模提示词目录 | 用作“数量不等于质量”的反例；不复制条目 |
| [gstack](https://github.com/garrytan/gstack) `7c9df1c568a9ea745508f679a329332b2c338063` | 角色化开发工作流与交接 | 借鉴任务交接；不引入整套角色运行时 |
| [Beads](https://github.com/gastownhall/beads) `812ad6df0a15566ee88bda8d0b22159a5dcfbddf` | 稳定任务 ID、依赖与 supersedes | 稳定 ID 已吸收；当前不值得增加数据库 |
| [Awesome Copilot](https://github.com/github/awesome-copilot) `30472ecf0fe34cc561df958c08501ecc5ca80ea4` | 多运行时指令、Agent、Prompt 资产 | 强化薄适配器原则；不复制供应商规则 |
| [Google Skills](https://github.com/google/skills) `250f8746974f829d984e5dd3f28a78acd28ac8bc` | 官方领域 Skill 的入口与资源组织 | 借鉴一手来源优先；不新增无用户路径的适配 |
| [HashiCorp Agent Skills](https://github.com/hashicorp/agent-skills) `957d5f95911bc22eaf2b7e141c3b08ba824091fe` | 供应商官方领域知识 | 强化官方源优先和版本边界 |
| [LangGraph](https://github.com/langchain-ai/langgraph) `95af6a00718588e7b7ce17310e8006d267896a77` | checkpoint、恢复与人工中断 | 语义吸收到 Long Goal；拒绝框架依赖 |
| [Langfuse](https://github.com/langfuse/langfuse) `7a3fa899c5b06217898d5bbc4bd0a5b7734b456c` | 观测、Trace、评测数据 | 借鉴证据字段；不引入外部服务 |
| [Letta](https://github.com/letta-ai/letta) `b76da9092518cbaa2d09042e52fdcbde69243e18` | 记忆块、作用域和生命周期 | 吸收到 memory schema v2；拒绝服务依赖 |
| [Matt Pocock skills](https://github.com/mattpocock/skills) `391a2701dd948f94f56a39f7533f8eea9a859c87` | 一个失败模式对应一个窄动词、用文档追问 | 强化窄路由与项目语言；不新增影子 Skill |
| [Skillgrade](https://github.com/mgechev/skillgrade) `cc06c6d87d1157283d212dc9d818d50eacf01393` | Skill 分级与可重复评测 | 吸收留出样本与失败注入；不采用单一总分 |
| [Skills best practices](https://github.com/mgechev/skills-best-practices) `675ee84307993f6df3516437dcd4703c3c32fab4` | Skill 编写与结构纪律 | 与公开规范交叉验证，避免私有格式漂移 |
| [SkillOpt](https://github.com/microsoft/SkillOpt) `e4ea6a6771e797ef820cdd8bfea64c57e0481065` | 会话采集、离线回放、限幅编辑、留出门禁 | 形成默认关闭的会话学习闭环；不自动改写生产 Skill |
| [AutoGen](https://github.com/microsoft/autogen) `027ecf0a379bcc1d09956d46d12d44a3ad9cee14` | 多 Agent 对话与编排 | 只借鉴边界；维护状态和复杂度不适合当前引入 |
| [Azure Skills](https://github.com/microsoft/azure-skills) `2026849a26893ea3e2d2c085f6c314a6746b190e` | 官方云领域 Skill 集 | 作为官方领域技能样本；不扩展当前产品范围 |
| [context-mode](https://github.com/mksglu/context-mode) `a6a990f0727c86ec126b6347123e3887dfa1d256` | 数据缩减与表达风格分离 | 吸收到上下文预算；不以“短”牺牲推理与证据 |
| [Agent Skills for Context Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) `c2b9a19107d263f965def4e8f7d1cd0d0fee1a59` | 上下文分类、压缩与交接 | 交叉验证现有 `context-compressor`；不复制目录 |
| [Superpowers](https://github.com/obra/superpowers) `d884ae04edebef577e82ff7c4e143debd0bbec99` | brief/report/review 包、BASE..HEAD、规格与质量双审 | 已吸收到 Long Goal v3 委派契约 |
| [Codex](https://github.com/openai/codex) `2b9c05046038c038ec6bddb9db7d11394995372d` | 官方运行时、会话与执行边界 | 用真实 JSONL 结构实现脱敏提取；不绑定未承诺内部接口 |
| [OpenAI Evals](https://github.com/openai/evals) `8eac7a7de5215c907fbddc30efdaf316913eccdd` | 数据集、样本和评测分离 | 借鉴结构/行为/活体三层证据 |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) `0354f482a8e76d33c50a6a3e462c814eefde1e6b` | Trace 与人工审批 | 吸收可观察动作和版本化授权；不公开隐藏推理 |
| [OpenAI plugins](https://github.com/openai/plugins) `bd2122cb92f2ade874d8c2b1d00383976ab9415b` | 插件包、Skill 与连接器分层 | 强化“发现、安装、激活、运行”分开验真 |
| [Symphony](https://github.com/openai/symphony) `4cbe3a9699a73b862466c0b157ceca0c1985d6d7` | issue/run/session ID、隔离工作区、重试与停滞上限 | 已吸收到委派返回状态、心跳和收束预算 |
| [Impeccable](https://github.com/pbakaus/impeccable) `da99645a58400ed7acb201e6904f9413efd89c6e` | 一个根 Skill、窄命令、确定性审美检测 | 强化根路由 + 窄能力，不再造前端 mega-skill |
| [Promptfoo](https://github.com/promptfoo/promptfoo) `a3114835a073fe14427d648fe11be094aae06fbe` | 提示词回归、断言与多模型比较 | 借鉴契约回归；当前不引入 Node 评测依赖 |
| [Remotion Skills](https://github.com/remotion-dev/skills) `6726bf2d4bcce0359806749b3656b0c886d74aaa` | 窄领域官方 Skill | 证明领域 Skill 应保留边界；不泛化成视频万能技能 |
| [Supabase Agent Skills](https://github.com/supabase/agent-skills) `1ad9aaeb49caafd9e95c0a91116f71890eebbc53` | 官方产品知识与工作流 | 强化版本敏感问题走官方一手来源 |
| [Tech Leads Club agent-skills](https://github.com/tech-leads-club/agent-skills) `6663279cd659b60cecb3e8d2dcc13162c88a8b7a` | 工程角色能力包 | 用作能力覆盖对照；拒绝以角色数量膨胀目录 |
| [Temporal Python SDK](https://github.com/temporalio/sdk-python) `4ec9ab05b41a14cf8bf37a83f09fbfeb59628f7a` | 可重放、补偿和持久工作流 | 重放分类已吸收；不引入工作流服务 |
| [claude-mem](https://github.com/thedotmack/claude-mem) `312d640b0188753acd92a1a82d95a84d5c7c43db` | 会话采集与长期记忆 | 借鉴离线提炼；因隐私和自动注入风险拒绝依赖 |
| [Cognee](https://github.com/topoteretes/cognee) `5b32da7c08237e7274342114a72d82667d97c1f4` | 图式记忆与检索 | 当前两层索引足够；拒绝知识图谱依赖 |
| [Vercel Skills](https://github.com/vercel-labs/skills) `4ce6d48ac44c8b637db87b2102fea3baca719df1` | 高安装量 Skill 的发布与发现 | 借鉴可发现性；安装量不作为质量门 |
| [wshobson/agents](https://github.com/wshobson/agents) `d7cf7dca8c4c7d0635e284f77204daa85552bfa4` | 大型 Agent/Plugin/Skill 目录 | 用作路由碰撞和上下文膨胀压力样本；不整包接入 |
| [System prompts and models](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools) `570364ce8146b24061a7e9ac43d3dc30c7e0f6a4` | 系统提示词归档 | 仅观察共性；因来源、许可和版本真实性不复制 |

## 已落地映射

| 生态共识 | 古月落点 | 验证方式 |
|---|---|---|
| 渐进披露与上下文预算 | `src/context_budget.py`、`scripts/check_context_budget.py` | 发现面、根入口、单 Skill 体积与路由碰撞门禁 |
| 正负路由与项目上下文门 | `src/skill_router.py`、`scripts/explain_route.py`、MCP `guyue_explain_route` | 16 条行为契约；通用请求不得误触项目 Skill |
| 结构、路由、行为分层评测 | `scripts/run_eval.py`、`scripts/check_behavior_replay.py` | 确定性路由与证据哈希分开报告 |
| 会话学习 | `scripts/codex_extractor.py` | 时间窗、主/子任务、项目、角色、去重、脱敏与清单测试 |
| 持久任务包与委派收束 | Long Goal v3 | 缺委派契约故障注入 |
| 当前产物证据 | Long Goal v3 evidence index | 旧证据和 SHA-256 篡改故障注入 |
| 默认关闭的离线优化 | 本研究账本 + 人工选择 | 不自动写回生产 Skill，不执行第三方代码 |
| Anti-Bloat | 仍为 26 个 Skill，0 个新框架依赖 | context budget、完整主门禁和发布清单 |

## 局限

这是一轮截至冻结时间的源码研究，不是对 52 个项目的完整安全审计、许可证意见或性能基准。临时克隆的 HEAD 会随上游变化而过期；任何未来接入必须重新核对 origin、精确提交、许可、安装脚本和运行权限。提示词归档类项目尤其只能作为观察材料，不能当作官方事实或可直接再分发的资产。
