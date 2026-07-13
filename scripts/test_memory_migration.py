#!/usr/bin/env python3
"""Failure-first tests for explicit legacy memory migration and rollback."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.memory_migration import (  # noqa: E402
    build_migration_plan,
    migrate,
    rollback,
    verify_receipt,
)
from src.memory_store import (  # noqa: E402
    empty_index,
    find_sensitive_memory_content,
    load_index,
    write_index_atomic,
    write_text_atomic,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fixture_entry(memory_id: str, filename: str) -> dict:
    return {
        "schema_version": 2,
        "id": memory_id,
        "filename": filename,
        "tags": ["migration"],
        "summary": "A verified migration fixture",
        "timestamp": "2026-07-13T00:00:00Z",
        "provenance": "focused migration test",
        "scope": "workspace",
        "evidence": "fixture hash",
        "confidence": "high",
        "status": "active",
        "supersedes": [],
        "review_after": "2026-10-13",
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="guyue-migration-") as temp_dir:
        root = Path(temp_dir)
        legacy = root / "legacy"
        target = root / "target"
        entry = fixture_entry("MEM-20260713T000000000001Z", "active/lesson.md")
        detail = "# Memory\n\n## Root Cause\nA verified legacy lesson.\n"
        write_text_atomic(legacy / entry["filename"], detail)
        write_index_atomic(legacy / "index.json", {"schema_version": 2, "memories": [entry]})

        plan = build_migration_plan(legacy, target)
        require(plan["status"] == "ready", f"valid migration must be ready: {plan}")
        require(plan["summary"]["ready"] == 1, "one entry must be planned")

        receipt = migrate(legacy, target)
        require(receipt["status"] == "migrated", "migration must produce a receipt")
        require(not verify_receipt(target, receipt), "receipt verification must pass")
        require(
            (legacy / entry["filename"]).read_text(encoding="utf-8") == detail,
            "migration must not alter legacy data",
        )
        repeated = build_migration_plan(legacy, target)
        require(
            repeated["summary"]["already_present"] == 1,
            "replanning must be idempotent",
        )

        rolled_back = rollback(target, receipt)
        require(rolled_back["status"] == "rolled_back", "rollback must succeed")
        require(
            json.loads((target / "index.json").read_text(encoding="utf-8"))
            == empty_index(),
            "rollback must remove only migrated index rows",
        )
        require(
            not (target / entry["filename"]).exists(),
            "rollback must remove unchanged migrated details",
        )

        sensitive = root / "sensitive"
        secret_entry = fixture_entry("MEM-20260713T000000000002Z", "active/secret.md")
        fake_token = "gh" + "p_" + "12345678901234567890"
        write_text_atomic(
            sensitive / secret_entry["filename"], f"token={fake_token}\n"
        )
        write_index_atomic(
            sensitive / "index.json",
            {"schema_version": 2, "memories": [secret_entry]},
        )
        blocked = build_migration_plan(sensitive, target)
        require(blocked["status"] == "blocked", "sensitive legacy data must block")
        require(blocked["summary"]["sensitive"] == 1, "block reason must be explicit")

        oldest = root / "oldest-layout"
        placeholder_path = "/" + "Users" + "/" + "xxx" + "/project"
        oldest_detail = (
            f"# Legacy lesson\n\nUse a portable placeholder such as {placeholder_path}.\n"
        )
        oldest_entry = {
            "filename": "active/oldest.md",
            "tags": ["legacy"],
            "summary": "An old entry requiring review",
            "timestamp": "2026-06-28",
        }
        write_text_atomic(oldest / oldest_entry["filename"], oldest_detail)
        write_index_atomic(oldest / "index.json", {"memories": [oldest_entry]})
        oldest_target = root / "oldest-target"
        oldest_plan = build_migration_plan(oldest, oldest_target)
        require(
            oldest_plan["status"] == "ready",
            f"oldest root layout must normalize safely: {oldest_plan}",
        )
        oldest_receipt = migrate(oldest, oldest_target)
        migrated_entry = load_index(oldest_target / "index.json")["memories"][0]
        require(
            migrated_entry["timestamp"] == "2026-06-28T00:00:00Z",
            "date-only legacy timestamps must gain an explicit UTC time",
        )
        require(
            migrated_entry["status"] == "needs_review",
            "inferred legacy metadata must not be presented as verified",
        )
        require(
            not verify_receipt(oldest_target, oldest_receipt),
            "normalized oldest-layout migration must verify",
        )
        require(
            find_sensitive_memory_content([f"See {placeholder_path} for an example"])
            is None,
            "documented placeholder paths must not be treated as private data",
        )
        personal_path = "/" + "Users" + "/" + "alice" + "/private-project"
        require(
            find_sensitive_memory_content([f"See {personal_path}"])
            == "personal absolute path",
            "real personal home paths must remain blocked",
        )

    print("Guyue memory migration tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
