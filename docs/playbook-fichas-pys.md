# Playbook — optimizar una ficha de PYS contra exoma

Metodología fija. Se aplica igual en cada ficha. La fase 4 (retrofeed) es
obligatoria y **no es opcional**: cada punto de esa lista salió de un error real
cometido en la sesión del 2026-07-30.

---

## Fase 0 — Línea base (antes de tocar nada)

Registrar en `docs/data/rundown-pys-baseline.json`:
posición actual, palabras, H1, número de secciones, y los mismos datos del
competidor. **Sin línea base no hay forma de saber si funcionó.**

```bash
py -3 scripts/cluster_pys_fase6_posiciones.py
```

## Fase 1 — Comparación 1 a 1

```bash
py -3 scripts/plan_pys_stock_actual.py          # tabla global
py -3 scripts/analiza_contenido_bpc157.py       # adaptar URL por ficha
```

Extraer del competidor: estructura completa de H2/H3, conteo de palabras,
términos frecuentes que la ficha de PYS no usa, y **secciones que ellos tienen y
nosotros no**.

## Fase 2 — Fuentes primarias

**Nunca reutilizar las afirmaciones del competidor sin verificarlas.** Sus PMIDs
se comprueban en PubMed antes de citarlos:

```bash
# título, revista, año y autores reales
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<PMIDS>&retmode=json
```

Buscar además **lo que el competidor declara no tener**. En BPC-157, exoma
escribió "no se dispone de datos farmacocinéticos"; existía un estudio completo
(PMID 36588717). Ese hueco es la ventaja competitiva más barata que hay.

## Fase 3 — Redacción

Plantilla de monográfico (13 secciones, la que usa exoma y funciona):

1. Presentación y precio · 2. Identidad y composición · 3. Mecanismo de acción ·
4. Farmacocinética · 5. Evidencia científica · 6. Comparativa directa (**tabla**) ·
7. Reconstitución (**tabla de volúmenes**) · 8. Estabilidad y conservación ·
9. Perfil de seguridad · 10. Estado regulatorio · 11. Historia y desarrollo ·
12. FAQ (10+ preguntas) · 13. Referencias

**Objetivo: superar al competidor en palabras Y en secciones cubiertas.**
Las tablas son la mejora más barata: casi nadie las pone y son lo más útil.

**H1 = nombre pelado del compuesto.** El `rank_math_title` conserva las keywords.

---

## Fase 4 — RETROFEED (obligatorio, antes de publicar)

Cada pregunta corresponde a un error realmente cometido. Si alguna falla, parar.

