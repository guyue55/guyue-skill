#!/usr/bin/env python3
"""Regression tests for explainable Guyue Skill routing."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from src.skill_router import resolve_routes  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    manifest = json.loads((ROOT / "skills_manifest.json").read_text(encoding="utf-8"))
    contracts = json.loads(
        (ROOT / "evals" / "behavior-contracts.json").read_text(encoding="utf-8")
    )

    for contract in contracts:
        result = resolve_routes(manifest, contract["prompt"], limit=8)
        selected = [item["name"] for item in result["selected"]]
        expected = set(contract["expected_routes"])
        forbidden = set(contract["forbidden_routes"])
        require(
            expected.issubset(selected),
            f"{contract['id']} missed expected routes "
            f"{sorted(expected - set(selected))}: {selected}",
        )
        require(
            forbidden.isdisjoint(selected),
            f"{contract['id']} selected a forbidden route: {selected}",
        )

    generic = resolve_routes(
        manifest,
        "给当前项目做一个普通权限管理页面和后端接口。",
        limit=8,
    )
    nexus_rejection = next(
        item
        for item in generic["rejected"]
        if item["name"] == "nexusflow-governance-workflow"
    )
    require(
        nexus_rejection["reason"] == "missing_required_context",
        "project-specific skills must explain missing context markers",
    )

    nexus = resolve_routes(
        manifest,
        "修复租户治理权限。",
        context_markers=["NexusFlow", "permissionSnapshot"],
        limit=5,
    )
    require(
        nexus["selected"][0]["name"] == "nexusflow-governance-workflow",
        "explicit project markers must select the project workflow first",
    )
    require(
        nexus["selected"][0]["matched_context"],
        "selected routes must expose the context evidence used",
    )

    for meta_phrase in ("是否触发", "是否应触发"):
        route_audit = resolve_routes(
            manifest,
            (
                "只读审查这个需求：给当前项目做一个普通权限管理页面和后端接口。"
                f"请判断 NexusFlow/EAC 项目专属能力{meta_phrase}；不要修改文件。"
            ),
            limit=8,
        )
        audit_selected = [item["name"] for item in route_audit["selected"]]
        require(
            audit_selected[0] == "reality-auditor",
            f"read-only audit must take routing priority: {audit_selected}",
        )
        require(
            {
                "nexusflow-governance-workflow",
                "eac-demo-hardening",
            }.isdisjoint(audit_selected),
            f"route-audit meta text must not activate project skills: {audit_selected}",
        )

    negative = resolve_routes(
        manifest,
        "implementation already approved and bounded; write code now",
        limit=5,
    )
    require(
        "product-sense" not in [item["name"] for item in negative["selected"]],
        "explicit negative intent must prevent route selection",
    )

    print(f"Skill router tests passed: {len(contracts)} behavior contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
