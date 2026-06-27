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
    "system-design": ["架构", "设计", "模式", "design", "refactor", "重构", "pattern", "方案", "选型", "类图", "组件拆分"],
    "debugging-mindset": ["报错", "失败", "error", "fix", "bug", "trace", "日志", "为什么", "排查", "修复", "问题"],
    "documentation": ["文档", "总结", "周报", "doc", "readme", "PRD", "规范", "沉淀", "复盘", "写个"]
}

samples = defaultdict(list)
for p in prompts:
    p_lower = p.lower()
    for cat, kws in categories.items():
        if any(kw in p_lower for kw in kws):
            clean_p = re.sub(r'```.*?```', '[CODE]', p, flags=re.DOTALL)
            if len(clean_p) > 20:
                samples[cat].append(clean_p)

# Write output files
base_dir = '/Users/apple/skills/guyue-perspective/references/research/'
for cat, texts in samples.items():
    if cat == "system-design": filename = "08-system-design.md"
    elif cat == "debugging-mindset": filename = "09-debugging-mindset.md"
    elif cat == "documentation": filename = "10-documentation.md"
    
    with open(os.path.join(base_dir, filename), 'w', encoding='utf-8') as f:
        f.write(f"# {cat.upper()} Corpus

")
        # Keep longest 100 prompts to avoid huge files
        for t in sorted(texts, key=len, reverse=True)[:100]:
            f.write(t + "

---

")

print("Files generated successfully.")
