#!/usr/bin/env python3
import os
import glob
import time
import json
import sqlite3
from datetime import datetime

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_dir_stats(path):
    total_size = 0
    file_count = 0
    latest_mtime = 0
    latest_file = None
    
    try:
        for root, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    stat = os.stat(filepath)
                    total_size += stat.st_size
                    file_count += 1
                    if stat.st_mtime > latest_mtime:
                        latest_mtime = stat.st_mtime
                        latest_file = filepath
                except Exception:
                    continue
    except Exception:
        return {
            "exists": False,
            "total_size": 0,
            "file_count": 0,
            "latest_mtime": 0,
            "latest_file": None
        }
        
    return {
        "exists": file_count > 0,
        "total_size": total_size,
        "file_count": file_count,
        "latest_mtime": latest_mtime,
        "latest_file": latest_file
    }

def scan_cursor_workspaces():
    base_path = os.path.expanduser("~/Library/Application Support/Cursor/User/workspaceStorage/")
    if not os.path.exists(base_path):
        return None
        
    db_count = 0
    total_size = 0
    latest_mtime = 0
    
    try:
        for workspace in os.listdir(base_path):
            db_path = os.path.join(base_path, workspace, "state.vscdb")
            if os.path.exists(db_path):
                db_count += 1
                stat = os.stat(db_path)
                total_size += stat.st_size
                if stat.st_mtime > latest_mtime:
                    latest_mtime = stat.st_mtime
    except Exception:
        return None
        
    if db_count == 0:
        return None
        
    return {
        "exists": True,
        "total_size": total_size,
        "file_count": db_count,
        "latest_mtime": latest_mtime,
        "latest_file": "Multiple SQLite state.vscdb files"
    }

def main():
    print("# 📡 主动环境侦察 (AI Log Scanner) 报告\n")
    print("正在扫描系统内常见的 AI 助手会话矿脉...\n")
    
    targets = {
        "Gemini / Antigravity": os.path.expanduser("~/.gemini/antigravity/brain/"),
        "Claude Code": os.path.expanduser("~/.claude/projects/"),
        "Codex / Opencode": os.path.expanduser("~/.codex/sessions/"),
        "AutoGLM / AutoClaw": os.path.expanduser("~/.openclaw-autoclaw/workspace/")
    }
    
    found_any = False
    
    for name, path in targets.items():
        stats = get_dir_stats(path)
        if stats["exists"]:
            found_any = True
            mtime_str = datetime.fromtimestamp(stats["latest_mtime"]).strftime('%Y-%m-%d %H:%M:%S')
            print(f"### 🟢 {name}")
            print(f"- **路径**: `{path}`")
            print(f"- **体量**: {stats['file_count']} 个文件, 共 {format_size(stats['total_size'])}")
            print(f"- **最后活跃**: {mtime_str}")
            print(f"- **最新文件**: `{stats['latest_file']}`\n")
            
    # Special handler for Cursor
    cursor_stats = scan_cursor_workspaces()
    if cursor_stats:
        found_any = True
        name = "Cursor AI"
        path = "~/Library/Application Support/Cursor/User/workspaceStorage/*/state.vscdb"
        mtime_str = datetime.fromtimestamp(cursor_stats["latest_mtime"]).strftime('%Y-%m-%d %H:%M:%S')
        print(f"### 🟢 {name}")
        print(f"- **路径**: `{path}` (SQLite)")
        print(f"- **体量**: {cursor_stats['file_count']} 个数据库, 共 {format_size(cursor_stats['total_size'])}")
        print(f"- **最后活跃**: {mtime_str}")
        print(f"- **注意**: 请在 Guyue 仓库根目录运行 `python3 scripts/cursor_extractor.py` 进行安全读取，切勿直接 `cat`。\n")
        
    # Check for Aider in current dir
    aider_log = os.path.join(os.getcwd(), ".aider.chat.history.md")
    if os.path.exists(aider_log):
        found_any = True
        stat = os.stat(aider_log)
        mtime_str = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"### 🟢 Aider (当前工作区)")
        print(f"- **路径**: `{aider_log}`")
        print(f"- **体量**: {format_size(stat.st_size)}")
        print(f"- **最后活跃**: {mtime_str}\n")
        
    if not found_any:
        print("> [!WARNING]")
        print("> 未在标准路径下检测到主流 AI 工具的会话日志。请询问用户是否自定义了路径。")
    else:
        print("---\n")
        print("> [!TIP]")
        print("> **点单指南**: 上述矿脉已探明。请将其出示给用户，询问需要深入挖掘哪条矿脉。")
        print("> **提取纪律**: Agent 在提取数据时，必须使用专用的安全脚本以防显存爆炸：")
        print("> - Cursor SQLite: `python3 scripts/cursor_extractor.py <db_path> [--keyword xxx]`")
        print("> - Claude JSONL: `python3 scripts/claude_extractor.py <jsonl_path> [--keyword xxx]`")

if __name__ == "__main__":
    main()
