# Guía de preparación para la defensa oral — Ventisur

La rúbrica evalúa **principalmente la defensa**: no basta leer un número, hay que explicar por qué.
Esta guía resume las preguntas más probables por dimensión y una respuesta corta y razonada para cada una.
Todas las cifras salen de `02_resultados/` (Excel, CSV o `resumen.json`).

---

## Guion de 5 minutos (8 diapositivas)

| Diap. | Tiempo | Mensaje central |
|---|---|---|
| 1 Portada | 0:15 | Plan agregado a 12 meses y, después, la compra de 5 componentes |
| 2 Políticas simples | 0:40 | Mismo costo laboral (288 MM$); cambia el mecanismo: inventario, HE o personal |
| 3 Modelo A | 1:00 | Combina los mecanismos: 18 trabajadores, HE en el peak, inventario corto y atrasos baratos |
| 4 B, C y Sol. 5 | 0:45 | Binaria con M; servicio completo cuesta solo 0,35 MM$ |
| 5 Recomendación agregada | 0:30 | Plan Sol. 5 + seguro de 19 trabajadores |
| 6 Componentes y EOQ | 0:40 | Tasas constantes → EOQ; infactible en espacio y capital |
| 7 Multiproducto | 0:50 | Ambas activas, pero el presupuesto vale 74 veces más |
| 8 Integración | 0:30 | Conectar las tres partes |

---

## D1. Políticas simples (10 %)

- **¿Por qué P1 no viola la bodega?** El inventario máximo es 7.000 u (ago–oct) ≤ 7.500. Producción anual 120.000 = demanda total, así que termina en 1.000 = inicial.
- **¿Por qué P2 tiene capacidad ociosa?** La regla fija 20 trabajadores (10.000 u regulares) pero la demanda de mar–ago es menor; como el inventario debe quedar en 1.000, se produce menos que la capacidad: 6.000 u ociosas.
- **¿Cómo se calcula la dotación de P3?** $W_t = \lceil (d_t + I^{obj}_t - I_{t-1}) / 500 \rceil$, acotada por 15–25 y por ±3 respecto del mes anterior. Marzo: (9.500 − 1.000)/500 = 17. Febrero: (10.500 + 1.000)/500 = 23.
- **¿Por qué las tres tienen igual costo laboral?** Las tres suman 240 trabajador-mes (P3: 17+18+17+17+18+19+20+20+23+25+23+23 = 240).
- **¿Qué pasa si sube el costo de mantener?** P1 sube 52.000 $ por cada $1 de aumento (52.000 u-mes); P2 sube 12.000 por $1; P3 casi no cambia.
- **¿Desde qué costo de HE P3 supera a P2?** P2 = 300 MM$ + 6.000·c_HE; P3 = 329,5 MM$ → c_HE > $4.917/u.

## D2. Modelo A (20 %)

- **Significado de cada restricción**: ver la tabla del informe. Claves: el costo laboral multiplica $W_t$ (se paga aunque no se produzca); capacidades regular y HE separadas; balance con inventario neto $I - B$.
- **¿Por qué $W, H, F$ enteras y la producción continua?** No existen fracciones de trabajador; la producción es de miles de unidades y redondear no cambia la decisión. La relajación lineal da 300,68 MM$ (diferencia 0,07 MM$).
- **¿Por qué no se exige usar primero la regular antes de HE?** Porque la regular ya está pagada (costo 0 marginal) y la HE cuesta $2.500: el óptimo lo hace solo (Guía de Modelos, pregunta 1e).
- **¿Puede haber $I_t > 0$ y $B_t > 0$ a la vez?** En el óptimo no: ambos cuestan, y reducir los dos en la misma cantidad mantiene el balance y baja el costo.
- **¿Por qué despide 2 en marzo?** Un trabajador cuesta 14,4 MM$/año; su capacidad extra solo sirve en el peak. Sus 500 u/mes de peak con HE cuestan 1,25 MM$/mes. Mantener 20 cuesta 306,5 MM$ (con cero pendientes) vs 301,1.
- **¿Por qué hay capacidad ociosa en marzo y mayo si luego se paga HE?** Guardar una unidad 3+ meses cuesta ≥ $3.000 > $2.500 de la HE. Solo conviene adelantar 1–2 meses (jun–jul → ago; oct–nov → dic).
- **¿Por qué acepta atrasos?** $b = 750 < h = 1.000$: atrasar un mes es más barato que adelantar un mes. Incluso con $b = 1.500$ sigue habiendo 200 u de atraso (301,0 MM$), porque adelantar exigiría HE en octubre + 2 meses de inventario (2.500 + 2.000 = 4.500) vs HE en enero + 1 mes de atraso (2.500 + 1.500 = 4.000).
- **¿Qué pasa si quito el límite de ±3?** Nada (mismo óptimo, 300,75 MM$): esa restricción no está activa.
- **¿Y si la bodega fuera 2.000?** Tampoco cambia: el inventario máximo del óptimo es 1.000.
- **¿Qué pasa si la HE rinde 100 u/trab-mes?** Contrata 2 en septiembre (20 trabajadores) y el costo sube a 304,5 MM$.
- **¿Si el costo de inventario fuera $500?** Adelanta más (5.000 u-mes de inventario) y el costo baja a 299,1 MM$.

## D3. Modelos B, C y recomendación (15 %)

