# Ecommerce Agent — peptidosysuplementos.mx

Agente con acceso a WooCommerce para consultar productos, órdenes, clientes e inventario.
Genera reportes PDF. Deploy en Railway.

## Stack
- Claude API (tool use) — `agent.py`
- WooCommerce REST API v3
- fpdf2 para reportes PDF
- `web.py` — interfaz web

## Variables de entorno
```
WC_STORE_URL=https://peptidosysuplementos.mx
WC_CONSUMER_KEY=ck_xxx
WC_CONSUMER_SECRET=cs_xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

## Herramientas disponibles
- `get_products` — buscar por nombre, categoría, popularidad
- `get_orders` — por estado (pending, processing, completed)
- `get_customers` — clientes
- Reportes PDF con fpdf2

## Regla absoluta del sitio: la ficha vende, la monografía informa

Cada molécula tiene dos páginas — `/product/<slug>/` y `/monografia/<slug>/` — y **un tema vive
en una sola de las dos**. Nunca se reparten un tema a medias: si las dos explican el mecanismo,
compiten entre ellas y Google elige una, que puede ser la que no tiene botón de compra.

- **La monografía posee** mecanismo de acción, historia y desarrollo, narrativa de la evidencia,
  tabla de protocolos con PMID, identidad química y estatus regulatorio. Eso **sale de la ficha**:
  ni duplicado ni resumido.
- **La ficha se queda** con lo que decide una compra: presentación y gramaje, precio, existencias,
  pureza y COA, envío, reconstitución práctica, seguridad operativa, reseñas y CTA. Al adelgazarla
  hay que reorganizar lo que queda para que venda mejor — **no puede quedar anémica**.
- **Keywords separadas por diseño:** la ficha reclama el nombre comercial en español más país,
  gramaje o precio; la monografía, el nombre científico, el código de laboratorio o la grafía
  inglesa. Ninguna usa la palabra clave de la otra, ni siquiera como texto de anclaje.
- **Enlazado:** un enlace contextual en cada sentido, por debajo del 80% de la página y nunca
  junto al botón de compra. En schema, `Product.subjectOf` → monografía; la monografía no devuelve
  el puntero, porque su entidad es la sustancia y no el producto.
- Una monografía por **molécula**, no por SKU: las mezclas y los formatos heredan la de su
  componente principal.
- **Nunca se publica la fecha de análisis ni de emisión de un COA** (sí el lote, la pureza, la
  masa, el método, el laboratorio y la referencia).
- **Nada sobre dopaje, en ninguna página.** Ni la AMA/WADA, ni su Lista de Prohibiciones, ni sus
  secciones (S0, S2.x), ni los controles antidopaje, ni los métodos de detección. Decisión del
  dueño del 2026-09-23: no aporta a la venta y no le corresponde informar de eso. El campo
  `regulatorio.wada` se eliminó de `rediseno/monografias/datos/*.json` para que ningún agente
  pueda renderizarlo; si alguna vez hiciera falta, está en el historial de git.
