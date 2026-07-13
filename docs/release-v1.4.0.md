# Guyue v1.4.0 Release

Date: 2026-07-13
Scope: capability discovery, activation, evidence inheritance, Long Goal v4, and failure-first output validation

## Why This Release Exists

Guyue already had 26 useful child Skills, but a file existing in the repository was too easily confused with a capability that users could discover, activate, execute, and trust. v1.4.0 unifies those stages into one machine-checked capability chain and makes evidence rules inherit by Skill risk.

## What Changed

- All 54 broad natural-language prompts now run through the real deterministic router.
- All 26 built-in Skills have explicit discovery exposure, activation policy, and E1-E4 evidence profiles.
- Twelve external enhancements remain source-pinned candidates until source, installation, security, and action authorization gates pass.
- Every Skill has eight adjacent near-miss negatives; project-only NexusFlow and EAC routes still require real context.
- All 26 Codex activations retain compact sanitized command and final-message artifacts with SHA-256.
- All 26 Skills run one realistic synthetic output task followed by an independent read-only review.
- Long Goal v4 adds authority revisions, failure preservation, approved recovery, promise/evidence links, and A/B/C Git sealing.

## Failure-First Evidence

The all-Skill output gate did not start green:

| Attempt | Result | What changed |
|---|---:|---|
| 1 | 18/26 | Found missing provisional acceptance criteria, fact expansion, unverified ecosystem claims, media lineage gaps, context-source drift, audio-decision drift, and overclaimed authorization absence; one reviewer session also failed. |
| 2 | 24/26 | Exposed missing compression stop conditions and an incomplete four-state deployment matrix. |
| 3 | 26/26 | All outputs and independent criteria passed; non-blocking findings remain in the receipts. |

The fixes were made in the owning Skills, not hidden in the evaluator.

## Reproducible Gates

```bash
python3 scripts/check_capability_chain.py --json
bash scripts/test_suite.sh
ruff check scripts src
git diff --check
python3 scripts/security_scanner.py .
```

Primary receipts:

- `evals/evidence/capability-live-canaries-2026-07-13.json`
- `evals/evidence/capability-output-quality-2026-07-13.json`
- `evals/evidence/capability-evidence-profile-replay-2026-07-13.json`
- `docs/guyue-capability-discovery-evidence-audit-plan-2026-07-12.md`

Final local candidate:

- physical files: 236
- strict index-mode birth-certificate release files: 236
- immutable identity: the final commit SHA and annotated `v1.4.0` tag; release-time hashes belong in the external release receipt so they do not change the tree they identify

## Boundaries

v1.4.0 proves deterministic routing, retained Codex activation evidence, one independently reviewed synthetic output per Skill, and local exact-candidate installation/restart behavior. By explicit scope decision it does not claim Claude or other runtime activation, public-network installation, controlled superiority over other products, arbitrary-input quality, or real-user value.
