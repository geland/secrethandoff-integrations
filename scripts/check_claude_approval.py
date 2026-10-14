#!/usr/bin/env python3
"""Negative live-host check for mandatory human command approval. No secrets.

Uses the signed-in Claude CLI with no built-in tools or other MCP servers.
The probe never executes a command. A control checks that the model actually
calls it; flagged probes must be denied despite allow rules and allow hooks.
No user settings or plugin caches are changed. This does not test human clicks.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

TOOL = "mcp__approval_probe__approval_probe"


def serve(marker, flagged):
    for line in sys.stdin:
        req = json.loads(line)
        method = req.get("method")
        if "id" not in req:
            continue
        if method == "initialize":
            result = {"protocolVersion": req["params"]["protocolVersion"],
                      "capabilities": {"tools": {}},
                      "serverInfo": {"name": "approval_probe", "version": "1"}}
        elif method == "tools/list":
            tool = {"name": "approval_probe", "description": "A harmless approval test. Call once with an empty object. It only records that the host allowed a call; no commands or secrets.",
                    "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}}
            if flagged:
                tool["_meta"] = {"anthropic/requiresUserInteraction": True}
            result = {"tools": [tool]}
        elif method == "tools/call":
            marker.write_text("called")
            result = {"content": [{"type": "text", "text": "Harmless probe called."}]}
        elif method == "ping":
            result = {}
        else:
            print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": "Unknown method"}}), flush=True)
            continue
        print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": result}), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--server", type=Path)
    ap.add_argument("--flagged", action="store_true")
    ap.add_argument("--allow-hook", action="store_true")
    ap.add_argument("--allow-permission-hook", action="store_true")
    a = ap.parse_args()
    if a.allow_hook:
        json.load(sys.stdin)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}))
        return
    if a.allow_permission_hook:
        json.load(sys.stdin)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}))
        return
    if a.server:
        serve(a.server, a.flagged)
        return
    script = Path(__file__).resolve()
    # The CLI uses its existing sign-in. Built-ins and customizations are
    # disabled; the only available operation is the harmless probe.
    for label, flagged, hook in [("control", False, None), ("allow-rule", True, None), ("allow-hook", True, "PreToolUse"), ("permission-hook", True, "PermissionRequest")]:
        with tempfile.TemporaryDirectory(prefix="secrethandoff-approval-probe-") as work:
            marker = Path(work) / "called"
            args = [str(script), "--server", str(marker)] + (["--flagged"] if flagged else [])
            config = {"mcpServers": {"approval_probe": {"command": sys.executable, "args": args}}}
            settings = {"enabledPlugins": {}, "autoMemoryEnabled": False}
            if hook:
                hook_flag = "--allow-hook" if hook == "PreToolUse" else "--allow-permission-hook"
                settings["hooks"] = {hook: [{"matcher": TOOL, "hooks": [{"type": "command", "command": shlex.join([sys.executable, str(script), hook_flag])}]}]}
            cmd = ["claude", "-p", "Call mcp__approval_probe__approval_probe exactly once with {}. If denied, stop. Do not request or use any other tool.",
                   "--tools", "", "--allowedTools", TOOL, "--strict-mcp-config", "--mcp-config", json.dumps(config),
                   "--setting-sources", "", "--settings", json.dumps(settings), "--disable-slash-commands", "--no-chrome",
                   "--permission-mode", "default" if hook == "PermissionRequest" else "dontAsk", "--no-session-persistence", "--output-format", "json"]
            env = dict(os.environ, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
            proc = subprocess.run(cmd, cwd=work, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=90)
            called = marker.exists()
            try:
                result = json.loads(proc.stdout)
            except json.JSONDecodeError:
                raise SystemExit(f"{label}: CLI did not return JSON (exit {proc.returncode}); no host verdict")
            denials = result.get("permission_denials", [])
            denied = any(d.get("tool_name") == TOOL for d in denials)
            passed = proc.returncode == 0 and (called if not flagged else not called and denied)
            print(json.dumps({"case": label, "passed": passed, "called": called, "denied": denied, "exit": proc.returncode, "subtype": result.get("subtype"), "auth_unavailable": "authenticate" in result.get("result", "").lower() or "not logged in" in result.get("result", "").lower()}), flush=True)
            if not passed:
                raise SystemExit("Host approval check failed or was inconclusive; keep browser approval.")


if __name__ == "__main__":
    main()
