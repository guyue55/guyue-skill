#!/usr/bin/env python3
"""Prove that concurrent local memory index updates do not lose rows."""

from __future__ import annotations

import multiprocessing as mp
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.memory_store import empty_index, index_lock, load_index, write_index_atomic  # noqa: E402


def append_rows(index_path_text: str, worker: int, count: int) -> None:
    index_path = Path(index_path_text)
    for position in range(count):
        with index_lock(index_path, timeout_seconds=10):
            index = load_index(index_path)
            index["memories"].append(
                {
                    "schema_version": 2,
                    "id": f"MEM-20260713T{worker:02d}{position:02d}00000000Z",
                    "filename": f"active/{worker}-{position}.md",
                    "tags": ["concurrency"],
                    "summary": "concurrent fixture",
                    "timestamp": "2026-07-13T00:00:00Z",
                    "provenance": "multiprocess test",
                    "scope": "workspace",
                    "evidence": "final row count",
                    "confidence": "high",
                    "status": "active",
                    "supersedes": [],
                    "review_after": "2026-10-13",
                }
            )
            write_index_atomic(index_path, index)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="guyue-concurrency-") as temp_dir:
        index_path = Path(temp_dir) / "memory" / "index.json"
        write_index_atomic(index_path, empty_index())
        workers = 4
        rows_per_worker = 8
        context = mp.get_context("spawn")
        processes = [
            context.Process(
                target=append_rows,
                args=(str(index_path), worker, rows_per_worker),
            )
            for worker in range(workers)
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(20)
            if process.exitcode != 0:
                raise AssertionError(f"concurrent writer failed: {process.exitcode}")

        index = load_index(index_path)
        expected = workers * rows_per_worker
        actual = len(index["memories"])
        if actual != expected:
            raise AssertionError(f"lost concurrent rows: expected {expected}, got {actual}")
        ids = {entry["id"] for entry in index["memories"]}
        if len(ids) != expected:
            raise AssertionError("concurrent writes produced duplicate IDs")

    print("Guyue memory concurrency tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
