#!/usr/bin/env python3
import os
import sys
import json
import yaml
import ast
import importlib.util
import re
import subprocess

def check_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except Exception as e:
        print(f"❌ [JSON LINT ERROR] {file_path}: {e}", file=sys.stderr)
        return False


def check_memory_index(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ [MEMORY INDEX ERROR] {file_path}: {e}", file=sys.stderr)
        return False

    if not isinstance(data, dict) or not isinstance(data.get('memories'), list):
        print(f"❌ [MEMORY INDEX ERROR] {file_path}: expected object with a memories list", file=sys.stderr)
        return False

    required_fields = {'filename', 'tags', 'summary', 'timestamp'}
    for idx, item in enumerate(data['memories']):
        if not isinstance(item, dict):
            print(f"❌ [MEMORY INDEX ERROR] {file_path}: memories[{idx}] must be an object", file=sys.stderr)
            return False
        missing = required_fields - set(item)
        if missing:
            print(f"❌ [MEMORY INDEX ERROR] {file_path}: memories[{idx}] missing {sorted(missing)}", file=sys.stderr)
            return False
        if not isinstance(item.get('tags'), list):
            print(f"❌ [MEMORY INDEX ERROR] {file_path}: memories[{idx}].tags must be a list", file=sys.stderr)
            return False

    return True


def check_manifest_skill_paths(repo_root):
    manifest_path = os.path.join(repo_root, 'skills_manifest.json')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ [MANIFEST ERROR] {manifest_path}: {e}", file=sys.stderr)
        return False

    skills = manifest.get('skills')
    if not isinstance(skills, list):
        print(f"❌ [MANIFEST ERROR] {manifest_path}: skills must be a list", file=sys.stderr)
        return False

    passed = True
    manifest_names = set()
    repo_real = os.path.realpath(repo_root)

    for idx, skill in enumerate(skills):
        if not isinstance(skill, dict):
            print(f"❌ [MANIFEST ERROR] skills[{idx}] must be an object", file=sys.stderr)
            passed = False
            continue

        name = str(skill.get('name', '')).strip()
        rel_path = str(skill.get('path', '')).strip()
        if not name:
            print(f"❌ [MANIFEST ERROR] skills[{idx}] missing name", file=sys.stderr)
            passed = False
            continue
        if name in manifest_names:
            print(f"❌ [MANIFEST ERROR] duplicate skill name: {name}", file=sys.stderr)
            passed = False
        manifest_names.add(name)

        if not rel_path:
            print(f"❌ [MANIFEST ERROR] {name}: missing path", file=sys.stderr)
            passed = False
            continue

        abs_path = os.path.realpath(os.path.join(repo_root, rel_path))
        if not (abs_path == repo_real or abs_path.startswith(repo_real + os.sep)):
            print(f"❌ [MANIFEST ERROR] {name}: path escapes repository: {rel_path}", file=sys.stderr)
            passed = False
            continue
        if not os.path.exists(abs_path):
            print(f"❌ [MANIFEST ERROR] {name}: path not found: {rel_path}", file=sys.stderr)
            passed = False
            continue
        if os.path.basename(abs_path) != 'SKILL.md':
            print(f"❌ [MANIFEST ERROR] {name}: path must point to SKILL.md: {rel_path}", file=sys.stderr)
            passed = False
        if os.path.basename(os.path.dirname(abs_path)) != name:
            print(f"❌ [MANIFEST ERROR] {name}: directory name does not match manifest path {rel_path}", file=sys.stderr)
            passed = False

        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if not content.startswith('---'):
                print(f"❌ [MANIFEST ERROR] {name}: missing frontmatter in {rel_path}", file=sys.stderr)
                passed = False
                continue
            end_idx = content.find('---', 3)
            if end_idx == -1:
                print(f"❌ [MANIFEST ERROR] {name}: unclosed frontmatter in {rel_path}", file=sys.stderr)
                passed = False
                continue
            frontmatter = yaml.safe_load(content[3:end_idx]) or {}
            frontmatter_name = frontmatter.get('name')
            if frontmatter_name != name:
                print(f"❌ [MANIFEST ERROR] {name}: frontmatter name is {frontmatter_name}", file=sys.stderr)
                passed = False
        except Exception as e:
            print(f"❌ [MANIFEST ERROR] {name}: failed to inspect {rel_path}: {e}", file=sys.stderr)
            passed = False

    skills_dir = os.path.join(repo_root, 'skills')
    actual_names = set()
    if os.path.isdir(skills_dir):
        for entry in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, entry, 'SKILL.md')
            if os.path.isfile(skill_path):
                actual_names.add(entry)

    missing_from_manifest = sorted(actual_names - manifest_names)
    missing_from_disk = sorted(manifest_names - actual_names)
    if missing_from_manifest:
        print(f"❌ [MANIFEST ERROR] skill directories missing from manifest: {missing_from_manifest}", file=sys.stderr)
        passed = False
    if missing_from_disk:
        print(f"❌ [MANIFEST ERROR] manifest skills missing from skills/: {missing_from_disk}", file=sys.stderr)
        passed = False

    return passed


