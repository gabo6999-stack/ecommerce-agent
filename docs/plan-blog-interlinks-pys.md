# Plan — enlaces internos blog → ficha (PYS)

> Medición del 2026-07-31 sobre los 18 posts publicados y 21 productos publicados.
> Datos crudos en `docs/data/blog-interlinks/`.
>
> **PARTE A COMPLETA el 2026-07-31.** Tiers 1 y 2 con
> `scripts/retro_interlinks_blog.py --apply` (12 posts, 21 enlaces muertos
> resueltos, 8 enlaces nuevos a ficha, 0 abortados). Tiers 3 y 4 con
> `scripts/tier3_pasajes_blog.py --apply` (6 posts, 6 pasajes redactados,
> 7 enlaces nuevos a ficha + 4 a fuentes PubMed verificadas, 0 fallos).
> Respaldos en `backups/blog-<id>-antes-*-2026-07-31.json`, diffs en
> `docs/data/blog-interlinks/diffs/`. **La PARTE B sigue pendiente.**
>
> Enlaces internos rotos en todo el blog: **0** (verificado con GET a las 47 URLs
> internas). Fichas huérfanas: **0**.
>
> **2147 (GLP-1 y adicciones) se dejó como estaba, a propósito.** Sus 2 enlaces
> —semaglutida y tirzepatida— son exactamente los dos compuestos con evidencia en
> adicción. Añadir un tercero exigía afirmar algo que la evidencia no sostiene.
>
> **Corrección sobre el pronóstico de MOTS-c:** los 5 enlaces muertos hacia el post
> inexistente de MOTS-c **no** se convirtieron en 5 enlaces nuevos a la ficha. Los
> cinco posts ya enlazaban `/product/mots-c-10mg/` por otro lado, así que el
> remapeo habría duplicado un enlace existente y el script los desenlazó. La ficha
> 790 sigue con 9 entrantes, no 14.

---

## 0. Lo que la medición contradice

La premisa de entrada era "el blog no enlaza a las fichas". **Medido: sí enlaza, y
mucho.** 16 de 18 posts ya tienen entre 8 y 23 enlaces a `/product/`, con anclas
variadas (`'combo BPC-157 + TB-500 10mg'`, `'agua bacteriostática para
reconstitución de péptidos'`, `'MOTS-c 10mg péptido para metabolismo y
longevidad'`). Enlaces a categoría: **0** — la regla 4 no tiene nada que arreglar,
solo que prevenir.

Añadir 2-3 enlaces más a cada uno de los 18 posts sobre-enlazaría los que ya están
saturados y no movería la aguja. El déficit real es **de distribución**, no de
volumen: unas pocas fichas se llevan todo y cinco no reciben casi nada.

### Los cuatro problemas que sí existen

| # | Problema | Tamaño |
|---|---|---|
| 1 | Enlaces internos **rotos (404)** | 21 enlaces → 5 URLs muertas, en 7 posts |
| 2 | Fichas **huérfanas o casi** | 2 con cero entrantes, 3 con uno solo |
| 3 | Compuestos mencionados **sin enlazar** | CJC-1295/Ipamorelina 26× en un post, 0 enlaces |
| 4 | Enlaces a fichas **agotadas** | 44 enlaces a 5 productos `outofstock` |

---

## 1. Enlaces rotos (404) — 21 enlaces, 7 posts

Las 5 URLs muertas son posts de blog que ya no existen (no redirigen: 404 duro).

| URL muerta | usos | posts afectados | destino propuesto |
|---|---:|---|---|
| `/composicion-corporal-guia-completa-transformacion/` | 7 | 2128, 1926, 1727(×2), 1675, 1647, 1476 | 2075 `perdida-de-grasa-…` |
| `/masa-muscular-guia-completa-peptidos-suplementos/` | 6 | 2128, 1926, 1913, 1727, 1675, 1476 | 1926 `optimizar-rendimiento-deportivo-…` |
| `/mots-c-peptido-mitocondrial-rendimiento-deportivo/` | 5 | 1926, 1913, 1727, 1675, 1476 | **ficha 790** `/product/mots-c-10mg/` |
| `/guia-completa-suplementos-deportivos-evidencia-cientifica/` | 2 | 1926, 1913 | 1926 (si es el propio post → desenlazar) |
| `/ghk-cu-peptido-de-cobre-beneficios/` | 1 | 1675 | 1913 `ghk-cu-peptido-cobre-regeneracion-…` |

Los MOTS-c apuntaban a un post inexistente y el compuesto **sí** tiene ficha: ese
remapeo convierte 5 enlaces rotos en 5 enlaces blog→ficha. Justo lo que busca la
campaña.

**Alternativa (más cara, más valiosa):** los dos temas muertos —composición
corporal y masa muscular— son los que 13 enlaces piden a gritos. Escribir esos dos
pilares y apuntar ahí es superficie nueva + los 404 resueltos de origen. Decisión
tuya; el remapeo no la bloquea.

## 2. Fichas huérfanas y compuestos sin enlazar

Enlaces entrantes desde el blog, por ficha en stock:

