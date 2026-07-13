#!/usr/bin/env python3
"""Run one disposable Long Goal v4 lifecycle through real CLI and Git boundaries."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.dont_write_bytecode = True

import check_long_goal_pack as checker  # noqa: E402
from test_long_goal_pack import (  # noqa: E402
    add_valid_failure_rows,
    apply_approved_revision_recovery,
    isolated_git_environment,
    run_git,
    update_final_evidence,
    write_valid_fixture,
)


MASTER_REL = "docs/goals/demo/goal-master.md"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"expected lifecycle marker missing from {path.name}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def run_checker(repo_root: Path, mode: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "check_long_goal_pack.py"),
            "--repo-root",
            str(repo_root),
            "--mode",
            mode,
            MASTER_REL,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def require_pass(result: subprocess.CompletedProcess[str], stage: str) -> None:
    if result.returncode != 0:
        raise AssertionError(f"{stage} failed:\n{result.stderr.strip()}")


def require_failure(
    result: subprocess.CompletedProcess[str], stage: str, expected: str
) -> None:
    output = result.stdout + result.stderr
    if result.returncode == 0 or expected not in output:
        raise AssertionError(
            f"{stage} did not fail with `{expected}`:\n{output.strip()}"
        )


def complete_recovered_pack(root: Path, master: Path) -> tuple[str, str, str]:
    ledger = master.parent / "execution-ledger.md"
    phase = master.parent / "phases/phase-01-baseline.md"
    evidence_dir = master.parent / "evidence"
    evidence_index = evidence_dir / "index.md"

    replace_once(phase, "- 状态：就绪待执行", "- 状态：完成")
    replace_once(master, "- 状态：执行中", "- 状态：终局候选")
    replace_once(ledger, "- 当前状态：执行中", "- 当前状态：终局候选")

    run_git(root, "init", "-q")
    run_git(root, "config", "user.name", "Guyue Lifecycle Simulation")
    run_git(root, "config", "user.email", "simulation@example.invalid")
    run_git(root, "add", ".")
    run_git(root, "commit", "-qm", "test(goal): lifecycle implementation")
    implementation_commit = run_git(root, "rev-parse", "HEAD")

    (evidence_dir / "baseline.txt").write_text(
        "verified implementation output\n", encoding="utf-8"
    )
    (evidence_dir / "risk-resolution.txt").write_text(
        "verified risk resolution\n", encoding="utf-8"
    )
    (evidence_dir / "revision-approval.txt").write_text(
        f"REV-0002 approved against {implementation_commit}\n", encoding="utf-8"
    )
    update_final_evidence(evidence_index, implementation_commit)
    run_git(root, "add", str(evidence_dir.relative_to(root)))
    run_git(root, "commit", "-qm", "test(goal): lifecycle evidence")
    evidence_commit = run_git(root, "rev-parse", "HEAD")

    replace_once(master, "- 状态：终局候选", "- 状态：完成")
    replace_once(master, "- 实现提交：待生成", f"- 实现提交：{implementation_commit}")
    replace_once(master, "- 证据提交：待生成", f"- 证据提交：{evidence_commit}")
    replace_once(master, "- 封账定位：待生成", "- 封账定位：derived@master+ledger")
    replace_once(ledger, "- 当前状态：终局候选", "- 当前状态：完成")
    replace_once(
        ledger,
        "- 当前阶段 ID：PHASE-01",
        "- 当前阶段 ID：无（Goal complete）",
    )
    replace_once(
        ledger,
        "- 当前入口：执行 TASK-01",
        "- 当前入口：无（Goal complete）",
    )
    replace_once(
        ledger,
        "- 停止原因：等待执行",
        "- 停止原因：全部终局条件满足",
    )
    replace_once(ledger, "- 完成判定：未完成", "- 完成判定：通过")
    run_git(root, "add", str(master.relative_to(root)), str(ledger.relative_to(root)))
    run_git(root, "commit", "-qm", "test(goal): lifecycle seal")
    seal_commit = run_git(root, "rev-parse", "HEAD")
    return implementation_commit, evidence_commit, seal_commit


def run_simulation() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="guyue-long-goal-lifecycle-") as temp_dir:
        with isolated_git_environment():
            root = Path(temp_dir)
            master = write_valid_fixture(root)
            ledger = master.parent / "execution-ledger.md"

            require_pass(run_checker(root, "ready"), "ready control pack")

            add_valid_failure_rows(ledger)
            require_failure(
                run_checker(root, "resume"),
                "three-failure fuse",
                "must enter BLOCKED_DESIGN_REVIEW_REQUIRED",
            )
            replace_once(
                master,
                "- 状态：就绪待执行",
                f"- 状态：{checker.DESIGN_REVIEW_BLOCKED}",
            )
            replace_once(
                ledger,
                "- 当前状态：就绪待执行",
                f"- 当前状态：{checker.DESIGN_REVIEW_BLOCKED}",
            )
            require_pass(run_checker(root, "resume"), "design-review block")

            replace_once(
                master,
                f"- 状态：{checker.DESIGN_REVIEW_BLOCKED}",
                "- 状态：就绪待执行",
            )
            replace_once(
                ledger,
                f"- 当前状态：{checker.DESIGN_REVIEW_BLOCKED}",
                "- 当前状态：就绪待执行",
            )
            apply_approved_revision_recovery(
                master,
                add_failure_history=False,
            )
            require_pass(run_checker(root, "resume"), "approved REV-0002 recovery")

            implementation, evidence, seal = complete_recovered_pack(root, master)
            require_pass(run_checker(root, "complete"), "A/B/C completion")
            require_pass(run_checker(root, "complete"), "restart completion replay")

            baseline = master.parent / "evidence/baseline.txt"
            baseline.write_text("post-seal mutation\n", encoding="utf-8")
            run_git(root, "add", str(baseline.relative_to(root)))
            run_git(root, "commit", "-qm", "test(goal): mutate sealed evidence")
            require_failure(
                run_checker(root, "complete"),
                "post-seal mutation guard",
                "commit history",
            )

            return {
                "schema_version": 1,
                "status": "pass",
                "control_pack_version": 4,
                "control_revision": "REV-0002",
                "stages": [
                    "ready",
                    "three_failures_force_design_review",
                    "blocked_state_valid",
                    "approved_revision_recovery",
                    "implementation_commit_A",
                    "evidence_commit_B",
                    "seal_commit_C",
                    "restart_replay",
                    "post_seal_mutation_rejected",
                ],
                "commits": {
                    "implementation_A": implementation,
                    "evidence_B": evidence,
                    "seal_C": seal,
                },
                "claims": {
                    "external_repo_cli_verified": True,
                    "failure_history_preserved": True,
                    "approval_evidence_verified": True,
                    "restart_verified": True,
                    "mutation_guard_verified": True,
                    "real_user_value_verified": False,
                },
            }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = run_simulation()
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print("Guyue Long Goal v4 生命周期模拟")
        for stage in receipt["stages"]:
            print(f"[PASS] {stage}")
        print("[PASS] 生命周期模拟完成；真实用户价值仍未由该夹具证明。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
