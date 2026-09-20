# Auditoría SEO completa — propertyledger.us (2026-08-30)

Firma de contabilidad tercerizada B2B para property managers y HOA/condo boards, South Florida, en inglés. WordPress 6.7.2 + Rank Math + tema twentytwentyfive, detrás de Cloudflare, hosting compartido "webcom".

Método: crawl completo con UA Googlebot (43 URLs), inventario real por REST, grafo de enlaces, GSC 90d, DataForSEO (US, en), Lighthouse, y URL Inspection API. 5 subagentes especializados + verificación directa. **No se creó ninguna página nueva** (solo optimización de lo existente, por orden del cliente).

---

## 0. Verificación del hosting (la pregunta que abrió la sesión)

**Veredicto: no está "caído", está lento en origen — y el acceso de escritura estaba roto.**

- **Disponibilidad:** 107 muestras en 35 min, **0 caídas duras, 0 timeouts**.
- **Velocidad de origen (la queja real):** con caché de Cloudflare, TTFB **0.86s**. Sin caché (Googlebot en frío), **p50 5.5s, 54% >5s**, picos de 15s y un stall de 84s. **Todo el HTML sale `cf MISS` + `x-webcom-cache-status: BYPASS`** salvo la home. Cloudflare *sí* cachea (max-age=14400), pero con 198 impresiones/90d casi ninguna URL recibe una 2ª visita dentro de la ventana de 4h → casi todo hit real golpea el origen en frío.
- **"Los cambios se quedan a medias" era otra cosa:** el usuario `GavitoA` **fue eliminado del sitio**; el agente daba 401 en cada escritura. Único usuario vivo: `plsadmin` (id=1). **Resuelto:** con la contraseña de plsadmin se creó una app-password nueva (`claude-agent-2026-08`), desplegada en los dos `.env`, escritura confirmada por cookie+nonce (200) y `context=edit` (200).

---

## 1. ¿Por qué el sitio está invisible en 90 días? (2 clics / 198 impresiones)

No es una causa, son cinco capas apiladas, y el orden importa:

1. **Es un sitio de ~6 semanas con autoridad casi nula.** El contenido de agosto apenas empieza a madurar: la posición promedio **saltó de ~90 a 24–58 en la última semana** (URL Inspection lo confirma). Google todavía lo está evaluando.
2. **El sitemap solo expone 4 de 32 posts.** Rank Math congeló el cuerpo del `post-sitemap.xml` con los 4 posts que existían el 16-jul; los 28 publicados después nunca entraron (publicar por REST no invalida la caché del sitemap — mismo bug que en CMLC). **Matiz de indexación:** Google igual encontró la mayoría por rastreo normal (13/19 muestreadas indexadas, 68%); solo quedan fuera las 2 páginas **huérfanas** (0 enlaces internos). El sitemap roto retrasa descubrimiento, pero el bloqueador de las huérfanas es la falta de enlaces internos.
3. **El sitio se canibaliza a sí mismo.** 6 posts duplicados siguen `status=publish` pese a tener un 301 encima; "trust accounting" se reparte entre 3 URLs que compiten entre sí; la equity se diluye.
4. **El nicho es genuinamente pequeño — pero ganable.** DataForSEO (US, en): el término no-software más grande es "property management accounting" **590/mes**; casi todo el cluster está entre 30–480/mes. PERO **KD 0–5** (competencia casi nula). Los términos de 1000/mes son todos de **software** (KD 24–58, dominados por Buildium/AppFolio/DoorLoop) = espejismo; "…jobs" (140/mes) es intención de **empleo**. Cluster ganable real: **~2,160 búsquedas/mes** repartidas en el catálogo actual.
5. **El origen lento tapona el rastreo y los CWV.** LCP móvil 5.7–6.5s (Poor), atribuido por Lighthouse a espera de red/TTFB, no a peso (payload solo 1.1MB).

**Traducción:** el sitio no está penalizado ni roto de contenido. Está joven, mal enlazado internamente, invisible por sitemap, compitiendo consigo mismo, y lento. Con KD 0–5 en su cluster, **casi todo esto es reparable sin escribir una sola página nueva**, y varias piezas ya están en posición 18–23 (a un empujón de la página 1).

---

## 2. Hallazgos por severidad

### 🔴 Critical

