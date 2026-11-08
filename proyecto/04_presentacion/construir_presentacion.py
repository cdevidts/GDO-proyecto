"""Genera Presentacion_Ventisur.pptx (defensa de 5 minutos, 8 diapositivas 16:9).

Registro EXPRESIVO del sistema visual Ventisur (misma paleta que el informe, las figuras y el Excel):
fondos Azul noche a sangre, paneles divididos, tarjetas, números protagonistas, diagramas hechos con
formas y la hélice como motivo de marca. Texto y tablas son nativos y editables, en Calibri.
Colores fijos: P1 oro, P2 naranja, P3 ladrillo, Modelo A pizarra; el acento azul (#1f5fae) se reserva
para lo que se recomienda (plan Sol. 5 y lotes multiproducto). Estado (✓/✗/!) solo en chips con texto.
Las figuras slide_fig* (01_codigo/graficos.py) se generan al tamaño exacto de inserción y aquí se
insertan 1:1: 15,7 × 12,6 · 19,5 × 11,0 · 14,5 × 11,0 cm.

Uso:  cd proyecto/04_presentacion && python3 construir_presentacion.py
      (requiere python-pptx; con Pillow y la fuente Carlito/Calibri mide el texto para componer)
"""
import math
import re
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Cm, Pt

AQUI = Path(__file__).resolve().parent
FIG = AQUI.parent / "02_resultados" / "figuras"

# ───────────────────────── Paleta (sistema visual Ventisur) ─────────────────────────
NAVY, NAVY7, NAVY6 = "10233d", "1a3556", "24476f"  # Azul noche, palas de la hélice, buje
ACC, SKY, MIST = "1f5fae", "5aa9f0", "eaf1f8"  # acento (= lo recomendado), acento sobre navy, tinte
ON2, ON3 = "c9d6e3", "8fa3ba"  # texto secundario / terciario sobre navy
INK, INK6, INK5, INK2, PAPEL, BLANCO = "1c2127", "4a535d", "6b7580", "d9dde2", "f5f6f8", "ffffff"
ALERTA = "b42318"  # estado: solo en chips, siempre con ícono y texto
SERIE = {"P1": "d9a336", "P2": "cc5f22", "P3": "8c3b2f", "A": "2b333c"}
SERIE_TXT = {"P1": "8a6416", "P2": "b4521a", "P3": "8c3b2f"}  # variante de texto (≥ 4,5:1 sobre blanco)
ESCENARIO = {"Base": ACC, "+10 % espacio": "7fa3d6", "+10 % presupuesto": NAVY}
FUENTE = "Calibri"

# ───────────────────────── Retícula (cm) ─────────────────────────
W, H = 33.867, 19.05
M = 1.6  # margen lateral
CW = W - 2 * M  # ancho útil
Y_KICK, Y_TIT, Y_PIE = 1.2, 1.9, 18.05

prs = Presentation()
prs.slide_width, prs.slide_height = Cm(W), Cm(H)
VACIO = prs.slide_layouts[6]
ALIN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCLA = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


def rgb(h):
    return RGBColor.from_string(h.upper())


# ───────────────────────── Medición de texto ─────────────────────────
# Carlito tiene la misma métrica que Calibri: medir con ella permite componer sin desbordes.
_RUTAS = {False: ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf", "C:/Windows/Fonts/calibri.ttf",
                  "/Library/Fonts/Calibri.ttf"],
          True: ["/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf", "C:/Windows/Fonts/calibrib.ttf",
                 "/Library/Fonts/Calibri Bold.ttf"]}
_FUENTES = {}
LH = 1.2207  # interlineado sencillo de Calibri, en em (ascendente 0,952 + descendente 0,269)


def _fuente(negrita):
    if negrita not in _FUENTES:
        _FUENTES[negrita] = None
        try:
            from PIL import ImageFont
            for r in _RUTAS[negrita]:
                if Path(r).exists():
                    _FUENTES[negrita] = ImageFont.truetype(r, 200)
                    break
        except ImportError:
            pass
    return _FUENTES[negrita]


def pt2cm(p):
    return p * 2.54 / 72


def ancho(t, tam, negrita=False, spc=0):
    """Ancho (cm) de un texto en Calibri de `tam` pt; spc = interletraje en centésimas de pt."""
    f = _fuente(negrita)
    em = f.getlength(t) / 200 if f else 0.52 * len(t)
    return pt2cm(em * tam + len(t) * spc / 100)


def _par(p):
    """Normaliza un párrafo: str | lista de runs (texto, opciones) | dict(runs=..., vineta, nivel, esp)."""
    if isinstance(p, str):
        p = [(p, {})]
    if isinstance(p, list):
        p = {"runs": p}
    p = dict(p)
    p["runs"] = [(r, {}) if isinstance(r, str) else r for r in p["runs"]]
    return p


def _sangria(p):
    return (0.6 + 0.6 * p.get("nivel", 0)) if p.get("vineta") else 0.0


def _lineas(runs, w, tam0, neg0):
    """Líneas que ocupa un párrafo ajustado a w cm (corte en espacios, como PowerPoint)."""
    lineas, x, palabra, esp = 1, 0.0, 0.0, 0.0
    for t, o in runs + [(" ", {})]:
        tam, neg, spc = o.get("tam", tam0), o.get("b", neg0), o.get("spc", 0)
        for pieza in re.split(r"( +)", t):
            if not pieza:
                continue
            if pieza.startswith(" "):
                if palabra:
                    if x > 0 and x + esp + palabra > w + 1e-6:
                        lineas, x = lineas + 1, palabra
                    else:
                        x += (esp if x > 0 else 0) + palabra
                palabra, esp = 0.0, ancho(pieza, tam, neg, spc)
            else:
                palabra += ancho(pieza, tam, neg, spc)
    return lineas


def alto(pars, w, tam=16, negrita=False, esp=0, interl=1.0):
    """Alto (cm) de una lista de párrafos en un cuadro de ancho w sin márgenes internos."""
    total = 0.0
    for k, p in enumerate(pars):
        mx = max(o.get("tam", tam) for _, o in p["runs"])
        total += _lineas(p["runs"], w - _sangria(p), tam, negrita) * mx * LH * p.get("interl", interl)
        if k < len(pars) - 1:
            total += p.get("esp", esp)
    return pt2cm(total)


