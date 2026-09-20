# Publicación SEO: Sermorelin y BPC-157 individual — 2026-08-04

## Alcance

Cambios autorizados y aplicados en PYS:

1. Ajuste de grafía internacional en el title SEO de Sermorelina.
2. Creación de ficha BPC-157 individual con inventario cero.
3. Enlaces internos recíprocos entre BPC-157 individual y el combo BPC-157 + TB-500.
4. Imagen informativa específica para la ficha sin existencias.

## 1. Sermorelina

- ID: 2231.
- URL: https://peptidosysuplementos.mx/product/sermorelina-10mg/
- Title anterior: `Sermorelina 10mg | Péptido GHRH | Precio México`.
- Title nuevo: `Sermorelina 10mg (Sermorelin) | Precio México`.
- H1 conservado: `Sermorelina`.
- La introducción ya contenía `Sermorelina (sermorelin) 10 mg`; no fue necesario reescribirla.
- API read-back: correcto.
- HTML normal y cache-bust: 0 fallos de 15 comprobaciones.
- Screenshot anónimo: layout correcto; producto, precio, imagen, H1 e introducción intactos.

## 2. BPC-157 individual

- ID: 2464.
- URL: https://peptidosysuplementos.mx/product/bpc-157/
- Estado: publicado.
- Inventario: 0.
- Estado de stock: sin existencias.
- Precio: vacío.
- Comprable: no.
- Pedidos pendientes: desactivados.
- H1: `BPC-157`.
- Title SEO: `BPC-157 Precio México | Presentación Individual | PYS`.
- Canonical: self-canonical.
- Robots: `follow, index`.
- Categoría: Péptidos Recuperación y Crecimiento Muscular.
- Contenido visible: 534 palabras, 6 H2 y una tabla.
- No contiene afirmaciones clínicas, protocolos ni recomendaciones de dosificación.
- Marco visible: material destinado exclusivamente a investigación de laboratorio; no debe administrarse a personas ni animales.
- Sin botón de compra para el producto individual.
- Imagen creada y publicada: gráfica informativa `BPC-157 — presentación individual — sin existencias`, sin representar falsamente un vial o lote disponible.
- HTML normal y cache-bust: 0 fallos de 17 comprobaciones.
- Screenshot anónimo: imagen, tabla, enlaces y layout correctos.

## 3. Enlazado interno

### Individual → combo

La nueva ficha contiene varios enlaces hacia:

https://peptidosysuplementos.mx/product/bpc-157-tb-500-10-10mg/

### Combo → individual

Se agregó una sección al final de la ficha del combo:

- Encabezado: `BPC-157 individual`.
- Marcador: `BPC-157 individual actualmente sin existencias`.
- Enlace hacia la nueva ficha.
- API read-back: correcto.
- HTML normal y cache-bust: 0 fallos de 15 comprobaciones.
- Screenshot anónimo: sección visible y layout intacto.

## 4. Sitemap

- La ficha es pública, tiene `index,follow`, self-canonical y recibe enlaces internos desde el combo y la categoría.
- Todavía no aparece en `product-sitemap.xml`.
- El sitemap sí incluye otros productos publicados sin existencias: la ausencia no es causada por el stock cero.
- Estado: caché/actualización pendiente de Rank Math. No se modificaron ajustes globales ni se forzó una purga insegura.
- La URL sigue siendo descubrible por los enlaces internos; se debe volver a comprobar el sitemap en el seguimiento.

## 5. Respaldos

- `backups/pys-sermorelina-bpc-baseline-20260804T135927Z.json`
- `backups/pys-combo-795-before-bpc-interlink-20260804T140848Z.json`
- `backups/pys-bpc157-draft-created-20260804T140518Z.json`

## 6. Evidencia local

- `docs/contenido/bpc-157-individual-sin-stock.html`
- `docs/contenido/bpc-157-proximamente.png`
- `docs/data/bpc157-individual-publicacion-2026-08-04.json`
- `docs/data/bpc157-individual-imagen-2026-08-04.json`
- `docs/data/verificacion-sermorelin-2026-08-04.json`
- `docs/data/verificacion-bpc157-individual-2026-08-04.json`
- `docs/data/verificacion-combo-bpc-interlink-2026-08-04.json`

## Veredicto

Publicación funcional y reversible. La ficha BPC-157 individual está indexable, sin stock, no comprable y enlazada recíprocamente con el combo. El único punto pendiente es su incorporación al sitemap de Rank Math.
