# PYS — Clustering de keywords por SERP real (Fase 2)

**Fecha:** 2026-07-30 · **Costo DataForSEO:** $0.57 (de $1.50/día) · **Método:** clustering por
solapamiento de SERP en vivo (≥3 URLs compartidas en top-10), no por similitud léxica ni por KD.

Datos crudos en `docs/data/cluster-pys-*.json`. Scripts reproducibles en `scripts/cluster_pys_*.py`
(los SERPs quedan cacheados: re-correr no vuelve a pagar).

---

## El hallazgo que cambia la estrategia

**El 96% del volumen medido no sirve.** De 358,390 búsquedas/mes en el universo relevante,
**344,550 son inalcanzables o de intención equivocada**. Lo alcanzable son 13,840/mes — pero son
las correctas.

Y el dato que lo enmarca todo:

| | apariciones en top-10 de las 39 keywords |
|---|---|
| **peptidosysuplementos.mx** | **0** |
| exomapeptides.mx | 26 |
| instagram.com | 21 |
| listado.mercadolibre.com.mx | 14 |
| zelara.com.mx | 10 |
| peptide.com.mx | 9 |

PYS es invisible en su propia categoría. No es un problema de volumen ni de contenido: es que no
rankea en ningún SERP de su catálogo.

---

## Las tres trampas de volumen

Las semillas obvias apuntan a números enormes que **no** son de PYS:

**1. GLP-1 cabeza — 250,700/mes — BLOQUEADO**
`semaglutida` (135K, 53% bloqueado), `tirzepatida` (90.5K, 82%). El top-10 es MedlinePlus,
Wikipedia, PLM, Medscape, más marca farmacéutica (Novo Nordisk, Mounjaro) y farmacias. Es un SERP
YMYL de definición médica. Un DR bajo no entra, y aunque entrara, quien busca ahí quiere saber qué
es el fármaco, no comprar un vial liofilizado.

**2. `péptidos` genérico — 33,090/mes — BLOQUEADO por cosmética**
11 de los resultados son Vichy, Lancôme, Estée Lauder y Mesoestetic. En México "péptidos" a secas
es una consulta de **skincare**, no de péptido de investigación. Es la misma palabra para otro
mercado. Perseguirla es traer tráfico que nunca compra.

**3. GLP-1 precio — 59,600/mes — MIXTO, dominado por farmacia**
`semaglutida precio`, `tirzepatida precio`, `semaglutida similares`. El top-10 es Farmacias
Similares, Del Ahorro, Guadalajara y las clínicas de telemedicina (zelara, clivi). PYS no compite
en "dónde consigo Ozempic barato".

---

## Lo que sí es ganable — 13,840/mes

SERP contestable (<30% bloqueado) **y** del negocio correcto. Ordenado por volumen:

| vol/mes | bloq | CPC | cluster | ¿PYS tiene producto? |
|--------:|-----:|----:|---------|----------------------|
| 1,900 | 12% | $0.84 | `ipamorelina` | Sí, solo como combo (2232) |
| 1,710 | 20% | $0.76 | `retatrutida` + `retatrutida precio` | Sí (19) |
| 1,600 | 0% | $0.46 | `agua bacteriostatica` | Sí (799) |
| 1,600 | 11% | $0.40 | `péptidos para bajar de peso` | Categoría GLP-1 |
| 1,000 | 25% | $0.62 | `cjc-1295` | Sí (2232) |
| 910 | 0% | $0.34 | `péptidos gym` + `péptidos para masa muscular` | Categoría |
| 880 | 28% | $2.14 | `mots-c` | Sí (790, 793) |
| 880 | 28% | $0.45 | `tb-500` | Sí, combo (795) |
| 880 | 11% | $0.50 | `péptidos inyectables` | Categoría |
| 780 | 5% | $0.59 | `péptidos mexico` + `péptidos precio` + `comprar péptidos` | Categoría |
| 590 | 12% | $0.16 | `cagrilintida` | Sí (2240) |
| 480 | 12% | $0.58 | `selank` | Sí (1699) |
| 210 | 22% | $0.45 | `bpc 157 precio` | Sí (795) |
| 210 | 14% | $0.10 | `sermorelina` | Sí (2231) |
| 140 | 12% | $1.35 | `bpc-157 y tb-500` | Sí (795) |

Dos observaciones que valen dinero:

- **`ipamorelina` es la keyword individual más grande del set ganable (1,900/mes) y PYS solo la
  vende dentro del combo CJC-1295+Ipamorelina.** Sumada a `cjc-1295` (1,000) son 2,900/mes que hoy
  dependen de una sola ficha combo. Una ficha propia de ipamorelina es la acción más obvia.
- **`mots-c` ($2.14) y `bpc-157 y tb-500` ($1.35) tienen el CPC más alto del set** — señal de que
  ahí sí hay intención de compra con dinero detrás, aunque el volumen sea modesto.

---

## Qué implica para la ejecución

El diagnóstico previo (`pys-competencia-seo-dataforseo`: *gap de ranking, no de contenido*) queda
confirmado y precisado: **PYS ya tiene ficha para 11 de los 15 clusters ganables.** El trabajo no
es escribir contenido nuevo, es hacer que esas fichas entren al top-10 en SERPs que están abiertos.

Prioridad sugerida:

1. **Ficha propia de ipamorelina** (2,900/mes con cjc-1295, hoy sin página dedicada).
2. **Optimizar las 11 fichas existentes** contra su keyword exacta del cuadro — es donde el SERP
   está abierto y PYS aparece en cero.
3. **Página de categoría comercial** para `péptidos mexico` / `péptidos precio` / `comprar péptidos`
   (780/mes, solo 5% bloqueado, y el top-10 es exoma + marketplaces = terreno directamente
   disputable).
4. **Tres piezas de uso/caso** para `péptidos para bajar de peso` (1,600), `péptidos inyectables`
   (880) y `péptidos gym`/`masa muscular` (910) — 3,390/mes de intención informativa-comercial con
   SERP casi limpio.
5. **No perseguir** semaglutida/tirzepatida cabeza ni `péptidos` genérico. El hub `/glp-1/` que ya
   existe sirve para capturar el long-tail de marca, no para pelear la cabeza.

---

## ADENDA 2026-07-30 — Posiciones reales medidas (profundidad 100)

Se midió dónde está PYS de verdad en las 32 keywords ganables. **No hay capa empujable.**

| situación | keywords | volumen |
|---|---:|---:|
| top-10 | **0** | 0 |
| empujable (11-20) | **0** | 0 |
| empujable (21-30) | 2 | 110/mes |
| lejos (31-50) | 3 | 710/mes |
| muy lejos (51+) | 8 | 10,190/mes |
| **fuera del top-100** | **19** | **27,300/mes** |

La mejor posición de PYS en algo con volumen es **28** (`retatrutida precio`, 110/mes). En todo lo
demás está en 47-88 o directamente fuera de las 100. exoma, en las mismas keywords, está en **2-10**.

`ranked_keywords` del dominio lo confirma: PYS rankea 18 keywords (5 en 21-50, 13 en 51+), **cero en
top-10, 0/mes de volumen capturado**. exoma rankea 64 keywords, 30 de ellas en top-10, con
**23,790/mes**.

**Esto invalida la recomendación de "optimizar las fichas existentes" como acción principal.** Un
salto de 88 → 10 no es un ajuste on-page. Y el argumento de autoridad no cierra: exoma tiene la
misma autoridad de dominio que PYS (1 backlink, ya medido el 2026-07-28) y está en el top-10 de
todo. La diferencia es estructural, no de enlaces — **antes de invertir en contenido o enlaces hay
que averiguar por qué las fichas de PYS no compiten** (indexación, tipo de URL, profundidad real del
contenido dentro de `_elementor_data`).

### Lo que la primera pasada se perdió por elegir mal la keyword

| keyword | vol/mes | PYS | exoma | ficha |
|---|---:|---:|---:|---|
| `glutation` | 6,600 | fuera | **—** | 2234 |
| `glutathione` | 6,600 | fuera | **—** | 2234 |
| `retatrutide precio` | 4,400 | 59 | 4 | 19 |
| `tesamorelina` | 3,600 | fuera | 4 | **no lo vende** |

**~~`glutation` / `glutathione` es el hallazgo más limpio del estudio~~ — CORREGIDO 2026-07-30, ver
abajo. Era una lectura equivocada: nadie rankea porque no es el mercado de PYS, no porque esté
libre.**

