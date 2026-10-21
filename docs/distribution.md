# Distribution status

Release scope, October 20, 2026: Claude Code and Codex repository plugins for
signed CLI 0.0.2, including grouped local requests and owner opt-in host approval.
Browser command approval remains the distribution default. See
[0.0.2 release checks](releases/0.0.2.md) and the
[upgrade and distribution checklist](distribution-0.0.2.md).

## Previous release

Release scope, October 14, 2026: Claude Code and Codex repository plugins for
signed binary 0.0.1, with local fill and browser command approval by default.
The public source is `geland/secrethandoff-integrations`; binary downloads are
in `geland/secrethandoff`. The newer Codex native-approval experiment is excluded.

## Release gates

- Import all twelve published artifacts and exact checksums with
  `scripts/pin_release.py`, using metadata from the signed release workflow.
- Run release importer regressions, official schema validation, package checks,
  and Claude manifest/card validation.
- Install the repository plugin in isolated Claude Code and Codex configurations.
  Confirm each installed package starts the signed binary and exposes its tools.
- Test the public GitHub install source after publication and record results in
  `docs/releases/0.0.1.md`. Host UI and model-behavior acceptance are distinct
  from installation and MCP protocol checks.

## Channels

| Channel | Scope |
| --- | --- |
| Claude Code repository marketplace | Current release |
| Codex repository marketplace | Current release |
| Vendor-curated Claude/OpenAI directories | Not submitted or approved |
| skills.sh | Public listing resolves; real isolated skill install passed |
| Gemini CLI gallery | Discovery topic enabled; release install and MCP connection passed; indexing pending |
| Cline Marketplace | [PR #307](https://github.com/cline/marketplace/pull/307) submitted; maintainer review pending |
| Cursor Directory | [Submitted](https://cursor.directory/plugins/secret-handoff); direct page available, search indexing and scan acceptance unconfirmed |
| Glama | Approved public page; ownership claim and search quality checks pending |
| MCP Registry | Not published; multiplatform bundle PR #2, publisher verification remains |
| Smithery | Held pending local-bundle eligibility after announced October 31 API/CLI shutdown |
| mcpservers.org | Free submission prepared; contact-email approval pending |
| PulseMCP / mcp.so | Intake paused / paid submission, respectively |
| Homebrew, Scoop, winget | Separate binary distribution work; not published here |

Phone/remote relay availability remains off on the public service. This local
release does not claim to close the independent protocol-review gate. No hosted
MCP endpoint or third-party bridge is included.

## References

- [Claude repository marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Codex plugin packaging and repository marketplaces](https://developers.openai.com/plugins/build/plugins)

Both repository installations and vendor directory listings must report their
actual status. A valid schema, a published ZIP, or an installed plugin does not
by itself prove a completed human secret-entry workflow.

Community publication evidence: [October 20 progress](community-publication-0.0.2.md).
