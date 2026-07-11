"""Versioned local memory storage shared by the MCP server and GC."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path


SCHEMA_VERSION = 2
CONFIDENCE_LEVELS = {"low", "medium", "high"}
MEMORY_STATUSES = {"active", "superseded", "archived"}
MEMORY_ID_RE = re.compile(r"^MEM-[0-9]{8}T[0-9]{12}Z$")


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def isoformat(value: dt.datetime) -> str:
    return (
        value.astimezone(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def runtime_memory_dir(workspace_root: Path) -> Path:
    configured = os.getenv("GUYUE_MEMORY_DIR")
    return (
        Path(configured).expanduser()
        if configured
        else workspace_root / ".guyue_memory" / "local"
    )


def empty_index() -> dict:
    return {"schema_version": SCHEMA_VERSION, "memories": []}


def _legacy_memory_id(item: dict, position: int) -> str:
    timestamp = re.sub(r"[^0-9]", "", str(item.get("timestamp", "")))[:8]
    day = timestamp if len(timestamp) == 8 else "19700101"
    return f"MEM-{day}T000000{position:06d}Z"


def normalize_entry(item: dict, position: int = 0) -> dict:
    """Normalize old index rows without presenting inferred fields as verified."""
    timestamp = str(item.get("timestamp", "")).strip() or "1970-01-01T00:00:00Z"
    tags = item.get("tags", [])
    supersedes = item.get("supersedes", [])
    return {
        "schema_version": SCHEMA_VERSION,
        "id": str(item.get("id", "")).strip() or _legacy_memory_id(item, position),
        "filename": str(item.get("filename") or item.get("file") or "").strip(),
        "tags": [str(tag).strip() for tag in tags if str(tag).strip()]
        if isinstance(tags, list)
        else [],
        "summary": str(item.get("summary", "")).strip(),
        "timestamp": timestamp,
        "provenance": str(item.get("provenance", "legacy index migration")).strip(),
        "scope": str(item.get("scope", "project")).strip(),
        "evidence": str(
            item.get("evidence", "legacy entry; evidence not recorded")
        ).strip(),
        "confidence": str(item.get("confidence", "low")).strip(),
        "status": str(item.get("status", "active")).strip(),
        "supersedes": [str(value).strip() for value in supersedes if str(value).strip()]
        if isinstance(supersedes, list)
        else [],
        "review_after": str(item.get("review_after", "1970-01-01")).strip(),
    }


def validate_entry(entry: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "id",
        "filename",
        "tags",
        "summary",
        "timestamp",
        "provenance",
        "scope",
        "evidence",
        "confidence",
        "status",
        "supersedes",
        "review_after",
    }
    missing = required - set(entry)
    if missing:
        errors.append("missing fields: " + ", ".join(sorted(missing)))
        return errors
    if entry.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not MEMORY_ID_RE.fullmatch(str(entry.get("id", ""))):
        errors.append("id must match MEM-YYYYMMDDTHHMMSSffffffZ")
    if not isinstance(entry.get("tags"), list) or not all(
        isinstance(tag, str) and tag.strip() for tag in entry.get("tags", [])
    ):
        errors.append("tags must be a string list")
    if entry.get("confidence") not in CONFIDENCE_LEVELS:
        errors.append("confidence must be low, medium, or high")
    if entry.get("status") not in MEMORY_STATUSES:
        errors.append("status must be active, superseded, or archived")
    if not isinstance(entry.get("supersedes"), list):
        errors.append("supersedes must be a list")
    else:
        invalid_supersedes = [
            value
            for value in entry["supersedes"]
            if not MEMORY_ID_RE.fullmatch(str(value))
        ]
        if invalid_supersedes:
            errors.append("supersedes contains an invalid memory ID")
        if entry.get("id") in entry["supersedes"]:
            errors.append("a memory cannot supersede itself")
    for field in (
        "filename",
        "summary",
        "timestamp",
        "provenance",
        "scope",
        "evidence",
        "review_after",
    ):
        if not str(entry.get(field, "")).strip():
            errors.append(f"{field} must not be empty")
    filename = Path(str(entry.get("filename", "")))
    if filename.is_absolute() or ".." in filename.parts:
        errors.append("filename must be a safe relative path")
    try:
        parsed_timestamp = dt.datetime.fromisoformat(
            str(entry.get("timestamp", "")).replace("Z", "+00:00")
        )
        if parsed_timestamp.tzinfo is None:
            errors.append("timestamp must include a timezone")
    except ValueError:
        errors.append("timestamp must be a valid ISO datetime")
    try:
        dt.date.fromisoformat(str(entry.get("review_after", "")))
    except ValueError:
        errors.append("review_after must be a valid ISO date")
    return errors


def load_index(path: Path, *, normalize_legacy: bool = True) -> dict:
    if not path.exists():
        return empty_index()
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw_memories = data
    elif isinstance(data, dict) and isinstance(data.get("memories"), list):
        raw_memories = data["memories"]
    else:
        raise ValueError(f"invalid memory index shape: {path}")
    if normalize_legacy:
        memories = [
            normalize_entry(item, index)
            for index, item in enumerate(raw_memories)
            if isinstance(item, dict)
        ]
        return {"schema_version": SCHEMA_VERSION, "memories": memories}
    return data


def write_index_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def safe_detail_path(memory_dir: Path, filename: str) -> Path:
    path = (memory_dir / filename).resolve()
    try:
        path.relative_to(memory_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"memory path escapes storage root: {filename}") from exc
    return path


def new_memory_id(now: dt.datetime | None = None) -> str:
    current = (now or utc_now()).astimezone(dt.timezone.utc)
    return "MEM-" + current.strftime("%Y%m%dT%H%M%S%fZ")


def default_review_after(now: dt.datetime | None = None, days: int = 90) -> str:
    current = (now or utc_now()).astimezone(dt.timezone.utc)
    return (current.date() + dt.timedelta(days=days)).isoformat()
