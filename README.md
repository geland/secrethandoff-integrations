# Secret Handoff for Claude Code and Codex

**Give your agent access with a sealed secret.**

Let your agent use temporary passwords, tokens, and one-time codes without
putting their values in the chat. The local tool opens a private browser page,
shows why the agent needs access, and applies secrets to requests you approve.
No vault to configure. No Secret Handoff account.

This repository publishes the Claude Code and Codex plugins for the signed
[Secret Handoff 0.0.1 release](https://github.com/geland/secrethandoff/releases/tag/cli-v0.0.1).
It includes the skill, local stdio MCP configuration, Claude detection hooks,
and a status-only Claude card. Secret entry stays in your browser.
These are repository plugins, not claims of vendor-curated directory approval.

## Install

[Download and install the local tool](https://secrethandoff.com/download) first.
Choose binary **0.0.1**. The website installer verifies its archive checksum and
runs `secrethandoff setup` for Claude Code and Codex when their CLIs are on PATH.

```sh
secrethandoff version
secrethandoff setup
secrethandoff doctor
```

Expected version: `0.0.1`. In the project where your agent works, run
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
`codex plugin marketplace add geland/secrethandoff-integrations --ref v0.0.1`.
Claude Code accepts the Git source
`https://github.com/geland/secrethandoff-integrations.git#v0.0.1` with
`claude plugin marketplace add`. The release ZIP is also available for review.

## Use

Ask your agent: “Use Secret Handoff for the temporary credential this task needs.”
Enter the value only on the Secret Handoff browser page. Approve a narrow API
host, method, and path. The agent uses a reference and receives redacted results.
Ask the agent to forget the secret when the task is done.

Secrets live in the tool process's memory until forgotten or the process exits.
Filled secrets do not have an automatic expiry timer. Approved APIs receive the
value. `run_with_secret` requires browser command approval by default; an approved
command receives the value and can leak it. The newer Codex native-approval
experiment is not part of this release.

Claude detection hooks can block some accidental pastes before they reach the
model. They cannot erase a value already saved in the client's local transcript.
Never paste secrets into chat. Read the [security boundaries](https://secrethandoff.com/security#local-tool).

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
`SECRETHANDOFF_TEST_TYPESCRIPT`. See [release status](docs/distribution.md),
[agent evals](evals/RESULTS.md), and [contributor guidance](AGENTS.md).
