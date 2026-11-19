# Guía de preparación para la defensa oral — Ventisur

La rúbrica evalúa **principalmente la defensa**: no basta leer un número, hay que explicar por qué.
Esta guía resume las preguntas más probables por dimensión y una respuesta corta y razonada para cada una.
Todas las cifras salen de `02_resultados/` (Excel, CSV o `resumen.json`).

---

## Guion de 5 minutos (8 diapositivas, total 4:40 + 20 s de margen)

| Diap. | Tiempo | Mensaje central |
|---|---|---|
| 1 Portada | 0:15 | Plan agregado a 12 meses y, después, la compra de 5 componentes |
| 2 Políticas simples | 0:35 | Mismo costo laboral (288 MM$); cambia el mecanismo: inventario, HE o personal |
| 3 Modelo A | 0:50 | Combina los mecanismos: 18 trabajadores, HE en el peak, inventario corto y atrasos baratos |
| 4 B, C y Sol. 5 | 0:45 | Binaria con M; servicio completo cuesta solo 0,35 MM$ |
| 5 Recomendación agregada | 0:30 | Plan Sol. 5 + seguro de 19 trabajadores |
| 6 Componentes y EOQ | 0:35 | Tasas constantes → EOQ; infactible en espacio y capital |
| 7 Multiproducto | 0:40 | Ambas activas, pero el presupuesto vale 74 veces más |
| 8 Integración | 0:30 | Conectar las tres partes |

---

## D1. Políticas simples (10 %)

- **¿Por qué P1 no viola la bodega?** El inventario máximo es 7.000 u (ago–oct) ≤ 7.500. Producción anual 120.000 = demanda total, así que termina en 1.000 = inicial.
- **¿Por qué P2 tiene capacidad ociosa?** La regla fija 20 trabajadores (10.000 u regulares) pero la demanda de mar–ago es menor (ociosidad 500/1.000/1.500/1.500/1.000/500); como el inventario debe quedar en 1.000, se produce menos que la capacidad: 6.000 u ociosas.
- **¿Cómo se calcula la dotación de P3?** $W_t = \lceil (d_t + I^{obj}_t - I_{t-1}) / 500 \rceil$, acotada por 15–25 y por ±3 respecto del mes anterior. Marzo: (9.500 − 1.000)/500 = 17. Febrero: (10.500 + 1.000)/500 = 23.
- **¿Por qué las tres tienen igual costo laboral?** Las tres suman 240 trabajador-mes (P3: 17+18+17+17+18+19+20+20+23+25+23+23 = 240).
- **¿Qué pasa si sube el costo de mantener?** P1 sube 52.000 $ por cada $1 de aumento (52.000 u-mes); P2 sube 12.000 por $1; P3 casi no cambia. P1 supera a P2 solo si h < $375/u-mes (40.000·h < 15 MM$); P3 igualaría a P2 si contratar/despedir costaran ≈36 % menos (40,5 → 26 MM$).
- **¿Desde qué costo de HE P3 resulta más barata que P2?** P2 = 300 MM$ + 6.000·c_HE; P3 = 329,5 MM$ → c_HE > $4.917/u (29,5 MM$ / 6.000 u); con $2.500, P2 gana. P2 supera a P1 mientras c_HE < $6.667/u (los 40.000 u-mes extra de P1 sostienen las mismas 6.000 u que P2 hace con HE: 6,7 meses de mantención por unidad vs 2,5 meses que equivale una HE).

## D2. Modelo A (20 %)

