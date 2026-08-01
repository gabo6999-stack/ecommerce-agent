# FASE 1 — Veracidad. Diagnóstico completo

> 2026-07-31. **Nada aplicado.** Diffs en `docs/data/blog-interlinks/diffs-fuentes/`.
> Scripts: `scripts/fase1_corrige_fuentes_blog.py` (dry-run),
> `scripts/audita_referencias_fichas.py` (solo diagnóstico).

## Resumen

| | Blog (18 posts) | Fichas (14) |
|---|---|---|
| Referencias auditadas | 119 enlaces externos (100 únicos) | 129 citas, 128 PMIDs |
| URLs fabricadas (404) | **13** | 0 (no usan hipervínculos) |
| PMID inexistentes | 0 | **0** |
| Autor/año/revista/título discrepantes | — | **0** |
| **Citas con PMID válido pero paper NO relacionado** | **10 de 16** | **0** |

El blog y las fichas los escribió el mismo redactor. Las fichas pasaron por la
compuerta 1 del playbook y salen **limpias**. El blog no pasó por ninguna
compuerta, y ahí están los 13 enlaces fabricados **y los 10 PMID mal atribuidos**.

---

## BLOQUE A — Enlaces externos del blog

### A.1 · Los 13 rotos (404). Diffs listos, sin aplicar

| # | post | afirmación que sostenía | veredicto | acción |
|---|---|---|---|---|
| 1 | 2207 | "Eli Lilly lanzó Mounjaro en 2022 con aprobación de la FDA" | **(a)** existe · el comunicado ya no vive en esa URL | href → *Drug Trials Snapshots: MOUNJARO* |
| 2 | 2201 | "muchos péptidos no tienen aprobación de la FDA" | **(a)** | href → *Bulk Drug Substances… Section 503A* |
| 3 | 2094 | "la FDA ha emitido comunicados sobre testosterona" | **(a)** | href → *Testosterone Information \| FDA* |
| 4 | 2075 | "la FDA advirtió sobre compuestos no regulados para pérdida de peso" | **(a)** | href → *FDA's Concerns with Unapproved GLP-1 Drugs* |
| 5 | 2070 | "la FDA advirtió sobre péptidos compuestos no supervisados" | **(a)** | href → *Certain Bulk Drug Substances… Safety Risks* |
| 6 | 1675 | "según el NIA, la biología del envejecimiento…" | **(a)** | href → *Aging Biology \| NIA* |
| 7 | 1647 | "la FDA advirtió sobre adquirir péptidos fuera de canales autorizados" | **(a)** | href → *FDA's Concerns with Unapproved GLP-1 Drugs* |
| 8 | 2128 | "el BPC-157 no está aprobado por la FDA" | **(b)** no existe ninguna página "FDA updates BPC-157"; el hecho sí se sostiene | href → *Certain Bulk Drug Substances…* (BPC-157 figura ahí) |
| 9 | 2256 | "**la FDA** advierte sobre reutilizar agujas y jeringas" | **(b)** la advertencia es de los **CDC**, no de la FDA | recitar CDC + cambiar "La FDA advierte" → "Los CDC advierten" |
| 10 | 2256 | "la FDA establece directrices sobre compatibilidad de diluyentes" | **(c) NO existe** — eso vive en la etiqueta de cada producto | borrar la frase completa |
| 11 | 2207 | "Examine.com mantiene un análisis sobre tirzepatida" | **(c) NO existe** (404; Examine cubre suplementos, no GLP-1) | borrar la frase |
| 12 | 2092 | "Examine.com ofrece análisis de los agonistas GLP-1" | **(c) NO existe** | borrar la afirmación; el párrafo arranca en la frase siguiente |
| 13 | 1913 | "según el análisis de Examine.com sobre GHK-Cu…" | **(c) NO existe** | quitar la atribución; el consejo genérico se conserva sin fuente |

**(a) 7 · (b) 2 · (c) 4.** 11 posts afectados. Verificado que los 4 párrafos con
borrado quedan coherentes.

### A.2 · Los 34 "no comprobables" NO son un problema

18 pubmed · 9 nejm.org · 5 mayoclinic.org · 1 nih.gov · 1 clinicaltrialsarena.
Todos devuelven 403 a un user-agent de script: bloqueo de bots, no enlace muerto.

