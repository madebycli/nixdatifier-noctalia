# Nixdatifier for Noctalia

Native Noctalia panels for Nix systems, user profiles and development environments.
Development version **0.1.0**, not a stable release.

`main` is the development branch and always contains our newest version. `master`
is upstream-only. A stable release creates a snapshot branch named exactly after
the version, such as `0.1.0`, and a matching `v0.1.0` release tag. No stable version
branch or release is created by an ordinary push.

## Requirements

- Native Noctalia v5 with **plugin API 26 or newer**. The current nix-config
  uses the upstream native shell flake; its Greeter remains independent.
- Linux with Nix and flakes. The Nix package supplies Python and runtime tools.
- For standalone Home Manager activation: the `home-manager` CLI on `PATH`.
- For personal-config commands: its existing installed commands and their existing
  user/repository guards. This plugin does not bypass them.

The old Quickshell v4 plugin API cannot run these Luau entry scripts.

## Try and install

Read-only target detection:

```sh
nix run github:madebycli/nixdatifier-noctalia/main -- targets
```

Install the backend and register the plugin without modifying your NixOS config:

```sh
nix profile install github:madebycli/nixdatifier-noctalia/main
nixdatifier-install-plugin
noctalia msg plugins enable madebycli/nixdatifier-noctalia
noctalia msg panel-toggle madebycli/nixdatifier-noctalia:panel
```

Add the bar widget with type `madebycli/nixdatifier-noctalia:status` through Noctalia's
bar settings. The control-center shortcut is `madebycli/nixdatifier-noctalia:open`.
The installer preserves an existing plugin directory rather than overwriting it.
For repeatable updates, use the Home Manager module below rather than a manually
registered store-path symlink.

## Declarative integration with your Nix config

Add this input to the personal config's `flake.nix`:

```nix
nixdatifier-noctalia = {
  url = "github:madebycli/nixdatifier-noctalia/main";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

Add the contents of [examples/nix-config-module.nix](examples/nix-config-module.nix)
as `modules/features/nixdatifier.nix` (or import it from your module list). It installs the backend system-wide and the plugin
through Home Manager. Empty `targets` uses autodetection, so no host-specific paths
need to be hardcoded into the module.

```sh
nix flake update nixdatifier-noctalia
sudo nixos-rebuild build --flake .#nyx  # choose nyx or aether
```

The Home Manager module alone also works with a standalone Home Manager config.
The NixOS module alone installs the backend and plugin files; register
`/run/current-system/sw/share/noctalia/plugins` as a Noctalia path source if you are
not using the Home Manager module. Neither module enables the plugin or switches
your system automatically. The source `madebycli/nix-config` is not modified by
installing this package.

## Multi-flake targets

Place JSON at `~/.config/nixdatifier-noctalia/targets.json`, or select another file
in the plugin's settings. See [examples/targets.json](examples/targets.json).

Each target has a unique `id`, `label`, `kind`, a `flake` and exact output
`attribute` where applicable. Supported kinds:

| Kind | Meaning |
|---|---|
| `nixos` | Named `nixosConfigurations` output, independent of hostname |
| `home-manager` | Named standalone `homeConfigurations` output |
| `devshell` | Named `devShells.<local system>` output |
| `profile` | Separate local Nix profile, with optional explicit `profile` path |

Different targets can use completely different flakes. Local directories support
lock inspection and input mutation. Remote flake refs support evaluation/build;
input editing requires a local checkout. Set `host` for NixOS targets so another
machine's output is clearly separated. Before activation the backend also checks
the actual `networking.hostName`, rather than trusting that label.

```sh
nixdatifier-noctalia discover /absolute/path/to/another/flake
nixdatifier-noctalia --config /path/targets.json query generations --target nyx
nixdatifier-noctalia --config /path/targets.json plan rebuild --target nyx
```

Discovery lists output names; it does not overwrite configuration. An explicit
target file disables default autodetection, so include your user-profile target
there if you want to keep it visible.

## Personal config support

On `nyx` or `aether`, autodetection reads `REPO` and `HOST` from the installed
`/etc/nixctl.conf`, shared with `nx` and `nixctl`. Custom `my.repoPath` checkouts
are supported. Without this file the default is `~/nix-config`. `NX_CONF` or
`NIXCTL_CONF` can select an explicit test/config file; conflicting files are rejected.

The current personal configuration exposes **two** real targets, `nyx` and `aether`,
plus a separate user-package profile. CI outputs are not offered as installable hosts.
Desktop choices live in `hosts/<host>/features.nix`; profile markers, saved
config-sync state and the old 18-output matrix are no longer used. Existing explicit
targets for another flake still work with the generic adapter. Update old personal
`targets.json` entries such as `nyx-niri` to `nyx` and the configured repo path.

`adapter = "madebycli"` delegates to the installed command suite:

| UI operation | Existing command |
|---|---|
| Build & switch | `nx switch` |
| Input check | `nx check` (all root inputs) |
| Refresh all/base/desktop/apps | `nx update` with the selected group |
| Refresh one input | `nx update INPUT` with build/confirmation/lock recovery |
| Pull configuration code | `nx pull` with local-lock reconciliation |
| Keep 5 backups | `nx clean 5` |
| Rollback / optimize | `nx rollback` / `nx optimise` |
| Config synchronization | `dots sync` |
| Open configuration TUI | `nix-settings-tui` in the interactive terminal |

Normal updates do not commit or push the local lock and require no GitHub login.
Dotfile pushes remain explicit. The adapter validates the exact local output,
configured checkout and Git origin. A foreign-host output can be built but cannot
run personal mutations here. User packages remain a distinct target, not a system
update category. Home Manager integrated into NixOS remains part of its rebuild.

## Interface and safety

The plugin uses Noctalia's native controls, palette-role tokens, font defaults,
scale, panel placement, corner-radius scale, panel borders and transparency mode.
There is no separate palette, hardcoded color scheme, font, window or tray process.
Palette tokens resolve live for light, dark and custom themes. English and German
translations are included. A real compositor/theme check is still required before
the first stable release.

Generation reads, closure comparisons, input checks, system health, hashes,
secret filenames, store roots/referrers and direnv inspection run on demand.
The idle service checks cheap local data once per minute and flake revisions at
the configured interval. Store-wide scans are not scheduled.

Before a mutation, the panel shows a concrete command plan and asks to run it in
the terminal. Password prompts and the personal scripts' own confirmations remain
visible. Jobs retain output under `~/.local/state/nixdatifier-noctalia/` with private
permissions. Closing the panel does not stop a terminal job. Every failed build
stops the command sequence before activation. Generation deletion protects running,
booted and selected next-boot generations. The operation lock coordinates this
plugin's jobs, not arbitrary independently started shell commands.

Noctalia's offline mode disables automatic revision checks and HTTPS hashing.
Secret values and private keys are never displayed or decrypted. `direnv allow`
is an explicit trust action; inspecting `.envrc` never evaluates it.

## Validation and scope

```sh
nix flake check --print-build-logs
nix develop --command python3 -m unittest discover -s tests -v
noctalia plugins lint ./nixdatifier-noctalia
```

The local suite currently passes 49 tests, including both current personal outputs,
multiple-flake configuration, action guards, partial network failures, process
timeouts, lock behavior, known hashes and Lua-compatible UI contract scenarios and a real pseudo-terminal password/input test.
CI additionally compiles the Luau files, builds the Nix package and runs the real
Noctalia manifest/settings linter. CI status is recorded in [.ai/TESTS.md](.ai/TESTS.md).
Lua contract tests do not prove Wayland layout or real system activation.

This clean native rewrite does not claim complete feature parity with upstream's
Qt app. Git config snapshots, release-note browsing, deep package metadata,
store-wide reclaimable-size scans and advanced devShell package inspection are
tracked separately in [.ai/TASKS.md](.ai/TASKS.md).

## Module boundaries

The panel entry owns lifecycle; `lib/panel-controller.luau` owns query/cancellation
and confirmation state; `lib/panel-layout.luau` owns native layout. Views remain
independent. Backend process execution and bounded output capture are separate.
See [docs/REVIEW.md](docs/REVIEW.md) for the optimization findings and validation.

## Upstream and project context

Based on the capabilities of [Muddyblack/nixdatifier](https://github.com/Muddyblack/nixdatifier).
Upstream code/history is preserved on `master`; development does not merge it into
`main` automatically. MIT notices are retained in [LICENSE](LICENSE).

Start AI work at [.ai/CONTEXT.md](.ai/CONTEXT.md), then follow the declared graph.
See [PLAN.md](PLAN.md) for architecture and release criteria.
