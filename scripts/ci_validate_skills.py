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


def load_json_file(file_path, label):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f), True
    except Exception as e:
        print(f"❌ [{label} ERROR] {file_path}: {e}", file=sys.stderr)
        return None, False


def check_project_config(repo_root):
    passed = True
    manifest_path = os.path.join(repo_root, 'skills_manifest.json')
    marketplace_path = os.path.join(repo_root, '.claude-plugin', 'marketplace.json')
    skills_json_path = os.path.join(repo_root, 'skills.json')
    workflow_path = os.path.join(repo_root, '.github', 'workflows', 'ci.yml')
    root_skill_path = os.path.join(repo_root, 'SKILL.md')

    manifest, ok = load_json_file(manifest_path, 'CONFIG')
    passed = passed and ok
    marketplace, ok = load_json_file(marketplace_path, 'CONFIG')
    passed = passed and ok
    skills_json, ok = load_json_file(skills_json_path, 'CONFIG')
    passed = passed and ok

    if not passed:
        return False

    if marketplace.get('name') != 'guyue':
        print(f"❌ [CONFIG ERROR] marketplace name must be guyue, got {marketplace.get('name')}", file=sys.stderr)
        passed = False

    if marketplace.get('entrypoint') != 'SKILL.md':
        print(f"❌ [CONFIG ERROR] marketplace entrypoint must be SKILL.md, got {marketplace.get('entrypoint')}", file=sys.stderr)
        passed = False

    if not os.path.exists(root_skill_path):
        print("❌ [CONFIG ERROR] SKILL.md entrypoint does not exist", file=sys.stderr)
        passed = False

    if manifest.get('version') != marketplace.get('version'):
        print(
            f"❌ [CONFIG ERROR] version mismatch: skills_manifest.json={manifest.get('version')} "
            f"marketplace.json={marketplace.get('version')}",
            file=sys.stderr,
        )
        passed = False

    if skills_json.get('entries') != [{'path': 'skills'}]:
        print(f"❌ [CONFIG ERROR] skills.json entries must be [{{'path': 'skills'}}], got {skills_json.get('entries')}", file=sys.stderr)
        passed = False

    for dep in manifest.get('external_dependencies', []):
        if dep.get('required', False):
            print(f"❌ [CONFIG ERROR] external dependency must be optional in this release: {dep.get('name')}", file=sys.stderr)
            passed = False

    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ [CONFIG ERROR] {workflow_path}: {e}", file=sys.stderr)
        return False

    workflow_text = json.dumps(workflow, ensure_ascii=False)
    required_ci_commands = [
        'pip install -r requirements.txt',
        'python scripts/security_scanner.py',
        'python scripts/ci_validate_skills.py',
        'python scripts/run_eval.py',
    ]
    for command in required_ci_commands:
        if command not in workflow_text:
            print(f"❌ [CONFIG ERROR] GitHub CI missing command: {command}", file=sys.stderr)
            passed = False

    return passed


def check_fixed_install_roots(repo_root):
    forbidden_patterns = [
        '~/skills/' + 'guyue',
    ]
    passed = True

    for file_path in list_release_files(repo_root):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            continue
        except OSError as e:
            print(f"❌ [CONFIG ERROR] Failed to read {file_path}: {e}", file=sys.stderr)
            passed = False
            continue

        rel_path = os.path.relpath(file_path, repo_root)
        for pattern in forbidden_patterns:
            if pattern in content:
                print(f"❌ [CONFIG ERROR] Fixed install root `{pattern}` found in {rel_path}", file=sys.stderr)
                passed = False

    return passed


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
    release_rel_paths = {
        os.path.relpath(path, repo_root).replace(os.sep, '/')
        for path in list_release_files(repo_root)
    }

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
        rel_path_posix = rel_path.replace(os.sep, '/')

        abs_path = os.path.realpath(os.path.join(repo_root, rel_path))
        if not (abs_path == repo_real or abs_path.startswith(repo_real + os.sep)):
            print(f"❌ [MANIFEST ERROR] {name}: path escapes repository: {rel_path}", file=sys.stderr)
            passed = False
            continue
        if not os.path.exists(abs_path):
            print(f"❌ [MANIFEST ERROR] {name}: path not found: {rel_path}", file=sys.stderr)
            passed = False
            continue
        if rel_path_posix not in release_rel_paths:
            print(f"❌ [MANIFEST ERROR] {name}: path is not tracked/staged for release: {rel_path}", file=sys.stderr)
            passed = False
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

    actual_names = set()
    for release_path in release_rel_paths:
        parts = release_path.split('/')
        if len(parts) == 3 and parts[0] == 'skills' and parts[2] == 'SKILL.md':
            actual_names.add(parts[1])

    missing_from_manifest = sorted(actual_names - manifest_names)
    missing_from_disk = sorted(manifest_names - actual_names)
    if missing_from_manifest:
        print(f"❌ [MANIFEST ERROR] release skill files missing from manifest: {missing_from_manifest}", file=sys.stderr)
        passed = False
    if missing_from_disk:
        print(f"❌ [MANIFEST ERROR] manifest skills missing from release file set: {missing_from_disk}", file=sys.stderr)
        passed = False

    return passed


