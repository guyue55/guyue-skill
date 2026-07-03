# Short Drama Example Learnings

Use this reference when a user provides a complete short-drama generation transcript or asks whether a one-click video flow should influence this SOP.

## What To Learn

- Keep a structured `brief.json` beside the human brief when reproducibility matters. Stable inputs include title, synopsis, era setting, duration, ratio, style, extra notes, drama type, episode duration targets, source route, and approval status.
- Preserve field provenance in `brief.json`: whether each requirement was user-provided, inferred, defaulted, or system-filled, plus fields still requiring confirmation.
- Treat the first proposal as editable, not final. The example changed genre and style before the requirements gate was approved.
- Every major stage needs an explicit human decision before the next expensive generation stage.
- Lock visual style before script, asset, or keyframe generation, and record the lock in `style_retrieval.md`. Style retrieval should translate style and era into medium, material, lighting, palette, camera language, and atmosphere, without including plot or character actions.
- Asset design and asset generation are separate gates. Character, scene, and prop specs come before avatars, turnarounds, scene plates, and prop sheets.
- Dialogue-driven short dramas need role dialogue, voice profiles, and timecodes. Do not flatten them into narrator copy.
- Storyboards must expose timeline math. Shot durations should sum exactly to the approved total and each episode target before keyframes or shot videos are produced.
- If the final timeline intentionally drifts from the original target, record the delta, reason, updated export target, and explicit approval. Do not hide duration drift behind "artistic deviation."
- Keyframe prompts should map each reference image to a role, then name lens, composition, subject placement, pose, expression, lighting, scene, continuity locks, and negative constraints.
- Two-character or prop-heavy keyframes need explicit anti-mixup instructions: each character's face, costume, body silhouette, and each prop reference must be named separately.
- Shot-video prompts should start from the approved keyframe, then add location, time, weather, style, duration, character voice, camera movement, timestamped action beats, global BGM, local SFX, audio ducking, and text/subtitle policy.
- Shot-video manifests may preserve provider-specific metadata such as first-frame relation, motion class, motion strength, fps, CFG, aspect ratio, and reference weights, but those fields are evidence, not mandatory dependencies.
- Real shot-video review can use measurable continuity evidence: frame color drift, prop contour deformation, face similarity, selected take, rejection reason, and manual inspection notes.
- Final assembly needs its own `compose_plan.json`: clip order, timeline sum, dialogue/SFX/BGM track specs, mix targets, ducking, subtitle policy, render command template, output codec, and inspection evidence.
- Final composition must compare storyboard shot count, compose clip count, and render command input count. A green export is not enough if the command silently dropped planned shots.
- Real generation runs should end with `run_audit.json`: elapsed time, generation counts, rejected takes, costs, native capabilities, provider-required capabilities, human-required checkpoints, and nonportable provider parameters.
- Generated media gates must report planned count, generated count, failure count, provider or native tool, output path, and inspection result.
- Asset manifests must carry permission evidence and publication status; provider-generated or platform-hosted assets are not automatically safe to publish.
- Final delivery should include both the media export and a production dossier that preserves the whole process and all reusable text assets.

## What Not To Copy Blindly

- Do not promise "one requirement or idea equals a finished video." The reliable unit is a staged production package with approval gates and capability checks.
- Do not claim final export success unless the final media file path exists and has been inspected.
- Do not treat provider labels, generated dimensions, or prompt text as enough proof of usable video.
- Do not require the example provider, exact motion buckets, exact weights, or exact FFmpeg command when the active runtime has equivalent native tools or a different configured provider.
- Do not copy contradictory live-sample claims blindly. If a sample says the storyboard has one count but the FFmpeg concat command includes another count, treat it as a QA finding, not a template.
- Do not replace approved character IDs with generic labels unless the manifest keeps a stable mapping.
- Do not hide skipped audio, missing subtitles, identity drift, broken motion, or silent clips behind optimistic summary text.
- Do not use arbitrary public videos, images, voices, music, or brand assets unless rights are clear in `asset_manifest.json`.
- Do not accept vague permission labels such as "platform generated" as publication evidence unless the provider terms or user authorization is linked.
- Do not run paid generation, long renders, installs, downloads, or publication steps without explicit user authorization.
