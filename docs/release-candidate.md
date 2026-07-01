# Release Candidate Evidence

Date: 2026-07-01
Status: not release-ready
Scope: productization evidence only. This document does not add skills, runtime adapters, install hooks, publishing automation, or behavior changes.

## Baseline

Current candidate baseline:

- commit: `0ce9b29 docs(runtime): 规划跨工具适配策略`
- branch state at intake: `main` ahead of `origin/main` by 5 commits
- unstaged files observed at intake:
  - `GUYUE_PRINCIPLES.md`
  - `skills/ecosystem-scout/SKILL.md`
  - `skills_manifest.json`

Those unstaged files are treated as user work outside this release-candidate slice. They must be reviewed, committed separately, or reverted by explicit user instruction before a public release tag or marketplace submission.

## Positioning

Guyue is a Personal Agent Operating Layer, not a complete autonomous person. The release candidate should prove that a new user can understand, install, trigger, verify, and safely stop the skill suite.

The release candidate should not prove that Guyue has more abilities. It should prove that the existing abilities are bounded and reproducible.

## Evidence Gate

A release candidate is eligible only when every item below is true:

- `git status --short` contains no unreviewed local changes.
- `bash scripts/test_suite.sh` exits with status code `0`.
- `git diff --check` exits with status code `0`.
- `python3 scripts/security_scanner.py` reports no secrets, private paths, cache files, or generated bloat.
- `examples/quickstart-output.md` contains at least one read-only live replay for the active runtime entrypoint.
- Runtime adapter work follows `docs/runtime-adapters.md`; no `CLAUDE.md`, `GEMINI.md`, Copilot, or Cursor adapter is added without a target-runtime live replay.
- `examples/showcase.md` or the README links to visible evidence of what Guyue produces.
- Known deviations are listed with a next action, not hidden in the release notes.

## Current Evidence

| Area | Current evidence | Result | Release impact |
|---|---|---|---|
| Positioning | README states Guyue is a Personal Agent Operating Layer and not a complete autonomous person. | pass | Keep wording stable for release. |
| Runtime entrypoint | `AGENTS.md` points to `RTK.md`; `examples/quickstart-output.md` records Codex read-only replay without the earlier missing-`RTK.md` issue. | pass | Codex path is the current verified runtime path. |
| Structural evaluation | `docs/evaluation.md` defines local and live evaluation gates. | pass | Needs current clean-worktree run before release. |
| Runtime adapters | `docs/runtime-adapters.md` keeps tool-specific files as thin adapters and blocks unverified adapter files. | pass | Do not pre-add `CLAUDE.md` or `GEMINI.md`. |
| Showcase | `examples/showcase.md` contains before/after scenarios. | partial | Needs evidence-style examples with prompts, routing, result, and deviation notes. |
| Dirty worktree | Unstaged changes exist in `GUYUE_PRINCIPLES.md`, `skills/ecosystem-scout/SKILL.md`, and `skills_manifest.json`. | block | Resolve before release. |
| Zero-Leakage | Current full suite stops at `skills_manifest.json` line 177 because an unstaged external dependency entry contains a machine-local absolute path. | block | Replace with a portable package id, public URL, or documented local alias before release. |

## Next Work Plan

### Within 24 hours

- Resolve the current unstaged external-skill intake changes as a separate review slice.
- Run the full release gate on a clean worktree.
- Record the exact command output summary in this file or in `examples/quickstart-output.md`.

### Within 3 days

- Add one non-Codex read-only live replay if the target runtime is available.
- Keep any target-runtime adapter as documentation-only until the replay proves that the adapter is required.
- Convert any failed replay into a concrete boundary fix or documented limitation.

### Within 7 days

- Upgrade `examples/showcase.md` from narrative examples to evidence examples:
  - user prompt;
  - expected routing;
  - observed output summary;
  - visible artifact or decision result;
  - deviation and next action.
- Attach release notes that explain why this release exists, not only what changed.

## Explicit Non-Goals

- Do not add new skills.
- Do not add `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, or Cursor rules without the adapter admission gate.
- Do not publish to a marketplace, create a release tag, push commits, merge branches, or deploy without explicit user authorization.
- Do not hide current dirty-worktree findings behind a release-ready label.

## Recheck Command Block

Run these commands from the repository root before release:

```bash
git status --short
git diff --check
python3 scripts/security_scanner.py
bash scripts/test_suite.sh
```

The release candidate remains blocked until the commands above pass on the intended release tree.

## Result Card

```text
┌─────────────────────────────────────┐
│  Release Candidate · Guyue          │
│                                     │
│  Status: not release-ready          │
│  Focus: evidence, boundaries, replay│
│  Verified runtime: Codex path       │
│  Current blocker: dirty worktree    │
│  Next step: external-skill intake   │
│                                     │
│  Reviewer: Luban                    │
└─────────────────────────────────────┘
```
