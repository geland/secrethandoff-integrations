#!/usr/bin/env python3
"""Regression checks for the release metadata import boundary."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/pin_release.py').write_text((ROOT / 'scripts/pin_release.py').read_text())
        for name in ['plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'gemini-extension.json']:
            path = self.root / name
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps({'version': '0.0.1'}))
        self.release = self.root / 'release'
        (self.release / 'registry').mkdir(parents=True)
        self.prefix = 'https://github.com/geland/secrethandoff/releases/download/cli-v0.1.0/'
        archives, bundles, sums = [], [], []
        for os in ['darwin', 'linux', 'windows']:
            for arch in ['amd64', 'arm64']:
                suffix = '.zip' if os == 'windows' else '.tar.gz'
                for ext in [suffix, '.mcpb']:
                    name = f'secrethandoff_0.1.0_{os}_{arch}{ext}'
                    data = name.encode()  # Synthetic artifact bytes, never a credential.
                    (self.release / name).write_bytes(data)
                    digest = hashlib.sha256(data).hexdigest()
                    sums.append(f'{digest}  {name}')
                    if ext == '.mcpb':
                        bundles.append({'registryType': 'mcpb', 'identifier': self.prefix + name,
                                        'version': '0.1.0', 'fileSha256': digest, 'transport': {'type': 'stdio'}})
                    else:
                        archives.append({'os': os, 'arch': arch, 'name': name,
                                         'url': self.prefix + name, 'sha256': digest, 'bytes': len(data)})
        (self.release / 'manifest.json').write_text(json.dumps({'version': '0.1.0', 'assets': archives}))
        (self.release / 'registry/server.json').write_text(json.dumps({
            'version': '0.1.0', 'name': 'com.secrethandoff/secrethandoff', 'packages': bundles}))
        (self.release / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
        self.before = self.metadata()

    def metadata(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*.json')
                if not p.is_relative_to(self.release)}

    def run_import(self):
        return subprocess.run([sys.executable, str(self.root / 'scripts/pin_release.py'), str(self.release)],
                              capture_output=True, text=True)

    def assert_rejected(self):
        result = self.run_import()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No metadata changed', result.stderr)
        self.assertEqual(self.metadata(), self.before)

    def mutate_server(self, change):
        path = self.release / 'registry/server.json'
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def test_verified_bytes_align_versions_and_record_hashes(self):
        result = self.run_import()
        self.assertEqual(result.returncode, 0, result.stderr)
        lock = json.loads((self.root / 'release-lock.json').read_text())
        self.assertEqual(lock['version'], '0.1.0')
        self.assertEqual(len(lock['archives']), 6)
        self.assertEqual(len(lock['bundles']), 6)
        for name in self.before:
            self.assertEqual(json.loads((self.root / name).read_text())['version'], '0.1.0')

    def test_tampered_bytes_leave_all_metadata_unchanged(self):
        next(self.release.glob('*.mcpb')).write_bytes(b'corrupt artifact')
        self.assert_rejected()

    def test_another_download_origin_is_refused(self):
        self.mutate_server(lambda s: s['packages'][0].update(identifier='https://other.example/package.mcpb'))
        self.assert_rejected()

    def test_duplicate_platform_bundle_is_refused(self):
        self.mutate_server(lambda s: s['packages'].__setitem__(1, s['packages'][0]))
        self.assert_rejected()

    def test_missing_platform_archive_is_refused(self):
        path = self.release / 'manifest.json'
        value = json.loads(path.read_text())
        value['assets'].pop()
        path.write_text(json.dumps(value))
        self.assert_rejected()

    def test_symlink_asset_is_refused(self):
        path = next(self.release.glob('*.mcpb'))
        moved = self.root / 'artifact'
        path.rename(moved)
        path.symlink_to(moved)
        self.assert_rejected()


if __name__ == '__main__':
    unittest.main()
