---
name: ecosystem-scout
description: 古月的生态寻猎者。处理外部工具链接、搜索推荐技能，并以极轻量的形式将它们作为外部依赖注册入库，实现海量工具扩展且零臃肿。
---

# ecosystem-scout (生态侦察兵)

> 一句话定位：古月的极简生态连接器，用两级缓存与外部依赖机制，让 Agent 拥有海量技能却不增一分臃肿。

## 你什么时候需要它？
- **场景一（主动求助）**：“帮我找个能做 XXX 的好用技能 / 插件 / 库。”
- **场景二（被动摄取）**：“收纳这个 GitHub 项目 `https://github.com/xxx/yyy`” 或 “整合 XXX 技能”。
- **场景三（生态防胖）**：希望 Agent 能记住几百个技能，但不想让全局 Context Window 被这几百个工具说明文书塞爆时。

## 核心机制：Two-Phase Loading (两级防胖挂载)
1. **Level 1 (轻量注册)**：将工具的 `name`, `description` 和 `trigger_intent` 写入 `skills_manifest.json` 下的 `external_dependencies`。
2. **Level 2 (按需提取)**：只有当用户当前的聊天语境完美匹配到某个 `trigger_intent` 时，古月才会利用该记录里的 `command` (克隆/安装) 或 `url` 去拉取真实的文档和能力。

## 工作流与分级安全边界 (Execution SOP)

### 1. 调研与横纵对比 (Search & Classification)
无论用户提供的是模糊需求还是明确链接（如“收纳 xxx”、“整合 xxx”），**强制第一步必须是 `search_web` 联网检索**。
- **搜什么**：项目口碑、是否有更轻量的竞品、是否长期不更新、它的核心依赖是什么。
- **意图分类**：通过检索分析，判断该工具属于哪一类：
  - **类型 A：Agent 技能 / 插件 (Skill/Plugin)** (例如：包含 `SKILL.md`，MCP Server，或专为大模型打造的工具)。
  - **类型 B：普通开源项目 / 库 / 外部工具 (Library/Tool)**。

### 2. 差异化执行 (Differentiated Execution)

#### 【分支 A：如果目标是 Agent 技能 / 插件】
这是古月需要“同化”的同类，采取**全自动收编策略**：
1. **自动安装**：根据公开仓库，自动克隆代码至本地的全局/古月技能扩展目录（如 `~/.gemini/antigravity/skills/` 或类似）。
2. **打磨同化**：立刻联动调用 `luban` 技能。对刚拉下来的技能代码进行“过尺、验料与慢刨”，强制确保其遵循古月的防臃肿规则。
3. **极简注册**：打磨完成后，将指向该技能的指针（包含 `name`, `description`, `trigger_intent`）写入 `skills_manifest.json` 下的 `external_dependencies` 中，方便日后随时调度。
4. **输出战报**：向用户展示自动打磨完成的《技能出师证书》。

#### 【分支 B：如果目标是普通开源项目 / 工具 / 库】
此类项目通常体量巨大且并非直接 Agent-readable，采取**审慎收纳策略**：
1. **生成评估报告**：整理出该工具的特点、同类竞品和在生态中的位置，生成 `[工具名]_评估报告.md` (Artifact)。
2. **等待授权 (Approval Gate)**：必须停下来询问用户：“该项目属于通用工具/库，请问是否需要在本地执行物理安装（如 `npm install -g`），还是仅记录为古月的外部依赖（仅收纳）？”
3. **执行决议**：若用户选择“仅收纳”，则按极简模式只写 `skills_manifest.json`；若选择“物理安装”，则拉取代码。

### 3. 安全检查 (P0)
绝不能主动执行未知链接里的大段 Bash 脚本；如果是普通库的自动物理安装，必须展示将要执行的 Shell 命令。

## 极简注册格式 (Registry Format)
写入 `skills_manifest.json`：
```json
// 在 external_dependencies 节点中追加：
{
    "name": "提取的名字",
    "description": "20字以内的极限摘要",
    "package_id": "仓库ID或唯一标识",
    "command": "若是类型 A 则填写调用的指令，若仅收纳则为空",
    "url": "官方链接或仓库路径"
}
```

## 测试样例 (Test Prompts)
* `dry_run`
> **User**: "收纳这个专门画甘特图的 Agent 技能 `https://github.com/example/gantt-skill`。"
> **Expected**: scout 启动 -> 发现它是类型 A (Agent Skill) -> 自动执行 `git clone` 到本地技能目录 -> 调用 `luban` 打磨它的 `SKILL.md` 确保防臃肿 -> 写入 manifest 的 external_dependencies -> 向用户展示打磨成功的战报。

> **User**: "整合 `https://github.com/torvalds/linux` 到古月里。"
> **Expected**: scout 启动 -> 发现它是类型 B (巨型开源项目) -> 生成《Linux 评估报告》Artifact -> 停下来询问：“这是通用开源库，是执行本地 Clone 还是仅做收纳记录？” -> 等待用户指示。
