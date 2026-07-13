# Changelog

## v1.4.0 - 2026-07-13

### Added

- Add a machine-readable capability-chain gate covering 54 broad routes, 345 internal triggers, 208 adjacent negative cases, 48 external-candidate triggers, 26 evidence profiles, and 26 hash-bound Codex activation canaries.
- Add E1 decision, E2 change, E3 lineage, and E4 audit evidence profiles with a shared envelope, failure-first representative output replay, and explicit non-claims for all-domain output quality, other runtimes, and public-network proof.
- Add one realistic synthetic output task and an independent review for every one of the 26 child Skills, retaining output, producer, review, failure history, and SHA-256 evidence artifacts.
- Add compact sanitized activation artifacts for all 26 Codex canaries so target Skill reads and final selections can be independently checked without publishing model reasoning or full raw event streams.
- Add Long Goal control-pack schema v4 with authority and inheritance rules, ultimate/current/time-only horizons, verified-fact/frozen-decision/hypothesis/experiment registers, recoverable three-failure design review, bidirectional promise/evidence links, and an auditable A/B/C Git seal; retain tested v2/v3 parsing compatibility.
- Add a versioned routing lifecycle plus 19 machine-readable behavior contracts, including hash-bound one-turn and multi-turn Long Goal Forge replays, deterministic route explanations, project-context gates, and an MCP route tool.
- Add disposable external-project Long Goal lifecycle and empty-HOME Git-clone install simulators with machine-readable receipts, restart checks, clean-install verification, and explicit public-network/user-value boundaries.
- Add `scripts/check_behavior_replay.py` to bind reviewed live observations to evidence files and SHA-256 hashes.
- Add `scripts/codex_extractor.py` with cwd/time-window/thread-source/keyword/role filters, deduplication, inventory mode, bounded output, statistics, and credential/home-path redaction.
- Add Long Goal control-pack schema v3 with stable IDs, promise coverage, replay classes, version-bound approvals, delegation ownership/BASE/report/review/convergence contracts, and artifact-hash-bound completion evidence; retain v2 parsing compatibility.
- Add a context-budget gate for discovery metadata, routing metadata, Unicode root size, UTF-8 byte size, activated Skill bodies, and route collisions.
- Add a frozen 52-repository ecosystem research ledger with exact source commits and per-project adoption or rejection decisions.
- Add `scripts/try_guyue.py`, a read-only 30-second first proof for package completeness, explainable routes, project gates, context budgets, and honest activation boundaries.
- Add memory schema v2 with public/private storage separation, provenance, scope, evidence, confidence, supersession, review timing, and lossless archive GC.
- Add machine-readable full-install receipts with runtime-specific payload checks and required-payload SHA-256.
- Add Ruff static analysis to the main validation suite.

### Changed

- Change 12 optional ecosystem entries from documentation-only pointers into source-pinned `external_candidates`; they cannot enter built-in selected routes or activate before source, installation, security, and action-specific authorization gates.
- Strengthen product, human-voice, software-advisor, security-gate, book-distiller, SOP, and ecosystem contracts so facts, assumptions, rewrite drift, catalog provenance, scan receipts, source locations, and discoverability remain auditable.
- Strengthen seven Skills from real output-review failures: provisional acceptance criteria, closed-world documentation facts, unverified ecosystem metadata, measured context baselines and stop conditions, media checksums and provenance, unresolved audio decisions, and four-state deployment evidence.
- Give Guyue an evidence-bound independent-judgment contract: challenge user-proposed means and its own prior control plan when they conflict with the user outcome, while requiring facts, impact, a recommendation, and a falsification condition instead of performative disagreement.
- Separate the published v1.3.0 proof from the unreleased Long Goal v4 candidate across the README, release evidence, checklist, showcase, and installation claims so historical green gates cannot masquerade as current proof.
- Calibrate Guyue autonomy by evidence level and reversibility: bounded repository work proceeds without duplicate approval, while public, paid, destructive, permission-changing, or irreversible actions require action-specific authorization.
- Reduce routed description size from 7234 to 5790 characters and define positive/negative routes for ambiguous and project-specific skills.
- Replace per-command Trace logging with one takeover trace plus meaningful state/risk transitions.
- Replace zero-dependency and fixed-age dogma with lifecycle-cost dependency stewardship; prefer proven libraries for parsers, auth, crypto, protocols, media, and domain engines.
- Rewrite `skill-crafting` around packaging-form selection, existing-capability reuse, evidence intake boundaries, with/without baselines, holdout cases, repeated replay, and installation truth.
- Make research conditional on unstable, unfamiliar, high-stakes, explicit, or decision-critical facts; stable local facts use direct inspection.
- Make system-design approval risk-tiered, documentation format audience-driven, debugging evidence minimally sufficient, website reconstruction existing-stack-first, and video extraction mode-specific.
- Pin every optional external dependency to a reviewed commit and verify existing local Skills against both exact HEAD and origin before linking.
- Expand the security preflight from a 200-file sample to all eligible files, reject empty targets, centralize credential patterns, and prevent allow-marker bypass in production scans.
- Separate curated public memory from ignored local runtime memory and remove the dangling tracked active-memory entry from the release payload.
- Update README, installation, runtime matrix, security, evaluation, Long Goal, and release-checklist documentation for the new contracts.
- Move README's first visible result ahead of the architecture catalog, and replace the stale narrative showcase/VHS script with the real first-run proof and current behavior contracts.

