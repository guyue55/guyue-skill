"""Versioned local memory storage shared by the MCP server and GC."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path

try:
    from src.paths import ensure_private_directory, private_memory_dir
except ModuleNotFoundError:
    from paths import ensure_private_directory, private_memory_dir  # type: ignore[no-redef]


SCHEMA_VERSION = 2
CONFIDENCE_LEVELS = {"low", "medium", "high"}
MEMORY_STATUSES = {"active", "needs_review", "superseded", "archived"}
MEMORY_ID_RE = re.compile(r"^MEM-[0-9]{8}T[0-9]{12}Z$")
DEFAULT_LOCK_TIMEOUT_SECONDS = 5.0
DEFAULT_STALE_LOCK_SECONDS = 60.0
SENSITIVE_MEMORY_PATTERNS = [
    (
        "API key or token",
        re.compile(r"(?i)(?:api[_ -]?key|access[_ -]?token|secret)\s*[:=]\s*[^\s,;]+"),
    ),
    ("bearer token", re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}")),
    (
        "provider credential",
        re.compile(
            r"(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})"
        ),
    ),
    (
        "personal absolute path",
        re.compile(r"(?:/(?:Users|home)/[^/\s]+/|[A-Za-z]:\\Users\\[^\\\s]+\\)"),
    ),
]
PLACEHOLDER_HOME_PATH_RE = re.compile(
    r"(?:/(?:Users|home)/(?:xxx|user|username|your[-_ ]?name|<[^/\n]+>)/"
    r"|[A-Za-z]:\\Users\\(?:xxx|user|username|your[-_ ]?name|<[^\\\n]+>)\\)",
    re.IGNORECASE,
)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def isoformat(value: dt.datetime) -> str:
    return (
        value.astimezone(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def find_sensitive_memory_content(values: list[str]) -> str | None:
    content = PLACEHOLDER_HOME_PATH_RE.sub("<home>/", "\n".join(values))
    for label, pattern in SENSITIVE_MEMORY_PATTERNS:
        if pattern.search(content):
            return label
    return None


def runtime_memory_dir(workspace_root: Path) -> Path:
    """Return the writable user-owned memory directory.

    ``workspace_root`` remains in the signature for compatibility with callers
    from schema v2, but private data is no longer owned by the installation.
    """
    del workspace_root
    return private_memory_dir()


def legacy_runtime_memory_dir(workspace_root: Path) -> Path:
    return workspace_root.resolve(strict=False) / ".guyue_memory" / "local"


def legacy_runtime_memory_dirs(workspace_root: Path) -> tuple[Path, ...]:
    """Return private legacy layouts from newest to oldest.

    Early releases wrote runtime entries directly below ``.guyue_memory``.
    Later releases isolated them under ``.guyue_memory/local``. Both remain
    read-only compatibility sources until an explicit migration succeeds.
    """
    root = workspace_root.resolve(strict=False) / ".guyue_memory"
    return (root / "local", root)


def empty_index() -> dict:
    return {"schema_version": SCHEMA_VERSION, "memories": []}


def _legacy_memory_id(item: dict, position: int) -> str:
    timestamp = re.sub(r"[^0-9]", "", str(item.get("timestamp", "")))[:8]
    day = timestamp if len(timestamp) == 8 else "19700101"
    return f"MEM-{day}T000000{position:06d}Z"


def _normalize_timestamp(value: object) -> str:
    timestamp = str(value or "").strip()
    if not timestamp:
        return "1970-01-01T00:00:00Z"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", timestamp):
        return f"{timestamp}T00:00:00Z"
    return timestamp


def normalize_entry(item: dict, position: int = 0) -> dict:
    """Normalize old index rows without presenting inferred fields as verified."""
    timestamp = _normalize_timestamp(item.get("timestamp"))
    tags = item.get("tags", [])
    supersedes = item.get("supersedes", [])
    normalized = dict(item)
    normalized.update({
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
        "status": str(item.get("status", "needs_review")).strip(),
        "supersedes": [str(value).strip() for value in supersedes if str(value).strip()]
        if isinstance(supersedes, list)
        else [],
        "review_after": str(item.get("review_after", "1970-01-01")).strip(),
    })
    return normalized


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
        errors.append("status must be active, needs_review, superseded, or archived")
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
        declared_version = data.get("schema_version")
        if declared_version not in {None, SCHEMA_VERSION}:
            raise ValueError(
                f"unsupported memory schema_version {declared_version}: {path}"
            )
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


def ensure_private_dir(path: Path) -> None:
    ensure_private_directory(path)


def write_text_atomic(path: Path, content: str, *, mode: int = 0o600) -> None:
    ensure_private_dir(path.parent)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def write_index_atomic(path: Path, data: dict) -> None:
    write_text_atomic(
        path,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )


@contextmanager
def index_lock(
    index_path: Path,
    *,
    timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    stale_after_seconds: float = DEFAULT_STALE_LOCK_SECONDS,
):
    """Serialize local index mutations with a recoverable exclusive lock."""
    ensure_private_dir(index_path.parent)
    lock_path = index_path.with_name(f".{index_path.name}.lock")
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            try:
                age = time.time() - lock_path.stat().st_mtime
            except FileNotFoundError:
                continue
            if age > stale_after_seconds:
                lock_path.unlink(missing_ok=True)
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for memory lock: {lock_path}")
            time.sleep(0.05)
            continue
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {"pid": os.getpid(), "created_at": isoformat(utc_now())},
                    ensure_ascii=True,
                )
                + "\n"
            )
        break
    try:
        yield
    finally:
        lock_path.unlink(missing_ok=True)


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
