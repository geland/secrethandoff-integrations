#!/usr/bin/env python3
"""Import verified release bytes into distribution metadata; never publishes."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {(os, arch) for os in ('darwin', 'linux', 'windows') for arch in ('amd64', 'arm64')}
REPO = 'https://github.com/geland/secrethandoff/releases/download/'


def read_json(path):
    return json.loads(path.read_text())


def prepare(directory):
    """Validate everything before returning a set of files to write."""
    manifest = read_json(directory / 'manifest.json')
    version = manifest['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Expected an exact binary version')
    prefix = f'{REPO}cli-v{version}/'
    sums = {}
    for line in (directory / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split()
        if not re.fullmatch(r'[a-f0-9]{64}', digest) or Path(name).name != name or name in sums:
            raise ValueError('Invalid or duplicate checksum entry')
        sums[name] = digest
    archives = manifest['assets']
    if len(archives) != 6 or {(a['os'], a['arch']) for a in archives} != TARGETS:
        raise ValueError('Expected six platform archives')
    server = read_json(directory / 'registry/server.json')
    if server['version'] != version or server['name'] != 'com.secrethandoff/secrethandoff' or server.get('remotes'):
        raise ValueError('Registry identity/version/transport mismatch')
    bundles = server['packages']
    if len(bundles) != 6:
        raise ValueError('Expected six MCPB bundles')
    expected_names = set()
    for a in archives:
        suffix = '.zip' if a['os'] == 'windows' else '.tar.gz'
        name = f"secrethandoff_{version}_{a['os']}_{a['arch']}{suffix}"
        if a['name'] != name or a['url'] != prefix + name or a['sha256'] != sums.get(name):
            raise ValueError('Archive metadata differs from release checksums')
        expected_names.add(name)
    for bundle in bundles:
        name = bundle['identifier'].removeprefix(prefix)
        valid_names = {f'secrethandoff_{version}_{os}_{arch}.mcpb' for os, arch in TARGETS}
        if (name not in valid_names or name in expected_names or
                bundle['identifier'] != prefix + name or bundle.get('version') != version or
                bundle['registryType'] != 'mcpb' or bundle['transport'] != {'type': 'stdio'} or
                bundle['fileSha256'] != sums.get(name)):
            raise ValueError('Invalid MCPB release package')
        expected_names.add(name)
    if set(sums) != expected_names:
        raise ValueError('Checksums must name exactly the twelve expected release assets')
    for name, digest in sums.items():
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Release assets must be regular files')
        with path.open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != digest:
                raise ValueError(f'Release checksum mismatch: {name}')
    lock = {'version': version, 'source': 'https://github.com/geland/secrethandoff',
            'archives': archives, 'bundles': bundles}
    outputs = {'release-lock.json': lock, 'server.json': server}
    for name in ['plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'gemini-extension.json']:
        obj = read_json(ROOT / name)
        obj['version'] = version
        outputs[name] = obj
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release_directory', type=Path)
    args = parser.parse_args()
    try:
        outputs = prepare(args.release_directory.resolve())
    except (KeyError, OSError, ValueError, TypeError) as error:
        raise SystemExit(f'No metadata changed: {error}') from error
    for name, value in outputs.items():
        (ROOT / name).write_text(json.dumps(value, indent=2) + '\n')
    print('Release bytes verified; metadata pinned. Signing, provenance, public downloads, and host acceptance need separate checks.')


if __name__ == '__main__':
    main()
