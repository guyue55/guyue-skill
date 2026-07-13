#!/usr/bin/env python3
"""Focused regression tests for Long Goal control-pack semantics."""

from __future__ import annotations

import contextlib
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import check_long_goal_pack as checker


def write_markdown(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def write_valid_fixture(root: Path) -> Path:
    goal_dir = root / "docs/goals/demo"
    phase_dir = goal_dir / "phases"
    evidence_dir = goal_dir / "evidence"
    phase_dir.mkdir(parents=True)
    evidence_dir.mkdir()
    goal_id = "GOAL-DEMO-001"

    baseline = evidence_dir / "baseline.txt"
    baseline.write_text("ready baseline\n", encoding="utf-8")
    risk_resolution = evidence_dir / "risk-resolution.txt"
    risk_resolution.write_text("risk resolved\n", encoding="utf-8")
    attempt_hashes: list[str] = []
    for index in range(1, 4):
        attempt = evidence_dir / f"attempt-{index:02}.txt"
        attempt.write_text(f"failed attempt {index}\n", encoding="utf-8")
        attempt_hashes.append(checker.file_sha256(attempt))

    ledger = goal_dir / "execution-ledger.md"
    write_markdown(
        ledger,
        f"""
        # Demo 执行账本

        ## 当前指针
        - 控制包版本：4
        - 当前控制修订：REV-0001
        - Goal ID：{goal_id}
        - 当前状态：就绪待执行
        - 当前阶段 ID：PHASE-01
        - 当前入口：执行 TASK-01
        - 最近有效提交：baseline-123
        - 最近新鲜证据：evidence/index.md
        - 当前阻塞：无
        - 停止原因：等待执行
        - 完成判定：未完成

        ## 状态转换
        - RUN-0001：铸造中 -> 就绪待执行

        ## 设计门失败记录
        | 尝试 ID | 控制修订 ID | 风险门 ID | 假设 ID | 实验 ID | 差异说明 | 失败证据 ID | 结论 |
        |---|---|---|---|---|---|---|---|

        ## 阶段记录
        ### RUN-0001 · 控制包就绪
        - 下一入口：执行 TASK-01
        """,
    )

    evidence = evidence_dir / "index.md"
    write_markdown(
        evidence,
        f"""
        # Demo 活体证据索引

        - Goal ID：{goal_id}

        | 证据 ID | 证据角色 | 覆盖承诺 | 证据路径 | 证据 SHA-256 | 实现版本 | 工作树状态 | 执行命令 | 退出码 | 生成时间 | 新鲜度对账 | 结果 |
        |---|---|---|---|---|---|---|---|---|---|---|---|
        | EVID-01 | FINAL | REQ-01 | docs/goals/demo/evidence/baseline.txt | {checker.file_sha256(baseline)} | baseline-123 | clean@baseline-123 | printf ok | 0 | 2026-07-10T00:00:00Z | 新鲜 | 通过 |
        | EVID-02 | ATTEMPT | RISK-01 | docs/goals/demo/evidence/attempt-01.txt | {attempt_hashes[0]} | baseline-123 | clean@baseline-123 | false | 1 | 2026-07-10T00:01:00Z | 历史 | 失败 |
        | EVID-03 | ATTEMPT | RISK-01 | docs/goals/demo/evidence/attempt-02.txt | {attempt_hashes[1]} | baseline-123 | clean@baseline-123 | false | 1 | 2026-07-10T00:02:00Z | 历史 | 失败 |
        | EVID-04 | ATTEMPT | RISK-01 | docs/goals/demo/evidence/attempt-03.txt | {attempt_hashes[2]} | baseline-123 | clean@baseline-123 | false | 1 | 2026-07-10T00:03:00Z | 历史 | 失败 |
        | EVID-05 | FINAL | RISK-01 | docs/goals/demo/evidence/risk-resolution.txt | {checker.file_sha256(risk_resolution)} | baseline-123 | clean@baseline-123 | printf resolved | 0 | 2026-07-10T00:04:00Z | 新鲜 | 通过 |
        """,
    )

    phase = phase_dir / "phase-01-baseline.md"
    write_markdown(
        phase,
        f"""
        # PHASE-01 基线

        - Goal ID：{goal_id}
        - 阶段 ID：PHASE-01
        - 状态：就绪待执行
        - 阶段目标：验证基线
        - 稳定输入：当前仓库
        - 依赖：无
        - 本阶段改动边界：只读检查
        - 本阶段不做：不发布
        - 定向检查：echo ok
        - 主线门禁：echo ok
        - 活体验收：读取真实产物
        - 失败处理：记录并阻塞
        - 回滚方式：无写入
        - 人工检查点：无
        - 阶段完成条件：REQ-01 与 RISK-01 通过
        - 下一入口：Goal 终局审查

        ## 工作项
        - TASK-01：执行基线验证。

        ## 副作用与重放
        | 任务 ID | 副作用 | 重放类别 | 核验或补偿 |
        |---|---|---|---|
        | TASK-01 | 无 | replay_safe | 重跑检查 |
        """,
    )

    master = goal_dir / "goal-master.md"
    write_markdown(
        master,
        f"""
        # Demo 总控

        ## 控制信息
        - 控制包版本：4
        - 当前控制修订：REV-0001
        - Goal ID：{goal_id}
        - 状态：就绪待执行
        - 唯一总控：本文件
        - 执行账本：`docs/goals/demo/execution-ledger.md`
        - 阶段计划目录：`docs/goals/demo/phases/`
        - 活体证据索引：`docs/goals/demo/evidence/index.md`
        - 基线提交或版本：baseline-123
        - 最后审查时间：2026-07-10T00:00:00Z

        ## 状态机
        - 正向：铸造中 -> 就绪待执行 -> 执行中 -> 终局候选 -> 完成
        - 恢复：执行中 -> 阻塞 -> 执行中
        - 设计复核：执行中 -> BLOCKED_DESIGN_REVIEW_REQUIRED；只有用户批准新修订后，BLOCKED_DESIGN_REVIEW_REQUIRED -> 执行中

        ## 控制权与三层时间尺度
        - 权威顺序：用户决定 > 仓库规则 > 本总控 > 阶段计划 > 执行账本
        - 当前控制基线：baseline-123
        - 替代或继承：无旧控制包；首次建立
        - 历史完成权：撤销；历史结果只作基线证据
        - 控制完整性边界：检查器通过只证明控制结构完整，不证明产品完成
        - 终极愿景：长期保持基线可信
        - 本 Goal 交付：完成一次可复跑的基线验证
        - 时间型结果：长期维护效果不在本 Goal 内宣称完成
        - 活跃控制文档上限：4
        - 控制包推翻条件：新事实证伪方向时暂停执行，由用户批准新修订后恢复

        ## 控制修订记录
        | 修订 ID | 前序修订 | 控制基线 | 批准动作 ID | 触发风险门 | 状态 | 变更原因 |
        |---|---|---|---|---|---|---|
        | REV-0001 | 无（首次建立） | baseline-123 | 无（首次建立） | 无（首次建立） | ACTIVE | 首次建立 |

        ## 活跃控制文档清单
        | 文档角色 | 仓库相对路径 |
        |---|---|
        | MASTER | docs/goals/demo/goal-master.md |
        | LEDGER | docs/goals/demo/execution-ledger.md |
        | PHASE | docs/goals/demo/phases/phase-01-baseline.md |
        | EVIDENCE_INDEX | docs/goals/demo/evidence/index.md |

        ## 认知与实验台账
        | 认知 ID | 类型 | 命题 | 当前证据 | 证伪或通过标准 | 关联项 | 失败或删除路径 |
        |---|---|---|---|---|---|---|
        | FACT-01 | VERIFIED_FACT | 仓库可读 | 文件存在 | 文件无法读取即证伪 | FDEC-01 | 回到项目摸底 |
        | FDEC-01 | FROZEN_DECISION | 本地验证优先 | 已确认范围 | 用户批准新修订才改变 | FACT-01 | 暂停并追加控制修订 |
        | HYP-01 | HYPOTHESIS | 单一基线足以验证链路 | 当前设计 | EXP-01 产物与哈希一致 | EXP-01 | 失败则删除假设并重做方案 |
        | EXP-01 | EXPERIMENT | 生成并复算基线证据 | 待执行 | 哈希一致且命令成功 | HYP-01 | 记录失败并修改最小机制 |
        | EXP-02 | EXPERIMENT | 更换输入样本复算证据 | 待执行 | 哈希一致且命令成功 | HYP-01 | 记录失败并修改最小机制 |
        | EXP-03 | EXPERIMENT | 更换验收路径复算证据 | 待执行 | 哈希一致且命令成功 | HYP-01 | 记录失败并进入设计复核 |

        ## 风险门与先纵切后扩张
        - 扩张规则：先纵切后扩张；GATE-01 未通过前不增加阶段或依赖。
        - 设计复核规则：同一风险门完成 3 次差异化实验仍失败，状态写为 BLOCKED_DESIGN_REVIEW_REQUIRED。

        | 风险门 ID | 用户结果 | 纵向切片 | 失败判据 | 放行证据 | 扩张权限 |
        |---|---|---|---|---|---|
        | GATE-01 | 基线可信 | 输入到证据复算 | 哈希不一致 | EVID-01 | 通过后才可扩张 |

        ## 阶段计划清单
        - `docs/goals/demo/phases/phase-01-baseline.md`

        ## 愿景与真实需求
        - 真实用户：维护者
        - 最终目标：基线可验证

        ## 项目现场
        - 已确认事实：仓库存在
        - 当前基线：baseline-123

        ## 范围契约
        - 必须完成：基线验证
        - 明确不做：发布

        ## 方案与取舍
        - 推荐方案：本地验证

        ## 阶段路线
        | 阶段 ID | 目标 | 交付物 |
        |---|---|---|
        | PHASE-01 | 验证基线 | 证据 |

        ## 承诺覆盖矩阵
        | 承诺 ID | 承诺或否定项 | 阶段 ID | 验证证据 |
        |---|---|---|---|
        | REQ-01 | 基线可验证 | PHASE-01 | EVID-01 |
        | RISK-01 | 基线证据可能不一致 | PHASE-01 | EVID-05 |

        ## 循环与预算
        - 最大修复轮数：2
        - 单阶段时间上限：30 分钟
        - Token 或上下文预算：只读定向检查
        - 子任务数量上限：1
        - 工具范围：本地只读
        - 缺证据熔断：立即阻塞
        - 重复运行要求：幂等

        ## 委派与收束
        - 委派判定：不委派；单 Agent 完成只读基线验证
        - 最大并发子任务：1
        - 单任务时间上限：20 分钟
        - 委派包：必须包含 Brief、所有权边界、基线版本、报告路径和审查包
        - 返回状态：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
        - 心跳与收束：两次无新证据即停止扩张并收束
        - 独立审查：终局由未参与实现的审查视角复核

        | 任务 ID | Brief | 所有权与可改范围 | 明确不做 | 基线版本 | 报告路径 | 审查包 | 收束预算 |
        |---|---|---|---|---|---|---|---|

        ## 主线验证门
        - 测试：echo ok
        - 真实运行：读取证据

        ## 最终完成定义
        - 正向条件：REQ-01 与 RISK-01 通过
        - 否定清单：不得伪造证据
        - 完成边界：仅本 Goal 的基线验证；不得外推为终极愿景或时间型结果完成

        ## 风险、授权与停止条件
        | 动作 ID | 风险或动作 | 版本或摘要哈希 | 有效期或失效条件 | 是否需要人工授权 | 授权状态 | 授权证据 |
        |---|---|---|---|---|---|---|
        | ACT-01 | 发布 | plan-v1 | 计划变化即失效 | 是 | PENDING | 待授权 |

        ## 恢复协议
        1. 读取账本。
        2. 从 TASK-01 继续。

        ## 终局封账顺序
        - 实现提交：待生成
        - 证据提交：待生成
        - 封账定位：待生成
        1. 完成报告、提交实现并从 clean 基线生成新鲜证据。
        2. 由独立验证者复算后提交证据。
        3. 最后只更新总控与账本状态。
        """,
    )
    return master


def convert_fixture_to_v3(master: Path) -> Path:
    ledger = master.parent / "execution-ledger.md"
    evidence = master.parent / "evidence/index.md"
    master_text = master.read_text(encoding="utf-8")
    ledger_text = ledger.read_text(encoding="utf-8")
    master_text = master_text.replace("- 控制包版本：4", "- 控制包版本：3", 1)
    master_text = re.sub(
        r"(?ms)^## 控制权与三层时间尺度\s*$.*?(?=^## 阶段计划清单)",
        "",
        master_text,
    )
    master_text = re.sub(
        r"(?ms)^## 终局封账顺序\s*$.*\Z", "", master_text
    )
    master_text = re.sub(r"(?m)^- 设计复核：.*$\n?", "", master_text)
    master_text = re.sub(r"(?m)^- 当前控制修订：.*$\n?", "", master_text)
    ledger_text = ledger_text.replace("- 控制包版本：4", "- 控制包版本：3", 1)
    ledger_text = re.sub(r"(?m)^- 当前控制修订：.*$\n?", "", ledger_text)
    ledger_text = re.sub(
        r"(?ms)^## 设计门失败记录\s*$.*?(?=^## 阶段记录)",
        "",
        ledger_text,
    )
    master.write_text(master_text, encoding="utf-8")
    ledger.write_text(ledger_text, encoding="utf-8")
    evidence_lines: list[str] = []
    for line in evidence.read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            cells = checker.split_markdown_table_row(line)
            if len(cells) >= 2 and (
                cells[1] == "证据角色" or checker.EVIDENCE_ID_RE.fullmatch(cells[0])
            ):
                del cells[1]
                line = "| " + " | ".join(cells) + " |"
            elif len(cells) == 12 and all(cell == "---" for cell in cells):
                del cells[1]
                line = "|" + "|".join(cells) + "|"
        evidence_lines.append(line)
    evidence.write_text("\n".join(evidence_lines) + "\n", encoding="utf-8")
    return ledger


def convert_fixture_to_v2(master: Path) -> Path:
    ledger = convert_fixture_to_v3(master)
    evidence = master.parent / "evidence/index.md"
    master_text = master.read_text(encoding="utf-8")
    master_text = master_text.replace("- 控制包版本：3", "- 控制包版本：2", 1)
    master_text = re.sub(
        r"(?ms)^## 委派与收束\s*$.*?(?=^## 主线验证门)",
        "",
        master_text,
    )
    master_text = re.sub(r"(?m)^\| RISK-01 \|.*$\n?", "", master_text)
    master.write_text(master_text, encoding="utf-8")
    ledger.write_text(
        ledger.read_text(encoding="utf-8").replace(
            "- 控制包版本：3", "- 控制包版本：2", 1
        ),
        encoding="utf-8",
    )
    write_markdown(
        evidence,
        """
        # Demo 活体证据索引

        - Goal ID：GOAL-DEMO-001

        | 证据 ID | 覆盖承诺 | 证据路径 | 来源版本 | 生成时间 | 新鲜度对账 | 复跑方式 | 结果 |
        |---|---|---|---|---|---|---|---|
        | EVID-01 | REQ-01 | docs/goals/demo/evidence/baseline.txt | baseline-123 | 2026-07-10T00:00:00Z | 新鲜 | printf ok | 通过 |
        """,
    )
    return ledger


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()


@contextlib.contextmanager
def isolated_git_environment():
    keys = ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE")
    previous = {key: os.environ.get(key) for key in keys}
    for key in keys:
        os.environ.pop(key, None)
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def update_final_evidence(
    index: Path,
    implementation_commit: str,
    *,
    worktree_state: str | None = None,
    freshness: str = "新鲜",
) -> None:
    lines: list[str] = []
    for line in index.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            lines.append(line)
            continue
        cells = checker.split_markdown_table_row(line)
        if len(cells) >= 12 and checker.EVIDENCE_ID_RE.fullmatch(cells[0]) and cells[1] == "FINAL":
            artifact = index.parents[4] / cells[3]
            cells[4] = checker.file_sha256(artifact)
            cells[5] = implementation_commit
            cells[6] = worktree_state or f"clean@{implementation_commit}"
            cells[9] = "2026-07-10T01:00:00Z"
            cells[10] = freshness
            line = "| " + " | ".join(cells) + " |"
        lines.append(line)
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_complete_git_pack(
    root: Path,
    *,
    forbidden_evidence_change: bool = False,
    descendant_commit: bool = False,
    external_final_state: bool = False,
    dirty_final_state: bool = False,
    final_freshness: str = "新鲜",
) -> tuple[Path, str, str, str]:
    master = write_valid_fixture(root)
    ledger = master.parent / "execution-ledger.md"
    phase = master.parent / "phases/phase-01-baseline.md"
    phase.write_text(
        phase.read_text(encoding="utf-8").replace(
            "- 状态：就绪待执行", "- 状态：完成", 1
        ),
        encoding="utf-8",
    )
    master.write_text(
        master.read_text(encoding="utf-8").replace(
            "- 状态：就绪待执行", "- 状态：终局候选", 1
        ),
        encoding="utf-8",
    )
    ledger.write_text(
        ledger.read_text(encoding="utf-8").replace(
            "- 当前状态：就绪待执行", "- 当前状态：终局候选", 1
        ),
        encoding="utf-8",
    )

    run_git(root, "init", "-q")
    run_git(root, "config", "user.name", "Guyue Test")
    run_git(root, "config", "user.email", "guyue-test@example.invalid")
    run_git(root, "add", ".")
    run_git(root, "commit", "-qm", "test: implementation")
    implementation_commit = run_git(root, "rev-parse", "HEAD")

    baseline = master.parent / "evidence/baseline.txt"
    baseline.write_text("verified implementation output\n", encoding="utf-8")
    risk_resolution = master.parent / "evidence/risk-resolution.txt"
    risk_resolution.write_text("verified risk resolution\n", encoding="utf-8")
    update_final_evidence(
        master.parent / "evidence/index.md",
        implementation_commit,
        worktree_state=(
            "external@prod-snapshot"
            if external_final_state
            else "dirty@candidate"
            if dirty_final_state
            else None
        ),
        freshness=final_freshness,
    )
    if forbidden_evidence_change:
        (root / "forbidden-source.txt").write_text(
            "must not be in the evidence commit\n", encoding="utf-8"
        )
    run_git(root, "add", ".")
    run_git(root, "commit", "-qm", "test: evidence")
    evidence_commit = run_git(root, "rev-parse", "HEAD")

    master_text = master.read_text(encoding="utf-8")
    master_text = master_text.replace("- 状态：终局候选", "- 状态：完成", 1)
    master_text = master_text.replace(
        "- 实现提交：待生成", f"- 实现提交：{implementation_commit}", 1
    )
    master_text = master_text.replace(
        "- 证据提交：待生成", f"- 证据提交：{evidence_commit}", 1
    )
    master_text = master_text.replace(
        "- 封账定位：待生成", "- 封账定位：derived@master+ledger", 1
    )
    master.write_text(master_text, encoding="utf-8")

    ledger_text = ledger.read_text(encoding="utf-8")
    ledger_text = ledger_text.replace("- 当前状态：终局候选", "- 当前状态：完成", 1)
    ledger_text = ledger_text.replace(
        "- 当前阶段 ID：PHASE-01", "- 当前阶段 ID：无（Goal complete）", 1
    )
    ledger_text = ledger_text.replace(
        "- 当前入口：执行 TASK-01", "- 当前入口：无（Goal complete）", 1
    )
    ledger_text = ledger_text.replace(
        "- 停止原因：等待执行", "- 停止原因：全部终局条件满足", 1
    )
    ledger_text = ledger_text.replace("- 完成判定：未完成", "- 完成判定：通过", 1)
    ledger.write_text(ledger_text, encoding="utf-8")
    run_git(root, "add", str(master.relative_to(root)), str(ledger.relative_to(root)))
    run_git(root, "commit", "-qm", "test: seal")
    seal_commit = run_git(root, "rev-parse", "HEAD")

    if descendant_commit:
        (root / "post-seal.txt").write_text(
            "unrelated descendant commit\n", encoding="utf-8"
        )
        run_git(root, "add", "post-seal.txt")
        run_git(root, "commit", "-qm", "test: unrelated descendant")

    return master, implementation_commit, evidence_commit, seal_commit


def add_failure_rows(ledger: Path) -> None:
    rows = (
        "| TRY-01 | REV-0001 | GATE-01 | HYP-01 | EXP-01 | 改变机制 | EVID-01 | 失败 |\n"
        "| TRY-02 | REV-0001 | GATE-01 | HYP-01 | EXP-02 | 改变样本 | EVID-01 | 失败 |\n"
        "| TRY-03 | REV-0001 | GATE-01 | HYP-01 | EXP-03 | 改变判据 | EVID-01 | 失败 |\n"
    )
    text = ledger.read_text(encoding="utf-8").replace(
        "|---|---|---|---|---|---|---|---|\n\n## 阶段记录",
        "|---|---|---|---|---|---|---|---|\n" + rows + "\n## 阶段记录",
    )
    ledger.write_text(text, encoding="utf-8")


def add_valid_failure_rows(ledger: Path) -> None:
    rows = (
        "| TRY-01 | REV-0001 | GATE-01 | HYP-01 | EXP-01 | 改变机制 | EVID-02 | 失败 |\n"
        "| TRY-02 | REV-0001 | GATE-01 | HYP-01 | EXP-02 | 改变样本 | EVID-03 | 失败 |\n"
        "| TRY-03 | REV-0001 | GATE-01 | HYP-01 | EXP-03 | 改变判据 | EVID-04 | 失败 |\n"
    )
    text = ledger.read_text(encoding="utf-8").replace(
        "|---|---|---|---|---|---|---|---|\n\n## 阶段记录",
        "|---|---|---|---|---|---|---|---|\n" + rows + "\n## 阶段记录",
    )
    ledger.write_text(text, encoding="utf-8")


def add_decision_evidence(
    master: Path,
    *,
    role: str = "FINAL",
    result: str = "通过",
    freshness: str = "新鲜",
) -> None:
    artifact = master.parent / "evidence/revision-approval.txt"
    artifact.write_text("REV-0002 approved\n", encoding="utf-8")
    evidence = master.parent / "evidence/index.md"
    exit_code = "0" if result == "通过" else "1"
    row = (
        f"| EVID-06 | {role} | DEC-01 | docs/goals/demo/evidence/revision-approval.txt | "
        f"{checker.file_sha256(artifact)} | baseline-123 | clean@baseline-123 | "
        f"printf approved | {exit_code} | 2026-07-10T00:05:00Z | {freshness} | {result} |"
    )
    evidence.write_text(
        evidence.read_text(encoding="utf-8").rstrip() + "\n" + row + "\n",
        encoding="utf-8",
    )


def apply_approved_revision_recovery(
    master: Path,
    *,
    decision_role: str = "FINAL",
    decision_result: str = "通过",
    decision_freshness: str = "新鲜",
    add_failure_history: bool = True,
) -> None:
    ledger = master.parent / "execution-ledger.md"
    if add_failure_history:
        add_valid_failure_rows(ledger)
    add_decision_evidence(
        master,
        role=decision_role,
        result=decision_result,
        freshness=decision_freshness,
    )

    master_text = master.read_text(encoding="utf-8")
    master_text = master_text.replace(
        "- 当前控制修订：REV-0001", "- 当前控制修订：REV-0002", 1
    )
    master_text = master_text.replace("- 状态：就绪待执行", "- 状态：执行中", 1)
    master_text = master_text.replace(
        "| REV-0001 | 无（首次建立） | baseline-123 | 无（首次建立） | 无（首次建立） | ACTIVE | 首次建立 |",
        "| REV-0001 | 无（首次建立） | baseline-123 | 无（首次建立） | 无（首次建立） | SUPERSEDED | 首次建立 |\n"
        "| REV-0002 | REV-0001 | baseline-456 | ACT-02 | GATE-01 | ACTIVE | 用户批准设计修正 |",
    )
    master_text = master_text.replace(
        "| REQ-01 | 基线可验证 | PHASE-01 | EVID-01 |",
        "| REQ-01 | 基线可验证 | PHASE-01 | EVID-01 |\n"
        "| DEC-01 | 批准 REV-0002 | PHASE-01 | EVID-06 |",
    )
    master_text = master_text.replace(
        "| ACT-01 | 发布 | plan-v1 | 计划变化即失效 | 是 | PENDING | 待授权 |",
        "| ACT-01 | 发布 | plan-v1 | 计划变化即失效 | 是 | PENDING | 待授权 |\n"
        "| ACT-02 | 批准控制修订 | rev-0002 | 修订变化即失效 | 是 | APPROVED | DEC-01 |",
    )
    master.write_text(master_text, encoding="utf-8")

    ledger_text = ledger.read_text(encoding="utf-8")
    ledger_text = ledger_text.replace(
        "- 当前控制修订：REV-0001", "- 当前控制修订：REV-0002", 1
    )
    ledger_text = ledger_text.replace(
        "- 当前状态：就绪待执行", "- 当前状态：执行中", 1
    )
    ledger_text = ledger_text.replace(
        "## 状态转换\n- RUN-0001：铸造中 -> 就绪待执行",
        "## 状态转换\n- RUN-0001：铸造中 -> 就绪待执行\n"
        "- RUN-0002：BLOCKED_DESIGN_REVIEW_REQUIRED -> 执行中；修订 REV-0002；批准 ACT-02",
    )
    ledger.write_text(ledger_text, encoding="utf-8")


class LongGoalSemanticRegressionTests(unittest.TestCase):
    def test_attempt_evidence_accepts_an_honest_dirty_worktree_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            evidence = master.parent / "evidence/index.md"
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace(
                    "clean@baseline-123 | false",
                    "dirty@experiment | false",
                    1,
                ),
                encoding="utf-8",
            )
            self.assertEqual(checker.validate_pack(master, root, "ready"), [])

    def test_cli_accepts_an_external_target_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_valid_fixture(root)
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(checker.__file__).resolve()),
                    "--repo-root",
                    str(root),
                    "--mode",
                    "ready",
                    "docs/goals/demo/goal-master.md",
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_rejects_a_master_outside_the_target_repository(self) -> None:
        with (
            tempfile.TemporaryDirectory() as repo_dir,
            tempfile.TemporaryDirectory() as outside_dir,
        ):
            outside_master = write_valid_fixture(Path(outside_dir))
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(checker.__file__).resolve()),
                    "--repo-root",
                    repo_dir,
                    str(outside_master),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must stay inside --repo-root", result.stderr)

    def test_valid_ready_pack_and_legacy_versions(self) -> None:
        for version in (4, 3, 2):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                master = write_valid_fixture(root)
                if version == 3:
                    convert_fixture_to_v3(master)
                elif version == 2:
                    convert_fixture_to_v2(master)
                self.assertEqual(checker.validate_pack(master, root, "ready"), [])

    def test_promise_cannot_reference_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "| REQ-01 | 基线可验证 | PHASE-01 | EVID-01 |",
                    "| REQ-01 | 基线可验证 | PHASE-01 | EVID-99 |",
                ),
                encoding="utf-8",
            )
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("absent from the index" in error for error in errors), errors)

    def test_duplicate_promise_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "| RISK-01 | 基线证据可能不一致 | PHASE-01 | EVID-05 |",
                    "| RISK-01 | 基线证据可能不一致 | PHASE-01 | EVID-05 |\n"
                    "| REQ-01 | 重复承诺 | PHASE-01 | EVID-01 |",
                ),
                encoding="utf-8",
            )
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("duplicate promise IDs" in error for error in errors), errors)

    def test_v4_evidence_cannot_reference_undeclared_promise(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            evidence = master.parent / "evidence/index.md"
            evidence.write_text(
                evidence.read_text(encoding="utf-8").replace(
                    "| EVID-02 | ATTEMPT | RISK-01 |",
                    "| EVID-02 | ATTEMPT | DEC-99 |",
                ),
                encoding="utf-8",
            )
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("undeclared promise" in error for error in errors), errors)

    def test_risk_gate_cannot_reference_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "| GATE-01 | 基线可信 | 输入到证据复算 | 哈希不一致 | EVID-01 |",
                    "| GATE-01 | 基线可信 | 输入到证据复算 | 哈希不一致 | EVID-99 |",
                ),
                encoding="utf-8",
            )
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("risk gate GATE-01" in error for error in errors), errors)

    def test_approved_revision_preserves_failures_and_recovers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            apply_approved_revision_recovery(master)
            self.assertEqual(checker.validate_pack(master, root, "resume"), [])

    def test_failed_attempt_cannot_authorize_revision_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            apply_approved_revision_recovery(
                master,
                decision_role="ATTEMPT",
                decision_result="失败",
            )
            errors = checker.validate_pack(master, root, "resume")
            self.assertTrue(
                any("fresh passing FINAL decision evidence" in error for error in errors),
                errors,
            )

    def test_stale_final_cannot_authorize_revision_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            apply_approved_revision_recovery(
                master,
                decision_freshness="不新鲜",
            )
            errors = checker.validate_pack(master, root, "resume")
            self.assertTrue(
                any("fresh passing FINAL decision evidence" in error for error in errors),
                errors,
            )

    def test_three_differentiated_failures_force_design_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            ledger = master.parent / "execution-ledger.md"
            add_valid_failure_rows(ledger)
            errors = checker.validate_pack(master, root, "resume")
            self.assertTrue(
                any("must enter BLOCKED_DESIGN_REVIEW_REQUIRED" in error for error in errors),
                errors,
            )

    def test_valid_design_review_block_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            ledger = master.parent / "execution-ledger.md"
            add_valid_failure_rows(ledger)
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "- 状态：就绪待执行",
                    f"- 状态：{checker.DESIGN_REVIEW_BLOCKED}",
                    1,
                ),
                encoding="utf-8",
            )
            ledger.write_text(
                ledger.read_text(encoding="utf-8").replace(
                    "- 当前状态：就绪待执行",
                    f"- 当前状态：{checker.DESIGN_REVIEW_BLOCKED}",
                    1,
                ),
                encoding="utf-8",
            )
            self.assertEqual(checker.validate_pack(master, root, "resume"), [])

    def test_v3_rejects_v4_design_review_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            ledger = convert_fixture_to_v3(master)
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "- 状态：就绪待执行",
                    f"- 状态：{checker.DESIGN_REVIEW_BLOCKED}",
                    1,
                ),
                encoding="utf-8",
            )
            ledger.write_text(
                ledger.read_text(encoding="utf-8").replace(
                    "- 当前状态：就绪待执行",
                    f"- 当前状态：{checker.DESIGN_REVIEW_BLOCKED}",
                    1,
                ),
                encoding="utf-8",
            )

            errors = checker.validate_pack(master, root, "resume")
            self.assertTrue(
                any("invalid state" in error for error in errors),
                errors,
            )

    def test_passing_evidence_cannot_count_as_failed_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            ledger = master.parent / "execution-ledger.md"
            add_failure_rows(ledger)
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "- 状态：就绪待执行",
                    f"- 状态：{checker.DESIGN_REVIEW_BLOCKED}",
                    1,
                ),
                encoding="utf-8",
            )
            ledger.write_text(
                ledger.read_text(encoding="utf-8").replace(
                    "- 当前状态：就绪待执行",
                    f"- 当前状态：{checker.DESIGN_REVIEW_BLOCKED}",
                    1,
                ),
                encoding="utf-8",
            )

            errors = checker.validate_pack(master, root, "resume")
            self.assertTrue(
                any("failure evidence" in error for error in errors),
                errors,
            )

    def test_active_document_limit_rejects_unregistered_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            notes = master.parent / "notes"
            notes.mkdir()
            for index in range(20):
                (notes / f"note-{index:02}.md").write_text(
                    f"# Note {index}\n", encoding="utf-8"
                )

            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(
                any("active control document" in error for error in errors),
                errors,
            )

    def test_active_document_roles_cannot_be_swapped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            text = master.read_text(encoding="utf-8")
            text = text.replace(
                "| MASTER | docs/goals/demo/goal-master.md |\n"
                "| LEDGER | docs/goals/demo/execution-ledger.md |",
                "| MASTER | docs/goals/demo/execution-ledger.md |\n"
                "| LEDGER | docs/goals/demo/goal-master.md |",
            )
            master.write_text(text, encoding="utf-8")
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("does not match" in error for error in errors), errors)

    def test_control_revision_chain_cannot_fork_or_reuse_approval(self) -> None:
        text = """
        - 当前控制修订：REV-0003

        ## 控制修订记录
        | 修订 ID | 前序修订 | 控制基线 | 批准动作 ID | 触发风险门 | 状态 | 变更原因 |
        |---|---|---|---|---|---|---|
        | REV-0001 | 无（首次建立） | base-1 | 无（首次建立） | 无（首次建立） | SUPERSEDED | 首次建立 |
        | REV-0002 | REV-0001 | base-2 | ACT-02 | 无（主动修订） | SUPERSEDED | 主动修订 |
        | REV-0003 | REV-0001 | base-3 | ACT-02 | 无（主动修订） | ACTIVE | 错误分叉 |
        """
        approvals = {
            "ACT-02": [
                "ACT-02",
                "批准修订",
                "rev-2",
                "修订变化即失效",
                "是",
                "APPROVED",
                "DEC-01",
            ]
        }
        errors: list[str] = []
        checker.validate_control_revisions(
            textwrap.dedent(text), approvals, set(), errors
        )
        self.assertTrue(any("directly follow" in error for error in errors), errors)
        self.assertTrue(any("reuses an approval" in error for error in errors), errors)

    def test_missing_delegation_and_meta_control_are_rejected(self) -> None:
        mutations = (
            (
                r"(?ms)^## 委派与收束\s*$.*?(?=^## 主线验证门)",
                "委派与收束",
            ),
            (
                r"(?ms)^## 控制权与三层时间尺度\s*$.*?(?=^## 认知与实验台账)",
                "meta-control",
            ),
        )
        for pattern, marker in mutations:
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                master = write_valid_fixture(root)
                master.write_text(
                    re.sub(pattern, "", master.read_text(encoding="utf-8")),
                    encoding="utf-8",
                )
                errors = checker.validate_pack(master, root, "ready")
                self.assertTrue(any(marker in error for error in errors), errors)

    def test_unlinked_hypothesis_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "EXP-01 产物与哈希一致 | EXP-01 |",
                    "产物与哈希一致 | FDEC-01 |",
                    1,
                ),
                encoding="utf-8",
            )
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("must link" in error for error in errors), errors)

    def test_duplicate_evidence_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            evidence = master.parent / "evidence/index.md"
            text = evidence.read_text(encoding="utf-8")
            duplicate = next(line for line in text.splitlines() if line.startswith("| EVID-01"))
            evidence.write_text(text.rstrip() + "\n" + duplicate + "\n", encoding="utf-8")
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("duplicate evidence IDs" in error for error in errors), errors)

    def test_orphan_delegation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            text = master.read_text(encoding="utf-8")
            text = text.replace(
                "|---|---|---|---|---|---|---|---|\n\n## 主线验证门",
                "|---|---|---|---|---|---|---|---|\n"
                "| TASK-99 | 独立检查 | docs | 不改代码 | baseline-123 | reports/task-99.md | reviews/task-99.md | 1 轮 |\n\n"
                "## 主线验证门",
            ).replace("- 委派判定：不委派；", "- 委派判定：可委派；")
            master.write_text(text, encoding="utf-8")
            errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("absent from phase plans" in error for error in errors), errors)

    def test_invalid_replay_and_unlisted_phase_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            phase = master.parent / "phases/phase-01-baseline.md"
            original = phase.read_text(encoding="utf-8")
            phase.write_text(original.replace("replay_safe", "unknown"), encoding="utf-8")
            replay_errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(any("replay" in error for error in replay_errors), replay_errors)
            phase.write_text(original, encoding="utf-8")
            unlisted = master.parent / "phases/phase-02-unlisted.md"
            unlisted.write_text(original.replace("PHASE-01", "PHASE-02"), encoding="utf-8")
            phase_errors = checker.validate_pack(master, root, "ready")
            self.assertTrue(
                any("not explicitly referenced" in error for error in phase_errors),
                phase_errors,
            )

    def test_fake_git_seal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            ledger = master.parent / "execution-ledger.md"
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "- 状态：就绪待执行", "- 状态：完成", 1
                ),
                encoding="utf-8",
            )
            ledger_text = ledger.read_text(encoding="utf-8")
            ledger_text = ledger_text.replace(
                "- 当前状态：就绪待执行", "- 当前状态：完成"
            )
            ledger_text = ledger_text.replace(
                "- 当前阶段 ID：PHASE-01", "- 当前阶段 ID：无（Goal complete）"
            )
            ledger_text = ledger_text.replace(
                "- 当前入口：执行 TASK-01", "- 当前入口：无（Goal complete）"
            )
            ledger_text = ledger_text.replace(
                "- 停止原因：等待执行", "- 停止原因：全部终局条件满足"
            )
            ledger_text = ledger_text.replace(
                "- 完成判定：未完成", "- 完成判定：通过"
            )
            ledger.write_text(ledger_text, encoding="utf-8")

            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("Git seal" in error for error in errors), errors)

    def test_complete_requires_every_phase_to_be_complete(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            ledger = master.parent / "execution-ledger.md"
            master.write_text(
                master.read_text(encoding="utf-8").replace(
                    "- 状态：就绪待执行", "- 状态：完成", 1
                ),
                encoding="utf-8",
            )
            ledger_text = ledger.read_text(encoding="utf-8")
            ledger_text = ledger_text.replace("- 当前状态：就绪待执行", "- 当前状态：完成")
            ledger_text = ledger_text.replace("- 当前入口：执行 TASK-01", "- 当前入口：无（Goal complete）")
            ledger_text = ledger_text.replace("- 停止原因：等待执行", "- 停止原因：全部终局条件满足")
            ledger_text = ledger_text.replace("- 完成判定：未完成", "- 完成判定：通过")
            ledger.write_text(ledger_text, encoding="utf-8")
            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("phase-01-baseline.md` must be complete" in error for error in errors), errors)

    def test_escaped_pipe_remains_inside_one_markdown_cell(self) -> None:
        cells = checker.table_cells(
            "| 证据 ID | 执行命令 | 结果 |\n"
            "|---|---|---|\n"
            r"| EVID-01 | printf ok \| grep ok | 通过 |" + "\n"
        )
        self.assertEqual(cells, [["EVID-01", "printf ok | grep ok", "通过"]])

    def test_non_pipe_backslashes_are_preserved_in_markdown_cells(self) -> None:
        cells = checker.table_cells(
            "| 证据 ID | 执行命令 | 结果 |\n"
            "|---|---|---|\n"
            r"| EVID-01 | printf '\n' C:\tmp | 通过 |" + "\n"
        )
        self.assertEqual(cells, [["EVID-01", r"printf '\n' C:\tmp", "通过"]])

    def test_freshness_requires_a_canonical_positive_status(self) -> None:
        self.assertTrue(checker.is_fresh("新鲜：基于当前实现复算"))
        for value in ("不新鲜", "非新鲜", "过期", "陈旧", "尚未证明新鲜"):
            with self.subTest(value=value):
                self.assertFalse(checker.is_fresh(value))


