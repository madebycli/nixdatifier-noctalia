local c = require("../lib/components.luau")
local M = {}

function M.render(ctx)
  local data = noctalia.state.get("generations") or {}
  local options = {}
  for _, row in ipairs(data.rows or {}) do table.insert(options, "#" .. row.number) end
  if #options < 2 then return c.empty("compare.empty") end
  local before, after = 1, 0
  for index, row in ipairs(data.rows) do
    if row.number == ctx.before then before = index - 1 end
    if row.number == ctx.after then after = index - 1 end
  end
  ctx.before, ctx.after = data.rows[before + 1].number, data.rows[after + 1].number
  local function run()
    ctx.query("diff", tostring(ctx.before), tostring(ctx.after))
  end
  local function choose(side, value)
    local row = data.rows[(tonumber(value) or 0) + 1]
    if row then ctx[side] = row.number; ctx.cancelQuery("diff") end
  end
  local result = ctx.data.diff or {}
  return ui.column({ gap = 12 }, {
    c.card({ ui.row({ gap = 8 }, {
      ui.select({ key = "compare-before", options = options, selectedIndex = before, flexGrow = 1,
        onChange = function(v) choose("before", v) end }),
      ui.glyph({ name = "arrow-right", color = "on_surface_variant" }),
      ui.select({ key = "compare-after", options = options, selectedIndex = after, flexGrow = 1,
        onChange = function(v) choose("after", v) end }),
      c.button(c.tr("compare.action"), run),
    }) }),
    c.card({ c.output(result.text or c.tr("compare.hint")) }),
  })
end

return M