- **Significado de cada restricción**: ver la tabla del informe. Claves: el costo laboral multiplica $W_t$ (se paga aunque no se produzca); capacidades regular y HE separadas; balance con inventario neto $I - B$.
- **¿Por qué $W, H, F$ enteras y la producción continua?** No existen fracciones de trabajador; la producción es de miles de unidades y redondear no cambia la decisión. La relajación lineal da 300,68 MM$ (diferencia 0,07 MM$).
- **¿Por qué no se exige usar primero la regular antes de HE?** Porque la regular ya está pagada (costo 0 marginal) y la HE cuesta $2.500: el óptimo lo hace solo (Guía de Modelos, pregunta 1e).
- **¿Puede haber $I_t > 0$ y $B_t > 0$ a la vez?** En el óptimo no: ambos cuestan, y reducir los dos en la misma cantidad mantiene el balance y baja el costo.
- **¿Por qué despide 2 en marzo?** Conservar un trabajador cuesta 14,4 MM$/año (11,4 netos del despido evitado), pero sus 500 u/mes solo se necesitan sep–feb; cubrir esas ~3.000 u con HE cuesta ≈7,5 MM$. Conservarlo solo convendría si se usara ≥ 9,1 meses al año (11,4 MM$ netos ÷ 1,25 MM$ de HE evitada por mes = 500 u × $2.500); aquí hacen falta ~6 (sep–feb). Para un trabajador nuevo, sin despido evitado, el umbral sería 11,5 meses (14,4 ÷ 1,25). Mantener 20 cuesta 306,5 MM$ (con cero pendientes) vs 301,1.
- **¿Qué combinación de decisiones mejora a las políticas simples?** Descomposición A − política (MM$): vs P2 = −14,25 (mano de obra −28,8; despidos +6,0; HE +17,5 por 7.000 u más; inventario −9,4; atrasos +0,45); vs P1 = −39,25 (−28,8; +6,0; HE +32,5; inventario −49,4; +0,45); vs P3 = −28,75 (mano de obra −28,8; contratación + despido −34,5, pues A evita 13 de los 15 movimientos de P3; HE +32,5; inventario +1,6; atrasos +0,45). Los 2 trabajadores de P2 no estaban ociosos todo el año: P2 solo deja 6.000 u de capacidad regular ociosa en mar–ago y de sep a feb los usa; A los reemplaza por HE.
- **¿Hay óptimos alternativos (otra distribución de HE con igual costo)?** No: el óptimo de A, B y C es único. Con el costo acotado a Z* + $10 y minimizando/maximizando cada variable, el rango es < 0,1 u en todos los meses (`python parte1_sensibilidad.py --unicidad`).
- **¿Por qué hay capacidad ociosa en marzo y mayo si luego se paga HE?** Guardar una unidad 3+ meses cuesta ≥ $3.000 > $2.500 de la HE. Solo conviene adelantar 1–2 meses (jun–jul → ago; oct–nov → dic).
- **¿Por qué acepta atrasos?** $b = 750 < h = 1.000$: atrasar un mes es más barato que adelantar un mes. Incluso con $b = 1.500$ sigue habiendo 200 u de atraso (301,0 MM$), porque adelantar exigiría HE en octubre + 2 meses de inventario (2.500 + 2.000 = 4.500) vs HE en enero + 1 mes de atraso (2.500 + 1.500 = 4.000).
- **¿Qué pasa si quito el límite de ±3?** Nada (mismo óptimo, 300,75 MM$): esa restricción no está activa.
- **¿Y si la bodega fuera 2.000?** Tampoco cambia: el inventario máximo del óptimo es 1.000. Con bodega < 1.000 es infactible (I₀ = I_fin = 1.000); desde 1.000 el óptimo es el mismo (300,75).
- **¿Qué pasa si la HE rinde 100 u/trab-mes?** Contrata 2 en septiembre (20 trabajadores) y el costo sube a 304,5 MM$.
- **¿Si el costo de inventario fuera $500?** Adelanta más (5.000 u-mes de inventario) y el costo baja a 299,1 MM$.
- **¿Y sin horas extra?** 312,9 MM$ (+12,15 vs A): 18 trabajadores durante 6 meses y luego 20, 22, 23, 23, 23, 23; inventario 4.000 u-mes.
- **¿Y si el inventario final fuera 0 o 2.000?** Modelo A: 297,15 MM$ con I_fin = 0 y 305,66 MM$ con I_fin = 2.000.
- **¿Y si despedir fuera gratis?** 293,95 MM$ (17 trabajadores mar–jun y 18 desde julio; HE 14.000 u).

## D3. Modelos B, C y recomendación (15 %)

