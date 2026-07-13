本地目录中有 2 个语义匹配的开源 CRM 候选：通用 CRM 优先看「悟空CRM」；企业微信私域场景看「LinkWeChat」。

- **名称 (Name)**: 悟空CRM
- **分类 (Category)**: 通用 CRM
- **链接 (URL)**: https://gitee.com/wukongcrm/crm_php
- **推荐理由 (Why)**: 本地目录明确将其描述为开源 CRM，并记录同时支持 PHP、Java。适合作为通用客户关系管理系统的首个评估候选。
- **来源与核对时间 (Source / Checked At)**: 本地目录 `skills/software-advisor/software_catalog.json`；2026-07-13T11:54:01+08:00；链接未联网核对
- **边界 (Boundary)**: 未核验许可证、当前版本、维护活跃度、安全状态、部署要求及 PHP/Java 版本的实际功能差异。

- **名称 (Name)**: LinkWeChat
- **分类 (Category)**: 企业微信 SCRM
- **链接 (URL)**: https://gitee.com/LinkWeChat/link-wechat
- **推荐理由 (Why)**: 本地目录将其描述为基于企业微信的开源 SCRM。仅在需求明确围绕企业微信客户运营时优先考虑。
- **来源与核对时间 (Source / Checked At)**: 本地目录 `skills/software-advisor/software_catalog.json`；2026-07-13T11:54:01+08:00；链接未联网核对
- **边界 (Boundary)**: 未核验许可证、当前版本、维护活跃度、企业微信接口兼容性、安全状态及部署成本。

本地检索方式：

```bash
rg -n -i '"description":.*(CRM|SCRM|客户关系)' \
  skills/software-advisor/software_catalog.json
```

检索得到 4 条字面命中：CRMEB、CRMEB知识付费系统、悟空CRM、LinkWeChat。其中前两项在目录中被描述为商城或知识付费系统，因此排除；CRM 语义候选为 2 个。

目录指纹：

```text
activity: local_catalog_lookup
catalog_path: skills/software-advisor/software_catalog.json
sha256: 7b68f24dfc7aa1b10f0b226013a440f19f4e23a76bde627e16e29d957719e288
observed_at: 2026-07-13T11:54:01+08:00
raw_hits: 4
candidate_count: 2
candidates: [悟空CRM, LinkWeChat]
artifact_ref: response
external_sources: not-applicable
external_version: not-applicable
external_hash: not-applicable
```

本次未联网，也未打开候选项目链接。因此这些结果只是本地目录线索，不能据此判断项目截至目前仍在维护、许可证仍适用或适合生产采用。正式选型前，最小下一步是联网核对两个项目的官方仓库、许可证、最近发布与提交、安全公告及部署文档。
