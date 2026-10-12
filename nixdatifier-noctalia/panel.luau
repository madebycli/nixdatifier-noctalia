local backend = require("./lib/backend.luau")
local c = require("./lib/components.luau")
local views = {
  overview = require("./views/overview.luau"),
  generations = require("./views/generations.luau"),
  updates = require("./views/updates.luau"),
  compare = require("./views/compare.luau"),
  tools = require("./views/tools.luau"),
  history = require("./views/history.luau"),
}
local tabs = { "overview", "generations", "updates", "compare", "tools", "history" }
local opened = false
local request = 0
local tick = 0
local ctx = { tab = "overview", data = {}, error = "", loading = false, confirmation = nil }

function ctx.target()
  local id = noctalia.state.get("selectedTarget")
  for _, target in ipairs(noctalia.state.get("targets") or {}) do if target.id == id then return target end end
  return nil
end

function ctx.query(view, argument, second)
  local target = ctx.target()
  if not target then return end
  request = request + 1
  local serial, ident = request, target.id
  ctx.loading, ctx.error = true, ""
  ctx.render()
  backend.query(view, ident, argument, second, function(data, err)
    if serial ~= request or not ctx.target() or ctx.target().id ~= ident then return end
    ctx.loading, ctx.error = false, err or ""
    if data then ctx.data[view] = data end
    ctx.render()
  end)
end

function ctx.ask(action, argument)
  local target = ctx.target()
  if not target then return end
  request = request + 1
  local serial, ident = request, target.id
  ctx.loading, ctx.error = true, ""
  backend.call("plan", { action, "--target", ident, "--argument", tostring(argument or "") }, function(data, err)
    if serial ~= request or not ctx.target() or ctx.target().id ~= ident then return end
    ctx.loading, ctx.error = false, err or ""
    if data then ctx.confirmation = { action = action, argument = tostring(argument or ""), target = ident, commands = data.commands } end
    ctx.render()
  end)
  ctx.render()
end

local function confirm()
  local pending = ctx.confirmation
  ctx.confirmation = nil
  if pending and ctx.target() and pending.target == ctx.target().id then
    if not backend.terminal(pending.action, pending.target, pending.argument) then
      ctx.error = c.tr("terminal.error")
    else ctx.error = "" end
  end
  ctx.render()
end

function ctx.render()
  if not opened then return end
  local targets = noctalia.state.get("targets") or {}
  local labels, selected = {}, 0
  for index, target in ipairs(targets) do
    table.insert(labels, target.label)
    if target.id == noctalia.state.get("selectedTarget") then selected = index - 1 end
  end
  local navigation = {}
  for _, name in ipairs(tabs) do
    table.insert(navigation, ui.button({ text = c.tr(name .. ".title"), selected = ctx.tab == name,
      variant = "ghost", controlSize = "sm", flexGrow = 1,
      onClick = function()
        ctx.tab = name
        if name == "history" then ctx.query("history") else ctx.render() end
      end }))
  end
  local children = {
    ui.row({ gap = 8, align = "center" }, {
      ui.glyph({ name = "snowflake", color = "primary" }), c.title("Nixdatifier"), ui.spacer({ flexGrow = 1 }),
      ui.button({ glyph = "refresh", variant = "ghost", tooltip = c.tr("action.reload"),
        onClick = function() noctalia.state.set("refreshRequested", noctalia.nowMs()); ctx.render() end }),
      ui.button({ glyph = "settings", variant = "ghost", tooltip = c.tr("settings.title"), onClick = function() noctalia.openSettings() end }),
      ui.button({ glyph = "x", variant = "ghost", tooltip = c.tr("action.close"), onClick = function() panel.close() end }),
    }),
    ui.select({ key = "target-select", options = labels, selectedIndex = selected, placeholder = c.tr("targets.select"),
      enabled = #labels > 0, onChange = function(value)
        local target = targets[(tonumber(value) or 0) + 1]
        if target then noctalia.state.set("selectedTarget", target.id) end
      end }),
    ui.row({ gap = 4 }, navigation), ui.separator({ color = "outline/0.4" }),
  }
  local serviceView = ctx.tab == "overview" and "health" or ctx.tab
  local error = ctx.error ~= "" and ctx.error or noctalia.state.get("error.targets") or ""
  if error == "" then error = noctalia.state.get("error." .. serviceView) or "" end
  if error ~= "" then table.insert(children, c.card({ ui.label({ text = error, color = "error" }) })) end
  if ctx.loading or noctalia.state.get("loading." .. serviceView) then
    table.insert(children, c.text(c.tr("loading"), true))
  end
  if ctx.confirmation then
    local lines = {}
    for _, argv in ipairs(ctx.confirmation.commands) do table.insert(lines, table.concat(argv, " ")) end
    table.insert(children, c.card({ c.title(c.tr("confirm.title")),
      c.text(ctx.confirmation.target .. " · " .. ctx.confirmation.action),
      c.text(table.concat(lines, "\n"), true), c.text(c.tr("confirm.terminal"), true),
      ui.row({ gap = 8 }, {
        c.button(c.tr("confirm.run"), confirm, "primary"),
        c.button(c.tr("confirm.cancel"), function() ctx.confirmation = nil; ctx.render() end),
      }),
    }))
  end
  local view = views[ctx.tab]
  table.insert(children, ui.scroll({ key = "content-" .. ctx.tab, flexGrow = 1, gap = 12 }, { view.render(ctx) }))
  panel.render(ui.column({ gap = 12, padding = 18, flexGrow = 1 }, children))
end

function onOpen(context)
  opened = true
  if context and views[context] then ctx.tab = context end
  panel.setWantsSecondTicks(true)
  ctx.render()
  if ctx.tab == "history" then ctx.query("history") end
end

function onClose() opened = false end

function update()
  tick = tick + 1
  if opened and ctx.tab == "history" and tick % 5 == 0 and not ctx.loading then ctx.query("history") end
end

noctalia.state.watch("selectedTarget", function()
  request = request + 1
  ctx.data, ctx.error, ctx.loading, ctx.confirmation = {}, "", false, nil
  ctx.before, ctx.after = nil, nil
  ctx.render()
end)
for _, key in ipairs({ "targets", "generations", "updates", "health", "error.targets", "error.generations",
  "error.updates", "error.health", "loading.generations", "loading.updates", "loading.health" }) do
  noctalia.state.watch(key, ctx.render)
end