### A.3 · HALLAZGO NUEVO — 10 PMID válidos con paper que no tiene nada que ver

Los 16 PMIDs distintos del blog **existen todos**. Pero al contrastar el paper
real contra la afirmación que sostienen:

| post | afirmación en el texto | el paper realmente es |
|---|---|---|
| 1675 | "investigación sobre **Epitalon y la telomerasa**" | *The synagogue as health proxy: a proposal* — Conserv Jud, 2000 |
| 1675 | "revisión sobre **Thymosin Beta-4** y regeneración" | *Fenvalerate causes brain impairment during zebrafish development* |
| 1647 | "**efectos metabólicos del retatrutide**, fase 2" | *Immune response after two doses of the BNT162b2 COVID-19 vaccine* |
| 1727 | "PubMed sobre **semaglutida y composición corporal**" | *LC-MS/MS metabolomics… texture* (Food Chem) |
| 1727 | "investigaciones sobre **NAD+ y metabolismo**" | *Soluble RAGE… Angiotensin II-induced LVH* |
| 1913 | "estudios genómicos: **GHK-Cu modula 4,000 genes**" | *Tissue optical properties for prostate PDT* |
| 1913 | "**GHK** y expresión génica en deterioro cognitivo" | *Catheter-Associated Rhodotorula mucilaginosa Fungemia* |
| 2070 | "investigaciones en **Journal of Cell Science**" sobre Tβ4 | *Cancers among female partners of prostate cancer patients* |
| 2096 | "estudio clínico en **J Clin Endocrinol**" sobre secretagogos | *Renal apoptosis following CO2 pneumoperitoneum in a rat model* |
| 2256 | "investigaciones preclínicas sobre **BPC-157**" | *Three-dimensional surface strain analyses of spine segments* |

Pertinentes: **6 de 16** — y 3 de esas 6 se agregaron en los Tiers 3-4 de esta
sesión (cagrilintida, glutatión, MOTS-c). De las 13 citas preexistentes,
**solo 3 sostienen su afirmación**.

**Por qué importa para el diseño de la compuerta:** verificar que el PMID
*existe* no detecta nada de esto. Hay que contrastar el **título del paper**
contra la afirmación. La compuerta 1 tal como está escrita no habría atrapado
ninguno de los 10.

---

> ## ⚠ CORRECCIÓN 2026-07-31 (posterior)
>
> **Lo que dice abajo sobre "0 discrepancias de autor, año, revista o título" era
> falso.** El regex que parsea las citas usaba `[^<.]` para el autor, que excluye
> el punto de «et al.», así que **nunca matcheó ninguna cita**: las 129 entraron
> por el fallback, con autor/revista/año/título vacíos, y las cuatro
> comprobaciones se saltaron todas en silencio.
>
> Con el parser arreglado (`[^<]`): autor, revista y título siguen dando **0
> discrepancias** —eso sí se sostiene—, pero el año da **39 de 129 mal**, y
> **36 de ellas exactamente +1 año**. Detalle en la sección corregida al final.

## BLOQUE B — Las 14 fichas: limpias

129 citas, 128 PMIDs distintos, formato texto plano
(«Autor et al. *Título.* Revista, año. PMID N») — **sin hipervínculos**, así que
no hay enlaces que romperse.

- **0** PMID inexistentes.
- **0** discrepancias de autor, año, revista o título contra eutils. Los cuatro
  campos coinciden en las 129 citas.
- 793 y 1531 tienen 0 referencias: son las fichas satélite cortas a propósito,
  consolidadas por canonical. Esperado.

### La única alerta, revisada a mano: es un falso positivo

El detector marcó 3 referencias de la ficha **795 (BPC-157 + TB-500)** por citar
estudios de **timosina beta-4 completa** en una página que vende TB-500 (el error
Tβ4 43 aa vs fragmento de 7 aa del playbook). Al leer cómo las usa el texto:

- PMID 20536472 → *«Existe un ensayo de Fase I de timosina beta-4 completa en
  voluntarios sanos, **que no es extrapolable ni a TB-500 ni a la combinación**»*
