#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

def print_status(msg, is_error=False):
    if is_error:
        print(f"❌ {msg}")
    else:
        print(f"✅ {msg}")

def check_dependencies():
    manifest_path = Path(__file__).parent.parent / "skills_manifest.json"
    principles_path = Path(__file__).parent.parent / "GUYUE_PRINCIPLES.md"
    
    if not principles_path.exists():
        print_status("GUYUE_PRINCIPLES.md not found. Architecture broken.", is_error=True)
        sys.exit(1)
        
    if not manifest_path.exists():
        print_status("skills_manifest.json not found", is_error=True)
        sys.exit(1)

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError:
        print_status("Invalid JSON in skills_manifest.json", is_error=True)
        sys.exit(1)

    deps = manifest.get("external_dependencies", [])
    if not deps:
        print_status("No external dependencies found. All good.")
        sys.exit(0)

    # Standard locations where skills might be installed
    home = Path.home()
    search_paths = [
        home / ".gemini/config/skills",
        home / ".cc-switch/skills",
        home / ".codex/skills",
        home / ".cursor/skills"
    ]
    
    # Also check if AGENT_SKILLS_PATH is set
    env_path = os.environ.get("AGENT_SKILLS_PATH") or os.environ.get("SKILLS_PATH")
    if env_path:
        search_paths.insert(0, Path(env_path))

    all_good = True
    missing_deps = []

    print("🩺 正在执行依赖健康探针 (Doctor)...")
    for dep in deps:
        name = dep.get("name")
        package_id = dep.get("package_id")
        command = dep.get("command")
        
        # Determine the likely folder name (usually the repo name or the skill name)
        repo_name = package_id.split("/")[-1] if "/" in package_id else package_id
        
        found = False
        for base_path in search_paths:
            # Check combinations: base/name or base/repo_name
            possible_paths = [
                base_path / name / "SKILL.md",
                base_path / repo_name / "SKILL.md"
            ]
            
            for p in possible_paths:
                if p.exists():
                    found = True
                    print_status(f"依赖正常: {name} ({package_id}) -> Found at {p.parent}")
                    break
            
            if found:
                break
        
        if not found:
            print_status(f"依赖缺失: {name} ({package_id})", is_error=True)
            missing_deps.append((name, command))
            all_good = False

    print("\n--- 探针诊断报告 ---")
    if all_good:
        print("🎉 所有依赖均已就绪，环境健康！")
        sys.exit(0)
    else:
        print("> [!WARNING]")
        print("> ⚠️ 侦测到必要的外部技能缺失，无法继续受控执行。")
        print("> 请用户一键授权以下命令补齐依赖：\n")
        for name, cmd in missing_deps:
            print(f"```bash\n{cmd}\n```\n")
        sys.exit(1)

if __name__ == "__main__":
    check_dependencies()
