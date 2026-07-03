# Video Production Contract

Use this file when a video request needs durable artifacts rather than a single response.

## `brief.json`

Use this structured companion to `brief.md` when another AI must reproduce the workflow.

```json
{
  "title": "project title",
  "synopsis": "one paragraph story or video summary",
  "era_setting": "modern|xianxia|sci-fi|brand-world|other",
  "duration_sec": 120,
  "ratio": "9:16",
  "style": "cinematic live action, elegant, soft light",
  "extra_notes": ["constraints, required lines, taboo content, platform notes"],
  "drama_type": "dialogue|narration|mixed|non-narrative",
  "episode_duration_sec": [70, 50],
  "language": "zh-CN",
  "source_route": "native|configured-provider|user-asset|stock|render|edit|planning-only",
  "approval_status": "approved|needs_revision|blocked|planning_only",
  "field_sources": {
    "title": "user_explicit|inferred|default|system",
    "synopsis": "user_explicit|inferred|default|system",
    "duration_sec": "user_explicit|inferred|default|system",
    "ratio": "user_explicit|inferred|default|system",
    "style": "user_explicit|inferred|default|system"
  },
  "required_confirmation_fields": ["title", "synopsis", "style"],
  "accepted_defaults": ["ratio"],
  "open_questions": []
}
```

Every inferred or defaulted creative field must remain visible until accepted. For dialogue-driven short dramas, preserve role dialogue, voice profiles, and dialogue timecodes. Do not convert the project into generic narration unless the user approves that change.

## `asset_manifest.json`

```json
{
  "project": "short-name",
  "assets": [
    {
      "id": "scene-01-bg",
      "type": "image|video|audio|font|voice|text|render",
      "role": "character-avatar|character-turnaround|scene-plate|prop-sheet|keyframe|shot-video|voice|music|caption|render",
      "source": "native-tool|user-provided|stock|provider|rendered",
      "path": "relative/output/path.ext",
      "origin_url": "https://example.com/or-empty",
      "license_or_permission": "user-owned|licensed|generated|unknown",
      "permission_evidence": "provider terms URL, user license note, receipt id, or planning-only blocker",
      "publication_status": "allowed|needs_review|blocked|planning_only",
      "provider": "native|openai|seedance|veo|runway|fal|pexels|pixabay|manual|none",
      "linked_ids": ["char-01", "scene-01", "shot-001"],
      "approval_status": "approved|needs_revision|blocked|planning_only",
      "prompt_file": "prompts/scene-01.md",
      "duration_seconds": 4,
      "notes": "why this asset is allowed and how it is used"
    }
  ]
}
```

Any `unknown` permission blocks final publication. Vague notes such as "platform generated" or "provider owned" are not enough for publication unless the provider terms, user authorization, or project-specific license evidence is linked. Planning may continue, but label the asset as a planning-only draft until rights are confirmed.

## Short Drama Stage Contracts

Use these contracts when the video is a short drama, AI skit, cinematic ad, serial episode, or any narrative video where continuity matters.

### `outline.md`

```markdown
# Outline

## Story Spine
- Title:
- Logline:
- Theme:
- Structure:
- Conflict arc:
- Cliffhanger or payoff:

## Episodes
| Episode | Duration | Abstract | Required Dialogue | Main Location | Turning Point |
|---|---:|---|---|---|---|

## Continuity Seeds
- Characters introduced:
- Scenes introduced:
- Props introduced:
- BGM or SFX direction:
- Visual motifs:
```

### `style_retrieval.md`

```markdown
# Style Retrieval

## Source Fields
- Style:
- Era setting:
- Aspect ratio:
- Platform:

## Query
cinematic aesthetic, medium, material, lighting, camera language, color palette, atmosphere

## Include
- visual medium:
- lighting:
- palette:
- camera/lens:
- atmosphere:
- costume/material direction:

## Exclude
- plot turns
- private story text
- specific character actions
- protected brand or artist copying

## References
| ID | Source | Permission | Why useful | Approved |
|---|---|---|---|---|

## Approval
- Status: approved/needs_revision/blocked/planning_only
- Decision:
```

