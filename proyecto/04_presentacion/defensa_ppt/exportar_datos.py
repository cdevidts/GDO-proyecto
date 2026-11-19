"""Exporta a JSON los datos que usa la presentación de la defensa (todo sale de 02_resultados y del código)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
PROY = AQUI.parent.parent
sys.path.insert(0, str(PROY / "01_codigo"))
import parte3_inventarios as p3  # noqa: E402
from datos import cargar  # noqa: E402

CSV = PROY / "02_resultados" / "csv"
rd = lambda f: pd.read_csv(CSV / f"{f}.csv")  # noqa: E731
A, B, C = rd("modelo_a"), rd("modelo_b"), rd("modelo_c")
pol = {k: rd(f"sol1_politica_{i}") for i, k in enumerate(["P1", "P2", "P3"], 1)}
eoq, lot = rd("sol7_eoq_individual"), rd("sol9_10_multiproducto_lotes")

_, _, inv = cargar()
P = np.array([[c["D"], c["S"]] for c in inv["comp"].values()], float)
H = np.array([c["i"] * c["c"] for c in inv["comp"].values()])


def costo(Q):
    return float(np.sum(P[:, 0] * P[:, 1] / Q + H * Q / 2))


base = costo(p3.multiproducto(inv, 90, 110e6)[0])
pcts = list(range(0, 19))
ahorro_esp = [round(base - costo(p3.multiproducto(inv, 90 * (1 + p / 100), 110e6)[0])) for p in pcts]
ahorro_cap = [round(base - costo(p3.multiproducto(inv, 90, 110e6 * (1 + p / 100))[0])) for p in pcts]

d = {
    "meses": ["Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic", "Ene", "Feb"],
    "demanda": A.Demanda.tolist(),
    "A": {"regular": A.Prod_regular.tolist(), "he": A.Prod_HE.tolist(), "inv": A.Inventario_final.tolist(), "pend": A.Pendientes.tolist()},
    "C": {"he": C.Prod_HE.tolist(), "inv": C.Inventario_final.tolist()},
    "resumen_ABC": {k: {"inv_umes": float(df.Inventario_final.sum()), "pend_umes": float(df.Pendientes.sum()),
                        "costo": float(df.C_total_mes.sum())} for k, df in [("A", A), ("B", B), ("C", C)]},
    "politicas": {k: {c: float(df[c].sum()) for c in ["C_laboral", "C_contratacion", "C_despido", "C_HE", "C_inventario", "C_total_mes"]}
                  for k, df in pol.items()},
    "eoq": eoq[["Componente", "Q", "N", "T_dias", "d_diaria", "L", "ROP", "Espacio", "Capital", "C_relevante"]].round(3).to_dict("records"),
    "multi": lot[lot.Escenario == "Base"][["Q", "N", "T_dias", "Espacio", "Capital"]].round(3).to_dict("records"),
    "sens_pct": pcts, "ahorro_esp": ahorro_esp, "ahorro_cap": ahorro_cap,
}
(AQUI / "datos.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
print("ok", ahorro_esp[:4], ahorro_cap[9:12], ahorro_cap[-1])
