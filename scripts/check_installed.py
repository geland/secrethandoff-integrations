#!/usr/bin/env python3
"""Check an installed plugin against a release binary without requesting secrets.

Usage: python scripts/check_installed.py /path/to/cached/plugin /path/to/secrethandoff
No browser opens, project init runs, or API request is sent.
"""
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
binary = Path(sys.argv[2]).resolve()
lock = json.loads((root / 'release-lock.json').read_text())
assert subprocess.check_output([str(binary), 'version'], text=True).strip() == lock['version']
env = dict(os.environ)
env.pop('SECRETHANDOFF_COMMAND_APPROVAL', None)
for name in ['.mcp.json', 'mcp.json']:
    spec = json.loads((root / name).read_text())['mcpServers']['secrethandoff']
    assert spec['command'] == 'secrethandoff' and spec['args'] == ['mcp'] and not spec.get('env')
proc = subprocess.Popen([str(binary), 'mcp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, env=env, text=True, bufsize=1)
selector = selectors.DefaultSelector()
selector.register(proc.stdout, selectors.EVENT_READ)
def send(value):
    proc.stdin.write(json.dumps(value) + '\n')
    proc.stdin.flush()
def call(i, method, params):
    send({'jsonrpc': '2.0', 'id': i, 'method': method, 'params': params})
    while True:
        if not selector.select(15):
            raise TimeoutError('MCP response timeout')
        line = proc.stdout.readline()
        if not line: raise RuntimeError('MCP server closed')
        message = json.loads(line)
        if message.get('id') == i:
            assert 'error' not in message, 'MCP protocol error'
            return message['result']
try:
    init = call(1, 'initialize', {'protocolVersion': '2025-06-18', 'capabilities': {},
                                'clientInfo': {'name': 'release-install-check', 'version': '1.0.0'}})
    assert init['serverInfo']['version'] == lock['version']
    send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
    tools = call(2, 'tools/list', {})['tools']
    assert {t['name'] for t in tools} == {'request_secret','wait_for_secret','list_secrets','forget_secret','http_request','proxy_settings','run_with_secret','confirm_secret'}
    listed = call(3, 'tools/call', {'name':'list_secrets','arguments':{}})
    assert not listed.get('isError')
    forgotten = call(4, 'tools/call', {'name':'forget_secret','arguments':{'name':'INSTALL_CHECK_UNUSED'}})
    assert forgotten['structuredContent']['status'] == 'missing'
    denied = call(5, 'tools/call', {'name':'http_request','arguments':{'method':'GET','url':'https://example.invalid/','headers':{'Authorization':'Bearer {{secret:INSTALL_CHECK_UNUSED}}'}}})
    assert denied.get('isError'), 'Missing secret must refuse the request'
finally:
    proc.stdin.close()
    try: proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait()
    selector.close()
print('Installed launch: 0.0.1, eight tools, empty store, missing-secret refusal, browser approval default')
hooks = json.loads((root / 'hooks/hooks.json').read_text())
for module in hooks['modules']: assert (root / 'hooks' / module).is_file()
# Deliberately synthetic test markers, generated in memory and never printed.
marker = 'ghp_' + 'aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5'
for kind, body in [('user-prompt', {'prompt':'test '+marker}), ('bash', {'tool_input':{'command':'echo '+marker}})]:
    result = subprocess.run([str(binary),'hook',kind], input=json.dumps(body), capture_output=True, text=True, env=env, timeout=10)
    assert result.returncode == 0 and marker not in result.stdout + result.stderr
    output = json.loads(result.stdout)
    if kind == 'user-prompt': assert output['decision'] == 'block'
    else: assert output['hookSpecificOutput']['permissionDecision'] == 'deny'
print('Claude hook wiring: modules present; synthetic pasted-secret and command checks refused without echo')
