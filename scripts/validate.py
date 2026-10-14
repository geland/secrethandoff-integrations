#!/usr/bin/env python3
"""Validate local distribution contracts and official publisher schemas.

Offline checks use the standard library. Online/release checks require
requirements-review.txt. Release mode refuses missing artifact metadata.
"""
import argparse
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="Validate review contracts, or require release metadata and official schemas.")
parser.add_argument('--offline', action='store_true', help='Local contracts only; official schema checks are explicitly skipped')
parser.add_argument('--release', action='store_true', help='Require exact release URLs/hashes and official schema checks')
options = parser.parse_args()
assert not (options.release and options.offline), 'Release validation cannot skip official schemas'

for path in ROOT.rglob('*.json'):
    if '.git' not in path.parts and 'dist' not in path.parts:
        json.loads(path.read_text())
print('All JSON files parse')

claude = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
codex = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
for key in ['name', 'version', 'description', 'author', 'homepage', 'repository', 'license', 'keywords']:
    assert claude[key] == codex[key], f'Claude and Codex manifests differ in {key}'
assert claude['license'] == 'MIT'
print('Claude and Codex manifests match')

expected = {'mcpServers': {'secrethandoff': {'command': 'secrethandoff', 'args': ['mcp']}}}
for name in ['.mcp.json', 'configs/stdio.json']:
    assert json.loads((ROOT / name).read_text()) == expected, f'{name} must run "secrethandoff mcp" over stdio'
print('MCP server entries run the local binary over stdio')

for name in ['.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json']:
    market = json.loads((ROOT / name).read_text())
    assert [p['name'] for p in market['plugins']] == [claude['name']], f'{name} lists the wrong plugin'
print('Marketplace entries match the plugin name')

skill = (ROOT / 'skills/secrethandoff/SKILL.md').read_text()
front = skill.split('---', 2)[1]
assert 'name: secrethandoff' in front and 'description:' in front, 'skill frontmatter needs name and description'
assert len(skill.encode()) < 5000, 'keep SKILL.md under 5000 bytes'
openai = (ROOT / 'skills/secrethandoff/agents/openai.yaml').read_text()
short = openai.split('short_description: "', 1)[1].split('"', 1)[0]
assert 0 < len(short) <= 40, 'short_description must be 1-40 characters'
print('Skill metadata and size checks passed')

hooks = json.loads((ROOT / 'hooks/hooks.json').read_text())['hooks']
for event, args in [('UserPromptSubmit', ['hook', 'user-prompt']), ('PreToolUse', ['hook', 'bash'])]:
    entry = hooks[event][0]['hooks'][0]
    assert entry['command'] == 'secrethandoff' and entry['args'] == args, f'{event} hook must run secrethandoff {" ".join(args)}'
assert hooks['PreToolUse'][0]['matcher'] == 'Bash'
print('Hooks run the secrethandoff binary')

for key in ['name', 'version', 'description', 'author', 'homepage', 'repository', 'license', 'keywords']:
    assert json.loads((ROOT / 'plugin.json').read_text())[key] == claude[key], f'plugin.json differs in {key}'
gemini = json.loads((ROOT / 'gemini-extension.json').read_text())
assert gemini['version'] == claude['version'] and gemini['mcpServers'] == {'secrethandoff': {'command': 'secrethandoff', 'args': ['mcp']}}
for name in ['configs/cursor.json', 'configs/vscode.json', 'configs/opencode.json', 'configs/codex.toml', 'mcp.json']:
    assert 'secrethandoff' in (ROOT / name).read_text() and 'mcp' in (ROOT / name).read_text()
print('Registry and client configs run the local binary')

ui = json.loads((ROOT / 'plugin.json').read_text())['extensions']['com.openai']
assert codex['interface'] == ui['interface'], 'Codex listing interface differs'
assert codex['extensions']['com.openai']['review'] == ui['review'], 'Codex review cases differ'
assert 0 < len(ui['interface']['shortDescription']) <= 30
cases = ui['review']['test_cases']
assert len(cases['positive']) == 5 and len(cases['negative']) == 3
for group in ['positive', 'negative']:
    for case in cases[group]:
        assert all(case.get(key) for key in ['description', 'prompt', 'expected_behavior'])
        if group == 'positive':
            assert case.get('tools_triggered')
