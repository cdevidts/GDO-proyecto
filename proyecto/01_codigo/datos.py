"""Carga de los datos oficiales del Proyecto Ventisur desde el Excel entregado por el curso.

Todos los scripts leen los parámetros desde aquí, de modo que si el equipo docente cambia
un dato en el Excel, basta volver a ejecutar `run_all.py`.
"""
from pathlib import Path

import openpyxl

RAIZ = Path(__file__).resolve().parents[1]
EXCEL = RAIZ / "00_enunciado_y_datos" / "Datos_Proyecto_Ventisur_1.xlsx"
RESULTADOS = RAIZ / "02_resultados"


def cargar():
    wb = openpyxl.load_workbook(EXCEL, data_only=True)

    # ---------- Parte I: planificación agregada ----------
    ws = wb["01_Planificacion"]
    meses = [ws.cell(r, 1).value for r in range(4, 16)]
    demanda = [ws.cell(r, 2).value for r in range(4, 16)]
    p = {ws.cell(r, 4).value: ws.cell(r, 5).value for r in range(4, 21) if ws.cell(r, 4).value}
    dot_min, dot_max = (int(x) for x in str(p["Dotación mínima / máxima"]).split("/"))
    plan = dict(
        meses=meses,
        demanda=demanda,
        W0=p["Dotación inicial (trabajadores)"],
        prod_reg=p["Productividad regular (u./trabajador-mes)"],
        prod_he=p["Capacidad horas extra (u./trabajador-mes)"],
        c_lab=p["Costo mensual por trabajador ($)"],
        c_con=p["Costo contratación por trabajador ($)"],
        c_des=p["Costo despido por trabajador ($)"],
        c_he=p["Costo horas extra ($/unidad)"],
        c_inv=p["Costo inventario ($/unidad-mes)"],
        c_pend=p["Costo faltante ($/unidad-mes)"],
        I0=p["Inventario inicial (u.)"],
        I_fin=p["Inventario final requerido (u.)"],
        I_max=p["Capacidad máxima bodega producto terminado (u.)"],
        W_min=dot_min,
        W_max=dot_max,
        H_max=p["Máximo de contrataciones por mes"],
        F_max=p["Máximo de despidos por mes"],
        B0=0,          # pedidos pendientes iniciales (enunciado)
        B_fin=0,       # pedidos pendientes al final del horizonte (enunciado)
        multa=3_000_000,   # Solicitud 3 (enunciado)
        pct_multa=0.01,    # Solicitud 3: umbral = 1 % de la demanda del mes
    )

    # ---------- Parte II: transición ----------
    ws = wb["02_Transicion"]
    tasa = ws["B4"].value
    mezcla = {ws.cell(r, 2).value: ws.cell(r, 3).value for r in range(9, 12)}
    modelos = list(mezcla)
    bom = {
        ws.cell(r, 1).value: dict(zip(modelos, (ws.cell(r, c).value for c in range(2, 5))))
        for r in range(16, 21)
    }
    transicion = dict(tasa=tasa, mezcla=mezcla, bom=bom)

    # ---------- Parte III: inventarios ----------
    ws = wb["03_Inventarios"]
    comp = {}
    for r in range(4, 9):
        comp[ws.cell(r, 1).value] = dict(
            D=ws.cell(r, 2).value,
            S=ws.cell(r, 3).value,
            c=ws.cell(r, 4).value,
            i=ws.cell(r, 5).value,
            v=ws.cell(r, 6).value,
            L=ws.cell(r, 7).value,
        )
    dias = ws["B12"].value

    ws = wb["04_Restricciones"]
    escenarios = {ws.cell(r, 1).value: (ws.cell(r, 2).value, ws.cell(r, 3).value) for r in range(10, 13)}
    inventarios = dict(comp=comp, dias=dias, V=ws["B4"].value, K=ws["B5"].value, escenarios=escenarios)

    return plan, transicion, inventarios


if __name__ == "__main__":
    import pprint

    for bloque in cargar():
        pprint.pprint(bloque, sort_dicts=False)
