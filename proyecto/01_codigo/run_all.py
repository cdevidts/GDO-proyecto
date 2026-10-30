"""Ejecuta el proyecto completo y regenera todos los respaldos en 02_resultados/.

Uso:  python run_all.py
"""
import json

import pandas as pd

import generar_excel
import graficos
import parte1_modelos
import parte1_politicas
import parte1_sensibilidad
import parte2_requerimientos
import parte3_inventarios
from datos import RESULTADOS, cargar

SENS1_NOTA = ("Análisis complementario: variantes del modelo recomendado (Sol. 5) y del Modelo A "
              "para cuantificar estabilidad, holgura de HE y efecto de cambios de costos.")


def main():
    RESULTADOS.mkdir(exist_ok=True)
    plan, tr, inv = cargar()

    politicas = parte1_politicas.ejecutar()
    modelos = parte1_modelos.ejecutar()
    sens1 = parte1_sensibilidad.ejecutar()
    prod, req = parte2_requerimientos.ejecutar()
    ind, fact, multi, multi_res = parte3_inventarios.ejecutar()

    # ---- CSV de respaldo ----
    csv = RESULTADOS / "csv"
    csv.mkdir(exist_ok=True)
    for n, df in politicas.items():
        df.to_csv(csv / f"sol1_{n.replace(' ', '_').replace('í', 'i').lower()}.csv", index=False)
    for n, (df, _) in modelos.items():
        df.to_csv(csv / f"{n.split(' (')[0].replace(' ', '_').lower()}.csv", index=False)
    sens1.to_csv(csv / "sensibilidad_parte1.csv", index=False)
    prod.to_csv(csv / "sol6_produccion_por_modelo.csv", index=False)
    req.to_csv(csv / "sol6_requerimientos.csv", index=False)
    ind.to_csv(csv / "sol7_eoq_individual.csv", index=False)
    multi.to_csv(csv / "sol9_10_multiproducto_lotes.csv", index=False)
    multi_res.to_csv(csv / "sol9_10_multiproducto_resumen.csv", index=False)

    # ---- resumen numérico (lo usa el informe) ----
    resumen = {
        "politicas": {n: parte1_politicas.resumen(df) for n, df in politicas.items()},
        "modelos": {n: {**parte1_politicas.resumen(df), "FO": z,
                        "multas": int(df.get("Multa_activa", pd.Series([0])).sum())}
                    for n, (df, z) in modelos.items()},
        "relajacion_lineal_A": parte1_modelos.relajacion_lineal(plan),
        "big_M": parte1_modelos.big_m(plan),
        "factibilidad_EOQ": fact,
        "multiproducto": multi_res.to_dict("records"),
    }
    with open(RESULTADOS / "resumen.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=2, default=float)

    parte3_inventarios.escribir_modelo(inv, multi_res)
    generar_excel.generar(plan, tr, inv, politicas, modelos, sens1, ind, multi_res, SENS1_NOTA)
    graficos.generar(politicas, modelos, ind, multi)

    # ---- consola ----
    print("Costos Parte I:")
    for n, df in politicas.items():
        print(f"  {n:<20} {df.C_total_mes.sum():>16,.0f}")
    for n, (_, z) in modelos.items():
        print(f"  {n:<20} {z:>16,.0f}")
    print("Factibilidad EOQ individuales:", {k: round(v, 2) for k, v in fact.items()})
    print(multi_res[["Escenario", "mu", "lam", "Espacio_usado", "Capital_usado", "Costo_relevante"]].to_string(index=False))
    print(f"\nListo. Resultados en {RESULTADOS}")


if __name__ == "__main__":
    main()
