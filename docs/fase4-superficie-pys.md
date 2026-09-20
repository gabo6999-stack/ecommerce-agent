# FASE 4 — Superficie

> 2026-08-02. Base: `docs/superficie-pys-vs-exoma.md`.

## a) Consolidación de categorías — APLICADA 2026-08-02

Aprobado y ejecutado. Los 4 redirects se crearon vía la REST API del plugin
"Redirection" (`/wp-json/redirection/v1/redirect`, JWT) y se verificaron en
vivo, los 4 con 301 limpio a `/category/blog/`:

| origen | verificado |
|---|---|
| `/category/metabolismo/` | ✅ 301 → `/category/blog/` (200) |
| `/category/salud-metabolica/` | ✅ 301 → `/category/blog/` (200) — tardó en propagar por caché LiteSpeed, resuelto re-guardando el post 1926 (dispara `purge-on-update`) |
| `/category/longevidad-y-regeneracion-biologica/` | ✅ 301 → `/category/blog/` (200) |
| `/category/crecimiento-y-reparacion/` | ✅ 301 → `/category/blog/` (200) |

**Verificación de enlaces internos:** barridos los 19 posts publicados — **0
enlaces** hacia cualquiera de las 4 categorías retiradas. Nada que corregir.

Reporte técnico: `scripts/fase4a_consolida_categorias.py`,
`docs/data/fase4a-redirects-2026-08-02.json`.

---

## a) Consolidación de los 5 archivos de categoría del blog

### Diagnóstico, medido antes de proponer nada

| categoría | ID | posts asignados | tráfico GSC (28d) | en menú de navegación |
|---|---:|---:|---:|---|
| `blog` | 207 | **13** (toda la actividad reciente) | 0 clics, 0 impresiones | no |
| `salud-metabolica` | 44 | 3 (posts de jul-2026) | 0 clics, 0 impresiones | no |
| `longevidad-y-regeneracion-biologica` | 38 | 2 (posts de jul-2026) | 0 clics, 0 impresiones | no |
| `metabolismo` | 110 | 1 (post de jul-2026) | 0 clics, 0 impresiones | no |
| `crecimiento-y-reparacion` | 42 | **0** — vacía, ya en `noindex` | 0 clics, 0 impresiones | no |

**El diagnóstico original ("metabolismo y salud-metabolica casi duplicados") se
queda corto: no son duplicados entre sí — son remanentes de un esquema de
categorización que se abandonó.** Los 6 posts de jul-2026 (1476, 1913, 1675,
1926, 1727, 1647) se repartieron a mano entre 3 categorías temáticas; desde
entonces, los 13 posts más recientes (incluido el más nuevo, 2392) caen todos
en `blog` sin excepción. `crecimiento-y-reparacion` quedó sin ni un post y
alguien ya la marcó `noindex` — la señal de que esto se detectó antes, pero no
se terminó de resolver.

Ninguna de las 5 tiene tráfico orgánico real ni enlace desde el menú de
navegación (verificado: ninguna cadena `category/*` aparece en el HTML de la
portada). El único riesgo no verificado es backlinks externos — no hay
herramienta de backlinks conectada en este stack para descartarlo del todo;
si te preocupa, lo mediría antes de aplicar.

### Propuesta: consolidar las 4 vacías/casi-vacías en `blog`

| origen (301 desde) | destino (301 hacia) |
|---|---|
| `/category/metabolismo/` | `/category/blog/` |
| `/category/salud-metabolica/` | `/category/blog/` |
| `/category/longevidad-y-regeneracion-biologica/` | `/category/blog/` |
| `/category/crecimiento-y-reparacion/` | `/category/blog/` |

`/category/blog/` se queda como está — es la única con contenido real (13
posts) y no requiere redirección.

**Nota de alcance:** el 301 resuelve el archivo (la página de categoría), no
requiere reasignar la categoría de los 6 posts individuales — sus permalinks
de post no cambian, solo desaparece la página de listado por categoría que
casi nadie visita.

