# Ahrefs — qué se puede sacar con la cuenta gratuita (AWT)

Fecha: 2026-08-27 · Workspace: "Antonio gavito's workspace" · Plan: Ahrefs Free (AWT)

## 1. Qué SÍ y qué NO desbloquea el plan gratis

| Herramienta | Estado | Alcance real |
|---|---|---|
| **Site Audit** | ✅ Completo | Crawl propio, 170+ chequeos, export CSV, Page/Link/Structure explorer, Patches |
| **Site Explorer** | ✅ Solo dominios verificados | Backlinks, refdomains, anchors, organic keywords (**con volumen, KD, CPC, intent, entities**), top pages, best by links, internal links |
| Web Analytics / Bot Analytics | ✅ Gratis | Analítica sin cookies + qué bots te rastrean |
| Opportunities | ✅ Gratis | Atajos a "low-hanging fruit" (pos 4–15), canibalización, redirects a reclamar |
| Internal link opportunities | ⚠️ Vacío | Existe, pero necesita keywords rankeando. En PYS da 0 resultados |
| **Keywords Explorer** | ❌ De pago | Muro total |
| **Content gap / Link intersect** | ❌ De pago | Muro total |
| **GSC Insights** | ❌ De pago | Muro total |
| Rank Tracker | ❌ De pago | "Not available on a Free plan" |
| Content Explorer, Brand Radar, SMM | ❌ De pago | — |
| Historial de métricas | ❌ De pago | Solo modo "Metrics"/"Years" sin filtros |

**Site Explorer sobre dominios ajenos: bloqueado.** `exoma.mx` → *"You can only check verified domains and their subdomains on a free plan."*

## 2. Corrección: ahrefs.com/site-audit NO espía dominios ajenos

Esa URL es la landing de marketing. Al meter `exoma.mx` redirige a `/signup?plan=awt` y, ya dentro, sigue exigiendo verificación de propiedad.

**La vía real para competidores son las herramientas públicas de `ahrefs.com/free-seo-tools`** (funcionan sin verificar nada):

| Tool | Qué da de CUALQUIER dominio |
|---|---|
| **Backlink Checker** | DR, nº backlinks, nº dominios, % dofollow + **top 20 backlinks con DR, anchor y URL destino** |
| **Website Traffic Checker** | Tráfico orgánico, valor $, tendencia 6 meses, top países, top keywords |
| Website Authority Checker | DR |
| **Broken Link Checker** | Enlaces rotos hacia/desde cualquier sitio (broken link building) |
| SERP Checker | Top 10 de cualquier keyword en cualquier país |
| Keyword Generator / KD Checker | Ideas + volumen, dificultad |
| AI Visibility / AI Mode / AI Overviews Tracker | Menciones de marca en LLMs |
| **Ahrefs SEO Toolbar** (extensión) | DR/UR de cualquier sitio **mientras navegas** + overlay en la SERP. Gratis con cuenta free |

> El Toolbar es el desbloqueo más grande: convierte cualquier SERP en un mini Site Explorer de competidores.

---

## 3. HALLAZGOS ACCIONABLES

### 3.1 🔴 Ataque de spam de enlaces en 5 dominios propios

Ahrefs etiqueta los dominios basura con `SPAM`. En **nodarishub.com**: de los 50 primeros dominios de referencia (ordenados por DR), **49 están marcados SPAM**. Solo `huggingface.co` es legítimo.

Red: `itxoft-*.site`, `fiverr-*-seo-*.site`, `rankyour.website`, decenas de `*.shop` de "SEO services", `rglinks.org`, `backlinkshop.site`… Todos con *first seen* entre **4 jul y 26 ago 2026** — la ráfaga sigue activa.

**Filtrando por dofollow: de 195 dominios, solo 3.**

| Dominio | DR | Links | Veredicto |
|---|---|---|---|
| `kravetpet.com` | 2 | 7 | ✅ Cliente real |
| `magnosbi.com` | 2 | 4 | ✅ Cliente real |
| `kaila.biz` | 17 | 1 | 🔴 SPAM — único candidato a disavow |

