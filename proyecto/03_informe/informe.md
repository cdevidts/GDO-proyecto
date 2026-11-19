---
title: "Proyecto Integrador Ventisur"
subtitle: "Informe técnico · Gestión de Operaciones, Sección 2 · Universidad Adolfo Ibáñez"
seccion: "Sección 2"
author:
  - Cristóbal De Vidts
  - Constanza Catalán
  - Bellonce Bulnes
  - Matias Rojas Rodriguez
date: "8 de noviembre de 2026"
lang: es
---

::: {.respaldo custom-style="Respaldo"}
**Respaldo reproducible.** Todos los resultados de este informe se pueden regenerar ejecutando `python proyecto/01_codigo/run_all.py` (PuLP 2.9 con CBC, y SciPy para verificar). La planilla `02_resultados/Resultados_Ventisur.xlsx` recalcula con sus propias fórmulas los balances, capacidades, costos, EOQ y uso de recursos a partir de las decisiones. Los Modelos A–D de la Parte I están exportados en formato `.lp` en `02_resultados/modelos_lp/`. El EOQ multiproducto, que no es lineal, está documentado en `ModeloE_Sol9_EOQ_multiproducto.txt` y se resuelve en `parte3_inventarios.py`. Todos los costos están en pesos chilenos (MM\$ = millones de pesos).
:::

# Parte I — Planificación agregada

## Solicitud 1. Políticas simples

| | Política 1: tasa constante | Política 2: dotación constante + HE | Política 3: persecución (solo regular) |
|--------------------------|--------------------|------------------------|-----------------------------|
| Regla | 20 trab., 10.000 u/mes regulares | 20 trab., producir $d_t$ (regular, luego HE), $I_t=1.000$ | $W_t=\lceil (d_t+I^{obj}_t-I_{t-1})/500\rceil$, $I_t=0$ salvo feb. (1.000) |
| Mecanismo de ajuste | Inventario | Horas extra (y capacidad ociosa) | Contratación/despido |
| Dotación | 20 fija | 20 fija | 17–25 (9 contrat., 6 desp.) |
| Uso de HE (u) | 0 | 6.000 (nov–feb) | 0 |
| Inventario máx. / acum. (u / u-mes) | 7.000 / 52.000 | 1.000 / 12.000 | 1.000 / 1.000 |
| Costo laboral (MM\$) | 288,0 | 288,0 | 288,0 |
| Costo contrat. + despido (MM\$) | 0 | 0 | 22,5 + 18,0 |
| Costo HE (MM\$) | 0 | 15,0 | 0 |
| Costo inventario (MM\$) | 52,0 | 12,0 | 1,0 |
| **Costo total (MM\$)** | **340,0** | **315,0** | **329,5** |

: Políticas simples: regla, recursos utilizados y costo anual.

| Mes | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct | Nov | Dic | Ene | Feb |
|----------------|----:|----:|----:|----:|----:|----:|-----:|-----:|-----:|-----:|-----:|-----:|
| $d_t$ | 9.500 | 9.000 | 8.500 | 8.500 | 9.000 | 9.500 | 10.000 | 10.000 | 11.500 | 12.500 | 11.500 | 10.500 |
| P1: $I_t$ ($W$=20, $R$=10.000) | 1.500 | 2.500 | 4.000 | 5.500 | 6.500 | 7.000 | 7.000 | 7.000 | 5.500 | 3.000 | 1.500 | 1.000 |
| P2: $R_t$ ($W$=20, $I_t$=1.000) | 9.500 | 9.000 | 8.500 | 8.500 | 9.000 | 9.500 | 10.000 | 10.000 | 10.000 | 10.000 | 10.000 | 10.000 |
| P2: $O_t$ | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.500 | 2.500 | 1.500 | 500 |
| P3: $W_t$ ($H_t$/$F_t$) | 17 (−3) | 18 (+1) | 17 (−1) | 17 | 18 (+1) | 19 (+1) | 20 (+1) | 20 | 23 (+3) | 25 (+2) | 23 (−2) | 23 |
| P3: $R_t$ ($I_t$=0 salvo feb.) | 8.500 | 9.000 | 8.500 | 8.500 | 9.000 | 9.500 | 10.000 | 10.000 | 11.500 | 12.500 | 11.500 | 11.500 |

: Plan mensual de las políticas simples (unidades y trabajadores).

Las tres políticas son factibles: respetan la bodega (≤7.500), dotación 15–25, ±3 trabajadores/mes, $I_0=I_{12}=1.000$ y cero pendientes. Lo verificamos en código y en la celda *Chequeos* (fila 18) de cada hoja de plan del Excel, todas en OK. En P3 la dotación entera cubre exactamente la demanda neta mensual, y en marzo aprovecha el inventario inicial (9.500−1.000 = 8.500 = 17×500). Las cotas de ±3 se alcanzan en marzo (−3) y noviembre (+3), y el máximo de 25 en diciembre, sin impedir seguir la demanda. Pero la regla es miope: con otros datos habría que contratar antes.