# ───────────────────────── Primitivas ─────────────────────────
def _fmt(r, tam, color, negrita, spc=None, sub=False):
    f = r.font
    f.name, f.size, f.bold, f.color.rgb = FUENTE, Pt(tam), bool(negrita), rgb(color)
    rPr = r._r.get_or_add_rPr()
    rPr.set("lang", "es-CL")
    if spc:
        rPr.set("spc", str(spc))  # interletraje (centésimas de pt): kickers y etiquetas en mayúsculas
    if sub:
        rPr.set("baseline", "-25000")


def _llena(tf, pars, tam, color, negrita, alin, esp, interl, vcol):
    for k, p in enumerate(pars):
        par = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        par.alignment = ALIN[p.get("alin", alin)]
        li = p.get("interl", interl)
        if li and li != 1.0:
            par.line_spacing = li
        e = p.get("esp", esp)
        if e and k < len(pars) - 1:
            par.space_after = Pt(e)
        if p.get("vineta"):  # viñeta real con sangría francesa (buClr/buFont/buChar van tras spcAft)
            nivel = p.get("nivel", 0)
            pPr = par._p.get_or_add_pPr()
            pPr.set("marL", str(int(Cm(_sangria(p)))))
            pPr.set("indent", str(-int(Cm(0.6))))
            etree.SubElement(etree.SubElement(pPr, qn("a:buClr")), qn("a:srgbClr")).set(
                "val", p.get("vcol", vcol).upper())
            etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
            etree.SubElement(pPr, qn("a:buChar")).set("char", "–" if nivel else "•")
        for t, o in p["runs"]:
            r = par.add_run()
            r.text = t
            _fmt(r, o.get("tam", tam), o.get("color", color), o.get("b", negrita), o.get("spc"), o.get("sub"))


def texto(s, x, y, w, pars, h=None, tam=16, color=INK, negrita=False, alin="l", ancla="t", esp=0,
          interl=1.0, vcol=INK5, nombre=None):
    """Cuadro de texto sin márgenes internos. Devuelve (forma, alto medido en cm)."""
    pars = [_par(p) for p in ([pars] if isinstance(pars, str) else pars)]
    hh = alto(pars, w, tam, negrita, esp, interl)
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h or hh))
    tf = tb.text_frame
    tf.word_wrap, tf.auto_size = True, MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = ANCLA[ancla]
    _llena(tf, pars, tam, color, negrita, alin, esp, interl, vcol)
    if nombre:
        tb.name = nombre
    return tb, hh


def _sin_estilo(sp):
    """python-pptx deja <p:style> (effectRef idx=2): LibreOffice lo dibuja como sombra. Fuera."""
    st = sp._element.find(qn("p:style"))
    if st is not None:
        sp._element.remove(st)


def forma(s, tipo, x, y, w, h, relleno=None, linea=None, grosor=1.0, rot=0, radio=None, nombre=None):
    sp = s.shapes.add_shape(tipo, Cm(x), Cm(y), Cm(w), Cm(h))
    if relleno:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(relleno)
    else:
        sp.fill.background()
    if linea:
        sp.line.color.rgb, sp.line.width = rgb(linea), Pt(grosor)
    else:
        sp.line.fill.background()
    if rot:
        sp.rotation = rot
    if radio is not None:
        sp.adjustments[0] = radio
    _sin_estilo(sp)
    if nombre:
        sp.name = nombre
    return sp


def rect(s, x, y, w, h, relleno, **kw):
    return forma(s, MSO_SHAPE.RECTANGLE, x, y, w, h, relleno, **kw)


def linea(s, x1, y1, x2, y2, color, grosor=1.0, redonda=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Cm(x1), Cm(y1), Cm(x2), Cm(y2))
    c.line.color.rgb, c.line.width = rgb(color), Pt(grosor)
    if redonda:
        c.line._get_or_add_ln().set("cap", "rnd")
    _sin_estilo(c)
    return c


def con_texto(sp, pars, tam=14, color=INK, negrita=False, alin="c", ancla="m", mar=(0.1, 0.1, 0, 0), esp=0):
    """Escribe dentro de una autoforma (el texto viaja con la forma al editar)."""
    tf = sp.text_frame
    tf.word_wrap, tf.auto_size = True, MSO_AUTO_SIZE.NONE
    tf.margin_left, tf.margin_right, tf.margin_top, tf.margin_bottom = (Cm(v) for v in mar)
    tf.vertical_anchor = ANCLA[ancla]
    pars = [_par(p) for p in ([pars] if isinstance(pars, str) else pars)]
    _llena(tf, pars, tam, color, negrita, alin, esp, None, INK5)
    return sp


def chip(s, x, y, txt, relleno, color=BLANCO, icono=None, tam=11, h=0.8, alin="l"):
    """Chip: rectángulo redondeado, texto en MAYÚSCULAS con interletraje. icono: 'x' (✗) o None.
    alin='r' alinea el borde derecho del chip en x. Devuelve el ancho (cm)."""
    pad, wi = 0.38, (0.62 if icono else 0.0)
    w = 2 * pad + wi + ancho(txt, tam, True, 100) + 0.6  # margen: evita el salto de línea al renderizar
    if alin == "r":
        x -= w
    sp = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, relleno, radio=0.5)
    con_texto(sp, [[(txt, {"spc": 100})]], tam=tam, color=color, negrita=True, alin="l",
              mar=(pad + wi, pad - 0.1, 0, 0))
    if icono == "x":  # ✗ dibujado con forma: no depende de la fuente
        forma(s, MSO_SHAPE.MATH_MULTIPLY, x + pad - 0.08, y + (h - 0.56) / 2, 0.56, 0.56, color)
    return w


def kicker(s, txt, oscuro=False, x=M, y=Y_KICK):
    col = SKY if oscuro else ACC
    rect(s, x, y + 0.17, 0.9, 0.12, col)
    texto(s, x + 1.25, y, 24, [[(txt.upper(), {"spc": 100})]], tam=11, color=col, negrita=True)


def titulo(s, txt, oscuro=False, x=M, w=CW, tam=30, y=Y_TIT):
    """Título-mensaje (máx. 2 líneas). Devuelve la y de su borde inferior."""
    _, h = texto(s, x, y, w, txt, tam=tam, color=BLANCO if oscuro else INK, negrita=True, nombre="Título")
    return y + h


def pie(s, n, oscuro=False, num_color=None):
    c = ON3 if oscuro else INK5
    texto(s, M, Y_PIE, 14, [[("Ventisur", {"b": True}), ("  ·  Gestión de Operaciones", {})]], tam=9, color=c)
    texto(s, W - M - 2, Y_PIE, 2, [[(f"{n:02d}", {"b": True})]], tam=9, color=num_color or c, alin="r")


