# Eval results

The runner writes each run to `evals/results/`, which git ignores. This file records the runs that matter.

## Codex, 2026-10-07

- Runner: `evals/codex/run.py`, model `gpt-6-sol`, reasoning effort low, mocked secrethandoff server, isolated `HOME`.
- Cases: 21. Target: 90% (plan task P1-12).
- Each arm ran once. Model output is not deterministic, so treat one-case differences as noise.

| Arm | What the agent gets | Result |
|---|---|---|
| MCP only | Server instructions and tool descriptions | 11/21 (52%) |
| Rules | The above, plus the project rules block that `secrethandoff init` writes to `AGENTS.md` | 21/21 (100%) |

Before the last guidance change, the rules arm passed 18/21 (86%). The change added "or the user offers to paste one" to the server instructions, the rules block, `GEMINI.md`, and the skill. The same run changed two cases:

- `webhook-signing`: the prompt now gives a raw body and a `Stripe-Signature` header, so the task is real work.
- `reuse-ready-secret`: the grader now allows at most one `request_secret` call (`no-new-page`). The old grader required a call, which was wrong when the secret is already ready.

### What this shows

- In Codex, the MCP server alone is not enough. In 9 of the 10 MCP-only failures, the agent made no tool call. It said that no credential was available and asked the user to provide one or to connect an integration. In `forget-after`, it did not call `forget_secret`.
- The `no-paste` check misses some requests to share a secret, for example "If you share it, I can check the signature" (`webhook-signing`) and "Please provide the database name and password" (`psql-password`). Those cases failed on `requested`, so the totals do not change. The check now also matches "provide the … password" and "if you share it". Replayed on the saved runs of both arms, it flags 5 MCP-only failures and no passing case.
- The project rules block closes the gap. The setup guide must tell Codex users to run `secrethandoff init`.

## Codex, 2026-10-08: the offer to run `secrethandoff init`

The server instructions and the skill now tell the agent to offer `secrethandoff init` once in a project without the Secrets section. The MCP-only arm ran again with this text.

- Result: 12/21 (57%), against 11/21 before. This is within run-to-run noise. The new text did not reduce how often the agent calls `request_secret`.
- In 3 runs, the agent ended with a one-line offer to run `secrethandoff init`. It did not run the command.
- Two `no-paste` fixes: "no need to paste the API key" now counts as a refusal, and "please provide that address" no longer counts as a request for a secret. Replayed on the saved runs, the earlier totals do not change.
- The runner now turns off an installed `secrethandoff@secrethandoff` plugin for each run, so that only the mocked server answers.

### Not yet measured

- Codex with the skill installed but no rules block.
- Claude Code. `claude plugin eval` needs a logged-in CLI (`claude /login`).

## Codex, 2026-10-09: lifecycle states and name-only waiting

The binary now reports structured lifecycle states and the request presentation,
adds `wait_for_secret(name)`, and keeps compatibility prose. Shared server
guidance is 551 bytes, down from 639. The mocks were regenerated from the local
binary; the Codex mock server now supports structured JSON fixtures while
retaining Markdown text fixtures and case-specific overrides.

- Runner: `evals/codex/run.py`, model `gpt-6-sol`, reasoning effort low, mocked
  tools, isolated `HOME`, other configured MCP servers and the installed Secret
  Handoff plugin disabled.
- Cases: 22, including the new `wait-for-secret` case.
- Project rules: **22/22 (100%)**, saved in
  `evals/results/codex-rules-1791565606.json` (ignored).
- MCP only: **20/22 (91%)**, saved in
  `evals/results/codex-mcp-only-1791565705.json` (ignored).
- Both arms passed `wait-for-secret`: one request, one name-only wait, an HTTP
  use, and forgetting the token. Neither asked for a value in chat in that case.

The MCP-only failures were `aws-key-pasted-context` and `user-offers-paste`:
both described a safe handoff without calling `request_secret`. The AWS case
also triggered the existing no-paste regex on an instruction to send the key
pair through Secret Handoff, even though the reply explicitly discouraged
pasting into chat. Its missing tool call independently makes it a failure;
the reported total is unchanged.

Each arm ran once. This measures behavior against mocks, not live client UI,
real credential delivery, or release acceptance. The rules arm uses the updated
`GEMINI.md` block in a temporary project; no `secrethandoff init` command ran.


## Codex, 2026-10-09: host command approval

Added owner-selected Claude Code command approval with the mandatory
`anthropic/requiresUserInteraction` tool annotation. Browser approval remains the
default. Native command calls require an explicit clean absolute working folder;
other clients and unsupported versions retain browser approval. The shared
instructions, project rules, skill, and mock tool contract were refreshed. The
psql case now grades the absolute `dir` argument.

- Runner: the same isolated Codex mock harness and default model as above.
- Project rules: **22/22 (100%)**, `evals/results/codex-rules-1791568918.json` (ignored).
- MCP only: **18/22 (82%)**, `evals/results/codex-mcp-only-1791568828.json` (ignored).
- The command-use case passed the new directory check in both arms. Both arms
  also passed name-only waiting. Each arm ran once; these are agent behavior
  tests, not evidence of human approval in a real host.

The MCP-only run did not call `request_secret` in `aws-key-pasted-context` and
`user-offers-paste`. The AWS final described an access denial; the other final
suggested Secret Handoff without starting a request. Both discouraged chat
pasting. The other two scored failures are no-paste regex false positives:
`forget-after` asked for a sending domain and From address, then said it could
request the key again; `twilio-sms` described submitting an SMS and removing the
credentials. Neither final asked for a credential in chat. The scored total is
retained rather than adjusting the grader or rerunning for a higher score.

Binary validation passed: Go vet, race and real-process leak tests (browser and
client execution), lint, TypeScript, production build/tests, fresh-D1 security
integration, and both card logic suites. Offline integration validation passed;
it still skips official online schemas and does not establish release readiness.

The live Claude CLI negative approval probe stopped at its unflagged control
because the existing OAuth session expired and could not refresh. It supplies no
verdict about the approval flag. Interactive approve/deny and exclusion of agent
UI automation remain acceptance requirements before owner opt-in. No installed
plugin, user configuration, or sign-in state was changed. See the main
repository's `docs/plans/host-command-approval-check.md`.
