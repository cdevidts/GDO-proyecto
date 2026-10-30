# GDO — Gestión de Operaciones (UAI) · Proyecto Integrador Ventisur

Repositorio con la materia del curso y el desarrollo completo del Proyecto Ventisur
(planificación agregada + requerimientos de materiales + inventarios determinísticos).

## Estructura

```
materia/                          Material del curso
  01_clases/                      Presentaciones de clases (planificación agregada, inventarios)
  02_ayudantias/                  Ayudantías y simulador
  03_guias_y_temas/               Guías con respuestas (pronósticos, plan. agregada, EOQ, modelos)
  04_pruebas_y_formularios/       Pruebas, pautas y formulario
  05_material_interactivo/        Clases y evaluaciones interactivas (HTML)

proyecto/
  00_enunciado_y_datos/           Enunciado, rúbrica y Excel de datos oficiales (NO modificar)
  01_codigo/                      Código Python reproducible
    datos.py                      Lee todos los parámetros desde el Excel oficial
    parte1_politicas.py           Sol. 1: tres políticas simples + validador de factibilidad
    parte1_modelos.py             Sol. 2–5: modelos A, B (multa, binaria), C (cero pendientes), D
    parte1_sensibilidad.py        Escenarios "¿qué pasa si…?" para la recomendación y la defensa
    parte2_requerimientos.py      Sol. 6: desagregación y requerimientos de componentes
    parte3_inventarios.py         Sol. 7–10: EOQ, factibilidad conjunta, EOQ multiproducto, sensibilidad
    generar_excel.py, graficos.py Respaldos (planilla con fórmulas y figuras)
    run_all.py                    Ejecuta todo
  02_resultados/                  Salidas generadas
    Resultados_Ventisur.xlsx      Planilla con fórmulas que recalculan balances, costos, EOQ y recursos
    modelos_lp/                   Modelos A–D (.lp; índice 0 = marzo, el lado derecho ya incluye d − I0)
                                  y Modelo E (EOQ multiproducto, no lineal) documentado en .txt
    csv/, figuras/, resumen.json
  03_informe/                     Informe técnico (≤ 6 páginas): informe.md → .docx y .pdf
  04_presentacion/                Presentación de 5 min (.pptx) y guía de preparación de la defensa
```

## Cómo reproducir

Requisitos: Python 3.10+, y para el informe `pandoc` y Node.js con Playwright
(`npm i playwright && npx playwright install chromium`). LibreOffice es opcional: si está,
la planilla se guarda con los valores ya calculados.

```bash
pip install -r proyecto/01_codigo/requirements.txt
cd proyecto/01_codigo && python run_all.py                 # resultados, Excel, figuras y modelos .lp
cd ../03_informe && python construir_informe.py           # informe (pandoc + Node/Playwright)
cd ../04_presentacion && python construir_presentacion.py # presentación
```

## Resultados principales

| Solicitud | Resultado |
|---|---|
| 1. Políticas simples | P1 340,0 · **P2 315,0** · P3 329,5 MM$ |
| 2. Modelo A | 300,75 MM$ — 18 trabajadores, HE sep–feb, pendientes dic–ene |
| 3. Modelo B (multa) | 300,94 MM$ — sin multas; pendientes de dic. = 1 % exacto |
| 4. Modelo C (cero pendientes) | 301,10 MM$ (+0,35 MM$ vs A) |
| 5. Multa + cero pendientes | 301,10 MM$ (= C) → **plan recomendado** |
| 6. Requerimientos | 96.000 / 24.000 / 120.000 / 60.000 / 24.000 u/año (= oficiales) |
| 7–8. EOQ individuales | 113,1 m³ > 90 y 135,1 MM$ > 110 MM$ → infactibles |
| 9. EOQ multiproducto | 34,50 MM$/año; ambas restricciones activas |
| 10. Sensibilidad | +10 % espacio ahorra $5.219/año; **+10 % presupuesto ahorra $386.591/año** |

> Antes de entregar: completar sección, grupo e integrantes en `proyecto/03_informe/informe.md`
> y en la portada de la presentación, y volver a generar el informe.
