# Release Candidate Evidence

Date: 2026-07-02
Status: v1.2.0 local release gates passed; public release action pending explicit authorization
Scope: release-preparation evidence and boundary fixes. This document does not create a tag, push commits, submit to a marketplace, deploy, or change the public runtime adapter policy.

## Baseline

Current candidate baseline at v1.2.0 deep release-audit intake:

- commit: `77b7cd5 docs(release): 刷新发版证据`
- branch state at intake: `main` ahead of `origin/main` by 10 commits
- local files observed at intake:
  - `SKILL.md`
  - 12 existing base child `skills/*/SKILL.md` files
  - 8 new child skill directories
  - `skills_manifest.json`
  - `scripts/extract_software_box.py`
  - `scripts/run_security_scan.py`
  - `test-prompts.json`
  - `README.md`
  - docs and changelog release evidence

These files form the v1.2.0 expansion review slice. The generated local index remains ignored because it can contain machine-specific paths.

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
| Structural evaluation | `docs/evaluation.md` defines local and live evaluation gates. | pass | Needs current full-suite run before any release action. |
| Runtime adapters | `docs/runtime-adapters.md` keeps tool-specific files as thin adapters and blocks unverified adapter files. | pass | Do not pre-add `CLAUDE.md` or `GEMINI.md`. |
| Showcase | README links to real replay evidence and `examples/showcase.md`; the non-informative 1x1 GIF placeholder was removed from the public README path. | pass | Do not reintroduce decorative or non-reproducible demo placeholders. |
| Skill registry | `skills_manifest.json` records 20 routed skills; `test-prompts.json` contains 20 structural prompts. | pass | Keep manifest, README, and tests synchronized when adding skills. |
| Marketplace metadata | `.claude-plugin/marketplace.json` now matches the v1.2.0 candidate version and positioning. | pass | Keep release metadata aligned with `skills_manifest.json`. |
| GitHub CI gate | `.github/workflows/ci.yml` runs zero-leakage scanning, skill structure validation, and prompt evaluation. | pass | `doctor.py` remains a local release gate because it checks machine-installed external skills. |
| v1.2.0 extension boundaries | New website, video, security, software, context, distillation, taste, and minimalism skills include authorization or verification boundaries. | pass | Do not loosen approval gates for CLI, network, install, download, or write actions. |
| Optional ecosystem dependencies | Newly referenced ecosystem projects are marked `required: false`; `scripts/doctor.py` reports them as optional and does not fail local validation. | pass | Optional dependencies are recommendations, not release blockers. |
| Security-gate target boundary | Live replay found that a missing target caused the runtime to infer a local skill directory. `security-gate`, root dispatch, evaluation docs, and test prompts now require an explicit target before scanning; regression replay now stops for clarification. | pass | Keep this case covered before external-intake wording changes. |
| External skill intake | `find-skills` is registered with `vercel-labs/skills@find-skills` and a public source URL; local path discovery is moved to `scripts/discover_local_skills.py`. | pass | Keep public manifest portable; keep local index ignored. |
| Generated local index | `.guyue_memory/local_skills_index.json` is generated by the discovery script and ignored by `.gitignore`. | pass | Never include machine-local path indexes in a public release package. |
| Zero-Leakage | `python3 scripts/security_scanner.py` passes after the local-index boundary fix. | pass | Re-run through `bash scripts/test_suite.sh` before commit/tag. |

## 2026-07-02 Release-Prep Checks

Initial blocker:

- `bash scripts/test_suite.sh` failed at `python3 scripts/ci_validate_skills.py`.
- Failure cause: `scripts/discover_local_skills.py` hardcoded the repository path, and `skills/ecosystem-scout/SKILL.md` contained a machine-path example.

Fix applied:

- `scripts/discover_local_skills.py` now derives the repository root from its own location.
- `.gitignore` excludes `.guyue_memory/local_skills_index.json`.
- `skills/ecosystem-scout/SKILL.md` forbids local hardcoded paths without embedding a machine-specific example.
- `skills_manifest.json` records `find-skills` as `vercel-labs/skills@find-skills` with a public GitHub source URL.

Pre-commit checks passed:

- `python3 scripts/discover_local_skills.py`
- `python3 scripts/ci_validate_skills.py`
- `git diff --check`
- `find . \( -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store' \) -print`
- `python3 scripts/security_scanner.py`
- `bash scripts/test_suite.sh`

## 2026-07-02 v1.2.0 Expansion Checks

Initial blockers:

- `bash scripts/test_suite.sh` failed because new ecosystem dependencies were treated as mandatory installations.
- `python3 scripts/run_eval.py` failed because new routed skills had no structural test prompts.
- `python3 scripts/ci_validate_skills.py` failed because several `trigger_includes` frontmatter lists were invalid YAML.
- `git diff --check` failed on trailing whitespace and extra EOF blank lines.
- New external-skill routing text implied direct CLI/network execution without an explicit approval gate.
- `software-advisor` and `extract_software_box.py` contained machine-local absolute paths.
- `security-gate` and `run_security_scan.py` overclaimed a full third-party security engine while shipping only local behavior.

Fix applied:

