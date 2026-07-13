#!/usr/bin/env python3
"""Validate Long Goal control packs for handoff, recovery, or completion."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
GOAL_ID_RE = re.compile(r"^GOAL-[A-Z0-9][A-Z0-9-]*$")
PHASE_ID_RE = re.compile(r"^PHASE-[0-9]{2,}$")
RUN_ID_RE = re.compile(r"RUN-[0-9]{4,}")
REQUIREMENT_ID_RE = re.compile(r"(?:REQ|NREQ|RISK|DEC)-[0-9]{2,}")
EVIDENCE_ID_RE = re.compile(r"EVID-[0-9]{2,}")
ACTION_ID_RE = re.compile(r"ACT-[0-9]{2,}")
REVISION_ID_RE = re.compile(r"REV-[0-9]{4,}")
SHA256_RE = re.compile(r"[a-f0-9]{64}")
GIT_OBJECT_ID_RE = re.compile(r"(?:[a-f0-9]{40}|[a-f0-9]{64})")
ISO_TIME_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})"
)
FRESHNESS_STATUS_RE = re.compile(
    r"^(新鲜|过期|不新鲜|非新鲜|陈旧)(?:$|[：:；;（(，,\s])"
)
WORKTREE_STATE_RE = re.compile(r"(?:clean|dirty|external)@.+")

LATEST_CONTROL_PACK_VERSION = "4"
SUPPORTED_CONTROL_PACK_VERSIONS = {"2", "3", LATEST_CONTROL_PACK_VERSION}

DESIGN_REVIEW_BLOCKED = "BLOCKED_DESIGN_REVIEW_REQUIRED"
BASE_STATES = (
    "铸造中",
    "就绪待执行",
    "执行中",
    "阻塞",
    "终局候选",
    "完成",
)
REPLAY_CLASSES = {
    "replay_safe",
    "verify_before_repeat",
    "compensate",
    "human_required",
}

MASTER_FIELDS = (
    "控制包版本",
    "Goal ID",
    "状态",
    "执行账本",
    "阶段计划目录",
    "活体证据索引",
    "基线提交或版本",
    "最后审查时间",
)
MASTER_SECTIONS = (
    "控制信息",
    "状态机",
    "阶段计划清单",
    "愿景与真实需求",
    "项目现场",
    "范围契约",
    "方案与取舍",
    "阶段路线",
    "承诺覆盖矩阵",
    "循环与预算",
    "主线验证门",
    "最终完成定义",
    "风险、授权与停止条件",
    "恢复协议",
)
V3_MASTER_SECTIONS = ("委派与收束",)
V4_MASTER_SECTIONS = (
    "控制权与三层时间尺度",
    "控制修订记录",
    "活跃控制文档清单",
    "认知与实验台账",
    "风险门与先纵切后扩张",
    "终局封账顺序",
)
LEDGER_FIELDS = (
    "控制包版本",
    "Goal ID",
    "当前状态",
    "当前阶段 ID",
    "当前入口",
    "最近有效提交",
    "最近新鲜证据",
    "当前阻塞",
    "停止原因",
    "完成判定",
)
PHASE_FIELDS = (
    "Goal ID",
    "阶段 ID",
    "状态",
    "阶段目标",
    "稳定输入",
    "依赖",
    "本阶段改动边界",
    "本阶段不做",
    "定向检查",
    "主线门禁",
    "活体验收",
    "失败处理",
    "回滚方式",
    "人工检查点",
    "阶段完成条件",
    "下一入口",
)


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def field_value(text: str, label: str) -> str | None:
    match = re.search(
        rf"(?m)^- {re.escape(label)}[：:]\s*(.+?)\s*$",
        text,
    )
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        value = value[1:-1].strip()
    return value


def field_path(text: str, label: str) -> str | None:
    value = field_value(text, label)
    if not value or any(char in value for char in "\r\n"):
        return None
    return value


def resolve_repo_path(repo_root: Path, rel_path: str, errors: list[str]) -> Path | None:
    path = (repo_root / rel_path).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError:
        errors.append(f"path escapes repository: {rel_path}")
        return None
    return path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_fresh(value: str) -> bool:
    match = FRESHNESS_STATUS_RE.match(value.strip())
    return bool(match and match.group(1) == "新鲜")


def git_result(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def resolve_git_commit(repo_root: Path, value: str) -> str | None:
    result = git_result(repo_root, "rev-parse", "--verify", f"{value}^{{commit}}")
    return result.stdout.strip() if result.returncode == 0 else None


def validate_git_seal(
    master_path: Path,
    master_text: str,
    ledger_path: Path,
    evidence_by_id: dict[str, list[str]],
    repo_root: Path,
    errors: list[str],
) -> None:
    sealing = section(master_text, "终局封账顺序")
    implementation_value = field_value(sealing, "实现提交") or ""
    evidence_value = field_value(sealing, "证据提交") or ""
    seal_locator = field_value(sealing, "封账定位") or ""
    if any(
        value in {"", "待生成", "待对账"}
        for value in (implementation_value, evidence_value, seal_locator)
    ):
        errors.append("Git seal is missing implementation, evidence, or seal locator fields")
        return
    if not all(
        GIT_OBJECT_ID_RE.fullmatch(value)
        for value in (implementation_value, evidence_value)
    ):
        errors.append("Git seal implementation and evidence commits must use full object IDs")
        return
    if seal_locator != "derived@master+ledger":
        errors.append("Git seal locator must be `derived@master+ledger`")
        return

    inside = git_result(repo_root, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        errors.append("Git seal requires a real Git worktree")
        return

    implementation_commit = resolve_git_commit(repo_root, implementation_value)
    evidence_commit = resolve_git_commit(repo_root, evidence_value)
    head_commit = resolve_git_commit(repo_root, "HEAD")
    master_rel = master_path.relative_to(repo_root).as_posix()
    ledger_rel = ledger_path.relative_to(repo_root).as_posix()
    seal_result = git_result(
        repo_root,
        "log",
        "-1",
        "--format=%H",
        "--",
        master_rel,
        ledger_rel,
    )
    seal_commit = seal_result.stdout.strip() if seal_result.returncode == 0 else ""
    if not implementation_commit or not evidence_commit or not head_commit or not seal_commit:
        errors.append("Git seal references an unknown implementation, evidence, seal, or HEAD commit")
        return
    if len({implementation_commit, evidence_commit, seal_commit}) != 3:
        errors.append("Git seal requires three distinct implementation, evidence, and seal commits")

    evidence_parent = resolve_git_commit(repo_root, f"{evidence_commit}^")
    seal_parent = resolve_git_commit(repo_root, f"{seal_commit}^")
    if evidence_parent != implementation_commit or seal_parent != evidence_commit:
        errors.append("Git seal must form the direct implementation -> evidence -> seal chain")
    ancestor = git_result(repo_root, "merge-base", "--is-ancestor", seal_commit, head_commit)
    if ancestor.returncode != 0:
        errors.append("Git seal commit must remain an ancestor of the current HEAD")
    status = git_result(repo_root, "status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0 or status.stdout.strip():
        errors.append("Git seal requires the current HEAD worktree to be clean")

    package_rel = master_path.parent.relative_to(repo_root).as_posix()
    package_prefix = "" if package_rel == "." else f"{package_rel}/"
    evidence_prefixes = tuple(
        f"{package_prefix}{directory}/"
        for directory in ("evidence", "reports", "reviews")
    )
    evidence_diff = git_result(
        repo_root, "diff", "--name-only", implementation_commit, evidence_commit
    )
    evidence_changes = {
        line.strip() for line in evidence_diff.stdout.splitlines() if line.strip()
    }
    if evidence_diff.returncode != 0 or not evidence_changes:
        errors.append("Git seal evidence commit must contain evidence changes")
    for changed in sorted(evidence_changes):
        if not changed.startswith(evidence_prefixes):
            errors.append(f"Git seal evidence commit changed a forbidden path: {changed}")

    evidence_index_rel = field_path(master_text, "活体证据索引") or ""
    if evidence_index_rel not in evidence_changes:
        errors.append("Git seal evidence commit must update the evidence index")

    seal_diff = git_result(repo_root, "diff", "--name-only", evidence_commit, seal_commit)
    seal_changes = {line.strip() for line in seal_diff.stdout.splitlines() if line.strip()}
    expected_seal_changes = {master_rel, ledger_rel}
    if seal_diff.returncode != 0 or seal_changes != expected_seal_changes:
        errors.append(
            "Git seal commit must change exactly the master and execution ledger"
        )

    immutable_evidence_paths = {evidence_index_rel}
    for evidence_id, row in evidence_by_id.items():
        if len(row) < 12 or row[1] != "FINAL":
            continue
        if not GIT_OBJECT_ID_RE.fullmatch(row[5]):
            errors.append(
                f"Git seal final evidence {evidence_id} must use a full implementation object ID"
            )
        row_commit = resolve_git_commit(repo_root, row[5])
        if row_commit != implementation_commit:
            errors.append(
                f"Git seal final evidence {evidence_id} is not bound to the implementation commit"
            )
        if not row[6].startswith("clean@"):
            errors.append(
                f"Git seal final evidence {evidence_id} must be captured from clean@ implementation"
            )
        else:
            captured_value = row[6].removeprefix("clean@")
            if not GIT_OBJECT_ID_RE.fullmatch(captured_value):
                errors.append(
                    f"Git seal final evidence {evidence_id} clean state must use a full object ID"
                )
            captured_commit = resolve_git_commit(repo_root, captured_value)
            if captured_commit != implementation_commit:
                errors.append(
                    f"Git seal final evidence {evidence_id} clean state does not match implementation"
                )
        artifact_path = row[3].strip("`")
        immutable_evidence_paths.add(artifact_path)
        if artifact_path not in evidence_changes:
            errors.append(
                f"Git seal final evidence {evidence_id} artifact was not captured by the evidence commit"
            )
        tracked = git_result(repo_root, "cat-file", "-e", f"{evidence_commit}:{artifact_path}")
        if tracked.returncode != 0:
            errors.append(
                f"Git seal final evidence {evidence_id} artifact is absent from the evidence commit"
            )

    changed_after_evidence = git_result(
        repo_root,
        "rev-list",
        f"{evidence_commit}..{head_commit}",
        "--",
        *sorted(path for path in immutable_evidence_paths if path),
    )
    if changed_after_evidence.returncode != 0 or changed_after_evidence.stdout.strip():
        errors.append(
            "Git seal final evidence or its index changed in commit history after the evidence commit"
        )


def require_fields(
    text: str,
    labels: tuple[str, ...],
    artifact: str,
    errors: list[str],
) -> dict[str, str]:
    values: dict[str, str] = {}
    for label in labels:
        value = field_value(text, label)
        if not value:
            errors.append(f"{artifact} missing `{label}` field")
            continue
        if value in {"待补", "TBD", "TODO"} or PLACEHOLDER_RE.search(value):
            errors.append(f"{artifact} has unresolved `{label}` field")
            continue
        values[label] = value
    return values


def require_sections(
    text: str,
    headings: tuple[str, ...],
    artifact: str,
    errors: list[str],
) -> None:
    for heading in headings:
        if not section(text, heading).strip():
            errors.append(f"{artifact} missing or empty `## {heading}` section")


def split_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    inner = stripped[1:-1] if stripped.endswith("|") else stripped[1:]
    cells: list[str] = []
    current: list[str] = []
    index = 0
    while index < len(inner):
        char = inner[index]
        if char == "\\" and index + 1 < len(inner) and inner[index + 1] == "|":
            current.append("|")
            index += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def table_data_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.count("|") < 2:
            continue
        cells = split_markdown_table_row(stripped)
        if cells and all(re.fullmatch(r":?-{3,}:?", cell or "---") for cell in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def table_cells(text: str) -> list[list[str]]:
    return table_data_rows(text)


def states_for_version(version: str) -> tuple[str, ...]:
    if version == LATEST_CONTROL_PACK_VERSION:
        return (*BASE_STATES, DESIGN_REVIEW_BLOCKED)
    return BASE_STATES


def evidence_records(text: str) -> dict[str, list[str]]:
    return {
        row[0]: row
        for row in table_cells(text)
        if row and EVIDENCE_ID_RE.fullmatch(row[0])
    }


def approval_records(text: str) -> dict[str, list[str]]:
    return {
        row[0]: row
        for row in table_cells(section(text, "风险、授权与停止条件"))
        if row and ACTION_ID_RE.fullmatch(row[0])
    }


def validate_promise_evidence_links(
    master_text: str,
    evidence_by_id: dict[str, list[str]],
    control_version: str,
    mode: str,
    errors: list[str],
) -> None:
    coverage_rows = [
        row
        for row in table_cells(section(master_text, "承诺覆盖矩阵"))
        if len(row) >= 4 and REQUIREMENT_ID_RE.fullmatch(row[0])
    ]
    declared_promises = {row[0] for row in coverage_rows}
    mapping_index = 2 if control_version == LATEST_CONTROL_PACK_VERSION else 1

    for promise_id, _, _, evidence_id, *_ in coverage_rows:
        evidence = evidence_by_id.get(evidence_id)
        if not evidence:
            errors.append(
                f"promise {promise_id} references evidence absent from the index: {evidence_id}"
            )
            continue
        if len(evidence) <= mapping_index or evidence[mapping_index] != promise_id:
            errors.append(
                f"promise {promise_id} and evidence {evidence_id} do not reference each other"
            )
        if (
            control_version == LATEST_CONTROL_PACK_VERSION
            and mode == "complete"
            and (len(evidence) < 12 or evidence[1] != "FINAL")
        ):
            errors.append(
                f"completed promise {promise_id} must resolve to FINAL evidence"
            )

    if control_version != LATEST_CONTROL_PACK_VERSION:
        return
    for evidence_id, evidence in evidence_by_id.items():
        if len(evidence) <= mapping_index:
            continue
        promise_id = evidence[mapping_index]
        if promise_id not in declared_promises:
            errors.append(
                f"v4 evidence {evidence_id} references an undeclared promise: {promise_id}"
            )

    for row in table_cells(section(master_text, "风险门与先纵切后扩张")):
        if len(row) < 5 or not re.fullmatch(r"GATE-[0-9]{2,}", row[0]):
            continue
        gate_id = row[0]
        evidence_id = row[4]
        evidence = evidence_by_id.get(evidence_id)
        if not evidence:
            errors.append(
                f"risk gate {gate_id} references evidence absent from the index: {evidence_id}"
            )
        elif mode == "complete" and (len(evidence) < 12 or evidence[1] != "FINAL"):
            errors.append(f"completed risk gate {gate_id} must resolve to FINAL evidence")


def validate_approved_action_evidence(
    master_text: str,
    approvals: dict[str, list[str]],
    evidence_by_id: dict[str, list[str]],
    control_version: str,
    errors: list[str],
) -> None:
    if control_version != LATEST_CONTROL_PACK_VERSION:
        return
    coverage_by_promise = {
        row[0]: row[3]
        for row in table_cells(section(master_text, "承诺覆盖矩阵"))
        if len(row) >= 4 and REQUIREMENT_ID_RE.fullmatch(row[0])
    }
    for action_id, approval in approvals.items():
        if len(approval) < 7 or approval[5] != "APPROVED":
            continue
        decision_id = approval[6]
        evidence_id = coverage_by_promise.get(decision_id, "")
        evidence = evidence_by_id.get(evidence_id)
        if (
            not evidence
            or len(evidence) < 12
            or evidence[1] != "FINAL"
            or evidence[2] != decision_id
            or evidence[8] not in {"0", "不适用"}
            or not is_fresh(evidence[10])
            or evidence[11] != "通过"
        ):
            errors.append(
                f"approved action {action_id} must bind fresh passing FINAL decision evidence"
            )


def validate_control_revisions(
    text: str,
    approvals: dict[str, list[str]],
    declared_gate_ids: set[str],
    errors: list[str],
) -> dict[str, dict[str, str]]:
    revision_section = section(text, "控制修订记录")
    required_headers = (
        "修订 ID",
        "前序修订",
        "控制基线",
        "批准动作 ID",
        "触发风险门",
        "状态",
        "变更原因",
    )
    if not all(header in revision_section for header in required_headers):
        errors.append("v4 control-revision register is missing required columns")
        return {}

    records: dict[str, dict[str, str]] = {}
    order: list[str] = []
    used_action_ids: set[str] = set()
    for row in table_cells(revision_section):
        if len(row) < 7 or not REVISION_ID_RE.fullmatch(row[0]):
            errors.append("each v4 control revision must start with a stable REV ID")
            continue
        revision_id, predecessor, baseline, action_id, trigger_gate, state, reason = row[:7]
        if revision_id in records:
            errors.append("v4 control-revision register contains duplicate revision IDs")
            continue
        if not baseline or not reason or state not in {"ACTIVE", "SUPERSEDED"}:
            errors.append(f"v4 control revision {revision_id} has incomplete metadata")
        if not order:
            if "首次建立" not in predecessor or "首次建立" not in action_id:
                errors.append("the first v4 control revision must declare first-establishment markers")
            if trigger_gate not in {"无", "无（首次建立）"}:
                errors.append("the first v4 control revision cannot have a trigger gate")
        else:
            if predecessor != order[-1]:
                errors.append(
                    f"v4 control revision {revision_id} must directly follow the previous revision"
                )
            if not ACTION_ID_RE.fullmatch(action_id):
                errors.append(f"v4 control revision {revision_id} must bind one approval action")
            else:
                if action_id in used_action_ids:
                    errors.append(
                        f"v4 control revision {revision_id} reuses an approval action"
                    )
                used_action_ids.add(action_id)
                approval = approvals.get(action_id)
                if not approval or len(approval) < 7 or approval[5] != "APPROVED":
                    errors.append(
                        f"v4 control revision {revision_id} requires an approved action"
                    )
            if trigger_gate not in {"无", "无（主动修订）"} and not re.fullmatch(
                r"GATE-[0-9]{2,}", trigger_gate
            ):
                errors.append(f"v4 control revision {revision_id} has an invalid trigger gate")
            elif (
                re.fullmatch(r"GATE-[0-9]{2,}", trigger_gate)
                and trigger_gate not in declared_gate_ids
            ):
                errors.append(
                    f"v4 control revision {revision_id} references an undeclared trigger gate"
                )
        records[revision_id] = {
            "predecessor": predecessor,
            "baseline": baseline,
            "action_id": action_id,
            "trigger_gate": trigger_gate,
            "state": state,
            "reason": reason,
        }
        order.append(revision_id)

    active = [revision_id for revision_id in order if records[revision_id]["state"] == "ACTIVE"]
    current = field_value(text, "当前控制修订") or ""
    if len(active) != 1 or active[0] != current:
        errors.append("v4 control-revision register must have one ACTIVE row matching current revision")
    if current and order and order[-1] != current:
        errors.append("the current v4 control revision must be the final append-only row")
    for revision_id in order[:-1]:
        if records[revision_id]["state"] != "SUPERSEDED":
            errors.append(f"historical v4 control revision {revision_id} must be SUPERSEDED")
    return records


def validate_delegation_contract(text: str, errors: list[str]) -> None:
    delegation = section(text, "委派与收束")
    fields = require_fields(
        delegation,
        (
            "委派判定",
            "最大并发子任务",
            "单任务时间上限",
            "委派包",
            "返回状态",
            "心跳与收束",
            "独立审查",
        ),
        "delegation contract",
        errors,
    )
    required_headers = (
        "任务 ID",
        "Brief",
        "所有权与可改范围",
        "明确不做",
        "基线版本",
        "报告路径",
        "审查包",
        "收束预算",
    )
    if not all(header in delegation for header in required_headers):
        errors.append("delegation table is missing required columns")

    concurrency = fields.get("最大并发子任务", "")
    number = re.search(r"\d+", concurrency)
    if concurrency and (not number or int(number.group()) < 1):
        errors.append("delegation concurrency must contain a positive integer")

    return_status = fields.get("返回状态", "")
    for status in ("DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED"):
        if status not in return_status:
            errors.append(f"delegation return states must include `{status}`")

    heartbeat = fields.get("心跳与收束", "")
    if heartbeat and not any(marker in heartbeat for marker in ("收束", "停止", "取消")):
        errors.append("delegation heartbeat must define a convergence or stop rule")

    decision = fields.get("委派判定", "")
    rows = table_cells(delegation)
    if "不委派" not in decision and not rows:
        errors.append("delegated work must contain at least one delegation row")
    for row in rows:
        if len(row) < 8 or not re.fullmatch(r"TASK-[0-9]{2,}", row[0]):
            errors.append("each delegation row must start with one stable TASK ID")
            continue
        if any(not value or value.casefold() in {"none", "n/a", "na", "无"} for value in row[1:8]):
            errors.append(
                f"delegation {row[0]} must bind brief, ownership, exclusions, baseline, report, review, and budget"
            )


def validate_v4_meta_control(text: str, errors: list[str]) -> None:
    authority = section(text, "控制权与三层时间尺度")
    fields = require_fields(
        authority,
        (
            "权威顺序",
            "当前控制基线",
            "替代或继承",
            "历史完成权",
            "控制完整性边界",
            "终极愿景",
            "本 Goal 交付",
            "时间型结果",
            "活跃控制文档上限",
            "控制包推翻条件",
        ),
        "v4 meta-control contract",
        errors,
    )
    if "检查器" not in fields.get("控制完整性边界", "") or "产品完成" not in fields.get(
        "控制完整性边界", ""
    ):
        errors.append(
            "v4 control-integrity boundary must distinguish checker integrity from product completion"
        )
    completion_boundary = field_value(section(text, "最终完成定义"), "完成边界") or ""
    if not all(
        marker in completion_boundary
        for marker in ("仅本 Goal", "终极愿景", "时间型结果")
    ):
        errors.append(
            "v4 completion boundary must limit completion to the current Goal and exclude ultimate/time-only outcomes"
        )
    history = fields.get("历史完成权", "")
    if history and not any(marker in history for marker in ("撤销", "保留")):
        errors.append("v4 inherited completion authority must be explicitly revoked or retained")
    overturn = fields.get("控制包推翻条件", "")
    if overturn and not all(marker in overturn for marker in ("暂停", "修订")):
        errors.append(
            "v4 control package must pause and require a new control revision when its direction is falsified"
        )
    document_limit = fields.get("活跃控制文档上限", "")
    number = re.search(r"\d+", document_limit)
    if document_limit and (not number or int(number.group()) < 1):
        errors.append("v4 active control-document limit must contain a positive integer")

    cognition = section(text, "认知与实验台账")
    required_headers = (
        "认知 ID",
        "类型",
        "命题",
        "当前证据",
        "证伪或通过标准",
        "关联项",
        "失败或删除路径",
    )
    if not all(header in cognition for header in required_headers):
        errors.append("v4 cognition register is missing required columns")
    cognition_rows = table_cells(cognition)
    required_types = {
        "VERIFIED_FACT",
        "FROZEN_DECISION",
        "HYPOTHESIS",
        "EXPERIMENT",
    }
    present_types = {row[1] for row in cognition_rows if len(row) >= 7}
    for cognition_type in sorted(required_types - present_types):
        errors.append(f"v4 cognition register must include `{cognition_type}`")
    hypothesis_ids = {
        row[0]
        for row in cognition_rows
        if len(row) >= 7 and row[1] == "HYPOTHESIS"
    }
    experiment_ids = {
        row[0]
        for row in cognition_rows
        if len(row) >= 7 and row[1] == "EXPERIMENT"
    }
    cognition_ids = [
        row[0]
        for row in cognition_rows
        if row and re.fullmatch(r"(?:FACT|FDEC|HYP|EXP)-[0-9]{2,}", row[0])
    ]
    if len(cognition_ids) != len(set(cognition_ids)):
        errors.append("v4 cognition register contains duplicate cognition IDs")
    expected_prefixes = {
        "VERIFIED_FACT": "FACT-",
        "FROZEN_DECISION": "FDEC-",
        "HYPOTHESIS": "HYP-",
        "EXPERIMENT": "EXP-",
    }
    for row in cognition_rows:
        if len(row) < 7 or not re.fullmatch(r"(?:FACT|FDEC|HYP|EXP)-[0-9]{2,}", row[0]):
            errors.append("each v4 cognition row must use a stable type-specific ID")
            continue
        if row[1] not in required_types:
            errors.append(f"v4 cognition {row[0]} has invalid type `{row[1]}`")
        elif not row[0].startswith(expected_prefixes[row[1]]):
            errors.append(f"v4 cognition {row[0]} ID does not match type `{row[1]}`")
        if any(not value for value in row[2:7]):
            errors.append(f"v4 cognition {row[0]} has an incomplete falsification contract")
    for row in cognition_rows:
        if len(row) < 7:
            continue
        linked_experiments = set(re.findall(r"EXP-[0-9]{2,}", row[5]))
        linked_hypotheses = set(re.findall(r"HYP-[0-9]{2,}", row[5]))
        if row[0] in hypothesis_ids and not linked_experiments.intersection(
            experiment_ids
        ):
            errors.append(f"v4 hypothesis {row[0]} must link to at least one experiment")
        if row[0] in experiment_ids and not linked_hypotheses.intersection(
            hypothesis_ids
        ):
            errors.append(f"v4 experiment {row[0]} must link back to a hypothesis")

    gates = section(text, "风险门与先纵切后扩张")
    if not all(
        header in gates
        for header in (
            "风险门 ID",
            "用户结果",
            "纵向切片",
            "失败判据",
            "放行证据",
            "扩张权限",
        )
    ):
        errors.append("v4 risk-gate table is missing required columns")
    gate_rows = table_cells(gates)
    if not gate_rows:
        errors.append("v4 risk-gate table must contain at least one stable GATE ID")
    gate_ids = [
        row[0]
        for row in gate_rows
        if row and re.fullmatch(r"GATE-[0-9]{2,}", row[0])
    ]
    if len(gate_ids) != len(set(gate_ids)):
        errors.append("v4 risk-gate table contains duplicate gate IDs")
    for row in gate_rows:
        if (
            len(row) < 6
            or not re.fullmatch(r"GATE-[0-9]{2,}", row[0])
            or not re.fullmatch(r"EVID-[0-9]{2,}", row[4])
            or any(not value for value in row[1:6])
        ):
            errors.append("each v4 risk gate must bind a stable gate, evidence, and scale boundary")
    if "先纵切后扩张" not in gates:
        errors.append("v4 risk gates must declare the vertical-slice-before-scale rule")
    if "3" not in gates or "BLOCKED_DESIGN_REVIEW_REQUIRED" not in gates:
        errors.append(
            "v4 risk gates must block for design review after three differentiated failures"
        )

    sealing = section(text, "终局封账顺序")
    for marker in ("报告", "提交", "clean", "新鲜证据", "独立验证", "账本"):
        if marker not in sealing:
            errors.append(f"v4 final sealing order is missing `{marker}`")


def validate_active_control_documents(
    master_text: str,
    master_path: Path,
    repo_root: Path,
    package_files: list[Path],
    expected_paths_by_role: dict[str, set[Path]],
    errors: list[str],
) -> None:
    authority = section(master_text, "控制权与三层时间尺度")
    limit_text = field_value(authority, "活跃控制文档上限") or ""
    limit_match = re.search(r"\d+", limit_text)
    if not limit_match:
        return
    limit = int(limit_match.group())

    registry = section(master_text, "活跃控制文档清单")
    if not all(header in registry for header in ("文档角色", "仓库相对路径")):
        errors.append("v4 active control-document registry is missing required columns")
        return

    registered_paths: list[Path] = []
    roles: list[str] = []
    for row in table_cells(registry):
        if len(row) < 2 or not re.fullmatch(r"[A-Z][A-Z0-9_]*", row[0]):
            errors.append("each v4 active control document must bind a stable role and path")
            continue
        role = row[0]
        if role not in expected_paths_by_role:
            errors.append(f"active control-document registry has unknown role `{role}`")
            continue
        path = resolve_repo_path(repo_root, row[1].strip("`"), errors)
        if not path:
            continue
        try:
            path.relative_to(master_path.parent)
        except ValueError:
            errors.append(f"active control document is outside its package: {row[1]}")
            continue
        if not path.is_file():
            errors.append(f"active control document not found: {row[1]}")
        if path not in expected_paths_by_role[role]:
            errors.append(
                f"active control document role `{role}` does not match its referenced artifact"
            )
        roles.append(role)
        registered_paths.append(path)

    if len(registered_paths) != len(set(registered_paths)):
        errors.append("active control-document registry contains duplicate paths")
    for singleton_role in ("MASTER", "LEDGER", "EVIDENCE_INDEX"):
        if roles.count(singleton_role) != 1:
            errors.append(f"active control-document registry requires one `{singleton_role}`")
    if "PHASE" not in roles:
        errors.append("active control-document registry requires at least one `PHASE`")
    if len(registered_paths) > limit:
        errors.append(
            f"active control document count {len(registered_paths)} exceeds declared limit {limit}"
        )

    registered = set(registered_paths)
    required_files = set().union(*expected_paths_by_role.values())
    for required in sorted(required_files):
        if required not in registered:
            errors.append(
                f"required active control document is not registered: {required.relative_to(repo_root)}"
            )

    exempt_roots = ("archive/", "reports/", "reviews/", "evidence/artifacts/")
    for path in package_files:
        relative = path.relative_to(master_path.parent).as_posix()
        if path not in registered and not relative.startswith(exempt_roots):
            errors.append(
                f"active control document is not registered: {path.relative_to(repo_root)}"
            )


def validate_master_contract(text: str, mode: str, errors: list[str]) -> dict[str, str]:
    fields = require_fields(text, MASTER_FIELDS, "master", errors)
    require_sections(text, MASTER_SECTIONS, "master", errors)

    version = fields.get("控制包版本", "")
    if version and version not in SUPPORTED_CONTROL_PACK_VERSIONS:
        errors.append(
            "master `控制包版本` must be one of: "
            + ", ".join(sorted(SUPPORTED_CONTROL_PACK_VERSIONS))
        )
    if version in {"3", LATEST_CONTROL_PACK_VERSION}:
        require_sections(text, V3_MASTER_SECTIONS, "master", errors)
        validate_delegation_contract(text, errors)
    if version == LATEST_CONTROL_PACK_VERSION:
        require_sections(text, V4_MASTER_SECTIONS, "master", errors)
        validate_v4_meta_control(text, errors)
        current_revision = field_value(text, "当前控制修订")
        if not current_revision or not REVISION_ID_RE.fullmatch(current_revision):
            errors.append("v4 master must declare a stable `当前控制修订`")
        else:
            fields["当前控制修订"] = current_revision
    goal_id = fields.get("Goal ID", "")
    if goal_id and not GOAL_ID_RE.fullmatch(goal_id):
        errors.append("master `Goal ID` must match GOAL-[A-Z0-9-]+")
    state = fields.get("状态", "")
    if state and state not in states_for_version(version):
        errors.append(f"master has invalid state: {state}")

    state_machine = section(text, "状态机")
    expected_flow = "铸造中 -> 就绪待执行 -> 执行中 -> 终局候选 -> 完成"
    if expected_flow not in state_machine:
        errors.append(
            "master state machine must declare the canonical forward transition"
        )
    if "执行中 -> 阻塞 -> 执行中" not in state_machine:
        errors.append("master state machine must declare blocked recovery transition")
    if version == LATEST_CONTROL_PACK_VERSION:
        if f"执行中 -> {DESIGN_REVIEW_BLOCKED}" not in state_machine:
            errors.append("v4 state machine must declare design-review blocking")
        if (
            f"{DESIGN_REVIEW_BLOCKED} -> 执行中" not in state_machine
            or "新修订" not in state_machine
        ):
            errors.append(
                "v4 state machine must require an approved new revision to recover from design-review blocking"
            )

    coverage = section(text, "承诺覆盖矩阵")
    required_headers = ("承诺 ID", "承诺或否定项", "阶段 ID", "验证证据")
    if not all(header in coverage for header in required_headers):
        errors.append("promise coverage matrix is missing required columns")
    if not REQUIREMENT_ID_RE.search(coverage):
        errors.append(
            "promise coverage matrix must contain stable REQ/NREQ/RISK/DEC IDs"
        )
    if re.search(r"(?i)未覆盖|unmapped|todo|tbd", coverage):
        errors.append("promise coverage matrix contains an unresolved mapping")
    coverage_rows = table_cells(coverage)
    if not coverage_rows:
        errors.append("promise coverage matrix must contain at least one data row")
    coverage_ids = [
        row[0]
        for row in coverage_rows
        if row and REQUIREMENT_ID_RE.fullmatch(row[0])
    ]
    if len(coverage_ids) != len(set(coverage_ids)):
        errors.append("promise coverage matrix contains duplicate promise IDs")
    for row in coverage_rows:
        if len(row) < 4 or not REQUIREMENT_ID_RE.fullmatch(row[0]):
            errors.append(
                "each promise coverage row must start with one stable promise ID"
            )
            continue
        if not PHASE_ID_RE.fullmatch(row[2]):
            errors.append(f"promise {row[0]} has an invalid or missing phase ID")
        if not EVIDENCE_ID_RE.fullmatch(row[3]):
            errors.append(f"promise {row[0]} has an invalid or missing evidence ID")

    budget = section(text, "循环与预算")
    for label in (
        "最大修复轮数",
        "单阶段时间上限",
        "Token 或上下文预算",
        "子任务数量上限",
        "工具范围",
        "缺证据熔断",
        "重复运行要求",
    ):
        if not field_value(budget, label):
            errors.append(f"master budget missing `{label}`")

    approval = section(text, "风险、授权与停止条件")
    for header in ("动作 ID", "版本或摘要哈希", "有效期或失效条件", "是否需要人工授权"):
        if header not in approval:
            errors.append(f"approval table missing `{header}` column")
    if version == LATEST_CONTROL_PACK_VERSION:
        for header in ("授权状态", "授权证据"):
            if header not in approval:
                errors.append(f"v4 approval table missing `{header}` column")
    if not ACTION_ID_RE.search(approval):
        errors.append("approval table must contain at least one stable ACT ID")
    approval_rows = table_cells(approval)
    approval_ids = [
        row[0]
        for row in approval_rows
        if row and ACTION_ID_RE.fullmatch(row[0])
    ]
    if len(approval_ids) != len(set(approval_ids)):
        errors.append("approval table contains duplicate action IDs")
    for row in approval_rows:
        if len(row) < 5 or not ACTION_ID_RE.fullmatch(row[0]):
            errors.append("each approval row must start with one stable ACT ID")
            continue
        if row[2].casefold() in {"", "none", "n/a", "na", "无"}:
            errors.append(
                f"approval {row[0]} is missing an action version or plan hash"
            )
        if not row[3] or row[3].casefold() in {"none", "n/a", "na", "无"}:
            errors.append(
                f"approval {row[0]} is missing expiry or invalidation conditions"
            )
        if row[4] not in {"是", "否"}:
            errors.append(f"approval {row[0]} must declare authorization as 是 or 否")
        if version == LATEST_CONTROL_PACK_VERSION:
            if len(row) < 7:
                errors.append(f"v4 approval {row[0]} is missing status or evidence")
                continue
            auth_state, auth_evidence = row[5], row[6]
            if row[4] == "是":
                if auth_state not in {"PENDING", "APPROVED"}:
                    errors.append(f"v4 approval {row[0]} has an invalid authorization state")
                if auth_state == "APPROVED" and not re.fullmatch(
                    r"DEC-[0-9]{2,}", auth_evidence
                ):
                    errors.append(f"approved v4 action {row[0]} must bind a DEC evidence ID")
                elif auth_state == "APPROVED" and auth_evidence not in coverage_ids:
                    errors.append(
                        f"approved v4 action {row[0]} references a DEC absent from promise coverage"
                    )
                if auth_state == "PENDING" and auth_evidence != "待授权":
                    errors.append(f"pending v4 action {row[0]} must use `待授权` evidence")
            elif auth_state != "NOT_REQUIRED" or not auth_evidence:
                errors.append(f"v4 action {row[0]} must explain why authorization is not required")

    effective_mode = mode
    if mode == "auto":
        effective_mode = (
            "ready"
            if state == "就绪待执行"
            else "complete"
            if state == "完成"
            else "resume"
        )
    resume_states = {"就绪待执行", "执行中", "阻塞", "终局候选"}
    if version == LATEST_CONTROL_PACK_VERSION:
        resume_states.add(DESIGN_REVIEW_BLOCKED)
    allowed_states = {
        "ready": {"就绪待执行"},
        "resume": resume_states,
        "complete": {"完成"},
    }
    if state and state not in allowed_states[effective_mode]:
        errors.append(
            f"master state `{state}` is invalid for `{effective_mode}` validation"
        )
    fields["effective_mode"] = effective_mode
    return fields


def validate_ledger(
    path: Path,
    goal_id: str,
    master_state: str,
    master_version: str,
    master_revision: str,
    mode: str,
    declared_gate_ids: set[str],
    declared_hypothesis_ids: set[str],
    declared_experiment_ids: set[str],
    evidence_by_id: dict[str, list[str]],
    revision_records: dict[str, dict[str, str]],
    errors: list[str],
) -> None:
    text = path.read_text(encoding="utf-8")
    fields = require_fields(text, LEDGER_FIELDS, "execution ledger", errors)
    require_sections(
        text, ("当前指针", "状态转换", "阶段记录"), "execution ledger", errors
    )
    if master_version == LATEST_CONTROL_PACK_VERSION:
        require_sections(text, ("设计门失败记录",), "v4 execution ledger", errors)
        current_revision = field_value(text, "当前控制修订")
        if not current_revision or not REVISION_ID_RE.fullmatch(current_revision):
            errors.append("v4 execution ledger must declare a stable `当前控制修订`")
        elif current_revision != master_revision:
            errors.append("execution ledger control revision does not match master")

    ledger_version = fields.get("控制包版本", "")
    if ledger_version and ledger_version not in SUPPORTED_CONTROL_PACK_VERSIONS:
        errors.append("execution ledger has an unsupported control-pack version")
    if ledger_version and master_version and ledger_version != master_version:
        errors.append("execution ledger control-pack version does not match master")
    if fields.get("Goal ID") and fields["Goal ID"] != goal_id:
        errors.append("execution ledger Goal ID does not match master")
    ledger_state = fields.get("当前状态", "")
    if ledger_state and ledger_state not in states_for_version(master_version):
        errors.append(f"execution ledger has invalid state: {ledger_state}")
    if ledger_state and master_state and ledger_state != master_state:
        errors.append("execution ledger state does not match master state")
    phase_id = fields.get("当前阶段 ID", "")
    if (
        phase_id
        and phase_id not in {"无", "无（Goal complete）"}
        and not PHASE_ID_RE.fullmatch(phase_id)
    ):
        errors.append("execution ledger current phase ID is invalid")
    if not RUN_ID_RE.search(section(text, "阶段记录")):
        errors.append("execution ledger must contain at least one stable RUN ID")
    if "->" not in section(text, "状态转换"):
        errors.append("execution ledger must record at least one state transition")

    if master_version == LATEST_CONTROL_PACK_VERSION:
        failure_log = section(text, "设计门失败记录")
        required_headers = (
            "尝试 ID",
            "控制修订 ID",
            "风险门 ID",
            "假设 ID",
            "实验 ID",
            "差异说明",
            "失败证据 ID",
            "结论",
        )
        if not all(header in failure_log for header in required_headers):
            errors.append("v4 design-failure log is missing required columns")
        failed_by_revision_gate: dict[tuple[str, str], list[list[str]]] = {}
        attempt_ids: list[str] = []
        for row in table_cells(failure_log):
            if not row:
                continue
            if not re.fullmatch(r"TRY-[0-9]{2,}", row[0]):
                errors.append("each v4 design-failure row must start with a stable TRY ID")
                continue
            attempt_ids.append(row[0])
            if (
                len(row) < 8
                or not REVISION_ID_RE.fullmatch(row[1])
                or not re.fullmatch(r"GATE-[0-9]{2,}", row[2])
                or not re.fullmatch(r"HYP-[0-9]{2,}", row[3])
                or not re.fullmatch(r"EXP-[0-9]{2,}", row[4])
                or not re.fullmatch(r"EVID-[0-9]{2,}", row[6])
                or row[7] not in {"通过", "失败"}
                or not row[5]
            ):
                errors.append(
                    "each v4 design-failure row must bind a differentiated experiment and evidence"
                )
                continue
            if row[1] not in revision_records:
                errors.append(f"v4 design attempt {row[0]} references an undeclared revision")
            if row[2] not in declared_gate_ids:
                errors.append(f"v4 design attempt {row[0]} references an undeclared risk gate")
            if row[3] not in declared_hypothesis_ids:
                errors.append(f"v4 design attempt {row[0]} references an undeclared hypothesis")
            if row[4] not in declared_experiment_ids:
                errors.append(f"v4 design attempt {row[0]} references an undeclared experiment")
            evidence = evidence_by_id.get(row[6])
            if not evidence:
                errors.append(f"v4 design attempt {row[0]} references undeclared failure evidence")
            elif len(evidence) < 12 or evidence[1] != "ATTEMPT" or evidence[11] != row[7]:
                errors.append(
                    f"v4 design attempt {row[0]} failure evidence role or result does not match"
                )
                evidence = None
            if row[7] == "失败" and evidence:
                failed_by_revision_gate.setdefault((row[1], row[2]), []).append(row)
        if len(attempt_ids) != len(set(attempt_ids)):
            errors.append("v4 design-failure log contains duplicate attempt IDs")
        blocked_by_revision: dict[str, set[str]] = {}
        for (revision_id, gate_id), rows in failed_by_revision_gate.items():
            if len(rows) < 3:
                continue
            experiment_ids = {row[4] for row in rows}
            difference_notes = {row[5] for row in rows}
            evidence_ids = {row[6] for row in rows}
            if (
                len(experiment_ids) < 3
                or len(difference_notes) < 3
                or len(evidence_ids) < 3
            ):
                errors.append(
                    f"v4 design gate {gate_id} has three failures without three differentiated experiments and evidence artifacts"
                )
                continue
            blocked_by_revision.setdefault(revision_id, set()).add(gate_id)

        current_blocked_gates = blocked_by_revision.get(master_revision, set())
        if current_blocked_gates and ledger_state != DESIGN_REVIEW_BLOCKED:
            errors.append(
                "v4 ledger must enter BLOCKED_DESIGN_REVIEW_REQUIRED after three differentiated failures on: "
                + ", ".join(sorted(current_blocked_gates))
            )
        if ledger_state == DESIGN_REVIEW_BLOCKED and not current_blocked_gates:
            errors.append(
                "v4 design-review blocked state requires three differentiated failed experiments on one gate"
            )

        current_record = revision_records.get(master_revision, {})
        predecessor = current_record.get("predecessor", "")
        predecessor_blocked = blocked_by_revision.get(predecessor, set())
        trigger_gate = current_record.get("trigger_gate", "")
        if predecessor_blocked:
            if trigger_gate not in predecessor_blocked:
                errors.append(
                    "v4 recovery revision must name the predecessor risk gate that forced design review"
                )
            transition = section(text, "状态转换")
            action_id = current_record.get("action_id", "")
            if not all(
                marker in transition
                for marker in (
                    f"{DESIGN_REVIEW_BLOCKED} -> 执行中",
                    master_revision,
                    action_id,
                )
            ):
                errors.append(
                    "v4 approved recovery must record the blocked-to-running transition, revision, and action"
                )
        elif re.fullmatch(r"GATE-[0-9]{2,}", trigger_gate):
            errors.append("v4 recovery revision names a risk gate without preserved predecessor failures")

    completion = fields.get("完成判定", "")
    stop_reason = fields.get("停止原因", "")
    if mode == "complete":
        if completion != "通过":
            errors.append("complete validation requires ledger `完成判定：通过`")
        if stop_reason in {"无", "未完成", "继续执行"}:
            errors.append(
                "complete validation requires an explicit terminal stop reason"
            )
        if fields.get("当前入口") not in {"无", "无（Goal complete）"}:
            errors.append("complete validation requires no remaining ledger entry")
    elif completion == "通过":
        errors.append("non-complete control pack cannot claim `完成判定：通过`")


def validate_phase(
    path: Path,
    goal_id: str,
    control_version: str,
    mode: str,
    errors: list[str],
) -> str | None:
    text = path.read_text(encoding="utf-8")
    artifact = f"phase `{path.name}`"
    fields = require_fields(text, PHASE_FIELDS, artifact, errors)
    require_sections(text, ("工作项", "副作用与重放"), artifact, errors)
    if fields.get("Goal ID") and fields["Goal ID"] != goal_id:
        errors.append(f"{artifact} Goal ID does not match master")
    phase_id = fields.get("阶段 ID", "")
    if phase_id and not PHASE_ID_RE.fullmatch(phase_id):
        errors.append(f"{artifact} has invalid phase ID")
    phase_state = fields.get("状态", "")
    if phase_state and phase_state not in states_for_version(control_version):
        errors.append(f"{artifact} has invalid state")
    if mode == "complete" and phase_state != "完成":
        errors.append(f"{artifact} must be complete before Goal completion")

    work = section(text, "工作项")
    task_ids = set(re.findall(r"TASK-[0-9]{2,}", work))
    if not task_ids:
        errors.append(f"{artifact} must contain stable TASK IDs")
    replay = section(text, "副作用与重放")
    if (
        "任务 ID" not in replay
        or "重放类别" not in replay
        or "核验或补偿" not in replay
    ):
        errors.append(f"{artifact} replay table is missing required columns")
    if not any(replay_class in replay for replay_class in REPLAY_CLASSES):
        errors.append(f"{artifact} must classify side-effect replay behavior")
    replay_rows = table_cells(replay)
    replay_task_ids: set[str] = set()
    for row in replay_rows:
        if len(row) < 4 or not re.fullmatch(r"TASK-[0-9]{2,}", row[0]):
            errors.append(f"{artifact} has a replay row without a stable TASK ID")
            continue
        replay_task_ids.add(row[0])
        if row[2] not in REPLAY_CLASSES:
            errors.append(
                f"{artifact} task {row[0]} has invalid replay class `{row[2]}`"
            )
        if not row[3]:
            errors.append(
                f"{artifact} task {row[0]} is missing verification or compensation"
            )
    missing_replay = task_ids - replay_task_ids
    if missing_replay:
        errors.append(
            f"{artifact} tasks missing replay rows: {', '.join(sorted(missing_replay))}"
        )
    return phase_id or None


def validate_evidence_index(
    path: Path,
    repo_root: Path,
    goal_id: str,
    control_version: str,
    mode: str,
    errors: list[str],
) -> None:
    text = path.read_text(encoding="utf-8")
    if field_value(text, "Goal ID") != goal_id:
        errors.append("evidence index Goal ID does not match master")
    evidence_cells = [
        row
        for row in table_cells(text)
        if row and EVIDENCE_ID_RE.fullmatch(row[0])
    ]
    if not evidence_cells:
        errors.append("evidence index must contain at least one stable EVID ID row")
    evidence_ids = [row[0] for row in evidence_cells]
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("evidence index contains duplicate evidence IDs")

    if control_version == LATEST_CONTROL_PACK_VERSION:
        required_headers = (
            "证据 ID",
            "证据角色",
            "覆盖承诺",
            "证据路径",
            "证据 SHA-256",
            "实现版本",
            "工作树状态",
            "执行命令",
            "退出码",
            "生成时间",
            "新鲜度对账",
            "结果",
        )
        if not all(header in text for header in required_headers):
            errors.append("v4 evidence index is missing required columns")
        for row in evidence_cells:
            evidence_id = row[0]
            if (
                len(row) < 12
                or row[1] not in {"FINAL", "ATTEMPT"}
                or not REQUIREMENT_ID_RE.fullmatch(row[2])
            ):
                errors.append(
                    f"v4 evidence {evidence_id} has an invalid role or promise mapping"
                )
                continue
            if any(not value for value in row[3:12]):
                errors.append(f"v4 evidence {evidence_id} has incomplete provenance")
                continue

            role = row[1]
            evidence_path = row[3].strip("`")
            expected_hash = row[4]
            implementation_version = row[5]
            worktree_state = row[6]
            exit_code = row[8]
            generated_at = row[9]
            freshness = row[10]
            result = row[11]
            pending = result in {"待生成", "阻塞"}
            if pending and mode != "complete":
                continue

            artifact = resolve_repo_path(repo_root, evidence_path, errors)
            if artifact and not artifact.is_file():
                errors.append(
                    f"evidence {evidence_id} artifact not found: {evidence_path}"
                )
            if not SHA256_RE.fullmatch(expected_hash):
                errors.append(
                    f"evidence {evidence_id} must contain a lowercase SHA-256"
                )
            elif artifact and artifact.is_file() and file_sha256(artifact) != expected_hash:
                errors.append(
                    f"evidence {evidence_id} SHA-256 does not match its artifact"
                )
            pending_values = {"", "未知", "待生成", "待对账", "none", "n/a", "na", "无"}
            if implementation_version.casefold() in pending_values:
                errors.append(f"evidence {evidence_id} lacks an implementation version")
            if not re.fullmatch(r"(?:clean|external|dirty)@.+", worktree_state):
                errors.append(
                    f"v4 evidence {evidence_id} worktree state must use clean@, external@, or dirty@"
                )
            if exit_code != "不适用" and not re.fullmatch(r"-?[0-9]+", exit_code):
                errors.append(f"evidence {evidence_id} has an invalid exit code")
            if not ISO_TIME_RE.search(generated_at):
                errors.append(f"evidence {evidence_id} has an invalid generation time")
            if role == "ATTEMPT" and result not in {"通过", "失败"}:
                errors.append(f"attempt evidence {evidence_id} must be passing or failing")
            if role == "FINAL" and mode == "complete":
                if not worktree_state.startswith("clean@"):
                    errors.append(
                        f"final evidence {evidence_id} must be captured from clean@ implementation"
                    )
                if not is_fresh(freshness):
                    errors.append(f"final evidence {evidence_id} is not fresh")
                if result != "通过":
                    errors.append(f"final evidence {evidence_id} is not passing")
                if exit_code not in {"0", "不适用"}:
                    errors.append(
                        f"final evidence {evidence_id} must record exit code 0 or 不适用"
                    )
        return

    if control_version == "3":
        required_headers = (
            "证据 ID",
            "覆盖承诺",
            "证据路径",
            "证据 SHA-256",
            "实现版本",
            "工作树状态",
            "执行命令",
            "退出码",
            "生成时间",
            "新鲜度对账",
            "结果",
        )
        if not all(header in text for header in required_headers):
            errors.append("v3 evidence index is missing required columns")
        for row in evidence_cells:
            evidence_id = row[0]
            if len(row) < 11 or not REQUIREMENT_ID_RE.fullmatch(row[1]):
                errors.append(
                    f"evidence {evidence_id} has an invalid or missing promise mapping"
                )
                continue
            if any(not value for value in row[2:11]):
                errors.append(f"evidence {evidence_id} has incomplete v3 provenance")
                continue
            if mode != "complete":
                continue

            evidence_path = row[2].strip("`")
            expected_hash = row[3]
            implementation_version = row[4]
            worktree_state = row[5]
            exit_code = row[7]
            generated_at = row[8]
            freshness = row[9]
            result = row[10]

            artifact = resolve_repo_path(repo_root, evidence_path, errors)
            if artifact and not artifact.is_file():
                errors.append(
                    f"evidence {evidence_id} artifact not found: {evidence_path}"
                )
            if not SHA256_RE.fullmatch(expected_hash):
                errors.append(
                    f"evidence {evidence_id} must contain a lowercase SHA-256"
                )
            elif artifact and artifact.is_file():
                actual_hash = file_sha256(artifact)
                if actual_hash != expected_hash:
                    errors.append(
                        f"evidence {evidence_id} SHA-256 does not match its artifact"
                    )
            pending_values = {"", "未知", "待生成", "待对账", "none", "n/a", "na", "无"}
            if implementation_version.casefold() in pending_values:
                errors.append(f"evidence {evidence_id} lacks an implementation version")
            if not WORKTREE_STATE_RE.fullmatch(worktree_state):
                errors.append(
                    f"evidence {evidence_id} worktree state must use clean@, dirty@, or external@"
                )
            if exit_code not in {"0", "不适用"}:
                errors.append(
                    f"evidence {evidence_id} must record exit code 0 or 不适用"
                )
            if not ISO_TIME_RE.search(generated_at):
                errors.append(f"evidence {evidence_id} has an invalid generation time")
            if not is_fresh(freshness):
                errors.append(f"evidence {evidence_id} is not fresh")
            if result != "通过":
                errors.append(f"evidence {evidence_id} is not passing")
        return

    required_headers = (
        "证据 ID",
        "覆盖承诺",
        "来源版本",
        "生成时间",
        "新鲜度对账",
        "结果",
    )
    if not all(header in text for header in required_headers):
        errors.append("evidence index is missing required columns")
    for row in evidence_cells:
        if len(row) < 8 or not REQUIREMENT_ID_RE.fullmatch(row[1]):
            errors.append(
                f"evidence {row[0]} has an invalid or missing promise mapping"
            )
        if (
            len(row) < 8
            or not row[3]
            or not row[4]
            or not row[5]
            or not row[6]
            or not row[7]
        ):
            errors.append(
                f"evidence {row[0]} has incomplete provenance, freshness, rerun, or result fields"
            )
    if mode == "complete":
        for cells in evidence_cells:
            row = " | ".join(cells)
            if len(cells) < 8 or not is_fresh(cells[5]) or cells[7] != "通过":
                errors.append(
                    "complete validation requires every evidence row to be fresh and passing"
                )
            if re.search(r"失败|阻塞|待生成|过期", row):
                errors.append(
                    "complete validation found failed, blocked, pending, or stale evidence"
                )


def validate_pack(master_path: Path, repo_root: Path, mode: str = "auto") -> list[str]:
    errors: list[str] = []
    repo_root = repo_root.resolve()
    master_path = master_path.resolve()
    if not master_path.is_file():
        return [f"master document not found: {master_path}"]

    master_text = master_path.read_text(encoding="utf-8")
    master_fields = validate_master_contract(master_text, mode, errors)
    goal_id = master_fields.get("Goal ID", "")
    master_state = master_fields.get("状态", "")
    control_version = master_fields.get("控制包版本", "")
    effective_mode = master_fields.get("effective_mode", mode)

    referenced_files: list[Path] = []
    referenced_by_label: dict[str, Path] = {}
    for label in ("执行账本", "活体证据索引"):
        rel_path = field_path(master_text, label)
        if not rel_path:
            continue
        path = resolve_repo_path(repo_root, rel_path, errors)
        if path:
            referenced_files.append(path)
            referenced_by_label[label] = path
            if not path.is_file():
                errors.append(f"referenced file not found: {rel_path}")

    phase_dir_rel = field_path(master_text, "阶段计划目录")
    phase_dir = (
        resolve_repo_path(repo_root, phase_dir_rel, errors) if phase_dir_rel else None
    )
    if phase_dir and not phase_dir.is_dir():
        errors.append(f"phase directory not found: {phase_dir_rel}")

    phase_section = section(master_text, "阶段计划清单")
    phase_refs = re.findall(r"`([^`]+\.md)`", phase_section)
    if not phase_refs:
        errors.append("master must list every phase file under `阶段计划清单`")

    resolved_phase_refs: list[Path] = []
    for rel_path in phase_refs:
        path = resolve_repo_path(repo_root, rel_path, errors)
        if path:
            resolved_phase_refs.append(path)
            referenced_files.append(path)
            if not path.is_file():
                errors.append(f"referenced phase file not found: {rel_path}")

    if len(resolved_phase_refs) != len(set(resolved_phase_refs)):
        errors.append("phase plan list contains duplicate file references")

    if phase_dir and phase_dir.is_dir():
        actual_phases = {
            path.resolve() for path in phase_dir.glob("*.md") if path.is_file()
        }
        listed_phases = set(resolved_phase_refs)
        for path in sorted(actual_phases - listed_phases):
            errors.append(
                f"phase file is not explicitly referenced: {path.relative_to(repo_root)}"
            )
        for path in sorted(listed_phases - actual_phases):
            errors.append(
                f"listed phase is outside the phase directory: {path.relative_to(repo_root)}"
            )

    phase_ids: list[str] = []
    for path in resolved_phase_refs:
        if path.is_file():
            phase_id = validate_phase(
                path,
                goal_id,
                control_version,
                effective_mode,
                errors,
            )
            if phase_id:
                phase_ids.append(phase_id)
    if len(phase_ids) != len(set(phase_ids)):
        errors.append("phase plan list contains duplicate phase IDs")
    if control_version in {"3", LATEST_CONTROL_PACK_VERSION}:
        delegation_rows = table_cells(section(master_text, "委派与收束"))
        delegated_task_ids = {
            row[0]
            for row in delegation_rows
            if row and re.fullmatch(r"TASK-[0-9]{2,}", row[0])
        }
        phase_task_ids = {
            task_id
            for path in resolved_phase_refs
            if path.is_file()
            for task_id in re.findall(
                r"TASK-[0-9]{2,}", path.read_text(encoding="utf-8")
            )
        }
        missing_delegated_tasks = delegated_task_ids - phase_task_ids
        if missing_delegated_tasks:
            errors.append(
                "delegation rows reference tasks absent from phase plans: "
                + ", ".join(sorted(missing_delegated_tasks))
            )
    coverage = section(master_text, "承诺覆盖矩阵")
    for phase_id in phase_ids:
        if phase_id not in coverage:
            errors.append(f"promise coverage matrix does not reference {phase_id}")

    ledger_path = referenced_by_label.get("执行账本")
    evidence_path = referenced_by_label.get("活体证据索引")
    evidence_text = (
        evidence_path.read_text(encoding="utf-8")
        if evidence_path and evidence_path.is_file()
        else ""
    )
    evidence_by_id = evidence_records(evidence_text)
    validate_promise_evidence_links(
        master_text,
        evidence_by_id,
        control_version,
        effective_mode,
        errors,
    )
    approvals = approval_records(master_text)
    validate_approved_action_evidence(
        master_text,
        approvals,
        evidence_by_id,
        control_version,
        errors,
    )
    cognition = section(master_text, "认知与实验台账")
    risk_gates = section(master_text, "风险门与先纵切后扩张")
    declared_gate_ids = set(re.findall(r"GATE-[0-9]{2,}", risk_gates))
    declared_hypothesis_ids = set(re.findall(r"HYP-[0-9]{2,}", cognition))
    declared_experiment_ids = set(re.findall(r"EXP-[0-9]{2,}", cognition))
    revisions: dict[str, dict[str, str]] = {}
    if control_version == LATEST_CONTROL_PACK_VERSION:
        revisions = validate_control_revisions(
            master_text,
            approvals,
            declared_gate_ids,
            errors,
        )
    if ledger_path and ledger_path.is_file():
        validate_ledger(
            ledger_path,
            goal_id,
            master_state,
            control_version,
            master_fields.get("当前控制修订", ""),
            effective_mode,
            declared_gate_ids,
            declared_hypothesis_ids,
            declared_experiment_ids,
            evidence_by_id,
            revisions,
            errors,
        )
    if evidence_path and evidence_path.is_file():
        validate_evidence_index(
            evidence_path,
            repo_root,
            goal_id,
            control_version,
            effective_mode,
            errors,
        )
    if (
        control_version == LATEST_CONTROL_PACK_VERSION
        and effective_mode == "complete"
        and ledger_path
        and ledger_path.is_file()
        and evidence_path
        and evidence_path.is_file()
    ):
        validate_git_seal(
            master_path,
            master_text,
            ledger_path,
            evidence_by_id,
            repo_root,
            errors,
        )

    package_dir = master_path.parent
    package_files = sorted(path for path in package_dir.rglob("*.md") if path.is_file())
    if control_version == LATEST_CONTROL_PACK_VERSION:
        expected_paths_by_role = {
            "MASTER": {master_path},
            "LEDGER": {ledger_path} if ledger_path else set(),
            "PHASE": set(resolved_phase_refs),
            "EVIDENCE_INDEX": {evidence_path} if evidence_path else set(),
        }
        validate_active_control_documents(
            master_text,
            master_path,
            repo_root,
            package_files,
            expected_paths_by_role,
            errors,
        )
    masters = [
        path
        for path in package_files
        if "- 唯一总控：本文件" in path.read_text(encoding="utf-8")
    ]
    if masters != [master_path]:
        errors.append("control pack must contain exactly one master document")

    for path in package_files:
        text = path.read_text(encoding="utf-8")
        if PLACEHOLDER_RE.search(text):
            errors.append(
                f"unresolved template placeholder found: {path.relative_to(repo_root)}"
            )

    return errors


def run_self_test() -> int:
    test_script = Path(__file__).with_name("test_long_goal_pack.py")
    result = subprocess.run(
        [sys.executable, str(test_script)],
        cwd=ROOT,
        check=False,
        timeout=120,
    )
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "master", nargs="?", help="repository-relative path to goal-master.md"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="target project root; defaults to the Guyue repository",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "ready", "resume", "complete"),
        default="auto",
        help="validation stage; auto derives it from the master state",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run checker regression and failure injection",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.master:
        parser.error("master path is required unless --self-test is used")

    repo_root = args.repo_root.resolve()
    if not repo_root.is_dir():
        parser.error(f"repository root does not exist: {repo_root}")
    master_arg = Path(args.master)
    master_path = (
        master_arg.resolve() if master_arg.is_absolute() else (repo_root / master_arg).resolve()
    )
    try:
        master_display = master_path.relative_to(repo_root).as_posix()
    except ValueError:
        parser.error("master path must stay inside --repo-root")

    errors = validate_pack(master_path, repo_root, args.mode)
    if errors:
        print("Long Goal control-pack check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Long Goal control-pack check passed ({args.mode}): {master_display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
