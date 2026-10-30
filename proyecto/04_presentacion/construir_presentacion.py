"""Genera Presentacion_Ventisur.pptx (defensa de 5 minutos, 8 diapositivas).

Uso:  python construir_presentacion.py   (requiere python-pptx; usa las figuras de 02_resultados)
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Cm, Pt

AQUI = Path(__file__).resolve().parent
FIG = AQUI.parent / "02_resultados" / "figuras"
AZUL = RGBColor(0x1F, 0x3A, 0x5F)
GRIS = RGBColor(0x44, 0x44, 0x44)

prs = Presentation()
prs.slide_width, prs.slide_height = Cm(33.867), Cm(19.05)
VACIO = prs.slide_layouts[6]


def titulo(s, texto, sub=None):
    tb = s.shapes.add_textbox(Cm(1.2), Cm(0.6), Cm(31.5), Cm(1.8)).text_frame
    tb.text = texto
    p = tb.paragraphs[0]
    p.runs[0].font.size, p.runs[0].font.bold, p.runs[0].font.color.rgb = Pt(28), True, AZUL
    if sub:
        q = tb.add_paragraph()
        q.text = sub
        q.runs[0].font.size, q.runs[0].font.color.rgb = Pt(15), GRIS


def vinetas(s, items, x, y, w, h, tam=16):
    tf = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h)).text_frame
    tf.word_wrap = True
    for k, it in enumerate(items):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        nivel = 1 if it.startswith("  ") else 0
        p.text = ("– " if nivel else "• ") + it.strip()
        p.level = nivel
        p.space_after = Pt(10)
        for r in p.runs:
            r.font.size = Pt(round((tam - 2 * nivel) * 1.25))
            r.font.color.rgb = GRIS if nivel else RGBColor(0x11, 0x11, 0x11)


def tabla(s, filas, x, y, w, alto_fila=0.85, tam=12, anchos=None):
    t = s.shapes.add_table(len(filas), len(filas[0]), Cm(x), Cm(y), Cm(w), Cm(alto_fila * 1.45 * len(filas))).table
    for i, f in enumerate(filas):
        for j, v in enumerate(f):
            c = t.cell(i, j)
            c.text = str(v)
            for p in c.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(round(tam * 1.3))
                    r.font.bold = i == 0
    if anchos:
        for j, a in enumerate(anchos):
            t.columns[j].width = Cm(a)


def nota(s, texto):
    s.notes_slide.notes_text_frame.text = texto


# 1. Portada
s = prs.slides.add_slide(VACIO)
tb = s.shapes.add_textbox(Cm(2), Cm(6), Cm(30), Cm(6)).text_frame
tb.text = "Proyecto Integrador Ventisur"
tb.paragraphs[0].runs[0].font.size, tb.paragraphs[0].runs[0].font.bold = Pt(40), True
tb.paragraphs[0].runs[0].font.color.rgb = AZUL
for t in ["Planificación agregada e inventarios determinísticos", "Gestión de Operaciones · UAI · Grupo [__]",
          "[Integrantes]"]:
    p = tb.add_paragraph()
    p.text = t
    p.runs[0].font.size, p.runs[0].font.color.rgb = Pt(20), GRIS
nota(s, "15 s. Presentar el problema: plan de 12 meses para 3 ventiladores (unidad agregada) y luego cómo comprar 5 componentes.")

# 2. Políticas simples
s = prs.slides.add_slide(VACIO)
titulo(s, "1. Tres políticas simples: mismo costo laboral, distinto mecanismo",
       "Las tres usan 240 trabajador-mes (288 MM$); cambia cómo absorben la demanda")
tabla(s, [["", "P1 Tasa constante", "P2 Dotación + HE", "P3 Persecución"],
          ["Mecanismo", "Inventario (hasta 7.000 u)", "Horas extra (6.000 u)", "Contratar/despedir (9 / 6)"],
          ["Costo clave", "Inventario 52 MM$", "HE 15 + inv. 12 MM$", "Movimientos 40,5 MM$"],
          ["Costo total", "340,0 MM$", "315,0 MM$  ← mejor", "329,5 MM$"]],
      1.2, 3.6, 31.4, 1.1, 15)
vinetas(s, ["P1: estable para personas y proveedores, pero guarda unidades 5–7 meses a $1.000/mes",
            "P2: una HE ($2.500) cuesta menos que 2,5 meses de mantención → la mejor regla simple",
            "P3: casi sin inventario, pero cada contratación ($2,5 MM) y despido ($3 MM) pesa más; inestable"],
        1.2, 11.0, 31, 7, 17)
nota(s, "40 s. Énfasis: la diferencia no es la masa laboral (igual) sino el mecanismo. Umbral: si HE > $4.917/u, P3 supera a P2.")

# 3. Modelo A
s = prs.slides.add_slide(VACIO)
titulo(s, "2. Modelo A (MILP): combina los tres mecanismos → 300,75 MM$",
       "min laboral + contratación + despido + HE + inventario + pendientes; W, H, F enteras")
vinetas(s, ["Balance:  I(t−1) − B(t−1) + R + O − d = I − B",
            "Capacidades R ≤ 500·W, O ≤ 150·W; W(t) = W(t−1) + H − F; límites 15–25 y ±3",
            "Borde: I(12) ≥ 1.000, B(12) = 0, bodega ≤ 7.500",
            "Solución: despide 2 en marzo y mantiene 18 todo el año",
            "  HE desde septiembre (saturada nov–feb), inventario solo 1–2 meses antes",
            "  Pendientes dic–ene: atrasar ($750) es más barato que adelantar ($1.000/mes)",
            "−14,25 MM$ (−4,5 %) vs la mejor política simple"], 1.2, 3.4, 15.5, 14, 15)
s.shapes.add_picture(str(FIG / "fig1_planes.png"), Cm(16.6), Cm(5.0), width=Cm(16.9))
nota(s, "60 s. Contraintuitivo: despedir y luego usar HE al 100 %; capacidad ociosa en marzo/mayo; atrasos con inventario antes. Todo por b<h y HE < 3 meses de mantención.")

# 4. B, C y D
s = prs.slides.add_slide(VACIO)
titulo(s, "3. Nivel de servicio: elevarlo cuesta muy poco",
       "B: multa con binaria  B ≤ 0,01·d + M·y ;  C: B = 0 ;  Sol. 5: multa + B = 0 (≡ C)")
tabla(s, [["", "A", "B (multa)", "C / Sol. 5 (cero pend.)"],
          ["Costo total", "300,75", "300,94", "301,10 MM$"],
          ["Pendientes máx.", "400 u (3,2 %)", "125 u (= 1 %)", "0"],
          ["Multas", "—", "0 (nunca conviene pagar $3 MM)", "0"],
          ["Costo vs A", "—", "+193.750", "+350.000 (0,12 %)"]],
      1.2, 3.6, 31.4, 1.0, 15)
vinetas(s, ["M(t) = demanda acumulada − I0 − 1 %·d(t): cota válida (peor caso no producir) y lo más ajustada posible",
            "Misma dotación (18) y HE (13.000 u): se compra servicio con 800 u-mes de inventario anticipado",
            "Con B = 0 la cláusula nunca se activa: Sol. 5 coincide con C"], 1.2, 12.0, 31, 6, 16)
nota(s, "45 s. Explicar y=1 forzado si B>1 %; si no, el costo hace y=0. M demasiado chico corta soluciones; muy grande debilita la relajación.")

# 5. Recomendación agregada
s = prs.slides.add_slide(VACIO)
titulo(s, "4. Recomendación de planificación agregada",
       "Plan Sol. 5: 18 trabajadores, regular ~9.000 u/mes, HE sep–feb, cero pendientes — 301,1 MM$")
s.shapes.add_picture(str(FIG / "fig2_costos.png"), Cm(0.8), Cm(4.6), width=Cm(20.5))
vinetas(s, ["−13,9 MM$ (−4,4 %) vs P2 y servicio completo",
            "Estable: un solo ajuste de personal",
            "Riesgo: HE al 100 % en nov–feb",
            "  Seguro: 19 trabajadores (+1,4 MM$, +0,46 %)",
            "  Sin despidos (20): +5,4 MM$"], 20.8, 4.0, 12.5, 12, 16)
nota(s, "30 s. No elegimos solo por costo: estabilidad, servicio y holgura de HE.")

# 6. Parte II + EOQ
s = prs.slides.add_slide(VACIO)
titulo(s, "5. De la producción a los componentes y EOQ individuales",
       "10.000 u/mes × mezcla 50-30-20 × BOM → tasas de consumo constantes (no lotes)")
tabla(s, [["Componente", "D anual", "h=0,25c", "Q*", "ROP = d·L", "Espacio", "Capital"],
          ["Motor estándar", "96.000", "3.000", "3.394", "2.400", "13,6 m³", "40,7 MM$"],
          ["Motor premium", "24.000", "5.000", "1.453", "1.000", "7,3 m³", "29,1 MM$"],
          ["Hélice–rejilla", "120.000", "1.125", "5.657", "4.000", "84,9 m³", "25,5 MM$"],
          ["Módulo electrónico", "60.000", "2.000", "3.464", "2.500", "5,2 m³", "27,7 MM$"],
          ["Control remoto", "24.000", "1.375", "2.211", "1.200", "2,2 m³", "12,2 MM$"],
          ["Total", "", "", "", "", "113,1 > 90", "135,1 > 110"]],
      1.2, 3.6, 31.4, 0.85, 13)
vinetas(s, ["Q* dice cuánto, ROP dice cuándo; L < T en todos → un pedido en tránsito como máximo",
            "Infactible en ambos recursos: cada EOQ ignora que compite por bodega y capital"], 1.2, 13.6, 31, 4, 16)
nota(s, "40 s. Supuestos EOQ ← tasa estable de la Parte II. Costo relevante individual 33,78 MM$/año.")

# 7. Multiproducto y sensibilidad
s = prs.slides.add_slide(VACIO)
titulo(s, "6. EOQ multiproducto: ambas restricciones activas, distinto valor",
       "min Σ DS/Q + hQ/2  s.a.  Σ vQ ≤ 90 (μ),  Σ cQ ≤ 110 MM (λ)  →  Q = √(2DS / (h + 2μv + 2λc))")
tabla(s, [["Escenario", "Espacio", "Capital", "Activas", "Costo relevante", "Ahorro"],
          ["Base", "90,0", "110,0", "ambas", "34.503.017", "—"],
          ["+10 % espacio", "92,1 de 99", "110,0", "solo capital", "34.497.798", "5.219"],
          ["+10 % presupuesto", "90,0", "121,0", "ambas", "34.116.426", "386.591"]],
      1.2, 3.6, 18.5, 1.0, 12)
vinetas(s, ["Lotes −18 % a −21 %; 94 → 116 pedidos/año; +0,72 MM$/año",
            "Costo de compra (2.784 MM$) no depende de Q",
            "Activa ≠ valiosa: al ampliar bodega el capital limita casi de inmediato",
            "Más presupuesto vale 74× más que más bodega"], 1.2, 10.8, 18.5, 8, 15)
s.shapes.add_picture(str(FIG / "fig3_lotes.png"), Cm(20.2), Cm(5.5), width=Cm(13.4))
nota(s, "50 s. μ = 5.098 $/m³-año y λ = 0,0595 $/$-año son valores marginales locales; al relajar cambian.")

# 8. Recomendación integrada
s = prs.slides.add_slide(VACIO)
titulo(s, "7. Recomendación integrada para Ventisur")
vinetas(s, ["Producción: plan Sol. 5 (18 trabajadores, HE en el peak, cero pendientes): 301,1 MM$",
            "  Servicio completo cuesta 0,35 MM$ ≪ una sola multa (3 MM$)",
            "Coherencia: comprar con la tasa estable de 10.000 u/mes exige holgura de componentes en nov–feb",
            "Compras: usar los lotes multiproducto (2.781 / 1.192 / 4.456 / 2.844 / 1.815) con ROP = d·L",
            "Inversión: priorizar presupuesto (+386 mil $/año) sobre bodega (+5 mil $/año)",
            "  Rentabilidad marginal ≈ 3,5 % anual: comparar con el costo de financiar 11 MM$",
            "Supuestos: demanda y plazos determinísticos, unidad agregada, lotes completos simultáneos"],
        1.2, 3.0, 31.5, 15, 18)
nota(s, "30 s. Cerrar conectando las tres partes y abrir a preguntas.")

prs.save(AQUI / "Presentacion_Ventisur.pptx")
print("OK", AQUI / "Presentacion_Ventisur.pptx")
