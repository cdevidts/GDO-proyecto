"""PDF de estudio para la defensa, ordenado por las solicitudes del enunciado.

Cada solicitud sigue la misma secuencia: lo que pide el enunciado -> respuesta punto por punto ->
cómo lo hicimos (con un ejemplo a mano) -> resultados -> por qué -> si te preguntan -> cuidado.
Las tablas se leen de proyecto/02_resultados (no hay cifras de planes copiadas a mano).

Uso:  cd proyecto/04_presentacion && python3 construir_pdf_defensa.py
Salida: Defensa_Ventisur_estudio.pdf (y el HTML intermedio Defensa_Ventisur_estudio.html)
"""
import json
import re
import subprocess
from pathlib import Path

import pandas as pd

from construir_guia_defensa import img, miles, svg_eoq, svg_valor

AQUI = Path(__file__).resolve().parent
RES = AQUI.parent / "02_resultados"
CSV = RES / "csv"
MESES = ["Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb"]


# ------------------------------------------------------------------ utilidades
def n(x, dec=0):
    return miles(float(x), dec)


def mm(x, dec=2):
    return miles(float(x) / 1e6, dec)


def pct(x, dec=1):
    return miles(100 * float(x), dec) + " %"


def tabla(cab, filas, num=(), clase="", cap="", tot=(), rec=()):
    """cab: encabezados; num: índices de columnas numéricas; tot/rec: índices de filas destacadas."""
    h = "".join(f'<th class="{"n" if i in num else ""}">{c}</th>' for i, c in enumerate(cab))
    cuerpo = []
    for k, f in enumerate(filas):
        cl = "tot" if k in tot else ("rec" if k in rec else "")
        celdas = "".join(f'<td class="{"n" if i in num else ""}">{c}</td>' for i, c in enumerate(f))
        cuerpo.append(f'<tr class="{cl}">{celdas}</tr>')
    cap_html = f"<caption>{cap}</caption>" if cap else ""
    return f'<table class="{clase}">{cap_html}<thead><tr>{h}</tr></thead><tbody>{"".join(cuerpo)}</tbody></table>'


def punto_por_punto(filas):
    """filas: (lo que piden, respuesta, dónde verlo)"""
    tr = "".join(
        f'<tr><td class="pp-q"><span class="ck">✓</span>{a}</td><td>{b}</td><td class="pp-v">{c}</td></tr>'
        for a, b, c in filas)
    return ('<table class="pp"><thead><tr><th>Lo que nos piden</th><th>Lo que hicimos → la respuesta</th>'
            f'<th>Ver</th></tr></thead><tbody>{tr}</tbody></table>')


def qa(pares):
    return '<div class="qa-grid">' + "".join(
        f'<div class="qa"><p class="q">{q}</p><p class="a">{a}</p></div>' for q, a in pares) + "</div>"


def lbl(i, txt):
    return f'<div class="lbl"><span class="i">{i}</span>{txt}</div>'


def pide(html):
    return f'<div class="pide"><div class="pide-t">Lo que pide el enunciado</div>{html}</div>'


def cabecera(num, titulo, parte, dim, donde):
    return f'''<div class="head"><div class="num">{num}</div><div>
  <div class="kicker">{parte} · {dim}</div>
  <h2>{titulo}</h2>
  <div class="meta">{donde}</div></div></div>'''


def ref(informe, excel, codigo, diap):
    partes = [f"<b>Informe:</b> {informe}", f"<b>Excel:</b> {excel}", f"<b>Código:</b> {codigo}"]
    if diap:
        partes.append(f"<b>Diapositiva:</b> {diap}")
    return " · ".join(partes)


# ------------------------------------------------------------------ datos
P = {k: pd.read_csv(CSV / f"{f}.csv") for k, f in
     [("P1", "sol1_politica_1"), ("P2", "sol1_politica_2"), ("P3", "sol1_politica_3"),
      ("A", "modelo_a"), ("B", "modelo_b"), ("C", "modelo_c")]}
EOQ = pd.read_csv(CSV / "sol7_eoq_individual.csv")
LOT = pd.read_csv(CSV / "sol9_10_multiproducto_lotes.csv")
MUL = pd.read_csv(CSV / "sol9_10_multiproducto_resumen.csv").set_index("Escenario")
SEN = pd.read_csv(CSV / "sensibilidad_parte1.csv")
REQ = pd.read_csv(CSV / "sol6_requerimientos.csv")
PRO = pd.read_csv(CSV / "sol6_produccion_por_modelo.csv")
RJ = json.loads((RES / "resumen.json").read_text())
NOMBRES = ["Motor estándar", "Motor premium", "Hélice–rejilla", "Módulo electrónico", "Control remoto"]
V = [0.004, 0.005, 0.015, 0.0015, 0.001]
COMP_COL = ["#1f5fae", "#6d4bb3", "#2e7d4f", "#b45309", "#8c3b2f"]


def costo(df, col):
    return float(df[col].sum())


def fila_mes(df, col, fmt=lambda v: n(v)):
    return [fmt(v) for v in df[col]]


# ------------------------------------------------------------------ diagramas nuevos
def svg_dientes():
    """Inventario del motor estándar en el tiempo: cuánto (Q*) y cuándo (ROP) pedir."""
    Q, d, L, ROP = 3394.1, 400.0, 6, 2400
    Tc = Q / d
    x0, x1, y0, y1, tmax = 70, 640, 200, 30, 3 * Tc + 1.5

    def X(t):
        return x0 + t / tmax * (x1 - x0)

    def Y(q):
        return y0 - q / 3800 * (y0 - y1)

    s = ['<svg viewBox="0 0 760 270" role="img" aria-label="Inventario del motor estándar en el tiempo: baja 400 unidades por día; cuando llega a 2.400 se pide; el pedido llega 6 días después justo cuando el inventario llega a cero">']
    for q in (0, 1000, 2000, 3000):
        s.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(q):.1f}" y2="{Y(q):.1f}" class="grid"/>')
        s.append(f'<text x="{x0 - 6}" y="{Y(q) + 4:.1f}" text-anchor="end" class="t-s">{n(q)}</text>')
    pts = []
    for k in range(3):
        pts += [f"{X(k * Tc):.1f},{Y(Q):.1f}", f"{X((k + 1) * Tc):.1f},{Y(0):.1f}"]
    pts.append(f"{X(3 * Tc):.1f},{Y(Q):.1f}")
    pts.append(f"{X(tmax):.1f},{Y(Q - d * (tmax - 3 * Tc)):.1f}")
    s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="var(--p3)" stroke-width="2.4"/>')
    s.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(ROP):.1f}" y2="{Y(ROP):.1f}" stroke="var(--warn)" stroke-dasharray="6 4" stroke-width="1.4"/>')
    s.append(f'<text x="{x1 + 6}" y="{Y(ROP) - 4:.1f}" class="t-s t-b" style="fill:var(--warn)">ROP = d·L</text>')
    s.append(f'<text x="{x1 + 6}" y="{Y(ROP) + 10:.1f}" class="t-s t-b" style="fill:var(--warn)">= 400 × 6 = 2.400</text>')
    for k in range(3):
        te = k * Tc + (Q - ROP) / d
        s.append(f'<circle cx="{X(te):.1f}" cy="{Y(ROP):.1f}" r="4.5" fill="var(--warn)"/>')
        s.append(f'<line x1="{X(te):.1f}" x2="{X(te + L):.1f}" y1="{y0 + 16}" y2="{y0 + 16}" stroke="var(--warn)" stroke-width="1.6"/>')
        s.append(f'<line x1="{X(te):.1f}" x2="{X(te):.1f}" y1="{y0 + 11}" y2="{y0 + 21}" stroke="var(--warn)"/>')
        s.append(f'<line x1="{X(te + L):.1f}" x2="{X(te + L):.1f}" y1="{y0 + 11}" y2="{y0 + 21}" stroke="var(--warn)"/>')
    te = (Q - ROP) / d
    s.append(f'<text x="{X(te):.1f}" y="{y0 + 32}" class="t-s">● se emite el pedido → viaja L = 6 días → llega</text>')
    s.append(f'<line x1="{X(Tc) + 6:.1f}" x2="{X(Tc) + 6:.1f}" y1="{Y(0):.1f}" y2="{Y(Q):.1f}" stroke="var(--p3)" stroke-width="1" stroke-dasharray="2 2"/>')
    s.append(f'<text x="{X(Tc) + 10:.1f}" y="{Y(Q * 0.2):.1f}" class="t-s t-b" style="fill:var(--p3)">llega Q* = 3.394</text>')
    s.append(f'<line x1="{X(Tc):.1f}" x2="{X(2 * Tc):.1f}" y1="{Y(Q) - 10:.1f}" y2="{Y(Q) - 10:.1f}" stroke="currentColor"/>')
    s.append(f'<text x="{X(1.5 * Tc):.1f}" y="{Y(Q) - 15:.1f}" text-anchor="middle" class="t-s">T = Q*/d = 8,5 días entre pedidos</text>')
    s.append(f'<text x="{x0 + 4}" y="{y1 - 12}" class="t-s">unidades en bodega</text>')
    s.append(f'<text x="{x1}" y="{y0 + 50}" text-anchor="end" class="t-s">días operativos →</text>')
    s.append("</svg>")
    return "\n".join(s)


def svg_recursos():
    """Uso de espacio y capital de los EOQ individuales frente a los límites."""
    esp = list(EOQ.Espacio)
    cap = list(EOQ.Capital / 1e6)
    x0, ancho = 120, 470
    s = ['<svg viewBox="0 0 760 200" role="img" aria-label="Los EOQ individuales usan 113,1 metros cúbicos de 90 disponibles y 135,1 millones de 110 disponibles; la hélice ocupa casi toda la bodega">']
    for fila, (nom, vals, lim, uni) in enumerate([("Espacio", esp, 90, "m³"), ("Capital", cap, 110, "MM$")]):
        y = 30 + fila * 78
        s.append(f'<text x="{x0 - 10}" y="{y + 20}" text-anchor="end" class="t-m t-b">{nom}</text>')
        x = x0
        for k, v in enumerate(vals):
            w = v / lim * ancho
            s.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="30" fill="{COMP_COL[k]}" stroke="#fff" stroke-width="1"/>')
            if w > 34:
                s.append(f'<text x="{x + w / 2:.1f}" y="{y + 19}" text-anchor="middle" class="t-s" style="fill:#fff;font-weight:600">{n(v, 1)}</text>')
            x += w
        tot = sum(vals)
        s.append(f'<text x="{x + 6:.1f}" y="{y + 14}" class="t-s t-b">{n(tot, 1)} {uni}</text>')
        s.append(f'<text x="{x + 6:.1f}" y="{y + 27}" class="t-s" style="fill:var(--bad)">+{n(100 * (tot / lim - 1), 1)} % sobre el límite</text>')
        s.append(f'<line x1="{x0 + ancho}" x2="{x0 + ancho}" y1="{y - 8}" y2="{y + 38}" stroke="var(--bad)" stroke-width="2" stroke-dasharray="4 3"/>')
        s.append(f'<text x="{x0 + ancho}" y="{y - 12}" text-anchor="middle" class="t-s" style="fill:var(--bad)">límite {n(lim)} {uni}</text>')
    lx = x0
    for k, nom in enumerate(NOMBRES):
        s.append(f'<rect x="{lx}" y="182" width="10" height="10" fill="{COMP_COL[k]}"/>')
        s.append(f'<text x="{lx + 14}" y="191" class="t-s">{nom}</text>')
        lx += 14 + len(nom) * 6.2 + 18
    s.append("</svg>")
    return "\n".join(s)


SVG_MAPA = """<svg viewBox="0 0 940 150" role="img" aria-label="Parte I decide producción y dotación; la Gerencia fija 10.000 unidades al mes; Parte II convierte eso en consumo de componentes; Parte III decide cuánto y cuándo comprar">
<defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<rect x="10" y="10" width="270" height="96" rx="10" fill="var(--p1s)" stroke="var(--p1)" stroke-width="2"/>
<text x="26" y="34" class="t-b" style="fill:var(--p1)">PARTE I · Planificación agregada</text>
<text x="26" y="56" class="t-m">¿Con cuánta gente y cuánto producir</text><text x="26" y="73" class="t-m">cada mes? · Solicitudes 1 a 5</text>
<text x="26" y="96" class="t-s">→ Sol. 5: 18 trabajadores, 301,10 MM$</text>
<rect x="335" y="10" width="270" height="96" rx="10" fill="var(--p2s)" stroke="var(--p2)" stroke-width="2"/>
<text x="351" y="34" class="t-b" style="fill:var(--p2)">PARTE II · Materiales</text>
<text x="351" y="56" class="t-m">¿Cuánto se consume de cada</text><text x="351" y="73" class="t-m">componente? · Solicitud 6</text>
<text x="351" y="96" class="t-s">→ 8.000 · 2.000 · 10.000 · 5.000 · 2.000 u/mes</text>
<rect x="660" y="10" width="270" height="96" rx="10" fill="var(--p3s)" stroke="var(--p3)" stroke-width="2"/>
<text x="676" y="34" class="t-b" style="fill:var(--p3)">PARTE III · Inventarios</text>
<text x="676" y="56" class="t-m">¿Cuánto y cuándo pedir cada</text><text x="676" y="73" class="t-m">componente? · Solicitudes 7 a 10</text>
<text x="676" y="96" class="t-s">→ lotes multiproducto, 34,50 MM$/año</text>
<line x1="282" y1="58" x2="331" y2="58" stroke="currentColor" stroke-width="1.6" marker-end="url(#fl)"/>
<line x1="607" y1="58" x2="656" y2="58" stroke="currentColor" stroke-width="1.6" marker-end="url(#fl)"/>
<text x="306" y="128" text-anchor="middle" class="t-s">la Gerencia fija</text><text x="306" y="142" text-anchor="middle" class="t-s t-b">10.000 u/mes</text>
<text x="631" y="128" text-anchor="middle" class="t-s">entrega la</text><text x="631" y="142" text-anchor="middle" class="t-s t-b">demanda anual Dᵢ</text>
</svg>"""

SVG_ESCALERA = """<svg viewBox="0 0 800 250" role="img" aria-label="Costo por unidad de cada forma de cubrir demanda: atrasar un mes 750, guardar un mes 1.000, guardar dos meses 2.000, horas extra 2.500, guardar tres meses 3.000, trabajador extra usado seis meses 3.800">
<g class="t-m"><text x="290" y="34" text-anchor="end">Atrasar 1 u un mes (b)</text><text x="290" y="68" text-anchor="end">Guardar 1 u un mes (h)</text>
<text x="290" y="102" text-anchor="end">Guardar 1 u dos meses</text><text x="290" y="136" text-anchor="end" class="t-b">Producir 1 u en horas extra</text>
<text x="290" y="170" text-anchor="end">Guardar 1 u tres meses</text><text x="290" y="204" text-anchor="end">Trabajador extra solo para sep–feb</text></g>
<rect x="300" y="20" width="90" height="20" rx="3" fill="var(--ok)"/><rect x="300" y="54" width="120" height="20" rx="3" fill="var(--ok)"/>
<rect x="300" y="88" width="240" height="20" rx="3" fill="var(--ok)"/><rect x="300" y="122" width="300" height="20" rx="3" fill="var(--accent)"/>
<rect x="300" y="156" width="360" height="20" rx="3" fill="var(--muted)"/><rect x="300" y="190" width="456" height="20" rx="3" fill="var(--muted)"/>
<g class="t-s t-b"><text x="396" y="35">$750</text><text x="426" y="69">$1.000</text><text x="546" y="103">$2.000</text>
<text x="606" y="137">$2.500</text><text x="666" y="171">$3.000</text><text x="756" y="227" text-anchor="end">≈ $3.800 por unidad (11,4 MM$ ÷ 3.000 u)</text></g>
<line x1="600" y1="14" x2="600" y2="214" stroke="var(--accent)" stroke-dasharray="4 4"/>
<text x="300" y="244" class="t-s">verde = más barato que la hora extra (el modelo lo usa) · gris = más caro (el modelo lo evita)</text>
</svg>"""