- **Rol de la binaria**: $B_t \le 0{,}01 d_t + M_t y_t$. Si $B_t$ supera el 1 %, la restricción solo se cumple con $y_t = 1$ (y se paga $3 MM). Si no lo supera, $y_t$ podría ser 1, pero el costo hace que el modelo elija 0.
- **¿Por qué ese $M$?** Debe ser ≥ el mayor valor posible de $B_t - 0{,}01 d_t$ para no cortar soluciones. El peor caso es no producir nada hasta $t$, ignorando las condiciones finales: $M_t = \sum_{k \le t} d_k - I_0 - 0{,}01 d_t$ (p. ej. $M_{dic} = 96.875$); vale para planes sin $I_t$ y $B_t$ positivos a la vez. Es una cota válida y simple, **no la más ajustada**: con $B_{12}=0$, $I_{12} \ge 1.000$ y la capacidad máxima mensual, el mayor $B_{dic}$ posible es 9.500 y bastaría $M_{dic} = 9.375$ (`big_m_ajustada`); con ese $M$ el óptimo no cambia (300.943.750). Un $M$ enorme (p. ej. $10^9$) también es válido pero debilita la relajación lineal.
- **¿Por qué B no paga multas?** Recortar los pendientes de dic. de 400 a 125 (y los de enero) cuesta +193.750 en total; una multa cuesta 3 MM$. Si la multa fuera $150 mil, B pagaría una (diciembre); desde ≈ $151,3 mil ya no (quiebre exacto: $151.250).
- **¿Y si el umbral de la multa fuera otro?** Con ≥ 3,2 % B reproduce A (300,75); con 2 % da 300,825; con 0 % reproduce C (301,10).
- **¿Cuál es la diferencia conceptual entre A, B y C?** A: atraso lineal y blando ($750/u-mes). B: costo fijo ($3 MM) al superar el 1 %: no convexo, por eso requiere la binaria. C: restricción dura B = 0. B queda justo en el borde (125 u = 1 % exacto de 12.500): una unidad más gatilla $3 MM. Pasar de B a C cuesta solo 0,156 MM$ (301,10 − 300,94).
- **¿Por qué Sol. 5 = Sol. 4?** Con $B_t = 0$, la condición $0 \le 0{,}01 d_t$ se cumple siempre con $y_t = 0$; la multa es irrelevante.
- **Costo de elevar el servicio**: A → C = +350.000 (0,12 %). Se cambian 600 u-mes de atraso por 800 u-mes de inventario (800·1.000 − 600·750 = 350.000).
- **¿Por qué no recomiendan simplemente el más barato (A)?** Tiene atrasos que gatillarían multas reales (dic 400 > 125; ene 200 > 115): bajo el contrato A pagaría 2 multas, 300,75 + 6,0 = 306,75 MM$ > 301,10 (C); además hay daño comercial, y el sobrecosto de servicio completo es mínimo. Re-optimizar con la multa (B) cuesta 5,8 MM$ menos que dejar el plan A.
- **¿Qué tan robusto es el plan?** Si la demanda de diciembre sube 5 % (13.125) y se conoce a tiempo, el modelo re-planifica con los mismos 18 trabajadores, más HE (13.625 u) e inventario (4.650 u-mes en total, vs 3.400): 303,9 MM$ (+2,8 MM$), cero pendientes. Si el alza NO se anticipa, el plan fijo no alcanza (dic.: 800 + 9.000 + 2.700 = 12.500 < 13.125 ⇒ ≥ 625 u pendientes > 1 % ⇒ multa, y febrero no cierra en I = 1.000 sin re-planificar). El riesgo es la HE al 100 % en nov–dic (93 % en ene–feb): el seguro de 19 trabajadores cuesta +1,4 MM$ y deja 700–850 u/mes de holgura en nov, ene y feb, pero no en diciembre (también queda saturado), así que solo ayuda si el alza se conoce al menos desde noviembre.
- **¿Y si la demanda de diciembre sube más (re-planificando con el alza conocida)?** +10 %: sigue factible con 18 (306,9 MM$, HE 14.250 u); +12,5 %: contrata 1 en septiembre (19 trabajadores, 308,4 MM$); +20 %: 312,6 MM$.
- **¿Qué se cede frente a P2, que no hace ningún ajuste de personal?** El plan Sol. 5 hace un ajuste (−2 en marzo) y duplica la HE (13.000 u = 10,8 % de la producción vs 6.000 u = 5,0 %; HE en 6 meses vs 4; HE al 100 % en nov–dic vs 83 % máx. en P2). A cambio ahorra 13,9 MM$ (4,4 %) y da servicio completo. "Estable" = dotación y producción regular (9.000 u/mes); la desviación estándar de la producción total no es menor que la de P2 (1.263 vs 1.225; P3 1.354); solo P1 es totalmente plana (0).

## D4. Desagregación (10 %)

