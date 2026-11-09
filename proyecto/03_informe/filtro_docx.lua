-- Filtro pandoc para la versión Word/Google Docs del informe.
-- Google Docs pierde símbolos (≤, ∈, μ, λ, ∑) al importar ecuaciones de Word; por eso las fórmulas se
-- escriben como texto con formato (cursiva, subíndices, superíndices y símbolos Unicode), que se ve igual
-- en Word, LibreOffice y Google Docs. Se usa el render "plain" de pandoc (el mismo de HTML sin MathML).

local function a_texto(m)
  local html = pandoc.write(pandoc.Pandoc({ pandoc.Plain({ m }) }), "html")
  local doc = pandoc.read(html, "html")
  if #doc.blocks == 0 then return {} end
  return doc.blocks[1].content
end

function Math(m)
  return a_texto(m)
end

-- Ecuaciones destacadas: párrafo centrado
function Para(p)
  if #p.content == 1 and p.content[1].t == "Math" and p.content[1].mathtype == "DisplayMath" then
    return pandoc.Div({ pandoc.Para(a_texto(p.content[1])) }, { ["custom-style"] = "Ecuacion" })
  end
end

return { { Para = Para }, { Math = Math } }
