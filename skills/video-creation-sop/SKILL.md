---
name: video-creation-sop
description: Workflow skill for planning auditable AI video creation from articles, product briefs, scripts, talking-head footage, or creative concepts. Use when the user asks to make a video, turn content into a short video, plan AI video production, choose between native agent media tools and providers, create storyboards, generate video/image prompts, package talking-head edits, or define a repeatable video SOP. Do not use for simple video metadata extraction; use video-extractor for that.
---

# video-creation-sop

## Core Job

Turn a video idea into a checked production package before generation, rendering, editing, or publishing.

This skill is a director workflow. It does not install OpenMontage, HyperFrames, video-use, Remotion, Seedance, Runway, fal.ai, or any other provider by default. Treat those projects as optional routes that require explicit user authorization before installation, API calls, downloads, or writes outside the workspace.

## Operating Contract

Always produce or update these artifacts when the task is more than a tiny one-shot prompt:

1. `brief.md` - goal, audience, platform, aspect ratio, duration, language, budget, deadline, and distribution channel.
2. `script.md` - narration, dialogue, on-screen text, pacing, and call to action.
3. `storyboard.md` - scene table with visual intent, source type, audio, captions, and acceptance notes.
4. `asset_manifest.json` - every image, clip, voice, music, font, model output, and license/source.
5. `edit_plan.json` - timeline, cuts, transitions, captions, overlays, output specs, and review checkpoints.
6. `prompts/` - model prompts for images, video clips, voice, music, or thumbnails when generation is needed.
7. `qa_report.md` - checks for aspect ratio, duration, caption sync, audio level, black frames, copyright, cost, and visible defects.

For a planning-only request, output the artifact contents in Markdown instead of writing files unless the user asks for files.

## Capability Resolver

Before requiring a third-party provider, probe the current runtime and configured environment.

1. Native runtime tools first.
   - If the active agent exposes image generation, image editing, video generation, video editing, render/export, browser capture, or FFmpeg/media tools, use the native capability first when it satisfies the deliverable.
   - Record the tool used, prompt, output path, limits, and visible cost if the runtime exposes them.
2. Configured providers second.
   - If native tools are missing or insufficient, check only already-configured providers or user-approved tools.
   - Examples: OpenAI image/video tools, Veo, Seedance, Runway, fal.ai, HeyGen, ElevenLabs, Pexels, Pixabay, Remotion, HyperFrames, video-use, FFmpeg.
3. Forced configuration gate.
   - If no native or configured path can produce the requested image, video, voice, stock media, or render, stop and list the smallest required configuration.
   - Do not fabricate assets, pretend a render succeeded, or describe a plan as an output file.
4. Separate generation from rendering.
   - Image/video generation creates new media assets.
   - HyperFrames and Remotion render deterministic compositions from HTML/React/assets; they do not automatically solve missing footage, voice, or music.
   - Editing tools package, cut, caption, and export existing media.

## Route Matrix

Choose one main route, then add supporting routes only when the artifact contract requires them.

| User intent | Default route | Use when | Avoid when |
|---|---|---|---|
| Article, tweet, product page, PR, or explainer to short video | HTML/motion route, preferably native render tools or HyperFrames if configured | The deliverable is typography, charts, screen captures, product cards, or deterministic motion | The user needs realistic generated footage and no source visuals exist |
| Fixed-column batch videos | Remotion or equivalent code-render route | Repeated template, data-driven visuals, reusable React/JS components | One-off creative short with no need for template reuse |
| Talking-head, interview, course, podcast, or vlog recut | Editing route: native video editor, video-use, FFmpeg, or similar configured tool | Source footage exists and transcript/caption cuts drive the edit | The task is pure text-to-video generation |
| AI ad, short drama, cinematic shot, or image-to-video | Generation route: native video tool first, then configured Seedance/Veo/Runway/fal.ai provider | New motion footage is needed | No provider/native video generation exists |
| Reference-video style analysis | `video-extractor` for metadata/transcript, then this skill for transformation plan | User owns or may lawfully analyze the reference | The request implies copying protected footage or bypassing platform limits |
| End-to-end production system exploration | `ecosystem-scout` and `security-gate` before installing OpenMontage or similar | User explicitly wants a full studio/toolchain | The user only needs a lightweight SOP or prompt pack |

