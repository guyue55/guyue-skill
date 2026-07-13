状态：规划版生产包已完成。未调用生成、渲染或外部服务，也未把“默认静音播放”误设为“最终成片必须无音轨”。

当前仅阻断生产执行。最小补充输入：

1. 三张截图原文件、尺寸及对应展示顺序。
2. 更新名称、三条核心变化、每条用户价值和 CTA。
3. 发布平台与画幅。
4. 确认截图是否允许裁切、缩放、加高亮标注。
5. 决定最终音频方向：真人配音、后续合成音、仅音乐/音效或无音轨。预览仍默认静音。

## `brief.md`

```markdown
# Video Brief

- Goal: 在 30 秒内说明一次产品更新，并引导用户采取下一步行动
- Audience: 待确认
- Platform: 待确认
- Distribution channel: 待确认
- Aspect ratio: 待确认
- Duration: 30 秒
- Language: 待确认
- Core message: [更新名称]、三项变化及其用户价值
- Tone: 待确认；默认采用清晰、克制的产品演示表达
- Source materials: 三张用户声明已授权的产品截图
- Allowed asset sources: 仅这三张截图、排版图形与经确认的字体；不新增生成媒体
- Source route: 用户资产 + HTML/确定性动效排版，planning-only
- Audio decision: open
- Playback constraint: 预览及发布载体不得默认自动播放声音；有音轨时默认静音，须由用户主动开启
- Sound-off requirement: 关闭声音时仍能完整理解更新内容
- Budget: 规划阶段无服务调用、无已发生成本；制作预算待确认
- Deadline: 待确认
- Review checkpoints:
  1. 平台、画幅和截图顺序
  2. 更新文案与 CTA
  3. 时间线与动效
  4. 最终音频方案
  5. 导出前 QA
- Required configuration for execution:
  - 一个已配置的确定性排版/视频渲染能力
  - 若最终包含声音，还需已授权的配音、音乐或音效资产
- Status: planning_only
```

## `script.md`

```markdown
# Script

说明：方括号内容必须由产品信息替换。配音尚未决定，因此旁白保持 open。

| 时间 | 画面文字 | 旁白 | 节奏 |
|---|---|---|---|
| 0–3s | `[更新名称] 已上线` / `[一句话核心价值]` | OPEN：未锁定旁白方案 | 快速建立主题 |
| 3–10s | `[变化一：短标题]` / `[用户价值，不超过一行]` | OPEN | 截图重点由高亮框或局部放大呈现 |
| 10–17s | `[变化二：短标题]` / `[用户价值，不超过一行]` | OPEN | 保持同一排版结构 |
| 17–24s | `[变化三：短标题]` / `[用户价值，不超过一行]` | OPEN | 形成第三个信息节拍 |
| 24–30s | `[总结收益]` / `[CTA：立即体验、查看详情等]` | OPEN | 收束并保留 CTA 阅读时间 |

文案约束：

- 即使全程静音，屏幕文字也必须表达完整信息。
- 每屏只保留一个主要结论。
- 不添加截图无法证明的功能、数据或效果。
- CTA、产品术语和品牌语气须经确认。
```

## `storyboard.md`

```markdown
# Storyboard

## Timeline Math

- Target duration: 30s
- Scene duration sum: 3 + 7 + 7 + 7 + 6 = 30s
- Result: plan-level pass
- Duration deviation: 0s
- Export target updated: no
- Production status: blocked pending source files and copy

| Scene | Time | Duration | Visual | Source route | Voice/Text | Audio | Acceptance check |
|---|---:|---:|---|---|---|---|---|
| 1 | 0–3s | 3s | 简洁标题卡；可使用品牌色块，不引入新图像 | HTML/render planning-only | 更新名称与一句话价值 | OPEN；预览默认静音 | 1 秒内可识别主题；移动端可读 |
| 2 | 3–10s | 7s | 截图 1 全貌进入，随后聚焦一个区域 | user asset + HTML/render | 变化一及用户价值 | OPEN | 不遮挡关键 UI；标注与真实界面一致 |
| 3 | 10–17s | 7s | 截图 2，沿用统一版式和聚焦方式 | user asset + HTML/render | 变化二及用户价值 | OPEN | 截图顺序正确；文字不超安全区 |
| 4 | 17–24s | 7s | 截图 3，展示第三项变化 | user asset + HTML/render | 变化三及用户价值 | OPEN | 不裁掉关键内容；无虚构操作 |
| 5 | 24–30s | 6s | 总结卡与 CTA；可保留三张截图的静态缩略概览 | HTML/render planning-only | 总结收益与 CTA | OPEN；若有音轨不得自动播放 | CTA 至少完整停留 3 秒 |

## Motion Direction

- 转场以硬切或 150–250ms 淡化为主。
- 截图只做轻微缩放、平移和高亮；须先确认修改权限。
- 不模拟不存在的点击结果，不生成额外产品界面。
- 禁止用快速闪烁、复杂粒子或音频节拍承担关键信息。
```

