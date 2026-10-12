local c = require("../lib/components.luau")
local M = {}

function M.render(ctx)
  local data = noctalia.state.get("generations") or {}
  local options = {}
  for _, row in ipairs(data.rows or {}) do table.insert(options, "#" .. row.number) end
  if #options < 2 then return c.empty("compare.empty") end
  local function run()
    local a = data.rows[(ctx.before or 1) + 1]
    local b = data.rows[(ctx.after or 0) + 1]
    if a and b then ctx.query("diff", tostring(a.number), tostring(b.number)) end
  end
  local result = ctx.data.diff or {}
  return ui.column({ gap = 12 }, {
    c.card({ ui.row({ gap = 8 }, {
      ui.select({ options = options, selectedIndex = ctx.before or 1, flexGrow = 1,
        onChange = function(v) ctx.before = tonumber(v); ctx.render() end }),
      ui.glyph({ name = "arrow-right", color = "on_surface_variant" }),
      ui.select({ options = options, selectedIndex = ctx.after or 0, flexGrow = 1,
        onChange = function(v) ctx.after = tonumber(v); ctx.render() end }),
      c.button(c.tr("compare.action"), run),
    }) }),
    c.card({ c.output(result.text or c.tr("compare.hint")) }),
  })
end

return M
