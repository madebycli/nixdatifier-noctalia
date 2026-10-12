local backend = require("./backend.luau")
local c = require("./components.luau")
local M = {}

function M.new()
  local epoch, serial, pending, errors = 0, {}, {}, {}
  local ctx = { tab = "overview", data = {}, error = "", loading = false, opened = false }
  function ctx.render() end

  function ctx.target()
    local id = noctalia.state.get("selectedTarget")
    for _, target in ipairs(noctalia.state.get("targets") or {}) do if target.id == id then return target end end
    return nil
  end

  local function status()
    ctx.loading = next(pending) ~= nil
    local keys, messages = {}, {}
    for key in pairs(errors) do table.insert(keys, key) end
    table.sort(keys)
    for _, key in ipairs(keys) do table.insert(messages, errors[key]) end
    ctx.error = table.concat(messages, "\n")
    ctx.render()
  end

  local function begin(channel, callback)
    local target = ctx.target()
    if not ctx.opened or not target then return nil end
    serial[channel] = (serial[channel] or 0) + 1
    local request, generation, ident = serial[channel], epoch, target.id
    pending[channel], errors[channel] = true, nil
    status()
    return function(data, err)
      if generation ~= epoch or request ~= serial[channel] or not ctx.opened
        or not ctx.target() or ctx.target().id ~= ident then return end
      pending[channel], errors[channel] = nil, err
      if data then callback(data, ident) end
      status()
    end, ident
  end

  function ctx.isPending(view) return pending[view] == true end

  function ctx.query(view, argument, second)
    local done, ident = begin(view, function(data) ctx.data[view] = data end)
    if done then backend.query(view, ident, argument, second, done) end
  end

  function ctx.cancelQuery(view)
    serial[view] = (serial[view] or 0) + 1
    pending[view], errors[view], ctx.data[view] = nil, nil, nil
    status()
  end

  function ctx.ask(action, argument)
    ctx.confirmation = nil
    local value = tostring(argument or "")
    local done, ident = begin("plan", function(data, target)
      ctx.confirmation = { action = action, argument = value, target = target, commands = data.commands }
    end)
    if done then backend.call("plan", { action, "--target", ident, "--argument", value }, done) end
  end

  function ctx.cancelPlan()
    serial.plan = (serial.plan or 0) + 1
    pending.plan, errors.plan, ctx.confirmation = nil, nil, nil
    status()
  end

  function ctx.confirm()
    local action = ctx.confirmation
    ctx.cancelPlan()
    if ctx.opened and action and ctx.target() and action.target == ctx.target().id then
      if not backend.terminal(action.action, action.target, action.argument) then errors.plan = c.tr("terminal.error") end
    end
    status()
  end

  function ctx.cancel()
    epoch = epoch + 1
    pending, errors = {}, {}
    ctx.confirmation = nil
    status()
  end

  function ctx.reset()
    ctx.data, ctx.before, ctx.after, ctx.search = {}, nil, nil, nil
    ctx.cancel()
  end

  return ctx
end

return M
