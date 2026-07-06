# Installation

This document keeps installation paths explicit. Use the path that matches your agent runtime, then run the local verification command before relying on the skill.

## Verify The Repository

From the repository root:

```bash
python3 scripts/install_guyue.py
bash scripts/test_suite.sh
```

This installs the small validation/runtime dependency set, automatically detects and installs optional enhancement skills from `skills_manifest.json`, runs the dependency doctor, then runs the zero-leakage scanner, SKILL.md validator, and test prompt evaluator.

## Optional Enhancement Skills

Guyue can discover optional third-party skills listed in `skills_manifest.json`, but optional dependencies are not required for the core skill to run.

The default installer already runs optional dependency installation:

```bash
python3 scripts/install_guyue.py
```

It installs every optional dependency declared in the manifest, including reviewed yellow/red dependencies, because running the top-level installer is treated as explicit installation intent.

Use the lower-level planner when you want to preview or audit optional skill changes before touching local skill directories:

```bash
python3 scripts/install_optional_dependencies.py
```

The default mode is a dry run. It scans local skill roots first, reports already installed skills, and prints the actions it would take without cloning or linking anything.

To install missing optional skills after reviewing the plan:

```bash
python3 scripts/install_optional_dependencies.py --install
```

Some optional skills contain shell helpers, command execution examples, or project layouts that are not a single `SKILL.md` directory. Those are intentionally stopped or adapter-mounted until you explicitly choose to proceed:

```bash
python3 scripts/install_optional_dependencies.py --install --force
```

For a conservative Guyue install that stops instead of force-installing yellow/red optional skills:

```bash
python3 scripts/install_guyue.py --optional-mode safe
```

For a plan-only optional dependency pass:

```bash
python3 scripts/install_guyue.py --optional-mode plan
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

Use a fresh Codex turn to confirm that the `guyue` root skill and child skills such as `coding-discipline`, `debugging-mindset`, and `frontend-expert` appear in the available skills list.

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

Install from the published skill source or copy the repository into your Claude skills/plugin workflow:

```bash
npx skills add guyue55/guyue-skill
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
