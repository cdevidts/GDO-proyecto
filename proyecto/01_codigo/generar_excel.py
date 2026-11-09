"""Genera 02_resultados/Resultados_Ventisur.xlsx.

Las decisiones (dotación, producción, lotes, multiplicadores) se escriben como valores y todo lo
derivado (capacidades, balance, costos, EOQ, uso de recursos) como FÓRMULAS de Excel, de modo que
la planilla permite verificar los resultados de Python de forma independiente.
"""
from numbers import Number
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import Rule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.styles.numbers import NumberFormat
from openpyxl.utils import get_column_letter

from datos import RESULTADOS

# ---- sistema visual Ventisur, registro sobrio (mismos hex que informe, figuras y presentación) ----
TINTA, TINTA3, NAVY, FILETE = "1C2127", "6B7580", "10233D", "D9DDE2"
EXITO, ALERTA = "2E7D4F", "B42318"  # solo para chequeos, siempre con ícono y texto
FUENTE = "Calibri"
ENCABEZADO = PatternFill("solid", fgColor=NAVY)
CREMA = PatternFill("solid", fgColor="FDF6E3")        # valor del modelo (decisión o multiplicador)
RECOMENDADO = PatternFill("solid", fgColor="EAF1F8")  # plan / escenario recomendado (Sol. 5, base)
NEGRITA = Font(name=FUENTE, size=10, bold=True, color=TINTA)
TITULO = Font(name=FUENTE, size=12, bold=True, color=TINTA)
NOTA = Font(name=FUENTE, size=9, italic=True, color=TINTA3)
LINEA_TINTA = Side(style="thin", color=TINTA)
LINEA_FILETE = Side(style="thin", color=FILETE)
# pestañas con el color fijo de cada plan (Modelo C = Sol. 5: mismo plan, acento)
COLOR_PLAN = {"P1": "D9A336", "P2": "CC5F22", "P3": "8C3B2F", "ModA": "2B333C", "ModB": "98A2AC",
              "ModC": "1F5FAE", "ModD": "1F5FAE"}
LEYENDA = "Crema = valor del modelo (decisión); blanco = fórmula."
MILES = "#,##0"
DEC = "#,##0.00"


def _encabezado(ws, fila, nombres):
    for j, n in enumerate(nombres, 1):
        c = ws.cell(fila, j, n)
        c.font = Font(name=FUENTE, size=10, bold=True, color="FFFFFF")
        c.fill = ENCABEZADO
        c.border = Border(bottom=LINEA_TINTA)
        c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="bottom")


def _marcar_fila(ws, fila, ncol, relleno=RECOMENDADO):
    for j in range(1, ncol + 1):
        ws.cell(fila, j).fill = relleno


def _chequeo(ws, ref, ok, error):
    """Formato condicional de una celda de chequeo: verde con ✓ si `ok`, rojo con ✗ si `error`.
    La fórmula no cambia: el ícono lo antepone el formato de número del estilo condicional."""
    for cond, color, icono, nid in [(ok, EXITO, "✓", 190), (error, ALERTA, "✗", 191)]:
        dxf = DifferentialStyle(font=Font(bold=True, color=color),
                                numFmt=NumberFormat(numFmtId=nid, formatCode=f'"{icono} "@'))
        ws.conditional_formatting.add(ref, Rule(type="expression", formula=[cond], stopIfTrue=True, dxf=dxf))


def _anchos(ws, ancho=14, primera=24):
    ws.column_dimensions["A"].width = primera
    for j in range(2, 30):
        ws.column_dimensions[get_column_letter(j)].width = ancho


