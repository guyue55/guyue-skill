#!/usr/bin/env python3
"""Validate a Long Goal control pack before execution handoff."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1) if match else ""


def field_path(text: str, label: str) -> str | None:
    match = re.search(
        rf"(?m)^- {re.escape(label)}：\s*(?:`([^`]+)`|([^`\s]+))\s*$",
        text,
    )
    return (match.group(1) or match.group(2)) if match else None


def resolve_repo_path(repo_root: Path, rel_path: str, errors: list[str]) -> Path | None:
    path = (repo_root / rel_path).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError:
        errors.append(f"path escapes repository: {rel_path}")
        return None
    return path


def validate_pack(master_path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    repo_root = repo_root.resolve()
    master_path = master_path.resolve()
    if not master_path.is_file():
        return [f"master document not found: {master_path}"]

    master_text = master_path.read_text(encoding="utf-8")
    referenced_files: list[Path] = []

    for label in ("执行账本", "活体证据索引"):
        rel_path = field_path(master_text, label)
        if not rel_path:
            errors.append(f"master missing `{label}` file reference")
            continue
        path = resolve_repo_path(repo_root, rel_path, errors)
        if path:
            referenced_files.append(path)
            if not path.is_file():
                errors.append(f"referenced file not found: {rel_path}")

    phase_dir_rel = field_path(master_text, "阶段计划目录")
    phase_dir = None
    if not phase_dir_rel:
        errors.append("master missing `阶段计划目录` reference")
    else:
        phase_dir = resolve_repo_path(repo_root, phase_dir_rel, errors)
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
        actual_phases = {path.resolve() for path in phase_dir.glob("*.md") if path.is_file()}
        listed_phases = set(resolved_phase_refs)
        for path in sorted(actual_phases - listed_phases):
            errors.append(f"phase file is not explicitly referenced: {path.relative_to(repo_root)}")
        for path in sorted(listed_phases - actual_phases):
            errors.append(f"listed phase is outside the phase directory: {path.relative_to(repo_root)}")

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
            errors.append(f"unresolved template placeholder found: {path.relative_to(repo_root)}")

    return errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="guyue-long-goal-pack-") as temp_dir:
        root = Path(temp_dir)
        goal_dir = root / "docs/goals/demo"
        phase_dir = goal_dir / "phases"
        evidence_dir = goal_dir / "evidence"
        phase_dir.mkdir(parents=True)
        evidence_dir.mkdir()
        (goal_dir / "execution-ledger.md").write_text("# Ledger\n", encoding="utf-8")
        (evidence_dir / "index.md").write_text("# Evidence\n", encoding="utf-8")
        phase_one = phase_dir / "phase-01-baseline.md"
        phase_one.write_text("# Phase 1\n", encoding="utf-8")
        master = goal_dir / "goal-master.md"
        master.write_text(
            "# Demo\n\n"
            "- 唯一总控：本文件\n"
            "- 执行账本：`docs/goals/demo/execution-ledger.md`\n"
            "- 阶段计划目录：`docs/goals/demo/phases/`\n"
            "- 活体证据索引：`docs/goals/demo/evidence/index.md`\n\n"
            "## 阶段计划清单\n"
            "- `docs/goals/demo/phases/phase-01-baseline.md`\n",
            encoding="utf-8",
        )
        if validate_pack(master, root):
            print("long goal pack self-test failed: valid pack was rejected", file=sys.stderr)
            return 1

        template_style = master.read_text(encoding="utf-8")
        for label in ("执行账本", "阶段计划目录", "活体证据索引"):
            template_style = re.sub(
                rf"(?m)^(- {re.escape(label)}：)`([^`]+)`$",
                rf"\1\2",
                template_style,
            )
        master.write_text(template_style, encoding="utf-8")
        if validate_pack(master, root):
            print("long goal pack self-test failed: template-style paths were rejected", file=sys.stderr)
            return 1

        (phase_dir / "phase-02-unlisted.md").write_text("# Phase 2\n", encoding="utf-8")
        errors = validate_pack(master, root)
        if not any("not explicitly referenced" in error for error in errors):
            print("long goal pack self-test failed: unlisted phase was accepted", file=sys.stderr)
            return 1

    print("Long Goal control-pack checker self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master", nargs="?", help="repository-relative path to goal-master.md")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker regression")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.master:
        parser.error("master path is required unless --self-test is used")

    master_path = (ROOT / args.master).resolve()
    errors = validate_pack(master_path, ROOT)
    if errors:
        print("Long Goal control-pack check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Long Goal control-pack check passed: {args.master}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