- Added `security-gate` to `skills_manifest.json` and bumped manifest version to `1.2.0`.
- Added test prompt coverage for all 20 routed skills.
- Marked newly referenced ecosystem projects as optional with `required: false`.
- Updated `scripts/doctor.py` so optional dependencies warn without failing local release validation.
- Rewrote external-skill invocation wording to require `security-gate`, visible action summaries, and explicit approval before CLI/network/install/write/download actions.
- Removed machine-local paths from `software-advisor` and `extract_software_box.py`.
- Reframed `security-gate` as a local heuristic preflight, not a complete supply-chain audit.
- Updated README from 12 skills to `12 + 8` routed capability framing and changed the public badge to release-candidate status.

Current local checks passed:

- `bash scripts/test_suite.sh`
- `git diff --check`
- `find . \( -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store' \) -print`
- `python3 scripts/security_scanner.py`

## 2026-07-02 Security-Gate Replay Follow-Up

Live replay command:

```bash
codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-v1.2-security-gate-replay.md "<security-gate prompt>"
```

Observed result:

- The runtime loaded the Guyue entrypoint and local `security-gate` instructions.
- The runtime did not edit files, install dependencies, or execute network requests.
- The runtime still inferred a local third-party skill directory when the prompt did not provide a target.

Release judgement:

- Initial run marked as `partial_pass`, not a release pass.
- Fixed by adding an explicit target-confirmation gate to `skills/security-gate/SKILL.md`, root ecosystem dispatch in `SKILL.md`, `test-prompts.json`, `docs/evaluation.md`, and live replay evidence.
- Regression replay passed: the runtime stopped because no concrete third-party target was provided, did not infer a local directory, and did not run `run_security_scan.py`.

## 2026-07-02 Release Evidence Refresh

Additional blockers found during release-readiness review:

- README still used the phrase "all-purpose digital partner", which conflicted with the public boundary that Guyue is not a complete autonomous person or universal automation system.
- README referenced `assets/demo.gif`, but that file was only a 1x1 placeholder and therefore not acceptable as public showcase evidence.
- `.claude-plugin/marketplace.json` still declared version `1.0.0` while the current manifest candidate is `1.2.0`.

Fix applied:

- Replaced the over-broad README positioning with Personal Agent Operating Layer wording.
- Replaced the placeholder GIF reference with links to real live replay and showcase evidence.
- Removed the placeholder GIF asset from the tracked release path.
- Updated marketplace metadata to version `1.2.0`.

Verification after refresh:

- `bash scripts/test_suite.sh`
- `git diff --check`
- `find . \( -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store' \) -print`
- `python3 scripts/security_scanner.py`

## 2026-07-02 Deep Release Audit

Additional issues found during a deeper release audit:

- The baseline file inventory still said 13 existing child skills plus 8 new child skills, which contradicted the current manifest and README count of 20 routed child skills.
- GitHub CI only ran `scripts/ci_validate_skills.py`, so a remote green check would not prove zero-leakage or prompt-evaluation coverage.
- The published `.guyue_memory/index.json` used a legacy list shape, while `src/mcp_server.py` and `skills/memory-bank/SKILL.md` require `{"memories": [...]}`. This would crash memory reads and writes through the MCP server.
- Fresh virtualenv verification failed because `ci_validate_skills.py` imports `yaml`, while `requirements.txt` only declared `mcp`.

Fix applied:

- Corrected the baseline inventory to 12 existing base child skills plus 8 extension child skills.
- Expanded GitHub CI to run `scripts/security_scanner.py`, `scripts/ci_validate_skills.py`, and `scripts/run_eval.py`.
- Kept `scripts/doctor.py` as a local-only release gate because it validates machine-installed external skills and would be unstable on a clean GitHub runner.
- Converted the published memory index to the documented object shape and made the MCP server tolerate legacy list-shaped indexes during upgrades.
- Added `PyYAML` to `requirements.txt`, changed GitHub CI to install from `requirements.txt`, and updated install docs to install dependencies before running `scripts/test_suite.sh`.

## Next Work Plan

### Before release action

- Re-run the full release gate on the intended release tree if any file changes before the release action.
- Confirm `git status --short` contains no unreviewed local changes.
- Decide whether the release is only a local candidate or should proceed to tag/marketplace submission.

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

- Do not add more skills beyond the reviewed v1.2.0 extension set without a new manifest/test/release-evidence cycle.
- Do not add `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, or Cursor rules without the adapter admission gate.
- Do not publish to a marketplace, create a release tag, push commits, merge branches, or deploy without explicit user authorization.
- Do not hide local generated indexes or machine-path findings behind a release-ready label.

## Recheck Command Block

Run these commands from the repository root before release:

```bash
git status --short
git diff --check
python3 scripts/security_scanner.py
bash scripts/test_suite.sh
```

The local release gates pass on the intended v1.2.0 candidate tree. Public release action remains blocked until explicit user authorization for push, tag, marketplace submission, or deployment.

## Result Card

```text
┌─────────────────────────────────────┐
│  Release Candidate · Guyue          │
│                                     │
│  Status: v1.2.0 local gates passed  │
│  Focus: skill expansion boundaries  │
│  Verified runtime: Codex path       │
│  Current blocker: release auth      │
│  Next step: release authorization    │
│                                     │
│  Reviewer: Luban                    │
└─────────────────────────────────────┘
```
