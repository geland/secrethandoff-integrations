# Secrets

When you need a password, API key, token, or other credential, or the user offers to paste one, call the `request_secret` tool of the secrethandoff MCP server. Never ask the user to paste a secret in the chat.

Use a secret only by name, through `http_request`, `proxy_settings` or `run_with_secret`. Never print, echo, or write a secret to a file or a commit.

For `run_with_secret`, supply an absolute `dir` and follow the owner-selected approval mode. Codex mode follows the owner's approval settings, including automatic approval; do not claim a human clicked. Enable client approval only when the user explicitly requests it.

For 2 to 8 related credentials, use request_secrets with a group name, named fields, and one narrow policy. Fill them together on the local page. Wait using the group name; forgetting the group or any member erases all members. Groups do not support phone or headless relay fill.

If a request is pending, call `wait_for_secret` with its name. Describe the presentation reported by the result. Chat cards show status; enter secrets only on the Secret Handoff page.
