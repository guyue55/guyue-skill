---
name: video-creation-sop
description: Auditable AI-video workflow for briefs, scripts, storyboards, prompts, assets, rendering, and repeatable production from text, footage, or concepts. Prefer native media capabilities before providers. For metadata, captions, transcripts, or source-media extraction only, use video-extractor.
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
6. `compose_plan.json` - clip order, audio tracks, subtitle burn-in or sidecar policy, render command template, codecs, and export evidence.
7. `prompts/` - model prompts for images, video clips, voice, music, or thumbnails when generation is needed.
8. `qa_report.md` - checks for aspect ratio, duration, caption sync, audio level, black frames, copyright, cost, and visible defects.

For short dramas, ads, cinematic stories, and other narrative videos, also produce or update:

1. `brief.json` - stable machine-readable requirements for title, synopsis, era, duration, ratio, style, drama type, episode targets, source route, approval status, field sources, accepted defaults, and required confirmations.
2. `outline.md` - episode structure, conflict, required dialogue, theme, pacing, and cliffhanger.
3. `style_retrieval.md` - style-lock query, include/exclude rules, visual references, and approval status before script or asset generation.
4. `visual_bible.md` - character, scene, prop, style, lighting, palette, and continuity rules.
5. `audio_plan.md` - global BGM arc, character voice profiles, per-shot SFX, and mixing rules.
6. `keyframe_manifest.json` - every approved keyframe, reference map, prompt file, shot id, identity lock, and consistency check.
7. `shot_video_manifest.json` - every generated or planned shot clip, duration, timeline beats, motion prompt, source keyframe, engine params, provider, and status.
8. `stage_gate_report.md` - human approval status, generated count, failure count, requested changes, blocked stages, and rework notes.
9. `production_dossier.md` - final consolidated document covering requirements, outline, style lock, visual bible, storyboard, prompts, assets, video clips, edit/export, and QA.

When real generation, rendering, or export runs, also produce `run_audit.json` with elapsed time, generated counts, failed counts, selected takes, rejected reasons, estimated or actual cost, native capabilities used, provider capabilities used, and provider-specific parameters that cannot be migrated directly.

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

## Model Capability And Seven-Axis Continuity Gate

Select the model before optimizing prompts. Add `model_capability_profile.json` to any narrative, reference-driven, or consistency-sensitive generation package. Record provider, model, exact version, supported input modes, first/last-frame or multi-image conditioning, maximum bounded duration, output dimensions, fixed-camera controls, local edit or mask support, seed/version reproducibility, completed-output retrieval, queue/access state, cost, and evidence. Keep these statuses distinct: `proven`, `documented_not_executed`, `supported_but_output_failed`, `unknown`, and `unsupported`.

Do not select a model merely because it is popular or already configured. Select it only when every hard capability required by the shot is neither `unknown` nor `unsupported`. A native capability still stays first when it meets the same contract; otherwise compare already configured or explicitly approved providers. Documentation proves routing eligibility, not output quality or queue availability.

For each generated shot, create `frame_qa.json` and assign every decoded frame to exactly one acceptance interval. Evaluate these seven axes without collapsing them into a single similarity score:

1. character or subject identity;
2. scene and world geometry;
3. prop identity and state;
4. expression and micro-expression, including nonhuman state cues such as indicator lights and hesitation timing;
5. action causality and physical contact;
6. background continuity and occlusion;
7. camera, lens, crop, horizon, scale, and motion continuity.

Every failure receives one primary axis, a stable failure code, frame or time range, evidence, and the smallest allowed repair scope. Prefer reference rebinding, keyframe edit, masked local repair, deterministic crop/normalization, or bounded temporal-segment regeneration. Do not jump directly to whole-shot regeneration when a smaller repair can preserve accepted regions.

