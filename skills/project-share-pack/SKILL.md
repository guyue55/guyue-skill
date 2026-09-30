---
name: project-share-pack
description: "Create or refresh an evidence-based, business-readable project or requirement sharing pack: a web PPT, an independent Markdown solution document, verified screenshots, and optional Feishu Drive publishing. Use when the user wants these deliverables together; use documentation, a PPT skill, or lark-cli directly for single-format work."
---

# project-share-pack

## Core Job

Turn current project or requirement evidence into one coherent sharing package:

1. a concise web PPT for live explanation;
2. an independent Markdown document for later reading;
3. clear, complete screenshots that prove the main experience;
4. optional publication to a user-specified Feishu Drive folder.

This is an orchestration skill. Reuse the active `documentation` capability for the document, the installed PPT capability such as `guizang-ppt-skill` for the deck, and version-matched `lark-cli` skills for Feishu. Do not copy their templates or API manuals into this skill.

## Trace

On takeover, emit once:

`[Trace: Guyue/project-share-pack] 核对项目事实，生成统一口径的网页 PPT 与独立方案文档；飞书发布仅在明确授权后执行并在线回读。`

## Route Boundary

Use this skill when the user asks for at least two connected outputs, for example:

- “给这个项目做一套可分享的 PPT 和方案文档”
- “把需求整理成分享材料，并上传到飞书”
- “更新现有项目介绍，PPT、文档和截图一起刷新”
- “一次生成项目分享包，减少人工整理”

Do not use it when:

- only a README, PRD, report, or solution document is needed: use `documentation`;
- only an existing deck needs visual editing: use the active PPT skill;
- only an already prepared file must be uploaded: use version-matched `lark-cli` Drive/Docs guidance;
- the user asks for a marketing landing page or a normal product UI, not a presentation pack;
- there is no stable source material and the user only wants brainstorming: first clarify or create a marked draft, never present assumptions as project facts.

## Stable Inputs

Discover from the workspace before asking:

- source project, requirement, or supplied materials;
- current truth sources and working-tree state;
- share goal, intended readers, and approximate duration;
- required and forbidden content;
- output location and existing pack to refresh;
- screenshot source and privacy boundary;
- optional Feishu folder URL/token and overwrite policy.

Ask only for missing information that changes the story, privacy boundary, or external write. If the repository and prior pack already answer the question, continue without ceremony.

## Output Contract

Default package:

```text
<share-root>/
├── <topic>-方案.md
└── ppt/
    ├── index.html
    ├── index-feishu.html
    └── images/
```

- `index.html`: maintainable local web PPT.
- `index-feishu.html`: single-file forwarding copy. It must not depend on sibling images, fonts, scripts, or styles.
- `<topic>-方案.md`: independent reading document. It must not require the PPT to make sense.
- `images/`: original product screenshots or generated visual assets used by the package.

Do not add a manifest, README, changelog, or extra design note unless it solves a real handoff or verification need.

Read [references/content-contract.md](references/content-contract.md) before planning the narrative or screenshots. Read [references/privacy-boundary.md](references/privacy-boundary.md) for every customer, partner, confidential, or externally owned project. Read [references/feishu-publishing.md](references/feishu-publishing.md) only when Feishu publication is requested.
Use [references/share-brief-template.md](references/share-brief-template.md) when the two outputs need a fresh shared story; keep the filled brief in `tmp/` by default.

## Workflow

### 1. Freeze Facts And Boundaries

Read the narrowest authoritative project material: local instructions, current docs, product entry points, main workflow, report/output paths, and relevant runtime evidence.

Separate:

- confirmed capability;
- demonstrated target experience;
- current deployment state;
- extension or future idea;
- unknown or conflicting claim.

Never infer production readiness, customer outcomes, or backend receipt from a demo, screenshot, frontend marker, or repository path alone.

For customer work, keep project-derived briefs, replay output, screenshots, denylist files, and validation reports in the customer project or temporary storage. Never copy them into this Skill, its tests, examples, evaluation evidence, or release package.

### 2. Build One Business Narrative

Create one shared story before writing either artifact:

1. what the project is and why it exists;
2. what problem it addresses;
3. the main user flow;
4. the few capabilities that change the outcome;
5. proof through screens or report evidence;
6. what the result contains and how it is used;
7. boundaries, current status, and next action.

