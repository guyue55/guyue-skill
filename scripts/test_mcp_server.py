#!/usr/bin/env python3
"""Focused safety, lifecycle, and GC tests for Guyue local memory."""

from __future__ import annotations

import datetime as dt
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from scripts import memory_gc  # noqa: E402
from src import mcp_server  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def write_memory(
    symptom: str,
    root_cause: str,
    solution: str,
    tags: list[str],
    *,
    review_after: str = "",
    supersedes: list[str] | None = None,
) -> str:
    return mcp_server.guyue_write_memory(
        symptom,
        root_cause,
        solution,
        "Add a targeted regression check before the next release.",
        "Reproduced locally and verified by the focused test.",
        tags,
        review_after=review_after,
        supersedes=supersedes,
    )


def main() -> int:
    generic_route = json.loads(
        mcp_server.guyue_explain_route(
            "给当前项目做一个普通权限管理页面和后端接口。",
            limit=8,
        )
    )
    generic_names = {item["name"] for item in generic_route["selected"]}
    require(
        "nexusflow-governance-workflow" not in generic_names,
        "generic requests must not select project-specific workflows",
    )
    nexus_route = json.loads(
        mcp_server.guyue_explain_route(
            "修复租户治理权限。",
            context_markers=["NexusFlow", "permissionSnapshot"],
        )
    )
    require(
        nexus_route["selected"][0]["name"] == "nexusflow-governance-workflow",
        "MCP route explanations must honor explicit project markers",
    )
    require(
        "must contain" in mcp_server.guyue_explain_route("   "),
        "MCP route explanations must reject empty intent",
    )

    originals = {
        "MEMORY_DIR": mcp_server.MEMORY_DIR,
        "ACTIVE_DIR": mcp_server.ACTIVE_DIR,
        "INDEX_FILE": mcp_server.INDEX_FILE,
        "CURATED_MEMORY_DIR": mcp_server.CURATED_MEMORY_DIR,
        "CURATED_INDEX_FILE": mcp_server.CURATED_INDEX_FILE,
    }

    with tempfile.TemporaryDirectory(prefix="guyue-mcp-test-") as temp_dir:
        root = Path(temp_dir)
        memory_dir = root / ".guyue_memory" / "local"
        curated_dir = root / ".guyue_memory"
        mcp_server.MEMORY_DIR = memory_dir
        mcp_server.ACTIVE_DIR = memory_dir / "active"
        mcp_server.INDEX_FILE = memory_dir / "index.json"
        mcp_server.CURATED_MEMORY_DIR = curated_dir
        mcp_server.CURATED_INDEX_FILE = curated_dir / "index.json"

        try:
            empty_result = mcp_server.guyue_read_memory("   ")
            require(
                "must contain" in empty_result, "empty memory queries must be rejected"
            )

            fake_credential = "sk" + "-" + "1234567890abcdefghijkl"
            secret_result = write_memory(
                "Provider request failed",
                f"The provider credential {fake_credential} was expired",
                "Rotate and redact the credential",
                ["provider"],
            )
            require(
                "Refused" in secret_result, "secret-bearing memory must be rejected"
            )
            require(
                not memory_dir.exists(), "rejected memory must not create storage files"
            )

            personal_path = "/" + "Users" + "/example/private-project/config.json"
            path_result = write_memory(
                "A local file was missing",
                f"The command depended on {personal_path}",
                "Use a repository-relative path",
                ["portability"],
            )
            require(
                "Refused" in path_result, "personal absolute paths must be rejected"
            )
            require(
                not memory_dir.exists(),
                "rejected path memory must not create storage files",
            )

            invalid_date = write_memory(
                "A valid-looking lesson had invalid lifecycle metadata",
                "The review date could not be parsed",
                "Validate metadata before writing",
                ["schema"],
                review_after="not-a-date",
            )
            require(
                "Refused invalid memory metadata" in invalid_date,
                "invalid review dates must be rejected",
            )
            require(
                not memory_dir.exists(),
                "invalid metadata must not create storage files",
            )

            first = write_memory(
                "The release page showed stale assets",
                "A previous development server was still running",
                "Restart the server and inspect the served HTML",
                ["release", "stale-artifact"],
                review_after="2000-01-01",
            )
            second = write_memory(
                "The theme script appeared missing",
                "The browser was connected to an old process",
                "Restart and compare the live artifact",
                ["theme", "stale-artifact"],
            )
            require(
                "Successfully saved" in first and "Successfully saved" in second,
                "normal memories must be stored",
            )

            index = json.loads(mcp_server.INDEX_FILE.read_text(encoding="utf-8"))
            require(
                index["schema_version"] == 2, "runtime index must use schema version 2"
            )
            filenames = [item["filename"] for item in index["memories"]]
            memory_ids = [item["id"] for item in index["memories"]]
            require(len(filenames) == 2, "two memory entries must be indexed")
            require(len(set(memory_ids)) == 2, "rapid writes must not collide")
            require(
                all(filename.startswith("active/") for filename in filenames),
                "details must live under active/",
            )
            require(
                all(
                    {
                        "provenance",
                        "scope",
                        "evidence",
                        "confidence",
                        "status",
                        "supersedes",
                        "review_after",
                    }
                    <= set(item)
                    for item in index["memories"]
                ),
                "memory lifecycle metadata must be complete",
            )
            detail = (memory_dir / filenames[0]).read_text(encoding="utf-8")
            require("## Prevention" in detail, "memory detail must include prevention")

            third = write_memory(
                "The stale-process pattern recurred",
                "A long-running process served an older artifact",
                "Verify the process start time before changing source code",
                ["stale-artifact", "superseding"],
                supersedes=[memory_ids[1]],
            )
            require(
                "Successfully saved" in third,
                "a verified memory must supersede an older lesson",
            )
            index = json.loads(mcp_server.INDEX_FILE.read_text(encoding="utf-8"))
            require(
                index["memories"][1]["status"] == "superseded",
                "superseded memory status must be updated",
            )

            read_result = mcp_server.guyue_read_memory("stale-artifact")
            read_entries = json.loads(read_result)
            require(
                len(read_entries) == 2,
                "lookup must return active entries and omit superseded ones",
            )
            require(
                all(entry["source"] == "local" for entry in read_entries),
                "runtime results must identify their source",
            )

            archived, messages = memory_gc.run_gc(
                memory_dir,
                now=dt.datetime(2026, 7, 10, tzinfo=dt.timezone.utc),
            )
            require(
                archived == 1,
                f"one due memory must be archived, got {archived}: {messages}",
            )
            index = json.loads(mcp_server.INDEX_FILE.read_text(encoding="utf-8"))
            archived_entry = index["memories"][0]
            require(
                archived_entry["status"] == "archived",
                "GC must update lifecycle status",
            )
            require(
                archived_entry["filename"].startswith("archive/"),
                "GC must update the detail path",
            )
            require(
                (memory_dir / archived_entry["filename"]).is_file(),
                "GC must preserve the full detail file",
            )
        finally:
            for name, value in originals.items():
                setattr(mcp_server, name, value)

    print("MCP route and memory lifecycle tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
