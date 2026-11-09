"""Convierte informe.md en Informe_Ventisur.pdf (entrega en LaTeX: portada + cuerpo ≤ 6 páginas) e Informe_Ventisur.docx (editable en Word).

Uso:  python construir_informe.py          (requiere pandoc, python-docx y XeLaTeX de TeX Live)
      python construir_informe.py --html   (PDF anterior: HTML + Chromium vía Node Playwright)

Registro visual SOBRIO (ver estilo.css): texto tinta casi monocromo, tablas tipo booktabs con cifras
alineadas a la derecha, fila total con filete, tablas y figuras numeradas. El único acento de color
(#1f5fae) es la regla bajo el bloque de título; el resto va en tinta.
  - PDF: pandoc -> HTML + MathML (estilo.css, fuente Inter) -> Chromium (Playwright de Node).
  - DOCX: pandoc con un reference.docx generado aquí (Times New Roman, en negro).
"""
import json
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

AQUI = Path(__file__).resolve().parent
REF = AQUI / "reference.docx"
DOCX = AQUI / "Informe_Ventisur.docx"

# Tokens del sistema visual (registro sobrio)
INK, INK2, INK3, HAIR, HAIR2, ACENTO = "000000", "333333", "555555", "BFBFBF", "D9D9D9", "000000"
FUENTE_DOCX = "Times New Roman"

# Fila "total" de una tabla: su primera celda va entera en negrita en informe.md
# (**Total**, **Costo total (MM$)**, **Costo de elevar el servicio vs A**) -> filete superior + negrita.
TD_TOTAL = re.compile(r"^\s*<strong>[^<]*</strong>\s*$")


# ----------------------------------------------------------------------------------------------
# DOCX
# ----------------------------------------------------------------------------------------------
def _rfonts(rpr, nombre=FUENTE_DOCX):
    """Fija la fuente explícita y elimina las referencias al tema (que tienen prioridad en Word)."""
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        rf.attrib.pop(qn(att), None)
    for att in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(att), nombre)


def _borde_parrafo(estilo, lado, sz, color, espacio=4):
    ppr = estilo.element.get_or_add_pPr()
    bdr = ppr.find(qn("w:pBdr"))
    if bdr is None:
        bdr = OxmlElement("w:pBdr")
        ppr.append(bdr)
    e = OxmlElement(f"w:{lado}")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), str(sz))
    e.set(qn("w:space"), str(espacio))
    e.set(qn("w:color"), color)
    bdr.append(e)


def _estilo(d, nombre):
    """Busca un estilo por su nombre visible (python-docx no encuentra 'Heading 1' del reference.docx de pandoc)."""
    for st in d.styles:
        if st.name == nombre:
            return st
    raise KeyError(nombre)