def check_skill_markdown(file_path):
    """
    Check if the SKILL.md has valid YAML frontmatter containing 'name' and 'description'
    and scan for hardcoded paths.
    """
    passed = True
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Hardcoded paths check (ignore common examples)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '/Users/' in line or 'C:\\Users\\' in line:
                if '`/Users/apple/...`' not in line and '`/Users/xxx`' not in line:
                    print(f"❌ [SECURITY ERROR] Hardcoded local path found in {file_path}:{i+1}", file=sys.stderr)
                    passed = False
            
        # Frontmatter check
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx != -1:
                frontmatter_str = content[3:end_idx]
                try:
                    data = yaml.safe_load(frontmatter_str)
                    if not data or 'name' not in data or 'description' not in data:
                        print(f"❌ [FRONTMATTER ERROR] Missing 'name' or 'description' in {file_path}", file=sys.stderr)
                        passed = False
                except yaml.YAMLError as e:
                    print(f"❌ [YAML ERROR] Invalid frontmatter in {file_path}: {e}", file=sys.stderr)
                    passed = False
            else:
                print(f"❌ [FRONTMATTER ERROR] Unclosed frontmatter in {file_path}", file=sys.stderr)
                passed = False
        else:
            print(f"❌ [FRONTMATTER ERROR] Missing frontmatter in {file_path}", file=sys.stderr)
            passed = False
            
        return passed
    except Exception as e:
        print(f"❌ [FILE ERROR] Failed to read {file_path}: {e}", file=sys.stderr)
        return False

def check_python_scripts(file_path):
    passed = True
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Hardcoded paths check
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '/Users/' in line or 'C:\\Users\\' in line:
                if '`/Users/apple/...`' not in line and '`/Users/xxx`' not in line:
                    print(f"❌ [SECURITY ERROR] Hardcoded local path found in {file_path}:{i+1}", file=sys.stderr)
                    passed = False

        try:
            ast.parse(content, filename=file_path)
        except SyntaxError as e:
            print(f"❌ [PYTHON SYNTAX ERROR] {file_path}: {e}", file=sys.stderr)
            passed = False
            
        return passed
    except Exception as e:
        print(f"❌ [FILE ERROR] Failed to read {file_path}: {e}", file=sys.stderr)
        return False


