# Release Checklist

This project should not be released just because the repository is clean. Release only when installation, verification, safety, and examples are all understandable to a new user.

## Current Candidate Snapshot

Date: 2026-07-03
Baseline commit before this deep release audit: `77b7cd5 docs(release): 刷新发版证据`

- [x] Positioning states Guyue is a Personal Agent Operating Layer, not a complete autonomous person.
- [x] README links to installation, security, evaluation, live replay evidence, and showcase material.
- [x] Skill count is consistent across README, manifest, and structural tests: 26 routed skills and 45 structural prompts.
- [x] `docs/runtime-adapters.md` blocks unverified `CLAUDE.md`, `GEMINI.md`, Copilot, and Cursor adapters.
- [x] `examples/quickstart-output.md` records Codex read-only live replay results, including fixed deviations.
- [x] `security-gate` missing-target behavior has a regression replay and now stops for clarification.
- [x] Placeholder demo GIF is removed; current visible evidence is text replay plus a reproducible showcase GIF referenced from `examples/showcase.md`.
- [x] Marketplace metadata is aligned to the current candidate positioning.
- [x] Current release-evidence refresh passed `bash scripts/test_suite.sh`, `git diff --check`, cache scan, and `python3 scripts/security_scanner.py`.
- [x] GitHub CI covers zero-leakage, SKILL structure validation, and prompt evaluation; local `doctor.py` remains part of the manual release gate.
- [x] Published memory index matches the documented `{"memories": [...]}` schema and the MCP server accepts legacy list-shaped indexes.
- [x] Fresh install path declares `PyYAML` in `requirements.txt`; README, installation docs, and GitHub CI all install from the same dependency file.
- [x] Fresh `HOME` validation path passes without preinstalled external ecosystem skills; external skills are optional enhancements, not release-gate blockers.
- [x] `git archive` release bundle can run `scripts/test_suite.sh` without a `.git` directory.
- [x] Release bundle must be created from `git archive` or the target source-package mechanism, not by zipping the working directory with ignored private files.
- [x] Validation scripts do not leave `__pycache__`, `.pyc`, or `.DS_Store` artifacts after `bash scripts/test_suite.sh`.
- [x] MCP server resolves manifest and memory paths from the repository root even when launched from `src/`.
- [x] `SKILL.md` distinguishes required dependency blockers from optional ecosystem enhancement warnings.
- [x] Public/tracked Markdown internal links are validated by `scripts/ci_validate_skills.py`.
- [x] Code-spanned Skill resource references such as `references/...` and `scripts/...` resolve to tracked or staged release files.
- [x] Manifest skill paths, directories, and child `SKILL.md` frontmatter names are validated by `scripts/ci_validate_skills.py`.
- [x] Diagnostic helper commands do not assume a fixed home-relative install root.
- [x] Project configuration alignment is validated across manifest, marketplace metadata, `skills.json`, GitHub CI, and optional dependency flags.
- [x] `human-voice` language defaults, mixed-label cleanup, manifest triggers, and live replay evidence are validated by `scripts/ci_validate_skills.py`.
- [x] Business-readable output defaults, term explanations,方案五要素, manifest triggers, and evaluation prompts are validated by `scripts/ci_validate_skills.py`.
- [x] `context-compressor` context-budget routing, MCP/tool-output boundaries, third-party quick-install gates, external-tool intake limits, and token-saving evidence rules are validated by `scripts/ci_validate_skills.py`.
- [x] Showcase GIF, `assets/demo.tape`, and `scripts/render_demo_gif.py` are validated as tracked or staged release files; ignored or untracked showcase assets fail CI.
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
- [ ] Any new `references/`, `scripts/`, `assets/`, or `examples/` file mentioned from a `SKILL.md` is tracked or staged before release packaging.

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