**Comparación.** Las tres pagan la misma masa laboral, 288 MM\$ o 240 trabajador-mes, y P3 solo redistribuye esos 240 en el año. Por eso la diferencia está únicamente en el mecanismo de ajuste. **P1**, de nivelación, es la más simple y estable para proveedores y personal, pero acumula hasta 7.000 u en bodega (93 % de su capacidad). El stock que forma de marzo a agosto para cubrir noviembre–febrero paga \$1.000 por unidad y mes: es la más cara. **P2**, mixta, mantiene la dotación y absorbe el peak con HE a \$2.500/u. Es la mejor de las simples porque una HE (\$2.500) equivale a 2,5 meses de mantención, mientras que P1 guarda las ~6.000 u del peak 6,7 meses en promedio (40.000 u-mes extra, o \$6.667/u). A cambio, deja 6.000 u de capacidad regular ociosa en marzo–agosto y en diciembre usa el 83 % de la capacidad de HE (2.500/3.000). **P3**, de persecución, casi elimina el inventario y no usa HE. Pero sus 9 contrataciones y 6 despidos (40,5 MM\$) cuestan más de lo que ahorra frente a P2 en inventario (11 MM\$) y HE (15 MM\$). Además, sus 15 movimientos generan inestabilidad laboral y costos de aprendizaje de los nuevos trabajadores. *Anticipación:* P2 supera a P1 mientras la HE cueste < \$6.667/u (40.000 u-mes extra de P1 ÷ 6.000 u) y a P3 mientras cueste < \$4.917/u (29,5 MM\$ ÷ 6.000 u). P1 superaría a P2 solo si mantener costara < \$375/u-mes (40.000·h < 15 MM\$).

## Solicitud 2. Modelo A: formulación

**Índices y conjuntos.** $t=1,\dots,12$ (marzo…febrero). **Parámetros:** demanda $d_t$; $W_0=20$; $I_0=1.000$; $B_0=0$; $a=500$, $e=150$ (u/trab-mes regular y HE); $c^W=1\text{,}2$ MM, $c^H=2\text{,}5$ MM, $c^F=3$ MM, $c^O=2.500$, $h=1.000$, $b=750$; $\bar I=7.500$; $\underline W=15$, $\overline W=25$; $\overline H=\overline F=3$; $I^{fin}=1.000$.

**Variables.** $W_t\in\mathbb Z_+$ trabajadores disponibles en $t$; $H_t,F_t\in\mathbb Z_+$ contratados/despedidos al inicio de $t$; $R_t\ge0$ unidades en tiempo regular; $O_t\ge0$ unidades en HE; $I_t\ge0$ inventario al cierre; $B_t\ge0$ pedidos pendientes al cierre (demanda aceptada no entregada). Las personas se modelan como enteras, porque no se contrata una fracción, y la producción como continua, pues son miles de unidades.

::: {style="break-after: avoid; break-inside: avoid"}
$$\min Z=\sum_{t=1}^{12}\left(c^W W_t+c^H H_t+c^F F_t+c^O O_t+h\,I_t+b\,B_t\right)$$
sujeto a, $\forall t$:
:::

| Restricción | Propósito en Ventisur |
|------|--------------|
| $W_t=W_{t-1}+H_t-F_t$ | Evolución de la dotación (conecta los meses) |
| $R_t\le a\,W_t$;  $O_t\le e\,W_t$ | Capacidad regular y de HE dependen de la dotación; capacidades independientes |
| $I_{t-1}-B_{t-1}+R_t+O_t-d_t=I_t-B_t$ | Balance de inventario neto: lo disponible menos la demanda queda en bodega o como pendiente |
| $I_t\le 7.500$ | Capacidad de bodega de producto terminado |
| $15\le W_t\le25$; $H_t\le3$; $F_t\le3$ | Políticas de dotación y de movimientos de personal |
| $I_{12}\ge1.000$; $B_{12}=0$; $W_0,I_0,B_0$ dados | Condiciones de borde: el horizonte no "consume" el inventario de seguridad ni traspasa deuda con clientes |

: Modelo A: restricciones y su propósito.

**Función objetivo.** Incluye todos los costos que cambian entre planes. El costo laboral se paga por trabajador disponible aunque no produzca, por eso multiplica $W_t$ y no $R_t$: la producción regular no tiene costo variable propio. Tampoco hace falta imponer que la HE se use solo tras agotar la regular. Como la regular ya está pagada y la HE cuesta \$2.500/u, el modelo nunca prefiere HE si hay capacidad regular útil.