**Implementación técnica, cuando lo apruebes:** PYS no tiene acceso SSH
(cuenta de Hostinger distinta a la de raditech — ver memoria del proyecto), así
que no hay `.htaccess` editable directo. El camino es el módulo de
Redirecciones de Rank Math (ya instalado, mismo plugin SEO del sitio) vía su
propio endpoint REST, o un snippet en el mu-plugin `pys-seo-tweaks.php` que ya
existe (`litespeed_buffer_before` para el ajuste de lazy-load) enganchado a
`template_redirect`. Lo decido en el momento de aplicar, no antes.

---

## b) Landings de intención en raíz — candidatas

### Resultado: 0 de 4 candidatos con volumen real pasaron las 4 compuertas

Las 6 landings existentes (`/glp-1/`, `/perdida-de-peso/`, `/longevidad/`,
`/reparacion-celular/`, `/capacidad-fisica-performance/`,
`/acelerar-el-metabolismo/`) comparten un patrón: son objetivos **anclados al
catálogo de péptidos** (pérdida de peso, recuperación, rendimiento), no temas
de bienestar genérico. Al buscar temas nuevos fuera de ese patrón — sueño,
sistema inmune, memoria, energía, estrés — con `keyword_suggestions("pys",
"peptidos " + tema)`, **la mayoría devolvió cero resultados**: nadie busca
"péptidos para dormir" como frase, con volumen medible, en este mercado.

Ampliando la búsqueda sin forzar el prefijo "péptidos" sí aparecieron 4
clústeres con volumen real. Los cuatro se cayeron en una compuerta distinta,
tal como debía pasar si el filtro funciona:

| candidato | volumen | compuerta que falló | evidencia |
|---|---:|---|---|
| **testosterona** ("cómo aumentar la testosterona" + variantes) | 14,800+ | **#3 — sin ficha vendible.** El catálogo no vende testosterona; la única coincidencia de búsqueda es Zinc Picolinato (Nutricost, **agotado**) | búsqueda directa en WooCommerce, 0 resultados relevantes en stock |
| **hormona de crecimiento** | 6,600 | **#4 — SERP capturado.** Top-10: Mayo Clinic (pos 2), Wikipedia, MedlinePlus, Elsevier, Clínica Universidad de Navarra, Mass General, KidsHealth — **Mayo Clinic y MedlinePlus, las dos que citaste como línea roja, están ahí las dos** | SERP en vivo, 2026-08-02 |
| **hgh** | 6,600 | **#2 — intención real es transaccional**, no informacional: en el propio top-10 rankea `exomapeptides.mx` con *"Comprar HGH Somatropina en México"* — es la página de producto del competidor, no un artículo. Y PYS tampoco lo vende (compuerta #3 también) | SERP en vivo — Mercado Libre, Amazon y la ficha de exoma ocupan la mitad del top-10 |
| **reforzar sistema inmune** (+ "vitaminas para...") | 140 + 880 | **#4 — SERP capturado** por sistemas hospitalarios y marcas de vitaminas de consumo (Houston Methodist, Quirón Salud, Clínica Alemana, gob.mx, Redoxon) — ninguna tienda de péptidos/suplementos de nicho aparece en ninguno de los dos top-10 | SERP en vivo, 2026-08-02 |

**No fuerzo candidatos débiles para llegar a 6-8.** Es el mismo patrón que ya
documentó `docs/plan-capa-necesidad-pys.md` (96% del volumen medido
inalcanzable o de intención equivocada) — aplicado aquí a landings en vez de
a fichas, con el mismo resultado.

### Lo que sí funciona, y por qué

El patrón ganador de las 6 landings existentes es **"péptidos + objetivo muy
específico y ya cubierto por el catálogo"**, no "objetivo de bienestar
genérico". `docs/data/cluster-pys-clusters.json` (de la auditoría de julio) ya
había medido esto para dos frases: `péptidos gym` / `péptidos para masa
muscular` (910/mes, **0% bloqueado**) — ese territorio ya lo cubre
`/capacidad-fisica-performance/` (ficha IGF-1 LR3). No hay hueco ahí.