class LongGoalGitSealTests(unittest.TestCase):
    def test_real_git_seal_survives_unrelated_descendant_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, isolated_git_environment():
            root = Path(temp_dir)
            master, _, _, _ = prepare_complete_git_pack(
                root, descendant_commit=True
            )
            self.assertEqual(checker.validate_pack(master, root, "complete"), [])

    def test_git_seal_rejects_forbidden_evidence_commit_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, isolated_git_environment():
            root = Path(temp_dir)
            master, _, _, _ = prepare_complete_git_pack(
                root, forbidden_evidence_change=True
            )
            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("forbidden path" in error for error in errors), errors)

    def test_git_seal_rejects_external_final_evidence_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, isolated_git_environment():
            root = Path(temp_dir)
            master, _, _, _ = prepare_complete_git_pack(
                root, external_final_state=True
            )
            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("captured from clean@" in error for error in errors), errors)

    def test_git_seal_rejects_dirty_final_evidence_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, isolated_git_environment():
            root = Path(temp_dir)
            master, _, _, _ = prepare_complete_git_pack(
                root, dirty_final_state=True
            )
            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("captured from clean@" in error for error in errors), errors)

    def test_complete_rejects_negated_freshness_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, isolated_git_environment():
            root = Path(temp_dir)
            master, _, _, _ = prepare_complete_git_pack(
                root, final_freshness="不新鲜"
            )
            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("is not fresh" in error for error in errors), errors)

    def test_git_seal_rejects_post_seal_evidence_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, isolated_git_environment():
            root = Path(temp_dir)
            master, implementation, _, _ = prepare_complete_git_pack(root)
            baseline = master.parent / "evidence/baseline.txt"
            baseline.write_text("mutated after sealing\n", encoding="utf-8")
            update_final_evidence(master.parent / "evidence/index.md", implementation)
            run_git(root, "add", ".")
            run_git(root, "commit", "-qm", "test: mutate sealed evidence")
            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("commit history" in error for error in errors), errors)

    def test_git_seal_rejects_mutation_even_after_content_is_restored(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, isolated_git_environment():
            root = Path(temp_dir)
            master, implementation, evidence_commit, _ = prepare_complete_git_pack(root)
            baseline_rel = "docs/goals/demo/evidence/baseline.txt"
            index_rel = "docs/goals/demo/evidence/index.md"
            (root / baseline_rel).write_text("temporary mutation\n", encoding="utf-8")
            update_final_evidence(master.parent / "evidence/index.md", implementation)
            run_git(root, "add", baseline_rel, index_rel)
            run_git(root, "commit", "-qm", "test: mutate sealed evidence")
            run_git(
                root,
                "restore",
                "--source",
                evidence_commit,
                "--",
                baseline_rel,
                index_rel,
            )
            run_git(root, "add", baseline_rel, index_rel)
            run_git(root, "commit", "-qm", "test: restore sealed evidence")
            errors = checker.validate_pack(master, root, "complete")
            self.assertTrue(any("commit history" in error for error in errors), errors)


def run_self_test() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(run_self_test())
