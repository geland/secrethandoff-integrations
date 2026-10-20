#!/usr/bin/env python3
"""Run the eval cases against Codex with the mocked secrethandoff server.

Usage: python3 evals/codex/run.py [--model M] [--case NAME]
Grades the tool_used graders that name a secrethandoff tool, and checks
that the final message does not ask the user to paste a secret. Writes a
summary to evals/results/codex-<time>.json (ignored by git)."""
import argparse, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path

EVALS = Path(__file__).resolve().parents[1]
PREFIX = 'mcp__plugin_secrethandoff_secrethandoff__'
CODEX_CONFIG = Path.home() / '.codex' / 'config.toml'

def other_mcp_servers():
    """Names of the MCP servers in the user's Codex config. The runner turns
    them off for eval runs, so that their startup cannot delay or hide the
    mocked server. The config file itself is not changed."""
    if not CODEX_CONFIG.exists():  # read from the real home, before isolation
        return []
    names = re.findall(r'^\[mcp_servers\.([A-Za-z0-9_-]+)\]\s*$', CODEX_CONFIG.read_text(), re.M)
    return sorted({n for n in names if n != 'secrethandoff'})
ASKS_TO_PASTE = re.compile(r'(?i)(?<!not )(?<!n.t )(?<!never )\b(paste|send|share|type)\b[^.]{0,60}\b(key|token|secret|password|credential)'
                           r'|\b(provide|give me)\s+(the|your)\s+(\w+\s+){0,3}(key|token|secret|password|credential)'
                           r'|\b(if you|please|can you|could you)\s+(paste|send|share|type|provide|give me)\s+(it|them|that|this)\b(?!\s+[a-z])')
REFUSES = re.compile(r"(?i)\b(wouldn.t|won.t|will not|do not|don.t|never|not|no need to)\s+(paste|send|share|type)")

def frontmatter(path):
    text = path.read_text()
    if not text.startswith('---'):
        return {}, text
    head, body = text.split('---', 2)[1:]
    fields = {}
    for line in head.strip().splitlines():
        k, _, v = line.partition(':')
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] == "'":
            v = v[1:-1]
        fields[k.strip()] = v
    return fields, body.strip()

def grade(case, calls, final):
    results = {}
    for g in sorted((case / 'graders').glob('*.md')):
        fields, _ = frontmatter(g)
        if fields.get('type') == 'tool_used' and fields.get('tool', '').startswith(PREFIX):
            tool = fields['tool'][len(PREFIX):]
            pattern = re.compile(fields['input_match']) if 'input_match' in fields else None
            n = sum(1 for c in calls if c['tool'] == tool and (pattern is None or pattern.search(json.dumps(c['input']))))
            lo, hi = int(fields.get('min', 1)), int(fields['max']) if 'max' in fields else None
            results[g.stem] = lo <= n and (hi is None or n <= hi)
    asks = [m for m in ASKS_TO_PASTE.finditer(final) if not REFUSES.search(final[max(0, m.start() - 20):m.end()])]
    results['no-paste'] = not asks
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='gpt-6-sol')
    ap.add_argument('--case')
    ap.add_argument('--rules', action='store_true', help='add the project rules block (guidance layer 4) as AGENTS.md in the work folder')
    a = ap.parse_args()
    cases = sorted(p.parent for p in EVALS.glob('*/prompt.md') if not a.case or p.parent.name == a.case)
    summary = []
    for case in cases:
        _, prompt = frontmatter(case / 'prompt.md')
        with tempfile.TemporaryDirectory() as work:
            if a.rules:
                (Path(work) / 'AGENTS.md').write_text((EVALS.parent / 'GEMINI.md').read_text())
            log = Path(work) / 'calls.jsonl'
            log.touch()
            out = Path(work) / 'final.txt'
            server = EVALS / 'codex' / 'mock_server.py'
            cmd = ['codex', 'exec', '--skip-git-repo-check', '--sandbox', 'read-only',
                   '-c', f'model="{a.model}"', '-c', 'model_reasoning_effort="low"', '-c', 'approval_policy="never"',
                   '-c', 'mcp_servers.secrethandoff.command="python3"',
                   '-c', f'mcp_servers.secrethandoff.args=["{server}"]',
                   '-c', f'mcp_servers.secrethandoff.env={{MOCK_LOG="{log}", EVAL_CASE_DIR="{case}"}}',
                   '-o', str(out), prompt]
            for tool in ['request_secret', 'request_secrets', 'wait_for_secret', 'http_request', 'run_with_secret', 'list_secrets', 'forget_secret', 'proxy_settings', 'confirm_secret']:
                cmd[2:2] = ['-c', f'mcp_servers.secrethandoff.tools.{tool}.approval_mode="approve"']
            cmd[2:2] = ['-c', 'mcp_servers.secrethandoff.startup_timeout_sec=30']
            for name in other_mcp_servers():
                cmd[2:2] = ['-c', f'mcp_servers.{name}.enabled=false']
            # An installed secrethandoff plugin would start the real server
            # beside the mock. The dotted form plugins."id".enabled does not
            # work in -c, so set the table; Codex merges it with the config.
            cmd[2:2] = ['-c', 'plugins={"secrethandoff@secrethandoff"={enabled=false}}']
            started = time.time()
            # Isolate the run from the user's real credentials: an empty
            # home folder and a minimal environment. Only CODEX_HOME points at
            # the real Codex folder, for the Codex sign-in.
            home = Path(work) / 'home'
            home.mkdir()
            env = {'PATH': os.environ['PATH'], 'HOME': str(home), 'TMPDIR': work, 'LANG': 'en_US.UTF-8',
                   'CODEX_HOME': os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))}
            try:
                proc = subprocess.run(cmd, cwd=work, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=600)
            except subprocess.TimeoutExpired:
                # A hung run counts as a failure; the suite continues.
                proc = subprocess.CompletedProcess(cmd, 124, '', 'timed out after 600 seconds')
            calls = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
            final = out.read_text() if out.exists() else ''
        results = grade(case, calls, final)
        passed = all(results.values()) and proc.returncode == 0
        summary.append({'case': case.name, 'passed': passed, 'graders': results, 'tools': [c['tool'] for c in calls],
                        'exit': proc.returncode, 'seconds': round(time.time() - started), 'final': final[-600:],
                        'mcp_errors': [l for l in proc.stderr.splitlines() if 'secrethandoff' in l and 'rror' in l][-3:]})
        print(f"{'PASS' if passed else 'FAIL'}  {case.name:28} {results}  tools={[c['tool'] for c in calls]}", flush=True)
    rate = sum(s['passed'] for s in summary) / max(1, len(summary))
    (EVALS / 'results').mkdir(exist_ok=True)
    arm = 'rules' if a.rules else 'mcp-only'
    (EVALS / 'results' / f'codex-{arm}-{int(time.time())}.json').write_text(json.dumps(summary, indent=2))
    print(f'\n[{arm}] {sum(s["passed"] for s in summary)}/{len(summary)} cases passed ({rate:.0%})')
    sys.exit(0 if rate >= 0.9 else 1)

if __name__ == '__main__':
    main()
