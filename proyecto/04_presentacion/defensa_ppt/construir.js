// Presentación de la defensa Ventisur (10 min, 4 integrantes), ordenada por solicitudes y rúbrica.
// Uso: python3 exportar_datos.py && NODE_PATH=<node_modules con pptxgenjs> SKILL_DIR=<skill pptx> node construir.js
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(path.join(process.env.SKILL_DIR, "scripts/apply_theme.js"));

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "datos.json"), "utf8"));
const SALIDA = path.join(__dirname, "..", "Presentacion_Defensa_Ventisur.pptx");

const THEME = {
  name: "Ventisur",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "15202B", lt1: "FFFFFF", dk2: "0B3B5A", lt2: "EEF3F7",
    accent1: "F2643A", accent2: "1F8A9E", accent3: "8FB8D0", accent4: "5E6B78",
    accent5: "2E9E6B", accent6: "B8461E", hlink: "1F8A9E", folHlink: "5E6B78",
  },
};
const HX = THEME.colors;
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13,333 x 7,5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Ventisur · Defensa del proyecto";
pres.author = "Grupo Ventisur · Sección 2";
const C = pres.SchemeColor;

// ---------------------------------------------------------------- utilidades
const fmt = (n, dec = 0) => {
  const s = Number(n).toFixed(dec).split(".");
  s[0] = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return s.join(",");
};
const W = 13.333, M = 0.6, CW = W - 2 * M;
const PR = {
  BB: { name: "Beyonce Bulnes", ini: "BB" },
  CC: { name: "Constanza Catalán", ini: "CC" },
  CD: { name: "Cristóbal De Vidts", ini: "CD" },
  PM: { name: "Priscilla N. Montenegro", ini: "PM" },
};
const t = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, margin: 0, valign: "top" }, o));

function card(s, x, y, w, h, o = {}) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, Object.assign({
    x, y, w, h, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" },
  }, o));
}

function chip(s, txt, oscuro = false) {
  const w = Math.min(txt.length * 0.098 + 0.45, 10.5);
  s.addText(txt, {
    x: M, y: 0.38, w, h: 0.42, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.21,
    fill: { color: C.accent1, transparency: oscuro ? 0 : 86 }, line: { type: "none" },
    color: oscuro ? C.background1 : C.accent6, fontSize: 14, bold: true, margin: [0, 12, 0, 12],
    valign: "middle", isTextBox: true, objectName: "pregunta",
  });
}

function badge(s, p, oscuro = false) {
  t(s, p.name, { x: 7.6, y: 0.38, w: 4.6, h: 0.42, align: "right", valign: "middle", fontSize: 13,
    color: oscuro ? C.background1 : C.accent4, objectName: "presenta" });
  s.addText(p.ini, { x: 12.29, y: 0.37, w: 0.44, h: 0.44, shape: pres.shapes.OVAL,
    fill: { color: oscuro ? C.accent1 : C.text2 }, line: { type: "none" }, color: C.background1,
    fontSize: 12, bold: true, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "iniciales" });
}

function num(s, n, x, y, d = 0.44, fill = C.accent1) {
  s.addText(String(n), { x, y, w: d, h: d, shape: pres.shapes.OVAL, fill: { color: fill }, line: { type: "none" },
    color: C.background1, fontSize: 15, bold: true, align: "center", valign: "middle", margin: 0, isTextBox: true });
}

const ejes = {
  catAxisLabelColor: HX.accent4, valAxisLabelColor: HX.accent4, catAxisLabelFontSize: 12, valAxisLabelFontSize: 12,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt", legendFontSize: 12,
  legendColor: HX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFontSize: 12, dataLabelColor: HX.dk1,
  valGridLine: { color: "DDE3E9", size: 0.75 }, catGridLine: { style: "none" },
  catAxisLineShow: true, valAxisLineShow: false,
};

function notas(s, quien, tiempo, guion, rubrica, preguntas) {
  s.addNotes(`PRESENTA: ${quien} · TIEMPO: ${tiempo}\n\nQUÉ DECIR:\n${guion}\n\nRÚBRICA (lo que pide el nivel 4 y esta diapositiva cubre):\n${rubrica}\n\nSI PREGUNTAN:\n${preguntas}`);
}

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "PORTADA",
  background: { color: HX.dk2 },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: M, y: 1.05, w: 10.2, h: 1.9,
    fontSize: 42, bold: true, color: C.background1, valign: "top", align: "left", margin: 0 }, text: "" } }],
});
pres.defineSlideMaster({
  title: "CONTENIDO",
  background: { color: HX.lt1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.98, w: CW, h: 0.9, fontSize: 32, bold: true,
      color: C.text1, valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "rubrica", type: "body", x: M, y: 6.98, w: 10.5, h: 0.32, fontSize: 11,
      color: C.accent4, valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.33, y: 6.98, w: 0.4, h: 0.32, fontSize: 11, color: HX.accent4, align: "right" },
});
pres.defineSlideMaster({
  title: "OSCURO",
  background: { color: HX.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.98, w: CW, h: 0.9, fontSize: 32, bold: true,
      color: C.background1, valign: "top", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "rubrica", type: "body", x: M, y: 6.98, w: 10.5, h: 0.32, fontSize: 11,
      color: C.accent3, valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.33, y: 6.98, w: 0.4, h: 0.32, fontSize: 11, color: HX.accent3, align: "right" },
});

let seccion = "";
function nueva(master, sec) {
  if (sec !== seccion) { pres.addSection({ title: sec }); seccion = sec; }
  return pres.addSlide({ masterName: master, sectionTitle: sec });
}
const titulo = (s, txt) => s.addText(txt, { placeholder: "title" });
const rubrica = (s, txt) => s.addText(txt, { placeholder: "rubrica" });

// ================================================================ 1 · PORTADA
{
  const s = nueva("PORTADA", "Apertura y S1");
  t(s, "PROYECTO INTEGRADOR · GESTIÓN DE OPERACIONES · SECCIÓN 2", { x: M, y: 0.55, w: 10, h: 0.35, fontSize: 13,
    bold: true, color: C.accent3, charSpacing: 2 });
  titulo(s, "Ventisur: cuánto producir, con cuánta gente y cómo comprar");
  t(s, "Planificación agregada, requerimientos de materiales e inventarios determinísticos", { x: M, y: 3.0, w: 10.5,
    h: 0.45, fontSize: 18, color: C.accent3 });
  const seg = [
    ["1", "Políticas simples", "Intro + S1", PR.CC, "1:25"],
    ["2", "Modelo A", "S2", PR.BB, "1:25"],
    ["3", "Servicio y recomendación", "S3 · S4 · S5", PR.CD, "2:10"],
    ["4", "Materiales y EOQ", "S6 · S7 · S8", PR.PM, "2:10"],
    ["5", "Multiproducto", "S9", PR.BB, "0:40"],
    ["6", "Sensibilidad y cierre", "S10 + recomendación", PR.CC, "1:30"],
  ];
  const gap = 0.15, bw = (CW - gap * 5) / 6, y0 = 4.15;
  seg.forEach((g, i) => {
    const x = M + i * (bw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y0, w: bw, h: 2.35, rectRadius: 0.12,
      fill: { color: C.background1, transparency: 90 }, line: { type: "none" } });
    num(s, g[0], x + 0.18, y0 + 0.2, 0.42);
    t(s, g[4], { x: x + 0.7, y: y0 + 0.2, w: bw - 0.88, h: 0.42, align: "right", valign: "middle", fontSize: 13,
      color: C.accent3 });
    t(s, g[2], { x: x + 0.18, y: y0 + 0.78, w: bw - 0.3, h: 0.32, fontSize: 13, bold: true, color: C.accent1 });
    t(s, g[1], { x: x + 0.18, y: y0 + 1.1, w: bw - 0.3, h: 0.62, fontSize: 15, bold: true, color: C.background1 });
    t(s, g[3].name, { x: x + 0.18, y: y0 + 1.82, w: bw - 0.3, h: 0.4, fontSize: 12, color: C.accent3 });
  });
  notas(s, PR.CC.name, "0:15",
    "Presentarse y presentar al grupo. 'Ventisur ensambla ventiladores y tiene que tomar tres decisiones encadenadas: cuánto producir y con cuánta gente, cuántas piezas consume eso, y cuánto y cuándo comprarlas. Las vamos a presentar en el orden del enunciado; cada uno defiende un bloque.'",
    "D7: conectar etapas y distinguir qué decisión responde cada modelo (se anuncia aquí y se cierra en la última diapositiva).",
    "Formato de la defensa: 10 minutos de presentación; cualquiera puede responder cualquier pregunta.");
}