def hoja_parametros(wb, plan):
    ws = wb.create_sheet("Parametros")
    filas = [
        ("W0", "Dotación inicial", plan["W0"]),
        ("q_reg", "Productividad regular (u/trab-mes)", plan["prod_reg"]),
        ("q_he", "Capacidad HE (u/trab-mes)", plan["prod_he"]),
        ("c_lab", "Costo laboral ($/trab-mes)", plan["c_lab"]),
        ("c_con", "Costo contratación ($/trab)", plan["c_con"]),
        ("c_des", "Costo despido ($/trab)", plan["c_des"]),
        ("c_he", "Costo HE ($/u)", plan["c_he"]),
        ("c_inv", "Costo inventario ($/u-mes)", plan["c_inv"]),
        ("c_pend", "Costo pendiente ($/u-mes)", plan["c_pend"]),
        ("I0", "Inventario inicial", plan["I0"]),
        ("I_fin", "Inventario final requerido", plan["I_fin"]),
        ("I_max", "Capacidad bodega", plan["I_max"]),
        ("W_min", "Dotación mínima", plan["W_min"]),
        ("W_max", "Dotación máxima", plan["W_max"]),
        ("H_max", "Máx. contrataciones/mes", plan["H_max"]),
        ("F_max", "Máx. despidos/mes", plan["F_max"]),
        ("multa", "Multa contractual ($/mes)", plan["multa"]),
        ("pct", "Umbral multa (% demanda)", plan["pct_multa"]),
    ]
    _encabezado(ws, 1, ["Símbolo", "Parámetro", "Valor"])
    ref = {}
    for i, (s, n, v) in enumerate(filas, 2):
        ws.cell(i, 1, s)
        ws.cell(i, 2, n)
        ws.cell(i, 3, v).number_format = MILES if v >= 1 else "0.00"
        ref[s] = f"Parametros!$C${i}"
    ws.column_dimensions["B"].width = 38
    return ref


def hoja_plan(wb, nombre, df, ref, titulo):
    """Escribe un plan mensual: decisiones como valores, todo lo demás como fórmula."""
    ws = wb.create_sheet(nombre)
    ws["A1"] = titulo
    ws["A1"].font = TITULO
    ws["A2"] = LEYENDA
    ws["A2"].font = NOTA
    if nombre in COLOR_PLAN:
        ws.sheet_properties.tabColor = COLOR_PLAN[nombre]
    cols = ["Mes", "Demanda", "Dotación W", "Contrat. H", "Despidos F", "Prod. regular R", "Cap. regular",
            "Prod. HE O", "Cap. HE", "Inventario I", "Pendientes B", "Chequeo balance (=0)",
            "Chequeo dotación (=0)", "C. laboral", "C. contratación", "C. despido", "C. HE", "C. inventario",
            "C. pendientes", "C. multa", "C. total mes"]
    _encabezado(ws, 3, cols)
    multa = "Multa_activa" in df
    f0 = 4
    for k, r in enumerate(df.itertuples(), 0):
        i = f0 + k
        ws.cell(i, 1, r.Mes)
        for j, v in zip([2, 3, 4, 5, 6, 8, 10, 11],
                        [r.Demanda, r.Dotacion, r.Contrataciones, r.Despidos, r.Prod_regular, r.Prod_HE,
                         r.Inventario_final, r.Pendientes]):
            ws.cell(i, j, v).fill = CREMA
        ws.cell(i, 7, f"=C{i}*{ref['q_reg']}")
        ws.cell(i, 9, f"=C{i}*{ref['q_he']}")
        I_prev = ref["I0"] if k == 0 else f"J{i-1}"
        W_prev = ref["W0"] if k == 0 else f"C{i-1}"
        if k == 0:  # B_0 = 0: no se resta
            ws.cell(i, 12, f"={I_prev}+F{i}+H{i}-B{i}-(J{i}-K{i})")
        else:
            ws.cell(i, 12, f"={I_prev}-K{i-1}+F{i}+H{i}-B{i}-(J{i}-K{i})")
        ws.cell(i, 13, f"=C{i}-{W_prev}-D{i}+E{i}")
        ws.cell(i, 14, f"=C{i}*{ref['c_lab']}")
        ws.cell(i, 15, f"=D{i}*{ref['c_con']}")
        ws.cell(i, 16, f"=E{i}*{ref['c_des']}")
        ws.cell(i, 17, f"=H{i}*{ref['c_he']}")
        ws.cell(i, 18, f"=J{i}*{ref['c_inv']}")
        ws.cell(i, 19, f"=K{i}*{ref['c_pend']}")
        if multa:
            # multa si B_t > 1 % d_t
            ws.cell(i, 20, f"=IF(K{i}>{ref['pct']}*B{i}+0.001,{ref['multa']},0)")
        else:
            ws.cell(i, 20, 0)
        ws.cell(i, 21, f"=SUM(N{i}:T{i})")
    fin = f0 + len(df) - 1
    t = fin + 1
    ws.cell(t, 1, "Total").font = NEGRITA
    for j in [2, 3, 4, 5, 6, 8, 10, 11] + list(range(14, 22)):
        col = get_column_letter(j)
        ws.cell(t, j, f"=SUM({col}{f0}:{col}{fin})").font = NEGRITA
    ws.cell(t + 2, 1, "Chequeos")
    ws.cell(t + 2, 2, f'=IF(AND(SUMPRODUCT(--(F{f0}:F{fin}>G{f0}:G{fin}+0.001))=0,'
                      f'SUMPRODUCT(--(H{f0}:H{fin}>I{f0}:I{fin}+0.001))=0,'
                      f'MAX(J{f0}:J{fin})<={ref["I_max"]},J{fin}>={ref["I_fin"]},K{fin}=0,'
                      f'MIN(C{f0}:C{fin})>={ref["W_min"]},MAX(C{f0}:C{fin})<={ref["W_max"]},'
                      f'MAX(D{f0}:D{fin})<={ref["H_max"]},MAX(E{f0}:E{fin})<={ref["F_max"]},'
                      f'SUMPRODUCT(ABS(L{f0}:L{fin}))<0.01,SUMPRODUCT(ABS(M{f0}:M{fin}))<0.01),"OK","REVISAR")')
    ws.cell(t + 2, 2).font = NEGRITA
    _chequeo(ws, f"B{t + 2}", f'B{t + 2}="OK"', f'B{t + 2}="REVISAR"')
    for row in ws.iter_rows(min_row=f0, max_row=t, min_col=2, max_col=21):
        for c in row:
            c.number_format = MILES
    ws.cell(t + 4, 1, "Celdas crema: decisiones (de la regla de la política o del solver). Resto: fórmulas.").font = NOTA
    _anchos(ws, 13, 12)
    ws.freeze_panes = "B4"
    return f"'{nombre}'!U{t}"


