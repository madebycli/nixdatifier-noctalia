local c = require("./components.luau")
local views = {
  overview = require("../views/overview.luau"),
  generations = require("../views/generations.luau"),
  updates = require("../views/updates.luau"),
  compare = require("../views/compare.luau"),
  tools = require("../views/tools.luau"),
  history = require("../views/history.luau"),
}
local tabs = { "overview", "generations", "updates", "compare", "tools", "history" }
local M = {}

function M.hasView(name) return name ~= nil and views[name] ~= nil end

function M.render(ctx)
  if not ctx.opened then return end
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
        c.button(c.tr("confirm.run"), ctx.confirm, "primary"),
        c.button(c.tr("confirm.cancel"), ctx.cancelPlan),
      }),
    }))
  end
  local view = views[ctx.tab]
  table.insert(children, ui.scroll({ key = "content-" .. ctx.tab, flexGrow = 1, gap = 12 }, { view.render(ctx) }))
  panel.render(ui.column({ gap = 12, padding = 18, flexGrow = 1 }, children))
end


return M
