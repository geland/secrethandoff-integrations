# Multiplatform MCPB distribution

This separate distribution package bundles the six unchanged binaries from
`release-lock.json`. It does not rebuild, re-sign, replace, or attach new assets
to the existing CLI or plugin releases. It is published separately as `mcpb-v0.0.2`; the latest-plugin release pointer is unchanged.

The MCPB host must provide Node.js 22 or newer. `server/launch.cjs` selects by
Node's `process.platform` and `process.arch`, verifies the selected binary's
SHA-256, and starts exactly that executable with `mcp`. It passes stdio directly
to the child without reading protocol input. Unsupported CPUs, altered binary
bytes, and invalid index paths fail closed with fixed messages. There is no
runtime download, shell, hosted bridge, secret configuration field, or write to
disk. This launcher is packaging glue; the released Go binary still enforces
all secret handling and approval policies.

Build from the six downloaded release archives:

```sh
python scripts/package_mcpb.py /path/to/verified/archives
node --test packaging/mcpb/launch.test.cjs
python scripts/test_mcpb.py
```

The builder independently verifies archive sizes and SHA-256 before reading
only the exact binary member. The bundle includes the release lock and a binary
hash index. ZIP metadata is fixed to support reproducible packaging on the same
compression toolchain. The official MCPB validator must pass before publication.

Native CI covers macOS, Linux, and Windows on x64 and ARM64. It asserts the actual
Node target, binary version, MCP initialization, nine tools, missing-secret
refusal, EOF shutdown, and rejection of a tampered binary. macOS also checks
Apple notarization. These are bundle launch checks, not acceptance of private
browser fill/approval UI in every MCPB host. No real credential or model task is
used. Existing PATH-based plugin releases are unchanged and require no Node
launcher.

## Registry publication

`registry-server.json` pins the separate public bundle and its exact checksum.
It uses `io.github.geland/secrethandoff`, which GitHub Actions OIDC can verify
from repository ownership. The unpublished domain-namespace listing metadata in the root
`server.json` remains an immutable record of the original CLI bundles, not a
second directory submission.

The manually dispatched Registry workflow runs only on `main`, validates the
metadata, downloads and verifies the public bundle plus a checksum-pinned
publisher, reruns local stdio installation checks, and then authenticates using
short-lived GitHub OIDC. It stores no permanent publisher secret and needs no
DNS or production website change. No pull request can trigger publication.

Validation evidence: all six artifacts from run `39529132802` have SHA-256
`5086abb4a5f6b2ec3b9bb7c362da169ce121ac4153fe6f0bf89e98d4fe846824`.