- Estándar 5.000, Plus 3.000, Premium 2.000 u/mes. Motor estándar = 5.000 + 3.000; módulo = 3.000 + 2.000; hélice = 10.000; motor premium = control = 2.000.
- **¿Por qué no son tamaños de pedido?** Son *tasas de consumo* ($D_i$). Cuánto y cuándo pedir lo decide el EOQ y el ROP.
- **¿Por qué constantes?** Tasa agregada fija, mezcla fija, BOM fija y producción pareja en los días operativos.
- **¿Qué pasa si se usa el plan óptimo de la Parte I?** La producción varía (8.500–11.700); el consumo de componentes no sería constante y el EOQ clásico sería una aproximación. Los $D_i$ anuales no cambian (todo plan con I₀ = I₁₂ = 1.000 y B = 0 produce 120.000 u); en nov–dic (11.700 u/mes, 20 días operativos) el consumo diario sube a 468 / 117 / 585 / 292,5 / 117 y los ROP a 2.808 / 1.170 / 4.680 / 2.925 / 1.404; con los lotes multiproducto T < L en motor estándar, hélice y módulo, así que el ROP se aplica sobre la posición de inventario.
- **¿Y con mezcla 40-30-30?** Motor estándar 7.000/mes (84.000/año), motor premium 3.000 (36.000), hélice 10.000 (120.000), módulo 6.000 (72.000), control 3.000 (36.000).
- **¿Por qué la lista de materiales es parcial?** El enunciado indica que solo se consideran los componentes relevantes y se omiten el pedestal y otros elementos comunes.

## D5. EOQ individuales y factibilidad (15 %)

- **Trade-off EOQ**: lotes grandes → pocos pedidos (menos $DS/Q$) pero más inventario (más $hQ/2$). En $Q^*$ ambos costos son iguales.
- **Sensibilidades rápidas**: $Q^* \propto \sqrt{D}, \sqrt{S}, 1/\sqrt{h}$. Si la demanda se duplica, $Q^*$ sube ×1,41 y el ROP se duplica.
- **Efecto del plazo**: el ROP = $d \cdot L$ crece con $L$; $Q^*$ no depende de $L$. Si $L > T$, hay pedidos en tránsito y el ROP se aplica a la posición de inventario (físico + en tránsito). Aquí $L < T$ en todos.
- **¿Por qué 240 días?** Son los días operativos del enunciado: $d = D/240$ y $T$ y $L$ se miden en días operativos (si $L$ fuera en días corridos habría que convertirlo).
- **¿Y si la tasa de mantención fuera 20 % o 30 %?** $Q^* \propto 1/\sqrt{i}$: con 20 % los EOQ usan 126,5 m³ y 151,1 MM$; con 30 %, 103,2 m³ y 123,3 MM$; en ambos casos siguen infactibles.
- **¿Por qué no hay stock de seguridad?** Demanda y plazos determinísticos (regla explícita de la rúbrica).
- **¿Por qué la suma de óptimos no es factible?** Cada EOQ minimiza su propio costo sin "ver" la bodega ni el capital; los EOQ requieren 113,1 m³ (> 90) y 135,1 MM$ (> 110).

## D6. Multiproducto y sensibilidad (20 %)

