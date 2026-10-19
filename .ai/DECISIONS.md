---
id: nixdatifier-noctalia-decisions
type: decisions
status: current
updated: 2026-10-19
---

# Decisions

- D001: Native Luau/plugin.toml API 26 instead of reusing the old Qt/QML UI.
  Evidence: pinned personal Noctalia source is the native C++ implementation.
- D002: Clean main tree with existing upstream history retained as parent. master
  untouched. No orphan/force rewrite required because both branches shared one head.
- D003: Work directly on main until stable, and keep newest development there afterward.
  Stable snapshots use exact MAJOR.MINOR.PATCH branches and vMAJOR.MINOR.PATCH tags.
  The manual stable workflow requires host verification and runs checks first.
- D004: Python standard library JSON backend for maintainable argv/process/state handling;
  separate Luau views use native controls. No cloud services or paid APIs.
- D005: The madebycli adapter delegates to existing CLI flows; generic targets stay independent.
  Do not bypass username/origin guards, confirmations or build-before-switch policies.
- D006: Keep system inputs and user profile packages distinct; permit multiple flakes.
- D007: No stable or full upstream-parity claim before real validation. Advanced upstream
  tools are explicit optional tasks, rather than silently copied into a monolith.
- D008: Isolate read-only process groups, but retain controlling tty for interactive
  jobs. A real pseudo-terminal regression test verifies prompt/input and output capture.
- D009: Backend-only CI changes do not rebuild Noctalia for unchanged frontend/native
  lint inputs. Native source changes and stable releases still run native lint.

- D010: Split panel lifecycle, interaction controller and layout by responsibility.
  Request serials are per query channel; target revisions and panel closure invalidate
  callbacks and unconfirmed plans. Comparison selections use generation numbers.
- D011: Bound read-only output while the process runs, with concurrent pipe draining.
  Do not accumulate unbounded temporary files and check their size only after exit.
  Preserve interactive tty behavior and incrementally decode UTF-8 job output.

- D012: Checkout scripts retain executable Git modes; patch their interpreters in the
  Nix test copy before direct execution, matching the package's normal fixup behavior.


- D013: Follow current nix-config outputs rather than reconstructing removed desktop
  profiles. REPO/HOST come from the same installed nx/nixctl configuration, with a
  ~/nix-config fallback. Preserve custom paths, exact output/origin checks, and
  generic multi-flake targets. Keep nx as the transaction/build/confirmation owner;
  dots owns dotfile synchronization and the Rust TUI owns configuration navigation.
