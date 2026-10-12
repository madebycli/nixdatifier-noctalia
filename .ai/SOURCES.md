---
id: nixdatifier-noctalia-sources
type: provenance
status: current
updated: 2026-10-12
---

# Sources

Primary implementation: main in madebycli/nixdatifier-noctalia.
Upstream baseline: Muddyblack/nixdatifier at 4847af59fc57196a727ce8d706ea7da625399eba,
retained unchanged on master; MIT notices preserved.

Personal integration: madebycli/nix-config's verified main flake.nix, flake.lock,
.ai/CONTEXT.md and scripts. Fixture source revision is recorded in
tests/fixtures/madebycli-outputs.json. Only this project's declared dependency
projects/nix-config/INDEX.md is required in master-context.

Native API evidence: noctalia-dev/noctalia commit
546ec1cd6f6ca6c93e2995043a7b89f43ff14ceb, its docs/user/plugins/development/,
docs/plugin-api.json, example.toml and actual CLI/source-path registry code.
No QML v4 APIs were substituted for native interfaces.

Nixpkgs runtime/tool metadata verified at
090e478bd64824e2122328df47a7efb74fdaf0c1, using real locked narHash from the personal
source. The plugin's standalone lock follows nixos-unstable-small.
