"""Figuras del informe y de la presentación (se guardan en 02_resultados/figuras).

Sistema visual Ventisur, una identidad con dos registros:
  * fig1_planes, fig2_costos, fig3_lotes -> informe (registro SOBRIO): Libertinus Serif (la del PDF en LaTeX; Inter si no está), grises tinta y un único
    acento azul para el plan recomendado; ancho de caja carta (7,2 in) para insertarlas a escala 1:1.
  * slide_fig1..3 -> diapositivas (registro EXPRESIVO): Carlito (= métrica de Calibri), trazos y texto
    grandes (>= 14 pt), generadas al tamaño exacto de inserción en la diapositiva (escala 1:1).

Colores fijos por serie en TODOS los entregables: P1 oro, P2 naranja, P3 ladrillo (cada uno igual al
componente de costo que la política usa como mecanismo), Modelo A pizarra, Modelo B gris y el plan
recomendado (Sol. 5 = Modelo C) en Azul Ventisur. Las barras parten siempre de 0; los ejes de línea que no
parten de 0 lo declaran. El texto va siempre en tinta, nunca en el color de la serie.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.transforms import offset_copy  # noqa: E402

from datos import RESULTADOS  # noqa: E402

FIG = RESULTADOS / "figuras"

# Las figuras del informe usan la misma tipografía que el PDF en LaTeX (Libertinus) si está instalada
# (TeX Live); si no, Inter. Las de diapositivas usan Carlito (= Calibri).
from pathlib import Path  # noqa: E402

from matplotlib import font_manager  # noqa: E402

_LIBERTINUS = Path("/usr/share/texlive/texmf-dist/fonts/opentype/public/libertinus-fonts")
FUENTE_INFORME = "Inter"
if _LIBERTINUS.is_dir():
    for _f in _LIBERTINUS.glob("LibertinusSerif-*.otf"):
        font_manager.fontManager.addfont(str(_f))
    FUENTE_INFORME = "Libertinus Serif"

# ---------------------------------------------------------------- tokens del sistema visual
SERIE = {"P1": "#d9a336", "P2": "#cc5f22", "P3": "#8c3b2f", "A": "#2b333c", "B": "#98a2ac", "S5": "#1f5fae"}
COMPONENTE = {"Laboral": "#d9dde2", "Contratación + despido": "#8c3b2f", "Horas extra": "#cc5f22",
              "Inventario": "#d9a336", "Pendientes": "#2b333c"}  # orden de apilado, de abajo hacia arriba
ESCENARIO = {"EOQ individual (infactible)": "#dde1e6", "Multiproducto · base": "#1f5fae",
             "+10 % espacio": "#7fa3d6", "+10 % presupuesto": "#10233d"}
DEM_FILL, DEM_EDGE, REF = "#e9ecef", "#8f99a3", "#6b7580"
INK, INK2, INK3, GRID, AXIS, BANDA = "#1c2127", "#4a535d", "#6b7580", "#eceef1", "#b9c0c7", "#eaf1f8"
ACENTO, BLANCO = "#1f5fae", "#ffffff"

ESTILO_INFORME = {
    "font.family": FUENTE_INFORME, "font.size": 7.5, "axes.titlesize": 8.5, "axes.titleweight": "semibold",
    "axes.titlelocation": "left", "axes.titlepad": 6, "axes.labelsize": 7.5, "axes.labelcolor": INK2,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "xtick.color": INK3, "ytick.color": INK3,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "xtick.major.size": 0, "ytick.major.size": 0,
    "xtick.major.pad": 4, "ytick.major.pad": 4, "legend.frameon": False, "legend.fontsize": 7,
    "text.color": INK, "axes.titlecolor": INK, "savefig.dpi": 300, "figure.facecolor": BLANCO,
    "axes.facecolor": BLANCO, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
    "axes.unicode_minus": True,
}
ESTILO_DIAP = {
    **ESTILO_INFORME, "font.family": "Carlito", "font.size": 14, "axes.titlesize": 14, "xtick.labelsize": 14,
    "ytick.labelsize": 14, "legend.fontsize": 14, "axes.labelsize": 14, "grid.linewidth": 0.8,
    "axes.linewidth": 0.9, "xtick.major.pad": 6, "ytick.major.pad": 6, "savefig.dpi": 250,
}
CM = 1 / 2.54  # cm -> pulgadas
TAM_DIAP = {"fig1": (15.7 * CM, 12.6 * CM), "fig2": (19.5 * CM, 11.0 * CM), "fig3": (14.5 * CM, 11.0 * CM)}

# Grosor de línea (pt) por registro: (políticas y Modelo A, recomendado, serie tapada que debe asomar)
LW_INF = dict(serie=1.3, reco=2.2, solape=2.4, marca=3.4, aro=0.9, dem=0.8, ref=0.7)
LW_DIAP = dict(serie=2.2, reco=3.5, solape=4.2, marca=7.0, aro=1.4, dem=1.1, ref=1.0)

NOMBRE = {"P1": "P1 Tasa constante", "P2": "P2 Dotación + HE", "P3": "P3 Persecución", "A": "Modelo A",
          "S5": "Sol. 5 (recomendado)"}


# ---------------------------------------------------------------- formato numérico (miles "." y decimal ",")
def _miles(v, _pos=None):
    return f"{v:,.0f}".replace(",", ".").replace("-", "−")


def _dec(v, n=2):
    return f"{v:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _mes(meses):
    return [m[:3] for m in meses]


# ---------------------------------------------------------------- datos
def _planes(politicas, modelos):
    """Producción total e inventario neto (I − B) de las series que se dibujan en fig1."""
    dfs = {"P1": politicas["Política 1"], "P2": politicas["Política 2"], "P3": politicas["Política 3"],
           "A": modelos["Modelo A (Sol. 2)"][0], "S5": modelos["Modelo D (Sol. 5)"][0]}
    prod = {k: (d.Prod_regular + d.Prod_HE).to_numpy(float) for k, d in dfs.items()}
    neto = {k: (d.Inventario_final - d.Pendientes).to_numpy(float) for k, d in dfs.items()}
    return dfs["P1"].Demanda.to_numpy(float), _mes(dfs["P1"].Mes), prod, neto


def _datos_costos(politicas, modelos):
    """Componentes de costo (MM$) por plan. La multa vale 0 en todos los planes: no se dibuja."""
    planes = [("P1", politicas["Política 1"]), ("P2", politicas["Política 2"]), ("P3", politicas["Política 3"]),
              ("A", modelos["Modelo A (Sol. 2)"][0]), ("B", modelos["Modelo B (Sol. 3)"][0]),
              ("C", modelos["Modelo C (Sol. 4)"][0]), ("S5", modelos["Modelo D (Sol. 5)"][0])]
    f = {"Laboral": lambda d: d.C_laboral, "Contratación + despido": lambda d: d.C_contratacion + d.C_despido,
         "Horas extra": lambda d: d.C_HE, "Inventario": lambda d: d.C_inventario,
         "Pendientes": lambda d: d.C_pendientes}
    comp = {k: np.array([g(d).sum() / 1e6 for _, d in planes]) for k, g in f.items()}
    multa = sum(d["C_multa"].sum() if "C_multa" in d else 0 for _, d in planes)
    assert multa == 0, "La multa ya no vale 0: agregarla a la pila y a la leyenda (color #98a2ac)."
    return [k for k, _ in planes], comp


def _datos_lotes(ind, multi):
    q = {"EOQ individual (infactible)": ind.Q.to_numpy(float)}
    for e, n in [("Base", "Multiproducto · base"), ("+10% espacio", "+10 % espacio"),
                 ("+10% presupuesto", "+10 % presupuesto")]:
        q[n] = multi[multi.Escenario == e].set_index("Componente").loc[list(ind.Componente), "Q"].to_numpy(float)
    return q


# ---------------------------------------------------------------- piezas comunes
def _poner_titulos(fig, ax, tit, sub, fs_t=8.5, fs_s=7.2, sep=2.5):
    """Título (la conclusión, semibold tinta) + subtítulo (qué se mide, en qué unidad; tinta secundaria)
    encima del área de datos. Quedan fuera de tight_layout: el espacio se reserva con `_techo`."""
    y_sub = 9.0
    y_tit = y_sub + fs_s * 1.25 + sep
    for txt, dy, kw in [(sub, y_sub, dict(fontsize=fs_s, color=INK2)),
                        (tit, y_tit, dict(fontsize=fs_t, color=INK, fontweight="semibold"))]:
        t = ax.text(0, 1, txt, ha="left", va="bottom", clip_on=False,
                    transform=offset_copy(ax.transAxes, fig=fig, x=0, y=dy, units="points"), **kw)
        t.set_in_layout(False)
        t._es_titulo, t._dy = True, dy
    return y_tit + fs_t * 1.25  # alto del bloque de títulos (pt)


def _techo(fig, alto_pt):
    """Fracción superior de la figura que queda libre para el bloque de títulos."""
    return 1 - (alto_pt + 2) / 72 / fig.get_figheight()


def _piso(fig, filas, fs, aire=9.0):
    """Fracción inferior reservada para una leyenda de `filas` filas bajo el gráfico (+ aire en pt)."""
    return (filas * fs * 1.45 + aire) / 72 / fig.get_figheight()


def _alinear_titulos(fig, axs):
    """Alinea títulos y subtítulos con el borde izquierdo de las etiquetas del eje y (llamar tras el layout)
    y verifica que no se salgan de la figura."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    for ax in axs:
        dx = (ax.yaxis.get_tightbbox(r).x0 - ax.get_window_extent(r).x0) * 72 / fig.dpi
        for t in ax.texts:
            if getattr(t, "_es_titulo", False):
                t.set_transform(offset_copy(ax.transAxes, fig=fig, x=dx, y=t._dy, units="points"))
    fig.canvas.draw()
    for ax in axs:
        for t in ax.texts:
            if getattr(t, "_es_titulo", False):
                assert t.get_window_extent(r).x1 <= fig.bbox.x1 + 0.5, f"Título fuera de la figura: {t.get_text()}"


