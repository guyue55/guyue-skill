## 规范化提取计划

- 模式：`metadata-only`
- 原因：当前仅要求规划与 schema，并明确不执行下载。
- 授权依据：作者允许下载，用途限内部评审。
- 计划资产：
  - `metadata.json`
  - `post_caption.txt`
- 不生成：
  - 源视频文件
  - `transcript.txt`
  - 音频中间文件
- 字幕处理：已知没有字幕，因此不规划平台字幕文件。若后续需要转写，必须另行请求 `transcript` 模式，并先说明 ASR 所需媒体下载、数据边界及可能成本。
- 校验规则：文件实际生成后记录 SHA-256、字节数和验证状态；规划阶段不得虚构摘要值。

当前不能执行实际提取：缺少视频 URL 和平台信息。最小下一步是提供公开视频 URL；若平台无法自动访问，则需用户手动提供平台元数据或媒体文件。

## 结果 schema

```json
{
  "schema_version": "1.0",
  "source": {
    "url": null,
    "platform": null,
    "visibility": "public"
  },
  "extraction": {
    "time": null,
    "selected_mode": "metadata-only",
    "execution_status": "planned_not_executed"
  },
  "authorization": {
    "authorized": true,
    "basis": "Author permits download for internal review",
    "scope": "internal_review",
    "provenance": "user_input"
  },
  "video": {
    "title": "Demo",
    "duration_seconds": 95,
    "post_caption": null,
    "platform_captions_available": false
  },
  "field_provenance": {
    "source.url": "unknown",
    "source.platform": "unknown",
    "source.visibility": "user_input",
    "authorization.authorized": "user_input",
    "authorization.basis": "user_input",
    "authorization.scope": "user_input",
    "video.title": "user_input",
    "video.duration_seconds": "user_input",
    "video.post_caption": "unknown_until_platform_metadata_is_available",
    "video.platform_captions_available": "user_input"
  },
  "assets": [
    {
      "path": "metadata.json",
      "role": "normalized_metadata",
      "status": "planned_not_generated",
      "sha256": null,
      "byte_size": null,
      "verification_status": "not_applicable_before_generation"
    },
    {
      "path": "post_caption.txt",
      "role": "platform_post_caption",
      "status": "blocked_pending_source_url",
      "sha256": null,
      "byte_size": null,
      "verification_status": "not_applicable_before_generation"
    }
  ],
  "asset_counts": {
    "planned": 2,
    "generated": 0,
    "failed": 0
  },
  "blocking_gaps": [
    "source.url",
    "source.platform",
    "video.post_caption"
  ]
}
```