for kind, install in [('skills', ['geland/secrethandoff-integrations', '--skill', 'secrethandoff']),
                      ('mcps', ['secrethandoff', '--', 'secrethandoff', 'mcp'])]:
    entry = json.loads((ROOT / f'listings/cline/{kind}/secrethandoff/entry.json').read_text())
    assert entry['id'] == 'secrethandoff' and entry['type'] == kind[:-1]
    assert entry['verified'] is False and entry['featured'] is False
    assert entry['install']['args'] == install and set(entry['tags']) <= {'software', 'security'}
    assert (ROOT / f'listings/cline/{kind}/secrethandoff/icon.svg').is_file()
for field in ['composerIcon', 'logo']:
    assert (ROOT / ui['interface'][field]).is_file()
print('Listing parity, review cases, icons, and Cline drafts passed')

lock_path = ROOT / 'release-lock.json'
if options.release or lock_path.exists():
    if not lock_path.is_file() or not (ROOT / 'server.json').is_file():
        raise SystemExit('Release metadata missing: import a verified signed artifact with scripts/pin_release.py before publishing')
    lock = json.loads(lock_path.read_text())
    server = json.loads((ROOT / 'server.json').read_text())
    version = claude['version']
    assert re.fullmatch(r'\d+\.\d+\.\d+', version)
    assert lock['version'] == server['version'] == version
    assert server['name'] == 'com.secrethandoff/secrethandoff' and not server.get('remotes')
    assert lock['bundles'] == server['packages']
    prefix = f'https://github.com/geland/secrethandoff/releases/download/cli-v{version}/'
    targets = {(os, arch) for os in ['darwin', 'linux', 'windows'] for arch in ['amd64', 'arm64']}
    assert len(lock['archives']) == 6
    assert {(a['os'], a['arch']) for a in lock['archives']} == targets
    for a in lock['archives']:
        suffix = '.zip' if a['os'] == 'windows' else '.tar.gz'
        name = f"secrethandoff_{version}_{a['os']}_{a['arch']}{suffix}"
        assert a['name'] == name and a['url'] == prefix + name
        assert re.fullmatch(r'[a-f0-9]{64}', a['sha256'])
    assert len(lock['bundles']) == 6
    assert {b['identifier'] for b in lock['bundles']} == {
        f'{prefix}secrethandoff_{version}_{os}_{arch}.mcpb' for os, arch in targets}
    for b in lock['bundles']:
        assert b['version'] == version and b['registryType'] == 'mcpb'
        assert b['transport'] == {'type': 'stdio'}
        assert re.fullmatch(r'[a-f0-9]{64}', b['fileSha256'])
    print('Exact binary archive and MCPB release metadata passed (installed binary version must be checked separately)')
else:
    print('REVIEW ONLY: signed release metadata is not imported; this is not publish-ready')

if options.offline:
    print('Official schema checks SKIPPED by --offline')
else:
    try:
        import jsonschema
        from referencing import Registry, Resource
    except ImportError as error:
        raise SystemExit('Official schema checks require requirements-review.txt; use --offline for local contracts only') from error
    for name in ['plugin.json', 'mcp.json'] + (['server.json'] if lock_path.exists() else []):
        value = json.loads((ROOT / name).read_text())
        with urllib.request.urlopen(value['$schema'], timeout=30) as response:
            jsonschema.validate(value, json.load(response))
        print(f'{name}: official schema passed')
    common = json.loads((ROOT / 'listings/cline/schemas/common.schema.json').read_text())
    registry = Registry().with_resource(common['$id'], Resource.from_contents(common))
    for kind in ['skills', 'mcps']:
        schema = json.loads((ROOT / f'listings/cline/schemas/{kind[:-1]}.schema.json').read_text())
        value = json.loads((ROOT / f'listings/cline/{kind}/secrethandoff/entry.json').read_text())
        jsonschema.Draft202012Validator(schema, registry=registry).validate(value)
        print(f'Cline {kind}: upstream schema snapshot passed (recheck before submission)')
