# Capa de contenido por NECESIDAD — peptidosysuplementos.mx

**Fecha:** 2026-07-28 · **Estado:** plan para aprobación, nada publicado todavía
**Insumo:** `Keywords-por-necesidad-PyS.xlsx` (119 kw / 13 ejes)
**Verificación:** DataForSEO Labs (MX/es, `location_code 2484`) + 12 SERPs reales + inventario WooCommerce/WP + perfil de enlaces. Costo total de verificación: ~$0.66 USD.

---

## 0. Respaldo — HECHO antes de tocar nada

`backups/pys-20260728-123503/` — 19 posts, 25 páginas, 21 productos, 8 categorías de producto, 12 categorías WP. Incluye contenido crudo **y** meta de Rank Math (`rank_math_title`, `_description`, `_focus_keyword`, `_seo_score`, `_schema_FAQPage`).

> ⚠️ Limitación conocida: la API rechazó `status=any` con app-password (PYS escribe por JWT, no app-password). **El respaldo cubre solo contenido publicado; los borradores no están respaldados.** Si hay borradores que importen, hay que sacarlos con JWT antes de la Fase 1.

---

## 1. Lo que cambia el plan (leer antes que nada)

El diagnóstico del brief es correcto en el síntoma pero incompleto en la causa. Tres hechos medidos:

**a) PYS casi no rankea, y la canibalización no es la razón principal.**
El dominio aparece en **18 keywords** del top-100. **Cero en top-10.** Mejor posición: 26.

**b) La autoridad no es el cuello de botella.** Comparativa de perfil de enlaces:

| Dominio | Dom. referentes | Keywords org. | Tráfico est. |
|---|--:|--:|--:|
| **peptidosysuplementos.mx** | **1** | 18 | 44 |
| exomapeptides.mx | 1 | 67 | **4,145** |
| peptide.com.mx | — | 70 | 2,057 |
| clivi.com.mx | 723 | 1,204 | 31,316 |
| gnc.com.mx | 736 | 10,222 | 904,580 |

Exoma tiene **la misma autoridad que PYS** (1 dominio referente) y saca 94× más tráfico: 28 keywords en top-10, 6 en top-3. Con enlaces no se explica. Se explica por **qué tipo de URL apunta a qué intención**.

**c) Dónde se está perdiendo el dinero, medido:**

| Keyword | Vol | KD | URL de PYS | Pos | URL de Exoma | Pos |
|---|--:|--:|---|--:|---|--:|
| retatrutide precio | 4,400 | 0 | *post* `/retatrutide-precio-guia-completa…` | 36 | *producto* `/producto/retatrutida-15mg` | **2** |
| retatrutide precio méxico | 1,000 | 0 | *post* (mismo) | 26 | *producto* (mismo) | **3** |
| retatrutide mexico | 2,400 | 0 | *post* (mismo) | 43 | *producto* (mismo) | **4** |
| retatrutide donde comprar | 390 | 0 | *producto* `/product/retatrutida-30mg` | 63 | *producto* (mismo) | **4** |

8,190 búsquedas/mes con **KD 0** donde un competidor sin autoridad está en top-4 con su ficha de producto, y PYS manda un blog. Y la ficha de producto de PYS que debería ganarlas tiene **Rank Math score = 10/100**.

**Conclusión operativa:** el mayor retorno inmediato no está en la capa nueva de contenido, está en arreglar la asignación URL↔intención de lo que ya existe. La capa por necesidad se construye encima, no en lugar de.

---

## 2. Verificación de volúmenes (punto 4 del brief)

**Agregado: el Excel es sólido — 403,430 reales vs 404,800 declarados (97%).** Pero hay desviaciones individuales que sí cambian decisiones:

