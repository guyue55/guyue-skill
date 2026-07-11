#!/usr/bin/env python3
"""Regression tests for Guyue context-budget accounting."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.context_budget import analyze_context_budget  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads((ROOT / "skills_manifest.json").read_text(encoding="utf-8"))
    report = analyze_context_budget(ROOT, manifest)
    require(not report["errors"], f"current catalog exceeds its budget: {report}")
    require(
        report["metrics"]["discovery_chars"] > 0,
        "discovery metadata must be measured",
    )
    require(
        report["metrics"]["root_skill_chars"] > 0,
        "root routing context must be measured",
    )
    require(
        len(report["largest_skill_bodies"]) >= 3,
        "the report must expose the largest activated bodies",
    )

    with tempfile.TemporaryDirectory(prefix="guyue-context-budget-") as temp_dir:
        root = Path(temp_dir)
        root_text = "# 根入口\n"
        (root / "SKILL.md").write_text(root_text, encoding="utf-8")
        (root / "skills" / "alpha").mkdir(parents=True)
        (root / "skills" / "alpha" / "SKILL.md").write_text(
            "# alpha\n", encoding="utf-8"
        )
        bad_manifest = {
            "skills": [
                {
                    "name": "alpha",
                    "path": "skills/alpha/SKILL.md",
                    "trigger_intent": ["audit release"],
                    "description": "x" * 1025,
                },
                {
                    "name": "beta",
                    "path": "skills/beta/SKILL.md",
                    "trigger_intent": ["audit release"],
                    "description": "audit release evidence and verify readiness",
                },
                {
                    "name": "gamma",
                    "path": "skills/gamma/SKILL.md",
                    "trigger_intent": ["audit release"],
                    "description": "audit release evidence and verify readiness",
                },
            ]
        }
        bad_report = analyze_context_budget(root, bad_manifest)
        require(
            bad_report["metrics"]["root_skill_chars"] == len(root_text),
            "root context must count Unicode characters rather than UTF-8 bytes",
        )
        require(
            bad_report["metrics"]["root_skill_bytes"] > len(root_text),
            "the report must expose byte size separately from the character budget",
        )
        require(
            any("description" in error for error in bad_report["errors"]),
            "overlong descriptions must fail",
        )
        require(
            any("not found" in error for error in bad_report["errors"]),
            "missing Skill bodies must fail",
        )
        require(
            bad_report["route_collisions"],
            "near-identical discovery descriptions must be reported",
        )

    print("Context budget tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
