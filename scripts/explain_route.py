#!/usr/bin/env python3
"""Explain Guyue Skill candidates for one user intent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.skill_router import resolve_routes  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", help="user intent to route")
    parser.add_argument(
        "--context-marker",
        action="append",
        default=[],
        help="verified project or environment marker; repeat as needed",
    )
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    manifest = json.loads((ROOT / "skills_manifest.json").read_text(encoding="utf-8"))
    try:
        result = resolve_routes(
            manifest,
            args.intent,
            context_markers=args.context_marker,
            limit=args.limit,
        )
    except ValueError as exc:
        parser.error(str(exc))

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["selected"] else 2

    if not result["selected"]:
        print("No route reached the local evidence threshold.")
        return 2
    print("Guyue route candidates:")
    for index, route in enumerate(result["selected"], start=1):
        trigger_evidence = ", ".join(
            item["trigger"] for item in route["matched_triggers"]
        ) or "description similarity"
        context_evidence = ", ".join(route["matched_context"])
        suffix = f"; context={context_evidence}" if context_evidence else ""
        print(
            f"{index}. {route['name']} score={route['score']:.3f}; "
            f"evidence={trigger_evidence}{suffix}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
