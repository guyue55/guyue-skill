# Guyue v1.8.0 Release Candidate

Date: 2026-07-30
Base tag: `v1.7.2`
State: `candidate`

## Why This Candidate Exists

Guyue already had research, requirements, system design, implementation discipline, independent audit and Long Goal control. The missing product surface was a reliable bridge from a normal compound product goal to that existing chain. Users still had to manually assemble the reference, contract, multi-Agent and verification steps.

This candidate repairs that bridge and adds a reusable contract/checker pair. It does not add a universal autonomous-development Skill.

## What Changed

- Extended the existing `product-delivery` workflow with reference-driven triggers, a research entry stage and a stricter completion gate.
- Added a machine-readable product contract for problem framing, references, scope, states, backend permissions, acceptance, loop budgets, maturity stage and traceability.
- Added `scripts/check_reference_product_contract.py` with a passing neutral example and failing boundary cases.
- Updated `requirement-analysis` to ask only necessary direction-changing questions and freeze shared product invariants before delegation.
- Updated `reality-auditor` to distinguish contract structure, implementation evidence, release-candidate evidence and production readiness.

## Verification Target

Before candidate approval:

- deterministic routing selects `product-delivery` for both the original B2B prompt and a held-out reference-driven vertical-slice prompt;
- the product-contract checker accepts the neutral example and rejects missing backend enforcement, unknown references, unbounded loops and incomplete traceability;
- context budgets and route-collision checks remain within limits;
- live activation and output-quality evidence are refreshed for the candidate semantics;
- the exact payload lock, full install proof, source-archive proof, Zero-Leakage scan and complete local suite pass on a clean committed snapshot.

## Evidence Boundary

The contract checker proves only structural completeness and cross-reference integrity. Model canaries prove bounded activation or one synthetic output, not arbitrary prompts, long-term autonomy, real-user adoption or production reliability. A real product must still supply code, data, permissions, tests, deployment, observability, recovery and user evidence appropriate to its claimed maturity stage.
