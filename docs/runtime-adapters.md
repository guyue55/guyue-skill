# Runtime Adapters

Guyue should stay portable without letting runtime-specific instruction files drift apart. This document defines the adapter strategy for Codex, Claude Code, Gemini CLI, GitHub Copilot, Cursor, and adjacent coding-agent runtimes.

## Decision

Use one canonical runtime kernel and keep every tool-specific file as a thin adapter.

```text
SKILL.md        public Skill entrypoint
README.md      human-facing product and installation entrypoint
RTK.md         repository runtime kernel for coding agents
AGENTS.md      currently active thin adapter
```

Do not add `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, or `.cursor/rules/*` until there is a real user path and a read-only live replay proving that the target runtime loads the adapter as expected.

## Current Adapter Matrix

| Runtime | Native instruction file | Current repository state | Policy |
|---|---|---|---|
| Codex | `AGENTS.md` plus `SKILL.md` for Skills | Active `AGENTS.md` points to `RTK.md` | Keep active. Codex live replay already proved `RTK.md` loads. |
| AGENTS.md-compatible agents | `AGENTS.md` | Active | Keep short. Do not duplicate `RTK.md`. |
| Claude Code | `CLAUDE.md`, `.claude/rules/` | Not present | Add only when Claude Code is a verified distribution target. |
| Gemini CLI | `GEMINI.md` | Not present | Add only when Gemini CLI is a verified distribution target. |
| GitHub Copilot | `.github/copilot-instructions.md`, `AGENTS.md` for coding agent flows | Not present except `AGENTS.md` | Prefer `AGENTS.md` first. Add Copilot file only for GitHub-native workflows. |
| Cursor | Project/User Rules, AGENTS.md support in recent docs | Not present except `AGENTS.md` | Add `.cursor/rules/` only for Cursor-specific users. |
| OpenClaw / other Skill runtimes | `SKILL.md` | Active | Keep `SKILL.md` canonical. |

## Thin Adapter Rule

Every runtime-specific adapter must be under 20 lines unless a live replay proves more context is necessary. It must point back to `RTK.md` and must not copy the full rules.

Template:

```markdown
# <RUNTIME>.md

This file is a thin adapter for <runtime>.

Canonical entrypoints:
1. `RTK.md`
2. `SKILL.md`
3. `GUYUE_PRINCIPLES.md`
4. `skills_manifest.json`

Do not duplicate runtime rules here. If this file conflicts with `RTK.md`, treat `RTK.md` as the repository runtime kernel unless the active tool's system instructions say otherwise.
```

## Adapter Admission Gate

Before adding a new active adapter file:

1. Confirm the target runtime has a real expected user path.
2. Read the runtime's current official documentation.
3. Add the thinnest possible adapter.
4. Run local validation:

   ```bash
   bash scripts/test_suite.sh
   git diff --check
   python3 scripts/security_scanner.py
   ```

5. Run one read-only live replay in the target runtime or document why it is unavailable.
6. Record the result in `examples/quickstart-output.md`.
7. If the adapter does not load or causes duplicated/conflicting instructions, remove it before commit.

## Anti-Patterns

- Do not keep full copies of `RTK.md` in `CLAUDE.md`, `GEMINI.md`, Copilot, or Cursor files.
- Do not create adapters for tools that no one has asked to use.
- Do not assume one runtime reads another runtime's file.
- Do not hide high-risk permissions, install commands, push/release rights, or secrets in adapter files.
- Do not add tool-specific adapters in the same commit as unrelated Skill behavior changes.

## References

- Codex `AGENTS.md`: https://developers.openai.com/codex/guides/agents-md
- Codex Skills: https://developers.openai.com/codex/skills
- AGENTS.md open format: https://agents.md/
- Claude Code memory: https://code.claude.com/docs/en/memory
- Gemini CLI context files: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
- GitHub Copilot custom instructions: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
