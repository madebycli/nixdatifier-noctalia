---
id: nixdatifier-noctalia-decisions
type: decisions
status: current
updated: 2026-10-12
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
