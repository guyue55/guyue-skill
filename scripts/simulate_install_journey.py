#!/usr/bin/env python3
"""Clone an exact Guyue candidate into an empty HOME and verify first/restart use."""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def clean_git_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"):
        env.pop(key, None)
    return env


def run(
    args: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"command failed ({' '.join(args)}):\n{result.stderr.strip()}"
        )
    return result


def is_git_checkout(source: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "--show-toplevel"],
        env=clean_git_env(),
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode == 0 and Path(result.stdout.strip()).resolve() == source


def export_candidate(source: Path, destination: Path, temp_root: Path) -> str:
    if not is_git_checkout(source):
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store"),
        )
        return "release_tree_copy"

    index_path = temp_root / "candidate.index"
    env = clean_git_env()
    env["GIT_INDEX_FILE"] = str(index_path)
    run(["git", "read-tree", "HEAD"], cwd=source, env=env)
    run(["git", "add", "-A"], cwd=source, env=env)
    tree = run(["git", "write-tree"], cwd=source, env=env).stdout.strip()
    archive = subprocess.run(
        ["git", "archive", "--format=tar", tree],
        cwd=source,
        env=env,
        check=True,
        capture_output=True,
    )
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as bundle:
        for member in bundle.getmembers():
            if member.issym() or member.islnk():
                raise AssertionError(f"archive link is not allowed: {member.name}")
            target = (destination / member.name).resolve()
            try:
                target.relative_to(destination.resolve())
            except ValueError as exc:
                raise AssertionError(f"archive path escapes candidate: {member.name}") from exc
        bundle.extractall(destination)
    return "temporary_git_tree_archive"


def parse_json_command(
    args: list[str], *, cwd: Path, home: Path
) -> dict[str, object]:
    env = clean_git_env()
    env["HOME"] = str(home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = run(args, cwd=cwd, env=env)
    return json.loads(result.stdout)


def run_simulation(source: Path) -> dict[str, object]:
    source = source.resolve()
    with tempfile.TemporaryDirectory(prefix="guyue-install-journey-") as temp_dir:
        temp_root = Path(temp_dir)
        seed = temp_root / "seed"
        remote = temp_root / "remote.git"
        home = temp_root / "home"
        install_root = home / ".codex/skills/guyue"
        home.mkdir()

        export_mode = export_candidate(source, seed, temp_root)
        git_env = clean_git_env()
        run(["git", "init", "-q"], cwd=seed, env=git_env)
        run(
            ["git", "config", "user.name", "Guyue Install Simulation"],
            cwd=seed,
            env=git_env,
        )
        run(
            ["git", "config", "user.email", "simulation@example.invalid"],
            cwd=seed,
            env=git_env,
        )
        run(["git", "add", "."], cwd=seed, env=git_env)
        run(["git", "commit", "-qm", "test(release): exact candidate"], cwd=seed, env=git_env)
        source_commit = run(
            ["git", "rev-parse", "HEAD"], cwd=seed, env=git_env
        ).stdout.strip()

        run(["git", "clone", "--quiet", "--bare", str(seed), str(remote)], cwd=temp_root, env=git_env)
        install_root.parent.mkdir(parents=True)
        run(
            ["git", "clone", "--quiet", f"file://{remote}", str(install_root)],
            cwd=temp_root,
            env=git_env,
        )

        receipt = parse_json_command(
            [
                sys.executable,
                "scripts/check_full_install.py",
                str(install_root),
                "--runtime",
                "codex",
                "--json",
            ],
            cwd=install_root,
            home=home,
        )
        if receipt.get("payload_status") != "complete":
            raise AssertionError(f"installed payload is incomplete: {receipt}")
        if receipt.get("source_commit") != source_commit:
            raise AssertionError("installed receipt is not bound to the cloned source commit")
        if receipt.get("worktree_dirty") is not False:
            raise AssertionError("installed candidate must start from a clean worktree")

        first_run = parse_json_command(
            [sys.executable, "scripts/try_guyue.py", "--runtime", "codex", "--json"],
            cwd=install_root,
            home=home,
        )
        lifecycle = parse_json_command(
            [sys.executable, "scripts/simulate_long_goal_lifecycle.py", "--json"],
            cwd=install_root,
            home=home,
        )
        restart_run = parse_json_command(
            [sys.executable, "scripts/try_guyue.py", "--runtime", "codex", "--json"],
            cwd=install_root,
            home=home,
        )

        first_hash = first_run["package"]["required_payload_sha256"]
        restart_hash = restart_run["package"]["required_payload_sha256"]
        if first_run.get("status") != "pass" or restart_run.get("status") != "pass":
            raise AssertionError("first or restart proof did not pass")
        if first_hash != restart_hash or first_hash != receipt["required_payload_sha256"]:
            raise AssertionError("payload identity changed between install and restart")
        if lifecycle.get("status") != "pass":
            raise AssertionError("installed Long Goal lifecycle simulation failed")

        status = run(["git", "status", "--porcelain"], cwd=install_root, env=git_env)
        if status.stdout.strip():
            raise AssertionError("installed verification polluted the cloned worktree")

        return {
            "schema_version": 1,
            "status": "pass",
            "transport": "file_git_remote",
            "export_mode": export_mode,
            "runtime": "codex",
            "source_commit": source_commit,
            "required_payload_sha256": receipt["required_payload_sha256"],
            "skill_count": receipt["skill_count"],
            "first_run_status": first_run["status"],
            "restart_status": restart_run["status"],
            "restart_same_payload": True,
            "long_goal_lifecycle_status": lifecycle["status"],
            "installed_worktree_clean": True,
            "claims": {
                "clone_transport_verified": True,
                "empty_home_verified": True,
                "runtime_payload_verified": True,
                "restart_verified": True,
                "public_network_verified": False,
                "real_user_feedback_verified": False,
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = run_simulation(args.source)
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print("Guyue 空 HOME 克隆安装模拟")
        for label in (
            "clone_transport_verified",
            "empty_home_verified",
            "runtime_payload_verified",
            "restart_verified",
        ):
            print(f"[PASS] {label}")
        print("[PASS] 本地克隆旅程完成；公网和真实用户反馈仍未由该模拟证明。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
