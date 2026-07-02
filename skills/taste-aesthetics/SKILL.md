---
name: taste-aesthetics
description: Aesthetic UI/UX constraints. Prevents AI generic output ("slop"). Applies 3-Dials (Variance, Motion, Density), enforces design system matching, limits boilerplate components, and requires real visual assets. Use when generating, reviewing, or refactoring front-end code, landing pages, or portfolios.
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

### 2. The Three Dials Translation
- **DESIGN_VARIANCE (1-10)**: If < 5, use strict grid alignment. If > 7, introduce asymmetrical padding, offset grids, or overlapping absolute layers.
- **MOTION_INTENSITY (1-10)**: If < 4, only `hover:opacity` and `transition-colors`. If > 7, use keyframes for entry (`animate-in fade-in slide-in-from-bottom`).
- **VISUAL_DENSITY (1-10)**: If < 4, use `p-8` or `p-12`. If > 7, use `p-2`, `text-xs`, tight leading.

### 3. Absolute Bans (Anti-Slop)
- 🚫 **Ban**: Warm beige + clay accents. AI-purple gradients (`from-purple-500 to-indigo-500`).
- 🚫 **Ban**: Centered hero layouts spanning 100% width with massive generic H1s.
- 🚫 **Ban**: "Inter" font default. Default to `sans` via `Geist` or `Satoshi` if available.