// ================================================================ 2 · EL PROBLEMA
{
  const s = nueva("CONTENIDO", "Apertura y S1");
  chip(s, "Contexto · ¿Qué tiene que decidir Ventisur?");
  badge(s, PR.CC);
  titulo(s, "La demanda sube 47 % de mayo a diciembre");
  s.addChart([
    { type: pres.charts.BAR, data: [{ name: "Demanda pronosticada (u)", labels: D.meses, values: D.demanda }],
      options: { chartColors: [HX.accent3], barGapWidthPct: 45 } },
    { type: pres.charts.LINE, data: [{ name: "Producción regular con 20 trabajadores (10.000 u)", labels: D.meses, values: Array(12).fill(10000) }],
      options: { chartColors: [HX.accent1], lineSize: 2.5, lineDataSymbol: "none" } },
  ], Object.assign({ x: M, y: 2.05, w: 7.5, h: 4.7, valAxisMinVal: 0, valAxisMaxVal: 14000, valAxisMajorUnit: 2000,
    showLegend: true, legendPos: "b", valAxisLabelFormatCode: "#,##0" }, ejes));
  const filas = [
    ["Parte I", "¿Con cuánta gente y cuánto producir cada mes?", "S1 a S5"],
    ["Parte II", "¿Cuántas piezas consume esa producción?", "S6"],
    ["Parte III", "¿Cuánto y cuándo comprar cada pieza, con bodega y capital limitados?", "S7 a S10"],
  ];
  filas.forEach((f, i) => {
    const y = 2.15 + i * 1.5;
    card(s, 8.45, y, 4.28, 1.3);
    num(s, i + 1, 8.65, y + 0.22);
    t(s, `${f[0]} · ${f[2]}`, { x: 9.25, y: y + 0.18, w: 3.35, h: 0.32, fontSize: 13, bold: true, color: C.accent2 });
    t(s, f[1], { x: 9.25, y: y + 0.5, w: 3.35, h: 0.72, fontSize: 15, color: C.text1 });
  });
  rubrica(s, "Rúbrica · D7 Integración (10 %): qué decisión responde cada parte del proyecto");
  notas(s, PR.CC.name, "0:20",
    "'La demanda va de 8.500 en mayo a 12.500 en diciembre, y la capacidad regular de los 20 trabajadores actuales es 10.000 al mes: en el peak falta y en otoño sobra. La Parte I decide cómo absorber ese peak; con esa producción, la Parte II calcula cuántas piezas se consumen; y la Parte III decide cuánto y cuándo comprarlas.'",
    "D7: distingue la pregunta de cada parte y cómo se encadenan.",
    "¿Por qué la Parte II usa 10.000 y no el plan óptimo? Porque la Gerencia fijó esa tasa estable para compras (lo exige el enunciado). Además 10.000 × 12 = 120.000 = demanda anual.");
}

// ================================================================ 3 · S1
{
  const s = nueva("CONTENIDO", "Apertura y S1");
  chip(s, "S1 · ¿Cuánto cuestan las reglas simples?");
  badge(s, PR.CC);
  titulo(s, "Mismo sueldo, distinto amortiguador: gana P2");
  const pol = [
    ["P1 · Tasa constante", "Amortigua con inventario", "340,0", ["20 trabajadores · 10.000 u/mes", "Inventario hasta 7.000 u (93 % de la bodega)", "Inventario: 52,0 MM$"], false],
    ["P2 · Dotación + HE", "Amortigua con horas extra", "315,0", ["20 trabajadores todo el año", "HE: 6.000 u en nov–feb", "HE 15,0 + inventario 12,0 MM$"], true],
    ["P3 · Persecución", "Amortigua contratando y despidiendo", "329,5", ["17 a 25 trabajadores", "9 contrataciones + 6 despidos", "Movimientos: 40,5 MM$"], false],
  ];
  const gap = 0.3, cw = (CW - 2 * gap) / 3;
  pol.forEach((p, i) => {
    const x = M + i * (cw + gap), y = 2.05, h = 3.45, dk = p[4];
    card(s, x, y, cw, h, dk ? { fill: { color: C.text2 } } : {});
    if (dk) t(s, "MEJOR SIMPLE", { x: x + cw - 1.8, y: y + 1.12, w: 1.5, h: 0.3, fontSize: 11, bold: true,
      color: C.accent1, align: "right", charSpacing: 1 });
    t(s, p[0], { x: x + 0.3, y: y + 0.22, w: cw - 0.6, h: 0.36, fontSize: 16, bold: true, color: dk ? C.background1 : C.text1 });
    t(s, p[1], { x: x + 0.3, y: y + 0.6, w: cw - 0.6, h: 0.32, fontSize: 14, color: dk ? C.accent3 : C.accent2 });
    t(s, [{ text: p[2], options: { fontSize: 44, bold: true, color: dk ? C.accent1 : C.text1 } },
      { text: "  MM$", options: { fontSize: 16, color: dk ? C.accent3 : C.accent4 } }],
      { x: x + 0.3, y: y + 1.0, w: cw - 0.6, h: 0.8, valign: "middle" });
    t(s, p[3].map((l, k) => ({ text: l, options: { bullet: true, breakLine: k < p[3].length - 1 } })),
      { x: x + 0.3, y: y + 1.95, w: cw - 0.5, h: 1.35, fontSize: 14, color: dk ? C.background1 : C.text1, paraSpaceAfter: 4 });
  });
  card(s, M, 5.72, CW, 1.0, { fill: { color: C.accent1, transparency: 88 } });
  t(s, [{ text: "Las tres pagan 288 MM$ en sueldos (240 trabajador-mes): solo cambia el amortiguador. ", options: { bold: true } },
    { text: "Si los costos cambian: con HE sobre $4.917/u ganaría P3, sobre $6.667/u ganaría P1; P1 solo le gana a P2 si mantener cuesta menos de $375/u-mes." }],
    { x: M + 0.3, y: 5.82, w: CW - 0.6, h: 0.8, fontSize: 15, color: C.text1, valign: "middle" });
  rubrica(s, "Rúbrica · D1 Políticas simples (10 %): mecanismo de cada política y efecto de cambiar costos");
  notas(s, PR.CC.name, "0:50",
    "'Las tres políticas pagan lo mismo en sueldos; la diferencia es con qué absorben el peak. P1 produce siempre 10.000 y acumula hasta 7.000 unidades: 52 millones de inventario. P2 mantiene 20 trabajadores y cubre nov–feb con 6.000 unidades de horas extra: 315 millones, la mejor. P3 contrata y despide: casi sin inventario, pero 15 movimientos cuestan 40,5 millones. Una hora extra cuesta $2.500, lo mismo que guardar una unidad 2,5 meses; por eso P2 le gana a P1.' Paso a Beyonce con el modelo de optimización.",
    "D1: tres planes correctos con sus reglas y bordes; costos consistentes; mecanismo de cada uno; anticipa el efecto de cambiar costos (umbrales $4.917, $6.667 y $375).",
    "¿P1 se sale de la bodega? No: máximo 7.000 de 7.500. ¿Por qué P2 tiene capacidad ociosa? Paga 20 trabajadores pero en mar–ago la demanda es menor: sobran 6.000 u. ¿P3 en marzo? (9.500 − 1.000)/500 = 17 trabajadores, despide 3 (el máximo).");
}