| Keyword | Excel | Real | Δ |
|---|--:|--:|--:|
| qué tomar para bajar de peso rápido | 12,100 | **210** | −98% |
| inyección para bajar de peso | 9,900 | **27,100** | +174% |
| como eliminar grasa visceral | 390 | **1,600** | +310% |
| pastillas para bajar de peso sin receta | 880 | **2,900** | +230% |
| proteína para aumentar masa muscular | 6,600 | 4,400 | −33% |
| pastillas para bajar de peso naturistas | 4,400 | 2,900 | −34% |
| dietas para aumentar masa muscular | 2,400 | 1,600 | −33% |
| pastillas para quitar el hambre farmacia | 1,300 | 880 | −32% |
| bajar de peso rápido | 6,600 | 4,400 | −33% |

9 keywords no devolvieron dato; 3 eran artefactos de acento (se recuperaron), 6 no tienen volumen medible.

**Advertencia sobre la columna de dificultad.** La "Dificultad (SD)" del Excel y el KD de DataForSEO no coinciden y **ninguna de las dos sirve como filtro aquí**: `pastillas para bajar de peso` sale SD 35 / KD 8, y su top-10 real es Mayo Clinic, NIDDK, Cigna y MedlinePlus. Ninguna métrica de dificultad captura el requisito de autoridad YMYL. **Por eso el filtro que usé es la composición real del SERP, no el KD.**

### Keywords del Excel bloqueadas por regla del proyecto

6 keywords (4,030 vol/mes) contienen la palabra prohibida por `CLAUDE.md`, que no puede aparecer en títulos, metas ni contenido. **No se puede optimizar para una keyword que no se puede escribir** — quedan fuera por decisión ya tomada, no por SEO:
`pastillas para bajar de peso f_______ guadalajara` (2,400), `pastillas para quitar el hambre f_______` (880), `pastillas para bajar de peso f_______ del ahorro` (590), `… sin receta f_______ guadalajara` (590), `medicamento para bajar de peso f_______ guadalajara` (140), `pastillas para quitar el hambre f_______ sin receta` (140).

---

## 3. Filtro SERP: qué es ganable y qué no

Saqué el top-10 real de 12 keywords objetivo. El patrón es nítido y parte el Excel en dos:

**SERP MÉDICO — no ir (aunque el KD diga que es fácil):**

| Keyword | Vol | Quién manda en el top-10 |
|---|--:|---|
| resistencia a la insulina | 90,500 | NIDDK, Mayo, CDC, Elsevier, Beyond Type 1 |
| resistencia a la insulina tratamiento | 3,600 | Elsevier, SciELO, Apollo, NIDDK, Medwave |
| inyecciones para bajar de peso | 27,100 | VeryWell, Columbia Surgery, BHF, MedlinePlus, NIDDK, Mayo, Cochrane |
| medicamento para bajar de peso | 14,800 | Mayo, NIDDK, Cigna, Cleveland Clinic, MedlinePlus |
| pastillas para bajar de peso | 40,500 | Mayo, NIDDK, Cigna, MedlinePlus, gob.mx |

Son SERPs YMYL puros. PYS tiene 1 dominio referente. Además, para competir ahí habría que escribir contenido de **tratamiento médico**, que es exactamente la exposición regulatoria que una tienda de péptidos de investigación no debe asumir. Doble razón para no ir.

**SERP COMERCIAL — sí ir:**

| Keyword | Vol | KD | Quién manda | Veredicto |
|---|--:|--:|---|---|
| quemador de grasa | 12,100 | 0 | GNC #2, MercadoLibre #4, iHerb, Amazon, suplementosgym | ganable |
| grasa visceral | 12,100 | 0 | clínicas + neoactives (marca de suplementos) | ganable |
| supresor de apetito | 480 | 0 | Amazon #2, iHerb #4, HSN #5, MercadoLibre #8 | ganable |
| inyección para bajar de peso **precio** | 320 | 18 | tiendas y cadenas + clivi + MercadoLibre — **CPC $2.27** | ganable |
| vitaminas para aumentar masa muscular | 320 | 0 | MercadoLibre #2, naturitas, tuasaude | ganable |
| como eliminar grasa visceral | 1,600 | 1 | clínicas/blogs, sin autoridad dura | ganable |

