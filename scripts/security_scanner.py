#!/usr/bin/env python3
import argparse
import sys
import subprocess
import re
from pathlib import Path

sys.dont_write_bytecode = True

from security_patterns import find_project_fingerprint_matches, find_secret_matches  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


def print_status(msg, is_error=False):
    if is_error:
        print(f"❌ {msg}")
    else:
        print(f"✅ {msg}")


def list_release_files(repo_root=REPO_ROOT):
    repo_root = Path(repo_root).resolve()
    try:
        candidate_files_output = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            text=True,
            stderr=subprocess.STDOUT,
            cwd=repo_root,
        )
        candidate_files = [f for f in candidate_files_output.splitlines() if f.strip()]
        if not candidate_files:
            return []

        attr_output = subprocess.check_output(
            ["git", "check-attr", "--stdin", "export-ignore"],
            input="\n".join(candidate_files) + "\n",
            text=True,
            stderr=subprocess.STDOUT,
            cwd=repo_root,
        )
        ignored = {
            line.split(": ", 2)[0]
            for line in attr_output.splitlines()
            if line.endswith(": export-ignore: set")
        }
        return [Path(f) for f in candidate_files if f not in ignored]
    except (FileNotFoundError, subprocess.CalledProcessError):
        files = []
        for path in repo_root.rglob("*"):
            if not path.is_file():
                continue
            relative_path = path.relative_to(repo_root)
            if ".git" in relative_path.parts:
                continue
            files.append(relative_path)
        return files


def _scan_repository(repo_root):
    repo_root = Path(repo_root).resolve()
    print("==========================================")
    print("🔒 Running Zero-Leakage Security Scanner...")
    print("🔒 Scope: Guyue repository release payload")
    print("==========================================")

    release_files = list_release_files(repo_root)

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
    for path_obj in repo_root.rglob("*"):
        relative_path = path_obj.relative_to(repo_root)
        if workspace_exclusions.intersection(relative_path.parts):
            continue
        if (
            path_obj.name in {'__pycache__', '.ruff_cache', '.DS_Store'}
            or path_obj.suffix == '.pyc'
        ):
            generated_bloat.append(relative_path)
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

    print("\n[2/2] Scanning file contents for secrets, project fingerprints, and personal paths...")
    secret_errors = 0
    fingerprint_errors = 0
    for path_obj in release_files:
        f_path = path_obj.as_posix()
        absolute_path = repo_root / path_obj
        if not absolute_path.is_file():
            continue

        if path_obj.suffix.lower() in ignore_content_extensions:
            continue

        try:
            with absolute_path.open('r', encoding='utf-8') as f:
                for line_idx, line in enumerate(f):
                    for desc in find_secret_matches(line):
                        print_status(
                            f"Security Leak [{desc}] found in {f_path} "
                            f"(line {line_idx + 1}; content redacted)",
                            is_error=True,
                        )
                        secret_errors += 1
                        has_error = True
                    for desc in find_project_fingerprint_matches(line):
                        print_status(
                            f"Project Fingerprint [{desc}] found in {f_path} "
                            f"(line {line_idx + 1}; content redacted)",
                            is_error=True,
                        )
                        fingerprint_errors += 1
                        has_error = True
        except UnicodeDecodeError:
            print_status(f"Undeclared binary or undecodable release file: {f_path}", is_error=True)
            has_error = True
        except OSError as exc:
            print_status(f"Could not read release file {f_path}: {exc}", is_error=True)
            has_error = True

    if secret_errors == 0 and fingerprint_errors == 0:
        print_status("No secrets, project fingerprints, or personal paths detected in contents.")

    if has_error:
        print("\n> [!CAUTION]")
        print("> 🚨 Zero-Leakage scanner found violations! Commit blocked.")
        print("> Please clean up caches or remove sensitive secrets/paths before proceeding.")
        return 1
    else:
        print("\n✅ Zero-Leakage check passed! Clean as a whistle.")
        return 0


def run_security_scan():
    return _scan_repository(REPO_ROOT)


def build_parser():
    return argparse.ArgumentParser(
        description=(
            "Run Guyue's repository-local Zero-Leakage release gate. "
            "This command does not scan the caller's project."
        )
    )


def main(argv=None):
    build_parser().parse_args(argv)
    return run_security_scan()


if __name__ == "__main__":
    raise SystemExit(main())
