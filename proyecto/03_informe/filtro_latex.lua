-- Filtro pandoc para la versión LaTeX del informe.
--  * El bloque ".respaldo" pasa a la portada (metadato `respaldo`).
--  * El bloque ".recomendacion" se envuelve en el entorno LaTeX `recomendacion` (filete a la izquierda).
--  * Los envoltorios de estilo solo-HTML (style="...") se eliminan conservando su contenido.

local respaldo = nil

local function envolver(entorno, bloques)
  local out = { pandoc.RawBlock("latex", "\\begin{" .. entorno .. "}") }
  for _, b in ipairs(bloques) do table.insert(out, b) end
  table.insert(out, pandoc.RawBlock("latex", "\\end{" .. entorno .. "}"))
  return out
end

function Div(div)
  if div.classes:includes("respaldo") then
    respaldo = div.content
    return {}
  end
  if div.classes:includes("recomendacion") then
    return envolver("recomendacion", div.content)
  end
  if div.attributes["style"] then
    -- "no cortar" en HTML -> reservar espacio en LaTeX para no separar la FO de su tabla de restricciones
    local out = { pandoc.RawBlock("latex", "\\needspace{12\\baselineskip}") }
    for _, b in ipairs(div.content) do table.insert(out, b) end
    return out
  end
end

function Meta(meta)
  if respaldo then
    meta.respaldo = pandoc.MetaBlocks(respaldo)
  end
  return meta
end

-- En el PDF las figuras van al 86 % del ancho de texto (ahorra espacio sin perder legibilidad)
function Image(img)
  img.attributes["width"] = "86%"
  return img
end

return { { Div = Div, Image = Image }, { Meta = Meta } }
