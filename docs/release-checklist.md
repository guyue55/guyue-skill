# Release Checklist

This project should not be released just because the repository is clean. Release only when installation, verification, safety, and examples are all understandable to a new user.

## Current Candidate Snapshot

Date: 2026-07-10
Candidate version: `1.3.0`
Baseline commit before this deep release audit: `995072c feat(goal): 完善长线目标铸造`

- [x] Positioning states Guyue is a Personal Agent Operating Layer, not a complete autonomous person.
- [x] README links to installation, security, evaluation, live replay evidence, and showcase material.
- [x] `docs/luban-report-v1.3.0.md` records the evidence-based score,同行对标, known limits, certificate, and post-release recheck path.
- [x] Skill count is consistent across README, manifest, and structural tests: 26 routed skills and 54 structural prompts.
- [x] `docs/runtime-adapters.md` blocks unverified `CLAUDE.md`, `GEMINI.md`, Copilot, and Cursor adapters.
- [x] `examples/quickstart-output.md` records Codex read-only live replay results, including fixed deviations.
- [x] `security-gate` missing-target behavior has a regression replay and now stops for clarification.
- [x] Placeholder demo GIF is removed; current visible evidence is text replay plus a reproducible showcase GIF referenced from `examples/showcase.md`.
- [x] Claude marketplace metadata passes `claude plugin validate --strict .` and declares the repository root as an explicit skill bundle.
- [x] An isolated Claude Code 2.1.170 install reports Guyue 1.3.0 enabled with 27 Skill components and a complete payload.
- [x] Current release-evidence refresh passed `bash scripts/test_suite.sh`, `git diff --check`, cache scan, and `python3 scripts/security_scanner.py`.
- [x] GitHub CI listens to `dev` and `main`, installs declared dependencies, and runs the complete release gate twice to catch non-idempotent cache or artifact pollution.
- [x] Published memory index matches the documented `{"memories": [...]}` schema and the MCP server accepts legacy list-shaped indexes.
- [x] Fresh install path declares `PyYAML` in `requirements.txt`; README, installation docs, and GitHub CI all install from the same dependency file.
- [x] Fresh `HOME` validation path passes without preinstalled external ecosystem skills; external skills are optional enhancements, not release-gate blockers.
- [x] GitHub-generated source archives are filtered by `.gitattributes` `export-ignore` rules.
- [x] Release source archives keep curated memory entrypoints (`.guyue_memory/index.json`, `.guyue_memory/global_context.md`) but exclude `.guyue_memory/active/**`.
- [x] `git archive` release bundle can run `scripts/test_suite.sh` without a `.git` directory.
- [x] Release bundle must be created from GitHub source archives, `git archive`, or the target source-package mechanism, not by zipping the working directory with ignored private files.
- [x] Validation scripts do not leave `__pycache__`, `.pyc`, or `.DS_Store` artifacts after `bash scripts/test_suite.sh`.
- [x] MCP server resolves manifest and memory paths from the repository root even when launched from `src/`.
- [x] `SKILL.md` distinguishes required dependency blockers from optional ecosystem enhancement warnings.
- [x] Public/tracked Markdown internal links are validated by `scripts/ci_validate_skills.py`.
- [x] Code-spanned Skill resource references such as `references/...` and `scripts/...` resolve to files included in the release source archive.
- [x] Manifest skill paths, directories, and child `SKILL.md` frontmatter names are validated by `scripts/ci_validate_skills.py`.
- [x] Diagnostic helper commands do not assume a fixed home-relative install root.
- [x] Project configuration alignment is validated across manifest, marketplace metadata, `skills.json`, GitHub CI, and optional dependency flags.
- [x] `human-voice` language defaults, mixed-label cleanup, manifest triggers, and live replay evidence are validated by `scripts/ci_validate_skills.py`.
- [x] Business-readable output defaults, term explanations,方案五要素, manifest triggers, and evaluation prompts are validated by `scripts/ci_validate_skills.py`.
- [x] `context-compressor` context-budget routing, MCP/tool-output boundaries, third-party quick-install gates, external-tool intake limits, and token-saving evidence rules are validated by `scripts/ci_validate_skills.py`.
- [x] Reuse-first engineering defaults, single-authoritative-entry rules for functions, models, tables, parameters, API contracts, permissions, components, prompts, dialogs, and scripts are validated by `scripts/ci_validate_skills.py`.
- [x] Full-stack development defaults for best practices, necessary comments, modularity, backend-owned permissions, frontend permission presentation, build/lint/test gates, Chinese commit format, and UI-only default frontend workflows are validated by `scripts/ci_validate_skills.py`.
- [x] Loop engineering and dynamic workflow routing, Loop Contract fields, subagent budgets, independent verifiers, stop conditions, and replay evidence are validated by `scripts/ci_validate_skills.py`.
- [x] Frontend design ecosystem routing, product-type classification, DESIGN.md/Figma/Refero reference boundaries, deterministic UI checks, and website reconstruction authorization limits are validated by `scripts/ci_validate_skills.py`.
- [x] Showcase GIF, `assets/demo.tape`, and `scripts/render_demo_gif.py` are validated as files included in the release source archive; ignored, untracked, or export-ignored showcase assets fail CI.
- [x] `scripts/check_birth_certificate.py` validates the public entrypoint, install path, trigger surface, evidence links, safety boundaries, and synchronized skill/prompt counts.
- [x] Long Goal masters explicitly list every phase-plan file, and `scripts/check_long_goal_pack.py --self-test` rejects an unlisted phase.
- [x] Zero-Leakage scans tracked and unignored untracked files; an untracked fake-key probe is blocked before staging.
- [x] Public release actions still require explicit authorization for push, tag, marketplace submission, or deployment.
- [x] Public install docs disclose that generic root-level `npx skills add` installs only `SKILL.md`; the supported full install preserves the whole repository tree.
- [x] `scripts/install_guyue.py` defaults optional dependencies to plan-only mode and requires explicit `safe` or `all` opt-in before third-party installation.
- [x] All child skills pass official frontmatter validation; unsupported `trigger_includes` fields were folded into descriptions.
- [x] MCP memory tests reject empty queries and common secret/path writes, preserve unique filenames for rapid writes, and verify keyword retrieval.
- [x] `scripts/check_full_install.py --self-test` rejects a root-only generic CLI payload and accepts the complete routed repository payload.
- [x] Independent Codex review found one template/checker mismatch; both plain and code-spanned Long Goal control paths now pass regression coverage.
- [x] The final staged source archive passes the ten-part release suite twice with no `.git` directory and an empty HOME.

