# Community publication progress for 0.0.2

Checked October 20, 2026, 18:56 PDT (October 21, 01:56 UTC).

The signed CLI `cli-v0.0.2` and Claude/Codex integrations `v0.0.2` were already
published and verified. None of their assets or tags were rebuilt, replaced,
or republished. The latest-plugin release pointer remains `v0.0.2`.
See `docs/releases/0.0.2.md` for preceding clean-install/upgrade evidence.

| Destination | Result | Evidence / remaining work |
| --- | --- | --- |
| skills.sh | Public listing resolves | https://skills.sh/geland/secrethandoff-integrations/secrethandoff. Real Skills CLI installation in an isolated profile passed; installed guidance matched the release. |
| Gemini CLI gallery | Installation verified; indexing pending | The `gemini-cli-extension` topic is enabled. Gemini CLI 0.65.0 installed public v0.0.2 and reported the local MCP Connected. Public gallery HTML had no `secrethandoff` or `Secret Handoff` reference at 18:54 PDT; earlier browser search also had none. |
| Cline Marketplace | Submitted; maintainer review pending | https://github.com/cline/marketplace/pull/307 is OPEN, no reviews or merge as of this check. Upstream validator and isolated Cline 3.0.73 configuration installation passed. Do not resubmit. |
| Cursor Directory | Direct page available; indexing/scan acceptance unconfirmed | https://cursor.directory/plugins/secret-handoff renders the H logo and local install configuration without the earlier hidden warning. Search `?q=secrethandoff` still did not return it at 18:54 PDT. No publication/indexing claim yet. |
| Official MCP Registry | Published; active 0.0.2 verified | `io.github.geland/secrethandoff`, published at 2026-10-21 01:53:47 UTC. Public API returned one matching active/latest entry and the exact separate bundle checksum. [Publication run](https://github.com/geland/secrethandoff-integrations/actions/runs/39529908141). |
| Glama | Approved; public listing live; claim/search checks pending | https://glama.ai/mcp/servers/geland/secrethandoff. Approval email at 2026-10-21 01:10:41 UTC and public Local-classified page verified. Owner explicitly approved GitHub sign-in to claim it. GitHub's Authorize button stayed disabled after reload; browser handoff is pending. No repository write access was shown; read-only email access was shown. Do not resubmit. |
| Smithery | Held; continuing local-bundle eligibility unconfirmed | https://smithery.ai/future announces October 31 shutdown of accounts, API, CLI, and connection services. The continuing directory is described around direct MCP URLs; local MCPB intake after the change is unconfirmed. Existing signed-in namespace is `gregaeland`; no upload, new credential, or hosted proxy. |
| mcpservers.org | Prepared; not submitted | https://mcpservers.org/submit has a free route. Automatic approval review blocked transmission of `hello@gregeland.com`; the explicit permission question remains unanswered. Do not retry through any route before owner approval. |
| PulseMCP | Intake paused | https://www.pulsemcp.com/submit says submissions/changes are paused and points publishers to the Official MCP Registry. No submission. |
| mcp.so | Outside free queue | https://mcp.so/submit?type=server offers a $39 paid submission. No payment or submission. |
| Grok community discovery | Deferred; required Grok Bot end-to-end proof is missing | Current CONTRIBUTING.md rule G2 requires having run it end to end, and section 5 defines plugins as tools a Grok Bot connects to. Official Grok Bot docs describe a hosted computer and separately approved local commands, not a verified local MCP/private-browser installation. No existing Secret Handoff PR was found. Grok Build stdio support is insufficient proof. No submission or bridge. |

## Separate multiplatform bundle

[Packaging PR #2](https://github.com/geland/secrethandoff-integrations/pull/2) and
[Registry workflow PR #3](https://github.com/geland/secrethandoff-integrations/pull/3)
were merged after checks passed.

[The separate `mcpb-v0.0.2` release](https://github.com/geland/secrethandoff-integrations/releases/tag/mcpb-v0.0.2)
contains the six unchanged, checksum-verified CLI 0.0.2 binaries. Its small Node
launcher selects `process.platform` and `process.arch`, verifies the chosen
binary's SHA-256, and passes stdio directly to `secrethandoff mcp`. It performs no
runtime download or secret processing. This MCPB route requires Node 22+ in the
host; existing PATH-based plugin installation does not acquire that dependency.

- Exact bundle SHA-256: `5086abb4a5f6b2ec3b9bb7c362da169ce121ac4153fe6f0bf89e98d4fe846824`.
- Source: `6acbbe9f5ec5b419ba0d3406355d1cd86241632b`; tested PR commit: `d26b38f20d3cb71b74882d14f191bbad774178bf`.
- [Native CI 39529132802](https://github.com/geland/secrethandoff-integrations/actions/runs/39529132802) passed macOS, Linux, and Windows on x64 and ARM64. Every output bundle was downloaded and all six hashes match exactly.
- Seven selector checks, official MCPB CLI 2.1.2 schema validation, and repository release validation passed. The existing H-brand PNG is accepted; 512px is a recommendation.
- Each native runner checked binary version, MCP initialize, the exact nine tools, empty-secret status, missing-secret request refusal, clean EOF exit, and tamper refusal before startup. Macs also checked Apple signature/notarization.
- A fresh download of the public bundle passed hash verification and the same macOS x64 checks. The Registry publishing job independently downloaded, verified, and ran it on Linux x64 before publication.
- macOS binaries retain their existing signatures and notarization. The outer bundle ZIP is unsigned. Its `provenance.json` records source/tests and is not a cryptographic attestation.

The initial artifact comparison caught Windows CRLF differences in three text
files, with identical binaries. Packaging now normalizes text and tests that
invariant; the final artifacts are byte-identical.

## Registry evidence and identity

Public readback: https://registry.modelcontextprotocol.io/v0.1/servers?search=secrethandoff
returned exactly one matching `io.github.geland/secrethandoff` entry, version
0.0.2, status `active`, `isLatest: true`, with the bundle hash above.

GitHub OIDC established publisher ownership without a permanent credential or
DNS change. The manually dispatched workflow runs only on main, pins the
publisher's version/checksum, validates metadata, and tests the exact public
bundle. The imported root `server.json` retains the original domain-namespace
CLI metadata for release reproducibility; it was not submitted as a second
listing. The published descriptor is `packaging/mcpb/registry-server.json`.

## Acceptance boundaries

No owner client configuration or installed binary was changed. No real secret,
model task, project init, or external authenticated credential-use request was
used. Native launch checks, Gemini connection, and Cline configuration checks
do not establish private browser entry, approval, or status-card UI acceptance
in every host. Native approval implementation and released artifacts were not
changed. Phone/remote relay remains disabled.

## Continue from here

1. Finish the owner-approved Glama sign-in/claim when GitHub permits authorization,
   then configure accurate source-build checks and verify search indexing. Glama's
   container checks must not become a hosted production bridge or a claim that
   private browser use works in arbitrary containers.
2. Complete mcpservers.org only after the pending contact-email permission.
3. Check Cline review and Gemini/Cursor indexing for meaningful changes without
   duplicate submissions. Do not republish the Registry or immutable releases.
4. Hold Smithery until continuing local-bundle distribution is established. Skip
   paused PulseMCP and paid mcp.so. Investigate Grok only with actual local host
   suitability. No new curated vendor applications.

Primary intake references: https://skills.sh/docs/faq,
https://geminicli.com/docs/extensions/releasing/,
https://github.com/cline/marketplace/blob/main/CONTRIBUTING.md,
https://github.com/cursor/community-plugins#contributing,
https://smithery.ai/docs/build/publish, https://smithery.ai/future,
https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md,
https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/github-actions.mdx.

## Follow-up at 2026-10-21 02:01 UTC

Cline PR #307 remains open without reviews. The owner-approved Glama sign-in
still shows GitHub's disabled Authorize button; the human handoff remains open.
The contact-email approval for mcpservers.org remains unanswered; no retry was
made. Indexing was checked shortly before this wake and was not polled again.

Grok discovery was investigated against the actual directory's
[submission rulebook](https://github.com/ZeroPointRepo/GrokBotDev/blob/main/CONTRIBUTING.md),
including G2 and section 5, and the official
[computer/app model](https://docs.x.ai/grok-bot/computer-and-apps).
That documentation describes a persistent cloud computer, account-wide
connectors, and separately approved local commands. It does not verify our local
stdio/private-browser path in Grok Bot. A Grok Build CLI check would not meet the
missing Grok Bot acceptance boundary. Defer this route until an actual supported
host installation and end-to-end private flow can be demonstrated; do not retry
with a hosted bridge or submit the unrelated Grok Build compatibility claim.