After any local repair, require a full-shot replay from first decoded frame to last. Re-run all seven axes, verify that the repaired failure is gone and that no accepted axis regressed, then update `stage_gate_report.md`. A machine-clean replay remains a candidate until the declared human reviewers approve it; do not claim natural performance, micro-expression quality, popularity, or final acceptance from machine checks alone.

## Route Matrix

Choose one main route, then add supporting routes only when the artifact contract requires them.

| User intent | Default route | Use when | Avoid when |
|---|---|---|---|
| Article, tweet, product page, PR, or explainer to short video | HTML/motion route, preferably native render tools or HyperFrames if configured | The deliverable is typography, charts, screen captures, product cards, or deterministic motion | The user needs realistic generated footage and no source visuals exist |
| Fixed-column batch videos | Remotion or equivalent code-render route | Repeated template, data-driven visuals, reusable React/JS components | One-off creative short with no need for template reuse |
| Talking-head, interview, course, podcast, or vlog recut | Editing route: native video editor, video-use, FFmpeg, or similar configured tool | Source footage exists and transcript/caption cuts drive the edit | The task is pure text-to-video generation |
| Short drama, cinematic story, AI skit, or serial episode | Short Drama Stage Gates | The output depends on character continuity, scene consistency, keyframes, shot clips, and human approval | The user only needs a one-scene prompt or simple explainer |
| AI ad, cinematic shot, or image-to-video | Generation route: native video tool first, then configured Seedance/Veo/Runway/fal.ai provider | New motion footage is needed for a bounded shot or asset | No provider/native video generation exists, or the task is a multi-scene short drama that needs stage gates first |
| Reference-video style analysis | `video-extractor` for metadata/transcript, then this skill for transformation plan | User owns or may lawfully analyze the reference | The request implies copying protected footage or bypassing platform limits |
| End-to-end production system exploration | `ecosystem-scout` and `security-gate` before installing OpenMontage or similar | User explicitly wants a full studio/toolchain | The user only needs a lightweight SOP or prompt pack |

Read `references/tool-routing.md` when the user asks which ecosystem project to use. Read `references/production-contract.md` when you need the exact artifact schemas. Read `references/short-drama-example-learnings.md` when learning from a full short-drama example or writing reusable short-drama prompt templates.

## Short Drama Stage Gates

Use this branch when the user asks for a short drama, scripted series, cinematic ad, AI skit, or any story-driven video where continuity matters.

Do not skip straight from idea to final export. Move through the gates in order, and mark each gate as `approved`, `needs_revision`, `blocked`, or `planning_only`.

| Gate | Output | Approval question | Hard stop before |
|---|---|---|---|
| 1. Requirements | `brief.md` and `brief.json` | Are title, synopsis, duration, aspect ratio, story mode, style, and constraints correct? | outline generation |
| 2. Outline | `outline.md` | Are episodes, conflict arc, required dialogue, theme, and cliffhanger right? | style lock and visual bible |
| 3. Style And Visual Bible | `style_retrieval.md`, `visual_bible.md`, and `audio_plan.md` | Are style references, characters, scenes, props, voice profiles, BGM direction, palette, and continuity rules right? | reference image generation |
| 4. Reference Assets | `asset_manifest.json` | Are character portraits, turnarounds, scene plates, prop sheets, and licenses acceptable? | storyboard |
| 5. Storyboard | `storyboard.md` | Are scene timing, shot list, camera movement, dialogue, SFX, and acceptance checks right? | keyframes |
| 6. Keyframes | `keyframe_manifest.json` | Are generated/planned keyframes consistent with approved characters, scenes, props, and style? | shot video generation |
| 7. Shot Clips | `shot_video_manifest.json` | Are shot clips or planned clips traceable, timed, and visually acceptable? | final edit/export |
| 8. Final Export | `edit_plan.json`, `compose_plan.json`, `qa_report.md`, and `production_dossier.md` | Does the final export path exist, pass QA, and have a complete production dossier? | completion claim |