def referencia():
    """reference.docx de pandoc con el Times New Roman, todo en negro."""
    datos = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], capture_output=True, check=True).stdout
    REF.write_bytes(datos)
    d = Document(REF)
    for s in d.sections:
        s.top_margin, s.bottom_margin = Cm(1.6), Cm(1.7)
        s.left_margin = s.right_margin = Cm(1.8)
        s.footer_distance = Cm(0.8)

    # Fuente del tema y valores por defecto -> Times New Roman explícito
    for parte in d.part.package.iter_parts():
        if str(parte.partname).startswith("/word/theme/"):
            xml = parte.blob.decode("utf-8")
            xml = re.sub(r'(<a:(?:major|minor)Font>\s*<a:latin typeface=")[^"]*"', r'\1Times New Roman"', xml)
            parte._blob = xml.encode("utf-8")
    rpr_def = d.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
    _rfonts(rpr_def)

    # nombre: (tamaño pt, negrita, color, antes pt, después pt)
    tabla = {
        "Normal": (11, False, INK, 0, 0),
        "Body Text": (11, False, INK, 0, 4),
        "First Paragraph": (11, False, INK, 0, 4),
        "Compact": (11, False, INK, 0, 3),
        "Title": (18, True, INK, 0, 3),
        "Subtitle": (12, False, INK2, 0, 0),
        "Author": (11, False, INK2, 0, 10),
        "Heading 1": (14, True, INK, 12, 3),
        "Heading 2": (12, True, INK, 8, 2),
        "Caption": (9, False, INK2, 0, 3),
        "Image Caption": (9, False, INK2, 3, 9),
        "Table Caption": (9, False, INK2, 8, 3),
    }
    for nombre, (pt, negrita, color, antes, despues) in tabla.items():
        try:
            st = _estilo(d, nombre)
        except KeyError:
            continue
        st.font.size = Pt(pt)
        st.font.bold = negrita
        st.font.italic = False
        st.font.color.rgb = RGBColor.from_string(color)
        _rfonts(st.element.get_or_add_rPr())
        pf = st.paragraph_format
        pf.space_before, pf.space_after = Pt(antes), Pt(despues)
        if nombre in ("Body Text", "First Paragraph"):
            pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            pf.line_spacing = 1.08
        if nombre in ("Title", "Subtitle", "Author", "Caption", "Image Caption", "Table Caption"):
            pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    _estilo(d, "Subtitle").paragraph_format.keep_with_next = True
    # Filetes: 0,75 pt sobre Heading 1; regla de acento de 1,5 pt bajo el bloque de título (único acento)
    _borde_parrafo(_estilo(d, "Heading 1"), "top", 6, INK, 4)
    _borde_parrafo(_estilo(d, "Author"), "bottom", 12, ACENTO, 6)

    codigo = _estilo(d, "Verbatim Char")  # rutas y nombres de archivo: más chicos y en gris, como en el PDF
    codigo.font.size = Pt(8)
    codigo.font.color.rgb = RGBColor.from_string(INK2)

    # Estilos de bloque usados con custom-style en informe.md
    resp = d.styles.add_style("Respaldo", WD_STYLE_TYPE.PARAGRAPH)
    resp.base_style = _estilo(d, "Body Text")
    resp.font.size = Pt(8.5)
    resp.font.color.rgb = RGBColor.from_string(INK2)
    resp.paragraph_format.space_after = Pt(6)
    reco = d.styles.add_style("Recomendacion", WD_STYLE_TYPE.PARAGRAPH)
    reco.base_style = _estilo(d, "Body Text")
    reco.paragraph_format.left_indent = Cm(0.3)
    reco.paragraph_format.space_before = Pt(4)
    reco.paragraph_format.space_after = Pt(6)
    _borde_parrafo(reco, "left", 6, INK, 6)
    d.save(REF)


def _tc_borde(celda, lado, sz, color):
    tcpr = celda._tc.get_or_add_tcPr()
    b = tcpr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders")
        tcpr.append(b)
    e = OxmlElement(f"w:{lado}")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), str(sz))
    e.set(qn("w:color"), color)
    b.append(e)


def _bordes_booktabs(tabla):
    pr = tabla._tbl.tblPr
    for viejo in pr.findall(qn("w:tblBorders")):
        pr.remove(viejo)
    b = OxmlElement("w:tblBorders")
    for lado, sz, color in (("top", 8, INK), ("left", 0, None), ("bottom", 8, INK), ("right", 0, None),
                            ("insideH", 2, HAIR2), ("insideV", 0, None)):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single" if sz else "nil")
        if sz:
            e.set(qn("w:sz"), str(sz))
            e.set(qn("w:color"), color)
        b.append(e)
    pr.append(b)


def _prefijo(parrafo, texto):
    """Antepone 'Tabla n. ' / 'Figura n. ' en negrita tinta al pie."""
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rpr.append(OxmlElement("w:b"))
    c = OxmlElement("w:color")
    c.set(qn("w:val"), INK)
    rpr.append(c)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = texto
    r.append(t)
    parrafo._p.insert(1 if parrafo._p.pPr is not None else 0, r)


def _campo(parrafo, instr):
    for tipo, texto in (("begin", None), (None, instr), ("separate", None), (None, "1"), ("end", None)):
        r = parrafo.add_run()
        if tipo:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), tipo)
            r._r.append(f)
        elif texto == instr:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = f" {instr} "
            r._r.append(it)
        else:
            r.text = texto


