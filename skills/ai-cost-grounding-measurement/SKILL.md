---
name: ai-cost-grounding-measurement
description: Real AI report-cost measurement for model tokens, Grounding/web-search metadata, dynamic pages, CSV/Markdown evidence, and USD/CNY reporting. Use for actual standard/deep runs, billable search-query checks, or estimate-versus-real-call verification; not for generic pricing questions.
---

# ai-cost-grounding-measurement

## Core Job

Measure AI report cost with evidence. Do not present a dry-run estimate as a real run.

The key question is always: did the expensive capabilities actually execute, and can we prove it from artifacts or response metadata?

## Measurement Contract

Before running anything expensive, identify:

- target sites or inputs
- report tiers or versions
- crawl page limits
- dynamic rendering requirement
- AI execution flag
- Grounding or web-search requirement
- output format requested by the user
- timeout and progress expectations

If the user says "讨论成本，不开发", stay in analysis mode and do not run calls.

## Real-Run Workflow

1. Inspect existing scripts and output directories.
2. Run or review a dry-run first when the script supports it.
3. For real measurement, require visible progress and hard timeouts.
4. Ensure prompts force external-fact work when Grounding must be tested.
   - Enabling a search tool is not enough.
   - The prompt must ask for market, competitor, benchmark, or external evidence work that requires search.
5. Capture artifacts:
   - machine-readable JSON
   - human-readable CSV
   - concise Markdown summary when useful
6. Verify evidence before reporting.

## Evidence Checklist

A run is "real" only when the artifacts prove the relevant execution:

- `execute_ai` or equivalent is true.
- `estimated_model_calls` or equivalent estimate-only counter is zero when claiming real model cost.
- Usage metadata contains actual input/output token counts.
- Grounding/search metadata contains actual queries when claiming billable search usage.
- Wall-clock time is recorded or can be derived from logs.
- Crawl and dynamic-render page counts are present.
- Errors, skipped pages, or low-crawl sites are called out.

## Cost Breakdown

Keep these buckets separate:

1. model token cost
2. Grounding or search query cost
3. cloud/runtime/rendering estimate
4. total USD
5. CNY conversion only when requested or already part of the artifact

Do not call cloud-billing estimates exact. Label them as estimates unless backed by a provider billing export.

## Presentation Rules

- Honor the user's requested table shape exactly.
- For Chinese-facing CSV/Excel output:
  - use Chinese headers
  - map `standard` to `标准`
  - map `deep` to `深度`
  - keep JSON keys machine-oriented unless the user asks otherwise
- When the user asks for a compact table, put the compact table first and move caveats below it.
- Explain USD/CNY units when those columns appear.

## Failure Modes

- Grounding configured but zero actual queries.
- Sitemap or crawl failure causes undercounted pages and artificially low cost.
- Long real runs without progress make the user think the job is stuck.
- CSV localization breaks machine-readable JSON.
- Search query budget is planned but not reconciled against actual metadata.

## Validation

Use the project's existing test suite when available. Add or update small tests for:

- CSV headers and tier labels
- Grounding query extraction
- total cost aggregation
- estimate-vs-real run flags

## Anti-Patterns

- Do not infer real Grounding from a command-line flag alone.
- Do not collapse all costs into one number without components.
- Do not rerun expensive calls just to change CSV presentation when existing JSON can be re-exported.
- Do not hide crawl undercoverage.
- Do not overwrite raw measurement artifacts without preserving enough provenance to audit them.

## Cross-Skill Invocation

- Need official pricing or API docs -> `research-and-sourcing`.
- Need EAC static report/demo changes -> `eac-demo-hardening`.
- Need concise result doc -> `documentation`.
- Need repeated measurement SOP after success -> `sop-maker`.
