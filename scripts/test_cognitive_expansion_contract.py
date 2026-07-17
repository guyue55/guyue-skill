#!/usr/bin/env python3
"""Regression checks for the cognitive-expansion control contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(text: str, marker: str, source: str) -> None:
    if marker not in text:
        raise AssertionError(f"{source} missing required marker: {marker}")


def main() -> int:
    root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills/cognitive-expansion/SKILL.md").read_text(
        encoding="utf-8"
    )
    output_contract = (
        ROOT / "skills/cognitive-expansion/references/output-contract.md"
    ).read_text(encoding="utf-8")
    behaviors = json.loads(
        (ROOT / "evals/behavior-contracts.json").read_text(encoding="utf-8")
    )
    output_cases = json.loads(
        (ROOT / "evals/capability-output-quality.json").read_text(encoding="utf-8")
    )["cases"]

    for marker in (
        "## 冻结探索预算",
        "微量拓界",
        "多维度/多角度/全面一点/有没有遗漏/第一次用/不懂这个产品",
        "联网升级门",
        "模式｜预计耗时区间｜联网/材料上限｜停止检查点｜主要不确定性",
        "任务级总账 BΣ",
        "最多 1 次自动实质重试",
        "最大轮数",
        "墙钟时间",
        "近似有效 Token",
        "只读工具调用",
        "材料打开",
        "可见输出",
        "授权子任务",
        "付费成本",
        "上限不是证据充分性",
        "B0 PRE-TOOL",
        "有效 Token",
        "缓存输入",
        "安全预留",
        "运行后收据",
        "激活前导",
        "bookkeeping",
        "材料打开只计算外部证据材料",
        "终稿草案只使用可见输出上限的 40%",
        "UTF-8 字节数÷2",
        "每轮不超过一行且不超过 40 tokens",
        "最小证据脊柱",
        "稀疏目标",
        "E门=开放",
        "原子类型=单命题",
        "命题类型=经验/定义/方法/规范立场",
        "一份可恢复材料或一个数据产物",
        "未核实：U#；下一证据 C#",
        "受影响者生产材料",
        "E0：“",
        "竞争预测",
        "合格专业复核",
        "D 是叶子决策轴",
        "输入门：状态=充分/缺口",
        "决策行动",
        "效果/增益",
        "禁止“同上/同前”",
        "P 设计来源账本",
        "K 构念签名",
        "A1.E/A1.F/A1.K/A1.H",
        "G 边界行",
        "一个原子结果",
        "第三列只能出现一个 `A1.E/A1.F/A1.K/A1.H` 或 D/I/U ID",
        "最多被一个 D 或行动分面直接引用",
        "章节：“Overview”；章节：“Methods”",
        "稳定 `CH#`",
        "覆盖:<决策总体→观察框/框外处理>",
        "行粒度:<一行代表什么>",
        "成员键:<稳定键>",
        "权重:<抽样/汇总权重或无>",
        "操作数=",
        "支持位置=",
        "统计口径=",
        "保持=<其余五项>",
        "判定口径=",
        "所需字段=",
        "验收口径=",
        "依据快照=",
        "独立性=",
        "算法/阈值=",
        "效果识别",
        "运营容量成本",
        "权利法域遗漏",
        "最高价值下一项",
        "最邻近触发",
        "规范立场 E 不进入经验 I",
        "已核实`、`已核验事实`、`部分支持` 不是自由状态",
        "规范 H2",
        "禁止在账本前写“结论先行”",
        "字面序列化门",
        "消费者只计算**直接写出该 E# 的 P/K/A 分面/D/I/R/U 规范行**",
        "`AR6` 等版本文字不算 R#",
        "一个非 ID 单元格",
        "不能写 `[D4] D4",
        "取得阻断=",
        "操作化=",
        "对象:<成员规则>",
        "产物=<一个版本化数据或分析产物>",
        "生产位置=受影响者/一线/独立权利",
        "迁移=<对象/测量/尺度/人口/时期/情境>",
        "认识影响=",
        "未知：命题=",
        "权利状态=",
        "适配=",
        "一个 I 最多桥接一个迁移缺口",
        "互斥证明",
        "结果→更新",
        "不得据此直接实施",
        "CE-BUDGET-EXHAUSTED",
        "当前仍有效且可追溯",
        "事实发生期/数据期",
        "搜索片段、聚合页",
        "比较/基准",
        "`未知=` 后必须是单一 U#",
        "机制→后果",
        "判定字段=",
        "主机制、竞争机制、机制判据",
        "字符/字节 dry-run",
        "容差与完成判定",
        "最多 1 次自动实质重试",
        "额度、usage limit",
    ):
        require(skill, marker, "cognitive-expansion/SKILL.md")

    for marker in (
        "开放列举与微量拓界",
        "种子而非闭集",
        "仅、只、严格限于、就这几项、不要扩展",
        "发布日、事实发生期/数据期、版本/更正/撤回和访问日",
        "预计超过 10 分钟",
        "不因“等”自动联网",
        "额度/usage limit",
    ):
        require(root_skill, marker, "root SKILL.md")

    for marker in (
        "budget_ledger",
        "UTF-8 字节数÷2",
        "上限｜实际消耗｜状态",
        "先到的硬上限",
        "丢弃未闭合轮次",
        "E0 → B0 → 框定/动作 → D → C → S → E → I → R → 挑战 → U → 所有权 → 摘要 → B1/停止",
        "触发 E/I ID 禁止使用连续范围",
        "未核实：U#；下一证据 C#",
        "原子类型=封闭集合",
        "命题类型=经验/定义/方法/规范立场",
        "数据产物",
        "竞争预测",
        "合格专业复核",
        "输入门：状态=充分/缺口",
        "决策行动",
        "效果/增益",
        "禁止“同上/同前”",
        "固定六列 P 表",
        "K 表",
        "A1.E/A1.F/A1.K/A1.H",
        "G 边界行",
        "一个原子结果",
        "第三列只能出现一个 `A1.E/A1.F/A1.K/A1.H` 或 D/I/U ID",
        "最多被一个 D/行动分面直接引用",
        "章节：“Overview”；章节：“Methods”",
        "稳定 `CH#`",
        "覆盖:<决策总体→观察框/框外处理>",
        "行粒度:<一行代表什么>",
        "成员键:<稳定键>",
        "权重:<抽样/汇总权重或无>",
        "操作数=",
        "支持位置=",
        "统计口径=",
        "保持=<其余五项>",
        "判定口径=",
        "所需字段=",
        "验收口径=",
        "依据快照=",
        "独立性=",
        "算法/阈值=",
        "效果识别",
        "运营容量成本",
        "权利法域遗漏",
        "最高价值下一项",
        "地图摘要` 最多五行",
        "字面序列化门",
        "消费者只包括直接写出该 E# 的 P/K/A 分面/D/I/R/U",
        "`AR6` 等版本文字不是 R#",
        "一个非 ID 单元格",
        "不得写 `[D4] D4",
        "取得阻断=",
        "操作化=",
        "对象:<成员规则>",
        "产物=<一个版本化数据或分析产物>",
        "生产位置=受影响者/一线/独立权利",
        "迁移=<对象/测量/尺度/人口/时期/情境>",
        "认识影响=",
        "未知：命题=",
        "不要用“已核实、已核验事实、部分支持",
        "权利状态=",
        "适配=",
        "一个 I 最多桥接一个迁移缺口",
        "互斥证明",
        "结果→更新",
        "不得据此直接实施",
        "S + C + 丢弃",
        "当前仍有效且可追溯",
        "事实发生期/数据期",
        "搜索摘要、聚合页和同源转载只能发现候选",
        "比较/基准",
        "机制→后果",
        "判定字段=",
        "主机制、竞争机制、机制判据",
        "字符/字节 dry-run",
        "依据快照=<带 v#/日期/hash",
        "普通专业交付按**语义合同**执行",
        "不发起新的模型回放",
    ):
        require(output_contract, marker, "output-contract.md")

    behavior = next(
        (
            item
            for item in behaviors
            if item["id"]
            == "unfamiliar-domain-budget-pressure-bounds-cognitive-loop"
        ),
        None,
    )
    if behavior is None:
        raise AssertionError("budget-pressure behavior contract is missing")
    if "continue searching after a hard cap" not in behavior["forbidden_side_effects"]:
        raise AssertionError("budget-pressure contract does not forbid overrun")
    if "wait indefinitely or repeatedly retry after runtime quota exhaustion" not in behavior["forbidden_side_effects"]:
        raise AssertionError("budget-pressure contract does not stop quota retry loops")

    behavior_ids = {item["id"] for item in behaviors}
    for behavior_id in (
        "ambient-micro-expands-open-list-without-research",
        "explicit-closed-list-suppresses-expansion",
    ):
        if behavior_id not in behavior_ids:
            raise AssertionError(f"missing open-set behavior contract: {behavior_id}")

    quality_case = next(
        (item for item in output_cases if item["skill"] == "cognitive-expansion"),
        None,
    )
    if quality_case is None or not any(
        "CE-BUDGET-EXHAUSTED" in criterion
        for criterion in quality_case["criteria"]
    ):
        raise AssertionError("output-quality contract does not cover budget exhaustion")

    print("Cognitive-expansion contract regression checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