- **Rol de la binaria**: $B_t \le 0{,}01 d_t + M_t y_t$. Si $B_t$ supera el 1 %, la restricción solo se cumple con $y_t = 1$ (y se paga $3 MM). Si no lo supera, $y_t$ podría ser 1, pero el costo hace que el modelo elija 0.
- **¿Por qué ese $M$?** Debe ser ≥ el mayor valor posible de $B_t - 0{,}01 d_t$ para no cortar soluciones. El peor caso es no producir nada hasta $t$ (factible, $R_t$ puede ser 0): $M_t = \sum_{k \le t} d_k - I_0 - 0{,}01 d_t$. Un $M$ enorme (p. ej. $10^9$) también es válido pero debilita la relajación lineal.
- **¿Por qué B no paga multas?** Recortar los pendientes de dic. de 400 a 125 cuesta +193.750; una multa cuesta 3 MM$.
- **¿Por qué Sol. 5 = Sol. 4?** Con $B_t = 0$, la condición $0 \le 0{,}01 d_t$ se cumple siempre con $y_t = 0$; la multa es irrelevante.
- **Costo de elevar el servicio**: A → C = +350.000 (0,12 %). Se cambian 600 u-mes de atraso por 800 u-mes de inventario (800·1.000 − 600·750 = 350.000).
- **¿Por qué no recomiendan simplemente el más barato (A)?** Tiene atrasos que gatillarían multas reales (dic 400 > 125; ene 200 > 115) y daño comercial; el sobrecosto de servicio completo es mínimo.
- **¿Qué tan robusto es el plan?** Con demanda de diciembre +5 % el mismo plan de 18 trabajadores sigue siendo factible sin atrasos (303,9 MM$), adelantando más inventario. El riesgo es la HE al 100 % en nov–feb: el seguro de 19 trabajadores cuesta +1,4 MM$.

## D4. Desagregación (10 %)

- Estándar 5.000, Plus 3.000, Premium 2.000 u/mes. Motor estándar = 5.000 + 3.000; módulo = 3.000 + 2.000; hélice = 10.000; motor premium = control = 2.000.
- **¿Por qué no son tamaños de pedido?** Son *tasas de consumo* ($D_i$). Cuánto y cuándo pedir lo decide el EOQ y el ROP.
- **¿Por qué constantes?** Tasa agregada fija, mezcla fija, BOM fija y producción pareja en los días operativos.
- **¿Qué pasa si se usa el plan óptimo de la Parte I?** La producción varía (8.500–11.700); el consumo de componentes no sería constante y el EOQ clásico sería una aproximación.

## D5. EOQ individuales y factibilidad (15 %)

- **Trade-off EOQ**: lotes grandes → pocos pedidos (menos $DS/Q$) pero más inventario (más $hQ/2$). En $Q^*$ ambos costos son iguales.
- **Sensibilidades rápidas**: $Q^* \propto \sqrt{D}, \sqrt{S}, 1/\sqrt{h}$. Si la demanda se duplica, $Q^*$ sube ×1,41 y el ROP se duplica.
- **Efecto del plazo**: el ROP = $d \cdot L$ crece con $L$; $Q^*$ no depende de $L$. Si $L > T$, hay pedidos en tránsito y el ROP se aplica a la posición de inventario (físico + en tránsito). Aquí $L < T$ en todos.
- **¿Por qué no hay stock de seguridad?** Demanda y plazos determinísticos (regla explícita de la rúbrica).
- **¿Por qué la suma de óptimos no es factible?** Cada EOQ minimiza su propio costo sin "ver" la bodega ni el capital; los EOQ requieren 113,1 m³ (> 90) y 135,1 MM$ (> 110).

## D6. Multiproducto y sensibilidad (20 %)

- **Formulación**: ver informe. Convexa → KKT suficiente: $Q_i = \sqrt{2 D_i S_i / (h_i + 2\mu v_i + 2\lambda c_i)}$.
- **¿Por qué no se incluye $D_i c_i$?** Es constante: se compra lo mismo al año con cualquier lote. Solo importaría con descuentos por cantidad.
- **¿Qué significa $\mu = 5.098$?** Un m³ más de bodega ahorraría ≈ $5.098/año (en el margen). **$\lambda = 0{,}0595$**: $1 más de presupuesto ahorraría ≈ $0,06/año.
- **¿Por qué +10 % de espacio ahorra tan poco (5.219)?** Con solo la restricción de capital, los lotes ocupan 92,07 m³: de los 9 m³ nuevos solo se usan 2,07 y el espacio deja de estar activo ($\mu = 0$).
- **¿Por qué +10 % de presupuesto ahorra 386.591?** Se aprovecha completo; el espacio sigue activo y $\mu$ sube (24.785) porque ahora la bodega es lo que más limita; $\lambda$ baja a 0,0135 (rendimientos decrecientes).
- **"Activa" vs "valor marginal"**: activa = se usa al 100 %. Su valor depende del multiplicador, que es *local* y cambia al relajar; dos restricciones activas pueden valer muy distinto.
- **¿Y si la restricción fuera de inventario promedio ($Q/2$)?** El recurso disponible equivaldría al doble para lotes completos; los EOQ (56,6 m³ y 67,6 MM$ promedio) serían factibles y el problema no tendría restricciones activas. Usamos lotes completos (Sesión 4: espacio para todos los lotes simultáneamente).

## D7. Integración (10 %)

- Parte I decide **cuánto producir y con cuánta gente**; Parte II traduce producción en **tasas de consumo**; Parte III decide **cuánto y cuándo comprar**.
- La Gerencia elige una tasa estable de 10.000 u/mes para compras (lógica de P1) aunque el plan agregado óptimo no sea plano: es un trade-off entre costo de producción y simplicidad/estabilidad del abastecimiento.
- **Uso de IA**: se usó como apoyo para programar y redactar; todos los resultados se verificaron (políticas recalculadas a mano y en Excel con fórmulas; MILP verificado con chequeos de balance y costo; EOQ multiproducto resuelto por KKT y verificado con un segundo optimizador).
