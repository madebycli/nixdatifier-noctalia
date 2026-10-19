---
id: nixdatifier-noctalia-status
type: status
status: development
updated: 2026-10-19
---

# Status

Native Noctalia plugin API 26, development version 0.1.0; no stable release.
The personal adapter now follows nix-config's current nyx/aether outputs and
nx/nixctl/dots contracts. It reads the installed /etc/nixctl.conf, supports custom
my.repoPath, and rejects conflicting NX_CONF/NIXCTL_CONF files. Old profile markers,
saved config-sync state and automatic 18-profile routing are retired.

Updates use nx's local-lock recovery and build/confirmation flow. No automatic
Git commit, push or login is introduced. User-profile packages remain separate.
The native panel can open the Rust nix-settings TUI in its interactive terminal.
Foreign-host activation, unexpected origins and wrong configured paths are rejected.

Local: 49 Python tests passed, including native UI contract scenarios and a real
controlling-terminal test. Nix/package/Luau/native lint CI for this change is pending.
No real system switch, cleanup, secret decryption or user configuration modification
was performed. Hardware, Wayland layout, theme and authentication QA remain pending.

master remains upstream-only at 4847af59fc57196a727ce8d706ea7da625399eba.
