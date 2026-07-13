## 治理合同

| 主体 | 范围 | 动作 | 结果 | 审计要求 |
|---|---|---|---|---|
| 租户管理员 | 当前租户 | 查看成员列表及成员详情 | 允许 | 按现有敏感读取策略记录 |
| 租户管理员 | 其他租户 | 查看成员 | 拒绝 | 记录越权拒绝 |
| 租户管理员 | 任意租户 | 修改平台角色 | 拒绝 | 记录操作者、租户、目标成员、动作及拒绝原因 |
| 平台授权管理员 | 平台范围 | 修改平台角色 | 由平台权限判定 | 成功与失败均记录变更前后值 |

## 实现方案

### 后端权限边界

1. 在既有权限注册表中分别使用两项能力，具体名称沿用项目现有命名：

   - 租户成员读取能力。
   - 平台角色修改能力。

2. 成员查询的 resolver/route 调用 `AuthorizationService.can()` 或既有封装：

   - 租户管理员仅获得当前租户的成员读取能力。
   - 租户范围取自服务端可信会话/授权上下文。
   - 客户端传入的 `tenantId` 不能扩大范围。
   - service/SQL 必须显式带当前租户过滤条件，不能先全量查询再由前端过滤。

3. 平台角色 mutation 在后端独立校验平台权限：

   - 租户管理员即使是目标成员所在租户的管理员，也不能通过。
   - 不使用角色显示名、JWT 角色字符串、`isAdmin` 或直接查成员关系代替授权服务。
   - mutation/service 两层中的既有安全边界必须保留，避免绕过页面后直接调用接口。

4. 拒绝修改平台角色时返回稳定的权限错误，不泄露其他租户或平台角色配置细节。

### `permissionSnapshot` 前端体现

后端生成的快照应表达两项独立能力：

- “可查看本租户成员”：真。
- “可修改平台角色”：假。

前端据此：

- 展示本租户成员入口、列表和详情。
- 平台角色可以只读展示，但编辑、批量修改和提交操作不可用。
- 禁用控件使用中文说明：`平台角色由平台授权管理员维护`。
- API 失败必须显示明确错误态，不能退化为空列表。
- 不按“租户管理员”字符串硬编码页面行为。
- 不把 `permissionSnapshot`、按钮隐藏或禁用当作安全边界；伪造快照也不能绕过后端。

### 审计证据

平台角色修改请求至少记录：

- actor、actor tenant；
- target member、target tenant；
- action、resource；
- 授权结果；
- 拒绝原因或变更前后角色；
- 时间和请求追踪标识。

审计内容不得记录令牌或其他敏感凭据。

## 验收方案

### 后端自动化验收

1. 租户管理员查询当前租户成员：成功，只返回当前租户数据。
2. 当前租户无成员：成功返回空集合，不返回其他租户成员。
3. 租户管理员指定或伪造其他 `tenantId`：拒绝或仍被约束到当前租户。
4. 租户管理员直接调用平台角色 mutation：权限拒绝，数据不变。
5. 租户管理员绕过 resolver 直接触达可调用 service 路径：仍被拒绝。
6. 平台授权管理员修改平台角色：成功，并产生完整审计记录。
7. 普通租户成员查看成员列表：按既有授权合同拒绝。
8. 篡改前端 `permissionSnapshot` 为可编辑：后端仍拒绝修改。
9. 越权和成功修改的审计事件均能关联操作者、目标资源与授权结果。

### 前端验收

1. 快照允许成员读取时，成员入口和列表可见。
2. 快照禁止平台角色修改时：

   - 平台角色为只读；
   - 编辑及批量修改入口不可用；
   - tooltip/说明文案正确；
   - 不发起修改请求。

3. 成员接口返回 403、500 或网络错误时显示错误态和重试入口。
4. 切换租户或刷新会话后重新获取快照，不沿用旧租户权限。
5. 前端定向测试、typecheck、lint、build 全部通过。

### 建议验证门

在真实 NexusFlow checkout 中执行可用的最小集合：

```bash
PYTHONPATH=backend backend/venv/bin/python -m pytest backend/tests/authorization -q
cd frontend && npx vitest run <对应权限测试>
cd frontend && npm run typecheck
cd frontend && npm run lint
cd frontend && npm run build
python3 scripts/permissions/scan_legacy_call_sites.py --check
git diff --check
```

## 当前阻断

当前可读 checkout 实际是 `guyue-skill`，且：

- 不存在 `backend/app/authorization/`；
- 不存在 `frontend/`；
- 不存在 `docs/plans/README.md`；
- `permissionSnapshot` 只出现在工作流 Skill、路由测试及验收样例中，没有 NexusFlow 产品实现；
- 工作树已有大量与本任务无关的修改。

因此目前可以确定治理合同与验收标准，但不能据仓库事实指出具体 resolver、service、组件、权限键或测试文件，也不能声称现有实现通过验收。

最小下一步：提供或切换到包含 NexusFlow 后端、前端及测试的真实 checkout，然后按“授权内核 → 接口/service → `permissionSnapshot` → 页面 → 定向测试”的顺序完成只读落点核验。