```
 10  1131 NAD+              9  1128 IGF-1 LR3        9  795 BPC-157+TB-500
  9  1689 Semaglutida 5mg   9   799 Agua bacter.     9  790 MOTS-c
  8  1525 Tirzepatida       8    19 Retatrutida      4  1699 Selank
  1  2232 CJC-1295+Ipamo.   1  2231 Sermorelina      1  2230 Timosina Alfa-1
  0  2240 Cagrilintida      0  2234 Glutatión
```

Los cinco de abajo son las fichas nuevas (publicadas 2026-07-26/30): el blog se
escribió antes de que existieran. Menciones sin enlace ya presentes en el texto:

| ficha | post | menciones sin enlazar |
|---|---|---:|
| 2232 CJC-1295 + Ipamorelina | 2075 pérdida de grasa | 26 |
| 2232 | 2096 biohacking | 20 |
| 2232 | 2201 péptidos (pilar) | 14 |
| 2232 | 1675 longevidad | 4 |
| 2232 | 2094 testosterona | 2 |
| 2231 Sermorelina | 2201 | 3 |
| 1128 IGF-1 LR3 | 2075 | 6 |
| 799 Agua bacteriostática | 1647 | 7 |
| 799 | 1675 | 2 |

**2240 Cagrilintida y 2234 Glutatión no se mencionan en ningún post.** No hay
enlace contextual honesto que agregar: hay que escribir el pasaje. Cagrilintida
entra natural en 2211 (comparativa GLP-1, vía CagriSema) y en 2075; Glutatión en
2096 (biohacking) y 1675 (longevidad).

## 3. Posts pobres en enlaces a ficha

| post | enlaces a ficha | acción |
|---|---:|---|
| 2190 dataset abierto (150 palabras) | 0 | +2 (es una nota corta; 2 basta) |
| 2147 GLP-1 y adicciones | 2 | +2 (semaglutida 1689, tirzepatida 1525) |
| 2075 pérdida de grasa | 3 | +3 (2232, 1128, 19) |

## 4. Deuda que se reporta, no se toca

44 enlaces apuntan a fichas `outofstock`: Omega-3 (18), Zinc Picolinato (15),
Complejo B (8), Semaglutida 20mg (8), DIM (3). Devuelven 200, así que no son
enlaces rotos — son enlaces a producto no comprable. Tres salidas: reabastecer,
re-apuntar, o desenlazar. **No lo decido yo**: son cuatro suplementos Nutricost y
la semaglutida de 20 mg, y la respuesta depende de si vuelven al catálogo.

---

## Alcance corregido de la PARTE A

| Tier | Qué | Enlaces | Posts | Método |
|---|---|---:|---:|---|
| 1 | Remapear 404 | 21 | 7 | Determinista (regex sobre `href`) — sin LLM |
| 2 | Enlazar menciones existentes | 18 | 6 | Determinista: envolver la 1ª mención en `<a>` |
| 3 | Fichas sin mención (2240, 2234) | 4 | 4 | LLM: redactar el pasaje |
| 4 | Posts pobres | 7 | 3 | LLM |

Tier 1 y 2 son sustitución de texto verificable, sin generación: menos riesgo y
diff legible. Todo sale a `docs/data/blog-interlinks/diffs/<post_id>.diff` +
`reporte.json`. **`--apply` es un flag explícito**; sin él no se escribe en WP.

Anclas: se genera una lista rotatoria por ficha para no repetir la misma en dos
posts (ya hay variedad; el script la conserva y la extiende).

---

## PARTE B — cambios propuestos a `web.py` / `templates/index.html`

### B1. Mapa de fichas cacheado (punto 6)

```python
# ─── Mapa compuesto → ficha (PYS) ────────────────────────────────────────────
# Lo consume el Blog Agent ANTES de generar, y /optimize-blog al enlazar.
PYS_ALIASES = {                      # alias que el nombre del producto no da
    19:   ["retatrutide"],
    795:  ["bpc157", "tb-500", "tb500", "timosina beta 4"],
    1128: ["igf-1", "igf 1", "mecasermina"],
    1525: ["tirzepatide", "mounjaro", "zepbound"],
    1689: ["semaglutide", "ozempic", "wegovy"],
    2230: ["thymosin alpha 1", "ta-1"],
    2231: ["sermorelin"],
    2232: ["cjc 1295", "ipamorelin"],
    2240: ["cagrilintide"],
}
_product_map_cache = {"at": 0, "data": None}

def build_product_map(ttl=1800, include_out_of_stock=False):
    """[{id, name, url, aliases}] de fichas enlazables.

    Reglas:
      - solo status=publish y stock_status=instock (nada de enlazar agotados)
      - si la ficha tiene rank_math_canonical_url a otra ficha, se colapsa a la
        principal (793 → 790, 1531 → 1525): el enlace va a la que consolida
      - NUNCA devuelve URLs de categoría: las de PYS están rotas
    """
```

Endpoint nuevo `GET /product-map` → lo llama el Blog Agent antes de escribir.