// ================================================================ 4 · S2 formulación
{
  const s = nueva("CONTENIDO", "S2 · Modelo A");
  chip(s, "S2 · ¿Cuál es el plan de mínimo costo?");
  badge(s, PR.BB);
  titulo(s, "Modelo A: un MILP que decide todo a la vez");
  // variables
  t(s, "Variables (t = marzo … febrero)", { x: M, y: 2.05, w: 5.3, h: 0.4, fontSize: 17, bold: true, color: C.text1 });
  const vars = [
    ["Wₜ", "entera", "trabajadores disponibles"],
    ["Hₜ · Fₜ", "enteras", "contratados · despedidos"],
    ["Rₜ · Oₜ", "≥ 0", "producción regular · horas extra"],
    ["Iₜ · Bₜ", "≥ 0", "inventario · pendientes al cierre"],
  ];
  vars.forEach((v, i) => {
    const y = 2.6 + i * 0.86;
    card(s, M, y, 5.3, 0.72);
    t(s, v[0], { x: M + 0.25, y, w: 1.25, h: 0.72, fontSize: 18, bold: true, color: C.accent2, valign: "middle" });
    t(s, v[2], { x: M + 1.5, y, w: 2.75, h: 0.72, fontSize: 15, color: C.text1, valign: "middle" });
    t(s, v[1], { x: M + 4.2, y, w: 0.95, h: 0.72, fontSize: 13, color: C.accent4, valign: "middle", align: "right" });
  });
  t(s, "El sueldo multiplica a Wₜ: se paga por trabajador disponible, así que producir en horario regular no cuesta extra.",
    { x: M, y: 6.1, w: 5.3, h: 0.65, fontSize: 13, italic: true, color: C.accent4 });
  // FO + restricciones
  const x2 = 6.25, w2 = W - M - x2;
  card(s, x2, 2.05, w2, 1.05, { fill: { color: C.text2 } });
  t(s, [{ text: "min Z = Σₜ ", options: { bold: true } },
    { text: "1,2 MM·Wₜ + 2,5 MM·Hₜ + 3 MM·Fₜ + 2.500·Oₜ + 1.000·Iₜ + 750·Bₜ" }],
    { x: x2 + 0.3, y: 2.05, w: w2 - 0.6, h: 1.05, fontSize: 17, color: C.background1, valign: "middle" });
  const res = [
    ["Dotación", "Wₜ = Wₜ₋₁ + Hₜ − Fₜ", "conecta los meses"],
    ["Capacidad", "Rₜ ≤ 500·Wₜ ;  Oₜ ≤ 150·Wₜ", "la gente limita la producción"],
    ["Balance", "Iₜ − Bₜ = Iₜ₋₁ − Bₜ₋₁ + Rₜ + Oₜ − dₜ", "lo que falta queda pendiente"],
    ["Límites", "Iₜ ≤ 7.500 ; 15 ≤ Wₜ ≤ 25 ; Hₜ, Fₜ ≤ 3", "bodega y reglas de personal"],
    ["Bordes", "W₀ = 20 ; I₀ = 1.000 ; I₁₂ ≥ 1.000 ; B₁₂ = 0", "cómo empieza y termina el año"],
  ];
  const rows = [[
    { text: "Familia", options: { bold: true, color: C.accent4 } },
    { text: "Restricción", options: { bold: true, color: C.accent4 } },
    { text: "Para qué sirve", options: { bold: true, color: C.accent4 } }]].concat(
    res.map((r) => [{ text: r[0], options: { bold: true } }, { text: r[1] }, { text: r[2] }]));
  s.addTable(rows, { x: x2, y: 3.3, w: w2, colW: [1.25, 3.33, w2 - 4.58], fontSize: 14, color: C.text1,
    border: { type: "solid", pt: 0.75, color: "DDE3E9" }, rowH: 0.48, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08] });
  rubrica(s, "Rúbrica · D2 Modelo A (20 %): variables, dominios, función objetivo y familias de restricciones");
  notas(s, PR.BB.name, "0:40",
    "'En vez de fijar un amortiguador, formulamos un modelo entero mixto que decide todo a la vez cada mes. Variables: trabajadores, contrataciones y despidos (enteras), producción regular, horas extra, inventario y pendientes. La función objetivo suma todos los costos que dependen de las decisiones; el sueldo multiplica a W porque se paga por trabajador disponible. Las restricciones conectan la dotación entre meses, limitan la producción por la gente, hacen el balance —lo que falta queda pendiente— y respetan bodega, límites y bordes.' Implementado en Python con PuLP y CBC; reproducible con run_all.py.",
    "D2: define variables, dominios, FO y restricciones; explica cada familia; implementación reproducible (PuLP + CBC, archivo ModeloA_Sol2.lp).",
    "¿Por qué W entera y R continua? No se contrata medio trabajador; la producción son miles de unidades. Relajación lineal: 300,68 (casi igual). ¿Hace falta forzar regular antes que HE? No: la regular ya está pagada y la HE cuesta $2.500. ¿Quitar el ±3? No cambia nada: no está activo.");
}

// ================================================================ 5 · S2 solución
{
  const s = nueva("CONTENIDO", "S2 · Modelo A");
  chip(s, "S2 · ¿Por qué mejora a las políticas?");
  badge(s, PR.BB);
  titulo(s, "300,75 MM$: menos gente, HE en el peak y atrasos cortos");
  s.addChart([
    { type: pres.charts.BAR, data: [
      { name: "Producción regular", labels: D.meses, values: D.A.regular },
      { name: "Horas extra", labels: D.meses, values: D.A.he }],
      options: { barGrouping: "stacked", chartColors: [HX.accent3, HX.accent1], barGapWidthPct: 40 } },
    { type: pres.charts.LINE, data: [{ name: "Demanda", labels: D.meses, values: D.demanda }],
      options: { chartColors: [HX.dk1], lineSize: 2.25, lineDataSymbol: "circle", lineDataSymbolSize: 6 } },
  ], Object.assign({ x: M, y: 2.05, w: 7.3, h: 4.7, valAxisMinVal: 0, valAxisMaxVal: 14000, valAxisMajorUnit: 2000,
    showLegend: true, legendPos: "b", valAxisLabelFormatCode: "#,##0" }, ejes));
  const x2 = 8.2, w2 = W - M - x2;
  t(s, [{ text: "−14,25 MM$", options: { fontSize: 36, bold: true, color: C.accent1 } },
    { text: "  vs P2 (−4,5 %)", options: { fontSize: 16, color: C.accent4 } }], { x: x2, y: 2.0, w: w2, h: 0.7, valign: "middle" });
  const raz = [
    ["Despide 2 en marzo", "Mantener un trabajador cuesta 11,4 MM$ netos; cubrir su producción con HE, 7,5 MM$."],
    ["Adelanta solo 1–2 meses", "Guardar 1–2 meses ($1.000–2.000) < HE ($2.500) < guardar 3 meses ($3.000)."],
    ["Atrasa en dic–ene", "Con la HE al tope (2.700 = 150 × 18), atrasar ($750) < guardar ($1.000)."],
  ];
  raz.forEach((r, i) => {
    const y = 2.9 + i * 1.28;
    card(s, x2, y, w2, 1.12);
    num(s, i + 1, x2 + 0.2, y + 0.18, 0.4);
    t(s, r[0], { x: x2 + 0.75, y: y + 0.14, w: w2 - 0.95, h: 0.34, fontSize: 15, bold: true, color: C.text1 });
    t(s, r[1], { x: x2 + 0.75, y: y + 0.48, w: w2 - 0.95, h: 0.6, fontSize: 13, color: C.text1 });
  });
  rubrica(s, "Rúbrica · D2 Modelo A (20 %): interpretación y por qué combina mecanismos que las políticas mantienen rígidos");
  notas(s, PR.BB.name, "0:45",
    "'El óptimo cuesta 300,75 millones, 14,25 menos que P2. Combina los tres amortiguadores. Primero, despide 2 trabajadores en marzo: mantener uno cuesta 11,4 millones netos y solo hace falta de septiembre a febrero; esa producción con horas extra cuesta 7,5. Segundo, adelanta solo 1 a 2 meses, porque guardar más de 2,5 meses sale más caro que una hora extra. Tercero, con la HE al tope en diciembre, atrasa 400 unidades, porque atrasar un mes cuesta $750 y guardar $1.000.' Paso a Cristóbal con los cambios de servicio.",
    "D2: interpreta las decisiones y justifica por qué mejora a las políticas combinando mecanismos; óptimo factible y único (verificado).",
    "¿Despedir y después pagar HE no es contradictorio? No: el trabajador solo se usaría 6 meses; convendría con 9,1 meses o más. ¿Y si atrasar costara $1.500? Igual atrasa 200 u (301,0 MM$). ¿Y si despedir fuera gratis? 293,95 MM$ con 17 trabajadores en mar–jun.");
}

