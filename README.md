# guyue-perspective (古月视角)

> 一句话钩子：不要再让 AI 像黑盒一样盲目瞎写代码了。给你的智能体装上这套“重工业级开发纪律套件”，让它学会停下来调研、懂得分层设计、并严格自证清白。

[![skills.sh](https://skills.sh/b/guyue55/guyue-perspective)](https://skills.sh/guyue55/guyue-perspective)
![Skill Badge](https://img.shields.io/badge/Agent_Skill-guyue--perspective-blue)
![Architecture](https://img.shields.io/badge/Architecture-Router_%2B_5_Specialties-success)
![Status](https://img.shields.io/badge/Status-Production_Ready-success)

## 为什么你需要它？

当你让 AI 帮你写代码时，你是否遇到过以下痛点：
1. **幻觉与过时**：AI 直接用它训练集里废弃了三年的旧版本 API 糊弄你。
2. **不管三七二十一直接梭哈**：抛出一个含糊的需求，AI 直接帮你生成了 500 行没有任何拆分、强耦合的垃圾代码。
3. **遇到报错只会盲目试错**：跑不过测试就盲目改代码，最后连原本好的部分也改坏了。

`guyue-perspective` 不是一个简单的“提示词”，它是一个**重工业级的防爆智能体开发套件 (Skill Suite)**。它将一位资深架构师的严苛纪律注入到了 AI 的血液中。

## 核心矩阵：1 个路由中枢 + 6 大垂直专精

本套件采用多智能体路由架构（Multi-Agent Orchestrator），主干会自动拦截你的意图，并派发给最专业的子心智：

- 🚦 **核心中枢 (guyue-perspective)**：拦截意图，强制注入模块化解耦、中文注释、规范化 Git 提交的底层纪律。
- 🔍 **前置调研 (research-and-sourcing)**：收到新需求时，**强制停手**，必须先去联网获取最新官方文档或对标高星开源项目。
- 🤔 **需求反问 (requirement-analysis)**：采用 WISER 框架，拒绝单向接受需求，强制通过链式反问挖掘边界和异常流。
- 🏛️ **系统设计 (system-design)**：采用 DEPTH 框架，强制执行 Human-in-the-Loop 审批，不看到高维度架构方案前，拒绝写一行代码。
- 💻 **开发纪律 (coding-discipline)**：进入编码阶段时，强制执行高内聚低耦合的架构规范，并默认应用前端/UI最佳实践。
- 🕵️ **受控排障 (debugging-mindset)**：引入 RCA 诊断矩阵，没看到原始日志/报错堆栈前，绝对拒绝通过盲猜来改代码。
- 📝 **结构化沉淀 (documentation)**：采用 RTFD 框架与 XML 隔离，写出极简、结构化、金字塔逻辑的 README 或架构决策记录。

## 快速开始

![Demo](assets/demo.gif)

### 方式 1：一键安装 (推荐)

如果你使用的是支持 Skills 体系的 Agent（如 Claude Code, OpenClaw）：

```bash
npx skills add guyue55/guyue-perspective
```

### 方式 2：本地克隆

```bash
# 1. 进入你的 agent 技能目录
cd ~/.gemini/config/skills/  # (以你的实际 Agent 技能路径为准)

# 2. 克隆本套件
git clone https://github.com/guyue55/guyue-perspective.git

# 3. 技能将自动生效，全局守护你的每一次代码生成！
```

## 触发方式

在与 AI 的对话中，你可以随时唤醒“古月视角”：

- "使用古月视角帮我分析一下这个需求..."
- "我们要加个支付模块，用古月的方式出个设计。"
- "线上报错了 502，启动古月的排障心法。"
- "帮我用古月的标准写一份这个仓库的 README。"
- "调研一下最新的 Next.js 权限控制，像古月那样严谨点。"

## 它会交付什么？

- **受控的设计契约**：而不是一堆杂乱无章的代码。
- **RCA 诊断表格**：而不是一次无效的 `try-catch`。
- **高内聚的模块**：包含完善中文注释、严格遵循你架构初衷的优质交付物。

## 安全边界

- **不执行危险代码**：在 `system-design` 阶段，在您确认方案前，绝对不执行写入操作。
- **事实隔离**：在 `research-and-sourcing` 阶段，调研回来的资料会强制放入 `<context>` 中，与执行指令硬隔离，防范幻觉污染。

## 文件结构

```text
guyue-perspective/
├── SKILL.md                 # 核心路由中枢
├── README.md                # 本文件
├── skills.json              # 技能注册表
├── examples/                # 实战对比展示案例
├── test-prompts.json        # 预设的干跑测试用例
├── references/              #
│   └── research/            # 萃取的训练语料沉淀
└── skills/                  # 六大垂直专精子技能
    ├── requirement-analysis/
    ├── system-design/
    ├── debugging-mindset/
    ├── documentation/
    ├── coding-discipline/
    └── research-and-sourcing/
```

## 出师证书

```text
┌───────────────────────────────────────────────┐
│  出师证书 · 鲁班工坊                            │
│                                               │
│  作品：guyue-perspective (古月视角套件)         │
│  打磨前：杂乱的私有提示词集，缺少引导与传播属性 │
│  打磨后：结构化、套件化的防爆工业级 AI 插件     │
│  定位：重工业级 AI 开发纪律套件                 │
│  绝活：Router + 6 大垂直防爆心智联合阵线        │
│                                               │
│  验收师傅：鲁班                                 │
└───────────────────────────────────────────────┘
```
