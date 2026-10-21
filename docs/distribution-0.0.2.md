# 0.0.2 integration update and community distribution

Prepared October 20, 2026. CLI `cli-v0.0.2` is published and the companion plugin
is pinned to its verified signed artifacts. Clean public installations and
0.0.1 upgrades passed for both clients in isolated profiles. See
[the release record](releases/0.0.2.md) for evidence and remaining UI acceptance.
The community distribution queue below remains a plan, not submitted listings.

## Verified starting point before publication

- Public CLI latest: `geland/secrethandoff`, `cli-v0.0.1`.
- Public integrations latest: `geland/secrethandoff-integrations`, `v0.0.1`,
  main `0e0abac64b11c54dbd9cff89797dea1ad54e5a25`.
- Claude Code and Codex repository marketplaces are published. Their public
  distribution record says curated directories have not been submitted.
- The local checkout has newer grouped-request, card, eval, and native approval
  work. Its older `docs/distribution.md` is not the public release status.
- No 0.0.2 public artifact was available during this check. Do not invent hashes,
  move the 0.0.1 tags, or advertise an unreleased download.

## Update the published integrations after the binary release

1. Start from current public `main` in an isolated checkout. Import only reviewed
   integration changes required by the actual 0.0.2 tool contract. Preserve the
   dirty development checkout and keep native approval changes separate unless
   they are explicitly included in the approved binary release.
2. Wait for the tagged binary workflow to succeed, including Apple signing and
   notarization. Record the tag, source SHA, run URL, and public release URL.
3. Download the complete workflow `release` artifact and compare its twelve
   archives/MCPB bundles with the public assets. Verify checksums and provenance.
   The complete artifact includes `registry/server.json`, which the importer
   needs; the public archives alone are insufficient.
4. Run `python3 scripts/pin_release.py /absolute/path/to/release`. It updates
   `release-lock.json`, `server.json`, the three plugin manifests, and the Gemini
   manifest to the verified release version. It does not install the binary.
5. Run `scripts/refresh_mocks.py` against the released binary. If schemas,
   descriptions, or instructions changed, synchronize the skill/project guidance,
   add mock responses for new tools, and rerun the evals required by AGENTS.md.
   In particular, reconcile grouped requests and the installed tool-count check
   with the released contract rather than assuming either eight or nine tools.
6. Run importer tests, official schema validation with `--release`, package build
   with `--release`, package regression checks, card tests, and Claude validation.
7. Test clean installs AND upgrades from 0.0.1 in isolated profiles. Verify the
   binary version on PATH, cached plugin version, MCP tool inventory, browser
   approval default, and a private fill/use/forget flow in both clients. Never
   capture a secret, private page URL, or request body as evidence.
8. Publish integrations `v0.0.2` with ZIP, checksums, lock, and release notes.
   Keep `v0.0.1` immutable. Verify public default-branch and tag-based installs.
9. Check the production download page and installers against the new binary.
   Local installer source resolves GitHub latest, but deployed page metadata and
   actual downloaded bytes still need verification. Update any explicit pins.

## Existing-user upgrades

The binary and plugin are separate installations. Updating the plugin does not
replace `secrethandoff` on PATH. Current `setup.go` skips already-enabled plugins,
so rerunning `secrethandoff setup` alone is not a verified upgrade procedure.

After installing the released binary through the download installer, refresh
the repository marketplace and installed plugin:

```sh
claude plugin marketplace update secrethandoff
claude plugin update secrethandoff@secrethandoff

codex plugin marketplace upgrade secrethandoff
codex plugin add secrethandoff@secrethandoff
```

Restart affected client sessions and verify both binary and cached plugin
versions. These commands passed against public 0.0.2 in isolated profiles. Users pinned to `v0.0.1`
must deliberately change their marketplace ref to `v0.0.2` or a tracking branch.
Do not silently remove a user's pin.

## Next publication queue

Follow Shareout's community distribution approach, adapted to local stdio.
For each destination, search for an existing Secret Handoff entry first and
record its URL, submitted version, date, scan/review status, and install evidence.
Update an existing entry rather than submitting a duplicate. No hosted endpoint,
third-party bridge, paid placement, or compatibility claim is implied.

| Order | Destination | Concrete next step after 0.0.2 |
| --- | --- | --- |
| 1 | skills.sh | Run a real isolated Skills CLI installation from the public repo, verify guidance plus the separate binary/MCP prerequisites, then check indexing. Discovery follows installations; no directory PR is needed. |
| 2 | Gemini CLI gallery | Test extension install and MCP launch; verify root manifest and release archive layout, then add the `gemini-cli-extension` topic and check crawler validation. |
| 3 | Cline Marketplace | Choose the local MCP entry, refresh copy and H icon from the public brand, test its install arguments, validate against current upstream schemas, and submit one catalog PR. |
| 4 | Cursor Directory | Submit the public repository through the community intake after checking detection of the local MCP and skill; record the security scan separately from publication. |
| 5 | Official MCP Registry | Verify publisher namespace ownership, released server metadata, and unambiguous OS/CPU selection before publishing the exact 0.0.2 package hashes. |
| 6 | Smithery | Use its Local (MCPB Bundle) route. Verify platform selection and local execution before uploading the signed bundle; do not use its hosted URL proxy route. |
| 7 | Glama and mcpservers.org | Recheck open-source local-server intake and free listing requirements, then submit accurate release/install links. |
| 8 | Remaining discovery | Recheck PulseMCP intake and mcp.so pricing. Consider Grok community discovery only when local-server compatibility is established; Shareout's hosted integration does not establish it. |

Homebrew, Scoop, and winget are a separate binary-distribution pass with real
platform installation checks. Keep curated vendor applications separate from
this community queue.

## Curated directory version updates

No curated Claude/OpenAI submission is recorded for Secret Handoff. Repository
publication does not create one. If an owner has submitted separately, retrieve
that listing and version before making changes.

For an existing OpenAI directory plugin, metadata/skill changes use a complete
new ZIP uploaded to the same plugin, followed by checks, review, and publication.
Only one review may be active. Hosted MCP rescan behavior does not update this
local binary. OpenAI's desktop-only route currently requires an allowlisted
organization and inclusion of the local server/dependencies in the package; the
current PATH-dependent repository ZIP is not automatically that submission.

## Primary references checked October 20

- [Claude marketplace](https://code.claude.com/docs/en/plugin-marketplaces) and [commands](https://code.claude.com/docs/en/plugins/cli-reference)
- [Codex packaging](https://developers.openai.com/plugins/build/plugins)
- [OpenAI updates](https://developers.openai.com/plugins/deploy/submission) and [desktop-only eligibility](https://developers.openai.com/plugins/deploy/desktop-only)
- [Skills discovery](https://skills.sh/docs/faq)
- [Gemini release and gallery](https://geminicli.com/docs/extensions/releasing/)
- [Cline catalog contributions](https://github.com/cline/marketplace/blob/main/CONTRIBUTING.md)
- [Cursor community directory](https://github.com/cursor/community-plugins)
- [Smithery local publishing](https://smithery.ai/docs/build/publish)

Later queue entries require intake revalidation when reached. This document
does not claim a new submission, published 0.0.2, or a completed host upgrade.