**Costo de esta ronda:** ~$0.44 en DataForSEO (keyword research + 5 SERPs en vivo).

---

## b, ronda 2 — rastreo dirigido por compuesto (aprobado, ejecutado)

Para cada uno de los 14 compuestos vendibles: variantes "para qué sirve",
"cómo funciona", "efectos secundarios", "vs [otro del catálogo]", "cómo
reconstituir/almacenar", "protocolo", "dosis". 98 búsquedas dirigidas →
**117 keywords con volumen medible.** Costo: ~$0.30 en `keyword_suggestions`
+ $0.012 en 6 SERPs en vivo. Datos crudos:
`docs/data/fase4b-compuestos-{ideas,serp}.json`.

### Candidata única que pasó las 4 compuertas + los 2 filtros extra

**NAD+ — "qué es el NAD+ y para qué sirve"**

| compuerta | resultado |
|---|---|
| Volumen real medido | **8,100/mes** el término cabeza (`nad para que sirve`); cluster completo sin la variante "resveratrol" ronda 15,000/mes (`para que sirve el nad` 1,900 · `que es el nad y para que sirve` 1,600 · `nad para que sirve en mujeres` 1,600 · `que es nad y para que sirve` 1,300 · `nad suplemento para que sirve` 720 · `nad suplementos para que sirve` 720) |
| Intención | Informacional en las 7 variantes listadas — ninguna con señal de compra (`route_keyword` no las marca transaccionales) |
| Ficha destino | **1131 NAD+, en stock**, con contenido ya fuerte (la distinción "NAD+ parenteral vs. precursores orales" que documenta `docs/fase1-veracidad-pys.md`) |
| Composición del SERP | **Revisada en vivo, 3 variantes distintas — consistente en las 3.** Ninguna tiene Mayo Clinic, MedlinePlus ni NIDDK. Sí aparece `cun.es` (autoridad médica, 1 de 8-10 resultados) — el resto son clínicas de bienestar/longevidad (neolifesalud.com, quironsalud.com, bluehealthcare.es, institutovalencianodeozonoterapia.com) y un sitio de contenido sobre suplementos (blife.mx). **No es un SERP abierto — es un SERP de competidores de nicho, no de autoridad médica inalcanzable.** Esa es justamente la categoría de SERP que una página bien ejecutada puede disputar |
| Filtro extra — canibalización | **Sin riesgo.** Ni PYS ni exoma aparecen en `cluster-pys-ranked.json` (caché histórica) para ninguna variante; tampoco aparecen en las 3 SERPs en vivo revisadas |
| Filtro extra — cobertura de exoma | **Exoma no aparece en ningún SERP revisado.** No hay landing ni ficha suya compitiendo aquí — campo abierto de verdad, no supuesto |

**Advertencia que hay que llevar a la redacción, no a la keyword:** una parte
del volumen del clúster completo (`nad resveratrol para que sirve` 2,900 ·
`para que sirve el nad con resveratrol` 1,000 · `resveratrol nad para que
sirve` 480 ≈ 4,400/mes) es sobre un **producto combinado NAD+/resveratrol de
otras marcas** que la ficha 1131 no vende. Es el mismo error de identidad
molecular que ya documentó el playbook (NMN/NR ≠ NAD+): esa demanda **no
cuenta** para justificar la landing, y el contenido no debe insinuar que el
producto de PYS incluye resveratrol.

### Todo lo demás: descartado con evidencia, no por falta de búsqueda

| candidato | volumen | por qué se descarta |
|---|---:|---|
| Semaglutida — "para qué sirve" | 22,200 | SERP: FDA, MedlinePlus, Cochrane, CUN, cardioteca.com — autoridad médica pura, 3 de 8 |
| Tirzepatida — "para qué sirve" | 12,100 | SERP: MedlinePlus, Cochrane, FDA, Apollo Hospitals, más el sitio oficial de Mounjaro (Lilly) — autoridad médica + marca pharma |
| Glutatión — "para qué sirve y cómo se toma" | 210 (cluster ~1,370) | Confirma el hallazgo ya documentado en el playbook: SERP de **cosmética** (mesoestetic.es, paulaschoice.es) + retail de suplementos (iHerb), no autoridad médica pero tampoco el mercado de PYS |
| BPC-157, TB-500, MOTS-c, Selank, CJC-1295+Ipamorelina, IGF-1 LR3, Sermorelina, Cagrilintida, Timosina Alfa-1, Agua Bacteriostática, Retatrutida | 10-90/mes cada uno | Volumen real pero **insuficiente para sostener una landing propia** — son compuestos de nicho dentro del nicho; ese tráfico ya se atiende bien desde la propia ficha y el blog |