def list_release_files(repo_root):
    try:
        output = subprocess.check_output(
            ['git', '-C', repo_root, 'ls-files'],
            text=True,
            stderr=subprocess.STDOUT,
        )
        return [os.path.join(repo_root, line) for line in output.splitlines() if line.strip()]
    except (FileNotFoundError, subprocess.CalledProcessError):
        release_files = []
        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__'}]
            for file in files:
                release_files.append(os.path.join(root, file))
        return release_files


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
    return [path for path in list_release_files(repo_root) if path.endswith('.md')]


def check_markdown_internal_links(repo_root):
    passed = True
    link_pattern = re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')
    release_rel_paths = {
        os.path.relpath(path, repo_root).replace(os.sep, '/')
        for path in list_release_files(repo_root)
    }

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
            target_rel = os.path.relpath(target_path, repo_root).replace(os.sep, '/')
            if not os.path.exists(target_path):
                print(f"❌ [MARKDOWN LINK ERROR] Broken link in {rel_file}: {match.group(1)}", file=sys.stderr)
                passed = False
            elif target_rel not in release_rel_paths:
                print(
                    f"❌ [MARKDOWN LINK ERROR] Link target is not tracked/staged for release in {rel_file}: {match.group(1)}",
                    file=sys.stderr,
                )
                passed = False

    return passed


def check_skill_resource_references(repo_root):
    passed = True
    resource_pattern = re.compile(r'`((?:references|scripts|assets|examples)/[^` \n]+)`')
    release_rel_paths = {
        os.path.relpath(path, repo_root).replace(os.sep, '/')
        for path in list_release_files(repo_root)
    }

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__'}]
        if 'SKILL.md' not in files:
            continue

        skill_path = os.path.join(root, 'SKILL.md')
        rel_skill = os.path.relpath(skill_path, repo_root).replace(os.sep, '/')
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ [RESOURCE ERROR] Failed to read {rel_skill}: {e}", file=sys.stderr)
            passed = False
            continue

        for match in resource_pattern.finditer(content):
            raw_target = match.group(1).rstrip('.,;:')
            target_path = os.path.normpath(os.path.join(root, raw_target))
            if not os.path.exists(target_path):
                target_path = os.path.normpath(os.path.join(repo_root, raw_target))
            target_rel = os.path.relpath(target_path, repo_root).replace(os.sep, '/')
            if not os.path.exists(target_path):
                print(f"❌ [RESOURCE ERROR] Broken resource reference in {rel_skill}: {raw_target}", file=sys.stderr)
                passed = False
            elif target_rel not in release_rel_paths:
                print(
                    f"❌ [RESOURCE ERROR] Resource is not tracked/staged for release in {rel_skill}: {raw_target}",
                    file=sys.stderr,
                )
                passed = False

    return passed


def check_video_creation_sop_contract(repo_root):
    files = {
        'skill': os.path.join(repo_root, 'skills', 'video-creation-sop', 'SKILL.md'),
        'contract': os.path.join(repo_root, 'skills', 'video-creation-sop', 'references', 'production-contract.md'),
        'learnings': os.path.join(repo_root, 'skills', 'video-creation-sop', 'references', 'short-drama-example-learnings.md'),
        'readme': os.path.join(repo_root, 'README.md'),
        'manifest': os.path.join(repo_root, 'skills_manifest.json'),
        'prompts': os.path.join(repo_root, 'test-prompts.json'),
    }
    passed = True
    contents = {}

    for label, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contents[label] = f.read()
        except Exception as e:
            print(f"❌ [VIDEO SOP ERROR] Failed to read {path}: {e}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    required_needles = {
        'skill': [
            '## Short Drama Stage Gates',
            '`brief.json`',
            '`style_retrieval.md`',
            '`audio_plan.md`',
            '`compose_plan.json`',
            '`run_audit.json`',
            '`production_dossier.md`',
            'approved duration deviation',
            'planned count, generated count, failed count',
            'field_sources',
            'permission evidence',
            'references/short-drama-example-learnings.md',
        ],
        'contract': [
            '## `brief.json`',
            '### `style_retrieval.md`',
            '### `storyboard.md`',
            '### `audio_plan.md`',
            '### `production_dossier.md`',
            '## `compose_plan.json`',
            '## `run_audit.json`',
            '"field_sources"',
            '"required_confirmation_fields"',
            '"permission_evidence"',
            '"publication_status"',
            '"reference_map"',
            '"global_style_prefix"',
            '"identity_lock"',
            '"motion_class"',
            '"engine_params"',
            '"reference_controls"',
            '"continuity_evidence"',
            '"clip_count_check"',
            '"duration_deviation"',
            '"prompt_sections"',
            '"timeline"',
            '"audio_policy"',
            '"subtitle_policy"',
            '"render_command_template"',
            '| Track | Target level | Peak limit | Ducking threshold | Attack | Release |',
            '| Gate | Status | Artifact | Planned | Generated | Failed | Duration deviation | User decision | Next blocked action | Blocker or rework |',
        ],
        'learnings': [
            '## What To Learn',
            '## What Not To Copy Blindly',
            'Lock visual style before script, asset, or keyframe generation',
            'Storyboards must expose timeline math',
            'Do not hide duration drift behind "artistic deviation."',
            'Final composition must compare storyboard shot count, compose clip count, and render command input count.',
            'Real generation runs should end with `run_audit.json`',
            'Final assembly needs its own `compose_plan.json`',
            'Generated media gates must report planned count, generated count, failure count',
            'Preserve field provenance in `brief.json`',
            'Asset manifests must carry permission evidence and publication status',
        ],
        'manifest': [
            '音频计划',
            '字段来源',
            '授权证据',
            '发布状态',
            'field provenance',
            'permission evidence',
            'publication status',
            '全案制作企划书',
            '复刻',
            '成片导出',
            'production dossiers',
        ],
        'readme': [
            '字段来源',
            '授权证据',
            '发布状态',
            '成片合成导出',
        ],
        'prompts': [
            'Trigger Short Drama Stage Gates',
            'Trigger Full Short Drama Example Learning',
            'brief.json',
            'style_retrieval.md',
            'compose_plan.json',
            'run_audit.json',
            'production_dossier.md',
        ],
    }

    for label, needles in required_needles.items():
        for needle in needles:
            if needle not in contents[label]:
                print(f"❌ [VIDEO SOP ERROR] Missing `{needle}` in {os.path.relpath(files[label], repo_root)}", file=sys.stderr)
                passed = False

    return passed