## Solicitud 2. Modelo A: solución e interpretación — **Z = 300,75 MM\$**

| Mes | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct | Nov | Dic | Ene | Feb |
|----------|----:|----:|----:|----:|----:|----:|-----:|-----:|-----:|-----:|-----:|-----:|
| $W_t$ (desp.) | 18 (−2) | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 |
| $R_t$ | 8.500 | 9.000 | 8.500 | 9.000 | 9.000 | 9.000 | 9.000 | 9.000 | 9.000 | 9.000 | 9.000 | 9.000 |
| $O_t$ | 0 | 0 | 0 | 0 | 0 | 0 | 1.000 | 1.200 | 2.700 | 2.700 | 2.700 | 2.700 |
| $I_t$ / $B_t$ | 0 | 0 | 0 | 500 | 500 | 0 | 0 | 200 | 400 | 0 / **400** | 0 / **200** | 1.000 |

: Modelo A: plan óptimo mes a mes (trabajadores y unidades).

Costos: laboral 259,2; despido 6,0; HE 32,5 (13.000 u); inventario 2,6, y pendientes 0,45 MM\$. El modelo **despide 2 trabajadores en marzo y mantiene 18 todo el año**. Conservar un trabajador cuesta 14,4 MM\$/año (11,4 netos del despido evitado), pero su capacidad solo hace falta de septiembre a febrero. Cubrir esas ~3.000 u con HE cuesta ≈7,5 MM\$. Conservarlo convendría solo si se usara ≥ 9,1 meses al año (11,4 MM\$ netos ÷ 1,25 MM\$ de HE evitada por mes de uso = 500 u × \$2.500), y aquí se requieren unos 6. Además, combina tres mecanismos que las políticas simples usaban por separado. Primero, **HE** desde septiembre, saturadas de noviembre a febrero (2.700 = 150×18). Segundo, **inventario anticipado corto** (junio–julio para agosto, octubre–noviembre para el peak), porque mantener 1–2 meses (\$1.000–2.000) cuesta menos que una HE (\$2.500), pero 3 o más meses no. Por eso queda capacidad regular ociosa en marzo y mayo (1.000 u) aunque luego se paguen HE. Tercero, **pedidos pendientes** en diciembre–enero, porque postergar una unidad un mes (\$750) cuesta menos que fabricarla antes y guardarla (\$1.000/mes). Así, mejora a P2 en 14,25 MM\$ (−4,5 %), a P3 en 28,75 y a P1 en 39,25 MM\$. *Descomposición:* frente a P2 ahorra 28,8 MM\$ de mano de obra (2 trabajadores × 12 meses que P2 solo usaba de septiembre a febrero, con 6.000 u ociosas en marzo–agosto) y 9,4 de inventario, y paga 6,0 de despidos, 17,5 de HE adicional (7.000 u) y 0,45 de atrasos. Frente a P1 evita 49,4 de inventario y 28,8 de mano de obra, a costa de 32,5 de HE, 6,0 de despidos y 0,45 de atrasos. Frente a P3 ahorra 28,8 de mano de obra y 34,5 de contratación y despido (evita 13 de sus 15 movimientos), a costa de 32,5 de HE, 1,6 de inventario y 0,45 de atrasos.

**Comportamientos contraintuitivos.** El modelo despide en marzo para luego operar con HE al 100 % en el peak, deja capacidad regular ociosa mientras paga HE meses después y acepta atrasos con clientes aun teniendo inventario dos meses antes. Todo se explica porque $b<h$: atrasar es más barato que adelantar. La relajación lineal (personas continuas) vale 300,68 MM\$: la integralidad cuesta solo 0,07 MM\$. El óptimo es único: al exigir $Z\le Z^*+10$ \$ y minimizar/maximizar cada variable, no queda holgura en $W,R,O,I,B$ (función `unicidad_optimo`, también para B y C). El modelo exige $I_{12}\ge1.000$, que en el óptimo se cumple con igualdad.

## Solicitud 3. Modelo B: multa contractual — **Z = 300,94 MM\$**

Agregamos $y_t\in\{0,1\}$, que vale 1 si en el mes $t$ se paga la multa, y:
$$B_t\le 0\text{,}01\,d_t+M_t\,y_t\quad\forall t,\qquad Z_B=Z_A+\sum_t 3.000.000\,y_t .$$
Si $B_t>0\text{,}01d_t$, la restricción obliga $y_t=1$. Si $B_t\le0\text{,}01d_t$, el modelo elige $y_t=0$ porque la multa es costosa, y no hace falta forzar el caso contrario. La constante $M_t$ debe acotar $B_t-0\text{,}01d_t$ sin eliminar soluciones factibles. Usamos $M_t=\sum_{k\le t}d_k-I_0-0\text{,}01d_t$, el peor caso de no producir nada hasta $t$ e ignorar las condiciones finales (p. ej., $M_{dic}=96.875$). Vale para planes sin $I_t$ y $B_t$ positivos a la vez, como ocurre siempre en el óptimo. Es válida y simple, pero **no la más ajustada**: con $B_{12}=0$, $I_{12}\ge1.000$ y la capacidad máxima mensual bastaría $M_{dic}=9.375$ sin cambiar el óptimo (300.943.750; `big_m_ajustada`), y $y_{12}$ sobra porque $B_{12}=0$. Un $M$ muy chico cortaría planes válidos, y uno exageradamente grande debilita la relajación lineal y la estabilidad numérica.

