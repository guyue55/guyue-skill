---
name: guyue/memory-bank
description: |
  记忆挂载模块。作为古月的数字分身，记录解决过的疑难杂症、系统性教训和架构决策。
  触发词：/guyue-remember (记录教训), /guyue-recall (检索历史经验)
---

# guyue / memory-bank

> 这是 `guyue` 的领域专属子技能：**自主记忆沉淀与检索**。
> 真正的数字孪生必须拥有“昨日之痛，今日之师”的闭环能力。

## 适用场景 (When to Use)

- 当你在排查完一个复杂的 Bug（如罕见的依赖冲突、框架暗坑）后。
- 当用户要求：“把我们今天踩的坑记下来”。
- 当开启一个新任务，你需要检查过去是否遇到过类似问题时。

## 绝对反模式 (Anti-Patterns to Avoid)
- ❌ 检索失败时，向用户强行编造一个不存在的历史记录。
- ❌ 在记忆文件中原封不动地贴出包含敏感 API Key 和真实服务器路径的日志。

## Step-by-Step Execution (执行工作流)
如果接收到记录记忆的指令，请遵循以下流程：

1. **寻址/创建存储区**：
   在当前项目的根目录下寻找 `.guyue_memory/` 文件夹。如果没有，立即创建它。
2. **结构化提取与双轨写入**：
   - **Markdown 详情**：将教训提取为标准的 Markdown 文件（如 `.guyue_memory/202606_react_hydration_error.md`）。
   - **JSON 元数据索引 (核心)**：必须同时解析并更新 `.guyue_memory/index.json`。如果文件不存在则新建一个包含 `{"memories": []}` 的文件。向数组中 push 新对象，必须包含字段：`filename`, `tags` (关键词数组), `summary` (一句话核心根因), `timestamp`。
3. **Markdown 详情内容必须包含**：
   - **症状 (Symptom)**：表面上报了什么错？
   - **根因 (Root Cause)**：最终发现到底是什么导致的？
   - **解法 (Solution)**：怎么修复的？（附带代码片段或命令）
   - **防范 (Prevention)**：未来遇到类似场景，如何前置规避？

## 记忆检索协议 (`/guyue-recall`)

作为 `guyue` 体系的子技能，每次主路由接管复杂请求前，**应当优先唤醒此技能进行历史查阅**：

1. 检查当前目录下是否存在 `.guyue_memory/index.json`。
2. 如果存在，**禁止暴力遍历整个文件夹**。必须优先读取 `index.json`，根据任务上下文（例如当前遇到 React 错误，则在 `index.json` 的 `tags` 或 `summary` 字段中查找匹配项）。
3. 定位到高相关性的 `filename` 后，再精准读取对应的 Markdown 文件全文。
4. 如果命中历史教训，必须在给用户的最终答复前，强制声明：
   > [!IMPORTANT]
   > **古月历史记忆加载：**
   > 检测到我们在历史档案 `xxx.md` 中曾处理过类似问题。核心规避点是...

## 诚实边界 (Guardrails) 与绝对纪律

1. **脱敏**：记录的记忆中，严禁包含服务器真实 IP、API Key、真实的绝对路径（如 `/Users/apple/...`）。必须做泛化处理。
2. **静默失败防御**：不要假设记忆库永远有用，如果检索不到，不要强行编造历史，立刻退回 `research-and-sourcing` 流程。

## 强制纪律 (Trace Discipline)
执行本技能检索或写入记忆时，必须在对话中明文输出诊断与执行轨迹：
`[Trace: Guyue/MemoryBank] 触发数字孪生记忆库，检索 .guyue_memory...`


## Cross-Skill Invocation (流转边界)
在执行过程中，如果超越了本视角的处理范围，请主动流转：
- 记忆中发现重大漏洞 -> 转交 `system-design` 或 `debugging-mindset`

## 展台 Showcase

**场景：用户问“我们上次那个 React Hydration Error 是怎么解决的？”**

*Guyue Memory Bank 回答：*
`[Trace: Guyue/MemoryBank] 触发数字孪生记忆库，检索 .guyue_memory...`
> [!IMPORTANT]
> **古月历史记忆加载：**
> 检测到我们在历史档案 `202606_react_hydration_error.md` 中曾处理过类似问题。
> 
> **核心规避点是**：不要在 SSR 阶段直接渲染依赖 `window` 对象的组件。
> **解法**：我们当时封装了一个 `ClientOnly` 组件，在 `useEffect` 后才挂载 children。需要我为您提供当时的代码骨架吗？
