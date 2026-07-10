#!/usr/bin/env python3
"""Verify that an installed Guyue directory contains the full routed payload."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BASE_REQUIRED_PATHS = [
    "SKILL.md",
    "GUYUE_PRINCIPLES.md",
    "skills_manifest.json",
    "RTK.md",
    "docs/installation.md",
    "docs/security.md",
    "scripts/doctor.py",
    "scripts/security_scanner.py",
]


def missing_payload_paths(install_root: Path) -> list[str]:
    missing = [path for path in BASE_REQUIRED_PATHS if not (install_root / path).is_file()]
    manifest_path = install_root / "skills_manifest.json"
    if not manifest_path.is_file():
        return missing

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [*missing, "skills_manifest.json (invalid JSON)"]

    skills = manifest.get("skills", []) if isinstance(manifest, dict) else []
    if not isinstance(skills, list):
        return [*missing, "skills_manifest.json (skills must be a list)"]

    for skill in skills:
        if not isinstance(skill, dict):
            missing.append("skills_manifest.json (skill entries must be objects)")
            continue
        path = str(skill.get("path", "")).strip()
        if path and not (install_root / path).is_file():
            missing.append(path)
    return sorted(set(missing))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="guyue-install-test-") as temp_dir:
        incomplete = Path(temp_dir) / "guyue"
        incomplete.mkdir()
        (incomplete / "SKILL.md").write_text("---\nname: guyue\ndescription: test\n---\n", encoding="utf-8")
        missing = missing_payload_paths(incomplete)
        if "skills_manifest.json" not in missing or "GUYUE_PRINCIPLES.md" not in missing:
            raise AssertionError("root-only install must fail the full-payload check")

    if missing_payload_paths(ROOT):
        raise AssertionError("repository source tree must satisfy the full-payload contract")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("install_root", nargs="?", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    missing = missing_payload_paths(args.install_root.resolve())
    if missing:
        print("Incomplete Guyue install. Missing payload:")
        for path in missing:
            print(f"- {path}")
        return 1

    print(f"Full Guyue install payload verified: {args.install_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
