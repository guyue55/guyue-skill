#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import discovery_cache_file, ensure_private_directory  # noqa: E402

# 定义可能存在技能的本地扩展目录。这里只保存可移植的家目录写法。
SEARCH_DIRS = [
    "~/.cc-switch/skills",
    "~/.gemini/config/skills",
    "~/.gemini/config/plugins",
    "~/.gemini/antigravity/skills",
    "~/skills"
]

def write_index_atomic(output_file: Path, index: dict[str, str]) -> None:
    ensure_private_directory(output_file.parent)
    temporary = output_file.with_name(f".{output_file.name}.{os.getpid()}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(index, indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(output_file)
        output_file.chmod(0o600)
    finally:
        temporary.unlink(missing_ok=True)


def discover(output_file: Path | None = None):
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

    destination = output_file or discovery_cache_file()
    write_index_atomic(destination, index)

    print(f"✅ 成功发现 {len(index)} 个本地技能并写入可重建缓存: {destination}")
    return destination

if __name__ == "__main__":
    discover()