## `asset_manifest.json`

```json
{
  "project": "product-update-30s",
  "status": "planning_only",
  "assets": [
    {
      "id": "screenshot-01",
      "type": "image",
      "role": "scene-plate",
      "source": "user-provided",
      "path": "",
      "origin_url": "",
      "license_or_permission": "licensed",
      "permission_evidence": "用户任务声明三张截图已授权；具体文件与授权范围待附",
      "publication_status": "planning_only",
      "provider": "none",
      "linked_ids": ["scene-02"],
      "approval_status": "planning_only",
      "prompt_file": "",
      "duration_seconds": 0,
      "notes": "缺少原文件、分辨率、内容说明及是否允许裁切/标注"
    },
    {
      "id": "screenshot-02",
      "type": "image",
      "role": "scene-plate",
      "source": "user-provided",
      "path": "",
      "origin_url": "",
      "license_or_permission": "licensed",
      "permission_evidence": "用户任务声明三张截图已授权；具体文件与授权范围待附",
      "publication_status": "planning_only",
      "provider": "none",
      "linked_ids": ["scene-03"],
      "approval_status": "planning_only",
      "prompt_file": "",
      "duration_seconds": 0,
      "notes": "缺少原文件、分辨率、内容说明及是否允许裁切/标注"
    },
    {
      "id": "screenshot-03",
      "type": "image",
      "role": "scene-plate",
      "source": "user-provided",
      "path": "",
      "origin_url": "",
      "license_or_permission": "licensed",
      "permission_evidence": "用户任务声明三张截图已授权；具体文件与授权范围待附",
      "publication_status": "planning_only",
      "provider": "none",
      "linked_ids": ["scene-04"],
      "approval_status": "planning_only",
      "prompt_file": "",
      "duration_seconds": 0,
      "notes": "缺少原文件、分辨率、内容说明及是否允许裁切/标注"
    },
    {
      "id": "caption-copy",
      "type": "text",
      "role": "caption",
      "source": "rendered",
      "path": "script.md",
      "origin_url": "",
      "license_or_permission": "user-owned",
      "permission_evidence": "最终文案尚待用户确认",
      "publication_status": "planning_only",
      "provider": "none",
      "linked_ids": ["scene-01", "scene-02", "scene-03", "scene-04", "scene-05"],
      "approval_status": "blocked",
      "prompt_file": "",
      "duration_seconds": 30,
      "notes": "缺少更新名称、三条变化、价值说明和 CTA"
    },
    {
      "id": "font-01",
      "type": "font",
      "role": "render",
      "source": null,
      "path": "",
      "origin_url": "",
      "license_or_permission": "unknown",
      "permission_evidence": "待提供品牌字体及使用许可，或确认可使用已授权系统字体",
      "publication_status": "blocked",
      "provider": "none",
      "linked_ids": ["caption-copy"],
      "approval_status": "blocked",
      "prompt_file": "",
      "duration_seconds": 0,
      "notes": "不得假定品牌字体可商用"
    },
    {
      "id": "voice-open",
      "type": "voice",
      "role": "voice",
      "source": null,
      "path": "",
      "origin_url": "",
      "license_or_permission": "unknown",
      "permission_evidence": "无配音人选，音频方案未决定",
      "publication_status": "planning_only",
      "provider": "none",
      "linked_ids": [],
      "approval_status": "planning_only",
      "prompt_file": "",
      "duration_seconds": 0,
      "notes": "不得擅自选择真人或合成声音"
    },
    {
      "id": "music-open",
      "type": "audio",
      "role": "music",
      "source": null,
      "path": "",
      "origin_url": "",
      "license_or_permission": "unknown",
      "permission_evidence": "音乐使用尚未决定",
      "publication_status": "planning_only",
      "provider": "none",
      "linked_ids": [],
      "approval_status": "planning_only",
      "prompt_file": "",
      "duration_seconds": 0,
      "notes": "默认静音播放不等于最终成片无音乐"
    },
    {
      "id": "sfx-open",
      "type": "audio",
      "role": "music",
      "source": null,
      "path": "",
      "origin_url": "",
      "license_or_permission": "unknown",
      "permission_evidence": "音效使用尚未决定",
      "publication_status": "planning_only",
      "provider": "none",
      "linked_ids": [],
      "approval_status": "planning_only",
      "prompt_file": "",
      "duration_seconds": 0,
      "notes": "若使用，需逐项登记来源和许可"
    }
  ]
}
```