def _linea_demanda(ax, x, dem, piso, lw):
    ax.fill_between(x, piso, dem, color=DEM_FILL, lw=0, zorder=1)
    ax.plot(x, dem, color=DEM_EDGE, lw=lw["dem"], zorder=2)


def _serie(ax, x, y, k, lw, solape=False, z=3):
    if k == "S5":
        ax.plot(x, y, color=SERIE[k], lw=lw["reco"], marker="o", ms=lw["marca"], mfc=SERIE[k], mec=BLANCO,
                mew=lw["aro"], zorder=8)
    else:
        ax.plot(x, y, color=SERIE[k], lw=lw["solape"] if solape else lw["serie"], zorder=z)


def _manijas_planes(lw, demanda=True, ms=None):
    h, n = [], []
    if demanda:
        h.append(Patch(facecolor=DEM_FILL, edgecolor=DEM_EDGE, lw=lw["dem"]))
        n.append("Demanda")
    for k in ["P1", "P2", "P3", "A"]:
        h.append(Line2D([], [], color=SERIE[k], lw=lw["serie"] + 0.3))
        n.append(NOMBRE[k])
    h.append(Line2D([], [], color=SERIE["S5"], lw=lw["reco"], marker="o", ms=ms or lw["marca"],
                    mec=BLANCO, mew=lw["aro"]))
    n.append(NOMBRE["S5"])
    return h, n


