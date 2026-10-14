# Contributor guide

This repository contains only distribution files for the `secrethandoff` binary. The binary, its security invariants, and its threat model live in the Secret Handoff repository (`packages/cli-go`, `AGENTS.md`, and `docs/security/`).

## Rules

- Keep the Claude and Codex manifests identical in the fields that `scripts/validate.py` compares.
- Every MCP server entry runs the local binary over stdio: `secrethandoff mcp`. Never add a hosted endpoint or a credential to any file here.
- Pin each published manifest to an exact binary version and checksum (plan task P1-14).
- Tool and skill text must stay factual. Never tell an agent to ignore other instructions.
- Run `python3 scripts/validate.py` before every commit.

## Local testing

Claude Code and Codex both run a cached copy of an installed plugin, not this folder. After you change a skill, a hook, or `hooks/card.tsx`:

- Claude Code: `claude plugin uninstall secrethandoff@secrethandoff`, then `claude plugin install secrethandoff@secrethandoff`. `claude plugin update` does nothing while the version number stays the same.
- Codex: `codex plugin add secrethandoff@secrethandoff` copies the plugin again.

Start a new session after either step.

## Agent guidance text

The text that tells agents when to call `request_secret` exists in four places. Change all four together:

- `skills/secrethandoff/SKILL.md`
- `GEMINI.md`, which is also the project rules block that the Codex eval uses
- the server instructions in `packages/cli-go/mcp.go` (Secret Handoff repository)
- the rules block in `packages/cli-go/initcmd.go` (Secret Handoff repository)

## Evals

The suite has one folder for each case under `evals/`: `prompt.md` and `graders/`. The mocked server reads the responses in `evals/mocks/secrethandoff/`.

After any change to tool names, descriptions, schemas, or server instructions in the binary:

1. Build the binary: `cd packages/cli-go && CGO_ENABLED=0 go build -trimpath -o /tmp/secrethandoff .`
2. Copy its tool list and instructions into the mocks: `python3 scripts/refresh_mocks.py /tmp/secrethandoff`. Add a mock response file for each new tool.
3. Run the evals and update `evals/RESULTS.md`.

### Codex

```bash
python3 evals/codex/run.py            # MCP server only
python3 evals/codex/run.py --rules    # with the project rules block
python3 evals/codex/run.py --case jira-api
```

- It needs the `codex` CLI, signed in.
- Each run uses an empty `HOME` and a minimal environment, so the agent cannot use your real credentials. Only `CODEX_HOME` points at your Codex folder, for the sign-in. Keep this isolation.
- It turns off your other Codex MCP servers for the run.
- Results go to `evals/results/`, which git ignores.

### Claude Code

`claude plugin eval .` runs the same cases. It needs a signed-in CLI.
