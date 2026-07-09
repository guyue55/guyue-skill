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


def is_git_checkout(repo_root):
    try:
        result = subprocess.run(
            ['git', '-C', repo_root, 'rev-parse', '--show-toplevel'],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return False

    if result.returncode != 0:
        return False

    return os.path.realpath(result.stdout.strip()) == os.path.realpath(repo_root)


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

    if is_git_checkout(repo_root):
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


def check_source_archive_export_rules(repo_root):
    attributes_path = os.path.join(repo_root, '.gitattributes')
    if not os.path.exists(attributes_path):
        if not is_git_checkout(repo_root):
            return True
        print("❌ [ARCHIVE ERROR] .gitattributes is required to filter GitHub source archives", file=sys.stderr)
        return False

    expected_ignored = [
        '.github/workflows/ci.yml',
        '.gitignore',
        '.gitattributes',
        '.guyue_memory/local_skills_index.json',
        'references/sources/example.md',
        'references/research/private-draft.md',
        '__pycache__/cache.pyc',
        '.env',
        'dist/package.tar.gz',
    ]
    expected_included = [
        'SKILL.md',
        'README.md',
        'skills_manifest.json',
        '.guyue_memory/index.json',
        '.guyue_memory/global_context.md',
        'references/research/14-permacomputing-lindy.md',
        'references/research/15-zero-leakage-security.md',
        'assets/demo.gif',
        'scripts/ci_validate_skills.py',
    ]
    paths = expected_ignored + expected_included

    try:
        output = subprocess.check_output(
            ['git', '-C', repo_root, 'check-attr', '--stdin', 'export-ignore'],
            input='\n'.join(paths) + '\n',
            text=True,
            stderr=subprocess.STDOUT,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"❌ [ARCHIVE ERROR] Failed to inspect export-ignore attributes: {e}", file=sys.stderr)
        return False

    attrs = {}
    for line in output.splitlines():
        parts = line.split(': ', 2)
        if len(parts) == 3:
            attrs[parts[0]] = parts[2]

    passed = True
    for path in expected_ignored:
        if attrs.get(path) != 'set':
            print(f"❌ [ARCHIVE ERROR] {path} must be excluded from GitHub source archives", file=sys.stderr)
            passed = False

    for path in expected_included:
        if attrs.get(path) == 'set':
            print(f"❌ [ARCHIVE ERROR] {path} must remain in GitHub source archives", file=sys.stderr)
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
            print(f"❌ [MANIFEST ERROR] {name}: path is not included in the release source archive: {rel_path}", file=sys.stderr)
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
        print(f"❌ [MANIFEST ERROR] source-archive skill files missing from manifest: {missing_from_manifest}", file=sys.stderr)
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
        tracked_files = [line for line in output.splitlines() if line.strip()]
        if not tracked_files:
            return []

        attr_output = subprocess.check_output(
            ['git', '-C', repo_root, 'check-attr', '--stdin', 'export-ignore'],
            input='\n'.join(tracked_files) + '\n',
            text=True,
            stderr=subprocess.STDOUT,
        )
        ignored = {
            line.split(': ', 2)[0]
            for line in attr_output.splitlines()
            if line.endswith(': export-ignore: set')
        }
        return [os.path.join(repo_root, line) for line in tracked_files if line not in ignored]
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
                    f"❌ [MARKDOWN LINK ERROR] Link target is not included in the release source archive in {rel_file}: {match.group(1)}",
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
                    f"❌ [RESOURCE ERROR] Resource is not included in the release source archive in {rel_skill}: {raw_target}",
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


def check_human_voice_language_contract(repo_root):
    files = {
        'principles': os.path.join(repo_root, 'GUYUE_PRINCIPLES.md'),
        'root_skill': os.path.join(repo_root, 'SKILL.md'),
        'human_voice': os.path.join(repo_root, 'skills', 'human-voice', 'SKILL.md'),
        'manifest': os.path.join(repo_root, 'skills_manifest.json'),
        'prompts': os.path.join(repo_root, 'test-prompts.json'),
        'readme': os.path.join(repo_root, 'README.md'),
        'replay': os.path.join(repo_root, 'examples', 'quickstart-output.md'),
    }
    passed = True
    contents = {}

    for label, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contents[label] = f.read()
        except Exception as e:
            print(f"❌ [HUMAN VOICE ERROR] Failed to read {path}: {e}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    required_needles = {
        'principles': [
            '默认使用简体中文',
            '不写成“一键诊断 (Analyze)”',
            '语言先一致',
            '英文只保留必要项',
        ],
        'root_skill': [
            '默认简体中文',
            '不必要的中英文混排',
            '产品、品牌、接口、命令、文件、指标、模型和协议名',
        ],
        'human_voice': [
            '### 3. Choose Language And Terminology',
            'Simplified Chinese',
            '一键诊断 (Analyze)',
            'unnecessary bilingual labels',
            'required for recognition or exact execution',
            'product names',
            'API names',
            'commands',
            'file paths',
            'metrics',
            'model names',
            'protocols',
        ],
        'readme': [
            '默认正常沟通用简体中文',
            '避免不必要中英文混排',
        ],
        'replay': [
            'Replay 14: Human Voice Language Default And Mixed Labels',
            '一键诊断',
            '生成报告',
            'required English identifiers',
        ],
    }

    for label, needles in required_needles.items():
        for needle in needles:
            if needle not in contents[label]:
                print(f"❌ [HUMAN VOICE ERROR] Missing `{needle}` in {os.path.relpath(files[label], repo_root)}", file=sys.stderr)
                passed = False

    try:
        manifest = json.loads(contents['manifest'])
    except Exception as e:
        print(f"❌ [HUMAN VOICE ERROR] Failed to parse skills_manifest.json: {e}", file=sys.stderr)
        return False

    human_voice = next((skill for skill in manifest.get('skills', []) if skill.get('name') == 'human-voice'), None)
    if not human_voice:
        print("❌ [HUMAN VOICE ERROR] human-voice missing from skills_manifest.json", file=sys.stderr)
        passed = False
    else:
        triggers = set(human_voice.get('trigger_intent', []))
        for trigger in {'中英文混排', '简体中文', '默认中文'}:
            if trigger not in triggers:
                print(f"❌ [HUMAN VOICE ERROR] Missing human-voice trigger: {trigger}", file=sys.stderr)
                passed = False
        description = str(human_voice.get('description', ''))
        for needle in {'language intent', 'Chinese-English mixing'}:
            if needle not in description:
                print(f"❌ [HUMAN VOICE ERROR] human-voice manifest description missing `{needle}`", file=sys.stderr)
                passed = False

    try:
        prompts = json.loads(contents['prompts'])
    except Exception as e:
        print(f"❌ [HUMAN VOICE ERROR] Failed to parse test-prompts.json: {e}", file=sys.stderr)
        return False

    prompt = next((item for item in prompts if item.get('name') == 'Human Voice Boundary - Simplified Chinese And Mixed Labels'), None)
    if not prompt:
        print("❌ [HUMAN VOICE ERROR] Missing Simplified Chinese mixed-label prompt", file=sys.stderr)
        passed = False
    else:
        prompt_text = json.dumps(prompt, ensure_ascii=False)
        for needle in ['Simplified Chinese', '一键诊断 (Analyze)', 'required identifier']:
            if needle not in prompt_text:
                print(f"❌ [HUMAN VOICE ERROR] Mixed-label prompt missing `{needle}`", file=sys.stderr)
                passed = False

    return passed


def check_business_readable_output_contract(repo_root):
    files = {
        'principles': os.path.join(repo_root, 'GUYUE_PRINCIPLES.md'),
        'root_skill': os.path.join(repo_root, 'SKILL.md'),
        'human_voice': os.path.join(repo_root, 'skills', 'human-voice', 'SKILL.md'),
        'documentation': os.path.join(repo_root, 'skills', 'documentation', 'SKILL.md'),
        'requirement_analysis': os.path.join(repo_root, 'skills', 'requirement-analysis', 'SKILL.md'),
        'product_sense': os.path.join(repo_root, 'skills', 'product-sense', 'SKILL.md'),
        'system_design': os.path.join(repo_root, 'skills', 'system-design', 'SKILL.md'),
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
            print(f"❌ [BUSINESS READABLE ERROR] Failed to read {path}: {e}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    required_needles = {
        'principles': [
            '业务侧可读',
            '解决什么问题、带来什么业务/用户价值、主要要做什么、成本风险限制是什么、需要哪些角色配合',
            '术语先解释',
            '命名先可沟通',
        ],
        'root_skill': [
            '业务侧可读 (Business-Readable Output)',
            '业务问题、用户价值、主要工作、成本风险限制和协作角色',
            '必要术语首次出现必须解释业务含义',
        ],
        'human_voice': [
            'Stay business-readable',
            'Build The Business-Readable Frame',
            'Problem solved',
            'Business/user value',
            'Collaboration roles',
            'business meaning',
        ],
        'documentation': [
            'Business-Facing Output Mode',
            '这个方案解决什么问题',
            '对业务/用户有什么价值',
            '成本、风险或限制',
            '需要哪些角色配合',
            '必要术语解释',
        ],
        'requirement_analysis': [
            '业务价值 (Business Value)',
            '主要工作 (Main Work)',
            '成本风险限制 (Cost/Risk/Limits)',
            '协作角色 (Collaboration Roles)',
            '术语解释 (Terms)',
        ],
        'product_sense': [
            '解决什么问题',
            '对业务/用户有什么价值',
            '有什么成本、风险或限制',
            '业务语义命名',
        ],
        'system_design': [
            '业务可读方案推演',
            '成本风险限制',
            '协作角色',
            '技术细节边界',
        ],
    }

    for label, needles in required_needles.items():
        for needle in needles:
            if needle not in contents[label]:
                print(f"❌ [BUSINESS READABLE ERROR] Missing `{needle}` in {os.path.relpath(files[label], repo_root)}", file=sys.stderr)
                passed = False

    try:
        manifest = json.loads(contents['manifest'])
    except Exception as e:
        print(f"❌ [BUSINESS READABLE ERROR] Failed to parse skills_manifest.json: {e}", file=sys.stderr)
        return False

    skill_map = {skill.get('name'): skill for skill in manifest.get('skills', [])}
    expected_manifest = {
        'human-voice': {
            'triggers': {'业务侧可读', '讲给业务听', '讲给产品听', '讲给运营听'},
            'description': {'business-readable'},
        },
        'documentation': {
            'triggers': {'业务侧可读', '业务汇报'},
            'description': {'business-readable'},
        },
        'requirement-analysis': {
            'triggers': {'业务侧需求', '业务可读需求'},
            'description': {'business-readable', 'cost/risk'},
        },
        'product-sense': {
            'triggers': {'业务价值', '业务侧方案'},
            'description': {'Business-readable', 'user impact'},
        },
        'system-design': {
            'triggers': {'业务侧架构方案', '业务可读方案'},
            'description': {'business-readable'},
        },
    }

    for skill_name, expected in expected_manifest.items():
        skill = skill_map.get(skill_name)
        if not skill:
            print(f"❌ [BUSINESS READABLE ERROR] {skill_name} missing from skills_manifest.json", file=sys.stderr)
            passed = False
            continue
        triggers = set(skill.get('trigger_intent', []))
        for trigger in expected['triggers']:
            if trigger not in triggers:
                print(f"❌ [BUSINESS READABLE ERROR] Missing {skill_name} trigger: {trigger}", file=sys.stderr)
                passed = False
        description = str(skill.get('description', ''))
        for needle in expected['description']:
            if needle not in description:
                print(f"❌ [BUSINESS READABLE ERROR] {skill_name} manifest description missing `{needle}`", file=sys.stderr)
                passed = False

    try:
        prompts = json.loads(contents['prompts'])
    except Exception as e:
        print(f"❌ [BUSINESS READABLE ERROR] Failed to parse test-prompts.json: {e}", file=sys.stderr)
        return False

    prompt = next((item for item in prompts if item.get('name') == 'Business-Readable Output Contract'), None)
    if not prompt:
        print("❌ [BUSINESS READABLE ERROR] Missing business-readable output prompt", file=sys.stderr)
        passed = False
    else:
        prompt_text = json.dumps(prompt, ensure_ascii=False)
        for needle in ['业务侧可读', 'problem solved', 'business or user value', 'collaboration roles', 'business-semantic names']:
            if needle not in prompt_text:
                print(f"❌ [BUSINESS READABLE ERROR] Business-readable prompt missing `{needle}`", file=sys.stderr)
                passed = False

    return passed


def check_reuse_first_engineering_contract(repo_root):
    files = {
        'principles': os.path.join(repo_root, 'GUYUE_PRINCIPLES.md'),
        'root_skill': os.path.join(repo_root, 'SKILL.md'),
        'system_design': os.path.join(repo_root, 'skills', 'system-design', 'SKILL.md'),
        'coding_discipline': os.path.join(repo_root, 'skills', 'coding-discipline', 'SKILL.md'),
        'code_minimalism': os.path.join(repo_root, 'skills', 'code-minimalism', 'SKILL.md'),
        'frontend_expert': os.path.join(repo_root, 'skills', 'frontend-expert', 'SKILL.md'),
        'manifest': os.path.join(repo_root, 'skills_manifest.json'),
        'prompts': os.path.join(repo_root, 'test-prompts.json'),
        'replay': os.path.join(repo_root, 'examples', 'quickstart-output.md'),
        'replay': os.path.join(repo_root, 'examples', 'quickstart-output.md'),
    }
    passed = True
    contents = {}

    for label, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contents[label] = f.read()
        except Exception as e:
            print(f"❌ [REUSE FIRST ERROR] Failed to read {path}: {e}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    required_needles = {
        'principles': [
            '标准件管家',
            '开发前先做复用扫描',
            '函数、模型、表格、配置、常量、全局参数、接口契约',
            '同一业务语义或工程能力被使用两次及以上',
            '不把“复用”理解成过早抽象',
        ],
        'root_skill': [
            '复用优先 (Reuse-First Engineering)',
            '函数、模型、表格、配置、常量、全局参数、接口契约',
            '第二次出现的函数、模型、表格、配置、常量、全局参数、接口契约',
        ],
        'system_design': [
            '关键工程标准件必须有单一权威入口',
            '领域模型、数据库表、枚举、全局参数、配置、接口契约',
            '标准件与契约归一',
            '不得让同一个模型、表格、全局参数、接口契约',
        ],
        'coding_discipline': [
            '拒绝重复造件',
            '拒绝错误抽象',
            '复用扫描',
            '二次使用即抽象',
            'models/',
            'schemas/',
            'migrations/',
            'parameters/',
            'scripts/',
        ],
        'code_minimalism': [
            '复用扫描',
            '二次使用即抽象',
            '函数、模型、表结构、配置、全局参数、接口契约',
            '只是偶然相似',
        ],
        'frontend_expert': [
            '如果是第二次出现的 UI 或交互，必须组件化',
            '先查标准件',
            '拒绝重复 UI',
            '弹窗、Toast、空状态、加载态、权限提示',
        ],
        'replay': [
            'Replay 20: Reuse-First Engineering Contract',
            '[Trace: Guyue/CodingDiscipline]',
            '[Ponytail Check]',
            '函数、服务、模型、表结构、迁移、常量、配置、全局参数、接口契约、权限规则、弹窗、提示文案、工具脚本、测试夹具',
            '本轮我只说明处理方式，不修改文件',
        ],
    }

    for label, needles in required_needles.items():
        for needle in needles:
            if needle not in contents[label]:
                print(f"❌ [REUSE FIRST ERROR] Missing `{needle}` in {os.path.relpath(files[label], repo_root)}", file=sys.stderr)
                passed = False

    try:
        manifest = json.loads(contents['manifest'])
    except Exception as e:
        print(f"❌ [REUSE FIRST ERROR] Failed to parse skills_manifest.json: {e}", file=sys.stderr)
        return False

    skill_map = {skill.get('name'): skill for skill in manifest.get('skills', [])}
    expected_manifest = {
        'coding-discipline': {
            'triggers': {'避免重复实现', '复用已有组件', '抽象公共逻辑', '工程标准件', '单一权威入口', '统一模型', '统一表格', '全局参数'},
            'description': {'reuse-first checks', 'models', 'tables', 'parameters', 'API contracts', 'scripts'},
        },
        'system-design': {
            'triggers': {'统一模型', '统一接口契约', '全局参数'},
            'description': {'single-source contracts', 'models', 'tables', 'parameters', 'APIs'},
        },
        'frontend-expert': {
            'triggers': {'复用组件', '统一弹窗', '统一提示'},
            'description': {'reuse-first UI standardization', 'dialogs', 'toasts'},
        },
        'code-minimalism': {
            'triggers': {'重复代码', '二次使用即抽象'},
            'description': {'reuse-first', 'duplicate-code'},
        },
    }

    for skill_name, expected in expected_manifest.items():
        skill = skill_map.get(skill_name)
        if not skill:
            print(f"❌ [REUSE FIRST ERROR] {skill_name} missing from skills_manifest.json", file=sys.stderr)
            passed = False
            continue
        triggers = set(skill.get('trigger_intent', []))
        for trigger in expected['triggers']:
            if trigger not in triggers:
                print(f"❌ [REUSE FIRST ERROR] Missing {skill_name} trigger: {trigger}", file=sys.stderr)
                passed = False
        description = str(skill.get('description', ''))
        for needle in expected['description']:
            if needle not in description:
                print(f"❌ [REUSE FIRST ERROR] {skill_name} manifest description missing `{needle}`", file=sys.stderr)
                passed = False

    try:
        prompts = json.loads(contents['prompts'])
    except Exception as e:
        print(f"❌ [REUSE FIRST ERROR] Failed to parse test-prompts.json: {e}", file=sys.stderr)
        return False

    prompt = next((item for item in prompts if item.get('name') == 'Reuse-First Engineering Contract'), None)
    if not prompt:
        print("❌ [REUSE FIRST ERROR] Missing reuse-first engineering prompt", file=sys.stderr)
        passed = False
    else:
        prompt_text = json.dumps(prompt, ensure_ascii=False)
        for needle in ['已有函数', '模型', '表格', '全局参数', '接口契约', 'two or more real usage points', 'single authoritative entry', 'wrong abstractions']:
            if needle not in prompt_text:
                print(f"❌ [REUSE FIRST ERROR] Reuse-first prompt missing `{needle}`", file=sys.stderr)
                passed = False

    return passed


def check_development_defaults_contract(repo_root):
    files = {
        'principles': os.path.join(repo_root, 'GUYUE_PRINCIPLES.md'),
        'root_skill': os.path.join(repo_root, 'SKILL.md'),
        'system_design': os.path.join(repo_root, 'skills', 'system-design', 'SKILL.md'),
        'coding_discipline': os.path.join(repo_root, 'skills', 'coding-discipline', 'SKILL.md'),
        'frontend_expert': os.path.join(repo_root, 'skills', 'frontend-expert', 'SKILL.md'),
        'manifest': os.path.join(repo_root, 'skills_manifest.json'),
        'prompts': os.path.join(repo_root, 'test-prompts.json'),
        'replay': os.path.join(repo_root, 'examples', 'quickstart-output.md'),
    }
    passed = True
    contents = {}

    for label, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contents[label] = f.read()
        except Exception as e:
            print(f"❌ [DEVELOPMENT DEFAULTS ERROR] Failed to read {path}: {e}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    required_needles = {
        'principles': [
            '全栈开发守门人',
            '权限分层者',
            '前端、后端、数据、脚本、配置、基础设施和文档',
            '降低使用门槛、提高体验、默认中文可读',
            '权限相关改动必须后端先兜底、前端再体现',
            '提交信息使用 `type(scope): 中文描述`',
            '`build`、`lint`、测试、安全扫描和缓存检查',
            '只有任务涉及前端或 UI 设计',
            '后端、数据、脚本、配置和基础设施任务仍按全栈开发守则执行',
        ],
        'root_skill': [
            '全栈开发默认守则 (Full-Stack Development Defaults)',
            '所有开发都必须遵守',
            '最佳实践、必要注释、高内聚、低耦合、模块化和页面化',
            '权限必须后端控制、前端体现',
            '`build`、`lint`、测试、安全扫描和缓存检查',
            '`type(scope): 中文描述`',
            '只有涉及前端或 UI 设计且用户未指定其他工作流时',
            '任何前端、后端、数据、脚本、配置、基础设施或文档实现',
        ],
        'system_design': [
            '权限架构必须后端控制、前端体现',
            '权限与体验分层',
            '后端授权点',
            '前端权限状态来源',
            '不得把前端硬编码当成安全策略',
        ],
        'coding_discipline': [
            '古月全栈开发纪律套件',
            '前端、后端、数据、脚本、配置、基础设施、文档或 UI 开发',
            '后端权限为准',
            '最佳实践底线',
            '必要注释、清晰命名、高内聚、低耦合、模块化和页面化',
            '全栈阵线对齐',
            '非前端任务不套用前端工作流',
            '权限分层检查',
            '`build`、`lint`、单元测试、集成测试、类型检查、格式检查、安全扫描和缓存检查',
            '`type(scope): 中文描述`',
            '`gsap-core` 与 `ui-ux-pro-max`',
        ],
        'frontend_expert': [
            '默认参考外部美学工作流',
            '`gsap-core` 的动画编排纪律',
            '`ui-ux-pro-max` 的商业级 UI 审美约束',
            '不替代后端权限',
        ],
        'replay': [
            'Replay 21: Development Defaults Contract',
            '[Trace: Guyue/Requirement-System-Frontend-Coding]',
            '后端作为真实权限边界',
            '前端只消费后端返回的权限状态',
            'build',
            'lint',
            'gsap-core',
            'ui-ux-pro-max',
            '本轮按你的要求只说明处理方式，不修改文件',
        ],
    }

    for label, needles in required_needles.items():
        for needle in needles:
            if needle not in contents[label]:
                print(f"❌ [DEVELOPMENT DEFAULTS ERROR] Missing `{needle}` in {os.path.relpath(files[label], repo_root)}", file=sys.stderr)
                passed = False

    try:
        manifest = json.loads(contents['manifest'])
    except Exception as e:
        print(f"❌ [DEVELOPMENT DEFAULTS ERROR] Failed to parse skills_manifest.json: {e}", file=sys.stderr)
        return False

    skill_map = {skill.get('name'): skill for skill in manifest.get('skills', [])}
    expected_manifest = {
        'coding-discipline': {
            'triggers': {'最佳实践', '高内聚低耦合', 'build lint', '后端控制权限', '中文提交'},
            'description': {'Full-stack implementation', 'frontend, backend, data, scripts, configuration, infrastructure, and documentation changes', 'best practices', 'necessary comments', 'high cohesion', 'low coupling', 'backend-owned permission checks', 'build/lint/test validation gates', 'Chinese conventional commits', 'frontend-expert only when UI work is involved'},
        },
        'system-design': {
            'triggers': {'权限分层', '后端控制权限'},
            'description': {'backend-owned permission boundaries', 'frontend permission presentation'},
        },
        'frontend-expert': {
            'triggers': {'gsap-core', 'ui-ux-pro-max'},
            'description': {'default gsap-core and ui-ux-pro-max workflow alignment'},
        },
    }

    for skill_name, expected in expected_manifest.items():
        skill = skill_map.get(skill_name)
        if not skill:
            print(f"❌ [DEVELOPMENT DEFAULTS ERROR] {skill_name} missing from skills_manifest.json", file=sys.stderr)
            passed = False
            continue
        triggers = set(skill.get('trigger_intent', []))
        for trigger in expected['triggers']:
            if trigger not in triggers:
                print(f"❌ [DEVELOPMENT DEFAULTS ERROR] Missing {skill_name} trigger: {trigger}", file=sys.stderr)
                passed = False
        description = str(skill.get('description', ''))
        for needle in expected['description']:
            if needle not in description:
                print(f"❌ [DEVELOPMENT DEFAULTS ERROR] {skill_name} manifest description missing `{needle}`", file=sys.stderr)
                passed = False

    try:
        prompts = json.loads(contents['prompts'])
    except Exception as e:
        print(f"❌ [DEVELOPMENT DEFAULTS ERROR] Failed to parse test-prompts.json: {e}", file=sys.stderr)
        return False

    prompt = next((item for item in prompts if item.get('name') == 'Development Defaults Contract'), None)
    if not prompt:
        print("❌ [DEVELOPMENT DEFAULTS ERROR] Missing development defaults prompt", file=sys.stderr)
        passed = False
    else:
        prompt_text = json.dumps(prompt, ensure_ascii=False)
        for needle in ['full-stack development baseline', 'frontend, backend, data, scripts, configuration, infrastructure, and documentation changes', 'frontend-expert` only when UI work is involved', 'best practices', 'necessary comments', 'high-cohesion', 'backend-owned', 'frontend permission presentation', 'build, lint, tests', 'type(scope): 中文描述', 'gsap-core', 'ui-ux-pro-max', 'only when UI/front-end guidance is unspecified']:
            if needle not in prompt_text:
                print(f"❌ [DEVELOPMENT DEFAULTS ERROR] Development defaults prompt missing `{needle}`", file=sys.stderr)
                passed = False

    return passed


def check_context_compressor_budget_contract(repo_root):
    files = {
        'root_skill': os.path.join(repo_root, 'SKILL.md'),
        'context_compressor': os.path.join(repo_root, 'skills', 'context-compressor', 'SKILL.md'),
        'ecosystem_scout': os.path.join(repo_root, 'skills', 'ecosystem-scout', 'SKILL.md'),
        'manifest': os.path.join(repo_root, 'skills_manifest.json'),
        'prompts': os.path.join(repo_root, 'test-prompts.json'),
        'replay': os.path.join(repo_root, 'examples', 'quickstart-output.md'),
    }
    passed = True
    contents = {}

    for label, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contents[label] = f.read()
        except Exception as e:
            print(f"❌ [CONTEXT BUDGET ERROR] Failed to read {path}: {e}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    required_needles = {
        'root_skill': [
            '上下文过长、节省 token、MCP 工具太多、工具输出太长',
            '不新建 `context-budget-manager`',
            '第三方工具看起来特别适合当前任务',
            '`context-compressor` -> `ecosystem-scout` -> `security-gate`',
            '没有明确授权前只给安装计划',
        ],
        'context_compressor': [
            'Agent 上下文预算管家',
            '先判断钱花在哪',
            '定位浪费源',
            '选择压缩处方',
            '量化节省口径',
            'MCP 工具定义过多',
            '工具输出过长',
            'Headroom',
            'Serena MCP',
            'Repomix / Gitingest',
            'Context7',
            'MCP compressor / Context Mode',
            '第三方工具快速接入模式',
            '先展示命令',
            '等明确授权',
            '前台执行',
            '外部工具、MCP、第三方 Skill intake -> 先转 `ecosystem-scout`',
            '只有通过以下检查，才可以声称“节省了 Token”',
            '没有 tokenizer 实测就标注“预估”',
        ],
        'ecosystem_scout': [
            '快速接入',
            '推荐不超过 3 个候选',
            '展示安装计划',
            '等待明确授权',
            '前台执行与小样本验证',
            '应用后复盘',
        ],
        'replay': [
            'Replay 19: Third-Party Quick Install Root Route Fix',
            'did not try to read or invent a separate `context-budget-manager` skill',
            '我不会现在安装或运行',
            'npx -y repomix@latest --compress --token-count-tree --output /tmp/guyue-repomix-output.xml',
        ],
    }

    for label, needles in required_needles.items():
        for needle in needles:
            if needle not in contents[label]:
                print(f"❌ [CONTEXT BUDGET ERROR] Missing `{needle}` in {os.path.relpath(files[label], repo_root)}", file=sys.stderr)
                passed = False

    try:
        manifest = json.loads(contents['manifest'])
    except Exception as e:
        print(f"❌ [CONTEXT BUDGET ERROR] Failed to parse skills_manifest.json: {e}", file=sys.stderr)
        return False

    context_skill = next((skill for skill in manifest.get('skills', []) if skill.get('name') == 'context-compressor'), None)
    if not context_skill:
        print("❌ [CONTEXT BUDGET ERROR] context-compressor missing from skills_manifest.json", file=sys.stderr)
        passed = False
    else:
        triggers = set(context_skill.get('trigger_intent', []))
        for trigger in {'压缩上下文', '节省token', '控制token', '上下文预算', 'token预算', 'MCP工具太多', '工具输出太长', '推荐第三方工具', '快速安装工具', 'headroom', 'Serena', 'Repomix', 'Context7'}:
            if trigger not in triggers:
                print(f"❌ [CONTEXT BUDGET ERROR] Missing context-compressor trigger: {trigger}", file=sys.stderr)
                passed = False
        description = str(context_skill.get('description', ''))
        for needle in {'Context budget manager', 'MCP tool schemas', 'tool outputs', 'controlled third-party quick installs', 'measured-or-marked token savings'}:
            if needle not in description:
                print(f"❌ [CONTEXT BUDGET ERROR] context-compressor manifest description missing `{needle}`", file=sys.stderr)
                passed = False

    ecosystem_skill = next((skill for skill in manifest.get('skills', []) if skill.get('name') == 'ecosystem-scout'), None)
    if not ecosystem_skill:
        print("❌ [CONTEXT BUDGET ERROR] ecosystem-scout missing from skills_manifest.json", file=sys.stderr)
        passed = False
    else:
        triggers = set(ecosystem_skill.get('trigger_intent', []))
        for trigger in {'recommend tool', '快速安装', '帮我装一下', '应用第三方工具'}:
            if trigger not in triggers:
                print(f"❌ [CONTEXT BUDGET ERROR] Missing ecosystem-scout trigger: {trigger}", file=sys.stderr)
                passed = False
        description = str(ecosystem_skill.get('description', ''))
        for needle in {'quick-install assistance', 'explicit approval', 'security-gate handoff', 'smoke tests'}:
            if needle not in description:
                print(f"❌ [CONTEXT BUDGET ERROR] ecosystem-scout manifest description missing `{needle}`", file=sys.stderr)
                passed = False

    try:
        prompts = json.loads(contents['prompts'])
    except Exception as e:
        print(f"❌ [CONTEXT BUDGET ERROR] Failed to parse test-prompts.json: {e}", file=sys.stderr)
        return False

    prompt = next((item for item in prompts if item.get('name') == 'Context Budget Manager - MCP And Tool Output'), None)
    if not prompt:
        print("❌ [CONTEXT BUDGET ERROR] Missing context budget prompt", file=sys.stderr)
        passed = False
    else:
        prompt_text = json.dumps(prompt, ensure_ascii=False)
        for needle in ['MCP 工具太多', 'tool schemas', 'search-plus-execute', 'measured or estimated', 'security boundaries']:
            if needle not in prompt_text:
                print(f"❌ [CONTEXT BUDGET ERROR] Context budget prompt missing `{needle}`", file=sys.stderr)
                passed = False

    quick_install_prompt = next((item for item in prompts if item.get('name') == 'Third-Party Tool Quick Install Gate'), None)
    if not quick_install_prompt:
        print("❌ [CONTEXT BUDGET ERROR] Missing third-party quick install prompt", file=sys.stderr)
        passed = False
    else:
        prompt_text = json.dumps(quick_install_prompt, ensure_ascii=False)
        for needle in ['third-party tool', 'explicit imperative authorization', 'security-gate', 'smoke test', 'rollback']:
            if needle not in prompt_text:
                print(f"❌ [CONTEXT BUDGET ERROR] Quick install prompt missing `{needle}`", file=sys.stderr)
                passed = False

    return passed


def check_loop_engineering_contract(repo_root):
    files = {
        'principles': os.path.join(repo_root, 'GUYUE_PRINCIPLES.md'),
        'root_skill': os.path.join(repo_root, 'SKILL.md'),
        'sop_maker': os.path.join(repo_root, 'skills', 'sop-maker', 'SKILL.md'),
        'skill_crafting': os.path.join(repo_root, 'skills', 'skill-crafting', 'SKILL.md'),
        'context_compressor': os.path.join(repo_root, 'skills', 'context-compressor', 'SKILL.md'),
        'coding_discipline': os.path.join(repo_root, 'skills', 'coding-discipline', 'SKILL.md'),
        'reality_auditor': os.path.join(repo_root, 'skills', 'reality-auditor', 'SKILL.md'),
        'manifest': os.path.join(repo_root, 'skills_manifest.json'),
        'prompts': os.path.join(repo_root, 'test-prompts.json'),
        'replay': os.path.join(repo_root, 'examples', 'quickstart-output.md'),
    }
    passed = True
    contents = {}

    for label, path in files.items():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                contents[label] = f.read()
        except Exception as e:
            print(f"❌ [LOOP ENGINEERING ERROR] Failed to read {path}: {e}", file=sys.stderr)
            passed = False

    if not passed:
        return False

    required_needles = {
        'principles': [
            '循环工程师',
            '有目标、边界、检查器、停止条件',
            '最大轮数、时间、Token、子任务数量',
            '不把循环工程理解成无限循环',
        ],
        'root_skill': [
            '循环工程 (Loop Engineering)',
            '有目标、有边界、有检查器、有停止条件、有成本控制',
            '动态工作流',
            '`context-compressor`、`sop-maker`、`skill-crafting`、`coding-discipline`、`system-design` 和 `reality-auditor`',
        ],
        'sop_maker': [
            'Loop Contract',
            '稳定输入',
            '停止条件',
            '最大轮数',
            '验证资产',
        ],
        'skill_crafting': [
            'Loop Engineering / Dynamic Workflow Packaging',
            'Skill、Custom subagent、Hook、Automation 或 CI gate',
            '最大轮数、最大时间、最大 Token、最大子任务数量',
            '先小样本回放',
        ],
        'context_compressor': [
            '循环和动态工作流预算',
            'max rounds',
            'subagent',
            'Token cap',
            'checkpoint',
        ],
        'coding_discipline': [
            '长任务循环边界',
            '循环契约',
            '不得开无限后台循环',
            '正常停止、预算耗尽、缺证据熔断、失败回滚',
        ],
        'reality_auditor': [
            'Loop And Dynamic Workflow Audit',
            '执行器和验证器',
            'max rounds',
            'subagent cap',
            'missing stop conditions',
        ],
        'replay': [
            'Replay 22: Loop Engineering Contract',
            '[Trace: Guyue/LoopEngineering]',
            'Loop Contract',
            'max rounds',
            'subagent',
            '不新建独立万能技能',
        ],
    }

    for label, needles in required_needles.items():
        for needle in needles:
            if needle not in contents[label]:
                print(f"❌ [LOOP ENGINEERING ERROR] Missing `{needle}` in {os.path.relpath(files[label], repo_root)}", file=sys.stderr)
                passed = False

    try:
        manifest = json.loads(contents['manifest'])
    except Exception as e:
        print(f"❌ [LOOP ENGINEERING ERROR] Failed to parse skills_manifest.json: {e}", file=sys.stderr)
        return False

    skill_map = {skill.get('name'): skill for skill in manifest.get('skills', [])}
    expected_manifest = {
        'sop-maker': {
            'triggers': {'循环工程', 'loop engineering', '动态工作流', '可重复工作流', 'Loop Contract'},
            'description': {'Loop Contract', 'stable inputs', 'stop conditions', 'validation assets'},
        },
        'skill-crafting': {
            'triggers': {'dynamic workflow', 'subagent workflow', '循环工程', 'Agent 工作循环', 'Custom subagent', 'CI gate'},
            'description': {'Skill, Custom subagent, Hook, Automation, or CI gate', 'stable inputs', 'verifiers', 'stop conditions', 'budgets'},
        },
        'context-compressor': {
            'triggers': {'动态工作流成本', '并行子 agent', 'loop budget', 'subagent budget'},
            'description': {'loop budgets', 'subagent budgets'},
        },
        'coding-discipline': {
            'triggers': {'长任务循环', '动态工作流开发', 'Agent loop', '循环契约'},
            'description': {'loop contracts', 'long-running agent workflows'},
        },
        'reality-auditor': {
            'triggers': {'循环验证', '动态工作流审查', 'subagent evidence'},
            'description': {'loop output audit', 'dynamic workflow stop conditions', 'subagent evidence'},
        },
    }

    for skill_name, expected in expected_manifest.items():
        skill = skill_map.get(skill_name)
        if not skill:
            print(f"❌ [LOOP ENGINEERING ERROR] {skill_name} missing from skills_manifest.json", file=sys.stderr)
            passed = False
            continue
        triggers = set(skill.get('trigger_intent', []))
        for trigger in expected['triggers']:
            if trigger not in triggers:
                print(f"❌ [LOOP ENGINEERING ERROR] Missing {skill_name} trigger: {trigger}", file=sys.stderr)
                passed = False
        description = str(skill.get('description', ''))
        for needle in expected['description']:
            if needle not in description:
                print(f"❌ [LOOP ENGINEERING ERROR] {skill_name} manifest description missing `{needle}`", file=sys.stderr)
                passed = False

    try:
        prompts = json.loads(contents['prompts'])
    except Exception as e:
        print(f"❌ [LOOP ENGINEERING ERROR] Failed to parse test-prompts.json: {e}", file=sys.stderr)
        return False

    prompt = next((item for item in prompts if item.get('name') == 'Loop Engineering Contract'), None)
    if not prompt:
        print("❌ [LOOP ENGINEERING ERROR] Missing loop engineering prompt", file=sys.stderr)
        passed = False
    else:
        prompt_text = json.dumps(prompt, ensure_ascii=False)
        for needle in ['Loop Engineering', '动态工作流', 'loop budget', 'Custom subagent', 'max rounds/time/token/subagent budget', 'unbounded loops', 'same executor/verifier view']:
            if needle not in prompt_text:
                print(f"❌ [LOOP ENGINEERING ERROR] Loop engineering prompt missing `{needle}`", file=sys.stderr)
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
            print(f"❌ [SHOWCASE ERROR] {label} is not included in the release source archive: {rel_path}", file=sys.stderr)
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

    if is_git_checkout(repo_root):
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

    if check_source_archive_export_rules(repo_root):
        print("✅ GitHub source archive export rules valid.")
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

    if check_human_voice_language_contract(repo_root):
        print("✅ human-voice language contract valid.")
    else:
        all_passed = False

    if check_business_readable_output_contract(repo_root):
        print("✅ business-readable output contract valid.")
    else:
        all_passed = False

    if check_reuse_first_engineering_contract(repo_root):
        print("✅ reuse-first engineering contract valid.")
    else:
        all_passed = False

    if check_development_defaults_contract(repo_root):
        print("✅ development defaults contract valid.")
    else:
        all_passed = False

    if check_context_compressor_budget_contract(repo_root):
        print("✅ context-compressor budget contract valid.")
    else:
        all_passed = False

    if check_loop_engineering_contract(repo_root):
        print("✅ loop engineering contract valid.")
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
