---
id: nixdatifier-noctalia-tests
type: tests
status: partial-verification
updated: 2026-10-19
---

# Verification

Observed locally:
- 45 Python unittest cases passed, including Lua 5.4 compatible host-contract execution.
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

Nix, Luau CLI and native Noctalia were unavailable locally.

Observed CI for source eadf36c6374101b93717c96a1b6d3f12368469d9:
run 38218542439 completed successfully. Nix package build, all 40 tests, Luau
compilation and packaged CLI smoke check passed, including the terminal-session fix.
https://github.com/madebycli/nixdatifier-noctalia/actions/runs/38218542439

Native lint was skipped in that backend/workflow-only run because the frontend
and actual native lint command were unchanged. Full runs 38217124145 and 38218204416
are now confirmed completed successfully, including the real native Noctalia lint.
https://github.com/madebycli/nixdatifier-noctalia/actions/runs/38218204416
Baseline main d812a374 passed package/tests/Luau/CLI in run 38218982211.

Optimization review regression coverage:
- Independent panel queries and action planning can overlap without losing results.
- Older same-channel callbacks, closed-panel plans and same-id config replies are discarded.
- Service target loaders reject stale results; delayed ticks use elapsed clock time.
- Search finds generations older than the first 100; comparison identity survives new entries.
- Changed comparison selections discard pending results.
- Output limits stop still-running producers; stderr drains concurrently; descendant-held
  pipes cannot extend a read request's deadline.
- Malformed target kinds/adapters/config roots and saved-state profiles are rejected/skipped.

Optimization source ee2946f9378db8c607d8756c25233c5a51b7c17f:
run 38223056672 passes Nix package build, all 45 tests and Luau compilation.
Native Noctalia lint is in progress; the CLI smoke step is pending.
https://github.com/madebycli/nixdatifier-noctalia/actions/runs/38223056672

The first optimization run 38222832023 failed only the new direct checkout-installer
test because /usr/bin/env is absent in the Nix build sandbox. The package itself built.
The corrected test derivation patches checkout shebangs before invoking the scripts;
the replacement run above passes the installer regression as well.
Current authoritative verification lives in master-context's projects/nixdatifier-noctalia/TESTS.md.
Actual host/UI/theme acceptance remains a required check before stable.


## 2026-10-19: current nx integration

49 local unittest cases passed. Coverage includes exactly two personal output
names from nix-config f0ca178, custom paths with spaces/quotes, literal config
parsing, conflicting configuration files, obsolete marker/state rejection,
foreign host/origin/path guards, nx update groups and per-input transaction routing,
unchanged separate user profiles, Luau-compatible UI contracts and controlling tty.
Python compilation and diff checks pass. CI for the new source remains pending.
No actual system activation or desktop/theme acceptance was performed here.
