# Guyue v1.5.1 Release Candidate

Date: 2026-07-13
State: `release-candidate`
Base tag: `v1.5.0`

## Purpose

v1.5.1 is a narrow release-engineering hotfix. It does not change Guyue's capability inventory, routing thresholds, collaboration contracts, memory schema or Long Goal protocol.

## Reproduced Failure

1. Download GitHub's generated `v1.5.0` tag archive into an empty directory.
2. Run `GUYUE_RELEASE_STRICT=1 bash scripts/test_suite.sh` under an empty HOME.
3. Ruff creates `.ruff_cache` during stage 2.
4. `scripts/test_try_guyue.py` fails during stage 4 because the exact payload verifier reports four undeclared cache files.

This sequence matters: `python3 scripts/try_guyue.py` passes before Ruff runs, and fails afterward. The payload verifier is behaving correctly.

## Fix

- Run Ruff with `--no-cache` inside the release gate.
- Reject `.ruff_cache` in Zero-Leakage alongside `__pycache__`, `.pyc` and `.DS_Store`.
- Add a focused regression for both the command contract and scanner behavior.
- Keep repository instructions and the release checklist aligned with the executable gate.

## Required Evidence

- Failure-first focused regression: pass.
- Exact manifest-backed payload lock: pass for the frozen candidate tree.
- Strict local 15-stage suite: pass without generated cache residue.
- Fresh staged no-Git source archive, empty HOME, first-run proof and strict 15-stage suite: pass.
- Doubled `dev` and `main` CI for the exact promoted commit.
- Public tag archive replay after an authorized tag is created.

## Boundaries

The candidate does not authorize `main`, tag creation or GitHub Release publication. Passing the archive gate proves verification idempotence and payload integrity for this workflow; it does not prove other runtime activation, arbitrary-domain quality or long-term user value.