**Resultado.** Ninguna multa se activa: el modelo baja los pendientes de diciembre de 400 a 125 u (justo el 1 % de 12.500) y elimina los de enero, con más HE en octubre (1.475 u) e inventario en octubre–noviembre (475 y 675 u). La dotación sigue en 18. Pagar una multa de \$3 MM nunca conviene: eliminar 400 u de atraso cuesta como máximo unos cientos de miles de pesos. Frente a A, el costo adicional es **+0,19 MM\$**.

## Solicitud 4. Modelo C: cero pendientes — **Z = 301,10 MM\$**

Al Modelo A se agrega $B_t=0\ \forall t$, que equivale a eliminar $B_t$ del balance y de la FO. La solución mantiene 18 trabajadores y 13.000 u de HE, pero adelanta producción: la HE de octubre sube a 1.600 u y el inventario de octubre–noviembre, a 600 y 800 u. Así cubre diciembre, cuya capacidad (9.000 + 2.700 = 11.700) es menor que la demanda (12.500).

| Indicador | A (Sol. 2) | B (Sol. 3) | C (Sol. 4) |
|----------------------------|----------:|----------:|------------:|
| Costo total (MM\$) | 300,75 | 300,94 | 301,10 |
| Dotación / despidos | 18 / 2 | 18 / 2 | 18 / 2 |
| Producción regular / total (u) | 107.000 / 120.000 | idem | idem |
| HE total (u) / inventario acumulado (u-mes) | 13.000 / 2.600 | 13.000 / 3.150 | 13.000 / 3.400 |
| HE octubre / ene–feb (u) | 1.200 / 5.400 | 1.475 / 5.125 | 1.600 / 5.000 |
| Inventario oct / nov (u) | 200 / 400 | 475 / 675 | 600 / 800 |
| Pendientes (u-mes) / máximo mensual | 600 / 400 (3,2 % dic.) | 125 / 125 (1 %) | 0 / 0 |
| Demanda atendida a tiempo (anual) | 99,5 % | 99,9 % | 100 % |
| **Costo de elevar el servicio vs A** | — | **+193.750** | **+350.000 (0,12 %)** |

: Modelos A, B y C: costo, uso de recursos y nivel de servicio.

Esos 350 mil pesos cambian 600 u-mes de atraso por 800 u-mes más de inventario, con la misma producción total (120.000 u). Para eso, C mueve HE de enero y febrero a octubre (+400 u) y guarda 400 u más en octubre–noviembre. Como en el peak las HE ya están al máximo, anticipar inventario es lo más barato para eliminar atrasos (+0,35 MM\$ sobre A). Mantener 19 trabajadores, en cambio, cuesta +1,4 MM\$ sobre C (hoja *Sensibilidad_P1*). Conceptualmente, A penaliza el atraso en forma lineal y blanda (\$750/u-mes), B agrega un costo fijo al superar el umbral (no convexo, por eso la binaria) y C lo prohíbe con una restricción dura. Con el contrato de la Sol. 3, el plan A costaría 306,75 MM\$ por dos multas (300,75 + 6,0). B lo baja a 300,94, pero deja 125 u, justo el 1 % de diciembre, sin margen ante errores de pronóstico: una unidad más gatilla \$3 MM. Pasar a C cuesta solo 0,156 MM\$ más.

## Solicitud 5. Multa + cero pendientes y recomendación (Modelo D en los archivos) — **Z = 301,10 MM\$**

Al Modelo B se agrega $B_t=0$. Así, $B_t=0\le0\text{,}01d_t$ se cumple siempre con $y_t=0$, la multa nunca se activa y el modelo **coincide con C** (mismo plan, 301,10 MM\$). Con servicio completo, la cláusula contractual deja de ser relevante.

