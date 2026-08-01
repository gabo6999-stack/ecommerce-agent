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