Style retrieval is for visual language only. It should not smuggle story beats or provider-specific prompt text into the style lock.

### `visual_bible.md`

```markdown
# Visual Bible

## Global Style
- Visual style:
- Aspect ratio:
- Color palette:
- Lighting:
- Camera language:
- Continuity rules:

## Characters
| ID | Name | Role | Description | Approved references | Continuity lock |
|---|---|---|---|---|---|
| char-01 | Name | protagonist | face, costume, posture, age, body type | assets/char-01-avatar.png | face, costume, body ratio |

## Scenes
| ID | Name | Environment | Approved references | Continuity lock |
|---|---|---|---|---|
| scene-01 | Location | weather, props, geography, time of day | assets/scene-01.png | layout, palette |

## Props
| ID | Name | Description | Approved references | Continuity lock |
|---|---|---|---|---|
| prop-01 | Object | material, silhouette, markings | assets/prop-01.png | full object shape |
```

### `storyboard.md`

```markdown
# Storyboard

## Timeline Math
- Total target duration:
- Episode targets:
- Shot duration sum:
- Result: pass/fail/blocked
- Duration deviation:
- Deviation reason:
- User-approved deviation: yes/no/pending
- Updated export target:

| Episode | Shot ID | Start | End | Duration | Visual Beat | Characters | Scene | Props | Camera | Motion Class | Dialogue | SFX/BGM | References | Acceptance Check |
|---|---|---:|---:|---:|---|---|---|---|---|---|---|---|---|---|
| 1 | shot-001 | 0 | 8 | 8 | opening confrontation | char-01, char-02 | scene-01 | prop-01 | slow push-in | slow-dialogue | line text | wind, low BGM | char-01-board, scene-01-plate | identities clear, no text overlay |
```

The storyboard must make timing arithmetic inspectable. If the target is 120 seconds split into episodes, each episode sum must match its approved target before keyframes begin. If the team intentionally keeps a longer or shorter cut, record the duration delta, reason, user decision, and updated export target before keyframes continue.

### `audio_plan.md`

```markdown
# Audio Plan

## Global BGM Arc
- Opening:
- Conflict:
- Climax:
- Resolution:

## Voice Profiles
| ID | Character ID | Voice | Delivery | Notes |
|---|---|---|---|---|
| voice-01 | char-01 | young male, clear and firm | restrained, determined | reuse exactly across shot prompts |

## Shot Audio Rules
| Shot ID | Dialogue | BGM | SFX | Mixing Rule |
|---|---|---|---|---|
| shot-001 | line or none | global arc segment | rain, wind | duck BGM under dialogue; never silent unless intentional |

## Mixing Parameters
| Track | Target level | Peak limit | Ducking threshold | Attack | Release |
|---|---:|---:|---:|---:|---:|
| dialogue | -12 dBFS | <= -6 dBFS | n/a | n/a | n/a |
| bgm | -22 dBFS | <= -10 dBFS | dialogue present | 80 ms | 350 ms |
| sfx | -18 dBFS | <= -8 dBFS | dialogue present | 20 ms | 200 ms |
```

### `stage_gate_report.md`

```markdown
# Stage Gate Report

| Gate | Status | Artifact | Planned | Generated | Failed | Duration deviation | User decision | Next blocked action | Blocker or rework |
|---|---|---|---:|---:|---:|---:|---|---|---|
| Requirements | approved/needs_revision/blocked/planning_only | brief.md | 1 | 1 | 0 | 0s | confirmed | none | none |
| Outline | approved/needs_revision/blocked/planning_only | outline.md | 1 | 1 | 0 | 0s | pending | wait for user | waiting for user |
```

### `keyframe_manifest.json`