// ================================================================ 6 · S3
{
  const s = nueva("CONTENIDO", "S3–S5 · Servicio");
  chip(s, "S3 · ¿Cómo cambia el plan con la multa contractual?");
  badge(s, PR.CD);
  titulo(s, "Una binaria enciende la multa de $3 MM");
  const wl = 6.4;
  card(s, M, 2.05, wl, 1.15, { fill: { color: C.text2 } });
  t(s, [{ text: "Bₜ ≤ 0,01·dₜ + Mₜ·yₜ      yₜ ∈ {0,1}", options: { breakLine: true } },
    { text: "min  Z(Modelo A) + 3.000.000 · Σₜ yₜ" }],
    { x: M + 0.3, y: 2.05, w: wl - 0.6, h: 1.15, fontSize: 19, bold: true, color: C.background1, valign: "middle", paraSpaceAfter: 4 });
  const casos = [
    ["yₜ = 0", "Pendientes ≤ 1 % de la demanda: no hay multa. El modelo elige 0 porque yₜ = 1 cuesta $3 MM."],
    ["yₜ = 1", "Pendientes > 1 %: la restricción solo se cumple pagando la multa."],
  ];
  const cw = (wl - 0.3) / 2;
  casos.forEach((c, i) => {
    const x = M + i * (cw + 0.3);
    card(s, x, 3.4, cw, 1.55);
    t(s, c[0], { x: x + 0.25, y: 3.52, w: cw - 0.5, h: 0.4, fontSize: 18, bold: true, color: C.accent2 });
    t(s, c[1], { x: x + 0.25, y: 3.95, w: cw - 0.45, h: 0.95, fontSize: 14, color: C.text1 });
  });
  card(s, M, 5.15, wl, 1.6);
  t(s, [{ text: "La constante M  ", options: { bold: true, color: C.accent2 } },
    { text: "Mₜ = demanda acumulada − I₀ − 0,01·dₜ (diciembre: 96.875). Debe ser grande para no cortar planes válidos; con la cota ajustada (9.375) el óptimo es el mismo." }],
    { x: M + 0.25, y: 5.25, w: wl - 0.5, h: 1.4, fontSize: 14, color: C.text1, valign: "middle" });
  // resultado
  const x2 = 7.3, w2 = W - M - x2;
  t(s, [{ text: "300,94 MM$", options: { fontSize: 40, bold: true, color: C.accent1, breakLine: true } },
    { text: "no paga ninguna multa (+193.750 vs A)", options: { fontSize: 16, color: C.accent4 } }],
    { x: x2, y: 2.0, w: w2, h: 1.25 });
  const tb = [
    [{ text: "", options: {} }, { text: "Modelo A", options: { bold: true, color: C.accent4 } }, { text: "Modelo B", options: { bold: true, color: C.accent4 } }],
    ["Pendientes diciembre", "400", { text: "125 (= 1 %)", options: { bold: true, color: C.accent6 } }],
    ["Pendientes enero", "200", "0"],
    ["HE de octubre", "1.200", "1.475"],
    ["Inventario oct / nov", "200 / 400", "475 / 675"],
  ];
  s.addTable(tb, { x: x2, y: 3.4, w: w2, colW: [2.3, 1.5, w2 - 3.8], fontSize: 14, color: C.text1, rowH: 0.42,
    border: { type: "solid", pt: 0.75, color: "DDE3E9" }, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08] });
  t(s, "Adelanta 275 u con HE de octubre y las guarda 2 meses: +550.000 de inventario, −356.250 de atrasos.",
    { x: x2, y: 5.7, w: w2, h: 0.95, fontSize: 14, italic: true, color: C.accent4 });
  rubrica(s, "Rúbrica · D3 Modelos B y C (15 %): papel de la variable binaria y lógica de la constante M");
  notas(s, PR.CD.name, "0:45",
    "'La multa no es un costo por unidad: es un monto fijo que aparece si los pendientes pasan el 1 %. Por eso agregamos una binaria y por mes. Si los pendientes están bajo el 1 %, la restricción se cumple con y = 0 y no hay multa; si lo pasan, solo se cumple con y = 1, y se suman 3 millones. M tiene que ser al menos el mayor exceso posible: usamos la demanda acumulada menos el inventario inicial. El modelo no paga ninguna multa: baja diciembre de 400 a 125 pendientes, justo el 1 %, adelantando 275 unidades de HE a octubre. Cuesta 193.750, mucho menos que una multa.'",
    "D3: modificación correcta con lógica binaria válida; explica el papel de la binaria y de la constante M.",
    "¿Qué pasa si M es muy chica? Corta planes válidos (con y = 1 la restricción seguiría limitando). ¿Cuándo pagaría la multa? Si costara menos de $151.250. ¿Y si el umbral fuera 3,2 %? B = A (300,75). ¿Con 0 %? B = C (301,10).");
}

