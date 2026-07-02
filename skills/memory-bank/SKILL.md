---
name: memory-bank
description: Digital twin memory system for documenting and recalling architectural decisions and bug fixes.
trigger_includes:
  - "记录教训"
  - "检索历史"
  - "记住这个坑"
  - "上次怎么修的"
  - "/guyue-remember"
  - "/guyue-recall"
---

# guyue / memory-bank

> 这是 `guyue` 的领域专属子技能：**自主记忆沉淀与检索**。
> 真正的数字孪生必须拥有“昨日之痛，今日之师”的闭环能力。

## When to Use (何时使用)

- 当你在排查完一个复杂的 Bug（如罕见的依赖冲突、框架暗坑）后。
- 当用户要求：“把我们今天踩的坑记下来”。
- 当开启一个新任务，你需要检查过去是否遇到过类似问题时。

## Anti-Patterns (防相控反模式)
- ❌ 检索失败时，向用户强行编造一个不存在的历史记录。
- ❌ 在记忆文件中原封不动地贴出包含敏感 API Key 和真实服务器路径的日志。

## Step-by-Step Execution (标准执行工作流)
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
   > 检测到我们在历史档案 `特定项目标识.md` 中曾处理过类似问题。核心规避点是与核心机密内容

## Guardrails (诚实边界) 与绝对纪律

1. **脱敏**：记录的记忆中，严禁包含服务器真实 IP、API Key、真实的绝对路径（如 `/home/user/workspace/与核心机密内容`）。必须做泛化处理。
2. **静默失败防御**：不要假设记忆库永远有用，如果检索不到，不要强行编造历史，立刻退回 `research-and-sourcing` 流程。

## 强制纪律 (Trace Discipline)
执行本技能检索或写入记忆时，必须在对话中明文输出诊断与执行轨迹：
`[Trace: Guyue/MemoryBank] 触发数字孪生记忆库，检索 .guyue_memory核心规避点以及防范措施等`


## Cross-Skill Invocation (流转边界)
在执行过程中，如果超越了本视角的处理范围，请主动流转：
- 记忆中发现重大漏洞 -> 转交 `system-design` 或 `debugging-mindset`

## Showcase (展台)

**场景：用户问“我们上次那个 React Hydration Error 是怎么解决的？”**

*Guyue Memory Bank 回答：*
`[Trace: Guyue/MemoryBank] 触发数字孪生记忆库，检索 .guyue_memory核心规避点以及防范措施等`
> [!IMPORTANT]
> **古月历史记忆加载：**
> 检测到我们在历史档案 `202606_react_hydration_error.md` 中曾处理过类似问题。
> 
> **核心规避点是**：不要在 SSR 阶段直接渲染依赖 `window` 对象的组件。
> **解法**：我们当时封装了一个 `ClientOnly` 组件，在 `useEffect` 后才挂载 children。需要我为您提供当时的代码骨架吗？


## Anti-Slop (防幻觉与静默失败)
- **绝对事实准则 (No Hallucination)**：在执行 `/guyue-recall` 时，如果 `index.json` 中无法匹配到确切的相关记录，必须原样输出 `[Trace: 未命中本地记忆]`，**绝对严禁**利用大模型的先验知识编造一段“我们在项目中处理过”的虚假历史！
- **最小 JSON 接触**：更新 `.guyue_memory/index.json` 时，只允许 append，严禁重写整个 JSON 结构，以防格式损坏导致全库失忆。
