#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

MEMORY_DIR = Path(os.getenv("GUYUE_MEMORY_DIR", "./.guyue_memory"))
TRACE_PATTERN = re.compile(r"\[Trace:\s*(Guyue/[^\]]+)\]\s*(.*)")

def scan_traces():
    if not MEMORY_DIR.exists():
        print(f"Memory directory {MEMORY_DIR} not found.")
        return

    traces = []
    
    # Scan all active memory files
    active_dir = MEMORY_DIR / "active"
    if active_dir.exists():
        for md_file in active_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            for line_no, line in enumerate(content.splitlines(), 1):
                match = TRACE_PATTERN.search(line)
                if match:
                    phase = match.group(1).strip()
                    message = match.group(2).strip()
                    traces.append({
                        "file": md_file.name,
                        "line": line_no,
                        "phase": phase,
                        "message": message
                    })

    if not traces:
        print("No trace logs found in active memory.")
        return

    print("\n🔍 Guyue Trace Auditor Report")
    print("=========================================")
    
    # Group by file
    traces_by_file = defaultdict(list)
    for t in traces:
        traces_by_file[t['file']].append(t)

    for file_name, file_traces in traces_by_file.items():
        print(f"\n📂 File: {file_name}")
        for t in file_traces:
            print(f"  [{t['phase']}] (Line {t['line']}): {t['message']}")

    print("\n✅ Trace audit complete.")

if __name__ == "__main__":
    scan_traces()
