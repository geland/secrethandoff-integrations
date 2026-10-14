#!/usr/bin/env python3
"""Stdio MCP server that answers the secrethandoff tools from the eval mocks.

Reads tools from evals/mocks/secrethandoff/_tools.json. Structured results
come from <tool>.json, with <tool>.md as a text fallback. A case's own mocks/
take precedence over the suite defaults. Logs each call
as one JSON line to the file in MOCK_LOG. Standard library only."""
import json, os, re, sys
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1]
SUITE = EVALS / 'mocks' / 'secrethandoff'
CASE = Path(os.environ.get('EVAL_CASE_DIR', '/nonexistent')) / 'mocks' / 'secrethandoff'
TOOLS = json.loads((SUITE / '_tools.json').read_text())['tools']
# The real server's instructions (guidance layer 1), saved from the binary.
INSTRUCTIONS = (SUITE / '_instructions.txt').read_text().strip()

def answer(tool, args):
    for base in (CASE, SUITE):
        path = base / f'{tool}.json'
        if path.is_file():
            # Substitute inside JSON strings with JSON escaping. Fixtures
            # hold only fictional metadata, never a secret value.
            text = re.sub(r'\{\{input\.(\w+)\}\}', lambda m: json.dumps(str(args.get(m.group(1), '')))[1:-1], path.read_text())
            return json.loads(text)
        path = base / f'{tool}.md'
        if path.is_file():
            text = path.read_text()
            if text.startswith('---'):
                text = text.split('---', 2)[2]
            return re.sub(r'\{\{input\.(\w+)\}\}', lambda m: str(args.get(m.group(1), '')), text).strip()
    return f'{tool} is not mocked'

def reply(i, result):
    sys.stdout.write(json.dumps({'jsonrpc': '2.0', 'id': i, 'result': result}) + '\n')
    sys.stdout.flush()

for line in sys.stdin:
    try:
        msg = json.loads(line)
    except ValueError:
        continue
    method, i = msg.get('method'), msg.get('id')
    if method == 'initialize':
        reply(i, {'protocolVersion': msg['params'].get('protocolVersion', '2025-06-18'), 'capabilities': {'tools': {}},
                  'serverInfo': {'name': 'secrethandoff', 'version': 'mock'}, 'instructions': INSTRUCTIONS})
    elif method == 'tools/list':
        reply(i, {'tools': TOOLS})
    elif method == 'tools/call':
        name, args = msg['params']['name'], msg['params'].get('arguments') or {}
        with open(os.environ['MOCK_LOG'], 'a') as log:
            log.write(json.dumps({'tool': name, 'input': args}) + '\n')
        result = answer(name, args)
        reply(i, result if isinstance(result, dict) else {'content': [{'type': 'text', 'text': result}]})
    elif i is not None:
        sys.stdout.write(json.dumps({'jsonrpc': '2.0', 'id': i, 'error': {'code': -32601, 'message': 'not found'}}) + '\n')
        sys.stdout.flush()
