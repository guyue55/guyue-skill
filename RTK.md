# Guyue Runtime Kernel

`RTK.md` is the lightweight runtime entrypoint for coding agents working inside this repository. It is not a public Skill standard and is not required by all AI tools.

## Scope

- `SKILL.md` is the public Skill entrypoint.
- `README.md` is the human installation and product entrypoint.
- `skills_manifest.json` is the routing and capability map.
- `GUYUE_PRINCIPLES.md` is the shared discipline layer.
- `AGENTS.md` and `RTK.md` are repository-level coding-agent adapters.

## Source Of Truth Order

When working in this repository:

1. Follow system, developer, and user instructions first.
2. Read `AGENTS.md` when the runtime loads it.
3. Read this file for local runtime rules.
4. Read `SKILL.md` for the public Guyue orchestrator behavior.
5. Read `GUYUE_PRINCIPLES.md` for cross-skill discipline.
6. Read `skills_manifest.json` before choosing a child skill.
7. Read only the relevant child `skills/*/SKILL.md` file for the current task.
8. Use `README.md`, `docs/`, and `examples/` for installation, evidence, and public-facing context.

If any instruction conflicts with higher-priority instructions from the active runtime, follow the higher-priority instruction and mention the conflict in the final response.

## Runtime Discipline

- Keep context small. Use `rg`, `sed`, and targeted reads instead of dumping large files.
- Prefer the existing skill structure and docs conventions over new abstractions.
- Do not invent hidden capabilities. If a runtime does not support `AGENTS.md`, `RTK.md`, or nested skills, say so and fall back to `SKILL.md`.
- Do not write private paths, account names, tokens, API keys, cookies, or local machine details into tracked files.
- Do not add dependencies, install third-party skills, call external APIs, push, tag, release, deploy, or run destructive commands without explicit user authorization.
- Treat frontend, debugging, product, and system-design work as separate routed skills. Do not silently merge them into one generic answer.

## Required Checks

Before committing a repository change, run:

```bash
bash scripts/test_suite.sh
git diff --check
find . \( -name '__pycache__' -o -name '*.pyc' -o -name '.DS_Store' \) -print
python3 scripts/security_scanner.py
```

For runtime-entrypoint changes, also run one read-only live replay when feasible:

```bash
codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-runtime-replay.md "<prompt>"
```

Record notable live replay results in `examples/quickstart-output.md`.

## Boundaries

- This file does not replace `SKILL.md`.
- This file does not define a cross-vendor standard.
- This file does not grant permission to push, tag, release, deploy, or expose data externally.
- This file exists to make the repository self-contained for coding agents that support project instruction files.
