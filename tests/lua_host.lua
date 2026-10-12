-- Contract harness, not a replacement for a real Noctalia/Wayland test.
local root = assert(os.getenv("NIXDATIFIER_PLUGIN"))
local originalLoadfile = loadfile
local stack, cache, state, watchers = {}, {}, {}, {}
local config = { backend = "nixdatifier-noctalia", config_file = "", check_interval = 3600, notifications = true }
local settings = { ["shell.offline_mode"] = false, ["shell.corner_radius_scale"] = 1,
  ["shell.panel.borders"] = true, ["shell.panel.transparency_mode"] = "solid" }
local target = { id = "nyx-niri", label = "Nyx Niri", kind = "nixos", flake = "/tmp/nix config", attribute = "nyx-niri", host = "nyx", adapter = "madebycli" }
local responses, lastTree, lastTerminal = {}, nil, nil
local clock = 1000
local function canonical(path)
  local parts = {}
  for item in string.gmatch(path, "[^/]+") do
    if item == ".." then table.remove(parts) elseif item ~= "." then table.insert(parts, item) end
  end
  return "/" .. table.concat(parts, "/")
end
function require(path)
  local caller = stack[#stack] or (root .. "/panel.luau")
  local absolute = canonical(string.sub(path, 1, 1) == "/" and path or (string.match(caller, "^(.*)/") .. "/" .. path))
  if cache[absolute] ~= nil then return cache[absolute] end
  local fn = assert(originalLoadfile(absolute))
  table.insert(stack, absolute)
  local result = fn()
  table.remove(stack)
  cache[absolute] = result
  return result
end
local function runEntry(name)
  local file = root .. "/" .. name
  table.insert(stack, file)
  assert(originalLoadfile(file))()
  table.remove(stack)
end
local function set(key, value)
  state[key] = value
  for _, fn in ipairs(watchers[key] or {}) do fn(value) end
end
noctalia = {
  getConfig = function(key) assert(config[key] ~= nil, "undeclared config " .. key); return config[key] end,
  getSetting = function(key) assert(settings[key] ~= nil, "unknown shell setting " .. key); return settings[key] end,
  expandPath = function(path) return path end,
  tr = function(key) return key end,
  log = function() end, notify = function() end,
  nowMs = function() return clock end, setUpdateInterval = function() end,
  togglePanel = function(id) assert(id == "madebycli/nixdatifier-noctalia:panel") end,
  openSettings = function() end, copyToClipboard = function() end,
  runInTerminal = function(command) lastTerminal = command; return true end,
  state = { get = function(key) return state[key] end, set = set,
    watch = function(key, fn) watchers[key] = watchers[key] or {}; table.insert(watchers[key], fn) end },
  json = { decode = function(token) return responses[token] end },
}
local counter = 0
noctalia.runAsync = function(argv, cb)
  assert(type(argv) == "table", "dynamic argv must not be a shell string")
  counter = counter + 1
  local token = tostring(counter)
  local data = {}
  if argv[2] == "targets" then data = { rows = { target,
    { id = "packages", label = "Packages", kind = "profile", flake = "", attribute = "", host = "", adapter = "generic", profile = "/tmp/profile" } } }
  elseif argv[2] == "plan" then data = { commands = { { "nix", "build", target.flake } } }
  elseif argv[3] == "generations" then data = { scope = "local", rows = {
    { number = 2, date = "2026-10-12", closure = "/nix/store/b", selected = true },
    { number = 1, date = "2026-10-11", closure = "/nix/store/a", running = true, booted = true },
  } }
  elseif argv[3] == "updates" then data = { updates = 1, rows = { { name = "nixpkgs", status = "update", revision = "aaa", upstream = "bbb" } } }
  elseif argv[3] == "health" then data = { host = "nyx", kernel = "6.18", nix = "nix 2.30", disks = {}, failed_units = {} }
  elseif argv[3] == "history" then data = { rows = {} }
  elseif argv[3] == "diff" then data = { text = "pkg 1 → 2" }
  end
  responses[token] = { api_version = 1, ok = true, data = data }
  cb({ exitCode = 0, stdout = token, stderr = "" })
  return true
end
ui = {}
local constructors = { "column", "row", "scroll", "label", "glyph", "button", "spacer", "separator", "select", "input", "progress" }
for _, name in ipairs(constructors) do
  ui[name] = function(props, children) return { type = name, props = props, children = children or {} } end
end
panel = { render = function(tree) lastTree = tree end, close = function() end, setWantsSecondTicks = function() end }
barWidget = setmetatable({}, { __index = function(_, key)
  return function(value) if key == "setText" then state.widgetText = value end end
end })
shortcut = setmetatable({}, { __index = function() return function() end end })
local function find(node, text)
  if node.props.text == text then return node end
  for _, child in ipairs(node.children) do local hit = find(child, text); if hit then return hit end end
end
local function allNodes(node, callback)
  callback(node)
  for _, child in ipairs(node.children) do allNodes(child, callback) end
end
runEntry("service.luau")
assert(state.selectedTarget == "nyx-niri", "service must select a target on first load")
assert(state.generations and state.updates and state.health, "service must populate all dashboard data")
-- A config reload must work even when the target id did not change.
onConfigChanged()
assert(state.generations, "same target reload must refresh")
local serviceReload, serviceUpdate = onIpc, update
runEntry("panel.luau")
onOpen("overview")
assert(lastTree)
for _, tab in ipairs({ "overview", "generations", "updates", "compare", "tools", "history" }) do
  onOpen(tab)
  assert(lastTree, "tab did not render: " .. tab)
  allNodes(lastTree, function(node)
    for _, prop in ipairs({ "color", "fill", "track", "border" }) do
      local value = node.props[prop]
      assert(not value or string.sub(value, 1, 1) ~= "#", "hardcoded palette color")
    end
  end)
end
onOpen("generations")
assert(find(lastTree, "action.delete").props.enabled == false, "selected generation delete must be disabled")
find(lastTree, "action.activate").props.onClick()
assert(find(lastTree, "confirm.title"), "action must show a concrete confirmation")
assert(lastTerminal == nil, "planning cannot start a job")
find(lastTree, "confirm.run").props.onClick()
assert(string.find(lastTerminal, "'--confirm'", 1, true), "only confirmation may launch a job")
assert(string.find(lastTerminal, "'--target' 'nyx-niri'", 1, true))
-- Changing target cancels an outstanding confirmation and clears cached results.
find(lastTree, "action.activate").props.onClick()
set("selectedTarget", "packages")
assert(not find(lastTree, "confirm.title"))
local c = require(root .. "/lib/components.luau")
settings["shell.corner_radius_scale"] = 0
settings["shell.panel.transparency_mode"] = "glass"
settings["shell.panel.borders"] = false
local card = c.card({ c.text("test") })
assert(card.props.radius == 0 and card.props.fill == "surface_variant/0.6" and card.props.borderWidth == 0)
runEntry("widget.luau")
set("updates", { updates = 0 })
update()
assert(state.widgetText == "#1", "running generation must take precedence over next boot")
local b = require(root .. "/lib/backend.luau")
b.terminal("direnv-allow", "nyx-niri", "a'$(touch nope)")
assert(string.find(lastTerminal, "'a'\\''$(touch nope)'", 1, true), "terminal argument must be shell quoted")
local scenarios = assert(originalLoadfile(root .. "/../tests/lua_async.lua"))()
scenarios({ state = state, set = set, target = target, find = find,
  tree = function() return lastTree end, responses = responses,
  serviceReload = serviceReload, serviceUpdate = serviceUpdate,
  advance = function(ms) clock = clock + ms end,
  root = root })
print("Native UI contract scenarios passed")
