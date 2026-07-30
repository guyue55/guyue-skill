#!/usr/bin/env python3
"""Validate a reference-driven product contract without claiming maturity."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_STAGES = {
    "prototype",
    "vertical_slice",
    "mvp",
    "release_candidate",
    "production_ready",
}
ALLOWED_EVIDENCE_LEVELS = {"L1", "L2", "L3", "L4"}


def is_non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_object(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def require_list(
    value: Any,
    path: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{path} must be a list")
        return []
    if not allow_empty and not value:
        errors.append(f"{path} must not be empty")
    return value


def require_text(value: Any, path: str, errors: list[str]) -> None:
    if not is_non_empty(value):
        errors.append(f"{path} must be a non-empty string")


def unique_ids(items: list[Any], path: str, errors: list[str]) -> set[str]:
    result: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{path}[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not is_non_empty(item_id):
            errors.append(f"{path}[{index}].id must be a non-empty string")
            continue
        if item_id in result:
            errors.append(f"{path}[{index}].id duplicates {item_id}")
        result.add(item_id)
    return result


def validate_contract(contract: Any) -> list[str]:
    errors: list[str] = []
    root = require_object(contract, "$", errors)
    if root.get("schema_version") != 1:
        errors.append("$.schema_version must equal 1")

    metadata = require_object(root.get("metadata"), "$.metadata", errors)
    for field in ("id", "title", "status", "owner", "decision_owner"):
        require_text(metadata.get(field), f"$.metadata.{field}", errors)
    if metadata.get("status") not in {"draft", "approved"}:
        errors.append("$.metadata.status must be draft or approved")

    problem = require_object(root.get("problem"), "$.problem", errors)
    for field in (
        "core_scenario",
        "current_workaround",
        "desired_outcome",
        "no_change_consequence",
    ):
        require_text(problem.get(field), f"$.problem.{field}", errors)
    users = require_list(problem.get("users"), "$.problem.users", errors)
    for index, user in enumerate(users):
        require_text(user, f"$.problem.users[{index}]", errors)
    metrics = require_list(
        problem.get("success_metrics"),
        "$.problem.success_metrics",
        errors,
    )
    unique_ids(metrics, "$.problem.success_metrics", errors)
    for index, metric in enumerate(metrics):
        if not isinstance(metric, dict):
            continue
        for field in ("metric", "target", "evidence"):
            require_text(
                metric.get(field),
                f"$.problem.success_metrics[{index}].{field}",
                errors,
            )

    references = require_list(root.get("references"), "$.references", errors)
    reference_ids = unique_ids(references, "$.references", errors)
    for index, reference in enumerate(references):
        if not isinstance(reference, dict):
            continue
        for field in (
            "source",
            "accessed_at",
            "mechanism",
            "adopted_as",
            "rights_boundary",
        ):
            require_text(
                reference.get(field),
                f"$.references[{index}].{field}",
                errors,
            )

    scope = require_object(root.get("scope"), "$.scope", errors)
    for field in ("must", "non_goals"):
        values = require_list(scope.get(field), f"$.scope.{field}", errors)
        for index, value in enumerate(values):
            require_text(value, f"$.scope.{field}[{index}]", errors)
    suggestions = require_list(
        scope.get("should"),
        "$.scope.should",
        errors,
        allow_empty=True,
    )
    for index, value in enumerate(suggestions):
        require_text(value, f"$.scope.should[{index}]", errors)

    domain = require_object(root.get("domain"), "$.domain", errors)
    for field in ("actors", "objects", "states"):
        values = require_list(domain.get(field), f"$.domain.{field}", errors)
        for index, value in enumerate(values):
            require_text(value, f"$.domain.{field}[{index}]", errors)
    states = {state for state in domain.get("states", []) if is_non_empty(state)}
    transitions = require_list(
        domain.get("transitions"),
        "$.domain.transitions",
        errors,
    )
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            errors.append(f"$.domain.transitions[{index}] must be an object")
            continue
        for field in ("from", "to", "actor", "guard", "audit_event"):
            require_text(
                transition.get(field),
                f"$.domain.transitions[{index}].{field}",
                errors,
            )
        for field in ("from", "to"):
            state = transition.get(field)
            if is_non_empty(state) and state not in states:
                errors.append(
                    f"$.domain.transitions[{index}].{field} "
                    f"references unknown state {state}"
                )

    permissions = require_list(root.get("permissions"), "$.permissions", errors)
    for index, permission in enumerate(permissions):
        if not isinstance(permission, dict):
            errors.append(f"$.permissions[{index}] must be an object")
            continue
        for field in (
            "actor",
            "action",
            "resource",
            "scope",
            "backend_enforcement",
            "ui_representation",
            "negative_test",
        ):
            require_text(
                permission.get(field),
                f"$.permissions[{index}].{field}",
                errors,
            )

    acceptance = require_list(root.get("acceptance"), "$.acceptance", errors)
    acceptance_ids = unique_ids(acceptance, "$.acceptance", errors)
    for index, item in enumerate(acceptance):
        if not isinstance(item, dict):
            continue
        for field in ("promise", "checker", "owner", "failure_condition"):
            require_text(item.get(field), f"$.acceptance[{index}].{field}", errors)
        if item.get("evidence_level") not in ALLOWED_EVIDENCE_LEVELS:
            errors.append(
                f"$.acceptance[{index}].evidence_level must be one of "
                f"{sorted(ALLOWED_EVIDENCE_LEVELS)}"
            )
        source_refs = require_list(
            item.get("source_refs"),
            f"$.acceptance[{index}].source_refs",
            errors,
        )
        for source_index, source_ref in enumerate(source_refs):
            if not is_non_empty(source_ref):
                errors.append(
                    f"$.acceptance[{index}].source_refs[{source_index}] "
                    "must be a non-empty string"
                )
            elif source_ref not in reference_ids:
                errors.append(
                    f"$.acceptance[{index}].source_refs[{source_index}] "
                    f"references unknown source {source_ref}"
                )

    loops = require_object(root.get("loop"), "$.loop", errors)
    for field in ("max_rounds", "max_minutes", "max_subtasks"):
        value = loops.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            errors.append(f"$.loop.{field} must be a positive integer")
    if loops.get("checker_independent") is not True:
        errors.append("$.loop.checker_independent must be true")
    for field in ("stop_conditions", "escalation_conditions"):
        values = require_list(loops.get(field), f"$.loop.{field}", errors)
        for index, value in enumerate(values):
            require_text(value, f"$.loop.{field}[{index}]", errors)
    require_text(loops.get("rollback"), "$.loop.rollback", errors)

    delivery = require_object(root.get("delivery"), "$.delivery", errors)
    if not isinstance(delivery.get("implementation_authorized"), bool):
        errors.append("$.delivery.implementation_authorized must be a boolean")
    if delivery.get("target_stage") not in ALLOWED_STAGES:
        errors.append(
            f"$.delivery.target_stage must be one of {sorted(ALLOWED_STAGES)}"
        )
    require_text(
        delivery.get("completion_definition"),
        "$.delivery.completion_definition",
        errors,
    )
    known_limits = require_list(
        delivery.get("known_limits"),
        "$.delivery.known_limits",
        errors,
    )
    for index, value in enumerate(known_limits):
        require_text(value, f"$.delivery.known_limits[{index}]", errors)

    traceability = require_object(
        root.get("traceability"),
        "$.traceability",
        errors,
    )
    mappings = require_list(
        traceability.get("reference_to_acceptance"),
        "$.traceability.reference_to_acceptance",
        errors,
    )
    mapped_acceptance: set[str] = set()
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict):
            errors.append(
                f"$.traceability.reference_to_acceptance[{index}] must be an object"
            )
            continue
        reference_id = mapping.get("reference_id")
        acceptance_id = mapping.get("acceptance_id")
        if reference_id not in reference_ids:
            errors.append(
                f"$.traceability.reference_to_acceptance[{index}].reference_id "
                f"references unknown source {reference_id}"
            )
        if acceptance_id not in acceptance_ids:
            errors.append(
                f"$.traceability.reference_to_acceptance[{index}].acceptance_id "
                f"references unknown acceptance {acceptance_id}"
            )
        if acceptance_id in acceptance_ids:
            mapped_acceptance.add(acceptance_id)
        require_text(
            mapping.get("adaptation"),
            f"$.traceability.reference_to_acceptance[{index}].adaptation",
            errors,
        )
    missing_mappings = acceptance_ids - mapped_acceptance
    if missing_mappings:
        errors.append(
            "$.traceability.reference_to_acceptance must cover every acceptance id: "
            + ", ".join(sorted(missing_mappings))
        )

    return errors


def load_contract(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def self_test() -> int:
    example_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "requirement-analysis"
        / "references"
        / "reference-driven-product-contract.example.json"
    )
    example = load_contract(example_path)
    errors = validate_contract(example)
    if errors:
        raise AssertionError(f"example contract must pass: {errors}")

    invalid = copy.deepcopy(example)
    invalid["permissions"][0]["backend_enforcement"] = ""
    invalid["acceptance"][0]["source_refs"] = ["REF-UNKNOWN"]
    invalid["loop"]["max_rounds"] = 0
    invalid["traceability"]["reference_to_acceptance"] = []
    invalid_errors = validate_contract(invalid)
    required_fragments = (
        "backend_enforcement",
        "unknown source",
        "max_rounds",
        "cover every acceptance id",
    )
    for fragment in required_fragments:
        if not any(fragment in error for error in invalid_errors):
            raise AssertionError(f"self-test did not detect {fragment}")

    print("Reference-driven product contract checker self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", nargs="?", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if args.contract is None:
        parser.error("contract path is required unless --self-test is used")

    try:
        errors = validate_contract(load_contract(args.contract))
    except (OSError, json.JSONDecodeError) as exc:
        errors = [f"unable to read contract: {exc}"]

    result = {
        "schema_version": 1,
        "status": "pass" if not errors else "fail",
        "contract": str(args.contract),
        "claim_boundary": (
            "Structural contract validation only; product maturity and runtime "
            "behavior remain unverified."
        ),
        "errors": errors,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print("Reference-driven product contract is structurally valid.")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