**El head term es médico, la cola comercial no lo es.** `inyecciones para bajar de peso` (27,100) es intocable; `inyección para bajar de peso precio` (320, CPC $2.27) tiene un SERP de tiendas. Ese es el punto de entrada al eje, no el head.

### Reparto del Excel

| Bucket | Vol/mes | % | kw |
|---|--:|--:|--:|
| DESCARTE — SERP médico YMYL (eje resistencia a la insulina completo) | 150,800 | 37% | 11 |
| DESCARTE — head terms médicos de peso | 118,800 | 29% | 13 |
| **GANABLE** | **96,420** | **24%** | **77** |
| Bajo valor — dieta/ejercicio/comida, sin producto destino | 33,380 | 8% | 12 |
| Bloqueado por regla del proyecto | 4,030 | 1% | 6 |

**El 66% del volumen del Excel está en SERPs que PYS no puede ganar hoy.** No es un defecto de la investigación — el Excel midió demanda, que es real; lo que faltaba era el filtro de viabilidad.

### Lo que el Excel no trae y sí conviene (aportación)

El Excel excluyó a propósito el vocabulario de marca, y con eso se saltó la franja donde PYS **sí** rankea: la necesidad expresada en vocabulario de producto. Todo esto es KD 0–4:

| Keyword | Vol | KD | Intención |
|---|--:|--:|---|
| péptidos | 27,100 | 0 | informacional |
| qué son los péptidos | 5,400 | 0 | informacional |
| péptidos para bajar de peso | 1,600 | 1 | **transaccional** |
| péptidos inyectables | 880 | 0 | informacional |
| péptidos gym | 590 | 0 | transaccional |
| péptidos méxico | 590 | 0 | transaccional |
| péptidos para masa muscular | 320 | 0 | transaccional |

~36,500 vol/mes en KD 0–4, con intención de necesidad y en el idioma donde el dominio ya compite. Exoma rankea su **home** en pos 60 para `péptidos para bajar de peso`; una página dedicada lo gana.

---

## 4. Orden de canibalización — un solo dueño por término

Estado real: casi toda la canibalización es **latente** (URLs solapadas que no rankean todavía), con **un caso vivo medido** (retatrutide). La regla que aplico:

> **Transaccional** (precio, comprar, méxico, mg) → **ficha de producto**
> **Comparativo** (X vs Y) → página de comparativa
> **Informacional** (qué es, cómo funciona) → **un solo** post
> **Estudio/dato** → post de estudio

### Retatrutida — 6 URLs, el caso vivo

| URL | Score | Decisión |
|---|--:|---|
| `/product/retatrutida-30mg` (prod 19) | **10** | **DUEÑO** de `retatrutide precio` · `retatrutide méxico` · `retatrutide donde comprar`. Subir a ≥80. |
| `/precio-de-retatrutida-en-mexico/` (pág 1046) | 87 | **301 → producto 19.** Duplica exactamente la intención del producto. |
| `/retatrutide-precio-guia-completa…/` (post 1647) | — | Slug de precio pero focus kw `retatrutida como funciona`. **Re-slug a `/retatrutida-que-es-como-funciona/` + 301.** Dueño de la intención informacional. |
| `/retatrutide-peptido-triple-agonista…/` (post 2092) | — | Solapa con 1647. **Fusionar en 1647 + 301.** |
| `/retatrutide-triumph-1/` (post 1476) | 88 | **Conservar.** Intención distinta (estudio clínico). |
| `/retatrutida-vs-tirzepatida/` (pág 2119) | — | **Conservar.** Comparativa. |

> ⚠️ **Riesgo de secuencia:** el post 1647 es la **única URL del sitio que rankea decentemente** (pos 26). Cambiarle el slug mueve el único activo con tracción. Por eso el re-slug va **después** de que la ficha de producto tome posición, no antes.

