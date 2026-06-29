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
            blocks = f.read().split('\n\n')
            for b in blocks:
                b = b.strip()
                if b and not b.startswith('{'):
                    prompts.append(b)
    return prompts

ag_file = os.path.expanduser('~/skills/guyue/references/sources/antigravity_prompts.txt')
codex_file = os.path.expanduser('~/skills/guyue/references/sources/codex_prompts.txt')
prompts = extract_prompts(ag_file, codex_file)

categories = {
    "requirement-analysis": ["需求", "prd", "功能点", "拆解", "脑图", "思维导图", "分析", "用户故事", "user story", "交互", "流程", "分析一下"]
}

samples = defaultdict(list)
for p in prompts:
    p_lower = p.lower()
    for cat, kws in categories.items():
        if any(kw in p_lower for kw in kws):
            clean_p = re.sub(r'```.*?```', '[CODE]', p, flags=re.DOTALL)
            if len(clean_p) > 20:
                samples[cat].append(clean_p)

base_dir = os.path.expanduser('~/skills/guyue/references/research/')
os.makedirs(base_dir, exist_ok=True)
for cat, texts in samples.items():
    if cat == "requirement-analysis": filename = "07-requirement-analysis.md"
    
    with open(os.path.join(base_dir, filename), 'w', encoding='utf-8') as f:
        f.write(f"# 07 - 需求分析与梳理 (Requirements Analysis)\n\n")
        for t in sorted(texts, key=len, reverse=True)[:50]:
            f.write(t + "\n\n---\n\n")

print("Requirement analysis extraction completed.")
