local M = {}

function M.tr(key) return noctalia.tr(key) end

function M.text(text, secondary)
  return ui.label({ text = tostring(text or ""), color = secondary and "on_surface_variant" or "on_surface" })
end

function M.title(text)
  return ui.label({ text = text, fontWeight = "bold", color = "on_surface" })
end

function M.card(children, key)
  local radius = 12 * (noctalia.getSetting("shell.corner_radius_scale") or 1)
  local borders = noctalia.getSetting("shell.panel.borders")
  local mode = noctalia.getSetting("shell.panel.transparency_mode")
  return ui.column({ key = key, gap = 10, padding = 14, radius = radius,
    fill = mode == "solid" and "surface_variant" or "surface_variant/0.6",
    border = borders and "outline/0.4" or nil, borderWidth = borders and 1 or 0 }, children)
end

function M.button(label, callback, variant, enabled)
  return ui.button({ text = label, onClick = callback, variant = variant or "default",
    controlSize = "sm", enabled = enabled ~= false })
end

function M.empty(key)
  return M.card({ M.text(M.tr(key), true) })
end

function M.bytes(value)
  value = tonumber(value) or 0
  local suffix = { "B", "KiB", "MiB", "GiB", "TiB" }
  local i = 1
  while value >= 1024 and i < #suffix do value = value / 1024; i = i + 1 end
  return string.format("%.1f %s", value, suffix[i])
end

function M.output(text)
  return ui.label({ text = text or "", color = "on_surface", maxLines = 240 })
end

return M
