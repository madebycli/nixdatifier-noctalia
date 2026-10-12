---
project_id: nixdatifier-noctalia
source_repo: https://github.com/madebycli/nixdatifier-noctalia
source_default_branch: main
status: development
updated: 2026-10-12
---

# Nixdatifier Noctalia Context Index

Read [[STATUS]], [[ARCHITECTURE]] and [[SOURCES]] first.
Follow [[DECISIONS]], [[TASKS]], [[RISKS]], [[TESTS]] and [[GRAPH]] as relevant.

Purpose: native Noctalia Nix tooling with multiple explicit flake/profile targets.
Explicit cross-project dependency: [[../nix-config/INDEX]] in master-context,
for madebycli's actual nyx/aether outputs and existing command safety contracts.

main contains the clean native rewrite. master remains upstream-only.
There is no stable release and no version snapshot branch yet.