// ================================================================ 7 · S4
{
  const s = nueva("CONTENIDO", "S3–S5 · Servicio");
  chip(s, "S4 · ¿Y si no se acepta ningún pendiente?");
  badge(s, PR.CD);
  titulo(s, "Servicio completo cuesta solo 350 mil (0,12 %)");
  const R = D.resumen_ABC;
  s.addChart(pres.charts.BAR, [
    { name: "Inventario acumulado (u-mes)", labels: ["A (Sol. 2)", "B (Sol. 3)", "C (Sol. 4)"], values: ["A", "B", "C"].map((k) => R[k].inv_umes) },
    { name: "Pendientes acumulados (u-mes)", labels: ["A (Sol. 2)", "B (Sol. 3)", "C (Sol. 4)"], values: ["A", "B", "C"].map((k) => R[k].pend_umes) },
  ], Object.assign({ x: M, y: 2.05, w: 6.2, h: 4.7, barGapWidthPct: 60, chartColors: [HX.accent3, HX.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", valAxisMinVal: 0, valAxisMaxVal: 4000,
    valAxisMajorUnit: 1000, valAxisLabelFormatCode: "#,##0", showLegend: true, legendPos: "b" }, ejes));
  const x2 = 7.15, w2 = W - M - x2;
  const mods = [
    ["A", "Atraso con costo lineal ($750/u-mes)", "300,75", "99,5 % a tiempo"],
    ["B", "Multa si se pasa el 1 % (binaria)", "300,94", "99,9 % a tiempo"],
    ["C", "Bₜ = 0: atraso prohibido", "301,10", "100 % a tiempo"],
  ];
  mods.forEach((m, i) => {
    const y = 2.05 + i * 1.05, dk = i === 2;
    card(s, x2, y, w2, 0.9, dk ? { fill: { color: C.text2 } } : {});
    t(s, m[0], { x: x2 + 0.2, y, w: 0.5, h: 0.9, fontSize: 24, bold: true, color: dk ? C.accent1 : C.accent2, valign: "middle" });
    t(s, [{ text: m[1], options: { bold: true, breakLine: true } }, { text: m[3], options: { color: dk ? C.accent3 : C.accent4 } }],
      { x: x2 + 0.75, y, w: w2 - 2.4, h: 0.9, fontSize: 14, color: dk ? C.background1 : C.text1, valign: "middle" });
    t(s, m[2], { x: x2 + w2 - 1.6, y, w: 1.4, h: 0.9, fontSize: 22, bold: true, align: "right", valign: "middle",
      color: dk ? C.accent1 : C.text1 });
  });
  card(s, x2, 5.3, w2, 1.45, { fill: { color: C.accent1, transparency: 88 } });
  t(s, "Los tres usan 18 trabajadores y 13.000 u de HE; solo cambia cuándo. C adelanta 400 u de HE a octubre: +800.000 de inventario, −450.000 de atrasos.",
    { x: x2 + 0.25, y: 5.38, w: w2 - 0.5, h: 1.3, fontSize: 14, color: C.text1, valign: "middle" });
  rubrica(s, "Rúbrica · D3 Modelos B y C (15 %): diferencia conceptual A–B–C y costo de elevar el nivel de servicio");
  notas(s, PR.CD.name, "0:45",
    "'El Modelo C toma el A y prohíbe los pendientes: Bₜ = 0 todos los meses. La diferencia conceptual: A castiga el atraso de forma blanda, B con un salto al pasar el 1 %, y C lo prohíbe. Los tres usan la misma gente y las mismas 13.000 unidades de horas extra; lo único que cambia es el calendario: cuanto menos atraso se permite, más HE se adelanta a octubre y más inventario se guarda. Pasar de A a servicio completo cuesta 350 mil, el 0,12 %, porque guardar ($1.000) cuesta poco más que atrasar ($750).'",
    "D3: Modelo C con cero pendientes; diferencia conceptual entre A, B y C; cuantifica el costo de elevar el servicio (A→B +193.750; B→C +156.250; A→C +350.000).",
    "¿Por qué C no mantiene más gente? Con 19 trabajadores cuesta 11,4 MM$ netos más y ahorra 10,0 en HE e inventario: +1,4 MM$ (302,5). ¿Qué significa 99,5 %? 600 u-mes de atraso sobre 120.000 u.");
}

// ================================================================ 8 · S5
{
  const s = nueva("CONTENIDO", "S3–S5 · Servicio");
  chip(s, "S5 · ¿Qué plan recomendamos?");
  badge(s, PR.CD);
  titulo(s, "Recomendamos la Sol. 5: 18 trabajadores y cero pendientes");
  card(s, M, 2.05, 4.45, 4.7, { fill: { color: C.text2 } });
  t(s, "B + cero pendientes", { x: M + 0.35, y: 2.3, w: 3.8, h: 0.35, fontSize: 15, bold: true, color: C.accent3 });
  t(s, "301,10", { x: M + 0.35, y: 2.7, w: 3.8, h: 1.0, fontSize: 60, bold: true, color: C.accent1, valign: "middle" });
  t(s, "MM$ al año", { x: M + 0.35, y: 3.7, w: 3.8, h: 0.35, fontSize: 16, color: C.accent3 });
  t(s, [
    { text: "Es igual a C: con Bₜ = 0 la multa nunca se activa (todas las yₜ = 0).", options: { bullet: true, breakLine: true } },
    { text: "−13,9 MM$ vs P2 (−4,4 %).", options: { bullet: true, breakLine: true } },
    { text: "+0,35 MM$ vs A, que con sus 2 multas costaría 306,75.", options: { bullet: true } }],
    { x: M + 0.35, y: 4.2, w: 3.85, h: 2.4, fontSize: 14, color: C.background1, paraSpaceAfter: 6 });
  const x2 = M + 4.75, w2 = W - M - x2, gw = (w2 - 0.25) / 2;
  const crit = [
    ["Estabilidad", "Un solo ajuste: −2 trabajadores en marzo (P3 hace 15 movimientos)."],
    ["Horas extra", "13.000 u en sep–feb; al 100 % en nov–dic."],
    ["Inventario", "Máximo 800 u; 3.400 u-mes al año (P1: 52.000)."],
    ["Servicio", "100 % a tiempo, sin riesgo de multa (B queda justo en el 1 %)."],
  ];
  crit.forEach((c, i) => {
    const x = x2 + (i % 2) * (gw + 0.25), y = 2.05 + Math.floor(i / 2) * 1.5;
    card(s, x, y, gw, 1.3);
    t(s, c[0], { x: x + 0.25, y: y + 0.15, w: gw - 0.5, h: 0.34, fontSize: 15, bold: true, color: C.accent2 });
    t(s, c[1], { x: x + 0.25, y: y + 0.5, w: gw - 0.45, h: 0.75, fontSize: 14, color: C.text1 });
  });
  card(s, x2, 5.15, w2, 1.6, { fill: { color: C.accent1, transparency: 88 } });
  t(s, [{ text: "Trade-off: ", options: { bold: true } },
    { text: "la HE queda sin holgura en nov–dic. Seguro si se desconfía del pronóstico: 19 trabajadores, +1,4 MM$ (302,5), deja 700–850 u/mes de HE libre en nov, ene y feb." }],
    { x: x2 + 0.25, y: 5.22, w: w2 - 0.5, h: 1.45, fontSize: 14, color: C.text1, valign: "middle" });
  rubrica(s, "Rúbrica · D3 Modelos B y C (15 %): recomendación coherente con costos, operación y servicio");
  notas(s, PR.CD.name, "0:40",
    "'La Solicitud 5 pide el Modelo B sin pendientes: da exactamente lo mismo que C, porque si nunca hay pendientes la multa no puede activarse. Recomendamos ese plan: 18 trabajadores, horas extra de septiembre a febrero y cero pendientes, 301,1 millones. No es el más barato —A cuesta 0,35 menos— pero A viola el contrato y con multas costaría 306,75. Es estable, con un solo ajuste de personal; guarda poco inventario y da servicio completo. El trade-off es que la HE queda al tope en nov–dic; si la Gerencia no confía en el pronóstico, mantener 19 trabajadores cuesta 1,4 millones más y deja holgura.' Paso a Nicole con los materiales.",
    "D3: comparación que integra costos, decisiones operacionales y servicio, con recomendación coherente con la evidencia y sus trade-offs.",
    "¿Por qué no B? Queda exactamente en el 1 %: un error de una unidad cuesta $3 MM y solo ahorra 156.250. ¿Y si la demanda de diciembre sube 5 %? Conocida a tiempo: 303,9 con los mismos 18; si no se anticipa, no alcanza (12.500 < 13.125).");
}

// ================================================================ 9 · S6
{
  const s = nueva("CONTENIDO", "S6–S8 · Materiales y EOQ");
  chip(s, "S6 · ¿Cuántas piezas consume la producción?");
  badge(s, PR.PM);
  titulo(s, "10.000 ventiladores al mes = consumo fijo de piezas");
  // columna 1
  card(s, M, 3.55, 2.0, 1.3, { fill: { color: C.text2 } });
  t(s, [{ text: "10.000", options: { fontSize: 30, bold: true, color: C.accent1, breakLine: true } },
    { text: "u/mes (Gerencia)", options: { fontSize: 13, color: C.accent3 } }], { x: M + 0.15, y: 3.55, w: 1.7, h: 1.3, align: "center", valign: "middle" });
  const mods = [["Estándar", "50 %", "5.000"], ["Plus", "30 %", "3.000"], ["Premium", "20 %", "2.000"]];
  mods.forEach((m, i) => {
    const y = 2.2 + i * 1.5;
    card(s, 3.25, y, 2.35, 1.2);
    t(s, `${m[0]} · ${m[1]}`, { x: 3.45, y: y + 0.14, w: 2.0, h: 0.32, fontSize: 14, color: C.accent4 });
    t(s, m[2], { x: 3.45, y: y + 0.48, w: 2.0, h: 0.6, fontSize: 26, bold: true, color: C.text1 });
  });
  const comps = [["Motor estándar", "8.000", "Estándar + Plus"], ["Motor premium", "2.000", "Premium"],
    ["Hélice–rejilla", "10.000", "los tres modelos"], ["Módulo electrónico", "5.000", "Plus + Premium"], ["Control remoto", "2.000", "Premium"]];
  comps.forEach((c, i) => {
    const y = 2.05 + i * 0.95;
    card(s, 6.25, y, 3.5, 0.82);
    t(s, c[1], { x: 6.4, y, w: 1.3, h: 0.82, fontSize: 22, bold: true, color: C.accent2, valign: "middle" });
    t(s, [{ text: c[0], options: { bold: true, breakLine: true } }, { text: "= " + c[2], options: { color: C.accent4 } }],
      { x: 7.7, y, w: 2.0, h: 0.82, fontSize: 13, color: C.text1, valign: "middle" });
  });
  [[2.7, 3.15], [5.7, 6.15]].forEach(([a, b]) => s.addShape(pres.shapes.LINE, { x: a, y: 4.2, w: b - a, h: 0,
    line: { color: C.accent4, width: 2, endArrowType: "triangle" } }));
  t(s, "× mezcla", { x: 2.62, y: 3.8, w: 0.65, h: 0.3, fontSize: 11, color: C.accent4, align: "center" });
  t(s, "× lista", { x: 5.6, y: 3.8, w: 0.65, h: 0.3, fontSize: 11, color: C.accent4, align: "center" });
  const x3 = 10.05, w3 = W - M - x3;
  card(s, x3, 2.05, w3, 4.7, { fill: { color: C.accent1, transparency: 88 } });
  t(s, [{ text: "Son tasas, no pedidos", options: { bold: true, fontSize: 16, breakLine: true } },
    { text: "Dicen cuánto se gasta al mes; cuánto y cuándo comprar lo decide la Parte III.", options: { breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "Constantes porque", options: { bold: true, fontSize: 16, breakLine: true } },
    { text: "la tasa, la mezcla y la lista de materiales no cambian y la producción se reparte pareja.", options: { breakLine: true } },
    { text: " ", options: { fontSize: 6, breakLine: true } },
    { text: "× 12 = valores oficiales", options: { bold: true, fontSize: 16, breakLine: true } },
    { text: "96.000 · 24.000 · 120.000 · 60.000 · 24.000" }],
    { x: x3 + 0.25, y: 2.25, w: w3 - 0.45, h: 4.35, fontSize: 14, color: C.text1 });
  rubrica(s, "Rúbrica · D4 Desagregación y requerimientos (10 %): mezcla 50–30–20, lista de materiales y tasas constantes");
  notas(s, PR.PM.name, "0:40",
    "'Para compras, la Gerencia fijó una tasa estable de 10.000 ventiladores al mes. Con la mezcla 50–30–20 son 5.000 Estándar, 3.000 Plus y 2.000 Premium. Con la lista de materiales: el motor estándar lo usan Estándar y Plus, 8.000; la hélice, los tres, 10.000; el módulo, Plus y Premium, 5.000; motor premium y control, solo el Premium, 2.000. Al año coinciden con los oficiales. Ojo: son tasas de consumo, no pedidos; y son constantes porque tasa, mezcla y lista no cambian.'",
    "D4: desagrega la tasa oficial con la mezcla, aplica la lista de materiales, obtiene requerimientos mensuales y anuales; distingue tasas de consumo de tamaños de pedido; justifica la constancia.",
    "¿Y con mezcla 40–30–30? Motor est. 7.000, prem. 3.000, hélice 10.000, módulo 6.000, control 3.000. ¿Qué supuestos de la Parte I lo permiten? Unidad agregada homogénea, demanda determinística, mezcla estable.");
}

// ================================================================ 10 · S7
{
  const s = nueva("CONTENIDO", "S6–S8 · Materiales y EOQ");
  chip(s, "S7 · ¿Cuánto y cuándo pedir cada pieza?");
  badge(s, PR.PM);
  titulo(s, "Q* dice cuánto; el punto de reorden, cuándo");
  // diente de sierra del motor estándar
  const Q = 3394, d = 400, L = 6, ROP = 2400, Tc = Q / d;
  const x0 = 1.35, x1 = 7.0, yT = 2.45, yB = 5.35, tmax = 3 * Tc + 1.2;
  const X = (tt) => x0 + (tt / tmax) * (x1 - x0), Y = (q) => yB - (q / 3700) * (yB - yT);
  const ln = (a, b, c, e, o = {}) => s.addShape(pres.shapes.LINE, Object.assign({ x: a, y: b, w: c, h: e,
    line: { color: C.accent2, width: 2.5 } }, o));
  for (let k = 0; k < 3; k++) {
    ln(X(k * Tc), Y(Q), X((k + 1) * Tc) - X(k * Tc), Y(0) - Y(Q));
    ln(X((k + 1) * Tc), Y(Q), 0, Y(0) - Y(Q));
  }
  ln(X(3 * Tc), Y(Q), X(tmax) - X(3 * Tc), Y(Q - d * (tmax - 3 * Tc)) - Y(Q));
  s.addShape(pres.shapes.LINE, { x: x0, y: Y(0), w: x1 - x0, h: 0, line: { color: C.accent4, width: 1 } });
  s.addShape(pres.shapes.LINE, { x: x0, y: Y(ROP), w: x1 - x0, h: 0, line: { color: C.accent1, width: 1.75, dashType: "dash" } });
  for (let k = 0; k < 3; k++) {
    const te = k * Tc + (Q - ROP) / d;
    s.addShape(pres.shapes.OVAL, { x: X(te) - 0.08, y: Y(ROP) - 0.08, w: 0.16, h: 0.16, fill: { color: C.accent1 }, line: { type: "none" } });
    s.addShape(pres.shapes.LINE, { x: X(te), y: yB + 0.22, w: X(te + L) - X(te), h: 0, line: { color: C.accent1, width: 1.5, endArrowType: "triangle" } });
  }
  t(s, "Q* = 3.394", { x: 0.35, y: Y(Q) - 0.15, w: 0.95, h: 0.3, fontSize: 12, bold: true, color: C.accent2, align: "right" });
  t(s, "ROP = 2.400", { x: 0.2, y: Y(ROP) - 0.15, w: 1.1, h: 0.3, fontSize: 12, bold: true, color: C.accent1, align: "right" });
  t(s, "0", { x: 0.6, y: Y(0) - 0.15, w: 0.7, h: 0.3, fontSize: 12, color: C.accent4, align: "right" });
  t(s, "● se pide al llegar a 2.400 → demora L = 6 días → llega cuando se acaba",
    { x: x0, y: yB + 0.38, w: x1 - x0 + 0.2, h: 0.32, fontSize: 12, color: C.accent4 });
  t(s, "Motor estándar: consume 400 u/día; pide cada 8,5 días operativos", { x: x0, y: 2.05, w: x1 - x0, h: 0.32,
    fontSize: 13, bold: true, color: C.text1 });
  card(s, M, 6.15, 6.6, 0.6, { fill: { color: C.accent1, transparency: 88 } });
  t(s, "Q* = √(2DS/h)  ·  ROP = d·L  ·  si L sube, sube el ROP y Q* no cambia", { x: M + 0.2, y: 6.15, w: 6.2, h: 0.6,
    fontSize: 14, bold: true, color: C.text1, valign: "middle" });
  // tabla de los cinco
  const x2 = 7.55, w2 = W - M - x2;
  const nom = ["Motor estándar", "Motor premium", "Hélice–rejilla", "Módulo electr.", "Control remoto"];
  const hdr = ["Pieza", "Q*", "Pedidos/año", "Cada (días)", "ROP"].map((h) => ({ text: h, options: { bold: true, color: C.accent4 } }));
  const rows = [hdr].concat(D.eoq.map((r, i) => [nom[i], fmt(r.Q), fmt(r.N, 1), fmt(r.T_dias, 1), fmt(r.ROP)]));
  s.addTable(rows, { x: x2, y: 2.05, w: w2, colW: [1.75, 0.85, 1.05, 0.95, w2 - 4.6], fontSize: 14, color: C.text1, rowH: 0.45,
    border: { type: "solid", pt: 0.75, color: "DDE3E9" }, valign: "middle", margin: [0.03, 0.06, 0.03, 0.06], align: "left" });
  card(s, x2, 5.0, w2, 1.75);
  t(s, [{ text: "Trade-off del EOQ", options: { bold: true, color: C.accent2, breakLine: true } },
    { text: "Lote más grande: menos pedidos, más inventario. En Q* se igualan: ordenar 16,89 = mantener 16,89 MM$/año (33,78 en total)." }],
    { x: x2 + 0.25, y: 5.08, w: w2 - 0.5, h: 1.6, fontSize: 14, color: C.text1, valign: "middle" });
  rubrica(s, "Rúbrica · D5 EOQ y factibilidad (15 %): Q* responde cuánto, ROP cuándo; trade-off y efecto del tiempo de entrega");
  notas(s, PR.PM.name, "0:45",
    "'Primero cada pieza por separado, con el EOQ clásico. El ejemplo es el motor estándar: h = 25 % de 12.000 = 3.000; Q* = raíz de 2 × 96.000 × 180.000 / 3.000 = 3.394. Se consumen 400 al día, así que dura 8,5 días. El plazo es 6 días: cuando quedan 400 × 6 = 2.400 se pide, y llega justo cuando se acaba. Q* dice cuánto, el ROP cuándo. En Q* el costo de ordenar y el de mantener se igualan.' Supuestos: consumo y plazo constantes (gracias a la Parte II), lote llega completo, sin quiebres ni descuentos; por eso no hay stock de seguridad.",
    "D5: h, Q*, N, T, d, ROP y costos correctos; interpreta Q* = cuánto y ROP = cuándo; explica el trade-off del EOQ y el efecto del plazo sobre el ROP.",
    "¿Demanda × 2? Q* × 1,41 y ROP × 2. ¿Tasa de mantención 20 %? Q* sube; siguen sin caber (126,5 m³). ¿Y si L > T? Habría pedidos en camino y el ROP se aplica a la posición de inventario.");
}

// ================================================================ 11 · S8
{
  const s = nueva("CONTENIDO", "S6–S8 · Materiales y EOQ");
  chip(s, "S8 · ¿Se pueden aplicar todos los EOQ a la vez?");
  badge(s, PR.PM);
  titulo(s, "Juntos no caben: piden 113 m³ y 135 MM$");
  const col = [HX.accent2, HX.dk2, HX.accent3, HX.accent1, HX.accent4];
  const nom = ["Motor estándar", "Motor premium", "Hélice–rejilla", "Módulo electrónico", "Control remoto"];
  const x0 = 2.3, escala = 7.4; // pulgadas que representan el 100 % del límite
  const filas = [["Espacio", D.eoq.map((r) => r.Espacio), 90, "m³"], ["Capital", D.eoq.map((r) => r.Capital / 1e6), 110, "MM$"]];
  filas.forEach((f, i) => {
    const y = 2.35 + i * 1.45, h = 0.8;
    t(s, f[0], { x: M, y, w: 1.55, h, fontSize: 18, bold: true, color: C.text1, valign: "middle" });
    let x = x0;
    f[1].forEach((v, k) => {
      const w = (v / f[2]) * escala;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: col[k] }, line: { color: "FFFFFF", width: 1 } });
      if (w > 0.6) t(s, fmt(v, 1), { x, y, w, h, fontSize: 13, bold: true, color: k === 2 ? C.text1 : C.background1, align: "center", valign: "middle" });
      x += w;
    });
    const tot = f[1].reduce((a, b) => a + b, 0);
    t(s, [{ text: `${fmt(tot, 1)} ${f[3]}`, options: { bold: true, breakLine: true } },
      { text: `${fmt(100 * tot / f[2], 0)} % del límite`, options: { color: C.accent6 } }],
      { x: x + 0.12, y, w: W - M - x - 0.1, h, fontSize: 14, color: C.text1, valign: "middle" });
    s.addShape(pres.shapes.LINE, { x: x0 + escala, y: y - 0.18, w: 0, h: h + 0.36, line: { color: C.accent6, width: 2.25, dashType: "dash" } });
    t(s, `límite ${f[2]} ${f[3]}`, { x: x0 + escala - 1.0, y: y - 0.45, w: 2.0, h: 0.26, fontSize: 12, color: C.accent6, align: "center" });
  });
  let lx = x0;
  nom.forEach((n, k) => {
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 5.08, w: 0.2, h: 0.2, fill: { color: col[k] }, line: { type: "none" } });
    t(s, n, { x: lx + 0.28, y: 5.03, w: 1.6, h: 0.3, fontSize: 12, color: C.text1 });
    lx += 1.82;
  });
  card(s, M, 5.6, CW, 1.15, { fill: { color: C.accent1, transparency: 88 } });
  t(s, [{ text: "Óptimo individual ≠ óptimo del sistema. ", options: { bold: true } },
    { text: "Cada EOQ minimiza solo su costo y no ve que comparte bodega y capital: la hélice sola usa el 94 % de la bodega y los motores, el 63 % del presupuesto." }],
    { x: M + 0.3, y: 5.65, w: CW - 0.6, h: 1.05, fontSize: 15, color: C.text1, valign: "middle" });
  rubrica(s, "Rúbrica · D5 EOQ y factibilidad (15 %): uso de cada recurso y por qué la optimalidad individual no garantiza factibilidad");
  notas(s, PR.PM.name, "0:45",
    "'Si aplicamos los cinco EOQ a la vez: espacio = Σ v·Q y capital = Σ c·Q, sobre lotes completos, como dice el enunciado. Piden 113 m³ de 90 y 135 millones de 110: no caben en ninguno de los dos. La hélice es voluminosa y barata de mantener, así que su lote es grande y ocupa el 94 % de la bodega ella sola; los motores son caros y concentran el capital. Cada EOQ optimiza su propio costo y no ve el recurso compartido; por eso hay que decidir los cinco lotes juntos.' Paso a Beyonce con el modelo multiproducto.",
    "D5: evalúa la aplicación simultánea y demuestra la incompatibilidad con espacio y presupuesto; explica por qué la optimalidad individual no garantiza factibilidad del sistema.",
    "¿Bastaría achicar la hélice? Arreglaría el espacio (bajaría a ≈4.117 u) pero el capital seguiría excedido en ≈18 MM$. ¿Y con inventario promedio Q/2? Cabrían (56,6 m³ y 67,6 MM$), pero el enunciado habla del valor de los lotes.");
}

