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

Do not add `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, or `.cursor/rules/*` until there is a real user path and a read-only live replay proving that the target runtime loads the adapter as expected. Claude's plugin manifest is a package/discovery surface, not evidence that Claude reads `AGENTS.md` or a substitute for a project adapter.

## Current Runtime Matrix

Discovery, repository instructions, and payload installation are separate claims. “File exists” does not prove that a runtime advertised or activated it.

| Runtime | Discovery/package path | Repository adapter | Verified state | Caveat |
|---|---|---|---|---|
| Codex | Full-repository mount under a configured Skill root | `AGENTS.md` -> `RTK.md` | Root instructions and repository adapter have read-only replay evidence | Recheck discovery after changing Skill roots or symlinks; routed children may not be advertised separately |
| AGENTS.md-compatible agents | Runtime-specific project loading | `AGENTS.md` -> `RTK.md` | Adapter is structurally active | Each runtime must still prove it reads `AGENTS.md` |
| Claude Code | `.claude-plugin/marketplace.json` Skill bundle | No `CLAUDE.md` | Strict validation and isolated 27-component install were verified for v1.3.0 | Repeat public-source install for each release; plugin discovery does not imply `AGENTS.md` loading |
| Generic Agent Skills CLI | Runtime-defined Skill directory | None | Frontmatter is standards-compatible | Root-only installers can omit routed payload; require a full-repository mount and install receipt |
| Gemini CLI | Runtime Skill support plus optional `GEMINI.md` | Not present | Not live-verified | Add an adapter only after a real user path and replay |
| GitHub Copilot | Runtime Skill support and project instructions | Only `AGENTS.md` | Not separately live-verified | Do not claim Copilot-specific loading from repository structure alone |
| Cursor | Runtime Skill support and project rules | Only `AGENTS.md` | Not separately live-verified | Add `.cursor/rules/` only after a real user path and replay |
| Other Skill runtimes | `SKILL.md` plus full payload | None | Unknown until tested | Run `check_full_install.py --runtime generic --json` and a read-only activation replay |

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
