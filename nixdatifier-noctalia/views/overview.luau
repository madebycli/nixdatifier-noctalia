local c = require("../lib/components.luau")
local M = {}

function M.render(ctx)
  local target = ctx.target()
  if not target then return c.empty("targets.empty") end
  local data = noctalia.state.get("health") or {}
  local children = {
    c.card({ c.title(target.label), c.text(target.flake ~= "" and target.flake or target.profile, true),
      c.text(target.attribute ~= "" and target.attribute or c.tr("profile.packages"), true) }),
  }
  local actions = {}
  local function add(key, action, arg)
    table.insert(actions, c.button(c.tr(key), function() ctx.ask(action, arg) end))
  end
  if target.kind ~= "profile" then
    add("action.build", "build")
    add("action.preview", "preview")
  else add("action.upgrade", "profile-upgrade") end
  if target.kind == "nixos" and (target.host == "" or target.host == data.host) then
    add("action.rebuild", "rebuild")
    add("action.boot", "boot")
  elseif target.kind == "home-manager" then add("action.home", "home-switch") end
  table.insert(children, c.card({ ui.row({ gap = 8 }, actions) }))
  if data.host then
    table.insert(children, c.card({ c.title(c.tr("health.title")),
      c.text(data.host .. " · " .. (data.kernel or "")), c.text(data.nix, true),
      c.text(data.pending_reboot and c.tr("health.reboot") or c.tr("health.running"), data.pending_reboot ~= true),
      c.text(data.nix_error or "", true), c.text(data.systemd_error or "", true) }))
    for _, disk in ipairs(data.disks or {}) do
      table.insert(children, c.card({ c.title(disk.path),
        c.text(c.bytes(disk.free) .. " " .. c.tr("health.free") .. " / " .. c.bytes(disk.total), true),
        ui.progress({ progress = disk.fraction, fill = disk.fraction > 0.9 and "error" or "primary" }) }, disk.path))
    end
    if #(data.failed_units or {}) > 0 then
      table.insert(children, c.card({ c.title(c.tr("health.failed")), c.output(table.concat(data.failed_units, "\n")) }))
    end
  end
  return ui.column({ gap = 12 }, children)
end

return M