::: {.recomendacion custom-style="Recomendacion"}
**Recomendación.** Proponemos adoptar el plan de cero pendientes (Sol. 5). (1) Cuesta solo 0,35 MM\$ (0,12 %) más que el óptimo con atrasos y elimina el riesgo contractual y reputacional con los clientes principales: el plan A habría gatillado multas en diciembre y enero (400 > 125 y 200 > 115). (2) Es 13,9 MM\$ (4,4 %) más barato que la mejor política simple (P2), a cambio de un ajuste de personal de −2, que P2 no hace, y del doble de HE: 13.000 u (10,8 % de la producción) frente a 6.000 u (5,0 %) en P2. (3) Es **estable** en dotación y producción regular, con un solo ajuste de −2 en marzo y 9.000 u/mes (8.500 en marzo y mayo), aunque solo P1 tiene producción totalmente plana. (4) Usa poco inventario: máximo 1.000 u, el 13 % de la bodega. Su principal *trade-off*: la HE queda al 100 % en noviembre y diciembre (93 % en enero y febrero), sin holgura si el pronóstico se queda corto. Lo cuantificamos en la hoja *Sensibilidad_P1* (columnas de HE mensual y holgura). Mantener **19 trabajadores** (despedir a 1) cuesta 302,5 MM\$ (+1,4 MM\$, +0,46 %) y baja la HE a 9.500 u, con 700–850 u/mes de holgura en noviembre, enero y febrero (capacidad 19×150 = 2.850 u). Diciembre sigue al 100 %. Limitar la HE al 80 % cuesta 303,1 MM\$ y no despedir (20) cuesta 306,5 MM\$. Sugerimos el plan de 18 trabajadores como base y la variante de 19 como seguro si la Gerencia percibe alta incertidumbre en la demanda de fin de año. Suponemos demanda determinística, unidad agregada homogénea y productividad constante. Si la HE se encareciera 20 %, el óptimo subiría de 18 a 19 trabajadores en septiembre (307,1 MM\$).
:::

![Izquierda: producción total de P1–P3 y del óptimo Sol. 5 contra la demanda (área gris; eje desde 7.000). Derecha: inventario neto (I−B) de P1–P3, del Modelo A y del óptimo Sol. 5. A produce 400 u menos que Sol. 5 en octubre y 200 u más en enero y febrero.](../02_resultados/figuras/fig1_planes.png){width=100%}

# Parte II — De la producción a los requerimientos de materiales

## Solicitud 6

Con la tasa oficial de 10.000 u/mes y la mezcla 50–30–20 se producen 5.000 u/mes de Estándar (60.000/año), 3.000 de Plus (36.000) y 2.000 de Premium (24.000). Con la lista de materiales, $r_j=\sum_m u_{jm}\,P_m$, se obtiene:

| Componente | Usado por | Mensual | Anual |
|---|---|---|---:|
| Motor estándar | Estándar + Plus | 5.000 + 3.000 = 8.000 | 96.000 |
| Motor premium | Premium | 2.000 | 24.000 |
| Conjunto hélice–rejilla | los tres | 10.000 | 120.000 |
| Módulo electrónico | Plus + Premium | 3.000 + 2.000 = 5.000 | 60.000 |
| Control remoto | Premium | 2.000 | 24.000 |

: Requerimientos de componentes con 10.000 u/mes y mezcla 50–30–20 (u).

Coinciden con los valores oficiales. La lista de materiales es parcial: omite el pedestal y otros elementos comunes. Son **tasas de consumo**, no tamaños de pedido ni calendario de compras: dicen cuánto se consume por mes, y cuánto y cuándo pedir lo decide la Parte III. Pueden tratarse como constantes porque la Gerencia fijó una tasa de producción estable de 10.000 u/mes (la lógica de la Política 1), la mezcla y la lista de materiales son fijas y la producción se distribuye uniformemente en los días operativos. También se apoyan en supuestos de la planificación agregada: unidad agregada homogénea (cualquier modelo usa la misma capacidad), demanda determinística y una mezcla estable entre meses.

**Conexión con la Parte I.** Toda política con $I_0=I_{12}=1.000$ y $B=0$ produce 120.000 u/año, así que los $D_i$ oficiales sirven para cualquier plan y solo cambia el patrón dentro del año. El plan de costo mínimo mueve la producción entre 8.500 y 11.700 u/mes. Con él, el consumo de componentes no sería constante y el EOQ clásico sería solo una aproximación. La Gerencia acepta la tasa estable a cambio de una coordinación simple con los proveedores, justamente la ventaja de la Política 1.

# Parte III — Inventarios determinísticos

## Solicitudes 7 y 8. EOQ individuales y factibilidad conjunta

Usamos $h_i=0\text{,}25c_i$, $Q_i^*=\sqrt{2D_iS_i/h_i}$, $N_i=D_i/Q_i^*$, $T_i=Q_i^*/d_i$ (días), $d_i=D_i/240$, $ROP_i=d_iL_i$ y costo relevante $=D_iS_i/Q_i+h_iQ_i/2$, con $L_i$ en días operativos, la misma base que $d_i$.