def hoja_resumen_planes(wb, totales, extra):
    ws = wb.create_sheet("Comparacion_Planes")
    _encabezado(ws, 1, ["Plan", "Costo total (fórmula)", "Unid. HE", "Inv. acumulado", "Pend. acumulados",
                        "Contrat.", "Despidos", "Dot. mín", "Dot. máx"])
    for i, (n, ref_total) in enumerate(totales.items(), 2):
        ws.cell(i, 1, n)
        if "Sol. 5" in n:
            _marcar_fila(ws, i, 9)
        ws.cell(i, 2, f"={ref_total}").number_format = MILES
        e = extra[n]
        for j, k in enumerate(["unid_HE", "inv", "pend", "H", "F", "wmin", "wmax"], 3):
            ws.cell(i, j, e[k]).number_format = MILES
    _anchos(ws, 16, 34)


def hoja_desagregacion(wb, tr):
    ws = wb.create_sheet("Desagregacion")
    ws["A1"], ws["B1"] = "Tasa agregada (u/mes)", tr["tasa"]
    _encabezado(ws, 3, ["Modelo", "Participación", "Prod. mensual", "Prod. anual"])
    modelos = list(tr["mezcla"])
    for i, m in enumerate(modelos, 4):
        ws.cell(i, 1, m)
        ws.cell(i, 2, tr["mezcla"][m])
        ws.cell(i, 3, f"=$B$1*B{i}").number_format = MILES
        ws.cell(i, 4, f"=C{i}*12").number_format = MILES
    _encabezado(ws, 9, ["Componente"] + [f"Uso {m}" for m in modelos] + ["Req. mensual", "Req. anual"])
    for i, (comp, uso) in enumerate(tr["bom"].items(), 10):
        ws.cell(i, 1, comp)
        for j, m in enumerate(modelos, 2):
            ws.cell(i, j, uso[m])
        ws.cell(i, 5, f"=B{i}*$C$4+C{i}*$C$5+D{i}*$C$6").number_format = MILES
        ws.cell(i, 6, f"=E{i}*12").number_format = MILES
    _anchos(ws, 16, 26)


