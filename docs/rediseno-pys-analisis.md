# Rediseño PYS — análisis del flujo del video y prueba en clon

Fecha: 13 sep 2026 · Rama: `claude/peptidos-suplementos-redesign-4xi3sw`

## 1. Qué propone el flujo del video

| Paso | Herramienta | Qué aporta |
|---|---|---|
| 1 | `npm install motion` (Framer Motion 12/13) | Motor de animación: scroll reveals, stagger, springs |
| 2 | UI UX Pro Max (`uipro init`) | Catálogo de decisiones: 57 estilos UI, 95 paletas, 56 pares tipográficos, 29 patrones de landing |
| 3 | Instalar como skill de Claude Code | El catálogo queda disponible como contexto en cada prompt |
| 4 | 21st.dev → "Copy prompt" | Componentes React/Tailwind ya hechos, pegados como prompt (~700 líneas) |

Prompt base del video: *"Use Framer Motion for all animations. Apply scroll-triggered
fades, staggered reveals, and smooth hover transitions on interactive elements."*

## 2. Dónde encaja y dónde no, para peptidosysuplementos.mx

**El supuesto del video es que ya tienes un proyecto React/Next + Tailwind.** PYS no lo tiene:

- La tienda real corre en **WordPress + WooCommerce** (PHP, tema, plugins).
- Este repo es **Python/Flask** (`agent.py`, `web.py`, `requirements.txt`). No hay `package.json`.

Consecuencia práctica: los pasos 1 y 4 **no se pueden aplicar sobre la tienda actual**.
Un componente de 21st.dev asume `shadcn/ui`, `tailwind.config`, el helper `cn()` y
`lucide-react`. Nada de eso existe en un tema de WordPress.

El paso 2 (UI UX Pro Max) **sí es portable**, porque no es código: es un brief de
decisiones de diseño. Su equivalente sin instalar nada es un archivo de tokens propio,
que es lo que se usó en este prototipo.

## 3. Las tres rutas reales

| Ruta | Qué implica | Riesgo SEO | Cuándo conviene |
|---|---|---|---|
| **A. Prototipo estático** (hecho) | 1 archivo HTML, Framer Motion por CDN | Cero: no toca producción | Decidir dirección visual antes de gastar |
| **B. Child theme WooCommerce** | Portar la dirección visual a CSS/JS del tema | Bajo, si se conservan URLs y marcado | Es la ruta de producción realista |
| **C. Headless Next.js + Store API** | Front nuevo contra WooCommerce | **Alto**: hay que rehacer checkout, pagos y redirects | Solo con presupuesto y plan de migración |

Nota sobre la ruta C: el repo documenta una inversión SEO fuerte (Rank Math, blogs
consolidados, interlinks, fichas con PMID verificados contra PubMed, competencia
directa con exomapeptides.mx). Un replatform sin mapa de redirects `/product/...`
tira esa inversión. No es un riesgo teórico.

## 4. Advertencias sobre el flujo tal cual

1. **Peso de JS.** Framer Motion pesa ~30–50 kB gzip. En un ecommerce, LCP y CLS
   son dinero y posición. Vale la pena medir antes y después.
2. **"Copy prompt" arrastra dependencias.** Las ~700 líneas que se pegan traen
   supuestos de stack; en una demo se ve bien, en producción hay que auditarlas.
3. **Animar todo cansa.** El prompt dice "all animations". Aquí se limitó a:
   reveals bajo la línea de flotación, stagger en rejillas, hover con spring y un
   barrido sobre el cromatograma. El primer pantallazo **nunca** queda oculto.
4. **`prefers-reduced-motion`** se respeta: con esa preferencia activa, todo queda estático.

## 5. Lo que se construyó (ruta A)

`rediseno/index.html` — una sola página, sin build, sin `node_modules`.

Dirección visual: **certificado de análisis**, no "landing de biotech genérica".
La tesis del hero es el cromatograma HPLC, que es el diferenciador real del negocio.

- **Color**: tinta `#0D1219`, papel frío `#EDEFF3`, acento azul de metileno `#1F4FD8`,
  ámbar `#A85C13` solo para suplementos, verde `#146B48` solo para estados verificados.
- **Tipografía**: Archivo (display) · IBM Plex Sans (texto) · IBM Plex Mono (todo dato:
  lotes, purezas, mg/ml, precios).
- **Layout**: rejilla estricta con filetes de 1 px; las fichas parecen etiquetas de
  espécimen, no tarjetas redondeadas con sombra.

Contenido real extraído del repo (no lorem):

- 12 productos del catálogo: Retatrutida, Tirzepatida, Cagrilintida, BPC-157 + TB-500,
  MOTS-c, CJC-1295 + Ipamorelina, NAD+, Sermorelina, agua bacteriostática y
  suplementos Nutricost.
- 3 referencias con PMID verificado: 14500546, 36588717, 27847966.
- 3 entradas reales del blog.

Dos piezas que la competencia no tiene:

- **Calculadora de reconstitución** (mg de vial + ml de agua → mg/ml y unidades en
  jeringa U-100, con la escala dibujada).
- **Tabla de volúmenes** por presentación.

Animaciones con `motion@13.2.0` (mismo motor que `framer-motion`, API para DOM),
cargado como módulo ESM desde jsDelivr. Si el CDN falla, la página se ve completa:
nada se oculta desde el CSS, solo desde JS y después de que la librería cargó.

## 6. Datos que faltan

Sin credenciales `WC_*` en el entorno y con egress bloqueado hacia
`peptidosysuplementos.mx`, **los precios, lotes, purezas y métricas del prototipo son
de ejemplo**, marcados como tales en la barra superior y en el pie. Con las llaves de
WooCommerce se pueden traer los reales.
