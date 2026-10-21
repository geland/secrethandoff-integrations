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
| Gemini CLI gallery | Discovery enabled; indexing pending | Added `gemini-cli-extension` topic. Gemini CLI 0.65.0 installed v0.0.2 from the public GitHub release, discovered context and skill, and reported the stdio server Connected. Check actual gallery indexing after the crawler runs. |
| Cline Marketplace | Submitted, awaiting maintainer review | https://github.com/cline/marketplace/pull/307 adds only registry/mcps/secrethandoff/entry.json and icon.svg. Upstream validator passed 204 entries. Cline 3.0.73 installed the local MCP configuration in an isolated profile without warnings; `cline config mcp` confirms the server. |
| Cursor Directory | Submitted, security scan pending | https://cursor.directory/plugins/secret-handoff shows the H logo, one MCP and one skill. The page says it is unpublished/hidden pending security scan. Removed the detected Claude-specific hook component before submitting. |

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
4. Continue Glama open-source-server intake and mcpservers.org free submission,
   then recheck other eligible free directories using distribution-0.0.2.md.
5. Record authenticated intake blockers precisely; never substitute a hosted
   proxy or make claims about unsupported clients to satisfy a listing form.

Reference intake rules: https://skills.sh/docs/faq,
https://geminicli.com/docs/extensions/releasing/,
https://github.com/cline/marketplace/blob/main/CONTRIBUTING.md,
https://github.com/cursor/community-plugins#contributing.