SVG_ABC = """<svg viewBox="0 0 780 206" role="img" aria-label="Costo de los pendientes en cada modelo: A crece en línea recta, B agrega un salto de 3 millones al pasar el 1 por ciento, C no permite pendientes">
<defs><marker id="ax" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<text x="20" y="20" class="t-b">A (Sol. 2) · costo lineal</text>
<line x1="30" y1="160" x2="230" y2="160" stroke="currentColor" marker-end="url(#ax)"/><line x1="30" y1="160" x2="30" y2="40" stroke="currentColor" marker-end="url(#ax)"/>
<line x1="30" y1="160" x2="220" y2="100" stroke="var(--s-a)" stroke-width="2.6"/>
<text x="130" y="196" text-anchor="middle" class="t-s">pendientes Bₜ</text><text x="44" y="62" class="t-s">$750 por u-mes, sin tope</text>
<text x="280" y="20" class="t-b">B (Sol. 3) · salto con binaria</text>
<line x1="290" y1="160" x2="490" y2="160" stroke="currentColor" marker-end="url(#ax)"/><line x1="290" y1="160" x2="290" y2="40" stroke="currentColor" marker-end="url(#ax)"/>
<line x1="290" y1="160" x2="350" y2="141" stroke="var(--s-p2)" stroke-width="2.6"/><line x1="350" y1="141" x2="350" y2="70" stroke="var(--s-p2)" stroke-width="1.4" stroke-dasharray="3 3"/>
<line x1="350" y1="70" x2="480" y2="29" stroke="var(--s-p2)" stroke-width="2.6"/>
<text x="350" y="176" text-anchor="middle" class="t-s">1 % de dₜ</text><text x="360" y="104" class="t-s">+$3 MM (yₜ = 1)</text>
<text x="390" y="196" text-anchor="middle" class="t-s">pendientes Bₜ</text>
<text x="540" y="20" class="t-b">C (Sol. 4) · prohibido</text>
<line x1="550" y1="160" x2="750" y2="160" stroke="currentColor" marker-end="url(#ax)"/><line x1="550" y1="160" x2="550" y2="40" stroke="currentColor" marker-end="url(#ax)"/>
<rect x="556" y="44" width="186" height="112" fill="var(--warn-s)" stroke="var(--warn)" stroke-dasharray="4 3"/>
<circle cx="550" cy="160" r="5" fill="var(--accent)"/><text x="650" y="104" text-anchor="middle" class="t-s t-b">Bₜ &gt; 0 no permitido</text>
<text x="650" y="196" text-anchor="middle" class="t-s">solo Bₜ = 0</text>
</svg>"""

SVG_BOM = """<svg viewBox="0 0 780 250" role="img" aria-label="Diez mil unidades al mes se reparten en 5.000 Estándar, 3.000 Plus y 2.000 Premium; con la lista de materiales dan 8.000 motores estándar, 2.000 motores premium, 10.000 hélices, 5.000 módulos y 2.000 controles al mes">
<g stroke-width="2" fill="none" opacity=".85">
<path d="M150,125 C210,125 230,55 290,55" stroke="var(--s-p1)"/><path d="M150,125 C210,125 230,125 290,125" stroke="var(--s-p2)"/><path d="M150,125 C210,125 230,195 290,195" stroke="var(--s-p3)"/>
<path d="M410,55 C480,55 500,30 560,30" stroke="var(--s-p1)"/><path d="M410,55 C480,55 500,120 560,120" stroke="var(--s-p1)"/>
<path d="M410,125 C480,125 500,30 560,30" stroke="var(--s-p2)"/><path d="M410,125 C480,125 500,120 560,120" stroke="var(--s-p2)"/><path d="M410,125 C480,125 500,165 560,165" stroke="var(--s-p2)"/>
<path d="M410,195 C480,195 500,75 560,75" stroke="var(--s-p3)"/><path d="M410,195 C480,195 500,120 560,120" stroke="var(--s-p3)"/><path d="M410,195 C480,195 500,165 560,165" stroke="var(--s-p3)"/><path d="M410,195 C480,195 500,210 560,210" stroke="var(--s-p3)"/>
</g>
<rect x="20" y="100" width="130" height="50" rx="8" fill="#fff" stroke="currentColor"/><text x="85" y="122" text-anchor="middle" class="t-b">10.000 u/mes</text><text x="85" y="139" text-anchor="middle" class="t-s">tasa de la Gerencia</text>
<rect x="290" y="35" width="120" height="40" rx="8" fill="#fff" stroke="var(--s-p1)"/><text x="350" y="60" text-anchor="middle" class="t-m">Estándar 5.000</text>
<rect x="290" y="105" width="120" height="40" rx="8" fill="#fff" stroke="var(--s-p2)"/><text x="350" y="130" text-anchor="middle" class="t-m">Plus 3.000</text>
<rect x="290" y="175" width="120" height="40" rx="8" fill="#fff" stroke="var(--s-p3)"/><text x="350" y="200" text-anchor="middle" class="t-m">Premium 2.000</text>
<g class="t-m"><text x="566" y="34">Motor estándar <tspan class="t-b">8.000</tspan></text><text x="566" y="79">Motor premium <tspan class="t-b">2.000</tspan></text>
<text x="566" y="124">Hélice–rejilla <tspan class="t-b">10.000</tspan></text><text x="566" y="169">Módulo electrónico <tspan class="t-b">5.000</tspan></text><text x="566" y="214">Control remoto <tspan class="t-b">2.000</tspan></text></g>
<text x="220" y="20" text-anchor="middle" class="t-s">× mezcla 50–30–20</text><text x="485" y="244" text-anchor="middle" class="t-s">× lista de materiales (1 componente por cada modelo que lo usa)</text>
</svg>"""


# ------------------------------------------------------------------ portada y páginas iniciales
def portada():
    dims = tabla(
        ["Dimensión de la rúbrica", "Peso", "Solicitudes del enunciado"],
        [["1. Políticas simples", "10 %", "S1"], ["2. Modelo A", "20 %", "S2"],
         ["3. Modelos B y C y recomendación", "15 %", "S3, S4, S5"],
         ["4. Desagregación y requerimientos", "10 %", "S6"], ["5. EOQ individuales y factibilidad", "15 %", "S7, S8"],
         ["6. EOQ multiproducto y sensibilidad", "20 %", "S9, S10"],
         ["7. Integración y dominio transversal", "10 %", "Todo + recomendación final"]],
        num=(1,), clase="compact")
    pasos = "".join(f'<li><span class="i" style="background:{c}">{i}</span><span><b>{t}</b> {d}</span></li>' for i, c, t, d in [
        (1, "#c48a1c", "Lo que pide el enunciado.", "El texto del enunciado, resumido sin cambiarle el sentido. Lo que va entre comillas es literal."),
        (2, "var(--ok)", "Respuesta punto por punto.", "Cada cosa que pide, con lo que hicimos y dónde está el resultado. Es la forma de comprobar que no falta nada."),
        (3, "var(--p1)", "Cómo lo hicimos.", "Pasos, fórmulas y un ejemplo calculado a mano para entender de dónde sale el número."),
        (4, "var(--p1)", "Resultados.", "Tablas y gráficos sacados directamente de los archivos del proyecto."),
        (5, "var(--p1)", "Por qué.", "La explicación que hay que saber decir con palabras propias. Es lo que más evalúan."),
        (6, "var(--p1)", "Si te preguntan.", "Preguntas probables del equipo docente con su respuesta corta."),
        (7, "var(--warn)", "Cuidado.", "El error típico que resta puntos en esa parte.")])
    cifras = "".join(f'<div class="cf"><b>{a}</b><span>{b}</span></div>' for a, b in [
        ("340,0 · 315,0 · 329,5", "MM$ de P1, P2 y P3 (S1)"), ("300,75 MM$", "Modelo A, con atrasos (S2)"),
        ("300,94 MM$", "Modelo B: diciembre queda en 125 u = 1 % (S3)"), ("301,10 MM$", "Modelo C = Sol. 5, el recomendado (S4, S5)"),
        ("18 trabajadores", "despide 2 en marzo; HE de sep a feb"), ("+350.000", "costo de pasar de A a servicio completo (0,12 %)"),
        ("8.000 · 2.000 · 10.000 · 5.000 · 2.000", "u/mes de cada componente (S6)"), ("113,1 m³ · 135,1 MM$", "lo que piden los EOQ juntos; límites 90 y 110 (S8)"),
        ("34,50 MM$/año", "EOQ multiproducto, +0,72 vs EOQ (S9)"), ("μ 5.098 · λ 0,0595", "las dos restricciones activas (S9)"),
        ("386.591 vs 5.219", "$/año: +10 % presupuesto vs +10 % bodega (S10)"), ("302,5 MM$", "seguro opcional con 19 trabajadores (S5)")])
    return f'''<section class="portada">
<div class="eyebrow">Gestión de Operaciones · Sección 2 · Universidad Adolfo Ibáñez</div>
<h1>Proyecto Ventisur<br><span>Guía de estudio para la defensa</span></h1>
<p class="sub">Qué nos pidieron, qué hicimos, qué obtuvimos y por qué. Solicitud por solicitud, en el orden del enunciado.</p>
<p class="autores">Cristóbal De Vidts · Constanza Catalán · Bellonce Bulnes · Matias Rojas Rodriguez</p>
<div class="dos">
<div class="box"><h3>Cómo está armada cada solicitud</h3><ol class="leyenda">{pasos}</ol>
<p class="muted small">Plan de estudio: (1) lee el mapa de la pág. 2 y las ideas de la pág. 4; (2) lee las solicitudes en orden; (3) repasa tapando las respuestas de "Si te preguntan"; (4) cierra con el anexo "¿Qué pasa si…?" y el guion.</p></div>
<div class="box"><h3>Cómo nos evalúan</h3>
<p>La nota sale de la <b>defensa oral</b>: 5 minutos de presentación y 10 de preguntas. El informe y los archivos solo respaldan. <b>Cualquiera puede ser preguntado por cualquier parte</b> y la nota puede ser distinta entre integrantes.</p>
<p>Las preguntas pueden ser: cambiar un parámetro, quitar o agregar una restricción, interpretar un resultado o explicar un supuesto. La rúbrica dice: <i>"La mera lectura de un resultado, fórmula o restricción no constituye evidencia suficiente de comprensión"</i>.</p>
{dims}
<p class="muted small">Nota = 10·s₁/4 + 20·s₂/4 + 15·s₃/4 + 10·s₄/4 + 15·s₅/4 + 20·s₆/4 + 10·s₇/4, con cada sᵢ entre 0 y 4.</p></div>
</div>
<div class="box" style="margin-top:12px"><h3>Las 12 cifras que hay que saber de memoria (todo lo demás se deduce)</h3>
<div class="cifras">{cifras}</div></div>
</section>'''


def mapa(pags):
    filas = [
        ("S1", "¿Cuánto cuesta planificar con una regla simple: guardar inventario, usar horas extra o contratar y despedir?", "Simular las 3 políticas mes a mes", "P2 (horas extra) es la más barata: 315,0 MM$. P1 340,0 · P3 329,5", "D1"),
        ("S2", "¿Cuál es el plan más barato si se pueden combinar todas las herramientas?", "Modelo A: programación lineal entera", "300,75 MM$: 18 trabajadores, HE en sep–feb y 600 u-mes de atraso en dic–ene", "D2"),
        ("S3", "¿Cómo cambia el plan con una multa de $3 MM si los atrasos superan el 1 %?", "Modelo B: A + variable binaria con constante M", "300,94 MM$: no paga ninguna multa; deja diciembre en 125 u (justo 1 %)", "D3"),
        ("S4", "¿Y si no se acepta ningún pedido pendiente?", "Modelo C: A + Bₜ = 0", "301,10 MM$: el servicio completo cuesta 350.000 más que A", "D3"),
        ("S5", "¿Qué plan le recomendamos a la Gerencia?", "B + Bₜ = 0 y comparación de todo", "Sol. 5 (= C): 18 trabajadores, cero pendientes, 301,10 MM$; seguro opcional: 19", "D3"),
        ("S6", "¿Cuántos componentes consume la producción?", "Mezcla 50–30–20 × lista de materiales", "8.000 · 2.000 · 10.000 · 5.000 · 2.000 u/mes (tasas, no pedidos)", "D4"),
        ("S7", "¿Cuánto y cuándo pedir cada componente, mirado por separado?", "EOQ y punto de reorden", "Q* = 3.394 · 1.453 · 5.657 · 3.464 · 2.211; ROP = d·L", "D5"),
        ("S8", "¿Se pueden aplicar todos esos EOQ al mismo tiempo?", "Sumar espacio y capital de los lotes", "No: piden 113,1 m³ (máx. 90) y 135,1 MM$ (máx. 110)", "D5"),
        ("S9", "¿Cuáles son los mejores lotes que sí caben?", "EOQ multiproducto (Lagrange / KKT)", "Lotes 18–21 % menores; 34,50 MM$/año (+2,1 %); ambas restricciones activas", "D6"),
        ("S10", "¿Conviene más ampliar la bodega o el presupuesto?", "Resolver de nuevo con +10 % de cada uno", "El presupuesto: ahorra 386.591 $/año contra 5.219 (74 veces más)", "D6"),
        ("Final", "¿Qué debe hacer Ventisur?", "Síntesis de las tres partes", "Sol. 5 + lotes multiproducto + ROP del peak + ampliar el presupuesto", "D7"),
    ]
    tr = "".join(
        f'<tr><td class="sid">{s}</td><td>{q}</td><td>{h}</td><td><b>{r}</b></td><td class="c">{d}</td><td class="c">{pags.get(s, "")}</td></tr>'
        for s, q, h, r, d in filas)
    return f'''<section class="salto">
<div class="eyebrow">Página para memorizar</div>
<h2 class="pt">El proyecto en una página: cada solicitud responde una pregunta de la Gerencia</h2>
<figure class="mapa">{SVG_MAPA}</figure>
<table class="mapa-t"><thead><tr><th>Sol.</th><th>La pregunta de la Gerencia (en simple)</th><th>Cómo la respondimos</th><th>La respuesta</th><th>Rúbrica</th><th>Pág.</th></tr></thead><tbody>{tr}</tbody></table>
<div class="why" style="margin-top:8px"><b>El hilo que conecta todo:</b> la Parte I decide <b>cuánto producir y con cuánta gente</b>; la Gerencia fija para compras una tasa estable de 10.000 u/mes; la Parte II la convierte en <b>consumo de cada componente</b>; la Parte III decide <b>cuánto y cuándo comprar</b> ese consumo con los recursos que hay. Cada modelo responde una decisión distinta: hay que saber decir cuál.</div>
</section>'''


def datos():
    dem = [9500, 9000, 8500, 8500, 9000, 9500, 10000, 10000, 11500, 12500, 11500, 10500]
    t_dem = tabla(["Mes"] + MESES + ["Total"], [["Demanda (u)"] + [n(x) for x in dem] + ["120.000"]],
                  num=tuple(range(1, 14)), clase="compact")
    p1 = tabla(["Parámetro (Parte I)", "Valor"], [
        ["Dotación inicial", "20 trabajadores"], ["Producción regular", "500 u/trabajador-mes"],
        ["Producción en HE (máx.)", "150 u/trabajador-mes"], ["Costo laboral", "$1.200.000/trabajador-mes"],
        ["Contratar / despedir", "$2.500.000 / $3.000.000 por trabajador"], ["Costo de HE", "$2.500/u"],
        ["Mantener inventario (h)", "$1.000/u-mes"], ["Pedido pendiente (b)", "$750/u-mes"],
        ["Inventario inicial y final", "1.000 u"], ["Bodega", "7.500 u"],
        ["Dotación permitida", "15 a 25"], ["Contrataciones y despidos", "máx. 3 por mes cada uno"],
        ["Pendientes al inicio y al final", "0"]], clase="compact")
    comp = tabla(["Componente", "Uso E/P/Pr", "D oficial", "S", "c", "v (m³)", "L"], [
        ["Motor estándar", "1 / 1 / 0", "96.000", "180.000", "12.000", "0,004", "6"],
        ["Motor premium", "0 / 0 / 1", "24.000", "220.000", "20.000", "0,005", "10"],
        ["Hélice–rejilla", "1 / 1 / 1", "120.000", "150.000", "4.500", "0,015", "8"],
        ["Módulo electrónico", "0 / 1 / 1", "60.000", "200.000", "8.000", "0,0015", "10"],
        ["Control remoto", "0 / 0 / 1", "24.000", "140.000", "5.500", "0,001", "12"]],
        num=(2, 3, 4, 5, 6), clase="compact")
    nota = tabla(["Símbolo", "Significado"], [
        ["Wₜ, Hₜ, Fₜ", "trabajadores, contratados y despedidos en el mes t"],
        ["Rₜ, Oₜ", "producción regular y en horas extra (HE)"],
        ["Iₜ, Bₜ", "inventario y pedidos pendientes al cierre de t"],
        ["yₜ", "binaria: 1 si se paga la multa en t (Modelo B)"],
        ["Dᵢ, Sᵢ, cᵢ", "demanda anual, costo por orden y costo unitario"],
        ["hᵢ = 0,25·cᵢ", "costo anual de mantener una unidad"],
        ["Qᵢ, dᵢ, Lᵢ", "lote, consumo diario (Dᵢ/240) y tiempo de entrega"],
        ["μ, λ", "multiplicadores de espacio y de capital"]], clase="compact")
    return f'''<section class="salto">
<div class="eyebrow">Para tener a mano</div>
<h2 class="pt">Los datos del caso y la notación</h2>
<div class="lbl0">Demanda pronosticada (Parte I)</div>{t_dem}
<div class="dos" style="margin-top:8px"><div>{p1}</div><div>{nota}
<div class="lbl0" style="margin-top:8px">Parte II</div>
<p class="small">Tasa fijada por la Gerencia: <b>10.000 u/mes</b>. Mezcla: Estándar 50 %, Plus 30 %, Premium 20 %. El pedestal y otros elementos comunes no se analizan.</p></div></div>
<div class="lbl0" style="margin-top:8px">Parte III: componentes</div>{comp}
<p class="small muted">Uso E/P/Pr = unidades por ventilador Estándar / Plus / Premium. S = costo por orden ($), c = costo unitario ($), L = tiempo de entrega (días operativos). Tasa de mantención 25 % anual; 240 días operativos; espacio máximo 90 m³; valor máximo de los lotes $110.000.000.</p>
</section>'''


