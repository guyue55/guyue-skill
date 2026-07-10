# Evaluation

Guyue is a workflow skill suite. Evaluation focuses on whether the agent follows the intended discipline, not whether it gives a single fixed answer.

## Local Evaluation Command

Run:

```bash
python3 scripts/run_eval.py
```

The evaluator checks `test-prompts.json` for:

- valid JSON structure;
- unique test names;
- non-empty user prompts;
- non-empty expected behavior;
- coverage for every registered skill in `skills_manifest.json`;
- coverage for the core safety disciplines: trace logging, human approval, research before action, controlled debugging, and memory write behavior.

Use the full suite before a commit:

```bash
bash scripts/test_suite.sh
```

The full suite also runs `python3 scripts/check_birth_certificate.py`, a release-readiness check that verifies the public entrypoint, install path, trigger surface, visible evidence links, safety boundaries, and current skill/prompt counts stay synchronized.

## Current Test Categories

`test-prompts.json` currently covers:

- root orchestration;
- 长线目标铸造、逐项澄清、一行交接、long Goal intake、execution-ledger recovery、stale-evidence refusal；
- debugging discipline;
- system design and human confirmation;
- documentation;
- business-readable output;
- research and sourcing;
- coding discipline, reuse-first engineering, and development defaults;
- loop engineering and dynamic workflow routing;
- frontend expert behavior;
- frontend design ecosystem boundaries;
- SOP generation;
- memory bank;
- product sense;
- skill crafting;
- ecosystem scout;
- security gate;
- server-side permission boundary review;
- website reconstruction;
- software advising;
- UI taste review;
- code minimalism and duplicate-code reduction;
- book distillation;
- video extraction;
- video creation and short-drama stage gates;
- context compression, context budget management, and third-party quick-install gates;
- reality auditing;
- NexusFlow governance workflow;
- EAC demo hardening;
- AI cost and Grounding measurement.

`ecosystem-scout` must stay covered because it controls external dependency intake.

## Pass Criteria

A release candidate passes evaluation when:

- every prompt has an expected behavior statement;
- each registered skill has at least one matching test prompt or explicit manifest coverage;
- safety-related tests require a pause, refusal, confirmation, or source check where relevant;
- vague long-goal replay inspects project evidence before asking exactly one direction-changing question, while urgency cannot force a premature handoff;
- ready long-goal replay creates or identifies the complete control pack and returns one physical handoff line without unresolved questions;
- the full `bash scripts/test_suite.sh` exits with status code `0`;
- `scripts/check_birth_certificate.py` confirms the public release assets are present and synchronized;
- the report does not contain missing skills or duplicate prompt names.

## Dry Run Versus Live Run

`scripts/run_eval.py` is a structural evaluator. It does not call an LLM and does not prove output quality by itself.

Live evaluation means replaying the prompts in a real agent session and saving the observed outputs under `examples/` or a release report. Mark structural checks as `dry_run`; mark real agent replay results as `live_run`.

## Live Replay Evidence

Current quickstart replay evidence lives in [../examples/quickstart-output.md](../examples/quickstart-output.md).

Use a read-only runtime when collecting replay output:

```bash
codex exec --ephemeral -C <repo-root> --sandbox read-only -o /tmp/guyue-replay-root.md "<prompt>"
```

Record both passes and deviations. For example, if the runtime follows Guyue's debugging trace but still emits concrete retry code before raw logs are available, mark it as `partial_pass` and convert it into a follow-up boundary fix.

Security-gate live runs must be strict about target admission: if the prompt says only "this third-party skill" but provides no path, URL, package name, or archive path, the correct result is to ask for the target and stop. Inferring a local skill directory is a replay deviation and must be fixed before release.

Runtime-entrypoint changes must also confirm that the agent no longer reports missing project instruction files such as `RTK.md`. Record that result in the live replay evidence.

Runtime adapter changes must follow [runtime-adapters.md](runtime-adapters.md):

- keep adapters thin and point them back to `RTK.md`;
- run the local validation suite;
- run a read-only live replay in the target runtime when feasible;
- remove the adapter before commit if the runtime does not load it or if it creates duplicated/conflicting instructions.

## Release Evidence Template

Release-candidate evidence and current blockers are tracked in [release-candidate.md](release-candidate.md). Update that file before a release tag or marketplace submission.

Use this template when preparing a release:

```markdown
## Evaluation Evidence

- Date:
- Commit:
- Command: `bash scripts/test_suite.sh`
- Result:
- Live prompts replayed:
- Deviations:
- Follow-up fixes:
```
