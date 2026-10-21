# Secret Handoff for Claude Code and Codex

**Give your agent access with a sealed secret.**

Let your agent use temporary passwords, tokens, and one-time codes without
putting their values in the chat. The local tool opens a private browser page,
shows why the agent needs access, and applies secrets to requests you approve.
No vault to configure. No Secret Handoff account.

This repository publishes the Claude Code and Codex plugins for the signed
[Secret Handoff 0.0.2 release](https://github.com/geland/secrethandoff/releases/tag/cli-v0.0.2).
It includes the skill, local stdio MCP configuration, Claude detection hooks,
and a status-only Claude card. Secret entry stays in your browser.
These are repository plugins, not claims of vendor-curated directory approval.

## Install

[Download and install the local tool](https://secrethandoff.com/download) first.
Choose binary **0.0.2**. The website installer verifies its archive checksum and
installs the binary. Run `secrethandoff setup` below to connect Claude Code and
Codex when their CLIs are on PATH.

```sh
secrethandoff version
secrethandoff setup
secrethandoff doctor
```

Expected version: `0.0.2`. In the project where your agent works, run
`secrethandoff init` to add credential guidance. Start a new agent session.

### Claude Code

If you prefer to install the plugin yourself after installing the binary:

```sh
claude plugin marketplace add geland/secrethandoff-integrations
claude plugin install secrethandoff@secrethandoff
```

### Codex

```sh
codex plugin marketplace add geland/secrethandoff-integrations
codex plugin add secrethandoff@secrethandoff
```

Restart the client or start a fresh session after installation. The binary must
be on the PATH inherited by the client, including when launching a desktop app.
`secrethandoff doctor` checks the local setup.

For a pinned marketplace, Codex accepts
`codex plugin marketplace add geland/secrethandoff-integrations --ref v0.0.2`.
Claude Code accepts the Git source
`https://github.com/geland/secrethandoff-integrations.git#v0.0.2` with
`claude plugin marketplace add`. The release ZIP is also available for review.

## Use

Ask your agent: “Use Secret Handoff for the temporary credential this task needs.”
Enter the value only on the Secret Handoff browser page. Approve a narrow API
host, method, and path. The agent uses a reference and receives redacted results.
Ask the agent to forget the secret when the task is done.

Secrets live in the tool process's memory until forgotten or the process exits.
Filled secrets do not have an automatic expiry timer. Approved APIs receive the
value. `run_with_secret` requires browser command approval by default; an approved
command receives the value and can leak it. Owners can opt into verified Claude
Code native permission prompts or Codex approval settings; Codex settings may
authorize automatically. These modes do not change how secrets are entered.

Claude detection hooks can block some accidental pastes before they reach the
model. They cannot erase a value already saved in the client's local transcript.
Never paste secrets into chat. Read the [security boundaries](https://secrethandoff.com/security#local-tool).

## Opt-in Codex command approval

With the supported binary and stable Codex 0.155.1 in the 0.155 series, or the
exact desktop build `0.162.0-alpha.17.2`, the owner can
choose native host-policy authorization. It follows the owner's settings,
including allow rules, hooks, and automatic review; a human click is not required
in that mode. Browser approval remains the distribution default. Secret entry
always stays on the isolated Secret Handoff page.

From a checkout of this repository, reload the plugin, run the owner opt-in
helper, then start a fresh chat. The helper is not included in the review ZIP:

```bash
codex plugin add secrethandoff@secrethandoff
python3 scripts/configure_codex_approval.py codex \
  --plugin-dir ~/.codex/plugins/cache/secrethandoff/secrethandoff/0.0.2
```

The helper validates and edits only the installed `mcp.json` and `.mcp.json`
launch environment. It does not change host policies, reviewer, or hooks.
Reinstallation resets the opt-in; rerun it after reload. Use `browser` instead
of `codex` to restore browser command approval. Agents may apply it only when
explicitly instructed by the owner.

`python3 scripts/check_codex_approval.py` tests live allow/deny delivery with a
harmless server. `python3 scripts/check_codex_approval.py --installed-plugin`
checks that the real cached plugin starts with native mode and can list a new
empty store. Both use child-only isolation and no secrets. Pass `--codex-bin /absolute/path/to/codex`
to either check to validate the desktop bundled executable instead of the terminal CLI. Run
`python3 -m unittest discover -s tests -p test_codex_approval_config.py` for helper
preservation and refusal tests. Desktop prompt rendering needs a separate
owner-run dummy test. Command results report `client_policy` / `host_policy`,
never a claim that a human clicked.

## Grouped credentials

`request_secrets` asks for 2–8 credentials on one local browser page. A group name
identifies the request; fields have separate names and optional labels. One policy
applies to every field, and all values become ready together. Wait using the group
name. Forgetting the group or any member erases all members. Phone/headless relay
fill is currently unsupported for groups. Existing `request_secret` calls still
collect one value. This feature does not change command approval settings.

## Release scope

- Local handoffs for Claude Code and Codex, using `secrethandoff mcp`.
- Phone and remote relay handoffs are not enabled on the public service.
- One-time reveal links remain available separately at [Share a secret](https://secrethandoff.com/share).
- Other client configurations and listing drafts are retained for later testing;
  they are not published marketplace listings or verified host support claims.
- `release-lock.json` pins all six platform archives and six MCPB bundle hashes.
  Plugins start the binary on PATH; metadata does not replace or enforce that
  binary. Check `secrethandoff version` before use. Source and release provenance
  are available in the [binary repository](https://github.com/geland/secrethandoff).

## Development and validation

Use Python 3.11+ and Node 24. Install `requirements-review.txt` in a virtual
environment, then run:

```sh
python scripts/test_release.py
python scripts/validate.py --release
python scripts/package.py --release
python scripts/test_package.py
```

`tests/card.test.tsx` runs with the Claude mod test runner.
`tests/card-state.test.mjs` runs with Node and TypeScript available through
`SECRETHANDOFF_TEST_TYPESCRIPT`. See [0.0.2 release status](docs/releases/0.0.2.md),
[agent evals](evals/RESULTS.md), and [contributor guidance](AGENTS.md).