def ideas():
    return f'''<section class="salto">
<div class="eyebrow">Antes de las solicitudes</div>
<h2 class="pt">Las 4 ideas que explican casi todos los resultados</h2>
<h3 class="h3">Idea 1 · La escalera de costos por unidad (explica todo el Modelo A)</h3>
<figure>{SVG_ESCALERA}<figcaption>Para cubrir una unidad de demanda del peak hay varias opciones. El modelo elige siempre la más barata disponible: atrasa antes que adelantar, adelanta como máximo 2 meses y prefiere HE a mantener un trabajador que solo se necesita 6 meses.</figcaption></figure>
<div class="cards">
<div class="card"><h4>Idea 2 · El sueldo se paga por trabajador, no por unidad</h4><p>El enunciado dice que el costo laboral se paga "por cada trabajador disponible, independientemente de que se utilice toda su capacidad". Por eso multiplica a <span class="f">Wₜ</span> y la producción regular no tiene costo propio: una vez contratado, producir en horario normal es gratis. La HE ($2.500) solo se usa cuando la regular no alcanza.</p></div>
<div class="card"><h4>Idea 3 · El EOQ equilibra ordenar y mantener</h4><p>Lote grande: pocos pedidos (ordenar barato) pero mucho inventario (mantener caro). <span class="f">Q* = √(2DS/h)</span> es el punto donde ambos costos se igualan. <b>Q* dice cuánto pedir</b>; el punto de reorden <span class="f">ROP = d·L</span> dice <b>cuándo</b>.</p></div>
<div class="card"><h4>Idea 4 · Activa no significa valiosa</h4><p>Una restricción activa se usa al 100 %. Su multiplicador (μ o λ) dice cuánto se ahorra con <b>una unidad más</b> de recurso, pero solo cerca del óptimo: cambia apenas se relaja. Dos restricciones activas pueden valer muy distinto.</p></div>
<div class="card"><h4>Atajo para las preguntas "¿qué pasa si…?"</h4><p>Ubica el parámetro en la escalera o en la fórmula. Si cambia el orden de las barras, cambia el plan. Si no cambia el orden, el plan se mantiene y solo cambia el costo. Ejemplo: si el atraso costara $1.500, ya no es lo más barato, pero adelantar desde octubre (HE + 3 meses) sigue siendo más caro, así que algo de atraso se mantiene.</p></div>
</div></section>'''


# ------------------------------------------------------------------ Parte I
def s1():
    p1, p2, p3 = P["P1"], P["P2"], P["P3"]
    ocio = (p2.Cap_regular - p2.Prod_regular).tolist()
    mov = [("+" + str(int(h)) if h else ("−" + str(int(f)) if f else "0")) for h, f in zip(p3.Contrataciones, p3.Despidos)]
    t1 = tabla(["Mes"] + MESES, [
        ["Demanda"] + fila_mes(p1, "Demanda"),
        ["P1 · inventario final"] + fila_mes(p1, "Inventario_final"),
        ["P2 · horas extra"] + fila_mes(p2, "Prod_HE"),
        ["P2 · capacidad regular ociosa"] + [n(x) for x in ocio],
        ["P3 · trabajadores"] + fila_mes(p3, "Dotacion"),
        ["P3 · contrata (+) / despide (−)"] + mov,
        ["P3 · producción regular"] + fila_mes(p3, "Prod_regular")],
        num=tuple(range(1, 13)), clase="compact meses", cap="Tabla 1.1 · Lo que cambia mes a mes en cada política (u). Lo que no aparece es fijo: P1 y P2 tienen 20 trabajadores y P1 produce 10.000 regulares cada mes.")
    filas = []
    for k in ("P1", "P2", "P3"):
        df = P[k]
        filas.append([k] + [mm(costo(df, c), 1) for c in ("C_laboral", "C_contratacion", "C_despido", "C_HE", "C_inventario")]
                     + [f"<b>{mm(costo(df, 'C_total_mes'), 1)}</b>"])
    t2 = tabla(["Política", "Laboral", "Contratar", "Despedir", "HE", "Inventario", "Total MM$"], filas,
               num=(1, 2, 3, 4, 5, 6), rec=(1,), cap="Tabla 1.2 · Costo anual por componente (MM$)")
    t3 = tabla(["Política", "Amortiguador del peak", "Ventaja", "Limitación"], [
        ["P1 Tasa constante", "<b>Inventario</b>: llega a 7.000 u en ago–oct (93 % de la bodega)", "Producción y personal 100 % estables; regla muy simple", "Inventario muy caro (52 MM$) y bodega casi llena"],
        ["P2 Dotación + HE", "<b>Horas extra</b>: 6.000 u en nov–feb (dic usa 83 % de la capacidad de HE)", "La más barata; dotación estable; poco inventario", "Paga 20 trabajadores pero deja 6.000 u de capacidad ociosa en mar–ago"],
        ["P3 Persecución", "<b>Contratar y despedir</b>: 9 contrataciones + 6 despidos", "Casi sin inventario ni HE", "40,5 MM$ en movimientos; usa los límites (±3 en mar y nov, tope de 25 en dic)"]],
        cap="Tabla 1.3 · Comparación operacional (lo que pide el enunciado además del costo)")
    return f'''<section class="sol parte-1">
{cabecera("S1", "Construir y comparar políticas simples", "Parte I · Planificación agregada", "Dimensión 1 · 10 %", ref("Solicitud 1", "hojas P1, P2, P3", "parte1_politicas.py", "2"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p>Para cada política: <q>construir el plan mensual completo, determinar su costo total y explicar la lógica operacional que representa</q>, identificando dotación, producción regular, HE, inventario, contrataciones y despidos.</p>
<ul><li><b>P1 Tasa constante:</b> 20 trabajadores y 10.000 u regulares todos los meses. Sin HE, contrataciones, despidos ni pendientes; las diferencias se absorben con inventario, respetando la bodega y el inventario final.</li>
<li><b>P2 Dotación constante + ajuste:</b> 20 trabajadores; se ajusta la producción regular a lo que pide el mes y, si no alcanza, HE. Inventario de 1.000 u al cierre de cada mes.</li>
<li><b>P3 Dotación variable:</b> ajustar los trabajadores para cumplir solo con producción regular y el menor inventario posible; usar el inventario inicial al comienzo y reconstruir 1.000 u en febrero; respetar 15–25 trabajadores y ±3 por mes.</li></ul>
<p>Comparar: <q>no deberá limitarse al costo total: explique qué mecanismo utiliza cada política para responder a las variaciones de demanda y qué ventajas o limitaciones presenta</q>.</p>''')}
<p class="simple">En simple: simular tres reglas fijas mes a mes, sumar sus costos y decir con qué "amortiguador" enfrenta cada una el peak de demanda de nov–ene.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("Plan mensual completo de cada política", "Calculado mes a mes en Python y repetido con fórmulas en el Excel. Lo que varía está en la Tabla 1.1.", "Tabla 1.1"),
        ("Costo total de cada una", "P1 <b>340,0</b> · P2 <b>315,0</b> · P3 <b>329,5</b> MM$. Las tres pagan lo mismo en sueldos (288 MM$).", "Tabla 1.2"),
        ("Lógica operacional", "P1 absorbe con <b>inventario</b>, P2 con <b>horas extra</b>, P3 con <b>contratar y despedir</b>.", "Tabla 1.3"),
        ("Comparación económica y operacional", "Mecanismo, ventaja y limitación de cada una; P2 es la mejor de las tres.", "Tabla 1.3, Por qué")])}
{lbl(3, "Cómo lo hicimos")}
<div class="formula">Balance de cada mes: Iₜ = Iₜ₋₁ + Rₜ + Oₜ − dₜ (sin pendientes)<br>Costo del mes = 1.200.000·Wₜ + 2.500.000·Hₜ + 3.000.000·Fₜ + 2.500·Oₜ + 1.000·Iₜ<br>
P1: Rₜ = 10.000 &nbsp;·&nbsp; P2: producción = dₜ, Rₜ = mín(dₜ; 10.000), Oₜ = el resto &nbsp;·&nbsp; P3: Wₜ = ⌈(dₜ + I_objetivo − Iₜ₋₁) / 500⌉ con 15 ≤ W ≤ 25 y cambio ≤ 3</div>
<p>Una función revisa cada plan (bodega ≤ 7.500, HE ≤ 150·W, 15–25 trabajadores, ±3, inventario final 1.000, cero pendientes) y el Excel repite las cuentas con fórmulas: la celda "Chequeos" de cada hoja dice OK.</p>
<div class="ej"><div class="ej-t">Ejemplos calculados a mano</div>
<p><b>P1, agosto:</b> I = 6.500 + 10.000 − 9.500 = <b>7.000 u</b> → 7,0 MM$ de inventario ese mes (el máximo del año, bajo 7.500).</p>
<p><b>P2, diciembre:</b> demanda 12.500 → regular 10.000 + <b>HE 2.500</b> → 2.500 × $2.500 = 6,25 MM$. La capacidad de HE es 150 × 20 = 3.000: usa el 83 %.</p>
<p><b>P3, marzo:</b> (9.500 + 0 − 1.000) / 500 = <b>17 trabajadores</b> → despide 3 (el máximo) = 9 MM$. <b>Febrero:</b> (10.500 + 1.000) / 500 = 23, para reconstruir las 1.000 u finales.</p></div>
{lbl(4, "Resultados")}
{t1}
{t2}
{t3}
{lbl(5, "Por qué")}
<div class="why"><p>Las tres usan en total 240 trabajador-mes, o sea los mismos 288 MM$ en sueldos: <b>la diferencia está solo en el amortiguador</b>. Una HE ($2.500) cuesta lo mismo que guardar una unidad 2,5 meses.</p>
<p><b>P2 vs P1:</b> P1 reemplaza las 6.000 u de HE de P2 por 40.000 u-mes extra de inventario, o sea 6,7 meses guardada cada una ($6.667/u, contra $2.500 de la HE). <b>P2 vs P3:</b> P3 se ahorra 26 MM$ (11 de inventario y 15 de HE), pero gasta 40,5 en movimientos de personal.</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Por qué P1 no se sale de la bodega?", "Su máximo es 7.000 u (ago–oct) y la bodega es de 7.500. Como produce 120.000 = demanda del año, termina con 1.000, igual que empezó."),
        ("¿Desde qué costo de HE P2 deja de ser la mejor?", "P2 = 300 MM$ + 6.000·c_HE. Le gana a P3 (329,5) mientras c_HE &lt; $4.917/u y a P1 (340) mientras c_HE &lt; $6.667/u."),
        ("¿Y si sube el costo de mantener inventario?", "P1 sube $52.000 por cada $1 (52.000 u-mes), P2 $12.000 y P3 $1.000. P1 solo le ganaría a P2 con h &lt; $375/u-mes."),
        ("¿Por qué P2 tiene capacidad ociosa?", "Paga 20 trabajadores (10.000 u), pero en mar–ago la demanda es menor y el inventario debe quedar en 1.000: sobran 500, 1.000, 1.500, 1.500, 1.000 y 500 u = 6.000 u."),
        ("¿Cuándo empataría P3 con P2?", "Si contratar y despedir costara ≈36 % menos (los 40,5 MM$ tendrían que bajar a 26)."),
        ("¿Cuál política es más estable?", "P1: producción y personal fijos. P2 tiene personal fijo pero producción variable. P3 es la menos estable (15 movimientos).")])}
