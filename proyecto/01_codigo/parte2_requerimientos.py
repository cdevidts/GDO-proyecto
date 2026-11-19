"""Parte II - Solicitud 6: desagregación de la tasa oficial y requerimientos de componentes.

Producción por modelo  = tasa agregada x participación.
Requerimiento de componente j = sum_modelos (unidades de j por modelo) x producción del modelo.
"""
import pandas as pd

from datos import cargar


def ejecutar():
    _, tr, inv = cargar()
    tasa, mezcla, bom = tr["tasa"], tr["mezcla"], tr["bom"]

    prod = pd.DataFrame(
        {
            "Modelo": list(mezcla),
            "Participacion": list(mezcla.values()),
            "Prod_mensual": [tasa * s for s in mezcla.values()],
        }
    )
    prod["Prod_anual"] = prod.Prod_mensual * 12

    filas = []
    for comp, uso in bom.items():
        mensual = sum(uso[mod] * tasa * s for mod, s in mezcla.items())
        filas.append(
            dict(
                Componente=comp,
                **{f"Uso_{mod.split()[-1]}": uso[mod] for mod in mezcla},
                Req_mensual=mensual,
                Req_anual=mensual * 12,
                Req_anual_oficial=inv["comp"][comp]["D"],
            )
        )
    req = pd.DataFrame(filas)
    req["Coincide_oficial"] = req.Req_anual == req.Req_anual_oficial
    return prod, req


if __name__ == "__main__":
    prod, req = ejecutar()
    print(prod.to_string(index=False))
    print()
    print(req.to_string(index=False))
