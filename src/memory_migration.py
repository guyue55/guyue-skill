"""Plan, execute, verify, and roll back legacy Guyue memory migration."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from src.memory_store import (
    SCHEMA_VERSION,
    empty_index,
    find_sensitive_memory_content,
    index_lock,
    isoformat,
    load_index,
    safe_detail_path,
    utc_now,
    validate_entry,
    write_index_atomic,
    write_text_atomic,
)


PLAN_SCHEMA_VERSION = 1
RECEIPT_SCHEMA_VERSION = 1
BLOCKING_STATUSES = {"conflict", "invalid", "missing_detail", "sensitive"}


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def index_sha256(path: Path) -> str | None:
    return sha256_file(path) if path.is_file() else None


def build_migration_plan(legacy_dir: Path, target_dir: Path) -> dict:
    legacy_index_path = legacy_dir / "index.json"
    target_index_path = target_dir / "index.json"
    if not legacy_index_path.is_file():
        return {
            "schema_version": PLAN_SCHEMA_VERSION,
            "status": "no_legacy_data",
            "items": [],
            "summary": {"total": 0},
        }

    try:
        legacy_index = load_index(legacy_index_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "schema_version": PLAN_SCHEMA_VERSION,
            "status": "blocked",
            "items": [],
            "summary": {"invalid_index": 1},
            "error": f"invalid legacy index: {exc}",
        }
    try:
        target_index = load_index(target_index_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "schema_version": PLAN_SCHEMA_VERSION,
            "status": "blocked",
            "items": [],
            "summary": {"invalid_index": 1},
            "error": f"invalid target index: {exc}",
        }

    target_by_id = {
        str(entry.get("id", "")): entry for entry in target_index.get("memories", [])
    }
    items: list[dict] = []
    counts: dict[str, int] = {}
    for entry in legacy_index.get("memories", []):
        memory_id = str(entry.get("id", ""))
        status = "ready"
        reason = "new admissible legacy entry"
        detail_hash = None
        errors = validate_entry(entry)
        if errors:
            status = "invalid"
            reason = "; ".join(errors)
        else:
            try:
                source = safe_detail_path(legacy_dir, str(entry["filename"]))
            except ValueError as exc:
                status = "invalid"
                reason = str(exc)
            else:
                if not source.is_file():
                    status = "missing_detail"
                    reason = f"missing detail: {entry['filename']}"
                else:
                    content = source.read_bytes()
                    detail_hash = sha256_bytes(content)
                    try:
                        detail_text = content.decode("utf-8")
                    except UnicodeDecodeError:
                        status = "invalid"
                        reason = "detail is not valid UTF-8"
                    else:
                        sensitive = find_sensitive_memory_content(
                            [detail_text, json.dumps(entry, ensure_ascii=False)]
                        )
                        if sensitive:
                            status = "sensitive"
                            reason = f"detail contains {sensitive}"

        target_entry = target_by_id.get(memory_id)
        if status == "ready" and target_entry is not None:
            try:
                target_detail = safe_detail_path(
                    target_dir, str(target_entry.get("filename", ""))
                )
                target_hash = sha256_file(target_detail)
            except (OSError, ValueError):
                status = "conflict"
                reason = "target ID exists but its detail is missing or unsafe"
            else:
                if target_hash == detail_hash and target_entry == entry:
                    status = "already_present"
                    reason = "target contains the same metadata and detail"
                else:
                    status = "conflict"
                    reason = "target ID exists with different metadata or detail"

        counts[status] = counts.get(status, 0) + 1
        items.append(
            {
                "id": memory_id,
                "filename": str(entry.get("filename", "")),
                "status": status,
                "reason": reason,
                "detail_sha256": detail_hash,
            }
        )

    blocked = any(item["status"] in BLOCKING_STATUSES for item in items)
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "status": "blocked" if blocked else "ready",
        "source_index_sha256": index_sha256(legacy_index_path),
        "target_index_sha256": index_sha256(target_index_path),
        "items": items,
        "summary": {"total": len(items), **counts},
    }


def migrate(legacy_dir: Path, target_dir: Path) -> dict:
    plan = build_migration_plan(legacy_dir, target_dir)
    if plan["status"] == "no_legacy_data":
        return {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "status": "no_legacy_data",
            "migrated": [],
        }
    if plan["status"] != "ready":
        raise ValueError("migration plan is blocked; resolve every conflict first")

    ready_ids = {
        item["id"] for item in plan["items"] if item["status"] == "ready"
    }
    legacy_index = load_index(legacy_dir / "index.json")
    source_entries = [
        entry
        for entry in legacy_index.get("memories", [])
        if entry.get("id") in ready_ids
    ]
    target_index_path = target_dir / "index.json"
    copied: list[tuple[Path, dict]] = []
    with index_lock(target_index_path):
        current_plan = build_migration_plan(legacy_dir, target_dir)
        if current_plan != plan:
            raise RuntimeError("migration inputs changed after planning; plan again")
        target_index = load_index(target_index_path) if target_index_path.exists() else empty_index()
        try:
            for entry in source_entries:
                source = safe_detail_path(legacy_dir, str(entry["filename"]))
                destination = safe_detail_path(target_dir, str(entry["filename"]))
                if destination.exists():
                    raise RuntimeError(f"target detail already exists: {entry['filename']}")
                content = source.read_text(encoding="utf-8")
                write_text_atomic(destination, content)
                copied.append((destination, entry))
            target_index.setdefault("memories", []).extend(source_entries)
            target_index["schema_version"] = SCHEMA_VERSION
            write_index_atomic(target_index_path, target_index)
        except Exception:
            for destination, _ in copied:
                destination.unlink(missing_ok=True)
            raise

    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "status": "migrated",
        "created_at": isoformat(utc_now()),
        "source_index_sha256": plan.get("source_index_sha256"),
        "target_index_before_sha256": plan.get("target_index_sha256"),
        "target_index_after_sha256": index_sha256(target_index_path),
        "migrated": [
            {
                "id": entry["id"],
                "filename": entry["filename"],
                "detail_sha256": sha256_file(destination),
            }
            for destination, entry in copied
        ],
    }


def verify_receipt(target_dir: Path, receipt: dict) -> list[str]:
    errors: list[str] = []
    try:
        index = load_index(target_dir / "index.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"invalid target index: {exc}"]
    by_id = {str(entry.get("id", "")): entry for entry in index.get("memories", [])}
    for item in receipt.get("migrated", []):
        entry = by_id.get(str(item.get("id", "")))
        if entry is None:
            errors.append(f"missing migrated ID: {item.get('id', '')}")
            continue
        if entry.get("filename") != item.get("filename"):
            errors.append(f"filename changed for {item.get('id', '')}")
            continue
        try:
            detail = safe_detail_path(target_dir, str(entry["filename"]))
            actual_hash = sha256_file(detail)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot verify {item.get('id', '')}: {exc}")
            continue
        if actual_hash != item.get("detail_sha256"):
            errors.append(f"detail hash changed for {item.get('id', '')}")
    return errors


def rollback(target_dir: Path, receipt: dict) -> dict:
    errors = verify_receipt(target_dir, receipt)
    if errors:
        raise ValueError("rollback refused: " + "; ".join(errors))
    target_index_path = target_dir / "index.json"
    migrated_ids = {str(item.get("id", "")) for item in receipt.get("migrated", [])}
    with index_lock(target_index_path):
        errors = verify_receipt(target_dir, receipt)
        if errors:
            raise ValueError("rollback refused after lock: " + "; ".join(errors))
        index = load_index(target_index_path)
        retained = [
            entry
            for entry in index.get("memories", [])
            if str(entry.get("id", "")) not in migrated_ids
        ]
        index["memories"] = retained
        moved: list[tuple[Path, Path]] = []
        try:
            for item in receipt.get("migrated", []):
                detail = safe_detail_path(target_dir, str(item["filename"]))
                temporary = detail.with_name(
                    f".{detail.name}.rollback.{os.getpid()}"
                )
                if temporary.exists():
                    raise RuntimeError(f"rollback temporary path exists: {temporary.name}")
                detail.replace(temporary)
                moved.append((detail, temporary))
            write_index_atomic(target_index_path, index)
        except Exception:
            for detail, temporary in reversed(moved):
                if temporary.exists():
                    temporary.replace(detail)
            raise
        for _, temporary in moved:
            temporary.unlink()
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "status": "rolled_back",
        "rolled_back_at": isoformat(utc_now()),
        "removed_ids": sorted(migrated_ids),
        "target_index_after_sha256": index_sha256(target_index_path),
    }


def write_receipt(path: Path, receipt: dict) -> None:
    write_text_atomic(path, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
