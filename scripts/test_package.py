#!/usr/bin/env python3
"""Check the distributable ZIP, including hook modules loaded at runtime."""
import json
import posixpath
from pathlib import Path
from zipfile import ZipFile

root = Path(__file__).resolve().parents[1]
version = json.loads((root / '.claude-plugin/plugin.json').read_text())['version']
with ZipFile(root / 'dist' / f'secrethandoff-plugin-{version}.zip') as archive:
    names = set(archive.namelist())
    hooks = json.loads(archive.read('hooks/hooks.json'))
    for module in hooks.get('modules', []):
        target = posixpath.normpath(posixpath.join('hooks', module))
        assert target.startswith('hooks/') and target in names, f'Missing hook module: {target}'
        assert archive.read(target) == (root / target).read_bytes(), f'Changed module: {target}'
    for name in ['.mcp.json', 'mcp.json']:
        server = json.loads(archive.read(name))['mcpServers']['secrethandoff']
        assert server['command'] == 'secrethandoff' and server['args'] == ['mcp']
        assert not server.get('env'), 'Distribution must not opt into native approval'
    for name in names:
        assert not name.startswith('/') and '..' not in Path(name).parts
        assert name not in {'scripts/configure_codex_approval.py', 'scripts/check_codex_approval.py'}
    assert json.loads(archive.read('release-lock.json'))['version'] == version
    print(f'Package passed: {len(names)} files, all hook modules included, browser-default launch preserved')
