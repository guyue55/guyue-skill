# Installation

This document keeps installation paths explicit. Use the path that matches your agent runtime, then run the local verification command before relying on the skill.

## Verify The Repository

From the repository root:

```bash
bash scripts/test_suite.sh
```

This runs the zero-leakage scanner, dependency doctor, SKILL.md validator, and test prompt evaluator.

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

## Claude Code

Install from the published skill source or copy the repository into your Claude skills/plugin workflow:

```bash
npx skills add guyue55/guyue-skill
```

Then start a new Claude Code session and trigger it with:

```text
使用古月的思路帮我分析这个需求，先别写代码。
```

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
