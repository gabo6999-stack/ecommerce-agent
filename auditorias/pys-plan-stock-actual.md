# PYS — Plan para competir con el stock actual

**2026-07-30.** Sin comprar producto nuevo. Sin páginas nuevas especulativas.
Basado en la comparación ficha por ficha contra la página de exoma que rankea
(`scripts/plan_pys_stock_actual.py`, datos en `docs/data/plan-pys-stock.json`).

---

## El diagnóstico, en una línea

**Tus fichas tienen entre 1/2 y 1/6 del contenido de la de exoma, y el H1 no coincide con
lo que la gente busca.** Eso es todo. No es autoridad, no es indexación, no es schema.

| ficha PYS | keyword | vol/mes | PYS | exoma | palabras PYS | palabras exoma | falta |
|---|---|---:|---:|---:|---:|---:|---:|
| 19 retatrutida-30mg | retatrutide precio | 4,400 | 59 | **4** | 1,661 | 3,092 | 1,431 |
| 2232 cjc-1295-ipamorelina | ipamorelina | 1,900 | fuera | **2** | 593 | 3,606 | 3,013 |
| 799 agua-bacteriostatica | agua bacteriostatica | 1,600 | 66 | **6** | 905 | 1,980 | 1,075 |
| 2231 sermorelina-10mg | sermorelin | 880 | fuera | **4** | 518 | 1,857 | 1,339 |
| 790 + 793 mots-c | mots-c | 880 | 82 | **4** | 972 / 423 | 2,878 | 1,906 |
| 2240 cagrilintida-10mg | cagrilintida | 590 | fuera | **18** | 511 | — | — |
| 1699 selank-10-mg | selank | 480 | 47 | **4** | 953 | 2,795 | 1,842 |
| 1128 igf-1-lr3-1mg | igf-1 lr3 | 390 | 75 | **2** | 1,107 | 2,483 | 1,376 |
| 795 bpc-157-tb-500 | bpc 157 precio | 210 | 38 | **6** | 951 | 1,766 | 815 |
| 2230 thymosin-alpha-1 | thymosin alpha 1 | 170 | fuera | **8** | 519 | 1,512 | 993 |

Promedio: PYS ~830 palabras, exoma ~2,400. **Estás compitiendo con un tercio del contenido.**

---

## Los 3 cambios, idénticos en las 10 fichas

### 1. H1 al nombre pelado (10/10 fichas lo tienen mal)

| hoy en PYS | debe ser |
|---|---|
| `MOTS-c 10mg \| Péptido Metabolismo y Longevidad México` | `MOTS-c` |
| `Selank 10mg \| Péptido Nootrópico Ansiedad y Focus México` | `Selank` |
| `IGF-1 LR3 1mg \| Crecimiento Muscular Avanzado México` | `IGF-1 LR3` |
| `Sermorelina 10mg \| Péptido Hormona de Crecimiento México` | `Sermorelina` |
| `Retatrutida 30mg \| Triple Agonista GLP-1 Control Peso` | `Retatrutida` |
| `Cagrilintida 10mg \| Amilina Control de Peso México` | `Cagrilintida` |
| `Thymosin Alpha-1 10mg \| Péptido Sistema Inmune México` | `Timosina Alfa-1` |
| `Agua Bacteriostática 3ml \| Reconstitución Péptidos México` | `Agua Bacteriostática` |
| `BPC-157 + TB-500 5mg \| Regeneración Muscular México` | `BPC-157 + TB-500` |
| `NAD+ 500mg \| Energía Celular Anti-Aging Nutricost México` | `NAD+` |

Tu H1 está keyword-stuffed y **no coincide exactamente con ninguna consulta**. El de exoma sí.
El `<title>` puede seguir llevando el "| Precio México" — ahí sí sirve. El H1 no.

**Riesgo: cero.** Es un campo, reversible en segundos.

### 2. Contenido: de ~830 a ~2,500 palabras

Es el delta más grande y el más consistente. Qué cubre exoma que tú no (visto en sus fichas):
mecanismo de acción, vida media, protocolo de reconstitución, dosis por objetivo, calendario de
resultados esperados, efectos secundarios, comparativa con péptidos afines, FAQ extensa, citas.

**No inventes contenido médico.** Toda afirmación clínica va con fuente, y respeta la línea de
"péptido de investigación" que ya usas.

### 3. Slug sin dosis — solo donde no tienes nada que perder

`mots-c-10mg` → `mots-c`, `selank-10-mg` → `selank`, etc.

**Hazlo solo en las que hoy están FUERA del top-100** (2232, 2231, 2240, 2230): ahí no hay
posición que arriesgar. En las que ya rankean (795 pos 38, 1699 pos 47, 19 pos 59, 799 pos 66,
1128 pos 75, 790/793 pos 82) **no toques el slug todavía** — un 301 mal hecho cuesta más de lo
que gana. Primero H1 + contenido; si en 8-10 semanas suben, entonces evalúa el slug.

