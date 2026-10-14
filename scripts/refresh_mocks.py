#!/usr/bin/env python3
"""Copy the tool list and server instructions from a secrethandoff binary into the eval mocks.

Usage: python3 scripts/refresh_mocks.py [path/to/secrethandoff]
The default binary is `secrethandoff` on PATH. Run this after any change to
tool names, descriptions, schemas, or server instructions, then run the evals."""
import json, pathlib, subprocess, sys

MOCKS = pathlib.Path(__file__).resolve().parent.parent / 'evals' / 'mocks' / 'secrethandoff'

def main():
    binary = sys.argv[1] if len(sys.argv) > 1 else 'secrethandoff'
    requests = [
        {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
         'params': {'protocolVersion': '2025-06-18', 'clientInfo': {'name': 'refresh-mocks', 'version': '1'}, 'capabilities': {}}},
        {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
    ]
    proc = subprocess.Popen([binary, 'mcp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    for r in requests:
        proc.stdin.write(json.dumps(r) + '\n')
    proc.stdin.flush()
    found = {}
    for line in proc.stdout:
        msg = json.loads(line)
        if msg.get('id') in (1, 2):
            found[msg['id']] = msg['result']
        if len(found) == 2:
            break
    proc.stdin.close()
    proc.wait(timeout=10)
    if len(found) != 2:
        sys.exit('the binary did not answer initialize and tools/list')
    (MOCKS / '_instructions.txt').write_text(found[1]['instructions'] + '\n')
    (MOCKS / '_tools.json').write_text(json.dumps(found[2], indent=2))
    names = sorted(t['name'] for t in found[2]['tools'])
    missing = [n for n in names if not (MOCKS / f'{n}.md').exists()]
    print(f'{len(names)} tools: {", ".join(names)}')
    if missing:
        sys.exit(f'add a mock response file for: {", ".join(missing)}')

if __name__ == '__main__':
    main()