| Componente | $h_i$ | $Q_i^*$ | $N_i$ | $T_i$ (días) | $d_i$ (u/día) | $L_i$ | ROP | Costo relevante | $v_iQ_i$ (m³) | $c_iQ_i$ (MM\$) |
|----------------|------:|------:|-----:|-------:|-------:|----:|------:|-----------:|---------:|---------:|
| Motor estándar | 3.000 | 3.394 | 28,3 | 8,5 | 400 | 6 | 2.400 | 10.182.338 | 13,58 | 40,73 |
| Motor premium | 5.000 | 1.453 | 16,5 | 14,5 | 100 | 10 | 1.000 | 7.266.361 | 7,27 | 29,07 |
| Hélice–rejilla | 1.125 | 5.657 | 21,2 | 11,3 | 500 | 8 | 4.000 | 6.363.961 | 84,85 | 25,46 |
| Módulo electrónico | 2.000 | 3.464 | 17,3 | 13,9 | 250 | 10 | 2.500 | 6.928.203 | 5,20 | 27,71 |
| Control remoto | 1.375 | 2.211 | 10,9 | 22,1 | 100 | 12 | 1.200 | 3.039.737 | 2,21 | 12,16 |
| **Total** | | | 94,2 | | | | | **33.780.600** | **113,10** | **135,12** |

: EOQ individual por componente y recursos que exigen los lotes completos.

**Política.** $Q^*$ indica *cuánto* pedir: equilibra el costo de ordenar, que baja con lotes grandes, con el de mantener, que sube. En el óptimo ambos son iguales (16,89 + 16,89 = 33,78 MM\$/año). El ROP indica *cuándo*: cuando el inventario llega a $d_iL_i$ se emite la orden y, con demanda y plazo conocidos, el lote llega justo al agotarse el stock, sin stock de seguridad. Por ejemplo: "pedir 3.394 motores estándar cuando queden 2.400 (6 días de consumo), unas 28 veces al año, cada 8,5 días operativos". Como $L_i<T_i$ en todos los casos, nunca hay más de un pedido en tránsito y el ROP sobre inventario físico coincide con el de la posición de inventario. El plazo solo mueve el *cuándo*, no el *cuánto*.

Los supuestos del EOQ se relacionan con la Parte II: la tasa estable de 10.000 u/mes da una demanda anual $D_i$ constante, la mezcla y la lista de materiales fijas hacen uniforme el consumo diario y el plazo conocido vuelve determinístico el ROP. Suponemos además plazo constante, reposición instantánea del lote completo, sin quiebres ni descuentos por cantidad, y costos $S,h$ constantes.

**Factibilidad conjunta.** Con el criterio conservador de la Sesión 4, que supone todos los lotes completos a la vez, los EOQ requieren **113,10 m³ > 90**, un exceso de 23,1 m³, y solo la hélice–rejilla ocupa 84,85 m³, el 94 % del espacio. En capital piden **135,12 MM\$ > 110 MM\$**, un exceso de 25,1 MM\$, y los motores usan 69,8 MM\$. Ambas restricciones se violan. Cada EOQ es óptimo mirando solo su propio trade-off e "ignora" que compite con los demás por la bodega y el capital. La suma de óptimos individuales no tiene por qué caber en recursos compartidos, y achicar todos los lotes por igual tampoco sería óptimo (ver Solicitud 9).

## Solicitud 9. EOQ multiproducto restringido

**Variables:** $Q_i>0$, tamaño de lote del componente $i$. Las restricciones reservan espacio y capital para lotes completos ($v_iQ_i$, $c_iQ_i$), según el "valor total de los lotes" del enunciado y la Sesión 4. Medidas sobre el inventario promedio ($Q_i/2$), los EOQ usarían 56,6 m³ y 67,6 MM\$ y serían factibles. **Modelo** no lineal y convexo (KKT entrega el óptimo global):
$$\min\ \sum_i\left(\frac{D_iS_i}{Q_i}+\frac{h_iQ_i}{2}\right)\quad\text{s.a.}\quad \sum_i v_iQ_i\le 90\ \ (\mu),\qquad \sum_i c_iQ_i\le 110.000.000\ \ (\lambda),\qquad Q_i>0.$$
La función objetivo suma, por componente, el costo anual de ordenar ($N_i=D_i/Q_i$ pedidos por $S_i$) y el de mantener (inventario promedio $Q_i/2$ por $h_i$). Las restricciones exigen que los cinco lotes, si llegan a la vez, quepan en los 90 m³ y no valgan más de 110 MM\$. Por KKT, $Q_i=\sqrt{2D_iS_i/(h_i+2\mu v_i+2\lambda c_i)}$, con $\mu,\lambda\ge0$ y holgura complementaria. Así, cada recurso escaso actúa como un costo de mantener extra, proporcional a lo que el componente consume de él. El factor 2 aparece porque la mantención se cobra sobre $Q_i/2$ y los recursos sobre $Q_i$ completo. Resolvimos por bisección sobre $(\mu,\lambda)$ y verificamos con SLSQP (mismo óptimo). **El costo de compra $\sum_iD_ic_i$ (2.784 MM\$/año) no depende de $Q_i$**: la compra anual es la misma con cualquier tamaño de lote, así que no cambia el óptimo y solo importaría con descuentos por cantidad. El precio sí entra en la restricción de capital y en $h_i$.

