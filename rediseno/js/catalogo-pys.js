/* ════════════════════════════════════════════════════════════════════
   CATÁLOGO REAL de peptidosysuplementos.mx

   Sale del inventario de WooCommerce levantado en una sesión anterior
   (docs/data/blog-interlinks/inventario.json): nombres, slugs, SKU,
   categorías y existencias son los de la tienda, no inventados.

   LO ÚNICO QUE NO ES REAL SON LOS PRECIOS. La toma del inventario no
   trajo el campo de precio y desde este entorno el dominio está
   bloqueado por política del proxy, así que van marcados como ejemplo
   en la página. Cuando llegue la lista real se cambia solo aquí.

   Dos péptidos (Cagrilintida y Timosina Alfa-1) no están entre las 15
   etiquetas de imprenta, así que se muestran con un render del vial sin
   rótulo en vez de inventarles uno.
   ════════════════════════════════════════════════════════════════════ */

const PYS_SITIO = "https://peptidosysuplementos.mx";

const PYS_CATS = [
 {
  "corto": "Metabolismo",
  "largo": "Péptidos para Metabolismo y Pérdida de Peso"
 },
 {
  "corto": "Bienestar",
  "largo": "Péptidos Bienestar General"
 },
 {
  "corto": "Reparación",
  "largo": "Péptidos Reparación Celular Anti-Aging"
 },
 {
  "corto": "Cognitivo",
  "largo": "Péptidos para Rendimiento Cognitivo"
 },
 {
  "corto": "Suplementos",
  "largo": "Suplementos Deportivos Premium"
 },
 {
  "corto": "Muscular",
  "largo": "Péptidos Recuperación y Crecimiento Muscular"
 },
 {
  "corto": "Deportivo",
  "largo": "Péptidos para Rendimiento Deportivo"
 }
];

