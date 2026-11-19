"""Parte I - Solicitudes 2 a 5: modelos de optimización de planificación agregada (PuLP + CBC).

Modelo A (Sol. 2): plan de costo mínimo, se permiten pedidos pendientes.
Modelo B (Sol. 3): A + multa contractual de $3.000.000 si B_t > 1 % d_t (variable binaria y_t).
Modelo C (Sol. 4): A + cero pedidos pendientes al cierre de todo mes (B_t = 0).
Modelo D (Sol. 5): B + cero pedidos pendientes (B_t = 0).

Notación (t = 1..12, marzo..febrero):
  W_t dotación, H_t contrataciones, F_t despidos      (enteras)
  R_t producción regular, O_t producción en HE         (continuas, unidades)
  I_t inventario final, B_t pedidos pendientes finales  (continuas, unidades)
  y_t = 1 si se gatilla la multa del mes t             (binaria, solo B y D)
"""
import pulp

from datos import RESULTADOS, cargar
from parte1_politicas import costear, validar

SOLVER = pulp.PULP_CBC_CMD(msg=False)


def big_m(plan):
    """Cota superior válida de B_t - 0,01 d_t.

    En el peor caso no se produce nada hasta t (la producción regular puede ser 0), por lo
    que los pendientes nunca superan la demanda acumulada menos el inventario inicial.
    M_t = sum_{k<=t} d_k - I_0 - 0,01 d_t es una cota válida y simple (existen cotas más ajustadas:
    ignora las condiciones finales B_12 = 0 e I_12 >= 1.000 y la capacidad máxima mensual).
    """
    acum, M = 0, []
    for d in plan["demanda"]:
        acum += d
        M.append(acum - plan["I0"] - plan["pct_multa"] * d)
    return M


def big_m_ajustada(plan):
    """Cota más ajustada de B_t - 0,01 d_t (solo para comparar con big_m; el modelo usa big_m).

    Resuelve, para cada mes t, el LP "maximizar B_t con I_t = 0" sobre el Modelo A, es decir, considera
    las condiciones finales (B_12 = 0, I_12 >= 1.000) y la capacidad máxima mensual. Coincide con big_m
    hasta abril y es mucho menor desde el peak (p. ej. diciembre: 9.375 contra 96.875).
    """
    T = range(len(plan["meses"]))
    M = []
    for t in T:
        m, v = construir(plan)
        m += v["I"][t] == 0, "sin_inventario_simultaneo"
        m.setObjective(v["B"][t])
        m.sense = pulp.LpMaximize
        m.solve(SOLVER)
        M.append(max(v["B"][t].value() - plan["pct_multa"] * plan["demanda"][t], 0.0))
    return M


def costo_optimo(plan, **kw):
    """Valor óptimo del modelo sin escribir archivos (sirve para comparar variantes, p. ej. otro M)."""
    m, _ = construir(plan, **kw)
    m.solve(SOLVER)
    return pulp.value(m.objective)


def construir(plan, multa=False, cero_pend=False, nombre="ModeloA", M=None):
    T = range(len(plan["meses"]))
    d = plan["demanda"]
    m = pulp.LpProblem(nombre, pulp.LpMinimize)

    W = pulp.LpVariable.dicts("W", T, lowBound=plan["W_min"], upBound=plan["W_max"], cat="Integer")
    H = pulp.LpVariable.dicts("H", T, lowBound=0, upBound=plan["H_max"], cat="Integer")
    F = pulp.LpVariable.dicts("F", T, lowBound=0, upBound=plan["F_max"], cat="Integer")
    R = pulp.LpVariable.dicts("R", T, lowBound=0)
    O = pulp.LpVariable.dicts("O", T, lowBound=0)
    I = pulp.LpVariable.dicts("I", T, lowBound=0, upBound=plan["I_max"])
    B = pulp.LpVariable.dicts("B", T, lowBound=0)

    costo = pulp.lpSum(
        plan["c_lab"] * W[t]
        + plan["c_con"] * H[t]
        + plan["c_des"] * F[t]
        + plan["c_he"] * O[t]
        + plan["c_inv"] * I[t]
        + plan["c_pend"] * B[t]
        for t in T
    )

    for t in T:
        W_prev = plan["W0"] if t == 0 else W[t - 1]
        I_prev = plan["I0"] if t == 0 else I[t - 1]
        B_prev = plan["B0"] if t == 0 else B[t - 1]
        m += W[t] == W_prev + H[t] - F[t], f"dotacion_{t}"
        m += R[t] <= plan["prod_reg"] * W[t], f"cap_regular_{t}"
        m += O[t] <= plan["prod_he"] * W[t], f"cap_HE_{t}"
        m += I_prev - B_prev + R[t] + O[t] - d[t] == I[t] - B[t], f"balance_{t}"
        if cero_pend:
            m += B[t] == 0, f"cero_pendientes_{t}"

    m += I[T[-1]] >= plan["I_fin"], "inventario_final"
    m += B[T[-1]] <= plan["B_fin"], "pendientes_final"

    y = None
    if multa:
        y = pulp.LpVariable.dicts("y", T, cat="Binary")
        M = M if M is not None else big_m(plan)
        for t in T:
            # Si B_t supera el 1 % de d_t, obliga y_t = 1 (y se paga la multa)
            m += B[t] <= plan["pct_multa"] * d[t] + M[t] * y[t], f"multa_{t}"
        costo += pulp.lpSum(plan["multa"] * y[t] for t in T)

    m += costo
    return m, dict(W=W, H=H, F=F, R=R, O=O, I=I, B=B, y=y)


