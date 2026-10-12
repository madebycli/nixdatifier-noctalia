---
id: nixdatifier-noctalia-architecture
type: architecture
status: current
updated: 2026-10-12
---

# Architecture

The frontend consists of four native entries: service, bar widget, shortcut and panel.
The service shares target-specific state through noctalia.state. Six small view modules
and four tool subviews build Noctalia-native ui trees. Only the panel owns interaction
and confirmation routing; components own presentation, backend.luau owns JSON transport.

The desktop-independent Python backend separates target configuration, personal adapter,
action planning, subprocesses, cache/locks, history, generations, flakes, health and tools.
Read requests use JSON API v1. Dynamic process inputs use argv. Terminal jobs own a
cross-process mutation lock, private logs and failure-aware command sequencing.
Read-only probes use isolated process groups. Interactive jobs retain the terminal's
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