def post_proceso():
    d = Document(DOCX)
    # Tablas tipo booktabs: filetes 1 pt arriba/abajo, 0,5 pt bajo el encabezado, separadores hairline
    for t in d.tables:
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        _bordes_booktabs(t)
        siguiente = t._tbl.getnext()  # aire entre la tabla y el párrafo que la sigue
        if siguiente is not None and siguiente.tag == qn("w:p"):
            Paragraph(siguiente, t._parent).paragraph_format.space_before = Pt(7)
        for i, fila in enumerate(t.rows):
            runs = [r for p in fila.cells[0].paragraphs for r in p.runs if r.text.strip()]
            total = i > 0 and bool(runs) and all(r.bold for r in runs)
            for celda in fila.cells:
                if i == 0:
                    _tc_borde(celda, "bottom", 4, INK)
                if total:
                    _tc_borde(celda, "top", 4, INK)
                for p in celda.paragraphs:
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.line_spacing = 1.0
                    for r in p.runs:
                        r.font.size = Pt(7.5)
                        if i == 0 or total:
                            r.font.bold = True
    # Numeración de pies: "Tabla n." y "Figura n."
    nt = nf = 0
    for p in d.paragraphs:
        estilo = p.style.name if p.style is not None else ""
        if estilo == "Table Caption":
            nt += 1
            _prefijo(p, f"Tabla {nt}. ")
        elif estilo == "Image Caption":
            nf += 1
            _prefijo(p, f"Figura {nf}. ")
    # Pie de página: título a la izquierda, n / N a la derecha
    for s in d.sections:
        s.page_width, s.page_height = Cm(21.59), Cm(27.94)  # carta, igual que el PDF
        pie = s.footer.paragraphs[0] if s.footer.paragraphs else s.footer.add_paragraph()
        pie.text = ""
        ancho = s.page_width - s.left_margin - s.right_margin
        pie.paragraph_format.tab_stops.add_tab_stop(ancho, WD_TAB_ALIGNMENT.RIGHT)
        pie.add_run("Proyecto Integrador Ventisur · Informe técnico\t")
        _campo(pie, "PAGE")
        pie.add_run(" / ")
        _campo(pie, "NUMPAGES")
        for r in pie.runs:
            r.font.size = Pt(7)
            r.font.name = FUENTE_DOCX
            r.font.color.rgb = RGBColor.from_string(INK3)
    d.save(DOCX)


# ----------------------------------------------------------------------------------------------
# PDF
# ----------------------------------------------------------------------------------------------
def _texto(html):
    return re.sub(r"<[^>]+>", "", html).strip()


