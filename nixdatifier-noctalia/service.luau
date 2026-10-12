local backend = require("./lib/backend.luau")
local current = nil
local pending = {}
local nextHealth = 0
local nextUpdates = 0
local epoch = 0
local targetRequest = 0
local revision = noctalia.state.get("targetRevision") or 0
local interval = 3600000

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
  local now = noctalia.nowMs()
  nextHealth, nextUpdates = now + 60000, now + interval
  refresh(false)
end

local function loadTargets()
  targetRequest = targetRequest + 1
  local request = targetRequest
  backend.call("targets", {}, function(data, err)
    if request ~= targetRequest then return end
    noctalia.state.set("error.targets", err or "")
    if not data then return end
    -- An id can keep its name while its flake or attribute changes.
    epoch = epoch + 1
    pending = {}
    noctalia.state.set("targets", data.rows)
    local chosen = data.rows[1] and data.rows[1].id
    local previous = current or noctalia.state.get("selectedTarget")
    for _, target in ipairs(data.rows) do if target.id == previous then chosen = previous end end
    current = nil
    revision = revision + 1
    noctalia.state.set("targetRevision", revision)
    if chosen then
      noctalia.state.set("selectedTarget", chosen)
      select(chosen)
    end
  end)
end

function update()
  noctalia.setUpdateInterval(1000)
  local now = noctalia.nowMs()
  if now >= nextHealth then nextHealth = now + 60000; probe("generations", false); probe("health", false) end
  if now >= nextUpdates then
    nextUpdates = now + interval
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
  interval = math.max(300, math.min(86400, tonumber(noctalia.getConfig("check_interval")) or 3600)) * 1000
  revision = revision + 1
  noctalia.state.set("targetRevision", revision)
  for _, view in ipairs({ "generations", "updates", "health" }) do
    noctalia.state.set(view, nil)
    noctalia.state.set("error." .. view, "")
    noctalia.state.set("loading." .. view, false)
  end
  current = nil
  loadTargets()
end

noctalia.state.watch("selectedTarget", function(id) if id then select(id) end end)
noctalia.state.watch("refreshRequested", function() refresh(true) end)
noctalia.state.watch("reloadRequested", function() loadTargets() end)
onConfigChanged()
