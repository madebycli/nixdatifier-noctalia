---
id: nixdatifier-noctalia-risks
type: risks
status: current
updated: 2026-10-19
---

# Risks and limits

- Source Repo pin does not prove the actually running shell version. Luau API 26 is required.
- Lua-compatible contract tests do not establish native rendering or Wayland behavior.
- System builds and genuine mutation have not been run on the user's hardware.
- Generic Home Manager activation requires its CLI on PATH.
- The personal adapter validates installed host, repository path and Git origin,
  and can reject execution if the installed machine does not satisfy them.
- The mutation lock does not serialize independently launched personal shell commands.
- HTTP/Git upstream checks are bounded and may fail. Failure is never 'up to date'.
- Large flake sets may exceed Noctalia's short subprocess deadline. Retry heavy work in
  a terminal; no unbounded invisible system operation should be introduced.
- Read-only remote flake targets can evaluate/download source but cannot edit local inputs.
- Secrets inspection exposes names/metadata only and is not an encryption proof.
- direnv allow deliberately trusts project code; inspection never evaluates .envrc.
- Installer preserves an existing plugin copy; manual store-path installations should
  migrate to the Home Manager module for repeatable updates.

- Terminal jobs retain the controlling session. Timeout/cancellation stops the immediate
  process; independently surviving descendants require terminal/host acceptance testing.
- Terminal logs and cache identities currently have no byte/age retention budget.
  Completed job history is capped at 100, but running records use PID liveness only.
- Legacy user-profile aliases may need an explicit underlying profile path for generation
  discovery. direnv trust display is metadata-based and can be stale; it is not proof
  that current .envrc content is authorized.


- Existing explicit personal targets.json entries with removed outputs (e.g. nyx-niri)
  require user migration to nyx/aether; no user file is automatically overwritten.
- The Settings action requires the new Rust nix-settings-tui package in the user's config.
- The adapter trusts the installed nx/nixctl configuration for the repository path,
  while still validating exact host/output and origin before personal actions.