def _panel_produccion(ax, x, dem, prod, lw):
    """Producción total mensual de P1-P3 y de Sol. 5 sobre la silueta de la demanda (eje desde 7.000).
    P3 coincide con la demanda y con P2 casi todo el año: se dibuja primero y más gruesa para que asome."""
    _linea_demanda(ax, x, dem, 7000, lw)
    _serie(ax, x, prod["P3"], "P3", lw, solape=True)
    _serie(ax, x, prod["P1"], "P1", lw, z=4)
    _serie(ax, x, prod["P2"], "P2", lw, z=5)
    _serie(ax, x, prod["S5"], "S5", lw)
    ax.set_ylim(7000, 13200)
    ax.set_yticks(range(7000, 13001, 1000))
    ax.yaxis.set_major_formatter(_miles)
    ax.set_xlim(-0.35, len(x) - 0.65)


def _panel_inventario(ax, x, neto, lw):
    """Inventario neto al cierre (I − B) con la capacidad de bodega como referencia continua."""
    ax.axhline(0, color=AXIS, lw=0.8, zorder=1)
    ax.axhline(7500, color=REF, lw=lw["ref"], zorder=2)
    _serie(ax, x, neto["P3"], "P3", lw, solape=True)
    _serie(ax, x, neto["P1"], "P1", lw, z=4)
    _serie(ax, x, neto["P2"], "P2", lw, z=4)
    _serie(ax, x, neto["A"], "A", lw, z=5)
    _serie(ax, x, neto["S5"], "S5", lw)
    ax.yaxis.set_major_formatter(_miles)
    ax.set_xlim(-0.35, len(x) - 0.65)


