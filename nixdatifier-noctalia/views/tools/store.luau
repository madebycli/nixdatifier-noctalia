local c = require("../../lib/components.luau")
local M = {}
function M.render(ctx)
  local data = ctx.data.store or {}
  return c.card({
    ui.input({ key = "store-path", placeholder = "/nix/store/…", value = ctx.storeInput or "",
      onChange = function(v) ctx.storeInput = v end }),
    c.button(c.tr("action.inspect"), function() ctx.query("store", ctx.storeInput or "") end),
    c.title(c.tr("store.roots")), c.output(table.concat(data.roots or {}, "\n")),
    c.title(c.tr("store.referrers")), c.output(table.concat(data.referrers or {}, "\n")),
    c.output(data.details or ""),
    c.button(c.tr("action.gc"), function() ctx.ask("gc") end),
  })
end
return M