### Resto

| Grupo | Situación | Decisión |
|---|---|---|
| BPC-157: posts 2128 y 1677 | Dos posts, misma molécula, misma intención | **Fusionar 1677 → 2128 + 301** |
| Tirzepatida: pág 1729 (86) vs prods 1525/1531 | Hub vs fichas | Página = hub comercial (`tirzepatida méxico`), fichas = `tirzepatida precio` / por mg. Hub enlaza a fichas. |
| Semaglutida: pág 1750 (85) vs prods 1689/1518 | Igual | Mismo criterio |
| MOTS-c 793 (score 17) / 790 (66) · Tirzep 1525/1531 | Presentaciones distintas | No es canibalización. Diferenciar focus kw **por mg**. |
| Longevidad: pág 26 vs post 1675 | Solapan | Pág 26 = hub comercial; post 1675 = artículo de evidencia |
| Productos 2230, 2231, 2232, 2234, 2240 | Sin score, sin optimizar | Optimizar a ≥80 |

> **Nota sobre `landing.peptidosysuplementos.mx` — verificado 2026-07-28, sin acción pendiente.**
> No existe ningún registro DNS del subdominio (ni A ni CNAME; los NS del dominio son de Hostinger). Y **ya no está en el índice de Google**: `site:landing.peptidosysuplementos.mx` devuelve cero resultados; `site:peptidosysuplementos.mx` devuelve 30 URLs y ninguna es del subdominio; en `peptidos gym` (95 orgánicos) y `peptidos mexico` (100 orgánicos) tampoco aparece.
> Las 4 keywords que figuraban a su nombre (`peptides` 6,600 · `peptidos mexico` 590 · `peptidos gym` 590 · `péptidos para masa muscular` 320) **quedan libres para el dominio principal** y ya están asignadas al Eje D.
> ⚠️ **Lección de método:** el `ranked_keywords` de DataForSEO es una instantánea histórica, no el SERP actual — reportó el subdominio en posiciones 56–95 cuando Google ya lo había soltado. Para afirmar que algo está indexado, confirmar con consulta `site:` en vivo.
| `landing.peptidosysuplementos.mx` | ✅ **CERRADO 2026-07-28 — no requiere acción** | Ver nota abajo |

---

## 5. Mapa de contenido — eje → pilar → artículos → producto

Prioridad = SERP ganable × intención comercial. **No** volumen bruto.

### FASE 0 — Reasignar los hubs que YA existen (0 contenido nuevo)

El sitio ya tiene 7 páginas hub. Están redactadas en vocabulario de producto ("Péptidos para X") y apuntan a keywords sin volumen medido. Reasignarlas cuesta casi nada y es lo primero:

| Página | Focus kw actual | Focus kw nuevo (medido) | Vol | KD |
|---|---|---|--:|--:|
| `/perdida-de-peso/` (2109) | cómo bajar de peso | ✔ ya correcto — falta optimizar | 14,800 | 6 |
| `/acelerar-el-metabolismo/` (23) | acelerar el metabolismo (320) | **como acelerar el metabolismo** | 1,900 | 2 |
| `/reparacion-celular/` (24) | reparacion celular, recuperacion fisica | **recuperación muscular** | 320 | 0 |
| `/longevidad/` (26) | longevidad (sin volumen) | **envejecimiento saludable** | 1,300 | 28 |
| `/capacidad-fisica-performance/` (643) | capacidad fisica, biohacking… | **rendimiento deportivo** | 320 | 0 |
| `/suplementos-en-mexico-2/` (1166) | suplementos en mexico | **suplementos deportivos** | 1,600 | 0 |
| `/peptidos-en-mexico/` (1551) | peptidos en mexico | **péptidos méxico** + `comprar péptidos` | 590 | 0 |
| post 2201 (qué son los péptidos) | — sin focus kw | **qué son los péptidos** (2ª: `péptidos` 27,100) | 5,400 | 0 |