def _dibujar_costos(ax, planes, comp, ancho, gap):
    xs = np.arange(len(planes))
    i5 = planes.index("S5")
    ax.axvspan(i5 - 0.47, i5 + 0.47, color=BANDA, lw=0, zorder=0)
    base = np.zeros(len(planes))
    for k, v in comp.items():
        if not v.any():
            continue
        ax.bar(xs, v, ancho, bottom=base, color=COMPONENTE[k], edgecolor=BLANCO, linewidth=gap, zorder=2)
        base += v
    return xs, base


def _dibujar_lotes(ax, q, ancho, gap):
    n = len(next(iter(q.values())))
    xs = np.arange(n)
    for j, (e, v) in enumerate(q.items()):
        ax.bar(xs + (j - 1.5) * ancho, v, ancho, color=ESCENARIO[e], edgecolor=BLANCO, linewidth=gap, zorder=2)
    ax.yaxis.set_major_formatter(_miles)
    ax.set_xlim(-0.6, n - 0.4)
    return xs


def _guardar(fig, nombre, **kw):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / nombre, facecolor=fig.get_facecolor(), **kw)
    plt.close(fig)


# ================================================================ INFORME (registro sobrio)
def fig_politicas(politicas, modelos):
    dem, meses, prod, neto = _planes(politicas, modelos)
    x = np.arange(len(dem))
    lw = LW_INF
    with plt.rc_context(ESTILO_INFORME):
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.6))
        _panel_produccion(a1, x, dem, prod, lw)
        a1.set_xticks(x, meses)
        a1.text(0.0, 7230, "Demanda", fontsize=6.8, color=INK3, zorder=3)
        a1.text(1.5, 10140, "P1", fontsize=6.8, color=INK, ha="center", va="bottom", fontweight="semibold")
        alto = _poner_titulos(fig, a1, "Sol. 5 sigue la demanda con HE en el peak; P1 produce plano",
                              "Producción total mensual (u) · eje desde 7.000", fs_t=8)

        _panel_inventario(a2, x, neto, lw)
        a2.set_ylim(-1150, 8300)
        a2.set_yticks(range(0, 8001, 2000))
        a2.set_xticks(x, meses)
        a2.text(len(x) - 0.65, 7630, "Capacidad de bodega 7.500", fontsize=6.6, color=INK3, ha="right",
                va="bottom")
        a2.text(6.0, 6800, "P1", fontsize=6.8, color=INK, ha="center", va="top", fontweight="semibold")
        a2.text(1.5, 1180, "P2", fontsize=6.8, color=INK, ha="center", va="bottom", fontweight="semibold")
        a2.text(9.0, -520, "Modelo A", fontsize=6.6, color=INK, ha="center", va="top")
        _poner_titulos(fig, a2, "P1 acumula hasta 7.000 u; Sol. 5 guarda como máximo 1.000 u",
                       "Inventario neto al cierre de mes, I − B (u)", fs_t=8)

        h, n = _manijas_planes(lw)
        fig.legend(h, n, ncol=6, loc="lower center", bbox_to_anchor=(0.5, 0.0), handlelength=1.8,
                   handleheight=0.8, columnspacing=1.4, fontsize=6.8)
        fig.tight_layout(w_pad=2.5, rect=(0, _piso(fig, 1, 6.8), 1, _techo(fig, alto)), pad=0.25)
        _alinear_titulos(fig, [a1, a2])
        _guardar(fig, "fig1_planes.png")


def fig_costos(politicas, modelos):
    planes, comp = _datos_costos(politicas, modelos)
    et = {"P1": "P1", "P2": "P2", "P3": "P3", "A": "Modelo A\nSol. 2", "B": "Modelo B\nSol. 3",
          "C": "Modelo C\nSol. 4", "S5": "Sol. 5\nrecomendado"}
    with plt.rc_context(ESTILO_INFORME):
        fig, ax = plt.subplots(figsize=(7.2, 2.6))
        xs, tot = _dibujar_costos(ax, planes, comp, ancho=0.56, gap=0.7)
        for i, t in enumerate(tot):
            reco = planes[i] == "S5"
            ax.text(i, t + 5, _dec(t, 2), ha="center", va="bottom", fontsize=7, color=INK,
                    fontweight="semibold" if reco else "normal")
        ax.set_xticks(xs, [et[p] for p in planes])
        lab = ax.get_xticklabels()[planes.index("S5")]
        lab.set_color(INK)
        lab.set_fontweight("semibold")
        ax.set_ylim(0, 370)
        ax.set_yticks(range(0, 301, 100))
        ax.set_xlim(-0.55, len(planes) - 0.45)
        alto = _poner_titulos(fig, ax, "Sol. 5: −13,9 MM$ (−4,4 %) vs P2 y con servicio completo",
                           "Costo total anual por plan y su composición (MM$)")
        h = [Patch(facecolor=c, edgecolor="none") for k, c in COMPONENTE.items() if comp[k].any()]
        n = [k for k in COMPONENTE if comp[k].any()]
        fig.legend(h, n, ncol=len(n), loc="lower center", bbox_to_anchor=(0.5, 0.0), handlelength=1.1,
                   handleheight=0.9, columnspacing=1.6, fontsize=6.8)
        fig.tight_layout(rect=(0, _piso(fig, 1, 6.8), 1, _techo(fig, alto)), pad=0.25)
        _alinear_titulos(fig, [ax])
        _guardar(fig, "fig2_costos.png")


