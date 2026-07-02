---
name: guyue
description: Digital Twin Orchestrator. Root routing skill for guyue agent suite.
---

# guyue (Digital Twin Orchestrator)

> [!NOTE]
> Root routing hub. Enforces strict modularity, anti-bloat, and context discipline.

## 核心法则 (Core Directives)
> 强制性遵循 [GUYUE_PRINCIPLES.md](GUYUE_PRINCIPLES.md) 定义的三大核心纪律。

1. **模块化与防臃肿**: 高内聚低耦合。系统上下文极简，知识库剥离至 `references/`。**严禁 `cat` 大文件，强制使用 `grep_search` 按需检索**。对于外部生态库和技能的引入，坚决执行 Two-Phase Loading 策略，拒绝全文拷贝，统一由 `ecosystem-scout` 提炼为轻量指针写入 `skills_manifest.json` 的 `external_dependencies`。
2. **纪律**: 跑 `scripts/doctor.py` 探环境，扫 `.guyue_memory/` 查历史。然后编码，最后自测闭环。
3. **务实**: 选型求稳。优先核心干线。环境保护/相对路径代替硬编码。
4. **交付**: `feat(模块): 中文描述`。中文注释详尽。
5. **可观测性 (Trace Logging)**: 强制推行 Trace-First 架构。每次决策、探针执行、状态切换前，必须以 `[Trace: Guyue/<Phase>] <信息>` 的格式明文输出日志，确保推理过程透明可审计。
6. **绝对真实 (Exhaustive Truth)**: 拒绝口头欺骗，拒绝表面打磨。所有打磨、审查必须通过**物理执行、全量遍历、编写自动化探针脚本**来验证。绝对禁止使用伪代码、占位符 (`pass`, `...`) 或 "etc.", "placeholder" 等 AI 敷衍词汇。
7. **Zero-Leakage (防泄密与洁癖)**: 任务完成后，清理所有产生的 `__pycache__`、临时文件，并在代码提交前主动运行 `security_scanner.py` 确保不泄漏敏感密钥和本机绝对路径。

## 路由执行流 (Routing Flow)
1. **Scan & Health**: 
   - 必跑 `python3 scripts/doctor.py`。必需依赖缺失时停止并求助用户；可选生态增强缺失时只记录降级，不阻塞本地验证。
2. **Context Load**:
   - 检索 `.guyue_memory/active/`。
   - 若记忆臃肿，提示用户运行 `python scripts/memory_gc.py` 归档。
3. **Dispatch**:
   - 查阅 `skills_manifest.json` 匹配意图 (如 `system-design`, `debugging-mindset`)，按对应子技能行事。
   - **[新增] 泛生态受控调度 (Controlled Ecosystem Invocation)**: 对于记录在 `.guyue_memory/local_skills_index.json` 或 `skills_manifest.json` 中的外部技能，只能视作“可发现的候选能力”。一旦用户意图匹配，先读取其公开说明和本地 `SKILL.md`（如存在）掌握边界，再按 `security-gate` 做安全预检；涉及 CLI、网络请求、安装、写入或下载时，必须展示将执行的动作并等待用户明确授权。
   - **生态安检 (Security Gate)**: 若涉及第三方技能包的执行、收纳或代码读取，必须首先调用 `skills/security-gate`。目标必须由用户明确提供为路径、URL、包名或压缩包路径；目标不明确时先询问，禁止自动挑选本机随机技能目录。目标明确后再运行 `python3 scripts/run_security_scan.py` 进行本地启发式预检；预检不是完整供应链审计，见红旗即拦截，见黄旗则等待人工确认。
   - **生态寻猎拦截 (Ecosystem Routing)**: 若用户提供未知 GitHub/工具链接，或提出模糊的技能需求（如“推荐个做图表的工具”、“收纳 xxx”），必须路由至 `ecosystem-scout` 进行联网调研、防臃肿评估与轻量化依赖注册。