def check_showcase_assets(repo_root):
    demo_gif = os.path.join(repo_root, 'assets', 'demo.gif')
    demo_tape = os.path.join(repo_root, 'assets', 'demo.tape')
    render_script = os.path.join(repo_root, 'scripts', 'render_demo_gif.py')
    release_rel_paths = {
        os.path.relpath(path, repo_root).replace(os.sep, '/')
        for path in list_release_files(repo_root)
    }
    passed = True

    for label, path in {
        'showcase GIF': demo_gif,
        'showcase tape': demo_tape,
        'showcase renderer': render_script,
    }.items():
        rel_path = os.path.relpath(path, repo_root).replace(os.sep, '/')
        if not os.path.exists(path):
            print(f"❌ [SHOWCASE ERROR] Missing {label}: {rel_path}", file=sys.stderr)
            passed = False
        elif rel_path not in release_rel_paths:
            print(f"❌ [SHOWCASE ERROR] {label} is not tracked/staged for release: {rel_path}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    try:
        with open(demo_gif, 'rb') as f:
            header = f.read(6)
        if header not in {b'GIF87a', b'GIF89a'}:
            print("❌ [SHOWCASE ERROR] assets/demo.gif is not a valid GIF file", file=sys.stderr)
            passed = False
    except OSError as e:
        print(f"❌ [SHOWCASE ERROR] Failed to read assets/demo.gif: {e}", file=sys.stderr)
        passed = False

    try:
        with open(demo_tape, 'r', encoding='utf-8') as f:
            tape = f.read()
        if 'Output assets/demo.gif' not in tape:
            print("❌ [SHOWCASE ERROR] assets/demo.tape must render assets/demo.gif", file=sys.stderr)
            passed = False
    except OSError as e:
        print(f"❌ [SHOWCASE ERROR] Failed to read assets/demo.tape: {e}", file=sys.stderr)
        passed = False

    result = subprocess.run(
        [sys.executable, render_script, '--check'],
        cwd=repo_root,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"❌ [SHOWCASE ERROR] render_demo_gif.py --check failed: {result.stderr.strip()}", file=sys.stderr)
        passed = False

    ignored = subprocess.run(
        ['git', '-C', repo_root, 'check-ignore', '--quiet', 'assets/demo.gif'],
        cwd=repo_root,
    )
    if ignored.returncode == 0:
        print("❌ [SHOWCASE ERROR] assets/demo.gif is ignored by git and will be missing from release packaging", file=sys.stderr)
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

    if check_project_config(repo_root):
        print("✅ project configuration files valid.")
    else:
        all_passed = False

    if check_fixed_install_roots(repo_root):
        print("✅ no fixed install-root commands detected.")
    else:
        all_passed = False

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

    if check_skill_resource_references(repo_root):
        print("✅ skill resource references valid.")
    else:
        all_passed = False

    if check_video_creation_sop_contract(repo_root):
        print("✅ video-creation-sop contract valid.")
    else:
        all_passed = False

    if check_showcase_assets(repo_root):
        print("✅ showcase demo assets valid.")
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
