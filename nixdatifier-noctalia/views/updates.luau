local c = require("../lib/components.luau")
local M = {}
local modes = { "all", "base", "desktop", "apps" }

function M.render(ctx)
  local target = ctx.target()
  if not target then return c.empty("targets.empty") end
  local rows = {}
  if target.adapter == "madebycli" then
    local options = {}
    for _, mode in ipairs(modes) do table.insert(options, c.tr("mode." .. mode)) end
    table.insert(rows, c.card({ c.title(c.tr("updates.categories")),
      ui.row({ gap = 8 }, {
        ui.select({ options = options, selectedIndex = ctx.mode or 0, flexGrow = 1,
          onChange = function(value) ctx.mode = tonumber(value); ctx.render() end }),
        c.button(c.tr("action.check"), function() ctx.ask("preview-updates", modes[(ctx.mode or 0) + 1]) end),
        c.button(c.tr("action.refresh"), function() ctx.ask("refresh", modes[(ctx.mode or 0) + 1]) end),
      }), c.text(c.tr("updates.active"), true) }))
  end
  if target.kind == "profile" then
    table.insert(rows, c.card({ c.text(c.tr("profile.separate")),
      c.button(c.tr("action.upgrade"), function() ctx.ask("profile-upgrade") end) }))
    return ui.column({ gap = 12 }, rows)
  end
  local data = noctalia.state.get("updates") or {}
  if #(data.rows or {}) == 0 then table.insert(rows, c.empty("updates.empty")) end
  for _, row in ipairs(data.rows or {}) do
    local writable = row.status ~= "pinned" and row.status ~= "follows"
    table.insert(rows, c.card({
      ui.row({ justify = "space_between", align = "center", gap = 8 }, {
        c.title(row.name), c.text(c.tr("status." .. row.status), true),
      }),
      c.text(string.sub(row.revision or "", 1, 12) .. (row.upstream and " → " .. string.sub(row.upstream, 1, 12) or ""), true),
      c.text(row.error or "", true),
      c.button(c.tr("action.input"), function() ctx.ask("update-input", row.name) end, "default", writable),
    }, row.name))
  end
  return ui.column({ gap = 12 }, rows)
end

return M
