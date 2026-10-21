#!/usr/bin/env python3
"""Harmless live Codex policy check: no secrets, command execution, or UI clicks.

Overrides are confined to child CLI invocations; owner settings stay unchanged.
The allow policy must deliver tools/call; prompt+never must deny delivery.
"""
import argparse
import json
import os
import re
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib


def serve(work):
    for line in sys.stdin:
        req = json.loads(line)
        if "id" not in req:
            continue
        method = req.get("method")
        if method == "initialize":
            info = req["params"].get("clientInfo", {})
            (work / "identity.json").write_text(json.dumps({k: info.get(k) for k in ("name", "version")}))
            result = {"protocolVersion": req["params"]["protocolVersion"], "capabilities": {"tools": {}},
                      "serverInfo": {"name": "approval_probe", "version": "1"}}
        elif method == "tools/list":
            result = {"tools": [{"name": "run_with_secret", "description": "Harmless native-approval probe. Records delivery only; no command or credential. Call once with {}.",
                                 "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
                                 "annotations": {"destructiveHint": True, "openWorldHint": True}}]}
        elif method == "tools/call":
            (work / "called").write_text("called")
            result = {"content": [{"type": "text", "text": "Harmless probe called."}]}
        else:
            result = {}
        print(json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": result}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path)
    parser.add_argument("--codex-bin", default="codex", help="Codex executable to validate, including the desktop app's bundled runtime")
    parser.add_argument("--installed-plugin", action="store_true", help="verify native launch environment and empty list in the installed plugin")
    args = parser.parse_args()
    if args.server:
        serve(args.server)
        return
    codex = shutil.which(args.codex_bin)
    if not codex:
        raise SystemExit("Codex executable not found")
    version = subprocess.run([codex, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    match = re.fullmatch(r"codex-cli (\S+)", version)
    if not match:
        raise SystemExit("Unrecognized Codex version output")
    expected_client = {"name": "codex-mcp-client", "version": match[1]}
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    config = tomllib.loads((codex_home / "config.toml").read_text())
    if args.installed_plugin:
        check_installed_launch(config, codex_home, codex)
        return
    for mode in ("approve", "prompt"):
        with tempfile.TemporaryDirectory(prefix="secrethandoff-codex-approval-") as temp:
            work = Path(temp)
            home = work / "home"
            home.mkdir()
            cmd = [codex, "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only"]
            overrides = {
                "approval_policy": '"never"', "features.hooks": "false",
                "plugins": "{" + ",".join(json.dumps(k) + "={enabled=false}" for k in config.get("plugins", {})) + "}",
                "mcp_servers.approval_probe.command": json.dumps(sys.executable),
                "mcp_servers.approval_probe.args": json.dumps([str(Path(__file__).resolve()), "--server", str(work)]),
                "mcp_servers.approval_probe.tools.run_with_secret.approval_mode": json.dumps(mode),
                "model": '"gpt-6-sol"', "model_reasoning_effort": '"low"',
            }
            for name in config.get("mcp_servers", {}):
                if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
                    raise SystemExit("Probe requires simple MCP names for safe CLI overrides")
                overrides[f"mcp_servers.{name}.enabled"] = "false"
            for key, value in overrides.items():
                cmd.extend(["-c", f"{key}={value}"])
            cmd.append("Call approval_probe.run_with_secret exactly once with {}. If the host denies it, stop. Use no other tool. This is a harmless delivery probe, not a real command or credential.")
            env = {"PATH": os.environ["PATH"], "HOME": str(home), "CODEX_HOME": str(codex_home), "TMPDIR": temp, "LANG": "en_US.UTF-8"}
            proc = subprocess.run(cmd, cwd=work, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)
            events = [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("{")]
            attempts = [e.get("item", {}) for e in events if e.get("item", {}).get("type") == "mcp_tool_call" and e["item"].get("tool") == "run_with_secret"]
            denied = any(i.get("status") == "failed" and any(w in json.dumps(i.get("error", {})).lower() for w in ("denied", "reject", "approval")) for i in attempts)
            called = (work / "called").exists()
            identity = json.loads((work / "identity.json").read_text()) if (work / "identity.json").exists() else None
            passed = proc.returncode == 0 and identity == expected_client and (called if mode == "approve" else not called and denied)
            print(json.dumps({"policy": mode, "passed": passed, "called": called, "denied": denied, "client": identity, "exit": proc.returncode}), flush=True)
            if not passed:
                # Public probe events only; no real secret server runs here.
                print(json.dumps({"probe_attempts": attempts, "errors": [e for e in events if e.get("type") == "error"], "diagnostic": proc.stderr[-1800:]}), flush=True)
                raise SystemExit("Host policy probe failed or was inconclusive.")


def check_installed_launch(config, codex_home, codex):
    binary = shutil.which("secrethandoff")
    if not binary:
        raise SystemExit("Install the binary first")
    with tempfile.TemporaryDirectory(prefix="secrethandoff-installed-launch-") as temp:
        work = Path(temp)
        (work / "home").mkdir()
        (work / "bin").mkdir()
        marker = work / "mode.json"
        wrapper = work / "bin/secrethandoff"
        wrapper.write_text(f"#!{sys.executable}\nimport os,json,sys\nfrom pathlib import Path\nPath({str(marker)!r}).write_text(json.dumps({{'approval_mode':os.environ.get('SECRETHANDOFF_COMMAND_APPROVAL')}}))\nos.execv({binary!r},['secrethandoff',*sys.argv[1:]])\n")
        wrapper.chmod(0o755)
        cmd = [codex, "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only"]
        overrides = {"model": '"gpt-6-sol"', "model_reasoning_effort": '"low"', "approval_policy": '"never"', "features.hooks": "false",
                     "plugins": "{" + ",".join(json.dumps(k) + "={enabled=" + ("true" if k == "secrethandoff@secrethandoff" else "false") + "}" for k in config.get("plugins", {})) + "}"}
        for name in config.get("mcp_servers", {}):
            if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
                raise SystemExit("Probe requires simple MCP names")
            overrides[f"mcp_servers.{name}.enabled"] = "false"
        for key, value in overrides.items():
            cmd.extend(["-c", f"{key}={value}"])
        cmd.append("Call the installed Secret Handoff plugin list_secrets exactly once. This is an empty new session; do not request any secret, use any other tool, or change any configuration. Report only whether the list is empty.")
        env = {"PATH": str(work / "bin") + ":" + os.environ["PATH"], "HOME": str(work / "home"), "CODEX_HOME": str(codex_home), "TMPDIR": temp, "LANG": "en_US.UTF-8"}
        proc = subprocess.run(cmd, cwd=work, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)
        events = [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("{")]
        calls = [e.get("item", {}) for e in events if e.get("item", {}).get("type") == "mcp_tool_call" and e.get("type") == "item.completed"]
        mode = json.loads(marker.read_text()) if marker.exists() else None
        passed = proc.returncode == 0 and mode == {"approval_mode": "codex"} and any(c.get("tool") == "list_secrets" and c.get("status") == "completed" for c in calls)
        print(json.dumps({"installed_plugin": True, "passed": passed, "launch": mode, "exit": proc.returncode}), flush=True)
        if not passed:
            raise SystemExit("Installed launch check failed or was inconclusive")


if __name__ == "__main__":
    main()
