local c = require("../../lib/components.luau")
local M = {}
local modes = { "file", "path", "url" }
function M.render(ctx)
  local result = ctx.data.hash or {}
  return c.card({
    ui.select({ options = { c.tr("hash.file"), c.tr("hash.path"), c.tr("hash.url") }, selectedIndex = ctx.hashMode or 0,
      onChange = function(v) ctx.hashMode = tonumber(v); ctx.render() end }),
    ui.input({ key = "hash-value", placeholder = c.tr("hash.placeholder"), value = ctx.hashInput or "",
      onChange = function(v) ctx.hashInput = v end }),
    c.button(c.tr("hash.action"), function() ctx.query("hash", ctx.hashInput or "", modes[(ctx.hashMode or 0) + 1]) end),
    c.output(result.sri or result.hash or ""),
    c.button(c.tr("action.copy"), function() noctalia.copyToClipboard(result.sri or result.hash or "", "text/plain") end,
      "ghost", result.sri ~= nil or result.hash ~= nil),
  })
end
return M
