local c = require("../../lib/components.luau")
local M = {}
function M.render(ctx)
  local data = ctx.data.devenv or {}
  local rows = {
    ui.input({ key = "devenv-directory", placeholder = c.tr("devenv.path"), value = ctx.envInput or "",
      onChange = function(v) ctx.envInput = v end }),
    ui.row({ gap = 8 }, {
      c.button(c.tr("action.inspect"), function() ctx.query("devenv", ctx.envInput or "") end),
      c.button(c.tr("devenv.allow"), function() ctx.ask("direnv-allow", ctx.envInput or "") end),
    }),
    c.text(data.path, true),
    c.text(data.allowed and c.tr("devenv.allowed") or c.tr("devenv.untrusted"), true),
    c.text(table.concat(data.directives or {}, ", "), true),
  }
  for system, shells in pairs(data.outputs or {}) do
    table.insert(rows, c.text(system .. ": " .. table.concat(shells, ", ")))
  end
  return c.card(rows)
end
return M
