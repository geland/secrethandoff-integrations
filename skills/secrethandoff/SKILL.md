---
name: secrethandoff
description: Get and use passwords, API keys, tokens, and other credentials without the value entering the chat. Use when a task needs a credential, when an API call or command fails with an authentication error, or when the user offers to paste a secret. If the user offers to paste one, call request_secret instead.
---

# Secret Handoff

The secrethandoff MCP server asks the user for a secret through a page in their own browser. You never see the value. You use the secret by name, and the server sends it only where its policy allows.

## When you need a credential

1. Call `request_secret` with a `name` (for example `STRIPE_KEY`), a one-sentence `reason`, and the narrowest `policy` that does the task.
2. Describe the `presentation` reported by the result: `browser_page` means the secret entry page opened in the browser; `client_prompt` means the client handles the remote page prompt; `remote_link` means a link for another device. A chat card shows status only, never secret entry. Do not claim that a card appeared unless the host confirms it.
3. The call waits for the human up to the configured time limit. If `status` is `pending`, call `wait_for_secret` with the name; it waits without opening another page or changing the policy. Repeat while pending. Older binaries can be rejoined by calling `request_secret` with the same arguments. Never ask for a secret in chat.
4. Use the secret only when `status` is `ready`. For `confirmation_required`, ask for the confirmation code the human read on their remote page and call `confirm_secret`; never guess it. If the result is `declined`, `cancelled`, or `expired`, stop and ask how the user wants to continue. `missing` means no request exists; `error` means the operation failed. Prose remains available for older hosts.

## Write a narrow policy

- `hosts`: the exact API host, for example `api.stripe.com`. Use a wildcard (`*.example.com`) only when the task needs several subdomains.
- `methods`: only the methods the task uses, for example `["GET"]`.
- `paths`: only the paths the task uses, for example `["/v1/charges"]`.

The user sees the policy before they give the secret. A narrow policy is easier to approve.

## Use a secret

Prefer the tools in this order:

1. `http_request`: write `{{secret:NAME}}` in a header, the URL query, or the body, for example `"Authorization": "Bearer {{secret:STRIPE_KEY}}"`. You never hold the value.
2. `proxy_settings`: when a tool such as `curl` or an SDK must make the request. Put the returned variables in front of that one command, and write `{{secret:NAME}}` where the secret goes.
3. `run_with_secret`: when a program must read the secret from its environment. Pass separate arguments and an absolute `dir`; no shell runs and stdin is empty. The user approves every command in the browser or an owner-enabled Claude Code permission prompt. Never enable client approval mode yourself. The command can send the secret anywhere; prefer HTTP/proxy policy enforcement.

In a JSON body or a form body, `http_request` encodes the value for you. Write `{{secret:NAME}}` inside the JSON quotes, or after `name=` in a form.

### curl with `run_with_secret`

When the task must use `curl`, let curl read the secret from its environment. Then the value is not in the command line, a file, or the chat. This needs curl 8.3 or later.

- Import the variable with `--variable %ENV_VAR`.
- Use it with an `--expand-` option and curl's `{{ENV_VAR}}` syntax. This is curl's syntax, not `{{secret:NAME}}`.

Example: `command` is `["curl", "--variable", "%BG_PASS", "--expand-data-urlencode", "password={{BG_PASS}}", "https://app.example.com/login"]`, and `secrets` is `["BG_PASS:BG_PASS"]`. For a header, use `"--expand-header", "Authorization: Bearer {{API_TOKEN}}"`.

## Never

- Never ask the user to paste a secret in chat.
- Never print, echo, log, or write a secret to a file, an environment file, or a commit.
- Never try to read a secret back, decode `[REDACTED:NAME]`, or send a secret to a host outside its policy.
- Never put `{{secret:NAME}}` in a URL host or path.

## Project rules

`secrethandoff init` adds a short Secrets section to the project's `AGENTS.md` or `CLAUDE.md`, so that every agent in the project uses `request_secret`. After your first `request_secret` in a project that has no such section, tell the user this once. Run `secrethandoff init` in the project folder only if the user agrees.

## Housekeeping

- `list_secrets` returns ready secrets and open requests, including remote requests waiting for confirmation. It never shows values.
- Call `forget_secret` when the task no longer needs a secret. It erases the value and cancels an open request, returning `forgotten` or `missing`. All secrets end when the session ends.
