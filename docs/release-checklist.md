# Release Checklist

This project should not be released just because the repository is clean. Release only when installation, verification, safety, and examples are all understandable to a new user.

## Current v1.2.0 Candidate Snapshot

Date: 2026-07-02
Baseline commit before this deep release audit: `77b7cd5 docs(release): 刷新发版证据`

- [x] Positioning states Guyue is a Personal Agent Operating Layer, not a complete autonomous person.
- [x] README links to installation, security, evaluation, live replay evidence, and showcase material.
- [x] Skill count is consistent across README, manifest, and structural tests: 20 routed skills.
- [x] `docs/runtime-adapters.md` blocks unverified `CLAUDE.md`, `GEMINI.md`, Copilot, and Cursor adapters.
- [x] `examples/quickstart-output.md` records Codex read-only live replay results, including fixed deviations.
- [x] `security-gate` missing-target behavior has a regression replay and now stops for clarification.
- [x] Placeholder demo GIF is removed from the public README path; current visible evidence is text replay and showcase examples.
- [x] Marketplace metadata is aligned to v1.2.0 candidate positioning.
- [x] Current release-evidence refresh passed `bash scripts/test_suite.sh`, `git diff --check`, cache scan, and `python3 scripts/security_scanner.py`.
- [x] GitHub CI covers zero-leakage, SKILL structure validation, and prompt evaluation; local `doctor.py` remains part of the manual release gate.
- [x] Published memory index matches the documented `{"memories": [...]}` schema and the MCP server accepts legacy list-shaped indexes.
- [x] Public release actions still require explicit authorization for push, tag, marketplace submission, or deployment.

The checklist below remains the reusable release gate. Re-run it after any additional change before tag or publication.

## Positioning

- [ ] README says Guyue is a Personal Agent Operating Layer, not a complete autonomous person.
- [ ] README explains who should use it and why they should install it instead of asking an agent ad hoc.
- [ ] README links to installation, security, and evaluation docs.
- [ ] Skill count is consistent across `README.md`, `skills_manifest.json`, and `skills/`.

## Installation

- [ ] `docs/installation.md` covers Codex.
- [ ] `docs/installation.md` covers Claude Code.
- [ ] `docs/installation.md` covers MCP clients.
- [ ] `docs/installation.md` covers VS Code/Copilot-style Agent Skills.
- [ ] `docs/installation.md` covers OpenClaw local install.
- [ ] `docs/runtime-adapters.md` is current before adding or changing runtime-specific adapter files.
- [ ] First-run prompt produces a visible planning or analysis result without editing files.

## Verification

- [ ] `docs/release-candidate.md` names the current baseline commit, blockers, live replay coverage, and next work plan.
- [ ] `python3 scripts/security_scanner.py` passes.
- [ ] `python3 scripts/doctor.py` passes.
- [ ] `python3 scripts/ci_validate_skills.py` passes.
- [ ] `python3 scripts/run_eval.py` passes.
- [ ] `bash scripts/test_suite.sh` passes.

## Security

- [ ] No API keys, tokens, cookies, private keys, or personal account details are present.
- [ ] No generated cache files are tracked.
- [ ] External skill intake requires `ecosystem-scout` assessment and approval.
- [ ] Unknown install scripts are not auto-executed.
- [ ] Publishing, marketplace submission, tag creation, and deployment require explicit user authorization.

## Showcase

- [ ] README includes a visible demo or links to one.
- [ ] `examples/showcase.md` includes before/after behavior.
- [ ] Any recorded GIF or screenshot can be regenerated or explained.
- [ ] Evaluation evidence is attached to the release notes.

## Release Notes

- [ ] `CHANGELOG.md` explains why the release exists, not only what changed.
- [ ] Known limitations are listed.
- [ ] Next iteration entry points are listed.
