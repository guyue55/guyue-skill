# 输出合同卡

## 标记事实状态

对关键条目使用以下状态之一，并保留来源、时间、适用范围与可推翻条件：

- `已给事实`：用户或给定材料直接提供；只证明材料中出现，不代表外部核验。
- `已核验事实`：已对相称的一手证据执行核验；写明核验活动和边界。
- `来源主张`：可归因于某来源，但真实性或独立性尚未核验。
- `推断`：由已标记证据推导；写明推导链和替代解释。
- `假设`：为继续探索暂时提出，必须能被证伪。
- `冲突`：可信材料之间不一致；并列双方，不强行消解。
- `未知`：当前没有足够证据；说明为什么重要和如何补证。

`决定` 单独记录为下游选择，不冒充事实。不要因来源数量、重复引用或表达自信而升级状态。

## 维护活地图

使用适合媒介的结构承载以下语义，而非强制固定版式：

```yaml
purpose_and_scope: decision, audience, boundaries, freshness, risk
domain_map: vocabulary, entities, relations, institutions, lifecycle
dimensions: observation_axis, inclusion_reason, provenance_anchor, status
source_ecology: branches, incentives, shared_upstreams, missing_voices
challenge_log: original_frame, competing_explanation, discriminating_evidence
revision_log: added, merged, reweighted, removed, unchanged
contradiction_unknown_ledger: item, impact, owner, next_evidence
handoff: downstream_skill, bounded_input, unresolved_gate
stop: reason, evidence_boundary, reopen_trigger
```

字段可折叠但语义不可丢失。地图是可修订状态，不是一次性文章。

## 选择输出形态

- **最小**：用一个紧凑视图给出目的、决定性维度及谱系、关键冲突/未知、一次认知修订、下一证据或停止理由。默认使用。
- **轻量**：为低风险探索补充领域关系、来源生态缺口、反例和下游研究议程。
- **专业**：补充逐项证据状态、竞争解释、引文谱系、修订日志、适用边界和明确交接包。
- **高风险**：在专业形态上增加当前来源核验、独立审计、合格专业人员复核门和“不得据此直接实施”的限制。

输出长度服从用途和风险，不以完整覆盖所有候选维度为目标。

## 使用失败代码

- `CE-INPUT-GAP`：缺少会改变探索方向的输入，且无法安全假设。
- `CE-BOOTSTRAP-INCOMPLETE`：领域语言、关系或来源入口不足以形成地图。
- `CE-EVIDENCE-GAP`：关键主张无相称证据或无法访问。
- `CE-CONFLICT-UNRESOLVED`：冲突会改变结论但当前无法区分。
- `CE-UNTRUSTED-SOURCE`：来源内容与指令混杂，无法安全分离。
- `CE-BUDGET-EXHAUSTED`：时间、Token、成本或轮次预算已耗尽。
- `CE-AUTHORIZATION-REQUIRED`：下一动作需要尚未取得的具体授权。
- `CE-PROFESSIONAL-REVIEW`：高风险用途缺少合格专业人员复核。

失败输出包含：代码、已完成地图、阻塞证据、不能声称什么、最小解阻动作和责任人。

## 写停止声明

使用以下语义收束：

> 停止：`<完成 / 信息增益不足 / 失败代码>`。当前地图足以支持 `<下游动作>`，但不证明 `<边界>`。剩余关键冲突或未知为 `<账本项>`；若出现 `<重新开启条件>`，优先取得 `<最高价值证据>`。

确保地图、证据状态、冲突/未知账本、下游交接和停止理由相互一致；任何一项不同意时，不声明完成。