// ================================================================ 12 · S9
{
  const s = nueva("CONTENIDO", "S9–S10 · Multiproducto");
  chip(s, "S9 · ¿Cuáles son los mejores lotes que sí caben?");
  badge(s, PR.BB);
  titulo(s, "Lotes 18–21 % menores por solo +2,1 % de costo");
  const wl = 5.6;
  card(s, M, 2.05, wl, 2.35, { fill: { color: C.text2 } });
  t(s, [
    { text: "min  Σᵢ DᵢSᵢ/Qᵢ + hᵢQᵢ/2", options: { bold: true, breakLine: true } },
    { text: "s.a.  Σᵢ vᵢQᵢ ≤ 90 m³   (μ)", options: { breakLine: true } },
    { text: "        Σᵢ cᵢQᵢ ≤ 110 MM$   (λ)", options: { breakLine: true } },
    { text: "Qᵢ = √( 2DᵢSᵢ / (hᵢ + 2μvᵢ + 2λcᵢ) )", options: { bold: true, color: C.accent1 } }],
    { x: M + 0.3, y: 2.15, w: wl - 0.6, h: 2.15, fontSize: 17, color: C.background1, valign: "middle", paraSpaceAfter: 6 });
  const k = [["μ = 5.098", "$/m³-año: bodega activa"], ["λ = 0,0595", "$/$-año: capital activo"], ["94 → 116", "pedidos al año"]];
  const kw = (wl - 0.3) / 3;
  k.forEach((v, i) => {
    const x = M + i * (kw + 0.15);
    card(s, x, 4.6, kw, 1.05);
    t(s, [{ text: v[0], options: { bold: true, fontSize: 18, color: C.accent2, breakLine: true } }, { text: v[1], options: { fontSize: 12, color: C.accent4 } }],
      { x: x + 0.15, y: 4.6, w: kw - 0.25, h: 1.05, valign: "middle" });
  });
  t(s, "Cada recurso escaso actúa como un costo de mantener extra. La compra (2.784 MM$/año) no depende de Q: no entra en la FO.",
    { x: M, y: 5.8, w: wl, h: 0.95, fontSize: 14, italic: true, color: C.accent4 });
  const nom = ["Motor est.", "Motor prem.", "Hélice", "Módulo", "Control"];
  s.addChart(pres.charts.BAR, [
    { name: "EOQ individual (no cabe)", labels: nom, values: D.eoq.map((r) => Math.round(r.Q)) },
    { name: "Multiproducto (cabe)", labels: nom, values: D.multi.map((r) => Math.round(r.Q)) },
  ], Object.assign({ x: 6.5, y: 2.05, w: W - M - 6.5, h: 4.7, barGapWidthPct: 55, chartColors: [HX.accent3, HX.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", valAxisMinVal: 0, valAxisMaxVal: 6500,
    valAxisMajorUnit: 1000, valAxisLabelFormatCode: "#,##0", showLegend: true, legendPos: "b",
    showTitle: true, title: "Tamaño de lote (u)", titleFontSize: 13, titleColor: HX.accent4, titleFontFace: "+mn-lt" }, ejes));
  rubrica(s, "Rúbrica · D6 EOQ multiproducto (20 %): formulación, restricciones, costo de compra y efecto en lotes y frecuencia");
  notas(s, PR.BB.name, "0:40",
    "'Ahora decidimos los cinco lotes juntos: minimizamos el costo de ordenar más mantener sujeto a 90 m³ y 110 millones. Con multiplicadores de Lagrange queda la misma fórmula del EOQ, pero con un costo de mantener aumentado: cada recurso escaso suma un recargo. Las dos restricciones quedan activas. Los lotes bajan 18 a 21 % —la hélice más, por el espacio—, se pide 116 veces al año en vez de 94, y el costo sube solo 0,72 millones, 2,1 %, porque la curva de costo es plana cerca del óptimo. El costo de compra no entra: se compra lo mismo al año con cualquier lote.' Lo verificamos con un segundo método (SLSQP): mismo resultado. Paso a Constanza con la sensibilidad.",
    "D6: formula e implementa el modelo; representa espacio y capital; justifica por qué el costo de compra no afecta la decisión; interpreta cómo cambian lotes, inventario y frecuencia.",
    "¿Restricción activa? Se usa completa en el óptimo (90 m³ y 110 MM$). ¿Por qué cuatro lotes bajan 18 % y la hélice 21 %? Como h = 25 %·c, el recargo del capital es igual para todos (8λ ≈ 48 %); el espacio solo pesa en la hélice. ¿Achicar todos parejo? Con 0,796 cuesta 34,67 MM$ (163 mil más).");
}

// ================================================================ 13 · S10
{
  const s = nueva("CONTENIDO", "S9–S10 · Multiproducto");
  chip(s, "S10 · ¿Conviene ampliar la bodega o el presupuesto?");
  badge(s, PR.CC);
  titulo(s, "Más presupuesto vale 74 veces más que más bodega");
  const lab = D.sens_pct.map((p) => `${p}%`);
  s.addChart(pres.charts.LINE, [
    { name: "Ampliar presupuesto", labels: lab, values: D.ahorro_cap.map((v) => Math.round(v / 1000)) },
    { name: "Ampliar bodega", labels: lab, values: D.ahorro_esp.map((v) => Math.round(v / 1000)) },
  ], Object.assign({ x: M, y: 2.05, w: 7.2, h: 4.7, chartColors: [HX.accent1, HX.accent2], lineSize: 3, lineDataSymbol: "none",
    valAxisMinVal: 0, valAxisMaxVal: 450, valAxisMajorUnit: 100, showLegend: true, legendPos: "b",
    showTitle: true, title: "Ahorro anual (miles de $) según cuánto se amplía cada recurso", titleFontSize: 13,
    titleColor: HX.accent4, titleFontFace: "+mn-lt", catAxisLabelFrequency: 2, showCatAxisTitle: true, catAxisTitle: "ampliación del recurso", catAxisTitleColor: HX.accent4, catAxisTitleFontSize: 12, catAxisTitleFontFace: "+mn-lt" }, ejes));
  const x2 = 8.1, w2 = W - M - x2;
  const cards = [
    ["+10 % bodega → 5.219 $/año", "El espacio deja de ser activo con solo 2,07 m³ extra; el capital, que ya estaba lleno, sigue limitando.", false],
    ["+10 % presupuesto → 386.591 $/año", "Las dos siguen activas y el capital extra se usa entero (sirve hasta ≈125 MM$).", false],
    ["Activa ≠ valiosa", "μ y λ son pendientes locales: μ × 9 m³ prometía 45.880 $/año y el ahorro real fue 5.219.", true],
  ];
  cards.forEach((c, i) => {
    const y = 2.05 + i * 1.6, dk = c[2];
    card(s, x2, y, w2, 1.45, dk ? { fill: { color: C.text2 } } : {});
    t(s, c[0], { x: x2 + 0.25, y: y + 0.13, w: w2 - 0.5, h: 0.36, fontSize: 15, bold: true, color: dk ? C.accent1 : C.text1 });
    t(s, c[1], { x: x2 + 0.25, y: y + 0.52, w: w2 - 0.45, h: 0.85, fontSize: 13, color: dk ? C.background1 : C.text1 });
  });
  rubrica(s, "Rúbrica · D6 Sensibilidad (20 %): cuál recurso vale más y diferencia entre restricción activa y valor marginal");
  notas(s, PR.CC.name, "0:40",
    "'Las dos restricciones están activas, pero eso no significa que valgan lo mismo. Con 10 % más de bodega se ahorran solo 5.219 pesos al año: con 2,07 m³ extra el espacio deja de limitar y el capital, que ya estaba lleno, sigue mandando. Con 10 % más de presupuesto se ahorran 386.591, 74 veces más: las dos siguen activas y el capital extra se usa entero. Los multiplicadores son pendientes locales y cambian apenas se relaja. Recomendación: si se puede ampliar algo, que sea el presupuesto.' Paso a Beyonce para cerrar.",
    "D6: sensibilidad de espacio y presupuesto correcta; recomienda el recurso que más vale; distingue restricción activa de su valor económico marginal.",
    "¿Ambos +10 %? 511.638, más que la suma (391.810): se complementan. ¿Hasta dónde ampliar presupuesto? ≈125,1 MM$ (techo 413.790; el +10 % ya captura el 93 %). ¿Por qué μ sube a 24.785 en b)? Con más capital el espacio pasa a ser lo que más aprieta.");
}

// ================================================================ 14 · CIERRE
{
  const s = nueva("OSCURO", "Cierre");
  chip(s, "Cierre · ¿Qué debe hacer Ventisur?", true);
  badge(s, PR.CC, true);
  titulo(s, "Recomendación integrada para Ventisur");
  const rec = [
    ["Producir", "Sol. 5: 18 trabajadores, HE de sep a feb y cero pendientes.", "301,10 MM$"],
    ["Conectar", "En nov–dic se producen 11.700 u: subir los ROP a 2.808 · 1.170 · 4.680 · 2.925 · 1.404 (sobre la posición de inventario).", "+17 % de consumo"],
    ["Comprar", "Lotes multiproducto con sus ROP, no los EOQ individuales (no caben).", "+0,72 MM$/año"],
    ["Invertir", "Si se amplía un recurso, que sea el presupuesto de lotes, no la bodega.", "386.591 $/año"],
  ];
  const gap = 0.25, cw = (CW - 3 * gap) / 4;
  rec.forEach((r, i) => {
    const x = M + i * (cw + gap), y = 2.05, h = 3.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h, rectRadius: 0.12, fill: { color: C.background1, transparency: 90 }, line: { type: "none" } });
    num(s, i + 1, x + 0.25, y + 0.25, 0.48);
    t(s, r[0], { x: x + 0.25, y: y + 0.9, w: cw - 0.5, h: 0.42, fontSize: 20, bold: true, color: C.background1 });
    t(s, r[1], { x: x + 0.25, y: y + 1.38, w: cw - 0.45, h: 1.55, fontSize: 14, color: C.background1 });
    t(s, r[2], { x: x + 0.25, y: y + 3.0, w: cw - 0.5, h: 0.42, fontSize: 18, bold: true, color: C.accent1 });
  });
  t(s, [{ text: "Supuestos: ", options: { bold: true, color: C.accent1 } },
    { text: "demanda y plazos determinísticos (sin stock de seguridad) · unidad agregada homogénea · espacio y capital medidos sobre lotes completos · el EOQ supone consumo parejo y el plan no lo es (por eso el punto 2)." }],
    { x: M, y: 5.95, w: CW, h: 0.8, fontSize: 14, color: C.background1, valign: "middle" });
  rubrica(s, "Rúbrica · D7 Integración (10 %): conectar las etapas, reconocer supuestos y limitaciones");
  notas(s, PR.CC.name, "0:50",
    "'Para cerrar, cuatro decisiones. Uno: producir con la Sol. 5, 18 trabajadores, horas extra de septiembre a febrero y cero pendientes, 301,1 millones. Dos: conectar las partes: las compras usan 10.000 al mes, pero el plan produce 11.700 en nov–dic, así que en esos meses hay que subir los puntos de reorden. Tres: comprar con los lotes multiproducto, que cumplen bodega y capital por solo 0,72 millones al año. Cuatro: si se amplía algo, el presupuesto. Todo con demanda y plazos determinísticos.' Gracias, quedamos atentos a sus preguntas.",
    "D7: conecta planificación con abastecimiento, distingue qué decisión responde cada modelo, reconoce supuestos y limitaciones.",
    "¿Qué decisión responde cada modelo? A–C y Sol. 5: gente y producción por mes; desagregación: consumo; EOQ: cuánto; ROP: cuándo; multiproducto: cuánto con recursos compartidos. ¿Cómo verificaron la IA? Costos recalculados, Excel con fórmulas, óptimo único, M ajustada, KKT y SLSQP.");
}

