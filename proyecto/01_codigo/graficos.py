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


def fig_politicas(politicas, modelos):
    FIG.mkdir(parents=True, exist_ok=True)
    df1 = next(iter(politicas.values()))
    x = np.arange(len(df1))
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.1))
    ax = axs[0]
    ax.bar(x, df1.Demanda, color="#e6e9ee", label="Demanda")
    etiquetas = [("Política 1", "P1"), ("Política 2", "P2"), ("Política 3", "P3")]
    for n, k in etiquetas:
        df = politicas[n]
        ax.plot(x, df.Prod_regular + df.Prod_HE, marker="o", ms=3, color=COL[k], label=n)
    dfa = modelos["Modelo D (Sol. 5)"][0]
    ax.plot(x, dfa.Prod_regular + dfa.Prod_HE, marker="s", ms=3, color=COL["C"], lw=2, label="Óptimo Sol. 5")
    ax.set_xticks(x, _mes(df1.Mes))
    ax.set_ylabel("Unidades / mes")
    ax.set_ylim(7000, 13000)
    ax.set_title("Producción total vs demanda")
    ax.legend(fontsize=7, ncol=2, frameon=False)
    ax = axs[1]
    for n, k in etiquetas:
        ax.plot(x, politicas[n].Inventario_final, marker="o", ms=3, color=COL[k], label=n)
    for n, k in [("Modelo A (Sol. 2)", "A"), ("Modelo D (Sol. 5)", "C")]:
        df = modelos[n][0]
        ax.plot(x, df.Inventario_final - df.Pendientes, marker="s", ms=3, color=COL[k], lw=2,
                label=n.split(" (")[0] + " (I−B)" if k == "A" else "Óptimo Sol. 5")
    ax.axhline(0, color="k", lw=0.6)
    ax.axhline(7500, color="grey", ls=":", lw=0.8)
    ax.text(0, 7550, "capacidad bodega 7.500", fontsize=7, color="grey")
    ax.set_xticks(x, _mes(df1.Mes))
    ax.set_title("Inventario neto al cierre de mes")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig1_planes.png", dpi=200)
    plt.close(fig)


def fig_costos(politicas, modelos):
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
    fig, ax = plt.subplots(figsize=(9, 3.0))
    base = np.zeros(len(nombres))
    colores = ["#c9d3df", "#e0a33a", "#5b8def", "#2f9e72", "#d0504f", "#8c5bd6"]
    for (k, v), c in zip(comp.items(), colores):
        ax.bar(nombres, v, bottom=base, color=c, label=k)
        base += np.array(v)
    for i, tot in enumerate(base):
        ax.text(i, tot + 0.8, f"{tot:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                ha="center", fontsize=7.5, fontweight="bold")
    ax.set_ylim(250, 350)
    ax.set_ylabel("MM$ (eje desde 250)")
    ax.set_title("Costo total por plan y su composición (MM$)")
    ax.legend(fontsize=7, ncol=6, frameon=False, loc="upper right")
    ax.tick_params(axis="x", labelsize=7.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_costos.png", dpi=200)
    plt.close(fig)


def fig_lotes(ind, multi):
    comps = list(ind.Componente)
    x = np.arange(len(comps))
    esc = ["Base", "+10% espacio", "+10% presupuesto"]
    w = 0.2
    fig, ax = plt.subplots(figsize=(9, 2.8))
    ax.bar(x - 1.5 * w, ind.Q, w, color="#c9d3df", label="EOQ individual (infactible)")
    for k, (e, c) in enumerate(zip(esc, ["#2f9e72", "#5b8def", "#e0a33a"])):
        q = multi[multi.Escenario == e].Q.values
        ax.bar(x + (k - 0.5) * w, q, w, color=c, label=f"Multiproducto – {e}")
    ax.set_xticks(x, [c.replace("Conjunto ", "") for c in comps])
    ax.set_ylabel("Tamaño de lote (u.)")
    ax.set_title("Tamaños de lote: EOQ individual vs EOQ restringido por espacio y capital")
    ax.legend(fontsize=7, ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig3_lotes.png", dpi=200)
    plt.close(fig)


def generar(politicas, modelos, ind, multi):
    fig_politicas(politicas, modelos)
    fig_costos(politicas, modelos)
    fig_lotes(ind, multi)
