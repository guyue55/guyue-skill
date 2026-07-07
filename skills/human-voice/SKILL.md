---
name: human-voice
description: Plain-language editing skill for making Guyue outputs sound direct, specific, business-readable, and human-readable without changing facts, sources, authorship, language intent, or risk boundaries. Use when the user asks to "说人话", "去 AI 味", "别写官话", "少点套话", "改得像人能看懂", "像人说话", "业务侧可读", explain technical content to business/product/operations/management readers, avoid unnecessary Chinese-English mixing, default to Simplified Chinese, simplify a response, tighten prose, or remove generic AI phrasing from reports, replies, product copy, release notes, or technical explanations.
---

# human-voice

> [!NOTE]
> This is Guyue's plain-language and anti-AI-slop editing gate. It rewrites text so a real reader can understand the point, trust the evidence, and know the next action. It is not a detector-evasion tool and must not pretend that AI-generated work came from a human.

## Core Job

Turn inflated, generic, or robotic output into clear working language. The goal is not to sound casual; the goal is to help the reader understand, judge, and act without losing truth.

The skill protects four things:

1. **Facts**: keep the original claims, numbers, names, caveats, and source references intact.
2. **Reader**: write for the person who must decide, approve, debug, buy, or continue the work.
3. **Action**: make the next step visible instead of ending with vague encouragement.
4. **Boundary**: keep risk, uncertainty, and limits explicit; never make a weak claim sound proven.

## Plain-Language Contract

Every rewrite must pass these checks:

1. **Understand**: the reader can say what changed, what is known, and what is not known.
2. **Judge**: the reader can see the evidence, tradeoff, risk, cost, or authorization gap behind the conclusion.
3. **Act**: the reader knows the next action, owner, command, file, approval, or blocker when one exists.
4. **Stay true**: facts, numbers, citations, file paths, source type, and authorship claims do not change.
5. **Stay honest**: the rewrite does not market, exaggerate, hide AI assistance, or pretend a human source exists.
6. **Stay consistent**: use the user's language when it is clear; when it is not clear, default normal communication to Simplified Chinese and keep only necessary English identifiers.
7. **Stay business-readable**: for business-facing output, explain the problem, business or user value, main work, cost/risk/limits, and required collaboration roles before adding technical detail.

## When to Use

Use this skill when the user asks for any of these:

- "说人话"
- "去 AI 味"
- "别写官话"
- "少点套话"
- "改得像人能看懂"
- "这段太像 AI 了"
- "把这个回复改自然一点"
- "把这份报告写得更直接"
- "把技术解释讲给业务听"
- "让读者能听懂、能判断、能行动"
- "别营销夸张"
- "不要伪装人工来源"
- "不要中英文混排"
- "默认用简体中文"
- "不需要一键诊断 (Analyze) 这种写法"
- "业务侧可读"
- "讲给产品/运营/管理者听"
- "别堆技术细节"

Also use it as a final editing gate for public-facing Guyue outputs when the draft is correct but sounds generic, inflated, or hard to act on.

## Do Not Use

- Do not use this skill to bypass AI detectors, hide AI involvement, hide authorship, or make false provenance claims.
- Do not use it as persuasive copywriting when the user's real goal is conversion, ads, email sequences, or sales pages; route marketing persuasion to the appropriate copywriting workflow if available.
- Do not use it to turn unsupported claims into marketing language. If evidence is missing, mark it as missing.
- Do not use it for UI visual slop; route UI aesthetic critique to `taste-aesthetics`.
- Do not use it for long-form technical documentation from scratch; route first to `documentation`, then use `human-voice` as the final language pass.
- Do not flatten expert content into simplistic language when precision matters. Explain the term, but keep the term.
- Do not edit files, change facts, add sources, or delete risk language when the user only asked for an expression pass.
- Do not append English glosses to ordinary Chinese labels for style, such as changing "一键诊断" into "一键诊断 (Analyze)".

## Workflow

Start with:

