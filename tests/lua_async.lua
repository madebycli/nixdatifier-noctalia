-- Deferred callbacks exercise races that a synchronous UI mock cannot reveal.
return function(h)
  local synchronous = noctalia.runAsync
  local queue = {}
  noctalia.runAsync = function(argv, cb)
    return synchronous(argv, function(result) table.insert(queue, { cb = cb, result = result, argv = argv }) end)
  end
  local function complete(index, data)
    local item = table.remove(queue, index or 1)
    assert(item, "expected a pending request")
    if data then h.responses[item.result.stdout].data = data end
    item.cb(item.result)
  end
  local function drain() while #queue > 0 do complete() end end

  h.state.selectedTarget = h.target.id
  local ctx = require(h.root .. "/lib/panel-controller.luau").new()
  ctx.opened = true
  ctx.query("history")
  ctx.query("log", "id")
  complete(2, { text = "retained log" })
  assert(ctx.loading, "unrelated pending requests must keep loading status")
  complete(1)
  assert(ctx.data.log.text == "retained log" and ctx.data.history and not ctx.loading,
    "history refresh must not discard a log request")

  ctx.query("hash", "old")
  ctx.query("hash", "new")
  complete(2, { sri = "new" })
  complete(1, { sri = "old" })
  assert(ctx.data.hash.sri == "new", "old responses cannot overwrite newer results")

  ctx.ask("build")
  ctx.query("history")
  complete(2)
  complete(1)
  assert(ctx.confirmation, "read requests cannot cancel action planning")
  ctx.ask("preview")
  assert(not ctx.confirmation, "new planning must clear the previous action")
  ctx.opened = false
  ctx.cancel()
  ctx.opened = true
  complete()
  assert(not ctx.confirmation, "closing/reopening must reject a late plan callback")
  ctx.query("hash", "old config")
  ctx.reset()
  complete(1, { sri = "stale" })
  assert(not ctx.data.hash, "same-id target reload must invalidate requests")

  -- Filter first, then cap displayed matches. An older generation must stay searchable.
  local rows = {}
  for number = 150, 1, -1 do
    table.insert(rows, { number = number, date = "date", closure = "/nix/store/test" })
  end
  h.state.generations = { scope = "local", rows = rows }
  ctx.search = "#1 ·"
  local tree = require(h.root .. "/views/generations.luau").render(ctx)
  assert(h.find(tree, "#1 · date"), "generation search must include rows beyond the first 100")

  local comparison = require(h.root .. "/views/compare.luau")
  ctx.before, ctx.after = 1, 2
  table.insert(rows, 1, { number = 151, date = "date", closure = "/nix/store/new" })
  tree = comparison.render(ctx)
  assert(ctx.before == 1 and ctx.after == 2, "new generations cannot shift comparison identity")
  ctx.query("diff", "1", "2")
  local function byKey(node, key)
    if node.props.key == key then return node end
    for _, child in ipairs(node.children) do local found = byKey(child, key); if found then return found end end
  end
  byKey(tree, "compare-before").props.onChange("0")
  complete(1, { text = "old selection" })
  assert(ctx.before == 151 and not ctx.data.diff, "changed comparison selections must discard late results")

  -- Same-id reloads reject every probe started against the previous configuration.
  h.serviceReload("reload")
  complete(1, { rows = { h.target } })
  drain()
  h.serviceReload("refresh")
  assert(#queue == 3)
  h.serviceReload("reload")
  complete(4, { rows = { h.target } })
  assert(h.state.updates == nil, "reload must clear previous results")
  complete(3, { updates = 99, rows = {} })
  assert(h.state.updates == nil, "stale service response must not cross a target revision")
  drain()
  assert(h.state.updates.updates == 1)

  h.serviceReload("reload")
  h.serviceReload("reload")
  local newer = { id = h.target.id, label = "New", kind = "nixos", flake = "/new", attribute = "nyx", host = "nyx" }
  complete(2, { rows = { newer } })
  complete(1, { rows = { h.target } })
  assert(h.state.targets[1].flake == "/new", "late target loaders cannot overwrite newer configuration")
  drain()

  h.advance(61000)
  h.serviceUpdate()
  assert(#queue == 2, "elapsed clock time must trigger health probes after a delayed tick")
  h.serviceUpdate()
  assert(#queue == 2, "pending probes must be coalesced")
  drain()
  noctalia.runAsync = synchronous
end
