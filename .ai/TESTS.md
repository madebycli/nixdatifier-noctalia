---
id: nixdatifier-noctalia-tests
type: tests
status: partial-verification
updated: 2026-10-19
---

# Verification

Current runtime: 9dc105baec7c4a98a150fc9eea02ac186a4c05cc.

- 49 local Python tests pass, including literal installed-config parsing, custom
  paths with quotes/spaces, conflicting configuration files, nyx/aether-only
  personal output mapping, foreign host/origin/path guards, obsolete marker/state
  rejection, nx update groups and individual-input routing, separate user profiles,
  native UI contracts through a Lua-compatible harness and a real controlling tty.
- Python compilation and own-source whitespace checks pass.
- Full native frontend migration c78b5d57 passed Nix package build, 49 tests,
  Luau compilation, real native Noctalia manifest/settings lint and packaged CLI:
  https://github.com/madebycli/nixdatifier-noctalia/actions/runs/39317318504
- Runtime 9dc105ba changed only the explicit nix-settings-tui command alias and docs.
  Package, 49 tests, Luau and CLI passed; frontend/native inputs were unchanged,
  so native lint was correctly skipped:
  https://github.com/madebycli/nixdatifier-noctalia/actions/runs/39317734339
- nix-config main 6b6e6bb3 pins runtime 9dc105ba and declaratively installs the backend
  and Home Manager plugin registration. Four normal/full host evaluations and local
  backend/TUI package builds pass; see the nix-config project for its final CI.

Earlier optimization/native lint runs remain historical provenance; the results
above are the current migration evidence. No real host switch, garbage collection,
secret decryption, desktop rendering/theme or user configuration test was performed.
Actual nyx/aether acceptance is required before stable.

Commands:
```sh
PYTHONPATH=backend python3 -m unittest discover -s tests -v
nix flake check --print-build-logs
noctalia plugins lint ./nixdatifier-noctalia
```
