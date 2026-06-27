#!/usr/bin/env python3
import os
import re
from collections import defaultdict

def extract_prompts(antigravity_file, codex_file):
    prompts = []
    if os.path.exists(antigravity_file):
        with open(antigravity_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', content, re.DOTALL)
            prompts.extend([m.strip() for m in matches if m.strip()])
            
    if os.path.exists(codex_file):
        with open(codex_file, 'r', encoding='utf-8') as f:
            blocks = f.read().split('

')
            for b in blocks:
                b = b.strip()
                if b and not b.startswith('{'):
                    prompts.append(b)
    return prompts

ag_file = '/Users/apple/skills/guyue-perspective/references/sources/antigravity_prompts.txt'
codex_file = '/Users/apple/skills/guyue-perspective/references/sources/codex_prompts.txt'

prompts = extract_prompts(ag_file, codex_file)

categories = {
    "debugging-mindset": ["报错", "失败", "error", "fix", "bug", "trace", "日志", "为什么", "排查", "修复", "问题"],
    "system-design": ["架构", "设计", "模式", "design", "refactor", "重构", "pattern", "方案", "选型", "类图", "组件拆分"],
    "documentation": ["文档", "总结", "周报", "doc", "readme", "PRD", "规范", "沉淀", "复盘", "写个"],
    "code-review": ["review", "代码审查", "审核", "代码质量", "坏味道", "smell", "规范", "格式化"]
}

counts = defaultdict(int)
samples = defaultdict(list)

for p in prompts:
    p_lower = p.lower()
    for cat, kws in categories.items():
        if any(kw in p_lower for kw in kws):
            counts[cat] += 1
            if len(samples[cat]) < 3 and len(p) > 20:
                clean_p = re.sub(r'```.*?```', '[CODE]', p, flags=re.DOTALL)
                samples[cat].append(clean_p[:150].replace('
', ' '))

print("=== Potential Skills Distribution ===")
for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{cat}: {count} occurrences")
    for s in samples[cat]:
        print(f"  - {s}")
    print()
