# AI Context Route

```yaml
schema_version: 1
context_repo: https://github.com/madebycli/master-context
project_id: nixdatifier-noctalia
source_repo: https://github.com/madebycli/nixdatifier-noctalia
context_root: projects/nixdatifier-noctalia/
entrypoint: projects/nixdatifier-noctalia/INDEX.md
```

Validate this exact mapping against REGISTRY.yaml. Read the declared entrypoint
before following relevant graph edges. The local .ai files mirror the project graph.
The only explicit cross-project dependency is projects/nix-config/INDEX.md.
Plans and handoffs belong under prompts/nixdatifier-noctalia/ in master-context.

main is newest development; master is upstream-only. Do not create a stable
version branch until a verified stable release. Update status, tasks, decisions,
risks and tests after changes. Never claim unobserved builds or host tests.
