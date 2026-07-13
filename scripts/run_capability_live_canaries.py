#!/usr/bin/env python3
"""Run read-only Codex canaries and prove each selected child Skill was read."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def routing_sha256() -> str:
    manifest = json.loads((ROOT / "skills_manifest.json").read_text(encoding="utf-8"))
    skill_fields = (
        "name", "path", "trigger_intent", "negative_intent",
        "required_any_context", "routing_priority", "description",
        "root_exposure", "activation_policy",
    )
    external_fields = (
        "name", "trigger_intent", "negative_intent", "description",
        "url", "ref", "root_exposure", "activation_policy",
    )
    payload = {
        "routing_contract": manifest["routing_contract"],
        "skills": [
            {key: skill[key] for key in skill_fields if key in skill}
            for skill in manifest["skills"]
        ],
        "external_dependencies": [
            {key: item[key] for key in external_fields if key in item}
            for item in manifest["external_dependencies"]
        ],
    }
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(encoded)


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def load_cases(selected_skill: str | None) -> list[dict[str, str]]:
    config = json.loads(
        (ROOT / "evals/capability-live-canaries.json").read_text(encoding="utf-8")
    )
    prompts = {
        item["name"]: item
        for item in json.loads((ROOT / "test-prompts.json").read_text(encoding="utf-8"))
    }
    cases = []
    for item in config["cases"]:
        if selected_skill and item["skill"] != selected_skill:
            continue
        prompt_entry = prompts[item["prompt_name"]]
        cases.append(
            {
                "skill": item["skill"],
                "prompt_name": item["prompt_name"],
                "prompt": prompt_entry["prompt"],
            }
        )
    if selected_skill and not cases:
        raise SystemExit(f"unknown canary skill: {selected_skill}")
    return cases


def parse_events(raw: str) -> list[dict[str, object]]:
    events = []
    for line in raw.splitlines():
        if not line.startswith("{"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def sanitize_text(value: object) -> str:
    text = str(value)
    replacements = (
        (str(ROOT), "<REPO_ROOT>"),
        (str(Path.home()), "<HOME>"),
    )
    for source, target in replacements:
        if source:
            text = text.replace(source, target)
    return text


def write_audit_artifact(
    artifact_dir: Path,
    case: dict[str, str],
    commands: list[dict[str, object]],
    final_message: str,
) -> tuple[str, str]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{case['skill']}.json"
    payload = {
        "schema_version": 1,
        "skill": case["skill"],
        "prompt_name": case["prompt_name"],
        "commands": commands,
        "observed_final": final_message,
        "boundary": (
            "Compact sanitized execution evidence; excludes reasoning and the full raw event stream."
        ),
    }
    artifact_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return str(artifact_path.relative_to(ROOT)), sha256_bytes(artifact_path.read_bytes())


def run_case(
    case: dict[str, str], timeout: int, artifact_dir: Path
) -> dict[str, object]:
    skill = case["skill"]
    child_path = f"skills/{skill}/SKILL.md"
    prompt = (
        "只读能力激活探针。真实用户意图如下：\n"
        f"{case['prompt']}\n\n"
        "按 RTK.md 的最小上下文规则，优先运行 "
        "`python3 scripts/explain_route.py <完整用户意图> --json`；"
        "选择最窄的内置能力并实际读取对应 `skills/<name>/SKILL.md`。"
        "禁止修改文件、运行测试、安装、联网或执行用户任务。"
        "最终只输出一行 `ACTIVATED:<实际读取的内置Skill名>`；"
        "没有实际读取则输出 `ACTIVATION_FAILED:<原因>`。"
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [
            "codex",
            "exec",
            "--ephemeral",
            "--json",
            "-C",
            str(ROOT),
            "--sandbox",
            "read-only",
            prompt,
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    raw = result.stdout + result.stderr
    events = parse_events(raw)
    commands: list[dict[str, object]] = []
    messages = []
    usage: dict[str, object] = {}
    for event in events:
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "command_execution":
            commands.append(
                {
                    "command": sanitize_text(item.get("command", "")),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                    "aggregated_output": sanitize_text(
                        str(item.get("aggregated_output", ""))[:4000]
                    ),
                }
            )
        if isinstance(item, dict) and item.get("type") == "agent_message":
            messages.append(str(item.get("text", "")))
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    final_message = messages[-1].strip() if messages else ""
    child_read = any(child_path in str(item["command"]) for item in commands)
    passed = (
        result.returncode == 0
        and child_read
        and final_message == f"ACTIVATED:{skill}"
    )
    artifact_ref, artifact_sha256 = write_audit_artifact(
        artifact_dir, case, commands, final_message
    )
    return {
        "skill": skill,
        "prompt_name": case["prompt_name"],
        "status": "pass" if passed else "fail",
        "expected_final": f"ACTIVATED:{skill}",
        "observed_final": final_message,
        "target_skill_file_read": child_read,
        "command_count": len(commands),
        "exit_code": result.returncode,
        "usage": usage,
        "raw_event_sha256": sha256_bytes(raw.encode("utf-8")),
        "audit_artifact": artifact_ref,
        "audit_artifact_sha256": artifact_sha256,
        "skills_context_budget_warning": (
            "Skill descriptions were shortened to fit the 2% skills context budget"
            in raw
        ),
        "boundary": "Proves one Codex routing/activation canary, not output quality.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("evals/evidence/artifacts/capability-live-canaries-2026-07-13"),
    )
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    cases = load_cases(args.skill)
    artifact_dir = (
        args.artifact_dir
        if args.artifact_dir.is_absolute()
        else ROOT / args.artifact_dir
    )
    results = []
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] live canary: {case['skill']}", flush=True)
        results.append(run_case(case, args.timeout, artifact_dir))
        print(f"  {results[-1]['status']}: {results[-1]['observed_final']}", flush=True)
    passed = sum(item["status"] == "pass" for item in results)
    receipt = {
        "schema_version": 1,
        "status": "pass" if passed == len(results) else "fail",
        "runtime": "codex-cli",
        "runtime_version": subprocess.run(
            ["codex", "--version"], capture_output=True, text=True, check=False
        ).stdout.strip(),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": git_output("rev-parse", "HEAD"),
        "worktree_state": "dirty" if git_output("status", "--porcelain") else "clean",
        "manifest_sha256": sha256_bytes(
            (ROOT / "skills_manifest.json").read_bytes()
        ),
        "routing_sha256": routing_sha256(),
        "passed": passed,
        "total": len(results),
        "results": results,
        "runtime_boundaries": [
            "Codex may shorten globally installed Skill descriptions to fit its shared 2% discovery budget.",
            "Compact sanitized command/final-message artifacts are retained and hash-bound; full raw event streams and model reasoning are not published.",
        ],
        "claims": {
            "model_activation_verified": passed == len(results),
            "output_quality_verified": False,
            "cross_runtime_verified": False,
            "public_network_verified": False,
        },
    }
    output = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output_path = args.output if args.output.is_absolute() else ROOT / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    print(output)
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
