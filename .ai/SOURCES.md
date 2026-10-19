---
id: nixdatifier-noctalia-sources
type: provenance
status: current
updated: 2026-10-19
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


Current personal contract: madebycli/nix-config f0ca178ce1cf1722066a7583fb8b2d79e60b1581,
flake.nix hosts [nyx aether], pkgs/nx/nx.py, pkgs/nixctl/nixctl.sh and pkgs/dots/dots.sh.
The fixture excludes four CI stand-ins from personal installable targets.

Runtime migration CI: runs 39317318504 (including native Noctalia lint) and
39317734339 (explicit Rust-TUI alias, unchanged frontend). Declarative integration:
nix-config main 6b6e6bb34a99a24912a508f03a2079857230b3ee pins plugin runtime
9dc105baec7c4a98a150fc9eea02ac186a4c05cc; the fixture remains the verified
two-host output contract from f0ca178, not a claim of actual host deployment.
