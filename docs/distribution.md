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
| skills.sh, Gemini, Cline, Cursor | Drafts only; later host validation and publication |
| MCP Registry, Smithery, Glama, other directories | Metadata prepared; not published |
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