### Fixed

- Fix the 54-prompt suite passing without sending its broad prompts through the deterministic router, and fix natural-language misses across all 26 built-in Skills.
- Fix negated project context such as “无 NexusFlow/EAC 标记” activating project-specific workflows, and fix EAC's own `Demo/index.html` trigger being rejected by its context gate.
- Fix a duplicate `replay` dictionary key in the CI validator.
- Fix Long Goal's previous false-green self-test that accepted blank ledger, evidence, and phase files.
- Fix memory writer/GC directory disagreement and prevent GC from truncating archived lessons.
- Fix project-specific NexusFlow and EAC skills being eligible from generic permission, dashboard, static-demo, PDF, or GSAP terms.
- Fix `video-extractor` requiring `video.mp4` even in metadata-only mode.
- Fix the context-budget gate counting UTF-8 bytes as characters for Chinese root instructions.
- Fix Long Goal completion evidence accepting a fresh label without recomputing the referenced artifact SHA-256.
- Fix the Long Goal CLI being bound to the Guyue repository by adding a validated `--repo-root` target, and allow honest `dirty@...` ATTEMPT provenance while continuing to require `clean@A` for completed FINAL evidence.
- Fix the full-package receipt omitting the router and context modules required by the public first-run command.
- Fix showcase examples that still encoded blanket research, blanket refusal, multi-question interrogation, and fabricated memory output from earlier Guyue behavior.
- Fix route-contract validation accepting any one expected route instead of requiring the complete expected route set.
- Fix read-only route-audit prompts treating project names in the audit question as verified NexusFlow or EAC context.

### Verification

- Pass the expanded 15-stage local suite, Ruff, strict Claude marketplace validation, all 26 official `skills-ref` child validations, security failure injection, Long Goal delegation/staleness/hash failure injection, memory/MCP route tests, Codex extractor tests, deterministic route tests, context-budget tests, and behavior-replay checker tests.
- Pass 26/26 retained Codex activation canaries and 26/26 independently reviewed synthetic output tasks after preserving 18/26 and 24/26 failed attempts and repairing their concrete causes.
- Pass a continuous external-repository Long Goal simulation covering ready state, three differentiated failures, design-review blocking, approved revision recovery, A/B/C sealing, restart replay, and rejection of post-seal mutation.
- Pass a real local bare-remote Git clone into an empty HOME, installed-package validation, first run, lifecycle execution, restart identity, and clean-worktree verification; public-network installation and real-user feedback remain unverified.
- Record the initial post-upgrade Codex replay as `blocked_before_model` due account usage limits and the Claude fallback as `blocked_before_model` because the local CLI was not logged in.
- After quota became available, pass a fresh Codex read-only route-audit replay, use it to expose and fix incomplete expected-route validation plus project-name meta-question pollution, then bind the reviewed evidence to SHA-256. This covers 1 of 17 behavior contracts, not all model behavior or every runtime.

## v1.3.0 - 2026-07-10

### Added