### B2. Ruteo por intención (punto 8)

`méxico` y `mg` **no** bastan por sí solos —`Tirzepatida … guía completa méxico
2026` es informacional y es uno de los posts que mejor funcionan—. Por eso hay dos
niveles:

```python
_KW_COMPRA  = r"\b(precio|precios|comprar|compra|costo|cu[aá]nto cuesta|venta|" \
              r"vender|barato|oferta|descuento|d[oó]nde comprar|tienda)\b"
_KW_MODIF   = r"(\b\d+\s?mg\b|\bm[eé]xico\b|\bcdmx\b|\benv[ií]o\b)"

def route_keyword(keyword, product_map, market="pys"):
    """'ficha' | 'blog'. Señal de compra = ficha directo.
    Modificador solo (mg/méxico) = ficha SOLO si además nombra un compuesto
    del catálogo; si no, es informacional con modificador geográfico."""
```

Cuando devuelve `ficha`, responde **qué ficha** y no se escribe post. Si hay
credenciales DataForSEO, se contrasta con `search_intent()` y se reporta la
discrepancia (no manda: la API marca `commercial` cosas que sí son de blog).

### B3. Validación previa a publicar (punto 9)

```python
def validate_blog_html(html, title, product_map, check_http=True):
    """Compuertas duras. Devuelve {"ok": bool, "fallos": [...], "avisos": [...]}"""
    #  V1  ≥2 enlaces a /product/ de fichas del mapa           → duro
    #  V2  ningún enlace 404 (GET a cada href, interno y externo) → duro
    #  V3  ningún enlace a /product-category/ ni /categoria/     → duro
    #  V4  no canibaliza: si el título entra en route_keyword()
    #      como 'ficha', se rechaza y se nombra la ficha dueña   → duro
    #  V5  ninguna ficha enlazada está agotada                   → aviso
    #  V6  no repetir la misma ancla para la misma URL           → aviso
```

### B4. Las 10 compuertas del retrofeed (punto 10)

De `docs/playbook-fichas-pys.md`, adaptadas a blog:

| # | Compuerta | Automatizable | Tipo |
|---|---|---|---|
| 1 | PMIDs existen y autor/revista/año coinciden (`eutils` esummary) | sí | duro |
| 2 | La keyword tiene volumen medido > 0 (DataForSEO) | sí | duro |
| 3 | El SERP es del mercado correcto | parcial | aviso |
| 4 | Ausencia del competidor = oportunidad o descarte | no | aviso |
| 5 | Estudios de la molécula exacta (TB-500 ≠ Tβ4) | parcial | aviso |
| 6 | **Palabra prohibida** + frase de refrigeración en transporte | sí | duro |
| 7 | Ninguna afirmación clínica sin fuente (párrafo con % o "estudio" sin `<a>` cerca) | sí | duro |
| 8 | Longitud mínima (blog: 1,200 palabras) | sí | duro |
| 9 | Marcadores en texto plano | sí | duro |
| 10 | No quita nada bueno que ya estaba (solo en reescritura) | sí | duro |

```python
FORBIDDEN = re.compile(r"farmacia|refrigeraci[oó]n.{0,40}transporte", re.I)
def retrofeed_gates(html, title, keyword=None, market="pys"): ...
```

Endpoint `POST /validate-post` corre B3 + B4 sin escribir nada.

### B5. Dónde se aplica la compuerta

Hoy el Blog Agent **publica y después** llama a `/optimize-blog`: cuando la
compuerta dispara el artículo ya está en vivo. Dos salidas:

- **(a) recomendada** — el Blog Agent publica en `draft` y `/optimize-blog`
  promueve a `publish` solo si pasa todo. Es un cambio de una línea en
  `agente-blogs/tools/wordpress.py`; **repo distinto, no lo toco sin tu visto bueno.**
- **(b) sin tocar el otro repo** — `/optimize-blog` degrada el post a `draft` y
  reporta. Queda publicado unos segundos.

### B6. Cambios a `/optimize-blog` y `/add-links`

- El prompt recibe el **mapa de fichas** (compuesto → URL) en vez del volcado de
  30 productos, con la regla: 2-3 enlaces contextuales, ancla natural y distinta
  en cada aparición, prohibido enlazar categorías y prohibido enlazar agotados.
- Tras la respuesta del LLM: `validate_blog_html` + `retrofeed_gates`. Si falla,
  **un** reintento con los fallos en el prompt; si vuelve a fallar, HTTP 422 y no
  se escribe en WP.
- Se conserva `sanitize_faq_jsonld` tal cual (el fix determinista de Rafa).

### B7. `templates/index.html`

Un botón más, `🕸️ Mapa de enlaces`, que abre un panel con lo que este documento
mide en vivo: entrantes por ficha, huérfanas en rojo, 404 y enlaces a agotados.
Reusa el patrón de `abrirAuditoria()`.

### B8. Script de la parte A

`scripts/retro_interlinks_blog.py` — dry-run por defecto, `--apply` para escribir,
respaldo por post en `backups/` antes de tocar, verificación en vivo después.
