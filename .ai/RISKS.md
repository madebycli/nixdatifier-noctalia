---
id: nixdatifier-noctalia-risks
type: risks
status: current
updated: 2026-10-12
---

# Risks and limits

- Source Repo pin does not prove the actually running shell version. Luau API 26 is required.
- Lua-compatible contract tests do not establish native rendering or Wayland behavior.
- System builds and genuine mutation have not been run on the user's hardware.
- Generic Home Manager activation requires its CLI on PATH.
- Existing personal scripts contain their own user/origin assumptions; these are retained,
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
