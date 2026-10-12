local controller = require("./lib/panel-controller.luau")
local layout = require("./lib/panel-layout.luau")
local ctx = controller.new()
local tick = 0

function ctx.render() layout.render(ctx) end

function onOpen(context)
  ctx.opened = true
  if layout.hasView(context) then ctx.tab = context end
  tick = 0
  panel.setWantsSecondTicks(true)
  ctx.render()
  if ctx.tab == "history" then ctx.query("history") end
end

function onClose()
  ctx.opened = false
  ctx.cancel()
  panel.setWantsSecondTicks(false)
end

function update()
  tick = tick + 1
  if ctx.opened and ctx.tab == "history" and tick % 5 == 0 and not ctx.isPending("history") then ctx.query("history") end
end

noctalia.state.watch("selectedTarget", ctx.reset)
noctalia.state.watch("targetRevision", ctx.reset)
for _, key in ipairs({ "targets", "generations", "updates", "health", "error.targets", "error.generations",
  "error.updates", "error.health", "loading.generations", "loading.updates", "loading.health" }) do
  noctalia.state.watch(key, ctx.render)
end
