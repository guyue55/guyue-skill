#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_step(label, command):
    print(f"[Trace: Guyue/Install] {label}", flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def optional_dependency_command(mode):
    base = [sys.executable, "scripts/install_optional_dependencies.py"]
    if mode == "plan":
        return base
    if mode == "safe":
        return base + ["--install"]
    if mode == "all":
        return base + ["--install", "--force"]
    raise ValueError(f"unknown optional dependency mode: {mode}")


def main():
    parser = argparse.ArgumentParser(
        description="Install Guyue runtime dependencies and optional enhancement skills."
    )
    parser.add_argument(
        "--skip-python-deps",
        action="store_true",
        help="Skip pip install -r requirements.txt.",
    )
    parser.add_argument(
        "--skip-optional-skills",
        action="store_true",
        help="Skip optional third-party skill detection and installation.",
    )
    parser.add_argument(
        "--optional-mode",
        choices=["all", "safe", "plan"],
        default="plan",
        help=(
            "Optional skill behavior: plan only prints a dry-run plan (default); safe installs "
            "green dependencies and stops on yellow/red findings; all requires explicit opt-in "
            "and force-installs every reviewed manifest dependency."
        ),
    )
    parser.add_argument(
        "--skip-doctor",
        action="store_true",
        help="Skip the final dependency doctor check.",
    )
    args = parser.parse_args()

    if not args.skip_python_deps:
        run_step(
            "installing Python runtime requirements",
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        )

    if not args.skip_optional_skills:
        run_step(
            f"installing optional enhancement skills ({args.optional_mode})",
            optional_dependency_command(args.optional_mode),
        )

    if not args.skip_doctor:
        run_step("running dependency doctor", [sys.executable, "scripts/doctor.py"])

    print("[Trace: Guyue/Install] complete", flush=True)


if __name__ == "__main__":
    main()