Las grafías inglesas no ganan siempre (`ipamorelin` 0 vs `ipamorelina` 1,900; `peptides` 6,600 vs
`péptidos` 27,100) pero cuando ganan, la diferencia es brutal: `retatrutide precio` 4,400 contra
`retatrutida precio` 110. Hay que decidirlo keyword por keyword, nunca por regla.

### Huecos de catálogo (demanda medida sin producto que vender)

| keyword | vol/mes | exoma |
|---|---:|---:|
| tesamorelina | 3,600 | 4 |
| kisspeptina | 720 | 10 |
| pt-141 | 590 | 2 |

4,910/mes de demanda que PYS no puede atender hoy. exoma sí.

---

## ADENDA 2 — POR QUÉ EXOMA GANA CON LA MISMA AUTORIDAD

**No es autoridad. Es superficie y arquitectura.** Medido el 2026-07-30 sobre los sitemaps y el
HTML que recibe Googlebot.

| | PYS | exoma | ratio |
|---|---:|---:|---:|
| URLs de contenido | **65** | **345** | **5.3×** |
| Productos | 22 | 95 | 4.3× |
| Blog | 19 | 65 | 3.4× |
| **Compendio (enciclopedia)** | **0** | **130** | **—** |
| Páginas + categorías | 24 | 55 | 2.3× |
| Palabras por ficha | 702–1,757 | 2,950–3,759 | 2–5× |
| Keywords en top-10 | **0** | **30** | — |

### El mecanismo: dos páginas por péptido, no una

exoma tiene **dos URLs por compuesto**:

- `/compendio/mots-c` — informacional, ataca el nombre pelado del péptido
- `/producto/mots-c` — transaccional, ataca la intención de compra

PYS tiene **una sola**, y encima diluida: `/product/mots-c-10mg` con H1
*"MOTS-c 10mg | Péptido Metabolismo y Longevidad México"*. exoma usa H1 `MOTS-c` a secas y slug
`mots-c`. La gente busca "mots-c", no "mots-c 10mg". El H1 de PYS está cargado de keywords y no
coincide exactamente con ninguna query.

### Las tres consecuencias

1. **Cobertura de catálogo.** exoma vende 95 productos, PYS 22. Por eso exoma rankea en
   `tesamorelina` (3,600/mes, pos 4), `kisspeptina` (720, pos 10) y `pt-141` (590, pos 2): tiene el
   producto *y* la página de compendio. PYS no puede competir por demanda que no vende.

2. **Equity interno.** exoma tiene **195 páginas informativas** (130 compendio + 65 blog) apuntando
   a 95 fichas. PYS tiene 38 informativas para 22 fichas. No es que a PYS le falten enlaces
   externos — es que casi no tiene enlaces *internos* que repartir, porque no tiene páginas desde
   dónde enlazar.

3. **Profundidad por página.** En las tres comparables directas exoma tiene 1.8×–5.4× más texto
   visible. El caso extremo: CJC-1295, PYS 702 palabras contra 3,759 de exoma.

### Lo que NO es el problema (descartado con evidencia)

- **No es indexación.** PYS rankea en posiciones 38, 47, 54, 57, 59, 66, 73, 75, 82, 88 — una página
  no puede rankear sin estar indexada. Las fichas están en el índice; simplemente no compiten.
- **No es `meta robots` ni canonical.** Ambos sitios declaran `index, follow` y canonical propio
  correcto. Revisado en las 4 fichas comparadas.
- **No es schema.** PYS tiene más tipos que exoma (le falta solo `BreadcrumbList`).
- **No es la meta description.** Ambos rondan 150-159 caracteres.
- **No es autoridad de dominio.** Ya medido el 2026-07-28: misma autoridad, 1 backlink.

### Qué haría falta para cerrar la brecha

En orden de impacto por esfuerzo:

1. **Página informativa por péptido** (el equivalente al compendio). Es la pieza que PYS no tiene y
   que explica la mitad de la diferencia. 22 páginas, una por producto del catálogo actual.
2. **Desdoblar los combos.** `ipamorelina` (1,900/mes) y `cjc-1295` (1,000/mes) hoy dependen de una
   sola ficha combo. exoma tiene ficha propia para cada uno.
3. **Slugs y H1 al nombre pelado.** `/product/mots-c-10mg` → el H1 debería ser `MOTS-c`, no la
   cadena con dosis y modificadores. (Cambiar slugs exige 301; evaluar caso por caso.)