<div class="trap"><b>Cuidado:</b> comparar solo el costo final es nivel 2 en la rúbrica. Hay que nombrar el amortiguador de cada política, su ventaja y su limitación, y poder anticipar qué pasa si cambia un costo.</div>
</section>'''


def s2():
    a = P["A"]
    t = tabla(["Mes"] + MESES, [
        ["Demanda"] + fila_mes(a, "Demanda"),
        ["Trabajadores"] + [f"{int(w)}{' (−2)' if f else ''}" for w, f in zip(a.Dotacion, a.Despidos)],
        ["Producción regular"] + fila_mes(a, "Prod_regular"),
        ["Capacidad regular ociosa"] + [n(c - r) for c, r in zip(a.Cap_regular, a.Prod_regular)],
        ["Horas extra"] + fila_mes(a, "Prod_HE"),
        ["Inventario final"] + fila_mes(a, "Inventario_final"),
        ["Pendientes"] + fila_mes(a, "Pendientes")],
        num=tuple(range(1, 13)), clase="compact meses", cap="Tabla 2.3 · Solución óptima del Modelo A (u)")
    tc = tabla(["Laboral", "Despidos", "HE (13.000 u)", "Inventario", "Pendientes", "Total"],
               [[mm(costo(a, c), 2) for c in ("C_laboral", "C_despido", "C_HE", "C_inventario", "C_pendientes")] + ["<b>300,75</b>"]],
               num=tuple(range(6)), cap="Tabla 2.4 · Costo del Modelo A (MM$)")
    tv = tabla(["Variable", "Tipo", "Qué significa en Ventisur"], [
        ["Wₜ", "entera", "trabajadores disponibles en el mes t (W₀ = 20)"],
        ["Hₜ, Fₜ", "enteras", "trabajadores contratados / despedidos al inicio del mes t"],
        ["Rₜ", "continua ≥ 0", "unidades producidas en horario regular"],
        ["Oₜ", "continua ≥ 0", "unidades producidas con horas extra"],
        ["Iₜ", "continua ≥ 0", "ventiladores en bodega al cierre del mes"],
        ["Bₜ", "continua ≥ 0", "demanda no entregada al cierre del mes, que se entrega después"]],
        cap="Tabla 2.1 · Variables de decisión (t = marzo … febrero)")
    tr = tabla(["Familia", "Restricción", "Para qué sirve"], [
        ["Evolución de la dotación", "Wₜ = Wₜ₋₁ + Hₜ − Fₜ", "conecta los meses: los trabajadores de hoy son los de ayer más contratados menos despedidos"],
        ["Capacidad regular", "Rₜ ≤ 500·Wₜ", "no se produce más de lo que permite la dotación (sí puede ser menos)"],
        ["Capacidad de HE", "Oₜ ≤ 150·Wₜ", "la HE también depende de cuánta gente hay"],
        ["Balance de inventario", "Iₜ − Bₜ = Iₜ₋₁ − Bₜ₋₁ + Rₜ + Oₜ − dₜ", "lo que había + lo producido − la demanda; si falta, queda como pendiente"],
        ["Bodega", "Iₜ ≤ 7.500", "capacidad de almacenamiento"],
        ["Límites de personal", "15 ≤ Wₜ ≤ 25; Hₜ ≤ 3; Fₜ ≤ 3", "reglas de dotación y de movimientos por mes"],
        ["Bordes", "W₀ = 20, I₀ = 1.000, B₀ = 0; I₁₂ ≥ 1.000, B₁₂ = 0", "cómo empieza y cómo debe terminar el año"]],
        cap="Tabla 2.2 · Familias de restricciones")
    return f'''<section class="sol parte-1">
{cabecera("S2", "Formular e implementar un modelo de optimización (Modelo A)", "Parte I · Planificación agregada", "Dimensión 2 · 20 %", ref("Solicitud 2", "hoja ModA", "parte1_modelos.py · ModeloA_Sol2.lp", "3"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p><q>Formule e implemente un modelo de optimización que determine simultáneamente, para cada mes del horizonte, las decisiones de dotación, contratación, despido, producción regular, producción mediante horas extraordinarias, inventario de producto terminado y pedidos pendientes</q>, respetando todas las condiciones del caso y minimizando el costo total. Además: (a) definir e interpretar cada variable; (b) explicar el propósito de cada familia de restricciones; (c) justificar la función objetivo; (d) interpretar la solución; (e) compararla con las tres políticas; (f) explicar qué combinación de decisiones permite mejorar; (g) discutir comportamientos relevantes o contraintuitivos. Aquí <q>los pedidos pendientes se permiten</q> con costo de $750/u-mes.</p>''')}
<p class="simple">En simple: en vez de fijar de antemano un amortiguador, dejar que el modelo combine gente, HE, inventario y atrasos de la forma más barata.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("Formular e implementar el modelo", "Programación lineal entera mixta en Python con PuLP y el solver CBC. Óptimo: <b>300,75 MM$</b>.", "Modelo completo"),
        ("(a) Variables definidas e interpretadas", "7 familias de variables por mes, enteras las de personal.", "Tabla 2.1"),
        ("(b) Propósito de cada familia de restricciones", "7 familias, cada una con su razón operacional.", "Tabla 2.2"),
        ("(c) Función objetivo justificada", "Suma todos los costos que dependen de las decisiones; el sueldo multiplica a W.", "Modelo completo"),
        ("(d) Solución interpretada", "18 trabajadores todo el año (despide 2 en marzo), HE de septiembre a febrero, inventario de 1–2 meses y 600 u-mes de atraso en dic–ene.", "Tabla 2.3"),
        ("(e) Comparación con las políticas", "−14,25 MM$ vs P2 (−4,5 %), −28,75 vs P3, −39,25 vs P1.", "Tabla 2.5"),
        ("(f) Qué combinación mejora", "Menos gente + HE en el peak + adelantar 1–2 meses + atrasar en dic–ene: usa los tres amortiguadores a la vez.", "Por qué"),
        ("(g) Comportamientos contraintuitivos", "Despide y después paga HE; deja capacidad ociosa en mar y may; acepta atrasos.", "Por qué")])}
{lbl(3, "Cómo lo hicimos · el modelo completo")}
<div class="formula">min Z = Σₜ ( 1.200.000·Wₜ + 2.500.000·Hₜ + 3.000.000·Fₜ + 2.500·Oₜ + 1.000·Iₜ + 750·Bₜ )</div>
<p class="small"><b>Por qué esta función objetivo:</b> incluye todos los costos que cambian con las decisiones. El sueldo multiplica a Wₜ porque se paga por trabajador disponible; la producción regular no tiene costo propio (ya está pagada). Materiales y ventas no se incluyen porque toda la demanda (120.000 u) se produce igual en cualquier plan.</p>
<div class="dos">{tv}{tr}</div>
<div class="ej"><div class="ej-t">Ejemplo calculado a mano: cómo aparecen los pendientes</div>
<p>Noviembre cierra con +400 u. <b>Diciembre:</b> 400 + 9.000 + 2.700 − 12.500 = <b>−400</b> → B = 400 u pendientes (costo 400 × $750 = $300.000). <b>Enero:</b> −400 + 11.700 − 11.500 = −200 → B = 200. <b>Febrero:</b> −200 + 11.700 − 10.500 = <b>1.000</b> = inventario final exigido.</p></div>
{lbl(4, "Resultados · Z = 300,75 MM$")}
{t}
{tc}
{tabla(["Frente a", "Laboral", "Contratar + despedir", "HE", "Inventario", "Pendientes", "Diferencia"], [
        ["P2 (315,0)", "−28,8", "+6,0", "+17,5", "−9,4", "+0,45", "<b>−14,25</b>"],
        ["P3 (329,5)", "−28,8", "−34,5", "+32,5", "+1,6", "+0,45", "<b>−28,75</b>"],
        ["P1 (340,0)", "−28,8", "+6,0", "+32,5", "−49,4", "+0,45", "<b>−39,25</b>"]],
        num=(1, 2, 3, 4, 5, 6), cap="Tabla 2.5 · De dónde sale el ahorro del Modelo A (MM$, A menos la política)")}
<figure><img src="__FIG1__" alt="Producción e inventario neto de cada plan"><figcaption>Figura 2.1 · Izquierda: producción total vs demanda. Derecha: inventario neto (inventario − pendientes). El Modelo A baja de cero en dic–ene: son los atrasos. La Sol. 5 se explica en S5.</figcaption></figure>
{lbl(5, "Por qué · las tres decisiones que explican el plan (mira la escalera de la pág. 4)")}
<div class="cards3">
<div class="why"><b>1. Despide 2 y usa HE.</b> Mantener un trabajador cuesta 14,4 MM$/año (11,4 si se descuenta el despido que se evita) y solo hace falta de sep a feb. Esas ≈3.000 u con HE cuestan 7,5 MM$. Convendría mantenerlo solo si se usara 9,1 meses o más (11,4 ÷ 1,25 MM$ por mes).</div>
<div class="why"><b>2. Adelanta solo 1–2 meses.</b> Guardar 1–2 meses ($1.000–2.000) es más barato que una HE ($2.500); 3 meses ya no. Por eso guarda en jun–jul (para agosto) y oct–nov (para dic), y deja <b>500 u ociosas en marzo y mayo</b>: guardarlas hasta septiembre costaría más de 4 meses.</div>
<div class="why"><b>3. Atrasa en dic–ene.</b> La HE está al tope (2.700 = 150 × 18) y atrasar un mes ($750) es más barato que fabricar antes y guardar ($1.000). Los atrasos se recuperan en enero y febrero.</div>
</div>
<p class="small" style="margin-top:6px"><b>Mejora a las políticas</b> porque combina los tres amortiguadores que cada política usa por separado. <b>Verificaciones:</b> la relajación lineal da 300,68 (la integralidad cuesta solo 0,07 MM$) y el óptimo es único (cada variable se minimizó y maximizó con el costo fijo en Z*).</p>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Por qué el costo laboral multiplica a W y no a la producción?", "Porque se paga por trabajador disponible, use o no toda su capacidad. La producción regular no tiene costo propio."),
        ("¿Hace falta forzar que la HE se use después de la regular?", "No: la regular ya está pagada y la HE cuesta $2.500, así que el óptimo nunca usa HE si queda capacidad regular útil."),
        ("¿Por qué W, H y F son enteras?", "No se contrata medio trabajador. La producción es continua porque son miles de unidades. Relajando todo da 300,68: casi igual."),
        ("¿Puede haber inventario y pendientes el mismo mes?", "En el óptimo no: ambos cuestan y bajar los dos en la misma cantidad mantiene el balance y ahorra."),
        ("¿Qué pasa si quitamos el límite de ±3?", "Nada: no está activo (mismo plan, 300,75). Tampoco cambia con bodega de 2.000: el óptimo guarda máximo 1.000."),
        ("¿Y si atrasar costara $1.500?", "Igual quedan 200 u de atraso (301,0 MM$): adelantar exigiría HE en octubre y guardar (2.500 + 2.000 = 4.500) vs HE en enero + 1 mes de atraso (2.500 + 1.500 = 4.000)."),
        ("¿Y si mantener costara $500?", "Adelanta más (5.000 u-mes de inventario) y el costo baja a 299,1 MM$."),
        ("¿Y si despedir fuera gratis?", "293,95 MM$: 17 trabajadores en mar–jun y 18 desde julio.")])}
<div class="trap"><b>Cuidado:</b> "el solver lo eligió" o "la IA lo calculó" no es una explicación. Cada decisión del plan se justifica con una barra de la escalera de costos.</div>
</section>'''


def s3():
    b = P["B"]
    umb = tabla(["Mes"] + MESES, [["1 % de la demanda"] + [n(x) for x in b.Umbral_1pct],
                                  ["Pendientes en A"] + fila_mes(P["A"], "Pendientes"),
                                  ["Pendientes en B"] + fila_mes(b, "Pendientes"),
                                  ["¿Multa en B? (yₜ)"] + [str(int(x)) for x in b.Multa_activa]],
                num=tuple(range(1, 13)), clase="compact meses", cap="Tabla 3.1 · Umbral de la multa y pendientes (u)")
    m = RJ["big_M"]
    ma = RJ["big_M_ajustada"]
    tm = tabla(["Mes"] + MESES, [["M usada"] + [n(x) for x in m], ["M ajustada"] + [n(x) for x in ma]],
               num=tuple(range(1, 13)), clase="compact meses", cap="Tabla 3.2 · Constante M de cada mes")
    return f'''<section class="sol parte-1">
{cabecera("S3", "Incorporar una condición contractual de servicio (Modelo B)", "Parte I · Planificación agregada", "Dimensión 3 · 15 %", ref("Solicitud 3", "hoja ModB", "parte1_modelos.py · ModeloB_Sol3_multa.lp", "4"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p><q>Si los pedidos pendientes al término de un mes exceden el 1 % de la demanda pronosticada para ese mismo período, la empresa incurre en una multa contractual adicional de $3.000.000 durante dicho mes.</q> Modificar el modelo de la Solicitud 2; <q>presentar y explicar las modificaciones introducidas en las variables, restricciones y función objetivo, implementar el nuevo modelo y analizar cómo la condición contractual modifica las decisiones óptimas y el costo total</q>.</p>''')}
<p class="simple">En simple: al Modelo A se le agrega un costo fijo que "se enciende" si los atrasos de un mes pasan el 1 %. Un costo que salta no se puede escribir como costo por unidad: por eso se necesita una variable binaria.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("Cambio en las variables", "Nueva binaria <b>yₜ ∈ {0,1}</b> por mes: 1 si se paga la multa en el mes t.", "Cómo"),
        ("Cambio en las restricciones", "Nueva restricción <b>Bₜ ≤ 0,01·dₜ + Mₜ·yₜ</b>. Todo lo demás del Modelo A queda igual.", "Cómo"),
        ("Cambio en la función objetivo", "Se suma <b>3.000.000·Σₜ yₜ</b>.", "Cómo"),
        ("Implementar y resolver", "PuLP + CBC: <b>300,94 MM$</b>, sin ninguna multa.", "Tabla 3.1"),
        ("Cómo cambian las decisiones", "Diciembre baja de 400 a <b>125</b> pendientes (justo el 1 %) y enero a 0. Para eso sube la HE de octubre (1.200 → 1.475) y el inventario de oct/nov (200/400 → 475/675).", "Tabla 3.1, Tabla 4.1"),
        ("Cómo cambia el costo", "<b>+193.750</b> frente a A. Mucho menos que una multa de $3 MM.", "Por qué")])}
{lbl(3, "Cómo lo hicimos · la lógica de la binaria")}
<figure>{SVG_ABC}<figcaption>Figura 3.1 · Cómo castiga los atrasos cada modelo. B es un costo "con salto" (no convexo): no se puede representar con un costo por unidad, por eso necesita una binaria.</figcaption></figure>
<div class="dos">
<div class="formula">Bₜ ≤ 0,01·dₜ + Mₜ·yₜ &nbsp;&nbsp; yₜ ∈ {{0,1}}<br>min Z_A + 3.000.000·Σₜ yₜ</div>
<div class="small"><p><b>Si Bₜ ≤ 1 % de dₜ:</b> la restricción se cumple con yₜ = 0; como yₜ = 1 cuesta $3 MM, el modelo elige 0 → no hay multa.</p>
<p><b>Si Bₜ &gt; 1 % de dₜ:</b> la única forma de cumplir la restricción es yₜ = 1 → se paga la multa.</p></div></div>
<p><b>La constante M:</b> tiene que ser al menos el mayor exceso posible Bₜ − 0,01dₜ, para que con yₜ = 1 la restricción "se apague" sin cortar ningún plan válido. Usamos el peor caso (no producir nada hasta t): <span class="f">Mₜ = Σ demanda hasta t − I₀ − 0,01·dₜ</span>. Diciembre: 98.000 − 1.000 − 125 = <b>96.875</b>. Es válida pero no la más ajustada: con la cota que considera la capacidad máxima (diciembre 9.375) el óptimo es el mismo (300.943.750). Un M muy chico corta planes válidos; uno muy grande debilita la relajación lineal (el solver se demora más), pero no cambia el óptimo.</p>
{tm}
{lbl(4, "Resultados · Z = 300,94 MM$")}
{umb}
<div class="ej"><div class="ej-t">De dónde salen los +193.750</div>
<p>B produce 275 u con HE en <b>octubre</b> en vez de en enero–febrero (la HE total sigue en 13.000 u, así que su costo no cambia) y las guarda dos meses: +550 u-mes de inventario = <b>+550.000</b>. A cambio evita 475 u-mes de atraso (dic 400 → 125, ene 200 → 0) = <b>−356.250</b>. Neto: <b>+193.750</b>.</p></div>
{lbl(5, "Por qué")}
<div class="why"><p>La multa cambia la escalera: atrasar ya no cuesta solo $750 por unidad, porque pasar del umbral cuesta $3 MM de una vez. Bajar los atrasos al 1 % cuesta 193.750, así que el modelo nunca paga multas. <b>Plan A bajo el contrato</b> pagaría dos multas (dic 400 &gt; 125; ene 200 &gt; 115): 300,75 + 6 = 306,75 MM$.</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Qué hace exactamente la binaria?", "Decide si se paga la multa. No cuenta pendientes: solo se activa (yₜ = 1) cuando los pendientes superan el 1 %, porque si no la restricción no se cumpliría."),
        ("¿Por qué B no paga ninguna multa?", "Evitar las multas cuesta 193.750, mucho menos que $3 MM. Solo convendría pagar una multa si costara menos de $151.250."),
        ("¿Qué pasa si M es muy chica?", "Corta planes válidos: con yₜ = 1 la restricción seguiría limitando los pendientes. Con M = 0 el modelo prohibiría pasar el 1 % aunque pagara."),
        ("¿Y si el umbral fuera otro?", "Con 3,2 % o más, B da lo mismo que A (300,75); con 2 %, 300,825; con 0 %, B es igual a C (301,10)."),
        ("¿Por qué no basta un costo por unidad?", "La multa no crece con cada unidad: es un monto fijo que aparece al cruzar el umbral. Eso es una función con salto y requiere variable binaria."),
        ("¿Cómo verificaron el resultado?", "Se recalculó el costo del plan fuera del modelo y se resolvió también con la M ajustada: mismo óptimo.")])}