```json
{
  "project": "short-name",
  "keyframes": [
    {
      "id": "kf-001",
      "shot_id": "shot-001",
      "storyboard_ref": "storyboard.md#shot-001",
      "source_route": "native-image|provider|user-asset|planning-only",
      "prompt_file": "prompts/keyframes/kf-001.md",
      "output_path": "assets/keyframes/kf-001.png",
      "reference_asset_ids": ["char-01-avatar", "scene-01-plate", "prop-01"],
      "reference_map": {
        "image_1": "char-01-avatar",
        "image_2": "char-02-avatar",
        "image_3": "scene-01-plate"
      },
      "global_style_prefix": "approved style lock from style_retrieval.md",
      "aspect_ratio": "9:16",
      "character_reference_ids": ["char-01-board", "char-02-board"],
      "prop_reference_ids": ["prop-01-sheet"],
      "identity_lock": {
        "face": ["char-01 face must match char-01-board", "char-02 face must match char-02-board"],
        "costume": ["char-01 grey coarse robes", "char-02 white robe with gold trim"],
        "prop": ["prop-01 silhouette and markings unchanged"]
      },
      "mixup_risks": ["face swap", "costume swap", "prop deformation"],
      "prompt_sections": ["style", "reference_map", "lens", "composition", "subjects", "pose", "expression", "lighting", "scene", "negative_constraints"],
      "negative_constraints": ["no subtitles", "no text overlay", "no split panels", "no broken anatomy", "no floating props"],
      "approval_status": "approved|needs_revision|blocked|planning_only",
      "continuity_checks": ["character face", "costume", "scene layout", "prop shape"],
      "notes": "what must remain stable for shot-video generation"
    }
  ]
}
```

### `shot_video_manifest.json`

```json
{
  "project": "short-name",
  "shots": [
    {
      "id": "shot-001",
      "keyframe_id": "kf-001",
      "end_keyframe_id": "kf-002-or-empty",
      "source_route": "native-video|provider|render|edit|planning-only",
      "prompt_file": "prompts/shot-videos/shot-001.md",
      "output_path": "assets/shot-videos/shot-001.mp4",
      "duration_seconds": 4,
      "resolution": "704x1280|1080x1920|unknown",
      "frame_relation": "first_frame_only|first_and_last_frame|multi_keyframe|provider_default",
      "location_time_weather": "cliff edge, daytime, rain",
      "motion_class": "slow-dialogue|action-vfx|transition|static-hold",
      "motion": "camera push-in, character raises sword, rain moves backward",
      "engine_params": {
        "input_image_url": "asset or provider URL for first frame",
        "motion_bucket_id": "20-40 for calm dialogue, 80-110 for action, or provider-specific value",
        "noise_aug_strength": "0.02-0.05 or provider-specific",
        "fps": 24,
        "cfg_scale": "2.5-3.5 or provider-specific",
        "aspect_ratio": "9:16",
        "provider_notes": "optional metadata; do not require this when the selected tool has different controls"
      },
      "reference_controls": {
        "face_reference_weight": "0.75 or provider-specific",
        "costume_reference_weight": "0.6 or provider-specific",
        "prop_reference_ids": ["prop-01-sheet"]
      },
      "generated_count": 1,
      "failed_count": 0,
      "selected_take": "take-1",
      "rejection_reasons": [],
      "continuity_evidence": {
        "frame_color_drift_pct": "within +/-8% or unknown",
        "prop_contour_deformation_pct": "within 15% or unknown",
        "face_similarity": {
          "char-01": "0.82 or unknown"
        },
        "manual_inspection_notes": "identity, scene, prop, and subtitle visibility observations"
      },
      "timeline": [
        {
          "start": 0,
          "end": 2,
          "beat": "camera starts from approved keyframe composition"
        }
      ],
      "dialogue_or_caption": "line or none",
      "voice_profile_ids": ["voice-01"],
      "audio_policy": "global BGM present, duck under dialogue, local SFX present, no accidental silence",
      "text_policy": "no subtitles|burned captions|safe-area captions",
      "approval_status": "approved|needs_revision|blocked|planning_only",
      "qa": ["duration", "resolution", "no identity drift", "no broken motion", "audio present", "caption timing"]
    }
  ]
}
```

