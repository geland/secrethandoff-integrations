# Community publication progress for 0.0.2

Checked October 20, 2026 (America/Los_Angeles).

The CLI and Claude/Codex integration releases were already published when the
scheduled follow-up ran. Public signing workflow 39519007654 succeeded, and
integration CI is green. See docs/releases/0.0.2.md for the preceding artifact,
provenance, and clean-install/upgrade verification. This pass independently
checked the downloaded Apple Silicon archive hash and Apple notarization.

| Destination | Result | Evidence / remaining work |
| --- | --- | --- |
| skills.sh | Public listing resolves | https://skills.sh/geland/secrethandoff-integrations/secrethandoff returned HTTP 200 with the matching title and grouped guidance. Real Skills CLI install from public main succeeded in an isolated profile; installed SKILL.md exactly matches released guidance. |
| Gemini CLI gallery | Discovery enabled; indexing pending | Added `gemini-cli-extension` topic. Gemini CLI 0.65.0 installed v0.0.2 from the public GitHub release, discovered context and skill, and reported the stdio server Connected. The gallery search for `secrethandoff` returned no entries at 18:10 PDT; check again after the crawler runs. |
| Cline Marketplace | Submitted, awaiting maintainer review | https://github.com/cline/marketplace/pull/307 adds only registry/mcps/secrethandoff/entry.json and icon.svg. Upstream validator passed 204 entries. Cline 3.0.73 installed the local MCP configuration in an isolated profile without warnings; `cline config mcp` confirms the server. |
| Cursor Directory | Submitted, security scan pending | https://cursor.directory/plugins/secret-handoff shows the H logo, one MCP and one skill. Initially unpublished/hidden pending security scan. At 18:08 PDT the direct page rendered its install configuration without that warning, but directory search did not return Secret Handoff and anonymous HTTP verification was rate limited (429). Public indexing and scan acceptance remain unconfirmed. Removed the detected Claude-specific hook component before submitting. |

| Glama | Submitted, awaiting review | Submitted through https://glama.ai/mcp/servers using its Runs from source form and https://github.com/geland/secrethandoff. Glama confirmation email received at 2026-10-21 01:05:08 UTC explicitly says Secret Handoff is pending review. No listing URL or approval yet; do not resubmit. |
| Official MCP Registry | Not published; package selection and publisher verification unresolved | Public registry search returned zero matches for `secrethandoff`. Released MCPB manifests constrain OS only, with separate ARM64/AMD64 files; current metadata does not establish reliable CPU selection. Preserve released hashes and tags. |
| Smithery | Not published; bundle selection unresolved | Current Local (MCPB Bundle) documentation accepts one pre-built bundle as the latest local artifact. A single released architecture-specific file is insufficient for the advertised platform set. No hosted URL route was used. |
| mcpservers.org | Prepared; not submitted | https://mcpservers.org/submit offers a free review. Automatic approval review blocked transmission of the requested contact email; owner approval is pending. No submission occurred. |
| PulseMCP | Intake paused | https://www.pulsemcp.com/submit explicitly says new submissions and changes are paused. It points publishers to the Official MCP Registry for later discovery. |
| mcp.so | Outside free queue | https://mcp.so/submit?type=server currently offers a $39 paid submission. No payment or submission. |

No owner client configuration or installed binary was changed. No real secret,
model task, project init, or external authenticated API request was used. Gemini
connection and Cline configuration checks do not establish interactive credential
entry, approval, or status-card acceptance in those hosts.

## Continue from here

1. Check Cline PR status and Cursor scan status without duplicate submissions.
2. Check Gemini gallery indexing. Discovery topics are not proof of inclusion.
3. Continue MCP Registry and Smithery local-bundle preparation. The released
   server.json contains six platform bundles without explicit architecture
   selectors. Resolve actual client selection and publisher namespace ownership
   before publication; do not infer platform compatibility from filenames.
4. Watch the existing Glama review; do not submit again. Complete the prepared
   mcpservers.org free submission only after the pending contact-email approval.
   PulseMCP is paused and mcp.so is paid, so neither has an eligible action now.
5. Record authenticated intake blockers precisely; never substitute a hosted
   proxy or make claims about unsupported clients to satisfy a listing form.

Reference intake rules: https://skills.sh/docs/faq,
https://geminicli.com/docs/extensions/releasing/,
https://github.com/cline/marketplace/blob/main/CONTRIBUTING.md,
https://github.com/cursor/community-plugins#contributing.

## Packaging follow-up

The published binary release generator sets MCPB `compatibility.platforms` but
has no CPU selector; `server.json` offers all six bundles. The current MCPB
manifest specification documents OS overrides but no architecture override.
Before Registry or Smithery upload, prepare and test an explicit installation
selection strategy without replacing any released artifact or adding a hosted
bridge. Options to investigate are a separate multi-platform distribution bundle
containing the unchanged, checksum-verified binaries and a local architecture
selector, or a platform-specific listing route that actually enforces CPU choice.
This is packaging work, not evidence of installation or directory acceptance.
Registry namespace `com.secrethandoff` also still needs verified publisher control.

Primary references rechecked: https://smithery.ai/docs/build/publish,
https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md,
https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/server-json/generic-server-json.md.
The Registry documentation also describes custom-install metadata with a website
link, but that is not a substitute for the plan's exact-artifact installation
checks and has not been published here.