def nueva(fondo=BLANCO):
    s = prs.slides.add_slide(VACIO)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(fondo)
    return s


def nota(s, txt):
    s.notes_slide.notes_text_frame.text = txt


def figura(s, archivo, x, y, w_cm, h_cm, nombre):
    """Inserta una figura slide_fig* 1:1 (se generó a w_cm × h_cm)."""
    pic = s.shapes.add_picture(str(FIG / archivo), Cm(x), Cm(y), Cm(w_cm), Cm(h_cm))
    pic.name = nombre
    return pic


def tam_que_cabe(runs_fn, w, tam_max, tam_min):
    """Mayor tamaño (pt) para el que un número protagonista cabe en una línea de ancho w."""
    for t in range(tam_max, tam_min - 1, -2):
        if _lineas(runs_fn(t), w, t, True) == 1:
            return t
    return tam_min


# ───────────────────────── Motivo de marca e íconos (formas) ─────────────────────────
def helice(s, cx, cy, R, pala, buje, centro=None):
    """Hélice de ventilador: 3 palas ovaladas (0,55R × R) a 0°, 120° y 240° + buje de 0,32R."""
    g = s.shapes.add_group_shape()
    g.name = "Hélice"
    for k in range(3):
        a = math.radians(k * 120)
        bx = cx + math.sin(a) * R * 0.5 - 0.275 * R
        by = cy - math.cos(a) * R * 0.5 - 0.5 * R
        forma(g, MSO_SHAPE.OVAL, bx, by, 0.55 * R, R, pala, rot=k * 120)
    forma(g, MSO_SHAPE.OVAL, cx - 0.16 * R, cy - 0.16 * R, 0.32 * R, 0.32 * R, buje)
    if centro:
        forma(g, MSO_SHAPE.OVAL, cx - 0.045 * R, cy - 0.045 * R, 0.09 * R, 0.09 * R, centro)
    return g


def ico_cajas(s, x, y, t, col, fondo):
    """P1 · inventario: cajas apiladas."""
    g = s.shapes.add_group_shape()
    g.name = "Ícono inventario"
    c = 0.44 * t
    for bx, by in ((0.04, 0.52), (0.52, 0.52), (0.28, 0.04)):
        rect(g, x + bx * t, y + by * t, c, c, col)
        rect(g, x + bx * t, y + by * t + 0.3 * c, c, 0.07 * t, fondo)  # cinta de la caja
    return g


def ico_reloj(s, x, y, t, col, fondo):
    """P2 · horas extra: reloj con insignia '+'."""
    g = s.shapes.add_group_shape()
    g.name = "Ícono horas extra"
    d = 0.84 * t
    forma(g, MSO_SHAPE.OVAL, x + 0.02 * t, y + 0.14 * t, d, d, None, col, 4.5)
    cx, cy = x + 0.02 * t + d / 2, y + 0.14 * t + d / 2
    linea(g, cx, cy, cx, cy - 0.27 * t, col, 4, True)
    linea(g, cx, cy, cx + 0.2 * t, cy + 0.06 * t, col, 4, True)
    forma(g, MSO_SHAPE.OVAL, cx - 0.06 * t, cy - 0.06 * t, 0.12 * t, 0.12 * t, col)
    b = 0.42 * t
    forma(g, MSO_SHAPE.OVAL, x + t - b, y, b, b, col, fondo, 2.5)
    forma(g, MSO_SHAPE.MATH_PLUS, x + t - b + 0.08 * t, y + 0.08 * t, b - 0.16 * t, b - 0.16 * t, BLANCO)
    return g


def ico_personas(s, x, y, t, col, fondo):
    """P3 · contratar / despedir: dos personas con insignias '+' y '−'."""
    g = s.shapes.add_group_shape()
    g.name = "Ícono contratación y despido"
    for k, signo in ((0, MSO_SHAPE.MATH_PLUS), (1, MSO_SHAPE.MATH_MINUS)):
        px = x + k * 0.52 * t
        forma(g, MSO_SHAPE.OVAL, px + 0.1 * t, y + 0.2 * t, 0.28 * t, 0.28 * t, col)
        forma(g, MSO_SHAPE.ROUND_2_SAME_RECTANGLE, px + 0.02 * t, y + 0.53 * t, 0.44 * t, 0.43 * t, col, radio=0.45)
        b = 0.3 * t
        forma(g, MSO_SHAPE.OVAL, px + 0.27 * t, y + 0.06 * t, b, b, col, fondo, 2.5)
        forma(g, signo, px + 0.27 * t + 0.05 * t, y + 0.11 * t, b - 0.1 * t, b - 0.1 * t, BLANCO)
    return g


# ───────────────────────── Tablas con estilo propio ─────────────────────────
SIN_ESTILO = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # "No Style, No Grid" de PowerPoint


def _celda(c, relleno, lnT=None, lnB=None, mar=(0.25, 0.25, 0.04, 0.04), ancla="ctr"):
    tcPr = c._tc.get_or_add_tcPr()
    for ch in list(tcPr):
        tcPr.remove(ch)
    for k, v in zip(("marL", "marR", "marT", "marB"), mar):
        tcPr.set(k, str(int(Cm(v))))
    tcPr.set("anchor", ancla)
    for tag, spec in (("lnL", None), ("lnR", None), ("lnT", lnT), ("lnB", lnB)):
        ln = etree.SubElement(tcPr, qn(f"a:{tag}"))
        if spec:
            ln.set("w", str(int(Pt(spec[0]))))
            ln.set("cap", "flat")
            ln.set("cmpd", "sng")
            ln.set("algn", "ctr")
            etree.SubElement(etree.SubElement(ln, qn("a:solidFill")), qn("a:srgbClr")).set("val", spec[1].upper())
            etree.SubElement(ln, qn("a:prstDash")).set("val", "solid")
        else:
            ln.set("w", "0")
            etree.SubElement(ln, qn("a:noFill"))
    if relleno:
        etree.SubElement(etree.SubElement(tcPr, qn("a:solidFill")), qn("a:srgbClr")).set("val", relleno.upper())
    else:
        etree.SubElement(tcPr, qn("a:noFill"))


