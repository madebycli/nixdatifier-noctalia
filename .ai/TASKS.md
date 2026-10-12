---
id: nixdatifier-noctalia-tasks
type: tasks
status: current
updated: 2026-10-12
---

# Tasks

Implemented:
- [x] Validate fork and exact personal source context.
- [x] Clean native main; preserve upstream master.
- [x] Modular native entries, palette roles, German/English labels.
- [x] Multi-flake target model and local/foreign host distinction.
- [x] All 18 personal output mappings and active-profile selection.
- [x] Generations, diff, input status, health, secrets metadata, hashes, store inspection,
  direnv metadata, terminal action plans and persisted history.
- [x] NixOS/Home Manager modules, installer, examples and release policy.
- [x] Local backend/UI contracts and graph context.
- [x] Review production modules, package/installer and workflow responsibilities.
- [x] Split panel lifecycle/controller/layout and add deferred-callback regression coverage.
- [x] Invalidate same-id target reloads, preserve independent read/plan requests,
  cancel unconfirmed actions on close and retain generation comparison identity.
- [x] Bound live read-only output, reduce repeated generation symlink resolution,
  bound metadata reads and validate malformed configuration types.

Before first stable:
- [x] Observe green Nix package, 40 tests, Luau compilation and CLI smoke for eadf36c6.
- [x] Native Noctalia lint passed in full runs 38217124145 and 38218204416.
- [x] Optimization pass: Nix package, 45 tests and Luau compilation pass in run 38223056672.
- [ ] Observe optimization pass's native lint and packaged CLI smoke completion.
- [ ] Test actual installed Noctalia on nyx and aether.
- [ ] Verify native layout, small screens, scale, light/dark/custom palette and reduced animation.
- [ ] Exercise a second flake, standalone Home Manager and separate user-profile packages.
- [ ] Observe sudo/password and personal-script confirmations in the terminal.
- [ ] Controlled build/switch and protected-generation test on actual hardware.
- [ ] Create a stable version branch/tag only after the release checklist passes.

Optional upstream parity, not part of an asserted stable baseline:
- [ ] Exact generation-to-Git build provenance and config diff.
- [ ] Input release notes/commit browsing and deep package metadata/icons.
- [ ] Store-wide reclaimable-size measurements with explicit scheduling.
- [ ] Advanced devShell package listings, cache totals and cache clearing.
- [ ] Generic custom command definitions with a reviewed trust boundary.

Further hardening:
- [ ] Retention for cache identities and large terminal logs; PID/start-time identity
  for interrupted history; legacy user-profile alias generation discovery.
- [ ] Verify direnv authorization against its current content identity rather than
  inferring trust from allow-file text; retain inspection without evaluation.
