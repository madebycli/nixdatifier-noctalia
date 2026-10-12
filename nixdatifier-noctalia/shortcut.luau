function update()
  noctalia.setUpdateInterval(60000)
  shortcut.setLabel("Nixdatifier")
  shortcut.setIcon("snowflake")
  shortcut.setEnabled(true)
end
function onClick() noctalia.togglePanel("madebycli/nixdatifier-noctalia:panel") end
update()