def hoja_eoq(wb, inv):
    ws = wb.create_sheet("EOQ_Individual")
    ws["A1"], ws["B1"] = "Días operativos", inv["dias"]
    ws["A2"], ws["B2"] = "Espacio máx (m3)", inv["V"]
    ws["A3"], ws["B3"] = "Capital máx ($)", inv["K"]
    ws["B3"].number_format = MILES
    cols = ["Componente", "D", "S", "c", "tasa i", "v", "L", "h=i·c", "Q*", "N=D/Q", "T (días)", "d diaria",
            "ROP=d·L", "C. ordenar", "C. mantener", "C. relevante", "Espacio v·Q", "Capital c·Q"]
    _encabezado(ws, 5, cols)
    f0 = 6
    for k, (n, p) in enumerate(inv["comp"].items()):
        i = f0 + k
        ws.cell(i, 1, n)
        for j, key in enumerate(["D", "S", "c", "i", "v", "L"], 2):
            ws.cell(i, j, p[key]).number_format = MILES if j in (2, 3, 4) else "General"
        fx = {
            8: f"=E{i}*D{i}", 9: f"=SQRT(2*B{i}*C{i}/H{i})", 10: f"=B{i}/I{i}", 11: f"=I{i}/L{i}",
            12: f"=B{i}/$B$1", 13: f"=L{i}*G{i}", 14: f"=B{i}*C{i}/I{i}", 15: f"=H{i}*I{i}/2",
            16: f"=N{i}+O{i}", 17: f"=F{i}*I{i}", 18: f"=D{i}*I{i}",
        }
        for j, f in fx.items():
            ws.cell(i, j, f).number_format = DEC
    fin = f0 + len(inv["comp"]) - 1
    t = fin + 1
    ws.cell(t, 1, "Total").font = NEGRITA
    for col in "NOPQR":
        ws[f"{col}{t}"] = f"=SUM({col}{f0}:{col}{fin})"
        ws[f"{col}{t}"].number_format = DEC
        ws[f"{col}{t}"].font = NEGRITA
    ws.cell(t + 2, 1, "¿Cabe en espacio?")
    ws.cell(t + 2, 2, f'=IF(Q{t}<=$B$2,"SÍ","NO: exceso "&TEXT(Q{t}-$B$2,"0.00")&" m3")')
    ws.cell(t + 3, 1, "¿Cumple capital?")
    ws.cell(t + 3, 2, f'=IF(R{t}<=$B$3,"SÍ","NO: exceso $"&TEXT(R{t}-$B$3,"#,##0"))')
    for f in (t + 2, t + 3):
        _chequeo(ws, f"B{f}", f'LEFT(B{f},2)="SÍ"', f'LEFT(B{f},2)="NO"')
    _anchos(ws, 13, 24)


def hoja_multiproducto(wb, inv, resumenes):
    """Q_i se reconstruye por fórmula a partir de mu y lambda (condición KKT)."""
    ws = wb.create_sheet("EOQ_Multiproducto")
    ws["A1"] = "Q_i = RAIZ(2·D·S / (h + 2·mu·v + 2·lambda·c))  — mu, lambda obtenidos en Python (KKT)"
    ws["A1"].font = NEGRITA
    ws["A2"], ws["B2"] = "Días operativos", inv["dias"]
    fila = 4
    for res in resumenes:
        ilimV, ilimK = res["V"] >= 1e12, res["K"] >= 1e12  # 1e18 = centinela de "recurso sin límite"
        ws.cell(fila, 1, f"Escenario: {res['Escenario']}").font = TITULO
        if res["Escenario"] == "Base":
            _marcar_fila(ws, fila, 16)
        ws.cell(fila + 1, 1, "V (m3)")
        ws.cell(fila + 1, 2, "sin límite" if ilimV else res["V"])
        ws.cell(fila + 2, 1, "K ($)")
        ws.cell(fila + 2, 2, "sin límite" if ilimK else res["K"]).number_format = MILES
        ws.cell(fila + 1, 3, "mu ($/m3-año)")
        ws.cell(fila + 1, 4, res["mu"]).fill = CREMA
        ws.cell(fila + 1, 4).number_format = "#,##0.0000"
        ws.cell(fila + 2, 3, "lambda ($/$-año)")
        ws.cell(fila + 2, 4, res["lam"]).fill = CREMA
        ws.cell(fila + 2, 4).number_format = "0.000000"
        vr, kr, mr, lr = f"$B${fila+1}", f"$B${fila+2}", f"$D${fila+1}", f"$D${fila+2}"
        h0 = fila + 4
        _encabezado(ws, h0, ["Componente", "D", "S", "c", "h", "v", "L", "Q", "N", "T (días)", "ROP posición",
                             "C. ordenar", "C. mantener", "C. relevante", "Espacio", "Capital"])
        for k, (n, p) in enumerate(inv["comp"].items()):
            i = h0 + 1 + k
            ws.cell(i, 1, n)
            for j, v in zip(range(2, 8), [p["D"], p["S"], p["c"], p["i"] * p["c"], p["v"], p["L"]]):
                ws.cell(i, j, v).number_format = MILES if j <= 5 else "General"
            fx = {
                8: f"=SQRT(2*B{i}*C{i}/(E{i}+2*{mr}*F{i}+2*{lr}*D{i}))", 9: f"=B{i}/H{i}",
                10: f"=H{i}/(B{i}/$B$2)", 11: f"=B{i}/$B$2*G{i}", 12: f"=B{i}*C{i}/H{i}",
                13: f"=E{i}*H{i}/2", 14: f"=L{i}+M{i}", 15: f"=F{i}*H{i}", 16: f"=D{i}*H{i}",
            }
            for j, f in fx.items():
                ws.cell(i, j, f).number_format = DEC
        a, b = h0 + 1, h0 + len(inv["comp"])
        t = b + 1
        ws.cell(t, 1, "Total").font = NEGRITA
        for col in "INOP":
            ws[f"{col}{t}"] = f"=SUM({col}{a}:{col}{b})"
            ws[f"{col}{t}"].number_format = DEC
            ws[f"{col}{t}"].font = NEGRITA
        ws.cell(t + 1, 1, "Holgura espacio")
        ws.cell(t + 1, 2, f'=IF(ISNUMBER({vr}),{vr}-O{t},"sin límite")').number_format = DEC
        ws.cell(t + 2, 1, "Holgura capital")
        ws.cell(t + 2, 2, f'=IF(ISNUMBER({kr}),{kr}-P{t},"sin límite")').number_format = MILES
        fila = t + 5
    _anchos(ws, 16, 22)
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["P"].width = 22


