#!/usr/bin/env python3
"""Regression tests for bounded Codex session extraction."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True

import codex_extractor  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def record(record_type: str, timestamp: str, payload: dict) -> str:
    return json.dumps({"type": record_type, "timestamp": timestamp, "payload": payload})


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="guyue-codex-extractor-") as temp_dir:
        root = Path(temp_dir)
        session_path = root / "rollout-demo.jsonl"
        secret = "sk" + "-" + "abcdefghijklmnopqrstuvwxyz123456"
        personal_path = "/" + "Users" + "/example/private/project"
        redacted_home = "/" + "Users" + "/<redacted>/"
        rows = [
            record(
                "session_meta",
                "2026-07-10T00:00:00Z",
                {
                    "cwd": personal_path,
                    "session_id": "session-1",
                    "originator": "Codex Desktop",
                    "thread_source": "subagent",
                    "cli_version": "0.144.1",
                },
            ),
            record(
                "event_msg",
                "2026-07-10T00:00:01Z",
                {
                    "type": "user_message",
                    "message": f"Check {personal_path} and redact {secret}",
                },
            ),
            record(
                "event_msg",
                "2026-07-10T00:00:02Z",
                {
                    "type": "user_message",
                    "message": f"Check {personal_path} and redact {secret}",
                },
            ),
            record(
                "response_item",
                "2026-07-10T00:00:03Z",
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": "I am checking the evidence."}
                    ],
                    "internal_chat_message_metadata_passthrough": {"turn_id": "turn-1"},
                },
            ),
            record(
                "response_item",
                "2026-07-10T00:00:04Z",
                {
                    "type": "message",
                    "role": "developer",
                    "content": [
                        {"type": "input_text", "text": "private developer instruction"}
                    ],
                },
            ),
            record(
                "response_item",
                "2026-07-10T00:00:05Z",
                {
                    "type": "function_call_output",
                    "output": "private tool output",
                },
            ),
            record(
                "response_item",
                "2026-07-10T00:00:06Z",
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": "Done with fresh evidence."}
                    ],
                    "internal_chat_message_metadata_passthrough": {"turn_id": "turn-1"},
                },
            ),
            record(
                "event_msg",
                "2026-07-10T00:00:07Z",
                {"type": "task_complete", "turn_id": "turn-1"},
            ),
            "{malformed",
        ]
        session_path.write_text("\n".join(rows) + "\n", encoding="utf-8")

        session = codex_extractor.parse_session(
            session_path,
            {"user", "commentary", "final"},
            max_chars=4000,
        )
        require(session.cwd == personal_path, "session cwd must be captured")
        require(session.session_id == "session-1", "session id must be captured")
        require(session.thread_source == "subagent", "thread source must be captured")
        require(session.originator == "Codex Desktop", "originator must be captured")
        require(session.cli_version == "0.144.1", "CLI version must be captured")
        require(
            session.first_timestamp == "2026-07-10T00:00:00Z"
            and session.last_timestamp == "2026-07-10T00:00:07Z",
            "session timestamp bounds must be captured",
        )
        require(
            session.malformed_lines == 1,
            "malformed lines must be counted without disclosure",
        )
        require(
            [message.role for message in session.messages]
            == ["user", "user", "commentary", "final"],
            "roles must be classified by completed turn",
        )
        combined = "\n".join(message.text for message in session.messages)
        require(
            "private developer instruction" not in combined,
            "developer messages must not be extracted",
        )
        require(
            "private tool output" not in combined, "tool output must not be extracted"
        )
        require(
            secret not in combined and "[REDACTED:provider API key]" in combined,
            "credentials must be redacted",
        )
        require(redacted_home in combined, "personal home roots must be redacted")

        filtered = codex_extractor.filter_messages(
            [session],
            cwd=personal_path,
            since=codex_extractor.parse_time("2026-07-10"),
            until=None,
            keyword=None,
            dedupe=True,
            limit=20,
        )
        require(len(filtered) == 3, "dedupe must remove the repeated user message")
        final_only = codex_extractor.filter_messages(
            [session],
            cwd=personal_path,
            since=None,
            until=None,
            keyword="fresh evidence",
            dedupe=False,
            limit=20,
        )
        require(
            len(final_only) == 1 and final_only[0].role == "final",
            "keyword filtering must retain the matching final",
        )
        require(
            not codex_extractor.filter_messages(
                [session],
                cwd="/workspace/other",
                since=None,
                until=None,
                keyword=None,
                dedupe=False,
                limit=20,
            ),
            "cwd filtering must reject unrelated sessions",
        )
        before_final = codex_extractor.filter_messages(
            [session],
            cwd=personal_path,
            since=None,
            until=codex_extractor.parse_time("2026-07-10T00:00:05Z"),
            keyword=None,
            dedupe=True,
            limit=20,
        )
        require(
            [message.role for message in before_final] == ["user", "commentary"],
            "until must freeze the evidence window before later messages",
        )
        end_of_day = codex_extractor.parse_bound(
            "2026-07-10", end_of_day=True
        )
        require(
            end_of_day is not None
            and end_of_day.isoformat() == "2026-07-10T23:59:59.999999+00:00",
            "date-only until bounds must include the full UTC day",
        )
        require(
            codex_extractor.filter_sessions([session], {"subagent"}) == [session],
            "thread-source filtering must retain matching subagent sessions",
        )
        require(
            not codex_extractor.filter_sessions([session], {"user"}),
            "thread-source filtering must reject unrelated main sessions",
        )
        inventory = codex_extractor.build_inventory([session])
        require(len(inventory) == 1, "inventory must include the parsed session")
        require(
            inventory[0]["cwd"] == redacted_home + "private/project",
            "inventory must redact personal home roots",
        )
        require(
            inventory[0]["thread_source"] == "subagent"
            and inventory[0]["message_count"] == 4,
            "inventory must expose bounded routing and message metadata",
        )
        stats = codex_extractor.build_stats(
            [session_path, session_path],
            [session],
            filtered,
            parsed_count=2,
            window_count=1,
            window_source_counts={"subagent": 1},
        )
        require(
            stats["malformed_lines"] == 1
            and stats["messages_emitted"] == 3
            and stats["sessions_parsed"] == 2
            and stats["sessions_selected"] == 1
            and stats["sessions_in_window"] == 1
            and stats["window_thread_sources"] == {"subagent": 1},
            "stats must separate parsed sessions, selected sessions, and bounded output",
        )

    print("Codex extractor tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
