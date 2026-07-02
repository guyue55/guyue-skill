# Video Tool Routing Reference

Use this file only when choosing between video creation ecosystems. Do not install or execute any external project from this reference without explicit user approval.

## Current Ecosystem Map

| Tool or skill | Role | Strength | Main risk or limit | Source |
|---|---|---|---|---|
| OpenMontage | End-to-end agentic video production system | Pipeline manifests, stage directors, provider preflight, checkpoints | Heavy stack and AGPL-3.0; best as architecture reference unless the user wants a full studio | https://github.com/calesthio/OpenMontage |
| HyperFrames | HTML/CSS/media to deterministic MP4 | Agent-friendly motion graphics, product videos, website-to-video, captions, local render loop | Rendering layer, not a complete media-generation provider | https://github.com/heygen-com/hyperframes |
| video-use | Agent video editing for existing footage | Transcript-driven cuts, silence/filler removal, visual sampling, previewable edits | Needs source footage and media-processing dependencies | https://github.com/browser-use/video-use |
| Remotion Skills | React/data-driven video rendering skills | Batch templates, PR/product explainers, repeatable code videos | More setup and React/Remotion surface area than HTML-only renderers | https://github.com/remotion-dev/skills |
| Generative Media Skills | AI media generation API skill pack | Multi-modal image, video, and audio API access | Provider/API dependency; do not make it default without configuration | https://github.com/SamurAIGPT/Generative-Media-Skills |
| chengfeng-videocut-skills | Chinese video-cutting Agent skills | Chinese talking-head workflows, storyboards, timeline preview, review-before-export | Claude Code-oriented workflow; evaluate before adapting | https://github.com/Agentchengfeng/chengfeng-videocut-skills |
| seedance2-skill | Seedance/Jimeng prompt-writing skill | Multimodal reference mapping, shot language, ad/drama/MV prompt patterns | Prompt layer only; not a renderer or editor | https://github.com/dexhunter/seedance2-skill |
| FireRed-OpenStoryline | Conversational AI editing agent | Natural-language refinement, media search, style skill archiving | Larger app, external services, not a lightweight SOP dependency | https://github.com/FireRedTeam/FireRed-OpenStoryline |
| claude-code-video-toolkit | Claude Code video workspace | Voice, music, image generation, templates, Remotion examples | Runtime-specific; use as showcase reference, not default route | https://github.com/digitalsamba/claude-code-video-toolkit |

## Routing Heuristics

1. Start with native runtime media tools when present.
2. Use HyperFrames-style render for short designed videos from text, web, product, charts, or HTML.
3. Use Remotion-style render when the output is a reusable code template or data-driven series.
4. Use video-use or FFmpeg-style editing when raw footage already exists.
5. Use Seedance/Veo/Runway/fal.ai-style providers only when real generated motion footage is required and configured.
6. Use OpenMontage-style pipeline only for full multi-stage production systems with provider setup, not for lightweight SOP planning.
7. Record source URL, license/permission, tool version if visible, and output path for every generated or imported asset.
