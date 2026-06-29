#!/usr/bin/env python3
import sys
import subprocess
import re
from pathlib import Path

def print_status(msg, is_error=False):
    if is_error:
        print(f"❌ {msg}")
    else:
        print(f"✅ {msg}")

def run_security_scan():
    print("==========================================")
    print("🔒 Running Zero-Leakage Security Scanner...")
    print("==========================================")

    # 1. Get all tracked files
    try:
        tracked_files_output = subprocess.check_output(
            ["git", "ls-files"], text=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to run git ls-files: {e.output}", is_error=True)
        sys.exit(1)

    tracked_files = [f for f in tracked_files_output.splitlines() if f.strip()]

    # 2. Define bloated/cache files rules (Anti-Bloat)
    bloat_patterns = [
        re.compile(r'__pycache__/'),
        re.compile(r'\.pyc$'),
        re.compile(r'\.DS_Store$'),
        re.compile(r'\.env$'),
        re.compile(r'\.idea/'),
        re.compile(r'\.vscode/'),
    ]

    # 3. Define secret/privacy patterns (Anti-Leak)
    secret_patterns = [
        (re.compile(r'sk-[a-zA-Z0-9_-]{20,}'), "Potential API Key (sk-...)"),
        (re.compile(r'AIza[0-9A-Za-z-_]{35}'), "Google API Key"),
        (re.compile(r'(?i)api[_-]?key[\s]*=[\s]*[\'"]?[a-zA-Z0-9_\-]{16,}'), "Generic API Key Assignment"),
        (re.compile(r'(?i)token[\s]*=[\s]*[\'"]?[a-zA-Z0-9_\-]{16,}'), "Generic Token Assignment"),
        (re.compile(r'/User' + r's/apple/'), "Hardcoded personal path (/User" + "s/apple/)"),
    ]

    # Ignore checking contents of specific binary or safe files
    ignore_content_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov']
    ignore_content_paths = ['GUYUE_PRINCIPLES.md', 'scripts/security_scanner.py', 'scripts/ci_validate_skills.py']

    has_error = False

    print("[1/2] Scanning for bloat and cache files...")
    for f_path in tracked_files:
        for p in bloat_patterns:
            if p.search(f_path):
                print_status(f"Bloat file tracked in Git: {f_path}", is_error=True)
                has_error = True

    if not has_error:
        print_status("No bloat files detected.")

    print("\n[2/2] Scanning file contents for secrets and personal paths...")
    secret_errors = 0
    for f_path in tracked_files:
        path_obj = Path(f_path)
        if not path_obj.is_file():
            continue
            
        if path_obj.suffix.lower() in ignore_content_extensions:
            continue
            
        if any(f_path.endswith(ignore_path) for ignore_path in ignore_content_paths):
            continue

        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                for line_idx, line in enumerate(f):
                    for pattern, desc in secret_patterns:
                        if pattern.search(line):
                            print_status(f"Security Leak [{desc}] found in {f_path} (line {line_idx + 1})", is_error=True)
                            print(f"   -> {line.strip()[:100]}...")  # Truncated for display
                            secret_errors += 1
                            has_error = True
        except UnicodeDecodeError:
            # Skip binary files that slipped through extension check
            pass

    if secret_errors == 0:
        print_status("No secrets or personal paths detected in contents.")

    if has_error:
        print("\n> [!CAUTION]")
        print("> 🚨 Zero-Leakage scanner found violations! Commit blocked.")
        print("> Please clean up caches or remove sensitive secrets/paths before proceeding.")
        sys.exit(1)
    else:
        print("\n✅ Zero-Leakage check passed! Clean as a whistle.")
        sys.exit(0)

if __name__ == "__main__":
    run_security_scan()
