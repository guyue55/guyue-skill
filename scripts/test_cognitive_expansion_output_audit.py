#!/usr/bin/env python3
"""Regression tests for the cognitive-expansion output auditor."""

from __future__ import annotations

from audit_cognitive_expansion_output import audit_output


VALID_OUTPUT = """## PRE-EVIDENCE-SNAPSHOT E0

用户原始框架｜模型候选假设｜原始已知｜冲突｜未知
模型候选假设：候选：单一观察轴；街区优先级可能变化。

## B0 PRE-TOOL 预算账本

| 资源 | 硬上限 | 起始消耗 | 安全预留 | 状态 | 测量依据 |
|---|---:|---:|---:|---|---|
| 最大轮数 | 4 | 0 | 1 | 未触顶 | 可观察计数 |
| 墙钟时间 | 25 分钟 | 0 | 5 分钟 | 未触顶 | 单调时钟 |
| 近似有效 Token | 150000 | 0 | 22500 | 未触顶 | 代理预留 |
| 只读工具调用 | 8 | 0 | 1 | 未触顶 | 调用计数 |
| 材料打开 | 6 | 0 | 1 | 未触顶 | 唯一材料身份 |
| 可见输出 | 5000 | 0 | 1000 | 未触顶 | token 估算 |
| 授权子任务 | 0 | 0 | 0 | 不适用 | 未授权 |
| 付费成本 | 0 | 0 | 0 | 不适用 | 禁止付费 |

## 框定与动作

| 认知动作 | 选择理由 | 预期地图变化 |
|---|---|---|
| 外证 | 约束 D1 | 决定 D1 去留 |

## D：维度取舍

| 候选维度 | 谱系锚点 | 处理 | 理由 | 对决定的影响 |
|---|---|---|---|---|
| D1 候选：单一观察轴 | E0 未知 | 价值/决定：选择 | 候选/假设：机制=关键机制；操作化=对象:目标对象,覆盖:目标总体→观测框/框外单列,行粒度:每对象每周期一行,成员键:object_id,采集:直接观测,缺失:标记未知,计算:单一结果,聚合:对象→决策单元,权重:无；操作数=单一结果；单位=类别；窗口=一次固定周期；参照=无；假设=无 | 价值/决定：约束下一证据 |

## C：候选线索

| 候选 ID | 线索/预期材料 | 预期约束的 A/D/I/U | 身份、访问或版本缺口 |
|---|---|---|---|
| C1 | 产物=待取得数据v1；总体=目标对象；行粒度=每对象每周期一行；成员键=object_id；字段=单一结果；设计字段=无；窗口=固定周期；版本=规则v1 | D1 | 取得阻断=数据未取得 |

## S：材料登记

本轮无已辨明材料；不得授 E。

## E：原子来源主张

本轮无 EVIDENCE-COMMIT。

## I：有界推断

本轮无可提交 I。

## R：真实认知修订

本轮无 E/I 触发的认知修订。

## 挑战记录

| 挑战 ID | 主解释 ID | 竞争解释 | 区分证据 C/E/U | 结果 | 地图影响 |
|---|---|---|---|---|---|
| CH1 | D1 | 候选/假设：主机制=关键机制；竞争机制=替代机制；机制判据=单一结果符号区分两种机制；同一判别域=对象:D1候选总体,判别量:单一结果,时窗:取得C1后的固定窗口；分界=预注册阈值0；所需字段=单一结果；竞争预测=单一结果小于0；主解释预测=单一结果大于等于0；互斥证明=同一值不能同时小于且大于等于0；穷尽说明=缺失值归未区分；结果→更新=竞争:D1降级,主解释:D1保留,未区分:U1保留 | C1、U1 | 未区分 | 保留 U1 |

## U：冲突与未知

| 冲突或未知 | 下游影响 | 所有者 | 下一证据 |
|---|---|---|---|
| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | C1 |

## 所有权交接

| 结果片段 | 所有者 | 本地图如何使用 |
|---|---|---|
| C1 取证 | research-and-sourcing | 约束 D1 |

## 地图摘要

[D1] 候选：单一观察轴

## B1 FINAL 与停止

| 资源 | 硬上限 | 实际消耗 | 状态 | 测量依据 |
|---|---:|---:|---|---|
| 最大轮数 | 4 | 1 | 未触顶 | 可观察计数 |
| 墙钟时间 | 25 分钟 | 3 分钟 | 未触顶 | 单调时钟 |
| 近似有效 Token | 150000 | 70000 | 未触顶 | 运行中代理估算；待运行后收据 |
| 只读工具调用 | 8 | 1 | 未触顶 | 调用计数 |
| 材料打开 | 6 | 1（S 0 + C 1 + 丢弃 0） | 未触顶 | S + C + 丢弃守恒 |
| 可见输出 | 5000 | 1200 | 未触顶 | token 估算 |
| 授权子任务 | 0 | 0 | 不适用 | 未授权 |
| 付费成本 | 0 | 0 | 不适用 | 禁止付费 |

地图状态：有界可用。决策就绪：否（CE-EVIDENCE-GAP）。最高价值下一证据：C1。重新开启条件：取得 C1。
"""


VALID_RECEIPT = {
    "input_tokens": 100000,
    "cached_input_tokens": 40000,
    "output_tokens": 8000,
    "reasoning_output_tokens": 3000,
    "wall_clock_seconds": 180,
    "rounds": 1,
    "read_only_tool_calls": 1,
    "materials_opened": 1,
    "authorized_subtasks": 0,
    "paid_cost": 0,
}


def require_error(errors: list[str], fragment: str) -> None:
    if not any(fragment in error for error in errors):
        raise AssertionError(f"missing expected error {fragment!r}: {errors}")