- **Formulación**: ver informe. Convexa → KKT suficiente: $Q_i = \sqrt{2 D_i S_i / (h_i + 2\mu v_i + 2\lambda c_i)}$.
- **¿Por qué no se incluye $D_i c_i$?** Es constante: se compra lo mismo al año con cualquier lote. Solo importaría con descuentos por cantidad.
- **¿Qué significa $\mu = 5.098$?** Un m³ más de bodega ahorraría ≈ $5.098/año (en el margen). **$\lambda = 0{,}0595$**: $1 más de presupuesto ahorraría ≈ $0,06/año.
- **¿Por qué +10 % de espacio ahorra tan poco (5.219)?** Con solo la restricción de capital, los lotes ocupan 92,07 m³: de los 9 m³ nuevos solo se usan 2,07 y el espacio deja de estar activo ($\mu = 0$).
- **¿Por qué +10 % de presupuesto ahorra 386.591?** Se aprovecha completo; el espacio sigue activo y $\mu$ sube (24.785) porque ahora la bodega es lo que más limita; $\lambda$ baja a 0,0135 (rendimientos decrecientes).
- **"Activa" vs "valor marginal"**: activa = se usa al 100 % ($g(Q^*)=0$); por holgura complementaria solo ella puede tener multiplicador positivo, pero activa no implica valiosa. Su valor depende del multiplicador, que es *local* y cambia al relajar; dos restricciones activas pueden valer muy distinto.
- **¿Hasta dónde sirve cada multiplicador?** Son pendientes locales, no precios constantes. El espacio deja de valer desde V ≥ 92,07 m³ (+2,3 %; μ = 0): 5.219 $/año es el techo de cualquier ampliación de bodega (≈2.500 $/m³ de valor medio vs 5.098 marginal). El capital deja de ser activo desde K ≥ 125,1 MM$ (+13,7 %; entonces solo limita el espacio, μ = 31.254): techo 413.790 $/año con 90 m³; el +10 % ya captura el 93 % (386.591 / 413.790).
- **¿Y con +10 % en ambos recursos?** Costo 33.991.379; ahorro 511.638 > 5.219 + 386.591 = 391.810: los recursos son complementarios.
- **¿Basta achicar todos los EOQ por igual?** Con factor 0,796 (−20,4 %) cumple 90 m³ (usa 107,5 MM$) pero cuesta 34,67 MM$: 163 mil $/año (+0,47 %) más que el óptimo, porque espacio y capital pesan distinto en cada componente.
- **¿Por qué en el multiproducto ordenar ≠ mantener?** Porque Q < Q*: la igualdad solo vale en el EOQ sin restricciones (motor estándar: ordenar 6.213.598 vs mantener 4.171.496). En total ordenar sube de 16,89 a 20,75 MM$ y mantener baja de 16,89 a 13,75 MM$ (= 0,25·110/2, exacto con el capital activo).
- **¿Y si solo existiera una de las dos restricciones?** Solo espacio: 34.089.228 $/año ($\mu$ = 31.254), pero usaría 125,1 MM$ de capital. Solo capital: 34.497.798 $/año ($\lambda$ = 0,0636), usando 92,07 m³. Ninguna de las dos por sí sola asegura cumplir la otra.
- **¿Y si la restricción fuera de inventario promedio ($Q/2$)?** El recurso disponible equivaldría al doble para lotes completos; los EOQ (56,6 m³ y 67,6 MM$ promedio) serían factibles y el problema no tendría restricciones activas. Usamos lotes completos (Sesión 4: espacio para todos los lotes simultáneamente).

## D7. Integración (10 %)

- Parte I decide **cuánto producir y con cuánta gente**; Parte II traduce producción en **tasas de consumo**; Parte III decide **cuánto y cuándo comprar**.
- La Gerencia elige una tasa estable de 10.000 u/mes para compras (lógica de P1) aunque el plan agregado óptimo no sea plano: es un trade-off entre costo de producción y simplicidad/estabilidad del abastecimiento.
- **Uso de IA**: se usó como apoyo para programar y redactar; todos los resultados se verificaron (políticas validadas con `validar()` en código y recalculadas con fórmulas en las hojas P1–P3 del Excel; MILP con chequeo de balance y costo recalculado = FO; EOQ multiproducto por KKT verificado con SLSQP).

## D8. Código y reproducibilidad

- **Ejecutar todo:** `cd proyecto/01_codigo && python run_all.py` (≈6 s; regenera `02_resultados/`: Excel, CSV, figuras, `.lp`, `resumen.json`).
- **Datos:** `datos.py` lee los parámetros del Excel oficial `Datos_Proyecto_Ventisur_1.xlsx`; nada está escrito a mano en los modelos.
- **Cambiar un parámetro en vivo:** `con(plan, c_he=3000)` (en `parte1_sensibilidad.py`) devuelve una copia del plan; luego `parte1_modelos.costo_optimo(plan, multa=True, cero_pend=True)` entrega el costo óptimo sin escribir archivos (o `construir` + `solve` para ver el plan). La constante M está en `big_m` (y la más ajustada en `big_m_ajustada`).
- **EOQ multiproducto:** `parte3_inventarios.py` lo resuelve por KKT con bisección anidada y lo verifica con SLSQP (aserción: diferencia relativa < 1e-5).
- **Excel:** celdas amarillas = decisiones o multiplicadores (valores); el resto son fórmulas; cada hoja de plan tiene una celda *Chequeos* (fila 18) que debe decir OK. En los `.lp` el índice 0 = marzo.
