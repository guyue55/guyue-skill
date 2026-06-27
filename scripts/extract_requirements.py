import os
import re

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

def clean_code_blocks(text):
    return re.sub(r'```.*?```', '[CODE BLOCK REMOVED]', text, flags=re.DOTALL)

def process_and_save():
    base_dir = '/Users/apple/skills/guyue-perspective/references/research/'
    os.makedirs(base_dir, exist_ok=True)
    
    ag_file = '/Users/apple/skills/guyue-perspective/references/sources/antigravity_prompts.txt'
    codex_file = '/Users/apple/skills/guyue-perspective/references/sources/codex_prompts.txt'
    
    prompts = extract_prompts(ag_file, codex_file)
    print(f"Total prompts extracted: {len(prompts)}")
    
    requirements = []
    
    # 关键词扩充：寻找涉及需求、梳理、澄清、产品功能等对话
    keywords = ['需求', '梳理', '分析', '目标', '用户说', '功能', '澄清', '要不要做', '做个什么', '帮我看看这个设计', '业务', '痛点']
    
    for p in prompts:
        clean_p = clean_code_blocks(p)
        
        # 仅保留包含特定关键词的语料
        if any(k in clean_p for k in keywords):
            requirements.append(clean_p)
            
    # 按照长度进行适当排序（过滤太短的无意义语料）
    requirements = [r for r in requirements if len(r) > 50]
    requirements.sort(key=len, reverse=True)
    
    import random
    random.seed(42)
    # 取前 50 个较长且包含需求关键词的语料作为重点参考
    sample_reqs = requirements[:50]
    
    with open(os.path.join(base_dir, '07-requirements.md'), 'w') as f:
        f.write("# 07 - 需求分析与梳理 (Requirements Analysis)\n\n")
        for i, r in enumerate(sample_reqs):
            f.write(f"## 需求场景记录 {i+1}\n{r}\n\n")

    print(f"Extraction complete. Found {len(requirements)} relevant requirement prompts.")

if __name__ == "__main__":
    process_and_save()
