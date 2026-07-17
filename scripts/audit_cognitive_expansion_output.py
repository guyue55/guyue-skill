#!/usr/bin/env python3
"""Mechanically audit a strict high-risk cognitive-expansion Markdown artifact."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SECTION_ORDER = (
    "## PRE-EVIDENCE-SNAPSHOT E0",
    "## B0 PRE-TOOL 预算账本",
    "## 框定与动作",
    "## D：维度取舍",
    "## C：候选线索",
    "## S：材料登记",
    "## E：原子来源主张",
    "## I：有界推断",
    "## R：真实认知修订",
    "## 挑战记录",
    "## U：冲突与未知",
    "## 所有权交接",
    "## 地图摘要",
    "## B1 FINAL 与停止",
)

BUDGET_RESOURCES = (
    "最大轮数",
    "墙钟时间",
    "近似有效 Token",
    "只读工具调用",
    "材料打开",
    "可见输出",
    "授权子任务",
    "付费成本",
)

TABLE_HEADERS = {
    "## B0 PRE-TOOL 预算账本": (
        "| 资源 | 硬上限 | 起始消耗 | 安全预留 | 状态 | 测量依据 |"
    ),
    "## 框定与动作": "| 认知动作 | 选择理由 | 预期地图变化 |",
    "## D：维度取舍": (
        "| 候选维度 | 谱系锚点 | 处理 | 理由 | 对决定的影响 |"
    ),
    "## C：候选线索": (
        "| 候选 ID | 线索/预期材料 | 预期约束的 A/D/I/U | 身份、访问或版本缺口 |"
    ),
    "## S：材料登记": (
        "| 来源 ID | 材料类型与规范入口/全文 | 发布、版本与访问 | 生产目的、受众与获取门槛 | 上游依赖与缺席声音 |"
    ),
    "## E：原子来源主张": (
        "| 证据 ID | 来源 ID | 原子来源主张 | 主张相关时期/版本 | 状态、新鲜度与边界 |"
    ),
    "## I：有界推断": (
        "| 推断 ID | 来源前提 E | 桥接条件 | 有界结论 | 共享依赖与缺席位置 | 状态与下游用途 |"
    ),
    "## R：真实认知修订": (
        "| 修订 ID | 快照 ID | 触发 E/I ID | 变化类型 | 认识状态与内容 | 下游影响 |"
    ),
    "## 挑战记录": (
        "| 挑战 ID | 主解释 ID | 竞争解释 | 区分证据 C/E/U | 结果 | 地图影响 |"
    ),
    "## U：冲突与未知": "| 冲突或未知 | 下游影响 | 所有者 | 下一证据 |",
    "## 所有权交接": "| 结果片段 | 所有者 | 本地图如何使用 |",
    "## B1 FINAL 与停止": (
        "| 资源 | 硬上限 | 实际消耗 | 状态 | 测量依据 |"
    ),
}

ROW_LIMITS = {
    "## D：维度取舍": ("D", 8),
    "## C：候选线索": ("C", 8),
    "## S：材料登记": ("S", 6),
    "## E：原子来源主张": ("E", 10),
    "## I：有界推断": ("I", 4),
    "## R：真实认知修订": ("R", 4),
    "## 挑战记录": ("CH", 3),
    "## U：冲突与未知": ("U", 6),
    "## 所有权交接": (None, 8),
}

ID_RANGE_RE = re.compile(
    r"(?:CH|[CDEIRU])\d+\s*[–—-]\s*(?:(?:CH|[CDEIRU])\s*)?\d+"
)
NORMATIVE_RE = re.compile(
    r"应该|应当|必须|不得|应优先|应采用|应使用|应将|应由|应予|应纳入|应排除"
)
ROLE_HEAD = r"负责人|主管|主任|经理|专员|顾问|专家|工程师|分析师|律师|医师|研究员"
ACTION_HEADER = (
    "决策行动",
    "目标总体与结果",
    "效果/增益",
    "采用/可达",
    "容量/成本",
    "替代/伤害/权利",
)
DESIGN_HEADER = (
    "设计 ID",
    "单一设计参数",
    "状态与值",
    "权威/依据",
    "下游作用域",
    "改变时的影响",
)
CONSTRUCT_HEADER = (
    "构念 ID",
    "对象",
    "测量",
    "尺度/聚合",
    "总体",
    "时期",
    "情境",
    "比较/基准",
    "决策用途",
    "状态/依据",
)
BOUNDARY_HEADER = (
    "遗漏 ID",
    "关联行动与观察框",
    "候选遗漏总体",
    "漏捕机制",
    "后果与权利状态",
    "所有者",
    "下一项",
)
ACTION_FACETS = ("E", "F", "K", "H")
ACTION_FACET_RE = re.compile(r"(?<![A-Za-z0-9])A\d+\.[EFKH](?![A-Za-z0-9])")
EVIDENCE_ROLES = {
    "定义边界",
    "测量方法",
    "机制",
    "因果效果",
    "采用失败",
    "容量成本",
    "伤害权利",
    "迁移约束",
    "反证",
    "修订触发",
}
INFERENCE_INVARIANTS = {"对象", "测量", "尺度", "人口", "时期", "情境"}
CONSUMER_ID_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:A\d+\.[EFKH]|[DIKPRU]\d+)(?![A-Za-z0-9])"
)


def section_text(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    match = re.search(r"^## ", text[start + len(heading) :], re.MULTILINE)
    end = start + len(heading) + match.start() if match else len(text)
    return text[start:end]


def table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def normalized_header_cell(value: str) -> str:
    """Ignore cosmetic Markdown whitespace inside a header label."""
    return re.sub(r"\s+", "", value)


def rows_for_header(section: str, header: tuple[str, ...]) -> list[list[str]]:
    """Return one Markdown table identified by semantic header cells."""
    lines = section.splitlines()
    normalized_header = tuple(normalized_header_cell(cell) for cell in header)
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        if tuple(normalized_header_cell(cell) for cell in cells) != normalized_header:
            continue
        rows = [list(cells)]
        for candidate in lines[index + 1 :]:
            candidate = candidate.strip()
            if not candidate.startswith("|") or not candidate.endswith("|"):
                if rows:
                    break
                continue
            parsed = [cell.strip() for cell in candidate.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in parsed):
                continue
            rows.append(parsed)
        return rows
    return []


def keyed_value(text: str, key: str) -> str:
    match = re.search(rf"(?:^|[；|]){re.escape(key)}=([^；|]+)", text)
    return match.group(1).strip().strip("<>") if match else ""


def field_items(value: str) -> set[str]:
    return {
        item.strip().strip("<>")
        for item in re.split(r"[,，、]", value)
        if item.strip().strip("<>")
    }


def parse_quantity(value: str) -> float | None:
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([kK万]?)", value)
    if not match:
        return None
    number = float(match.group(1))
    suffix = match.group(2)
    if suffix in {"k", "K"}:
        number *= 1_000
    elif suffix == "万":
        number *= 10_000
    return number


def budget_rows(text: str, heading: str) -> dict[str, list[str]]:
    rows = table_rows(section_text(text, heading))
    return {
        row[0]: row
        for row in rows[1:]
        if len(row) >= 2 and row[0] in BUDGET_RESOURCES
    }


def require_receipt_number(
    receipt: dict[str, Any], key: str, errors: list[str]
) -> float | None:
    value = receipt.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"运行后收据缺少数值字段 {key}")
        return None
    return float(value)


def compare_cap(
    name: str,
    actual: float | None,
    cap_text: str,
    errors: list[str],
    *,
    multiplier: float = 1.0,
) -> None:
    cap = parse_quantity(cap_text)
    if cap is None:
        errors.append(f"{name} 的硬上限不可解析: {cap_text}")
        return
    if actual is not None and actual > cap * multiplier:
        errors.append(f"{name} 超过硬上限: actual={actual:g}, cap={cap * multiplier:g}")


def audit_receipt(
    rows: dict[str, list[str]], receipt: dict[str, Any], errors: list[str]
) -> None:
    input_tokens = require_receipt_number(receipt, "input_tokens", errors)
    cached_tokens = require_receipt_number(
        receipt, "cached_input_tokens", errors
    )
    output_tokens = require_receipt_number(receipt, "output_tokens", errors)
    reasoning_tokens = require_receipt_number(
        receipt, "reasoning_output_tokens", errors
    )
    if None not in (input_tokens, cached_tokens, output_tokens):
        effective = max(input_tokens - cached_tokens, 0) + output_tokens
        if "近似有效 Token" in rows:
            compare_cap(
                "有效 Token",
                effective,
                rows["近似有效 Token"][1],
                errors,
            )
    if (
        output_tokens is not None
        and reasoning_tokens is not None
        and "可见输出" in rows
    ):
        visible = max(output_tokens - reasoning_tokens, 0)
        compare_cap("可见输出", visible, rows["可见输出"][1], errors)

    comparisons = (
        ("最大轮数", "rounds", 1.0),
        ("墙钟时间", "wall_clock_seconds", 60.0),
        ("只读工具调用", "read_only_tool_calls", 1.0),
        ("材料打开", "materials_opened", 1.0),
        ("授权子任务", "authorized_subtasks", 1.0),
        ("付费成本", "paid_cost", 1.0),
    )
    for resource, receipt_key, multiplier in comparisons:
        actual = require_receipt_number(receipt, receipt_key, errors)
        if resource in rows:
            compare_cap(
                resource,
                actual,
                rows[resource][1],
                errors,
                multiplier=multiplier,
            )


def audit_output(text: str, receipt: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    high_risk = "CE-PROFESSIONAL-REVIEW" in text
    level_two = re.findall(r"^## .+$", text, re.MULTILINE)
    positions: list[int] = []
    for heading in SECTION_ORDER:
        try:
            position = level_two.index(heading)
        except ValueError:
            position = -1
            errors.append(f"缺少精确 H2 区块: {heading}")
        positions.append(position)
    present_positions = [position for position in positions if position >= 0]
    if present_positions != sorted(present_positions):
        errors.append("终稿区块未按规范依赖顺序排列")

    if level_two[:2] != list(SECTION_ORDER[:2]):
        errors.append("E0 和 B0 必须是终稿前两个语义区块")
    if "结论先行" in text:
        errors.append("禁止在规范账本前或终稿中使用“结论先行”")

    for heading, header in TABLE_HEADERS.items():
        section = section_text(text, heading)
        expected_cells = tuple(
            cell.strip() for cell in header.strip("|").split("|")
        )
        if (
            section
            and re.search(r"^\|", section, re.MULTILINE)
            and not rows_for_header(section, expected_cells)
        ):
            errors.append(f"{heading} 缺少固定表头: {header}")

    for heading, (prefix, limit) in ROW_LIMITS.items():
        rows = table_rows(section_text(text, heading))
        if prefix is None:
            count = max(len(rows) - 1, 0)
        else:
            count = sum(
                bool(row and re.fullmatch(rf"{prefix}\d+", row[0].split(maxsplit=1)[0]))
                for row in rows[1:]
            )
        if count > limit:
            errors.append(f"{heading} 超过最小证据脊柱行上限: {count}>{limit}")

    ranged_sections = "\n".join(
        section_text(text, heading)
        for heading in SECTION_ORDER[3:13]
    )
    if ID_RANGE_RE.search(ranged_sections):
        errors.append("跨表引用禁止使用连续范围，必须逐项列出 ID")

    framing = section_text(text, "## 框定与动作")
    design_rows = rows_for_header(framing, DESIGN_HEADER)
    construct_rows = rows_for_header(framing, CONSTRUCT_HEADER)
    action_rows = rows_for_header(framing, ACTION_HEADER)
    boundary_rows = rows_for_header(framing, BOUNDARY_HEADER)
    action_ids: set[str] = set()
    action_facet_fields: dict[str, set[str]] = {}
    action_facet_next: dict[str, str] = {}
    action_facet_population: dict[str, str] = {}
    action_facet_member_key: dict[str, str] = {}
    action_facet_window: dict[str, str] = {}
    boundary_candidate_fields: dict[str, set[str]] = {}
    design_parameters: dict[str, str] = {}
    if high_risk:
        input_gate = re.search(
            r"输入门：状态=(充分|缺口)；关键缺口=([^；]+)；"
            r"设计占位=([^；]+)；影响=([^\n]+)",
            framing,
        )
        if input_gate is None:
            errors.append("高风险框定缺少规范输入门")
        elif input_gate.group(1) == "缺口" and "CE-INPUT-GAP" not in text:
            errors.append("输入门有关键缺口却未标 CE-INPUT-GAP")

        design_ids: set[str] = set()
        open_design_ids: set[str] = set()
        if not design_rows:
            errors.append("高风险框定缺少 P 设计来源账本")
        for row in design_rows[1:]:
            if len(row) != len(DESIGN_HEADER) or not re.fullmatch(r"P\d+", row[0]):
                errors.append("P 设计来源行必须使用固定六列和稳定 P#")
                continue
            design_ids.add(row[0])
            design_parameters[row[0]] = row[1]
            if re.search(r"、|以及|或|且", row[1]):
                errors.append(f"{row[0]} 必须只含一个设计参数")
            statuses = re.findall(
                r"(?:已给输入|已核来源|候选占位|未知|价值决定)=", row[2]
            )
            if len(statuses) != 1 or not re.match(
                r"^(?:已给输入|已核来源|候选占位|未知|价值决定)=\S", row[2]
            ):
                errors.append(f"{row[0]} 缺少闭集设计来源状态")
            if row[2].startswith(("候选占位=", "未知=")):
                open_design_ids.add(row[0])
            if row[2].startswith("未知=") and not re.fullmatch(r"未知=U\d+", row[2]):
                errors.append(f"{row[0]} 的未知设计必须逐字引用单一 U#")
            if row[2].startswith("已核来源=") and not re.fullmatch(
                r"已核来源=E\d+", row[2]
            ):
                errors.append(f"{row[0]} 的已核来源必须逐字引用单一 E#")
            shared_actions = set(re.findall(r"A\d+", row[4]))
            if (
                len(shared_actions) > 1
                and re.search(r"资格|比较项|结果|阈值|权重|时窗|保障", row[1])
                and row[3] in {"无", "模型", "AI", "待定"}
            ):
                errors.append(f"{row[0]} 跨行动共享设计却缺少授权依据")
            if re.search(r"<[A-Za-z\u4e00-\u9fff][^>]*>", " ".join(row)):
                errors.append(f"{row[0]} 保留了未替换的尖括号模板")
        if open_design_ids:
            if input_gate is not None and input_gate.group(1) != "缺口":
                errors.append("P 含候选占位/未知时输入门必须为缺口")
            if "CE-INPUT-GAP" not in text:
                errors.append("P 含候选占位/未知却未标 CE-INPUT-GAP")
            gate_placeholders = (
                set(re.findall(r"P\d+", input_gate.group(3))) if input_gate else set()
            )
            missing_from_gate = open_design_ids - gate_placeholders
            if missing_from_gate:
                errors.append(
                    "输入门设计占位未列全开放 P#: "
                    + ", ".join(sorted(missing_from_gate))
                )

        construct_ids: set[str] = set()
        construct_signatures: list[tuple[str, ...]] = []
        construct_comparators: dict[str, str] = {}
        if len(construct_rows) < 3:
            errors.append("高风险框定至少需要一对 K 构念签名")
        for row in construct_rows[1:]:
            if len(row) != len(CONSTRUCT_HEADER) or not re.fullmatch(r"K\d+", row[0]):
                errors.append("K 构念签名必须使用固定九列和稳定 K#")
                continue
            construct_ids.add(row[0])
            if any(not cell for cell in row[1:]):
                errors.append(f"{row[0]} 构念签名存在空字段")
            construct_signatures.append(tuple(row[1:9]))
            construct_comparators[row[0]] = row[7]
        if len(construct_signatures) >= 2 and len(set(construct_signatures)) == 1:
            errors.append("K 竞争构念八项签名完全相同，未形成可判别定义")

        if not action_rows:
            errors.append("高风险行动选择缺少 A# 行动契约表")
        for row in action_rows[1:]:
            if len(row) != len(ACTION_HEADER):
                errors.append("A 行动契约必须使用固定六列")
                continue
            match = re.match(r"(A\d+)\s+候选/假设：\S", row[0])
            if match is None:
                errors.append("行动契约第一格必须使用 A# 候选/假设：")
                continue
            action_id = match.group(1)
            action_ids.add(action_id)
            if "仅认知" not in row[0]:
                target = re.fullmatch(
                    r"总体=([^；]+)；成员键=([^；]+)；结果=([^；]+)；"
                    r"时窗=([^；]+)；构念=(K\d+)；设计依据=([^；]+)",
                    row[1],
                )
                if target is None:
                    errors.append(
                        f"{action_id} 目标格缺少总体/成员键/原子结果/时窗/构念/设计依据"
                    )
                    target_values: tuple[str, ...] | None = None
                else:
                    target_values = target.groups()
                if target is not None and re.search(r"、|以及|或|且", target.group(3)):
                    errors.append(f"{action_id} 的目标结果必须是一个原子结果")
                if target is not None and target.group(5) not in construct_ids:
                    errors.append(f"{action_id} 引用未登记构念 {target.group(5)}")
                if target is not None:
                    unknown_p = set(re.findall(r"P\d+", target.group(6))) - design_ids
                    if unknown_p:
                        errors.append(
                            f"{action_id} 设计依据引用未登记 P#: "
                            + ", ".join(sorted(unknown_p))
                        )

                facet_specs = {
                    "E": (
                        "状态=",
                        "总体=",
                        "分配/暴露=",
                        "比较项=",
                        "结果=",
                        "时窗=",
                        "效应量=",
                        "识别=",
                        "所需字段=",
                        "来源位置=因果研究/本地评估",
                        "依据=",
                        "下一=",
                    ),
                    "F": (
                        "状态=",
                        "漏斗=",
                        "关键转移=",
                        "分母=",
                        "失败=",
                        "所需字段=",
                        "来源位置=受影响者/一线",
                        "依据=",
                        "下一=",
                    ),
                    "K": (
                        "状态=",
                        "交付单位=",
                        "固定资源=",
                        "瓶颈=",
                        "总上限=",
                        "成本分母=",
                        "时窗=",
                        "所需字段=",
                        "来源位置=运营/财政",
                        "依据=",
                        "下一=",
                    ),
                    "H": (
                        "状态=",
                        "比较项=",
                        "受影响总体=",
                        "主机制=",
                        "原子后果=",
                        "风险扫描=",
                        "权利状态=",
                        "候选保障=",
                        "所需字段=",
                        "来源位置=受影响者/独立权利/规则制定",
                        "依据=",
                        "下一=",
                    ),
                }
                executable_next = False
                for suffix, cell in zip(ACTION_FACETS, row[2:6], strict=True):
                    facet_id = f"{action_id}.{suffix}"
                    if not cell.startswith(f"{facet_id}；"):
                        errors.append(f"{action_id} 缺少稳定分面 {facet_id}")
                    for key in facet_specs[suffix]:
                        if key not in cell:
                            errors.append(f"{facet_id} 缺少行动契约键 {key}")
                    state = keyed_value(cell, "状态")
                    if state not in {"未知", "候选", "有界", "不适用"}:
                        errors.append(f"{facet_id} 状态必须使用闭集")
                    fields = field_items(keyed_value(cell, "所需字段"))
                    action_facet_fields[facet_id] = fields
                    if target_values is not None:
                        action_facet_population[facet_id] = (
                            keyed_value(cell, "受影响总体")
                            if suffix == "H"
                            else target_values[0]
                        )
                        action_facet_member_key[facet_id] = target_values[1]
                        action_facet_window[facet_id] = target_values[3]
                    next_item = keyed_value(cell, "下一")
                    action_facet_next[facet_id] = next_item
                    if not re.fullmatch(
                        r"(?:C\d+|P\d+|专业复核|未排期（.+）)", next_item
                    ):
                        errors.append(f"{facet_id} 下一项必须是单一 C#/P#/专业复核/未排期")
                    elif state in {"未知", "候选"} and next_item.startswith("未排期"):
                        errors.append(f"{facet_id} 未闭合却没有可执行下一项")
                    elif not next_item.startswith("未排期"):
                        executable_next = True
                    if suffix == "E" and target_values is not None:
                        for key, expected in (
                            ("总体", target_values[0]),
                            ("结果", target_values[2]),
                            ("时窗", target_values[3]),
                        ):
                            if keyed_value(cell, key) != expected:
                                errors.append(f"{facet_id} 的{key}与目标格不一致")
                        comparator = construct_comparators.get(target_values[4], "")
                        if (
                            comparator
                            and not comparator.startswith("不适用")
                            and keyed_value(cell, "比较项") != comparator
                        ):
                            errors.append(
                                f"{facet_id} 的比较项与构念 {target_values[4]} 不一致"
                            )
                    elif suffix == "F":
                        funnel = keyed_value(cell, "漏斗")
                        stages = [stage.strip() for stage in funnel.split("→") if stage.strip()]
                        transition = keyed_value(cell, "关键转移")
                        if len(stages) < 5:
                            errors.append(f"{facet_id} 采用漏斗少于五个阶段")
                        if transition and transition not in {
                            f"{left}→{right}" for left, right in zip(stages, stages[1:])
                        }:
                            errors.append(f"{facet_id} 关键转移不是漏斗相邻阶段")
                    elif suffix == "H":
                        scan = keyed_value(cell, "风险扫描")
                        for risk_key in ("直接:", "替代:", "挤出:", "反馈:"):
                            if risk_key not in scan:
                                errors.append(f"{facet_id} 风险扫描缺少 {risk_key}")
                            else:
                                risk_value = re.search(
                                    rf"{re.escape(risk_key)}([^,，]+)", scan
                                )
                                if (
                                    risk_value
                                    and "→" not in risk_value.group(1)
                                    and not risk_value.group(1).startswith("未识别（")
                                ):
                                    errors.append(
                                        f"{facet_id} {risk_key} 必须写机制→后果或未识别（理由）"
                                    )
                        if re.search(r"(?:直接|替代|挤出|反馈):无(?:[,，]|$)", scan):
                            errors.append(f"{facet_id} 风险扫描不得裸写无")
                        rights = keyed_value(cell, "权利状态")
                        if not re.fullmatch(
                            r"(?:已核:E\d+|未核:U\d+|价值决定:P\d+)", rights
                        ):
                            errors.append(f"{facet_id} 权利状态不在闭集")
                    elif suffix == "K":
                        total_cap = keyed_value(cell, "总上限")
                        if total_cap in {"未知", "待定", "无"}:
                            errors.append(f"{facet_id} 总上限不得裸写未知/待定/无")
                if not executable_next:
                    errors.append(f"{action_id} 四个分面均无可执行下一项")
            if re.search(r"<[A-Za-z\u4e00-\u9fff][^>]*>", " ".join(row)):
                errors.append(f"{action_id} 保留了未替换的尖括号模板")

        boundary_actions: set[str] = set()
        if not boundary_rows:
            errors.append("高风险框定缺少 G 遗漏边界表")
        for row in boundary_rows[1:]:
            if len(row) != len(BOUNDARY_HEADER) or not re.fullmatch(r"G\d+", row[0]):
                errors.append("G 边界行必须使用固定七列和稳定 G#")
                continue
            refs = set(re.findall(r"A\d+", row[1]))
            if len(refs) != 1 or "观察框=" not in row[1]:
                errors.append(f"{row[0]} 必须绑定一个 A# 与观察框=")
            else:
                boundary_actions.update(refs)
            if not row[2] or re.search(r"、|以及|或", row[2]):
                errors.append(f"{row[0]} 必须只含一个候选遗漏总体")
            mechanism_match = re.fullmatch(r"机制=([^；]+)；判定字段=(.+)", row[3])
            if mechanism_match is None:
                errors.append(f"{row[0]} 漏捕机制必须写机制=与判定字段=")
            if "后果=" not in row[4] or "权利状态=" not in row[4]:
                errors.append(f"{row[0]} 缺少后果=或权利状态=")
            if re.search(r"、|/|＋|\+|以及|或", row[5]):
                errors.append(f"{row[0]} 必须只有一个所有者")
            if not re.fullmatch(r"(?:C\d+|U\d+|P\d+|未排期（.+）)", row[6]):
                errors.append(f"{row[0]} 下一项必须是单一 C#/U#/P#/未排期")
            elif row[6].startswith("C") and mechanism_match is not None:
                boundary_candidate_fields.setdefault(row[6], set()).update(
                    field_items(mechanism_match.group(2))
                )
        missing_boundaries = action_ids - boundary_actions
        if missing_boundaries:
            errors.append(
                "每个行动至少需要一个 G 边界行，缺少: "
                + ", ".join(sorted(missing_boundaries))
            )

    b0_rows = budget_rows(text, "## B0 PRE-TOOL 预算账本")
    b1_rows = budget_rows(text, "## B1 FINAL 与停止")
    for resource in BUDGET_RESOURCES:
        if resource not in b0_rows:
            errors.append(f"B0 缺少预算资源: {resource}")
        elif len(b0_rows[resource]) < 6 or parse_quantity(b0_rows[resource][2]) is None:
            errors.append(f"B0 {resource} 必须记录可解析的起始消耗和测量依据")
        if resource not in b1_rows:
            errors.append(f"B1 缺少预算资源: {resource}")
        elif len(b1_rows[resource]) < 5:
            errors.append(f"B1 {resource} 缺少实际消耗、状态或测量依据")

    material_row = b1_rows.get("材料打开", [])
    if material_row and not all(
        marker in " ".join(material_row) for marker in ("S", "C", "丢弃")
    ):
        errors.append("材料打开必须按 S + C + 丢弃守恒")

    visible_row = b1_rows.get("可见输出", [])
    if visible_row and re.search(
        r"Unicode|UTF-8|字符代理", " ".join(visible_row), re.IGNORECASE
    ):
        conservative_proxy = max(len(text), len(text.encode("utf-8")) / 2)
        reported_proxy = parse_quantity(visible_row[2]) if len(visible_row) > 2 else None
        if reported_proxy is None:
            errors.append("B1 可见输出字符代理必须记录可解析数值")
        elif reported_proxy < conservative_proxy:
            errors.append(
                "B1 可见输出字符代理低报: "
                f"reported={reported_proxy:g}, recomputed={conservative_proxy:g}"
            )
        compare_cap(
            "可见输出字符代理",
            conservative_proxy,
            visible_row[1],
            errors,
        )
    wall_row = b1_rows.get("墙钟时间", [])
    if wall_row and not re.search(r"起止|单调时钟", " ".join(wall_row[3:])):
        errors.append("B1 墙钟时间必须记录起止或单调时钟依据")

    revision = section_text(text, "## R：真实认知修订")
    if re.search(r"[EI]\d+\s*[–—-]\s*[EI]\d+", revision):
        errors.append("R 的触发 E/I ID 禁止使用连续范围")
    revision_rows = table_rows(revision)
    for row in revision_rows[1:]:
        if len(row) >= 6 and re.fullmatch(r"R\d+", row[0]):
            revision_tail = " ".join(row[4:])
            if (
                NORMATIVE_RE.search(revision_tail)
                or "禁止" in revision_tail
                or re.search(r"验证门|升为|治理门", revision_tail)
            ):
                errors.append(f"{row[0]} 认识内容或下游影响包含规范动作")
            if not row[4].startswith("E0：“") or "→ 本轮：“" not in row[4]:
                errors.append(f"{row[0]} 缺少 E0 逐字差分格式")
            delta_match = re.fullmatch(
                r"E0：“(.+)”\s*→\s*本轮：“(.+)”",
                row[4],
            )
            if delta_match:
                before, after = delta_match.groups()
                causal = re.compile(r"导致|造成|驱动|决定")
                if (
                    row[3] != "新增"
                    and causal.search(after)
                    and not causal.search(before)
                ):
                    errors.append(f"{row[0]} 新增因果谓词却未使用新增/E0无")
            if not row[5].startswith("认识影响="):
                errors.append(f"{row[0]} 第六列缺少字面键 认识影响=")
            elif not re.fullmatch(
                r"认识影响=(?:[DIUR]\d+)；认识状态=\S.+→.+\S",
                row[5],
            ):
                errors.append(
                    f"{row[0]} 第六列必须使用单一 ID 与认识状态=原状态→新状态"
                )

    dimension_rows = table_rows(section_text(text, "## D：维度取舍"))
    dimension_ids: set[str] = set()
    dimension_operands: dict[str, set[str]] = {}
    dimension_links: dict[str, set[str]] = {}
    for row in dimension_rows[1:]:
        if not row or not re.match(r"D\d+\b", row[0]):
            continue
        dimension_id = row[0].split(maxsplit=1)[0]
        dimension_ids.add(dimension_id)
        row_text = " ".join(row)
        name = re.sub(
            r"^D\d+\s*(?:候选/假设：|候选：)?",
            "",
            row[0],
        )
        if re.search(r"、|(?<!\d)/(?!\d)|＋|\+|以及|或|(?<!参)与", name):
            errors.append(f"{dimension_id} 名称不是叶子单轴")
        if re.search(r"<[A-Za-z\u4e00-\u9fff][^>]*>", row_text):
            errors.append(f"{dimension_id} 保留了未替换的尖括号模板")
        if len(row) >= 4:
            missing = [
                key
                for key in (
                    "机制=",
                    "操作化=",
                    "操作数=",
                    "单位=",
                    "窗口=",
                    "参照=",
                    "假设=",
                )
                if key not in row[3]
            ]
            if missing:
                errors.append(
                    f"{row[0].split(maxsplit=1)[0]} 理由缺少操作化键: "
                    + ", ".join(missing)
                )
            operation = row[3].split("操作化=", maxsplit=1)[-1].split(
                "；", maxsplit=1
            )[0]
            missing_operation = [
                key
                for key in (
                    "对象:",
                    "覆盖:",
                    "行粒度:",
                    "成员键:",
                    "采集:",
                    "缺失:",
                    "计算:",
                    "聚合:",
                    "权重:",
                )
                if key not in operation
            ]
            if "操作化=" in row[3] and missing_operation:
                errors.append(
                    f"{row[0].split(maxsplit=1)[0]} 操作化缺少子键: "
                    + ", ".join(missing_operation)
                )
            dimension_operands[dimension_id] = field_items(
                keyed_value(row[3], "操作数")
            )
            if high_risk:
                weight_match = re.search(r"(?:^|,)权重:([^,；]+)", operation)
                if (
                    weight_match
                    and weight_match.group(1).strip() != "无"
                    and not re.search(r"(?:P|E)\d+|用户", weight_match.group(1))
                ):
                    errors.append(f"{dimension_id} 的非空权重缺少 P#/E#/用户来源")
                reference = keyed_value(row[3], "参照")
                if (
                    reference
                    and reference != "无"
                    and not re.search(r"(?:P|E)\d+|用户", reference)
                ):
                    errors.append(f"{dimension_id} 的参照缺少 P#/E#/用户来源")
                if re.search(r"阈值|参照期|日历窗", row[3]) and not re.search(
                    r"P\d+", row[3]
                ):
                    errors.append(f"{dimension_id} 的阈值/参照期/日历窗缺少 P#")
        if len(row) >= 2 and len(set(re.findall(r"[UC]\d+", row[1]))) > 1:
            errors.append(f"{dimension_id} 含多个未闭合 U/C 锚点")
        dimension_links[dimension_id] = set(re.findall(r"[CU]\d+", row_text))
        if "代理" in row_text and not dimension_links[dimension_id]:
            errors.append(f"{dimension_id} 使用代理量却没有专门 U/C 验证")
        if high_risk and len(row) >= 5:
            impact = re.fullmatch(r"价值/决定：行动=(A\d+)；用途=\S.+", row[4])
            if impact is None:
                errors.append(f"{dimension_id} 影响格必须绑定单一 行动=A# 与用途=")
            elif impact.group(1) not in action_ids:
                errors.append(f"{dimension_id} 引用未登记行动 {impact.group(1)}")

    candidate_rows = table_rows(section_text(text, "## C：候选线索"))
    candidate_ids: set[str] = set()
    candidate_fields: dict[str, set[str]] = {}
    candidate_consumers: dict[str, str] = {}
    candidate_population: dict[str, str] = {}
    candidate_member_key: dict[str, str] = {}
    candidate_window: dict[str, str] = {}
    for row in candidate_rows[1:]:
        if len(row) < 4 or not re.fullmatch(r"C\d+", row[0]):
            continue
        candidate_ids.add(row[0])
        consumers = set(CONSUMER_ID_RE.findall(row[2]))
        if len(consumers) != 1:
            errors.append(f"{row[0]} 必须只有一个主要 A分面/D/I/U 消费者")
        else:
            candidate_consumers[row[0]] = next(iter(consumers))
        expected = row[1]
        if re.search(r"<[A-Za-z\u4e00-\u9fff][^>]*>", expected):
            errors.append(f"{row[0]} 保留了未替换的尖括号模板")
        if "产物=" in expected:
            product_keys = ["总体=", "字段=", "窗口="]
            if high_risk:
                product_keys.extend(
                    ("行粒度=", "成员键=", "设计字段=", "版本=")
                )
            missing_product = [
                key
                for key in product_keys
                if not re.search(rf"(?:^|；){re.escape(key)}", expected)
            ]
            if missing_product:
                errors.append(
                    f"{row[0]} 数据产物缺少可计算键: "
                    + ", ".join(missing_product)
                )
            candidate_fields[row[0]] = field_items(keyed_value(expected, "字段"))
            candidate_fields[row[0]].update(
                field_items(keyed_value(expected, "设计字段"))
            )
            candidate_population[row[0]] = keyed_value(expected, "总体")
            candidate_member_key[row[0]] = keyed_value(expected, "成员键")
            candidate_window[row[0]] = keyed_value(expected, "窗口")
            if re.search(r"A\d+(?:总体|目标|成员)|同上|同前", expected):
                errors.append(f"{row[0]} 数据产物使用行动别名而非成员规则")
        elif "材料=" not in expected:
            errors.append(f"{row[0]} 必须逐字使用材料=或产物=模板")
        blocker_keys = re.findall(r"(?:身份|访问|版本|取得)阻断=", row[3])
        if len(blocker_keys) != 1:
            errors.append(
                f"{row[0]} 必须逐字使用且只使用一个身份/访问/版本/取得阻断=键"
            )

    unknown_rows = table_rows(section_text(text, "## U：冲突与未知"))
    unknown_ids: set[str] = set()
    unknown_next: dict[str, str] = {}
    unknown_text: dict[str, str] = {}
    unknown_fields: dict[str, set[str]] = {}
    for row in unknown_rows[1:]:
        if row and not re.match(r"U\d+\b", row[0]):
            errors.append("U 账本每行第一格必须以稳定 U# 开头")
            continue
        if len(row) < 4:
            continue
        unknown_id = row[0].split(maxsplit=1)[0]
        unknown_ids.add(unknown_id)
        unknown_text[unknown_id] = row[0]
        observation_match = re.search(r"观测量:([^,，；]+)", row[0])
        unknown_fields[unknown_id] = (
            field_items(observation_match.group(1)) if observation_match else set()
        )
        proposition = row[0].split("；判定口径=", maxsplit=1)[0]
        if not re.match(r"U\d+\s+(?:未知|冲突)：命题=\S", row[0]):
            errors.append(f"{unknown_id} 必须逐字使用‘未知/冲突：命题=’固定极性")
        for key in ("；判定口径=", "对象:", "观测量:", "窗口:", "阈值/方向:"):
            if key not in row[0]:
                errors.append(f"{unknown_id} 缺少可证伪判定键 {key}")
        if re.search(r"是否|能否|有无", proposition):
            errors.append(f"{unknown_id} 使用是否/能否/有无隐藏命题极性")
        if re.search(r"、|/|＋|\+|以及|或|且", proposition):
            errors.append(f"{unknown_id} 合并了多个可独立未知")
        multiple_role_heads = re.search(
            rf"(?:{ROLE_HEAD}).*(?:和|与).*(?:{ROLE_HEAD})",
            row[2],
        )
        if re.search(r"、|/|＋|\+|以及|或", row[2]) or multiple_role_heads:
            errors.append(f"{unknown_id} 必须只有一个所有者")
        if not re.fullmatch(r"C\d+", row[3]):
            errors.append(f"{unknown_id} 下一证据必须是单一 C#")
        else:
            unknown_next[unknown_id] = row[3]
        if re.search(r"<[A-Za-z\u4e00-\u9fff][^>]*>", " ".join(row)):
            errors.append(f"{unknown_id} 保留了未替换的尖括号模板")
        if re.search(r"会|将|导致|排除|伤害|遗漏|侵犯", row[1]) and not re.search(
            rf"若\s*{re.escape(unknown_id)}\s*成立，则",
            row[1],
        ):
            errors.append(f"{unknown_id} 的未知事实后果必须显式条件化")

    for candidate_id in candidate_ids:
        direct_dimensions = {
            dimension_id
            for dimension_id, links in dimension_links.items()
            if candidate_id in links
        }
        next_unknowns = {
            unknown_id
            for unknown_id, next_candidate in unknown_next.items()
            if next_candidate == candidate_id
        }
        if len(direct_dimensions) > 1:
            errors.append(
                f"{candidate_id} 被多个 D 直接消费: "
                + ", ".join(sorted(direct_dimensions))
            )
        if len(next_unknowns) > 1:
            errors.append(
                f"{candidate_id} 被多个 U 作为下一证据: "
                + ", ".join(sorted(next_unknowns))
            )

    for facet_id, next_item in action_facet_next.items():
        if not next_item.startswith("C"):
            continue
        if next_item not in candidate_ids:
            errors.append(f"{facet_id} 下一项引用未登记 {next_item}")
            continue
        if candidate_consumers.get(next_item) != facet_id:
            errors.append(f"{next_item} 的主消费者必须是 {facet_id}")
        missing_fields = action_facet_fields.get(facet_id, set()) - candidate_fields.get(
            next_item, set()
        )
        if missing_fields:
            errors.append(
                f"{next_item} 字段未覆盖 {facet_id} 所需字段: "
                + ", ".join(sorted(missing_fields))
            )
        expected_population = action_facet_population.get(facet_id, "")
        if (
            expected_population
            and candidate_population.get(next_item) != expected_population
        ):
            errors.append(f"{next_item} 总体与 {facet_id} 不一致")
        expected_member_key = action_facet_member_key.get(facet_id, "")
        if (
            expected_member_key
            and candidate_member_key.get(next_item) != expected_member_key
        ):
            errors.append(f"{next_item} 成员键与 {facet_id} 不一致")
        expected_window = action_facet_window.get(facet_id, "")
        if expected_window and candidate_window.get(next_item) != expected_window:
            errors.append(f"{next_item} 窗口与 {facet_id} 不一致")

    for candidate_id, required_fields in boundary_candidate_fields.items():
        if candidate_id not in candidate_ids:
            errors.append(f"G 边界下一项引用未登记 {candidate_id}")
            continue
        missing_fields = required_fields - candidate_fields.get(candidate_id, set())
        if missing_fields:
            errors.append(
                f"{candidate_id} 字段未覆盖 G 边界判定字段: "
                + ", ".join(sorted(missing_fields))
            )

    for unknown_id, candidate_id in unknown_next.items():
        if candidate_id not in candidate_ids:
            continue
        missing_fields = unknown_fields.get(unknown_id, set()) - candidate_fields.get(
            candidate_id, set()
        )
        if missing_fields:
            errors.append(
                f"{candidate_id} 字段未覆盖 {unknown_id} 观测量: "
                + ", ".join(sorted(missing_fields))
            )

    for dimension_id, operands in dimension_operands.items():
        linked_candidates = {
            ref for ref in dimension_links.get(dimension_id, set()) if ref.startswith("C")
        }
        for unknown_id in {
            ref for ref in dimension_links.get(dimension_id, set()) if ref.startswith("U")
        }:
            if unknown_id in unknown_next:
                linked_candidates.add(unknown_next[unknown_id])
        if not linked_candidates:
            continue
        available = set().union(
            *(candidate_fields.get(candidate_id, set()) for candidate_id in linked_candidates)
        )
        missing_operands = operands - available
        if missing_operands:
            errors.append(
                f"{dimension_id} 的 C 字段未覆盖操作数: "
                + ", ".join(sorted(missing_operands))
            )

    source_rows = table_rows(section_text(text, "## S：材料登记"))
    source_gates: dict[str, str] = {}
    for row in source_rows[1:]:
        if len(row) < 3 or not re.fullmatch(r"S\d+", row[0]):
            continue
        gate = row[2]
        if "E门=开放" not in gate and "E门=关闭" not in gate:
            errors.append(f"{row[0]} 未声明 E门=开放/关闭")
        if "E门=开放" in gate and not all(
            marker in gate for marker in ("发布：", "版本：", "访问：")
        ):
            errors.append(f"{row[0]} 开放 E 门但发布/版本/访问记录不完整")
        locator = re.search(r"E门=开放（([^）]+)）", gate)
        if locator and not re.search(
            r"第?\d+\s*(?:页|节|章|段)|p{1,2}\.?\s*\d+|§|表\s*\d+|图\s*\d+|fig(?:ure)?\.?\s*\d+|附录|锚点|章节|段落",
            locator.group(1),
            re.IGNORECASE,
        ):
            errors.append(f"{row[0]} 的 E 门缺少可复现支持位置")
        source_gates[row[0]] = gate

    evidence_rows = table_rows(section_text(text, "## E：原子来源主张"))
    evidence_consumers: dict[str, set[str]] = {}
    evidence_types: dict[str, str] = {}
    evidence_sources: dict[str, str] = {}
    evidence_producers: dict[str, str] = {}
    evidence_claims: dict[str, str] = {}
    evidence_adaptations: dict[str, dict[str, str]] = {}
    for row in evidence_rows[1:]:
        if len(row) < 5 or not re.fullmatch(r"E\d+", row[0]):
            continue
        source_id = row[1]
        if not re.fullmatch(r"S\d+", source_id):
            errors.append(f"{row[0]} 的来源 ID 必须是纯 S#，不能放链接或说明")
            gate = None
        else:
            gate = source_gates.get(source_id)
        if gate is None:
            if re.fullmatch(r"S\d+", source_id):
                errors.append(f"{row[0]} 引用未登记的来源 {source_id}")
            gate = ""
        if "E门=关闭" in gate:
            errors.append(f"{row[0]} 来自 E门=关闭 的 {source_id}")
        elif "E门=开放" not in gate:
            errors.append(f"{row[0]} 的来源 {source_id} 未开放 E 门")

        status = row[-1]
        claim = row[2]
        evidence_claims[row[0]] = claim
        if "原子类型=单命题" not in status and "原子类型=封闭集合" not in status:
            errors.append(f"{row[0]} 缺少原子类型=单命题/封闭集合")
        if "原子类型=单命题" in status and re.search(
            r"；|并指出|同时(?!期)|且|或|以及", claim
        ):
            errors.append(f"{row[0]} 单命题使用连接词引入第二谓词")
        claim_type = next(
            (
                value
                for value in ("经验", "定义", "方法", "规范立场")
                if f"命题类型={value}" in status
            ),
            "",
        )
        if not claim_type:
            errors.append(f"{row[0]} 缺少命题类型=经验/定义/方法/规范立场")
        evidence_types[row[0]] = claim_type
        evidence_sources[row[0]] = source_id
        producer_match = re.search(
            r"生产位置=(受影响者|一线|独立权利|规则制定|运营|研究|供应|其他)",
            status,
        )
        if producer_match is None:
            errors.append(f"{row[0]} 缺少闭集生产位置=")
            evidence_producers[row[0]] = ""
        else:
            evidence_producers[row[0]] = producer_match.group(1)
        for key in (
            "支持位置=",
            "消费者=",
            "适配=",
            "统计口径=",
            "新鲜度=",
            "边界=",
        ):
            if key not in status:
                errors.append(f"{row[0]} 状态列缺少字面键 {key}")
        support_position = keyed_value(status, "支持位置")
        if support_position and support_position not in gate:
            errors.append(f"{row[0]} 支持位置未逐字回指 {source_id} 的开放定位")
        if not CONSUMER_ID_RE.search(status):
            errors.append(f"{row[0]} 缺少命名的 A分面/D/I/R/U 消费者")
        evidence_consumers[row[0]] = set(CONSUMER_ID_RE.findall(status))
        adaptations: dict[str, str] = {}
        for item in re.split(r"[,，]", keyed_value(status, "适配")):
            item = item.strip()
            if not item:
                continue
            pair = re.fullmatch(r"(A\d+\.[EFKH]|[DIKPRU]\d+):(.+)", item)
            if pair is None:
                errors.append(f"{row[0]} 适配项格式错误: {item}")
                continue
            consumer, role = pair.groups()
            if role not in EVIDENCE_ROLES:
                errors.append(f"{row[0]} 使用未知支持角色: {role}")
            adaptations[consumer] = role
            if role == "因果效果" and claim_type != "经验":
                errors.append(f"{row[0]} 非经验命题不能适配为因果效果")
        evidence_adaptations[row[0]] = adaptations
        if set(adaptations) != evidence_consumers[row[0]]:
            errors.append(f"{row[0]} 消费者与适配集合不一致")
        if any(consumer.startswith("A") for consumer in evidence_consumers[row[0]]):
            boundary = keyed_value(status, "边界")
            if re.search(r"不可直接迁移|不可迁移|异地|非本地", boundary):
                errors.append(f"{row[0]} 有迁移缺口却直接支持行动分面")

    consumer_sections = (
        ("## D：维度取舍", "D"),
        ("## I：有界推断", "I"),
        ("## R：真实认知修订", "R"),
        ("## U：冲突与未知", "U"),
    )
    actual_consumers: dict[str, set[str]] = {}
    for rows, allowed_roles in (
        (design_rows[1:], {"定义边界"}),
        (construct_rows[1:], {"定义边界", "测量方法"}),
    ):
        for row in rows:
            consumer_match = re.match(r"([PK]\d+)\b", row[0]) if row else None
            if not consumer_match:
                continue
            consumer = consumer_match.group(1)
            for evidence_id in set(re.findall(r"E\d+", " ".join(row))):
                if evidence_id not in evidence_consumers:
                    continue
                actual_consumers.setdefault(evidence_id, set()).add(consumer)
                role = evidence_adaptations.get(evidence_id, {}).get(consumer)
                if role not in allowed_roles:
                    errors.append(
                        f"{evidence_id} 对 {consumer} 必须使用定义边界/测量方法适配"
                    )
    for row in action_rows[1:]:
        action_match = re.match(r"(A\d+)\b", row[0]) if row else None
        if not action_match or len(row) < 6:
            continue
        action_id = action_match.group(1)
        for suffix, cell in zip(ACTION_FACETS, row[2:6], strict=True):
            consumer = f"{action_id}.{suffix}"
            for evidence_id in set(re.findall(r"E\d+", cell)):
                if evidence_id in evidence_consumers:
                    actual_consumers.setdefault(evidence_id, set()).add(consumer)
                    expected_role = {
                        "E": "因果效果",
                        "F": "采用失败",
                        "K": "容量成本",
                        "H": "伤害权利",
                    }[suffix]
                    if evidence_adaptations.get(evidence_id, {}).get(consumer) != expected_role:
                        errors.append(
                            f"{evidence_id} 对 {consumer} 必须使用适配角色 {expected_role}"
                        )
    for heading, prefix in consumer_sections:
        rows = table_rows(section_text(text, heading))
        for row in rows[1:]:
            match = re.match(rf"({prefix}\d+)\b", row[0]) if row else None
            if not match:
                continue
            consumer = match.group(1)
            for evidence_id in set(re.findall(r"E\d+", " ".join(row))):
                if evidence_id in evidence_consumers:
                    actual_consumers.setdefault(evidence_id, set()).add(consumer)
    for evidence_id, consumers in actual_consumers.items():
        undeclared = consumers - evidence_consumers.get(evidence_id, set())
        if undeclared:
            errors.append(
                f"{evidence_id} 状态列未声明实际消费者: {', '.join(sorted(undeclared))}"
            )
    for evidence_id, consumers in evidence_consumers.items():
        extra = consumers - actual_consumers.get(evidence_id, set())
        if extra:
            errors.append(
                f"{evidence_id} 状态列存在虚挂消费者: {', '.join(sorted(extra))}"
            )

    inference_rows = table_rows(section_text(text, "## I：有界推断"))
    inference_bridges: dict[str, str] = {}
    inference_conclusions: dict[str, str] = {}
    for row in inference_rows[1:]:
        if len(row) < 6 or not re.fullmatch(r"I\d+", row[0]):
            continue
        bridge = row[2]
        inference_bridges[row[0]] = bridge
        conclusion = row[3]
        inference_conclusions[row[0]] = conclusion
        status = row[5]
        if NORMATIVE_RE.search(conclusion):
            errors.append(f"{row[0]} 有界结论包含规范词")
        if "；" in conclusion:
            errors.append(f"{row[0]} 有界结论使用分号连接第二结论")

        if bridge.startswith("已闭合："):
            if not re.search(r"E\d+", bridge):
                errors.append(f"{row[0]} 已闭合桥接缺少 E#")
        elif bridge.startswith("逻辑桥："):
            if not bridge.removeprefix("逻辑桥：").strip():
                errors.append(f"{row[0]} 逻辑桥为空")
        else:
            match = re.fullmatch(
                r"未核实：\s*(U\d+)\s*；\s*下一证据\s*(C\d+)\s*；\s*"
                r"迁移=(对象|测量|尺度|人口|时期|情境)：\s*([^；]+→[^；]+)；\s*"
                r"保持=([对象测量尺度人口时期情境/、，,]+)",
                bridge,
            )
            if not match:
                errors.append(f"{row[0]} 桥接条件不属于三种规范格式")
            else:
                unknown_id, candidate_id = match.group(1), match.group(2)
                migration_type = match.group(3)
                kept = set(re.split(r"[/、，,]", match.group(5))) - {""}
                expected_kept = INFERENCE_INVARIANTS - {migration_type}
                if kept != expected_kept:
                    errors.append(
                        f"{row[0]} 保持= 必须逐项列出其余五项: "
                        + "/".join(sorted(expected_kept))
                    )
                if unknown_next.get(unknown_id) != candidate_id:
                    errors.append(f"{row[0]} 桥接 U/C 与 U 账本下一证据不一致")
                if not re.match(
                    rf"若\s*{re.escape(unknown_id)}\s*成立，则",
                    conclusion,
                ):
                    errors.append(f"{row[0]} 未把未知桥接写成显式条件结论")
                if re.search(r"高估|低估|增加|降低|上升|下降", conclusion) and re.search(
                    r"命题=[^；]*存在", unknown_text.get(unknown_id, "")
                ):
                    errors.append(f"{row[0]} 用‘存在’桥接总体方向或量级")

        if "主用途" not in status:
            errors.append(f"{row[0]} 状态列缺少主用途")
        primary_uses = set(re.findall(r"[DU]\d+", status))
        if len(primary_uses) > 1:
            errors.append(f"{row[0]} 必须只有单一主用途")
        normative_premises = [
            evidence_id
            for evidence_id in re.findall(r"E\d+", row[1])
            if evidence_types.get(evidence_id) == "规范立场"
        ]
        if normative_premises:
            errors.append(
                f"{row[0]} 把规范立场 E 当作经验推断前提: "
                + ", ".join(normative_premises)
            )
        if high_risk and re.search(
            r"负担|暴露|可达|使用|排斥|权利|伤害|遗漏",
            conclusion,
        ):
            premise_producers = {
                evidence_producers.get(evidence_id, "")
                for evidence_id in re.findall(r"E\d+", row[1])
            }
            if not premise_producers.intersection(
                {"受影响者", "一线", "独立权利"}
            ):
                errors.append(f"{row[0]} 高风险结论未直接消费受影响者/一线/独立权利 E")
        source_family = " ".join((row[4], row[5]))
        premise_evidence = re.findall(r"E\d+", row[1])
        premise_sources = {
            evidence_sources[evidence_id]
            for evidence_id in premise_evidence
            if evidence_id in evidence_sources
        }
        single_family = bool(premise_evidence) and len(premise_sources) <= 1
        family_declared = bool(
            re.search(
                r"单一来源家族|同一来源家族|同属.{0,12}来源|只有一个来源",
                source_family,
            )
        )
        if (family_declared or (high_risk and single_family)) and "CE-EVIDENCE-GAP" not in status:
            errors.append(f"{row[0]} 单一来源家族却未标 CE-EVIDENCE-GAP")

    e0_section = section_text(text, "## PRE-EVIDENCE-SNAPSHOT E0")
    trigger_cells = {**evidence_claims, **inference_conclusions}
    for row in revision_rows[1:]:
        if len(row) < 6 or not re.fullmatch(r"R\d+", row[0]):
            continue
        triggers = re.findall(r"[EI]\d+", row[2])
        if len(triggers) != 1:
            errors.append(f"{row[0]} 必须只有一个最近触发 E/I")
            continue
        delta_match = re.fullmatch(r"E0：“(.+)”\s*→\s*本轮：“(.+)”", row[4])
        if delta_match is None:
            continue
        before, after = delta_match.groups()
        if before != "无" and before not in e0_section:
            errors.append(f"{row[0]} 的 E0 片段不是 E0 逐字内容")
        trigger_cell = trigger_cells.get(triggers[0])
        if trigger_cell is None:
            errors.append(f"{row[0]} 引用不存在的触发 {triggers[0]}")
        elif after != trigger_cell:
            errors.append(f"{row[0]} 本轮片段未逐字复制触发主张/结论")

    challenge_rows = table_rows(section_text(text, "## 挑战记录"))
    for row in challenge_rows[1:]:
        if not row:
            continue
        if not re.fullmatch(r"CH\d+", row[0]):
            errors.append("挑战记录每行第一格必须以稳定 CH# 开头")
            continue
        if len(row) != 6:
            errors.append(f"{row[0]} 必须使用固定六列挑战格式")
            continue
        if not row[2].startswith("候选/假设"):
            errors.append(f"{row[0]} 的竞争解释必须显式标为候选/假设")
        if len(row) >= 3:
            required_fields = {
                "主机制": r"主机制[=：:]",
                "竞争机制": r"竞争机制[=：:]",
                "机制判据": r"机制判据[=：:]",
                "同一判别域": r"同一判别域[=：:]",
                "判别量": r"判别量[=：:]",
                "时窗": r"时窗[=：:]",
                "分界": r"分界[=：:]",
                "所需字段": r"所需字段[=：:]",
                "竞争预测": r"竞争预测[=：:]",
                "主解释预测": r"主解释预测[=：:]",
                "互斥证明": r"互斥证明[=：:]",
                "穷尽说明": r"穷尽说明[=：:]",
                "结果→更新": r"结果→更新[=：:]",
            }
            missing = [
                field
                for field, pattern in required_fields.items()
                if not re.search(pattern, row[2])
            ]
            if missing:
                errors.append(
                    f"{row[0]} 的竞争解释缺少字面判别字段: {', '.join(missing)}"
                )
            main_mechanism = re.search(r"主机制[=：:]([^；|]+)", row[2])
            competing_mechanism = re.search(r"竞争机制[=：:]([^；|]+)", row[2])
            if (
                main_mechanism
                and competing_mechanism
                and main_mechanism.group(1).strip()
                == competing_mechanism.group(1).strip()
            ):
                errors.append(f"{row[0]} 主机制与竞争机制相同")
            prediction_values: dict[str, str] = {}
            for field in ("竞争预测", "主解释预测", "互斥证明", "穷尽说明"):
                value_match = re.search(rf"{field}[=：:]([^；|]+)", row[2])
                if value_match:
                    prediction_values[field] = value_match.group(1).strip()
            if (
                prediction_values.get("竞争预测")
                and prediction_values.get("竞争预测")
                == prediction_values.get("主解释预测")
            ):
                errors.append(f"{row[0]} 两项预测相同，不能判别")
            update_match = re.search(r"结果→更新[=：:]([^|]+)$", row[2])
            if update_match and not all(
                marker in update_match.group(1)
                for marker in ("竞争:", "主解释:", "未区分:")
            ):
                errors.append(f"{row[0]} 结果→更新必须覆盖竞争/主解释/未区分")
            main_id = row[1]
            if main_id in inference_bridges and inference_bridges[main_id].startswith(
                "逻辑桥："
            ):
                errors.append(f"{row[0]} 不得把逻辑桥 I 当作经验挑战主解释")
            challenge_candidates = set(re.findall(r"C\d+", row[3])) if len(row) > 3 else set()
            if len(row) > 4 and row[4] in {"证据不足", "未区分"}:
                if len(challenge_candidates) != 1:
                    errors.append(f"{row[0]} 未执行挑战必须绑定一个区分 C#")
                else:
                    candidate_id = next(iter(challenge_candidates))
                    needed = field_items(
                        re.search(
                            r"所需字段[=：:]([^；|]+)", row[2]
                        ).group(1)
                    ) if re.search(r"所需字段[=：:]([^；|]+)", row[2]) else set()
                    missing_fields = needed - candidate_fields.get(candidate_id, set())
                    if missing_fields:
                        errors.append(
                            f"{row[0]} 的 C 字段未覆盖所需字段: "
                            + ", ".join(sorted(missing_fields))
                        )

    canonical_rows: dict[str, list[str]] = {}
    for heading, prefix in (
        ("## D：维度取舍", "D"),
        ("## I：有界推断", "I"),
        ("## U：冲突与未知", "U"),
        ("## C：候选线索", "C"),
    ):
        for row in table_rows(section_text(text, heading))[1:]:
            if not row:
                continue
            match = re.match(rf"({prefix}\d+)\b", row[0])
            if not match:
                continue
            first_cell = re.sub(rf"^{match.group(1)}\s*", "", row[0])
            canonical_rows[match.group(1)] = [first_cell, *row[1:]]

    def normalize_summary_value(value: str) -> str:
        return re.sub(r"[。；;.!！\s]+$", "", value.replace("**", "").strip())

    summary = section_text(text, "## 地图摘要")
    summary_lines = [
        line.strip()
        for line in summary.splitlines()[1:]
        if line.strip()
    ]
    if len(summary_lines) > 5:
        errors.append("地图摘要超过五行")
    for line in summary_lines:
        normalized = re.sub(r"^(?:[-*]|\d+\.)\s*", "", line)
        match = re.match(r"^\[((?:[DIUC])\d+)\]\s*(.+)$", normalized)
        if not match:
            errors.append("地图摘要每行必须以既有 [D#]/[I#]/[U#]/[C#] 开头")
            break
        summary_id, value = match.groups()
        allowed = {
            normalize_summary_value(cell)
            for cell in canonical_rows.get(summary_id, [])
            if cell.strip()
        }
        if normalize_summary_value(value) not in allowed:
            errors.append(f"地图摘要 {summary_id} 必须逐字复制该行一个既有单元格")

    positive_verified = re.search(r"(?<!不是)(?<!并非)已核实", text)
    if positive_verified or "部分支持" in text:
        errors.append("终稿使用了非闭集认识状态（已核实/部分支持）")

    stop = section_text(text, "## B1 FINAL 与停止")
    if not re.search(r"地图状态：(?:完成|有界可用|未完成)", stop):
        errors.append("停止声明缺少规范地图状态")
    if not re.search(r"决策就绪：.*CE-[A-Z-]+", stop):
        errors.append("停止声明缺少带失败代码的决策就绪状态")
    legacy_next = re.search(r"最高价值下一证据：C\d+", stop)
    input_next = re.search(
        r"最高价值下一项：类型=输入；目标=(P\d+)；产物=([^；。]+)；"
        r"所需字段=([^；。]+)；选择依据=([^。\n]+)",
        stop,
    )
    other_next = re.search(
        r"最高价值下一项：类型=(?:证据|授权|专业复核)；"
        r"目标=[^；。]+；选择依据=[^。\n]+",
        stop,
    )
    structured_next = input_next or other_next
    if high_risk and structured_next is None:
        errors.append("高风险停止声明缺少结构化最高价值下一项及选择依据")
    elif not high_risk and legacy_next is None and structured_next is None:
        errors.append("停止声明缺少唯一最高价值下一项")
    if "重新开启条件：" not in stop:
        errors.append("停止声明缺少重新开启条件")
    if input_next is not None:
        target_p, product, fields, rationale = input_next.groups()
        if not re.search(r"v\d+|20\d{2}[-年]|hash[:=]", product, re.IGNORECASE):
            errors.append("输入下一项产物必须具名且版本化")
        other_parameters = {
            parameter
            for design_id, parameter in design_parameters.items()
            if design_id != target_p and parameter and parameter in f"{product}；{fields}"
        }
        if other_parameters:
            errors.append(
                "输入下一项混入其他 P 参数: " + ", ".join(sorted(other_parameters))
            )
        rationale_facets = set(ACTION_FACET_RE.findall(rationale))
        if len(rationale_facets) != 1:
            errors.append("输入下一项选择依据必须只绑定一个 A# 分面")
    if "CE-CONFLICT-UNRESOLVED" in stop and not any(
        re.match(r"U\d+\s+冲突：", row[0]) for row in unknown_rows[1:] if row
    ):
        errors.append("CE-CONFLICT-UNRESOLVED 缺少规范 U# 冲突")
    if "CE-PROFESSIONAL-REVIEW" in stop:
        ownership_rows = table_rows(section_text(text, "## 所有权交接"))[1:]
        review_domains: set[str] = set()
        review_rows = [row for row in ownership_rows if row and row[0] == "合格专业复核"]
        for row in review_rows:
            if len(row) != 3 or not re.fullmatch(r"主责专业=\S.+", row[1]):
                errors.append("合格专业复核必须保持三列且第二列仅含主责专业=")
                continue
            role = row[1].removeprefix("主责专业=")
            if role in {"独立专家", "领域专家", "独立领域专家"}:
                errors.append("合格专业复核必须给出领域特异主责专业")
            missing_review_keys = [
                key
                for key in (
                    "复核域=",
                    "复核产物=",
                    "验收口径=",
                    "算法/阈值=",
                    "依据快照=",
                    "独立性=",
                    "通过证据=",
                )
                if key not in row[2]
            ]
            if missing_review_keys:
                errors.append(
                    "合格专业复核缺少: " + ", ".join(missing_review_keys)
                )
                continue
            domain = keyed_value(row[2], "复核域")
            for expected_domain in ("效果识别", "运营容量成本", "权利法域遗漏"):
                if domain.startswith(expected_domain):
                    review_domains.add(expected_domain)
            if re.search(r"(?:验收口径|通过证据)=[^；]*(?:满足口径|符合要求|签署结论)", row[2]):
                errors.append("合格专业复核不得使用循环验收或签署代替可观测证据")
            product = keyed_value(row[2], "复核产物")
            acceptance = keyed_value(row[2], "验收口径")
            algorithm = keyed_value(row[2], "算法/阈值")
            snapshot = keyed_value(row[2], "依据快照")
            if not re.search(r"v\d+|20\d{2}[-年]|hash[:=]", product, re.IGNORECASE):
                errors.append("合格专业复核产物缺少可识别版本")
            if not re.search(
                r"(?:[<>≤≥=]\s*\d|\d+(?:\.\d+)?\s*%|百分之\d+|全部|每项|零)",
                acceptance,
            ):
                errors.append("合格专业复核验收口径缺少可观测阈值")
            if (
                not re.search(r"v\d+|规则|算法|计划|阈值", algorithm, re.IGNORECASE)
                or re.fullmatch(r"待?P\d+(?:[/,，]P\d+)*", algorithm)
            ):
                errors.append("合格专业复核算法/阈值不是具名规则")
            if not re.search(
                r"v\d+|20\d{2}[-年]|hash[:=]|版本[:=]\S",
                snapshot,
                re.IGNORECASE,
            ):
                errors.append("合格专业复核依据快照缺少冻结版本")
        missing_domains = {"效果识别", "运营容量成本", "权利法域遗漏"} - review_domains
        if missing_domains:
            errors.append(
                "CE-PROFESSIONAL-REVIEW 的合格专业复核缺少独立复核域: "
                + ", ".join(sorted(missing_domains))
            )
    if "CE-PROFESSIONAL-REVIEW" in stop and "不得据此直接实施" not in stop:
        errors.append("高风险决策未就绪时必须逐字写‘不得据此直接实施’")
    stable_rights = "\n".join(
        section_text(text, heading)
        for heading in (
            "## 框定与动作",
            "## C：候选线索",
            "## E：原子来源主张",
            "## U：冲突与未知",
        )
    )
    if high_risk and "权利状态=" not in stable_rights:
        errors.append("高风险输出必须把至少一项权利状态=落入 A.H/G/E/U")

    receipt_caps = {**b0_rows, **b1_rows}
    if receipt is not None:
        audit_receipt(receipt_caps, receipt, errors)
    if any("超过硬上限" in error or "字符代理低报" in error for error in errors):
        if "CE-BUDGET-EXHAUSTED" not in stop:
            errors.append("预算已越界却未返回 CE-BUDGET-EXHAUSTED")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = (
        json.loads(args.receipt.read_text(encoding="utf-8"))
        if args.receipt
        else None
    )
    errors = audit_output(args.artifact.read_text(encoding="utf-8"), receipt)
    if args.json:
        print(json.dumps({"status": "pass" if not errors else "fail", "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}")
    else:
        print("Cognitive-expansion output audit passed.")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
