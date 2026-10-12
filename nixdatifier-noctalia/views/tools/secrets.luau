local c = require("../../lib/components.luau")
local M = {}
function M.render(ctx)
  local rows = { c.text(c.tr("secrets.metadata"), true),
    c.button(c.tr("action.inspect"), function() ctx.query("secrets") end) }
  for _, group in ipairs((ctx.data.secrets or {}).deployed or {}) do
    table.insert(rows, c.title(group.path))
    table.insert(rows, c.output(group.error or table.concat(group.names or {}, "\n")))
  end
  for _, source in ipairs((ctx.data.secrets or {}).sources or {}) do
    table.insert(rows, c.text(source.path, true))
  end
  return c.card(rows)
end
return M