def check_mcp_server_paths(repo_root):
    server_path = os.path.join(repo_root, 'src', 'mcp_server.py')
    if not os.path.exists(server_path):
        print(f"❌ [MCP ERROR] {server_path} not found", file=sys.stderr)
        return False

    try:
        spec = importlib.util.spec_from_file_location('guyue_mcp_server_check', server_path)
        module = importlib.util.module_from_spec(spec)
        previous_dont_write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous_dont_write_bytecode
    except Exception as e:
        print(f"❌ [MCP ERROR] Failed to import {server_path}: {e}", file=sys.stderr)
        return False

    expected_manifest = os.path.join(repo_root, 'skills_manifest.json')
    expected_memory = os.path.join(repo_root, '.guyue_memory')
    actual_manifest = os.fspath(module.MANIFEST_FILE)
    actual_memory = os.fspath(module.MEMORY_DIR)

    if actual_manifest != expected_manifest:
        print(f"❌ [MCP ERROR] MANIFEST_FILE points to {actual_manifest}, expected {expected_manifest}", file=sys.stderr)
        return False

    if actual_memory != expected_memory:
        print(f"❌ [MCP ERROR] MEMORY_DIR points to {actual_memory}, expected {expected_memory}", file=sys.stderr)
        return False

    return True


def list_markdown_files(repo_root):
    try:
        output = subprocess.check_output(
            ['git', '-C', repo_root, 'ls-files', '*.md'],
            text=True,
            stderr=subprocess.STDOUT,
        )
        return [os.path.join(repo_root, line) for line in output.splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        markdown_files = []
        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__'}]
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
        return markdown_files


def check_markdown_internal_links(repo_root):
    passed = True
    link_pattern = re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')

    for file_path in list_markdown_files(repo_root):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ [MARKDOWN LINK ERROR] Failed to read {file_path}: {e}", file=sys.stderr)
            passed = False
            continue

        base_dir = os.path.dirname(file_path)
        rel_file = os.path.relpath(file_path, repo_root)
        for match in link_pattern.finditer(content):
            target = match.group(1).split('#', 1)[0].strip()
            if not target:
                continue
            if re.match(r'^[a-z][a-z0-9+.-]*:', target):
                continue
            if target.startswith('/') or target.startswith('~'):
                continue

            target_path = os.path.normpath(os.path.join(base_dir, target))
            if not os.path.exists(target_path):
                print(f"❌ [MARKDOWN LINK ERROR] Broken link in {rel_file}: {match.group(1)}", file=sys.stderr)
                passed = False

    return passed

def main():
    print("🚀 Starting Guyue Perspective CI Validation...")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_passed = True
    
    # 1. Check JSON files
    json_files = ['skills.json', 'test-prompts.json']
    for jf in json_files:
        path = os.path.join(repo_root, jf)
        if os.path.exists(path):
            if not check_json(path):
                all_passed = False
            else:
                print(f"✅ {jf} valid.")

    memory_index = os.path.join(repo_root, '.guyue_memory', 'index.json')
    if os.path.exists(memory_index):
        if not check_memory_index(memory_index):
            all_passed = False
        else:
            print("✅ .guyue_memory/index.json valid.")

    if check_manifest_skill_paths(repo_root):
        print("✅ skills_manifest.json skill paths valid.")
    else:
        all_passed = False

    if check_mcp_server_paths(repo_root):
        print("✅ src/mcp_server.py repository paths valid.")
    else:
        all_passed = False

    if check_markdown_internal_links(repo_root):
        print("✅ tracked markdown internal links valid.")
    else:
        all_passed = False
                
    # 2. Check all SKILL.md files
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__'}]
        if 'references' in root:
            continue
        for file in files:
            if file == 'SKILL.md':
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, repo_root)
                if not check_skill_markdown(path):
                    all_passed = False
                else:
                    print(f"✅ {rel_path} valid.")
                    
            if file.endswith('.py'):
                if file == 'ci_validate_skills.py':
                    continue
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, repo_root)
                if not check_python_scripts(path):
                    all_passed = False
                else:
                    print(f"✅ {rel_path} valid.")

    if not all_passed:
        print("\n❌ CI Validation FAILED. Please fix the errors above.")
        sys.exit(1)
        
    print("\n🎉 CI Validation PASSED. Local skill structure is valid.")

if __name__ == "__main__":
    main()
