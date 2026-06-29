import os
import re
import sys

def extract_coding_discipline(sessions_dir, antigravity_dir, output_file):
    print(f"Scanning {sessions_dir} and {antigravity_dir} for coding discipline context...")
    
    keywords = [
        "最佳实践", "高内聚", "低耦合", "模块化", "页面化", 
        "降低门槛", "体验", "优先中文", 
        "git 提交", "中文注释", "commit格式", "xxx(xxx)"
    ]
    
    found_snippets = []
    
    def scan_dir(directory):
        if not os.path.exists(directory):
            return
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.jsonl') or file.endswith('.md') or file.endswith('.txt'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Find paragraphs containing our keywords
                            paragraphs = content.split('\n\n')
                            for p in paragraphs:
                                if any(kw in p for kw in keywords):
                                    found_snippets.append(p.strip())
                    except Exception as e:
                        continue
    
    scan_dir(sessions_dir)
    scan_dir(antigravity_dir)
    
    # Deduplicate and clean
    unique_snippets = list(set(found_snippets))
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Coding Discipline Context\n\n")
        for s in unique_snippets[:50]: # Limit to top 50 to avoid massive files
            if len(s) > 20:
                f.write(f"- {s}\n\n")
                
    print(f"Extracted {len(unique_snippets)} snippets to {output_file}")

if __name__ == "__main__":
    extract_coding_discipline(
        os.path.expanduser("~/.codex/sessions/"),
        os.path.expanduser("~/.gemini/antigravity/brain/"),
        os.path.expanduser("~/skills/guyue/references/research/12-coding-discipline.md")
    )