The checklist below remains the reusable release gate. Re-run it after any additional change before tag or publication.

## Positioning

- [ ] README says Guyue is a Personal Agent Operating Layer, not a complete autonomous person.
- [ ] README explains who should use it and why they should install it instead of asking an agent ad hoc.
- [ ] README links to installation, security, and evaluation docs.
- [ ] Skill count is consistent across `README.md`, `skills_manifest.json`, and `skills/`.

## Installation

- [ ] `docs/installation.md` covers Codex.
- [ ] `docs/installation.md` covers Claude Code.
- [ ] Public GitHub marketplace installation succeeds after push and before tag creation.
- [ ] `docs/installation.md` covers MCP clients.
- [ ] `docs/installation.md` covers VS Code/Copilot-style Agent Skills.
- [ ] `docs/installation.md` covers OpenClaw local install.
- [ ] Installation preserves the full repository payload; do not approve a root-only generic CLI copy as a complete Guyue install.
- [ ] Default optional dependency handling is plan-only; networked third-party installation requires explicit mode selection.
- [ ] `docs/runtime-adapters.md` is current before adding or changing runtime-specific adapter files.
- [ ] First-run prompt produces a visible planning or analysis result without editing files.

## Verification

- [ ] `docs/release-candidate.md` names the current baseline commit, blockers, live replay coverage, and next work plan.
- [ ] `python3 scripts/security_scanner.py` passes.
- [ ] `python3 scripts/doctor.py` passes.
- [ ] `python3 scripts/ci_validate_skills.py` passes.
- [ ] `python3 scripts/run_eval.py` passes.
- [ ] `python3 scripts/check_birth_certificate.py` passes.
- [ ] `python3 scripts/check_long_goal_pack.py --self-test` passes.
- [ ] `python3 scripts/check_full_install.py --self-test` passes.
- [ ] `claude plugin validate --strict .` passes when preparing a Claude marketplace release.
- [ ] `python3 scripts/test_mcp_server.py` passes.
- [ ] Official `skills-ref` validation passes for every child skill and for the root staged under a directory named `guyue`.
- [ ] `bash scripts/test_suite.sh` passes.
- [ ] Any new `references/`, `scripts/`, `assets/`, or `examples/` file mentioned from a `SKILL.md` is included in the release source archive before release packaging.

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