Read `references/tool-routing.md` when the user asks which ecosystem project to use. Read `references/production-contract.md` when you need the exact artifact schemas.

## Step-by-Step Workflow

### 1. Intake And Boundaries

Collect only the missing fields needed to proceed:

- purpose and audience
- target platform and aspect ratio
- target duration
- source material: article, product URL, raw footage, brand assets, reference video, script, or concept
- whether media may be generated, downloaded, edited, or only planned
- language, tone, voice, subtitles, and brand constraints
- budget and provider limits

Stop if ownership or reuse rights are unclear. Do not bypass login, paywalls, DRM, private groups, anti-abuse controls, or platform rules.

### 2. Production Brief

Create the brief before creative execution:

```markdown
## Video Brief
- Goal:
- Audience:
- Platform:
- Aspect ratio:
- Duration:
- Core message:
- Source materials:
- Allowed asset sources:
- Native/configured capabilities:
- Required configuration if missing:
- Review checkpoints:
```

### 3. Script And Storyboard

Write the script and storyboard as tables. Keep them testable.

```markdown
| Scene | Time | Visual | Source route | Voice/Text | Audio | Acceptance check |
|---|---:|---|---|---|---|---|
| 1 | 0-3s | Product problem hook | HTML/render | "Manual reporting wastes launch week." | beat hit | readable on mobile |
```

Every scene must name its source route: native image, native video, stock, user asset, generated prompt, HTML render, existing footage, or planning-only asset draft.

### 4. Asset And Prompt Plan

For generated assets:

- Put prompts in `prompts/`.
- Include negative constraints, aspect ratio, duration, reference inputs, and legal/brand limits.
- For Seedance-style multimodal prompts, explicitly map each uploaded reference to its role, such as first frame, last frame, character, product, motion, style, music, or transition.

For stock or user assets:

- Record source, license/permission, filename, duration, resolution, and whether modification is allowed.
- Prefer user-owned media or clearly licensed stock sources. Do not treat arbitrary public videos as reusable source footage.

### 5. Composition Or Edit

Pick the smallest path:

- Use HTML/HyperFrames-style rendering for kinetic type, product cards, dashboards, web captures, charts, and short explainers.
- Use Remotion-style rendering for repeatable React/data templates.
- Use video-use/FFmpeg-style editing for transcript-driven cuts, captions, silence removal, lower thirds, and packaging existing footage.
- Use OpenMontage-style pipeline thinking only when the user wants a full multi-provider production system.

Before rendering or editing, show the timeline/edit plan and get approval if the next action is expensive, long-running, irreversible, or requires external API calls.

### 6. QA Gate

Do not call the work done until the relevant checks are recorded:

- duration and aspect ratio match the brief
- all text is readable on the target platform
- captions are synced and safe-area aware
- audio does not clip and has intelligible speech
- no black frames, broken assets, or missing fonts
- asset_manifest has source and permission for every asset
- generated media prompts and provider outputs are traceable
- cost and provider usage are separated from estimates
- final export path is real and inspectable

## Anti-Patterns

- Do not say "generated" when only a prompt or plan exists.
- Do not require provider setup when the active runtime already exposes a suitable native media tool.
- Do not treat render frameworks as video generation services.
- Do not install or run third-party tools without explicit approval.
- Do not copy reference videos or brand assets without rights.
- Do not produce a single giant prompt without a brief, storyboard, and QA gate for multi-scene work.
- Do not hide missing capability behind vague language such as "use a suitable tool".

## Cross-Skill Invocation

- Need metadata, transcripts, or authorized source extraction -> `video-extractor`.
- Need latest ecosystem/tool comparison or external skill intake -> `ecosystem-scout`.
- Need third-party skill/package safety scan -> `security-gate`.
- Need motion-heavy frontend/HTML composition -> `frontend-expert`.
- Need real cost measurement or Grounding evidence -> `ai-cost-grounding-measurement`.
- Need post-implementation truth audit -> `reality-auditor`.
- Need public README/report after production -> `documentation`.
