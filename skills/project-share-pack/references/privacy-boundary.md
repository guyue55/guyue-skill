# Customer Information Boundary

## Public Skill Rule

This Skill, its tests, examples, evaluation prompts, evidence, and release package
must remain project-neutral. Never copy material from a customer project into the
Guyue repository, including:

- customer, product, project, tenant, or account names;
- repository names, local absolute paths, domains, URLs, folder or document tokens;
- screenshots, reports, scores, recommendations, source code, configuration, or data;
- credentials, personal information, customer identifiers, or realistic sample records;
- generated replay output, browser captures, or model transcripts containing any of the above.

Use synthetic labels such as `示例项目`, `示例报告`, and `example.invalid` in reusable
fixtures. A sanitized customer artifact is still customer-derived; keep it in the
customer project unless the user explicitly approves a separate public-safe fixture.

## Working Boundary

Project facts may be read only to create that project's requested deliverables.
Keep generated briefs, denylist files, media plans, browser traces, and validation
reports inside the target project `tmp/` directory or the operating-system temporary
directory. Delete temporary copies created by this workflow after verification.

Do not place customer-derived live-canary prompts or audit artifacts in Guyue. Generic
activation prompts may prove routing; customer content must not be sent merely to
prove that the Skill works.

## Pre-Publication Check

Create a temporary denylist containing the customer and project names, repository
name, domains, sensitive URLs, known tokens, and distinctive internal terms. Do not
commit this file.

```bash
python3 <skill-root>/scripts/validate_share_pack.py \
  --document <share-root>/<topic>-方案.md \
  --deck <share-root>/ppt/index.html \
  --portable-deck <share-root>/ppt/index-feishu.html \
  --forbid-terms-file <temporary-denylist.txt>
```

The checker detects textual leakage and local-path traces. It cannot prove that text
inside an image is safe. Inspect every screenshot at original resolution for names,
accounts, URLs, identifiers, notifications, browser profiles, and hidden page areas.

Before completing Skill development, scan only the files changed for the Skill
against the same denylist. Do not print matching customer text into logs or final
reports; report the rule and affected artifact using redacted labels.
