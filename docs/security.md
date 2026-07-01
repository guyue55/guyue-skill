# Security Boundaries

Guyue is designed to reduce agent risk, not to bypass human approval. Treat every skill, script, MCP server, and external dependency as part of the agentic supply chain.

## Non-Negotiable Boundaries

- Do not execute unknown installation scripts from a third-party repository.
- Do not copy third-party README files or source trees into `skills/` just to make the agent "know more".
- Do not store API keys, tokens, cookies, private SSH keys, or personal account details in examples, tests, or docs.
- Do not publish, tag, push to a marketplace, or deploy without an explicit user command.
- Do not let an agent rewrite `SKILL.md` or `skills_manifest.json` from a vague suggestion; require a visible proposal and approval.

## External Skill Intake

`ecosystem-scout` exists to keep external tool intake lightweight and reviewable.

Required flow:

1. Search for the tool or skill and at least one comparable alternative.
2. Produce a short evaluation artifact that explains the use case, dependency cost, risks, and fit.
3. Stop for approval.
4. If approved, register only a lightweight dependency pointer in `skills_manifest.json`.

Allowed registry fields:

```json
{
  "name": "tool-name",
  "description": "short purpose",
  "package_id": "owner/repo-or-unique-id",
  "command": "install command",
  "url": "official source"
}
```

Do not import the whole external skill into this repository unless the user explicitly asks for vendoring and accepts the maintenance burden.

## MCP And Script Execution

MCP servers and scripts can expose local files, shell commands, credentials, and network access. Keep them scoped.

- Prefer workspace-level installs over global installs.
- Prefer read-only tools unless write access is required.
- Review every new script before adding it to `scripts/`.
- Keep script dependencies explicit and minimal.
- Run `python3 scripts/security_scanner.py` before every commit.

## Approval Points

The agent must stop before:

- Deleting files or directories.
- Installing external skills globally.
- Running unknown shell commands copied from a website.
- Writing credentials or environment files.
- Pushing code, creating releases, publishing packages, or submitting marketplace entries.
- Changing the public positioning of the project in a way that implies the skill is a full autonomous person.

## Commit Gate

Before committing:

```bash
python3 scripts/security_scanner.py
python3 scripts/doctor.py
python3 scripts/ci_validate_skills.py
python3 scripts/run_eval.py
```

`scripts/test_suite.sh` runs the same gate as a single command.
