# New-User Six-Question Audit - 2026-07-12

## Scope

- Reviewer: independent read-only subagent
- Model: `gpt-5.6-luna`
- Mode: repository read-only
- Prohibited actions: file changes, tests, network research, commit
- Question set: who uses Guyue, why install it, how to trigger it, what it delivers, how it differs from adjacent forms, and how it is proved

## Verdict

`PASS`

1. **Who uses it**: people who rely on agents for complex engineering, cross-session recovery, multiple Skills/runtimes, and traceable acceptance. Evidence: `README.md` audience section.
2. **Why install it**: Guyue explicitly distinguishes itself from a temporary prompt and a single-task Skill through versioned routing, recovery ledgers, evidence contracts, and final sealing. Evidence: `README.md` form-comparison table.
3. **How to trigger it**: natural-language examples and machine-readable route/receipt entrypoints are both present. Evidence: `README.md` install and routing sections.
4. **What it delivers**: visible outputs include requirement boundaries, plans, RCA, SOPs, Long Goal control documents, installation receipts, and behavior evidence. Evidence: `README.md` output sections and Showcase.
5. **Where it is stronger**: Long Goal v4 adds control revisions, preserved failure evidence, approved recovery, and A/B/C Git sealing without adding another universal Skill. Evidence: the Long Goal v4 report and protocol.
6. **How it is proved**: Showcase, the candidate checklist, the hash-bound 2026-07-12 replay, and the exact candidate package agree. The replay asks one direction-changing question and does not emit a premature Goal handoff.

## Historical-Evidence Check

`v1.3.0` is explicitly marked as the published historical release in the README, historical release evidence, and release checklist. Its public install, tag, and remote CI proof no longer masquerade as evidence for the current unreleased v4 candidate.

## Residual Boundary

This audit did not run tests or repeat the model replay; it reviewed the public entrypoints and existing evidence chain. The live evidence proves one Codex clarification turn, not another runtime, a complete multi-turn Forge, or long-term user value.