- Add five evidence-heavy workflow skills: `video-creation-sop`, `reality-auditor`, `nexusflow-governance-workflow`, `eac-demo-hardening`, and `ai-cost-grounding-measurement`.
- Add `human-voice` as a plain-language gate for "说人话" and anti-AI-slop expression rewrites.
- Add evaluation prompts covering the new workflow skills.
- Add route-boundary evaluation prompts for overlapping skills.
- Add a CI guard for `video-creation-sop` short-drama contract completeness.
- Add a CI guard for the `human-voice` language contract across principles, routing, manifest, tests, README, and live replay evidence.
- Add a CI guard for business-readable output across persona principles, root routing, output skills, manifest, and evaluation prompts.
- Add a CI guard for the `context-compressor` context-budget and third-party quick-install contract across Skill instructions, manifest routing, and evaluation prompts.
- Add a CI guard for reuse-first engineering across persona principles, root routing, development skills, manifest routing, and evaluation prompts.
- Add a CI guard for full-stack default development discipline covering best practices, modularity, backend-owned permissions, frontend permission presentation, validation gates, Chinese commit format, and UI-only default frontend workflow routing.
- Add a CI guard for Loop Engineering and dynamic workflow routing across persona principles, root routing, workflow skills, manifest routing, evaluation prompts, and live replay evidence.
- Add a CI guard for frontend design ecosystem routing across frontend-expert, taste-aesthetics, ai-website-cloner, manifest routing, evaluation prompts, README, and live replay evidence.
- Add a Long Goal Forge regression gate and reusable control-pack template covering vague-goal interrogation, decision closure, planning assets, independent readiness review, and one-line execution handoff.
- Add a Long Goal control-pack checker that rejects unlisted phases, missing references, competing masters, and unresolved placeholders.
- Add a full-install payload checker that rejects root-only installs and verifies every routed skill remains present.
- Add focused MCP memory tests for empty queries, secret/path refusal, rapid-write uniqueness, and keyword retrieval.

### Changed

- Expand `documentation` with a code-backed project-orientation mode.
- Expand `documentation` project orientation with repo-cartographer evidence, source-of-truth, and worktree-risk checks.
- Expand `reality-auditor` with deployment/release reality verification.
- Expand `coding-discipline` with dirty-worktree commit-boundary rules.
- Expand `skill-crafting` with local Skill intake verification and release-candidate / zero-leakage lanes.
- Expand `video-creation-sop` with short-drama stage gates, structured brief JSON, style retrieval, visual-bible, audio-plan, storyboard timeline math, keyframe, shot-video, continuity evidence, compose/export, run-audit, and production-dossier contracts.
- Distill recent release-readiness, live replay, human-voice, and dirty-worktree lessons into Guyue's shared persona DNA.
- Strengthen `scripts/ci_validate_skills.py` so public Markdown links and code-spanned Skill resource references must resolve to tracked or staged release files.
- Update the README skill matrix from 20 to 25 routed skills.
- Update the README skill matrix from 25 to 26 routed skills with a dedicated human-voice boundary.
- Add public routing-arbitration rules and clarify adjacent-skill boundaries across `SKILL.md`, `README.md`, and `skills_manifest.json`.
- Strengthen Guyue's human-voice persona contract so plain-language output must preserve facts, sources, authorship, authorization, and risk boundaries without marketing exaggeration.
- Strengthen Guyue's language contract so normal communication defaults to Simplified Chinese when unspecified and removes unnecessary Chinese-English mixed labels while preserving required identifiers.
- Strengthen `scripts/ci_validate_skills.py` so the human-voice language contract cannot drift silently across public docs and release evidence.
- Strengthen Guyue's business-facing output contract so方案、文档和汇报 explain business problem, user value, main work, cost/risk limits, collaboration roles, and first-use term meanings.
- Strengthen `context-compressor` from a file/log compression tactic into a context budget manager covering token-waste diagnosis, MCP tool schemas, tool outputs, repository maps, docs, long sessions, controlled third-party quick installs, and measured-or-marked savings.
- Strengthen `ecosystem-scout` so third-party quick-install assistance requires source checks, an install plan, explicit authorization, foreground execution, smoke tests, and post-use evidence.
- Strengthen Guyue's full-stack development defaults so frontend, backend, data, script, configuration, infrastructure, and documentation implementation work preserves the original goal of lower barriers, better experience, Simplified Chinese by default, backend authorization boundaries, frontend permission presentation, and explicit build/lint/test evidence before commit.
- Strengthen Guyue's development persona so architecture and coding start with reuse scanning, second use triggers abstraction, and common functions, models, tables, constants, global parameters, API contracts, dialogs, prompts, scripts, formatters, and permission checks have a single authoritative entry.
- Strengthen Guyue's Loop Engineering posture so repeated manual Agent work is packaged with stable inputs, loop bodies, independent checkers, stop conditions, max rounds/time/Token/subagent budgets, and asset-deposition choices instead of becoming an unbounded new skill.
- Strengthen Guyue's frontend design posture so `frontend-design`, `taste-skill`, Impeccable, `DESIGN.md`, Refero, Figma, html.to.design, GSAP skills, and website cloning tools are routed by product type, design-reference safety, deterministic UI checks, and authorization boundaries instead of becoming another frontend mega-skill.
- Strengthen Guyue's long-goal posture by separating preparation from execution: inspect project evidence first, confirm one direction-changing decision per turn, block urgency-driven vague goals, then create the control pack before returning a one-line Goal entrypoint.
- Bound decision-open Long Goal clarification rounds to targeted evidence reads, and extend Zero-Leakage scanning to unignored untracked files before staging.
- Strengthen showcase validation so `assets/demo.gif`, `assets/demo.tape`, and `scripts/render_demo_gif.py` must be release-packaged assets, not local-only files.
- Align every child Skill frontmatter with the public Agent Skills field set and official name/description constraints.
- Change optional enhancement installation from force-install-by-default to plan-only-by-default, with explicit `safe` and `all` modes.
- Replace the incomplete root-level generic CLI installation claim with a verified full-repository mount contract.
- Make frontend guidance product-type-first and existing-stack-first; GSAP, Tailwind, glass effects, asymmetry, and conversion claims are conditional rather than defaults.
- Harden the optional MCP memory layer with bounded queries, common secret/path detection, collision-resistant filenames, and atomic index replacement.
- Replace the invalid custom Claude marketplace object with the official skill-bundle schema and verify a complete 27-component isolated installation.
- Run the complete GitHub CI release gate twice on both `dev` and `main` pushes so cache pollution and non-idempotent checks cannot hide behind a single green run.
- Upgrade GitHub CI to the Node 24-native `actions/checkout@v6` and `actions/setup-python@v6`, and lock both majors in project configuration validation.
- Bound Python dependencies to compatible major versions (`mcp` 1.x and PyYAML 6.x); the release candidate was exercised with mcp 1.28.1 and PyYAML 6.0.3 on Python 3.11.
- Accept both template-style and code-spanned Long Goal control paths, with regression coverage for each form.
- Let the birth-certificate gate validate either a matching release-candidate certificate or the matching final release certificate.

