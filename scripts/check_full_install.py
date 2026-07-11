#!/usr/bin/env python3
"""Verify that an installed Guyue directory contains the full routed payload."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
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
    "scripts/check_full_install.py",
    "scripts/doctor.py",
    "scripts/security_scanner.py",
    "scripts/try_guyue.py",
    "src/context_budget.py",
    "src/skill_router.py",
]
RUNTIME_REQUIRED_PATHS = {
    "generic": [],
    "codex": ["AGENTS.md"],
    "claude": [".claude-plugin/marketplace.json"],
}


def required_payload_paths(install_root: Path, runtime: str = "generic") -> list[str]:
    paths = [*BASE_REQUIRED_PATHS, *RUNTIME_REQUIRED_PATHS[runtime]]
    manifest_path = install_root / "skills_manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return sorted(set(paths))
        for skill in manifest.get("skills", []) if isinstance(manifest, dict) else []:
            if isinstance(skill, dict) and str(skill.get("path", "")).strip():
                paths.append(str(skill["path"]).strip())
    return sorted(set(paths))


def missing_payload_paths(install_root: Path, runtime: str = "generic") -> list[str]:
    missing = [
        path
        for path in required_payload_paths(install_root, runtime)
        if not (install_root / path).is_file()
    ]
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
    return sorted(set(missing))


def payload_hash(install_root: Path, runtime: str) -> str | None:
    digest = hashlib.sha256()
    for rel_path in required_payload_paths(install_root, runtime):
        path = install_root / rel_path
        if not path.is_file():
            return None
        digest.update(rel_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def git_state(install_root: Path) -> tuple[str | None, bool | None]:
    result = subprocess.run(
        ["git", "-C", str(install_root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None, None
    status = subprocess.run(
        ["git", "-C", str(install_root), "status", "--porcelain"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip(), bool(
        status.stdout.strip()
    ) if status.returncode == 0 else None


def build_receipt(install_root: Path, runtime: str) -> dict:
    manifest_path = install_root / "skills_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        manifest = {}
    missing = missing_payload_paths(install_root, runtime)
    commit, dirty = git_state(install_root)
    return {
        "schema_version": 1,
        "package": str(manifest.get("name", "guyue-digital-twin")),
        "version": str(manifest.get("version", "unknown")),
        "runtime": runtime,
        "payload_status": "complete" if not missing else "incomplete",
        "required_file_count": len(required_payload_paths(install_root, runtime)),
        "skill_count": len(manifest.get("skills", []))
        if isinstance(manifest.get("skills"), list)
        else 0,
        "required_payload_sha256": payload_hash(install_root, runtime),
        "source_commit": commit,
        "worktree_dirty": dirty,
        "missing": missing,
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="guyue-install-test-") as temp_dir:
        incomplete = Path(temp_dir) / "guyue"
        incomplete.mkdir()
        (incomplete / "SKILL.md").write_text(
            "---\nname: guyue\ndescription: test\n---\n", encoding="utf-8"
        )
        missing = missing_payload_paths(incomplete)
        if (
            "skills_manifest.json" not in missing
            or "GUYUE_PRINCIPLES.md" not in missing
        ):
            raise AssertionError("root-only install must fail the full-payload check")

    if missing_payload_paths(ROOT):
        raise AssertionError(
            "repository source tree must satisfy the full-payload contract"
        )
    for runtime in RUNTIME_REQUIRED_PATHS:
        receipt = build_receipt(ROOT, runtime)
        if (
            receipt["payload_status"] != "complete"
            or not receipt["required_payload_sha256"]
        ):
            raise AssertionError(
                f"repository must produce a complete {runtime} install receipt"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("install_root", nargs="?", type=Path, default=ROOT)
    parser.add_argument(
        "--runtime", choices=tuple(RUNTIME_REQUIRED_PATHS), default="generic"
    )
    parser.add_argument(
        "--json", action="store_true", help="print a machine-readable install receipt"
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()

    install_root = args.install_root.resolve()
    receipt = build_receipt(install_root, args.runtime)
    missing = receipt["missing"]
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 1 if missing else 0
    if missing:
        print("Incomplete Guyue install. Missing payload:")
        for path in missing:
            print(f"- {path}")
        return 1

    print(
        f"Full Guyue install payload verified for {args.runtime}: {install_root} "
        f"({receipt['skill_count']} skills, sha256={receipt['required_payload_sha256']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
