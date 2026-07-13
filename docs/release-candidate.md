# Guyue v1.5.0 Release Candidate

Date: 2026-07-13
State: release preparation on `dev`; not tagged or published
Base tag: `v1.4.0`
Green collaboration parent: `2916a4bfda8fb64bb4434b9238ae752d7652075e`

## Current Baseline

The candidate combines two commits after v1.4.0: `794a883` establishes durable data, knowledge and installed-payload ownership; `2916a4b` adds machine-readable collaboration for all 26 capabilities. Release metadata is prepared as `1.5.0` with `release_state=release-candidate`. The final preparation commit and its remote run are recorded externally after commit so the candidate tree does not claim its own future object ID.

## Current Evidence

- 15/15 local release stages pass.
- 54/54 broad routes, 10/10 collaboration cases and 26/26 workflow Skill coverage pass.
- 345/345 internal triggers, 208/208 near misses, 48/48 external candidates and 26/26 retained activation/output evidence pass.
- A fresh read-only Codex session returns `collaboration_candidate`, selects `skill-release`, preserves four-stage order and rejects automatic commit, merge, tag or release.
- Empty-HOME file-Git installation, restart identity, installed payload checks, private-memory lifecycle and Long Goal recovery/sealing pass.
- Claude marketplace metadata passes strict schema validation. This is metadata proof, not current Claude model activation proof.
- Collaboration baseline `2916a4b` passes doubled `dev` CI run `29229209401`.

## Remaining Blockers

1. The final release-preparation commit must pass the doubled remote CI on `dev`.
2. `main` still points to v1.4.0 and requires explicit authorization for a fast-forward merge and push.
3. The resulting `main` must pass doubled remote CI and a public-network empty-HOME installation before tag creation.
4. Creating and pushing annotated tag `v1.5.0` requires explicit action-specific authorization.
5. GitHub Release publication is a separate action and is not implied by tag preparation.

## Next Work Plan

1. Freeze and push the exact v1.5.0 candidate on `dev`; record commit, CI run and payload SHA-256.
2. Stop and obtain explicit authorization for `main` fast-forward and push.
3. Verify doubled `main` CI and public-network empty-HOME installation against the frozen payload.
4. Stop and obtain explicit authorization for annotated tag `v1.5.0` and tag push.
5. Publish a GitHub Release only under separate authorization, then record the release URL and final install replay.

The historical evidence below is retained for provenance. It does not grant current authorization or prove the v1.5.0 candidate.

---

# Historical Release Evidence: Guyue v1.3.0

Date: 2026-07-10
Status: historical snapshot; v1.3.0 passed public-source installation and remote CI verification and was released
Scope: evidence for the completed v1.3.0 release operation. Its authorization, tag, public installation and remote CI results do not authorize or prove the current unreleased candidate.

