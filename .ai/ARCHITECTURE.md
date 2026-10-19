---
id: nixdatifier-noctalia-architecture
type: architecture
status: current
updated: 2026-10-19
---

# Architecture

The frontend consists of four native entries: service, bar widget, shortcut and panel.
The service shares target-specific state through noctalia.state. Six small view modules
and four tool subviews build Noctalia-native ui trees. panel.luau owns entry lifecycle,
panel-controller.luau owns independent query channels, cancellation and confirmation,
panel-layout.luau owns header/navigation/confirmation presentation. Components own
native theme presentation, backend.luau owns JSON transport. Target revisions invalidate
responses even when the target id stays the same. Service timers use elapsed clock time.

The desktop-independent Python backend separates target configuration, personal adapter,
action planning, subprocesses, cache/locks, history, generations, flakes, health and tools.
Read requests use JSON API v1. Dynamic process inputs use argv. Terminal jobs own a
cross-process mutation lock, private logs and failure-aware command sequencing.
Read-only probes use isolated process groups. output.py concurrently drains stdout/stderr
with per-stream byte limits and one deadline, including descendant-held pipes. Generation
listing resolves selected/running/booted profile identity once per snapshot. Interactive jobs retain the terminal's
controlling session so sudo and script input work; output is streamed and logged.

Target identity is {id, kind, flake, attribute, host, adapter, profile}. No singleton
system flake. Generic actions verify output host identity before activation. Foreign
hosts are build-only. Profile packages remain independent of system inputs.
Home Manager integrated into NixOS remains part of the system rebuild.

Native palette roles resolve live. Layout honors shell.corner_radius_scale and
shell.panel.borders/transparency_mode. Native controls own focus, scale and appearance.
No separate QML shell, tray daemon, fixed palette or custom fonts.

Nix modules package/install the backend and register user plugin data via Home Manager.
The NixOS module alone requires a path source registration. The interactive installer
refuses to overwrite an existing plugin. No personal source repo is auto-modified.


Current personal routing uses only nyx/aether plus a separate user package profile.
personal.py parses the installed nx/nixctl REPO/HOST data without sourcing shell
code; adapters.py validates the selected output, configured path and Git origin.
System updates and input updates delegate to nx, dotfile actions to dots. The
Settings action opens the installed Rust nix-settings-tui frontend in the same confirmed
interactive terminal. Generic multi-flake/Home Manager/devShell targets stay distinct.
