# Guyue v1.5.0 Release

Date: 2026-07-13
State: `released`
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
- Release candidate `1abeb2a`: doubled `dev` CI run `29230196872` and doubled `main` CI run `29230447741`, pass.
- Public HTTPS clone of `main@1abeb2a` in an empty HOME: complete 247-file payload, first-run proof and strict 15-stage suite pass with candidate payload SHA-256 `4090c1de483f3466269f8f58f265f3757c61e1fdc74c195e532e95dca385a5a6`.

## Boundaries

This release proves the local and remote gates listed above, including public-source installation. It does not prove GitHub Release publication, current Claude model activation, arbitrary-domain quality or long-term user value. The final release commit, annotated tag object and remote tag ref belong in the external release receipt so the tree does not claim its own future identity.

## Tag Operation

After explicit authorization, and only after the final release commit passes `main` CI and public-source replay:

```bash
git tag -a v1.5.0 -m "release: 古月 v1.5.0"
git push origin v1.5.0
```

Record the exact main commit, run URL, installed payload SHA-256 and tag object ID outside the tagged tree. Do not run these commands from this document alone; tag and GitHub Release remain separate action-specific authorization boundaries.
