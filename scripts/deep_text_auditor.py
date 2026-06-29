import os
import glob
import re

def audit_markdown_files():
    print("🔍 Deep Text Auditor: Searching for AI Vagueness and Unfinished Sections\n")
    
    lazy_patterns = [
        (r'TODO|FIXME', "Unfinished tasks"),
        (r'等等|相关内容|进一步的|具体的实现', "Vague filler words"),
        (r'在此处添加|在这添加|填入', "Placeholders"),
        (r'\[.*?\]\(.*?\)', "Check links (will verify if broken manually)")
    ]
    
    issues_found = 0
    md_files = glob.glob('**/*.md', recursive=True)
    
    for filepath in md_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for idx, line in enumerate(lines):
            line_stripped = line.strip()
            # Ignore false positives in auditor scripts themselves
            if 'exhaustive_truth_auditor.py' in filepath or 'deep_text_auditor.py' in filepath:
                continue
                
            for pattern, reason in lazy_patterns:
                if re.search(pattern, line_stripped, flags=re.IGNORECASE):
                    # We might have false positives, just report them
                    print(f"[{reason}] {filepath}:{idx+1} -> {line_stripped[:80]}")
                    issues_found += 1
                    
        # Check for section length (too short means lazy)
        content = "".join(lines)
        sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
        for sec in sections[1:]:
            lines_in_sec = [l for l in sec.split('\n') if l.strip() and not l.startswith('#')]
            if len(lines_in_sec) < 2:
                sec_title = sec.split('\n')[0][:50]
                print(f"[Shallow Section] {filepath} -> Section '## {sec_title}' is too short/empty.")
                issues_found += 1

    if issues_found == 0:
        print("✅ No deep issues found!")
    else:
        print(f"\n❌ Found {issues_found} potential issues to polish.")

if __name__ == '__main__':
    audit_markdown_files()