### FASE 2 — Ejes nuevos, TIER 1 (SERP comercial verificado)

**Eje A · Quema de grasa / composición corporal** — 19,400 vol ganable
| | |
|---|---|
| **Pilar comercial** | `/quemadores-de-grasa/` — `quemador de grasa` (12,100 · KD 0 · transaccional) |
| **Pilar informacional** | `/grasa-visceral/` — `grasa visceral` (12,100 · KD 0) |
| **Artículos** | `como eliminar grasa visceral` (1,600·KD1) · `cómo quemar grasa abdominal rápidamente` (1,600·KD0) · `quemar grasa abdominal` (1,000·KD0) · `quemar grasa abdominal mujeres` (170) · `bajar grasa corporal` (210) |
| **Producto destino** | MOTS-c 10mg/40mg · Cagrilintida · Tirzepatida |

**Eje B · Control de apetito / saciedad** — 2,000 vol ganable, la mejor coincidencia producto↔necesidad
| | |
|---|---|
| **Pilar** | `/supresor-de-apetito/` — `supresor de apetito` (480 · KD 0 · **transaccional**) |
| **Artículos** | `como quitar el hambre` (720·KD0) · `pastillas para quitar el hambre` (590) · `control de apetito` (40) · `suplementos para quitar el hambre` (50) |
| **Producto destino** | **Cagrilintida** (análogo de amilina = saciedad; hoy 0 ventas) · Semaglutida · Tirzepatida |
| **Nota** | Las variantes de este eje con la palabra prohibida (1,440 vol) quedan fuera |

**Eje C · Masa muscular / rendimiento** — 41,370 vol ganable, el eje más grande de los viables
| | |
|---|---|
| **Pilar** | `/suplementos-para-masa-muscular/` — `como ganar masa muscular` (2,900·KD3) + `suplementos para masa muscular` (170·KD0) |
| **Artículos** | `vitaminas para subir de peso y masa muscular` (3,600) · `alimentos para aumentar masa muscular` (2,400·KD15) · `dietas para aumentar masa muscular` (1,600) · `masa muscular en mujer` (1,600·KD15) · `pérdida de masa muscular` (1,600) · `proteínas … piernas y glúteos mujeres` (1,900) |
| **Herramienta** | Calculadora de composición corporal → `índice de masa muscular` (12,100·KD32). Ya existe la calculadora de dosis: mismo patrón, imán de enlaces |
| **Producto destino** | IGF-1 LR3 · CJC-1295+Ipamorelina · Sermorelina · BPC-157+TB-500 |

**Eje D · Péptidos por necesidad** — el puente (no está en el Excel) — ~36,500 vol en KD 0–4
| | |
|---|---|
| **Pilar** | `/peptidos-para-bajar-de-peso/` — `péptidos para bajar de peso` (1,600 · KD 1 · **transaccional**) |
| **Artículos** | `péptidos inyectables` (880·KD0) · `péptidos gym` (590·KD0) · `péptidos para masa muscular` (320·KD0) |
| **Refuerzo** | post 2201 toma `qué son los péptidos` (5,400·KD0) y `péptidos` (27,100·KD0) |
| **Producto destino** | Fichas GLP-1 y de performance directamente |
| **Por qué primero** | Es el único eje que combina necesidad + KD 0 + vocabulario donde el dominio ya compite. Exoma rankea aquí con su home; una página dedicada lo gana. |

### FASE 3 — TIER 2 (encuadre delicado)

