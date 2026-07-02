---
name: video-extractor
description: Methodologies for extracting normalized metadata, post captions, transcripts, and source media from video platforms. Useful when building media ingestion tools or analyzing video links.
---

# video-extractor (Platform Extraction Workflow)

**Mission:** Convert video-platform URLs into a normalized local source-material folder containing predictable assets (`metadata.json`, `post_caption.txt`, `transcript.txt`, `video.mp4`).

## The Standard Asset Contract
You must create a dedicated folder for each extraction and place these exact files:
- `metadata.json`
- `post_caption.txt`
- `transcript.txt`
- `video.mp4`

## Authorization Boundary
- Only extract media the user owns, is authorized to process, or that is explicitly licensed for download and reuse.
- Do not bypass login, paywalls, DRM, geo-blocking, private groups, or platform anti-abuse controls.
- Default to `--metadata-only` when the user only needs analysis, title, description, or transcript planning.

## Provider Strategies

### 1. yt-dlp Primary (Default for YT/Bili)
- When executing extraction, prefer this command template:
  `yt-dlp --write-info-json --write-description --format "bv*+ba/b" --merge-output-format mp4 -o "video.%(ext)s" [URL]`
- Parse the resulting `.info.json` and `.description` to populate `metadata.json` and `post_caption.txt`.

### 2. ASR Integration (Transcript)
- Always ask the user if they want ASR generation: "Would you like me to extract the transcript using ASR (e.g. Whisper)?"
- Provide an option for `--metadata-only` to skip downloading large video chunks if the user only needs the title and description.

### 3. Graceful Degradation
- If blocked (e.g. WeChat Channels), say: `[Extractor] Target is heavily walled. Please download manually and place the file here. I will resume the ASR workflow.`