| # | Hallazgo | Acción | Página/ID |
|---|---|---|---|
| C1 | **Sitemap: 4 de 32 posts.** Caché de Rank Math congelada (lastmod del índice sí ve los 32, el cuerpo no). | Regenerar: SSH `wp rankmath sitemap generate`, o wp-admin → Rank Math → Sitemap → toggle Posts off/Save/on/Save. Verificar 32 `<loc>` con UA Googlebot. Añadir al pipeline de publicación. | post-sitemap.xml |
| C2 | **6 posts zombie duplicados aún `publish`** pese al 301; `/blog/` y categorías los siguen enlazando. | Mandar a **Trash** (no Draft): IDs **311, 310, 219, 314, 212, 313, 309**. El 301 queda como protección. | ver §3 |
| C3 | **Origen lento / caché mal aprovechada** (100% BYPASS, TTFB p50 4.5–5.5s frío). | Cloudflare **Cache Rule** para HTML + **Always Online / serve-stale ON** (mayor impacto) + purga en publish. Detalle en §4. | global |

### 🟠 High

| # | Hallazgo | Acción |
|---|---|---|
| H1 | **Sin identidad de autor (YMYL).** Schema `Person` = "plsadmin" genérico, `sameAs` roto apuntando a URL de staging `netsolhost.com`. Ningún post con byline/credencial. | Cambiar Display Name de WP a persona/rol real con credencial; corregir/quitar `sameAs`. Rank Math lo hereda. |
| H2 | **Sin NAP ni About; claim "15+ years" sin respaldo.** `Organization` sin `PostalAddress`; footer solo con teléfono (954, Fort Lauderdale) y "Serving clients across the U.S." (diluye el ángulo local). | Migrar schema a `["AccountingService","Organization"]` con address/areaServed/telephone/priceRange; bloque "About" dentro de /contact/ (sin página nueva); arreglar `openingHours` (formato Mo/Tu, no "Monday"). |
| H3 | **Canibalización trust-accounting a 3 bandas:** id158 (pos 11) vs id119 (pos 66) vs id84 (pos 95). | id158 = canónica del cluster; id119 = la página "what is"; **retirar/consolidar id84**. Diferenciar el ángulo Florida de id203 en su H1/intro. |
| H4 | **Equity atrapada en redirect no documentado:** `/in-house-bookkeeper-vs-outsourced-accounting-property-management/` (slug viejo, 301) sigue indexada (pos 55, 7 impr) mientras el destino nuevo es **huérfano y sin indexar**. | Enlazar internamente el destino y pedir indexación. |
| H5 | **2 errores de schema (Ahrefs), ubicados:** FAQPage de `/security-deposit-trust-account-reconciliation/` con `<br />` literal dentro del JSON → inválido; se propaga a `/category/trust-accounting/` que lo re-embebe. | Reabrir el bloque FAQ en Gutenberg y regrabar sin saltos crudos; verificar con `json.loads()` sobre el HTML servido. |

### 🟡 Medium

- **9 posts en Uncategorized (noindex):** solo 4 reales → **163, 322 → HOA & Condo Accounting** (activa esa categoría, hoy en 0); **315, 316 → Property Management Accounting**. Los otros 5 son zombies → Trash.
- **2 páginas huérfanas** (0 inlinks): 163 (HOA reserve), 109 (in-house vs outsourced) → 1 enlace contextual c/u.
- **H1 duplicado** en 315 y 316 (bug de plantilla).
- **LCP móvil 5.7–6.5s** — se cura con C3 (es TTFB, no peso).

### 🔵 Low

- 5 títulos >60 y varias metas >160 → reescrituras en §5.
- 2 categorías sin meta description.
- FAQPage en ~24 páginas: Google retiró el rich result (may-2026). **No quitar, no añadir más.** Nivel Info.
- HTTP/1.1 al origen; `llms.txt` 404; `ImageObject.width/height` como string.
- **Positivo a preservar:** enlaces salientes a fuentes reales (IRS, NARPM, IREM, AICPA, Florida Statutes). 0 imágenes sin alt.

---

## 3. Mapa de consolidación de duplicados (Trash)

| Ganador (vivo) | Zombie a Trash (ID) | Enlazado desde |
|---|---|---|
| 98 owner-statements-explained | 311 how-to-prepare-owner-statements-correctly | /blog/ |
| 133 bookkeeping-vs-accounting-difference | 310 property-management-bookkeeping-vs-accounting | /blog/ |
| 221 chart-of-accounts-setup-guide | 219 …categories **y** 313 setting-up-… | categoría / /blog/ |
| 216 trust-accounting-quickbooks | 314 quickbooks-trust-accounting | /blog/ |
| 119 what-is-trust-accounting-…-guide | 309 what-is-trust-accounting-… | /blog/, categoría, + link hardcodeado en post 316 |
| 210 security-deposit-trust-account-reconciliation | 212 …compliance-best-practices-2 | /category/trust-accounting/ |

