#!/usr/bin/env python3
"""Validate Long Goal control packs for handoff, recovery, or completion."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
GOAL_ID_RE = re.compile(r"^GOAL-[A-Z0-9][A-Z0-9-]*$")
PHASE_ID_RE = re.compile(r"^PHASE-[0-9]{2,}$")
RUN_ID_RE = re.compile(r"RUN-[0-9]{4,}")
REQUIREMENT_ID_RE = re.compile(r"(?:REQ|NREQ|RISK|DEC)-[0-9]{2,}")
EVIDENCE_ID_RE = re.compile(r"EVID-[0-9]{2,}")
ACTION_ID_RE = re.compile(r"ACT-[0-9]{2,}")
SHA256_RE = re.compile(r"[a-f0-9]{64}")
ISO_TIME_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})"
)
WORKTREE_STATE_RE = re.compile(r"(?:clean|dirty|external)@.+")

LATEST_CONTROL_PACK_VERSION = "3"
SUPPORTED_CONTROL_PACK_VERSIONS = {"2", LATEST_CONTROL_PACK_VERSION}

STATES = ("铸造中", "就绪待执行", "执行中", "阻塞", "终局候选", "完成")
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


def table_data_rows(text: str) -> list[str]:
    rows: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.count("|") < 2:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell or "---") for cell in cells):
            continue
        rows.append(stripped)
    return rows[1:] if rows else []


def table_cells(text: str) -> list[list[str]]:
    rows = table_data_rows(text)
    return [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]


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


def validate_master_contract(text: str, mode: str, errors: list[str]) -> dict[str, str]:
    fields = require_fields(text, MASTER_FIELDS, "master", errors)
    require_sections(text, MASTER_SECTIONS, "master", errors)

    version = fields.get("控制包版本", "")
    if version and version not in SUPPORTED_CONTROL_PACK_VERSIONS:
        errors.append(
            "master `控制包版本` must be one of: "
            + ", ".join(sorted(SUPPORTED_CONTROL_PACK_VERSIONS))
        )
    if version == LATEST_CONTROL_PACK_VERSION:
        require_sections(text, V3_MASTER_SECTIONS, "master", errors)
        validate_delegation_contract(text, errors)
    goal_id = fields.get("Goal ID", "")
    if goal_id and not GOAL_ID_RE.fullmatch(goal_id):
        errors.append("master `Goal ID` must match GOAL-[A-Z0-9-]+")
    state = fields.get("状态", "")
    if state and state not in STATES:
        errors.append(f"master has invalid state: {state}")

    state_machine = section(text, "状态机")
    expected_flow = "铸造中 -> 就绪待执行 -> 执行中 -> 终局候选 -> 完成"
    if expected_flow not in state_machine:
        errors.append(
            "master state machine must declare the canonical forward transition"
        )
    if "执行中 -> 阻塞 -> 执行中" not in state_machine:
        errors.append("master state machine must declare blocked recovery transition")

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
    if not ACTION_ID_RE.search(approval):
        errors.append("approval table must contain at least one stable ACT ID")
    approval_rows = table_cells(approval)
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

    effective_mode = mode
    if mode == "auto":
        effective_mode = (
            "ready"
            if state == "就绪待执行"
            else "complete"
            if state == "完成"
            else "resume"
        )
    allowed_states = {
        "ready": {"就绪待执行"},
        "resume": {"就绪待执行", "执行中", "阻塞", "终局候选"},
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
    mode: str,
    errors: list[str],
) -> None:
    text = path.read_text(encoding="utf-8")
    fields = require_fields(text, LEDGER_FIELDS, "execution ledger", errors)
    require_sections(
        text, ("当前指针", "状态转换", "阶段记录"), "execution ledger", errors
    )

    ledger_version = fields.get("控制包版本", "")
    if ledger_version and ledger_version not in SUPPORTED_CONTROL_PACK_VERSIONS:
        errors.append("execution ledger has an unsupported control-pack version")
    if ledger_version and master_version and ledger_version != master_version:
        errors.append("execution ledger control-pack version does not match master")
    if fields.get("Goal ID") and fields["Goal ID"] != goal_id:
        errors.append("execution ledger Goal ID does not match master")
    ledger_state = fields.get("当前状态", "")
    if ledger_state and ledger_state not in STATES:
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


def validate_phase(path: Path, goal_id: str, errors: list[str]) -> str | None:
    text = path.read_text(encoding="utf-8")
    artifact = f"phase `{path.name}`"
    fields = require_fields(text, PHASE_FIELDS, artifact, errors)
    require_sections(text, ("工作项", "副作用与重放"), artifact, errors)
    if fields.get("Goal ID") and fields["Goal ID"] != goal_id:
        errors.append(f"{artifact} Goal ID does not match master")
    phase_id = fields.get("阶段 ID", "")
    if phase_id and not PHASE_ID_RE.fullmatch(phase_id):
        errors.append(f"{artifact} has invalid phase ID")
    if fields.get("状态") and fields["状态"] not in STATES:
        errors.append(f"{artifact} has invalid state")

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
            if "新鲜" not in freshness or "过期" in freshness:
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
            if "新鲜" not in row or "通过" not in row:
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
            phase_id = validate_phase(path, goal_id, errors)
            if phase_id:
                phase_ids.append(phase_id)
    if len(phase_ids) != len(set(phase_ids)):
        errors.append("phase plan list contains duplicate phase IDs")
    if control_version == LATEST_CONTROL_PACK_VERSION:
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
    if ledger_path and ledger_path.is_file():
        validate_ledger(
            ledger_path,
            goal_id,
            master_state,
            control_version,
            effective_mode,
            errors,
        )
    evidence_path = referenced_by_label.get("活体证据索引")
    if evidence_path and evidence_path.is_file():
        validate_evidence_index(
            evidence_path,
            repo_root,
            goal_id,
            control_version,
            effective_mode,
            errors,
        )

    package_dir = master_path.parent
    package_files = sorted(path for path in package_dir.rglob("*.md") if path.is_file())
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


def write_valid_fixture(root: Path) -> Path:
    goal_dir = root / "docs/goals/demo"
    phase_dir = goal_dir / "phases"
    evidence_dir = goal_dir / "evidence"
    phase_dir.mkdir(parents=True)
    evidence_dir.mkdir()
    goal_id = "GOAL-DEMO-001"

    baseline = evidence_dir / "baseline.txt"
    baseline.write_text("ok\n", encoding="utf-8")
    baseline_hash = file_sha256(baseline)

    ledger = goal_dir / "execution-ledger.md"
    ledger.write_text(
        "# Demo 执行账本\n\n"
        "## 当前指针\n"
        f"- 控制包版本：{LATEST_CONTROL_PACK_VERSION}\n"
        f"- Goal ID：{goal_id}\n"
        "- 当前状态：就绪待执行\n"
        "- 当前阶段 ID：PHASE-01\n"
        "- 当前入口：执行 TASK-01\n"
        "- 最近有效提交：baseline-123\n"
        "- 最近新鲜证据：evidence/index.md\n"
        "- 当前阻塞：无\n"
        "- 停止原因：等待执行\n"
        "- 完成判定：未完成\n\n"
        "## 状态转换\n- RUN-0001：铸造中 -> 就绪待执行\n\n"
        "## 阶段记录\n"
        "### RUN-0001 · 控制包就绪\n- 下一入口：执行 TASK-01\n",
        encoding="utf-8",
    )

    evidence = evidence_dir / "index.md"
    evidence.write_text(
        "# Demo 活体证据索引\n\n"
        f"- Goal ID：{goal_id}\n\n"
        "| 证据 ID | 覆盖承诺 | 证据路径 | 证据 SHA-256 | 实现版本 | 工作树状态 | 执行命令 | 退出码 | 生成时间 | 新鲜度对账 | 结果 |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
        f"| EVID-01 | REQ-01 | docs/goals/demo/evidence/baseline.txt | {baseline_hash} | baseline-123 | clean@baseline-123 | printf ok | 0 | 2026-07-10T00:00:00Z | 新鲜 | 通过 |\n",
        encoding="utf-8",
    )

    phase = phase_dir / "phase-01-baseline.md"
    phase.write_text(
        "# PHASE-01 基线\n\n"
        f"- Goal ID：{goal_id}\n"
        "- 阶段 ID：PHASE-01\n"
        "- 状态：就绪待执行\n"
        "- 阶段目标：验证基线\n"
        "- 稳定输入：当前仓库\n"
        "- 依赖：无\n"
        "- 本阶段改动边界：只读检查\n"
        "- 本阶段不做：不发布\n"
        "- 定向检查：echo ok\n"
        "- 主线门禁：echo ok\n"
        "- 活体验收：读取真实产物\n"
        "- 失败处理：记录并阻塞\n"
        "- 回滚方式：无写入\n"
        "- 人工检查点：无\n"
        "- 阶段完成条件：REQ-01 通过\n"
        "- 下一入口：Goal 终局审查\n\n"
        "## 工作项\n- TASK-01：执行基线验证。\n\n"
        "## 副作用与重放\n"
        "| 任务 ID | 副作用 | 重放类别 | 核验或补偿 |\n"
        "|---|---|---|---|\n"
        "| TASK-01 | 无 | replay_safe | 重跑检查 |\n",
        encoding="utf-8",
    )

    master = goal_dir / "goal-master.md"
    master.write_text(
        "# Demo 总控\n\n"
        "## 控制信息\n"
        f"- 控制包版本：{LATEST_CONTROL_PACK_VERSION}\n"
        f"- Goal ID：{goal_id}\n"
        "- 状态：就绪待执行\n"
        "- 唯一总控：本文件\n"
        "- 执行账本：`docs/goals/demo/execution-ledger.md`\n"
        "- 阶段计划目录：`docs/goals/demo/phases/`\n"
        "- 活体证据索引：`docs/goals/demo/evidence/index.md`\n"
        "- 基线提交或版本：baseline-123\n"
        "- 最后审查时间：2026-07-10T00:00:00Z\n\n"
        "## 状态机\n"
        "- 正向：铸造中 -> 就绪待执行 -> 执行中 -> 终局候选 -> 完成\n"
        "- 恢复：执行中 -> 阻塞 -> 执行中\n\n"
        "## 阶段计划清单\n- `docs/goals/demo/phases/phase-01-baseline.md`\n\n"
        "## 愿景与真实需求\n- 真实用户：维护者\n- 最终目标：基线可验证\n\n"
        "## 项目现场\n- 已确认事实：仓库存在\n- 当前基线：baseline-123\n\n"
        "## 范围契约\n- 必须完成：基线验证\n- 明确不做：发布\n\n"
        "## 方案与取舍\n- 推荐方案：本地验证\n\n"
        "## 阶段路线\n| 阶段 ID | 目标 | 交付物 |\n|---|---|---|\n| PHASE-01 | 验证基线 | 证据 |\n\n"
        "## 承诺覆盖矩阵\n"
        "| 承诺 ID | 承诺或否定项 | 阶段 ID | 验证证据 |\n"
        "|---|---|---|---|\n"
        "| REQ-01 | 基线可验证 | PHASE-01 | EVID-01 |\n\n"
        "## 循环与预算\n"
        "- 最大修复轮数：2\n- 单阶段时间上限：30 分钟\n"
        "- Token 或上下文预算：只读定向检查\n- 子任务数量上限：1\n"
        "- 工具范围：本地只读\n- 缺证据熔断：立即阻塞\n- 重复运行要求：幂等\n\n"
        "## 委派与收束\n"
        "- 委派判定：不委派；单 Agent 完成只读基线验证\n"
        "- 最大并发子任务：1\n"
        "- 单任务时间上限：20 分钟\n"
        "- 委派包：必须包含 Brief、所有权边界、基线版本、报告路径和审查包\n"
        "- 返回状态：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED\n"
        "- 心跳与收束：两次无新证据即停止扩张并收束\n"
        "- 独立审查：终局由未参与实现的审查视角复核\n\n"
        "| 任务 ID | Brief | 所有权与可改范围 | 明确不做 | 基线版本 | 报告路径 | 审查包 | 收束预算 |\n"
        "|---|---|---|---|---|---|---|---|\n\n"
        "## 主线验证门\n- 测试：echo ok\n- 真实运行：读取证据\n\n"
        "## 最终完成定义\n- 正向条件：REQ-01 通过\n- 否定清单：不得伪造证据\n\n"
        "## 风险、授权与停止条件\n"
        "| 动作 ID | 风险或动作 | 版本或摘要哈希 | 有效期或失效条件 | 是否需要人工授权 |\n"
        "|---|---|---|---|---|\n"
        "| ACT-01 | 发布 | plan-v1 | 计划变化即失效 | 是 |\n\n"
        "## 恢复协议\n1. 读取账本。\n2. 从 TASK-01 继续。\n",
        encoding="utf-8",
    )
    return master


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="guyue-long-goal-pack-") as temp_dir:
        root = Path(temp_dir)
        master = write_valid_fixture(root)
        if validate_pack(master, root, "ready"):
            print(
                "long goal pack self-test failed: valid pack was rejected",
                file=sys.stderr,
            )
            for error in validate_pack(master, root, "ready"):
                print(f"- {error}", file=sys.stderr)
            return 1

        ledger = master.parent / "execution-ledger.md"
        original_ledger = ledger.read_text(encoding="utf-8")
        ledger.write_text("# Empty ledger\n", encoding="utf-8")
        if not any(
            "execution ledger" in error
            for error in validate_pack(master, root, "ready")
        ):
            print(
                "long goal pack self-test failed: empty ledger was accepted",
                file=sys.stderr,
            )
            return 1
        ledger.write_text(original_ledger, encoding="utf-8")

        original_master = master.read_text(encoding="utf-8")
        master.write_text(
            original_master.replace("| REQ-01 |", "| 未覆盖 |"), encoding="utf-8"
        )
        if not any(
            "promise coverage" in error
            for error in validate_pack(master, root, "ready")
        ):
            print(
                "long goal pack self-test failed: unmapped promise was accepted",
                file=sys.stderr,
            )
            return 1
        master.write_text(original_master, encoding="utf-8")

        master.write_text(
            re.sub(
                r"(?ms)^## 委派与收束\s*$.*?(?=^## 主线验证门)",
                "",
                original_master,
            ),
            encoding="utf-8",
        )
        if not any(
            "委派与收束" in error or "delegation" in error
            for error in validate_pack(master, root, "ready")
        ):
            print(
                "long goal pack self-test failed: missing delegation contract was accepted",
                file=sys.stderr,
            )
            return 1
        master.write_text(original_master, encoding="utf-8")

        evidence = master.parent / "evidence/index.md"
        original_evidence = evidence.read_text(encoding="utf-8")
        duplicate_row = next(
            line for line in original_evidence.splitlines() if line.startswith("| EVID-01")
        )
        evidence.write_text(
            original_evidence.rstrip() + "\n" + duplicate_row + "\n",
            encoding="utf-8",
        )
        if not any(
            "duplicate evidence IDs" in error
            for error in validate_pack(master, root, "ready")
        ):
            print(
                "long goal pack self-test failed: duplicate evidence ID was accepted",
                file=sys.stderr,
            )
            return 1
        evidence.write_text(original_evidence, encoding="utf-8")

        delegated_master = original_master.replace(
            "|---|---|---|---|---|---|---|---|\n\n## 主线验证门",
            "|---|---|---|---|---|---|---|---|\n"
            "| TASK-99 | 独立检查 | docs | 不改代码 | baseline-123 | reports/task-99.md | reviews/task-99.md | 1 轮 |\n\n"
            "## 主线验证门",
        ).replace("- 委派判定：不委派；", "- 委派判定：可委派；")
        master.write_text(delegated_master, encoding="utf-8")
        if not any(
            "absent from phase plans" in error
            for error in validate_pack(master, root, "ready")
        ):
            print(
                "long goal pack self-test failed: orphan delegation task was accepted",
                file=sys.stderr,
            )
            return 1
        master.write_text(original_master, encoding="utf-8")

        phase = master.parent / "phases/phase-01-baseline.md"
        original_phase = phase.read_text(encoding="utf-8")
        phase.write_text(
            original_phase.replace("replay_safe", "unknown"), encoding="utf-8"
        )
        if not any("replay" in error for error in validate_pack(master, root, "ready")):
            print(
                "long goal pack self-test failed: missing replay class was accepted",
                file=sys.stderr,
            )
            return 1
        phase.write_text(original_phase, encoding="utf-8")

        unlisted = master.parent / "phases/phase-02-unlisted.md"
        unlisted.write_text(
            original_phase.replace("PHASE-01", "PHASE-02"), encoding="utf-8"
        )
        if not any(
            "not explicitly referenced" in error
            for error in validate_pack(master, root, "ready")
        ):
            print(
                "long goal pack self-test failed: unlisted phase was accepted",
                file=sys.stderr,
            )
            return 1
        unlisted.unlink()

        master.write_text(
            original_master.replace("- 状态：就绪待执行", "- 状态：完成"),
            encoding="utf-8",
        )
        completed_ledger = original_ledger.replace(
            "- 当前状态：就绪待执行", "- 当前状态：完成"
        )
        completed_ledger = completed_ledger.replace(
            "- 当前阶段 ID：PHASE-01", "- 当前阶段 ID：无（Goal complete）"
        )
        completed_ledger = completed_ledger.replace(
            "- 当前入口：执行 TASK-01", "- 当前入口：无（Goal complete）"
        )
        completed_ledger = completed_ledger.replace(
            "- 停止原因：等待执行", "- 停止原因：全部终局条件满足"
        )
        completed_ledger = completed_ledger.replace(
            "- 完成判定：未完成", "- 完成判定：通过"
        )
        ledger.write_text(completed_ledger, encoding="utf-8")
        evidence = master.parent / "evidence/index.md"
        current_evidence = evidence.read_text(encoding="utf-8")
        evidence.write_text(
            current_evidence.replace("| 新鲜 |", "| 过期 |"), encoding="utf-8"
        )
        completion_errors = validate_pack(master, root, "complete")
        if not any("evidence" in error for error in completion_errors):
            print(
                "long goal pack self-test failed: stale completion evidence was accepted",
                file=sys.stderr,
            )
            return 1

        evidence.write_text(current_evidence, encoding="utf-8")
        baseline = master.parent / "evidence/baseline.txt"
        baseline.write_text("changed after evidence capture\n", encoding="utf-8")
        hash_errors = validate_pack(master, root, "complete")
        if not any("SHA-256" in error for error in hash_errors):
            print(
                "long goal pack self-test failed: mismatched evidence hash was accepted",
                file=sys.stderr,
            )
            return 1

    print("Long Goal control-pack checker self-test passed with failure injection.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "master", nargs="?", help="repository-relative path to goal-master.md"
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

    master_path = (ROOT / args.master).resolve()
    errors = validate_pack(master_path, ROOT, args.mode)
    if errors:
        print("Long Goal control-pack check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Long Goal control-pack check passed ({args.mode}): {args.master}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