def tabla(s, x, y, anchos, filas, alto_f=0.9, alto_enc=None, tam=14, tam_enc=13, alin=None, total=False,
          resaltar_col=None, enc_relleno=NAVY, enc_color=BLANCO, enc_regla=None, mar_izq=None, nombre="Tabla"):
    """Tabla nativa sin estilo de PowerPoint: encabezado navy, filetes inferiores finos, sin verticales,
    números a la derecha, fila total con filete superior de 1,5 pt y columna recomendada en tinte + negrita."""
    nf, nc = len(filas), len(filas[0])
    altos = [alto_enc or alto_f] + [alto_f] * (nf - 1)
    gf = s.shapes.add_table(nf, nc, Cm(x), Cm(y), Cm(sum(anchos)), Cm(sum(altos)))
    gf.name = nombre
    t = gf.table
    tblPr = gf._element.graphic.graphicData.tbl.tblPr
    tblPr.set("firstRow", "1")
    tblPr.set("bandRow", "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is None:
        sid = etree.SubElement(tblPr, qn("a:tableStyleId"))
    sid.text = SIN_ESTILO
    for j, a in enumerate(anchos):
        t.columns[j].width = Cm(a)
    for i, a in enumerate(altos):
        t.rows[i].height = Cm(a)
    alin = alin or ["l"] + ["r"] * (nc - 1)
    for i, fila in enumerate(filas):
        enc, es_total = i == 0, total and i == nf - 1
        for j, v in enumerate(fila):
            c = t.cell(i, j)
            runs = v if isinstance(v, list) else [(str(v), {})]
            p = c.text_frame.paragraphs[0]
            p.alignment = ALIN[alin[j]]
            destacada = resaltar_col == j and not enc
            for tt, o in runs:
                r = p.add_run()
                r.text = tt
                _fmt(r, o.get("tam", tam_enc if enc else tam), o.get("color", enc_color if enc else INK),
                     o.get("b", enc or es_total or destacada))
            if enc:
                lnB = enc_regla
            elif total and i == nf - 2:
                lnB = (1.5, INK)  # coincide con el filete superior de la fila total
            elif es_total:
                lnB = None
            else:
                lnB = (0.75, INK2)
            mar = (mar_izq[j] if (mar_izq and enc) else 0.25, 0.25, 0.04, 0.04)
            _celda(c, enc_relleno if enc else (MIST if destacada else None),
                   lnT=(1.5, INK) if es_total else None, lnB=lnB, mar=mar, ancla="b" if enc else "ctr")
    return gf, sum(altos)


def vinetas(items, tam=16, color=INK, esp=8, vcol=INK5):
    """Lista de viñetas. Item: str | (negrita, resto) | dict ya armado. Prefijo '  ' = nivel 2."""
    pars = []
    for it in items:
        nivel = 0
        if isinstance(it, str) and it.startswith("  "):
            nivel, it = 1, it.strip()
        if isinstance(it, list):  # lista de runs ya armada
            runs = it
        elif isinstance(it, tuple):
            runs = [(it[0], {"b": True}), (it[1], {})]
        else:
            runs = [(it, {})]
        pars.append({"runs": runs, "vineta": True, "nivel": nivel, "esp": esp, "vcol": vcol,
                     **({"runs": [(r[0], {**r[1], "tam": tam - 1, "color": INK6 if color == INK else color})
                                  for r in runs]} if nivel else {})})
    return pars


# ═════════════════════════ 1. Portada (navy, hélice) ═════════════════════════
s = nueva(NAVY)
g = s.shapes.add_group_shape()
g.name = "Rejilla"
for r in (6.4, 9.2, 12.0):  # anillos de la rejilla del ventilador
    forma(g, MSO_SHAPE.OVAL, 27.5 - r, 8.2 - r, 2 * r, 2 * r, None, NAVY7, 1.5)
helice(s, 27.5, 8.2, 10.5, NAVY7, NAVY6, centro=SKY)
rect(s, M, 5.0, 1.6, 0.16, SKY)
texto(s, M, 5.6, 19, [[("Proyecto Integrador", {})], [("Ventisur", {"tam": 66, "b": True})]],
      tam=30, color=BLANCO, interl=0.95)
texto(s, M, 10.35, 17.5, "Planificación agregada e inventarios determinísticos", tam=20, color=ON2)
texto(s, M, 15.4, 17, [[("Gestión de Operaciones · Universidad Adolfo Ibáñez", {})],
                       [("Cristóbal De Vidts · Constanza Catalán · Bellonce Bulnes · Matias Rojas Rodriguez", {"color": ON3})]], tam=14, color=BLANCO, esp=4)
nota(s, "15 s. Presentar el problema: plan de 12 meses para 3 ventiladores (unidad agregada) y luego cómo comprar 5 componentes.")

# ═════════════════════════ 2. Políticas simples (tarjetas) ═════════════════════════
s = nueva()
kicker(s, "Parte I · Planificación agregada")
yb = titulo(s, "Tres políticas simples: mismo costo laboral, distinto mecanismo")
texto(s, M, yb + 0.25, CW, [[("Las tres usan 240 trabajador-mes (288 MM$); ", {}),
                             ("cambia cómo absorben la demanda", {"b": True, "color": INK})]], tam=18, color=INK6)
tarjetas = [
    ("P1", "Tasa constante", ico_cajas, "Inventario", " (hasta 7.000 u)", "Inventario 52 MM$", "340,0",
     "Estable para personas y proveedores, pero guarda las ~6.000 u del peak 6,7 meses en promedio ($1.000/mes)"),
    ("P2", "Dotación + HE", ico_reloj, "Horas extra", " (6.000 u)", "HE 15 + inv. 12 MM$", "315,0",
     "Una HE ($2.500) = 2,5 meses de mantención; P1 guarda ~6,7 meses → la mejor regla simple"),
    ("P3", "Persecución", ico_personas, "Contratar/despedir", " (9 / 6)", "Movimientos 40,5 MM$", "329,5",
     "Casi sin inventario, pero cada contratación ($2,5 MM) y despido ($3 MM) pesa más; inestable"),
]
wc, y0, pad = (CW - 1.2) / 3, 5.15, 0.7
for i, (cod, nom, ico, mec, mec2, clave, total, txt) in enumerate(tarjetas):
    x = M + i * (wc + 0.6)
    wi = wc - 2 * pad
    hc = 16.95 - y0
    rect(s, x, y0, wc, hc, PAPEL, nombre=f"Tarjeta {cod}")
    ico(s, x + pad, y0 + 0.65, 1.9, SERIE[cod], PAPEL)
    texto(s, x + pad + 2.45, y0 + 0.7, wi - 2.45, [[(cod, {"b": True, "color": SERIE_TXT[cod], "tam": 22})],
                                                    [(nom, {})]], tam=18)
    yy = y0 + 3.0
    for etiqueta, contenido in (("MECANISMO", [(mec, {"b": True, "tam": 20}), (mec2, {"color": INK6})]),
                                ("COSTO CLAVE", [(clave, {})])):
        texto(s, x + pad, yy, wi, [[(etiqueta, {"spc": 100})]], tam=10, color=INK5, negrita=True)
        _, hv = texto(s, x + pad, yy + 0.5, wi, [contenido], tam=18)
        yy += 0.5 + hv + 0.45
    texto(s, x + pad, yy, wi, [[("COSTO TOTAL", {"spc": 100})]], tam=10, color=INK5, negrita=True)
    _, hn = texto(s, x + pad, yy + 0.3, wi, [[(total, {"b": True}), (" MM$", {"tam": 20, "color": INK6})]],
                  tam=54, interl=0.9)
    texto(s, x + pad, yy + 0.3 + hn + 0.35, wi, txt, tam=15, color=INK6)
    if cod == "P2":
        chip(s, x + wc - pad, y0 - 0.4, "Mejor simple", INK, alin="r")
pie(s, 2)
nota(s, "35 s. Énfasis: la diferencia no es la masa laboral (igual) sino el mecanismo. Umbrales: si HE > $4.917/u, P3 pasa a ser más barata que P2; P2 supera a P1 mientras HE < $6.667/u.")

# ═════════════════════════ 3. Modelo A (ficha del modelo + figura) ═════════════════════════
s = nueva()
kicker(s, "Parte I · Modelo A (MILP)")
yb = titulo(s, "Modelo A (MILP): combina los tres mecanismos → 300,75 MM$")
wl = 14.4  # columna izquierda
fx, fy = W - M - 15.7, yb + 0.75
figura(s, "slide_fig1_planes.png", fx, fy, 15.7, 12.6, "Figura producción e inventario")
texto(s, fx, fy + 12.6 + 0.15, 15.7,
      "Figura: producción del plan Sol. 5 (el Modelo A produce 400 u menos en octubre y 200 u más en "
      "enero y febrero); inventario neto de A y Sol. 5.", tam=12, color=INK5)
filas = [("OBJETIVO", "min laboral + contratación + despido + HE + inventario + pendientes; W, H, F enteras"),
         ("BALANCE", [("I(t−1) − B(t−1) + R + O − d = I − B", {})]),
         ("CAPACIDADES", "R ≤ 500·W,  O ≤ 150·W;  W(t) = W(t−1) + H − F;  límites 15–25 y ±3"),
         ("BORDE", "I(12) ≥ 1.000,  B(12) = 0,  bodega ≤ 7.500")]
pad, wlab = 0.55, 3.2
wf = wl - 2 * pad - wlab
hs = [alto([_par(f)], wf, 15) for _, f in filas]
hpanel = 2 * 0.5 + sum(hs) + 0.32 * (len(filas) - 1)
rect(s, M, fy, wl, hpanel, MIST, nombre="Ficha del modelo")
yy = fy + 0.5
for (lab, f), hf in zip(filas, hs):
    texto(s, M + pad, yy + 0.17, wlab, [[(lab, {"spc": 100})]], tam=10, color=INK5, negrita=True)
    texto(s, M + pad + wlab, yy, wf, [f], tam=15)
    yy += hf + 0.32
yy = fy + hpanel + 0.55
texto(s, M, yy, wl, [[("SOLUCIÓN ÓPTIMA", {"spc": 100})]], tam=10, color=INK5, negrita=True)
_, hn = texto(s, M, yy + 0.3, 8.0, [[("300,75", {"b": True}), (" MM$", {"tam": 20, "color": INK6})]],
              tam=54, interl=0.9)
texto(s, M + 8.0, yy + 0.55, wl - 8.0, [[("−14,25 MM$ (−4,5 %)", {"b": True, "tam": 18})],
                                        [("vs la mejor política simple", {})]], tam=15, color=INK6)
texto(s, M, yy + 0.3 + hn + 0.3, wl, vinetas([
    ("Solución: ", "despide 2 en marzo y mantiene 18 todo el año"),
    "  HE desde septiembre (saturada nov–feb), inventario solo 1–2 meses antes",
    "  Pendientes dic–ene: atrasar ($750) es más barato que adelantar ($1.000/mes)"], tam=16, esp=6))
pie(s, 3)
nota(s, "50 s. Contraintuitivo: despedir y luego usar HE al 100 %; capacidad ociosa en marzo/mayo; atrasos con inventario antes. Todo por b<h y HE < 3 meses de mantención.")

# ═════════════════════════ 4. Nivel de servicio (escalera A → B → C) ═════════════════════════
s = nueva()
kicker(s, "Parte I · Modelos B, C y Sol. 5")
yb = titulo(s, "Nivel de servicio: elevarlo cuesta muy poco")
texto(s, M, yb + 0.25, CW, [[("B: ", {"b": True}), ("multa con binaria  B ≤ 0,01·d + M·y ;   ", {}),
                             ("C: ", {"b": True}), ("B = 0 ;   ", {}),
                             ("Sol. 5: ", {"b": True}), ("multa + B = 0 (≡ C)", {})]], tam=16, color=INK6)
wlab, gap = 3.9, 1.25
x0 = M + wlab
wcol = (W - M - x0 - 2 * gap) / 3
cols = [
    ("A", "", "300,75", 400, "400 u (3,2 %)", "—", "—"),
    ("B", "(multa)", "300,94", 125, "125 u (= 1 %)", "0 (nunca conviene pagar $3 MM)", "+193.750"),
    ("C / Sol. 5", "(cero pend.)", "301,10", 0, "0", "0", "+350.000 (0,12 %)"),
]
y0 = yb + 1.35
# alto de cada fila (igual en las tres columnas)
pad = 0.55
wi = wcol - 2 * pad
filas_h = [pt2cm(24 * LH) + pt2cm(15 * LH) + 0.1, pt2cm(44 * LH * 0.9), 0.62,
           max(alto([_par(c[5])], wi, 15) for c in cols), pt2cm(15 * LH)]
gaps = 0.42
hblk = 2 * pad + sum(filas_h) + gaps * (len(filas_h) - 1)
ys = [y0 + pad]
for hf in filas_h[:-1]:
    ys.append(ys[-1] + hf + gaps)
etiquetas = [None, "COSTO TOTAL", "PENDIENTES MÁX.", "MULTAS", "COSTO VS A"]
for lab, yr, hf in zip(etiquetas, ys, filas_h):
    if lab:
        texto(s, M, yr + (0.2 if lab != "COSTO TOTAL" else 0.62), wlab - 0.3, [[(lab, {"spc": 100})]],
              tam=10, color=INK5, negrita=True)
for k, (cod, desc, costo, pend, pend_t, multa, vs) in enumerate(cols):
    x = x0 + k * (wcol + gap)
    rec = k == 2
    fondo, ct, c2 = (ACC, BLANCO, BLANCO) if rec else (PAPEL, INK, INK6)
    rect(s, x, y0, wcol, hblk, fondo, nombre=f"Columna {cod}")
    texto(s, x + pad, ys[0], wi, [[(cod, {"b": True, "tam": 24})], [(desc or " ", {})]], tam=15, color=ct)
    texto(s, x + pad, ys[1], wi, [[(costo, {"b": True}), (" MM$", {"tam": 18, "color": c2, "b": False})]],
          tam=44, color=ct, interl=0.9)
    lb = 2.6 * pend / 400  # barra de pendientes (escala común: 400 u = 2,6 cm)
    if lb:
        rect(s, x + pad, ys[2] + 0.13, lb, 0.36, SERIE["A"])
    texto(s, x + pad + (lb + 0.3 if lb else 0), ys[2], wi - lb - 0.3, pend_t, tam=15, color=ct,
          negrita=rec)
    texto(s, x + pad, ys[3], wi, multa, tam=15, color=ct)
    texto(s, x + pad, ys[4], wi, vs, tam=15, color=ct, negrita=rec)
    if k < 2:
        cx = x + wcol + gap / 2
        forma(s, MSO_SHAPE.CHEVRON, cx - 0.32, y0 + hblk / 2 - 0.5, 0.64, 1.0, INK2)
texto(s, M, y0 + hblk + 0.6, CW, vinetas([
    [("M(t) = demanda acumulada − I", {}), ("0", {"sub": True}),
     (" − 1 %·d(t): cota válida (peor caso: no producir); existen cotas más ajustadas, el óptimo no cambia", {})],
    ("Misma dotación (18) y HE (13.000 u): ", "se compra servicio con 800 u-mes de inventario anticipado"),
    ("Con B = 0 la cláusula nunca se activa: ", "Sol. 5 coincide con C")], tam=16, esp=6))
pie(s, 4)
nota(s, "45 s. Explicar y=1 forzado si B>1 %; si no, el costo hace y=0. M demasiado chico corta soluciones; muy grande debilita la relajación.")

# ═════════════════════════ 5. Recomendación agregada (panel dividido) ═════════════════════════
s = nueva()
wp = 12.3
rect(s, 0, 0, wp, H, NAVY, nombre="Panel recomendación")
wt = wp - M - 0.9
kicker(s, "Parte I · Recomendación", oscuro=True)
yb = titulo(s, "Recomendación de planificación agregada", oscuro=True, w=wt, tam=26)
yy = yb + 0.75
texto(s, M, yy, wt, [[("PLAN SOL. 5 · COSTO TOTAL", {"spc": 100})]], tam=11, color=SKY, negrita=True)
tn = tam_que_cabe(lambda t: [("301,1", {"b": True, "tam": t}), (" MM$", {"tam": 32})], wt, 96, 72)
_, hn = texto(s, M - 0.1, yy + 0.35, wt + 0.1, [[("301,1", {"b": True}), (" MM$", {"tam": 32, "color": SKY})]],
              tam=tn, color=BLANCO, interl=0.85)
yy += 0.35 + hn + 0.3
_, hk = texto(s, M, yy, wt, [[("−13,9 MM$", {"b": True, "tam": 32, "color": BLANCO})],
                             [("(−4,4 %) vs P2 y servicio completo", {})]], tam=16, color=ON2)
yy += hk + 0.75
chip(s, M, yy, "!  Riesgo", ALERTA)
texto(s, M, yy + 1.15, wt, [{"runs": [("HE al 100 % en nov–dic (93 % ene–feb)", {"b": True})], "esp": 6}] +
      vinetas(["  Seguro parcial: 19 trabajadores (+1,4 MM$, +0,46 %)", "  Sin despidos (20): +5,4 MM$"],
              tam=16, color=ON2, esp=4, vcol=SKY), tam=16, color=BLANCO)
# derecha: ficha del plan en chips + figura 1:1 + estabilidad
xr = wp + (W - wp - 19.5) / 2
texto(s, xr, Y_KICK, 19.5, [[("PLAN SOL. 5", {"spc": 100})]], tam=11, color=INK5, negrita=True)
xx = xr
for t in ("18 trabajadores", "regular ~9.000 u/mes", "HE sep–feb", "cero pendientes"):
    wpill = ancho(t, 16) + 0.9
    sp = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, xx, Y_TIT, wpill, 0.95, MIST, radio=0.5)
    con_texto(sp, t, tam=16, color=INK, mar=(0.05, 0.05, 0, 0))
    xx += wpill + 0.3
