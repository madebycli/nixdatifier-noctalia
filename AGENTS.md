# Agent contract

Read `.ai/CONTEXT.md` first and validate the exact route against the declared
registry. Follow only relevant context graph edges. Do not load sibling projects
without a declared dependency.

Work directly in `main` until the first stable release; it always tracks our newest
development. `master` is upstream-only. Never push feature code to `master`, reset
its history or create a stable snapshot during an ordinary development change.
Stable branches are named after the exact version, with a matching `v` release tag.

Keep responsibilities separate. Production source modules should stay below 250
lines; split by behavior rather than manufacturing thin wrappers. Use native
Noctalia controls, palette tokens and host theme settings. No embedded hex palettes,
custom QML shell, independent font stack or fixed desktop assumption.

Preserve the current `madebycli/nix-config` nx/nixctl/dots contracts, exact nyx/aether
output routing and command guards. The old 18-profile matrix is retired. Never infer a selected configuration solely from the hostname. Do not run
real switching, garbage collection, secret decryption or direnv trust during tests.

Use argv subprocesses. Require explicit confirmation for mutation jobs. Keep
running, booted and next-boot generations protected. Stop command sequences on
failure. Cache successes by identity, not partial network failures.

Run `PYTHONPATH=backend python3 -m unittest discover -s tests -v` locally, and
`nix flake check --print-build-logs` when Nix is available. Native Noctalia lint and
Wayland/theme QA are distinct checks; do not substitute Lua contracts for them.

Reconcile `.ai` and the exact master-context nodes after work. Record checks that
could not run and pending CI honestly. Do not claim a release or build from metadata.