<div class="trap"><b>Cuidado:</b> B deja diciembre exactamente en 125 u = 1 %. Está en el borde: un error de pronóstico de una unidad gatilla $3 MM. Esto se usa en la recomendación (S5).</div>
</section>'''


def s4():
    a, b, c = P["A"], P["B"], P["C"]

    def he(df):
        return " / ".join(n(x) for x in df.Prod_HE[6:])

    def inv(df):
        return n(df.Inventario_final.sum())

    def pend(df):
        return n(df.Pendientes.sum())

    t = tabla(["", "A (Sol. 2)", "B (Sol. 3)", "C (Sol. 4)"], [
        ["Trabajadores", "18 (despide 2 en marzo)", "18 (igual)", "18 (igual)"],
        ["Producción regular", n(a.Prod_regular.sum()) + " u", "igual", "igual"],
        ["HE sep / oct / nov / dic / ene / feb", he(a), he(b), he(c)],
        ["HE total", n(a.Prod_HE.sum()) + " u", n(b.Prod_HE.sum()) + " u", n(c.Prod_HE.sum()) + " u"],
        ["Inventario oct / nov", "200 / 400", "475 / 675", "600 / 800"],
        ["Inventario acumulado (u-mes)", inv(a), inv(b), inv(c)],
        ["Pendientes (u-mes)", pend(a), pend(b), pend(c)],
        ["Demanda entregada a tiempo", "99,5 %", "99,9 %", "<b>100 %</b>"],
        ["Costo total (MM$)", "300,75", "300,94", "<b>301,10</b>"],
        ["Diferencia vs A", "—", "+193.750", "<b>+350.000 (+0,12 %)</b>"]],
        cap="Tabla 4.1 · Comparación de las Solicitudes 2, 3 y 4 (lo que pide el enunciado)")
    return f'''<section class="sol parte-1">
{cabecera("S4", "Política de cero pedidos pendientes (Modelo C)", "Parte I · Planificación agregada", "Dimensión 3 · 15 %", ref("Solicitud 4", "hoja ModC", "parte1_modelos.py · ModeloC_Sol4_cero_pendientes.lp", "4"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p>Retomar el modelo de la <b>Solicitud 2</b> (no el de la 3) y suponer que <q>no se aceptan pedidos pendientes al cierre de ningún período</q>. Explicar los cambios, implementar, resolver e interpretar. Luego: <q>Compare las soluciones obtenidas en las Solicitudes 2, 3 y 4 … dotación, producción, horas extraordinarias, inventario y pedidos pendientes, y cuantifique el costo asociado a mejorar el nivel de servicio.</q></p>''')}
<p class="simple">En simple: al Modelo A se le prohíbe atrasar. Después se comparan A, B y C para ver cuánto cuesta mejorar el servicio.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("Cambio en la formulación", "Se agrega <b>Bₜ = 0</b> para todos los meses. Nada más cambia.", "Cómo"),
        ("Implementar y resolver", "<b>301,10 MM$</b>.", "Tabla 4.1"),
        ("Interpretar", "Mismo plan que A, pero produce 400 u más con HE en octubre y las guarda para cubrir dic–ene.", "Por qué"),
        ("Comparar dotación, producción, HE, inventario y pendientes", "Igual dotación y producción regular; igual HE total; cambia <b>cuándo</b> se hace la HE y cuánto se guarda.", "Tabla 4.1"),
        ("Cuantificar el costo de mejorar el servicio", "A → B: +193.750 · B → C: +156.250 · A → C: <b>+350.000</b> (0,12 %).", "Tabla 4.1")])}
{lbl(3, "Cómo lo hicimos")}
<div class="formula">Modelo A + &nbsp; Bₜ = 0 para t = mar … feb &nbsp;&nbsp;(equivale a sacar Bₜ del balance: Iₜ = Iₜ₋₁ + Rₜ + Oₜ − dₜ)</div>
<div class="ej"><div class="ej-t">De dónde salen los +350.000</div>
<p>C mueve 400 u de HE de enero–febrero a <b>octubre</b> (HE total igual, 13.000 u) y las guarda: +800 u-mes de inventario × $1.000 = <b>+800.000</b>. Elimina 600 u-mes de atraso × $750 = <b>−450.000</b>. Neto: <b>+350.000</b>.</p></div>
{lbl(4, "Resultados · Z = 301,10 MM$")}
{t}
{lbl(5, "Por qué")}
<div class="why"><p>Los tres modelos usan las <b>mismas</b> herramientas en la misma cantidad (18 trabajadores, 107.000 u regulares, 13.000 u de HE). Lo único que cambia es el <b>calendario</b>: cuanto menos atraso se permite, más HE se adelanta a octubre y más inventario se guarda. Como guardar ($1.000) cuesta poco más que atrasar ($750), el servicio completo es casi gratis: 0,12 % del costo.</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Por qué C no contrata gente para el peak?", "Un trabajador extra para sep–feb cuesta ≈11,4 MM$ al año (≈$3.800 por unidad); adelantar con HE y guardar 2 meses cuesta $4.500 por unidad solo para 400 u. Ver la escalera."),
        ("¿Por qué la HE total no cambia entre A, B y C?", "Porque la producción total del año es la misma (120.000 u); solo cambia en qué mes se hace la HE."),
        ("¿Qué significa 99,5 % a tiempo?", "De las 120.000 u, 600 u-mes quedaron atrasadas al cierre de algún mes: 1 − 600/120.000 = 99,5 %."),
        ("¿C queda con holgura?", "No: la HE de nov–dic está al 100 % y la de ene–feb al 93 %. Esto se discute en S5.")])}
<div class="trap"><b>Cuidado:</b> C se construye sobre A (Solicitud 2), no sobre B. El modelo "B + cero pendientes" es el que pide la Solicitud 5.</div>
</section>'''


def s5():
    def dot(lst):
        lst = json.loads(lst)
        if len(set(lst)) == 1:
            return str(lst[0])
        cambios = [MESES[i].lower() for i in range(1, 12) if lst[i] != lst[i - 1]]
        return f"{lst[0]} → {lst[-1]} (desde {cambios[0]})"

    sel = ["Recomendado (Sol. 5)", "Sol. 5 con dotación fija 19", "Sol. 5 con dotación fija 20 (sin despidos)",
           "Sol. 5 con HE <= 80 % de su capacidad", "Sol. 5 con costo HE +20 % ($3.000)",
           "Sol. 5 con costo despido x2 ($6.000.000)", "Sol. 5 con demanda de diciembre +5 % (13.125)"]
    nom = {"Recomendado (Sol. 5)": "<b>Recomendado (Sol. 5)</b>", "Sol. 5 con HE <= 80 % de su capacidad": "Sol. 5 con HE ≤ 80 % de su capacidad"}
    filas = []
    for e in sel:
        r = SEN[SEN.Escenario == e].iloc[0]
        filas.append([nom.get(e, e), mm(r.costo, 2), dot(r.dotacion), n(r.unid_HE), n(r.inv_total)])
    tsen = tabla(["Escenario (siempre con cero pendientes)", "Costo MM$", "Trabajadores", "HE (u)", "Inventario (u-mes)"], filas,
                 num=(1, 3, 4), rec=(0,), cap="Tabla 5.2 · ¿Qué tan robusta es la recomendación? (parte1_sensibilidad.py)")
    tcomp = tabla(["Plan", "Costo MM$", "Trabajadores", "Movimientos", "HE (u)", "Inventario (u-mes)", "Pendientes (u-mes)", "A tiempo", "Multas con el contrato"], [
        ["P1", "340,00", "20", "0", "0", "52.000", "0", "100 %", "0"],
        ["P2", "315,00", "20", "0", "6.000", "12.000", "0", "100 %", "0"],
        ["P3", "329,50", "17 a 25", "15", "0", "1.000", "0", "100 %", "0"],
        ["A (Sol. 2)", "300,75", "18", "2", "13.000", "2.600", "600", "99,5 %", "2 (+6 MM$)"],
        ["B (Sol. 3)", "300,94", "18", "2", "13.000", "3.150", "125", "99,9 %", "0"],
        ["<b>C = Sol. 5</b>", "<b>301,10</b>", "18", "2", "13.000", "3.400", "0", "100 %", "0"]],
        num=(1, 3, 4, 5, 6), rec=(5,), cap="Tabla 5.1 · Todos los planes lado a lado")
    return f'''<section class="sol parte-1">
{cabecera("S5", "Recomendación de planificación agregada", "Parte I · Planificación agregada", "Dimensión 3 · 15 %", ref("Solicitud 5", "hojas ModD, Comparacion_Planes, Sensibilidad_P1", "parte1_modelos.py, parte1_sensibilidad.py · ModeloD_Sol5_multa_y_cero_pend.lp", "5"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p>Retomar el modelo de la <b>Solicitud 3</b> (con multa) y modificarlo para que <q>no permite pedidos pendientes al término de ningún período</q>. Con las políticas y los modelos, formular una recomendación que considere <q>costos, estabilidad operacional, utilización de horas extraordinarias, evolución de la dotación, inventarios, nivel de servicio</q>. <q>No es suficiente identificar la alternativa de menor costo: la recomendación deberá explicar por qué la política seleccionada resulta apropiada para Ventisur y qué trade-offs implica.</q></p>''')}
<p class="simple">En simple: resolver "B + cero pendientes", poner todos los planes lado a lado y elegir uno con argumentos que vayan más allá del costo.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("Resolver B + cero pendientes", "<b>301,10 MM$, idéntico a C</b>: si Bₜ = 0 nunca se pasa el 1 %, todas las yₜ valen 0 y la multa desaparece. (En los archivos se llama Modelo D.)", "Cómo"),
        ("Costos", "13,9 MM$ menos que P2 (−4,4 %); solo 0,35 MM$ más que A, que con multas costaría 306,75.", "Tabla 5.1"),
        ("Estabilidad operacional", "Un solo ajuste de personal (−2 en marzo), contra 15 movimientos de P3. Producción regular estable (9.000; 8.500 en mar y may).", "Tabla 5.1"),
        ("Uso de horas extra", "13.000 u (10,8 % de la producción) en sep–feb; al 100 % en nov–dic y 93 % en ene–feb.", "Tabla 5.2"),
        ("Evolución de la dotación", "18 trabajadores todo el año.", "Tabla 5.1"),
        ("Inventarios", "Máximo 800 u (noviembre); 3.400 u-mes en el año contra 52.000 de P1.", "Tabla 5.1"),
        ("Nivel de servicio", "100 % a tiempo; ningún riesgo de multa.", "Tabla 5.1"),
        ("Trade-offs", "Menos holgura ante errores de pronóstico (HE saturada) a cambio de menor costo. Seguro: 19 trabajadores por +1,4 MM$.", "Recomendación")])}
{lbl(3, "Cómo lo hicimos")}
<div class="formula">Modelo B + &nbsp; Bₜ = 0 &nbsp;⇒&nbsp; Bₜ = 0 ≤ 0,01·dₜ siempre &nbsp;⇒&nbsp; yₜ = 0 &nbsp;⇒&nbsp; mismo modelo y misma solución que C</div>
<p>Además corrimos escenarios con el modelo de la Sol. 5 para ver qué tan robusta es la recomendación (Tabla 5.2).</p>
{lbl(4, "Resultados")}
{tcomp}
<figure><img src="__FIG2__" alt="Costo total de cada plan por componente"><figcaption>Figura 5.1 · Costo total de cada plan y su composición. Las tres políticas pagan 288 MM$ de sueldos; los modelos, 259,2.</figcaption></figure>
{tsen}
<div class="reco"><div class="reco-t">Nuestra recomendación</div>
<p><b>Adoptar la Sol. 5: 18 trabajadores (despedir 2 en marzo), HE de septiembre a febrero y cero pendientes, por 301,10 MM$.</b></p>
<p><b>Por qué esta y no otra:</b> es 13,9 MM$ más barata que la mejor política simple; cuesta solo 0,12 % más que A y, a diferencia de A, cumple el contrato (A pagaría 306,75); B ahorra apenas 156.250 frente a la Sol. 5, pero queda justo en el umbral de la multa.</p>
<p><b>Trade-off que asumimos:</b> la HE queda sin holgura en nov–dic. Si la Gerencia no confía en el pronóstico, el <b>seguro</b> es mantener 19 trabajadores: +1,4 MM$ (302,5) y deja 700–850 u/mes de HE libre en nov, ene y feb (diciembre sigue al tope).</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Por qué no recomendar A si es el más barato?", "Sus atrasos violan el contrato: con las dos multas cuesta 306,75 MM$. Además deja 0,5 % de la demanda atrasada."),
        ("¿Por qué no B?", "Queda exactamente en el 1 % en diciembre: un error mínimo de pronóstico cuesta $3 MM. Solo ahorra 156.250."),
        ("¿P2 no es más estable?", "Mantiene la dotación fija, pero lo paga con 6.000 u de capacidad ociosa y 13,9 MM$ más. La Sol. 5 hace un único ajuste en marzo."),
        ("¿Y si la demanda de diciembre sube 5 %?", "Si se sabe a tiempo, se re-planifica con los mismos 18 (303,9 MM$). Si no, no alcanza: 800 + 9.000 + 2.700 = 12.500 &lt; 13.125. Por eso el seguro de 19."),
        ("¿Por qué dicen “estable” si la producción total varía?", "Estable = dotación y producción regular. La HE sí varía; solo P1 tiene producción totalmente plana."),
        ("¿Qué pasa si la HE sube a $3.000?", "Conviene contratar 1 en septiembre (19 desde sep): 307,05 MM$.")])}
