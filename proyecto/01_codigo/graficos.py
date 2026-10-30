"""Figuras para el informe y la presentación (se guardan en 02_resultados/figuras)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from datos import RESULTADOS  # noqa: E402

FIG = RESULTADOS / "figuras"
COL = {"P1": "#9aa5b1", "P2": "#5b8def", "P3": "#e0a33a", "A": "#2f9e72", "B": "#8c5bd6", "C": "#d0504f"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def _mes(m):
    return [x[:3] for x in m]


def _panel_produccion(ax, x, df1, politicas, modelos):
    """Producción total mensual de las políticas y del óptimo Sol. 5 contra la demanda (línea)."""
    ax.plot(x, df1.Demanda, color="k", ls=":", lw=1.2, label="Demanda", zorder=1)
    for n, k, kw in [("Política 1", "P1", dict(marker="o", ms=3)), ("Política 3", "P3", dict(marker="o", ms=3)),
                     ("Política 2", "P2", dict(marker="o", ms=3, ls="--", lw=1.6, zorder=5))]:
        df = politicas[n]
        ax.plot(x, df.Prod_regular + df.Prod_HE, color=COL[k], label=n, **kw)
    dfa = modelos["Modelo D (Sol. 5)"][0]
    ax.plot(x, dfa.Prod_regular + dfa.Prod_HE, marker="s", ms=3, color=COL["C"], lw=2, label="Óptimo Sol. 5", zorder=4)
    ax.set_xticks(x, _mes(df1.Mes))
    ax.set_ylabel("Unidades / mes (eje desde 7.000)")
    ax.set_ylim(7000, 13000)
    ax.set_title("Producción total vs demanda")


def _panel_inventario(ax, x, df1, politicas, modelos, texto_fs=7):
    etiquetas = [("Política 1", "P1"), ("Política 2", "P2"), ("Política 3", "P3")]
    for n, k in etiquetas:
        ax.plot(x, politicas[n].Inventario_final, marker="o", ms=3, color=COL[k], label=n)
    for n, k in [("Modelo A (Sol. 2)", "A"), ("Modelo D (Sol. 5)", "C")]:
        df = modelos[n][0]
        ax.plot(x, df.Inventario_final - df.Pendientes, marker="s", ms=3, color=COL[k], lw=2,
                label=n.split(" (")[0] + " (I−B)" if k == "A" else "Óptimo Sol. 5")
    ax.axhline(0, color="k", lw=0.6)
    ax.axhline(7500, color="grey", ls=":", lw=0.8)
    ax.text(0, 7550, "capacidad bodega 7.500", fontsize=texto_fs, color="grey")
    ax.set_xticks(x, _mes(df1.Mes))
    ax.set_title("Inventario neto al cierre de mes")


def fig_politicas(politicas, modelos):
    FIG.mkdir(parents=True, exist_ok=True)
    df1 = next(iter(politicas.values()))
    x = np.arange(len(df1))
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.1))
    ax = axs[0]
    _panel_produccion(ax, x, df1, politicas, modelos)
    ax.legend(fontsize=7, ncol=2, frameon=False)
    ax = axs[1]
    _panel_inventario(ax, x, df1, politicas, modelos)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_planes.png", dpi=200)
    plt.close(fig)


def _datos_costos(politicas, modelos):
    nombres, comp = [], {k: [] for k in ["Laboral", "Contrat.+Despido", "Horas extra", "Inventario", "Pendientes", "Multa"]}
    planes = list(politicas.items()) + [(k, v[0]) for k, v in modelos.items()]
    for n, df in planes:
        nombres.append(n.replace(" (Sol. ", "\n(Sol. ").replace("Política", "Pol."))
        comp["Laboral"].append(df.C_laboral.sum() / 1e6)
        comp["Contrat.+Despido"].append((df.C_contratacion.sum() + df.C_despido.sum()) / 1e6)
        comp["Horas extra"].append(df.C_HE.sum() / 1e6)
        comp["Inventario"].append(df.C_inventario.sum() / 1e6)
        comp["Pendientes"].append(df.C_pendientes.sum() / 1e6)
        comp["Multa"].append(df.get("C_multa", df.C_pendientes * 0).sum() / 1e6)
    return nombres, comp


def _dibujar_costos(ax, nombres, comp, fs_total, leyenda):
    base = np.zeros(len(nombres))
    colores = ["#c9d3df", "#e0a33a", "#5b8def", "#2f9e72", "#d0504f", "#8c5bd6"]
    for (k, v), c in zip(comp.items(), colores):
        ax.bar(nombres, v, bottom=base, color=c, label=k)
        base += np.array(v)
    for i, tot in enumerate(base):
        ax.text(i, tot + 4, f"{tot:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                ha="center", fontsize=fs_total, fontweight="bold")
    ax.set_ylim(0, 365)  # eje desde cero: el costo laboral (~260-290) es la mayor parte de cada barra
    ax.set_ylabel("MM$")
    ax.set_title("Costo total por plan y su composición (MM$)")
    leyenda(ax)


def fig_costos(politicas, modelos):
    nombres, comp = _datos_costos(politicas, modelos)
    fig, ax = plt.subplots(figsize=(9, 3.4))
    _dibujar_costos(ax, nombres, comp, 7.5, lambda a: a.legend(fontsize=7, ncol=6, frameon=False, loc="upper center",
                                                                 bbox_to_anchor=(0.5, -0.2)))
    ax.tick_params(axis="x", labelsize=7.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_costos.png", dpi=200)
    plt.close(fig)


def _dibujar_lotes(ax, ind, multi, etiquetas):
    x = np.arange(len(ind))
    esc = ["Base", "+10% espacio", "+10% presupuesto"]
    w = 0.2
    ax.bar(x - 1.5 * w, ind.Q, w, color="#c9d3df", label="EOQ individual (infactible)")
    for k, (e, c) in enumerate(zip(esc, ["#2f9e72", "#5b8def", "#e0a33a"])):
        q = multi[multi.Escenario == e].Q.values
        ax.bar(x + (k - 0.5) * w, q, w, color=c, label=f"Multiproducto – {e}")
    ax.set_xticks(x, etiquetas)
    ax.set_ylabel("Tamaño de lote (u.)")


def fig_lotes(ind, multi):
    fig, ax = plt.subplots(figsize=(9, 2.8))
    _dibujar_lotes(ax, ind, multi, [c.replace("Conjunto ", "") for c in ind.Componente])
    ax.set_title("Tamaños de lote: EOQ individual vs EOQ restringido por espacio y capital")
    ax.legend(fontsize=7, ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_lotes.png", dpi=200)
    plt.close(fig)


def fig_slides(politicas, modelos, ind, multi):
    """Versiones para las diapositivas: se insertan a escala 1:1 (figsize = tamaño final), de modo que
    el texto queda en 11-12 pt. Las figuras del informe (fig1, fig3) no cambian de formato."""
    ancho = {"fig1": 16.0 / 2.54, "fig2": 20.3 / 2.54, "fig3": 13.46 / 2.54}  # cm de inserción -> pulgadas
    with plt.rc_context({"font.size": 12, "legend.fontsize": 11, "axes.titlesize": 12}):
        # Diap. 3: producción y inventario apilados
        fig, axs = plt.subplots(2, 1, figsize=(ancho["fig1"], 6.0), sharex=True)
        df1 = next(iter(politicas.values()))
        x = np.arange(len(df1))
        _panel_produccion(axs[0], x, df1, politicas, modelos)
        axs[0].set_ylabel("u / mes (eje desde 7.000)", fontsize=10)
        axs[0].legend(ncol=2, frameon=False, fontsize=10.5, loc="upper left")
        axs[0].set_ylim(7000, 14800)
        _panel_inventario(axs[1], x, df1, politicas, modelos, texto_fs=10)
        axs[1].legend(ncol=3, frameon=False, fontsize=10.5, loc="upper center", columnspacing=1.0, handlelength=1.6)
        axs[1].set_ylim(-600, 11200)
        axs[1].set_ylabel("Unidades")
        fig.tight_layout()
        fig.savefig(FIG / "slide_fig1_planes.png", dpi=200)
        plt.close(fig)

        # Diap. 5: costos por plan (eje desde 0), leyenda bajo el gráfico
        nombres, comp = _datos_costos(politicas, modelos)
        fig, ax = plt.subplots(figsize=(ancho["fig2"], 4.9))
        _dibujar_costos(ax, nombres, comp, 11,
                        lambda a: a.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.17)))
        ax.tick_params(axis="x", labelsize=10)
        fig.tight_layout()
        fig.savefig(FIG / "slide_fig2_costos.png", dpi=200)
        plt.close(fig)

        # Diap. 7: lotes, etiquetas en dos líneas y leyenda de una columna bajo el gráfico
        fig, ax = plt.subplots(figsize=(ancho["fig3"], 4.6))
        et = ["Motor\nestándar", "Motor\npremium", "Hélice–\nrejilla", "Módulo\nelectr.", "Control\nremoto"]
        _dibujar_lotes(ax, ind, multi, et)
        ax.tick_params(axis="x", labelsize=10)
        ax.legend(ncol=1, frameon=False, fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.2))
        fig.tight_layout()
        fig.savefig(FIG / "slide_fig3_lotes.png", dpi=200)
        plt.close(fig)


def generar(politicas, modelos, ind, multi):
    fig_politicas(politicas, modelos)
    fig_costos(politicas, modelos)
    fig_lotes(ind, multi)
    fig_slides(politicas, modelos, ind, multi)