const PYS_PRODUCTOS = [
 {
  "nombre": "Cagrilintida",
  "nombreSeo": "Cagrilintida",
  "slug": "cagrilintida-10mg",
  "url": "https://peptidosysuplementos.mx/product/cagrilintida-10mg/",
  "sku": "CAGRI-10MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-sin-etiqueta.jpg",
  "frasco": false,
  "precio": 2650
 },
 {
  "nombre": "Glutatión 1500mg",
  "nombreSeo": "Glutatión 1500mg | Antioxidante y Detox Celular México",
  "slug": "glutation-1500mg",
  "url": "https://peptidosysuplementos.mx/product/glutation-1500mg/",
  "sku": "GLUT-1500MG",
  "existencia": "instock",
  "cats": [
   "Péptidos Bienestar General"
  ],
  "cat": "Bienestar",
  "img": null,
  "frasco": true,
  "precio": 860
 },
 {
  "nombre": "CJC-1295 (no-DAC) + Ipamorelina",
  "nombreSeo": "CJC-1295 (no-DAC) + Ipamorelina",
  "slug": "cjc-1295-ipamorelina-5mg",
  "url": "https://peptidosysuplementos.mx/product/cjc-1295-ipamorelina-5mg/",
  "sku": "CJC-IPA-5MG",
  "existencia": "instock",
  "cats": [
   "Péptidos Reparación Celular Anti-Aging"
  ],
  "cat": "Reparación",
  "img": "img/vial-cjc-1295-ipamorelin-no-dac-5-5mg.jpg",
  "frasco": false,
  "precio": 1320
 },
 {
  "nombre": "Sermorelina",
  "nombreSeo": "Sermorelina",
  "slug": "sermorelina-10mg",
  "url": "https://peptidosysuplementos.mx/product/sermorelina-10mg/",
  "sku": "SERMO-10MG",
  "existencia": "instock",
  "cats": [
   "Péptidos Reparación Celular Anti-Aging"
  ],
  "cat": "Reparación",
  "img": "img/vial-sermorelin-10-mg.jpg",
  "frasco": false,
  "precio": 1540
 },
 {
  "nombre": "Timosina Alfa-1",
  "nombreSeo": "Timosina Alfa-1",
  "slug": "thymosin-alpha-1-10mg",
  "url": "https://peptidosysuplementos.mx/product/thymosin-alpha-1-10mg/",
  "sku": "THYA1-10MG",
  "existencia": "instock",
  "cats": [
   "Péptidos Bienestar General"
  ],
  "cat": "Bienestar",
  "img": "img/vial-sin-etiqueta.jpg",
  "frasco": false,
  "precio": 2980
 },
 {
  "nombre": "Selank",
  "nombreSeo": "Selank",
  "slug": "selank-10-mg",
  "url": "https://peptidosysuplementos.mx/product/selank-10-mg/",
  "sku": "SELANK-10MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Rendimiento Cognitivo"
  ],
  "cat": "Cognitivo",
  "img": "img/vial-selank-10-mg.jpg",
  "frasco": false,
  "precio": 1180
 },
 {
  "nombre": "Semaglutida 5mg",
  "nombreSeo": "Semaglutida 5mg | Péptido GLP-1 Control Peso México",
  "slug": "semaglutida-5-mg",
  "url": "https://peptidosysuplementos.mx/product/semaglutida-5-mg/",
  "sku": "SEMA-5MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-semaglutida-5-mg.jpg",
  "frasco": false,
  "precio": 1450
 },
 {
  "nombre": "Tirzepatida 60 mg",
  "nombreSeo": "Tirzepatida 60 mg",
  "slug": "tirzepatida-60-mg",
  "url": "https://peptidosysuplementos.mx/product/tirzepatida-60-mg/",
  "sku": "TIRZ-60MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-tirzepatida-60-mg.jpg",
  "frasco": false,
  "precio": 6400
 },
 {
  "nombre": "Tirzepatida",
  "nombreSeo": "Tirzepatida",
  "slug": "tirzepatida-30-mg",
  "url": "https://peptidosysuplementos.mx/product/tirzepatida-30-mg/",
  "sku": "TIRZ-30MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-tirzepatida-30-mg.jpg",
  "frasco": false,
  "precio": 3600
 },
 {
  "nombre": "Semaglutida 20mg",
  "nombreSeo": "Semaglutida 20mg | Péptido Control de Peso y Apetito México",
  "slug": "semaglutida-20mg",
  "url": "https://peptidosysuplementos.mx/product/semaglutida-20mg/",
  "sku": "SEMA-20MG",
  "existencia": "outofstock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-semaglutida-20-mg.jpg",
  "frasco": false,
  "precio": 3200
 },
 {
  "nombre": "Complejo B Metilado Nutricost 60 Caps Energía y Metabolismo",
  "nombreSeo": "Complejo B Metilado Nutricost 60 Caps Energía y Metabolismo",
  "slug": "methylated-vitamin-b-complex-nutricost",
  "url": "https://peptidosysuplementos.mx/product/methylated-vitamin-b-complex-nutricost/",
  "sku": "CPLXB-60CAP",
  "existencia": "outofstock",
  "cats": [
   "Suplementos Deportivos Premium",
   "Péptidos Bienestar General"
  ],
  "cat": "Suplementos",
  "img": null,
  "frasco": true,
  "precio": 480
 },
 {
  "nombre": "DIM 300mg Nutricost",
  "nombreSeo": "DIM 300mg Nutricost | Balance Hormonal 120 Cápsulas México",
  "slug": "dim-nutricost-300mg",
  "url": "https://peptidosysuplementos.mx/product/dim-nutricost-300mg/",
  "sku": "DIM-300MG",
  "existencia": "outofstock",
  "cats": [
   "Suplementos Deportivos Premium",
   "Péptidos Bienestar General"
  ],
  "cat": "Suplementos",
  "img": null,
  "frasco": true,
  "precio": 540
 },
 {
  "nombre": "Zinc Picolinato 50mg",
  "nombreSeo": "Zinc Picolinato 50mg | 240 Cápsulas Nutricost México",
  "slug": "zinc-picolinato-nutricost-50mg",
  "url": "https://peptidosysuplementos.mx/product/zinc-picolinato-nutricost-50mg/",
  "sku": "ZINC-50MG",
  "existencia": "outofstock",
  "cats": [
   "Suplementos Deportivos Premium",
   "Péptidos Bienestar General"
  ],
  "cat": "Suplementos",
  "img": null,
  "frasco": true,
  "precio": 420
 },
 {
  "nombre": "Omega-3 2500mg EPA DHA",
  "nombreSeo": "Omega-3 2500mg EPA DHA | 120 Softgels Nutricost México",
  "slug": "omega-3-nutricost-2500mg",
  "url": "https://peptidosysuplementos.mx/product/omega-3-nutricost-2500mg/",
  "sku": "OMEGA3-2500MG",
  "existencia": "outofstock",
  "cats": [
   "Suplementos Deportivos Premium"
  ],
  "cat": "Suplementos",
  "img": null,
  "frasco": true,
  "precio": 690
 },
 {
  "nombre": "NAD+",
  "nombreSeo": "NAD+",
  "slug": "nad-plus-500mg",
  "url": "https://peptidosysuplementos.mx/product/nad-plus-500mg/",
  "sku": "NAD-500MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-nad-500-mg.jpg",
  "frasco": false,
  "precio": 2400
 },
 {
  "nombre": "IGF-1 LR3",
  "nombreSeo": "IGF-1 LR3",
  "slug": "igf-1-lr3-1mg",
  "url": "https://peptidosysuplementos.mx/product/igf-1-lr3-1mg/",
  "sku": "IGF1-1MG",
  "existencia": "instock",
  "cats": [
   "Péptidos Reparación Celular Anti-Aging"
  ],
  "cat": "Reparación",
  "img": "img/vial-igf-1-lr3-1-mg.jpg",
  "frasco": false,
  "precio": 2290
 },
 {
  "nombre": "Agua Bacteriostática",
  "nombreSeo": "Agua Bacteriostática",
  "slug": "agua-bacteriostatica-3ml",
  "url": "https://peptidosysuplementos.mx/product/agua-bacteriostatica-3ml/",
  "sku": "AGUA-BACT",
  "existencia": "instock",
  "cats": [
   "Péptidos Recuperación y Crecimiento Muscular"
  ],
  "cat": "Muscular",
  "img": "img/vial-agua-bacteriostatica-0-9-alcohol-bencilico.jpg",
  "frasco": false,
  "ml": 3,
  "precio": 180
 },
 {
  "nombre": "BPC-157 + TB-500",
  "nombreSeo": "BPC-157 + TB-500",
  "slug": "bpc-157-tb-500-10-10mg",
  "url": "https://peptidosysuplementos.mx/product/bpc-157-tb-500-10-10mg/",
  "sku": "BPC-TB500-5MG",
  "existencia": "instock",
  "cats": [
   "Péptidos Recuperación y Crecimiento Muscular"
  ],
  "cat": "Muscular",
  "img": "img/vial-bpc-157-tb500-5-5mg.jpg",
  "frasco": false,
  "precio": 2150
 },
 {
  "nombre": "MOTS-c 40 mg",
  "nombreSeo": "MOTS-c 40 mg",
  "slug": "mots-c-40mg",
  "url": "https://peptidosysuplementos.mx/product/mots-c-40mg/",
  "sku": "MOTSC-40MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso",
   "Péptidos para Rendimiento Deportivo"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-mots-c-40-mg.jpg",
  "frasco": false,
  "precio": 4950
 },
 {
  "nombre": "MOTS-c",
  "nombreSeo": "MOTS-c",
  "slug": "mots-c-10mg",
  "url": "https://peptidosysuplementos.mx/product/mots-c-10mg/",
  "sku": "MOTSC-10MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-mots-c-10-mg.jpg",
  "frasco": false,
  "precio": 1890
 },
 {
  "nombre": "Retatrutida",
  "nombreSeo": "Retatrutida",
  "slug": "retatrutida-30mg",
  "url": "https://peptidosysuplementos.mx/product/retatrutida-30mg/",
  "sku": "RETAT-30MG",
  "existencia": "instock",
  "cats": [
   "Péptidos para Metabolismo y Pérdida de Peso"
  ],
  "cat": "Metabolismo",
  "img": "img/vial-retatrutida-30-mg.jpg",
  "frasco": false,
  "precio": 4900
 }
];

