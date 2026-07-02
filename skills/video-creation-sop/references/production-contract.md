# Video Production Contract

Use this file when a video request needs durable artifacts rather than a single response.

## `asset_manifest.json`

```json
{
  "project": "short-name",
  "assets": [
    {
      "id": "scene-01-bg",
      "type": "image|video|audio|font|voice|text|render",
      "source": "native-tool|user-provided|stock|provider|rendered",
      "path": "relative/output/path.ext",
      "origin_url": "https://example.com/or-empty",
      "license_or_permission": "user-owned|licensed|generated|unknown",
      "provider": "native|openai|seedance|veo|runway|fal|pexels|pixabay|manual|none",
      "prompt_file": "prompts/scene-01.md",
      "duration_seconds": 4,
      "notes": "why this asset is allowed and how it is used"
    }
  ]
}
```

Any `unknown` permission blocks final publication. Planning may continue, but label the asset as a planning-only draft until rights are confirmed.

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

## `qa_report.md`

```markdown
# QA Report

| Check | Result | Evidence |
|---|---|---|
| Duration matches brief | pass/fail | final.mp4 metadata |
| Aspect ratio matches platform | pass/fail | 1080x1920 |
| Captions synced | pass/fail | sampled timestamps |
| Audio intelligible and not clipped | pass/fail | waveform/preview |
| Asset permissions complete | pass/fail | asset_manifest.json |
| Generated outputs traceable | pass/fail | prompts + output paths |
| Cost separated from estimates | pass/fail | provider metadata or "not available" |
```

If final media cannot be generated in the current environment, write `blocked` instead of `pass` and list the missing native capability or provider configuration.