| Componente | $Q_i$ | vs EOQ | $N_i$ | $T_i$ (días) | ROP | Costo relevante |
|----------------------|-----------:|-----------:|---------:|-----------:|-----------:|-------------------:|
| Motor estándar | 2.781 | −18,1 % | 34,5 | 6,95 | 2.400 | 10.385.094 |
| Motor premium | 1.192 | −18,0 % | 20,1 | 11,9 | 1.000 | 7.409.393 |
| Hélice–rejilla | 4.456 | −21,2 % | 26,9 | 8,9 | 4.000 | 6.546.129 |
| Módulo electrónico | 2.844 | −17,9 % | 21,1 | 11,4 | 2.500 | 7.063.396 |
| Control remoto | 1.815 | −17,9 % | 13,2 | 18,2 | 1.200 | 3.099.005 |
| **Total** | | | **115,9** | | | **34.503.017** |

: EOQ multiproducto con espacio (90 m³) y capital (110 MM\$) restringidos.

Ambas restricciones quedan activas (90,0 m³ y 110,0 MM\$ exactos), con $\mu=5.098$ \$/m³-año y $\lambda=0\text{,}0595$ \$/\$-año. Todos los lotes se achican y se pide más seguido (94 → 116 pedidos/año). El costo de ordenar sube de 16,89 a 20,75 MM\$ (+3,86) y el de mantener baja de 16,89 a 13,75 MM\$ (−3,14), así que el costo relevante aumenta 0,72 MM\$/año (+2,1 %) respecto del EOQ infactible. Con el capital activo, mantener vale exactamente 0,25·110/2 = 13,75 MM\$, porque $h_i=0\text{,}25c_i$. La hélice–rejilla, gran consumidora de espacio, se reduce más (−21 %) y los demás cerca de 18 %, por el capital. Tampoco es óptimo achicar todos los EOQ por igual (factor 0,796, −20,4 %): cumple 90 m³ y usa 107,5 MM\$, pero cuesta 34,67 MM\$, 163 mil \$/año (+0,47 %) más que este óptimo. El espacio y el capital pesan distinto en cada componente, como muestra el costo de mantener efectivo $h_i+2\mu v_i+2\lambda c_i$. Una restricción activa cumple $g(Q^*)=0$ y, por holgura complementaria, solo ella puede tener multiplicador positivo. Si $\mu>0$, relajarla ahorra localmente $\mu$ por unidad. Si queda holgura (el espacio en el escenario a: 92,07 < 99), su multiplicador es 0. Activa no implica valiosa. El ROP no cambia ($d_iL_i$), pero $T_i$ queda muy cerca de $L_i$ en la hélice–rejilla (8,9 vs 8 días, y 8,5 vs 8 con +10 % de presupuesto). Con lotes más chicos habría pedidos en tránsito y el ROP debería aplicarse sobre la posición de inventario.

## Solicitud 10. Sensibilidad y recomendación

| Escenario | Espacio usado | Capital usado | ¿Activas? | $\mu$ | $\lambda$ | Costo relevante | Pedidos/año | Ahorro vs base |
|----------------------|------------:|--------:|----------|-------:|-------:|-----------:|--------:|--------:|
| Base (90 m³; 110 MM\$) | 90,0 | 110,0 | ambas | 5.098 | 0,0595 | 34.503.017 | 115,9 | — |
| a) +10 % espacio (99 m³) | 92,1 (holgura 6,9) | 110,0 | solo capital | 0 | 0,0636 | 34.497.798 | 115,7 | **5.219** |
| b) +10 % presupuesto (121 MM\$) | 90,0 | 121,0 | ambas | 24.785 | 0,0135 | 34.116.426 | 106,8 | **386.591** |

: Sensibilidad del EOQ multiproducto a +10 % de espacio o de presupuesto.

**a)** Con más bodega, el único límite es el capital y todos los lotes se escalan igual (−18,6 % vs EOQ, porque la tasa de mantención es común). Ocupan 92,07 m³, así que de los 9 m³ extra solo se aprovechan 2,07 y el resto queda ocioso. Los lotes casi no cambian (hélice +3,4 %, el resto entre −0,6 y −0,9 %) y los pedidos pasan de 115,9 a 115,7 al año: la operación no mejora. **b)** Con más presupuesto los lotes crecen entre 12,6 % y 13,9 %, salvo la hélice (−4,5 %), que cede espacio a los demás porque la bodega sigue llena. Se eliminan 9 pedidos al año (−7,9 %) a cambio de 5,5 MM\$ más de inventario promedio. Sube $\mu$, porque el espacio vale más, y cae $\lambda$ por rendimientos decrecientes.

