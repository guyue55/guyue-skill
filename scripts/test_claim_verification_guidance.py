#!/usr/bin/env python3
"""Guard the second-pass review contract against silent erosion.

This is a change detector over rule text, not a behavior test.

Three layers:
1. Required clauses: specific obligations must still be stated, so deletion is
   named precisely rather than surfacing as an opaque hash mismatch.
2. Forbidden clauses: known weakenings are rejected by pattern (softened floors,
   permission instead of duty, "keep the rule and add an exception", lineage
   treated as independent confirmation, a single pass allowed to seal).
3. Region digest: each protected region is hashed after removing all whitespace.
   Any added, removed, reordered, reworded or merged sentence changes the digest
   and fails, until someone runs `--update` and reviews the diff. That explicit
   step is the approval mechanism. A set-of-sentences comparison would miss
   reordering and short inserted exceptions, so the digest is the real gate and
   the sentence list exists only to make a failure readable.

Re-wrapping is invisible to the gate because whitespace is removed first.
Passing proves the protected text is unchanged, ignoring whitespace. It proves
nothing about model behavior; a semantically equivalent rewrite is not
detectable here and still needs human or independent-agent review.

Run `python3 scripts/test_claim_verification_guidance.py --update` only after
reviewing an intentional rule change.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "evals" / "second-pass-guidance-snapshot.json"

REGIONS = (
    ("SKILL.md 核心法则", "SKILL.md", r"^## 核心法则", (r"^## 路由执行流",)),
    (
        "GUYUE_PRINCIPLES.md 证据校准",
        "GUYUE_PRINCIPLES.md",
        r"^### 证据校准与可逆自治",
        (r"^### 独立判断契约",),
    ),
)

REQUIRED = (
    ("coverage duty", r"每个实质问句"),
    ("risk-proportionate review", r"与风险相称的复核"),
    ("sub-item decomposition", r"拆成可核对的实质子项"),
    ("proportionate light path", r"低风险.*自检"),
    ("method freedom", r"不预设固定清单"),
    ("free method choice", r"自由选择"),
    ("no mechanical ritual", r"不要为了形式机械套步骤"),
    ("escalation basis", r"结论能否被推翻"),
    ("escalation duty", r"第二遍必须增加判别依据"),
    ("external evidence floor", r"必须来自模型之外"),
    ("model-external definition", r"原始来源、真实运行产物、接口响应、第三方可核验记录或人工验收"),
    ("third-party record must be locatable", r"第三方记录必须带可定位来源和观察时间"),
    ("generated output is not external", r"任何模型生成的输出、缓存响应和用户粘贴的文本都不算模型之外"),
    ("self-review is not external", r"子 Agent、自审和换种算法的复算"),
    ("calculation is still external fact", r"外部数据上的计算仍属外部事实"),
    ("user input is not external fact", r"用户自己提供的输入不算外部事实"),
    ("stable-knowledge standard", r"合格标准是逐项覆盖、口径不漂移"),
    ("no extra evidence for stable knowledge", r"不额外要求外部证据"),
    ("stable-knowledge test", r"不得归入稳定知识"),
    ("user premise is inference", r"用户给定的任务前提不算已验证证据"),
    ("confirmation requires coverage check", r"一次直接证据加逐项覆盖核对即可写"),
    ("confirmation requires direct evidence", r"有当前有效证据直接支持"),
    ("inference includes unfinished review", r"复核不足以升级"),
    ("anti-restatement", r"原样重念"),
    ("anti-wording-only", r"换措辞、换视角(而|但)没有新增判别依据"),
    ("source lineage", r"只算一个来源家族|同一来源家族"),
    ("lineage cannot self-confirm", r"不能互相升级为"),
    ("lineage required for confirmation", r"且来源关系成立"),
    ("five-state freeze", r"五类事实状态不变|沿用五类"),
    ("high-risk factual floor", r"对外承诺的事实性结论"),
    ("decision pause path", r"暂停并取得授权"),
    ("style maps to decision", r"纯风格与偏好选择"),
)

FORBIDDEN = (
    ("softened evidence floor", r"(最好|原则上|尽量|可选)[^。；]{0,10}来自模型之外"),
    ("permission instead of duty", r"(可以|可)来自模型之外"),
    ("exception clause re-opens confirmation", r"(但|不过|然而)[^。；]{0,50}(升级|认定|视为|算作)[^。；]{0,10}已确认"),
    ("user premise shortcut", r"用户[^。；]{0,15}(足够|即可|就|可以)[^。；]{0,10}(写成|写|算)"),
    ("restatement treated as confirmation", r"一次直接证据即可写"),
    ("same-family treated as independent", r"同源[^。；]{0,30}(视为|算作|当作)[^。；]{0,12}独立"),
    ("internal coherence treated as external", r"内部[^。；]{0,40}(自洽|排除竞争)[^。；]{0,30}(可|即可|应)[^。；]{0,10}升级"),
    ("explicit skip permission", r"(可跳过|可免|允许跳过|不必取证)(复核|验证|取证)?"),
    ("external evidence not required", r"(不强制|无需|可以不做)[^。；]{0,6}外部取数"),
    ("single pass allowed to seal", r"只做一次[^。；]{0,12}(复核|验证)[^。；]{0,10}(封板|完成)"),
)

CONTRACTS = (
    (
        "material-conclusion-gets-second-pass-without-fixed-checklist",
        "Second-Pass Review Challenges Conflicting Research",
        ("five fact states", "adds testable evidence", "trace source lineage",
         "same-model repeats without new input"),
        "repeat the same reasoning",
    ),
    (
        "simple-dialogue-second-pass-stays-proportionate",
        "Second-Pass Review Stays Proportionate In Simple Dialogue",
        ("both requested concepts", "proportionate semantic", "lightweight"),
        "launch a sub-agent",
    ),
    (
        "development-second-pass-uses-fresh-task-evidence",
        "Second-Pass Review In Development Uses Fresh Evidence",
        ("fresh task-relevant evidence", "residual unverified"),
        "unrelated green gate",
    ),
    (
        "high-impact-second-pass-escalates-and-downgrades-on-conflict",
        "Second-Pass Review Escalates High-Risk Conflict",
        ("source family", "downgrade", "stop condition"),
        "repeat the same check without new evidence",
    ),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def compact(value: str) -> str:
    """Drop whitespace so re-wrapping never counts as a rule change."""
    return re.sub(r"\s+", "", value)


def region(text: str, start_pattern: str, stop_patterns: tuple[str, ...]) -> str:
    lines = text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if re.match(start_pattern, line)),
        None,
    )
    require(start is not None, f"rule region not found: {start_pattern}")
    body = [lines[start]]
    for line in lines[start + 1 :]:
        if any(re.match(pattern, line) for pattern in stop_patterns):
            break
        body.append(line)
    return "\n".join(body)


def sentences(body: str) -> list[str]:
    parts = re.split(r"[。；]", compact(body))
    cleaned = []
    for part in parts:
        stripped = re.sub(r"^[*>\-]+", "", part).strip("，,、")
        if len(stripped) >= 6:
            cleaned.append(stripped)
    return cleaned


def digest(body: str) -> str:
    return hashlib.sha256(compact(body).encode("utf-8")).hexdigest()


def read_regions() -> dict[str, dict[str, object]]:
    collected = {}
    for name, filename, start, stop in REGIONS:
        body = region((ROOT / filename).read_text(encoding="utf-8"), start, stop)
        collected[name] = {"sha256": digest(body), "sentences": sentences(body)}
    return collected


def update_snapshot(collected: dict[str, dict[str, object]]) -> int:
    payload = {
        "schema_version": 2,
        "note": "Approved baseline for the Guyue core doctrine regions (including the "
        "second-pass review gate). The digest is the gate; the sentence list exists so a "
        "failure can be read. Regenerate with --update only after an intentional, "
        "reviewed rule change.",
        "regions": collected,
    }
    SNAPSHOT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    total = sum(len(value["sentences"]) for value in collected.values())
    print(f"Snapshot updated: {SNAPSHOT.name} ({len(collected)} regions, {total} sentences)")
    return 0


def explain_drift(name: str, current: dict[str, object], known: dict[str, object]) -> str:
    current_sentences = Counter(current["sentences"])
    known_sentences = Counter(known.get("sentences", []))
    added = list((current_sentences - known_sentences).elements())[:3]
    removed = list((known_sentences - current_sentences).elements())[:3]
    return (
        f"{name} (core doctrine baseline) changed; review the diff, then run --update. "
        f"added≈{added} removed≈{removed}"
    )


def main() -> int:
    collected = read_regions()
    if "--update" in sys.argv:
        return update_snapshot(collected)

    approved = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["regions"]
    for name in collected:
        require(name in approved, f"snapshot missing region: {name}")
        require(
            collected[name]["sha256"] == approved[name].get("sha256"),
            explain_drift(name, collected[name], approved[name]),
        )

    combined = compact(
        "\n".join(
            region((ROOT / filename).read_text(encoding="utf-8"), start, stop)
            for _, filename, start, stop in REGIONS
        )
    )
    for label, pattern in REQUIRED:
        require(
            re.search(compact(pattern), combined) is not None,
            f"clause missing or weakened: {label} ({pattern})",
        )
    for label, pattern in FORBIDDEN:
        require(
            re.search(compact(pattern), combined) is None,
            f"forbidden clause reintroduced: {label} ({pattern})",
        )

    contracts = json.loads(
        (ROOT / "evals" / "behavior-contracts.json").read_text(encoding="utf-8")
    )
    prompts = json.loads((ROOT / "test-prompts.json").read_text(encoding="utf-8"))
    prompt_by_name = {prompt.get("name"): prompt.get("prompt") for prompt in prompts}
    by_id = {contract.get("id"): contract for contract in contracts}
    for contract_id, prompt_name, actions_required, forbidden_required in CONTRACTS:
        contract = by_id.get(contract_id)
        require(contract is not None, f"missing behavior contract: {contract_id}")
        require(prompt_name in prompt_by_name, f"missing prompt: {prompt_name}")
        require(
            contract.get("prompt") == prompt_by_name[prompt_name],
            f"{contract_id} prompt drifted from {prompt_name}",
        )
        actions = "\n".join(contract.get("required_actions", []))
        forbidden = "\n".join(contract.get("forbidden_side_effects", []))
        require(actions.strip(), f"{contract_id} has no required actions")
        require(forbidden.strip(), f"{contract_id} has no forbidden side effects")
        for phrase in actions_required:
            require(phrase in actions, f"{contract_id} lost required action: {phrase}")
        require(
            forbidden_required in forbidden,
            f"{contract_id} lost forbidden side effect: {forbidden_required}",
        )

    print("Claim verification guidance structure checks passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Claim verification guidance check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error