// ================================================================ 15–16 · RESPALDO
{
  const s = nueva("CONTENIDO", "Respaldo");
  chip(s, "Respaldo para preguntas · ¿Qué pasa si…?");
  titulo(s, "Respaldo: cambios de parámetros ya resueltos");
  const p1 = [["Si cambia…", "Resultado"], ["Sin límite ±3", "nada (300,75)"], ["Mantener cuesta $500", "299,10"], ["Atrasar cuesta $1.500", "301,00 (sigue atrasando 200 u)"],
    ["HE cuesta $3.000 (Sol. 5)", "307,05 (19 desde sep)"], ["Sin horas extra", "312,90 (20 a 23 trabajadores)"], ["Despedir gratis", "293,95"],
    ["Multa < $151.250", "B paga 1 multa"], ["Dic +5 % (conocido)", "303,91 con 18"]];
  const p3 = [["Si cambia…", "Resultado"], ["Demanda × 2 (EOQ)", "Q* × 1,41 · ROP × 2"], ["Plazo L mayor", "sube ROP; Q* igual"], ["Mantención 20 % / 30 %", "126,5 / 103,2 m³: no caben"],
    ["Solo espacio", "34.089.228 $/año (usa 125,1 MM$)"], ["Solo capital", "34.497.798 $/año (usa 92,07 m³)"], ["+10 % ambos", "ahorro 511.638"],
    ["Hélice × 2 (multi)", "lote ≈ igual; μ sube a 70.284"], ["Mezcla 40–30–30", "7.000 · 3.000 · 10.000 · 6.000 · 3.000"]];
  const tw = (CW - 0.4) / 2;
  [[p1, M, "Parte I (MM$)"], [p3, M + tw + 0.4, "Parte II y III"]].forEach(([tb, x, cap]) => {
    t(s, cap, { x, y: 2.05, w: tw, h: 0.35, fontSize: 15, bold: true, color: C.accent2 });
    const rows = tb.map((r, i) => r.map((c) => ({ text: c, options: i === 0 ? { bold: true, color: C.accent4 } : {} })));
    s.addTable(rows, { x, y: 2.5, w: tw, colW: [2.6, tw - 2.6], fontSize: 13, color: C.text1, rowH: 0.46,
      border: { type: "solid", pt: 0.75, color: "DDE3E9" }, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08] });
  });
  rubrica(s, "Rúbrica · reglas de aplicación: preguntas de modificación de parámetros y restricciones");
  notas(s, "Cualquiera", "solo si preguntan", "Diapositiva de respaldo: no se presenta. Úsenla para responder preguntas de cambios de parámetros.", "Todas las dimensiones: razonar frente a modificaciones.", "Ver la guía de estudio, anexo A.");
}
{
  const s = nueva("CONTENIDO", "Respaldo");
  chip(s, "Respaldo para preguntas · plan mes a mes");
  titulo(s, "Respaldo: plan recomendado (Sol. 5) mes a mes");
  const reg = D.A.regular; // la producción regular de C es igual a la de A
  const hdr = [{ text: "", options: {} }].concat(D.meses.map((m) => ({ text: m, options: { bold: true, color: C.accent4, align: "right" } })));
  const fila = (nom, arr) => [{ text: nom, options: { bold: true } }].concat(arr.map((v) => ({ text: fmt(v), options: { align: "right" } })));
  const rows = [hdr, fila("Demanda", D.demanda), fila("Trabajadores", Array(12).fill(18)), fila("Producción regular", reg),
    fila("Horas extra", D.C.he), fila("Inventario final", D.C.inv), fila("Pendientes", Array(12).fill(0))];
  s.addTable(rows, { x: M, y: 2.1, w: CW, colW: [2.33].concat(Array(12).fill((CW - 2.33) / 12)), fontSize: 14, color: C.text1,
    rowH: 0.52, border: { type: "solid", pt: 0.75, color: "DDE3E9" }, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08] });
  t(s, "Marzo: despide 2 (20 → 18). La HE está al 100 % en nov–dic (2.700 = 150 × 18) y al 93 % en ene–feb. Inventario máximo: 800 u en noviembre.",
    { x: M, y: 6.0, w: CW, h: 0.7, fontSize: 14, color: C.accent4 });
  rubrica(s, "Rúbrica · D3: decisiones operacionales del plan recomendado");
  notas(s, "Cualquiera", "solo si preguntan", "Diapositiva de respaldo con el plan mensual de la Sol. 5.", "D3: decisiones de dotación, producción, HE e inventario.", "—");
}

(async () => {
  await pres.writeFile({ fileName: SALIDA });
  await applyTheme(SALIDA, THEME);
  console.log("escrito", SALIDA);
})();
