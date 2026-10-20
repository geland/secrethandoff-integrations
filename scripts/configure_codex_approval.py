#!/usr/bin/env python3
"""Select command approval in an installed Codex plugin, without changing host policy.

Run after `codex plugin add secrethandoff@secrethandoff`, then start a fresh chat.
Reinstallation resets this local choice to browser approval. No secrets are read.
"""
import argparse
import json
import os
from pathlib import Path
import tempfile


def configure(plugin_dir: Path, mode: str):
    plugin_dir = plugin_dir.resolve(strict=True)
    # The current distribution uses this shared launch file. Refuse unexpected
    # layouts instead of silently editing an unused file or another plugin.
    for name in ("plugin.json", ".codex-plugin/plugin.json"):
        manifest = json.loads((plugin_dir / name).read_text())
        if manifest.get("name") != "secrethandoff" or manifest.get("mcpServers") not in ((None, "./.mcp.json") if name == "plugin.json" else ("./.mcp.json",)):
            raise ValueError("Unexpected Secret Handoff plugin layout")
    # Current Agent Plugins read mcp.json; the legacy Codex manifest reads
    # .mcp.json. Validate both before changing either so an unexpected layout
    # cannot leave a partially selected mode.
    updates = []
    for name in ("mcp.json", ".mcp.json"):
        path = plugin_dir / name
        if path.is_symlink():
            raise ValueError("Launch configuration must not be a symlink")
        data = json.loads(path.read_text())
        server = data["mcpServers"]["secrethandoff"]
        if server.get("command") != "secrethandoff" or server.get("args") != ["mcp"] or server.get("type", "stdio") != "stdio":
            raise ValueError("Expected the local secrethandoff mcp command")
        env = server.setdefault("env", {})
        env["SECRETHANDOFF_COMMAND_APPROVAL"] = mode
        updates.append((path, data))
    for path, data in updates:
        with tempfile.NamedTemporaryFile(mode="w", dir=plugin_dir, delete=False) as f:
            temporary = Path(f.name)
            try:
                json.dump(data, f, indent=2)
                f.write("\n")
                f.flush()
                os.fchmod(f.fileno(), path.stat().st_mode & 0o777)
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["codex", "browser"])
    parser.add_argument("--plugin-dir", type=Path, required=True, help="installed Codex plugin cache directory")
    args = parser.parse_args()
    configure(args.plugin_dir, args.mode)
    print(f"Installed plugin command approval: {args.mode}. Start a fresh Codex chat. Host approval settings unchanged.")
