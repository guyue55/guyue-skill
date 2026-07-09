# Changelog

## Unreleased

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
- Strengthen showcase validation so `assets/demo.gif`, `assets/demo.tape`, and `scripts/render_demo_gif.py` must be release-packaged assets, not local-only files.

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
