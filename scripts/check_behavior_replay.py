#!/usr/bin/env python3
"""Check reviewed live-replay observations against behavior contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_PATH = ROOT / "evals" / "behavior-contracts.json"
LEVELS = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_evidence(observations_path: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    return path if path.is_absolute() else (observations_path.parent / path).resolve()


def string_set(value: object) -> set[str] | None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        return None
    return {item.strip() for item in value}


def validate_observations(
    observations_path: Path,
    *,
    require_all: bool = False,
    verify_evidence: bool = True,
) -> list[str]:
    errors: list[str] = []
    contracts_raw = load_json(CONTRACTS_PATH)
    observations_raw = load_json(observations_path)
    if not isinstance(contracts_raw, list) or not isinstance(observations_raw, list):
        return ["contracts and observations must both contain JSON lists"]
    contracts = {
        str(contract.get("id")): contract
        for contract in contracts_raw
        if isinstance(contract, dict) and contract.get("id")
    }
    seen: set[str] = set()

    for index, observation in enumerate(observations_raw, start=1):
        if not isinstance(observation, dict):
            errors.append(f"observation #{index} must be an object")
            continue
        contract_id = str(observation.get("contract_id", "")).strip()
        if contract_id not in contracts:
            errors.append(
                f"observation #{index} has unknown contract_id: {contract_id or '<missing>'}"
            )
            continue
        if contract_id in seen:
            errors.append(f"duplicate observation for contract: {contract_id}")
            continue
        seen.add(contract_id)
        contract = contracts[contract_id]

        observed_routes = string_set(observation.get("observed_routes"))
        observed_actions = string_set(observation.get("observed_actions"))
        observed_side_effects = string_set(observation.get("observed_side_effects"))
        if (
            observed_routes is None
            or observed_actions is None
            or observed_side_effects is None
        ):
            errors.append(
                f"{contract_id}: observed routes/actions/side effects must be string lists"
            )
            continue

        expected_routes = set(contract.get("expected_routes", []))
        forbidden_routes = set(contract.get("forbidden_routes", []))
        required_actions = set(contract.get("required_actions", []))
        forbidden_side_effects = set(contract.get("forbidden_side_effects", []))
        if missing := expected_routes - observed_routes:
            errors.append(
                f"{contract_id}: missing expected routes: {', '.join(sorted(missing))}"
            )
        if forbidden := forbidden_routes & observed_routes:
            errors.append(
                f"{contract_id}: observed forbidden routes: {', '.join(sorted(forbidden))}"
            )
        if missing := required_actions - observed_actions:
            errors.append(
                f"{contract_id}: missing required actions: {', '.join(sorted(missing))}"
            )
        if forbidden := forbidden_side_effects & observed_side_effects:
            errors.append(
                f"{contract_id}: observed forbidden side effects: {', '.join(sorted(forbidden))}"
            )

        observed_level = str(observation.get("evidence_level", ""))
        required_level = str(contract.get("minimum_evidence_level", ""))
        if observed_level not in LEVELS:
            errors.append(
                f"{contract_id}: invalid evidence_level: {observed_level or '<missing>'}"
            )
        elif (
            required_level not in LEVELS
            or LEVELS[observed_level] < LEVELS[required_level]
        ):
            errors.append(
                f"{contract_id}: evidence {observed_level} is below required {required_level}"
            )

        for field in ("reviewer", "observed_at", "evidence_path", "evidence_sha256"):
            if not str(observation.get(field, "")).strip():
                errors.append(f"{contract_id}: missing {field}")
        expected_hash = str(observation.get("evidence_sha256", "")).strip()
        if expected_hash and not SHA256_RE.fullmatch(expected_hash):
            errors.append(f"{contract_id}: evidence_sha256 must be lowercase SHA-256")
        if verify_evidence and observation.get("evidence_path"):
            evidence_path = resolve_evidence(
                observations_path, str(observation["evidence_path"])
            )
            if not evidence_path.is_file():
                errors.append(
                    f"{contract_id}: evidence file not found: {evidence_path}"
                )
            elif expected_hash and file_sha256(evidence_path) != expected_hash:
                errors.append(f"{contract_id}: evidence hash does not match file")

    if require_all:
        missing_contracts = set(contracts) - seen
        if missing_contracts:
            errors.append(
                "missing required observations: " + ", ".join(sorted(missing_contracts))
            )
    if not seen:
        errors.append("no valid behavior observations found")
    return errors


def run_self_test() -> int:
    contracts = load_json(CONTRACTS_PATH)
    contract = contracts[0]
    with tempfile.TemporaryDirectory(prefix="guyue-behavior-replay-") as temp_dir:
        root = Path(temp_dir)
        evidence = root / "replay.md"
        evidence.write_text("# Reviewed live replay\n", encoding="utf-8")
        observation = {
            "contract_id": contract["id"],
            "observed_routes": contract["expected_routes"],
            "observed_actions": contract["required_actions"],
            "observed_side_effects": [],
            "evidence_level": contract["minimum_evidence_level"],
            "reviewer": "independent-test-reviewer",
            "observed_at": "2026-07-10T00:00:00Z",
            "evidence_path": "replay.md",
            "evidence_sha256": file_sha256(evidence),
        }
        observations = root / "observations.json"
        observations.write_text(
            json.dumps([observation], indent=2) + "\n", encoding="utf-8"
        )
        if validate_observations(observations):
            print(
                "behavior replay self-test failed: valid observation was rejected",
                file=sys.stderr,
            )
            return 1

        observation["observed_routes"] = (
            contract["expected_routes"] + contract["forbidden_routes"]
        )
        if not contract["forbidden_routes"]:
            observation["observed_side_effects"] = [
                contract["forbidden_side_effects"][0]
            ]
        observations.write_text(
            json.dumps([observation], indent=2) + "\n", encoding="utf-8"
        )
        errors = validate_observations(observations)
        if not any("forbidden" in error for error in errors):
            print(
                "behavior replay self-test failed: forbidden observation was accepted",
                file=sys.stderr,
            )
            return 1

        observation["observed_routes"] = contract["expected_routes"]
        observation["observed_side_effects"] = []
        observation["evidence_sha256"] = "0" * 64
        observations.write_text(
            json.dumps([observation], indent=2) + "\n", encoding="utf-8"
        )
        if not any("hash" in error for error in validate_observations(observations)):
            print(
                "behavior replay self-test failed: stale evidence hash was accepted",
                file=sys.stderr,
            )
            return 1

    print("Behavior replay checker self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observations", nargs="?", type=Path)
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--skip-evidence-files", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    if not args.observations:
        parser.error("observations JSON is required unless --self-test is used")

    errors = validate_observations(
        args.observations.resolve(),
        require_all=args.require_all,
        verify_evidence=not args.skip_evidence_files,
    )
    if errors:
        print("Behavior replay check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Behavior replay check passed: {args.observations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
