local function render()
  local generations = noctalia.state.get("generations") or {}
  local updates = noctalia.state.get("updates") or {}
  local active = ""
  for _, row in ipairs(generations.rows or {}) do
    if row.running then active = "#" .. tostring(row.number); break end
  end
  if active == "" then
    for _, row in ipairs(generations.rows or {}) do
      if row.selected then active = "#" .. tostring(row.number); break end
    end
  end
  local count = updates.updates or 0
  barWidget.setGlyph("snowflake")
  barWidget.setText(count > 0 and tostring(count) or active)
  barWidget.setGlyphColor(count > 0 and "primary" or "on_surface")
  barWidget.setTooltip({ { "Nixdatifier", noctalia.state.get("selectedTarget") or "" },
    { noctalia.tr("updates.title"), tostring(count) },
    { noctalia.tr("generations.title"), active } })
end

function update() noctalia.setUpdateInterval(60000); render() end
function onClick() noctalia.togglePanel("madebycli/nixdatifier-noctalia:panel") end
function onRightClick() noctalia.openSettings() end
for _, key in ipairs({ "generations", "updates", "selectedTarget" }) do noctalia.state.watch(key, render) end
render()
