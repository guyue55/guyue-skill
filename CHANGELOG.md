# Changelog

## Unreleased

- No unreleased changes yet.

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
