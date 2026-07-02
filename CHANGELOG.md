# Changelog

## Unreleased

### Changed

- Reposition Guyue as a Personal Agent Operating Layer rather than a complete autonomous person.
- Align the README with the current productization goal: installation, visible output, safety boundaries, and evaluation.
- Add public-facing docs for installation, security, evaluation, and release readiness.
- Tighten `debugging-mindset` so retry code is blocked until logs, metrics, error type, and idempotency boundaries are available.
- Tighten `ecosystem-scout` so external skills are vetted through official sources and public manifests never store machine-local paths.

### Added

- Add `docs/release-candidate.md` to freeze the current productization baseline, evidence gate, blockers, and next work plan.
- Add `AGENTS.md` and `RTK.md` as lightweight coding-agent runtime entrypoints.
- Add `docs/runtime-adapters.md` to define cross-runtime adapter policy without enabling extra tool-specific entrypoints.
- Add a structural evaluator for `test-prompts.json`.
- Add `ecosystem-scout` as the lightweight intake path for external skills and tools.
- Add `scripts/discover_local_skills.py` for local-only skill path discovery, with generated indexes excluded from public release artifacts.
- Add Codex read-only live replay evidence under `examples/quickstart-output.md`.

### Verification

- Run `bash scripts/test_suite.sh` before release or commit.
- Replay three quickstart prompts in Codex read-only mode and record one `partial_pass` debugging boundary deviation.
