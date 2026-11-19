"""Parte I - Solicitud 1: tres políticas simples de planificación agregada.

Cada política se construye con reglas operacionales explícitas (no con optimización)
y luego se valida contra todas las condiciones del caso.
"""
import math

import pandas as pd

from datos import cargar


def costear(plan, W, H, F, R, O, I, B=None):
    """Arma la tabla mensual y calcula los costos de un plan dado."""
    T = len(plan["meses"])
    B = B or [0] * T
    df = pd.DataFrame(
        dict(
            Mes=plan["meses"],
            Demanda=plan["demanda"],
            Dotacion=W,
            Contrataciones=H,
            Despidos=F,
            Prod_regular=R,
            Cap_regular=[plan["prod_reg"] * w for w in W],
            Prod_HE=O,
            Inventario_final=I,
            Pendientes=B,
        )
    )
    df["C_laboral"] = df.Dotacion * plan["c_lab"]
    df["C_contratacion"] = df.Contrataciones * plan["c_con"]
    df["C_despido"] = df.Despidos * plan["c_des"]
    df["C_HE"] = df.Prod_HE * plan["c_he"]
    df["C_inventario"] = df.Inventario_final * plan["c_inv"]
    df["C_pendientes"] = df.Pendientes * plan["c_pend"]
    df["C_total_mes"] = df[[c for c in df.columns if c.startswith("C_") and c != "C_total_mes"]].sum(axis=1)
    return df


def validar(plan, df, permite_pend=False):
    """Revisa balance, capacidades, límites de dotación, bodega y condiciones de borde."""
    err = []
    I_prev, B_prev, W_prev = plan["I0"], plan["B0"], plan["W0"]
    for _, r in df.iterrows():
        lhs = I_prev - B_prev + r.Prod_regular + r.Prod_HE - r.Demanda
        if abs(lhs - (r.Inventario_final - r.Pendientes)) > 1e-6:
            err.append(f"{r.Mes}: balance no cuadra")
        if r.Prod_regular > plan["prod_reg"] * r.Dotacion + 1e-6:
            err.append(f"{r.Mes}: excede capacidad regular")
        if r.Prod_HE > plan["prod_he"] * r.Dotacion + 1e-6:
            err.append(f"{r.Mes}: excede capacidad HE")
        if not plan["W_min"] <= r.Dotacion <= plan["W_max"]:
            err.append(f"{r.Mes}: dotación fuera de [{plan['W_min']},{plan['W_max']}]")
        if r.Dotacion - W_prev != r.Contrataciones - r.Despidos:
            err.append(f"{r.Mes}: evolución de dotación inconsistente")
        if r.Contrataciones > plan["H_max"] or r.Despidos > plan["F_max"]:
            err.append(f"{r.Mes}: excede máximo de contrataciones/despidos")
        if r.Inventario_final > plan["I_max"] + 1e-6 or r.Inventario_final < -1e-6:
            err.append(f"{r.Mes}: inventario fuera de [0, {plan['I_max']}]")
        if not permite_pend and r.Pendientes > 1e-6:
            err.append(f"{r.Mes}: hay pedidos pendientes")
        I_prev, B_prev, W_prev = r.Inventario_final, r.Pendientes, r.Dotacion
    if I_prev < plan["I_fin"] - 1e-6:
        err.append("Inventario final < requerido")
    if B_prev > plan["B_fin"] + 1e-6:
        err.append("Pendientes al final del horizonte")
    return err


def politica_1(plan):
    """Tasa constante: 20 trabajadores, 10.000 u./mes en tiempo regular, el inventario absorbe."""
    T = len(plan["meses"])
    W = [plan["W0"]] * T
    R = [plan["prod_reg"] * plan["W0"]] * T  # 20 x 500 = 10.000
    I, inv = [], plan["I0"]
    for d, r in zip(plan["demanda"], R):
        inv = inv + r - d
        I.append(inv)
    return costear(plan, W, [0] * T, [0] * T, R, [0] * T, I)


def politica_2(plan):
    """Dotación constante (20); producción = demanda del mes, primero regular, luego HE; I_t = 1.000."""
    T = len(plan["meses"])
    W = [plan["W0"]] * T
    cap = plan["prod_reg"] * plan["W0"]
    R, O, I = [], [], []
    inv_obj = plan["I0"]  # se mantiene 1.000 al cierre de cada mes
    inv = plan["I0"]
    for d in plan["demanda"]:
        req = d + inv_obj - inv  # producción necesaria para cerrar en 1.000
        R.append(min(req, cap))
        O.append(max(req - cap, 0))
        inv = inv + R[-1] + O[-1] - d
        I.append(inv)
    return costear(plan, W, [0] * T, [0] * T, R, O, I)


def politica_3(plan):
    """Persecución con solo producción regular e inventario mínimo.

    Mes a mes se calcula la producción neta requerida (demanda + inventario objetivo - inventario
    disponible) y la dotación entera mínima que la cubre (redondeo hacia arriba), respetando
    límites de dotación y de contrataciones/despidos. El inventario objetivo es 0 salvo en
    febrero, donde es 1.000.

    La regla es miope (no anticipa el límite de +3 contrataciones/mes). Con estos datos basta,
    porque nunca se necesita más de lo permitido; con otros datos `validar` detectaría el
    faltante y habría que adelantar contrataciones.
    """
    T = len(plan["meses"])
    W, H, F, R, I = [], [], [], [], []
    w_prev, inv = plan["W0"], plan["I0"]
    for t, d in enumerate(plan["demanda"]):
        obj = plan["I_fin"] if t == T - 1 else 0
        req = max(d + obj - inv, 0)
        w = math.ceil(req / plan["prod_reg"])
        w = min(max(w, plan["W_min"], w_prev - plan["F_max"]), plan["W_max"], w_prev + plan["H_max"])
        r = min(req, plan["prod_reg"] * w)  # se permite producir bajo la capacidad
        inv = inv + r - d
        W.append(w)
        H.append(max(w - w_prev, 0))
        F.append(max(w_prev - w, 0))
        R.append(r)
        I.append(inv)
        w_prev = w
    return costear(plan, W, H, F, R, [0] * T, I)


def resumen(df):
    return dict(
        costo_total=df.C_total_mes.sum(),
        laboral=df.C_laboral.sum(),
        contratacion=df.C_contratacion.sum(),
        despido=df.C_despido.sum(),
        horas_extra=df.C_HE.sum(),
        inventario=df.C_inventario.sum(),
        pendientes=df.C_pendientes.sum(),
        unid_HE=df.Prod_HE.sum(),
        inv_promedio=df.Inventario_final.mean(),
        inv_max=df.Inventario_final.max(),
        contrataciones=df.Contrataciones.sum(),
        despidos=df.Despidos.sum(),
        dot_min=df.Dotacion.min(),
        dot_max=df.Dotacion.max(),
        capacidad_ociosa=(df.Cap_regular - df.Prod_regular).sum(),
    )


def ejecutar():
    plan, _, _ = cargar()
    out = {}
    for nombre, f in [("Política 1", politica_1), ("Política 2", politica_2), ("Política 3", politica_3)]:
        df = f(plan)
        err = validar(plan, df)
        assert not err, f"{nombre} infactible: {err}"
        out[nombre] = df
    return out


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    for n, df in ejecutar().items():
        print(f"\n===== {n} =====")
        print(df.to_string(index=False))
        print({k: f"{v:,.0f}" for k, v in resumen(df).items()})
