[Trace: Guyue/MemoryBank] 检索或记录已验证教训；只读取命中项，不暴露私有内容

```yaml
id: MEM-AUTH-BACKEND-ENFORCEMENT-001
summary: 所有权限必须由后端强制控制，前端仅负责体现权限状态。
Symptom: 仅依赖前端隐藏、禁用或限制操作，无法构成可靠的权限控制。
Root Cause: 前端逻辑可被绕过，不能作为权限校验与授权的安全边界。
Solution: 所有权限在后端统一校验和执行；前端根据后端返回的权限结果展示、隐藏或禁用相应功能。
Prevention: 新增或修改受限功能时，必须验证后端具备对应权限校验；不得以仅有前端控制作为完成依据。
provenance: 当前任务中由用户提供，并明确说明为团队确认的长期规则。
scope: 项目全局；适用于所有涉及身份、角色、资源访问和操作授权的功能。
evidence:
  - 团队人工确认：所有权限必须后端控制、前端体现。
confidence: high
status: active
supersedes: []
review_after: 2027-07-13
tags:
  - authorization
  - backend-enforcement
  - frontend-presentation
  - security
  - architecture-decision
timestamp: 2026-07-13T03:52:02Z
```

状态：仅为候选记忆，未写入任何文件。
