---
name: guyue
description: Digital Twin Orchestrator. Root routing skill for guyue agent suite.
---

# guyue (Digital Twin Orchestrator)

> [!NOTE]
> Root routing hub. Enforces strict modularity, anti-bloat, and context discipline.

## 核心法则 (Core Directives)
> 强制性遵循 [GUYUE_PRINCIPLES.md](GUYUE_PRINCIPLES.md) 定义的三大核心纪律。

1. **模块化与防臃肿**: 高内聚低耦合。系统上下文极简，知识库剥离至 `references/`。**严禁 `cat` 大文件，强制使用 `grep_search` 按需检索**。
2. **纪律**: 跑 `scripts/doctor.py` 探环境，扫 `.guyue_memory/` 查历史。然后编码，最后自测闭环。
3. **务实**: 选型求稳。优先核心干线。环境保护/相对路径代替硬编码。
4. **交付**: `feat(模块): 中文描述`。中文注释详尽。
5. **可观测性 (Trace Logging)**: 强制推行 Trace-First 架构。每次决策、探针执行、状态切换前，必须以 `[Trace: Guyue/<Phase>] <信息>` 的格式明文输出日志，确保推理过程透明可审计。

## 路由执行流 (Routing Flow)
1. **Scan & Health**: 
   - 必跑 `python scripts/doctor.py`。缺失依赖则停止并求助用户。
2. **Context Load**:
   - 检索 `.guyue_memory/active/`。
   - 若记忆臃肿，提示用户运行 `python scripts/memory_gc.py` 归档。
3. **Dispatch**:
   - 查阅 `skills_manifest.json` 匹配意图 (如 `system-design`, `debugging-mindset`)，按对应子技能行事。
4. **Verify**:
   - 遵循 `superpowers` 验证交付。