`[Trace: Guyue/HumanVoice] 启用说人话门禁：先锁事实和来源，再删套话，最后检查读者能否听懂、判断、行动。`

### 1. Lock The Facts

Before rewriting, extract the facts that must survive:

- decisions, constraints, dates, versions, commands, file paths, metrics, risks, citations;
- confirmed vs unconfirmed claims;
- source type and authorship claims, including whether text is generated, user-supplied, quoted, inferred, or externally sourced;
- language intent and identifiers that must stay exact, such as product names, brand names, API names, commands, file paths, code symbols, metrics, model names, protocols, and user-provided proper nouns;
- user-provided wording that must be preserved;
- required legal, safety, or technical caveats.

If the draft has unsupported claims, do not make them smoother. Mark them as unsupported or remove them.

### 2. Identify The Reader And Job

Classify the reader in one line:

- developer, operator, product owner, executive, customer, reviewer, or general reader;
- what they need to do after reading: decide, approve, fix, verify, learn, compare, or respond.

The rewrite must serve that job, not just sound polished.

If the reader includes business, product, operations, or management, treat the output as business-facing by default. The reader should understand the value and tradeoffs without needing an engineering background.

### 3. Choose Language And Terminology

Apply these rules before rewriting:

- Use the user's chosen language when the prompt or surrounding context makes it clear.
- If the language is not specified or cannot be inferred, use Simplified Chinese for normal communication.
- Avoid Chinese-English mixed labels when the Chinese phrase is already clear. Write "一键诊断", not "一键诊断 (Analyze)".
- Keep English only when it is required for recognition or exact execution: product names, brand names, API names, CLI commands, file paths, code symbols, metrics, model names, protocols, quoted source text, or user-provided proper nouns.
- When an English term is necessary but unfamiliar to the reader, explain it once in Chinese instead of repeating bilingual labels everywhere.
- When any industry, product, or technical term first appears in business-facing output, add a short "business meaning" explanation. Example: "API（系统之间交换数据的接口）".
- Prefer business-semantic names for方案、功能、阶段 and deliverables. Do not use opaque abbreviations unless the abbreviation is a product name, metric, interface, or widely understood industry term.

### 4. Build The Business-Readable Frame

For each方案 or recommendation in business-facing output, cover these five points:

- **Problem solved**: what customer, workflow, cost, risk, or decision problem it addresses.
- **Business/user value**: what improves for users, operations, revenue, cost, compliance, speed, or quality.
- **Main work**: the 3-5 visible work packages, described in business language.
- **Cost, risk, or limits**: implementation effort, dependency, timing, operational burden, uncertainty, and what is not covered.
- **Collaboration roles**: product, operations, design, engineering, data, legal, customer support, or management owners needed to make it real.

### 5. Remove AI-Slop Markers

Rewrite or delete these patterns:

- empty summary: "总而言之", "综上所述", "这将极大提升效率";
- vague praise: "强大", "先进", "优雅", "丝滑", unless proven by concrete evidence;
- marketing inflation: "革命性", "领先", "全自动", "端到端解决一切", unless the claim is sourced and bounded;
- fake balance: "既...又..." when no tradeoff is stated;
- padded transitions: "值得注意的是", "需要强调的是" when the sentence works without them;
- abstract nouns hiding the actor: "进行优化", "实现提升", "完成赋能";
- disclaimer fog that hides the actual answer;
- over-formatted lists where a short paragraph would be clearer.
- false source cues: "用户调研证明", "客户都认为", "人工撰写", when no such source is present.
- unnecessary bilingual labels: "一键诊断 (Analyze)", "开始分析 (Start Analysis)", "生成报告 (Generate Report)" when the English is not a product, command, metric, or required UI identifier.
- technical-name dumping: long lists of frameworks, APIs, tables, classes, acronyms, or model names that do not affect cost, timeline, risk, or business decision.

### 6. Rewrite In Plain Working Language

Use these rules:

- Lead with the conclusion or required action.
- Prefer short sentences. One sentence should carry one job.
- Use concrete nouns and verbs. Name the owner, file, command, risk, or decision.
- Keep technical terms when they are the correct terms; add a short explanation if the reader may not know them.
- Replace slogans with evidence.
- Keep uncertainty visible: "未验证", "当前证据只证明", "还需要".
- Say "我推断", "当前材料显示", or "这部分未验证" when the source is not direct.
- Keep AI authorship or assistance transparent when it matters; never claim the text came from a human when it did not.
- Keep necessary English identifiers exact; translate the surrounding explanation into Chinese when the reader is Chinese.
- Move deep implementation details into a short "影响成本/周期/风险的技术点" section only when they change a decision.
- End with the next action only when a real next action exists.

### 7. Compare Before And After

For rewrite requests, output this structure unless the user asks for a different format:

```markdown
[Trace: Guyue/HumanVoice] ...

## 改写后
...

## 删改说明
- 保留了：...
- 删除了：...
- 改强了：...
- 未改动的风险/边界：...
```

For normal task answers, do not add a heavy comparison block. Apply the gate silently after the trace and keep the final answer tight.

## Quality Checklist

Before sending the final text, check:

- Could the target reader repeat the main point in 10 seconds?
- Could the reader judge whether the claim is proven, inferred, or still blocked?
- Could the reader take the next action without guessing what file, command, owner, approval, or evidence is needed?
- Did any fact, caveat, citation, or number change?
- Did the rewrite remove empty praise and generic conclusions?
- Does every bullet carry distinct information?
- Is the next action concrete, or absent when no action is needed?
- Does the text avoid claiming human authorship or detector evasion?
- Did the rewrite avoid destructive edits, scope creep, and unsourced source claims?
- Is the output language consistent, with unnecessary bilingual labels removed and required English identifiers preserved?
- If the output is business-facing, does each方案 explain problem, value, main work, cost/risk/limits, and collaboration roles?
- Are required technical terms explained on first use in business language?

## Anti-Patterns

- "本次优化全面提升了系统的稳定性和可维护性。"
  - Better: "这次只改了鉴权缓存失效路径。它降低了重复查询，但还没有覆盖多租户切换场景。"
- "该方案能够显著赋能业务增长。"
  - Better: "该方案减少客服手动查单次数。是否能带来增长，还需要看工单量和转化数据。"
- "从多维度来看，这是一个兼具效率与体验的优秀方案。"
  - Better: "如果目标是两周内上线，选方案 A。它少改数据库，但牺牲了后续扩展空间。"
- "点击一键诊断 (Analyze) 后生成报告 (Generate Report)。"
  - Better: "点击一键诊断后生成报告。"
- "方案 B 采用 RAG、向量库、Embedding、LLM Router 和多 Agent 编排。"
  - Better: "方案 B 先把历史资料整理成可检索知识库，再让系统按问题类型调用合适能力。业务含义：客服和运营不用在多个文档里手动找答案。"

## Cross-Skill Invocation

- Need source-backed README, ADR, PRD, or project orientation first -> use `documentation`, then apply this skill as the final plain-language pass.
- Need UI anti-slop, density, motion, and visual taste -> use `taste-aesthetics`.
- Need value, ROI, or product wording clarity -> use `product-sense` first, then this skill for expression.
- Need marketing persuasion or conversion copy -> use a copywriting workflow, not this skill alone.

## Guardrails

- Preserve truth over tone.
- For business-facing output, lead with business meaning and decision impact, not implementation vocabulary.
- Default normal communication to Simplified Chinese when language is unspecified or unclear.
- Avoid unnecessary Chinese-English mixing; keep English only when it is a required identifier or exact user/source term.
- Never hide uncertainty to make text sound confident.
- Never remove safety, legal, cost, permission, or verification boundaries for readability.
- Never present generated text as human-written.
- Never add fake quotes, fake user research, fake metrics, or fake before/after evidence.
- Never change files or mutate project state during a language-only pass unless the user explicitly asks for file edits.