<div class="trap"><b>Cuidado:</b> el enunciado dice que <i>no basta</i> con elegir la alternativa más barata. La recomendación debe mencionar estabilidad, HE, dotación, inventario, servicio y el trade-off.</div>
</section>'''


# ------------------------------------------------------------------ Parte II
def s6():
    t1 = tabla(["Modelo", "Participación", "Producción mensual", "Producción anual"],
               [[r.Modelo.replace("Ventilador ", ""), pct(r.Participacion, 0), n(r.Prod_mensual), n(r.Prod_anual)] for r in PRO.itertuples()],
               num=(1, 2, 3), cap="Tabla 6.1 · Producción por modelo")
    t2 = tabla(["Componente", "Lo usan", "Mensual", "Anual (× 12)", "¿= oficial?"],
               [[NOMBRES[k], ["Estándar + Plus", "Premium", "los tres", "Plus + Premium", "Premium"][k], n(r.Req_mensual), n(r.Req_anual),
                 "sí" if r.Coincide_oficial else "no"] for k, r in enumerate(REQ.itertuples())],
               num=(2, 3), cap="Tabla 6.2 · Requerimientos de componentes")
    return f'''<section class="sol parte-2">
{cabecera("S6", "Desagregar la producción y determinar requerimientos", "Parte II · De la producción a los materiales", "Dimensión 4 · 10 %", ref("Solicitud 6", "hoja Desagregacion", "parte2_requerimientos.py", "6"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p>Con la tasa de <b>10.000 u/mes</b> que fijó la Gerencia (se usa <q>independientemente de la recomendación desarrollada por el equipo en la Parte I</q>) y la mezcla 50–30–20: (a) producción mensual y anual de cada modelo; (b) requerimientos mensuales y anuales de los cinco componentes; (c) <q>explique por qué … estos requerimientos pueden tratarse como aproximadamente constantes en el tiempo</q>; (d) <q>identifique qué supuestos de la planificación anterior permiten realizar esta simplificación</q>. Ojo: son <q>tasas esperadas de consumo … No corresponden todavía a cantidades a ordenar</q>.</p>''')}
<p class="simple">En simple: pasar de "ventiladores" a "piezas": cuántas unidades de cada componente se consumen por mes y por año.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("(a) Producción por modelo", "Estándar 5.000, Plus 3.000, Premium 2.000 u/mes (60.000, 36.000 y 24.000 al año).", "Tabla 6.1"),
        ("(b) Requerimientos de componentes", "8.000 · 2.000 · 10.000 · 5.000 · 2.000 u/mes; al año 96.000 · 24.000 · 120.000 · 60.000 · 24.000. Coinciden con los oficiales.", "Tabla 6.2"),
        ("(c) Por qué son constantes", "Tasa fija + mezcla fija + lista de materiales fija ⇒ cada mes se consume lo mismo, repartido parejo en los días operativos.", "Por qué"),
        ("(d) Supuestos que lo permiten", "Unidad agregada homogénea; demanda determinística; mezcla estable mes a mes; producción nivelada por decisión de la Gerencia.", "Por qué")])}
{lbl(3, "Cómo lo hicimos")}
<figure>{SVG_BOM}<figcaption>Figura 6.1 · Requerimiento = Σ (producción del modelo × unidades del componente que usa ese modelo).</figcaption></figure>
<div class="ej"><div class="ej-t">Ejemplo calculado a mano</div>
<p><b>Motor estándar</b> = 1 × 5.000 (Estándar) + 1 × 3.000 (Plus) + 0 × 2.000 (Premium) = <b>8.000 u/mes</b> → × 12 = <b>96.000 u/año</b>. <b>Módulo</b> = 0 × 5.000 + 1 × 3.000 + 1 × 2.000 = 5.000. <b>Hélice</b> = 5.000 + 3.000 + 2.000 = 10.000.</p></div>
{lbl(4, "Resultados")}
<div class="dos">{t1}{t2}</div>
{lbl(5, "Por qué")}
<div class="why"><p><b>Son tasas, no pedidos:</b> dicen cuánto se gasta por mes. Cuánto y cuándo comprar se decide en la Parte III. <b>Son constantes</b> porque la tasa (10.000), la mezcla y la lista de materiales no cambian en el año, y la producción se reparte pareja en 20 días operativos por mes (240 ÷ 12).</p>
<p><b>Supuestos de la Parte I que lo permiten:</b> que una unidad de cualquier modelo use la misma capacidad (unidad agregada), que el pronóstico se cumpla (determinístico) y que la mezcla 50–30–20 se mantenga todos los meses. Si se usara nuestro plan de la Sol. 5, la producción iría de 8.500 a 11.700 u/mes y el consumo ya no sería constante (ver Integración).</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Por qué el motor estándar es 8.000 y no 5.000?", "Porque lo usan el Estándar (5.000) y el Plus (3.000). El módulo lo usan Plus y Premium; la hélice, los tres."),
        ("¿Y con mezcla 40–30–30?", "Motor est. 7.000/mes, motor prem. 3.000, hélice 10.000, módulo 6.000, control 3.000."),
        ("¿Por qué no aparece el pedestal?", "El enunciado solo analiza los cinco componentes seleccionados; los elementos comunes se omiten."),
        ("¿Por qué usar 10.000 y no su recomendación?", "El enunciado lo exige: la Gerencia fijó esa tasa por estabilidad y coordinación con proveedores. Además da un consumo constante, que es lo que necesita el EOQ.")])}
<div class="trap"><b>Cuidado:</b> no confundas desagregar con lotificar (la rúbrica lo nombra como error de nivel 1). Esta etapa no dice tamaños de pedido.</div>
</section>'''


# ------------------------------------------------------------------ Parte III
def s7():
    filas = []
    for k, r in enumerate(EOQ.itertuples()):
        filas.append([NOMBRES[k], n(r.h), n(r.Q), n(r.N, 1), n(r.T_dias, 1), n(r.d_diaria), n(r.L), n(r.ROP),
                      mm(r.C_ordenar, 2), mm(r.C_mantener, 2), mm(r.C_relevante, 2)])
    filas.append(["<b>Total</b>", "", "", n(EOQ.N.sum(), 1), "", "", "", "", mm(EOQ.C_ordenar.sum(), 2), mm(EOQ.C_mantener.sum(), 2),
                  f"<b>{mm(EOQ.C_relevante.sum(), 2)}</b>"])
    t = tabla(["Componente", "hᵢ ($/año)", "Q*", "N/año", "T (días)", "d (u/día)", "L", "ROP", "Ordenar", "Mantener", "Total MM$"],
              filas, num=tuple(range(1, 11)), tot=(5,), cap="Tabla 7.1 · Política EOQ de cada componente por separado")
    return f'''<section class="sol parte-3">
{cabecera("S7", "Políticas EOQ individuales", "Parte III · Inventarios determinísticos", "Dimensión 5 · 15 %", ref("Solicitudes 7 y 8", "hoja EOQ_Individual", "parte3_inventarios.py (eoq_individual)", "6"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p>Tratando cada componente por separado, con consumo y tiempo de entrega conocidos y constantes, calcular: (a) el costo anual de mantener <b>hᵢ</b>; (b) el lote económico <b>Qᵢ*</b>; (c) pedidos por año; (d) tiempo entre pedidos en días operativos; (e) consumo diario; (f) punto de reorden; (g) costos anuales de ordenar y mantener; (h) <q>interprete operacionalmente la política obtenida, indicando cuánto y cuándo debería ordenar Ventisur</q>. Además, <q>explique los principales supuestos que permiten utilizar el modelo EOQ clásico y un punto de reorden determinístico … y relacione dichos supuestos con las decisiones adoptadas en la Parte II</q>.</p>''')}
<p class="simple">En simple: para cada pieza, decidir de qué tamaño hacer cada pedido (cuánto) y con cuánto stock en bodega emitirlo (cuándo).</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("(a) hᵢ", "hᵢ = 25 % × cᵢ: 3.000 · 5.000 · 1.125 · 2.000 · 1.375 $/u-año.", "Tabla 7.1"),
        ("(b) Qᵢ*", "√(2DᵢSᵢ/hᵢ): 3.394 · 1.453 · 5.657 · 3.464 · 2.211 u.", "Tabla 7.1"),
        ("(c) Pedidos por año", "Nᵢ = Dᵢ/Qᵢ*: 28,3 · 16,5 · 21,2 · 17,3 · 10,9 (94,2 en total).", "Tabla 7.1"),
        ("(d) Tiempo entre pedidos", "Tᵢ = 240/Nᵢ: 8,5 · 14,5 · 11,3 · 13,9 · 22,1 días operativos.", "Tabla 7.1"),
        ("(e) Consumo diario", "dᵢ = Dᵢ/240: 400 · 100 · 500 · 250 · 100 u/día.", "Tabla 7.1"),
        ("(f) Punto de reorden", "ROPᵢ = dᵢ·Lᵢ: 2.400 · 1.000 · 4.000 · 2.500 · 1.200 u.", "Tabla 7.1"),
        ("(g) Costos de ordenar y mantener", "Iguales en cada componente (propiedad del EOQ): 16,89 + 16,89 = <b>33,78 MM$/año</b>.", "Tabla 7.1"),
        ("(h) Cuánto y cuándo", "\"Pedir 3.394 motores estándar cada vez que queden 2.400 en bodega\" (y así cada uno).", "Figura 7.1"),
        ("Supuestos y relación con la Parte II", "Consumo constante (gracias a la tasa y mezcla fijas de la Parte II), plazo fijo, sin quiebres ni descuentos.", "Por qué")])}
{lbl(3, "Cómo lo hicimos")}
<div class="formula">hᵢ = 0,25·cᵢ &nbsp;·&nbsp; Qᵢ* = √(2·Dᵢ·Sᵢ / hᵢ) &nbsp;·&nbsp; Nᵢ = Dᵢ/Qᵢ* &nbsp;·&nbsp; Tᵢ = Qᵢ*/dᵢ = 240/Nᵢ &nbsp;·&nbsp; dᵢ = Dᵢ/240 &nbsp;·&nbsp; ROPᵢ = dᵢ·Lᵢ<br>Costo relevante = Dᵢ·Sᵢ/Qᵢ (ordenar) + hᵢ·Qᵢ/2 (mantener el inventario promedio)</div>
<div class="ej"><div class="ej-t">Ejemplo calculado a mano: motor estándar</div>
<p>h = 0,25 × 12.000 = <b>3.000</b> · Q* = √(2 × 96.000 × 180.000 / 3.000) = √11.520.000 = <b>3.394</b> · N = 96.000/3.394 = <b>28,3</b> pedidos · d = 96.000/240 = <b>400 u/día</b> · T = 3.394/400 = <b>8,5 días</b> · ROP = 400 × 6 = <b>2.400</b> · Ordenar = 28,3 × 180.000 = 5,09 MM$ = Mantener = 3.000 × 3.394/2 = 5,09 MM$.</p></div>
{lbl(4, "Resultados")}
{t}
<figure>{svg_dientes()}<figcaption>Figura 7.1 · La política del motor estándar en el tiempo. Cuando quedan 2.400 u (ROP) se pide; el pedido demora 6 días, en los que se consumen 6 × 400 = 2.400 u, así que llega justo cuando la bodega queda en cero.</figcaption></figure>
{lbl(5, "Por qué")}
<div class="why"><p><b>El trade-off del EOQ:</b> pedir más grande baja el costo de ordenar (menos pedidos) pero sube el de mantener (más inventario promedio). Q* es el punto donde ambos se igualan. <b>Q* responde cuánto; el ROP responde cuándo.</b> Como el ciclo T es mayor que el plazo L en todos los componentes, cada pedido llega antes de emitir el siguiente: nunca hay dos pedidos en camino.</p>
<p><b>Supuestos:</b> consumo constante y conocido; plazo de entrega constante y conocido; el lote llega completo; sin quiebres; sin descuentos por cantidad; S y h constantes. El primero viene de la <b>Parte II</b>: la tasa estable de 10.000 y la mezcla fija hacen que el consumo sea parejo. Como todo es determinístico, <b>no corresponde stock de seguridad</b>.</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Qué pasa si la demanda se duplica?", "Q* sube √2 ≈ 1,41 veces (Q* depende de la raíz de D) y el ROP se duplica (ROP = d·L)."),
        ("¿Y si aumenta el tiempo de entrega?", "Cambia el cuándo, no el cuánto: el ROP sube y Q* no cambia. Si L superara a T habría pedidos en camino y el ROP se aplica sobre la posición de inventario (bodega + pedidos en camino)."),
        ("¿Por qué ordenar y mantener cuestan lo mismo?", "Es una propiedad del óptimo del EOQ: en Q*, D·S/Q = h·Q/2."),
        ("¿Y con tasa de mantención de 20 % o 30 %?", "Q* cambia con 1/√h. Con 20 % los EOQ piden 126,5 m³ y 151,1 MM$; con 30 %, 103,2 m³ y 123,3 MM$. Siguen sin caber."),
        ("¿Por qué no hay stock de seguridad?", "La rúbrica lo dice explícitamente: demanda y plazos determinísticos."),
        ("¿Por qué 240 días y no 365?", "El enunciado define 240 días operativos; el consumo y el plazo se miden en esos días.")])}
<div class="trap"><b>Cuidado:</b> no mezcles días calendario con días operativos, y no agregues stock de seguridad.</div>
</section>'''


def s8():
    filas = []
    for k, r in enumerate(EOQ.itertuples()):
        filas.append([NOMBRES[k], n(r.Q), n(V[k], 4 if V[k] < 0.0015 else 4).rstrip("0").rstrip(","), n(r.Espacio, 2), pct(r.Espacio / 90), n(r.c), mm(r.Capital, 2), pct(r.Capital / 110e6)])
    e, c = EOQ.Espacio.sum(), EOQ.Capital.sum()
    filas.append(["<b>Total</b>", "", "", f"<b>{n(e, 2)}</b>", pct(e / 90), "", f"<b>{mm(c, 2)}</b>", pct(c / 110e6)])
    t = tabla(["Componente", "Q*", "vᵢ (m³)", "Espacio vᵢ·Q* (m³)", "% de 90", "cᵢ ($)", "Capital cᵢ·Q* (MM$)", "% de 110"], filas,
              num=tuple(range(1, 8)), tot=(5,), cap="Tabla 8.1 · Cómo usa cada EOQ los recursos compartidos")
    return f'''<section class="sol parte-3">
{cabecera("S8", "Evaluar la factibilidad conjunta de los EOQ", "Parte III · Inventarios determinísticos", "Dimensión 5 · 15 %", ref("Solicitudes 7 y 8", "hoja EOQ_Individual", "parte3_inventarios.py", "6"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p>Hay <q>un máximo de 90 m³ de espacio de almacenamiento asignado a los lotes de estos cinco componentes</q> y <q>el valor total de los lotes objetivo no puede exceder $110.000.000</q>. <q>Evalúe si los EOQ individuales pueden implementarse simultáneamente</q>. <q>El análisis deberá mostrar explícitamente cómo se utiliza cada recurso y explicar por qué una colección de decisiones individualmente óptimas puede resultar infactible cuando los productos compiten por recursos compartidos.</q></p>''')}
<p class="simple">En simple: sumar cuánto espacio y cuánta plata ocupan los cinco lotes de la S7 y compararlo con lo que hay.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("¿Se pueden implementar juntos?", "<b>No.</b> Piden 113,1 m³ (máx. 90) y 135,1 MM$ (máx. 110).", "Figura 8.1"),
        ("Mostrar cómo se usa cada recurso", "Espacio y capital de cada componente, en m³, MM$ y % del límite.", "Tabla 8.1"),
        ("Por qué óptimos individuales pueden ser infactibles", "Cada EOQ minimiza solo su propio costo y no \"ve\" que los demás usan la misma bodega y el mismo presupuesto.", "Por qué")])}
{lbl(3, "Cómo lo hicimos")}
<div class="formula">Espacio = Σᵢ vᵢ·Qᵢ* ≤ 90 m³ &nbsp;&nbsp;·&nbsp;&nbsp; Capital = Σᵢ cᵢ·Qᵢ* ≤ 110.000.000 $</div>
<p>Medimos sobre el <b>lote completo</b>: es lo que dice el enunciado ("espacio asignado a los lotes", "valor total de los lotes") y es lo conservador, porque los lotes podrían llegar juntos.</p>
<div class="ej"><div class="ej-t">Ejemplo calculado a mano: hélice–rejilla</div>
<p>Espacio = 0,015 × 5.657 = <b>84,85 m³</b> (94 % de la bodega, ella sola). Capital = 4.500 × 5.657 = 25,46 MM$.</p></div>
{lbl(4, "Resultados")}
<figure>{svg_recursos()}<figcaption>Figura 8.1 · Uso de cada recurso por componente. Ambos se pasan del límite.</figcaption></figure>
{t}
{lbl(5, "Por qué")}
<div class="why"><p>Cada EOQ se calculó mirando solo su propio costo. Nada lo obligaba a compartir. La <b>hélice</b> es voluminosa (0,015 m³, la más grande) y barata de mantener, por eso su lote es grande y llena la bodega. Los <b>motores</b> son caros y concentran el capital (63 %). La suma de decisiones óptimas por separado no es óptima ni factible para el sistema completo: hay que decidir los cinco lotes juntos (S9).</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Qué componente causa el problema de espacio? ¿Y el de capital?", "Espacio: la hélice (84,9 de 113,1 m³). Capital: los motores (40,7 + 29,1 de 135,1 MM$)."),
        ("¿Bastaría con achicar solo el lote de la hélice?", "Arreglaría el espacio, pero el capital seguiría excedido en 25 MM$. Hay que ajustar todos."),
        ("¿Y si se midiera con el inventario promedio (Q/2)?", "Los EOQ usarían 56,6 m³ y 67,6 MM$ y cabrían. Usamos lotes completos porque es lo que pide el enunciado y es lo conservador."),
        ("¿Se pierde mucho por no poder usar los EOQ?", "No: la S9 muestra que cumplir los límites cuesta solo 0,72 MM$/año (+2,1 %).")])}
<div class="trap"><b>Cuidado:</b> decir solo "es infactible" no basta: hay que mostrar el uso de cada recurso y explicar por qué pasa.</div>
</section>'''


def s9():
    base = LOT[LOT.Escenario == "Base"].reset_index(drop=True)
    filas = []
    for k in range(5):
        e, m_ = EOQ.iloc[k], base.iloc[k]
        filas.append([NOMBRES[k], n(e.Q), n(m_.Q), n(100 * (m_.Q / e.Q - 1), 1) + " %", n(e.N, 1), n(m_.N, 1), n(m_.T_dias, 1),
                      n(m_.Espacio, 1), mm(m_.Capital, 1)])
    filas.append(["<b>Total</b>", "", "", "", n(EOQ.N.sum(), 1), n(base.N.sum(), 1), "", "<b>90,0</b>", "<b>110,0</b>"])
    t = tabla(["Componente", "Q EOQ", "Q multi", "Cambio", "N EOQ", "N multi", "T multi (días)", "Espacio (m³)", "Capital (MM$)"], filas,
              num=tuple(range(1, 9)), tot=(5,), cap="Tabla 9.1 · EOQ individual vs multiproducto")
    tc = tabla(["", "EOQ individual (infactible)", "Multiproducto", "Cambio"], [
        ["Costo de ordenar", mm(EOQ.C_ordenar.sum()), mm(base.C_ordenar.sum()), "+" + mm(base.C_ordenar.sum() - EOQ.C_ordenar.sum())],
        ["Costo de mantener", mm(EOQ.C_mantener.sum()), mm(base.C_mantener.sum()), mm(base.C_mantener.sum() - EOQ.C_mantener.sum())],
        ["<b>Costo relevante (MM$/año)</b>", mm(EOQ.C_relevante.sum()), f"<b>{mm(base.C_relevante.sum())}</b>", "+" + mm(base.C_relevante.sum() - EOQ.C_relevante.sum()) + " (+2,1 %)"],
        ["Pedidos al año", n(EOQ.N.sum(), 1), n(base.N.sum(), 1), "+" + n(base.N.sum() - EOQ.N.sum(), 1)]],
        num=(1, 2, 3), cap="Tabla 9.2 · Qué cambia en los costos y la frecuencia")
    return f'''<section class="sol parte-3">
{cabecera("S9", "Formular e implementar un EOQ multiproducto restringido", "Parte III · Inventarios determinísticos", "Dimensión 6 · 20 %", ref("Solicitud 9", "hojas EOQ_Multiproducto, Resumen_Multiproducto", "parte3_inventarios.py (multiproducto, verificar_slsqp) · ModeloE_Sol9_EOQ_multiproducto.txt", "7"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p><q>Formule e implemente un modelo de optimización que determine simultáneamente los tamaños de lote de los cinco componentes, minimizando el costo relevante anual de inventarios y respetando las restricciones de espacio y capital disponible.</q> Debe: (a) definir las variables; (b) formular y explicar la función objetivo; (c) formular y explicar las restricciones; (d) <q>justificar por qué el costo anual de compra … no modifica la elección de los tamaños de lote</q>; (e) implementar y resolver; (f) comparar con los EOQ individuales; (g) analizar cambios en lotes, frecuencia y costos; (h) <q>explicar qué significa que una restricción se encuentre activa en la solución óptima</q>.</p>''')}
<p class="simple">En simple: elegir los cinco lotes al mismo tiempo, lo más parecidos posible a los EOQ, pero que quepan en 90 m³ y 110 MM$.</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("(a) Variables", "Qᵢ &gt; 0: unidades por pedido de cada componente (5 variables continuas).", "Cómo"),
        ("(b) Función objetivo", "Costo anual de ordenar + mantener de los cinco: Σ(DᵢSᵢ/Qᵢ + hᵢQᵢ/2).", "Cómo"),
        ("(c) Restricciones", "Espacio Σ vᵢQᵢ ≤ 90 y capital Σ cᵢQᵢ ≤ 110 MM$ (lotes completos, igual que en S8).", "Cómo"),
        ("(d) Por qué no va el costo de compra", "Σ Dᵢcᵢ = 2.784 MM$/año es igual para cualquier Q: se compra lo mismo al año. Solo importaría con descuentos por cantidad.", "Cómo"),
        ("(e) Implementar y resolver", "Multiplicadores de Lagrange (condiciones KKT) resueltos por bisección; verificado con un optimizador no lineal (SLSQP): mismo costo, 34.503.017.", "Cómo"),
        ("(f) Comparar con EOQ", "Lotes 18–21 % menores; costo +0,72 MM$/año (+2,1 %).", "Tabla 9.1"),
        ("(g) Lotes, frecuencia y costos", "94,2 → 115,9 pedidos/año; ordenar 16,89 → 20,75; mantener 16,89 → 13,75.", "Tabla 9.2"),
        ("(h) Qué es una restricción activa", "Se usa completa en el óptimo (90,0 m³ y 110,0 MM$). Las dos lo están, con μ = 5.098 y λ = 0,0595.", "Por qué")])}
{lbl(3, "Cómo lo hicimos")}
<div class="formula">min Σᵢ ( Dᵢ·Sᵢ/Qᵢ + hᵢ·Qᵢ/2 ) &nbsp;&nbsp; s.a. &nbsp; Σᵢ vᵢ·Qᵢ ≤ 90 &nbsp;(μ) &nbsp;&nbsp; Σᵢ cᵢ·Qᵢ ≤ 110.000.000 &nbsp;(λ) &nbsp;&nbsp; Qᵢ &gt; 0<br>
Lagrange: derivar y despejar &nbsp;⇒&nbsp; Qᵢ = √( 2·Dᵢ·Sᵢ / (hᵢ + 2μ·vᵢ + 2λ·cᵢ) )</div>
<p>La fórmula es la del EOQ con un <b>costo de mantener aumentado</b>: cada recurso escaso suma un recargo (2μvᵢ por espacio y 2λcᵢ por capital). Buscamos μ y λ ≥ 0 tales que se cumplan las restricciones y, si una no está llena, su multiplicador sea 0. El problema es convexo, así que el resultado es el óptimo global.</p>
<div class="ej"><div class="ej-t">Ejemplo calculado a mano: hélice–rejilla con μ = 5.098 y λ = 0,0595</div>
<p>h aumentado = 1.125 + 2 × 5.098 × 0,015 + 2 × 0,0595 × 4.500 = 1.125 + 153 + 535 = <b>1.813</b> (+61 %). Q = √(2 × 120.000 × 150.000 / 1.813) = <b>4.456</b> (−21 % frente a 5.657). El motor estándar tiene un recargo de +49 %, por eso baja menos (−18 %).</p></div>
{lbl(4, "Resultados · 34,50 MM$/año")}
{t}
{tc}
<figure>{svg_eoq()}<figcaption>Figura 9.1 · Costo anual del motor estándar según su lote. La curva es plana cerca del óptimo: achicar el lote 18 % lo encarece solo 2 %.</figcaption></figure>
{lbl(5, "Por qué")}
<div class="why"><p><b>Lotes más chicos ⇒ más pedidos ⇒ más costo de ordenar y menos de mantener.</b> El costo total sube poco porque la curva de costo es plana cerca del EOQ. Los lotes no bajan todos igual: baja más el que más consume del recurso escaso en relación con su h (la hélice, por espacio).</p>
<p><b>Restricción activa:</b> en el óptimo se usa completa (holgura cero). Su <b>multiplicador</b> es cuánto bajaría el costo con una unidad más de recurso: <b>μ = 5.098 $/m³-año</b> y <b>λ = 0,0595 $ por $ al año</b> (6 centavos por cada peso más de presupuesto). Si no estuviera activa, su multiplicador sería 0. Los puntos de reorden no cambian (ROP = d·L no depende de Q) porque T sigue mayor que L (hélice: 8,9 &gt; 8 días).</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Por qué no basta achicar todos los EOQ en la misma proporción?", "Con un factor de 0,796 se cumple la bodega, pero cuesta 34,67 MM$ (163 mil más que el óptimo): espacio y capital pesan distinto en cada componente."),
        ("¿Cómo saben que es el óptimo global?", "La función es convexa (DS/Q es convexa y hQ/2 es lineal) y las restricciones son lineales: si se cumplen las condiciones KKT, es el óptimo global. SLSQP da lo mismo."),
        ("¿Por qué no incluir el costo de compra?", "Es una constante (2.784 MM$/año): no cambia con Q, así que no cambia qué Q es mejor. Con descuentos por cantidad sí habría que incluirlo."),
        ("¿Qué significa λ = 0,0595?", "Un peso más de presupuesto en lotes ahorraría ≈6 centavos al año. Es una tasa marginal: vale para cambios pequeños."),
        ("¿Cambian los puntos de reorden?", "No: ROP = d·L no depende del lote, mientras el ciclo T siga siendo mayor que el plazo L."),
        ("¿Qué pasa si sacamos la restricción de capital?", "Solo limita el espacio: 34.089.228 $/año, pero usaría 125,1 MM$ de capital.")])}
