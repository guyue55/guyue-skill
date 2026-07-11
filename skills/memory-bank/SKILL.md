---
name: memory-bank
description: Record or recall verified decisions, fixes, lessons, and prevention for "记住这个坑", "上次怎么修的", /guyue-remember, and /guyue-recall. Separate public curation from private runtime memory, require provenance/evidence/lifecycle metadata, reject secrets, and never invent a match.
---

# guyue / memory-bank

记忆不是聊天摘要仓库。它只保存经证据确认、未来可能改变判断的决策与教训，并带来源、作用域、置信度、生命周期和复查期限。

## 存储边界

- `.guyue_memory/index.json` 是随包发布的**公共精选索引**，默认可以为空；不得把私有运行记录写入这里。
- `.guyue_memory/local/index.json` 与 `.guyue_memory/local/active/` 是默认的**本地私有运行存储**，由 Git 忽略并从发布归档排除。可用 `GUYUE_MEMORY_DIR` 指向其他私有目录。
- `.guyue_memory/local/archive/` 保存无损归档详情。归档改变状态和路径，不截断原始教训。
- 索引是定位入口，Markdown 是详情；先查索引，命中后只读相关详情。

## 何时使用

- 用户明确要求记录、回忆或更新一条历史教训。
- 已验证的架构决定、复杂故障根因或发布事故可能在未来重复发生。
- 当前任务与已知历史故障、长期 Goal 恢复或既往决定高度相关。

普通新请求不默认加载全部记忆。检索失败只说明“未命中”，继续当前任务的正常取证路线，不自动假设需要联网调研。

## 写入契约

优先调用 `guyue_write_memory`。每条 schema v2 记忆必须包含：

- `id`：稳定 `MEM-...` 标识；
- `Symptom`、`Root Cause`、`Solution`、`Prevention`；
- `provenance`：来自哪次任务、决定或证据；
- `scope`：适用项目、模块或通用范围；
- `evidence`：支持根因和解法的测试、日志、产物或人工确认；
- `confidence`：`low`、`medium` 或 `high`；
- `status`：`active`、`superseded` 或 `archived`；
- `supersedes`：被本条替代的记忆 ID；
- `review_after`：需要重新验证的日期；
- `tags`、一句话 `summary` 和 UTC `timestamp`。

只记录已验证教训。仍在猜测的根因应留在排障记录，不写成高置信记忆。写入前扫描密钥、Token、私有地址、个人绝对路径和敏感日志；发现后先脱敏。索引使用临时文件原子替换，不能对 JSON 做无锁字符串追加。

## 检索契约

1. 把查询收敛为项目、模块、错误、决定或风险关键词。
2. 先检索公共精选索引和本地私有索引的 `tags`、`summary`、`scope`、`evidence`。
3. 默认只返回 `active`；`superseded` 和 `archived` 仅在追溯历史时读取。
4. 命中后核对 `scope`、`confidence`、`review_after` 和证据是否仍适用于当前版本。
5. 只有高相关且未过期的记录才影响当前决定；否则把它标成历史线索并重新验证。
6. 未命中时明确输出 `[Trace: 未命中本地记忆]`，严禁编造“我们上次处理过”。

## 生命周期与 GC

- 新结论替代旧结论时，写新记忆并用 `supersedes` 把旧条目标成 `superseded`，保留审计链。
- 到达 `review_after`、超过年龄上限或详情过大时，运行 `python3 scripts/memory_gc.py --dry-run` 预览，再运行无 `--dry-run` 的命令归档。
- GC 必须移动完整详情、原子更新索引并保留 `archived_at` 与原因；缺文件、非法路径或坏索引要报告，不能静默删除。
- 记忆不是完成证据。发布、权限和架构结论仍需对当前源码与活体产物重新核验。

## Trace 与边界

首次检索或写入时输出一次：

`[Trace: Guyue/MemoryBank] 检索或记录已验证教训；只读取命中项，不暴露私有内容`

只有命中状态、写入结果或安全边界变化时追加 Trace。不得逐条输出索引内容、内部推演或敏感详情。

## 反模式

- 不把整段聊天、原始日志或未经验证的猜测存成记忆。
- 不让公开索引指向被发布规则排除或不存在的私有文件。
- 不把“曾经有效”写成“当前仍然有效”。
- 不因检索命中就跳过当前项目的测试、权限或版本核验。
- 不在用户未要求且历史不会改变判断时，为仪式感加载记忆。
