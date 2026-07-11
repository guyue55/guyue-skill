---
name: taste-aesthetics
description: Review-only or pre-implementation UI taste constraints for "AI 味", anti-slop critique, product-type classification, design dials, and reference boundaries. Use frontend-expert to change code; do not trigger for backend-only work.
---

# taste-aesthetics (Aesthetic Constraint Engine)

**Mission:** Eradicate generic AI UI output. Enforce deliberate, high-quality design choices based on the target audience and context.

**Core Philosophy:**
- AI default is bad (AI purple gradients, centered hero, identical bento boxes, generic glassmorphism).
- Read the room first.

## Workflow

### 1. Brief Inference & Dial Setting
Before writing **any** CSS/UI code, you MUST output your design read and Dial values in this format:
`[Taste: Reading page as Dashboard | Dials: Variance 4, Motion 2, Density 8]`

First classify the surface:
- **Marketing / brand page**: higher variance is allowed; visual identity and first-screen memorability matter.
- **SaaS dashboard / internal tool**: density, scan speed, table ergonomics, filters, keyboard/focus states, and predictable navigation matter more than drama.
- **Report / audit page**: hierarchy, anchors, evidence cards, export readability, and mobile overflow matter more than decorative composition.
- **Portfolio / campaign page**: stronger visual signature is allowed, but must still preserve content legibility and asset rights.

### 2. The Three Dials Translation
- **DESIGN_VARIANCE (1-10)**: If < 5, use strict grid alignment. If > 7, introduce asymmetrical padding, offset grids, or overlapping absolute layers.
- **MOTION_INTENSITY (1-10)**: If < 4, only `hover:opacity` and `transition-colors`. If > 7, use keyframes for entry (`animate-in fade-in slide-in-from-bottom`).
- **VISUAL_DENSITY (1-10)**: If < 4, use `p-8` or `p-12`. If > 7, use `p-2`, `text-xs`, tight leading.

### 3. Absolute Bans (Anti-Slop)
- 🚫 **Ban**: Warm beige + clay accents. AI-purple gradients (`from-purple-500 to-indigo-500`).
- 🚫 **Ban**: Centered hero layouts spanning 100% width with massive generic H1s.
- 🚫 **Ban**: "Inter" font default. Default to `sans` via `Geist` or `Satoshi` if available.

### 4. Deterministic Anti-Slop Checks
Before approving a UI, check these items explicitly:

1. **Template tells**: no nested cards, rounded icon tiles above every heading, generic bento grids, fake glassmorphism, or purple-blue gradients unless the brand requires them.
2. **Hierarchy**: page title, section title, body, labels, helper text, and data values must have distinct size/weight/spacing roles.
3. **Contrast and a11y**: text/background contrast, focus states, hit areas, labels, and keyboard reachability must be visible.
4. **Responsive proof**: mobile and desktop layouts must avoid text overlap, clipped buttons, horizontal overflow, and hero sections that hide all next content.
5. **Motion purpose**: motion must explain state, guide attention, or support brand tone; decorative motion that slows a dashboard is a defect.
6. **Design-reference boundary**: `DESIGN.md`, Refero, Figma, screenshots, and competitor pages can inform tokens and layout logic, but cannot justify copying brand marks, proprietary illustrations, protected copy, or private screens.

### 5. Output Shape
When this skill is used for review, return:

```markdown
[Taste: Reading page as <type> | Dials: Variance X, Motion Y, Density Z]

Findings
- P1/P2 issue with concrete UI impact.

Reference Boundary
- What can be borrowed.
- What must not be copied.

Fix Direction
- 3-5 concrete changes.
```
