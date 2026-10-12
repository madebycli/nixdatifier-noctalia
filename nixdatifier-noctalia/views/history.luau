local c = require("../lib/components.luau")
local M = {}

function M.render(ctx)
  local rows = { c.button(c.tr("action.reload"), function() ctx.query("history") end) }
  for _, row in ipairs((ctx.data.history or {}).rows or {}) do
    table.insert(rows, c.card({
      c.title(row.action .. " · " .. row.target),
      c.text(row.status .. " · " .. tostring(row.argument or ""), true),
      c.text(row.error or "", true),
      c.button(c.tr("history.log"), function() ctx.query("log", row.id) end),
    }, row.id))
  end
  if ctx.data.log then table.insert(rows, c.card({ c.output(ctx.data.log.text) })) end
  if #rows == 1 then table.insert(rows, c.empty("history.empty")) end
  return ui.column({ gap = 12 }, rows)
end

return M