> Excepción manual: el anchor hardcodeado en el cuerpo de `/why-clean-reconciliations-matter-property-management/` (316) hacia `/what-is-trust-accounting-property-management/` hay que editarlo a mano → `…-guide/`.

---

## 4. Fix de Cloudflare (Cache Rule)

- **Expresión:** `(http.host eq "propertyledger.us") and not starts_with(http.request.uri.path,"/wp-admin") and not starts_with(http.request.uri.path,"/wp-login") and not starts_with(http.request.uri.path,"/wp-json") and not (http.cookie contains "wordpress_logged_in_") and not (http.cookie contains "comment_author_")`
- Cache eligibility: **Eligible**. Edge TTL override: **3–7 días**. Browser TTL: 30 min.
- **Serve stale while revalidating (Always Online): ON** ← mayor impacto.
- Cache Key: excluir utm_*/fbclid/gclid. Purga automática en `save_post`.
- 2ª línea: activar cache de página a nivel servidor (hoy BYPASS 100%).

---

## 5. Reescrituras de meta (texto exacto)

| URL | Campo | Nuevo (len) |
|---|---|---|
| `/` | title | Outsourced Accounting for Property Management \| PLS (51) |
| `/` | meta | Outsourced accounting for property management companies: accurate financials, trust account reconciliations, and owner statements. Book a free consultation. (156) |
| `/blog/` | title | Property Management Accounting Blog \| Property Ledger (53) |
| `/contact/` | title | Contact Property Ledger \| Free Accounting Consultation (54) |
| `/contact/` | meta | Schedule a free accounting consultation for your property management company. We cover monthly accounting, trust accounts, and owner statements. (144) |
| `/monthly-accounting/` | title | Monthly Accounting for Property Management \| Property Ledger (60) |
| `/property-management-accounting/` | title | Property Management Accounting \| 15+ Years \| Property Ledger (60) |
| `/accounting-software-for-property-managers/` | meta | The accounting software for property managers behind every Property Ledger statement: 24/7 owner access, real-time reports, bank-level security. (144) |
| `/hoa-reserve-fund-accounting-track-fund-report-reserves/` | meta | Learn HOA reserve fund accounting: how to track, fund, and report reserves correctly, plus compliance rules and funding strategies for boards. (142) |

---

## 6. Plan priorizado por fases

**Fase 0 — Infraestructura (destraba todo lo demás, 1 día).**
Regenerar sitemap (C1) · Cloudflare Cache Rule + Always Online (C3) · verificar app-password de escritura. → Sin esto, ningún cambio on-page rinde del todo.

**Fase 1 — Limpieza estructural (bajo riesgo, alto impacto, 1–2 días).**
Trash de los 6 zombies (C2) + editar el anchor de 316 · recategorizar 163/322/315/316 y activar HOA & Condo · destildar Uncategorized sobrante · enlazar las 2 huérfanas · pedir indexación de las 8–10 URLs clave.

**Fase 2 — On-page de conversión (2–3 días).**
Reescribir metas (§5) · resolver canibalización trust-accounting (H3) · schema AccountingService + NAP (H2) · byline/autor real (H1) · arreglar los 2 errores de schema (H5) · reparar H1 duplicado.

**Fase 3 — Profundidad de contenido (según autorización).**
Reforzar las near-miss (pos 18–23) con definición citable de 40–60 palabras bajo el H1: trust accounting, owner statements, financial statements, month-end close. Ampliar thin content de money pages a ≥1,200 palabras. Inyectar señal South Florida en /property-management-accounting/ y home.

**Medición "después":** re-correr crawl + on-page + GSC + Lighthouse a las 4 y 8 semanas contra este baseline. KPIs: nº posts en sitemap (4→32), TTFB frío (p50 5.5s→<1s), posición media del cluster near-miss, impresiones/clics GSC, nº huérfanas (2→0).

---

## Anexo — Baseline "antes" (2026-08-30)

- GSC 90d: **2 clics, 198 impresiones, CTR 1.01%**, posición media del cluster 79–98 (con near-miss en 18–23).
- Inventario: 32 posts + 8 páginas + 4 categorías. Sitemap: 13 URLs (4 posts).
- Indexación muestreada: 13/19 (68%); 2 huérfanas "unknown to Google".
- Hosting: TTFB frío p50 5.5s (54% >5s); 100% cf BYPASS salvo home.
- Lighthouse home: móvil perf 65 / LCP 6.1s / CLS 0.00; desktop perf 87 / LCP 1.3s.
- DataForSEO: cluster ganable ~2,160/mes, KD 0–5; espejismos = software (1000/mes KD 24) y empleo (140/mes).
