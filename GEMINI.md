# Secrets

When you need a password, API key, token, or other credential, or the user offers to paste one, call the `request_secret` tool of the secrethandoff MCP server. Never ask the user to paste a secret in the chat.

Use a secret only by name, through `http_request`, `proxy_settings` or `run_with_secret`. Never print, echo, or write a secret to a file or a commit.

For `run_with_secret`, supply an absolute `dir` and wait for human command approval. Never enable client approval mode yourself.

If a request is pending, call `wait_for_secret` with its name. Describe the presentation reported by the result. Chat cards show status; enter secrets only on the Secret Handoff page.
