local c = require("../lib/components.luau")
local M = {}

function M.render(ctx)
  local data = noctalia.state.get("generations") or {}
  local rows = {}
  if data.test_build then table.insert(rows, c.card({ c.text(c.tr("generations.test")) })) end
  if #(data.rows or {}) == 0 then
    return c.card({ c.text(c.tr("generations.empty")), c.text(data.scope or "", true) })
  end
  local filter = ctx.search or ""
  local normalized = string.lower(filter)
  local shown = 0
  table.insert(rows, ui.input({ key = "generation-search", placeholder = c.tr("generations.search"),
    value = filter, onChange = function(value) ctx.search = value; ctx.render() end }))
  for _, row in ipairs(data.rows) do
    local text = "#" .. row.number .. " · " .. row.date
    if string.find(string.lower(text), normalized, 1, true) then
      shown = shown + 1
      local badges = {}
      if row.running then table.insert(badges, c.tr("generations.running")) end
      if row.booted then table.insert(badges, c.tr("generations.booted")) end
      if row.selected then table.insert(badges, c.tr("generations.next")) end
      local items = { c.title(text), c.text(table.concat(badges, " · "), true), c.text(row.closure, true) }
      if ctx.target() and ctx.target().kind == "nixos" and data.scope == "local" then
        table.insert(items, ui.row({ gap = 8 }, {
          c.button(c.tr("action.activate"), function() ctx.ask("generation-switch", row.number) end),
          c.button(c.tr("action.boot"), function() ctx.ask("generation-boot", row.number) end),
          c.button(c.tr("action.delete"), function() ctx.ask("generation-delete", row.number) end,
            "destructive", not row.running and not row.booted and not row.selected),
        }))
      end
      table.insert(rows, c.card(items, tostring(row.number)))
      if shown >= 100 then break end
    end
  end
  return ui.column({ gap = 10 }, rows)
end

return M