**Eje E · Inyectables por precio** — 11,500 vol ganable, CPC alto
| | |
|---|---|
| **Pilar** | `/inyecciones-para-bajar-de-peso-precio/` — `inyección para bajar de peso precio` (320 · KD 18 · **CPC $2.27**) |
| **Artículos** | `cuál es la mejor inyección para bajar de peso` (390) · `nombre de inyecciones para quemar grasa abdominal` (480·KD14) · `medicamento para bajar de peso inyectado` (590) |
| **Producto destino** | Semaglutida · Tirzepatida · Retatrutida |
| **Límite duro** | **No** atacar el head `inyecciones para bajar de peso` (27,100): SERP 100% médico. Contenido comparativo de costos y formatos, sin afirmaciones terapéuticas. |

**Eje F · Control de peso comercial** — refuerza `/perdida-de-peso/` (2109) y la categoría `/metabolismo-activo/` con `control de peso` (2,400·KD9·CPC $1.92).

### Ejes menores — usar categorías existentes, no crear páginas

Articulaciones (1,080), Antiedad (1,300), Recuperación (520), Energía (230). Se resuelven optimizando `/reparacion-celular/`, `/longevidad/` y las categorías de producto.

> **Hueco de catálogo detectado:** `suplementos para articulaciones` tiene 1,000 vol / KD 0 y **PYS no tiene producto articular** (lo más cercano es BPC-157+TB-500). Es una oportunidad de catálogo, no de contenido.

---

## 6. Orden de ejecución

| # | Acción | Por qué en este orden | Riesgo |
|--:|---|---|---|
| **0** | ✅ Respaldo (hecho) · sacar borradores por JWT | Nada se toca sin respaldo | — |
| **1** | Ficha **Retatrutida 30mg** (prod 19): score 10 → ≥80, dueña de `retatrutide precio/méxico/donde comprar` | 8,190 vol · KD 0 · el peer sin autoridad está en top-4. Mayor ROI del sitio. | Bajo |
| **2** | 301 `/precio-de-retatrutida-en-mexico/` → producto 19 | Elimina el duplicado directo de intención | Medio — la página tiene score 87 |
| **3** | Optimizar fichas restantes a ≥80: MOTS-c 40mg (17), IGF-1 (10), Selank (13), Semaglutida/Tirzepatida (56–59), y los 5 productos nuevos sin score | Mismo patrón que #1 en todo el catálogo | Bajo |
| **4** | **Fase 0** — reasignar focus kw de los 7 hubs existentes | Contenido cero, keywords medidas | Bajo |
| **5** | Fusiones/301: BPC-157 (1677→2128), retatrutida (2092→1647) | Consolida señales antes de crear nada nuevo | Medio |
| ~~6~~ | ~~Decidir `landing.peptidosysuplementos.mx`~~ ✅ **cerrado — ya sin DNS y fuera del índice** | — | — |
| **7** | **Eje D** — `/peptidos-para-bajar-de-peso/` + 3 artículos + post 2201 | Primer eje nuevo: KD 0–4, donde el dominio ya compite | Bajo |
| **8** | **Eje A** — `/quemadores-de-grasa/` + `/grasa-visceral/` + 4 artículos | 24,200 vol KD 0, SERP de tiendas | Bajo |
| **9** | **Eje B** — `/supresor-de-apetito/` + 3 artículos → Cagrilintida | Mejor coincidencia producto↔necesidad del catálogo | Bajo |
| **10** | **Eje C** — `/suplementos-para-masa-muscular/` + 5 artículos + calculadora | El eje viable más grande | Bajo |
| **11** | Re-slug post 1647 → `/retatrutida-que-es-como-funciona/` + 301 | **Después** de que la ficha tome posición | **Alto** — es la única URL con tracción |
| **12** | **Eje E** — inyectables por precio | El de mayor exposición regulatoria, al final y con revisión | Alto (contenido) |
| **13** | Medir a 30/60 días y decidir la siguiente tanda | — | — |

### Estado de ejecución — 2026-07-28

**Pasos 1–5 ejecutados y verificados en vivo.** Respaldo previo en `backups/pys-20260728-123503/`.

Además, con profundidad tipo competidor (~2,000 palabras, evidencia citada, FAQ schema):