If no image generation is available, stop at `visual_bible.md` and mark `keyframe_manifest.json` as `blocked` or `planning_only`. If no video generation/render/edit path is available, stop after approved keyframes and mark `shot_video_manifest.json` as `blocked`. Provider parameter examples are optional metadata, not a requirement to configure that provider.

### `production_dossier.md`

```markdown
# Production Dossier

## Requirements
- Link or copy from `brief.md`.
- Link or copy structured fields from `brief.json` when present.
- Include field provenance, accepted defaults, open questions, and remaining confirmations.

## Outline
- Link or copy from `outline.md`.

## Visual And Audio Bible
- Style retrieval:
- Characters:
- Scenes:
- Props:
- Global style:
- Audio plan:

## Storyboard
- Episode and shot table:

## Generated Assets
- Reference assets:
- Keyframes:
- Shot clips:
- Permission evidence and publication status:

## Edit And Export
- Timeline:
- Compose plan:
- Run audit:
- Final output path:

## QA
- Link or copy from `qa_report.md`.
```

## `edit_plan.json`

```json
{
  "platform": "tiktok|youtube|bilibili|wechat|website|internal",
  "aspect_ratio": "9:16|16:9|1:1|4:5",
  "duration_seconds": 30,
  "timeline": [
    {
      "scene": 1,
      "start": 0,
      "end": 3,
      "visual_asset_ids": ["scene-01-bg"],
      "audio_asset_ids": ["voice-01"],
      "caption": "on-screen caption",
      "transition": "cut|fade|match-cut|none",
      "qa": ["safe-area text", "mobile readable"]
    }
  ],
  "exports": [
    {
      "format": "mp4",
      "resolution": "1080x1920",
      "fps": 30,
      "path": "dist/final.mp4"
    }
  ]
}
```

## `compose_plan.json`

```json
{
  "status": "approved|needs_revision|blocked|planning_only",
  "expected_duration_seconds": 120,
  "clip_order": [
    {
      "shot_id": "shot-001",
      "path": "assets/shot-videos/shot-001.mp4",
      "start": 0,
      "end": 8,
      "duration_seconds": 8
    }
  ],
  "timeline_sum_check": "pass|fail|blocked",
  "duration_deviation": {
    "expected_seconds": 120,
    "actual_seconds": 128,
    "delta_seconds": 8,
    "reason": "why the longer or shorter edit was accepted",
    "approval_status": "approved|needs_revision|blocked|planning_only"
  },
  "clip_count_check": {
    "storyboard_shots": 14,
    "compose_clips": 14,
    "render_command_inputs": 14,
    "result": "pass|fail|blocked"
  },
  "audio_tracks": [
    {
      "id": "dialogue",
      "path": "assets/audio/dialogue.wav",
      "format": "PCM WAV",
      "sample_rate_hz": 48000,
      "channels": "mono",
      "target_level": "-12 dBFS",
      "peak_limit": "<= -6 dBFS"
    },
    {
      "id": "sfx",
      "path": "assets/audio/sfx.wav",
      "format": "PCM WAV",
      "sample_rate_hz": 48000,
      "channels": "stereo",
      "target_level": "-18 dBFS",
      "peak_limit": "<= -10 dBFS"
    },
    {
      "id": "bgm",
      "path": "assets/audio/bgm.wav",
      "format": "WAV or MP3",
      "sample_rate_hz": 48000,
      "channels": "stereo",
      "target_level": "-22 dBFS",
      "ducking_rule": "duck to -28 dBFS under dialogue"
    }
  ],
  "dialogue_timecodes": [{"start": 0.5, "end": 3.2, "speaker": "char-01", "text": "line"}],
  "sfx_timecodes": [{"time": 4.0, "asset_id": "sfx-sword", "note": "impact"}],
  "subtitle_policy": {
    "mode": "burned|sidecar|none",
    "safe_area": "mobile lower third",
    "style": "white text, black outline, readable at target platform size"
  },
  "render_command_template": "ffmpeg concat/filter_complex/native-render command or planning-only placeholder",
  "output": {
    "path": "dist/final.mp4",
    "container": "mp4",
    "video_codec": "libx264 or native equivalent",
    "audio_codec": "aac or native equivalent",
    "resolution": "1080x1920",
    "fps": 24,
    "pixel_format": "yuv420p",
    "video_bitrate": "6.5 Mbps or native metadata"
  },
  "ffprobe_metadata": {
    "duration_seconds": 120,
    "video_codec": "h264",
    "audio_codec": "aac",
    "width": 1080,
    "height": 1920,
    "fps": 24,
    "pixel_format": "yuv420p"
  },
  "inspection_evidence": ["ffprobe metadata", "sampled playback", "subtitle screenshot", "audio loudness check"]
}
```