## `edit_plan.json`

```json
{
  "status": "planning_only",
  "platform": "TBD",
  "aspect_ratio": "TBD",
  "duration_seconds": 30,
  "audio_decision_status": "open",
  "default_playback": {
    "autoplay": "platform-dependent",
    "muted": true,
    "sound_requires_user_action": true
  },
  "timeline": [
    {
      "scene": 1,
      "start": 0,
      "end": 3,
      "visual_asset_ids": ["caption-copy", "font-01"],
      "audio_asset_ids": [],
      "caption": "[更新名称] 已上线 / [一句话核心价值]",
      "transition": "cut",
      "qa": ["主题立即可识别", "静音可理解", "安全区内可读"]
    },
    {
      "scene": 2,
      "start": 3,
      "end": 10,
      "visual_asset_ids": ["screenshot-01", "caption-copy", "font-01"],
      "audio_asset_ids": [],
      "caption": "[变化一] / [用户价值]",
      "transition": "fade",
      "qa": ["关键 UI 不被遮挡", "高亮内容可由截图证明"]
    },
    {
      "scene": 3,
      "start": 10,
      "end": 17,
      "visual_asset_ids": ["screenshot-02", "caption-copy", "font-01"],
      "audio_asset_ids": [],
      "caption": "[变化二] / [用户价值]",
      "transition": "cut",
      "qa": ["版式一致", "文字在目标平台可读"]
    },
    {
      "scene": 4,
      "start": 17,
      "end": 24,
      "visual_asset_ids": ["screenshot-03", "caption-copy", "font-01"],
      "audio_asset_ids": [],
      "caption": "[变化三] / [用户价值]",
      "transition": "cut",
      "qa": ["关键内容完整", "无虚构界面或交互"]
    },
    {
      "scene": 5,
      "start": 24,
      "end": 30,
      "visual_asset_ids": ["caption-copy", "font-01"],
      "audio_asset_ids": [],
      "caption": "[总结收益] / [CTA]",
      "transition": "fade",
      "qa": ["CTA 停留至少 3 秒", "静音状态信息完整"]
    }
  ],
  "exports": [
    {
      "format": "mp4",
      "resolution": "TBD after aspect-ratio approval",
      "fps": 30,
      "path": "dist/product-update-30s.mp4",
      "status": "planning_only"
    }
  ]
}
```

## `compose_plan.json`

