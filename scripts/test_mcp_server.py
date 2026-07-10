#!/usr/bin/env python3
"""Focused safety and behavior tests for the local Guyue MCP server."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src import mcp_server


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    original_memory_dir = mcp_server.MEMORY_DIR
    original_index_file = mcp_server.INDEX_FILE

    with tempfile.TemporaryDirectory(prefix="guyue-mcp-test-") as temp_dir:
        memory_dir = Path(temp_dir) / ".guyue_memory"
        mcp_server.MEMORY_DIR = memory_dir
        mcp_server.INDEX_FILE = memory_dir / "index.json"

        try:
            empty_result = mcp_server.guyue_read_memory("   ")
            require("must contain" in empty_result, "empty memory queries must be rejected")

            fake_credential = "sk" + "-" + "1234567890abcdefghijkl"
            secret_result = mcp_server.guyue_write_memory(
                "Provider request failed",
                f"The provider credential {fake_credential} was expired",
                "Rotate and redact the credential",
                ["provider"],
            )
            require("Refused" in secret_result, "secret-bearing memory must be rejected")
            require(not memory_dir.exists(), "rejected memory must not create storage files")

            personal_path = "/" + "Users" + "/example/private-project/config.json"
            path_result = mcp_server.guyue_write_memory(
                "A local file was missing",
                f"The command depended on {personal_path}",
                "Use a repository-relative path",
                ["portability"],
            )
            require("Refused" in path_result, "personal absolute paths must be rejected")
            require(not memory_dir.exists(), "rejected path memory must not create storage files")

            first = mcp_server.guyue_write_memory(
                "The release page showed stale assets",
                "A previous development server was still running",
                "Restart the server and inspect the served HTML",
                ["release", "stale-artifact"],
            )
            second = mcp_server.guyue_write_memory(
                "The theme script appeared missing",
                "The browser was connected to an old process",
                "Restart and compare the live artifact",
                ["theme", "stale-artifact"],
            )
            require("Successfully saved" in first and "Successfully saved" in second, "normal memories must be stored")

            index = json.loads(mcp_server.INDEX_FILE.read_text(encoding="utf-8"))
            filenames = [item["filename"] for item in index["memories"]]
            require(len(filenames) == 2, "two memory entries must be indexed")
            require(len(set(filenames)) == 2, "rapid writes must not collide")

            read_result = mcp_server.guyue_read_memory("stale-artifact")
            read_entries = json.loads(read_result)
            require(len(read_entries) == 2, "keyword lookup must return matching index entries")
        finally:
            mcp_server.MEMORY_DIR = original_memory_dir
            mcp_server.INDEX_FILE = original_index_file

    print("MCP server tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