Do not mark `compose_plan.json` as approved unless every referenced clip/audio/subtitle asset exists or the user explicitly requests a planning-only package.

## `run_audit.json`

```json
{
  "status": "completed|blocked|planning_only",
  "elapsed_time": {
    "total_minutes": 330,
    "requirements_minutes": 5,
    "outline_script_minutes": 15,
    "asset_generation_minutes": 90,
    "keyframe_minutes": 60,
    "shot_video_minutes": 150,
    "compose_export_minutes": 10
  },
  "generation_counts": {
    "static_images": 32,
    "shot_videos": 18,
    "failed_or_rejected": 4,
    "selected_takes": 14
  },
  "cost": {
    "currency": "USD",
    "image_generation": 4.5,
    "video_generation": 18.0,
    "voice_or_audio": 0.8,
    "total": 23.3,
    "source": "provider metadata|estimate|unknown"
  },
  "capability_boundaries": {
    "native_supported": ["brief parsing", "storyboard math", "script formatting", "local compose planning"],
    "provider_required": ["image generation", "video generation", "voice synthesis"],
    "human_required": ["character-board approval", "action-intensity selection", "subtitle readability review"],
    "nonportable_provider_params": ["voice profile id", "motion bucket", "reference weight"]
  }
}
```

Use `run_audit.json` only after a real or inspected dry-run workflow exists. For planning-only packages, mark it `planning_only` and do not invent elapsed time, costs, or provider counts.

## `qa_report.md`

```markdown
# QA Report

| Check | Result | Evidence |
|---|---|---|
| Duration matches brief | pass/fail | final.mp4 metadata |
| Aspect ratio matches platform | pass/fail | 1080x1920 |
| Captions synced | pass/fail | sampled timestamps |
| Audio intelligible and not clipped | pass/fail | waveform/preview |
| Stage gates approved or blocked honestly | pass/fail/blocked | stage_gate_report.md |
| Character, scene, and prop continuity stable | pass/fail/blocked | visual_bible.md + keyframe_manifest.json |
| Shot clips trace to keyframes | pass/fail/blocked | shot_video_manifest.json |
| Timeline sums match approved duration or approved deviation | pass/fail/blocked | storyboard.md + compose_plan.json |
| Compose clip count matches storyboard and render command inputs | pass/fail/blocked | compose_plan.json |
| Continuity metrics or inspection notes recorded | pass/fail/blocked | shot_video_manifest.json |
| Shot engine params recorded without hard provider dependency | pass/fail/blocked | shot_video_manifest.json |
| Audio mix, subtitle policy, and export codec recorded | pass/fail/blocked | compose_plan.json |
| Final media inspected before completion claim | pass/fail/blocked | output path + ffprobe/playback evidence |
| Asset permissions complete | pass/fail | asset_manifest.json |
| Asset publication status explicit | pass/fail/blocked | asset_manifest.json |
| Generated outputs traceable | pass/fail | prompts + output paths |
| Cost separated from estimates | pass/fail | run_audit.json or provider metadata |
```

If final media cannot be generated in the current environment, write `blocked` instead of `pass` and list the missing native capability or provider configuration.
