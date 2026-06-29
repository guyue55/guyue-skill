import os
import glob

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix split('\n\n')
    broken_split = "split('" + chr(10) + chr(10) + "')"
    content = content.replace(broken_split, "split('\\n\\n')")

    # Fix replace('\n', ' ')
    broken_replace = "replace('" + chr(10) + "', ' ')"
    content = content.replace(broken_replace, "replace('\\n', ' ')")

    broken_replace_2 = ".replace(chr(10), ' ')"
    content = content.replace(broken_replace_2, ".replace('\\n', ' ')")

    # Fix f.write with newlines
    broken_write_01 = '"# 01 - 系统性输出与架构设计 (Writings)' + chr(10) + chr(10) + '"'
    content = content.replace(broken_write_01, '"# 01 - 系统性输出与架构设计 (Writings)\\n\\n"')

    broken_write_01_b = 'f.write(f"## 核心输出 {i+1}' + chr(10) + '{w}' + chr(10) + chr(10) + '")'
    content = content.replace(broken_write_01_b, 'f.write(f"## 核心输出 {i+1}\\n{w}\\n\\n")')

    broken_write_02 = '"# 02 - 日常互动与调试 (Conversations)' + chr(10) + chr(10) + '"'
    content = content.replace(broken_write_02, '"# 02 - 日常互动与调试 (Conversations)\\n\\n"')

    broken_write_02_b = 'f.write(f"## 互动 {i+1}' + chr(10) + '{c}' + chr(10) + chr(10) + '")'
    content = content.replace(broken_write_02_b, 'f.write(f"## 互动 {i+1}\\n{c}\\n\\n")')

    broken_write_03 = '"# 03 - 表达 DNA 与口头禅 (Expression DNA)' + chr(10) + chr(10) + '"'
    content = content.replace(broken_write_03, '"# 03 - 表达 DNA 与口头禅 (Expression DNA)\\n\\n"')

    broken_write_03_b = '"## 典型短指令样本' + chr(10) + '"'
    content = content.replace(broken_write_03_b, '"## 典型短指令样本\\n"')

    broken_write_03_c = 'f.write(f"- {d.replace(chr(10), \' \')}' + chr(10) + '")'
    content = content.replace(broken_write_03_c, 'f.write(f"- {d.replace(\'\\\\n\', \' \')}\\n")')

    broken_write_05 = '"# 05 - 关键技术与架构决策 (Decisions)' + chr(10) + chr(10) + '"'
    content = content.replace(broken_write_05, '"# 05 - 关键技术与架构决策 (Decisions)\\n\\n"')

    broken_write_05_b = 'f.write(f"## 决策/判定 {i+1}' + chr(10) + '{d}' + chr(10) + chr(10) + '")'
    content = content.replace(broken_write_05_b, 'f.write(f"## 决策/判定 {i+1}\\n{d}\\n\\n")')

    broken_write_cat = 'f.write(f"# {cat.upper()} Corpus' + chr(10) + chr(10) + '")'
    content = content.replace(broken_write_cat, 'f.write(f"# {cat.upper()} Corpus\\n\\n")')

    broken_write_t = 'f.write(t + "' + chr(10) + chr(10) + '---' + chr(10) + chr(10) + '")'
    content = content.replace(broken_write_t, 'f.write(t + "\\n\\n---\\n\\n")')

    # Also fix extract_coding_discipline.py pass
    content = content.replace("except Exception as e:\n                        pass", "except Exception as e:\n                        continue")

    # Also fix ai_log_scanner.py if present
    content = content.replace("except Exception:\n                    pass", "except Exception:\n                    continue")
    content = content.replace("except Exception:\n        pass", "except Exception:\n        return None")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

for p in glob.glob('scripts/*.py'):
    if 'fix_strings' not in p:
        fix_file(p)
