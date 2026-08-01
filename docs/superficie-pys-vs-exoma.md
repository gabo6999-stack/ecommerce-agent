# Superficie PYS vs exoma — qué parte del gap vale la pena cerrar

> Medido el 2026-07-31 desde los sitemaps de ambos sitios + `docs/data/cluster-pys-ranked.json`.

## 1. El déficit de superficie es real y se reproduce

| tipo de URL | PYS | exoma |
|---|---:|---:|
| ficha de producto | 21 | 95 |
| compendio | 0 | 131 |
| blog | 18 + índice | 66 |
| páginas sueltas / landings (raíz) | 36 (incluye los 18 posts) | 41 |
| archivos de categoría | 5 | 11 |
| **TOTAL indexable** | **64** | **345** |

Gap: **281 URLs**.

## 2. Pero la superficie no es tráfico: qué gana cada tipo de URL en exoma

De las 64 keywords rankeadas que DataForSEO le mide a exoma:

| tipo de URL de exoma | URLs | keywords | top-10 | vol/mes | pos. media |
|---|---:|---:|---:|---:|---:|
| `/producto/` | 95 | **44** | **21** | 23,980 | 23.2 |
| landings en raíz | 41 | 11 | 7 | 13,100 | 23.5 |
| `/blog/` | 66 | 4 | 1 | 870 | 28.2 |
| **`/compendio/`** | **131** | **1** | **0** | 3,600 | **62.0** |

**131 compendios producen UNA keyword rankeada, en posición 62.** Son el 38% de
su superficie y rinden el 1.5% de sus keywords. Las fichas, con menos URLs,
rinden 44 keywords y 21 posiciones de top-10.

Segunda medición independiente, sobre los 39 SERPs cacheados del clúster de PYS:
exoma aparece 26 veces — 16 con `/producto/` (posición media 5.2), 4 con la raíz,
3 con `/peptidos-investigacion/`, 1 con `/blog/`, 1 con `/comprar-peptidos-mexico/`,
1 con `/como-reconstituir/`. Con `/compendio/`: **cero**.

**Límite honesto de esta evidencia:** `ranked_keywords` es una instantánea
histórica de las keywords que DataForSEO rastrea, y n=64 es poco. Los compendios
podrían estar aportando enlazado interno o long-tail que no se mide aquí. Pero la
asimetría es de 44 a 1, no marginal.

## 3. Y aunque funcionaran, no cerrarían el gap

Doblar (compendio + ficha) solo aplica a los 21 compuestos que PYS ya vende: como
mucho 64 → 85. **El gap es de 281.** De los 130 compendios de exoma, **119 son
sobre compuestos que PYS no vende**. El gap es de catálogo, no de duplicación.

Además, en los compuestos que PYS sí vende, el SERP es transaccional
(`scripts/diag_compendio_vs_producto.py`): 6 keywords "solo ficha" (6,520/mes),
4 "no doblar", 1 sola "sí doblar" (selank, 480/mes). En 13 de esas keywords exoma
rankea con `/producto/`, en ninguna con `/compendio/`.

## 4. Corrección: las categorías de PYS no están rotas

Lo di por bueno sin medirlo. Medido, los 5 `/category/*` responden **HTTP 200**:

| URL | palabras | robots |
|---|---:|---|
| `/category/blog/` | 630 | index |
| `/category/salud-metabolica/` | 303 | index |
| `/category/longevidad-y-regeneracion-biologica/` | 262 | index |
| `/category/metabolismo/` | 214 | index |
| `/category/crecimiento-y-reparacion/` | 187 | **noindex** |

No son categorías de producto: son **archivos de categoría del blog**, los cinco
con el mismo H1 ("Blog de Péptidos y Biohacking") y un solo enlace a producto.
El problema real es que son finos y casi duplicados entre sí
(`metabolismo` vs `salud-metabolica`) — razón suficiente para no enlazarlos, pero
distinta de la que yo di.

Y las páginas "por objetivo" **sí son landings intencionales**, no categorías:

| landing | palabras | fichas enlazadas |
|---|---:|---:|
| `/glp-1/` | 1,212 | 2 |
| `/perdida-de-peso/` | 1,041 | 1 |
| `/acelerar-el-metabolismo/` | 830 | 2 |
| `/reparacion-celular/` | 795 | 3 |
| `/longevidad/` | 729 | 3 |
| `/capacidad-fisica-performance/` | 686 | 3 |

Son exactamente el tipo de URL que en exoma es el **segundo mejor rendidor**
(11 keywords, 7 en top-10, 13,100/mes con solo 41 páginas).

## 5. La alternativa: no perseguir 345

345 es un número prestado, y el 38% de él no rinde. El orden por rendimiento
medido:

| # | Palanca | URLs | Por qué |
|---|---|---:|---|
| 1 | **Fichas nuevas** | hasta +78 | El tipo de URL con mejor rendimiento medido (44 kws, 21 top-10). Decisión de inventario, no de SEO |
| 2 | **Landings de intención en raíz** | +10-20 | Segundo mejor rendidor y no necesita inventario. PYS tiene 6, exoma 41 |
| 3 | **Blog** | +2/semana | 18 → 66 son ~6 meses. Rinde poco por URL pero alimenta a las fichas |
| 4 | **Consolidar los 5 archivos de categoría** | −4 | Finos y duplicados; consolidar en `/category/blog/` |
| 5 | Capa informativa sobre compuestos SIN ficha | (condicionado) | Es el único lugar donde el modelo compendio no canibaliza, porque no hay ficha que canibalizar. **Pero la evidencia dice que a exoma no le rinde**: no lo haría antes de 1 y 2 |

Objetivo razonable sin tocar inventario: **~90-100 URLs de los tipos que sí
rinden**. Con expansión de catálogo, 150-180. Igualar 345 exige copiar los 131
compendios, que es copiar justo la parte que no gana.

**La medición que falta** para cerrar el punto 5: SERPs vivos de keywords de
compuestos que PYS no vende (epithalon, GHK-Cu, GHRP-2/6, melanotan, DSIP,
AOD-9604, PT-141…). Si ahí los compendios de exoma sí rankean, el veredicto
cambia para esos compuestos. Hoy nadie lo ha medido.
