# Installation

This document keeps installation paths explicit. Use the path that matches your agent runtime, then run the local verification command before relying on the skill.

## Verify The Repository

From the repository root:

```bash
python3 scripts/install_guyue.py
bash scripts/test_suite.sh
```

This installs the small validation/runtime dependency set, prints a dry-run plan for optional enhancement skills from `skills_manifest.json`, runs the dependency doctor, then runs the zero-leakage scanner, SKILL.md validator, MCP tests, and test prompt evaluator. The default command does not download or link third-party skills.

## Full-Package Contract

Guyue is one root orchestrator with repository-local principles, routed modules, scripts, docs, and optional MCP support. A complete installation must preserve the whole repository tree under one runtime skill directory.

Do not use `npx skills add guyue55/guyue-skill` as a full installation path. Current generic Skills CLI behavior intentionally installs only a root-level `SKILL.md`; the resulting directory omits files that the Guyue entrypoint references. Clone the repository, then link or copy that checkout into the skill directory supported by your runtime.

Verify the mounted directory itself before relying on it:

```bash
python3 /path/to/guyue/scripts/check_full_install.py /path/to/guyue
```

## Optional Enhancement Skills

Guyue can discover optional third-party skills listed in `skills_manifest.json`, but optional dependencies are not required for the core skill to run.

The default installer only plans optional dependency changes:

```bash
python3 scripts/install_guyue.py
```

It scans the manifest and local skill roots, reports what is already present, and prints proposed actions without cloning, downloading, or linking anything.

Use the lower-level planner when you want to preview or audit optional skill changes before touching local skill directories:

```bash
python3 scripts/install_optional_dependencies.py
```

The default mode is a dry run. It scans local skill roots first, reports already installed skills, and prints the actions it would take without cloning or linking anything.

To install green optional skills after reviewing the plan, while stopping on yellow/red findings:

```bash
python3 scripts/install_guyue.py --optional-mode safe
```

Some optional skills contain shell helpers, command execution examples, or project layouts that are not a single `SKILL.md` directory. Only after reviewing those findings should you explicitly allow every declared dependency:

```bash
python3 scripts/install_guyue.py --optional-mode all
```

The installer keeps third-party source checkouts under:

```text
~/.cc-switch/skills/_sources
```

Then it creates links from `~/.cc-switch/skills/<skill-name>` and `~/.codex/skills/<skill-name>` back to the single source location. This avoids multiple editable copies drifting apart.

## Codex

Codex discovers local skills from configured skill roots. Use your local checkout path as the source:

```text
/path/to/guyue
```

For a portable setup, link or copy the repository into your local Codex skills directory and restart the prompt session:

```bash
ln -s /path/to/guyue ~/.codex/skills/guyue
```

Use a fresh Codex turn to confirm that the `guyue` root skill appears and can resolve routed files such as `skills/coding-discipline/SKILL.md`, `skills/debugging-mindset/SKILL.md`, and `skills/frontend-expert/SKILL.md`. Do not assume every runtime advertises repository-local routed modules as separate top-level skills.

This repository also includes a minimal `AGENTS.md` and `RTK.md` for coding-agent runtime guidance. They are adapters, not public Skill standards:

- `SKILL.md` remains the public Skill entrypoint.
- `README.md` remains the human-facing entrypoint.
- `AGENTS.md` tells compatible coding agents to read `RTK.md`.
- `RTK.md` defines the local source-of-truth order, verification gates, and safety boundaries.

Cross-runtime adapter policy lives in [runtime-adapters.md](runtime-adapters.md). Do not add active `CLAUDE.md`, `GEMINI.md`, Copilot, or Cursor adapter files until that runtime has a real user path and a read-only live replay.

For a quick runtime check:

```bash
codex exec --ephemeral -C <repo-root> --sandbox read-only "使用古月的思路评估这个需求：我们要加一个支付模块。只分析，不写代码。"
```

## Claude Code

Use the repository's validated marketplace manifest for a complete plugin install:

```bash
claude plugin marketplace add guyue55/guyue-skill
claude plugin install guyue@guyue
claude plugin details guyue@guyue
```

Before publication, `claude plugin validate --strict .` and an isolated local marketplace install must pass. After the candidate is pushed, repeat the same install from the public GitHub source before tagging the release.

The source checkout path remains available when you want to develop or customize Guyue:

```bash
git clone https://github.com/guyue55/guyue-skill.git /path/to/guyue
```

Then start a new Claude Code session and trigger it with:

```text
使用古月的思路帮我分析这个需求，先别写代码。
```

Claude Code has its own project memory conventions. If you need persistent Claude-specific guidance, mirror the small runtime-entrypoint summary into `CLAUDE.md` instead of assuming Claude will load `AGENTS.md` or `RTK.md`.

When adding `CLAUDE.md`, keep it as a thin adapter to `RTK.md`; do not copy the full runtime rules.

## MCP Clients

Use the MCP server when you want the agent to read the skill manifest or use the local memory bank through tools.

```json
{
  "mcpServers": {
    "guyue": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "mcp_server.py"],
      "cwd": "/path/to/guyue/src"
    }
  }
}
```

Replace `/path/to/guyue/src` with the absolute path to your checkout's `src` directory.

## VS Code And GitHub Copilot

Agent Skills are directory-based. The skill directory must contain `SKILL.md`, and the frontmatter `name` should match the directory name. For a workspace-level setup, copy or link this repository into the workspace skill directory supported by your VS Code/Copilot configuration.

After installation, review `SKILL.md` before enabling script execution. Keep terminal auto-approval narrow and avoid broad shell allow-lists.

GitHub Copilot and Cursor have their own repository instruction mechanisms. Keep `SKILL.md` as the canonical Skill asset and only copy the runtime-entrypoint summary into those tool-specific instruction files when needed.

If a Copilot or Cursor adapter is added, it must pass the adapter admission gate in [runtime-adapters.md](runtime-adapters.md).

## OpenClaw

For a local install:

```bash
openclaw skills install /path/to/guyue --as guyue
```

Before installing any third-party dependency suggested by `ecosystem-scout`, inspect its `SKILL.md`, source repository, and security scan results. Do not install unknown skills globally until they have been reviewed.

## First Run Prompt

Use this prompt to verify behavior without touching project files:

```text
使用古月的思路评估这个需求：我们要加一个支付模块。只做需求边界和风险分析，不写代码。
```

Expected behavior:

- The agent pauses instead of writing code immediately.
- The agent routes to requirement analysis, research, and system design concerns.
- The agent names missing business/security details and asks for confirmation before implementation.