| Ficha | Focus kw | Vol | KD | Antes → después |
|---|---|--:|--:|---|
| Retatrutida 30mg (19) | retatrutide | — | 0 | 1,166 → 2,560 pal |
| Semaglutida 5mg (1689) | **semaglutida** | 135,000 | 0 | ~370 → 2,142 pal |
| Tirzepatida 30mg (1525) | **tirzepatida** | 90,500 | 4 | ~370 → 2,062 pal |
| Glutatión 1500mg (2234) | **glutation** | 33,100 | 6 | ~280 → 1,900 pal |
| Picolinato de zinc (1154) | **picolinato de zinc** | 12,100 | 0 | ~390 → 1,839 pal |

Y en una segunda tanda, las 9 fichas restantes **con volumen medible**: NAD (4,400), Omega 3 (3,600), agua bacteriostática (1,600), DIM (1,000), MOTS-c (880), complejo B (590), Selank (480), IGF-1 LR3 (390), BPC-157+TB-500 (210). Todas pasaron de ~370 a 1,575–1,925 palabras.

**Resultado: 14 de 21 fichas con contenido profundo.** Las 7 restantes (793, 1518, 1531, 2230, 2231, 2232, 2240) se quedan en el nivel base porque no tienen volumen medible; las de presentación alternativa además conviene dejarlas cortas para que canalicen hacia la ficha principal de su molécula.

Citas verificadas antes de publicar: STEP-1 (NEJM 2021, DOI 10.1056/NEJMoa2032183), SURMOUNT-1 (NEJM 2022, DOI 10.1056/NEJMoa2206038), retatrutide fase 2 (NEJM 2023, DOI 10.1056/NEJMoa2301972), glutatión (PMID 21875351 + PMC4536296), zinc picolinato (Barrie et al., *Agents Actions* 1987, PMID 3630857), NAD/nicotinamida ribósido (Nature Communications 2018), omega-3 (PMC8413259 + PMC10184047), DIM (AACR CEBP 2017), MOTS-c (Lee et al., *Cell Metabolism* 2015).

**Dónde NO había cita verificable:** Selank, IGF-1 LR3, BPC-157 y TB-500 no tienen ensayos clínicos de fase avanzada. En vez de inventar referencias, esas fichas declaran explícitamente que la evidencia es preclínica y enlazan la literatura indexada en PubMed. Es lo honesto y además diferencia de la competencia de la categoría.

**Corrección de dato:** la ficha 795 decía «10mg» de cada péptido en el cuerpo mientras el nombre del producto dice 5mg. Corregido a 5mg.

### Eje D — PUBLICADO 2026-07-28

| URL | Focus kw | Vol | KD | Palabras | Enlaces entrantes |
|---|---|--:|--:|--:|--:|
| `/peptidos-para-bajar-de-peso/` (2323) | peptidos para bajar de peso | 1,600 | 1 | 1,882 | 5 |
| `/peptidos-inyectables/` (2325) | peptidos inyectables | 880 | 0 | 1,709 | 3 |
| `/peptidos-para-masa-muscular/` (2327) | peptidos para masa muscular | 320 | 0 | 1,607 | 2 |

**Cambio de estructura respecto al plan:** el plan preveía piezas separadas para «péptidos gym» (590) y «péptidos para masa muscular» (320). Al mirar los SERP reales resultó que devuelven prácticamente el mismo top-10 —con la **misma URL de MercadoLibre en el #2 de ambas**—, así que Google las trata como una sola intención. Se unificaron en una página; crear dos habría sido fabricar canibalización el día uno, justo lo contrario del objetivo del proyecto.