def main() -> int:
    errors = audit_output(VALID_OUTPUT, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"valid output was rejected: {errors}")

    compact_header_spacing = VALID_OUTPUT.replace(
        "| 候选 ID | 线索/预期材料 | 预期约束的 A/D/I/U | 身份、访问或版本缺口 |",
        "| 候选ID | 线索/预期材料 | 预期约束的A/D/I/U | 身份、访问或版本缺口 |",
    ).replace(
        "| 挑战 ID | 主解释 ID | 竞争解释 | 区分证据 C/E/U | 结果 | 地图影响 |",
        "| 挑战ID | 主解释ID | 竞争解释 | 区分证据C/E/U | 结果 | 地图影响 |",
    )
    errors = audit_output(compact_header_spacing, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"cosmetic header spacing was rejected: {errors}")

    nonzero_activation = VALID_OUTPUT.replace(
        "| 只读工具调用 | 8 | 0 | 1 |",
        "| 只读工具调用 | 8 | 1 | 1 |",
    ).replace(
        "| 近似有效 Token | 150000 | 0 | 22500 |",
        "| 近似有效 Token | 150000 | 12000 | 22500 |",
    )
    errors = audit_output(nonzero_activation, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"honest activation footprint was rejected: {errors}")

    summary_first = VALID_OUTPUT.replace(
        "## 地图摘要", "## 结论先行", 1
    )
    require_error(audit_output(summary_first, VALID_RECEIPT), "结论先行")

    incomplete_budget = VALID_OUTPUT.replace(
        "| 墙钟时间 | 25 分钟 | 3 分钟 | 未触顶 | 单调时钟 |\n", "", 1
    )
    require_error(audit_output(incomplete_budget, VALID_RECEIPT), "墙钟时间")

    overrun_receipt = {
        **VALID_RECEIPT,
        "input_tokens": 200000,
        "cached_input_tokens": 20000,
    }
    require_error(audit_output(VALID_OUTPUT, overrun_receipt), "有效 Token")

    hidden_overrun = VALID_OUTPUT.replace(
        "| 材料打开 | 6 | 1（S 0 + C 1 + 丢弃 0） |",
        "| 外部材料打开 | 6 | 1（S 0 + C 1 + 丢弃 0） |",
    )
    visible_overrun = {
        **VALID_RECEIPT,
        "output_tokens": 9000,
        "reasoning_output_tokens": 0,
    }
    require_error(audit_output(hidden_overrun, visible_overrun), "可见输出")

    low_reported_character_proxy = VALID_OUTPUT.replace(
        "| 可见输出 | 5000 | 1200 | 未触顶 | token 估算 |",
        "| 可见输出 | 50000 | 1 | 未触顶 | Unicode 字符代理 |",
    )
    require_error(
        audit_output(low_reported_character_proxy, VALID_RECEIPT),
        "字符代理低报",
    )

    exceeded_character_proxy = VALID_OUTPUT.replace(
        "| 可见输出 | 5000 | 1200 | 未触顶 | token 估算 |",
        "| 可见输出 | 1000 | 100000 | 已触顶 | UTF-8 字符代理 |",
    )
    require_error(
        audit_output(exceeded_character_proxy, VALID_RECEIPT),
        "可见输出字符代理",
    )

    range_trigger = VALID_OUTPUT.replace(
        "本轮无 E/I 触发的认知修订。",
        "| R1 | E0 | E1–E3 | 支持/升权 | 候选得到支持 | D1 |",
    )
    require_error(audit_output(range_trigger, VALID_RECEIPT), "连续范围")

    missing_u_id = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 |",
        "| 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 |",
    )
    require_error(audit_output(missing_u_id, VALID_RECEIPT), "U#")

    renamed_heading = VALID_OUTPUT.replace(
        "## D：维度取舍", "## D：维度取舍账本"
    )
    require_error(audit_output(renamed_heading, VALID_RECEIPT), "精确 H2")

    normative_inference = VALID_OUTPUT.replace(
        "本轮无可提交 I。",
        "| 推断 ID | 来源前提 E | 桥接条件 | 有界结论 | 共享依赖与缺席位置 | 状态与下游用途 |\n"
        "|---|---|---|---|---|---|\n"
        "| I1 | E1 | 未核实：U1；下一证据 C1；迁移=人口：来源总体→目标总体；保持=对象/测量/尺度/时期/情境 | 若 U1 成立，则应该采用三套队列 | U1、C1 | 推断 I1；主用途 D1 |",
    )
    require_error(audit_output(normative_inference, VALID_RECEIPT), "规范词")

    unlabelled_challenge = VALID_OUTPUT.replace(
        "候选/假设：主机制=关键机制",
        "主机制=关键机制",
    )
    require_error(audit_output(unlabelled_challenge, VALID_RECEIPT), "候选/假设")

    missing_prediction = VALID_OUTPUT.replace(
        "；竞争预测=单一结果小于0；主解释预测=单一结果大于等于0",
        "；竞争预测=单一结果小于0",
    )
    require_error(audit_output(missing_prediction, VALID_RECEIPT), "字面判别字段")

    equals_prediction = VALID_OUTPUT.replace(
        "竞争预测=单一结果小于0；主解释预测=单一结果大于等于0",
        "竞争预测=单一结果小于0；主解释预测=单一结果大于等于0",
    )
    errors = audit_output(equals_prediction, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"equivalent prediction separators were rejected: {errors}")

    enhanced_summary = VALID_OUTPUT.replace(
        "[D1] 候选：单一观察轴",
        "这里新增一个没有规范归宿的专业分类。",
    )
    require_error(audit_output(enhanced_summary, VALID_RECEIPT), "地图摘要")

    undeclared_consumer = VALID_OUTPUT.replace(
        "本轮无已辨明材料；不得授 E。",
        "| 来源 ID | 材料类型与规范入口/全文 | 发布、版本与访问 | 生产目的、受众与获取门槛 | 上游依赖与缺席声音 |\n"
        "|---|---|---|---|---|\n"
        "| S1 | 规范入口与正文 | 发布：2026；版本：v1；访问：2026-07-17 正文第1节；E门=开放（正文第1节） | 研究材料 | 无 |",
    ).replace(
        "本轮无 EVIDENCE-COMMIT。",
        "| 证据 ID | 来源 ID | 原子来源主张 | 主张相关时期/版本 | 状态、新鲜度与边界 |\n"
        "|---|---|---|---|---|\n"
        "| E1 | S1 | 一个主张 | 不适用（仅核验文本） | 来源主张 E1；原子类型=单命题；命题类型=经验；生产位置=研究；支持位置=正文第1节；消费者=D1；适配=D1:测量方法；统计口径=不适用（非汇总）；新鲜度=当前；边界=文本 |",
    ).replace(
        "本轮无可提交 I。",
        "| 推断 ID | 来源前提 E | 桥接条件 | 有界结论 | 共享依赖与缺席位置 | 状态与下游用途 |\n"
        "|---|---|---|---|---|---|\n"
        "| I1 | E1 | 逻辑桥：不引入当前事实 | 单一条件结论 | 无 | 推断 I1；主用途 D1 |",
    )
    require_error(audit_output(undeclared_consumer, VALID_RECEIPT), "I1")

    evidence_output = VALID_OUTPUT.replace(
        "E0 未知", "E1", 1
    ).replace(
        "本轮无已辨明材料；不得授 E。",
        "| 来源 ID | 材料类型与规范入口/全文 | 发布、版本与访问 | 生产目的、受众与获取门槛 | 上游依赖与缺席声音 |\n"
        "|---|---|---|---|---|\n"
        "| S1 | 规范入口与正文 | 发布：2026；版本：v1；访问：2026-07-17 正文第1节；E门=开放（正文第1节） | 研究材料 | 无 |",
    ).replace(
        "本轮无 EVIDENCE-COMMIT。",
        "| 证据 ID | 来源 ID | 原子来源主张 | 主张相关时期/版本 | 状态、新鲜度与边界 |\n"
        "|---|---|---|---|---|\n"
        "| E1 | S1 | 单一来源主张 | 2026/v1 | 来源主张 E1；原子类型=单命题；命题类型=经验；生产位置=研究；支持位置=正文第1节；消费者=D1；适配=D1:测量方法；统计口径=不适用（非汇总）；新鲜度=当前；边界=单一材料 |",
    )
    errors = audit_output(evidence_output, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"valid evidence chain was rejected: {errors}")

    version_like_consumer = evidence_output.replace(
        "新鲜度=当前",
        "新鲜度=AR6",
    )
    errors = audit_output(version_like_consumer, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"version text was parsed as a consumer ID: {errors}")

    closed_collection_without_prefix = evidence_output.replace(
        "单一来源主张",
        "来源定义项目甲、项目乙",
    ).replace(
        "原子类型=单命题",
        "原子类型=封闭集合",
    )
    errors = audit_output(closed_collection_without_prefix, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"typed closed collection was rejected: {errors}")

    closed_source = evidence_output.replace(
        "E门=开放（正文第1节）", "E门=关闭（仅摘要）"
    )
    require_error(audit_output(closed_source, VALID_RECEIPT), "E门=关闭")

    missing_atomic_type = evidence_output.replace("；原子类型=单命题", "")
    require_error(audit_output(missing_atomic_type, VALID_RECEIPT), "原子类型")

    missing_claim_type = evidence_output.replace("；命题类型=经验", "")
    require_error(audit_output(missing_claim_type, VALID_RECEIPT), "命题类型")

    missing_production_position = evidence_output.replace("；生产位置=研究", "")
    require_error(
        audit_output(missing_production_position, VALID_RECEIPT),
        "生产位置=",
    )

    compound_evidence = evidence_output.replace(
        "单一来源主张", "来源主张一；同时来源主张二"
    )
    require_error(audit_output(compound_evidence, VALID_RECEIPT), "第二谓词")

    different_periods_evidence = evidence_output.replace(
        "单一来源主张", "来源使用不同时期的数据"
    )
    errors = audit_output(different_periods_evidence, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"'不同时期' false positive: {errors}")

    ranged_reference = evidence_output.replace("消费者=D1", "消费者=D1–D3")
    require_error(audit_output(ranged_reference, VALID_RECEIPT), "连续范围")

    linked_source_id = evidence_output.replace(
        "| E1 | S1 |", "| E1 | [S1](https://example.test/source) |"
    )
    require_error(audit_output(linked_source_id, VALID_RECEIPT), "来源 ID")

    vague_locator = evidence_output.replace(
        "E门=开放（正文第1节）", "E门=开放（全文）"
    )
    require_error(audit_output(vague_locator, VALID_RECEIPT), "支持位置")

    extra_consumer = evidence_output.replace(
        "消费者=D1", "消费者=D1、U1"
    )
    require_error(audit_output(extra_consumer, VALID_RECEIPT), "虚挂")

    conditional_inference = evidence_output.replace(
        "消费者=D1；适配=D1:测量方法",
        "消费者=D1、I1；适配=D1:测量方法,I1:迁移约束",
    ).replace(
        "本轮无可提交 I。",
        "| 推断 ID | 来源前提 E | 桥接条件 | 有界结论 | 共享依赖与缺席位置 | 状态与下游用途 |\n"
        "|---|---|---|---|---|---|\n"
        "| I1 | E1 | 未核实：U1；下一证据 C1；迁移=人口：来源总体→目标总体；保持=对象/测量/尺度/时期/情境 | 若 U1 成立，则形成一个描述性结论 | U1、C1 | 推断 I1；主用途 D1 |",
    )
    errors = audit_output(conditional_inference, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"valid conditional inference was rejected: {errors}")

    hidden_bridge = conditional_inference.replace(
        "若 U1 成立，则形成一个描述性结论", "形成一个描述性结论"
    )
    require_error(audit_output(hidden_bridge, VALID_RECEIPT), "显式条件结论")

    compact_spacing = conditional_inference.replace(
        "未核实：U1；下一证据 C1；迁移=人口：来源总体→目标总体；保持=对象/测量/尺度/时期/情境",
        "未核实：U1；下一证据C1；迁移=人口：来源总体→目标总体；保持=对象/测量/尺度/时期/情境",
    ).replace(
        "若 U1 成立，则", "若U1成立，则"
    )
    errors = audit_output(compact_spacing, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"whitespace-only bridge variant was rejected: {errors}")

    context_migration = conditional_inference.replace(
        "迁移=人口：来源总体→目标总体；保持=对象/测量/尺度/时期/情境",
        "迁移=情境：来源法域→目标法域；保持=对象/测量/尺度/人口/时期",
    )
    errors = audit_output(context_migration, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"context migration was rejected: {errors}")

    noncanonical_region = context_migration.replace("迁移=情境", "迁移=地域")
    require_error(audit_output(noncanonical_region, VALID_RECEIPT), "桥接条件")

    multi_use_inference = conditional_inference.replace(
        "主用途 D1", "主用途 D1、U1"
    )
    require_error(audit_output(multi_use_inference, VALID_RECEIPT), "单一主用途")

    normative_premise = conditional_inference.replace(
        "命题类型=经验", "命题类型=规范立场"
    )
    require_error(audit_output(normative_premise, VALID_RECEIPT), "规范立场")

    valid_revision = evidence_output.replace(
        "消费者=D1；适配=D1:测量方法",
        "消费者=D1、R1；适配=D1:测量方法,R1:修订触发",
    ).replace(
        "本轮无 E/I 触发的认知修订。",
        "| 修订 ID | 快照 ID | 触发 E/I ID | 变化类型 | 认识状态与内容 | 下游影响 |\n"
        "|---|---|---|---|---|---|\n"
        "| R1 | E0 | E1 | 支持/升权 | E0：“候选：单一观察轴” → 本轮：“单一来源主张” | 认识影响=D1；认识状态=高不确定→较低不确定 |",
    )
    errors = audit_output(valid_revision, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"valid revision delta was rejected: {errors}")

    priority_as_object = valid_revision.replace(
        "单一来源主张",
        "街区优先级跨定义不同序",
    ).replace(
        "E0：“候选：单一观察轴” → 本轮：“街区优先级跨定义不同序”",
        "E0：“街区优先级可能变化” → 本轮：“街区优先级跨定义不同序”",
    )
    errors = audit_output(priority_as_object, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"descriptive priority object was rejected: {errors}")

    unanchored_revision = valid_revision.replace(
        "E0：“候选：单一观察轴” → 本轮：“单一来源主张”",
        "该候选得到支持并新增机制",
    )
    require_error(audit_output(unanchored_revision, VALID_RECEIPT), "E0 逐字差分")

    hidden_causal_revision = valid_revision.replace(
        "本轮：“单一来源主张”",
        "本轮：“该机制导致结果”",
    )
    require_error(
        audit_output(hidden_causal_revision, VALID_RECEIPT),
        "新增因果谓词",
    )

    compound_dimension = VALID_OUTPUT.replace(
        "D1 候选：单一观察轴", "D1 候选：观察轴与另一轴"
    )
    require_error(audit_output(compound_dimension, VALID_RECEIPT), "叶子单轴")

    alternative_dimension = VALID_OUTPUT.replace(
        "D1 候选：单一观察轴", "D1 候选：观察轴或另一轴"
    )
    require_error(audit_output(alternative_dimension, VALID_RECEIPT), "叶子单轴")

    slash_dimension = VALID_OUTPUT.replace(
        "D1 候选：单一观察轴", "D1 候选：观察轴/另一轴"
    )
    require_error(audit_output(slash_dimension, VALID_RECEIPT), "叶子单轴")

    numeric_sensitivity_dimension = VALID_OUTPUT.replace(
        "D1 候选：单一观察轴",
        "D1 候选：权重0.5/1/1.5倍扰动下名次重合率",
    ).replace(
        "[D1] 候选：单一观察轴",
        "[D1] 候选：权重0.5/1/1.5倍扰动下名次重合率",
    )
    errors = audit_output(numeric_sensitivity_dimension, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"numeric sensitivity set was rejected: {errors}")

    missing_dimension_spec = VALID_OUTPUT.replace(
        "；操作化=对象:目标对象,覆盖:目标总体→观测框/框外单列,行粒度:每对象每周期一行,成员键:object_id,采集:直接观测,缺失:标记未知,计算:单一结果,聚合:对象→决策单元,权重:无",
        "",
    )
    require_error(audit_output(missing_dimension_spec, VALID_RECEIPT), "操作化=")

    missing_operation_subkey = VALID_OUTPUT.replace(",缺失:标记未知", "")
    require_error(
        audit_output(missing_operation_subkey, VALID_RECEIPT),
        "缺失:",
    )

    missing_product_field = VALID_OUTPUT.replace("；字段=单一结果", "")
    require_error(
        audit_output(missing_product_field, VALID_RECEIPT),
        "字段=",
    )

    multi_gap_dimension = VALID_OUTPUT.replace(
        "| D1 候选：单一观察轴 | E0 未知 |",
        "| D1 候选：单一观察轴 | U1、C1 |",
    )
    require_error(audit_output(multi_gap_dimension, VALID_RECEIPT), "多个未闭合")

    standard_dimension_prefix = VALID_OUTPUT.replace(
        "D1 候选：单一观察轴", "D1 候选/假设：单一观察轴"
    ).replace(
        "[D1] 候选：单一观察轴", "[D1] 候选/假设：单一观察轴"
    )
    errors = audit_output(standard_dimension_prefix, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"standard D prefix was rejected: {errors}")

    compound_candidate = VALID_OUTPUT.replace(
        "| C1 | 产物=待取得数据v1；总体=目标对象；行粒度=每对象每周期一行；成员键=object_id；字段=单一结果；设计字段=无；窗口=固定周期；版本=规则v1 | D1 | 取得阻断=数据未取得 |",
        "| C1 | 产物=材料甲、材料乙；总体=目标对象；行粒度=每对象每周期一行；成员键=object_id；字段=单一结果；设计字段=无；窗口=固定周期；版本=规则v1 | D1、U1 | 取得阻断=数据未取得 |",
    )
    require_error(audit_output(compound_candidate, VALID_RECEIPT), "C1")

    compound_candidate_gap = VALID_OUTPUT.replace(
        "| C1 | 产物=待取得数据v1；总体=目标对象；行粒度=每对象每周期一行；成员键=object_id；字段=单一结果；设计字段=无；窗口=固定周期；版本=规则v1 | D1 | 取得阻断=数据未取得 |",
        "| C1 | 产物=待取得数据v1；总体=目标对象；行粒度=每对象每周期一行；成员键=object_id；字段=单一结果；设计字段=无；窗口=固定周期；版本=规则v1 | D1 | 版本阻断=未知；取得阻断=未取得 |",
    )
    require_error(
        audit_output(compound_candidate_gap, VALID_RECEIPT),
        "取得阻断",
    )

    multiple_dimension_consumers = VALID_OUTPUT.replace(
        "E0 未知",
        "C1",
        1,
    ).replace(
        "\n## C：候选线索",
        "\n| D2 候选：第二观察轴 | C1 | 价值/决定：选择 | 候选/假设：机制=第二机制；操作化=对象:目标对象,覆盖:目标总体→观测框/框外单列,行粒度:每对象每周期一行,成员键:object_id,采集:直接观测,缺失:标记未知,计算:单一结果,聚合:对象→决策单元,权重:无；操作数=单一结果；单位=类别；窗口=一次固定周期；参照=无；假设=无 | 价值/决定：约束下一证据 |\n\n## C：候选线索",
    )
    require_error(
        audit_output(multiple_dimension_consumers, VALID_RECEIPT),
        "多个 D 直接消费",
    )

    multiple_unknown_consumers = VALID_OUTPUT.replace(
        "\n## 所有权交接",
        "\n| U2 未知：命题=第二机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 仍未知 | 独立审计负责人 | C1 |\n\n## 所有权交接",
    )
    require_error(
        audit_output(multiple_unknown_consumers, VALID_RECEIPT),
        "多个 U 作为下一证据",
    )

    compound_unknown = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | C1 |",
        "| U1 未知：命题=机制甲、机制乙 | D1 不能晋级 | 团队甲＋团队乙 | C1、C2 |",
    )
    require_error(audit_output(compound_unknown, VALID_RECEIPT), "U1")

    slash_unknown = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | C1 |",
        "| U1 未知：命题=机制甲/机制乙 | D1 不能晋级 | 单一团队 | C1 |",
    )
    require_error(audit_output(slash_unknown, VALID_RECEIPT), "多个可独立未知")

    disjunctive_unknown = VALID_OUTPUT.replace(
        "U1 未知：命题=关键机制成立",
        "U1 未知：命题=机制甲或机制乙成立",
    )
    require_error(
        audit_output(disjunctive_unknown, VALID_RECEIPT),
        "多个可独立未知",
    )

    unconditioned_unknown_impact = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | C1 |",
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | 对象会被排除 | research-and-sourcing | C1 |",
    )
    require_error(
        audit_output(unconditioned_unknown_impact, VALID_RECEIPT),
        "显式条件化",
    )

    rights_prefixed_condition = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 |",
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | 权利约束=具体约束；若U1成立，则对象会被排除 |",
    )
    errors = audit_output(rights_prefixed_condition, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"prefixed U condition was rejected: {errors}")

    ambiguous_unknown_polarity = VALID_OUTPUT.replace(
        "U1 未知：命题=关键机制成立",
        "U1 未知：命题=关键机制是否成立",
    )
    require_error(
        audit_output(ambiguous_unknown_polarity, VALID_RECEIPT),
        "隐藏命题极性",
    )

    false_conflict_stop = VALID_OUTPUT.replace(
        "CE-EVIDENCE-GAP",
        "CE-CONFLICT-UNRESOLVED",
    )
    require_error(
        audit_output(false_conflict_stop, VALID_RECEIPT),
        "缺少规范 U# 冲突",
    )

    compound_owner = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | C1 |",
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | 无障碍与交通审计负责人 | C1 |",
    )
    errors = audit_output(compound_owner, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"single compound owner was rejected: {errors}")

    multiple_owners = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | C1 |",
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | 甲负责人、乙负责人 | C1 |",
    )
    require_error(audit_output(multiple_owners, VALID_RECEIPT), "只有一个所有者")

    valid_unknown_summary = VALID_OUTPUT.replace(
        "[D1] 候选：单一观察轴",
        "[U1] 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立",
    )
    errors = audit_output(valid_unknown_summary, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"U summary without duplicated ID was rejected: {errors}")

    duplicated_unknown_id = valid_unknown_summary.replace(
        "[U1] 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立",
        "[U1] U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立",
    )
    require_error(audit_output(duplicated_unknown_id, VALID_RECEIPT), "地图摘要")

    negated_verified = VALID_OUTPUT.replace(
        "## 框定与动作\n\n",
        "## 框定与动作\n\n候选/假设：该结构不是已核实公式。\n\n",
    )
    errors = audit_output(negated_verified, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"negated verification boundary was rejected: {errors}")

    positive_verified = VALID_OUTPUT.replace(
        "## 框定与动作\n\n",
        "## 框定与动作\n\n状态=已核实。\n\n",
    )
    require_error(audit_output(positive_verified, VALID_RECEIPT), "非闭集认识状态")

    figure_locator = evidence_output.replace(
        "E门=开放（正文第1节）", "E门=开放（图2）"
    )
    errors = audit_output(figure_locator, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"figure locator was rejected: {errors}")

    missing_literal_key = evidence_output.replace("；消费者=D1", "；消费者 D1")
    require_error(audit_output(missing_literal_key, VALID_RECEIPT), "消费者=")

    professional_review_gap = VALID_OUTPUT.replace(
        "决策就绪：否（CE-EVIDENCE-GAP）",
        "决策就绪：否（CE-EVIDENCE-GAP；CE-PROFESSIONAL-REVIEW）",
    )
    require_error(
        audit_output(professional_review_gap, VALID_RECEIPT),
        "合格专业复核",
    )

    valid_professional_review = VALID_OUTPUT.replace(
        "## 框定与动作\n\n",
        "## 框定与动作\n\n"
        "输入门：状态=充分；关键缺口=无；设计占位=无；影响=无。\n\n"
        "| 设计 ID | 单一设计参数 | 状态与值 | 权威/依据 | 下游作用域 | 改变时的影响 |\n"
        "|---|---|---|---|---|---|\n"
        "| P1 | 目标总体 | 已给输入=目标对象 | 用户输入 | A1 | 改变效果与采用分母 |\n"
        "| P2 | 目标时窗 | 已给输入=固定周期 | 用户输入 | A1 | 改变结果归因窗口 |\n"
        "| P3 | 最低保障 | 价值决定=法定授权主体 | 授权待定 | A1.H | 改变权利约束 |\n"
        "| P4 | 容量上限 | 已给输入=100服务单位/固定周期 | 测试输入 | A1.K | 改变可交付总量 |\n\n"
        "| 构念 ID | 对象 | 测量 | 尺度/聚合 | 总体 | 时期 | 情境 | 比较/基准 | 决策用途 | 状态/依据 |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
        "| K1 | 行动结果 | 单一结果 | 对象级不聚合 | 目标对象 | 固定周期 | 本地服务 | 未提供行动 | 估计行动效果 | 候选/假设 |\n"
        "| K2 | 基线需要 | 观察轴 | 决策单元均值 | 目标对象 | 固定周期前 | 本地服务 | 不适用（描述性） | 描述需要 | 候选/假设 |\n\n"
        "| 决策行动 | 目标总体与结果 | 效果/增益 | 采用/可达 | 容量/成本 | 替代/伤害/权利 |\n"
        "|---|---|---|---|---|---|\n"
        "| A1 候选/假设：单一行动 | 总体=目标对象；成员键=object_id；结果=单一结果；时窗=固定周期；构念=K1；设计依据=P1,P2 | A1.E；状态=未知；总体=目标对象；分配/暴露=offer_assignment；比较项=未提供行动；结果=单一结果；时窗=固定周期；效应量=风险差；识别=预注册比较设计待取得；所需字段=object_id,offer_assignment,outcome_value；来源位置=因果研究/本地评估；依据=P1,P2；下一=C2 | A1.F；状态=候选；漏斗=资格→触达→接受→交付→实际获益；关键转移=接受→交付；分母=已接受者；失败=交付失败；所需字段=eligible,notified,accepted,delivered,benefited；来源位置=受影响者/一线；依据=P1；下一=P1 | A1.K；状态=未知；交付单位=获益对象次；固定资源=人员时和预算；瓶颈=交付班次；总上限=100服务单位/固定周期:P4；成本分母=货币/获益对象次；时窗=固定周期；所需字段=delivered,staff_hours,total_cost；来源位置=运营/财政；依据=P2,P4；下一=专业复核 | A1.H；状态=未知；比较项=不行动；受影响总体=观察框外目标对象；主机制=资格漏捕；原子后果=失去服务机会；风险扫描=直接:资格漏捕→被拒服务,替代:资源改投→挤占其他服务,挤出:预算转移→减少其他项目,反馈:负面标签→降低申请；权利状态=价值决定:P3；候选保障=P3；所需字段=eligibility,frame_status,denial_reason；来源位置=受影响者/独立权利/规则制定；依据=P3；下一=P3 |\n\n"
        "| 遗漏 ID | 关联行动与观察框 | 候选遗漏总体 | 漏捕机制 | 后果与权利状态 | 所有者 | 下一项 |\n"
        "|---|---|---|---|---|---|---|\n"
        "| G1 | A1；观察框=登记名册 | 未登记目标对象 | 机制=名册外漏捕；判定字段=frame_status,eligibility | 后果=失去行动接触机会；权利状态=价值决定:P3 | 服务公平审计负责人 | C1 |\n\n",
    ).replace(
        "价值/决定：约束下一证据",
        "价值/决定：行动=A1；用途=约束下一证据",
    ).replace(
        "| C1 | 产物=待取得数据v1；总体=目标对象；行粒度=每对象每周期一行；成员键=object_id；字段=单一结果；设计字段=无；窗口=固定周期；版本=规则v1 | D1 | 取得阻断=数据未取得 |",
        "| C1 | 产物=待取得数据v1；总体=目标对象；行粒度=每对象每周期一行；成员键=object_id；字段=单一结果,frame_status,eligibility；设计字段=无；窗口=固定周期；版本=规则v1 | D1 | 取得阻断=数据未取得 |\n"
        "| C2 | 产物=行动效果估计包v1；总体=目标对象；行粒度=每对象每分配一行；成员键=object_id；字段=object_id,outcome_value；设计字段=offer_assignment；窗口=固定周期；版本=分析规则v1 | A1.E | 取得阻断=本地比较数据未取得 |",
    ).replace(
        "| C1 取证 | research-and-sourcing | 约束 D1 |",
        "| C1 取证 | research-and-sourcing | 约束 D1 |\n"
        "| 合格专业复核 | 主责专业=因果推断方法负责人 | 复核域=效果识别:A1.E；复核产物=effect-eval-v1可复算报告；验收口径=预注册效应估计覆盖率大于95%；算法/阈值=分析计划v1；依据快照=数据v1/规则v1；独立性=与生产者分离并披露冲突；通过证据=待取得:独立复算日志 |\n"
        "| 合格专业复核 | 主责专业=服务运营与成本会计负责人 | 复核域=运营容量成本:A1.K；复核产物=capacity-cost-v1台账；验收口径=资源总量对账差异小于1%；算法/阈值=成本归集规则v1；依据快照=运营台账v1/预算v1；独立性=与服务排班者分离并披露冲突；通过证据=待取得:总量对账记录 |\n"
        "| 合格专业复核 | 主责专业=行政法与公平影响审计负责人 | 复核域=权利法域遗漏:A1.H；复核产物=rights-gap-v1审计；验收口径=全部拒绝路径具名法源与申诉入口；算法/阈值=待P3:权利判定规则v1；依据快照=规则v1/法域快照v1；独立性=与资源授权者分离并披露冲突；通过证据=待取得:逐路径审计记录 |",
    ).replace(
        "最高价值下一证据：C1。",
        "最高价值下一项：类型=证据；目标=C2；选择依据=先闭合A1.E。",
    ).replace(
        "决策就绪：否（CE-EVIDENCE-GAP）",
        "决策就绪：否（CE-EVIDENCE-GAP；CE-PROFESSIONAL-REVIEW）",
    ).replace(
        "重新开启条件：取得 C1。",
        "重新开启条件：取得 C2。不得据此直接实施。",
    )
    errors = audit_output(valid_professional_review, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"valid professional handoff was rejected: {errors}")

    missing_input_gate = valid_professional_review.replace(
        "输入门：状态=充分；关键缺口=无；设计占位=无；影响=无。\n\n",
        "",
    )
    require_error(audit_output(missing_input_gate, VALID_RECEIPT), "输入门")

    missing_design_ledger = valid_professional_review.replace(
        "| 设计 ID | 单一设计参数 | 状态与值 | 权威/依据 | 下游作用域 | 改变时的影响 |\n"
        "|---|---|---|---|---|---|\n"
        "| P1 | 目标总体 | 已给输入=目标对象 | 用户输入 | A1 | 改变效果与采用分母 |\n"
        "| P2 | 目标时窗 | 已给输入=固定周期 | 用户输入 | A1 | 改变结果归因窗口 |\n"
        "| P3 | 最低保障 | 价值决定=法定授权主体 | 授权待定 | A1.H | 改变权利约束 |\n"
        "| P4 | 容量上限 | 已给输入=100服务单位/固定周期 | 测试输入 | A1.K | 改变可交付总量 |\n\n",
        "",
    )
    require_error(
        audit_output(missing_design_ledger, VALID_RECEIPT),
        "P 设计来源账本",
    )

    indistinguishable_constructs = valid_professional_review.replace(
        "| K2 | 基线需要 | 观察轴 | 决策单元均值 | 目标对象 | 固定周期前 | 本地服务 | 不适用（描述性） | 描述需要 | 候选/假设 |",
        "| K2 | 行动结果 | 单一结果 | 对象级不聚合 | 目标对象 | 固定周期 | 本地服务 | 未提供行动 | 估计行动效果 | 候选/假设 |",
    )
    require_error(
        audit_output(indistinguishable_constructs, VALID_RECEIPT),
        "完全相同",
    )

    mismatched_construct_comparator = valid_professional_review.replace(
        "比较项=未提供行动；结果=单一结果",
        "比较项=另一行动；结果=单一结果",
    )
    require_error(
        audit_output(mismatched_construct_comparator, VALID_RECEIPT),
        "比较项与构念 K1 不一致",
    )

    unlisted_open_design = valid_professional_review.replace(
        "输入门：状态=充分；关键缺口=无；设计占位=无；影响=无。",
        "输入门：状态=缺口；关键缺口=法域保障未定；设计占位=P2；影响=A1.H。",
    ).replace(
        "| P3 | 最低保障 | 价值决定=法定授权主体 |",
        "| P3 | 最低保障 | 未知=法域保障规则 |",
    ).replace(
        "CE-EVIDENCE-GAP；CE-PROFESSIONAL-REVIEW",
        "CE-INPUT-GAP；CE-EVIDENCE-GAP；CE-PROFESSIONAL-REVIEW",
    )
    require_error(
        audit_output(unlisted_open_design, VALID_RECEIPT),
        "未列全开放 P#",
    )

    malformed_unknown_design = valid_professional_review.replace(
        "价值决定=法定授权主体",
        "未知=待法域确认",
    ).replace(
        "输入门：状态=充分；关键缺口=无；设计占位=无；影响=无。",
        "输入门：状态=缺口；关键缺口=法域；设计占位=P3；影响=A1.H。",
    ).replace(
        "CE-EVIDENCE-GAP；CE-PROFESSIONAL-REVIEW",
        "CE-INPUT-GAP；CE-EVIDENCE-GAP；CE-PROFESSIONAL-REVIEW",
    )
    require_error(
        audit_output(malformed_unknown_design, VALID_RECEIPT),
        "单一 U#",
    )

    unauthorized_shared_design = valid_professional_review.replace(
        "| P1 | 目标总体 | 已给输入=目标对象 | 用户输入 | A1 |",
        "| P1 | 行动资格 | 已给输入=目标对象 | 无 | A1,A2 |",
    )
    require_error(
        audit_output(unauthorized_shared_design, VALID_RECEIPT),
        "跨行动共享设计",
    )

    mismatched_effect_population = valid_professional_review.replace(
        "A1.E；状态=未知；总体=目标对象",
        "A1.E；状态=未知；总体=另一总体",
    )
    require_error(
        audit_output(mismatched_effect_population, VALID_RECEIPT),
        "总体与目标格不一致",
    )

    truncated_funnel = valid_professional_review.replace(
        "漏斗=资格→触达→接受→交付→实际获益；关键转移=接受→交付",
        "漏斗=触达→实际获益；关键转移=触达→实际获益",
    )
    require_error(
        audit_output(truncated_funnel, VALID_RECEIPT),
        "少于五个阶段",
    )

    missing_capacity_cap = valid_professional_review.replace(
        "；总上限=100服务单位/固定周期:P4",
        "",
    )
    require_error(
        audit_output(missing_capacity_cap, VALID_RECEIPT),
        "总上限=",
    )

    bare_unknown_capacity = valid_professional_review.replace(
        "总上限=100服务单位/固定周期:P4",
        "总上限=未知",
    )
    require_error(
        audit_output(bare_unknown_capacity, VALID_RECEIPT),
        "总上限不得裸写",
    )

    compound_action_result = valid_professional_review.replace(
        "结果=单一结果；时窗=固定周期",
        "结果=结果甲或结果乙；时窗=固定周期",
    )
    require_error(
        audit_output(compound_action_result, VALID_RECEIPT),
        "原子结果",
    )

    missing_substitution_scan = valid_professional_review.replace(
        "替代:资源改投→挤占其他服务,",
        "",
    )
    require_error(
        audit_output(missing_substitution_scan, VALID_RECEIPT),
        "替代:",
    )

    result_only_harm_scan = valid_professional_review.replace(
        "直接:资格漏捕→被拒服务",
        "直接:被拒服务",
    )
    require_error(
        audit_output(result_only_harm_scan, VALID_RECEIPT),
        "机制→后果",
    )

    inherited_action_scope = valid_professional_review.replace(
        "总体=目标对象；成员键=object_id；结果=单一结果；时窗=固定周期；构念=K1；设计依据=P1,P2",
        "总体=目标对象；成员键=object_id；结果=单一结果；时窗同上；构念=K1；设计依据=P1,P2",
    )
    require_error(
        audit_output(inherited_action_scope, VALID_RECEIPT),
        "目标格缺少",
    )

    missing_boundary = valid_professional_review.replace(
        "| 遗漏 ID | 关联行动与观察框 | 候选遗漏总体 | 漏捕机制 | 后果与权利状态 | 所有者 | 下一项 |\n"
        "|---|---|---|---|---|---|---|\n"
        "| G1 | A1；观察框=登记名册 | 未登记目标对象 | 机制=名册外漏捕；判定字段=frame_status,eligibility | 后果=失去行动接触机会；权利状态=价值决定:P3 | 服务公平审计负责人 | C1 |\n\n",
        "",
    )
    require_error(audit_output(missing_boundary, VALID_RECEIPT), "G 遗漏边界")

    boundary_field_mismatch = valid_professional_review.replace(
        "字段=单一结果,frame_status,eligibility；设计字段=无",
        "字段=单一结果；设计字段=无",
    )
    require_error(
        audit_output(boundary_field_mismatch, VALID_RECEIPT),
        "G 边界判定字段",
    )

    ritual_review = valid_professional_review.replace(
        "；算法/阈值=分析计划v1",
        "",
        1,
    )
    require_error(audit_output(ritual_review, VALID_RECEIPT), "算法/阈值")

    threshold_free_review = valid_professional_review.replace(
        "验收口径=预注册效应估计覆盖率大于95%",
        "验收口径=预注册效应估计及置信区间",
    )
    require_error(
        audit_output(threshold_free_review, VALID_RECEIPT),
        "缺少可观测阈值",
    )

    unversioned_review_product = valid_professional_review.replace(
        "复核产物=effect-eval-v1可复算报告",
        "复核产物=版本化效果评估报告",
    )
    require_error(
        audit_output(unversioned_review_product, VALID_RECEIPT),
        "产物缺少可识别版本",
    )

    generic_review_snapshot = valid_professional_review.replace(
        "依据快照=数据v1/规则v1",
        "依据快照=数据与方案版本",
    )
    require_error(
        audit_output(generic_review_snapshot, VALID_RECEIPT),
        "依据快照缺少冻结版本",
    )

    bare_design_as_algorithm = valid_professional_review.replace(
        "算法/阈值=待P3:权利判定规则v1",
        "算法/阈值=P3",
    )
    require_error(
        audit_output(bare_design_as_algorithm, VALID_RECEIPT),
        "不是具名规则",
    )

    unreasoned_next = valid_professional_review.replace(
        "；选择依据=先闭合A1.E",
        "",
    )
    require_error(audit_output(unreasoned_next, VALID_RECEIPT), "选择依据")

    versioned_input_next = valid_professional_review.replace(
        "最高价值下一项：类型=证据；目标=C2；选择依据=先闭合A1.E。",
        "最高价值下一项：类型=输入；目标=P3；产物=法域保障规则v1；"
        "所需字段=适用法域,最低保障,申诉入口；选择依据=先闭合A1.H。",
    )
    errors = audit_output(versioned_input_next, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"versioned input handoff was rejected: {errors}")

    mixed_design_input = versioned_input_next.replace(
        "适用法域,最低保障,申诉入口",
        "适用法域,最低保障,目标时窗,申诉入口",
    )
    require_error(
        audit_output(mixed_design_input, VALID_RECEIPT),
        "混入其他 P 参数",
    )

    bundled_input_rationale = versioned_input_next.replace(
        "选择依据=先闭合A1.H",
        "选择依据=先闭合A1.H,A1.K",
    )
    require_error(
        audit_output(bundled_input_rationale, VALID_RECEIPT),
        "只绑定一个 A# 分面",
    )

    unbound_action_impact = valid_professional_review.replace(
        "价值/决定：行动=A1；用途=约束下一证据",
        "价值/决定：约束下一证据",
    )
    require_error(audit_output(unbound_action_impact, VALID_RECEIPT), "行动=A#")

    incomplete_effect_product = valid_professional_review.replace(
        "字段=object_id,outcome_value；设计字段=offer_assignment",
        "字段=object_id；设计字段=offer_assignment",
    )
    require_error(
        audit_output(incomplete_effect_product, VALID_RECEIPT),
        "未覆盖 A1.E 所需字段",
    )

    aliased_effect_population = valid_professional_review.replace(
        "产物=行动效果估计包v1；总体=目标对象",
        "产物=行动效果估计包v1；总体=A1总体",
    )
    require_error(
        audit_output(aliased_effect_population, VALID_RECEIPT),
        "行动别名",
    )

    mismatched_effect_member_key = valid_professional_review.replace(
        "产物=行动效果估计包v1；总体=目标对象；行粒度=每对象每分配一行；成员键=object_id",
        "产物=行动效果估计包v1；总体=目标对象；行粒度=每对象每分配一行；成员键=other_id",
    )
    require_error(
        audit_output(mismatched_effect_member_key, VALID_RECEIPT),
        "成员键与 A1.E 不一致",
    )

    misadapted_effect_evidence = valid_professional_review.replace(
        "；依据=P1,P2；下一=C2",
        "；依据=P1,P2,E1；下一=C2",
        1,
    ).replace(
        "本轮无已辨明材料；不得授 E。",
        "| 来源 ID | 材料类型与规范入口/全文 | 发布、版本与访问 | 生产目的、受众与获取门槛 | 上游依赖与缺席声音 |\n"
        "|---|---|---|---|---|\n"
        "| S1 | 规范入口与正文 | 发布：2026；版本：v1；访问：2026-07-17 正文第1节；E门=开放（正文第1节） | 研究材料 | 无 |",
    ).replace(
        "本轮无 EVIDENCE-COMMIT。",
        "| 证据 ID | 来源 ID | 原子来源主张 | 主张相关时期/版本 | 状态、新鲜度与边界 |\n"
        "|---|---|---|---|---|\n"
        "| E1 | S1 | 行动组与比较组结果不同 | 2026/v1 | 来源主张 E1；原子类型=单命题；命题类型=经验；生产位置=研究；支持位置=正文第1节；消费者=A1.E；适配=A1.E:容量成本；统计口径=组间比较；新鲜度=当前；边界=单一研究 |",
    )
    require_error(
        audit_output(misadapted_effect_evidence, VALID_RECEIPT),
        "必须使用适配角色 因果效果",
    )

    unmigrated_effect_evidence = misadapted_effect_evidence.replace(
        "适配=A1.E:容量成本",
        "适配=A1.E:因果效果",
    ).replace(
        "边界=单一研究",
        "边界=异地研究不可直接迁移",
    )
    require_error(
        audit_output(unmigrated_effect_evidence, VALID_RECEIPT),
        "迁移缺口却直接支持行动分面",
    )

    linked_dimension = VALID_OUTPUT.replace("E0 未知", "C1", 1)
    errors = audit_output(linked_dimension, VALID_RECEIPT)
    if errors:
        raise AssertionError(f"linked D/C operands were rejected: {errors}")

    missing_operand = linked_dimension.replace("字段=单一结果", "字段=其他结果")
    require_error(audit_output(missing_operand, VALID_RECEIPT), "未覆盖操作数")

    missing_frame_coverage = VALID_OUTPUT.replace(
        ",覆盖:目标总体→观测框/框外单列",
        "",
    )
    require_error(audit_output(missing_frame_coverage, VALID_RECEIPT), "覆盖:")

    unvalidated_proxy = VALID_OUTPUT.replace("机制=关键机制", "机制=代理机制")
    require_error(audit_output(unvalidated_proxy, VALID_RECEIPT), "代理量")

    wrong_support_position = evidence_output.replace(
        "支持位置=正文第1节",
        "支持位置=正文第2节",
    )
    require_error(audit_output(wrong_support_position, VALID_RECEIPT), "支持位置")

    compound_source_claim = evidence_output.replace(
        "单一来源主张",
        "来源主张甲或来源主张乙",
    )
    require_error(audit_output(compound_source_claim, VALID_RECEIPT), "第二谓词")

    missing_statistic_basis = evidence_output.replace(
        "；统计口径=不适用（非汇总）",
        "",
    )
    require_error(audit_output(missing_statistic_basis, VALID_RECEIPT), "统计口径=")

    hidden_second_migration = conditional_inference.replace(
        "保持=对象/测量/尺度/时期/情境",
        "保持=对象/测量/尺度/时期",
    )
    require_error(audit_output(hidden_second_migration, VALID_RECEIPT), "其余五项")

    missing_unknown_criterion = VALID_OUTPUT.replace(
        "；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立",
        "",
    )
    require_error(audit_output(missing_unknown_criterion, VALID_RECEIPT), "判定口径")

    noncandidate_unknown_evidence = VALID_OUTPUT.replace(
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | C1 |",
        "| U1 未知：命题=关键机制成立；判定口径=对象:目标对象,观测量:单一结果,窗口:固定周期,阈值/方向:结果成立 | D1 不能晋级 | research-and-sourcing | 现场审计 |",
    )
    require_error(audit_output(noncandidate_unknown_evidence, VALID_RECEIPT), "单一 C#")

    unknown_observation_field_gap = VALID_OUTPUT.replace(
        "观测量:单一结果",
        "观测量:另一观测量",
    )
    require_error(
        audit_output(unknown_observation_field_gap, VALID_RECEIPT),
        "未覆盖 U1 观测量",
    )

    challenge_without_candidate = VALID_OUTPUT.replace("| C1、U1 | 未区分 |", "| U1 | 未区分 |")
    require_error(audit_output(challenge_without_candidate, VALID_RECEIPT), "区分 C#")

    unstable_challenge_id = VALID_OUTPUT.replace("| CH1 | D1 |", "| T1 | D1 |")
    require_error(
        audit_output(unstable_challenge_id, VALID_RECEIPT),
        "稳定 CH#",
    )

    challenge_field_gap = VALID_OUTPUT.replace(
        "所需字段=单一结果",
        "所需字段=单一结果,分组标签",
    )
    require_error(audit_output(challenge_field_gap, VALID_RECEIPT), "未覆盖所需字段")

    single_family_inference = conditional_inference.replace(
        "| U1、C1 | 推断 I1；主用途 D1 |",
        "| 同一来源家族 | 推断 I1；主用途 D1 |",
    )
    require_error(
        audit_output(single_family_inference, VALID_RECEIPT),
        "CE-EVIDENCE-GAP",
    )

    missing_migration_signature = conditional_inference.replace(
        "；迁移=人口：来源总体→目标总体；保持=对象/测量/尺度/时期/情境",
        "",
    )
    require_error(
        audit_output(missing_migration_signature, VALID_RECEIPT),
        "桥接条件",
    )

    missing_revision_impact_key = valid_revision.replace("认识影响=", "")
    require_error(
        audit_output(missing_revision_impact_key, VALID_RECEIPT),
        "认识影响=",
    )

    logical_challenge = undeclared_consumer.replace(
        "| CH1 | D1 |", "| CH1 | I1 |"
    )
    require_error(
        audit_output(logical_challenge, VALID_RECEIPT),
        "逻辑桥 I",
    )

    extra_dimensions = "\n".join(
        f"| D{index} 候选：轴{index} | E0 未知 | 价值/决定：选择 | "
        f"候选/假设：独立轴{index} | 价值/决定：用途{index} |"
        for index in range(2, 10)
    )
    too_many_dimensions = VALID_OUTPUT.replace(
        "| D1 候选：单一观察轴 | E0 未知 | 价值/决定：选择 | 候选/假设：机制=关键机制；操作化=对象:目标对象,覆盖:目标总体→观测框/框外单列,行粒度:每对象每周期一行,成员键:object_id,采集:直接观测,缺失:标记未知,计算:单一结果,聚合:对象→决策单元,权重:无；操作数=单一结果；单位=类别；窗口=一次固定周期；参照=无；假设=无 | 价值/决定：约束下一证据 |",
        "| D1 候选：单一观察轴 | E0 未知 | 价值/决定：选择 | 候选/假设：机制=关键机制；操作化=对象:目标对象,覆盖:目标总体→观测框/框外单列,行粒度:每对象每周期一行,成员键:object_id,采集:直接观测,缺失:标记未知,计算:单一结果,聚合:对象→决策单元,权重:无；操作数=单一结果；单位=类别；窗口=一次固定周期；参照=无；假设=无 | 价值/决定：约束下一证据 |\n"
        + extra_dimensions,
    )
    require_error(audit_output(too_many_dimensions, VALID_RECEIPT), "行上限")

    print("Cognitive-expansion output auditor tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