def hoja_df(wb, nombre, df, nota=None, renombre=None, anchos=None, recomendado=None):
    """Vuelca un DataFrame; `renombre` solo cambia los encabezados del Excel (el CSV no cambia).
    `recomendado(valor de la 1.ª columna)` marca la fila del plan o escenario recomendado."""
    ws = wb.create_sheet(nombre)
    _encabezado(ws, 1, [(renombre or {}).get(c, c) for c in df.columns])
    for i, row in enumerate(df.itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            if isinstance(v, (list, tuple)):
                v = ", ".join(map(str, v))
            elif hasattr(v, "item"):
                v = v.item()
            if isinstance(v, float) and v >= 1e12:  # centinela 1e18 = "recurso sin límite"
                v = "sin límite"
            c = ws.cell(i, j, v)
            if isinstance(v, bool):
                continue
            if isinstance(v, float):
                c.number_format = DEC if abs(v) < 1000 else MILES
            elif isinstance(v, int):
                c.number_format = MILES
        if recomendado and recomendado(row[0]):
            _marcar_fila(ws, i, len(df.columns))
    if nota:
        ws.cell(len(df) + 3, 1, nota).font = NOTA
    _anchos(ws, 16, 34)
    for col, ancho in (anchos or {}).items():
        ws.column_dimensions[col].width = ancho


def generar(plan, tr, inv, politicas, modelos, sens1, ind, multi_res, sens1_nota):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leeme"
    texto = [
        "Proyecto Ventisur — Respaldo de cálculos (generado por 01_codigo/run_all.py)",
        "",
        "Celdas crema = decisiones (regla de la política, solución del solver o multiplicadores KKT).",
        "Celdas blancas = fórmulas de Excel que recalculan capacidades, balances, costos y uso de recursos.",
        "Cada hoja de plan tiene una celda 'Chequeos' (capacidades, bodega, dotación 15-25, ±3, balance, borde) que debe mostrar OK.",
        "En EOQ_Multiproducto, mu y lambda vienen de Python; los lotes, costos y uso de recursos se recalculan con fórmulas.",
        "",
        "Hojas: Parametros | P1, P2, P3 (Sol. 1) | ModA (Sol. 2) | ModB (Sol. 3) | ModC (Sol. 4) | ModD (Sol. 5)",
        "       Comparacion_Planes | Sensibilidad_P1 | Desagregacion (Sol. 6) | EOQ_Individual (Sol. 7-8)",
        "       EOQ_Multiproducto (Sol. 9-10) | Resumen_Multiproducto",
        "Modelos: 02_resultados/modelos_lp/ (A-D en .lp, índice 0 = marzo; E = EOQ multiproducto en .txt).",
    ]
    for i, t in enumerate(texto, 1):
        ws.cell(i, 1, t)
    ws["A1"].font = TITULO
    ws.column_dimensions["A"].width = 110
    ref = hoja_parametros(wb, plan)
    totales, extra = {}, {}
    hojas = [("P1", "Política 1"), ("P2", "Política 2"), ("P3", "Política 3")]
    for h, n in hojas:
        totales[n] = hoja_plan(wb, h, politicas[n], ref, f"{n} (Solicitud 1)")
    for h, n in [("ModA", "Modelo A (Sol. 2)"), ("ModB", "Modelo B (Sol. 3)"), ("ModC", "Modelo C (Sol. 4)"),
                 ("ModD", "Modelo D (Sol. 5)")]:
        totales[n] = hoja_plan(wb, h, modelos[n][0], ref, n)
    for n, df in list(politicas.items()) + [(k, v[0]) for k, v in modelos.items()]:
        extra[n] = dict(unid_HE=df.Prod_HE.sum(), inv=df.Inventario_final.sum(), pend=df.Pendientes.sum(),
                        H=df.Contrataciones.sum(), F=df.Despidos.sum(), wmin=df.Dotacion.min(), wmax=df.Dotacion.max())
    hoja_resumen_planes(wb, totales, extra)
    ren = {"estado": "Estado solver", "costo": "Costo total ($)", "dotacion": "Dotación mensual (trab.)",
           "contrataciones": "Contrataciones (trab.)", "despidos": "Despidos (trab.)", "unid_HE": "HE total (u)",
           "HE_mensual": "HE mensual (u)", "holgura_HE": "Holgura de HE mensual (u)",
           "inv_total": "Inventario acumulado (u-mes)", "pendientes": "Pendientes acumulados (u-mes)"}
    hoja_df(wb, "Sensibilidad_P1", sens1, sens1_nota, ren,
            anchos={"A": 56, "B": 13, "C": 16, "D": 46, "H": 62, "I": 70},
            recomendado=lambda v: str(v).startswith("Recomendado"))
    hoja_desagregacion(wb, tr)
    hoja_eoq(wb, inv)
    hoja_multiproducto(wb, inv, multi_res.to_dict("records"))
    hoja_df(wb, "Resumen_Multiproducto", multi_res, anchos={"A": 28}, recomendado=lambda v: v == "Base")
    for w in wb.worksheets:
        _estilo_hoja(w)
    out = RESULTADOS / "Resultados_Ventisur.xlsx"
    wb.save(out)
    _cachear_valores(out)
    return out


def _es_encabezado(c):
    return c.fill is not None and str(c.fill.fgColor.rgb).upper().endswith(NAVY)


def _estilo_hoja(ws):
    """Pasada final de formato (no toca valores, fórmulas, formatos numéricos, anchos ni paneles):
    Calibri 10 en tinta, sin cuadrícula, encabezados alineados como su columna, filetes inferiores
    finos en el cuerpo de cada tabla y fila Total con filete superior en tinta."""
    ws.sheet_view.showGridLines = False
    for fila in ws.iter_rows():
        for c in fila:
            if c.value is None or _es_encabezado(c):
                continue
            f = c.font
            if f.sz and f.sz >= 12:
                c.font = TITULO
            elif f.italic:
                continue  # notas: ya tienen su estilo
            else:
                c.font = Font(name=FUENTE, size=10, bold=f.b, color=TINTA)
    for r in range(1, ws.max_row + 1):
        cols = [c.column for c in ws[r] if _es_encabezado(c)]
        if not cols:
            continue
        ncol = max(cols)
        for j in cols:  # cada encabezado se alinea como el contenido de su columna
            abajo = ws.cell(r + 1, j).value
            numero = isinstance(abajo, Number) and not isinstance(abajo, bool)
            formula = isinstance(abajo, str) and abajo.startswith("=")
            h = "right" if (numero or formula) else "left"
            ws.cell(r, j).alignment = Alignment(wrap_text=True, horizontal=h, vertical="bottom")
        rr = r + 1
        while any(ws.cell(rr, j).value is not None for j in range(1, ncol + 1)):
            if ws.cell(rr, 1).value == "Total":
                for j in range(1, ncol + 1):
                    ws.cell(rr, j).border = Border(top=LINEA_TINTA)
                    ws.cell(rr - 1, j).border = Border(bottom=LINEA_TINTA)
                break
            for j in range(1, ncol + 1):
                ws.cell(rr, j).border = Border(bottom=LINEA_FILETE)
            rr += 1


def _cachear_valores(ruta):
    """Recalcula con LibreOffice (si está instalado) para que el archivo traiga los valores ya calculados."""
    import shutil
    import subprocess
    import tempfile

    if not shutil.which("soffice"):
        return
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(["soffice", "--headless", "--convert-to", "xlsx", "--outdir", tmp, str(ruta)],
                           capture_output=True)
        nuevo = Path(tmp) / ruta.name
        if r.returncode == 0 and nuevo.exists():
            shutil.move(str(nuevo), ruta)