const PYS_BLOG = [
 {
  "titulo": "Agua Bacteriostática: Qué Es, Para Qué Sirve y Cómo Reconstituir Péptidos Paso a Paso (Guía 2026)",
  "url": "https://peptidosysuplementos.mx/agua-bacteriostatica-que-es-para-que-sirve-como-reconstituir-peptidos/",
  "fecha": "2026-07-27",
  "palabras": 3687
 },
 {
  "titulo": "Ozempic vs Mounjaro vs Zepbound: Comparativa GLP-1 para Bajar de Peso en México 2026",
  "url": "https://peptidosysuplementos.mx/ozempic-vs-mounjaro-vs-zepbound-comparativa-glp-1-mexico-2026/",
  "fecha": "2026-07-25",
  "palabras": 3520
 },
 {
  "titulo": "Tirzepatida: qué es, para qué sirve, cómo funciona, dosis y resultados — Guía Completa 2026",
  "url": "https://peptidosysuplementos.mx/tirzepatida-para-que-sirve-guia-completa-mexico-2026/",
  "fecha": "2026-07-24",
  "palabras": 3478
 },
 {
  "titulo": "Péptidos: Qué son, para qué sirven y cómo usarlos de forma segura en 2026",
  "url": "https://peptidosysuplementos.mx/peptidos-que-son-para-que-sirven-como-usarlos/",
  "fecha": "2026-07-18",
  "palabras": 3324
 },
 {
  "titulo": "Publicamos un dataset abierto de péptidos de investigación",
  "url": "https://peptidosysuplementos.mx/publicamos-un-dataset-abierto-de-peptidos-de-investigacion/",
  "fecha": "2026-07-14",
  "palabras": 150
 },
 {
  "titulo": "Péptidos GLP-1 y adicciones: qué dice la evidencia científica",
  "url": "https://peptidosysuplementos.mx/peptidos-glp-1-adicciones-evidencia-cientifica/",
  "fecha": "2026-07-12",
  "palabras": 2060
 },
 {
  "titulo": "BPC-157: El Péptido de Recuperación que Está Revolucionando el Mundo Deportivo",
  "url": "https://peptidosysuplementos.mx/bpc-157-peptido-recuperacion-deportiva/",
  "fecha": "2026-07-11",
  "palabras": 4568
 },
 {
  "titulo": "Biohacking: La Guía Definitiva para Optimizar tu Cuerpo con Péptidos y Suplementos en 2025",
  "url": "https://peptidosysuplementos.mx/biohacking-guia-definitiva-peptidos-suplementos-2025/",
  "fecha": "2026-07-02",
  "palabras": 3896
 },
 {
  "titulo": "Testosterona: Qué es, funciones, niveles óptimos y cómo optimizarla naturalmente en 2026",
  "url": "https://peptidosysuplementos.mx/testosterona-que-es-funciones-niveles-optimos-como-optimizarla/",
  "fecha": "2026-06-29",
  "palabras": 4405
 },
 {
  "titulo": "Retatrutide: El Péptido Triple Agonista que Está Revolucionando la Pérdida de Peso en 2026",
  "url": "https://peptidosysuplementos.mx/retatrutide-peptido-triple-agonista-perdida-de-peso/",
  "fecha": "2026-06-25",
  "palabras": 3610
 },
 {
  "titulo": "Pérdida de Grasa con Péptidos y Suplementos: Guía Científica Completa 2026",
  "url": "https://peptidosysuplementos.mx/perdida-de-grasa-peptidos-suplementos-guia-cientifica/",
  "fecha": "2026-06-22",
  "palabras": 3280
 },
 {
  "titulo": "TB-500: El Péptido de Recuperación que Todo Atleta Debe Conocer",
  "url": "https://peptidosysuplementos.mx/tb-500-peptido-recuperacion-atletas/",
  "fecha": "2026-06-20",
  "palabras": 3442
 },
 {
  "titulo": "Cómo Optimizar el Rendimiento Deportivo con Suplementos y Péptidos: Guía Completa 2026",
  "url": "https://peptidosysuplementos.mx/optimizar-rendimiento-deportivo-suplementos-peptidos/",
  "fecha": "2026-06-08",
  "palabras": 3180
 },
 {
  "titulo": "GHK-Cu: El Péptido de Cobre que Revoluciona la Regeneración y el Antienvejecimiento",
  "url": "https://peptidosysuplementos.mx/ghk-cu-peptido-cobre-regeneracion-antienvejecimiento/",
  "fecha": "2026-06-05",
  "palabras": 2530
 },
 {
  "titulo": "Semaglutida 2026: Guia Completa de Perdida de Peso",
  "url": "https://peptidosysuplementos.mx/semaglutida-2026-guia-completa-perdida-peso/",
  "fecha": "2026-06-02",
  "palabras": 2330
 },
 {
  "titulo": "Peptidos para Longevidad: Ciencia del Antienvejecimiento",
  "url": "https://peptidosysuplementos.mx/peptidos-para-longevidad-ciencia-antienvejecimiento/",
  "fecha": "2026-05-28",
  "palabras": 2402
 },
 {
  "titulo": "Retatrutida: qué es, cómo funciona y beneficios",
  "url": "https://peptidosysuplementos.mx/retatrutide-precio-guia-completa-costos-beneficios/",
  "fecha": "2026-05-26",
  "palabras": 2119
 },
 {
  "titulo": "Retatrutida TRIUMPH-1: Resultados Clinicos Reales 2026",
  "url": "https://peptidosysuplementos.mx/retatrutide-triumph-1/",
  "fecha": "2026-05-21",
  "palabras": 2630
 }
];

/* landings reales que ya existen en el sitio */
const PYS_LANDINGS = [
  { t:"GLP-1",                 u:"/glp-1/" },
  { t:"Péptidos inyectables",  u:"/peptidos-inyectables/" },
  { t:"Bajar de peso",         u:"/peptidos-para-bajar-de-peso/" },
  { t:"Masa muscular",         u:"/peptidos-para-masa-muscular/" },
  { t:"Pérdida de peso",       u:"/perdida-de-peso/" },
];