<div class="trap"><b>Cuidado:</b> el multiplicador no es un "precio fijo" del recurso. Es una pendiente local que cambia apenas se relaja la restricción (ver S10).</div>
</section>'''


def s10():
    sc = ["Base", "+10% espacio", "+10% presupuesto"]
    L = {s: LOT[LOT.Escenario == s].reset_index(drop=True) for s in sc}
    filas = []
    for k in range(5):
        qb = L["Base"].Q[k]
        filas.append([NOMBRES[k], n(qb), n(L["+10% espacio"].Q[k]), n(100 * (L["+10% espacio"].Q[k] / qb - 1), 1) + " %",
                      n(L["+10% presupuesto"].Q[k]), n(100 * (L["+10% presupuesto"].Q[k] / qb - 1), 1) + " %"])
    tl = tabla(["Componente", "Q base", "Q +10 % espacio", "Cambio", "Q +10 % presupuesto", "Cambio"], filas,
               num=(1, 2, 3, 4, 5), cap="Tabla 10.1 · Efecto sobre los tamaños de lote")
    fr = []
    for s, etq in zip(sc, ["Base (90 m³; 110 MM$)", "a) +10 % espacio (99 m³)", "b) +10 % presupuesto (121 MM$)"]):
        r = MUL.loc[s]
        act = "ambas" if r.Espacio_activa and r.Capital_activa else ("solo capital" if r.Capital_activa else "solo espacio")
        ahorro = MUL.loc["Base"].Costo_relevante - r.Costo_relevante
        fr.append([etq, f"{n(r.Espacio_usado, 2)} de {n(r.V)}", f"{mm(r.Capital_usado, 1)} de {mm(r.K, 0)}", act, n(r.mu), n(r.lam, 4),
                   n(r.Costo_relevante), n(r.Pedidos_totales, 1), "—" if s == "Base" else f"<b>{n(ahorro)}</b>"])
    tr = tabla(["Escenario", "Espacio usado (m³)", "Capital usado (MM$)", "Activas", "μ", "λ", "Costo $/año", "Pedidos", "Ahorro $/año"], fr,
               num=(4, 5, 6, 7, 8), rec=(2,), cap="Tabla 10.2 · Los tres escenarios")
    return f'''<section class="sol parte-3">
{cabecera("S10", "Análisis de sensibilidad y recomendación", "Parte III · Inventarios determinísticos", "Dimensión 6 · 20 %", ref("Solicitud 10", "hoja Resumen_Multiproducto", "parte3_inventarios.py (tabla_multiproducto)", "7"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p>Dos alternativas: <b>a)</b> aumentar 10 % el espacio manteniendo el presupuesto; <b>b)</b> aumentar 10 % el presupuesto manteniendo el espacio. <q>Resuelva nuevamente el modelo bajo cada escenario y compare sus resultados con la situación actual.</q> Analizar como mínimo: efecto sobre los lotes; utilización de espacio y presupuesto; costo relevante anual; qué restricciones siguen activas y cuáles no; cuál alternativa genera más valor. <q>En particular, discuta por qué el hecho de que dos restricciones sean activas en la solución original no implica que relajarlas genere necesariamente el mismo beneficio económico.</q></p>''')}
<p class="simple">En simple: si la Gerencia pudiera agrandar un solo recurso, ¿cuál le conviene?</p>
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("Resolver cada escenario", "Mismo modelo de S9 con V = 99 m³ o K = 121 MM$.", "Tabla 10.2"),
        ("Efecto sobre los lotes", "a) casi no cambian (hélice +3 %, resto −1 %). b) suben 13–14 % todos menos la hélice, que baja 4,5 %.", "Tabla 10.1"),
        ("Utilización de espacio y presupuesto", "a) usa solo 92,07 de 99 m³ y todo el capital. b) usa todo: 90 m³ y 121 MM$.", "Tabla 10.2"),
        ("Costo relevante", "Base 34.503.017 · a) 34.497.798 (−5.219) · b) 34.116.426 (<b>−386.591</b>).", "Tabla 10.2"),
        ("Qué restricciones siguen activas", "a) el espacio deja de ser activa (μ = 0); queda solo el capital. b) siguen ambas (μ sube a 24.785, λ baja a 0,0135).", "Tabla 10.2"),
        ("Cuál genera más valor", "<b>El presupuesto</b>: ahorra 74 veces más.", "Recomendación"),
        ("Por qué dos activas no valen lo mismo", "El multiplicador es una pendiente local. Con más bodega, el capital pasa a limitar casi de inmediato; el capital extra, en cambio, se usa completo.", "Por qué")])}
{lbl(3, "Cómo lo hicimos")}
<p>Se resolvió el mismo modelo dos veces más cambiando solo V o K. Además se recorrió cada recurso desde su valor actual hasta +11 % para ver dónde se "satura" (Figura 10.1).</p>
<div class="ej"><div class="ej-t">Estimación con los multiplicadores vs resultado real</div>
<p>Espacio: μ × 9 m³ = 5.098 × 9 = 45.881, pero el ahorro real es solo <b>5.219</b> (9 veces menos). Capital: λ × 11 MM$ = 0,0595 × 11.000.000 = 654.421, real <b>386.591</b>. Los multiplicadores sirven para cambios chicos; para cambios grandes hay que volver a resolver.</p></div>
{lbl(4, "Resultados")}
{tr}
{tl}
<figure>{svg_valor()}<figcaption>Figura 10.1 · Ahorro anual al ampliar cada recurso, en la misma escala vertical. La bodega deja de servir en 92,07 m³ (de los 9 m³ nuevos solo se usan 2,07). El presupuesto se aprovecha completo hasta ≈125 MM$.</figcaption></figure>
{lbl(5, "Por qué")}
<div class="why"><p><b>Activa no implica valiosa.</b> Las dos restricciones están llenas en la base, pero eso solo dice que relajarlas un poco ayuda. Cuando se agrega espacio, los lotes crecen hasta que el <b>capital</b> se llena (con solo 2,07 m³ extra): desde ahí, más bodega no sirve, y el ahorro máximo posible es 5.219 $/año. Cuando se agrega presupuesto, los motores (caros y chicos) pueden crecer y la hélice cede espacio: el capital extra se usa entero y el ahorro sigue creciendo hasta ≈125 MM$ (máximo 413.790 $/año; el +10 % ya captura el 93 %).</p></div>
<div class="reco"><div class="reco-t">Nuestra recomendación</div>
<p><b>Si la Gerencia puede flexibilizar un recurso, que sea el presupuesto (+10 %): ahorra 386.591 $/año contra 5.219 de la bodega.</b> Ampliar la bodega no vale la pena. El ahorro es una rentabilidad media de 3,5 % sobre los 11 MM$ extra (la marginal parte en 5,95 % y cae a 1,35 %); como h ya incluye el costo de capital, es un beneficio neto.</p></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Y si se amplían ambos recursos 10 %?", "Se ahorran 511.638, más que la suma por separado (391.810): los recursos se complementan."),
        ("¿Hasta dónde conviene ampliar el presupuesto?", "Hasta ≈125,1 MM$: desde ahí el capital deja de estar activo y solo limita el espacio."),
        ("¿Por qué la hélice baja con más presupuesto?", "La bodega sigue llena: para que los motores crezcan, la hélice (la que más espacio usa) cede lugar."),
        ("¿Por qué μ sube de 5.098 a 24.785 en el escenario b?", "Porque con más capital el espacio pasa a ser el recurso que más aprieta: una unidad más de bodega ahora vale mucho más.")])}
<div class="trap"><b>Cuidado:</b> "las dos están activas, así que da lo mismo cuál relajar" es exactamente el error que la rúbrica busca. Diferencia restricción activa de su valor económico marginal.</div>
</section>'''


def final():
    return f'''<section class="sol parte-x">
{cabecera("F", "Recomendación final del proyecto", "Integración", "Dimensión 7 · 10 %", ref("Recomendación final integrada", "Leeme", "run_all.py", "8"))}
{lbl(1, "Lo que pide el enunciado")}
{pide('''<p><q>Una síntesis integrada de las principales conclusiones obtenidas en ambas áreas de decisión.</q> <q>Se espera que el equipo conecte los resultados de planificación agregada con las decisiones de abastecimiento e inventario, identifique los principales trade-offs observados y formule recomendaciones comprensibles para una audiencia gerencial.</q> No repetir las respuestas de cada solicitud: elegir lo más relevante y decir qué debe hacer Ventisur y por qué.</p>''')}
{lbl(2, "Respuesta punto por punto")}
{punto_por_punto([
        ("Conectar planificación con abastecimiento", "La Parte I fija cuánto se produce; eso define el consumo de piezas (Parte II) y por lo tanto los lotes y ROP (Parte III). Ojo con el desfase del peak (abajo).", "Las 4 recomendaciones"),
        ("Trade-offs principales", "Costo vs servicio; costo vs holgura ante errores; tamaño de lote vs recursos; espacio vs capital.", "Tabla F.1"),
        ("Recomendaciones para la Gerencia", "Cuatro decisiones concretas.", "Las 4 recomendaciones")])}
{lbl(3, "Las 4 recomendaciones (dilas en este orden)")}
<ol class="big">
<li><b>Producción:</b> adoptar la Sol. 5: 18 trabajadores, HE en septiembre–febrero y cero pendientes (301,10 MM$, 13,9 MM$ menos que la mejor política simple). Si se desconfía del pronóstico, mantener 19 trabajadores como seguro (+1,4 MM$).</li>
<li><b>Coherencia entre las partes:</b> las compras usan la tasa estable de 10.000 u/mes, pero el plan recomendado produce 11.700 en nov–dic. La demanda anual Dᵢ no cambia (todo plan produce 120.000), pero en el peak el consumo diario sube 17 % y el ROP debería subir a 2.808 · 1.170 · 4.680 · 2.925 · 1.404. Si no se ajusta, la hélice queda corta en ≈680 u durante cada plazo de entrega del peak.</li>
<li><b>Compras:</b> usar los lotes multiproducto con sus ROP, no los EOQ individuales (que no caben). Cumplir los límites cuesta solo 0,72 MM$/año, frente a 2.784 MM$/año de compras.</li>
<li><b>Inversión:</b> si se puede ampliar un recurso, que sea el presupuesto de lotes, no la bodega.</li></ol>
{tabla(["Trade-off", "Lo que se gana", "Lo que se paga", "Nuestra decisión"], [
        ["Servicio vs costo", "100 % a tiempo, sin riesgo de multa", "+350.000 frente a A", "Servicio completo (Sol. 5)"],
        ["Costo vs holgura", "Plan más barato (18 trabajadores)", "HE al 100 % en nov–dic", "18, con opción de 19 como seguro"],
        ["Lotes vs recursos", "Cumplir 90 m³ y 110 MM$", "+0,72 MM$/año y 22 pedidos más", "Lotes multiproducto"],
        ["Espacio vs capital", "Ahorro de 386.591 $/año", "11 MM$ más en lotes", "Ampliar el presupuesto"]],
        cap="Tabla F.1 · Los trade-offs del proyecto")}
{lbl(5, "Supuestos y limitaciones (dilos antes de que te los pregunten)")}
<div class="dos small"><div><ul><li>Demanda y plazos determinísticos: sin stock de seguridad.</li><li>Unidad agregada homogénea: cualquier ventilador usa la misma capacidad.</li><li>Productividad y costos constantes todo el año.</li></ul></div>
<div><ul><li>Espacio y capital medidos para todos los lotes completos a la vez: con llegadas escalonadas se necesitaría menos.</li><li>El EOQ supone consumo uniforme, pero el plan agregado no es plano (punto 2).</li><li>La recomendación de la Parte I depende del pronóstico de diciembre.</li></ul></div></div>
{lbl(6, "Si te preguntan")}
{qa([
        ("¿Qué decisión responde cada modelo?", "A–C y Sol. 5: con cuánta gente y cuánto producir cada mes. Desagregación: cuánto se consume. EOQ: cuánto pedir; ROP: cuándo. Multiproducto: cuánto pedir cuando los lotes compiten por bodega y capital."),
        ("¿Cómo usaron y verificaron la IA?", "Para programar, revisar y redactar. Verificamos: costos recalculados fuera de los modelos, Excel con fórmulas y celda de chequeos, óptimo único en A, M ajustada en B, multiproducto resuelto de dos formas (KKT y SLSQP) y dos revisiones independientes de todas las cifras.")])}
</section>'''


def anexos():
    filas = [
        ["Quitar el límite de ±3 contrataciones/despidos", "No estaba activo: nada cambia", "300,75"],
        ["Bodega de 2.000 u", "El óptimo guarda máximo 1.000: nada cambia", "300,75"],
        ["Mantener inventario cuesta $500", "Adelanta más producción (5.000 u-mes)", "299,10"],
        ["Atrasar cuesta $250", "Mismo plan, más barato", "300,45"],
        ["Atrasar cuesta $1.500", "Igual atrasa 200 u (adelantar sale más caro)", "301,00"],
        ["HE cuesta $3.000 (Sol. 5)", "19 trabajadores desde septiembre", "307,05"],
        ["HE rinde 100 u/trabajador-mes", "Contrata 2 en septiembre (20)", "304,48"],
        ["Sin horas extra", "Sube a 20–23 trabajadores en el peak", "312,90"],
        ["Despedir es gratis", "17 trabajadores mar–jun, 18 desde julio", "293,95"],
        ["Despedir cuesta el doble (Sol. 5)", "Mantiene 19 todo el año (despide 1)", "305,50"],
        ["Inventario final 0 / 2.000 (Modelo A)", "Menos / más producción al final", "297,15 / 305,66"],
        ["HE limitada al 80 % (Sol. 5)", "Contrata 1 en septiembre (19)", "303,06"],
        ["Multa menor a $151.250", "B prefiere pagar una multa en diciembre", "—"],
        ["Umbral de la multa 3,2 % / 0 %", "B se vuelve A / se vuelve C", "300,75 / 301,10"],
        ["Demanda de diciembre +5 % / +10 % (conocida)", "Sigue con 18 y más HE", "303,91 / 306,90"],
        ["Mezcla 40–30–30", "Motor est. 7.000, prem. 3.000, módulo 6.000, control 3.000 u/mes", "—"],
        ["Demanda de un componente × 2", "Q* × 1,41 y ROP × 2", "—"],
        ["Tiempo de entrega mayor", "Sube el ROP; Q* no cambia", "—"],
        ["Tasa de mantención 20 % / 30 %", "EOQ siguen sin caber (126,5 m³ / 103,2 m³)", "—"],
        ["Solo restricción de espacio", "Usaría 125,1 MM$ de capital", "34.089.228 $/año"],
        ["Solo restricción de capital", "Usaría 92,07 m³", "34.497.798 $/año"],
        ["+10 % en ambos recursos", "Se complementan", "ahorro 511.638"],
    ]
    q = tabla(["Si cambia…", "Qué pasa", "Resultado"], filas, num=(2,), clase="compact",
              cap="Parte I en MM$ (salvo indicación); Parte III en $/año.")
    guion = tabla(["Diap.", "Tiempo", "Mensaje que no puede faltar", "Solicitud"], [
        ["1 Portada", "0:15", "Planificamos 12 meses de producción y cómo comprar 5 componentes.", "—"],
        ["2 Políticas simples", "0:35", "Mismo costo laboral; cambia el amortiguador. P2 gana (315,0).", "S1"],
        ["3 Modelo A", "0:50", "18 trabajadores, HE en el peak, adelanta 1–2 meses y atrasa porque atrasar &lt; guardar. 300,75.", "S2"],
        ["4 B, C y servicio", "0:45", "Binaria con M; servicio completo cuesta 350.000.", "S3, S4"],
        ["5 Recomendación", "0:30", "Sol. 5 con 18; seguro de 19 si hay incertidumbre.", "S5"],
        ["6 Componentes y EOQ", "0:35", "Tasas constantes → EOQ; no caben (113 m³, 135 MM$).", "S6–S8"],
        ["7 Multiproducto", "0:40", "Ambas activas, pero el presupuesto vale 74 veces más.", "S9, S10"],
        ["8 Integración", "0:30", "Las 4 recomendaciones.", "Final"]], clase="compact")
    archivos = tabla(["Archivo", "Qué contiene"], [
        ["Informe_Ventisur.pdf", "Informe de 6 páginas + portada (respaldo de todo lo de esta guía)"],
        ["Resultados_Ventisur.xlsx", "15 hojas: parámetros, P1–P3, ModA–ModD, comparación, sensibilidad, desagregación, EOQ y multiproducto, con fórmulas"],
        ["01_codigo/run_all.py", "Regenera todo: políticas, modelos, sensibilidad, Parte II y III, Excel y figuras"],
        ["02_resultados/modelos_lp/", "Modelos A, B, C, D exportados (.lp) y el multiproducto (.txt)"],
        ["02_resultados/csv/ y resumen.json", "Todos los resultados numéricos (de ahí salen las tablas de esta guía)"]], clase="compact")
    return f'''<section class="salto">
<div class="eyebrow">Anexo A · Consulta rápida</div>
<h2 class="pt">¿Qué pasa si…?</h2>
<p class="small muted">Todas estas variantes se resolvieron con el código del proyecto (parte1_sensibilidad.py y parte3_inventarios.py).</p>
{q}
</section>
<section class="salto">
<div class="eyebrow">Anexo B · Presentación de 5 minutos</div>
<h2 class="pt">Guion y archivos de respaldo</h2>
{guion}
<p class="small muted">Total 4:40, con 20 s de margen. Sugerencia: cada integrante presenta dos diapositivas, pero todos estudian todo.</p>
<div class="dos" style="margin-top:8px">
<div class="trap"><b>Frases que restan puntos:</b> "el solver lo eligió", "la IA lo calculó", "las dos restricciones valen lo mismo", "agregamos stock de seguridad", "la Parte II nos dice cuánto pedir".</div>
<div class="why"><b>Frases que suman:</b> "porque atrasar cuesta menos que guardar", "la binaria activa la multa solo si se pasa del 1 %", "Q* dice cuánto y el ROP dice cuándo", "activa no implica valiosa".</div></div>
<div class="lbl0" style="margin-top:12px">Dónde está cada cosa</div>
{archivos}
</section>'''


CSS = r"""
@page { size: Letter; margin: 12mm 13mm 14mm 13mm; }
:root{
  --ink:#1b2129; --muted:#5b6672; --line:#d9dee5; --soft:#f3f5f8; --surface:#fff;
  --p1:#1f5fae; --p1s:#e9f1fb; --p2:#2e7d4f; --p2s:#e8f4ed; --p3:#6d4bb3; --p3s:#f0ebf9; --px:#2b333c; --pxs:#eef0f3;
  --pide:#faf3e3; --pide-bd:#c48a1c; --ok:#2e7d4f; --warn:#b45309; --warn-s:#fdf1e4; --bad:#b42318; --accent:#1f5fae;
  --s-p1:#d9a336; --s-p2:#cc5f22; --s-p3:#8c3b2f; --s-a:#2b333c;
}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font:9.2pt/1.42 "IBM Plex Sans",system-ui,sans-serif;color:var(--ink);background:#fff}
h1,h2,h3,h4{margin:0;line-height:1.15}
h2.pt{font:600 17pt/1.15 "Newsreader",Georgia,serif;margin:2px 0 8px}
h3.h3{font:700 10pt/1.2 "IBM Plex Sans";margin:6px 0 4px}
p{margin:3px 0}
ul,ol{margin:3px 0;padding-left:16px}
li{margin:1.5px 0}
q{quotes:"“" "”";font-style:italic}
.small{font-size:8.4pt} .muted{color:var(--muted)}
.f{font-family:"IBM Plex Mono",monospace;font-size:8.4pt;background:var(--soft);border-radius:4px;padding:0 4px;white-space:nowrap}
.salto{break-before:page}
.eyebrow{font:700 7.4pt/1 "IBM Plex Sans";letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}
.lbl0{font:700 7.6pt/1 "IBM Plex Sans";letter-spacing:.07em;text-transform:uppercase;color:var(--muted);margin:6px 0 4px}
/* portada */
.portada h1{font:600 30pt/1.05 "Newsreader",Georgia,serif;margin:10px 0 6px}
.portada h1 span{font-size:20pt;color:var(--p1)}
.portada .sub{font-size:11pt;color:var(--muted);margin:2px 0 6px}
.portada .autores{font-weight:600;margin:4px 0 12px}
.dos{display:grid;grid-template-columns:1fr 1fr;gap:12px;align-items:start}
.box{border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.box h3{font:700 10.5pt/1.2 "IBM Plex Sans";margin-bottom:6px}
.cifras{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.cf{background:var(--soft);border-radius:7px;padding:6px 8px;display:grid;gap:1px}
.cf b{font:600 9.6pt/1.2 "IBM Plex Mono",monospace}
.cf span{font-size:7.6pt;color:var(--muted);line-height:1.25}
ol.leyenda{list-style:none;padding:0;margin:0 0 6px}
ol.leyenda li{display:grid;grid-template-columns:20px 1fr;gap:6px;align-items:start;margin:4px 0}
ol.leyenda .i,.lbl .i{display:inline-grid;place-items:center;width:17px;height:17px;border-radius:50%;color:#fff;font:700 8pt/1 "IBM Plex Sans"}
/* encabezado de solicitud */
section.sol{break-before:page;--c:var(--p1);--cs:var(--p1s)}
section.parte-2{--c:var(--p2);--cs:var(--p2s)} section.parte-3{--c:var(--p3);--cs:var(--p3s)} section.parte-x{--c:var(--px);--cs:var(--pxs)}
.head{display:grid;grid-template-columns:58px 1fr;gap:12px;align-items:center;border-bottom:2.5px solid var(--c);padding-bottom:7px;margin-bottom:6px}
.head .num{background:var(--c);color:#fff;font:600 21pt/1 "Newsreader",serif;border-radius:9px;height:58px;display:grid;place-items:center}
.head .kicker{font:700 7.4pt/1 "IBM Plex Sans";letter-spacing:.08em;text-transform:uppercase;color:var(--c)}
.head h2{font:600 16.5pt/1.12 "Newsreader",Georgia,serif;margin:3px 0 3px}
.head .meta{font-size:7.6pt;color:var(--muted)}
.lbl{display:flex;align-items:center;gap:6px;font:700 7.6pt/1 "IBM Plex Sans";letter-spacing:.07em;text-transform:uppercase;color:var(--c);margin:10px 0 4px;break-after:avoid}
.lbl .i{background:var(--c)}
.pide{background:var(--pide);border-left:4px solid var(--pide-bd);border-radius:6px;padding:7px 11px;break-inside:avoid}
.pide-t{display:none}
.simple{font-weight:600;margin:6px 0 2px;padding-left:2px}
.simple::before{content:"→ ";color:var(--c)}
/* tablas */
table{width:100%;border-collapse:collapse;font-size:8.1pt;margin:4px 0 6px}
tr{break-inside:avoid}
caption{break-after:avoid}
caption{caption-side:top;text-align:left;font:700 7.8pt/1.3 "IBM Plex Sans";color:var(--muted);padding-bottom:3px}
th{font-weight:700;text-align:left;border-bottom:1.4px solid var(--ink);padding:3px 4px;vertical-align:bottom}
td{border-bottom:1px solid var(--line);padding:2.6px 4px;vertical-align:top}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
td.n{font-family:"IBM Plex Mono",monospace;font-size:7.7pt;white-space:nowrap}
td.c{text-align:center}
tr.tot td{border-top:1.4px solid var(--ink);font-weight:700}
tr.rec td{background:var(--cs,#e9f1fb)}
table.compact{font-size:7.8pt} table.compact td,table.compact th{padding:2px 4px}
table.meses td:first-child{white-space:nowrap;font-weight:600}
table.pp{font-size:8.2pt}
table.pp th{background:var(--soft)}
table.pp td{padding:3.4px 5px}
table.pp .pp-q{width:31%;font-weight:600}
table.pp .pp-v{width:13%;color:var(--muted);font-size:7.6pt}
.ck{display:inline-grid;place-items:center;width:13px;height:13px;border-radius:50%;background:var(--ok);color:#fff;font-size:7.5pt;margin-right:5px;vertical-align:-1px}
table.mapa-t{font-size:8pt}
table.mapa-t td{padding:4px 5px}
table.mapa-t .sid{font:700 9pt/1 "Newsreader",serif;white-space:nowrap}
table.mapa-t tr:nth-child(-n+5) .sid{color:var(--p1)} table.mapa-t tr:nth-child(6) .sid{color:var(--p2)}
table.mapa-t tr:nth-child(n+7) .sid{color:var(--p3)} table.mapa-t tr:nth-child(11) .sid{color:var(--px)}
/* bloques */
.formula{font-family:"IBM Plex Mono",monospace;font-size:8.1pt;line-height:1.65;background:var(--soft);border-radius:6px;padding:6px 10px;margin:4px 0;break-inside:avoid}
.ej{border:1.3px dashed var(--c);border-radius:8px;padding:6px 11px;margin:6px 0;break-inside:avoid}
.ej-t{font:700 7.4pt/1 "IBM Plex Sans";letter-spacing:.07em;text-transform:uppercase;color:var(--c);margin-bottom:3px}
.why{background:var(--cs,#e9f1fb);border-radius:8px;padding:7px 11px;break-inside:avoid}
.cards3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.cards3 .why{font-size:8.3pt}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px}
.card{border:1px solid var(--line);border-radius:9px;padding:8px 11px;break-inside:avoid}
.card h4{font:700 9.4pt/1.25 "IBM Plex Sans";margin-bottom:3px}
.reco{border:2px solid var(--c);border-radius:10px;padding:8px 12px;margin:8px 0;break-inside:avoid}
.reco-t{font:700 7.6pt/1 "IBM Plex Sans";letter-spacing:.07em;text-transform:uppercase;color:var(--c);margin-bottom:4px}
.trap{background:var(--warn-s);border-left:4px solid var(--warn);border-radius:6px;padding:6px 11px;margin-top:8px;break-inside:avoid}
.trap b:first-child{color:var(--warn)}
.qa-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px 14px}
.qa{border-top:1px solid var(--line);padding-top:4px;break-inside:avoid}
.qa .q{font-weight:700;font-size:8.6pt}
.qa .a{font-size:8.4pt}
ol.big li{margin:4px 0}
figure{margin:6px 0;break-inside:avoid}
figure svg,figure img{width:100%;height:auto;display:block}
figure.mapa svg{max-height:120px}
figcaption{font-size:7.7pt;color:var(--muted);margin-top:3px}
svg{color:var(--ink);font-family:"IBM Plex Sans",sans-serif}
svg .grid{stroke:var(--line);stroke-width:1}
svg .t-s{font-size:11px;fill:var(--muted)} svg .t-m{font-size:12.5px;fill:var(--ink)} svg .t-b{font-weight:700;fill:var(--ink)}
"""


def documento(pags):
    cuerpo = "\n".join([portada(), mapa(pags), datos(), ideas(), s1(), s2(), s3(), s4(), s5(), s6(), s7(), s8(), s9(), s10(), final(), anexos()])
    cuerpo = (cuerpo.replace("__FIG1__", img("fig1_planes.png")).replace("__FIG2__", img("fig2_costos.png")))
    return f'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>Defensa Ventisur · guía de estudio</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,400;0,600;0,700;1,400&family=Newsreader:opsz,wght@6..72,500;6..72,600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{cuerpo}</body></html>'''


TITULOS = {"S1": "Construir y comparar políticas simples", "S2": "Formular e implementar un modelo de optimización",
           "S3": "Incorporar una condición contractual de servicio", "S4": "Política de cero pedidos pendientes",
           "S5": "Recomendación de planificación agregada", "S6": "Desagregar la producción y determinar requerimientos",
           "S7": "Políticas EOQ individuales", "S8": "Evaluar la factibilidad conjunta de los EOQ",
           "S9": "Formular e implementar un EOQ multiproducto", "S10": "Análisis de sensibilidad y recomendación",
           "Final": "Recomendación final del proyecto"}


def a_pdf(html_path, pdf_path):
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto({json.dumps(html_path.as_uri())}, {{waitUntil: 'networkidle'}});
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({{path: {json.dumps(str(pdf_path))}, format: 'Letter', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-family:Helvetica,Arial,sans-serif;font-size:7pt;width:100%;padding:0 13mm;display:flex;justify-content:space-between;color:#7a838d"><span>Proyecto Ventisur · Guía de estudio para la defensa · Sección 2</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'}});
  await b.close();
}})();
"""
    subprocess.run(["node", "-e", js], check=True, timeout=240)


def paginas(pdf_path):
    txt = subprocess.run(["pdftotext", "-layout", str(pdf_path), "-"], capture_output=True, text=True, check=True).stdout
    pags = {}
    for i, pg in enumerate(txt.split("\f"), start=1):
        plano = re.sub(r"\s+", " ", pg)
        for k, t in TITULOS.items():
            if k not in pags and t in plano and "LO QUE PIDE" not in plano[:0]:
                # el título debe aparecer en el encabezado (no en el mapa, que usa preguntas)
                pags[k] = str(i)
    return pags


def main():
    html = AQUI / "Defensa_Ventisur_estudio.html"
    pdf = AQUI / "Defensa_Ventisur_estudio.pdf"
    html.write_text(documento({}), encoding="utf-8")
    a_pdf(html, pdf)
    pags = paginas(pdf)
    html.write_text(documento(pags), encoding="utf-8")
    a_pdf(html, pdf)
    print(pdf, pags)


if __name__ == "__main__":
    main()