> [!WARNING]
> This document is frozen historical evidence. For current work, use [release-checklist.md](release-checklist.md#unreleased-candidate-work) and [guyue-long-goal-meta-control-polish-2026-07-11.md](guyue-long-goal-meta-control-polish-2026-07-11.md). Do not reuse the result card below as current release readiness.

## 2026-07-10 Comprehensive Luban Audit

- Full-package truth: source inspection and a live Codex replay confirmed that generic root-level `npx skills add` copies only `SKILL.md`; public installation now requires mounting the complete repository, and `scripts/check_full_install.py --self-test` rejects a root-only payload.
- Public specification: all 26 child skills pass `npx skills-ref validate`; the root passes when staged under its install name `guyue`. Five unsupported `trigger_includes` fields were folded into standard descriptions.
- Installation safety: `scripts/install_guyue.py` now defaults optional dependencies to dry-run planning. Networked third-party installation requires explicit `safe` or `all` selection.
- MCP safety: empty memory queries, common credential patterns, and personal absolute paths are rejected before storage; rapid writes use microsecond filenames and atomic index replacement. Focused temporary-directory tests pass.
- Frontend judgment: defaults now preserve the product type, existing design system, and current stack. GSAP, Tailwind, glass effects, asymmetry, and unverified conversion claims are conditional rather than stylistic defaults.
- Live evidence: the full-install replay reached the correct safe conclusion without scripts after the routing fix, but still used 16 read-only commands; mark context efficiency `partial_pass`. The React/MUI SaaS replay correctly refused four unnecessary frontend additions and passed.
- Local gate: `bash scripts/test_suite.sh`, `git diff --check`, official frontmatter validation, install-plan replay, and focused MCP tests passed before final review. Later release authorization and public evidence are recorded below.
- Claude marketplace: the former custom object failed Claude Code 2.1.170 validation because it omitted `owner` and `plugins`; v1.3.0 now uses the official marketplace schema and an explicit root skill bundle. Official strict validation and isolated install evidence are required below.
- Claude install evidence: `claude plugin validate --strict .` passed; an empty-HOME local marketplace install enabled `guyue@guyue` at 1.3.0, reported 27 Skill components and about 1,940 always-on tokens, preserved the full payload, and passed the complete suite twice from the installed cache.
- CI evidence: v1.3.0 CI listens to `dev` and `main` pushes plus pull requests to `main`, then runs the same complete release gate twice after installing `requirements.txt`.
- CI runtime evidence: the first remote pass exposed GitHub's Node 20 deprecation warning despite green jobs. The workflow now uses `actions/checkout@v6` and `actions/setup-python@v6`, and the local configuration gate requires those Node 24-native majors before release.
- Remote CI evidence: commit `10237d7` passed the complete gate twice on `dev` run `29083000196` and `main` run `29083044900`; both check runs completed without annotations.
- Public installation evidence: an empty `HOME` added `guyue55/guyue-skill` over HTTPS, installed `guyue@guyue` 1.3.0 from public `main`, reported 27 Skill components and about 1,940 always-on tokens, passed `scripts/check_full_install.py`, and passed the installed-cache release suite twice.
- Dependency evidence: runtime dependencies are bounded to compatible major lines and were verified with Python 3.11, mcp 1.28.1, and PyYAML 6.0.3.
- Independent review: Codex review found that the Long Goal checker accepted only code-spanned control paths while the public template used plain paths. The parser and self-test now cover both formats.

## Baseline

Historical baseline at v1.2.0 deep release-audit intake:

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

## Evidence At The v1.3.0 Freeze

| Area | Current evidence | Result | Release impact |
|---|---|---|---|
| Positioning | README states Guyue is a Personal Agent Operating Layer and not a complete autonomous person. | pass | Keep wording stable for release. |
| Runtime entrypoint | `AGENTS.md` points to `RTK.md`; `examples/quickstart-output.md` records Codex read-only replay without the earlier missing-`RTK.md` issue. | pass | Codex path is the current verified runtime path. |
| Structural evaluation | `docs/evaluation.md` defines local and live evaluation gates; the final local suite and doubled remote CI pass. | pass | Re-run after any post-evidence source change. |
| Runtime adapters | `docs/runtime-adapters.md` keeps tool-specific files as thin adapters and blocks unverified adapter files. | pass | Do not pre-add `CLAUDE.md` or `GEMINI.md`. |
| Showcase | README links to real replay evidence and `examples/showcase.md`; the non-informative 1x1 GIF placeholder was removed from the public README path. | pass | Do not reintroduce decorative or non-reproducible demo placeholders. |
| Skill registry | `skills_manifest.json` records 26 routed skills; `test-prompts.json` contains 54 structural prompts. | pass | Keep manifest, README, and tests synchronized when adding skills. |
| Marketplace metadata | `.claude-plugin/marketplace.json` matches v1.3.0 and the official skill-bundle schema; public empty-HOME installation succeeds. | pass | Keep release metadata aligned with `skills_manifest.json`. |
| GitHub CI gate | `.github/workflows/ci.yml` uses Node 24-native Actions and runs the complete release suite twice on `dev` and `main`. | pass | Preserve doubled idempotence coverage and inspect annotations, not only conclusions. |
| v1.2.0 extension boundaries | New website, video, security, software, context, distillation, taste, and minimalism skills include authorization or verification boundaries. | pass | Do not loosen approval gates for CLI, network, install, download, or write actions. |
| Optional ecosystem dependencies | Newly referenced ecosystem projects are marked `required: false`; `scripts/doctor.py` reports them as optional and does not fail local validation. | pass | Optional dependencies are recommendations, not release blockers. |
| Security-gate target boundary | Live replay found that a missing target caused the runtime to infer a local skill directory. `security-gate`, root dispatch, evaluation docs, and test prompts now require an explicit target before scanning; regression replay now stops for clarification. | pass | Keep this case covered before external-intake wording changes. |
| External skill intake | `find-skills` is registered with `vercel-labs/skills@find-skills` and a public source URL; local path discovery is moved to `scripts/discover_local_skills.py`. | pass | Keep public manifest portable; keep local index ignored. |
| Generated local index | `.guyue_memory/local_skills_index.json` is generated by the discovery script and ignored by `.gitignore`. | pass | Never include machine-local path indexes in a public release package. |
| Active memory packaging | `.gitattributes` excludes `.guyue_memory/active/**`; CI keeps `.guyue_memory/index.json` and `.guyue_memory/global_context.md` included while blocking active-memory leakage into source archives. | pass | Ship curated memory entrypoints only; keep working memory local. |
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
- Fresh `HOME` verification failed because `doctor.py` treated external ecosystem skills as mandatory, making `bash scripts/test_suite.sh` fail for a new user who had only cloned Guyue and installed Python dependencies.
- `git archive` verification failed because `scripts/security_scanner.py` depended on `git ls-files`; GitHub source tarballs and marketplace bundles do not include `.git`.
- `bash scripts/test_suite.sh` left `__pycache__` and `.pyc` files behind because the Python validator used `py_compile.compile()` for syntax checks.
- MCP import verification passed, but runtime data lookup was wrong when following the documented `cwd=/path/to/guyue/src` setup because `src/mcp_server.py` treated the process cwd as the repository root.
- `SKILL.md` still said missing doctor dependencies should always stop execution, which contradicted the v1.2.0 optional-enhancement boundary.
- Public Markdown internal links were only checked manually, so README, docs, examples, and tracked skill docs could regress with broken relative links after release.
- `skills_manifest.json` paths and child `SKILL.md` frontmatter were only checked by ad hoc probes, so a future manifest entry could point to a missing or mismatched skill without failing CI.
- `scripts/ai_log_scanner.py` printed helper commands under one fixed home-relative install root, which contradicted the documented `/path/to/guyue` portable install model.
- Cross-file release configuration was only checked manually, so manifest version, marketplace metadata, `skills.json`, CI workflow commands, optional dependency status, and fixed install-root strings could drift without failing validation.
- `assets/demo.tape` outputs `assets/demo.gif`, but showcase validation did not require the GIF and fallback renderer to be release files. A local green check could still depend on untracked files that would be missing from a packaged release.

Fix applied:

- Corrected the baseline inventory to 12 existing base child skills plus 8 extension child skills.
- Expanded GitHub CI to run `scripts/security_scanner.py`, `scripts/ci_validate_skills.py`, and `scripts/run_eval.py`.
- Kept `scripts/doctor.py` as a local-only release gate because it validates machine-installed external skills and would be unstable on a clean GitHub runner.
- Converted the published memory index to the documented object shape and made the MCP server tolerate legacy list-shaped indexes during upgrades.
- Added `PyYAML` to `requirements.txt`, changed GitHub CI to install from `requirements.txt`, and updated install docs to install dependencies before running `scripts/test_suite.sh`.
- Marked external ecosystem skills as optional enhancements in `skills_manifest.json` and updated README wording so missing third-party skills warn without blocking fresh local validation.
- Added a filesystem fallback to `scripts/security_scanner.py` so release bundles without `.git` can still run `scripts/test_suite.sh`; the fallback scans the bundle tree itself and only skips `.git` internals.
- Replaced write-producing Python bytecode compilation in `scripts/ci_validate_skills.py` with AST syntax parsing so validation does not leave cache artifacts.
- Do not create release bundles by zipping the working directory. Use `git archive` or the target marketplace/source-package mechanism so ignored private research files and local indexes are not included accidentally.
- Changed `src/mcp_server.py` to resolve the repository root from `__file__` instead of the launch directory and added a CI validator assertion for MCP manifest and memory paths.
- Updated `SKILL.md` so doctor only blocks on required dependencies; optional ecosystem skills remain non-blocking enhancement warnings.
- Added tracked/public Markdown internal-link validation to `scripts/ci_validate_skills.py`; ignored local research drafts remain outside the public release gate.
- Added `skills_manifest.json` skill-path validation to `scripts/ci_validate_skills.py`, covering path existence, repository containment, `SKILL.md` target, directory/name alignment, frontmatter name alignment, and manifest coverage for every `skills/*/SKILL.md`.
- Replaced the hardcoded home-relative helper-command examples in `scripts/ai_log_scanner.py` with repository-root-relative `python3 scripts/...` commands.
- Added project configuration validation to `scripts/ci_validate_skills.py`, covering marketplace/manifest version alignment, marketplace entrypoint, `skills.json`, required CI commands, optional external dependency status, and fixed install-root command strings.
- Removed the old `assets/demo.gif` ignore rule and made `scripts/ci_validate_skills.py` require the showcase GIF, `assets/demo.tape`, and `scripts/render_demo_gif.py` to be included in the release source archive.

Fresh install verification after fix:

- `python3 -m venv /tmp/guyue-fresh-venv`
- `/tmp/guyue-fresh-venv/bin/python -m pip install -r requirements.txt`
- `HOME=/tmp/guyue-empty-home PATH=/tmp/guyue-fresh-venv/bin:$PATH bash scripts/test_suite.sh`
- `git archive --format=tar HEAD | tar -xf - -C /tmp/guyue-archive-check`
- `HOME=/tmp/guyue-archive-home PATH=/tmp/guyue-archive-venv/bin:$PATH bash scripts/test_suite.sh`
- `cd src && python3 - <<'PY' ... import mcp_server ... assert MANIFEST_FILE and MEMORY_DIR point to the repository root ... PY`
- `python3 scripts/ci_validate_skills.py` now reports `tracked markdown internal links valid.`
- `python3 scripts/ci_validate_skills.py` now reports `skills_manifest.json skill paths valid.`
- Fixed-install-root string scan over tracked files returns no matches.
- `python3 scripts/ci_validate_skills.py` now reports `project configuration files valid.` and `no fixed install-root commands detected.`
- `python3 scripts/render_demo_gif.py --check` validates the GIF header and decodability; `scripts/ci_validate_skills.py` blocks ignored or untracked showcase assets.

## 2026-07-03 Capability Fusion Audit

Additional issues found during Luban deep polishing:

- A tracked `SKILL.md` referenced `references/short-drama-example-learnings.md`, but that new reference file was not in the release file set.
- `scripts/ci_validate_skills.py` only checked Markdown links, so code-spanned Skill resources such as `references/...` could exist locally but be omitted from the package.
- Release checklist and evaluation docs still described the older 20-skill baseline after the manifest and README expanded to 25 routed skills.
- Later human-voice, business-readable output, context-budget, third-party quick-install gate, reuse-first engineering, development-defaults, loop-engineering, frontend-design-ecosystem, and long-goal integration expanded the manifest to 26 routed skills and `test-prompts.json` to 52 structural prompts, but release evidence still carried older count snapshots.
- The human-voice language-default rule was present in docs and tests, but no CI guard checked that principles, root routing, manifest triggers, README, test prompt, and live replay evidence stayed synchronized.

Fix applied:

- Added `skills/video-creation-sop/references/short-drama-example-learnings.md` to the release slice.
- Added Skill resource reference validation to `scripts/ci_validate_skills.py`, with child-skill-relative resolution first and repository-root fallback for shared scripts.
- Tightened Markdown link validation so relative link targets must be included in the release source archive, not merely present in the local working tree.
- Added `.gitattributes` `export-ignore` rules so GitHub-generated source archives exclude repository maintenance metadata, local indexes, private/raw research inputs, caches, environment files, build outputs, and logs while keeping runtime/installable files.
- Added CI validation for the key GitHub source archive export rules so the automatic zip/tar.gz packaging contract cannot silently drift.
- Added active-memory archive validation so public source packages include only curated memory entrypoints, not `.guyue_memory/active/**` working notes.
- Updated release and evaluation docs to reflect 25 routed skills and 36 structural prompts.
- Updated release evidence and checklist counts again to reflect the current 26 routed skills and 52 structural prompts after the human-voice, business-readable, context-budget, third-party quick-install, reuse-first engineering, development-defaults, loop-engineering, frontend-design-ecosystem, and long-goal gates were integrated.
- Added a context-budget CI guard so `context-compressor` keeps MCP/tool-output boundaries, third-party quick-install gates, external-tool intake limits, and measured-or-marked token-saving claims synchronized across Skill instructions, manifest routing, and evaluation prompts.
- Added a reuse-first engineering CI guard so function, model, table, global-parameter, API-contract, permission, component, prompt, dialog, script, and wrong-abstraction boundaries stay synchronized across principles, root routing, development skills, manifest routing, evaluation prompts, and live replay evidence.
- Added a development-defaults CI guard so full-stack best practices, necessary comments, high-cohesion/low-coupling modularity, backend-owned permission checks, frontend permission presentation, build/lint/test gates, Chinese commit format, and UI-only default frontend workflow routing stay synchronized across principles, root routing, development skills, manifest routing, and evaluation prompts.
- Added a loop-engineering CI guard so Loop Contract fields, dynamic workflow routing, max rounds/time/Token/subagent budgets, independent verifier requirements, stop conditions, and replay evidence stay synchronized across principles, root routing, workflow skills, manifest routing, evaluation prompts, and live replay evidence.
- Added a frontend-design-ecosystem CI guard so product-type classification, deterministic UI checks, DESIGN.md/Figma/Refero reference boundaries, website reconstruction authorization limits, manifest triggers, evaluation prompts, and live replay evidence stay synchronized.
- Added `check_human_voice_language_contract()` to `scripts/ci_validate_skills.py` so Simplified Chinese defaults, mixed-label cleanup, required English identifiers, manifest triggers, and replay evidence are validated together.
- Added `check_business_readable_output_contract()` to `scripts/ci_validate_skills.py` so business-facing outputs preserve problem, value, main work, cost/risk limits, collaboration roles, term explanations, and business-semantic naming across the root skill and output skills.

Current local checks passed:

- `python3 scripts/ci_validate_skills.py`
- `python3 scripts/run_eval.py`
- `python3 scripts/check_birth_certificate.py`
- `bash scripts/test_suite.sh`
- `git diff --check`
- `git diff --cached --check`
- `find . \( -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store' \) -print`
- `python3 scripts/security_scanner.py`
- Short-drama route live replay in Codex read-only mode passed and is recorded in `examples/quickstart-output.md`.

## Next Work Plan

### Before release action

- Re-run the full release gate on the intended release tree if any file changes before the release action.
- Confirm `git status --short` contains no unreviewed local changes.
- Confirm the intended tag and GitHub Release still point to the public-source-verified commit lineage.

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

## 2026-07-10 Long Goal Forge Evidence

- Two read-only baseline replays exposed the same missing boundary: one deferred an unresolved user/core-scenario decision into the execution prompt, while the urgency replay accepted `行业最好` without measurable success criteria.
- Guyue now separates Long Goal Forge from Long Goal Intake. Forge inspects project evidence, asks one direction-changing question per turn, creates the control pack, and requires an independent readiness review before a one-line handoff.
- `test-prompts.json` now contains 54 structural prompts, including vague-vision and urgency-pressure regression scenarios.
- The reusable control-pack schema lives in `docs/templates/long-goal-control-pack.md`; no overlapping routed child skill or new dependency was added.
- Concentrated repair added `scripts/check_long_goal_pack.py`: the master must explicitly list every phase-plan file, and the checker rejects unlisted phases, duplicate references, missing files, competing masters, and unresolved placeholders.
- `scripts/security_scanner.py` now scans tracked files plus unignored untracked files. A live untracked fake-key probe was blocked with exit code `1` and removed after the check.
- Decision-open Forge rounds now have a four-read plus one-status budget and forbid full gates before the next question. Codex pressure replay reduced measured input from `122480` to `51238` tokens and avoided all heavy gates, but remains `partial_pass` because the runtime still exceeded the requested per-file line cap and used one broad Markdown search.

## Explicit Non-Goals

- Do not add more skills beyond the reviewed extension and workflow set without a new manifest/test/release-evidence cycle.
- Do not add `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, or Cursor rules without the adapter admission gate.
- Do not publish to a marketplace, create a release tag, push commits, merge branches, or deploy without explicit user authorization.
- Do not hide local generated indexes or machine-path findings behind a release-ready label.

## Recheck Command Block

Run these commands from the repository root before release:

```bash
git status --short
git diff --check
python3 scripts/security_scanner.py
python3 scripts/check_long_goal_pack.py --self-test
python3 scripts/check_birth_certificate.py
bash scripts/test_suite.sh
```

The local and public-source release gates passed on the intended v1.3.0 lineage before that release. The authorization recorded here was consumed by that operation and grants no permission for a later commit, push, tag, release, marketplace listing, or deployment.

## Result Card

```text
┌─────────────────────────────────────┐
│  Historical Release · Guyue v1.3.0  │
│                                     │
│  Status: released historical proof  │
│  Focus: skill expansion boundaries  │
│  Verified: Codex + Claude install   │
│  Current use: historical only        │
│  Next step: none                     │
│                                     │
│  Reviewer: Luban                    │
└─────────────────────────────────────┘
```
