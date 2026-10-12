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
Local 45-test suite passes, including deferred UI races and a real controlling-tty test.
Review split panel lifecycle/controller/layout and bounded live read-only output.
Production Python/Luau modules remain below 250 lines; the largest is 135 lines.
Native Noctalia lint passed in full CI runs 38217124145 and 38218204416.
Baseline main d812a374 also passed package/tests/Luau/CLI in run 38218982211.
Optimization source ee2946f9378db8c607d8756c25233c5a51b7c17f passes Nix package,
45 tests and Luau compilation in CI run 38223056672. Native lint is in progress;
consult [[TESTS]]. No real system action was run here.

master baseline: 4847af59fc57196a727ce8d706ea7da625399eba.
No stable version snapshot or GitHub release has been created.
