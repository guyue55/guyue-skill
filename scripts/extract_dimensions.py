#!/usr/bin/env python3
import os
import re
from collections import Counter

def extract_prompts(antigravity_file, codex_file):
    prompts = []
    
    # Antigravity parsing
    if os.path.exists(antigravity_file):
        with open(antigravity_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract everything between <USER_REQUEST> and </USER_REQUEST>
            matches = re.findall(r'<USER_REQUEST>(.*?)</USER_REQUEST>', content, re.DOTALL)
            prompts.extend([m.strip() for m in matches if m.strip()])
            
    # Codex parsing (raw lines or jsonl extracted strings)
    if os.path.exists(codex_file):
        with open(codex_file, 'r', encoding='utf-8') as f:
            # We assume codex prompts are separated by newlines or are just raw text.
            # Some might be huge. Let's read blocks separated by empty lines.
            blocks = f.read().split('

')
            for b in blocks:
                b = b.strip()
                if b and not b.startswith('{'):
                    prompts.append(b)
                    
    return prompts

def clean_code_blocks(text):
    # Remove large code blocks to focus on natural language
    return re.sub(r'```.*?```', '[CODE BLOCK REMOVED]', text, flags=re.DOTALL)

def process_and_save():
    base_dir = os.path.expanduser('~/skills/guyue/references/research/')
    os.makedirs(base_dir, exist_ok=True)
    
    ag_file = os.path.expanduser('~/skills/guyue/references/sources/antigravity_prompts.txt')
    codex_file = os.path.expanduser('~/skills/guyue/references/sources/codex_prompts.txt')
    
    prompts = extract_prompts(ag_file, codex_file)
    print(f"Total prompts extracted: {len(prompts)}")
    
    writings = []
    conversations = []
    dna_candidates = []
    decisions = []
    
    for p in prompts:
        clean_p = clean_code_blocks(p)
        length = len(clean_p)
        
        # Categorize
        if length > 500:
            writings.append(clean_p)
            if '架构' in clean_p or '重构' in clean_p or '方案' in clean_p:
                decisions.append(clean_p)
        elif 100 < length <= 500:
            conversations.append(clean_p)
            if '决定' in clean_p or '改用' in clean_p or '不需要' in clean_p:
                decisions.append(clean_p)
        elif length > 0:
            dna_candidates.append(clean_p)
            
    # Save 01-writings.md (sample top 20 longest)
    writings.sort(key=len, reverse=True)
    with open(os.path.join(base_dir, '01-writings.md'), 'w') as f:
        f.write("# 01 - 系统性输出与架构设计 (Writings)

")
        for i, w in enumerate(writings[:30]):
            f.write(f"## 核心输出 {i+1}
{w}

")
            
    # Save 02-conversations.md (sample random 30)
    import random
    random.seed(42)
    sample_convs = random.sample(conversations, min(40, len(conversations)))
    with open(os.path.join(base_dir, '02-conversations.md'), 'w') as f:
        f.write("# 02 - 日常互动与调试 (Conversations)

")
        for i, c in enumerate(sample_convs):
            f.write(f"## 互动 {i+1}
{c}

")
            
    # Save 03-expression-dna.md (extract top phrases and sample short commands)
    with open(os.path.join(base_dir, '03-expression-dna.md'), 'w') as f:
        f.write("# 03 - 表达 DNA 与口头禅 (Expression DNA)

")
        f.write("## 典型短指令样本
")
        sample_dna = random.sample(dna_candidates, min(50, len(dna_candidates)))
        for d in sample_dna:
            f.write(f"- {d.replace(chr(10), ' ')}
")
            
    # Save 05-decisions.md (all identified decisions)
    with open(os.path.join(base_dir, '05-decisions.md'), 'w') as f:
        f.write("# 05 - 关键技术与架构决策 (Decisions)

")
        for i, d in enumerate(decisions[:30]):
            f.write(f"## 决策/判定 {i+1}
{d}

")

    print("Extraction complete.")

if __name__ == "__main__":
    process_and_save()
