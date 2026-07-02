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
   - 必跑 `python scripts/doctor.py`。缺失依赖则停止并求助用户。
2. **Context Load**:
   - 检索 `.guyue_memory/active/`。
   - 若记忆臃肿，提示用户运行 `python scripts/memory_gc.py` 归档。
3. **Dispatch**:
   - 查阅 `skills_manifest.json` 匹配意图 (如 `system-design`, `debugging-mindset`)，按对应子技能行事。
   - **[新增] 泛生态受控调度 (Controlled Ecosystem Invocation)**: 对于记录在 `.guyue_memory/local_skills_index.json` 或 `skills_manifest.json` 中的外部技能，只能视作“可发现的候选能力”。一旦用户意图匹配，先读取其公开说明和本地 `SKILL.md`（如存在）掌握边界，再按 `security-gate` 做安全预检；涉及 CLI、网络请求、安装、写入或下载时，必须展示将执行的动作并等待用户明确授权。
   - **生态安检 (Security Gate)**: 若涉及第三方技能包的执行、收纳或代码读取，必须首先调用 `skills/security-gate`。目标必须由用户明确提供为路径、URL、包名或压缩包路径；目标不明确时先询问，禁止自动挑选本机随机技能目录。目标明确后再运行 `python3 scripts/run_security_scan.py` 进行本地启发式预检；预检不是完整供应链审计，见红旗即拦截，见黄旗则等待人工确认。
   - **生态寻猎拦截 (Ecosystem Routing)**: 若用户提供未知 GitHub/工具链接，或提出模糊的技能需求（如“推荐个做图表的工具”、“收纳 xxx”），必须路由至 `ecosystem-scout` 进行联网调研、防臃肿评估与轻量化依赖注册。
