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

Before first stable:
- [ ] Observe green Nix/Luau/native Noctalia CI for the final source commit.
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
