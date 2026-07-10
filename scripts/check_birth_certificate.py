#!/usr/bin/env python3
"""Release-readiness birth certificate for the Guyue skill suite.

This is a lightweight public-asset check. It complements
ci_validate_skills.py by asking whether a new user can understand, install,
trigger, verify, and trust the skill suite from the tracked release files.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_RELEASE_FILES = [
    "SKILL.md",
    "README.md",
    "GUYUE_PRINCIPLES.md",
    "skills.json",
    "skills_manifest.json",
    "test-prompts.json",
    "docs/installation.md",
    "docs/security.md",
    "docs/evaluation.md",
    "docs/release-checklist.md",
    "docs/runtime-adapters.md",
    "docs/long-goal-protocol.md",
    "docs/templates/long-goal-control-pack.md",
    "scripts/check_birth_certificate.py",
    "examples/quickstart-output.md",
    "examples/showcase.md",
    ".claude-plugin/marketplace.json",
]

README_NEEDLES = [
    "一句话钩子",
    "Personal Agent Operating Layer",
    "快速开始",
    "触发方式",
    "它会交付什么",
    "安全边界",
    "出师证书",
    "examples/quickstart-output.md",
    "examples/showcase.md",
    "docs/installation.md",
    "docs/security.md",
    "docs/evaluation.md",
]

ROOT_SKILL_NEEDLES = [
    "Material Check",
    "Long Goal Forge",
    "Long Goal Intake",
    "Controlled Ecosystem Invocation",
    "Security Gate",
    "Routing Arbitration",
]

PRINCIPLE_NEEDLES = [
    "验料、造镜子、活体对账",
    "长线目标铸造",
    "长程自治协议",
    "Human Voice Gate",
    "Zero-Leakage",
    "阶段完成不等于愿景完成",
]

PROMPT_NAMES = [
    "Forge Long Goal From Vague Vision",
    "Long Goal Forge Resists Urgency And Vague Superlatives",
    "Trigger Long Goal Protocol",
    "Trigger Stale Artifact Debugging",
    "Trigger Server Permission Boundary Review",
]


def release_files() -> set[str]:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "--cached"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        return {line.strip() for line in output.splitlines() if line.strip()}
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }


def read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def load_json(rel_path: str) -> object:
    return json.loads(read_text(rel_path))


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def require_files(errors: list[str], files: set[str]) -> None:
    for rel_path in REQUIRED_RELEASE_FILES:
        path = ROOT / rel_path
        if not path.exists():
            add_error(errors, f"missing required release file: {rel_path}")
        elif rel_path not in files:
            add_error(errors, f"required file is not tracked/staged for release: {rel_path}")


def require_needles(errors: list[str], rel_path: str, needles: list[str], label: str) -> None:
    try:
        text = read_text(rel_path)
    except OSError as exc:
        add_error(errors, f"cannot read {rel_path}: {exc}")
        return

    for needle in needles:
        if needle not in text:
            add_error(errors, f"{label} missing `{needle}` in {rel_path}")


def check_manifest_and_prompts(errors: list[str]) -> tuple[int, int]:
    try:
        manifest = load_json("skills_manifest.json")
        prompts = load_json("test-prompts.json")
    except Exception as exc:
        add_error(errors, f"cannot parse manifest or prompts: {exc}")
        return 0, 0

    skills = manifest.get("skills", []) if isinstance(manifest, dict) else []
    if not isinstance(skills, list):
        add_error(errors, "skills_manifest.json field `skills` must be a list")
        skills = []

    if not isinstance(prompts, list):
        add_error(errors, "test-prompts.json must be a list")
        prompts = []

    skill_names = {str(skill.get("name", "")).strip() for skill in skills if isinstance(skill, dict)}
    prompt_text = json.dumps(prompts, ensure_ascii=False)
    prompt_names = {str(item.get("name", "")).strip() for item in prompts if isinstance(item, dict)}

    for name in sorted(skill_names):
        if name and name.lower() not in prompt_text.lower():
            add_error(errors, f"registered skill has no prompt coverage: {name}")

    for prompt_name in PROMPT_NAMES:
        if prompt_name not in prompt_names:
            add_error(errors, f"missing regression prompt: {prompt_name}")

    return len(skill_names), len(prompts)


def check_release_sync(errors: list[str], skill_count: int, prompt_count: int) -> None:
    readme = read_text("README.md")
    release = read_text("docs/release-checklist.md")

    if f"{skill_count} routed skills" not in release and f"{skill_count} 个" not in readme:
        add_error(errors, f"release/readme skill count does not mention current count: {skill_count}")

    if f"{prompt_count} structural prompts" not in release:
        add_error(errors, f"release checklist does not mention current prompt count: {prompt_count}")

    if re.search(r"\b41 structural prompts\b", release):
        add_error(errors, "release checklist still contains stale prompt count: 41")


def check_public_boundaries(errors: list[str]) -> None:
    security = read_text("docs/security.md")
    release = read_text("docs/release-checklist.md")
    runtime = read_text("docs/runtime-adapters.md")

    for needle in [
        "Do not store API keys",
        "External skill intake",
        "Unknown install scripts are not auto-executed",
    ]:
        if needle not in security and needle not in release:
            add_error(errors, f"public safety boundary missing `{needle}`")

    if "push, tag, marketplace submission, or deployment" not in release:
        add_error(errors, "release checklist must preserve explicit public-action authorization boundary")

    adapter_needles = ["thin adapter", "thinnest possible adapter", "薄适配器"]
    if not any(needle in runtime for needle in adapter_needles):
        add_error(errors, "runtime adapter doc must keep adapters thin")


def main() -> int:
    errors: list[str] = []
    files = release_files()

    require_files(errors, files)
    require_needles(errors, "README.md", README_NEEDLES, "README public entrypoint")
    require_needles(errors, "SKILL.md", ROOT_SKILL_NEEDLES, "root runtime")
    require_needles(errors, "GUYUE_PRINCIPLES.md", PRINCIPLE_NEEDLES, "principle layer")
    skill_count, prompt_count = check_manifest_and_prompts(errors)
    check_release_sync(errors, skill_count, prompt_count)
    check_public_boundaries(errors)

    print("==========================================")
    print("Guyue Birth Certificate Check")
    print("==========================================")
    print(f"release files: {len(files)}")
    print(f"registered skills: {skill_count}")
    print(f"structural prompts: {prompt_count}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nBirth certificate passed.")
    print("A new user can identify the entrypoint, install path, trigger modes, visible evidence, safety boundaries, and release gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
