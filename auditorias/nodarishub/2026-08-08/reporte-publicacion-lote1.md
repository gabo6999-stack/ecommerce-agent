# Publicación lote 1 seguro — NodarisHub EC/MX

Fecha: 2026-08-08 UTC

## Alcance publicado

### ID 183 — México, diseño web

URL: https://nodarishub.com/mx/diseno-web/

- Se eliminó la referencia cruzada a precios de Ecuador.
- El enlace ahora apunta a `https://nodarishub.com/mx/crear-pagina-web/`.
- Texto visible nuevo: “¿Quieres conocer los costos antes de decidir? Consulta cuánto cuesta crear una página web en México.”
- Title SEO, title WordPress, canonical y hreflang conservados.

### ID 195 — México, SEO

URL: https://nodarishub.com/mx/seo/

H1 nuevo:

> Posicionamiento SEO para PyMEs en México: técnica, contenido y medición

- Se retiró la promesa de “primera página de Google” del H1.
- Title SEO, title WordPress, canonical y hreflang conservados.

### ID 196 — Ecuador, SEO

URL: https://nodarishub.com/ec/seo/

H1 nuevo:

> Agencia SEO en Ecuador para mejorar visibilidad, tráfico y medición

- Se retiró la promesa de “primera página de Google” del H1.
- Title SEO, title WordPress, canonical y hreflang conservados.

## Hallazgo previo que evitó cambios innecesarios

La aparente separación antes del punto/coma en los H1 de portada y diseño era un falso positivo del extractor de texto al atravesar elementos `span`. El HTML fuente tenía `</span>.` y `</span>,` correctamente. Por ello no se modificaron las portadas ni la puntuación de diseño web.

## Seguridad y verificación

- Respaldos frescos: 6/6 páginas candidatas.
- Páginas modificadas: 3/6.
- Páginas Elementor: 0/3 modificadas.
- Dry run: 3/3 PASS.
- Validación determinista local: 3/3 PASS.
- Control negativo del validador: PASS; detectó el cambio no autorizado inyectado.
- API read-back: 6/6 comprobaciones PASS (hash de `content.raw` y title WordPress).
- HTML público normal y cache-bust: 45/45 comprobaciones PASS.
- Canonical: 3/3 correcto.
- JSON-LD inválido: 0/3.
- Screenshot/DOM anónimo: 3/3 revisados; H1/bloque nuevo visibles y cabeceras sin desbordamiento.
- Rank Math title público comparado con la línea base: 3/3 sin cambios.
- Rollback: no requerido.

## Evidencia

- Respaldos: `2026-08-08/backups-pre-publicacion-lote1/`
- Manifest de cambios: `2026-08-08/lote1-preparado/manifest.json`
- Read-back API: `2026-08-08/verificacion-api-lote1.json`
- Verificación página 183: `2026-08-08/verificacion-183.json`
- Verificación página 195: `2026-08-08/verificacion-195.json`
- Verificación página 196: `2026-08-08/verificacion-196.json`

Las capturas full-page muestran grandes zonas vacías en secciones con animaciones diferidas porque el capturador no recorre la página para activar cada reveal. El DOM anónimo sí contiene esas secciones y este comportamiento ya existía; no se atribuye al lote publicado.
