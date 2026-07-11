#!/usr/bin/env python3
"""Archive stale or oversized private Guyue memories without losing content."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.memory_store import (  # noqa: E402
    isoformat,
    load_index,
    runtime_memory_dir,
    safe_detail_path,
    utc_now,
    validate_entry,
    write_index_atomic,
)


DEFAULT_MAX_FILE_KB = 50
DEFAULT_MAX_AGE_DAYS = 90


def archive_reason(
    file_path: Path,
    entry: dict,
    now: dt.datetime,
    max_file_bytes: int,
    max_age_days: int,
) -> str | None:
    stats = file_path.stat()
    modified = dt.datetime.fromtimestamp(stats.st_mtime, tz=dt.timezone.utc)
    age_days = (now - modified).total_seconds() / 86400
    if stats.st_size > max_file_bytes:
        return (
            f"size {stats.st_size / 1024:.1f} KB exceeds {max_file_bytes / 1024:.1f} KB"
        )
    if age_days > max_age_days:
        return f"age {age_days:.1f} days exceeds {max_age_days} days"
    try:
        review_after = dt.date.fromisoformat(str(entry.get("review_after", "")))
    except ValueError:
        return "invalid review_after date"
    if review_after < now.date():
        return f"review_after {review_after.isoformat()} has passed"
    return None


def run_gc(
    memory_dir: Path,
    *,
    max_file_kb: int = DEFAULT_MAX_FILE_KB,
    max_age_days: int = DEFAULT_MAX_AGE_DAYS,
    dry_run: bool = False,
    now: dt.datetime | None = None,
) -> tuple[int, list[str]]:
    current = (now or utc_now()).astimezone(dt.timezone.utc)
    index_path = memory_dir / "index.json"
    active_dir = memory_dir / "active"
    archive_dir = memory_dir / "archive"
    active_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    index = load_index(index_path)
    messages: list[str] = []
    archived_count = 0

    for entry in index.get("memories", []):
        validation_errors = validate_entry(entry)
        if validation_errors:
            messages.append(
                f"skip invalid {entry.get('id', '<unknown>')}: {'; '.join(validation_errors)}"
            )
            continue
        if entry.get("status") != "active":
            continue
        try:
            source = safe_detail_path(memory_dir, str(entry["filename"]))
        except ValueError as exc:
            messages.append(str(exc))
            continue
        if not source.is_file():
            messages.append(f"missing detail for {entry['id']}: {entry['filename']}")
            continue
        reason = archive_reason(
            source,
            entry,
            current,
            max_file_kb * 1024,
            max_age_days,
        )
        if not reason:
            continue
        destination_name = f"archive/{source.name}"
        destination = safe_detail_path(memory_dir, destination_name)
        messages.append(f"archive {entry['id']}: {reason}")
        archived_count += 1
        if dry_run:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.replace(destination)
        entry["filename"] = destination_name
        entry["status"] = "archived"
        entry["archived_at"] = isoformat(current)
        entry["archive_reason"] = reason

    if not dry_run:
        write_index_atomic(index_path, index)
    return archived_count, messages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--memory-dir", type=Path, help="override the private memory directory"
    )
    parser.add_argument("--max-file-kb", type=int, default=DEFAULT_MAX_FILE_KB)
    parser.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.max_file_kb <= 0 or args.max_age_days <= 0:
        parser.error("archive limits must be positive")

    memory_dir = args.memory_dir or runtime_memory_dir(ROOT)
    archived_count, messages = run_gc(
        memory_dir,
        max_file_kb=args.max_file_kb,
        max_age_days=args.max_age_days,
        dry_run=args.dry_run,
    )
    for message in messages:
        print(f"- {message}")
    action = "would archive" if args.dry_run else "archived"
    print(f"Guyue memory GC {action} {archived_count} entries in {memory_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
