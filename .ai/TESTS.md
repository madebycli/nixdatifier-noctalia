---
id: nixdatifier-noctalia-tests
type: tests
status: partial-verification
updated: 2026-10-12
---

# Verification

Observed locally:
- 40 Python unittest cases passed, including Lua 5.4 compatible host-contract execution.
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
and actual native lint command were unchanged. Runs 38217124145 and 38218204416
are still building the pinned Noctalia shell for the real native lint at the time
of this note. Native lint has NOT been reported as passed. Stable releases always
run all checks. Current authoritative verification lives in master-context's
projects/nixdatifier-noctalia/TESTS.md; the Actions pages expose live results.

Actual host/UI/theme acceptance remains a required check before stable.
