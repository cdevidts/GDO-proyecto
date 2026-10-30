"""Parte III - Solicitudes 7 a 10: EOQ individuales, factibilidad conjunta, EOQ multiproducto
restringido (espacio y capital) y análisis de sensibilidad.

Modelo multiproducto (lotes completos, como en Sesión 4):
    min  sum_i  D_i S_i / Q_i + h_i Q_i / 2
    s.a. sum_i v_i Q_i <= V          (espacio, m3)       multiplicador mu
         sum_i c_i Q_i <= K          (capital, $)        multiplicador lam
         Q_i > 0
Condición de KKT:  Q_i = sqrt( 2 D_i S_i / (h_i + 2 mu v_i + 2 lam c_i) ),
con mu, lam >= 0 y holgura complementaria. Se resuelve con bisección anidada sobre los
multiplicadores y se verifica independientemente con SLSQP (scipy).
"""
import math

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from datos import cargar


def eoq_individual(inv):
    filas = []
    for nombre, p in inv["comp"].items():
        h = p["i"] * p["c"]
        Q = math.sqrt(2 * p["D"] * p["S"] / h)
        N = p["D"] / Q
        d = p["D"] / inv["dias"]
        T = Q / d
        filas.append(
            dict(
                Componente=nombre, D=p["D"], S=p["S"], c=p["c"], h=h, Q=Q, N=N,
                T_dias=T, d_diaria=d, L=p["L"], ROP=d * p["L"],
                C_ordenar=p["D"] * p["S"] / Q, C_mantener=h * Q / 2,
                Espacio=p["v"] * Q, Capital=p["c"] * Q,
            )
        )
    df = pd.DataFrame(filas)
    df["C_relevante"] = df.C_ordenar + df.C_mantener
    return df


def _Q(p, h, mu, lam):
    return np.sqrt(2 * p[:, 0] * p[:, 1] / (h + 2 * mu * p[:, 3] + 2 * lam * p[:, 2]))


def multiproducto(inv, V, K):
    """Devuelve (Q, mu, lam) óptimos por KKT con bisección anidada."""
    p = np.array([[c["D"], c["S"], c["c"], c["v"]] for c in inv["comp"].values()], float)
    h = np.array([c["i"] * c["c"] for c in inv["comp"].values()])
    esp = lambda Q: p[:, 3] @ Q  # noqa: E731
    cap = lambda Q: p[:, 2] @ Q  # noqa: E731

    def mu_dado_lam(lam):
        if esp(_Q(p, h, 0.0, lam)) <= V:
            return 0.0
        lo, hi = 0.0, 1.0
        while esp(_Q(p, h, hi, lam)) > V:
            hi *= 2
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if esp(_Q(p, h, mid, lam)) > V else (lo, mid)
        return hi

    if cap(_Q(p, h, mu_dado_lam(0.0), 0.0)) <= K:
        lam = 0.0
    else:
        lo, hi = 0.0, 1e-6
        while cap(_Q(p, h, mu_dado_lam(hi), hi)) > K:
            hi *= 2
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if cap(_Q(p, h, mu_dado_lam(mid), mid)) > K else (lo, mid)
        lam = hi
    mu = mu_dado_lam(lam)
    return _Q(p, h, mu, lam), mu, lam


def verificar_slsqp(inv, V, K):
    """Resuelve el mismo problema con un optimizador no lineal genérico (control cruzado)."""
    p = np.array([[c["D"], c["S"], c["c"], c["v"]] for c in inv["comp"].values()], float)
    h = np.array([c["i"] * c["c"] for c in inv["comp"].values()])
    f = lambda Q: np.sum(p[:, 0] * p[:, 1] / Q + h * Q / 2)  # noqa: E731
    cons = [
        {"type": "ineq", "fun": lambda Q: (V - p[:, 3] @ Q) / V},
        {"type": "ineq", "fun": lambda Q: (K - p[:, 2] @ Q) / K},
    ]
    x0 = np.full(len(p), 1000.0)
    r = minimize(f, x0, constraints=cons, bounds=[(1, None)] * len(p), method="SLSQP",
                 options={"ftol": 1e-12, "maxiter": 1000})
    return r.x, r.fun


def tabla_multiproducto(inv, V, K, escenario):
    Q, mu, lam = multiproducto(inv, V, K)
    filas = []
    for (nombre, c), q in zip(inv["comp"].items(), Q):
        h = c["i"] * c["c"]
        d = c["D"] / inv["dias"]
        T = q / d
        L = c["L"]
        k = math.floor(L / T)  # pedidos en tránsito al momento de reordenar
        filas.append(
            dict(
                Escenario=escenario, Componente=nombre, Q=q, N=c["D"] / q, T_dias=T, L=L,
                ROP_posicion=d * L,               # punto de reorden sobre la posición de inventario
                Pedidos_en_transito=k,
                ROP_fisico=d * L - k * q,         # equivalente sobre inventario físico
                C_ordenar=c["D"] * c["S"] / q, C_mantener=h * q / 2,
                Espacio=c["v"] * q, Capital=c["c"] * q,
            )
        )
    df = pd.DataFrame(filas)
    df["C_relevante"] = df.C_ordenar + df.C_mantener
    res = dict(
        Escenario=escenario, V=V, K=K, mu=mu, lam=lam,
        Espacio_usado=df.Espacio.sum(), Capital_usado=df.Capital.sum(),
        Espacio_activa=abs(df.Espacio.sum() - V) < 1e-6 * V,
        Capital_activa=abs(df.Capital.sum() - K) < 1e-6 * K,
        Costo_relevante=df.C_relevante.sum(),
        Pedidos_totales=df.N.sum(),
    )
    _, z = verificar_slsqp(inv, V, K)
    res["Costo_SLSQP"] = z
    assert abs(z - res["Costo_relevante"]) / z < 1e-5, "KKT y SLSQP no coinciden"
    return df, res


def ejecutar():
    _, _, inv = cargar()
    ind = eoq_individual(inv)
    fact = dict(
        Espacio_EOQ=ind.Espacio.sum(), V=inv["V"], Exceso_espacio=ind.Espacio.sum() - inv["V"],
        Capital_EOQ=ind.Capital.sum(), K=inv["K"], Exceso_capital=ind.Capital.sum() - inv["K"],
    )
    tablas, resumenes = [], []
    for esc, (V, K) in inv["escenarios"].items():
        df, res = tabla_multiproducto(inv, V, K, esc)
        tablas.append(df)
        resumenes.append(res)
    # escenarios adicionales que ayudan a explicar el valor marginal (no solicitados)
    extra = [("Solo espacio (sin capital)", inv["V"], 1e18), ("Solo capital (sin espacio)", 1e18, inv["K"])]
    for esc, V, K in extra:
        df, res = tabla_multiproducto(inv, V, K, esc)
        tablas.append(df)
        resumenes.append(res)
    return ind, fact, pd.concat(tablas, ignore_index=True), pd.DataFrame(resumenes)


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.float_format", lambda x: f"{x:,.4f}")
    ind, fact, multi, res = ejecutar()
    print(ind.to_string(index=False))
    print(fact)
    print(multi.to_string(index=False))
    print(res.to_string(index=False))
