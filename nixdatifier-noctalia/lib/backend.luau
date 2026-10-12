local M = {}

function M.argv(command, extra)
  local result = { noctalia.getConfig("backend") }
  local config = noctalia.getConfig("config_file")
  if config and config ~= "" then
    table.insert(result, "--config")
    table.insert(result, noctalia.expandPath(config))
  end
  table.insert(result, command)
  for _, value in ipairs(extra or {}) do table.insert(result, tostring(value)) end
  return result
end

function M.call(command, extra, callback)
  local accepted = noctalia.runAsync(M.argv(command, extra), function(result)
    if result.timedOut then callback(nil, "Request timed out; retry in a terminal"); return end
    if result.stdoutTruncated or result.stderrTruncated then
      callback(nil, "Backend output was truncated"); return
    end
    local envelope, err = noctalia.json.decode(result.stdout or "")
    if not envelope then callback(nil, err or result.stderr or "Invalid backend response"); return end
    if envelope.api_version ~= 1 then callback(nil, "Unsupported backend API version"); return end
    if not envelope.ok then callback(nil, envelope.error or "Backend failed"); return end
    if result.exitCode ~= 0 then callback(nil, result.stderr or "Backend process failed"); return end
    callback(envelope.data, nil)
  end)
  if not accepted then callback(nil, "Could not start the backend") end
end

function M.query(view, target, argument, second, callback, force)
  local args = { view }
  if target then table.insert(args, "--target"); table.insert(args, target) end
  if argument then table.insert(args, "--argument"); table.insert(args, argument) end
  if second then table.insert(args, "--second"); table.insert(args, second) end
  if force then table.insert(args, "--force") end
  if noctalia.getSetting("shell.offline_mode") then table.insert(args, "--offline") end
  M.call("query", args, callback)
end

local function quote(value)
  return "'" .. string.gsub(tostring(value), "'", "'\\''") .. "'"
end

function M.terminal(action, target, argument)
  local args = M.argv("job", { action, "--target", target, "--argument", argument or "", "--confirm" })
  for i, value in ipairs(args) do args[i] = quote(value) end
  return noctalia.runInTerminal(table.concat(args, " "))
end

return M