4. **Profundidad de contenido** en las fichas que ya existen: de ~1,000 a ~2,500-3,000 palabras.
5. **Ampliar catálogo** hacia la demanda medida sin producto: tesamorelina, kisspeptina, pt-141
   (4,910/mes combinados).

**Cuidado con la lectura fácil:** esto no significa "publicar 130 páginas". exoma tardó en
construirlas y muchas serán delgadas. Lo accionable es que la brecha es de *cobertura temática*, no
de enlaces — y eso sí se puede cerrar con trabajo propio, sin depender de conseguir backlinks.

---

## ADENDA 3 — CORRECCIÓN: glutatión NO es oportunidad

SERP medido el 2026-07-30 (`scripts/diag_serp_glutation.py`, $0.008). **La lectura anterior estaba
mal y hay que descartarla.**

| keyword | composición del top-10 | qué se vende ahí |
|---|---|---|
| `glutation` (6,600) | 3 informativo · 5 otro · 1 transaccional | Wikipedia, CUN, BBC, + **skincare** (Paula's Choice, Mesoestetic) |
| `glutathione` (6,600) | 3 informativo · 3 transaccional | **Amazon, iHerb, Walmart — cápsulas orales** |
| `glutation precio` | casi todo transaccional | Amazon, MercadoLibre, Walmart, **Farmacia del Ahorro — cápsulas orales** |
| `glutation inyectable` | 7 otro · 2 transaccional | **clínicas de IV estético** + distribuidores de ampolletas listas |

**Todos los resultados transaccionales son glutatión ORAL en cápsulas** — producto de góndola de
Walmart y Amazon, mercado masivo. PYS vende un **vial liofilizado de 1500mg para reconstituir**. Es
la misma palabra para otro producto y otro comprador, exactamente la misma trampa que `péptidos` =
cosmética.

Y `glutation inyectable`, que es lo más cercano al producto de PYS, tiene un SERP de **clínicas de
sueroterapia y blanqueamiento estético** (Clínica Carrasco "tratamiento con glutatión intravenoso",
Century Medical "razones para recibir una inyección de glutatión"), no de tiendas de péptidos.

**Por qué me equivoqué:** interpreté la ausencia de exoma como campo abierto. Era lo contrario —
**exoma no está ahí porque no es su mercado**. La ausencia del competidor más fuerte de la categoría
en una keyword de 6,600/mes debió leerse como señal de descarte, no de oportunidad.

**Regla que queda:** cuando ningún competidor directo aparece en una keyword de volumen alto,
la hipótesis por defecto es *no es tu mercado*, no *nadie la ha trabajado*. Confirmar siempre con la
composición del SERP antes de priorizar.

---

## Cómo saber si falla

- **Métrica líder:** apariciones de peptidosysuplementos.mx en top-10 de las 15 keywords ganables.
  Hoy: **0/15**. Re-correr `scripts/cluster_pys_fase3_serps.py` (borrando el caché) lo vuelve a medir
  por ~$0.03.
- **Señal de que la tesis está equivocada:** si tras optimizar las fichas siguen sin entrar al
  top-10 en SERPs marcados ABIERTO, entonces el problema no es on-page sino autoridad de dominio, y
  la palanca pasa a ser enlaces (ver `hf-backlinks-strategy`).
- **Ojo con la caducidad:** los SERPs son una foto del 2026-07-30. La composición cambia; re-medir
  antes de invertir en un cluster que se midió hace meses.

---

## Limitaciones de esta corrida

- 39 SERPs muestreados, no las 801 keywords limpias. Los clusters de una sola keyword no están
  validados por solapamiento (no tienen con qué solapar).
- `bpc 157`, `glutation liofilizado`, `nad+ inyectable`, `como reconstituir peptidos` y
  `péptidos vs esteroides` dieron volumen 0 en Google Ads exact-match; probablemente el volumen
  vive en variantes con guion o plural. Vale re-consultarlas con variantes antes de descartarlas.
- `igf-1 lr3` (390) y `thymosin alpha 1` (170) salieron MIXTO 33% — quedaron fuera del cuadro
  ganable por poco; revisables.
- No se midió posición actual de PYS más allá del top-10: puede estar en 11-30 en varias de estas
  y eso cambiaría el esfuerzo estimado (empujar del 15 al 8 no es lo mismo que entrar desde cero).
