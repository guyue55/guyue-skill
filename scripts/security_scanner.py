#!/usr/bin/env python3
import sys
import subprocess
import re
from pathlib import Path

sys.dont_write_bytecode = True

from security_patterns import find_secret_matches  # noqa: E402

def print_status(msg, is_error=False):
    if is_error:
        print(f"❌ {msg}")
    else:
        print(f"✅ {msg}")


def list_release_files():
    try:
        candidate_files_output = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            text=True,
            stderr=subprocess.STDOUT,
        )
        candidate_files = [f for f in candidate_files_output.splitlines() if f.strip()]
        if not candidate_files:
            return []

        attr_output = subprocess.check_output(
            ["git", "check-attr", "--stdin", "export-ignore"],
            input="\n".join(candidate_files) + "\n",
            text=True,
            stderr=subprocess.STDOUT,
        )
        ignored = {
            line.split(": ", 2)[0]
            for line in attr_output.splitlines()
            if line.endswith(": export-ignore: set")
        }
        return [Path(f) for f in candidate_files if f not in ignored]
    except (FileNotFoundError, subprocess.CalledProcessError):
        files = []
        for path in Path(".").rglob("*"):
            if not path.is_file():
                continue
            if ".git" in path.parts:
                continue
            files.append(path)
        return files


def run_security_scan():
    print("==========================================")
    print("🔒 Running Zero-Leakage Security Scanner...")
    print("==========================================")

    release_files = list_release_files()

    # Release-only patterns and whole-worktree generated cache rules.
    bloat_patterns = [
        re.compile(r'\.env$'),
        re.compile(r'\.idea/'),
        re.compile(r'\.vscode/'),
    ]
    workspace_exclusions = {'.git', 'node_modules', '.venv', 'venv'}

    # 二进制媒体不做文本扫描；代码和规则文件不再整文件豁免。
    ignore_content_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov']

    has_error = False

    print("[1/2] Scanning for bloat and cache files...")
    generated_bloat = []
    for path_obj in Path('.').rglob('*'):
        if workspace_exclusions.intersection(path_obj.parts):
            continue
        if path_obj.name == '__pycache__' or path_obj.name == '.DS_Store' or path_obj.suffix == '.pyc':
            generated_bloat.append(path_obj)
    for path_obj in sorted(generated_bloat):
        print_status(f"Generated cache present in worktree: {path_obj.as_posix()}", is_error=True)
        has_error = True

    for path_obj in release_files:
        f_path = path_obj.as_posix()
        for p in bloat_patterns:
            if p.search(f_path):
                print_status(f"Bloat or cache file present: {f_path}", is_error=True)
                has_error = True
                break

    if not has_error:
        print_status("No bloat files detected.")

    print("\n[2/2] Scanning file contents for secrets and personal paths...")
    secret_errors = 0
    for path_obj in release_files:
        f_path = path_obj.as_posix()
        if not path_obj.is_file():
            continue
            
        if path_obj.suffix.lower() in ignore_content_extensions:
            continue
            
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                for line_idx, line in enumerate(f):
                    for desc in find_secret_matches(line):
                        print_status(f"Security Leak [{desc}] found in {f_path} (line {line_idx + 1})", is_error=True)
                        print(f"   -> {line.strip()[:100]}...")
                        secret_errors += 1
                        has_error = True
        except UnicodeDecodeError:
            print_status(f"Undeclared binary or undecodable release file: {f_path}", is_error=True)
            has_error = True
        except OSError as exc:
            print_status(f"Could not read release file {f_path}: {exc}", is_error=True)
            has_error = True

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