**Limitación conocida:** los enlaces entrantes salen de páginas planas (2109, 2102, 2201) y de 4 fichas de producto. Las 3 páginas hub construidas con Elementor (`/peptidos-en-mexico/` 1551, `/capacidad-fisica-performance/` 643, `/reparacion-celular/` 24) **no se pudieron enlazar por API**: la escritura de `_elementor_data` devuelve 200 y persiste, pero la página sigue renderizando lo anterior. Detalle en [[pys-paginas-elementor-vs-plano]] de la memoria del proyecto. **Añadir esos 3 enlaces a mano desde el editor de Elementor** cuando se pueda; no bloquea nada, las páginas ya no son huérfanas.

**Corrección al paso 5:** la fusión `2092 → 1647` **no se hizo**, y no debe hacerse. Al abrir ambos posts resultó que no son duplicados: 1647 es un artículo de *precio* y 2092 uno informacional de 3,610 palabras. La duplicación real de 1647 es contra la ficha de producto, y eso se resuelve en el paso 11.

**Decisión de método:** no se cambiaron los slugs de producto pese a que Rank Math penaliza «focus kw en URL». El competidor que rankea #2 en `retatrutide precio` lo hace con slug en español y sin la palabra «precio». La evidencia del SERP pesa más que el checklist del plugin.

**Nota sobre `rank_math_seo_score`:** no sirve como criterio. Solo lo recalcula el editor de wp-admin; ninguna edición por REST lo actualiza. Verificar factores on-page contra el HTML renderizado. Ver [[pys-fichas-elementor-faq-schema]] en la memoria del proyecto.

**Volumen de trabajo:** 6 páginas pilar nuevas + ~19 artículos de soporte + ~15 optimizaciones de activos existentes.

---

## 7. Guardarraíles de nicho salud (punto 5)

Aplican a **toda** pieza nueva; sin esto no se publica:

- **Sin promesas médicas.** Nada de "cura", "elimina", "garantiza", "resultados en X días", ni cifras de pérdida de peso como promesa. Los datos clínicos se citan como **hallazgos de estudio**, con nombre del estudio y población, no como resultado esperable.
- **Sin encuadre de tratamiento.** No se escribe "tratamiento para la resistencia a la insulina" ni equivalentes: eso es lo que exige el SERP médico que ya descartamos, y es la exposición regulatoria a evitar.
- **Supervisión profesional explícita** en toda pieza que toque peso, glucosa o apetito.
- **Evidencia enlazada** a fuente primaria (PubMed/DOI), no a blogs.
- **Naturaleza del producto** declarada con el encuadre habitual del sitio.
- **Palabra prohibida y frase de envío/refrigeración:** no aparecen. Regla de `CLAUDE.md`, sin excepción.
- **PTM Novo:** cero CTA cruzado. Son empresas independientes.
- **Rank Math ≥80** por pieza: focus kw en título/H1/URL/primer párrafo/meta, densidad válida, ≥1 enlace interno al producto destino y ≥1 externo a evidencia, alt en imágenes, meta 150–160 car., schema FAQPage.
  - Recordatorio técnico: `rank_math_*` **no** persiste por el campo `meta` de `/wp/v2/*` — va por `POST /wp-json/rankmath/v1/updateMeta`. En productos, el schema FAQ va como meta `rank_math_schema_FAQPage` vía `wc/v3`.

---

## 8. Decisiones que necesito de ti antes de ejecutar

1. **301 de `/precio-de-retatrutida-en-mexico/` (score 87) al producto.** Es la jugada correcta por intención, pero se sacrifica una página bien optimizada. ¿Procedo, o prefieres conservarla como hub que enlaza al producto?
2. ~~`landing.peptidosysuplementos.mx`~~ — ✅ **resuelto 2026-07-28**: sin DNS y fuera del índice. No requiere acción.
3. **Eje E (inyectables por precio):** es el de mayor CPC y mayor exposición. ¿Lo incluimos o lo dejamos fuera de esta tanda?
4. **Alcance de la primera tanda:** ¿ejecuto pasos 1–5 (arreglos, sin contenido nuevo) y medimos, o sigo de corrido hasta el paso 10?
