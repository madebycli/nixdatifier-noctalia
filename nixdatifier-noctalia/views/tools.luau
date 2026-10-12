local c = require("../lib/components.luau")
local secrets = require("./tools/secrets.luau")
local hashes = require("./tools/hashes.luau")
local store = require("./tools/store.luau")
local environments = require("./tools/environments.luau")
local M = {}
local ids = { "secrets", "hash", "store", "devenv" }
local views = { secrets, hashes, store, environments }

function M.render(ctx)
  local labels = {}
  for _, id in ipairs(ids) do table.insert(labels, c.tr(id .. ".title")) end
  local rows = {
    ui.select({ options = labels, selectedIndex = ctx.tool or 0,
      onChange = function(value) ctx.tool = tonumber(value); ctx.render() end }),
    views[(ctx.tool or 0) + 1].render(ctx),
  }
  local target = ctx.target()
  if target and target.adapter == "madebycli" then
    table.insert(rows, c.card({ c.title(c.tr("tools.personal")), ui.row({ gap = 8 }, {
      c.button(c.tr("action.clean"), function() ctx.ask("clean", "5") end),
      c.button(c.tr("action.optimize"), function() ctx.ask("optimize") end),
      c.button(c.tr("action.rollback"), function() ctx.ask("rollback") end),
    }), ui.row({ gap = 8 }, {
      c.button(c.tr("action.sync"), function() ctx.ask("sync") end),
      c.button(c.tr("action.save"), function() ctx.ask("save-config") end),
      c.button(c.tr("action.scripts"), function() ctx.ask("script-update") end),
    }) }))
  end
  return ui.column({ gap = 12 }, rows)
end

return M
