#!/usr/bin/env python3
"""Build the exact hash lock for the current exportable Guyue candidate."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.release_payload import load_manifest  # noqa: E402


def candidate_paths(root: Path, lock_file: str, forbidden: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard"],
        text=True,
        capture_output=True,
        check=True,
    )
    paths = sorted(
        path
        for path in result.stdout.splitlines()
        if path and path != lock_file and (root / path).is_file()
    )
    attrs = subprocess.run(
        ["git", "-C", str(root), "check-attr", "--stdin", "export-ignore"],
        input="\n".join(paths) + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    ignored = {
        line.split(": export-ignore:", 1)[0]
        for line in attrs.stdout.splitlines()
        if line.endswith(": set")
    }
    return [
        path
        for path in paths
        if path not in ignored
        and not any(fnmatch.fnmatch(path, pattern) for pattern in forbidden)
    ]


def main() -> int:
    manifest = load_manifest(ROOT)
    lock_file = str(manifest["lock_file"])
    paths = candidate_paths(
        ROOT,
        lock_file,
        [str(pattern) for pattern in manifest.get("forbidden_patterns", [])],
    )
    lock = {
        "schema_version": 1,
        "package": manifest.get("package"),
        "version": manifest.get("version"),
        "release_state": manifest.get("release_state"),
        "base_tag": manifest.get("base_tag"),
        "files": [
            {
                "path": path,
                "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            }
            for path in paths
        ],
    }
    destination = ROOT / lock_file
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(
            json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Release payload lock updated: {lock_file} ({len(paths)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
