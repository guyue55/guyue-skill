#!/usr/bin/env python3
import os
import sys
import time
import shutil
from pathlib import Path

# Configuration
MEMORY_DIR = Path(os.getenv("GUYUE_MEMORY_DIR", "./.guyue_memory"))
ACTIVE_DIR = MEMORY_DIR / "active"
ARCHIVE_DIR = MEMORY_DIR / "archive"
MAX_FILE_SIZE_BYTES = 50 * 1024  # 50 KB
MAX_AGE_DAYS = 7

def setup_directories():
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    global_ctx = MEMORY_DIR / "global_context.md"
    if not global_ctx.exists():
        global_ctx.write_text("# Global Context\n\n- Name: guyue\n- Role: Digital Twin Orchestrator\n- Principle: Keep context minimal and efficient.\n")

def check_bloat(file_path: Path):
    """Check if file exceeds size or age limits."""
    stats = file_path.stat()
    age_days = (time.time() - stats.st_mtime) / (24 * 3600)
    size_kb = stats.st_size / 1024
    
    if size_kb > (MAX_FILE_SIZE_BYTES / 1024):
        return True, f"Size {size_kb:.1f}KB > {MAX_FILE_SIZE_BYTES/1024}KB"
    if age_days > MAX_AGE_DAYS:
        return True, f"Age {age_days:.1f} days > {MAX_AGE_DAYS} days"
    return False, ""

def generate_naive_summary(content: str, filename: str) -> str:
    """Generate a naive summary by taking the first and last few lines if no LLM is present."""
    lines = content.splitlines()
    if len(lines) < 20:
        return content
    
    summary = f"# [ARCHIVED] {filename}\n\n"
    summary += "> Note: This is an auto-archived memory to prevent context bloat.\n\n"
    summary += "### Original Header\n"
    summary += "\n".join(lines[:10]) + "\n...\n"
    summary += "### Original Footer\n"
    summary += "\n".join(lines[-10:]) + "\n"
    return summary

def run_gc():
    print(f"🧹 Running Guyue Memory GC (Garbage Collection)...")
    setup_directories()
    
    if not ACTIVE_DIR.exists():
        print(f"No active directory found at {ACTIVE_DIR}")
        return

    archived_count = 0
    for md_file in ACTIVE_DIR.glob("*.md"):
        needs_gc, reason = check_bloat(md_file)
        if needs_gc:
            print(f"  [GC TARGET] {md_file.name} - Reason: {reason}")
            try:
                content = md_file.read_text(encoding="utf-8")
                # In a full AI workflow, this calls an LLM. For the script, we do naive summary
                # to save tokens and prevent blocking. Agents can refine this later if needed.
                summary = generate_naive_summary(content, md_file.name)
                
                archive_path = ARCHIVE_DIR / f"{md_file.stem}_archived.md"
                archive_path.write_text(summary, encoding="utf-8")
                
                md_file.unlink()
                print(f"  -> Archived to {archive_path.relative_to(MEMORY_DIR)}")
                archived_count += 1
            except Exception as e:
                print(f"  -> Error processing {md_file.name}: {e}")
                
    if archived_count == 0:
        print("✅ Memory bank is healthy. No GC required.")
    else:
        print(f"✅ GC Complete. {archived_count} memory files archived.")

if __name__ == "__main__":
    run_gc()