**Conclusión:** el "crecimiento" de +56 dominios/mes es ruido nofollow — inofensivo pero engañoso. La autoridad real de nodarishub son **2 enlaces de clientes**. Mismo patrón en el dashboard: propertyledger +72, cmlc +76, tlaollinwaldorfcholula +65 (397 dominios en un sitio de colegio Waldorf), arcademotorsmx +59.

> ⚠️ No usar el conteo de referring domains como métrica de progreso en ninguno de estos sitios sin filtrar dofollow primero.

### 3.2 🟠 PYS — 34 problemas técnicos vivos (Site Audit, crawl 21 ago)

Health 90 · 219 URLs internas · **64 con errores**

Indexables (lo que importa):
- **42 páginas con `<meta description>` DUPLICADA** ← el bug más grande y más barato de arreglar. Firma clásica de Rank Math + tema/LiteSpeed emitiendo ambos.
- **5 páginas con múltiples H1**
- **80 páginas indexables enlazan a redirecciones** ← contradice la auditoría previa de "0 hops". Verificar si son redirects nuevos.
- 5 páginas con un solo enlace interno dofollow entrante (casi huérfanas)
- 9 meta description muy largas · 8 muy cortas · 4 vacías · 2 títulos largos
- **19 páginas indexables fuera del sitemap** + 11 redirects 3XX dentro del sitemap
- 5 imágenes rotas · 4 páginas con imagen rota
- 13 páginas lentas · 40 CSS demasiado grandes
- 1 error de validación de schema.org
- 0 imágenes sin alt ✅

### 3.3 🟡 PYS — AhrefsBot está siendo bloqueado

En el índice web de Ahrefs, de 332 páginas rastreadas de PYS: **27.7% son 4XX "otros errores de cliente" (92 páginas)** y 6.6% son 404. Pero el crawler propio de Site Audit solo encontró 6 errores 4xx en 673 URLs.

La discrepancia apunta a que **el edge (LiteSpeed/hCDN) responde 403 a AhrefsBot** pero no al crawler autenticado del proyecto. Mismo síntoma ya documentado en propertyledger. Efecto: los datos públicos de PYS en Ahrefs están degradados.

### 3.4 🟢 Raditech — 3 keywords KD 0 a un empujón de página 1 alta

Raditech rankea 7 keywords en MX. Volumen y KD salen gratis vía Site Explorer:

| Keyword | Vol/mes | KD | CPC | Pos | URL |
|---|---|---|---|---|---|
| **ris pacs** | 150 | **0** | $0.54 | **7** | `/sistema-pacs-ris/` |
| monitores medicos | 90 | **0** | $0.40 | **8** | `/monitores-medicos-radiologia/` |
| ris/pacs | 40 | **0** | — | 5 | `/sistema-pacs-ris/` |
| pacs mexico | 20 | **0** | $0.50 | 10 | `/teleradiologia/` ⚠️ |
| raditech (marca) | 70 | 0 | — | 1 | home |

- Todo KD 0 y en el fondo de la página 1 → el mejor ROI disponible del portafolio.
- ⚠️ **`pacs mexico` rankea con `/teleradiologia/`, no con `/sistema-pacs-ris/`** → desajuste consulta↔página; confirma el diagnóstico previo del cuello de botella.
- El tráfico cayó de ~245 a **84** (−161) en 30 días.

### 3.5 🟢 Raditech — prospectos de enlaces reales (robados a radiocare.mx)

`radiocare.mx`: DR 5, 670 backlinks, 450 dominios, **solo 7-8% dofollow**. Su perfil está inflado con basura comprada (`bhs-links-*.xyz`, `rankwagon.shop`, `seogrowthresults.shop`, `dr-90-rank-forge-department.store`…). **No copiar eso.**

Lo que sí vale la pena replicar:

| Donante | DR | Cómo lo consiguieron | Replicable para Raditech |
|---|---|---|---|
| `medium.com/@Radiocare` | 94 | Blog propio en Medium | ✅ Trivial |
| `crunchbase.com` | 91 | Perfil de empresa | ✅ Gratis |
| `colombia.com` | 68 | Cita editorial a su post de cáncer silencioso | ✅ Vía PR de contenido |
| `healthcaretechoutlook.com` | 64 | Premio "Top Radiology Solution 2025" | ✅ Postularse |
| `glassdoor.com.mx` | 63 | Perfil de empleador | ✅ Gratis — encaja con el ángulo de reclutamiento de radiólogos |
| `centromedicoabc.com` | 56 | Citado junto a MedlinePlus e INCMNSZ en su revista digital | ⭐ El mejor |
| **`actualpacs.com`** | 49 | **Caso de éxito publicado por su proveedor PACS** | ⭐⭐ **Raditech es reseller de Medsi → pedir el caso de éxito equivalente** |
| `startupeable.com` | 45 | Directorio de startups LatAm | ✅ Gratis |
| `actualmed.com` | 12 | Página de "Referencias" | ✅ |

### 3.6 Estado del portafolio (dashboard)

| Sitio | DR | Ref.dom | Tráfico org. | Keywords | Site Audit |
|---|---|---|---|---|---|
| raditech.mx | 0 | 2 | 84 (−161) | 8 | Health 99 |
| nodarishub.com | 9 | 195 | 0 | 0 | **Sin crawl** |
| propertyledger.us | 0 | 208 | 0 | 0 | **Sin crawl** |
| centromedicolasconchas.com | 0 | 203 | 2.6 | 3 | Health 100 |
| arcademotorsmx.com | 2 | 380 | 1.3 | 2 | **Sin crawl** |
| tlaollinwaldorfcholula.com | 2 | 397 | 0 (−59) | 2 | Health 94 |
| peptidosysuplementos.mx | 2 | 2 | 0 | 0 | Health 90 |

**3 proyectos nunca se han auditado** (nodarishub, propertyledger, arcademotors) — valor gratis sin usar.

---

## 4. Qué hacer con esto

**Inmediato (gratis, alto impacto)**
1. Correr Site Audit en nodarishub, propertyledger y arcademotors — nunca se ha hecho.
2. Arreglar las 42 meta description duplicadas de PYS.
3. Instalar el **Ahrefs SEO Toolbar** — es el único modo de ver DR/UR de competidores en esta cuenta.
4. Meter al sitemap las 19 páginas indexables de PYS que faltan.

**Corto plazo**
5. Raditech: empujar `ris pacs` (pos 7) y `monitores medicos` (pos 8) a top 3. KD 0.
6. Raditech: reapuntar `pacs mexico` de `/teleradiologia/` a `/sistema-pacs-ris/`.
7. Raditech: perfiles gratis en Crunchbase, Glassdoor y Startupeable + pedir caso de éxito a Medsi.
8. Investigar el 403 a AhrefsBot en PYS.

**Rutina**
9. Backlink Checker gratis mensual sobre cada competidor → cosechar donantes.
10. Nunca reportar "referring domains" sin filtrar dofollow en estos 5 dominios.

## 5. Gotchas encontrados

- Las URLs directas de reportes (`/site-audit/<id>/all-issues`, `/gsc-insights`) dan **404**; hay que navegar por el sidebar. Las rutas buenas son `/site-audit/<id>/issues`, `/gsc/project/<id>/overview`, `/site-audit/<id>/link-opportunity`.
- Al cambiar un filtro en Site Explorer hay que pulsar **"Show results"**; si no, la tabla no se actualiza.
- El índice de Ahrefs es flojo para sitios pequeños de MX: `exoma.mx` devuelve **0 tráfico orgánico** (DataForSEO le veía mucho más). Para nichos MX chicos, DataForSEO sigue siendo la fuente buena; Ahrefs gana en **backlinks y detección de spam**.