If the current runtime has no image or video generation capability, still produce gates 1-5 as planning artifacts, then stop at gate 6 or 7 with the smallest required configuration. If image generation exists but video generation does not, generate or plan reference assets and keyframes, then block shot clips until a video provider or render/edit path is configured.

For each gate, record:

- accepted inputs and changes from the previous gate
- artifact path or inline artifact content
- source route: native, configured provider, user asset, stock, render, edit, or planning-only
- planned count, generated count, failed count, and inspected sample when media is generated
- approval status and next blocked action
- approved duration deviation when the timeline no longer matches the original brief
- cost, provider, and output path when a real generation call ran

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
- for narrative videos: episode count, story mode, character count, reference-image policy, and approval cadence

For short dramas, capture the stable requirement fields explicitly: `title`, `synopsis`, `era_setting`, `duration_sec`, `ratio`, `style`, `extra_notes`, `drama_type`, `episode_duration_sec`, and `approval_status`. Also record `field_sources`, `required_confirmation_fields`, `accepted_defaults`, and `open_questions` so another AI can distinguish user-provided requirements from inferred or defaulted fields. If `drama_type` is dialogue-driven, storyboard and audio planning must preserve character dialogue and voice profiles instead of collapsing the script into narration.

Stop if ownership or reuse rights are unclear. Do not bypass login, paywalls, DRM, private groups, anti-abuse controls, or platform rules.

Preserve unresolved media decisions exactly. `voice talent unknown` means voice, narration, music, and SFX remain `open` or `planning_only`; it does not authorize choosing a silent final. A no-default-audio or muted-autoplay constraint controls playback behavior, not whether production may contain an audio track. Record the default used for a preview separately from the final audio decision and require confirmation before locking it.

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

For narrative work that needs another AI to reproduce the plan, also produce `brief.json` using the schema in `references/production-contract.md`.

### 3. Script And Storyboard

Write the script and storyboard as tables. Keep them testable.

```markdown
| Scene | Time | Visual | Source route | Voice/Text | Audio | Acceptance check |
|---|---:|---|---|---|---|---|
| 1 | 0-3s | Product problem hook | HTML/render | "Manual reporting wastes launch week." | beat hit | readable on mobile |
```

Every scene must name its source route: native image, native video, stock, user asset, generated prompt, HTML render, existing footage, or planning-only asset draft. For short dramas, include camera angle, shot size, movement, dialogue, SFX/BGM, duration, and the approved character/scene/prop references used by the shot.

Storyboard duration math must be auditable. If the shot duration sum differs from the brief or an episode target, do not hide it as a creative choice. Record the delta, reason, user decision, and whether the edit/export target has been updated before keyframes continue.

### 4. Asset And Prompt Plan

For generated assets:

- Put prompts in `prompts/`.
- Include negative constraints, aspect ratio, duration, reference inputs, and legal/brand limits.
- Before script or asset generation for cinematic stories, lock visual style in `style_retrieval.md`. The query should translate style and era into medium, material, lighting, palette, camera, and atmosphere terms. Do not include plot turns, character actions, or proprietary scene text in style retrieval.
- For Seedance-style multimodal prompts, explicitly map each uploaded reference to its role, such as first frame, last frame, character, product, motion, style, music, or transition.
- For keyframes, state the reference map, character images, scene plates, prop sheets, composition zone, camera specification, subject pose, expression, lighting, continuity constraints, and exclusion terms.
- For two-person or prop-heavy keyframes, name each character/prop reference separately and list mix-up risks, such as face swap, costume drift, or prop deformation.
- For shot clips, state the source keyframe, optional end keyframe, frame relation, location/time/weather, visual style, duration, motion class, camera path, action beats, timestamped dialogue or subtitle timing, voice profile, global BGM, local SFX, audio ducking rules, provider-specific optional engine params, and what must remain unchanged from the keyframe.

For stock or user assets:

- Record source, license/permission, filename, duration, resolution, and whether modification is allowed.
- Record permission evidence and publication status; generated or provider-hosted assets are not publication-ready until terms, user authorization, or a planning-only blocker is explicit.
- Prefer user-owned media or clearly licensed stock sources. Do not treat arbitrary public videos as reusable source footage.

### 5. Composition Or Edit

Pick the smallest path:

- Use HTML/HyperFrames-style rendering for kinetic type, product cards, dashboards, web captures, charts, and short explainers.
- Use Remotion-style rendering for repeatable React/data templates.
- Use video-use/FFmpeg-style editing for transcript-driven cuts, captions, silence removal, lower thirds, and packaging existing footage.
- Use OpenMontage-style pipeline thinking only when the user wants a full multi-provider production system.

Before rendering or editing, show the timeline/edit plan and get approval if the next action is expensive, long-running, irreversible, or requires external API calls.

For final assembly, record `compose_plan.json` before claiming export readiness. It must include clip order, expected timeline sum, audio track specs and mix targets, subtitle policy, render command template or native render settings, codec/container, output path, and inspection evidence. If assets are not present, mark the plan `blocked` or `planning_only` instead of inventing a render.

Before export, verify the compose plan against the storyboard: clip count, clip order, expected duration, render command input count, subtitle file, and audio track list must match the approved artifacts or carry an explicit blocker/approved deviation.

### 6. QA Gate

Do not call the work done until the relevant checks are recorded:

- duration and aspect ratio match the brief
- all text is readable on the target platform
- captions are synced and safe-area aware
- audio does not clip and has intelligible speech
- no black frames, broken assets, or missing fonts
- asset_manifest has source and permission for every asset
- asset_manifest has permission evidence and publication status for every publication-bound asset
- generated media prompts and provider outputs are traceable
- cost and provider usage are separated from estimates
- short-drama gate statuses are recorded as approved, needs_revision, blocked, or planning_only
- keyframes trace to the visual bible, and shot clips trace to approved keyframes
- storyboard shot durations sum to the brief or each episode target, or carry an explicit approved duration deviation
- generated media counts match the plan, and every failure or skipped asset is visible
- shot clips record duration, resolution, audio policy, text/subtitle policy, and inspected defects
- shot clips record continuity evidence when available, such as frame color drift, prop contour stability, face similarity, or manual inspection notes
- shot-video manifests record engine parameters only as provider-specific metadata, not as mandatory dependencies
- final composition records clip concat order, audio mix levels, subtitle policy, codec/container, and export evidence
- final composition clip count and render input count match the approved storyboard, or the mismatch is blocked before completion
- final export path is real and inspectable

## Anti-Patterns

- Do not say "generated" when only a prompt or plan exists.
- Do not require provider setup when the active runtime already exposes a suitable native media tool.
- Do not treat render frameworks as video generation services.
- Do not install or run third-party tools without explicit approval.
- Do not copy reference videos or brand assets without rights.
- Do not produce a single giant prompt without a brief, storyboard, and QA gate for multi-scene work.
- Do not hide missing capability behind vague language such as "use a suitable tool".
- Do not treat short-drama stages as optional when character or scene continuity is required.
- Do not collapse character IDs into generic labels without keeping a manifest mapping back to approved characters.
- Do not proceed from visual bible to keyframes, from keyframes to shot clips, or from shot clips to export without recording approval or a clear user instruction to continue.
- Do not accept timeline drift, missing clips, or mismatched concat inputs as "artistic choices" unless the deviation is explicit, evidenced, and approved.

## Cross-Skill Invocation

- Need metadata, transcripts, or authorized source extraction -> `video-extractor`.
- Need latest ecosystem/tool comparison or external skill intake -> `ecosystem-scout`.
- Need third-party skill/package safety scan -> `security-gate`.
- Need motion-heavy frontend/HTML composition -> `frontend-expert`.
- Need real cost measurement or Grounding evidence -> `ai-cost-grounding-measurement`.
- Need post-implementation truth audit -> `reality-auditor`.
- Need public README/report after production -> `documentation`.