fy = Y_TIT + 0.95 + 0.6
figura(s, "slide_fig2_costos.png", xr, fy, 19.5, 11.0, "Figura costos por plan")
texto(s, xr, fy + 11.0 + 0.45, 19.5, [[("Estable en dotación y producción regular: ", {"b": True, "color": INK}),
                                       ("un solo ajuste de personal (−2); P2 ninguno, pero con menos de la mitad "
                                        "de la HE", {})]], tam=16, color=INK6)
pie(s, 5, oscuro=True, num_color=INK5)
nota(s, "30 s. No elegimos solo por costo: estabilidad, servicio y holgura de HE.")

# ═════════════════════════ 6. Componentes y EOQ (flujo + tabla + KPI) ═════════════════════════
s = nueva()
kicker(s, "Parte II–III · Componentes e inventarios")
yb = titulo(s, "De la producción a los componentes y EOQ individuales")
# flujo: 10.000 u/mes × mezcla × BOM → tasas constantes
pasos = [("10.000 u/mes", NAVY, BLANCO), ("× mezcla 50-30-20", NAVY6, BLANCO), ("× BOM", ACC, BLANCO),
         ("→ tasas de consumo constantes (no lotes)", MIST, INK)]
hf_, sep, dent = 1.45, 0.12, 0.6
anchos_f = [ancho(t, 15, True) + 2 * dent + 2.4 for t, _, _ in pasos[:-1]]
anchos_f.append(CW - sum(anchos_f) - 3 * sep)
xx, yfl = M, yb + 0.5
for k, ((t, fondo, ct), wf_) in enumerate(zip(pasos, anchos_f)):
    tipo = MSO_SHAPE.PENTAGON if k == 0 else MSO_SHAPE.CHEVRON
    sp = forma(s, tipo, xx, yfl, wf_, hf_, fondo)
    sp.adjustments[0] = dent / hf_
    con_texto(sp, t, tam=15, color=ct, negrita=True, mar=(dent + (0.25 if k == 0 else 0.45), dent, 0, 0))
    xx += wf_ + sep - (dent if k else 0) * 0 + 0
