#!/usr/bin/env python3
"""Run one realistic output task and an independent review for every Guyue Skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT_DIR = Path(
    "evals/evidence/artifacts/capability-output-quality-2026-07-13"
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sanitize(value: object) -> str:
    text = str(value)
    for source, target in (
        (str(ROOT), "<REPO_ROOT>"),
        (str(Path.home()), "<HOME>"),
    ):
        if source:
            text = text.replace(source, target)
    return text


def parse_events(raw: str) -> tuple[list[dict[str, object]], list[str], dict[str, object]]:
    commands: list[dict[str, object]] = []
    messages: list[str] = []
    usage: dict[str, object] = {}
    for line in raw.splitlines():
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item")
        if isinstance(item, dict) and item.get("type") == "command_execution":
            commands.append(
                {
                    "command": sanitize(item.get("command", "")),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                }
            )
        if isinstance(item, dict) and item.get("type") == "agent_message":
            messages.append(str(item.get("text", "")))
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return commands, messages, usage


def run_codex(prompt: str, timeout: int) -> dict[str, object]:
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
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    raw = result.stdout + result.stderr
    commands, messages, usage = parse_events(raw)
    return {
        "exit_code": result.returncode,
        "commands": commands,
        "messages": messages,
        "usage": usage,
        "raw_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


def parse_review(message: str) -> dict[str, object] | None:
    candidates = [message.strip()]
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", message, re.DOTALL)
    if fenced:
        candidates.insert(0, fenced.group(1))
    first = message.find("{")
    last = message.rfind("}")
    if first >= 0 and last > first:
        candidates.append(message[first : last + 1])
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def artifact_ref(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def run_case(case: dict[str, object], artifact_dir: Path, timeout: int) -> dict[str, object]:
    skill = str(case["skill"])
    skill_path = f"skills/{skill}/SKILL.md"
    output_path = artifact_dir / f"{skill}.output.md"
    producer_path = artifact_dir / f"{skill}.producer.json"
    review_path = artifact_dir / f"{skill}.review.json"
    producer_prompt = (
        f"你正在接受 Guyue 子能力输出质量验收。必须先读取 `{skill_path}`，"
        "然后仅依据该 Skill、仓库内可用事实和下面的自包含任务作答。"
        "全程只读；不修改文件、不联网、不安装、不提交。若完成任务缺少必要输入，"
        "正确输出应明确阻断、缺口和最小下一步，禁止编造。不要解释验收流程，直接交付用户产物。\n\n"
        f"用户任务：{case['prompt']}"
    )
    producer = run_codex(producer_prompt, timeout)
    messages = producer.pop("messages")
    output = sanitize(messages[-1].strip()) if messages else ""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output + "\n", encoding="utf-8")
    producer_artifact = {
        "schema_version": 1,
        "skill": skill,
        "skill_file_read": any(
            skill_path in str(item.get("command", ""))
            for item in producer["commands"]
            if isinstance(item, dict)
        ),
        "output_artifact": artifact_ref(output_path),
        "output_sha256": file_sha256(output_path),
        **producer,
        "boundary": "Sanitized command evidence; full raw stream and reasoning are not retained.",
    }
    write_json(producer_path, producer_artifact)

    criteria = [str(item) for item in case.get("criteria", [])]
    reviewer_prompt = (
        "你是独立只读验收者，不采信作者自述。先读取 "
        f"`{skill_path}` 和 `{artifact_ref(output_path)}`，逐项核验以下标准：\n"
        + "\n".join(f"{index}. {criterion}" for index, criterion in enumerate(criteria, 1))
        + "\n同时检查输出是否实质回答任务、是否编造事实、是否越过授权或证据边界。"
        "最终只能输出一个 JSON 对象，格式："
        '{"status":"pass|fail","criteria":[{"criterion":"...","status":"pass|fail","evidence":"..."}],'
        '"findings":["..."],"boundary":"..."}。'
        "只有全部标准通过且无重大真实性问题时总状态才是 pass。"
    )
    reviewer = run_codex(reviewer_prompt, timeout)
    review_messages = reviewer.pop("messages")
    review_message = sanitize(review_messages[-1].strip()) if review_messages else ""
    parsed_review = parse_review(review_message)
    review_artifact = {
        "schema_version": 1,
        "skill": skill,
        "parsed_review": parsed_review,
        "raw_final": review_message,
        **reviewer,
        "boundary": "Independent Codex session; synthetic task, not a real-user outcome.",
    }
    write_json(review_path, review_artifact)
    criteria_results = (
        parsed_review.get("criteria", []) if isinstance(parsed_review, dict) else []
    )
    passed = (
        producer_artifact["exit_code"] == 0
        and producer_artifact["skill_file_read"] is True
        and len(output) >= 120
        and reviewer["exit_code"] == 0
        and isinstance(parsed_review, dict)
        and parsed_review.get("status") == "pass"
        and len(criteria_results) >= len(criteria)
        and all(
            isinstance(item, dict) and item.get("status") == "pass"
            for item in criteria_results
        )
    )
    return {
        "skill": skill,
        "status": "pass" if passed else "fail",
        "criteria_count": len(criteria),
        "producer_artifact": artifact_ref(producer_path),
        "producer_artifact_sha256": file_sha256(producer_path),
        "output_artifact": artifact_ref(output_path),
        "output_sha256": file_sha256(output_path),
        "review_artifact": artifact_ref(review_path),
        "review_artifact_sha256": file_sha256(review_path),
        "producer_usage": producer_artifact["usage"],
        "reviewer_usage": review_artifact["usage"],
        "findings": parsed_review.get("findings", []) if isinstance(parsed_review, dict) else ["review JSON was not parseable"],
        "boundary": "One synthetic read-only task and one independent review for this Skill.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", action="append", dest="skills")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--merge-existing", action="store_true")
    args = parser.parse_args()
    config = json.loads(
        (ROOT / "evals/capability-output-quality.json").read_text(encoding="utf-8")
    )
    cases = [
        case
        for case in config["cases"]
        if not args.skills or case["skill"] in args.skills
    ]
    if not cases:
        raise SystemExit(f"unknown output-quality skills: {args.skills}")
    artifact_dir = args.artifact_dir if args.artifact_dir.is_absolute() else ROOT / args.artifact_dir
    if args.workers <= 0:
        raise SystemExit("workers must be positive")
    results_by_skill: dict[str, dict[str, object]] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(run_case, case, artifact_dir, args.timeout): str(case["skill"])
            for case in cases
        }
        for completed, future in enumerate(as_completed(futures), 1):
            skill = futures[future]
            result = future.result()
            results_by_skill[skill] = result
            print(
                f"[{completed}/{len(cases)}] {skill}: "
                f"{result['status']} {result['findings']}",
                flush=True,
            )
    results = [results_by_skill[str(case["skill"])] for case in cases]
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    if args.merge_existing and output_path.is_file():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        merged = {
            str(result["skill"]): result
            for result in existing.get("results", [])
            if isinstance(result, dict)
        }
        merged.update(results_by_skill)
        configured_order = [str(case["skill"]) for case in config["cases"]]
        results = [merged[skill] for skill in configured_order if skill in merged]
    passed = sum(result["status"] == "pass" for result in results)
    receipt = {
        "schema_version": 1,
        "status": "pass" if passed == len(results) else "fail",
        "runtime": "codex-cli",
        "runtime_version": subprocess.run(
            ["codex", "--version"], capture_output=True, text=True, check=False
        ).stdout.strip(),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "total": len(results),
        "results": results,
        "claims": {
            "all_skill_synthetic_output_quality_verified": passed == len(results),
            "real_user_value_verified": False,
            "cross_runtime_verified": False,
            "public_network_verified": False,
        },
        "boundary": (
            "Covers one realistic synthetic task per Skill with an independent review; "
            "does not prove every domain input or real-user value."
        ),
    }
    write_json(output_path, receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
