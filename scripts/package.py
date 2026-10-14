#!/usr/bin/env python3
"""Build a review ZIP that contains only public plugin files."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--release', action='store_true', help='Require release-ready metadata and official schema checks')
args = parser.parse_args()
subprocess.run([sys.executable, str(ROOT / 'scripts/validate.py')] + (['--release'] if args.release else ['--offline']), check=True)
FILES = [
    '.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json', 'assets/icon.svg',
    '.claude-plugin/plugin.json', '.codex-plugin/plugin.json', '.mcp.json',
    'configs/stdio.json', 'configs/codex.toml', 'configs/cursor.json', 'configs/vscode.json', 'configs/opencode.json',
    'plugin.json', 'mcp.json', 'gemini-extension.json', 'GEMINI.md',
    'README.md', 'LICENSE', 'hooks/hooks.json', 'hooks/card.tsx',
    'skills/secrethandoff/SKILL.md', 'skills/secrethandoff/agents/openai.yaml',
]
if args.release or (ROOT / 'release-lock.json').exists():
    FILES += ['release-lock.json', 'server.json']

version = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())['version']
out = ROOT / 'dist' / f'secrethandoff-plugin-{version}.zip'
out.parent.mkdir(exist_ok=True)
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    for name in FILES:
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f'Not a regular package file: {name}')
        archive.write(path, name)
print(out)
