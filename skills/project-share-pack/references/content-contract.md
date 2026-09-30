# Content And Screenshot Contract

## 1. Reader Contract

Visible content must help a mixed business and technical audience answer:

1. What is this project?
2. What problem does it address?
3. What is the main flow?
4. What can it currently produce?
5. What proof supports the description?
6. What does it not prove or do?
7. What should happen next?

Prefer common business language. Keep product names, metrics, file names, commands, and necessary industry terms; explain a term when its meaning changes a decision. Do not use technical detail merely to demonstrate technical depth.

## 2. Shared Narrative

The document and PPT must use the same:

- project name and one-sentence purpose;
- capability and workflow names;
- current-state wording;
- evidence and privacy boundaries;
- delivery/output names;
- unknowns and production caveats.

The PPT may omit detail but must not simplify a qualified statement into an absolute claim.

## 3. Default PPT Shape

For a 10-20 minute overview, use 7-10 pages:

1. project name, purpose, and core function;
2. problem or opportunity;
3. end-to-end workflow;
4. capability map;
5. product/result overview proof;
6. complete report-detail proof;
7. delivery/action-result proof;
8. boundary and current status;
9. closing takeaway or next action.

Combine or remove pages when the content does not justify them. Do not add an agenda page, chapter divider, quote page, or decorative transition by default.

## 4. Independent Document Shape

Use only sections that carry distinct reader value:

- conclusion;
- problem;
- capability scope;
- workflow;
- report and delivery examples;
- relevant technical structure;
- evidence and AI boundary;
- permission and data boundary;
- current state and production checks;
- fact sources.

The document may be longer than the deck, but it is not a full PRD, API manual, deployment guide, or test report.

## 5. Screenshot Rules

### Source

- Capture the actual product, demo, or report page.
- Record whether the source is real runtime, sanitized demo, or target experience.
- Keep customer information, tokens, URLs with sensitive parameters, and private account data out of the image.

### Completeness

- Capture the whole component needed to understand the point.
- A score without its conclusion is incomplete.
- Evidence without the associated impact or recommendation is incomplete when the slide claims to show a full report item.
- A delivery table should include its headers and enough rows to explain how work is assigned.

### Readability

- Prefer 2x device pixel ratio.
- Do not enlarge a low-resolution crop.
- Use one strong image per proof page, or a small set with equal reading priority.
- Long complete screenshots belong in the document with click-to-open originals; PPT pages should use bounded sections that remain readable at presentation size.
- Do not place a decorative PPT frame inside the source image. Apply presentation framing in the slide layout.

## 6. Default Output Layout

When the project has no established share directory:

```text
docs/share/<topic-slug>/
├── <topic>-方案.md
└── ppt/
    ├── index.html
    ├── index-feishu.html
    └── images/
```

Follow an existing project convention when one exists. Do not move or rename an established pack merely to match this default.

## 7. Completion Checklist

- The opening explains purpose and function without requiring prior context.
- Visible content does not label the audience unless requested.
- The deck can be understood in a quick scan.
- The document stands alone.
- Screenshots are source-faithful, complete, clear, and sanitized.
- The deck and document agree on facts and boundaries.
- No unsupported ROI, production, customer, compliance, or backend-receipt claim is present.
- Every claimed file and link exists.
