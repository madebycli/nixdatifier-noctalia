---
id: nixdatifier-noctalia-tests
type: tests
status: partial-verification
updated: 2026-10-12
---

# Verification

Observed locally:
- 39 Python unittest cases passed, including Lua 5.4 compatible host-contract execution.
- All 18 personal output names verified from a pinned nix-config source fixture.
- Backend Python compilation passed.
- Installer Bash syntax passed.
- Checkout CLI --version and read-only targets smoke checks passed.
- No genuine build, switching, GC, direnv trust or secret decryption was executed.

Commands:
```sh
PYTHONPATH=backend python3 -m unittest discover -s tests -v
nix flake check --print-build-logs
noctalia plugins lint ./nixdatifier-noctalia
```

Nix, Luau CLI and native Noctalia were unavailable locally. The Check workflow
builds the package, compiles Luau, runs tests and native Noctalia settings/manifest lint.
CI has not yet been observed for the new main commit at the time of this note.
Actual host/UI/theme acceptance remains a separate required check before stable.