### Propuesta final: 1 candidata, no 6-8

**Solo `NAD+ — qué es y para qué sirve` cumple las 4 compuertas y los 2
filtros.** No relleno la lista — es exactamente el resultado honesto después
de 2 rondas de investigación (bienestar genérico: 0 de 4; por compuesto: 1 de
14). **Nada escrito.** Si apruebas, la landing se redacta con la salvedad del
resveratrol explícita desde el primer borrador, no como corrección posterior.

---

## b, ronda 2 — APROBADA con condiciones (2026-08-02)

Redactada `docs/contenido/landing-nad-que-es-para-que-sirve.html`, verificada
contra las funciones reales del retrofeed (no una reimplementación) vía
`/validate-post` en producción:

- **route_keyword()** confirma "blog" (informacional) para las 4 variantes
  objetivo — ninguna se clasifica como transaccional. Cumple la condición (c).
- **retrofeed_gates() → ok: true.** 1,722 palabras, cero palabra prohibida,
  las 7 citas verificadas RELACIONADAS contra el abstract real de su PMID.
- **Hallazgo durante la verificación de años:** 4 de las 7 citas, copiadas de
  la ficha 1131 asumiendo que ya estaban auditadas, declaraban un año distinto
  al `pubdate`/`epubdate` real de eutils (26785480: 2016→2015 real;
  24786309: 2015→2014 real; 31278280: 2020→2019 real; 29249689: 2019→2018
  real). Corregidas en la landing. **La ficha 1131 publicada todavía tiene
  estos 4 años mal** — no estaban entre las 39 discrepancias que corrigió el
  Bloque A de Fase 2, así que se colaron. Pendiente de un fix mecánico
  idéntico al de esa fase; no aplicado aquí por estar fuera del alcance de
  esta tarea.
- **Bug encontrado y corregido:** `check_url()` (la validación de enlaces,
  separada de `retrofeed_gates`) marcó 3 PMIDs reales como "no existe en
  PubMed" — falso positivo por el mismo bug de caché/reintento que ya se
  había corregido en `_pubmed_record()` pero nunca se aplicó a esta función
  hermana. Corregido y desplegado (commit `54d5ae9`), verificado estable en
  producción.
- **Tensión sin resolver, expuesta en vez de forzada:** `validate_blog_html()`
  exige mínimo 2 fichas distintas enlazadas — una regla pensada para posts de
  blog que tocan varios compuestos. Esta landing, sobre un único compuesto,
  enlaza a 1 (la 1131). Forzar un segundo enlace a una ficha no relacionada
  violaría la misma condición (a) de honestidad. Se deja como excepción
  revisada, igual que la compuerta 5 (molécula exacta) siempre fue asesora y
  no bloqueante.
- Publicada en **borrador** en WordPress para tu revisión — condición (d).

## Conclusión de Fase 4b — hallazgo estructural

De 14 compuestos investigados con rastreo dirigido, **10 tienen volumen de
búsqueda informacional de uno o dos dígitos por mes.** No es un problema de
qué se escribe ni de cómo se escribe: es que el mercado de búsqueda para esos
compuestos, tal como está definido hoy el catálogo, es minúsculo. El techo de
superficie de PYS —cuántas landings de intención puede sostener con evidencia
real, sin inflar la lista— está determinado por el **tamaño del catálogo**,
no por la estrategia de contenido. Ampliar esa superficie es una decisión de
inventario, no de redacción; no se proponen compuestos nuevos aquí.