::: {.recomendacion custom-style="Recomendacion"}
**Recomendación:** si hay que elegir, **ampliar el presupuesto** genera 74 veces más valor que ampliar el espacio. Que ambas restricciones estén activas no significa que relajarlas valga lo mismo. El multiplicador es un valor marginal *local*: estimaría 5.098×9 = 45.881, nueve veces el ahorro real, y 0,0595×11 MM = 654.421, 1,7 veces el real. Aun así, ya anticipa una ventaja de 14 a 1 para el presupuesto. Además, cambia al relajar: con más espacio el capital limita casi de inmediato, mientras el capital extra se aprovecha completo. Un recurso puede estar activo y tener poco valor económico si otro está a punto de limitar. Por eso, $\mu$ y $\lambda$ son pendientes locales en el punto base y no precios constantes: caen al relajar y se anulan en un umbral. El espacio deja de valer desde 92,07 m³ ($\mu=0$), así que 5.219 \$/año es el techo de cualquier ampliación de bodega (≈2.500 \$/m³ de valor medio frente a 5.098 marginal). El capital sigue valiendo hasta ≈125,1 MM\$ (techo de 413.790 \$/año con el espacio en 90 m³), y el +10 % ya captura el 93 % (386.591/413.790).
:::

![Tamaños de lote por componente: EOQ individual (infactible) y EOQ multiproducto en el escenario base, con +10 % de espacio y con +10 % de presupuesto.](../02_resultados/figuras/fig3_lotes.png){width=100%}

# Recomendación final integrada

1. **Planificación agregada:** recomendamos operar con **18 trabajadores** (ajuste único de −2 en marzo), producción regular nivelada de ~9.000 u/mes, HE de septiembre a febrero y **sin pedidos pendientes** (Sol. 5: 301,1 MM\$). Cuesta 4,4 % menos que la mejor regla simple, da servicio completo y mantiene bajo inventario. Su riesgo es la HE saturada en el peak, que se mitiga en parte con 19 trabajadores (1,4 MM\$ adicionales). El servicio completo cuesta solo 0,35 MM\$, muy poco frente a una sola multa de 3 MM\$.
2. **Coherencia entre decisiones:** el abastecimiento se planifica con la tasa estable de 10.000 u/mes, como instruyó la Gerencia, y los $D_i$ no cambian con el plan agregado. Pero el plan óptimo no es plano. En nov–dic produce 11.700 u/mes (+17 %), el consumo diario sube a 468 / 117 / 585 / 292,5 / 117 u y los ROP deberían pasar de 2.400 / 1.000 / 4.000 / 2.500 / 1.200 a 2.808 / 1.170 / 4.680 / 2.925 / 1.404. Además, con los lotes del multiproducto, $T<L$ en el motor estándar (5,9 vs 6 días), la hélice (7,6 vs 8) y el módulo (9,7 vs 10), así que el ROP debe aplicarse sobre la posición de inventario. Con los ROP actuales, la hélice quedaría corta en ≈680 u durante su plazo.
3. **Inventarios:** proponemos implementar los lotes del EOQ multiproducto (2.781 / 1.192 / 4.456 / 2.844 / 1.815) con los ROP de la tabla, y no los EOQ individuales, que no caben ni en la bodega ni en el presupuesto. Al redondear, dejar la hélice en 4.455 respeta estrictamente el tope (89,99 m³ y 109,99 MM\$). El sobrecosto de las restricciones, 0,72 MM\$/año con lotes 18–21 % menores y ≈22 pedidos más al año (94 → 116), es pequeño frente al costo de compra (2.784 MM\$/año).
4. **Inversión:** priorizar **más presupuesto para lotes** antes que más bodega (ahorro de 386.591 vs 5.219 \$/año). Esos 386.591 \$/año equivalen a una rentabilidad *media* de 3,5 % anual sobre los 11 MM\$ (la marginal parte en 5,95 % y cae a 1,35 %). Como $h_i$ ya incluye el costo de capital, ese 3,5 % es un beneficio neto adicional. Conviene ampliar si el tope de 110 MM\$ responde a una restricción de caja que pueda levantarse sin otros costos.

*Limitaciones:* supusimos demanda y plazos determinísticos, sin stock de seguridad por indicación del curso, una unidad agregada homogénea y espacio reservado para todos los lotes completos a la vez. Con llegadas escalonadas, el espacio efectivo requerido sería menor.
