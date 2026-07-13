#!/usr/bin/env python3
"""Verify an installed Guyue directory against its shared payload manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.release_payload import (  # noqa: E402
    load_lock,
    load_manifest,
    locked_payload_hash,
    profile_paths,
    verify_payload,
)


RUNTIMES = ("generic", "codex", "claude")


def required_payload_paths(install_root: Path, runtime: str = "generic") -> list[str]:
    try:
        manifest = load_manifest(install_root)
    except (OSError, json.JSONDecodeError, ValueError):
        return ["release-manifest.json"]
    return profile_paths(manifest, "install", runtime)


def missing_payload_paths(install_root: Path, runtime: str = "generic") -> list[str]:
    return verify_payload(install_root, profile="install", runtime=runtime)


def payload_hash(install_root: Path, runtime: str) -> str | None:
    del runtime
    try:
        return locked_payload_hash(install_root)
    except (OSError, json.JSONDecodeError, ValueError):
        return None


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
    return result.stdout.strip(), bool(status.stdout.strip()) if status.returncode == 0 else None


def build_receipt(install_root: Path, runtime: str) -> dict:
    try:
        skill_manifest = json.loads(
            (install_root / "skills_manifest.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        skill_manifest = {}
    missing = missing_payload_paths(install_root, runtime)
    commit, dirty = git_state(install_root)
    try:
        policy = load_manifest(install_root)
        lock = load_lock(install_root, policy)
        locked_count = len(lock["files"]) + 1
    except (OSError, json.JSONDecodeError, ValueError):
        policy = {}
        locked_count = 0
    return {
        "schema_version": 2,
        "package": str(policy.get("package", skill_manifest.get("name", "guyue"))),
        "version": str(policy.get("version", skill_manifest.get("version", "unknown"))),
        "release_state": str(policy.get("release_state", "unknown")),
        "base_tag": str(policy.get("base_tag", "")),
        "runtime": runtime,
        "payload_status": "complete" if not missing else "incomplete",
        "required_file_count": locked_count,
        "skill_count": len(skill_manifest.get("skills", []))
        if isinstance(skill_manifest.get("skills"), list)
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
        if not any(item.startswith("release-manifest.json") for item in missing):
            raise AssertionError("root-only install must fail the manifest-backed check")

    for runtime in RUNTIMES:
        receipt = build_receipt(ROOT, runtime)
        if receipt["payload_status"] != "complete" or not receipt["required_payload_sha256"]:
            raise AssertionError(f"repository must produce a complete {runtime} receipt: {receipt}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("install_root", nargs="?", type=Path, default=ROOT)
    parser.add_argument("--runtime", choices=RUNTIMES, default="generic")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()

    install_root = args.install_root.resolve()
    receipt = build_receipt(install_root, args.runtime)
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 1 if receipt["missing"] else 0
    if receipt["missing"]:
        print("Incomplete Guyue install. Payload errors:")
        for path in receipt["missing"]:
            print(f"- {path}")
        return 1
    print(
        f"Full Guyue payload verified for {args.runtime}: {install_root} "
        f"({receipt['skill_count']} skills, {receipt['required_file_count']} files, "
        f"sha256={receipt['required_payload_sha256']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