### Verification

- Pass the complete release suite twice on both `dev` and `main` GitHub CI with no check-run annotations after the Node 24 action upgrade.
- Install `guyue@guyue` 1.3.0 from the public GitHub marketplace in an empty `HOME`, verify all 27 Skill components and the complete repository payload, then pass the installed-cache release suite twice.

## v1.2.0 - 2026-07-02

### Changed

- Reposition Guyue as a Personal Agent Operating Layer rather than a complete autonomous person.
- Align the README with the current productization goal: installation, visible output, safety boundaries, and evaluation.
- Add public-facing docs for installation, security, evaluation, and release readiness.
- Tighten `debugging-mindset` so retry code is blocked until logs, metrics, error type, and idempotency boundaries are available.
- Tighten `ecosystem-scout` so external skills are vetted through official sources and public manifests never store machine-local paths.
- Mark newly indexed ecosystem skills as optional dependencies so local validation does not fail when optional tools are absent.
- Replace unsafe "direct external skill execution" wording with controlled invocation, safety preflight, and explicit approval gates.
- Tighten `security-gate` so missing targets stop for clarification instead of inferring or scanning a local skill directory.

### Added

- Add eight routed extension skills: `security-gate`, `ai-website-cloner`, `software-advisor`, `taste-aesthetics`, `code-minimalism`, `book-distiller`, `video-extractor`, and `context-compressor`.
- Add release evaluation prompts covering every new routed extension skill.
- Add `docs/release-candidate.md` to freeze the current productization baseline, evidence gate, blockers, and next work plan.
- Add `AGENTS.md` and `RTK.md` as lightweight coding-agent runtime entrypoints.
- Add `docs/runtime-adapters.md` to define cross-runtime adapter policy without enabling extra tool-specific entrypoints.
- Add a structural evaluator for `test-prompts.json`.
- Add `ecosystem-scout` as the lightweight intake path for external skills and tools.
- Add `scripts/discover_local_skills.py` for local-only skill path discovery, with generated indexes excluded from public release artifacts.
- Add Codex read-only live replay evidence under `examples/quickstart-output.md`.

### Verification

- Run `bash scripts/test_suite.sh` before release or commit.
- Replay quickstart prompts in Codex read-only mode and record both fixed deviations and current security-gate target-boundary evidence.