def fig_lotes(ind, multi):
    q = _datos_lotes(ind, multi)
    et = [c.replace("Conjunto hélice-rejilla", "Hélice–rejilla") for c in ind.Componente]
    with plt.rc_context(ESTILO_INFORME):
        fig, ax = plt.subplots(figsize=(7.2, 2.35))
        xs = _dibujar_lotes(ax, q, ancho=0.19, gap=0.8)
        ax.set_xticks(xs, et)
        ax.set_ylim(0, 6000)
        ax.set_yticks(range(0, 6001, 1000))
        alto = _poner_titulos(fig, ax, "Los lotes multiproducto son 18–21 % menores que el EOQ individual",
                           "Tamaño de lote por componente (u) · +10 % presupuesto agranda todos salvo la "
                           "hélice–rejilla; +10 % espacio casi no los cambia")
        h = [Patch(facecolor=c, edgecolor="none") for c in ESCENARIO.values()]
        fig.legend(h, list(ESCENARIO), ncol=4, loc="lower center", bbox_to_anchor=(0.5, 0.0), handlelength=1.1,
                   handleheight=0.9, columnspacing=1.8, fontsize=6.8)
        fig.tight_layout(rect=(0, _piso(fig, 1, 6.8), 1, _techo(fig, alto)), pad=0.25)
        _alinear_titulos(fig, [ax])
        _guardar(fig, "fig3_lotes.png")