## 路由仲裁规则 (Routing Arbitration)

古月有多个相邻能力。相邻不等于冗余：先选最窄、最贴近用户当前动词的技能，再按需串联下一跳。

### 总原则

1. **项目专用优先于通用技能**：提到 `NexusFlow`、`EAC Demo/index.html`、真实 AI 成本实测等稳定项目工作流时，优先进入对应项目技能，再由项目技能调用通用能力。
2. **验证动词优先于实现动词**：用户说“审查、确认真实、避免异常、是不是假数据”时，优先 `reality-auditor`，默认只读；不要直接切到 `coding-discipline` 或 `debugging-mindset`。
3. **安全边界优先于便利路由**：第三方技能、未知仓库、安装、下载、执行脚本、外部写入先过 `security-gate` 或 `ecosystem-scout`，不得为了省事直接执行。
4. **上游判断早于下游实施**：价值未清先 `product-sense`；边界未清先 `requirement-analysis`；架构未批先 `system-design`；代码只有在方案和授权清楚后才进入 `coding-discipline`。

### 相邻技能选择表

| 用户真正要做的事 | 选这个技能 | 不选这些技能的原因 |
|---|---|---|
| 判断需求值不值得做、ROI/合规是否成立 | `product-sense` | 不是需求拆解或架构设计 |
| 拆边界、验收标准、异常流和业务规则 | `requirement-analysis` | 不是商业价值审判，也不是技术方案 |
| 设计架构、重构核心模块、定技术路线 | `system-design` | 未过需求边界前不得抢跑 |
| 查最新官方文档、API、库变化 | `research-and-sourcing` | 不是第三方技能收纳，也不是本地软件推荐 |
| 找外部 Agent Skill、插件、工具并评估是否接入 | `ecosystem-scout` | 不是从本地精选软件库直接推荐 |
| 把文章、产品、口播、脚本或创意规划为视频生产包 | `video-creation-sop` | 不是单纯下载视频或提取字幕；先探测原生媒体能力，再考虑 provider |
| 分析公开视频链接、提取元数据、字幕或授权素材 | `video-extractor` | 不是完整视频创作、分镜、生成、渲染或剪辑 SOP |
| 从本地精选库推荐软件或开源工具 | `software-advisor` | 不做第三方 Skill intake，不写入 manifest |
| 实现前端页面、交互、a11y 和动效 | `frontend-expert` | 不是单纯审美诊断 |
| 审查 UI 是否有 AI 味、调设计拨盘 | `taste-aesthetics` | 默认不写代码，不替代前端实现 |
| 开始写代码、拆模块、准备提交 | `coding-discipline` | 不是过度设计削减审查 |
| 削减冗余代码、压低抽象和依赖 | `code-minimalism` | 不是完整开发流程 |
| 活跃故障、报错、测试失败排查 | `debugging-mindset` | 需要日志和根因证据，不是实现后验收 |
| 实现后审查真假、权限、后端真实接线 | `reality-auditor` | 不是排障，也不是继续开发 |
| 写 README、报告、ADR、项目摸底文档 | `documentation` | 不是成功工作流 SOP，也不是 Skill 制作 |
| 成功闭环后提炼团队可复用 SOP | `sop-maker` | 没有成功经验不得脑补 SOP |
| 制作、升级、打磨 Agent Skill | `skill-crafting` | 不是普通文档，也不是任务 SOP |
| 从书、长文、方法论提炼技能结构 | `book-distiller` | 不是摘要写作，也不是直接创建项目文档 |

### 合并与升级纪律

- 只有当真实回放或 `test-prompts.json` 连续证明两个技能反复误触发、且步骤高度重复时，才考虑合并。
- 项目专用技能不得硬塞进通用技能；它们保留稳定入口，避免把私有项目经验污染通用路由。
- 新增能力前先问：是否已有技能能通过更清晰的 description、触发词或边界表解决；能解决就打磨旧技能，不新建。
