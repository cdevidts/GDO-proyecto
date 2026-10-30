"""Convierte informe.md en Informe_Ventisur.docx (editable en Word) e Informe_Ventisur.pdf.

Uso:  python construir_informe.py     (requiere pandoc, python-docx y Node con Playwright)
"""
import json
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AQUI = Path(__file__).resolve().parent
REF = AQUI / "reference.docx"
DOCX = AQUI / "Informe_Ventisur.docx"


def referencia():
    datos = subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], capture_output=True, check=True).stdout
    REF.write_bytes(datos)
    d = Document(REF)
    for s in d.sections:
        s.top_margin = s.bottom_margin = Cm(1.5)
        s.left_margin = s.right_margin = Cm(1.7)
    tam = {"Normal": 9, "Body Text": 9, "First Paragraph": 9, "Compact": 8, "Title": 15, "Subtitle": 10,
           "Author": 9, "Heading 1": 12, "Heading 2": 10, "Image Caption": 8, "Table Caption": 8}
    for nombre, pt in tam.items():
        try:
            st = d.styles[nombre]
        except KeyError:
            continue
        st.font.size = Pt(pt)
        st.font.name = "Calibri"
        pf = st.paragraph_format
        pf.space_before = Pt(6 if nombre.startswith("Heading 1") else 3 if nombre.startswith("Heading") else 0)
        pf.space_after = Pt(2 if nombre.startswith("Heading") else 3)
        if nombre.startswith("Heading"):
            st.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    d.save(REF)


def _bordes(tabla):
    tbl = tabla._tbl
    pr = tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "bottom", "insideH"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "A0A0A0")
        b.append(e)
    pr.append(b)


def post_proceso():
    d = Document(DOCX)
    for t in d.tables:
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        _bordes(t)
        for i, fila in enumerate(t.rows):
            for celda in fila.cells:
                for p in celda.paragraphs:
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.space_before = Pt(0)
                    for r in p.runs:
                        r.font.size = Pt(7.5)
                        if i == 0:
                            r.font.bold = True
    d.save(DOCX)


def pdf_desde_html():
    """El PDF se arma vía HTML + MathML impreso con Chromium (LibreOffice no dibuja bien las ecuaciones)."""
    html = AQUI / "informe.html"
    subprocess.run(["pandoc", "informe.md", "-s", "--mathml", "--embed-resources", "--css", "estilo.css",
                    "--metadata", "lang=es", "-o", str(html)], cwd=AQUI, check=True)
    pdf = AQUI / "Informe_Ventisur.pdf"
    pie = ('<div style="font-size:7pt;width:100%;text-align:center;color:#666">Ventisur · Informe técnico · '
           '<span class="pageNumber"></span>/<span class="totalPages"></span></div>')
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.goto({json.dumps(html.as_uri())});
  await pg.pdf({{ path: {json.dumps(str(pdf))}, preferCSSPageSize: true, printBackground: true,
                 displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: {json.dumps(pie)} }});
  await b.close();
}})();
"""
    subprocess.run(["node", "-e", js], check=True)  # Playwright de Node (Chromium)
    html.unlink()
    return pdf


def main():
    referencia()
    subprocess.run(["pandoc", "informe.md", "-o", str(DOCX), "--reference-doc", str(REF), "--resource-path", str(AQUI)],
                   cwd=AQUI, check=True)
    post_proceso()
    REF.unlink()
    pdf = pdf_desde_html()
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    print(pdf, [l for l in info.splitlines() if l.startswith("Pages")])


if __name__ == "__main__":
    main()
