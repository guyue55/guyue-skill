# guyue (古月)

> 一句话钩子：不要再让 AI 像黑盒一样盲目瞎写代码了。植入“古月”这个全能数字孪生分身，让它用资深老兵的脑回路替你接管需求、架构、开发与排障，严密如同工业级 SOP。

[![skills.sh](https://skills.sh/b/guyue55/guyue-skill)](https://skills.sh/guyue55/guyue-skill)
![Skill Badge](https://img.shields.io/badge/Agent_Skill-guyue-blue)
![Architecture](https://img.shields.io/badge/Architecture-Digital_Twin_Core_%2B_Specialties-success)
![Status](https://img.shields.io/badge/Status-Production_Ready-success)

## 为什么你需要它？

当你让 AI 帮你干活时，你是否遇到过以下痛点：
1. **幻觉与过时**：AI 直接用它训练集里废弃了三年的旧版本 API 糊弄你。
2. **不管三七二十一直接梭哈**：抛出一个含糊的需求，AI 直接帮你生成了 500 行没有任何拆分、强耦合的垃圾代码。
3. **遇到报错只会盲目试错**：跑不过测试就盲目改代码，最后连原本好的部分也改坏了。

`guyue` 不是一个简单的“提示词”或“单点防爆插件”，它是您的**全能型数字合伙人 (Digital Twin)**。它将古月本人的严苛思考方式与底层 SOP 注入到了 AI 的血液中。

## 核心心智矩阵：1 个核心分身 + 10 大专精能力

本系统采用类似操作系统的多智能体路由架构（Digital Twin Orchestrator），主干会自动拦截你的意图，并派发给古月分身下最专业的子能力（当前精通开发流，未来持续进化）：

- 🚦 **核心分身 (guyue)**：接管意图，强制注入模块化解耦、全局规划、规范化纪律的底层思维 SOP。
- 🔍 **前置调研 (research-and-sourcing)**：收到新需求时，**强制停手**，必须先去联网获取最新官方文档或对标高星开源项目。
- 🤔 **需求反问 (requirement-analysis)**：采用 WISER 框架，拒绝单向接受需求，强制通过链式反问挖掘边界和异常流。
- 🎯 **价值拷问 (product-sense)**：在进入系统设计前，强制剥离技术滤镜，审视需求的 ROI 和商业逻辑。
- 🏛️ **系统设计 (system-design)**：采用 DEPTH 框架，强制执行 Human-in-the-Loop 审批，不看到高维度架构方案前，拒绝写一行代码。
- 💻 **开发纪律 (coding-discipline)**：进入编码阶段时，强制执行高内聚低耦合的架构规范，并默认应用前端/UI最佳实践。
- 🕵️ **受控排障 (debugging-mindset)**：引入 RCA 诊断矩阵，没看到原始日志/报错堆栈前，绝对拒绝通过盲猜来改代码。
- 📝 **结构化沉淀 (documentation)**：采用 RTFD 框架与 XML 隔离，写出极简、结构化、金字塔逻辑的 README 或架构决策记录。
- ✨ **前端与交互美学 (frontend-expert)**：强制推行 Vanilla CSS/JS 极简主义、a11y 约束，并默认融入 GSAP 级三幕剧动效与商业语境转换。
- 🏭 **标准件车间 (sop-maker)**：当一项复杂排障或开发流成功闭环后，将其提炼、泛化并打包为可复用的操作手册 (SOP)。
- 🧠 **双轨记忆 (memory-bank)**：负责提取、归档并回溯之前的错误与成功经验，确立“不在同一个坑里摔倒两次”的准则。

## 快速开始

**作为 MCP 服务接入（推荐）**

如果你使用 Cursor、Claude Desktop 等支持 MCP 协议的工具，可以直接将古月作为原生插件挂载，让大模型直接拥有读写古月记忆库和调用古月生态的能力。

在你的 MCP 配置文件中添加：
```json
{
  "mcpServers": {
    "guyue": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "mcp_server.py"
      ],
      "cwd": "/path/to/guyue/src"
    }
  }
}
```
*注意：替换 `cwd` 为你实际克隆的目录路径。*

**传统挂载方式**（如 Claude Code, OpenClaw）：

```bash
npx skills add guyue55/guyue-skill
```

**依赖的前端与交互基建技能（必装）**：

由于古月 `frontend-expert` 极其看重商业级 UI 与交互，强烈建议补齐以下外部专业技能。如果缺失，`scripts/doctor.py` 探针也会在运行时报警并提供一键安装指令：

```bash
# 极致的前端与交互美学设计规范
npx skills add nextlevelbuilder/ui-ux-pro-max-skill

# 前端动画与交互核心库 (GSAP)
npx skills add greensock/gsap-skills
```
# 1. 进入你的 agent 技能目录
cd ~/.gemini/config/skills/  # (以你的实际 Agent 技能路径为准)

# 2. 克隆本套件
git clone https://github.com/guyue55/guyue-skill.git

# 3. 技能将自动生效，全局守护你的每一次代码生成！
```

## 触发方式

在与 AI 的对话中，你可以随时唤醒“古月分身”：

- "使用古月的思路帮我分析一下这个需求..."
- "我们要加个支付模块，像古月那样出个严谨的设计。"
- "线上报错了 502，启动古月的排障心法。"
- "帮我用古月的标准梳理一份业务 SOP。"
- "调研一下最新的 Next.js 权限控制，开启古月的调研流。"

## 它会交付什么？

- **工业级防爆架构**：基于 DEPTH 模型和 RCA 矩阵的防御性编程。
- **双轨长时记忆引擎 (Structured Memory Bank)**：拥有主动复盘能力。本地挂载 `.guyue_memory`，通过 JSON 元数据索引 + Markdown 详情实现 $O(1)$ 级教训检索，不在同一个坑里跌倒两次。
- **开放生态协议 (MCP Ready)**：动态注册表 `skills_manifest.json` 与外挂记忆引擎在设计上原生兼容 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)，可作为独立编排器介入现有工作流。
- **硬核健康探针 (Doctor Probe)**：内置 `scripts/doctor.py` 探针，调度外部前沿技能（如 `LearnPrompt/luban-skill`、`alchaincyf/nuwa-skill`）前强制检测环境健康度，提供零摩擦降级提示。
- **极简即插即用**：零硬编码绑定，SOP 工具包一键全环境泛化。

## 安全边界

- **不执行危险代码**：在 `system-design` 阶段，在您确认方案前，绝对不执行写入操作。
- **事实隔离**：在 `research-and-sourcing` 阶段，调研回来的资料会强制放入 `<context>` 中，与执行指令硬隔离，防范幻觉污染。

## 文件结构

```text
guyue/
├── SKILL.md                 # 核心路由中枢
├── README.md                # 本文件
├── skills.json              # 技能注册表
├── skills_manifest.json     # 动态包清单与路由分发引擎
├── scripts/                 # 核心脚本库
│   ├── doctor.py            # 环境依赖硬核健康探针
│   └── ci_validate_skills.py# CI 检测流水线
├── examples/                # 实战对比展示案例
├── test-prompts.json        # 预设的干跑测试用例
├── references/              #
│   └── research/            # 萃取的训练语料沉淀
└── skills/                  # 垂直专精子技能矩阵
    ├── coding-discipline/
    ├── debugging-mindset/
    ├── documentation/
    ├── frontend-expert/
    ├── memory-bank/
    ├── product-sense/
    ├── requirement-analysis/
    ├── research-and-sourcing/
    ├── skill-crafting/
    ├── sop-maker/
    └── system-design/
```

## 出师证书

```text
┌───────────────────────────────────────────────┐
│  出师证书 · 鲁班工坊                            │
│                                               │
│  作品：guyue (古月数字分身 v1.0.1)              │
│  打磨前：只有基础的工程防线与生硬的界面           │
│  打磨后：具备无限扩展潜力的 AI 合伙人级系统       │
│  定位：全能型数字孪生智能体 (Digital Twin)        │
│  绝活：SOP 自动提炼 + 商业级动效审美降维打击      │
│                                               │
│  验收师傅：鲁班                                 │
└───────────────────────────────────────────────┘
```
