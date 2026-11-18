"""Genera la guía de estudio de la defensa (Defensa_Ventisur.html y Defensa_Ventisur.pdf).

Uso:  cd proyecto/04_presentacion && python3 construir_guia_defensa.py
Las curvas de los diagramas se calculan con el código del proyecto (no hay cifras dibujadas a mano).
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "01_codigo"))
FIG = AQUI.parent / "02_resultados" / "figuras"

import numpy as np  # noqa: E402

import parte3_inventarios as p3  # noqa: E402
from datos import cargar  # noqa: E402


def miles(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ------------------------------------------------------------------ datos para los diagramas
_, _, INV = cargar()
_P = np.array([[c["D"], c["S"], c["c"], c["v"]] for c in INV["comp"].values()], float)
_H = np.array([c["i"] * c["c"] for c in INV["comp"].values()])


def _costo(Q):
    return float(np.sum(_P[:, 0] * _P[:, 1] / Q + _H * Q / 2))


_BASE = _costo(p3.multiproducto(INV, 90, 110e6)[0])
CURVA_ESP = [(V, _BASE - _costo(p3.multiproducto(INV, V, 110e6)[0])) for V in np.arange(90, 100.01, 0.25)]
CURVA_CAP = [(K / 1e6, _BASE - _costo(p3.multiproducto(INV, 90, K)[0])) for K in np.arange(110e6, 130.01e6, 0.5e6)]


def svg_valor():
    """Dos paneles con la MISMA escala vertical: ahorro anual al relajar espacio vs presupuesto."""
    W, H, top, bot = 380, 250, 34, 200
    ymax = 450_000

    def panel(x0, datos, xmin, xmax, titulo, eje, marcas, color, notas):
        def X(v):
            return x0 + 50 + (v - xmin) / (xmax - xmin) * (W - 80)

        def Y(v):
            return bot - v / ymax * (bot - top)

        s = [f'<text x="{x0 + 50}" y="18" class="t-b">{titulo}</text>']
        for v in (0, 100_000, 200_000, 300_000, 400_000):
            s.append(f'<line x1="{x0 + 50}" x2="{x0 + W - 30}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" class="grid"/>')
            s.append(f'<text x="{x0 + 44}" y="{Y(v) + 4:.1f}" text-anchor="end" class="t-s">{miles(v / 1000)} mil</text>')
        for m in marcas:
            s.append(f'<text x="{X(m):.1f}" y="{bot + 16}" text-anchor="middle" class="t-s">{miles(m)}</text>')
        s.append(f'<text x="{x0 + 50 + (W - 80) / 2}" y="{bot + 34}" text-anchor="middle" class="t-s">{eje}</text>')
        pts = " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in datos)
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.6"/>')
        for xv, yv, txt, anchor, dy in notas:
            s.append(f'<circle cx="{X(xv):.1f}" cy="{Y(yv):.1f}" r="4" fill="{color}"/>')
            s.append(f'<text x="{X(xv):.1f}" y="{Y(yv) + dy:.1f}" text-anchor="{anchor}" class="t-s t-b">{txt}</text>')
        return "\n".join(s)

    esp = panel(0, CURVA_ESP, 90, 100, "Ampliar la bodega", "espacio disponible (m³)", (90, 92, 95, 99),
                "var(--warn)", [(92.07, 5219, "techo: 5.219 $/año desde 92,07 m³", "start", -30),
                                (99, 5219, "+10 %: 5.219", "end", -10)])
    cap = panel(W, CURVA_CAP, 110, 130, "Ampliar el presupuesto", "capital disponible (MM$)", (110, 115, 121, 125, 130),
                "var(--accent)", [(121, 386_591, "+10 %: 386.591 $/año", "end", -12),
                                  (125.1, 413_790, "techo 413.790", "start", -12)])
    return (f'<svg viewBox="0 0 {2 * W} {H}" role="img" aria-label="Ahorro anual al ampliar la bodega frente a '
            f'ampliar el presupuesto, en la misma escala: la bodega aporta como máximo 5.219 pesos al año y el '
            f'presupuesto hasta 413.790">{esp}{cap}</svg>')


def svg_eoq():
    """Curva de costo del motor estándar: ordenar + mantener; EOQ y lote multiproducto."""
    D, S, h = 96_000, 180_000, 3_000
    x0, x1, y0, y1 = 60, 540, 220, 24
    qmin, qmax, cmax = 1000, 7000, 20e6

    def X(q):
        return x0 + (q - qmin) / (qmax - qmin) * (x1 - x0)

    def Y(c):
        return y0 - c / cmax * (y0 - y1)

    qs = np.linspace(qmin, qmax, 120)
    path = lambda f: " ".join(f"{X(q):.1f},{Y(f(q)):.1f}" for q in qs)  # noqa: E731
    s = [f'<svg viewBox="0 0 580 270" role="img" aria-label="Costo anual del motor estándar según el tamaño de lote: '
         f'el costo total es plano cerca del óptimo; achicar el lote de 3.394 a 2.781 sube el costo solo 2 %">']
    for c in (0, 5e6, 10e6, 15e6, 20e6):
        s.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(c):.1f}" y2="{Y(c):.1f}" class="grid"/>')
        s.append(f'<text x="{x0 - 6}" y="{Y(c) + 4:.1f}" text-anchor="end" class="t-s">{miles(c / 1e6)} MM$</text>')
    for q in (1000, 2000, 3000, 4000, 5000, 6000, 7000):
        s.append(f'<text x="{X(q):.1f}" y="{y0 + 16}" text-anchor="middle" class="t-s">{miles(q)}</text>')
    s.append(f'<text x="{(x0 + x1) / 2}" y="{y0 + 36}" text-anchor="middle" class="t-s">tamaño de lote Q (u)</text>')
    s.append(f'<polyline points="{path(lambda q: D * S / q)}" fill="none" stroke="var(--muted)" stroke-width="1.6" stroke-dasharray="5 4"/>')
    s.append(f'<polyline points="{path(lambda q: h * q / 2)}" fill="none" stroke="var(--muted)" stroke-width="1.6" stroke-dasharray="1 3"/>')
    s.append(f'<polyline points="{path(lambda q: D * S / q + h * q / 2)}" fill="none" stroke="var(--ink)" stroke-width="2.6"/>')
    s.append(f'<text x="{X(5600):.1f}" y="{Y(D * S / 5600) + 16:.1f}" text-anchor="middle" class="t-s">ordenar D·S/Q</text>')
    s.append(f'<text x="{X(6300):.1f}" y="{Y(h * 6300 / 2) + 16:.1f}" text-anchor="middle" class="t-s">mantener h·Q/2</text>')
    s.append(f'<text x="{X(6500):.1f}" y="{Y(D * S / 6500 + h * 6500 / 2) - 8:.1f}" text-anchor="end" class="t-s t-b">total</text>')
    for q, txt, col, yl in ((3394, "EOQ individual 3.394 → 10,18 MM$", "var(--ink)", 14.3e6),
                            (2781, "multiproducto 2.781 → 10,39 MM$ (+2 %)", "var(--accent)", 17.6e6)):
        c = D * S / q + h * q / 2
        s.append(f'<line x1="{X(q):.1f}" x2="{X(q):.1f}" y1="{Y(c):.1f}" y2="{y0}" stroke="{col}" stroke-width="1.2"/>')
        s.append(f'<line x1="{X(q):.1f}" x2="{X(q):.1f}" y1="{Y(yl) + 4:.1f}" y2="{Y(c):.1f}" stroke="{col}" stroke-width="1" stroke-dasharray="2 3"/>')
        s.append(f'<circle cx="{X(q):.1f}" cy="{Y(c):.1f}" r="4.5" fill="{col}"/>')
        s.append(f'<text x="{X(q) + 6:.1f}" y="{Y(yl):.1f}" class="t-s" style="fill:{col};font-weight:700">{txt}</text>')
    s.append("</svg>")
    return "\n".join(s)


def img(nombre):
    return "data:image/png;base64," + base64.b64encode((FIG / nombre).read_bytes()).decode()


HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Defensa Ventisur</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,700&display=swap" rel="stylesheet">
<style>
/* Guía de estudio: lectura lineal por dimensión de la rúbrica; cada bloque = qué piden → cómo → resultado → por qué → preguntas → cuidado */
:root{
  --bg:#f3f5f8; --surface:#ffffff; --ink:#1b2129; --muted:#5b6672; --line:#dde2e8;
  --accent:#1f5fae; --accent-soft:#e8f0fa;
  --p1:#1f5fae; --p2:#2e7d4f; --p3:#6d4bb3;
  --ok:#2e7d4f; --warn:#b45309; --warn-soft:#fdf3e7; --bad:#b42318;
  --s-p1:#d9a336; --s-p2:#cc5f22; --s-p3:#8c3b2f; --s-a:#2b333c;
  --display:"Newsreader","Libertinus Serif",Georgia,serif;
  --body:"IBM Plex Sans","Inter",system-ui,sans-serif;
  --mono:"IBM Plex Mono","JetBrains Mono",ui-monospace,monospace;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#12161c; --surface:#1a2029; --ink:#e7ebf0; --muted:#9aa6b3; --line:#2c3440;
  --accent:#6aa3ec; --accent-soft:#1c2a3d; --p1:#6aa3ec; --p2:#5cbf86; --p3:#a98be0;
  --ok:#5cbf86; --warn:#f0a35a; --warn-soft:#2c2116; --bad:#f07a6e; --s-a:#c9d1db; color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#12161c; --surface:#1a2029; --ink:#e7ebf0; --muted:#9aa6b3; --line:#2c3440;
  --accent:#6aa3ec; --accent-soft:#1c2a3d; --p1:#6aa3ec; --p2:#5cbf86; --p3:#a98be0;
  --ok:#5cbf86; --warn:#f0a35a; --warn-soft:#2c2116; --bad:#f07a6e; --s-a:#c9d1db; color-scheme:dark;}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 var(--body)}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
.wrap{max-width:980px;margin:0 auto;padding:0 20px 80px}
h1,h2,h3{font-family:var(--display);text-wrap:balance;line-height:1.15;margin:0}
h1{font-size:2.3rem} h2{font-size:1.75rem} h3{font-size:1.15rem;font-family:var(--body);font-weight:700}
p{margin:.45rem 0} small,.muted{color:var(--muted)}
.num,.tile>b,td.n{font-family:var(--mono);font-variant-numeric:tabular-nums}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
header.hero{padding:34px 0 18px;display:grid;gap:10px}
.eyebrow{font:600 .78rem/1 var(--body);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
nav.toc{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(6px);
  border-bottom:1px solid var(--line);padding:8px 0;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
nav.toc a{font:600 .8rem/1 var(--body);text-decoration:none;color:var(--ink);padding:6px 9px;border-radius:999px;border:1px solid var(--line);background:var(--surface)}
nav.toc a:hover{border-color:var(--accent)}
nav.toc .sp{flex:1}
button.modo{font:600 .8rem/1 var(--body);padding:7px 12px;border-radius:999px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer}
body.practica button.modo{background:var(--surface);color:var(--accent)}
section{margin-top:44px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.grid2.g4{grid-template-columns:repeat(auto-fit,minmax(380px,1fr))}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:10px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;display:grid;gap:2px}
.tile>b{font-size:1.4rem;font-weight:600;line-height:1.2}
.tile.sm>b{font-size:1.02rem}
.tile span{font-size:.84rem;color:var(--muted);line-height:1.3}
.tile.key{border-color:var(--accent);background:var(--accent-soft)}
.dim{border-left:6px solid var(--c,var(--accent));padding-left:18px}
.dim-h{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;margin-bottom:10px}
.peso{font:700 .8rem/1 var(--body);background:var(--c,var(--accent));color:#fff;border-radius:6px;padding:6px 8px}
.parte-1{--c:var(--p1)} .parte-2{--c:var(--p2)} .parte-3{--c:var(--p3)} .parte-x{--c:var(--ink)}
.blk{display:grid;gap:12px}
.lbl{font:700 .74rem/1 var(--body);letter-spacing:.07em;text-transform:uppercase;color:var(--c,var(--accent));margin:14px 0 4px}
ol.steps{margin:.2rem 0;padding-left:1.3rem} ol.steps li{margin:.25rem 0}
.why{background:var(--accent-soft);border-radius:10px;padding:12px 16px}
.trap{background:var(--warn-soft);border-left:4px solid var(--warn);border-radius:8px;padding:10px 14px}
.trap b{color:var(--warn)}
.qa{border-top:1px solid var(--line);padding:9px 0;display:grid;gap:3px}
.qa p{margin:0}
.qa .q{font-weight:600}
.qa .a{color:var(--ink)}
body.practica .qa .a{filter:blur(6px);cursor:pointer;user-select:none;transition:filter .15s}
body.practica .qa.visto .a{filter:none}
.tbl{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.88rem;background:var(--surface)}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-weight:700;border-bottom:2px solid var(--ink)}
td.n,th.n{text-align:right}
tr.tot td{font-weight:700;border-top:2px solid var(--ink)}
tr.rec td{background:var(--accent-soft)}
.f{font-family:var(--mono);font-size:.9rem;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:1px 6px;white-space:nowrap}
.formula{font-family:var(--mono);background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 14px;overflow-x:auto;font-size:.92rem;line-height:1.7}
figure{margin:12px 0;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px}
figure svg,figure img{width:100%;height:auto;display:block}
figcaption{font-size:.86rem;color:var(--muted);margin-top:8px}
svg{color:var(--ink);font-family:var(--body)}
svg .grid{stroke:var(--line);stroke-width:1}
svg .t-s{font-size:11px;fill:var(--muted)} svg .t-m{font-size:12.5px;fill:var(--ink)} svg .t-b{font-weight:700;fill:var(--ink)}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:.82rem;color:var(--muted)}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:5px;vertical-align:-1px}
.chip{display:inline-block;font:600 .74rem/1 var(--body);padding:4px 7px;border-radius:999px;border:1px solid currentColor}
.chip.ok{color:var(--ok)} .chip.bad{color:var(--bad)} .chip.acc{color:var(--accent)}
footer{margin-top:50px;color:var(--muted);font-size:.85rem}
@media (max-width:560px){h1{font-size:1.8rem} h2{font-size:1.45rem} .wrap{padding:0 16px 60px}}
@media print{
  :root{--bg:#fff} body{font-size:10.5pt;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  nav.toc,button.modo{display:none} .wrap{max-width:none;padding:0 0 0 0}
  section{margin-top:18px;break-inside:auto} section.salto{break-before:page}
  .card,figure,.qa,.why,.trap,table,.tile{break-inside:avoid}
  body.practica .qa .a{filter:none}
  @page{size:Letter;margin:14mm 34mm 14mm 14mm}
}
</style>
</head>
<body>
<div class="wrap">

<header class="hero">
  <div class="eyebrow">Gestión de Operaciones · Sección 2 · Defensa oral</div>
  <h1>Defensa Ventisur: cómo se hizo y por qué</h1>
  <p class="muted">Cristóbal De Vidts · Constanza Catalán · Bellonce Bulnes · Matias Rojas Rodriguez</p>
  <div class="card">
    <h3>Cómo usar esta guía</h3>
    <ol class="steps">
      <li><b>Primera lectura (25 min):</b> de corrido. Lee primero <a href="#reglas">las 4 reglas</a>: explican casi todos los resultados.</li>
      <li><b>Segunda lectura:</b> activa <b>Modo práctica</b> (arriba a la derecha), responde cada pregunta en voz alta y toca la respuesta para comprobar.</li>
      <li><b>Memoriza solo <a href="#cifras">12 cifras</a>.</b> Todo lo demás se deduce de las reglas; en la defensa se premia razonar, no recitar.</li>
    </ol>
  </div>
</header>

<nav class="toc" aria-label="Secciones">
  <a href="#evaluacion">Evaluación</a><a href="#mapa">Mapa</a><a href="#reglas">4 reglas</a><a href="#cifras">12 cifras</a>
  <a href="#d1">D1</a><a href="#d2">D2</a><a href="#d3">D3</a><a href="#d4">D4</a><a href="#d5">D5</a><a href="#d6">D6</a><a href="#d7">D7</a>
  <a href="#quepasa">¿Qué pasa si…?</a><a href="#guion">Guion 5 min</a>
  <span class="sp"></span><button class="modo" id="modo" type="button" aria-pressed="false">Modo práctica</button>
</nav>

<!-- ================================================================ EVALUACIÓN -->
<section id="evaluacion">
  <div class="eyebrow">Antes de estudiar</div>
  <h2>Cómo nos evalúan</h2>
  <div class="grid2" style="margin-top:12px">
    <div class="card">
      <h3>Formato</h3>
      <p>5 minutos de presentación y 10 de preguntas. <b>La nota sale de la defensa</b>; el informe solo respalda. Cualquiera de nosotros puede ser preguntado sobre cualquier parte, y la nota puede ser distinta entre integrantes.</p>
      <p>Las preguntas típicas son: <b>cambiar un parámetro</b>, <b>quitar o agregar una restricción</b>, <b>interpretar un resultado</b> y <b>explicar un supuesto</b>. Leer una fórmula no cuenta como entenderla.</p>
    </div>
    <div class="card">
      <h3>Para sacar 4 en todo, hay que poder…</h3>
      <p>Explicar <b>qué decisión responde cada modelo</b>, <b>por qué</b> el número es el que es (no solo cuál es) y <b>qué pasaría</b> si cambia algo. Esta guía está ordenada exactamente así.</p>
      <p class="muted">En inventarios todo es determinístico: no corresponde stock de seguridad (regla de la rúbrica).</p>
    </div>
  </div>
  <div class="tbl" style="margin-top:12px"><table>
    <thead><tr><th>Dimensión</th><th class="n">Peso</th><th>Lo que la rúbrica exige para un 4</th></tr></thead>
    <tbody>
      <tr><td><a href="#d1">D1 Políticas simples</a></td><td class="n">10 %</td><td>Las 3 políticas correctas y saber qué mecanismo usa cada una para absorber la demanda; anticipar el efecto de cambiar costos.</td></tr>
      <tr><td><a href="#d2">D2 Modelo A</a></td><td class="n">20 %</td><td>Variables, restricciones y FO bien definidas; explicar cada familia de restricciones y por qué el modelo mejora a las políticas.</td></tr>
      <tr><td><a href="#d3">D3 Modelos B y C</a></td><td class="n">15 %</td><td>Lógica de la binaria y de la constante M; diferencia conceptual A–B–C; costo de mejorar el servicio; recomendación.</td></tr>
      <tr><td><a href="#d4">D4 Desagregación</a></td><td class="n">10 %</td><td>Mezcla 50–30–20 y lista de materiales; esto da tasas de consumo, no tamaños de pedido.</td></tr>
      <tr><td><a href="#d5">D5 EOQ y factibilidad</a></td><td class="n">15 %</td><td>h, Q*, N, T, d, ROP y costos; Q* = cuánto, ROP = cuándo; mostrar que los EOQ no caben juntos.</td></tr>
      <tr><td><a href="#d6">D6 Multiproducto</a></td><td class="n">20 %</td><td>Formulación, por qué el costo de compra no importa, sensibilidad y distinguir restricción activa de su valor marginal.</td></tr>
      <tr><td><a href="#d7">D7 Integración</a></td><td class="n">10 %</td><td>Conectar las 3 partes, reconocer supuestos y limitaciones, responder modificaciones no vistas.</td></tr>
    </tbody></table></div>
</section>

<!-- ================================================================ MAPA -->
<section id="mapa">
  <div class="eyebrow">El proyecto en una imagen</div>
  <h2>Tres preguntas en cadena</h2>
  <figure>
    <svg viewBox="0 0 940 230" role="img" aria-label="Parte I decide producción y dotación; la Gerencia fija 10.000 unidades al mes; Parte II convierte eso en consumo de componentes; Parte III decide cuánto y cuándo comprar cada componente">
      <defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
      <g>
        <rect x="10" y="20" width="270" height="110" rx="12" fill="none" stroke="var(--p1)" stroke-width="2.5"/>
        <text x="28" y="48" class="t-b" style="fill:var(--p1)">PARTE I · Planificación agregada</text>
        <text x="28" y="74" class="t-m">¿Con cuánta gente y cuánto</text>
        <text x="28" y="92" class="t-m">producir cada mes?</text>
        <text x="28" y="116" class="t-s">Sol. 1–5 · D1, D2, D3</text>
        <rect x="335" y="20" width="270" height="110" rx="12" fill="none" stroke="var(--p2)" stroke-width="2.5"/>
        <text x="353" y="48" class="t-b" style="fill:var(--p2)">PARTE II · Materiales</text>
        <text x="353" y="74" class="t-m">¿Cuánto se consume de cada</text>
        <text x="353" y="92" class="t-m">componente?</text>
        <text x="353" y="116" class="t-s">Sol. 6 · D4</text>
        <rect x="660" y="20" width="270" height="110" rx="12" fill="none" stroke="var(--p3)" stroke-width="2.5"/>
        <text x="678" y="48" class="t-b" style="fill:var(--p3)">PARTE III · Inventarios</text>
        <text x="678" y="74" class="t-m">¿Cuánto y cuándo pedir</text>
        <text x="678" y="92" class="t-m">cada componente?</text>
        <text x="678" y="116" class="t-s">Sol. 7–10 · D5, D6</text>
        <line x1="282" y1="75" x2="331" y2="75" stroke="currentColor" stroke-width="1.6" marker-end="url(#fl)"/>
        <line x1="607" y1="75" x2="656" y2="75" stroke="currentColor" stroke-width="1.6" marker-end="url(#fl)"/>
        <text x="306" y="150" text-anchor="middle" class="t-s">la Gerencia fija</text>
        <text x="306" y="164" text-anchor="middle" class="t-s t-b">10.000 u/mes</text>
        <text x="631" y="150" text-anchor="middle" class="t-s">entrega</text>
        <text x="631" y="164" text-anchor="middle" class="t-s t-b">Dᵢ anual</text>
        <text x="28" y="200" class="t-s">Resultado: 18 trabajadores, HE sep–feb,</text>
        <text x="28" y="216" class="t-s">cero pendientes · 301,10 MM$</text>
        <text x="353" y="200" class="t-s">8.000 · 2.000 · 10.000 · 5.000 · 2.000</text>
        <text x="353" y="216" class="t-s">u/mes de cada componente</text>
        <text x="678" y="200" class="t-s">Lotes multiproducto + punto de reorden</text>
        <text x="678" y="216" class="t-s">34,50 MM$/año</text>
      </g>
    </svg>
    <figcaption>Cada parte responde una pregunta distinta. La Parte II no usa el plan óptimo de la Parte I sino la tasa estable que fijó la Gerencia (ver D7).</figcaption>
  </figure>
</section>

<!-- ================================================================ REGLAS -->
<section id="reglas" class="salto">
  <div class="eyebrow">Lo más importante de la guía</div>
  <h2>Las 4 reglas que explican casi todo</h2>

  <h3 style="margin-top:16px">Regla 1 · La escalera de costos por unidad (Parte I)</h3>
  <figure>
    <svg viewBox="0 0 800 270" role="img" aria-label="Costo por unidad de cada forma de cubrir demanda: atrasar un mes 750, guardar un mes 1.000, guardar dos meses 2.000, horas extra 2.500, guardar tres meses 3.000, trabajador extra usado seis meses 3.800">
      <g class="t-m">
        <text x="290" y="34" text-anchor="end">Atrasar 1 u un mes (b)</text>
        <text x="290" y="70" text-anchor="end">Guardar 1 u un mes (h)</text>
        <text x="290" y="106" text-anchor="end">Guardar 1 u dos meses</text>
        <text x="290" y="142" text-anchor="end" class="t-b">Producir 1 u en horas extra</text>
        <text x="290" y="178" text-anchor="end">Guardar 1 u tres meses</text>
        <text x="290" y="214" text-anchor="end">Trabajador extra solo para sep–feb</text>
      </g>
      <rect x="300" y="20" width="90" height="20" rx="3" fill="var(--ok)"/>
      <rect x="300" y="56" width="120" height="20" rx="3" fill="var(--ok)"/>
      <rect x="300" y="92" width="240" height="20" rx="3" fill="var(--ok)"/>
      <rect x="300" y="128" width="300" height="20" rx="3" fill="var(--accent)"/>
      <rect x="300" y="164" width="360" height="20" rx="3" fill="var(--muted)"/>
      <rect x="300" y="200" width="456" height="20" rx="3" fill="var(--muted)"/>
      <g class="t-s t-b">
        <text x="396" y="35">$750</text><text x="426" y="71">$1.000</text><text x="546" y="107">$2.000</text>
        <text x="606" y="143">$2.500</text><text x="666" y="179">$3.000</text><text x="756" y="238" text-anchor="end">≈ $3.800 (11,4 MM$ ÷ 3.000 u)</text>
      </g>
      <line x1="600" y1="14" x2="600" y2="226" stroke="var(--accent)" stroke-dasharray="4 4"/>
      <text x="300" y="258" class="t-s">verde = más barato que la hora extra, se usa · gris = más caro, se evita</text>
    </svg>
    <figcaption>El Modelo A compara estas barras. Por eso atrasa en vez de adelantar, adelanta como máximo 2 meses y prefiere horas extra antes que conservar un trabajador que solo se necesita 6 meses.</figcaption>
  </figure>

  <div class="grid2 g4">
    <div class="card"><h3>Regla 2 · El sueldo se paga por trabajador, no por unidad</h3>
      <p>El costo laboral multiplica a la dotación <span class="f">W</span>. Una vez contratado, producir en horario regular no cuesta nada extra; por eso la HE solo se usa cuando falta capacidad regular, sin necesidad de forzarlo con una restricción.</p></div>
    <div class="card"><h3>Regla 3 · EOQ equilibra ordenar y mantener</h3>
      <p>Lote grande: pocos pedidos pero mucho inventario. <span class="f">Q* = √(2DS/h)</span> iguala ambos costos. <b>Q* dice cuánto</b> pedir; el punto de reorden <span class="f">ROP = d·L</span> dice <b>cuándo</b>.</p></div>
    <div class="card"><h3>Regla 4 · Activa no significa valiosa</h3>
      <p>Una restricción activa se usa al 100 %. Su <b>multiplicador</b> es el ahorro por una unidad más de recurso, pero solo en el margen: cambia apenas relajas. Dos restricciones activas pueden valer muy distinto.</p></div>
    <div class="card"><h3>Atajo para preguntas de "¿qué pasa si…?"</h3>
      <p>Ubica el parámetro en la escalera o en la fórmula. Si cambia el orden de las barras, cambia el plan; si no, el plan se mantiene y solo cambia el costo.</p></div>
  </div>
</section>

<!-- ================================================================ CIFRAS -->
<section id="cifras">
  <div class="eyebrow">Memorizar</div>
  <h2>Las 12 cifras</h2>
  <div class="tiles" style="margin-top:12px">
    <div class="tile sm"><b>340,0 · 315,0 · 329,5</b><span>MM$: P1, P2 y P3. La mejor simple es P2.</span></div>
    <div class="tile"><b>300,75</b><span>MM$ Modelo A (con atrasos). −14,25 vs P2.</span></div>
    <div class="tile"><b>300,94</b><span>MM$ Modelo B (multa). Deja diciembre en 125 u = 1 % exacto.</span></div>
    <div class="tile key"><b>301,10</b><span>MM$ Modelo C = Sol. 5. <b>Plan recomendado.</b></span></div>
    <div class="tile sm"><b>18 trabajadores</b><span>Despide 2 en marzo y los mantiene todo el año.</span></div>
    <div class="tile"><b>+350.000</b><span>Costo de pasar de A a servicio completo (0,12 %).</span></div>
    <div class="tile sm"><b>8.000 · 2.000 · 10.000 · 5.000 · 2.000</b><span>u/mes: motor est., motor prem., hélice, módulo, control.</span></div>
    <div class="tile sm"><b>113,1 m³ · 135,1 MM$</b><span>Lo que piden los EOQ juntos. Límites: 90 m³ y 110 MM$.</span></div>
    <div class="tile key"><b>34,50 MM$/año</b><span>Costo del EOQ multiproducto (+0,72 vs EOQ individual).</span></div>
    <div class="tile sm"><b>μ 5.098 · λ 0,0595</b><span>$/m³-año y $/$-año. Ambas restricciones activas.</span></div>
    <div class="tile key sm"><b>386.591 vs 5.219</b><span>$/año de ahorro: +10 % presupuesto vs +10 % espacio (74×).</span></div>
    <div class="tile"><b>302,5</b><span>MM$ con 19 trabajadores: el "seguro" (+1,4 MM$) que da holgura de HE en nov, ene y feb.</span></div>
  </div>
</section>

<!-- ================================================================ D1 -->
<section id="d1" class="dim parte-1 salto">
  <div class="dim-h"><span class="peso">10 %</span><h2>D1 · Políticas simples</h2><span class="muted">Solicitud 1</span></div>
  <div class="lbl">Qué piden</div>
  <p>Construir mes a mes tres reglas fijas, costearlas y explicar con qué mecanismo absorbe cada una la variación de demanda (pronóstico 120.000 u/año, peak en diciembre con 12.500).</p>
  <div class="lbl">Cómo lo hicimos</div>
  <ol class="steps">
    <li><b>P1 tasa constante:</b> 20 trabajadores × 500 = 10.000 u/mes siempre; el inventario se calcula como <span class="f">Iₜ = Iₜ₋₁ + 10.000 − dₜ</span>.</li>
    <li><b>P2 dotación fija + HE:</b> 20 trabajadores; se produce justo la demanda para cerrar cada mes con 1.000 u; lo que pasa de 10.000 va a horas extra.</li>
    <li><b>P3 persecución:</b> <span class="f">Wₜ = ⌈(dₜ + I_objetivo − Iₜ₋₁)/500⌉</span>, respetando 15–25 trabajadores y ±3 por mes; inventario 0 salvo febrero (1.000).</li>
    <li>Validamos en código y en Excel: bodega ≤ 7.500, dotación, ±3, inventario final 1.000 y cero pendientes.</li>
  </ol>
  <div class="lbl">Resultado</div>
  <div class="tbl"><table>
    <thead><tr><th></th><th>Mecanismo</th><th class="n">Laboral</th><th class="n">Contrat.+desp.</th><th class="n">HE</th><th class="n">Inventario</th><th class="n">Total MM$</th></tr></thead>
    <tbody>
      <tr><td><span class="sw" style="background:var(--s-p1)"></span>P1</td><td>Inventario (hasta 7.000 u)</td><td class="n">288,0</td><td class="n">0</td><td class="n">0</td><td class="n">52,0</td><td class="n">340,0</td></tr>
      <tr class="rec"><td><span class="sw" style="background:var(--s-p2)"></span>P2</td><td>Horas extra (6.000 u, nov–feb)</td><td class="n">288,0</td><td class="n">0</td><td class="n">15,0</td><td class="n">12,0</td><td class="n"><b>315,0</b></td></tr>
      <tr><td><span class="sw" style="background:var(--s-p3)"></span>P3</td><td>Contratar/despedir (9 y 6)</td><td class="n">288,0</td><td class="n">40,5</td><td class="n">0</td><td class="n">1,0</td><td class="n">329,5</td></tr>
    </tbody></table></div>
  <div class="lbl">Por qué</div>
  <div class="why">Las tres pagan lo mismo en sueldos (240 trabajador-mes = 288 MM$): la diferencia está <b>solo en el mecanismo</b>. P2 gana porque una HE ($2.500) equivale a 2,5 meses de inventario, y P1 guarda en promedio 6,7 meses cada una de las ~6.000 u del peak (40.000 u-mes extra = $6.667 por unidad). P3 ahorra 26 MM$ frente a P2 (11 de inventario y 15 de HE), pero gasta 40,5 en contratar y despedir.</div>
  <div class="lbl">Preguntas del profesor</div>
  <div class="qa"><p class="q">¿Por qué P1 no se sale de la bodega?</p><p class="a">Su inventario máximo es 7.000 u (ago–oct), bajo 7.500. Como produce 120.000 = demanda anual, termina en 1.000, igual que empezó.</p></div>
  <div class="qa"><p class="q">¿Desde qué costo de HE P3 sería más barata que P2?</p><p class="a">P2 = 300 + 6.000 × c_HE (MM$) y P3 = 329,5 ⇒ c_HE > $4.917/u. P2 le gana a P1 mientras c_HE < $6.667/u; P1 solo le ganaría a P2 si mantener costara < $375/u-mes.</p></div>
  <div class="qa"><p class="q">¿Por qué P2 tiene capacidad ociosa?</p><p class="a">Paga 20 trabajadores (10.000 u) pero de marzo a agosto la demanda es menor y el inventario debe quedar en 1.000: deja 6.000 u ociosas.</p></div>
  <div class="qa"><p class="q">¿Cómo sale la dotación de P3 en marzo?</p><p class="a">(9.500 − 1.000)/500 = 17: usa el inventario inicial y despide 3 (justo el máximo permitido).</p></div>
  <div class="trap"><b>Cuidado:</b> no digas que P3 "es mejor porque no tiene inventario". El criterio es el costo total y la estabilidad: P3 tiene 15 movimientos de personal.</div>
</section>

<!-- ================================================================ D2 -->
<section id="d2" class="dim parte-1 salto">
  <div class="dim-h"><span class="peso">20 %</span><h2>D2 · Modelo A: formulación e interpretación</h2><span class="muted">Solicitud 2 · la dimensión más pesada junto a D6</span></div>
  <div class="lbl">Qué piden</div>
  <p>Un modelo que decida todo a la vez cada mes (dotación, contrataciones, despidos, producción regular, HE, inventario y pendientes) al mínimo costo, y explicar por qué mejora a las políticas simples.</p>
  <div class="lbl">Cómo lo hicimos · el modelo completo</div>
  <div class="formula">
    min Z = Σₜ ( 1,2MM·Wₜ + 2,5MM·Hₜ + 3MM·Fₜ + 2.500·Oₜ + 1.000·Iₜ + 750·Bₜ )<br>
    Wₜ = Wₜ₋₁ + Hₜ − Fₜ &nbsp;&nbsp;<small>(dotación conecta los meses)</small><br>
    Rₜ ≤ 500·Wₜ &nbsp; Oₜ ≤ 150·Wₜ &nbsp;&nbsp;<small>(capacidades regular y HE, separadas)</small><br>
    Iₜ₋₁ − Bₜ₋₁ + Rₜ + Oₜ − dₜ = Iₜ − Bₜ &nbsp;&nbsp;<small>(balance con inventario neto)</small><br>
    Iₜ ≤ 7.500 &nbsp; 15 ≤ Wₜ ≤ 25 &nbsp; Hₜ, Fₜ ≤ 3 &nbsp;&nbsp;<small>(bodega y reglas de personal)</small><br>
    I₁₂ ≥ 1.000 &nbsp; B₁₂ = 0 &nbsp; W₀ = 20, I₀ = 1.000, B₀ = 0 &nbsp;&nbsp;<small>(bordes)</small><br>
    W, H, F enteras ≥ 0 &nbsp; R, O, I, B continuas ≥ 0
  </div>
  <p class="muted">Implementado en PuLP con el solver CBC (archivo <span class="f">parte1_modelos.py</span>; el modelo exportado está en <span class="f">ModeloA_Sol2.lp</span>).</p>
  <div class="lbl">Resultado · Z = 300,75 MM$</div>
  <div class="tbl"><table>
    <thead><tr><th>Mes</th><th class="n">Mar</th><th class="n">Abr</th><th class="n">May</th><th class="n">Jun</th><th class="n">Jul</th><th class="n">Ago</th><th class="n">Sep</th><th class="n">Oct</th><th class="n">Nov</th><th class="n">Dic</th><th class="n">Ene</th><th class="n">Feb</th></tr></thead>
    <tbody>
      <tr><td>Dotación</td><td class="n">18 (−2)</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td><td class="n">18</td></tr>
      <tr><td>Regular</td><td class="n">8.500</td><td class="n">9.000</td><td class="n">8.500</td><td class="n">9.000</td><td class="n">9.000</td><td class="n">9.000</td><td class="n">9.000</td><td class="n">9.000</td><td class="n">9.000</td><td class="n">9.000</td><td class="n">9.000</td><td class="n">9.000</td></tr>
      <tr><td>HE</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td class="n">1.000</td><td class="n">1.200</td><td class="n">2.700</td><td class="n">2.700</td><td class="n">2.700</td><td class="n">2.700</td></tr>
      <tr><td>Inventario / pendientes</td><td class="n">0</td><td class="n">0</td><td class="n">0</td><td class="n">500</td><td class="n">500</td><td class="n">0</td><td class="n">0</td><td class="n">200</td><td class="n">400</td><td class="n">0 / 400</td><td class="n">0 / 200</td><td class="n">1.000</td></tr>
    </tbody></table></div>
  <p>Costos: laboral 259,2 · despido 6,0 · HE 32,5 (13.000 u) · inventario 2,6 · pendientes 0,45 MM$.</p>
  <div class="lbl">Por qué · tres mecanismos combinados (mira la escalera)</div>
  <div class="grid2">
    <div class="why"><b>1. Despide 2 y usa HE.</b> Conservar un trabajador cuesta 14,4 MM$/año (11,4 descontando el despido evitado) y solo se necesita de sep a feb. Cubrir esas ~3.000 u con HE cuesta 7,5 MM$. Convendría conservarlo solo si se usara ≥ 9,1 meses al año.</div>
    <div class="why"><b>2. Adelanta solo 1–2 meses.</b> Guardar 1–2 meses ($1.000–2.000) es más barato que una HE ($2.500); 3 meses ya no. Por eso hay inventario en jun–jul y oct–nov, y capacidad ociosa en marzo y mayo.</div>
    <div class="why"><b>3. Atrasa en dic–ene.</b> Atrasar un mes ($750) es más barato que fabricar antes y guardar ($1.000). Con la HE ya saturada (2.700 = 150 × 18), el faltante de diciembre se posterga.</div>
  </div>
  <p style="margin-top:10px">Frente a P2 ahorra 28,8 de sueldos y 9,4 de inventario, y paga 6,0 de despidos, 17,5 de HE extra y 0,45 de atrasos: <b>−14,25 MM$</b> (−4,5 %). Frente a P3: −28,75; frente a P1: −39,25.</p>
  <figure><img src="__FIG1__" alt="Producción total y su inventario neto mes a mes: P1 produce plano y acumula hasta 7.000 unidades; el plan óptimo sigue la demanda con horas extra en el peak y guarda como máximo 1.000"><figcaption>Izquierda: producción vs demanda. Derecha: inventario neto (inventario − pendientes). El Modelo A baja de cero en dic–ene: son los atrasos.</figcaption></figure>
  <div class="lbl">Preguntas del profesor</div>
  <div class="qa"><p class="q">¿Por qué el costo laboral multiplica a W y no a la producción?</p><p class="a">Porque el enunciado dice que se paga por trabajador disponible aunque no use toda su capacidad. La producción regular no tiene costo propio.</p></div>
  <div class="qa"><p class="q">¿Hace falta una restricción para que la HE se use solo después de la regular?</p><p class="a">No. La regular ya está pagada y la HE cuesta $2.500: el óptimo nunca usa HE si hay capacidad regular útil.</p></div>
  <div class="qa"><p class="q">¿Por qué W, H y F son enteras y la producción continua?</p><p class="a">No se contrata medio trabajador; la producción es de miles de unidades. La relajación lineal da 300,68: la integralidad cuesta solo 0,07 MM$.</p></div>
  <div class="qa"><p class="q">¿Puede haber inventario y pendientes positivos el mismo mes?</p><p class="a">En el óptimo no: ambos cuestan, y bajar los dos en la misma cantidad mantiene el balance y reduce el costo.</p></div>
  <div class="qa"><p class="q">¿Hay otros óptimos con el mismo costo?</p><p class="a">No. Lo comprobamos minimizando y maximizando cada variable con el costo fijo en Z*: no hay holgura (función <span class="f">unicidad_optimo</span>).</p></div>
  <div class="qa"><p class="q">¿Qué pasa si quitamos el límite de ±3 contrataciones/despidos?</p><p class="a">Nada: no está activo. Mismo plan y 300,75.</p></div>
  <div class="qa"><p class="q">¿Y si el costo de atrasar fuera $1.500 (mayor que mantener)?</p><p class="a">Igual quedan 200 u de atraso (301,0 MM$): adelantar exigiría HE en octubre + 2 meses guardando (2.500 + 2.000 = 4.500), mientras atrasar desde enero cuesta 2.500 + 1.500 = 4.000.</p></div>
  <div class="trap"><b>Cuidado:</b> "el solver lo eligió" no es una explicación. Cada decisión se justifica con una barra de la escalera.</div>
</section>

<!-- ================================================================ D3 -->
<section id="d3" class="dim parte-1 salto">
  <div class="dim-h"><span class="peso">15 %</span><h2>D3 · Modelos B y C y recomendación</h2><span class="muted">Solicitudes 3, 4 y 5</span></div>
  <div class="lbl">Qué piden</div>
  <p>B: multa de $3 MM si los pendientes de un mes superan el 1 % de su demanda. C: cero pendientes. Sol. 5: B + cero pendientes. Comparar y recomendar.</p>
  <div class="lbl">La diferencia conceptual en una imagen</div>
  <figure>
    <svg viewBox="0 0 780 206" role="img" aria-label="Costo de los pendientes en cada modelo: A crece en línea recta, B agrega un salto de 3 millones al pasar el 1 por ciento, C no permite pendientes">
      <defs><marker id="ax" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
      <g>
        <text x="20" y="20" class="t-b">A · costo lineal</text>
        <line x1="30" y1="160" x2="230" y2="160" stroke="currentColor" marker-end="url(#ax)"/><line x1="30" y1="160" x2="30" y2="40" stroke="currentColor" marker-end="url(#ax)"/>
        <line x1="30" y1="160" x2="220" y2="100" stroke="var(--s-a)" stroke-width="2.6"/>
        <text x="130" y="196" text-anchor="middle" class="t-s">pendientes Bₜ</text><text x="44" y="62" class="t-s">$750 por u-mes, sin tope</text>
        <text x="280" y="20" class="t-b">B · salto (binaria)</text>
        <line x1="290" y1="160" x2="490" y2="160" stroke="currentColor" marker-end="url(#ax)"/><line x1="290" y1="160" x2="290" y2="40" stroke="currentColor" marker-end="url(#ax)"/>
        <line x1="290" y1="160" x2="350" y2="141" stroke="var(--s-p2)" stroke-width="2.6"/>
        <line x1="350" y1="141" x2="350" y2="70" stroke="var(--s-p2)" stroke-width="1.4" stroke-dasharray="3 3"/>
        <line x1="350" y1="70" x2="480" y2="29" stroke="var(--s-p2)" stroke-width="2.6"/>
        <text x="350" y="176" text-anchor="middle" class="t-s">1 % de dₜ</text><text x="360" y="104" class="t-s">+$3 MM</text>
        <text x="390" y="196" text-anchor="middle" class="t-s">pendientes Bₜ</text>
        <text x="540" y="20" class="t-b">C · prohibido</text>
        <line x1="550" y1="160" x2="750" y2="160" stroke="currentColor" marker-end="url(#ax)"/><line x1="550" y1="160" x2="550" y2="40" stroke="currentColor" marker-end="url(#ax)"/>
        <rect x="556" y="44" width="186" height="112" fill="var(--warn-soft)" stroke="var(--warn)" stroke-dasharray="4 3"/>
        <circle cx="550" cy="160" r="5" fill="var(--accent)"/>
        <text x="650" y="104" text-anchor="middle" class="t-s t-b">Bₜ > 0 no permitido</text>
        <text x="650" y="196" text-anchor="middle" class="t-s">solo Bₜ = 0</text>
      </g>
    </svg>
    <figcaption>A penaliza el atraso de forma blanda; B agrega un costo fijo al cruzar el umbral (no convexo, por eso necesita una binaria); C lo prohíbe con una restricción dura.</figcaption>
  </figure>
  <div class="lbl">Cómo lo hicimos</div>
  <ol class="steps">
    <li><b>B:</b> binaria <span class="f">yₜ</span> (1 = se paga la multa), restricción <span class="f">Bₜ ≤ 0,01·dₜ + Mₜ·yₜ</span> y se suma <span class="f">3.000.000·yₜ</span> a la FO. Si Bₜ pasa el 1 %, solo se cumple con yₜ = 1; si no, el costo hace que el modelo elija yₜ = 0.</li>
    <li><b>La constante M:</b> debe ser ≥ el mayor Bₜ − 0,01dₜ posible, para no cortar soluciones. Usamos el peor caso de no producir nada: <span class="f">Mₜ = Σ demanda hasta t − I₀ − 0,01dₜ</span> (dic: 96.875). Es válida pero no la más ajustada: bastaría 9.375 y el óptimo no cambia. Un M muy chico corta planes válidos; uno enorme debilita la relajación.</li>
    <li><b>C:</b> Modelo A + <span class="f">Bₜ = 0</span>. <b>Sol. 5:</b> B + Bₜ = 0. Como Bₜ = 0 ≤ 1 % siempre, yₜ = 0 y <b>Sol. 5 da exactamente C</b>.</li>
  </ol>
  <div class="lbl">Resultado</div>
  <div class="tbl"><table>
    <thead><tr><th></th><th class="n">Costo MM$</th><th class="n">HE oct</th><th class="n">Inv. oct/nov</th><th class="n">Pendientes máx.</th><th class="n">A tiempo</th><th class="n">Δ vs A</th></tr></thead>
    <tbody>
      <tr><td>A</td><td class="n">300,75</td><td class="n">1.200</td><td class="n">200 / 400</td><td class="n">400 (3,2 % dic)</td><td class="n">99,5 %</td><td class="n">—</td></tr>
      <tr><td>B</td><td class="n">300,94</td><td class="n">1.475</td><td class="n">475 / 675</td><td class="n">125 (= 1 %)</td><td class="n">99,9 %</td><td class="n">+193.750</td></tr>
      <tr class="rec"><td>C = Sol. 5</td><td class="n"><b>301,10</b></td><td class="n">1.600</td><td class="n">600 / 800</td><td class="n">0</td><td class="n">100 %</td><td class="n">+350.000</td></tr>
    </tbody></table></div>
  <p>Los tres usan 18 trabajadores y 13.000 u de HE; solo mueven HE de ene–feb a octubre y guardan más inventario. Los +350.000 = 800 u-mes más de inventario × $1.000 − 600 u-mes menos de atraso × $750.</p>
  <div class="lbl">Recomendación (Sol. 5) y su porqué</div>
  <div class="why">
    <p><b>Cero pendientes con 18 trabajadores, 301,10 MM$.</b> Cuesta solo 0,12 % más que A, y A bajo el contrato pagaría 2 multas (dic 400 > 125, ene 200 > 115): 306,75 MM$. B queda justo en el borde (125 = 1 %): una unidad más de error gatilla $3 MM. Es 13,9 MM$ más barato que P2 a cambio de un ajuste de personal y el doble de HE.</p>
    <p><b>Riesgo:</b> la HE queda al 100 % en nov–dic (93 % ene–feb). <b>Seguro:</b> 19 trabajadores cuesta +1,4 MM$ (302,5) y deja 700–850 u/mes de holgura en nov, ene y feb; diciembre sigue saturado.</p>
  </div>
  <div class="lbl">Preguntas del profesor</div>
  <div class="qa"><p class="q">¿Qué hace exactamente la binaria?</p><p class="a">Activa la multa: si los pendientes superan el 1 %, la única forma de cumplir la restricción es yₜ = 1, que suma $3 MM. Si no lo superan, yₜ queda en 0 porque el modelo minimiza costo.</p></div>
  <div class="qa"><p class="q">¿Por qué B no paga ninguna multa?</p><p class="a">Bajar los pendientes de diciembre de 400 a 125 cuesta en total 193.750, mucho menos que $3 MM. Solo pagaría con una multa menor a $151.250.</p></div>
  <div class="qa"><p class="q">¿Por qué la Sol. 5 coincide con C?</p><p class="a">Si Bₜ = 0, nunca se supera el 1 %: la multa no puede activarse y el modelo es C.</p></div>
  <div class="qa"><p class="q">¿Y si la demanda de diciembre sube 5 %?</p><p class="a">Si se sabe a tiempo, se re-planifica con los mismos 18 (303,9 MM$). Si no se anticipa, el plan fijo no alcanza: 800 + 9.000 + 2.700 = 12.500 < 13.125.</p></div>
  <div class="trap"><b>Cuidado:</b> no recomiendes A "porque es el más barato": sus atrasos violan el contrato y cuestan más con las multas.</div>
</section>

<!-- ================================================================ D4 -->
<section id="d4" class="dim parte-2 salto">
  <div class="dim-h"><span class="peso">10 %</span><h2>D4 · Desagregación y requerimientos</h2><span class="muted">Solicitud 6</span></div>
  <div class="lbl">Qué piden</div>
  <p>Con la tasa oficial de 10.000 u/mes y la mezcla 50–30–20, obtener la producción por modelo y el consumo de cada componente, y explicar por qué es constante.</p>
  <div class="lbl">Cómo lo hicimos</div>
  <figure>
    <svg viewBox="0 0 780 250" role="img" aria-label="Diez mil unidades al mes se reparten en 5.000 Estándar, 3.000 Plus y 2.000 Premium; según la lista de materiales dan 8.000 motores estándar, 2.000 motores premium, 10.000 hélices, 5.000 módulos y 2.000 controles al mes">
      <g stroke-width="2" fill="none" opacity=".85">
        <path d="M150,125 C210,125 230,55 290,55" stroke="var(--s-p1)"/><path d="M150,125 C210,125 230,125 290,125" stroke="var(--s-p2)"/><path d="M150,125 C210,125 230,195 290,195" stroke="var(--s-p3)"/>
        <path d="M410,55 C480,55 500,30 560,30" stroke="var(--s-p1)"/><path d="M410,55 C480,55 500,120 560,120" stroke="var(--s-p1)"/>
        <path d="M410,125 C480,125 500,30 560,30" stroke="var(--s-p2)"/><path d="M410,125 C480,125 500,120 560,120" stroke="var(--s-p2)"/><path d="M410,125 C480,125 500,165 560,165" stroke="var(--s-p2)"/>
        <path d="M410,195 C480,195 500,75 560,75" stroke="var(--s-p3)"/><path d="M410,195 C480,195 500,120 560,120" stroke="var(--s-p3)"/><path d="M410,195 C480,195 500,165 560,165" stroke="var(--s-p3)"/><path d="M410,195 C480,195 500,210 560,210" stroke="var(--s-p3)"/>
      </g>
      <rect x="20" y="100" width="130" height="50" rx="8" fill="var(--surface)" stroke="currentColor"/><text x="85" y="122" text-anchor="middle" class="t-b">10.000 u/mes</text><text x="85" y="139" text-anchor="middle" class="t-s">tasa oficial</text>
      <rect x="290" y="35" width="120" height="40" rx="8" fill="var(--surface)" stroke="var(--s-p1)"/><text x="350" y="60" text-anchor="middle" class="t-m">Estándar 5.000</text>
      <rect x="290" y="105" width="120" height="40" rx="8" fill="var(--surface)" stroke="var(--s-p2)"/><text x="350" y="130" text-anchor="middle" class="t-m">Plus 3.000</text>
      <rect x="290" y="175" width="120" height="40" rx="8" fill="var(--surface)" stroke="var(--s-p3)"/><text x="350" y="200" text-anchor="middle" class="t-m">Premium 2.000</text>
      <g class="t-m"><text x="566" y="34">Motor estándar <tspan class="t-b">8.000</tspan></text><text x="566" y="79">Motor premium <tspan class="t-b">2.000</tspan></text>
      <text x="566" y="124">Hélice–rejilla <tspan class="t-b">10.000</tspan></text><text x="566" y="169">Módulo electrónico <tspan class="t-b">5.000</tspan></text><text x="566" y="214">Control remoto <tspan class="t-b">2.000</tspan></text></g>
      <text x="220" y="20" text-anchor="middle" class="t-s">× mezcla 50–30–20</text><text x="485" y="244" text-anchor="middle" class="t-s">× lista de materiales (1 unidad por modelo que lo usa)</text>
    </svg>
    <figcaption>Al año (× 12): 96.000 · 24.000 · 120.000 · 60.000 · 24.000. Coinciden con los valores oficiales.</figcaption>
  </figure>
  <div class="lbl">Por qué</div>
  <div class="why">Son <b>tasas de consumo</b>, no pedidos: dicen cuánto se gasta por mes. Cuánto y cuándo comprar lo decide la Parte III. Son constantes porque la tasa (10.000), la mezcla y la lista de materiales son fijas y la producción se reparte pareja en los días operativos. Se apoyan en supuestos de la Parte I: unidad agregada homogénea y demanda determinística.</div>
  <div class="lbl">Preguntas del profesor</div>
  <div class="qa"><p class="q">¿Por qué el motor estándar es 8.000?</p><p class="a">Lo usan Estándar (5.000) y Plus (3.000). El módulo lo usan Plus y Premium (3.000 + 2.000); la hélice, los tres.</p></div>
  <div class="qa"><p class="q">¿Y con mezcla 40–30–30?</p><p class="a">Motor est. 7.000/mes, motor prem. 3.000, hélice 10.000, módulo 6.000, control 3.000.</p></div>
  <div class="qa"><p class="q">¿Por qué la lista de materiales no incluye el pedestal?</p><p class="a">El enunciado solo considera los componentes relevantes para inventarios; los elementos comunes se omiten.</p></div>
  <div class="trap"><b>Cuidado:</b> no confundas desagregar con lotificar. Esta etapa no dice tamaños de pedido.</div>
</section>

<!-- ================================================================ D5 -->
<section id="d5" class="dim parte-3 salto">
  <div class="dim-h"><span class="peso">15 %</span><h2>D5 · EOQ individuales y factibilidad conjunta</h2><span class="muted">Solicitudes 7 y 8</span></div>
  <div class="lbl">Cómo lo hicimos</div>
  <div class="formula">hᵢ = 0,25·cᵢ &nbsp; Qᵢ* = √(2DᵢSᵢ/hᵢ) &nbsp; Nᵢ = Dᵢ/Qᵢ* &nbsp; dᵢ = Dᵢ/240 &nbsp; Tᵢ = Qᵢ*/dᵢ &nbsp; ROPᵢ = dᵢ·Lᵢ &nbsp; costo = DᵢSᵢ/Q + hᵢQ/2</div>
  <div class="lbl">Resultado</div>
  <div class="tbl"><table>
    <thead><tr><th>Componente</th><th class="n">h</th><th class="n">Q*</th><th class="n">N/año</th><th class="n">T días</th><th class="n">d u/día</th><th class="n">L</th><th class="n">ROP</th><th class="n">m³</th><th class="n">MM$</th></tr></thead>
    <tbody>
      <tr><td>Motor estándar</td><td class="n">3.000</td><td class="n">3.394</td><td class="n">28,3</td><td class="n">8,5</td><td class="n">400</td><td class="n">6</td><td class="n">2.400</td><td class="n">13,6</td><td class="n">40,7</td></tr>
      <tr><td>Motor premium</td><td class="n">5.000</td><td class="n">1.453</td><td class="n">16,5</td><td class="n">14,5</td><td class="n">100</td><td class="n">10</td><td class="n">1.000</td><td class="n">7,3</td><td class="n">29,1</td></tr>
      <tr><td>Hélice–rejilla</td><td class="n">1.125</td><td class="n">5.657</td><td class="n">21,2</td><td class="n">11,3</td><td class="n">500</td><td class="n">8</td><td class="n">4.000</td><td class="n">84,9</td><td class="n">25,5</td></tr>
      <tr><td>Módulo electrónico</td><td class="n">2.000</td><td class="n">3.464</td><td class="n">17,3</td><td class="n">13,9</td><td class="n">250</td><td class="n">10</td><td class="n">2.500</td><td class="n">5,2</td><td class="n">27,7</td></tr>
      <tr><td>Control remoto</td><td class="n">1.375</td><td class="n">2.211</td><td class="n">10,9</td><td class="n">22,1</td><td class="n">100</td><td class="n">12</td><td class="n">1.200</td><td class="n">2,2</td><td class="n">12,2</td></tr>
      <tr class="tot"><td>Total</td><td></td><td></td><td class="n">94,2</td><td></td><td></td><td></td><td></td><td class="n">113,1 &gt; 90</td><td class="n">135,1 &gt; 110</td></tr>
    </tbody></table></div>
  <p>Costo relevante total 33,78 MM$/año: 16,89 de ordenar + 16,89 de mantener (en el EOQ son iguales). <span class="chip bad">infactible en espacio</span> <span class="chip bad">infactible en capital</span></p>
  <div class="lbl">Por qué</div>
  <div class="why"><b>Cómo se dice la política:</b> "pedir 3.394 motores estándar cuando queden 2.400, unas 28 veces al año, cada 8,5 días operativos". Como el plazo L es menor que el ciclo T en todos, nunca hay más de un pedido en camino. <b>No caben juntos</b> porque cada EOQ se calculó mirando solo su propio costo; nada lo obligaba a compartir la bodega (la hélice sola ocupa 84,9 m³, el 94 %) ni el capital.</div>
  <div class="lbl">Preguntas del profesor</div>
  <div class="qa"><p class="q">¿Qué supuestos permiten usar el EOQ y un ROP fijo?</p><p class="a">Demanda constante (gracias a la tasa estable de 10.000 y la mezcla fija de la Parte II), plazo conocido, reposición de todo el lote, sin quiebres ni descuentos y costos S, h constantes.</p></div>
  <div class="qa"><p class="q">¿Qué pasa si la demanda se duplica?</p><p class="a">Q* sube × √2 ≈ 1,41 (Q* ∝ √D) y el ROP se duplica (ROP = d·L).</p></div>
  <div class="qa"><p class="q">¿Y si el plazo de entrega aumenta?</p><p class="a">Cambia el cuándo (ROP sube), no el cuánto (Q* no depende de L). Si L superara a T habría pedidos en tránsito y el ROP se aplica sobre la posición de inventario.</p></div>
  <div class="qa"><p class="q">¿Y con tasa de mantención 20 % o 30 %?</p><p class="a">Q* ∝ 1/√h. Con 20 % piden 126,5 m³ y 151,1 MM$; con 30 %, 103,2 m³ y 123,3 MM$. Siguen sin caber.</p></div>
  <div class="trap"><b>Cuidado:</b> no agregues stock de seguridad: la rúbrica dice que todo es determinístico.</div>
</section>

<!-- ================================================================ D6 -->
<section id="d6" class="dim parte-3 salto">
  <div class="dim-h"><span class="peso">20 %</span><h2>D6 · EOQ multiproducto y sensibilidad</h2><span class="muted">Solicitudes 9 y 10</span></div>
  <div class="lbl">Cómo lo hicimos · el modelo</div>
  <div class="formula">
    min Σᵢ ( DᵢSᵢ/Qᵢ + hᵢQᵢ/2 )<br>
    s.a. Σᵢ vᵢQᵢ ≤ 90 m³ &nbsp;(μ) &nbsp;&nbsp; Σᵢ cᵢQᵢ ≤ 110.000.000 $ &nbsp;(λ) &nbsp;&nbsp; Qᵢ > 0<br>
    KKT: Qᵢ = √( 2DᵢSᵢ / (hᵢ + 2μvᵢ + 2λcᵢ) )
  </div>
  <ol class="steps">
    <li>Las restricciones usan <b>lotes completos</b> (todos los lotes podrían llegar juntos), como en la Sesión 4 y el "valor total de los lotes" del enunciado.</li>
    <li>Cada recurso escaso actúa como un <b>costo de mantener extra</b> (2μv + 2λc): el componente que más consume de un recurso se achica más.</li>
    <li>Resolvimos buscando μ y λ (bisección) y verificamos con un optimizador no lineal (SLSQP): mismo resultado. El problema es convexo, así que es el óptimo global.</li>
    <li>El <b>costo de compra</b> Σ Dᵢcᵢ (2.784 MM$/año) no está en la FO: se compra lo mismo al año con cualquier lote. Solo importaría con descuentos por cantidad.</li>
  </ol>
  <div class="lbl">Resultado</div>
  <div class="tiles">
    <div class="tile sm"><b>2.781 · 1.192 · 4.456 · 2.844 · 1.815</b><span>lotes (−18 % a −21 % vs EOQ; la hélice baja más por el espacio)</span></div>
    <div class="tile"><b>94 → 116</b><span>pedidos al año</span></div>
    <div class="tile key"><b>34,50 MM$</b><span>+0,72 MM$/año (+2,1 %): ordenar sube a 20,75 y mantener baja a 13,75</span></div>
    <div class="tile sm"><b>μ 5.098 · λ 0,0595</b><span>ambas activas: 90,0 m³ y 110,0 MM$ exactos</span></div>
  </div>
  <figure>__EOQ_SVG__<figcaption>El costo es plano cerca del óptimo: achicar el lote del motor estándar 18 % lo encarece solo 2 %. Por eso cumplir los límites cuesta poco.</figcaption></figure>
  <div class="lbl">Sensibilidad · la pregunta clave de la rúbrica</div>
  <figure>__VALOR_SVG__<figcaption>Mismo eje vertical en ambos paneles. La bodega deja de servir desde 92,07 m³ (de los 9 m³ nuevos solo se usan 2,07). El presupuesto se aprovecha completo hasta ≈125 MM$.</figcaption></figure>
  <div class="tbl"><table>
    <thead><tr><th>Escenario</th><th>Activas</th><th class="n">μ</th><th class="n">λ</th><th class="n">Costo $/año</th><th class="n">Pedidos</th><th class="n">Ahorro</th></tr></thead>
    <tbody>
      <tr><td>Base (90 m³; 110 MM$)</td><td>ambas</td><td class="n">5.098</td><td class="n">0,0595</td><td class="n">34.503.017</td><td class="n">115,9</td><td class="n">—</td></tr>
      <tr><td>+10 % espacio (99 m³)</td><td>solo capital</td><td class="n">0</td><td class="n">0,0636</td><td class="n">34.497.798</td><td class="n">115,7</td><td class="n">5.219</td></tr>
      <tr class="rec"><td>+10 % presupuesto (121 MM$)</td><td>ambas</td><td class="n">24.785</td><td class="n">0,0135</td><td class="n">34.116.426</td><td class="n">106,8</td><td class="n"><b>386.591</b></td></tr>
    </tbody></table></div>
  <div class="why"><b>Recomendación:</b> ampliar el presupuesto vale 74 veces más que ampliar la bodega. Que ambas estén activas no significa que valgan lo mismo: el multiplicador es una pendiente local (estimaría 45.881 para el espacio, nueve veces lo real, y 654.421 para el capital, 1,7 veces lo real) y cambia al relajar. Con más bodega, el capital pasa a limitar casi de inmediato; el capital extra, en cambio, se usa completo.</div>
  <div class="lbl">Preguntas del profesor</div>
  <div class="qa"><p class="q">¿Qué significa que una restricción esté activa?</p><p class="a">Que se usa al 100 % en el óptimo (holgura cero). Solo una restricción activa puede tener multiplicador positivo, pero estar activa no garantiza que relajarla ahorre mucho.</p></div>
  <div class="qa"><p class="q">¿Qué significa μ = 5.098?</p><p class="a">Un m³ más de bodega ahorraría ≈ $5.098 al año, solo para cambios pequeños. λ = 0,0595: un peso más de presupuesto ahorra ≈ 6 centavos al año.</p></div>
  <div class="qa"><p class="q">¿Por qué no basta achicar todos los EOQ en la misma proporción?</p><p class="a">Con factor 0,796 se cumple la bodega, pero cuesta 34,67 MM$ (163 mil más que el óptimo): espacio y capital pesan distinto en cada componente.</p></div>
  <div class="qa"><p class="q">¿Y si se amplían ambos recursos 10 %?</p><p class="a">Se ahorran 511.638, más que la suma de los dos por separado (391.810): los recursos se complementan.</p></div>
  <div class="qa"><p class="q">¿Y si la restricción fuera sobre el inventario promedio (Q/2)?</p><p class="a">Los EOQ usarían 56,6 m³ y 67,6 MM$: cabrían y no habría restricciones activas. Usamos lotes completos por ser lo conservador y lo que pide el enunciado.</p></div>
  <div class="qa"><p class="q">¿Conviene invertir los 11 MM$ extra?</p><p class="a">Ahorran 386.591 $/año, una rentabilidad media de 3,5 % (la marginal parte en 5,95 % y cae a 1,35 %). Como h ya incluye el costo de capital, es un beneficio neto: conviene si el tope es una restricción de caja que se puede levantar.</p></div>
  <div class="trap"><b>Cuidado:</b> no digas "las dos están activas, así que da lo mismo cuál relajar". Es exactamente el error que la rúbrica busca.</div>
  <figure><img src="__FIG3__" alt="Tamaños de lote de cada componente: EOQ individual, multiproducto base, con más espacio y con más presupuesto"><figcaption>Con más presupuesto todos los lotes crecen menos la hélice, que cede espacio porque la bodega sigue llena.</figcaption></figure>
</section>

<!-- ================================================================ D7 -->
<section id="d7" class="dim parte-x salto">
  <div class="dim-h"><span class="peso">10 %</span><h2>D7 · Integración y dominio del proyecto</h2></div>
  <div class="lbl">La historia completa en 4 frases</div>
  <ol class="steps">
    <li><b>Producción:</b> adoptar la Sol. 5 (18 trabajadores, HE sep–feb, cero pendientes, 301,1 MM$), con la opción de 19 trabajadores como seguro (+1,4 MM$).</li>
    <li><b>Coherencia:</b> las compras usan la tasa estable de 10.000, pero el plan óptimo produce 11.700 en nov–dic. Los Dᵢ anuales no cambian (todo plan factible produce 120.000), pero en el peak el consumo diario sube 17 % y el ROP debería subir a 2.808 · 1.170 · 4.680 · 2.925 · 1.404; si no, la hélice queda corta ≈680 u.</li>
    <li><b>Compras:</b> usar los lotes multiproducto con sus ROP, no los EOQ individuales. Cumplir los límites cuesta solo 0,72 MM$/año frente a 2.784 de compras.</li>
    <li><b>Inversión:</b> si se puede ampliar algo, que sea el presupuesto.</li>
  </ol>
  <div class="lbl">Supuestos y limitaciones (dilos antes de que te los pregunten)</div>
  <div class="grid2">
    <div class="card"><p>Demanda y plazos determinísticos (sin stock de seguridad). Unidad agregada homogénea: cualquier ventilador usa la misma capacidad. Productividad constante.</p></div>
    <div class="card"><p>Espacio y capital reservados para todos los lotes completos a la vez: con llegadas escalonadas se necesitaría menos. El EOQ supone consumo uniforme, y el plan agregado no es plano.</p></div>
  </div>
  <div class="lbl">Preguntas del profesor</div>
  <div class="qa"><p class="q">¿Qué decisión responde cada modelo?</p><p class="a">A–C: con cuánta gente y cuánto producir cada mes. Desagregación: cuánto se consume. EOQ: cuánto pedir; ROP: cuándo. Multiproducto: cuánto pedir cuando los lotes compiten por bodega y capital.</p></div>
  <div class="qa"><p class="q">¿Cómo verificaron lo que hizo la IA?</p><p class="a">Las políticas se validan en código y con fórmulas en el Excel (celda Chequeos en OK). En los modelos, el costo recalculado coincide con la FO y comprobamos que el óptimo es único. El multiproducto se resolvió de dos formas (KKT y SLSQP). Además hubo dos rondas de revisión independiente de todas las cifras.</p></div>
  <div class="qa"><p class="q">¿Cómo cambian un parámetro en vivo si se lo piden?</p><p class="a">Todo sale del Excel oficial vía <span class="f">datos.py</span>; <span class="f">python run_all.py</span> regenera todo en segundos y <span class="f">parte1_sensibilidad.py</span> tiene la función para cambiar un costo y re-optimizar.</p></div>
</section>

<!-- ================================================================ QUÉ PASA SI -->
<section id="quepasa" class="salto">
  <div class="eyebrow">Consulta rápida</div>
  <h2>¿Qué pasa si…?</h2>
  <div class="tbl"><table>
    <thead><tr><th>Cambio</th><th>Efecto</th><th class="n">Resultado</th></tr></thead>
    <tbody>
      <tr><td>Sin límite de ±3 contrataciones/despidos</td><td>No estaba activo: nada cambia</td><td class="n">300,75</td></tr>
      <tr><td>Bodega de 2.000 u</td><td>El óptimo guarda máx. 1.000: nada cambia</td><td class="n">300,75</td></tr>
      <tr><td>Costo de inventario $500</td><td>Adelanta más producción (5.000 u-mes)</td><td class="n">299,1</td></tr>
      <tr><td>Costo de atraso $1.500</td><td>Igual atrasa 200 u (adelantar sale más caro)</td><td class="n">301,0</td></tr>
      <tr><td>HE +20 % ($3.000)</td><td>Pasa a 19 trabajadores desde septiembre</td><td class="n">307,05</td></tr>
      <tr><td>HE rinde 100 u/trab-mes</td><td>Contrata 2 en septiembre (20)</td><td class="n">304,5</td></tr>
      <tr><td>Sin horas extra</td><td>Sube a 20–23 trabajadores en el peak</td><td class="n">312,9</td></tr>
      <tr><td>Despedir gratis</td><td>17 trabajadores mar–jun, 18 desde julio</td><td class="n">293,95</td></tr>
      <tr><td>Inventario final 0 / 2.000</td><td>Modelo A</td><td class="n">297,15 / 305,66</td></tr>
      <tr><td>Multa menor a $151.250</td><td>B prefiere pagar una multa en diciembre</td><td class="n">—</td></tr>
      <tr><td>Umbral de la multa 3,2 % / 0 %</td><td>B se vuelve A / se vuelve C</td><td class="n">300,75 / 301,10</td></tr>
      <tr><td>Fijar 19 / 20 trabajadores (Sol. 5)</td><td>Más holgura de HE, más caro</td><td class="n">302,5 / 306,5</td></tr>
      <tr><td>Demanda dic. +10 % (conocida)</td><td>Sigue con 18, más HE</td><td class="n">306,9</td></tr>
      <tr><td>Demanda × 2 (EOQ)</td><td>Q* × 1,41; ROP × 2</td><td class="n">—</td></tr>
      <tr><td>Solo restricción de espacio</td><td>Usaría 125,1 MM$ de capital</td><td class="n">34.089.228</td></tr>
      <tr><td>Solo restricción de capital</td><td>Usaría 92,07 m³</td><td class="n">34.497.798</td></tr>
      <tr><td>+10 % ambos recursos</td><td>Se complementan</td><td class="n">ahorro 511.638</td></tr>
    </tbody></table></div>
</section>

<!-- ================================================================ GUION -->
<section id="guion">
  <div class="eyebrow">Presentación de 5 minutos</div>
  <h2>Guion</h2>
  <div class="tbl"><table>
    <thead><tr><th>Diap.</th><th class="n">Tiempo</th><th>Mensaje que no puede faltar</th></tr></thead>
    <tbody>
      <tr><td>1 Portada</td><td class="n">0:15</td><td>Plan de producción a 12 meses y luego cómo comprar 5 componentes.</td></tr>
      <tr><td>2 Políticas simples</td><td class="n">0:35</td><td>Mismo costo laboral; cambia el mecanismo. P2 gana (315,0).</td></tr>
      <tr><td>3 Modelo A</td><td class="n">0:50</td><td>18 trabajadores, HE en el peak, adelanta 1–2 meses y atrasa porque b &lt; h. 300,75.</td></tr>
      <tr><td>4 B, C y Sol. 5</td><td class="n">0:45</td><td>Binaria con M; servicio completo cuesta 350 mil.</td></tr>
      <tr><td>5 Recomendación agregada</td><td class="n">0:30</td><td>Sol. 5 con 18; seguro de 19 si hay incertidumbre.</td></tr>
      <tr><td>6 Componentes y EOQ</td><td class="n">0:35</td><td>Tasas constantes → EOQ; no caben (113 m³, 135 MM$).</td></tr>
      <tr><td>7 Multiproducto</td><td class="n">0:40</td><td>Ambas activas, pero el presupuesto vale 74 veces más.</td></tr>
      <tr><td>8 Integración</td><td class="n">0:30</td><td>Las 4 frases de D7.</td></tr>
    </tbody></table></div>
  <p class="muted">Total 4:40, con 20 s de margen. Sugerencia: un integrante por cada dos diapositivas, pero todos estudian todo.</p>
  <div class="trap" style="margin-top:12px"><b>Frases que restan puntos:</b> "el solver lo eligió", "la IA lo calculó", "las dos restricciones valen lo mismo", "agregamos stock de seguridad". <b>Frases que suman:</b> "porque atrasar cuesta menos que guardar", "la binaria activa la multa solo si se pasa del 1 %", "activa no implica valiosa".</div>
</section>

<footer>Todas las cifras salen de <span class="f">proyecto/02_resultados</span> (Excel, CSV y resumen.json) y del informe. Guía generada con <span class="f">construir_guia_defensa.py</span>.</footer>
</div>
<script>
(function(){
  var b=document.getElementById('modo'), k='ventisur-practica';
  function set(on){document.body.classList.toggle('practica',on);b.setAttribute('aria-pressed',on?'true':'false');
    b.textContent=on?'Mostrar respuestas':'Modo práctica';try{localStorage.setItem(k,on?'1':'0')}catch(e){}}
  b.addEventListener('click',function(){set(!document.body.classList.contains('practica'));
    document.querySelectorAll('.qa.visto').forEach(function(q){q.classList.remove('visto')});});
  document.querySelectorAll('.qa').forEach(function(q){q.addEventListener('click',function(){
    if(document.body.classList.contains('practica'))q.classList.toggle('visto');});});
  try{if(localStorage.getItem(k)==='1')set(true)}catch(e){}
})();
</script>
</body>
</html>
"""


def main():
    html = HTML
    for k, v in (("EOQ_SVG", svg_eoq()), ("VALOR_SVG", svg_valor()),
                 ("FIG1", img("fig1_planes.png")), ("FIG3", img("fig3_lotes.png"))):
        html = html.replace(f"__{k}__", v)
    out = AQUI / "Defensa_Ventisur.html"
    out.write_text(html, encoding="utf-8")
    pdf = AQUI / "Defensa_Ventisur.pdf"
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto({json.dumps(out.as_uri())}, {{waitUntil: 'networkidle'}});
  await p.emulateMedia({{media: 'print'}});
  await p.pdf({{path: {json.dumps(str(pdf))}, format: 'Letter', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:7pt;width:100%;text-align:center;color:#777">Defensa Ventisur · <span class="pageNumber"></span>/<span class="totalPages"></span></div>'}});
  await b.close();
}})();
"""
    subprocess.run(["node", "-e", js], check=True, timeout=180)
    print(out, pdf)


if __name__ == "__main__":
    main()
