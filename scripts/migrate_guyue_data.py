#!/usr/bin/env python3
"""Explicitly migrate legacy install-local Guyue memory into GUYUE_HOME."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.memory_migration import (  # noqa: E402
    build_migration_plan,
    migrate,
    rollback,
    verify_receipt,
    write_receipt,
)
from src.memory_store import (  # noqa: E402
    legacy_runtime_memory_dir,
    legacy_runtime_memory_dirs,
    runtime_memory_dir,
)
from src.paths import migration_state_dir  # noqa: E402


def load_receipt(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("invalid migration receipt")
    return data


def default_receipt_path(receipt: dict) -> Path:
    created = str(receipt.get("created_at", "migration")).replace(":", "").replace("-", "")
    return migration_state_dir() / f"{created}.json"


def default_legacy_dir() -> Path:
    """Prefer the isolated legacy store, then the earliest root layout."""
    for candidate in legacy_runtime_memory_dirs(ROOT):
        if (candidate / "index.json").is_file():
            return candidate
    return legacy_runtime_memory_dir(ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "migrate", "verify", "rollback", "doctor"))
    parser.add_argument("--legacy-dir", type=Path)
    parser.add_argument("--target-dir", type=Path, default=runtime_memory_dir(ROOT))
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    legacy_dir = args.legacy_dir or default_legacy_dir()

    try:
        if args.action in {"plan", "doctor"}:
            result = build_migration_plan(legacy_dir, args.target_dir)
        elif args.action == "migrate":
            result = migrate(legacy_dir, args.target_dir)
            if result["status"] == "migrated":
                receipt_path = args.receipt or default_receipt_path(result)
                write_receipt(receipt_path, result)
                result = {**result, "receipt": str(receipt_path)}
        else:
            if args.receipt is None:
                parser.error(f"{args.action} requires --receipt")
            receipt = load_receipt(args.receipt)
            if args.action == "verify":
                errors = verify_receipt(args.target_dir, receipt)
                result = {"status": "valid" if not errors else "invalid", "errors": errors}
            else:
                result = rollback(args.target_dir, receipt)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") in {"blocked", "invalid"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