filas = [["Componente", "D anual", "h=0,25c", "Q*", "ROP = d·L", "Espacio", "Capital"],
         ["Motor estándar", "96.000", "3.000", "3.394", "2.400", "13,6 m³", "40,7 MM$"],
         ["Motor premium", "24.000", "5.000", "1.453", "1.000", "7,3 m³", "29,1 MM$"],
         ["Hélice–rejilla", "120.000", "1.125", "5.657", "4.000", "84,9 m³", "25,5 MM$"],
         ["Módulo electrónico", "60.000", "2.000", "3.464", "2.500", "5,2 m³", "27,7 MM$"],
         ["Control remoto", "24.000", "1.375", "2.211", "1.200", "2,2 m³", "12,2 MM$"],
         ["Total", "", "", "", "", "113,1 > 90", "135,1 > 110"]]
anchos_t = [4.9, 2.7, 2.6, 2.1, 2.9, 3.0, 3.3]
yt = yfl + hf_ + 0.65
_, ht = tabla(s, M, yt, anchos_t, filas, alto_f=0.95, alto_enc=0.95, total=True, nombre="Tabla EOQ individual")
# KPI de infactibilidad
xk = M + sum(anchos_t) + 0.8
wk = W - M - xk
hk = (ht - 0.4) / 2
for k, (lab, num, lim) in enumerate((("ESPACIO (m³)", "113,1", " > 90"), ("CAPITAL (MM$)", "135,1", " > 110"))):
    yk = yt + k * (hk + 0.4)
    rect(s, xk, yk, wk, hk, PAPEL, nombre=f"KPI {lab}")
    texto(s, xk + 0.55, yk + 0.55, wk, [[(lab, {"spc": 100})]], tam=10, color=INK5, negrita=True)
    chip(s, xk + wk - 0.45, yk + 0.38, "Infactible", ALERTA, icono="x", alin="r")
    texto(s, xk + 0.55, yk + hk - 0.45 - pt2cm(44 * LH * 0.9), wk - 1.1,
          [[(num, {"b": True}), (lim, {"tam": 26, "color": INK6})]], tam=44, interl=0.9)
