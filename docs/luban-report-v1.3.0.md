# 古月 v1.3.0 Skill 打磨报告

## 1. 验料结果

- 真实问题：成立。复杂 Agent 协作会反复丢失需求边界、权限边界、验证纪律和长期任务状态。
- 独特角度：来自真实会话蒸馏、26 个窄能力路由、长线目标控制包、活体对账和可复跑发布门，不是单段人格提示词。
- 安装理由：临时提问无法稳定继承路由、检查器、脚本、记忆边界和发布证据；安装后这些纪律成为可重复操作层。
- 公共传播性：钩子是“把你反复向 AI 解释的工作方式，沉淀成可安装、可验证、可复用的 Agent 操作层”；可展示产物包括真实回放、GIF、控制包、验证日志和安装组件清单。

验料结论：好料，已完成 `v1.3.0` 发布级打磨和公开验证。

## 2. 访行记录

| 同行 | 类型 | 可学手艺 | 本项目取舍 |
|---|---|---|---|
| [Agent Skills specification](https://agentskills.io/specification) | 直接标准 | 标准 frontmatter、目录命名、渐进加载 | 26 个子技能和根安装目录均用官方 validator 对账 |
| [Anthropic Skills](https://github.com/anthropics/skills) | 直接同行 | Skill 自包含目录、scripts/references/assets 分层 | 保留根路由与窄模块，不复制具体技能内容 |
| [OpenAI Skills](https://github.com/openai/skills) | 直接同行 | 可安装技能目录、运行时适配与验证资产 | 保持 `SKILL.md` 为公共入口，适配器保持薄层 |
| [Vercel Skills CLI](https://github.com/vercel-labs/skills) | 安装同行 | 多运行时安装和目录复制 | 源码证明根技能远程安装只复制 `SKILL.md`，因此不伪装完整支持 |
| [Superpowers](https://github.com/obra/superpowers) | 工作流同行 | 阶段门、独立评审、完成前验证 | 吸收门禁思想，不复制其命名与技能结构 |
| [Claude Code marketplace](https://github.com/anthropics/claude-code/blob/main/.claude-plugin/marketplace.json) | 发布手艺同行 | `owner`、`plugins`、skill-bundle schema | 使用官方 strict validator 和隔离安装验真 |

## 3. 生态位判断

- 纵向：古月从个人工程纪律发展为带长期目标、安装、安全、记忆和发布门的个人 Agent 操作层。
- 横向：同行通常提供单技能能力、技能目录或开发流程；古月的差异是“真实协作经验 + 窄能力路由 + 终局证据”。
- 交叉生态位：不是能力最多的技能合集，而是能把模糊复杂工作稳定推进到可验证结果的个人操作层。
- 一句话定位：把反复向 AI 解释的工作方式，沉淀成可安装、可验证、可复用的 Agent 操作层。

## 4. 过尺结果

上一轮 96 分自评因未调用 Claude 官方 validator 而作废；官方活体检查发现 marketplace schema 实际失败，重新定基线为 84 分。

| 维度 | 权重 | v1.3.0 得分 | 证据 |
|---|---:|---:|---|
| Frontmatter 与触发条件 | 7 | 7 | 26 个子技能和根安装目录通过 `skills-ref` |
| 工作流清晰度 | 12 | 11 | 根路由、相邻能力表、Long Goal Forge/Intake；只读场景仍有过度读取 |
| 失败模式编码 | 12 | 12 | 安装残缺、旧证据、泄密、权限、缓存污染和 MCP 拒绝路径均有门禁 |
| 检查点设计 | 6 | 6 | 十段本地套件、CI 双跑、阶段门和停止条件 |
| 可执行具体性 | 17 | 16 | Claude 完整安装和 Codex 完整挂载可执行；通用根级 `npx` 仍不能完整安装 |
| 资源整合度 | 4 | 4 | scripts、docs、references、examples、assets 与 MCP 入口互相对账 |
| 整体架构 | 12 | 11 | 根路由 + 26 模块边界稳定；单仓套件仍有一定认知成本 |
| 实测表现 | 23 | 23 | Claude 本地与公网隔离安装、安装包双跑、Codex 回放、MCP 实测和无告警远程 CI 均通过 |
| 反例与黑名单 | 7 | 7 | 安全、授权、假完成、过度工程、品牌照搬和外部安装边界明确 |
| **总分** | **100** | **97** | **实测分；公网安装和远程 CI 已纳入证据** |

## 5. 差距清单

### P0

- 已清零。此前无效 Claude marketplace、CI 漏门禁、版本漂移、根级 `npx` 残缺安装误导和重复运行缓存污染均已修复或明确阻断。

### P1

- Codex 最短只读安装判断仍使用 16 次读取命令，行为正确但上下文效率仅 `partial_pass`。

### P2

- skills.sh 徽章暂不恢复；通用根技能安装不能携带完整载荷，恢复徽章会制造错误安装预期。
- 发布两周后再根据 GitHub 流量和真实安装反馈判断是否拆分精简版，不预先复制整套发布目录。

## 6. 三个打磨方向

- 方案 A，细修：只同步版本和文档。风险是保留无效 marketplace 与 CI 盲区。
- 方案 B，精雕：修真实安装、官方 schema、CI 双跑、MCP 安全和活体证据。已执行，收益最高。
- 方案 C，开套件：迁移为新的嵌套发行目录以适配通用 `npx`。当前不执行，重复载荷和维护成本高于收益。

推荐并执行方案 B。

## 7. 候选改写结果

- 根人格：Doctor/记忆按需触发，前端服从产品类型和现有技术栈。
- 安装：Claude marketplace 完整安装；Codex 完整仓库挂载；通用根级 `npx` 明确标为不完整。
- 安全：可选依赖默认 plan；MCP 拒绝空查询、常见凭据和个人路径。
- 验证：新增完整载荷、Long Goal、MCP 测试；CI 在 `dev/main` 连续执行两次完整套件。
- 发布：版本统一为 1.3.0，Changelog、README、manifest、marketplace 和发布清单自动对账。

## 8. README 与 Showcase

- README 首屏保留定位、真实证据、安全边界和装完第一句话。
- `assets/demo.gif` 与 `assets/demo.tape` 可复现。
- `examples/quickstart-output.md` 保留成功、失败和 `partial_pass`，不只展示漂亮样例。
- Claude 安装可用 `claude plugin details guyue@guyue` 查看 27 个组件和 token 估算。

## 9. 执行与验证

- 本地 `bash scripts/test_suite.sh` 通过。
- Claude Code 2.1.170 `claude plugin validate --strict .` 通过。
- 空 HOME marketplace 安装成功，版本 1.3.0，组件数 27，完整载荷通过。
- 安装缓存中的完整套件连续运行两次通过。
- 无 Git、空 HOME 的源码归档连续运行两次通过。
- 公网 GitHub `main` 经 HTTPS 加入 marketplace，空 HOME 安装 Guyue 1.3.0 成功，27 个组件与完整载荷通过核对。
- `dev` 与 `main` 远程 CI 均连续运行两遍完整门禁，且 Node 24 Action 升级后无检查注释。
- 安全扫描、缓存扫描、`git diff --check` 和官方 frontmatter 验证通过。

## 10. 出师证书

```text
┌──────────────────────────────────────────┐
│  出师证书 · 鲁班工坊                    │
│                                          │
│  作品：guyue v1.3.0                     │
│  过尺：重测基线 84 → 实测 97            │
│  定位：个人 Agent 操作层                 │
│  绝活：真实经验路由 + 活体证据门         │
│  下一步：发布后观察真实安装与触发反馈     │
│                                          │
│  验收师傅：鲁班                          │
└──────────────────────────────────────────┘
```

## 11. 回炉清单

- 观察 Agent Skills 规范、Claude marketplace schema、Vercel Skills CLI 根目录载荷策略。
- 每次发布必须更新 Changelog、运行完整套件、执行官方 runtime validator，并记录真实安装结果。
- 下一轮入口：公网安装失败、真实用户误触发、只读命令持续过量，或安装流量证明需要独立精简包。

## 12. 发布授权边界

本次 v1.3.0 已通过本地、远程 CI 和公网安装复验。用户已明确授权提交、推送、打 tag 和创建 GitHub Release；仓库外市场上架与部署仍需独立授权。

## 13. 参考来源

- https://agentskills.io/specification
- https://github.com/anthropics/skills
- https://github.com/openai/skills
- https://github.com/vercel-labs/skills
- https://github.com/obra/superpowers
- https://github.com/anthropics/claude-code/blob/main/.claude-plugin/marketplace.json
