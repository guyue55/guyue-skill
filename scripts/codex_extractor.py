#!/usr/bin/env python3
"""Extract bounded user/final evidence from Codex rollout JSONL sessions."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from security_patterns import redact_sensitive_text  # noqa: E402


ALLOWED_ROLES = {"user", "final", "assistant", "commentary"}


@dataclass
class Message:
    role: str
    text: str
    timestamp: str
    session: str
    turn_id: str = ""


@dataclass
class SessionResult:
    source: str
    cwd: str
    session_id: str
    messages: list[Message]
    originator: str = ""
    thread_source: str = ""
    cli_version: str = ""
    first_timestamp: str = ""
    last_timestamp: str = ""
    malformed_lines: int = 0


def parse_time(value: str) -> dt.datetime | None:
    if not value:
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError:
        try:
            parsed = dt.datetime.fromisoformat(normalized + "T00:00:00+00:00")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def parse_bound(value: str, *, end_of_day: bool = False) -> dt.datetime | None:
    """Parse an ISO bound, treating a date-only upper bound as the full day."""
    parsed = parse_time(value)
    if parsed and end_of_day and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
        parsed += dt.timedelta(days=1) - dt.timedelta(microseconds=1)
    return parsed


def extract_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for item in content:
        if not isinstance(item, dict):
            continue
        if item.get("type") not in {"input_text", "output_text", "text"}:
            continue
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts)


def bounded_text(text: str, max_chars: int) -> str:
    redacted = redact_sensitive_text(text.strip())
    if len(redacted) <= max_chars:
        return redacted
    return redacted[:max_chars].rstrip() + "\n...[truncated]"


def parse_session(path: Path, roles: set[str], max_chars: int) -> SessionResult:
    result = SessionResult(source=path.name, cwd="", session_id="", messages=[])
    pending_assistant: dict[str, list[Message]] = {}

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                result.malformed_lines += 1
                continue
            if not isinstance(record, dict):
                continue
            timestamp = str(record.get("timestamp", ""))
            if timestamp:
                result.first_timestamp = result.first_timestamp or timestamp
                result.last_timestamp = timestamp
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            record_type = record.get("type")
            payload_type = payload.get("type")

            if record_type == "session_meta":
                result.cwd = result.cwd or str(payload.get("cwd", ""))
                result.session_id = result.session_id or str(
                    payload.get("session_id") or payload.get("id") or ""
                )
                result.originator = result.originator or str(
                    payload.get("originator", "")
                )
                result.thread_source = result.thread_source or str(
                    payload.get("thread_source", "")
                )
                result.cli_version = result.cli_version or str(
                    payload.get("cli_version", "")
                )
                continue

            if record_type == "event_msg" and payload_type == "user_message":
                if "user" not in roles:
                    continue
                raw_text = payload.get("message") or payload.get("text") or ""
                if isinstance(raw_text, str) and raw_text.strip():
                    result.messages.append(
                        Message(
                            "user",
                            bounded_text(raw_text, max_chars),
                            timestamp,
                            path.name,
                        )
                    )
                continue

            if (
                record_type == "response_item"
                and payload_type == "message"
                and payload.get("role") == "assistant"
            ):
                metadata = payload.get("internal_chat_message_metadata_passthrough")
                turn_id = (
                    str(metadata.get("turn_id", ""))
                    if isinstance(metadata, dict)
                    else ""
                )
                text = extract_content(payload.get("content"))
                if not text:
                    continue
                message = Message(
                    "assistant",
                    bounded_text(text, max_chars),
                    timestamp,
                    path.name,
                    turn_id,
                )
                pending_assistant.setdefault(turn_id, []).append(message)
                if "assistant" in roles:
                    result.messages.append(message)
                continue

            if record_type == "event_msg" and payload_type == "task_complete":
                turn_id = str(payload.get("turn_id", ""))
                buffered = pending_assistant.pop(turn_id, [])
                if not buffered:
                    continue
                if "commentary" in roles and "assistant" not in roles:
                    for message in buffered[:-1]:
                        result.messages.append(
                            Message(
                                "commentary",
                                message.text,
                                message.timestamp,
                                path.name,
                                turn_id,
                            )
                        )
                if "final" in roles and "assistant" not in roles:
                    final = buffered[-1]
                    result.messages.append(
                        Message(
                            "final", final.text, final.timestamp, path.name, turn_id
                        )
                    )

    return result


def discover_paths(inputs: list[str]) -> list[Path]:
    discovered: set[Path] = set()
    for raw in inputs:
        path = Path(raw).expanduser()
        if path.is_dir():
            discovered.update(
                item.resolve() for item in path.rglob("*.jsonl") if item.is_file()
            )
        elif path.is_file():
            discovered.add(path.resolve())
    return sorted(discovered)


def filter_messages(
    sessions: list[SessionResult],
    *,
    cwd: str | None,
    since: dt.datetime | None,
    until: dt.datetime | None,
    keyword: str | None,
    dedupe: bool,
    limit: int,
) -> list[Message]:
    selected: list[Message] = []
    seen: set[str] = set()
    cwd_filter = str(Path(cwd).expanduser().resolve()) if cwd else ""
    keyword_filter = keyword.casefold() if keyword else ""

    for session in sessions:
        if cwd_filter:
            try:
                session_cwd = str(Path(session.cwd).expanduser().resolve())
            except OSError:
                session_cwd = session.cwd
            if session_cwd != cwd_filter:
                continue
        for message in session.messages:
            message_time = parse_time(message.timestamp)
            if since and (not message_time or message_time < since):
                continue
            if until and (not message_time or message_time > until):
                continue
            if keyword_filter and keyword_filter not in message.text.casefold():
                continue
            if dedupe:
                normalized = " ".join(message.text.casefold().split())
                digest = hashlib.sha256(
                    f"{message.role}\0{normalized}".encode()
                ).hexdigest()
                if digest in seen:
                    continue
                seen.add(digest)
            selected.append(message)
            if len(selected) >= limit:
                return selected
    return selected


def filter_sessions(
    sessions: list[SessionResult],
    thread_sources: set[str],
    cwd: str | None = None,
) -> list[SessionResult]:
    """Return sessions whose recorded source is in the requested source set."""
    cwd_filter = str(Path(cwd).expanduser().resolve()) if cwd else ""
    selected = []
    for session in sessions:
        if thread_sources and session.thread_source not in thread_sources:
            continue
        if cwd_filter:
            try:
                session_cwd = str(Path(session.cwd).expanduser().resolve())
            except OSError:
                session_cwd = session.cwd
            if session_cwd != cwd_filter:
                continue
        selected.append(session)
    return selected


def build_inventory(
    sessions: list[SessionResult],
    *,
    since: dt.datetime | None = None,
    until: dt.datetime | None = None,
) -> list[dict]:
    """Build a bounded, redacted session inventory without message bodies."""
    inventory = []
    for session in sessions:
        window_messages = []
        for message in session.messages:
            message_time = parse_time(message.timestamp)
            if since and (not message_time or message_time < since):
                continue
            if until and (not message_time or message_time > until):
                continue
            window_messages.append(message)
        if (since or until) and not window_messages:
            continue
        inventory.append(
            {
                "source": session.source,
                "session_id": session.session_id,
                "cwd": redact_sensitive_text(session.cwd),
                "originator": session.originator,
                "thread_source": session.thread_source,
                "cli_version": session.cli_version,
                "first_timestamp": session.first_timestamp,
                "last_timestamp": session.last_timestamp,
                "window_first_timestamp": (
                    window_messages[0].timestamp if window_messages else ""
                ),
                "window_last_timestamp": (
                    window_messages[-1].timestamp if window_messages else ""
                ),
                "message_count": len(window_messages),
                "malformed_lines": session.malformed_lines,
            }
        )
    return inventory


def render_markdown(messages: list[Message], stats: dict | None) -> str:
    lines = ["# Codex Session Evidence", ""]
    current_session = ""
    for message in messages:
        if message.session != current_session:
            current_session = message.session
            lines.extend([f"## {current_session}", ""])
        timestamp = f" · {message.timestamp}" if message.timestamp else ""
        lines.extend([f"### {message.role}{timestamp}", "", message.text, ""])
    if not messages:
        lines.extend(["> No matching messages.", ""])
    if stats is not None:
        lines.extend(["## Stats", ""])
        for key, value in stats.items():
            lines.append(f"- {key}: {value}")
    return "\n".join(lines).rstrip() + "\n"


def render_inventory_markdown(inventory: list[dict], stats: dict | None) -> str:
    lines = ["# Codex Session Inventory", ""]
    for item in inventory:
        lines.extend(
            [
                f"## {item['source']}",
                "",
                f"- session_id: {item['session_id'] or '<unknown>'}",
                f"- thread_source: {item['thread_source'] or '<unknown>'}",
                f"- cwd: {item['cwd'] or '<unknown>'}",
                f"- originator: {item['originator'] or '<unknown>'}",
                f"- cli_version: {item['cli_version'] or '<unknown>'}",
                f"- first_timestamp: {item['first_timestamp'] or '<unknown>'}",
                f"- last_timestamp: {item['last_timestamp'] or '<unknown>'}",
                f"- window_first_timestamp: {item['window_first_timestamp'] or '<none>'}",
                f"- window_last_timestamp: {item['window_last_timestamp'] or '<none>'}",
                f"- message_count: {item['message_count']}",
                f"- malformed_lines: {item['malformed_lines']}",
                "",
            ]
        )
    if not inventory:
        lines.extend(["> No matching sessions.", ""])
    if stats is not None:
        lines.extend(["## Stats", ""])
        for key, value in stats.items():
            lines.append(f"- {key}: {value}")
    return "\n".join(lines).rstrip() + "\n"


def build_stats(
    paths: list[Path],
    sessions: list[SessionResult],
    messages: list[Message],
    *,
    parsed_count: int | None = None,
    window_count: int | None = None,
    window_source_counts: dict[str, int] | None = None,
) -> dict:
    role_counts = Counter(message.role for message in messages)
    source_counts = Counter(session.thread_source or "unknown" for session in sessions)
    return {
        "files_scanned": len(paths),
        "sessions_parsed": parsed_count if parsed_count is not None else len(sessions),
        "sessions_selected": len(sessions),
        "sessions_in_window": window_count if window_count is not None else len(sessions),
        "messages_emitted": len(messages),
        "malformed_lines": sum(session.malformed_lines for session in sessions),
        "roles": dict(sorted(role_counts.items())),
        "thread_sources": dict(sorted(source_counts.items())),
        "window_thread_sources": dict(
            sorted((window_source_counts or dict(source_counts)).items())
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Codex JSONL files or directories")
    parser.add_argument(
        "--cwd", help="only sessions whose recorded cwd exactly matches this path"
    )
    parser.add_argument("--since", help="ISO timestamp or YYYY-MM-DD lower bound")
    parser.add_argument("--until", help="inclusive ISO timestamp or date upper bound")
    parser.add_argument(
        "--thread-source",
        help="comma-separated recorded sources, for example user,subagent",
    )
    parser.add_argument("--keyword", help="case-insensitive message keyword")
    parser.add_argument(
        "--roles",
        default="user,final",
        help="comma-separated: user,final,assistant,commentary",
    )
    parser.add_argument(
        "--dedupe", action="store_true", help="remove duplicate role/text pairs"
    )
    parser.add_argument(
        "--stats", action="store_true", help="include aggregate extraction statistics"
    )
    parser.add_argument("--format", choices=("md", "json"), default="md")
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="emit redacted session metadata instead of message bodies",
    )
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--max-chars", type=int, default=4000)
    args = parser.parse_args()

    roles = {role.strip() for role in args.roles.split(",") if role.strip()}
    unknown_roles = roles - ALLOWED_ROLES
    if not roles or unknown_roles:
        parser.error("--roles must contain only user, final, assistant, commentary")
    if "assistant" in roles and roles.intersection({"final", "commentary"}):
        parser.error(
            "--roles assistant is the raw all-assistant mode and cannot be combined with final/commentary"
        )
    if args.limit <= 0 or args.max_chars <= 0:
        parser.error("--limit and --max-chars must be positive")
    since = parse_bound(args.since or "")
    if args.since and not since:
        parser.error("--since must be ISO timestamp or YYYY-MM-DD")
    until = parse_bound(args.until or "", end_of_day=True)
    if args.until and not until:
        parser.error("--until must be ISO timestamp or YYYY-MM-DD")
    if since and until and since > until:
        parser.error("--since must not be later than --until")
    thread_sources = {
        value.strip()
        for value in (args.thread_source or "").split(",")
        if value.strip()
    }
    unknown_sources = thread_sources - {"user", "subagent"}
    if unknown_sources:
        parser.error("--thread-source must contain only user or subagent")

    paths = discover_paths(args.paths)
    if not paths:
        parser.error("no JSONL files found")
    parsed_sessions = [parse_session(path, roles, args.max_chars) for path in paths]
    sessions = filter_sessions(
        parsed_sessions,
        thread_sources,
        cwd=args.cwd,
    )
    messages = filter_messages(
        sessions,
        cwd=args.cwd,
        since=since,
        until=until,
        keyword=args.keyword,
        dedupe=args.dedupe,
        limit=args.limit,
    )
    inventory = (
        build_inventory(sessions, since=since, until=until)
        if args.inventory or args.stats
        else []
    )
    stats = (
        build_stats(
            paths,
            sessions,
            messages,
            parsed_count=len(parsed_sessions),
            window_count=len(inventory),
            window_source_counts=dict(
                Counter(item["thread_source"] or "unknown" for item in inventory)
            ),
        )
        if args.stats
        else None
    )

    if args.inventory:
        if args.format == "json":
            payload = {"sessions": inventory}
            if stats is not None:
                payload["stats"] = stats
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(render_inventory_markdown(inventory, stats), end="")
    elif args.format == "json":
        payload = {"messages": [asdict(message) for message in messages]}
        if stats is not None:
            payload["stats"] = stats
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(messages, stats), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