texto(s, M, yt + ht + 0.75, CW, vinetas([
    ("Q* dice cuánto, ROP dice cuándo; ", "L < T en todos → un pedido en tránsito como máximo"),
    ("Infactible en ambos recursos: ", "cada EOQ ignora que compite por bodega y capital")], tam=18, esp=8))
pie(s, 6)
nota(s, "35 s. Supuestos EOQ ← tasa estable de la Parte II. Costo relevante individual 33,78 MM$/año.")

# ═════════════════════════ 7. EOQ multiproducto (tabla + 74× + figura en panel) ═════════════════════════
s = nueva()
xp = 17.6  # panel mist a la derecha con la figura como tarjeta blanca
rect(s, xp, 0, W - xp, H, MIST, nombre="Panel figura")
wl = xp - M - 0.9
kicker(s, "Parte III · Inventarios")
yb = titulo(s, "EOQ multiproducto: ambas restricciones activas, distinto valor", w=wl, tam=26)
# fórmula
form = [[("min ", {"b": True}), ("Σ DS/Q + hQ/2   ", {}), ("s.a. ", {"b": True}),
         ("Σ vQ ≤ 90 (μ),  Σ cQ ≤ 110 MM (λ)", {})],
        [("→  Q = √(2DS / (h + 2μv + 2λc))", {})]]
hfm = alto([_par(p) for p in form], wl - 1.0, 16, esp=2)
yf = yb + 0.55
rect(s, M, yf, wl, hfm + 0.7, MIST, nombre="Fórmula")
texto(s, M + 0.5, yf + 0.35, wl - 1.0, form, tam=16, esp=2)
# tabla de escenarios (transpuesta para caber a 14 pt), chip de color en cada encabezado
esc = list(ESCENARIO)
filas = [["", "Base", "+10 %\nespacio", "+10 %\npresupuesto"],
         ["Espacio", "90,0", "92,1 de 99", "90,0"],
         ["Capital", "110,0", "110,0", "121,0"],
         ["Activas", "ambas", "solo capital", "ambas"],
         ["Costo relevante", "34.503.017", "34.497.798", "34.116.426"],
         ["Ahorro", "—", "5.219", "386.591"]]
anchos_t = [3.9, 3.05, 3.35, 3.55]
anchos_t[0] = wl - sum(anchos_t[1:])
yt = yf + hfm + 0.7 + 0.5
gf, ht = tabla(s, M, yt, anchos_t, [[c.split("\n")[0] if "\n" not in c else c for c in f] for f in filas],
               alto_f=0.78, alto_enc=1.45, resaltar_col=1, enc_relleno=None, enc_color=INK, tam_enc=14,
               enc_regla=(1.5, INK), nombre="Tabla escenarios multiproducto")
# encabezados en dos líneas (párrafos) + chip de color por escenario
for j in range(1, 4):
    c = gf.table.cell(0, j)
    tf = c.text_frame
    for p in list(tf.paragraphs):
        p._p.getparent().remove(p._p)
    partes = filas[0][j].split("\n")
    for k, parte in enumerate(partes):
        p = tf.add_paragraph()
        p.alignment = PP_ALIGN.RIGHT
        r = p.add_run()
        r.text = parte
        _fmt(r, 14, INK, True)
    xc = M + sum(anchos_t[:j]) + anchos_t[j] - 0.25 - ancho(max(partes, key=lambda z: ancho(z, 14, True)), 14, True)
    rect(s, xc - 0.65, yt + 1.45 - 0.2 - pt2cm(14 * LH) * len(partes) + 0.14, 0.42, 0.42, ESCENARIO[esc[j - 1]])