---

## Dos problemas estructurales que te estás haciendo solo

### A. Dos fichas peleando por la misma keyword

- **MOTS-c**: fichas 790 (10mg) y 793 (40mg) → ambas en **posición 82** para `mots-c`.
- **Tirzepatida**: fichas 1525 (30mg) y 1531 (60mg) → misma keyword.

exoma tiene **una sola** página por compuesto; su título es literalmente
*"Comprar MOTS-c en México | Péptido Mitocondrial | **10 y 40 mg**"*. Cubre las dos dosis en una
URL y concentra toda la señal ahí.

**Acción:** consolidar en una ficha por compuesto con variantes de dosis (variable product de
WooCommerce), y 301 de la que se retira hacia la que queda. Esto no cuesta stock: es el mismo
inventario en una sola página.

### B. Ipamorelina: 1,900/mes enterrados en un combo

`ipamorelina` es la keyword individual más grande que es alcanzable (1,900/mes) y exoma está
en **posición 2** con una página de 3,606 palabras. Tú la tienes dentro de la ficha 2232, con
H1 *"CJC-1295 no-DAC + Ipamorelina 5mg | Combo GH México"* y **593 palabras**.

Sin stock nuevo no puedes abrir una ficha standalone de ipamorelina. **Lo que sí puedes:**
convertir 2232 en una página seria que apunte a los dos términos (`ipamorelina` 1,900 +
`cjc-1295` 1,000 = 2,900/mes), con 2,500+ palabras y H1 `CJC-1295 + Ipamorelina`. No va a ganarle
a una página dedicada, pero pasar de 593 palabras a 2,500 en la keyword más grande del catálogo
es el movimiento de mayor retorno disponible hoy.

---

## Orden de ejecución

Ordenado por retorno, no por volumen bruto:

| # | ficha | por qué primero |
|---|---|---|
| 1 | **795** BPC-157+TB-500 | Mejor posición del catálogo (**38**) y el gap más chico (815 palabras). Es el que menos trabajo necesita para entrar al top-20. |
| 2 | **1699** Selank | Segunda mejor posición (**47**). Gap 1,842. |
| 3 | **2240** Cagrilintida | **exoma solo está en 18** — la única keyword donde no domina el top-10. Mejor probabilidad de llegar a top-10 de todo el catálogo. |
| 4 | **19** Retatrutida | El mayor volumen alcanzable (4,400/mes). Está en 59, exoma en 4. |
| 5 | **799** Agua bacteriostática | 1,600/mes, posición 66, producto utilitario de baja competencia. |
| 6 | **790+793** MOTS-c | Consolidar las dos fichas + profundizar. 880/mes. |
| 7 | **2232** CJC-1295+Ipamorelina | 2,900/mes combinados, pero es el gap más grande (3,013 palabras). |
| 8 | **1128** IGF-1 LR3 | 390/mes, posición 75. |
| 9 | **2231** Sermorelina | 880/mes pero fuera del top-100. Ojo: la keyword fuerte es `sermorelin` (880), no `sermorelina` (210). |
| 10 | **2230** Timosina Alfa-1 | 170/mes. El más chico, va al final. |

**Fuera del plan:**
- **2234 Glutatión** — descartado, el SERP es de cápsulas orales de Walmart/Amazon, otro mercado.
- **1689 Semaglutida / 1525+1531 Tirzepatida** — la cabeza (135K y 90.5K) está bloqueada por
  autoridad médica y farmacias. Arregla sus H1 y consolida las de tirzepatida, pero **no esperes
  ranking en la keyword principal**; su valor está en el long-tail de marca.
- Los 5 productos **agotados** (semaglutida-20mg, Omega-3, Zinc, DIM, Complejo B).

---

## Cómo saber si funciona

**Métrica única:** posición de PYS en las 10 keywords de la tabla. Hoy: **0 en top-10, 0 en
top-20**, mejor posición 38.

Re-medir con `scripts/cluster_pys_fase6_posiciones.py` (borrando el caché) cuesta ~$0.20.
Hazlo **a las 8 semanas**, no antes — Google tarda en reprocesar cambios de contenido.

**Señal de éxito temprano:** que las que hoy están en 38-47 entren al top-20. Si eso pasa, el
diagnóstico era correcto y vale seguir con el resto.

**Señal de que el diagnóstico falla:** si tras subir a 2,500 palabras y arreglar los H1 las
fichas siguen en 38-80 a las 8 semanas, entonces sí es autoridad de dominio y la palanca pasa a
enlaces externos (ver `hf-backlinks-strategy`). Pero **no gastes en enlaces antes de agotar
esto** — exoma gana con la misma autoridad que tú.