# ================================================================ DIAPOSITIVAS (registro expresivo)
def _etiqueta_pastilla(ax, x, y, texto, color, **kw):
    """Etiqueta directa sobre un relleno de color (texto blanco): solo para la serie recomendada."""
    ax.text(x, y, texto, color=BLANCO, fontsize=14, fontweight="bold", zorder=10, va="center",
            bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.5", facecolor=color, edgecolor="none"), **kw)


def slide_fig1(politicas, modelos):
    """Diap. 3: producción (arriba) e inventario neto (abajo), sin título interno (lo da la diapositiva)."""
    dem, meses, prod, neto = _planes(politicas, modelos)
    x = np.arange(len(dem))
    lw = LW_DIAP
    with plt.rc_context(ESTILO_DIAP):
        fig, (a1, a2) = plt.subplots(2, 1, figsize=TAM_DIAP["fig1"], sharex=True)
        _panel_produccion(a1, x, dem, prod, lw)
        a1.set_ylim(7000, 13400)
        a1.set_yticks(range(7000, 13001, 2000))
        a1.text(0.0, 7300, "Demanda", fontsize=14, color=INK3, zorder=3)
        a1.text(1.6, 10180, "P1", fontsize=14, color=INK, ha="center", va="bottom", fontweight="bold")
        _etiqueta_pastilla(a1, 11.35, 12350, "Sol. 5", SERIE["S5"], ha="right")
        a1.text(0, 1.04, "Producción total (u/mes) · eje desde 7.000", transform=a1.transAxes, fontsize=14,
                color=INK2, ha="left", va="bottom")

        _panel_inventario(a2, x, neto, lw)
        a2.set_ylim(-1700, 8600)
        a2.set_yticks(range(0, 8001, 4000))
        a2.set_xticks(x, meses)
        a2.text(len(x) - 0.65, 7750, "Bodega 7.500", fontsize=14, color=INK3, ha="right", va="bottom")
        a2.text(6.0, 6650, "P1", fontsize=14, color=INK, ha="center", va="top", fontweight="bold")
        a2.text(1.6, 1250, "P2", fontsize=14, color=INK, ha="center", va="bottom", fontweight="bold")
        a2.text(9.0, -650, "Modelo A", fontsize=14, color=INK, ha="center", va="top")
        a2.text(0, 1.04, "Inventario neto al cierre, I − B (u)", transform=a2.transAxes, fontsize=14,
                color=INK2, ha="left", va="bottom")

        h, n = _manijas_planes(lw, ms=8)
        n = ["Demanda", "P1", "P2", "P3", "Modelo A", "Sol. 5"]
        fig.legend(h, n, ncol=6, loc="lower center", bbox_to_anchor=(0.5, 0.0), handlelength=1.5,
                   handleheight=0.8, columnspacing=1.0, handletextpad=0.5)
        fig.tight_layout(h_pad=1.6, rect=(0, _piso(fig, 1, 14, 12), 1, 1), pad=0.3)
        _guardar(fig, "slide_fig1_planes.png")


def slide_fig2(politicas, modelos):
    """Diap. 5: costo por plan; el recomendado con banda, total en negrita y en acento."""
    planes, comp = _datos_costos(politicas, modelos)
    et = {"P1": "P1", "P2": "P2", "P3": "P3", "A": "Modelo A", "B": "Modelo B", "C": "Modelo C", "S5": "Sol. 5"}
    with plt.rc_context(ESTILO_DIAP):
        fig, ax = plt.subplots(figsize=TAM_DIAP["fig2"])
        xs, tot = _dibujar_costos(ax, planes, comp, ancho=0.6, gap=1.4)
        for i, t in enumerate(tot):
            reco = planes[i] == "S5"
            ax.text(i, t + 6, _dec(t, 2), ha="center", va="bottom", fontsize=17 if reco else 15,
                    color=ACENTO if reco else INK, fontweight="bold" if reco else "normal")
        ax.set_xticks(xs, [et[p] for p in planes])
        for p, lab in zip(planes, ax.get_xticklabels()):
            if p == "S5":
                lab.set_fontsize(15)
                lab.set_color(INK)
                lab.set_fontweight("bold")
        ax.set_ylim(0, 375)
        ax.set_yticks(range(0, 301, 100))
        ax.set_xlim(-0.55, len(planes) - 0.45)
        h = [Patch(facecolor=c, edgecolor="none") for k, c in COMPONENTE.items() if comp[k].any()]
        n = [k for k in COMPONENTE if comp[k].any()]
        fig.legend(h, n, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.0), handlelength=1.0,
                   handleheight=1.0, columnspacing=1.4, handletextpad=0.5)
        fig.tight_layout(rect=(0, _piso(fig, 2, 14, 16), 1, 1), pad=0.3)
        _guardar(fig, "slide_fig2_costos.png")


def slide_fig3(ind, multi):
    """Diap. 7: lotes por componente y escenario; el multiproducto base (a implementar) en acento."""
    q = _datos_lotes(ind, multi)
    et = ["Motor\nestándar", "Motor\npremium", "Hélice–\nrejilla", "Módulo\nelectrónico", "Control\nremoto"]
    with plt.rc_context(ESTILO_DIAP):
        fig, ax = plt.subplots(figsize=TAM_DIAP["fig3"])
        xs = _dibujar_lotes(ax, q, ancho=0.2, gap=1.2)
        ax.set_xticks(xs, et)
        ax.set_ylim(0, 6000)
        ax.set_yticks(range(0, 6001, 2000))
        h = [Patch(facecolor=c, edgecolor="none") for c in ESCENARIO.values()]
        n = ["EOQ individual (infactible)", "Multiproducto · base", "+10 % espacio", "+10 % presupuesto"]
        fig.legend(h, n, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 0.0), handlelength=1.0,
                   handleheight=1.0, columnspacing=1.2, handletextpad=0.5)
        fig.tight_layout(rect=(0, _piso(fig, 2, 14, 16), 1, 1), pad=0.3)
        _guardar(fig, "slide_fig3_lotes.png")


def fig_slides(politicas, modelos, ind, multi):
    """Versiones para diapositivas, al tamaño exacto de inserción (figsize = cm / 2,54; insertar 1:1):
    slide_fig1 15,7 × 12,6 cm · slide_fig2 19,5 × 11,0 cm · slide_fig3 14,5 × 11,0 cm."""
    slide_fig1(politicas, modelos)
    slide_fig2(politicas, modelos)
    slide_fig3(ind, multi)


def generar(politicas, modelos, ind, multi):
    fig_politicas(politicas, modelos)
    fig_costos(politicas, modelos)
    fig_lotes(ind, multi)
    fig_slides(politicas, modelos, ind, multi)
