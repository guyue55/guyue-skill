---
name: sop-maker
description: Use after a task or incident has genuinely succeeded and the user wants a reusable SOP, runbook, checklist, or team procedure. Extract steps from actual evidence, inputs, failures, verification, and boundaries; do not invent procedures for unproven work or replace general documentation.
---

# 古月 / SOP 生成器 (SOP Maker)

> [!NOTE]
> 这是 `guyue` 的“数字孪生传承中心”。
> 我们不仅解决问题，还要把每一次成功的经验固化下来，变成可供人类或衍生 Agent 学习和复用的企业级资产。

## 核心心智模型 (Core Mental Models)

1. **以终为始 (End-to-End Extraction)**
   - 从成功的结果倒推，提取出**必不可少的关键步骤**。
   - 删除无信息量的试错流水，但保留会改变判断的失败模式、诊断分支、恢复动作和不可重放副作用；SOP 既要能走通，也要知道何时停下。

2. **结构化表达 (Structured Output)**
   - SOP 必须是一份高度结构化的 Markdown 文档。
   - 包含：适用场景、前置依赖、核心执行步骤、异常处理方案 (Troubleshooting)。

3. **去除冗余与信息永续性 (Zero Fluff & Information Permacomputing)**
   - 坚决杜绝“车轱辘话”。SOP 不是长篇大论的散文，而是可以作为“说明书”直接照着做的硬核工作流。
   - 把稳定方法和版本快照分开：稳定步骤保留长期价值，操作系统、工具版本、权限和环境依赖必须明确记录并设置复查条件，不能为了“永续”删掉复现所需信息。
4. **长程任务四件套 (Long Goal Asset Set)**
   - 若成功经验来自多阶段任务、Goal 模式、发布候选或长期执行，SOP 必须沉淀四件套：总控文档、执行账本、阶段计划、活体证据包。
   - SOP 不能只写“按计划执行并验证”。必须写清恢复入口、失败记录格式、证据新鲜度检查、否定清单和最终完成定义。

## 强制纪律 (Trace Discipline)
首次接管时输出一次：
`[Trace: Guyue/SOPMaker] 从已验证结果提取可重复步骤、失败分支与停止条件`

只有适用范围、验证结果或循环封装结论变化时追加。

## When to Use (何时使用)
- 当古月成功完成了一次复杂的架构设计、功能开发或故障排查时。
- 当用户要求将当前的解决链路总结为教程、说明书或标准作业程序 (SOP) 时。
- 当用户要求把已经跑通的反复手工提示、周常审查、发布检查或多 Agent 协作沉淀为循环工程资产时。

## Anti-Patterns (防相控反模式)
- 不用理论科普挤占执行步骤；必要原理只解释会影响判断的部分。
- 没有成功结果或可复跑证据时，只能写实验记录或排障计划，不能脑补“已验证 SOP”。
- 环境、版本、权限和数据前置条件必须明确，并写出何时需要复查。
- 避免只写“确保、注意、检查”等空动作；改成可观察步骤、命令、责任人或通过标准。
- 一次性任务不包装成 Loop Contract。没有稳定输入、可重复步骤、验证资产和停止条件时，只写复盘或改进建议。
- 阶段完成、脚本通过或截图无白屏不等于终局完成；长程 SOP 保留 MVP、local-only、release candidate、production-ready 等状态差异。

## Loop Contract (循环契约)

当 SOP 面向循环工程或动态工作流时，必须在普通 SOP 之外增加 `Loop Contract` 小节。它用于让下一次 Agent、Custom subagent 或自动化脚本知道什么时候启动、如何循环、何时停止。

`Loop Contract` 必须包含：

1. **目标**：这个循环解决什么重复问题，业务或用户价值是什么。
2. **稳定输入**：每次循环需要的仓库、文档、日志、需求、测试、接口或发布证据。
3. **循环体**：每轮固定执行的动作，例如扫描、分派、实现、汇总、修正、验证。
4. **检查器**：谁或什么脚本判断这一轮是否通过；执行器和检查器不能完全同一视角。
5. **停止条件**：通过标准、失败熔断、缺证据熔断、授权熔断和回退条件。
6. **预算上限**：最大轮数、最长时间、最大 Token、最大子任务数量、可用工具范围。
7. **验证资产**：测试、截图、日志、diff、报告、CI gate、回放记录或人工确认点。
8. **沉淀出口**：继续作为 SOP，还是升级为 Skill、Custom subagent、Hook、Automation 或 CI gate。

## Step-by-Step Execution (标准执行工作流)
1. **证据倒推**：定位成功结果、核心动作、失败分支和验证证据。
2. **抽象提炼**：把私人路径和地址改成仓库相对路径或 `/path/to/project` 等安全示例。
3. **适用边界**：记录环境、版本、权限、输入和不适用场景。
4. **失败复盘**：保留最容易误判的分支、最小诊断动作和恢复方式。
5. **循环判断**：如果链路会重复，补充 `Loop Contract`；不满足稳定输入、停止条件和验证资产时，明确“不适合包装为循环”。
6. **长程资产抽取**：跨阶段任务补齐 v3 总控、承诺覆盖、账本状态、重放类别、委派收束、哈希绑定活体证据、否定清单和恢复顺序。
7. **模板输出**：按目标读者和项目惯例选择模板，不机械扩写空章节。

## 长程任务 SOP 模板补丁

当 SOP 来自长期 Goal 或多阶段工程时，在普通 SOP 模板中追加：

```markdown
## 总控入口
- 控制包版本：3
- Goal ID：
- 总控文档：
- 执行账本：
- 阶段计划目录：
- 委派包与收束预算：

## 每阶段账本字段
- RUN ID：
- 当前状态：
- 当前阶段 ID：
- 当前任务 ID：
- 本轮改动：
- 失败命令：
- 修复动作：
- 活体证据文件、SHA-256、实现版本与工作树状态：
- 人工判断：
- commit：
- 停止原因：
- 完成判定：
- 下一入口：

## 承诺覆盖
- REQ-/NREQ-/DEC-/RISK- ID：
- 对应阶段与 EVID- ID：

## 副作用重放
- TASK- ID：
- replay_safe / verify_before_repeat / compensate / human_required：
- 核验、补偿或重新审批方式：

## 否定清单
- 不能出现：
- 出现时的最小修复和重跑命令：

## 恢复顺序
1. 读总控文档。
2. 读执行账本最后一条记录。
3. 查当前工作树。
4. 重跑必要的新鲜度检查。
5. 继续下一阶段。
```
