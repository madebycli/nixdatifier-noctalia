local backend = require("./lib/backend.luau")
local current = nil
local pending = {}
local elapsed = 0
local checks = 0
local epoch = 0

local function offline() return noctalia.getSetting("shell.offline_mode") == true end

local function probe(view, force)
  if pending[view] or not current then return end
  local captured, generation = current, epoch
  pending[view] = true
  noctalia.state.set("loading." .. view, true)
  backend.query(view, captured, nil, nil, function(data, err)
    if generation ~= epoch or captured ~= current then return end
    pending[view] = false
    noctalia.state.set("loading." .. view, false)
    noctalia.state.set("error." .. view, err or "")
    if data then
      noctalia.state.set(view, data)
      if view == "updates" and data.updates and data.updates > 0
        and noctalia.getConfig("notifications") and not force then
        noctalia.notify("Nixdatifier", tostring(data.updates) .. " " .. noctalia.tr("updates.available"))
      end
    end
  end, force)
end

local function targetKind()
  for _, target in ipairs(noctalia.state.get("targets") or {}) do
    if target.id == current then return target.kind end
  end
  return "profile"
end

local function refresh(force)
  probe("generations", force)
  probe("health", force)
  if targetKind() ~= "profile" then probe("updates", force) end
end

local function select(id)
  if id == current then return end
  current = id
  epoch = epoch + 1
  pending = {}
  for _, view in ipairs({ "generations", "updates", "health" }) do
    noctalia.state.set(view, nil)
    noctalia.state.set("error." .. view, "")
    noctalia.state.set("loading." .. view, false)
  end
  elapsed, checks = 0, 0
  refresh(false)
end

local function loadTargets()
  local generation = epoch
  backend.call("targets", {}, function(data, err)
    if generation ~= epoch then return end
    noctalia.state.set("error.targets", err or "")
    if not data then return end
    noctalia.state.set("targets", data.rows)
    local chosen = data.rows[1] and data.rows[1].id
    for _, target in ipairs(data.rows) do if target.id == current then chosen = current end end
    if chosen then
      local same = current == chosen
      noctalia.state.set("selectedTarget", chosen)
      select(chosen)
      if same then refresh(false) end
    end
  end)
end

function update()
  noctalia.setUpdateInterval(1000)
  elapsed, checks = elapsed + 1, checks + 1
  if elapsed >= 60 then elapsed = 0; probe("generations", false); probe("health", false) end
  if checks >= noctalia.getConfig("check_interval") then
    checks = 0
    if targetKind() ~= "profile" and not offline() then probe("updates", false) end
  end
end

function onIpc(event)
  if event == "refresh" then refresh(true)
  elseif event == "reload" then loadTargets() end
end

function onConfigChanged()
  epoch = epoch + 1
  pending = {}
  current = nil
  loadTargets()
end

noctalia.state.watch("selectedTarget", function(id) if id then select(id) end end)
noctalia.state.watch("refreshRequested", function() refresh(true) end)
noctalia.state.watch("reloadRequested", function() loadTargets() end)
onConfigChanged()