| # | Verificación | Error que previene |
|---|---|---|
| 1 | ¿Verifiqué **autores, revista y año** de cada referencia en PubMed? | Se inferieron 3 autores y 2 años estaban mal |
| 2 | ¿La keyword objetivo tiene el **volumen que creo**, medido? | Se muestreó `glutation liofilizado` (0) en vez de `glutation` (6,600) |
| 3 | ¿El **SERP es del mercado correcto**? ¿Qué se vende ahí de verdad? | `glutation` = cápsulas orales de góndola; `péptidos` = cosmética |
| 4 | Si el competidor **no aparece**: ¿es oportunidad o señal de descarte? | Se leyó la ausencia de exoma como campo abierto; era "no es su mercado" |
| 5 | ¿Estoy citando estudios de **la molécula exacta**? | Tβ4 completa (43 aa) ≠ TB-500 (fragmento de 7 aa) |
| — | *(#5 es aviso, NUNCA bloqueo automático — ver nota abajo)* | |
| 6 | ¿Aparece la **palabra prohibida** o la frase de refrigeración en transporte? | Reglas absolutas del `CLAUDE.md` |
| 7 | ¿Alguna afirmación clínica **sin fuente**? | Contenido YMYL sin respaldo |
| 8 | ¿Superé al competidor en palabras **y** en secciones? | Igualar no basta para desbancar |
| 9 | ¿Los **marcadores de verificación** son texto plano, sin etiquetas HTML? | Un marcador con `</u>` nunca casa contra el texto visible y dispara un rollback falso |
| 10 | ¿Estoy **quitando** algo bueno que la ficha ya tenía? | En la 19 el borrador eliminó las cifras de eficacia que la versión previa ya reportaba bien encuadradas |

**Trampa específica de la competencia:** exoma afirma en su ficha de retatrutida que la actividad sobre GIP-R es «atenuada». El paper que citan (PMID 35985340) dice literalmente lo contrario: *«balanced GCGR and GLP-1R activity but **more** GIPR activity»*. **Verificar siempre contra el abstract, nunca contra su redacción.**

---

### Lecciones de la auditoría de veracidad (2026-07-31/08-01)

Cuatro hallazgos que cambian cómo se opera esta fase, no solo qué se corrige.

**1. Las instrucciones no validan, las comprobaciones sí.** El prompt del blog
decía textualmente "NO inventes URLs — usa solo URLs que sepas que existen", y
el redactor inventó 9 URLs de fda.gov de todos modos (docs/fase1-veracidad-pys.md).
Una instrucción en el prompt es una petición al modelo, no una garantía; solo
una comprobación por HTTP (o eutils, para PubMed) after-the-fact cierra el
hueco. Ningún texto de instrucción sustituye a una compuerta ejecutable.

**2. Toda compuerta necesita control negativo.** Un verde sin un caso de
prueba que DEBA fallar no significa nada — significa, como mucho, que la
compuerta no se rompió *esta vez*. El caso real: la compuerta de años de las
fichas reportó "0 discrepancias" en 129 citas porque un regex mal escrito
(`[^<.]` excluía el punto de "et al.") nunca matcheó ninguna cita; las 129
cayeron por un `fallback` con campos vacíos, y las comparaciones tenían
guardas del tipo `if ref["anio"] and anio and ...` que saltaban en silencio
cuando el campo llegaba vacío. "0 discrepancias" era, en realidad, "0
comparaciones intentadas" — y se reportó como éxito. La regla que se sigue de
esto, aplicada ahora en `web.py` (`ejecuta_controles_negativos`): cada
sub-compuerta trae un caso sintético que **debe** fallar (un PMID inexistente,
un año que solo coincide con la fecha de indexación MEDLINE, una cita de
"sinagogas" para una afirmación sobre Epitalon, la palabra prohibida, una
cifra clínica sin ninguna fuente); si algún caso no falla, la compuerta se
marca ROTA y el resto del pipeline se niega a evaluar contenido real hasta que
se arregle. Un campo vacío al parsear se reporta como fallo de parseo, nunca
como "sin discrepancia".

**3. Citar la fecha de indexación MEDLINE en vez de la de publicación es un
error sistemático a vigilar.** De 39 años mal citados en las 14 fichas, 33
(87%) coincidían **exactamente** con `History[medline]` de PubMed — la fecha
en que el registro terminó de indexarse en la base MEDLINE, que suele caer
meses o más de un año después de la publicación real (impresa o epub). No es
invención: el año existe de verdad en el registro de PubMed, solo que en el
campo equivocado para citar (ninguna convención de citación —Vancouver, APA—
usa la fecha de indexación). La compuerta de año debe comparar **solo** contra
`pubdate` (impreso) o `epubdate`, nunca contra `history[medline]`.

**Nota sobre la #5 (molécula exacta):** no puede ser una compuerta dura
automática — depende de cómo encuadre la frase, y eso exige lectura humana.
Caso real: el detector marcó 3 citas de Tβ4 completa en la ficha 795 (que
vende TB-500) como sospechosas; leídas, el propio texto explicita la
distinción tres veces ("TB-500 no es timosina beta-4 completa... no es
extrapolable ni a TB-500 ni a la combinación") — era exactamente la
verificación correcta, no un error. Un bloqueo automático la habría rechazado
por hacer bien lo que pide esta misma fase. Además, el título de un paper no
basta para juzgar la molécula: en la ficha 1128 (IGF-1 LR3), dos citas cuyo
título solo dice "IGF-1" (sin "LR3") resultaron ser, leído el abstract
completo, genuinamente sobre LR3 — el compuesto administrado en el experimento
solo se nombra dentro del abstract, no en el título. Juzgar por título es
juzgar con evidencia incompleta.

**4. El diagnóstico de la skill `claude-seo` es generador de hipótesis, no de
conclusiones.** Acumula tres hallazgos que resultaron falsos al medirlos:
metas sobrelargas, la ubicación real del `reviewedBy` en el schema, y que las
5 páginas `/category/*` de PYS estaban "rotas" (responden HTTP 200; el
problema real es que son finas y redundantes entre sí, no que estén caídas —
ver `docs/superficie-pys-vs-exoma.md`). Ninguna de las tres se ejecuta sin
medición propia primero.

**5. Cachear un fallo transitorio convierte un hipo de red en un bloqueo
permanente — el veredicto de una compuerta NUNCA debe cachearse en estado
ROTO.** Al desplegar la compuerta de tema con la clave real (2026-08-01), el
control negativo seguía marcando la compuerta ROTA incluso después de
corregirse el placeholder. Causa: `_pubmed_record()` cacheaba en memoria
*cualquier* resultado, incluido un fallo transitorio (una excepción de red
puntual dejaba el registro con título vacío), y `ejecuta_controles_negativos()`
cacheaba ese veredicto ROTO como definitivo. Una única llamada fallida —de la
propia primera prueba del control, antes del fix— envenenó esa entrada para el
resto de la vida del proceso: el sitio se negó a validar cualquier contenido
real hasta que se corrigió el código y se redesplegó. Verificado con
`esummary`/`efetch` en aislamiento: no era un problema de red ni de
rate-limit, era la caché. Fix: solo se cachea un resultado que sí trajo datos;
si algo falla, el siguiente intento reintenta desde cero en vez de repetir el
veredicto viejo.

**Corolario: los controles negativos hay que correrlos contra producción, no
solo en local.** Este bug específico no se manifestaba en local — ahí la clave
de Anthropic era un placeholder y el control fallaba por esa razón,
enmascarando el bug de caché de abajo. Solo apareció al correr el control con
credenciales reales, en el proceso real de Railway, con su propio ciclo de
vida en memoria. Un control negativo que solo se ha visto pasar en local no
está verificado — el proceso de producción tiene caches, procesos concurrentes
y variables de entorno que el entorno local no reproduce.

**6. Un bug de robustez corregido en una función se busca en TODAS las que
hacen la misma clase de llamada, no solo en la que falló.** `check_url()`
(la validación de enlaces) tenía exactamente el mismo defecto que ya se había
corregido en `_pubmed_record()` para `retrofeed_gates`: una sola llamada a
eutils sin reintento, que ante un timeout puntual marcaba un PMID real como
"no existe en PubMed". Nunca se replicó el fix a la función hermana hasta que
la landing NAD+ (Fase 4b, 2026-08-02) lo disparó de nuevo, con 3 PMIDs
verificados manualmente como falsos positivos. Regla: cuando se arregla un
bug de reintentos/caché de fallos, se audita el resto del archivo por el mismo
patrón de llamada (`requests.get` a eutils sin retry, en este caso), no solo
el punto donde se manifestó.

**Dato a favor del propio sistema:** los 4 años mal citados que arrastraba la
ficha 1131 (PMID 26785480, 24786309, 31278280, 29249689 — ninguno de los 39
que corrigió el Bloque A de Fase 2) los encontró **la compuerta 1, al validar
contenido nuevo que citaba los mismos PMIDs**, no una auditoría dedicada. Es
la compuerta funcionando exactamente como se diseñó: no hace falta acordarse
de re-auditar todo cada vez — basta con que cualquier contenido nuevo que
toque esas citas pase por retrofeed_gates() para que el error salga a la luz.

**7. Mínimo de enlaces internos: la regla depende del tipo de contenido, no
es un número fijo.** `validate_blog_html()` exige mínimo 2 fichas distintas
enlazadas — pensada para artículos de blog que tocan varios compuestos. Al
redactar la landing NAD+ (monocompuesto, Fase 4b) esa regla no encajaba:
forzar un segundo enlace a una ficha no relacionada solo para satisfacer el
número **es en sí mismo una violación de la regla de relevancia** que el
resto del sistema protege. Regla explícita, no caso especial: el mínimo de
**2** aplica a blog multi-compuesto; una **landing monocompuesto** (o
cualquier contenido cuyo alcance real cubra un solo compuesto vendible) tiene
mínimo **1** enlace, a su ficha destino. Un segundo enlace forzado no cuenta
como cumplimiento — cuenta como el mismo error que esta regla existe para
prevenir.

**8. Un conteo de verificación siempre reporta cuántos elementos examinó, no
solo cuántos fallaron — es la misma lección de la #2, con una instancia nueva
y más cara.** Fase 2 (2026-08-01) corrigió 41 años mal citados y reverificó
"129 citas, 0 discrepancias". Era cierto **solo sobre el subconjunto que su
regex podía ver**: el formato de lista bibliográfica
(`<li><em>Título</em> Revista, año. PMID: n.</li>`). Esa regex es ciega a las
citas que aparecen **inline, en prosa dentro del cuerpo** (`(Revista, año ·
PMID n)`), que citan los mismos PMID con su propio año declarado — y que
Fase 2 nunca examinó. El 2026-08-02, un parser que sí barre todo el
documento encontró **33 discrepancias adicionales, las 33 inline, en 10 de
las 14 fichas**, con el mismo sesgo sistemático (+1 año) que ya se había
diagnosticado y dado por resuelto. Confirmado por comparación de las dos
corridas (mismo campo `pubdate`/`epubdate`, mismo criterio; el diff de Fase 2
para la 1131 muestra que sí corrigió la lista de referencias y dejó intactas
las mismas citas repetidas en el cuerpo) — no es un cambio de criterio, es
cobertura incompleta, exactamente el patrón del regex de "et al." de la
lección 2. **Regla: todo reporte de verificación debe declarar el
denominador** ("N discrepancias de M examinadas"), nunca solo el numerador.
"0 fallos" sin decir cuántos se examinaron es indistinguible de "0
examinados" — y esa ambigüedad fue, literalmente, la causa raíz dos veces en
esta misma fase. Aplicado y verificado: los 33 se corrigieron con el mismo
mecanismo (backup + Elementor/plano + verificación en vivo) y la re-corrida
final confirma **0 discrepancias de 254 citas examinadas** en las 14 fichas
(`scripts/fase4c_reaudita_corrige_anios.py`).

**9. Schema en PÁGINAS (no fichas, no productos): el `<script>` embebido en
el contenido es el único mecanismo que funciona.** Al añadir el bloque
`reviewedBy` + FAQPage a la landing NAD+ (Fase 4b, 2026-08-03):
`rankmath/v1/updateSchemas` devuelve HTTP 200 con cuerpo `[]` pero **no
persiste nada** — verificado hasta despachando `updateSchemas` directo en el
store de React del propio editor de Rank Math (`wp.data.dispatch('rank-math')`)
y guardando con el botón real; al recargar, el schema seguía sin estar. Causas
de fondo, confirmadas desde el Schema Generator de la UI: **FAQ es función
PRO** (su radio button en el selector de tipos enlaza a `rankmath.com/pricing`)
y **`MedicalWebPage` ni siquiera es un tipo del generador** (no está en la
lista de 20 tipos disponibles). El mecanismo que sí funciona, verificado en
vivo: un `<script type="application/ld+json">` embebido directo en el
`content` de la página. A diferencia de `description` de productos vía
`wc/v3` (que SÍ lo borra — ver Fase 5, publicación), `wp/v2/pages` **no
sanea `<script>`** del contenido: sobrevive el guardado y renderiza en el
front-end tal cual. Mismo principio que el inyector PHP de fichas
(`pys-medical-reviewer` en `wp_head`), solo que aquí va en el body vía
contenido en lugar de un hook PHP.

**10. Los widgets Elementor tipo `"html"` tienen el mismo bug de escapado
que los `"text-editor"` — persisten, no renderizan.** Al intentar enlazar
la landing NAD+ desde `/longevidad/` (página Elementor de un solo widget
`html` gigante, id `96c40f4`): escribir `_elementor_data` vía
`POST wp/v2/pages/{id}` con `{"meta": {"_elementor_data": ..., "_elementor_element_cache": ""}}`
devolvió HTTP 200 y **sí persistió** en la base de datos (confirmado
releyendo el meta) — pero el HTML servido en vivo, confirmado sin caché
(`X-Litespeed-Cache: miss`, `x-hcdn-cache-status: MISS`, longitud de
respuesta consistente con una renderización real, no una versión vieja),
**no incluía el cambio**. Es el mismo síntoma ya documentado para widgets
`text-editor` ("persiste, formato de escapado, no renderiza"), ahora
confirmado también en widgets `html`. Se revirtió el cambio (no dejar la
BD con una edición invisible/inconsistente) y se dejó para edición manual
en el editor de Elementor. **Regla: ninguna edición de `_elementor_data`
por API se da por buena solo con el HTTP 200 ni con releer el meta —
hay que verificar el HTML servido en vivo, sin caché, antes de reportarla
como aplicada.**

```bash
# comprobación automática de las reglas 6 y del tamaño
py -3 -c "import re,html,pathlib;t=pathlib.Path('docs/contenido/<archivo>.html').read_text(encoding='utf-8');p=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t)));print('palabras',len(p.split()));print('prohibidas',re.findall(r'farmacia|refrigeraci[oó]n.{0,40}transporte',p,re.I))"
```

---

## Fase 5 — Publicación

```bash
py -3 scripts/publica_ficha.py <id> <archivo.html> "<Nombre>" marcador1 marcador2 ...
```

**Hay DOS mecanismos y el script los detecta solo.** No asumir cuál aplica:

| tipo | cómo se detecta | dónde se escribe |
|---|---|---|
| **Elementor** | `_elementor_edit_mode == "builder"` | `settings.editor` del widget `text-editor` dentro de `_elementor_data` + **vaciar `_elementor_element_cache`** + sincronizar `description` |
| **Plano** | sin `_elementor_data` | solo `description` en `wc/v3` |

Verificado: 795 y 1699 son Elementor; **2240 es plano**. Escribir en el lugar
equivocado devuelve HTTP 200 y no cambia nada de lo que ve Google.

En ambos casos: `name` → H1 limpio, `rank_math_title` **no se toca**. El script
respalda antes y **revierte solo** si la verificación en vivo no pasa.

### Consolidar dos fichas que compiten por la misma keyword

Cuando dos productos pelean por una keyword (MOTS-c 10 mg y 40 mg estaban ambas
en posición 82), **consolidar con `rank_math_canonical_url`, no con 301**:

```bash
py -3 scripts/consolida_motsc.py    # plantilla adaptable
```

- La secundaria **sigue publicada y comprable** — cero riesgo comercial.
- Google consolida la señal en la principal.
- Es reversible borrando un campo.
- **Verificado que `rank_math_canonical_url` sí persiste por `wc/v3`** y aparece
  en el `<link rel="canonical">` renderizado.

No convertir a producto variable por API sobre una tienda viva: arriesga el
checkout y la plantilla Elementor puede no renderizar el selector de variaciones.

La ficha secundaria se deja **corta a propósito**, apuntando a la principal.
Para publicarla usar `--min 800`, porque el umbral por defecto (1800) está
pensado para monográficos y dispararía un rollback falso.

Nota para fichas planas: `wc/v3` despoja las etiquetas `<script>`. Si el
contenido necesitara JSON-LD embebido, usar `POST /wp-json/wp/v2/product/<id>`
con `content` vía JWT. Las tablas y el HTML normal sí sobreviven por `wc/v3`.

## Fase 6 — Verificación en vivo

Con cache-bust **y** sin él. Comprobar H1, conteo de palabras y 5-6 marcadores
de texto que solo existan en la versión nueva.

El `purge-on-update` de LiteSpeed suele bastar (`x-litespeed-cache: miss` +
contenido nuevo servido). Si sigue sirviendo lo viejo: purgar hcdn en
hPanel → Rendimiento → CDN → Vaciar caché. **LiteSpeed no purga hcdn.**

## Fase 7 — Medición

```bash
py -3 scripts/rundown_pys.py            # mide y compara contra la línea base
py -3 scripts/rundown_pys.py --seco     # solo estado, sin gastar API
```

**Calendario:**

| Momento | Qué esperar | Qué hacer |
|---|---|---|
| Semana 0 | — | Registrar línea base |
| Semana 4 | Señal temprana | Medir. **No decidir nada todavía.** |
| **Semana 8** | **Punto de decisión** | Si ≥50% de las fichas maduras mejoraron 10+ posiciones → el diagnóstico se confirma, seguir. Si no → el cuello de botella es autoridad, pasar a enlaces. |
| Semana 12 | Confirmación | Medir y consolidar |

**Marcador inicial (2026-07-30):** 0 en top-10, 0 en top-20, mejor posición 38.

**Regla de oro:** no reescribir las 10 fichas antes de la semana 8. Optimizar
2-3, esperar la señal, y solo entonces escalar. Si el diagnóstico es incorrecto,
un lote de 3 cuesta mucho menos que uno de 10.

---

## Orden de ejecución

| # | ficha | keyword | vol | estado |
|---|---|---|---:|---|
| 1 | 795 BPC-157+TB-500 | bpc 157 precio | 210 | ✅ publicada 2026-07-30 (939 → 2,530 · Elementor) |
| 2 | 1699 Selank | selank | 480 | ✅ publicada 2026-07-30 (996 → 3,253 · Elementor) |
| 3 | 2240 Cagrilintida | cagrilintida | 590 | ✅ publicada 2026-07-30 (552 → 3,076 · **plano**) |
| 4 | 19 Retatrutida | retatrutide precio | 4,400 | ✅ publicada 2026-07-30 (1,702 → 3,319 · Elementor) |
| 5 | 799 Agua bacteriostática | agua bacteriostatica | 1,600 | ✅ publicada 2026-07-30 (919 → 2,363 · Elementor) |
| 6 | 790+793 MOTS-c | mots-c | 880 | ✅ publicada + **consolidada** 2026-07-30 (972 → 3,101 · canonical 793→790) |
| 7 | 2232 CJC-1295+Ipamorelina | ipamorelina | 1,900 | ✅ publicada 2026-07-30 (608 → 3,066 · **plano**) |
| 8 | 1128 IGF-1 LR3 | igf-1 lr3 | 390 | ✅ publicada 2026-07-30 (1,118 → 2,723 · Elementor) |
| 9 | 2231 Sermorelina | sermorelin | 880 | ✅ publicada 2026-07-30 (528 → 2,134 · **plano**) |
| 10 | 2230 Timosina Alfa-1 | thymosin alpha 1 | 170 | ✅ publicada 2026-07-30 (536 → 2,272 · **plano**) |

| 11 | 1525+1531 Tirzepatida | tirzepatida precio mexico | 1,200 | ✅ publicada + **consolidada** 2026-07-30 (1,052 → 2,450 · canonical 1531→1525) |
| 12 | 1131 NAD+ | nad iv | 390 | ✅ publicada 2026-07-30 (964 → 2,753 · Elementor) |

**Fuera del plan, con razón:**
- **2234 Glutatión** — SERP de cápsulas orales de góndola, otro mercado. No rankeará se haga lo que se haga.
- **1689 Semaglutida** — cabeza bloqueada 53%; el long-tail de investigación (`semaglutida liofilizada`, `semaglutida investigacion`) tiene **0 volumen**. Toda la demanda GLP-1 es de marca farmacéutica. Retorno mínimo.
- **5 agotados** — semaglutida 20mg y los 4 Nutricost (suplementos de góndola, otro mercado).

---

## Reseñas de producto — criterio de moderación y captura (Fase 5, decidido 2026-08-02)

Autorizado como pieza independiente de la Fase 5 (el resto de Fase 5 queda
congelada como especificación acumulada). Nada de esto se ha implementado
todavía — queda documentado para cuando se ejecute.

**Configuración:** reseñas solo de compradores verificados; toda reseña queda
**pendiente de aprobación manual** antes de publicarse — nunca se auto-publica.

**`AggregateRating` condicionado, nunca inventado.** Mismo principio que
`availability: OutOfStock` en el schema (ver `docs/superficie-pys-vs-exoma.md`
y las lecciones de arriba): un dato falso en resultados enriquecidos es peor
que no tener el dato. El bloque `aggregateRating` del schema de producto se
omite por completo mientras `reviewCount == 0` — se genera únicamente cuando
existe al menos una reseña real y aprobada.

**El criterio de moderación es por CONTENIDO, nunca por calificación.** Se
retira una reseña cuando:
1. afirma que el producto cura, trata o previene una enfermedad;
2. sugiere una dosis o pauta de uso;
3. menciona un padecimiento concreto en el que se usó.

Riesgo regulatorio real: es producto sin registro sanitario para uso clínico.
**Se conserva** una reseña negativa, una queja de servicio, un "no me
funcionó" — eso no es riesgo regulatorio, es una opinión real, y filtrar por
calificación en vez de por contenido convertiría la sección de reseñas en
propaganda, que es exactamente lo que la regla de "cero trampas, cero spam"
de Fase 5 prohíbe.

**Correo post-compra — a los 14 días DESPUÉS DE LA ENTREGA** (no de la
compra: da margen al tránsito nacional y a que el cliente ya haya recibido y
usado el producto). Sin cupón, sin descuento, sin incentivo de ningún tipo —
una reseña pagada no es una reseña.

**Regla de redacción del correo, la más importante de las dos:** preguntar
por la **experiencia de compra** — empaque, discreción del envío, tiempo de
entrega, presentación del producto, atención — **nunca por resultados ni
efectos**. Invitar a reseñar "cómo te funcionó" genera exactamente el
contenido clínico que la regla de moderación de arriba obliga a retirar
después. Es más barato no provocar esas reseñas que moderarlas una por una
tras el hecho — el filtro más eficiente es la pregunta que nunca se hizo.
