#!/usr/bin/env python3
"""Regression tests for manifest-backed exact release payload verification."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.release_payload import verify_payload  # noqa: E402


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="guyue-release-payload-") as temp_dir:
        root = Path(temp_dir)
        payload = root / "payload.txt"
        payload.write_text("verified\n", encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "lock_file": "release-payload.lock.json",
            "profiles": {"install": {"required_paths": ["payload.txt"]}},
            "runtime_required": {"generic": []},
            "forbidden_patterns": [".guyue_memory/**"],
        }
        write_json(root / "release-manifest.json", manifest)
        lock = {
            "schema_version": 1,
            "files": [
                {
                    "path": "payload.txt",
                    "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
                },
                {
                    "path": "release-manifest.json",
                    "sha256": hashlib.sha256(
                        (root / "release-manifest.json").read_bytes()
                    ).hexdigest(),
                },
            ],
        }
        write_json(root / "release-payload.lock.json", lock)
        if verify_payload(root, profile="install", runtime="generic"):
            raise AssertionError("matching payload must pass")

        payload.write_text("tampered\n", encoding="utf-8")
        errors = verify_payload(root, profile="install", runtime="generic")
        if "payload.txt (sha256 mismatch)" not in errors:
            raise AssertionError("tampered payload must fail by hash")

        payload.write_text("verified\n", encoding="utf-8")
        forbidden = root / ".guyue_memory" / "local" / "index.json"
        forbidden.parent.mkdir(parents=True)
        forbidden.write_text("{}\n", encoding="utf-8")
        errors = verify_payload(root, profile="install", runtime="generic")
        if not any("forbidden payload path" in error for error in errors):
            raise AssertionError("private legacy state must be rejected from payload")

    print("Guyue release payload tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
