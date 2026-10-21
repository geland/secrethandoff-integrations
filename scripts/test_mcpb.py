#!/usr/bin/env python3
"""Verify the built bundle, native MCP launch, and refusal of changed binaries.

No credentials, fill pages, network calls, owner configuration, or model task.
"""
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
bundle = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'dist/secrethandoff-multiplatform.mcpb'
node = shutil.which('node')
assert node, 'Node required'
with tempfile.TemporaryDirectory(prefix='secrethandoff-bundle-') as folder:
    root = Path(folder)
    with ZipFile(bundle) as archive:
        assert all('..' not in Path(x.filename).parts and not Path(x.filename).is_absolute() for x in archive.infolist())
        archive.extractall(root)
        for entry in archive.infolist():
            (root / entry.filename).chmod((entry.external_attr >> 16) & 0o777)
    for name in ('server/launch.cjs', 'release-lock.json', 'LICENSE'):
        assert b'\r\n' not in (root / name).read_bytes(), 'Packaged text must use LF on every runner'
    manifest = json.loads((root / 'manifest.json').read_text())
    index = json.loads((root / 'server/binaries.json').read_text())
    lock = json.loads((ROOT / 'release-lock.json').read_text())
    assert json.loads((root / 'release-lock.json').read_text()) == lock
    assert manifest['version'] == index['version'] == lock['version']
    assert manifest['server']['mcp_config'] == {'command':'node','args':['${__dirname}/server/launch.cjs']}
    assert set(index['binaries']) == {f'{p}-{a}' for p in ('darwin','linux','win32') for a in ('x64','arm64')}
    for entry in index['binaries'].values():
        assert hashlib.sha256((root / 'server' / entry['path']).read_bytes()).hexdigest() == entry['sha256']
        assert entry['archiveSha256'] in {a['sha256'] for a in lock['archives']}
    env = {k: os.environ[k] for k in ('PATH','SystemRoot','WINDIR') if k in os.environ}
    env.update({k: folder for k in ('HOME','USERPROFILE','APPDATA','LOCALAPPDATA','TMP','TEMP')})
    target = subprocess.check_output([node, '-p', 'process.platform+"-"+process.arch'], text=True, env=env).strip()
    if os.environ.get('EXPECTED_BUNDLE_TARGET'):
        assert target == os.environ['EXPECTED_BUNDLE_TARGET'], 'Runner did not test the intended native CPU'
    entry = index['binaries'][target]
    binary = root / 'server' / entry['path']
    assert subprocess.check_output([str(binary),'version'],text=True,env=env).strip() == lock['version']
    if sys.platform == 'darwin':
        subprocess.run(['codesign','--verify','--strict','--check-notarization',str(binary)],check=True)
    proc = subprocess.Popen([node,str(root/'server/launch.cjs')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
    replies = queue.Queue()
    def read_replies():
        for line in proc.stdout:
            replies.put(json.loads(line))
    reader = threading.Thread(target=read_replies,daemon=True)
    reader.start()
    def call(i, method, params):
        proc.stdin.write(json.dumps({'jsonrpc':'2.0','id':i,'method':method,'params':params})+'\n')
        proc.stdin.flush()
        while True:
            reply=replies.get(timeout=15)
            if reply.get('id') == i:
                assert 'error' not in reply, 'MCP error'
                return reply['result']
    try:
        init=call(1,'initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'bundle-install-check','version':'1.0.0'}})
        assert init['serverInfo']['version'] == lock['version']
        proc.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        proc.stdin.flush()
        tools=call(2,'tools/list',{})['tools']
        assert {t['name'] for t in tools} == {'request_secret','request_secrets','wait_for_secret','list_secrets','forget_secret','http_request','proxy_settings','run_with_secret','confirm_secret'}
        assert not call(3,'tools/call',{'name':'list_secrets','arguments':{}}).get('isError')
        denied=call(4,'tools/call',{'name':'http_request','arguments':{'method':'GET','url':'https://example.invalid/','headers':{'Authorization':'Bearer {{secret:BUNDLE_CHECK_UNUSED}}'}}})
        assert denied.get('isError'), 'Missing secret must refuse request'
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise AssertionError('Launcher did not exit when stdio closed')
    assert proc.returncode == 0
    print(f'Native bundle launch passed: {target}, CLI {lock["version"]}, nine tools, missing-secret refusal, clean EOF exit')
    binary.write_bytes(binary.read_bytes()+b'tamper-check')
    refused=subprocess.run([node,str(root/'server/launch.cjs')],input='',capture_output=True,text=True,env=env,timeout=10)
    assert refused.returncode == 1 and refused.stdout == ''
    assert 'invalid bundle' in refused.stderr
    print('Tampered binary refused before MCP startup')
