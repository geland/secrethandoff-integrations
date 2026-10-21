---
name: secrethandoff
description: Get and use passwords, API keys, tokens, and other credentials without the value entering the chat. Use when a task needs a credential, when an API call or command fails with an authentication error, or when the user offers to paste a secret. If the user offers to paste one, call request_secret instead.
---

# Secret Handoff

Secret Handoff collects credentials in the user’s browser. Use them by name; never read their values. HTTP/proxy tools enforce the approved policy.

## When you need a credential

1. Call `request_secret` with a `name` (for example `STRIPE_KEY`), a one-sentence `reason`, and the narrowest `policy` that does the task.
2. Describe the `presentation` reported by the result: `browser_page` means the secret entry page opened in the browser; `client_prompt` means the client handles the remote page prompt; `remote_link` means a link for another device. A chat card shows status only, never secret entry. Do not claim that a card appeared unless the host confirms it.
3. The call waits for the human up to the configured time limit. If `status` is `pending`, call `wait_for_secret` with the name; it waits without opening another page or changing the policy. Repeat while pending. Older binaries can be rejoined by calling `request_secret` with the same arguments. Never ask for a secret in chat.
4. Use the secret only when `status` is `ready`. For `confirmation_required`, ask for the confirmation code the human read on their remote page and call `confirm_secret`; never guess it. If the result is `declined`, `cancelled`, or `expired`, stop and ask how the user wants to continue. `missing` means no request exists; `error` means the operation failed. Prose remains available for older hosts.

## Related credentials together

For 2–8 related credentials (such as username and password), use `request_secrets`
with a unique group `name`, `secrets: [{name, label}, ...]`, one `reason`, and one
narrow `policy`. Group and field names must differ. One local form makes all fields ready together. Use each field by its own name.
Wait using the group name. Forgetting the group or any member erases all members.
Groups require a local browser; phone/headless relay fill is unsupported.

## Write a narrow policy

- `hosts`: the exact API host, for example `api.stripe.com`. Use a wildcard (`*.example.com`) only when the task needs several subdomains.
- `methods`: only the methods the task uses, for example `["GET"]`.
- `paths`: only the paths the task uses, for example `["/v1/charges"]`.

## Use a secret

Prefer the tools in this order:

1. `http_request`: write `{{secret:NAME}}` in a header, the URL query, or the body, for example `"Authorization": "Bearer {{secret:STRIPE_KEY}}"`. You never hold the value.
2. `proxy_settings`: when a tool such as `curl` or an SDK must make the request. Put the returned variables in front of that one command, and write `{{secret:NAME}}` where the secret goes.
3. `run_with_secret`: when a program must read the secret from its environment. Pass separate arguments and an absolute `dir`; no shell runs and stdin is empty. Follow the owner-selected approval mode: browser approval, Claude Code permission prompt, or Codex approval settings (including automatic approval). Codex results use `presentation: client_policy` and `approval: host_policy`; do not claim a human clicked. Enable client approval only when the user explicitly requests it. The command can send the secret anywhere; prefer HTTP/proxy policy enforcement.

In a JSON body or a form body, `http_request` encodes the value for you. Write `{{secret:NAME}}` inside the JSON quotes, or after `name=` in a form.

### curl with `run_with_secret`

curl 8.3+ can read credentials from the environment: import with `--variable
%ENV_VAR` and use `--expand-header` or `--expand-data-urlencode`. Its expansion
syntax is `{{ENV_VAR}}`, distinct from `{{secret:NAME}}`.

Example argv: `["curl", "--variable", "%API_TOKEN", "--expand-header",
"Authorization: Bearer {{API_TOKEN}}", "https://api.example.com/items"]`;
secret binding: `["API_TOKEN:API_TOKEN"]`.

## Never

- Never ask the user to paste a secret in chat.
- Never print, echo, log, or write a secret to a file, an environment file, or a commit.
- Never try to read a secret back, decode `[REDACTED:NAME]`, or send a secret to a host outside its policy.
- Never put `{{secret:NAME}}` in a URL host or path.

## Project rules

Offer `secrethandoff init` once if the project lacks Secrets guidance. Run it
only with the user's consent. It adds a Secrets section to AGENTS.md or CLAUDE.md.

## Housekeeping

- `list_secrets` returns ready secrets and open requests, including remote requests waiting for confirmation. It never shows values.
- Call `forget_secret` when the task no longer needs a secret. It erases the value and cancels an open request, returning `forgotten` or `missing`. All secrets end when the session ends.
