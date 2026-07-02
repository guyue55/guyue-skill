#!/usr/bin/env python3
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 定义可能存在技能的本地扩展目录。这里只保存可移植的家目录写法。
SEARCH_DIRS = [
    "~/.cc-switch/skills",
    "~/.gemini/config/skills",
    "~/.gemini/config/plugins",
    "~/.gemini/antigravity/skills",
    "~/skills"
]

def discover():
    index = {}
    for d in SEARCH_DIRS:
        p = Path(d).expanduser()
        if p.exists():
            # 扫描目录下的 SKILL.md
            for skill_file in p.rglob("SKILL.md"):
                skill_dir = skill_file.parent
                skill_name = skill_dir.name

                # 避免一些不规范的嵌套导致覆盖，优先保留层级浅的
                if skill_name not in index:
                    index[skill_name] = str(skill_dir)

    memory_dir = REPO_ROOT / ".guyue_memory"
    memory_dir.mkdir(exist_ok=True)

    output_file = memory_dir / "local_skills_index.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4, ensure_ascii=False)
        f.write("\n")

    print(f"✅ 成功发现并沉淀了 {len(index)} 个本地技能到知识库: {output_file}")

if __name__ == "__main__":
    discover()
