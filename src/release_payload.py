"""Shared release-payload policy and exact-lock verification."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import subprocess
from pathlib import Path


MANIFEST_NAME = "release-manifest.json"


def load_manifest(root: Path) -> dict:
    path = root / MANIFEST_NAME
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("release-manifest.json must use schema_version 1")
    if not isinstance(data.get("profiles"), dict):
        raise ValueError("release-manifest.json must define profiles")
    if not str(data.get("lock_file", "")).strip():
        raise ValueError("release-manifest.json must define lock_file")
    return data


def profile_paths(manifest: dict, profile: str, runtime: str) -> list[str]:
    profiles = manifest.get("profiles", {})
    if profile not in profiles:
        raise ValueError(f"unknown release profile: {profile}")
    seen: set[str] = set()
    paths: list[str] = []

    def collect(name: str) -> None:
        if name in seen:
            raise ValueError(f"cyclic release profile inheritance: {name}")
        seen.add(name)
        current = profiles.get(name)
        if not isinstance(current, dict):
            raise ValueError(f"invalid release profile: {name}")
        parent = str(current.get("extends", "")).strip()
        if parent:
            collect(parent)
        paths.extend(str(path) for path in current.get("required_paths", []))

    collect(profile)
    runtime_paths = manifest.get("runtime_required", {}).get(runtime)
    if not isinstance(runtime_paths, list):
        raise ValueError(f"unknown runtime payload profile: {runtime}")
    paths.extend(str(path) for path in runtime_paths)
    return sorted(set(paths))


def load_lock(root: Path, manifest: dict) -> dict:
    lock_path = root / str(manifest["lock_file"])
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("release payload lock must use schema_version 1")
    files = data.get("files")
    if not isinstance(files, list):
        raise ValueError("release payload lock must contain a files list")
    previous = ""
    for item in files:
        if not isinstance(item, dict):
            raise ValueError("release payload lock file entries must be objects")
        path = str(item.get("path", ""))
        digest = str(item.get("sha256", ""))
        if not path or Path(path).is_absolute() or ".." in Path(path).parts:
            raise ValueError(f"unsafe release payload path: {path}")
        if len(digest) != 64:
            raise ValueError(f"invalid release payload hash: {path}")
        if path <= previous:
            raise ValueError("release payload lock paths must be unique and sorted")
        previous = path
    return data


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_export_ignored(root: Path, rel_path: str) -> bool:
    if not (root / ".gitattributes").is_file():
        return False
    result = subprocess.run(
        ["git", "-C", str(root), "check-attr", "export-ignore", "--", rel_path],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.rstrip().endswith(": set")


def verify_payload(root: Path, *, profile: str, runtime: str) -> list[str]:
    try:
        manifest = load_manifest(root)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{MANIFEST_NAME} ({exc})"]
    errors = [
        path
        for path in profile_paths(manifest, profile, runtime)
        if not (root / path).is_file()
    ]
    try:
        lock = load_lock(root, manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return sorted({*errors, f"{manifest['lock_file']} ({exc})"})
    expected_paths = {str(item["path"]) for item in lock["files"]}
    expected_paths.add(str(manifest["lock_file"]))
    for item in lock["files"]:
        rel_path = str(item["path"])
        path = root / rel_path
        if not path.is_file():
            errors.append(rel_path)
        elif file_sha256(path) != item["sha256"]:
            errors.append(f"{rel_path} (sha256 mismatch)")

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root).as_posix()
        rel_parts = path.relative_to(root).parts
        if ".git" in rel_parts or ".worktrees" in rel_parts:
            continue
        if rel_path in expected_paths or is_export_ignored(root, rel_path):
            continue
        if any(
            fnmatch.fnmatch(rel_path, pattern)
            for pattern in manifest.get("forbidden_patterns", [])
        ):
            errors.append(f"{rel_path} (forbidden payload path)")
        else:
            errors.append(f"{rel_path} (not declared in payload lock)")
    return sorted(set(errors))


def locked_payload_hash(root: Path, manifest: dict | None = None) -> str | None:
    policy = manifest or load_manifest(root)
    try:
        lock = load_lock(root, policy)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    digest = hashlib.sha256()
    for item in lock["files"]:
        path = root / str(item["path"])
        if not path.is_file() or file_sha256(path) != item["sha256"]:
            return None
        digest.update(str(item["path"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
