# Guyue v1.5.0 Release Candidate

Date: 2026-07-13
State: `release-candidate`
Base tag: `v1.4.0`
Candidate parent: `2916a4bfda8fb64bb4434b9238ae752d7652075e`

## Why This Candidate Exists

v1.4.0 proved that 26 child Skills could be discovered, activated and reviewed. It did not yet make cross-Skill sequencing a machine-checkable contract, and its repository/runtime data ownership still needed a durable installation and migration model. v1.5.0 closes those two gaps without claiming that a workflow candidate grants permission to act.

## What Changed

- Add nine machine-readable collaboration workflows covering all 26 built-in Skills.
- Distinguish direct Skill selection, bounded collaboration candidates and failed routing.
- Require project-specific collaboration to carry verified context markers.
- Expose stage order, stage mode, completion gate and non-authorization boundary through the CLI and MCP route result.
- Add ten collaboration evaluations, including a generic-permission near miss.
- Separate immutable installed payload, private `GUYUE_HOME` data, rebuildable cache and migration receipts.
- Keep the installed `.cc-switch` source copy immutable while real memory writes remain under `~/.guyue`.
- Define `.guyue_memory` read compatibility through `v1.6.x`; removal cannot occur before `v1.7.0` and still requires evidence and authorization.

## Current Evidence

- Local suite: 15/15 pass.
- Capability routing: 54/54.
- Collaboration evaluation: 10/10, 9 workflows, 26/26 Skill coverage.
- Internal triggers: 345/345; near misses: 208/208; external candidates: 48/48.
- Retained activation and synthetic output evidence: 26/26 each.
- Fresh read-only Codex replay: `skill-release`, stages `craft -> secure -> verify -> publishable`; automatic commit, merge, tag and release rejected.
- Empty-HOME file-Git install, restart identity and Long Goal lifecycle: pass.
- Claude marketplace schema validation: pass.
- Zero-Leakage and Ruff: pass.
- Remote `dev` collaboration baseline: commit `2916a4b`, doubled CI run `29229209401`, pass.

## Boundaries

This candidate does not prove `main` integration, tag existence, GitHub Release publication, public-network installation, current Claude model activation, arbitrary-domain quality or long-term user value. The parent commit identifies the green collaboration baseline; the final release-preparation commit and remote CI run belong in the external release receipt so the tree does not claim its own future identity.

## Tag Preparation

After explicit authorization, and only after `dev` remote CI is green:

```bash
git switch main
git merge --ff-only dev
git push origin main
gh run watch <main-run-id> --exit-status
git tag -a v1.5.0 -m "release: 古月 v1.5.0"
git push origin v1.5.0
```

Before creating the tag, verify the public `main` install in an empty HOME and record the exact main commit, run URL, installed payload SHA-256 and tag object ID. Do not run these commands from this document alone; merge, push, tag and release each remain action-specific authorization boundaries.
