---
id: nixdatifier-noctalia-status
type: status
status: development
updated: 2026-10-12
---

# Status

Development version 0.1.0. Native Noctalia plugin API 26.
Modular Python JSON backend and Luau service/widget/panel/shortcut implemented.
Supports several independent flake targets, named NixOS outputs, standalone
Home Manager, development shells and separate user package profiles.

Personal integration covers all 18 outputs from the verified nix-config source:
nyx/aether, Mango/Niri/Hyprland, combinations, -all and Hyprland-only Caelestia.
Active output uses the installed profile marker and saved state, not hostname alone.
Existing update/build/sync/cleanup commands retain their guards and prompts.

Theme binding uses native controls, role tokens, global radius, panel borders,
transparency and inherited fonts/scaling. Real host/compositor QA is pending.
Local 40-test suite passes. Nix package build, Luau compilation, all 40 tests and
packaged CLI smoke passed in CI run 38218542439 for eadf36c6374101b93717c96a1b6d3f12368469d9.
This includes the controlling-terminal correction. Native Noctalia lint is still
in progress in earlier runs; consult [[TESTS]]. No real system action was run here.

master baseline: 4847af59fc57196a727ce8d706ea7da625399eba.
No stable version snapshot or GitHub release has been created.