- PMID 14500546 → *«**TB-500 no es timosina beta-4 completa, y esa distinción
  importa.** La Tβ4 es una proteína de 43 aminoácidos; TB-500 corresponde
  únicamente al motivo de unión a actina de 7 aminoácidos»*
- PMID 41235866 → *«**No existen datos farmacocinéticos publicados específicos
  del fragmento TB-500 aislado**»*

Están citadas **correctamente y con el encuadre explícito**. No hay error.

**Lección para la compuerta 5:** "el estudio es de otra molécula" no puede ser
una compuerta dura automática — depende de cómo lo encuadre la frase, y eso
exige lectura humana. Se queda como aviso, nunca como bloqueo.

---

# BLOQUE B corregido + barrido de identidad molecular

> 2026-07-31, tras arreglar el parser de citas. Scripts:
> `scripts/audita_referencias_fichas.py`, `scripts/barrido_identidad_molecular.py`.

## B.1 · Años mal citados: 39 de 129 (30%)

| desviación | citas |
|---|---:|
| **+1 año** | **36** |
| +2 años | 1 (Timosina Alfa-1, PMID 23327199: ficha 2015, real 2013) |
| +4 años | 1 (IGF-1 LR3, PMID 36091374: ficha 2026, real 2022) |
| +10 años | 1 (Sermorelina, PMID 18031173: ficha 2009, real 1999) |

Ninguna desviación es negativa: **todas envejecen el artículo hacia adelante**,
es decir, lo hacen parecer más reciente de lo que es. Se descartó el artefacto
epub-vs-impreso comprobando `pubdate` **y** `epubdate`: solo se marca cuando la
ficha no coincide con ninguna de las dos.

Por ficha: 2232 (6) · 1131 (5) · 1699, 799, 790, 2230 (4 c/u) · 795 (3) ·
2240, 1128, 2231, 1525 (2 c/u) · 19 (1).

Autor, revista y título: **0 discrepancias en las 129 citas.** Eso sí se sostiene.

## B.2 · Barrido de identidad molecular: 29 marcas, casi todas bien encuadradas

| ficha | marcas | lectura del encuadre |
|---|---:|---|
| 795 BPC-157 + TB-500 | 3 | **Correcto.** «TB-500 no es timosina beta-4 completa… no es extrapolable» |
| **1131 NAD+** | **6** | **Correcto, y es el mejor ejemplo del catálogo.** Los 6 ensayos son de nicotinamida ribósido (precursor), y la ficha lo dice con tabla propia: «Obsérvese el patrón: todos emplean precursores orales. Ninguno administra NAD+ directamente» |
| 2231 Sermorelina | 9 | **Falso positivo del detector.** Sermorelina *es* GHRH(1-29); los títulos lo escriben «GH-releasing hormone(1-29)-NH2» y el texto dice «la GHRH y sus análogos» |
| **1128 IGF-1 LR3** | **5** | **2 falsos positivos** («Long [R3]» y «long(R3)» con corchetes/paréntesis que el matcher no reconoció). **3 a revisar**: PMID 33938236, 36499281 y 36091374 son de IGF-1 nativo/recombinante, no de LR3. El texto los etiqueta «IGF-1», pero **la ficha no incluye una frase de no-extrapolación** como sí hacen la 795 y la 1131 |
| 1699 Selank | 1 | Correcto: la tuftsina se presenta como origen histórico |
| 2240, 799, 2232, 1525 | 1-2 | Correcto: revisiones de clase (análogos de amilina, secretagogos, agonistas GLP-1) legítimamente aplicables |
| 19, 790, 793, 1531, 2230 | 0 | — |

**No apareció ni una cita de CJC-1295 CON DAC en la ficha 2232**, que era el
riesgo que el playbook ya documentaba. Ese frente está limpio.

## B.3 · Lo único que queda para tu decisión

**Ficha 1128 (IGF-1 LR3).** Tres de sus ocho referencias son de IGF-1
nativo/recombinante. El texto nombra la molécula correctamente en cada caso, así
que no miente; pero un lector de una página titulada «IGF-1 LR3» puede leerlas
como evidencia del LR3. Las fichas 795 y 1131 resuelven exactamente esto con una
frase explícita de no-extrapolación. Añadirla aquí costaría dos líneas.