Do not put “for sales”, “for pre-sales”, or similar audience labels in visible slide content unless the user explicitly wants them. Adapt the language to the readers without talking about the readers.

For a refresh, update the existing story instead of creating a second brief. The brief is working state, not a third deliverable.

### 3. Capture Proof, Not Decoration

Use raw product or report pages as the screenshot source. Default proof set:

- one product entry or home screen;
- one complete result overview;
- one complete report detail;
- one delivery or action-result view.

Use 2x pixel density when possible. Preserve complete component boundaries. Do not bake PPT backgrounds, dot grids, browser chrome, or decorative frames into evidence screenshots. Do not compress several unreadable images into one slide; spread them across pages or use a controlled gallery.

Inspect screenshots at original resolution for customer names, accounts, domains, URLs, identifiers, browser profiles, notifications, and hidden page content. Text scanning does not replace this visual review.

### 4. Write The Independent Document

Use `documentation` and business-readable language. The document should normally cover:

- conclusion and purpose;
- problem and capability scope;
- main workflow;
- report/output examples with screenshots;
- only the technical structure needed to explain cost, quality, responsibility, or risk;
- evidence, AI, permission, and data boundaries;
- current status and production checks;
- main fact sources.

Keep it concise. Remove repeated captions, duplicated status tables, and internal debate that does not help a reader judge or act.

### 5. Build The Web PPT

Use the active PPT skill and its own templates and validators. Default to 7-10 pages for a short project overview. Prefer a project-specific opening that states the purpose and capability plainly; do not reuse a generic cover merely because other decks use it.

The PPT is for quick understanding, not a compressed copy of the document. One page should carry one decision or idea. Technical detail belongs in the document unless it changes a business decision.

### 6. Cross-Check The Package

Before publication, verify:

- project name, purpose, capability names, flow, and boundaries agree across both artifacts;
- screenshots come from the named source and are readable;
- local image links resolve;
- the normal deck works from its intended location;
- the single-file deck opens without sibling assets;
- desktop and smaller viewport checks show no clipping, overlap, blank canvas, or console error;
- the document remains understandable if the PPT is never opened.

An upload command succeeding is not publication verification.

Run the deterministic local contract check:

```bash
python3 <skill-root>/scripts/validate_share_pack.py \
  --document <share-root>/<topic>-方案.md \
  --deck <share-root>/ppt/index.html \
  --portable-deck <share-root>/ppt/index-feishu.html \
  --forbid-terms-file <temporary-denylist.txt>
```

For non-confidential work, omit the denylist option. For customer work, the denylist is required and must remain outside this Skill repository. Fix errors before publication. Warnings such as a narrow screenshot or remote document image require judgment, not automatic failure.

### 7. Publish To Feishu Only When Requested

External writes require the user to provide or approve the target folder and overwrite behavior.

- Locate an existing same-name Docx in the target folder before creating a new one.
- Prefer overwriting the existing document to preserve its URL when the user says it may be covered.
- Prepare Markdown and a media insertion plan with:

```bash
python3 <skill-root>/scripts/prepare_feishu_publish.py \
  --source <solution.md> \
  --output-dir <temporary-output-dir>
```

- Overwrite the Docx body, then insert each local image at its caption or nearest heading.
- Upload or update `index-feishu.html` as a Drive file.
- Read the online Docx back and count images, diagrams, and the last section.
- Re-list the folder and report the final URLs.

Feishu storage and Feishu browser execution are different states. Only say “online preview works” after opening the uploaded HTML in the actual tenant/browser and verifying rendered slides and navigation. Otherwise report `uploaded_not_render_verified`. See [references/feishu-publishing.md](references/feishu-publishing.md).

## Stop Conditions

Stop and report the smallest blocker when:

- project facts conflict and would change the visible story;
- required screenshots contain sensitive data without an approved sanitization path;
- a screenshot source cannot be opened or reproduced;
- Feishu user authorization, folder access, or required scope is missing;
- overwrite targets are ambiguous;
- HTML is stored but cannot be proven to render online;
- three materially different layout repairs fail the same visual check.

Do not solve a publication blocker by creating duplicates, weakening privacy, or claiming a local file is an online page.

## Verification Level

Minimum for local generation: current files plus browser-rendered deck and inspected screenshots (`L3`).

Minimum for Feishu completion: successful write responses plus online document fetch, media count, folder re-list, and actual HTML browser rendering if “online preview” is claimed (`L3`, or `L4` when an independent reviewer is available).