def _tabla(m):
    """Ajusta cada <table> de pandoc: tablas numéricas con ancho automático y fila total marcada."""
    t = m.group(0)
    numerica = "text-align: right" in t
    if numerica:  # el navegador reparte mejor las columnas de cifras que los anchos fijos de pandoc
        t = re.sub(r"<colgroup>.*?</colgroup>\s*", "", t, flags=re.S)
        t = re.sub(r'^<table style="width:100%;">', "<table>", t)
    clases = []
    ncol = len(re.findall(r"<th\b", t.split("</thead>")[0]))
    primera = re.search(r"<th[^>]*>(.*?)</th>", t, re.S)
    if primera and _texto(primera.group(1)) == "Mes":
        clases.append("meses")
    if ncol >= 7 or not numerica:
        clases.append("ancha")
    if numerica:
        clases.append("cifras")
    if clases:
        t = re.sub(r"^<table(?: style=\"[^\"]*\")?", f'<table class="{" ".join(clases)}"', t)

    def fila(mf):
        tr = mf.group(0)
        celda = re.search(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if celda and TD_TOTAL.match(celda.group(1)):
            if tr.startswith('<tr class="'):
                tr = tr.replace('<tr class="', '<tr class="total ', 1)
            else:
                tr = tr.replace("<tr", '<tr class="total"', 1)
        return tr
    return re.sub(r"<tr\b.*?</tr>", fila, t, flags=re.S)


def _h2_resultado(m):
    """'Solicitud n. … — **Z = …**' -> resultado alineado a la derecha del título."""
    return (f'<h2{m.group(1)} class="con-res"><span class="tit">{m.group(2).strip()}</span>'
            f'<span class="res">{m.group(3).strip()}</span></h2>')


def _sin_corte(html):
    """Espacio duro entre cifra y unidad ('10 %', '301,1 MM$', '90 m³', '7.000 u') para que no se separen al justificar."""
    cuerpo = html.split("<body", 1)
    if len(cuerpo) < 2:
        return html
    trozos = re.split(r"(<[^>]+>)", cuerpo[1])
    for i in range(0, len(trozos), 2):  # solo texto, nunca dentro de etiquetas
        trozos[i] = re.sub(r"(\d) (%|MM\$|MM\b|m³|u\b|u-mes\b)", "\\1\u00a0\\2", trozos[i])
    return cuerpo[0] + "<body" + "".join(trozos)


def html_final(html):
    html = _sin_corte(html)
    html = re.sub(r"<table\b.*?</table>", _tabla, html, flags=re.S)
    # \bar / \overline / \underline de una letra: Inter no tiene tabla MATH y el acento queda corto y corrido
    html = re.sub(r'<mover><mi>([^<]*)</mi><mo accent="true">[‾¯]</mo></mover>', r'<mi class="sobre">\1</mi>', html)
    html = re.sub(r'<munder><mi>([^<]*)</mi><mo accent="true">_</mo></munder>', r'<mi class="bajo">\1</mi>', html)
    html = re.sub(r"<h2([^>]*)>((?:(?!</h2>).)*?)\s+—\s+<strong>(Z\s*=[^<]*)</strong>\s*</h2>", _h2_resultado, html, flags=re.S)
    return html


PIE = ('<div style="box-sizing:border-box;width:100%;padding:0 1.65cm;font-family:Inter,sans-serif;'
       'font-size:6.5pt;color:#6b7580;-webkit-print-color-adjust:exact">'
       '<div style="display:flex;justify-content:space-between;border-top:0.5pt solid #d9dde2;padding-top:4pt">'
       '<span>Proyecto Integrador Ventisur · Informe técnico</span>'
       '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div></div>')


def pdf_desde_html():
    """El PDF se arma vía HTML + MathML impreso con Chromium (LibreOffice no dibuja bien las ecuaciones)."""
    html = AQUI / "informe.html"
    subprocess.run(["pandoc", "informe.md", "-s", "--mathml", "--embed-resources", "--css", "estilo.css",
                    "--metadata", "lang=es", "-o", str(html)], cwd=AQUI, check=True)
    html.write_text(html_final(html.read_text(encoding="utf-8")), encoding="utf-8")
    pdf = AQUI / "Informe_Ventisur.pdf"
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.goto({json.dumps(html.as_uri())});
  await pg.evaluate(() => document.fonts.ready);
  await pg.pdf({{ path: {json.dumps(str(pdf))}, preferCSSPageSize: true, printBackground: true,
                 displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: {json.dumps(PIE)} }});
  await b.close();
}})();
"""
    subprocess.run(["node", "-e", js], check=True)  # Playwright de Node (Chromium)
    html.unlink()
    return pdf


def pdf_latex():
    """PDF de entrega con LaTeX (pandoc -> plantilla.tex -> XeLaTeX): portada + cuerpo numerado.

    Deja además Informe_Ventisur_LaTeX.zip (informe.tex + figuras) listo para abrir en Overleaf
    (compilador: XeLaTeX)."""
    import shutil
    import tempfile
    import zipfile

    figs = AQUI.parent / "02_resultados" / "figuras"
    tex = subprocess.run(["pandoc", "informe.md", "-t", "latex", "--template", "plantilla.tex",
                          "--lua-filter", "filtro_latex.lua"], cwd=AQUI, check=True,
                         capture_output=True, text=True).stdout
    tex = tex.replace("../02_resultados/figuras/", "figuras/")
    pdf = AQUI / "Informe_Ventisur.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "figuras").mkdir()
        usadas = sorted(set(re.findall(r"figuras/([\w.-]+\.png)", tex)))
        for f in usadas:
            shutil.copy(figs / f, tmp / "figuras" / f)
        (tmp / "informe.tex").write_text(tex, encoding="utf-8")
        for _ in range(2):  # 2 pasadas: referencia a la última página ("Página x de N")
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "informe.tex"],
                               cwd=tmp, capture_output=True, text=True)
            if r.returncode:
                raise RuntimeError("XeLaTeX falló:\n" + r.stdout[-3000:])
        shutil.copy(tmp / "informe.pdf", pdf)
        with zipfile.ZipFile(AQUI / "Informe_Ventisur_LaTeX.zip", "w", zipfile.ZIP_DEFLATED) as z:
            z.write(tmp / "informe.tex", "informe.tex")
            for f in usadas:
                z.write(tmp / "figuras" / f, f"figuras/{f}")
    return pdf


def main():
    referencia()
    subprocess.run(["pandoc", "informe.md", "-o", str(DOCX), "--reference-doc", str(REF), "--resource-path", str(AQUI)],
                   cwd=AQUI, check=True)
    post_proceso()
    REF.unlink()
    # PDF de entrega: LaTeX (por defecto). Con --html se usa la versión anterior HTML + Chromium.
    import sys

    pdf = pdf_desde_html() if "--html" in sys.argv else pdf_latex()
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    paginas = int(next(l.split()[-1] for l in info.splitlines() if l.startswith("Pages")))
    cuerpo = paginas - 1 if "--html" not in sys.argv else paginas  # la portada no cuenta en el límite
    print(pdf, f"{paginas} páginas ({cuerpo} de cuerpo)", "(OK ≤ 6)" if cuerpo <= 6 else "(EXCEDE el límite de 6)")


if __name__ == "__main__":
    main()
