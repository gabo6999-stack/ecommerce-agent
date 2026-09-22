# Inventario de páginas — rediseño de PYS

Levantado del sitemap de Rank Math (`/sitemap_index.xml`) el 2026-09-21, más las
URLs que existen pero el sitemap no lista. **Todas** responden y **todas** reciben ya
la cabecera, el pie y el fondo nuevos (capa global `pys-diseno.php`). Lo que cambia
por familia es si su *cuerpo* ya está rediseñado.

| Familia | URLs | Cuerpo rediseñado | Archivo |
|---|---:|---|---|
| Portada | 1 | ✅ plantilla propia · auditada 2026-09-22 | `pys-home-2026/template.php` |
| Catálogo (tienda + categorías + etiquetas) | 1 + 7 + etiquetas | ✅ fase 2 · auditado 2026-09-22 | `pys-diseno/catalogo.php` |
| Ficha de producto | 22 (21 en sitemap) | ✅ fase 3 · auditada 2026-09-22 | `pys-diseno/ficha.php` |
| Blog (listado + entradas) | 21 | ✅ fase 4 · auditado 2026-09-22 | `pys-diseno/blog.php` |
| Carrito y finalizar compra | 2 | ✅ fase 5 · auditado 2026-09-22 | `pys-diseno/tienda.php` |
| Mi cuenta | 1 (+ recuperar contraseña) | ✅ 2026-09-22 | `pys-diseno/cuenta.php` |
| Elementor: políticas e informativas | 8 (incl. `/pedido/`) | ✅ 2026-09-22 | `pys-diseno/paginas-elementor.php` |
| Elementor: landings comerciales | 4 | ✅ 2026-09-22 | `pys-diseno/landings.php` |
| Páginas planas (Gutenberg/HTML) | 9 (incl. términos) | ✅ 2026-09-22 | `pys-diseno/paginas-planas.php` |
| Búsqueda y 404 | 2 | ✅ 2026-09-22 | `pys-diseno/utilitarias.php` |

Cada familia se dio por buena con `herramientas/verificar.py` antes/después
(contenido IDÉNTICO en escritorio y móvil) y revisión visual de las tiras
(`herramientas/revisar.py`). Protocolo: `PROTOCOLO-AGENTES.md`.

**64 URLs en el sitemap** (la tienda va dentro del de productos) + 3 de tienda + 7 categorías + etiquetas + búsqueda + 404.

## ⚠️ Hallazgo de SEO (fuera del alcance del diseño)

Las **7 categorías de producto son indexables** (`index, follow`) **pero no están
en el sitemap**. Rank Math tiene apagado el sitemap de la taxonomía `product_cat`.
Google las puede encontrar por enlaces, pero el sitemap es la vía directa.

## Portada (1)

- `/`

## Catálogo (8)

Más `/product-tag/*`, que son `noindex`.

- `/comprar-peptidos-en-mexico/`
- `/product-category/metabolismo-activo/`
- `/product-category/performance-top/`
- `/product-category/recuperacion-rapida/`
- `/product-category/bienestar-general/`
- `/product-category/peptidos-para-rendimiento-cognitivo/`
- `/product-category/reparacion-celular/`
- `/product-category/suplementos/`

## Fichas de producto (22)

21 en el sitemap. La 22.ª es `/product/mots-c-40mg/`, que **está fuera a propósito**:
tiene la canónica apuntando a `/product/mots-c-10mg/` (consolidación deliberada) y
Rank Math no mete en el sitemap lo que canoniza a otra URL. Se ve y se vende igual.

- `/product/agua-bacteriostatica-3ml/`
- `/product/bpc-157-tb-500/`
- `/product/bpc-157/`
- `/product/cagrilintida-10mg/`
- `/product/cjc-1295-ipamorelina-5mg/`
- `/product/complejo-b-metilado/`
- `/product/dim-suplemento/`
- `/product/ghk-cu/`
- `/product/glutation-1500mg/`
- `/product/igf-1-lr3-1mg/`
- `/product/mots-c-10mg/`
- `/product/mots-c-40mg/` — canónica a la de 10 mg
- `/product/nad-suplemento/`
- `/product/omega-3-nutricost-2500mg/`
- `/product/picolinato-de-zinc/`
- `/product/retatrutida/`
- `/product/selank-10-mg/`
- `/product/semaglutida-20mg/`
- `/product/semaglutida-5-mg/`
- `/product/sermorelina-10mg/`
- `/product/thymosin-alpha-1-10mg/`
- `/product/tirzepatida/`

## Blog — listados (2)

- `/blog/`
- `/category/blog/`

## Blog — entradas (19)

- `/agua-bacteriostatica-que-es/`
- `/biohacking-guia-definitiva-peptidos-suplementos-2025/`
- `/bpc-157-para-que-sirve/`
- `/dataset-peptidos/`
- `/estudio-triumph-1-retatrutide/`
- `/ghk-cu-peptido-cobre-regeneracion-antienvejecimiento/`
- `/igf-1-lr3-que-es-hormona-de-crecimiento-para-que-sirve/`
- `/longevidad-significado-peptidos-2026/`
- `/mots-c-que-es-para-que-sirve-beneficios-dosis-peptido-mitocondrial/`
- `/peptidos-glp-1-y-adicciones/`
- `/peptidos-para-longevidad-ciencia-antienvejecimiento/`
- `/precio-retatrutida/`
- `/que-son-los-peptidos/`
- `/rendimiento-deportivo-con-peptidos/`
- `/retatrutide-que-es/`
- `/selank-beneficios-y-dosis/`
- `/tb-500-peptido-recuperacion-atletas/`
- `/testosterona-que-es-funciones-niveles-optimos-como-optimizarla/`
- `/tirzepatida-para-que-sirve/`

## Tienda funcional (3)

Las tres son `noindex`. `/finalizar-compra/` da 302 con el carrito vacío, que es lo normal.

- `/carrito/`
- `/finalizar-compra/`
- `/mi-cuenta/`

## Páginas hechas con Elementor (11 + `/pedido/`)

Traen sus propios estilos en línea: son las más delicadas de rediseñar sin tocar contenido.

- `/calculadora-de-dosis-de-peptidos/`
- `/como-acelerar-el-metabolismo/`
- `/envejecimiento-saludable/`
- `/peptidos-mexico/`
- `/politica-de-envios-y-devoluciones/`
- `/politica-de-privacidad/`
- `/recuperacion-muscular/`
- `/rendimiento-deportivo/`
- `/semaglutida-en-mexico/`
- `/suplementos-deportivos/`
- `/tirzepatida-en-mexico/`

## Páginas planas (8)

- `/comparativas-de-peptidos/`
- `/contacto/`
- `/glp-1/`
- `/nad-para-que-sirve/`
- `/peptidos-inyectables/`
- `/peptidos-para-masa-muscular/`
- `/retatrutida-vs-tirzepatida/`
- `/tirzepatida-vs-semaglutida/`

## Utilitarias (2)

- `/?s=… (búsqueda)`
- `404`