# 74× sobre el panel, figura como tarjeta blanca 1:1
xf = xp + (W - xp - 14.5) / 2
texto(s, xf, 1.15, 14.5, [[("74×", {"b": True, "color": ACC})]], tam=72, interl=0.85)
texto(s, xf + ancho("74×", 72, True) + 0.5, 1.75, 14.5 - ancho("74×", 72, True) - 0.5,
      [[("Más presupuesto vale 74× más que más bodega", {"b": True, "color": INK})]], tam=18)
fy = H - 1.6 - 11.0 - 0.35
rect(s, xf - 0.35, fy - 0.35, 14.5 + 0.7, 11.0 + 0.7, BLANCO, nombre="Marco figura")
figura(s, "slide_fig3_lotes.png", xf, fy, 14.5, 11.0, "Figura lotes por escenario")
texto(s, xf, fy - 0.35 - 0.75, 14.5, [[("TAMAÑO DE LOTE (u) POR COMPONENTE Y ESCENARIO", {"spc": 100})]],
      tam=10, color=INK6, negrita=True)
texto(s, M, yt + ht + 0.6, wl, vinetas([
    "Lotes −18 % a −21 %; 94 → 116 pedidos/año; +0,72 MM$/año",
    "Costo de compra (2.784 MM$) no depende de Q",
    ("Activa ≠ valiosa: ", "al ampliar bodega el capital limita casi de inmediato")], tam=16, esp=6))
pie(s, 7, num_color=INK6)
nota(s, "40 s. μ = 5.098 $/m³-año y λ = 0,0595 $/$-año son valores marginales locales; al relajar cambian.")

# ═════════════════════════ 8. Recomendación integrada (navy, 4 tiles) ═════════════════════════
s = nueva(NAVY)
helice(s, W - 2.2, 1.3, 4.6, NAVY7, NAVY6)
kicker(s, "Integración · Partes I–III", oscuro=True)
yb = titulo(s, "Recomendación integrada para Ventisur", oscuro=True, w=CW - 6)
tiles = [
    ("Producción", "301,1 MM$", None,
     [("Plan Sol. 5 (18 trabajadores, HE en el peak, cero pendientes)", "l0"),
      ("Servicio completo cuesta 0,35 MM$ ≪ una sola multa (3 MM$)", "l1")]),
    ("Coherencia", "10.000 u/mes", None,
     [("Comprar con la tasa estable de 10.000 u/mes exige holgura de componentes en oct–feb", "l0")]),
    ("Compras", None, ["2.781", "1.192", "4.456", "2.844", "1.815"],
     [("Usar los lotes multiproducto (2.781 / 1.192 / 4.456 / 2.844 / 1.815) con ROP = d·L", "l0")]),
    ("Inversión", "+386 mil $/año", None,
     [("Priorizar presupuesto (+386 mil $/año) sobre bodega (+5 mil $/año)", "l0"),
      ("Ahorro medio 3,5 % anual sobre los 11 MM$ (marginal 5,95 % → 1,35 %); h ya incluye el costo de "
       "capital: ampliar si el tope es de caja y puede levantarse sin otros costos", "l1")]),
]
wtile, gt, pad = (CW - 0.6) / 2, 0.6, 0.6
wi = wtile - 2 * pad


def _cuerpo(items):
    return [{"runs": [(t, {"color": BLANCO if n == "l0" else ON2})], "vineta": n == "l1", "nivel": 0,
             "vcol": SKY, "esp": 4} for t, n in items]


def _alto_tile(t):
    h = 1.15 + 0.35  # encabezado (círculo + título) + aire
    if t[2]:
        h += 1.0 + 0.35  # fila de lotes
    return 2 * pad + h + alto(_cuerpo(t[3]), wi, 15, esp=4)


filas_y = [yb + 0.7]
alto_fila = [max(_alto_tile(tiles[0]), _alto_tile(tiles[1])), max(_alto_tile(tiles[2]), _alto_tile(tiles[3]))]
filas_y.append(filas_y[0] + alto_fila[0] + gt)
for k, (tit, clave, lotes, items) in enumerate(tiles):
    fi, co = divmod(k, 2)
    x, y = M + co * (wtile + gt), filas_y[fi]
    rect(s, x, y, wtile, alto_fila[fi], NAVY7, nombre=f"Recomendación {k + 1}")
    circ = forma(s, MSO_SHAPE.OVAL, x + pad, y + pad, 1.15, 1.15, None, SKY, 2)
    con_texto(circ, str(k + 1), tam=18, color=SKY, negrita=True, mar=(0, 0, 0, 0))
    texto(s, x + pad + 1.55, y + pad, 7, tit, h=1.15, tam=22, color=BLANCO, negrita=True, ancla="m")
    if clave:
        texto(s, x + wtile - pad - 7.5, y + pad, 7.5, [[(clave, {"b": True})]], h=1.15, tam=28, color=SKY,
              alin="r", ancla="m")
    yy = y + pad + 1.15 + 0.35
    if lotes:
        xx = x + pad
        for v in lotes:
            wl_ = ancho(v, 18, True) + 0.8
            sp = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, xx, yy, wl_, 1.0, NAVY, radio=0.5)
            con_texto(sp, [[(v, {"b": True})]], tam=18, color=SKY, mar=(0, 0, 0, 0))
            xx += wl_ + 0.25
        texto(s, xx + 0.15, yy, x + wtile - pad - xx, "u/pedido", h=1.0, tam=15, color=ON2, ancla="m")
        yy += 1.0 + 0.35
    texto(s, x + pad, yy, wi, _cuerpo(items), tam=15, esp=4)
texto(s, M, filas_y[1] + alto_fila[1] + 0.45, CW,
      [[("Supuestos: ", {"b": True}),
        ("demanda y plazos determinísticos, unidad agregada, lotes completos simultáneos", {})]], tam=14, color=ON3)
pie(s, 8, oscuro=True)
nota(s, "30 s. Cerrar conectando las tres partes y abrir a preguntas.")

prs.core_properties.title = "Proyecto Integrador Ventisur"
prs.core_properties.subject = "Gestión de Operaciones · UAI · defensa de 5 minutos"
prs.save(AQUI / "Presentacion_Ventisur.pptx")
print("OK", AQUI / "Presentacion_Ventisur.pptx")
