# Listing copy for later directory submissions

These are drafts. The current publication scope is the Claude Code and Codex
repository plugins described in [distribution status](distribution.md).

- Name: Secret Handoff
- Subtitle: Use secrets without seeing
- Description: Let your agent use temporary secrets without seeing them. No vault to configure.
- Website: https://secrethandoff.com
- Source: https://github.com/geland/secrethandoff-integrations
- Binary: https://github.com/geland/secrethandoff/releases/tag/cli-v0.0.2
- Support: hello@gregeland.com
- Icon: `assets/icon.svg`, the Clear Passage H mark
- Transport: local stdio, `secrethandoff mcp`
- Prerequisite: install the signed 0.0.2 binary and make it available on PATH

The local tool requests a password, token, or one-time code in a private browser
page, shows its use policy, and lets the agent use it by reference. Values remain
out of model context and are redacted from tool results. The tool keeps secrets
in process memory until forgotten or the process exits. Approved APIs receive
values, and an approved command can leak a value it holds. Browser command
approval is the default. No account or permanent vault is required.

Phone and remote relay handoffs are not enabled on the public service. One-time
reveal links are a separate feature whose recipients can read the value.

The Cline skill and MCP entries are alternative drafts. Submit only a tested
choice after running the current upstream catalog validator. Do not mark an
entry verified or featured. Other client configs require real-host acceptance
before advertising support. Do not claim that a mock eval is a live-host test.
