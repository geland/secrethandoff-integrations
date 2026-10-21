#!/usr/bin/env python3
"""Package unchanged released binaries for automatic local OS/CPU selection.

Requires all six archives in a supplied directory. Downloads and publication
are deliberately separate operations. No build, signing, or release mutation.
"""
import argparse
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {(os, arch) for os in ('darwin', 'linux', 'windows') for arch in ('amd64', 'arm64')}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def released_binary(archive, directory, version):
    os_name, arch = archive['os'], archive['arch']
    suffix = '.zip' if os_name == 'windows' else '.tar.gz'
    expected = f'secrethandoff_{version}_{os_name}_{arch}{suffix}'
    if archive['name'] != expected:
        raise ValueError('unexpected archive name')
    data = (directory / expected).read_bytes()
    if len(data) != archive['bytes'] or sha(data) != archive['sha256']:
        raise ValueError(f'archive checksum or size mismatch: {expected}')
    binary = 'secrethandoff.exe' if os_name == 'windows' else 'secrethandoff'
    if suffix == '.zip':
        with ZipFile(io.BytesIO(data)) as source:
            matches = [x for x in source.infolist() if x.filename == binary]
            if len(matches) != 1 or matches[0].is_dir():
                raise ValueError('missing or ambiguous binary')
            return source.read(matches[0])
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as source:
        matches = [x for x in source.getmembers() if x.name == binary]
        if len(matches) != 1 or not matches[0].isfile():
            raise ValueError('missing or ambiguous binary')
        return source.extractfile(matches[0]).read()

def build(directory, output):
    lock = json.loads((ROOT / 'release-lock.json').read_text())
    version = lock['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('invalid version')
    if len(lock['archives']) != 6 or {(a['os'], a['arch']) for a in lock['archives']} != TARGETS:
        raise ValueError('release must contain all six targets')
    files = {}
    index = {'version': version, 'binaries': {}}
    for archive in lock['archives']:
        platform = 'win32' if archive['os'] == 'windows' else archive['os']
        arch = 'x64' if archive['arch'] == 'amd64' else archive['arch']
        target = f'{platform}-{arch}'
        name = 'secrethandoff.exe' if platform == 'win32' else 'secrethandoff'
        relative = f'bin/{target}/{name}'
        data = released_binary(archive, directory, version)
        files[f'server/{relative}'] = (data, 0o755)
        index['binaries'][target] = {'path': relative, 'sha256': sha(data), 'archiveSha256': archive['sha256']}
    manifest = {
        'manifest_version': '0.3', 'name': 'secrethandoff', 'display_name': 'Secret Handoff',
        'version': version, 'description': 'Let agents use temporary secrets without receiving their values in chat.',
        'author': {'name': 'Greg Eland', 'url': 'https://gregeland.com'},
        'homepage': 'https://secrethandoff.com', 'license': 'MIT', 'icon': 'icon.png',
        'long_description': 'Local stdio server with browser approval by default. Bundles the unchanged CLI release for macOS, Linux and Windows on x64 and ARM64. Requires Node.js 22 or newer in the host. No runtime download, hosted bridge, account or vault. Secrets stay in the binary process memory until forgotten or the process exits. Phone/remote relay is disabled.',
        'server': {'type': 'node', 'entry_point': 'server/launch.cjs',
                   'mcp_config': {'command': 'node', 'args': ['${__dirname}/server/launch.cjs']}},
        'compatibility': {'platforms': ['darwin', 'linux', 'win32'], 'runtimes': {'node': '>=22.0.0'}},
    }
    encode = lambda obj: (json.dumps(obj, indent=2, sort_keys=True) + '\n').encode()
    files.update({
        'manifest.json': (encode(manifest), 0o644),
        'server/binaries.json': (encode(index), 0o644),
        'server/launch.cjs': ((ROOT / 'packaging/mcpb/launch.cjs').read_bytes(), 0o644),
        'release-lock.json': ((ROOT / 'release-lock.json').read_bytes(), 0o644),
        'LICENSE': ((ROOT / 'LICENSE').read_bytes(), 0o644),
        'icon.png': ((ROOT / 'assets/icon.png').read_bytes(), 0o644),
    })
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', compression=ZIP_DEFLATED) as bundle:
        for name, (data, mode) in sorted(files.items()):
            entry = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (0o100000 | mode) << 16
            entry.compress_type = ZIP_DEFLATED
            bundle.writestr(entry, data)
    print(f'{sha(output.read_bytes())}  {output.name}')
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archives', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/secrethandoff-multiplatform.mcpb')
    args = parser.parse_args()
    build(args.archives, args.output)