def resolver(plan, **kw):
    m, v = construir(plan, **kw)
    (RESULTADOS / "modelos_lp").mkdir(parents=True, exist_ok=True)
    m.writeLP(str(RESULTADOS / "modelos_lp" / f"{m.name}.lp"))
    m.solve(SOLVER)
    assert pulp.LpStatus[m.status] == "Optimal", f"{m.name}: {pulp.LpStatus[m.status]}"
    T = range(len(plan["meses"]))
    val = lambda x: round(x.value(), 6) + 0.0  # noqa: E731  (+0.0 elimina -0.0)
    sol = {k: [val(var[t]) for t in T] for k, var in v.items() if var is not None}
    df = costear(plan, sol["W"], sol["H"], sol["F"], sol["R"], sol["O"], sol["I"], sol["B"])
    if v["y"] is not None:
        df["Multa_activa"] = [int(round(x)) for x in sol["y"]]
        df["Umbral_1pct"] = [plan["pct_multa"] * x for x in plan["demanda"]]
        df["C_multa"] = df.Multa_activa * plan["multa"]
        df["C_total_mes"] += df.C_multa
    err = validar(plan, df, permite_pend=True)
    assert not err, f"{m.name}: {err}"
    assert abs(df.C_total_mes.sum() - pulp.value(m.objective)) < 1, "costo recalculado != FO"
    return df, pulp.value(m.objective)


def relajacion_lineal(plan, **kw):
    """Valor del modelo con W, H, F continuas (sirve para discutir el efecto de la integralidad)."""
    m, v = construir(plan, **kw)
    for var in list(v["W"].values()) + list(v["H"].values()) + list(v["F"].values()):
        var.cat = "Continuous"
    m.solve(SOLVER)
    return pulp.value(m.objective)


def ejecutar():
    plan, _, _ = cargar()
    return {
        "Modelo A (Sol. 2)": resolver(plan, nombre="ModeloA_Sol2"),
        "Modelo B (Sol. 3)": resolver(plan, multa=True, nombre="ModeloB_Sol3_multa"),
        "Modelo C (Sol. 4)": resolver(plan, cero_pend=True, nombre="ModeloC_Sol4_cero_pendientes"),
        "Modelo D (Sol. 5)": resolver(plan, multa=True, cero_pend=True, nombre="ModeloD_Sol5_multa_y_cero_pend"),
    }


if __name__ == "__main__":
    import pandas as pd

    pd.set_option("display.width", 250)
    plan, _, _ = cargar()
    for n, (df, z) in ejecutar().items():
        print(f"\n===== {n}: costo = {z:,.0f} =====")
        cols = ["Mes", "Demanda", "Dotacion", "Contrataciones", "Despidos", "Prod_regular", "Cap_regular",
                "Prod_HE", "Inventario_final", "Pendientes"] + (["Multa_activa"] if "Multa_activa" in df else [])
        print(df[cols].to_string(index=False))
    print("\nRelajación lineal A:", f"{relajacion_lineal(plan):,.0f}")
    print("Relajación lineal C:", f"{relajacion_lineal(plan, cero_pend=True):,.0f}")
    print("Big-M:", big_m(plan))
    Mt = big_m_ajustada(plan)
    print("Big-M ajustada:", Mt)
    print("Z_B con M simple:", f"{costo_optimo(plan, multa=True):,.0f}", "| con M ajustada:",
          f"{costo_optimo(plan, multa=True, M=Mt):,.0f}")