```json
{
  "status": "blocked",
  "expected_duration_seconds": 30,
  "clip_order": [
    {
      "shot_id": "scene-01",
      "path": "",
      "start": 0,
      "end": 3,
      "duration_seconds": 3
    },
    {
      "shot_id": "scene-02",
      "path": "",
      "start": 3,
      "end": 10,
      "duration_seconds": 7
    },
    {
      "shot_id": "scene-03",
      "path": "",
      "start": 10,
      "end": 17,
      "duration_seconds": 7
    },
    {
      "shot_id": "scene-04",
      "path": "",
      "start": 17,
      "end": 24,
      "duration_seconds": 7
    },
    {
      "shot_id": "scene-05",
      "path": "",
      "start": 24,
      "end": 30,
      "duration_seconds": 6
    }
  ],
  "timeline_sum_check": "pass",
  "duration_deviation": {
    "expected_seconds": 30,
    "actual_seconds": 30,
    "delta_seconds": 0,
    "reason": "",
    "approval_status": "planning_only"
  },
  "clip_count_check": {
    "storyboard_shots": 5,
    "compose_clips": 5,
    "render_command_inputs": 0,
    "result": "blocked"
  },
  "audio_decision": {
    "status": "open",
    "final_track_policy": "不得在确认前锁定为有声或无声",
    "default_playback_muted": true,
    "sound_requires_user_action": true
  },
  "audio_tracks": [],
  "subtitle_policy": {
    "mode": "conditional",
    "rule": "若最终加入旁白，必须提供同步字幕；无论是否有旁白，核心更新信息均以屏幕文字呈现",
    "safe_area": "待目标平台确认",
    "style": "待品牌字体、画幅和平台确认"
  },
  "render_command_template": "PLANNING_ONLY — 选择并确认本地确定性渲染路径后填写",
  "output": {
    "path": "dist/product-update-30s.mp4",
    "container": "mp4",
    "video_codec": "h264 or native equivalent",
    "audio_codec": "aac if an audio track is approved",
    "resolution": "TBD",
    "fps": 30,
    "pixel_format": "yuv420p",
    "video_bitrate": "TBD"
  },
  "ffprobe_metadata": null,
  "inspection_evidence": [],
  "blockers": [
    "三张截图文件未提供",
    "更新文案与 CTA 未提供",
    "平台和画幅未确认",
    "字体未确认",
    "最终音频方案未确认",
    "渲染路径未选择"
  ]
}
```

## `prompts/`

```markdown
不适用。

本项目不需要生成式图片、视频、配音或音乐提示词。若后续授权生成媒体，必须另行建立提示词文件、来源记录、成本记录和输出追踪。
```

## `qa_report.md`

```markdown
# QA Report

| Check | Result | Evidence / blocker |
|---|---|---|
| 规划时间线总长为 30 秒 | pass | 3 + 7 + 7 + 7 + 6 = 30 秒 |
| 最终文件时长为 30 秒 | blocked | 尚未渲染，无媒体元数据 |
| 画幅符合发布平台 | blocked | 平台与画幅未确认 |
| 三张截图均已登记 | pass | asset_manifest.json 中 screenshot-01 至 03 |
| 截图文件可读取且分辨率足够 | blocked | 原文件未提供 |
| 截图授权已声明 | pass at planning level | 用户明确说明三张截图已授权 |
| 裁切、缩放和标注权限明确 | blocked | 授权修改范围未确认 |
| 所有屏幕文字可在静音状态理解 | blocked | 更新文案尚未提供 |
| 字体许可完整 | blocked | 字体未确认 |
| 旁白和最终音频方向已锁定 | blocked | 无配音人选，音乐及音效也保持 open |
| 默认播放不会自动发声 | planning_only | compose_plan 已规定 muted=true、声音需用户主动开启 |
| 若使用旁白则字幕同步 | blocked | 旁白方案尚未决定 |
| 无黑帧、损坏资源或缺失字体 | blocked | 尚未渲染 |
| 画面文字处于平台安全区 | blocked | 平台与画幅未确认 |
| Compose 片段数匹配 storyboard | blocked | 规划均为 5 段，但实际渲染输入为 0 |
| 编码、容器和输出路径已记录 | planning_only | MP4/H.264/yuv420p 为候选；分辨率待定 |
| 最终成片已人工抽查 | blocked | 不存在最终输出文件 |
| 服务调用与成本记录真实 | pass | 未调用生成或渲染服务；未产生已知服务成本 |

## Release Gate

不得进入渲染或发布，直到：

1. 原始截图及其修改授权范围确认；
2. 更新文案与 CTA 批准；
3. 平台、画幅和字体批准；
4. 最终音频方案明确；
5. 渲染路径和导出规格明确。
```
