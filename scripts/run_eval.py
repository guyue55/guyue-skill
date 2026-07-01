#!/usr/bin/env python3
"""Structural evaluator for Guyue test prompts.

This script does not call a model. It verifies that the local prompt suite is
complete enough to support repeatable live evaluation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROMPTS_PATH = ROOT / "test-prompts.json"
MANIFEST_PATH = ROOT / "skills_manifest.json"

SAFETY_KEYWORDS = {
    "trace": ["trace", "[Trace", "轨迹"],
    "approval": ["确认", "等待", "halt", "approval", "授权"],
    "research": ["research", "联网", "官方", "latest", "检索"],
    "debugging": ["RCA", "日志", "stack", "盲猜"],
    "memory": ["memory", "记忆", ".guyue_memory"],
}


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}")


def normalize_skill_name(name: str) -> str:
    return name.split("/", 1)[-1].lower()


def prompt_text(entry: dict[str, str]) -> str:
    return f"{entry.get('name', '')}\n{entry.get('prompt', '')}\n{entry.get('expected_behavior', '')}".lower()


def main() -> int:
    prompts = load_json(PROMPTS_PATH)
    manifest = load_json(MANIFEST_PATH)

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(prompts, list):
        errors.append("test-prompts.json must contain a list")
        prompts = []

    if not isinstance(manifest, dict):
        errors.append("skills_manifest.json must contain an object")
        manifest = {}

    names_seen: set[str] = set()
    combined_text = ""

    for index, raw_entry in enumerate(prompts, start=1):
        if not isinstance(raw_entry, dict):
            errors.append(f"prompt #{index} must be an object")
            continue

        name = str(raw_entry.get("name", "")).strip()
        user_prompt = str(raw_entry.get("prompt", "")).strip()
        expected = str(raw_entry.get("expected_behavior", "")).strip()

        if not name:
            errors.append(f"prompt #{index} is missing name")
        elif name in names_seen:
            errors.append(f"duplicate prompt name: {name}")
        else:
            names_seen.add(name)

        if not user_prompt:
            errors.append(f"prompt '{name or index}' is missing prompt")
        if not expected:
            errors.append(f"prompt '{name or index}' is missing expected_behavior")

        combined_text += "\n" + prompt_text(raw_entry)

    manifest_skills = manifest.get("skills", []) if isinstance(manifest, dict) else []
    if not isinstance(manifest_skills, list):
        errors.append("skills_manifest.json field 'skills' must be a list")
        manifest_skills = []

    missing_skills: list[str] = []
    for raw_skill in manifest_skills:
        if not isinstance(raw_skill, dict):
            errors.append("each manifest skill must be an object")
            continue
        skill_name = normalize_skill_name(str(raw_skill.get("name", "")).strip())
        if not skill_name:
            errors.append("manifest skill is missing name")
            continue
        if skill_name not in combined_text:
            missing_skills.append(skill_name)

    if missing_skills:
        errors.append("missing test prompt coverage for skills: " + ", ".join(sorted(missing_skills)))

    for safety_name, keywords in SAFETY_KEYWORDS.items():
        if not any(keyword.lower() in combined_text for keyword in keywords):
            warnings.append(f"weak safety coverage: {safety_name}")

    print("==========================================")
    print("Guyue Test Prompt Evaluation")
    print("==========================================")
    print(f"prompts: {len(prompts)}")
    print(f"manifest skills: {len(manifest_skills)}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nEvaluation structure passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
