"""Parte I - Análisis complementario (no solicitado explícitamente) para la recomendación y la defensa.

Se resuelven variantes del modelo recomendado (Sol. 5: multa + cero pendientes) y del Modelo A
para cuantificar trade-offs de estabilidad, holgura de horas extra y cambios de costos.
"""
import copy
import sys

import pandas as pd
import pulp

from datos import cargar
from parte1_modelos import SOLVER, construir


def _resolver(plan, extra=None, **kw):
    m, v = construir(plan, **kw)
    if extra:
        extra(m, v, plan)
    m.solve(SOLVER)
    estado = pulp.LpStatus[m.status]
    if estado != "Optimal":
        return dict(estado=estado)
    T = range(len(plan["meses"]))
    return dict(
        estado=estado,
        costo=pulp.value(m.objective),
        dotacion=[round(v["W"][t].value()) for t in T],
        unid_HE=round(sum(v["O"][t].value() for t in T), 6),
        HE_mensual=[round(v["O"][t].value()) for t in T],
        # holgura de HE = capacidad de HE (150 u por trabajador) menos HE usada, por mes
        holgura_HE=[round(plan["prod_he"] * v["W"][t].value() - v["O"][t].value()) for t in T],
        pendientes=round(sum(v["B"][t].value() for t in T), 6),
        inv_total=round(sum(v["I"][t].value() for t in T), 6),
        despidos=sum(round(v["F"][t].value()) for t in T),
        contrataciones=sum(round(v["H"][t].value()) for t in T),
    )


def he_max(frac):
    def f(m, v, plan):
        for t in v["O"]:
            m += v["O"][t] <= frac * plan["prod_he"] * v["W"][t]
    return f


def dotacion_fija(n):
    def f(m, v, plan):
        for t in v["W"]:
            m += v["W"][t] == n
    return f


def con(plan, **cambios):
    p = copy.deepcopy(plan)
    p.update(cambios)
    return p


def ejecutar():
    plan, _, _ = cargar()
    rec = dict(multa=True, cero_pend=True)
    casos = [
        ("Recomendado (Sol. 5)", plan, rec, None),
        ("Sol. 5 con HE <= 80 % de su capacidad", plan, rec, he_max(0.8)),
        ("Sol. 5 con dotación fija 19", plan, rec, dotacion_fija(19)),
        ("Sol. 5 con dotación fija 20 (sin despidos)", plan, rec, dotacion_fija(20)),
        ("Sol. 5 con costo HE +20 % ($3.000)", con(plan, c_he=3000), rec, None),
        ("Sol. 5 con costo despido x2 ($6.000.000)", con(plan, c_des=6_000_000), rec, None),
        ("Modelo A con costo pendiente $1.500 (> mantener)", con(plan, c_pend=1500), {}, None),
        ("Modelo A con costo pendiente $250", con(plan, c_pend=250), {}, None),
        ("Modelo A con costo inventario $500", con(plan, c_inv=500), {}, None),
        ("Modelo A sin límite de ±3 contrataciones/despidos", con(plan, H_max=None, F_max=None), {}, None),
        ("Modelo A con productividad HE 100 u/trab-mes", con(plan, prod_he=100), {}, None),
        ("Sol. 5 con demanda de diciembre +5 % (13.125)", con(plan, demanda=plan["demanda"][:9] + [13125] + plan["demanda"][10:]), rec, None),
    ]
    filas = []
    for nombre, p, kw, extra in casos:
        r = _resolver(p, extra, **kw)
        r["Escenario"] = nombre
        filas.append(r)
    df = pd.DataFrame(filas)
    cols = ["Escenario", "estado", "costo", "dotacion", "contrataciones", "despidos", "unid_HE", "HE_mensual",
            "holgura_HE", "inv_total", "pendientes"]
    return df[cols]


def unicidad_optimo(plan, tol=10.0, variables=("W", "R", "O", "I", "B"), **kw):
    """Comprueba si el óptimo es único: con el costo acotado por Z* + tol ($), minimiza y maximiza cada
    variable en cada mes y devuelve el mayor rango (max - min) hallado por variable. Un rango ~0
    (< 0,1 u; el resto es la tolerancia de costo y ruido numérico) significa que no hay óptimos alternativos.
    No se ejecuta desde run_all.py (son ~120 optimizaciones por modelo):  python parte1_sensibilidad.py --unicidad
    """
    m0, _ = construir(plan, **kw)
    m0.solve(SOLVER)
    z = pulp.value(m0.objective)
    T = range(len(plan["meses"]))
    rangos = {}
    for nombre in variables:
        mayor = 0.0
        for t in T:
            extremos = []
            for sentido in (pulp.LpMinimize, pulp.LpMaximize):
                m, v = construir(plan, **kw)
                m += m.objective <= z + tol, "tope_costo"
                m.setObjective(v[nombre][t])
                m.sense = sentido
                m.solve(SOLVER)
                extremos.append(v[nombre][t].value())
            mayor = max(mayor, extremos[1] - extremos[0])
        rangos[nombre] = round(mayor, 4)
    return z, rangos


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 80)
    if "--unicidad" in sys.argv:
        plan0, _, _ = cargar()
        for nombre, kw in [("Modelo A", {}), ("Modelo B", dict(multa=True)), ("Modelo C", dict(cero_pend=True))]:
            z, rangos = unicidad_optimo(plan0, **kw)
            print(f"{nombre}: Z* = {z:,.0f}; mayor rango (max - min) de cada variable en el conjunto óptimo: {rangos}")
    else:
        print(ejecutar().to_string(index=False))
