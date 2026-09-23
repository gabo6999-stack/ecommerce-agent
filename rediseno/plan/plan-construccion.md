## PLAN DE CONSTRUCCIÓN — PYS hacia el modelo exomapeptides.mx

### 0. Lo que verifiqué yo mismo antes de planear (los estudios se contradecían en un punto grave)

Tres comprobaciones propias sobre el sitio real, hoy 22-sep-2026:

**(a) El namespace /monografia/ NO está limpio — el estudio 1 se equivoca y el estudio 3 acierta.** Medido con curl anónimo, UA de Chrome:

```
/monografia/bpc-157/     -> 301 -> /product/bpc-157/
/monografia/semaglutida/ -> 301 -> /product/semaglutida-20mg/
/monografia/mots-c/      -> 301 -> /product/mots-c-10mg/
/monografia/retatrutida/ -> 301 -> /product/retatrutida/
/monografia/xyz-inexistente/ -> 404
/monografia/            -> 404
```

Las dos cosas son ciertas a la vez: no existe ninguna regla de Redirection ni ninguna página que ocupe la ruta (estudio 1), pero el adivinador de 404 de WordPress (`redirect_canonical`) resuelve el slug contra el producto (estudio 3). **Consecuencia que ningún estudio sacó: `/monografia/semaglutida/` apunta hoy a `/product/semaglutida-20mg/`, que es exactamente la URL que la fusión va a pasar a borrador.** Si se fusiona Semaglutida antes de neutralizar el adivinador, esa ruta queda mandando a un 404. Esto convierte un filtro de tres líneas en un requisito bloqueante, no en un detalle.

**(b) El atributo duplicado sigue vivo.** `wp_woocommerce_attribute_taxonomies` devuelve dos filas idénticas: `1 | gramaje | Gramaje | select` y `2 | gramaje | Gramaje | select`. Términos existentes en `pa_gramaje`: 249 (5 mg), 250 (10 mg), 251 (30 mg), 252 (60 mg), `count=1` cada uno. Faltan 20 mg y 40 mg, confirmado.

**(c) Reseñas: el cuadro exacto.** `woocommerce_enable_reviews='yes'`, `woocommerce_review_rating_verification_required='no'`, `verification_label='yes'`, `comment_previously_approved='1'`, `admin_email='enlace@grupoptm.com'`, `comments_notify=1`, `moderation_notify=1`. Comentarios en toda la base: `order_note = 31` y nada más. **Cero reseñas.** Y `monografia` no existe como post type.

Inventario de productos publicados confirmado: 22 (IDs 19, 790, 793, 795, 799, 1128, 1131, 1151, 1154, 1158, 1161, 1518, 1525, 1689, 1699, 2230, 2231, 2232, 2234, 2240, 2464, 2823).

---

## 1. ORDEN DE CONSTRUCCIÓN

La secuencia no la decide la importancia, la deciden tres dependencias duras:

1. **Las reseñas cuelgan de un `post_id`.** Fusionar después de tener reseñas obliga a trasvasar comentarios a mano. Hoy fusionar es gratis (0 reseñas). **La fusión va antes que las reseñas, sin discusión.**
2. **La monografía enlaza a la ficha y la ficha a la monografía.** El enlace tiene que apuntar a la URL definitiva. **El enlace se escribe después de la fusión**, aunque la infraestructura se construya antes.
3. **La regla de protocolos es una compuerta de contenido.** Ninguna monografía se escribe antes de que la regla esté congelada en el repo.

Todo lo demás es paralelizable. Tres carriles:

- **Carril A — servidor** (mu-plugins, WooCommerce, sitemap). Un agente técnico.
- **Carril B — contenido científico** (regla, monografías, limpieza de tablas y blog). Un agente redactor con verificación en PubMed.
- **Carril C — dueño** (COA de 21 productos, decisiones, petición de reseñas a clientes). No depende de código y **arranca el día 1**, porque es lo que más tarda y lo que más rinde.

```
Sem 0   FASE 0  decisiones + regla + respaldos        [A+B+C]
Sem 1   FASE 1A fusión MOTS-c        ||  FASE 1B infraestructura monografías
Sem 2   medición MOTS-c              ||  hub + capa de diseño + 3 monografías en borrador
Sem 3   FASE 2 reseñas (buzón, verificación, sección) || publicación piloto + sitemap
Sem 4   FASE 1C fusión Semaglutida   ||  medición piloto
Sem 5-6 FASE 3 resto de monografías por lotes de 4 + consolidación 301
Sem 7   FASE 4 limpieza (schema Offer, SKU, blog, correo de reseñas activo)
Sem 8   FASE 5 medición
Sem 12  FASE 5 medición
```

Lo único que **no puede solaparse**: Fase 1A con Fase 1C (hay que poder atribuir una caída a una fusión concreta, dos semanas de separación mínimo), y la publicación de cualquier monografía con la Fase 1B sin terminar (sin `pt_monografia_sitemap` las páginas no existen para Google y nadie se entera, porque el sitemap se sigue generando sin error).

---

## 2. LAS FASES, UNA POR UNA

### Protocolo de verificación V (se aplica igual en todas las fases)

1. `php -l` sobre cada archivo **antes** del `scp`. Un error de sintaxis en `mu-plugins/` tumba el sitio entero.
2. `scp -P 65002 -i ~/.ssh/cmlc` al servidor.
3. Purgar las dos cachés: `wp litespeed-purge all` **y** hcdn por hPanel → Rendimiento → CDN. LiteSpeed no purga hcdn.
4. `curl` anónimo con UA de navegador: código HTTP, `<title>`, `canonical`, `robots`, y `grep` de los `@type` del JSON-LD. Para confirmar el CDN: pedir la URL **exacta** (sin `?nc=`) 10 veces y agrupar por `x-hcdn-request-id`; hcdn se refresca por edge.
5. `rediseno/herramientas/verificar.py` — **página entera, 1440 y 390 px, antes y después, contenido idéntico salvo lo aprobado**. Más `revisar.py` para la lectura visual.
6. Si se tocó `_elementor_data`: `json.loads()` sobre el resultado. El HTTP 200 no detecta comillas sin escapar; ya casi rompió 6 fichas una vez.
7. **Quién verifica: el coordinador re-verifica lo que entrega cada agente.** Ningún agente se autocertifica. Es la regla que ya está escrita en `pys-verificacion-antes-despues`.

---

### FASE 0 — Decisiones y respaldo (bloqueante, sin tocar nada)

**Qué se toca:** nada en el sitio. Solo repo local.

- Respaldo completo antes de nada: `scp -r .../wp-content/mu-plugins/` → `C:\Users\gabom\Proyectos\ecommerce-agent\rediseno\respaldos\monografias-20260922\`.
- Exportar íntegros los posts 790, 793, 1689, 1518 (post_content, `_elementor_data`, todos los metas de Rank Math, `_sku`, `_price`, `_stock`) → `rediseno\respaldos\fusion-20260922\`.
- Fotografiar `wp_woocommerce_attribute_taxonomies` con sus dos filas `gramaje` (`wp eval` con `$wpdb`; **`wp db query` no funciona**, proc_open deshabilitado).
- Congelar `C:\Users\gabom\Proyectos\ecommerce-agent\rediseno\regla-protocolos.md`: la regla en una frase, la plantilla de 5 columnas, el pie de cita fijo y la lista de 16 comprobaciones del estudio 4. **Sin este archivo la regla vive en una conversación y se pierde en la siguiente.**
- Cerrar las decisiones del apartado 4.

**Verificación:** que los respaldos abren y que el `.md` está commiteado (rama aparte; recordar que `rediseno/` tiene hoy 6 rutas sin seguimiento en git).

**Carril C arranca aquí:** el dueño empieza a capturar los COA de los 21 productos que no lo tienen. Hoy solo el 19 (Retatrutida, lote AA54YCH, pureza 99.76) tiene `_pys_coa`.

---

### FASE 1A — Fusión de MOTS-c (ventana 1)

**Por qué primero:** `/product/mots-c-40mg/` ya lleva `<link rel="canonical">` a `/product/mots-c-10mg/`, su propio texto dice que es la misma molécula, no tiene COA, no tiene reseñas y nunca se ha vendido. Google ya la trata como duplicado: no se cede nada.

**Qué se toca:**
- `wp term create pa_gramaje "40 mg"` — **sobre la taxonomía, nunca sobre la tabla `woocommerce_attribute_taxonomies`.** El duplicado (ids 1 y 2) se deja en paz en esta ventana.
- Producto **790** → variable, `pa_gramaje` con 10 mg y 40 mg marcado «usado para variaciones». Variación 10 mg: $1200, SKU `MOTSC-10MG`, imagen 2272. Variación 40 mg: $2800, SKU `MOTSC-40MG`, imagen 2273.
- **SKU del padre: `MOTSC` (código de molécula), no el de una variación.** Éste es el defecto que arrastra Tirzepatida (padre `TIRZ-30MG`, variaciones `TIRZE-30MG`/`TIRZE-60MG`) y que alimenta un `mpn` que no existe. No se replica.
- Imagen destacada genérica nueva `MOTS-c-v4.png` sin gramaje, al estilo de `BPC-157-v4.png`. Galería 2272 + 2273.
- Regenerar `wc_product_meta_lookup` y `wc_product_attributes_lookup`; limpiar `_elementor_element_cache`.
- Reescribir el cuerpo de 790 **desde el editor de Elementor** (sale de `_elementor_data`, y hoy dice literalmente «esta ficha corresponde al vial de 10 mg»). Sin dosis, ciclos ni vías: encuadre de investigación.
- Producto **793 → borrador** (no borrar). Regla 301 en Redirection de `/product/mots-c-40mg/` a `/product/mots-c-10mg/`, **sin regex y sin anclar con `$`**, igual que las reglas 16 y 17 que ya funcionan para Tirzepatida.
- Repuntar los **12 enlaces internos** a `/product/mots-c-40mg/`: 8 en `post_content` (páginas 24, 26, 1551 y posts 1675, 1926, 2096, 2256, 2462) y 4 en `_elementor_data` (24, 26, 643 y el propio 790), donde **las barras van escapadas `\/`**.

**Verificación:** protocolo V completo. Además, específicamente: que `/product/mots-c-10mg/` pinta el selector con los dos precios; que `/product/mots-c-40mg/` devuelve 301 y no 404; que el JSON-LD sale como `AggregateOffer` con un `mpn` que **sí existe**; captura a 1440 y 390.

**Rollback:** 793 vuelve a `publish`, se borra la regla 301, 790 vuelve a simple desde el respaldo.

**Después:** dos semanas de espera y nueva medición de esas URLs en Search Console antes de tocar Semaglutida.

---

### FASE 1B — Infraestructura de monografías (paralela a 1A, no se pisan)

**Qué se toca — archivo nuevo `wp-content/mu-plugins/pys-monografias.php`:**

1. `register_post_type('monografia')` en `init`: `public=true`, **`has_archive=false`** (si se pone archivo, la plantilla #155 «Elementor Archive» con condición `include/archive` se apodera de `/monografia/`), `hierarchical=false`, `rewrite => ['slug'=>'monografia','with_front'=>false]`, supports title/editor/excerpt/thumbnail/custom-fields/revisions, `show_in_rest=true`, etiquetas en español.
2. `register_post_meta('monografia','_pys_producto_id')` — un solo dato que da los dos sentidos del enlace, sin doble contabilidad.
3. **El filtro que yo añado y que ningún estudio propuso:** neutralizar `redirect_canonical` cuando la petición empieza por `/monografia/`, para que una monografía todavía no publicada devuelva 404 limpio en vez de mandar al usuario y al robot a la ficha equivocada. Medido arriba: hoy `/monografia/semaglutida/` manda a `/product/semaglutida-20mg/`. **Esto tiene que estar en producción antes de la Fase 1C.**
4. Migas propias `Inicio › Monografías › <molécula>` + JSON-LD `BreadcrumbList`, acotado a `is_singular('monografia')`. Rank Math las tiene apagadas (`"breadcrumbs":"off"`) y la ficha no emite `BreadcrumbList` hoy.
5. JSON-LD `WebPage` + `about: MolecularEntity` (nombre, alternateName, `molecularFormula`, `molecularWeight`, identificador CAS, `hasBioChemEntityPart: Protein` con la secuencia, `sameAs` a PubChem) + `citation[]` por referencia + `reviewedBy`. **Explícitamente NO `MedicalWebPage`**: lleva `medicalAudience: Patient`, que es justo el encuadre que el sitio está evitando; el competidor tampoco lo usa en su compendio. El `MedicalWebPage` que ya inyecta `pys-seo-tweaks.php` se queda donde está, en la ficha (`is_singular('product')`).
6. Bloque «Disponible para investigación» al final del contenido de la monografía, con enlace a la ficha.
7. Enlace inverso en la ficha: `woocommerce_single_product_summary` prioridad **45** (después del botón de compra en 30 y del meta en 40, antes de las pestañas). Ancla descriptiva: «Monografía científica de la Retatrutida», no «leer más». **No pisar** `pys-seo-tweaks.php`, que ya usa `woocommerce_after_single_product_summary` en 11.
8. Un comentario de cabecera que diga, en el propio archivo, que si se borra este plugin las 22 URLs devuelven 404 de golpe.

**Capa de diseño — archivo nuevo `wp-content/mu-plugins/pys-diseno/monografias.php`** (una sola función `pys_dis_css_monografias()`, partiendo del CSS de `blog.php`, que es el que ya viste prosa larga con h2/h3/tablas). Y en **`pys-diseno.php` y solo ahí**: añadir `'monografias'` al `foreach` de familias, definir `pys_dis_es_monografia() { return is_singular('monografia') || is_page('monografia'); }`, añadirla al mapa `$familias` del `wp_head`, y añadir `is_page('monografia')` a `pys_dis_pagina_especial()` para que el hub no reciba además la hoja de `paginas-planas`.

La cabecera (plantilla 1099) y el pie (205) se aplican solos: su condición es `include/general` y `pys_dis_ajena()` solo excluye `is_front_page()`. El tema `hello-elementor 3.4.7` no tiene `single.php` ni `singular.php`, así que la entrada se pinta como H1 + contenido plano.

**Sitemap — el paso que se olvida y no avisa:**
```
wp option patch update rank-math-options-sitemap pt_monografia_sitemap on
wp rankmath sitemap generate
```
Comprobado en el código: `includes/modules/sitemap/providers/class-post-type.php:78` exige `sitemap.pt_<tipo>_sitemap`, y esa clave no existe → `handles_type('monografia')` devuelve `false`. Sin esto las monografías quedan fuera y **el sitemap se sigue generando sin error**.

**Hub:** página normal (Gutenberg / HTML plano, **nunca Elementor**) con slug `monografia`, con el índice y la **tabla de identidad química** (CAS, fórmula, peso molecular). Es lo que hace que el hub valga por sí mismo; el competidor tiene esa tabla con 106 compuestos.

**Verificación:** `wp rewrite flush --hard`; `curl -I` sobre una monografía de prueba → 200; sobre `/monografia/<slug-inexistente>/` → **404, no 301**; sobre `/monografia/` → 200 con el hub; `/sitemap_index.xml` lista `monografia-sitemap.xml`. Protocolo V completo. **Dejar el mu-plugin 48 h estable antes de publicar contenido encima.**

---

### FASE 1C — Fusión de Semaglutida (ventana 2, mínimo 2 semanas después de 1A)

Es el caso caro y hay que decirlo: `/product/semaglutida-20mg/` (1518) **es auto-canónica**, tiene sus propias focus keywords (`semaglutida 20mg, semaglutida alta dosis, semaglutida vial 20mg`) y `/product/semaglutida-5-mg/` tiene 158 impresiones en 28 días. Aquí sí se cede algo que Google hoy considera página distinta.

**Antes de ejecutar:** sacar de Search Console impresiones y clics por URL de las cuatro (`mots-c-40mg`, `mots-c-10mg`, `semaglutida-20mg`, `semaglutida-5-mg`) con ventana de 90 días. El endpoint interno (`web.py:7353`, `fetch_gsc_data` en 6784) está fijado a 28 días y 10 filas por clics, así que hay que ampliarlo o consultar desde la interfaz.

**Qué se toca:** término «20 mg» en `pa_gramaje`; 1689 → variable (5 mg $800 imagen 2278; 20 mg $1400 imagen 2277, hoy agotada); SKU del padre `SEMA`; destacada genérica `Semaglutida-v4.png`; 1518 → borrador; 301 de `/product/semaglutida-20mg/` a `/product/semaglutida-5-mg/`; 7 enlaces internos repuntados, incluida la landing 1750 «Semaglutida en México 2026». Y **resolver el agua bacteriostática incluida**, que hoy solo existe en la presentación de 5 mg (junto con GHK-Cu 2823 y Retatrutida 19): las descripciones de las 4 variaciones existentes están vacías, así que si nadie decide, el regalo se pierde en silencio.

**Verificación:** protocolo V + comprobar que `/monografia/semaglutida/` ya **no** manda a un borrador (el filtro de 1B tiene que estar arriba).

---

### FASE 2 — Reseñas (paralela a las monografías, no comparte archivos)

El dueño pidió «la sección en cada producto como ellos» y va a pedir calificaciones a clientes. Técnicamente no falta nada: ya está todo activo y la pestaña ya se pinta. **Lo que falta es honestidad y visibilidad.** Orden obligatorio:

**Paso 1 — el buzón, antes que nada.** Los avisos de reseña pendiente van a `enlace@grupoptm.com`, del dominio anterior, y con `comment_previously_approved=1` la primera reseña de cada persona queda retenida. Si nadie lee ese buzón, el cliente que se tomó la molestia no ve publicado su texto. Filtro sobre `comment_moderation_recipients` y `comment_notification_recipients` hacia `ventas@peptidosysuplementos.mx` (recomendado) o cambiar `admin_email`. Probar con una reseña de prueba que luego se borra.

**Paso 2 — cerrar la puerta.** `woocommerce_review_rating_verification_required` → `yes`. Hoy está en `no`: cualquiera con el enlace puede dejar cinco estrellas sin haber comprado nunca. Si la promesa es «reseñas de clientes reales», el sitio tiene que poder sostenerla técnicamente. **Costo medido y hay que aceptarlo: solo habilita pedidos en `processing` o `completed`, y de 6 pedidos históricos 4 están cancelados → 2 clientes habilitados.**

**Paso 3 — sacar las valoraciones de la tercera pestaña.** Archivo nuevo `wp-content/mu-plugins/pys-resenas.php` (**nunca dentro de `pys-diseno/ficha.php`, que es solo CSS**): quitar `'reviews'` del filtro `woocommerce_product_tabs` y llamar a `comments_template()` en `woocommerce_after_single_product_summary` **prioridad 20** — después del panel de COA (prio 9) y de las pestañas (prio 10). Como el CSS cuelga del id `#reviews` que pinta `single-product-reviews.php`, el bloque «── valoraciones ──» de `ficha.php` líneas 474-500 sigue aplicando sin tocarlo.

**Paso 4 — estado vacío honesto.** Mientras `get_review_count() == 0`: **no** pintar estrellas vacías, ni «0.0 de 5», ni el cartel «Valoraciones (0)», que hoy es lo peor de la ficha. Una línea sobria más, si el producto tiene COA, el enlace al certificado del lote. El formulario sigue accesible.

**Paso 5 — la solicitud automática.** `woocommerce_order_status_completed` → `as_schedule_single_action(time() + 14*DAY_IN_SECONDS, 'pys_pedir_resena', [$order_id])`. Action Scheduler está vivo (última acción completada 2026-09-22 19:31:48, 15 pendientes). Guardas en el manejador: salir si reembolsado/cancelado, si el cliente ya reseñó, o si ya se envió (meta `_pys_resena_solicitada`). **Solo pedidos futuros, nunca retroactivo.** Enlace directo `/product/<slug>/#tab-reviews`: WooCommerce abre la pestaña sola con ese hash (`single-product.js:18`) y ese JS sí llega dentro del bundle de LiteSpeed.

**Paso 6 — el texto del correo** dirige la reseña a empaque, etiquetado, entrega y atención, y dice explícitamente que no se publican reseñas que describan uso en personas. **Sin descuento, cupón ni regalo a cambio**: además de sesgar, va contra las políticas de reseñas de Google. El texto completo del estudio 2 (paso 8) está revisado y no contiene la palabra prohibida ni menciona refrigeración en transporte.

**Verificación:** protocolo V, con énfasis en que sacar el panel de las pestañas **cambia el DOM de las 22 fichas** — `verificar.py` a 1440 y 390 sobre las 22, antes y después. Y `grep` de `aggregateRating` en el HTML anónimo antes y después de la primera reseña: con 0 debe seguir sin emitirse (`class-product-woocommerce.php:191` corta si `get_rating_count() < 1`); con la primera aprobada debe aparecer `ratingCount=1`, `reviewCount=1`.

---

### FASE 3 — Monografías, por lotes

**Piloto de 3, de moléculas SIN URL informativa previa:** Cagrilintida (2240), Sermorelina (2231), Timosina Alfa-1 (2230). No canibalizan nada y son prueba limpia.

**Generación por código, nunca por el editor ni por REST:** un archivo de datos por molécula en `rediseno/monografias/<slug>.json` (nombre, alternateName, CAS, fórmula, peso molecular, secuencia, secciones en HTML plano, protocolos con PMID, FAQ) y un `wp eval-file` que haga `wp_insert_post` en `post_status=draft` + `update_post_meta` de `_pys_producto_id`, `rank_math_title`, `rank_math_description` y `rank_math_focus_keyword`. **`rank_math_*` no persiste por el campo `meta` de la REST API** (devuelve 200 y lo ignora en silencio); por `update_post_meta` sí. Y **el `rank_math_title` de las fichas no se toca.**

Cada monografía lleva la sección **«Protocolos de investigación publicados»** con la plantilla de 5 columnas (Estudio · Modelo · Vía · Pauta reportada · Desenlace medido), el PMID enlazado dentro de la celda «Estudio», el aviso de estado de la evidencia antes de la tabla y el pie de cita fijo. **La columna «Modelo» va segunda a propósito: obliga a declarar la especie antes que el número.** La lista de 16 comprobaciones se corre fila por fila; si una respuesta es «no», la fila se borra, no se parchea con una nota al pie.

**Verificación del piloto:** protocolo V sobre las 3 monografías **y sobre las 3 fichas que ganaron el bloque de enlace** (la ficha cambia, así que entra en el antes/después). Más: 200, `<title>`, meta description, robots `index`, JSON-LD presente con `WebPage` + `MolecularEntity` + `BreadcrumbList`, y la URL listada en `monografia-sitemap.xml`.

**Lotes siguientes de 4, solo si el piloto pasa.** En el lote que incluya una molécula con URL informativa previa se ejecuta la decisión D1: los 301 por **mu-plugin en `init`** si son URLs de blog (Rank Math Redirections deja 404 en este stack), o por el plugin Redirection 5.7.5 si son de producto (ahí sí funciona, reglas 16 y 17 lo demuestran con 78 y 49 impactos).

Pedir indexación en GSC con la cuota real (~9-10 URLs/día).

---

### FASE 4 — Limpieza (independiente, cuando se quiera)

- **`pys-merchant-schema.php`**: emitir un `Offer` por variación con su precio y su SKU, para que el `AggregateOffer` no se coma el dato por gramaje en Merchant Center. Corregir el `mpn` del padre de Tirzepatida (1525, hoy `TIRZ-30MG`, que no coincide con ninguna variación), poner SKU al padre de BPC-157 (2464, vacío) y a GHK-Cu (2823).
- Borrar el borrador 1531 («Tirzepatida 60 mg archivado»), cuya canónica apunta a una URL que ya no existe.
- **La fila que ya rompe la regla**, en la ficha 1128 (IGF-1 LR3): «Estudio previo del mismo grupo · Fetos ovinos normales · 6.6 µg·kg⁻¹·h⁻¹, 1 semana». Da una cifra por kilo sin PMID. Localizar la fuente o borrar la fila. **Mientras siga ahí, cualquier agente redactor la citará como precedente de que se vale.**
- Convertir a ancla los PMID en texto plano de las tablas de 19, 1128, 1131 y 2232.
- **El blog, que es el riesgo residual real:** 4 entradas con «dosis recomendada» (1926, 2094, 2096, 2207), 6 con «se recomienda» (1926, 2094, 2207, 2462, 2519, 2521) y la 2070 con «usuarios reportan». Mismo criterio que los lotes 1 y 2 ya aprobados. **Un inspector lee el dominio, no la plantilla.**
- Meter la lista de 16 puntos como compuerta dura en `seo_guardas.py` del agente de blogs (ya está en `main` desde el 21-ago).
- **Reparar el duplicado de `pa_gramaje`** — en ventana propia, con respaldo, y nunca junto a una fusión.

---

### FASE 5 — Medición

A 4 y 8 semanas: clics e impresiones de `/monografia/*` contra `rediseno/seo/linea_base_rediseno.json`; posición de `/product/mots-c-10mg/` y `/product/semaglutida-5-mg/` antes y después; reseñas recibidas por correo enviado. **Con 2 pedidos completados en toda la historia del sitio, el resultado esperado de la campaña de reseñas es cercano a cero, y eso mismo es el argumento para que el esfuerzo del trimestre vaya al COA y al tráfico.**

---

## 3. RIESGOS, POR GRAVEDAD

**1. Regulatorio, en la sección de protocolos (COFEPRIS).** Es literalmente el contenido que se acaba de retirar de 10 páginas, multiplicado por 22 y con la firma de un médico encima. El competidor publica un factor alométrico 6.2 y «~250–500 µg/día para un adulto de 70 kg», más vías, ciclos, stacks, calibre de aguja y analíticas de monitoreo — **y no cita un solo PMID dentro de esa sección**. *Mitigación:* la regla en una frase — un número solo aparece si va en la misma fila que el PMID del estudio que lo publicó y la especie en que se midió; sin especie no hay fila, sin PMID no hay número. Cero conversiones a persona. Lista de 16 puntos como compuerta dura, en el repo y en `seo_guardas.py`. Aclaración que hay que dejar por escrito porque se lee al revés: **los ensayos humanos de retatrutida, tirzepatida y cagrilintida sí se reportan con sus dosis humanas** — son hechos de un ensayo con su n y su diseño, no una pauta. Lo prohibido no es la especie: es la conversión, la recomendación y el imperativo.

**2. Canibalización.** 11 de las 22 moléculas ya tienen URL informativa y esas URLs suman **0 clics en 90 días** (`/igf-1-lr3-que-es.../` 0 clics / 25 impr pos 64; `/mots-c-que-es.../` 0/14 pos 60; `/selank-beneficios-y-dosis/` 0/13 pos 45; `/nad-para-que-sirve/` 0/11 pos 74; `/glp-1/` 0/51 pos 68), mientras las fichas se llevan el tráfico (`/product/igf-1-lr3-1mg/` 9 clics, `/product/retatrutida-30mg/` 6). Publicar 22 monografías sin decidir antes qué pasa con esas 11 añade 22 páginas a competir contra su propia ficha y su propio blog. *Mitigación:* decisión D1 **antes** de escribir una línea; piloto con las 3 que no canibalizan nada; consolidar con 301 lo que tenga 0 clics.

**3. SEO de la fusión.** El precedente del propio sitio es favorable: `/product/tirzepatida/` es hoy la URL de producto **mejor posicionada de PYS** (pos 15.6, 214 impresiones en 28 d) y sigue captando «tirzepatida 60mg» (29 impr, pos 18.3) sin tener URL dedicada. Pero Semaglutida 20 mg es auto-canónica y con keywords propias: ahí sí se cede una página que Google considera distinta, y `semaglutida-5-mg` tiene 158 impresiones que se juegan. *Mitigación:* ventanas separadas por 2 semanas; sacar el dato de 90 días por URL antes de ejecutar (ampliando `web.py:6784`); 301 sin regex y sin anclar con `$` (el query string es global en Redirection); **no renombrar slugs en la misma ventana que la fusión** — es lo único que orfana una URL que hoy recibe impresiones, y hay que poder distinguir de dónde viene un bajón.

**4. Romper el sitio.** Un error de sintaxis en `mu-plugins/` lo tumba entero; `_elementor_data` con comillas sin escapar ya casi rompió 6 fichas y el HTTP 200 no lo detecta. *Mitigación:* `php -l` antes de cada `scp`, `json.loads()` después de cada escritura, respaldo previo siempre.

**5. `pa_gramaje` duplicado.** Dos filas con el mismo `attribute_name` (ids 1 y 2), y ya hay antecedente de que la fila 2 desapareció sola. Crear términos o convertir a variable con el duplicado presente puede dejar variaciones huérfanas de su atributo. *Mitigación:* trabajar solo a nivel de **taxonomía** (`wp term create pa_gramaje`), no tocar la tabla, fotografiarla antes y verificar el selector en la ficha después de cada paso. Reparar el duplicado en ventana propia.

**6. El adivinador de 404 sobre `/monografia/`.** Medido hoy: cada slug aún no publicado manda al usuario y al robot a una ficha. Y `/monografia/semaglutida/` apunta precisamente a la URL que la Fase 1C convierte en borrador. *Mitigación:* el filtro `redirect_canonical` de la Fase 1B **en producción antes de la Fase 1C**.

**7. Sitemap y schema invisibles.** Sin `pt_monografia_sitemap` las 22 quedan fuera y **nadie se entera**, porque el sitemap se sigue generando sin error (`handles_type('monografia') = false`). Y Rank Math no generará schema para el tipo nuevo (`default_rich_snippet = false`). *Mitigación:* los dos pasos son parte de la definición de «hecho» de la Fase 1B, con verificación por `curl` al sitemap y `grep` de los `@type`.

**8. Reseñas.** Hoy cualquiera puede reseñar sin haber comprado; los avisos van a un buzón muerto; y el techo real son **2 reseñas** sobre 22 fichas. *Mitigación:* buzón primero, `verification_required=yes` segundo, estado vacío honesto tercero. **No inyectar `AggregateRating` a mano**: que lo emita WooCommerce cuando existan reseñas reales. Y moderación con criterio escrito: se rechaza la reseña que describa uso, dosis, vía o resultados en personas — una reseña así es un pasivo publicado en la propia ficha, justo después de haber retirado eso de 10 páginas.

**9. Contenido de molde.** 22 páginas con los mismos 10 H2 es lo que Google trata como plantilla. El competidor sostiene 132 compendios porque cada uno lleva CAS, fórmula, peso molecular, secuencia y estudios distintos. *Mitigación:* decisión D2 (no son 22, son 14) y dato duro obligatorio por molécula.

**10. Caché en dos capas.** LiteSpeed con TTL de 7 días y hcdn respondiendo HIT con `Age: 303`. hcdn **no** se purga desde LiteSpeed. *Mitigación:* protocolo V paso 3 y 4, siempre en anónimo.

**11. Dependencia del mu-plugin.** Si alguien borra `pys-monografias.php`, las 22 URLs dan 404 de golpe. *Mitigación:* escrito en la cabecera del archivo y en el respaldo.

**12. El competidor va a rankear mejor en una consulta que no vamos a responder.** Su sección responde literalmente «cuánto BPC-157 me pongo» y la nuestra no. *Mitigación:* asumirlo y no medir la monografía por esa consulta. Si se mide con la vara del competidor, el proyecto parecerá fracasado sin serlo.

---

## 4. DECISIONES DEL DUEÑO, ANTES DE EMPEZAR

**D1 — Las 11 URLs informativas que ya existen** (`bpc-157-para-que-sirve`, `selank-beneficios-y-dosis`, `igf-1-lr3-que-es...`, `mots-c-que-es...`, `agua-bacteriostatica-que-es`, `tirzepatida-para-que-sirve`, `retatrutide-que-es`, `precio-retatrutida`, `tb-500-peptido-recuperacion-atletas`, `ghk-cu-peptido-cobre...`, `/nad-para-que-sirve/`):
 (a) **301 a la monografía** — recomendado para las que dan 0 clics: consolidar cuesta poco y evita competir consigo mismo.
 (b) Coexistir con canónicas distintas y enlace cruzado — solo para `/glp-1/` y `/semaglutida-en-mexico/`, que son hubs comerciales.
 (c) Dejarlas como están — es lo que ya produjo impresiones sin clics en 2026.

**D2 — ¿Cuántas monografías?** Recomiendo **14, no 22**: las 13 moléculas peptídicas (GHK-Cu 2823, BPC-157 2464, Cagrilintida 2240, CJC+Ipamorelina 2232, Sermorelina 2231, Timosina Alfa-1 2230, Selank 1699, Semaglutida 1689, Tirzepatida 1525, IGF-1 LR3 1128, MOTS-c 790, Retatrutida 19) más la combinación BPC-157+TB-500 (795). **Fuera:** los 5 suplementos Nutricost (Glutatión 2234, Complejo B 1161, DIM 1158, Zinc 1154, Omega-3 1151), NAD+ 1131 y Agua Bacteriostática 799. Alternativa: plantilla corta para NAD+ y agua bacteriostática (que es imán de tráfico).

**D3 — Slug superviviente de la fusión:** (a) **conservar el gramaje** (`/product/mots-c-10mg/`, `/product/semaglutida-5-mg/`) — recomendado, cero URLs orfanadas ahora; (b) renombrar a `/product/mots-c/` y `/product/semaglutida/` en una cuarta ventana, más limpio pero orfana una URL que hoy tiene 158 impresiones.

**D4 — Compra verificada para reseñar:** (a) **sí** (recomendado, es lo que sostiene la promesa) — habilita a 2 clientes hoy y a todos los futuros; (b) no, y moderar a mano — más reseñas posibles, pero sin poder demostrar que vinieron de compradores.

**D5 — Buzón de avisos:** (a) **filtro a `ventas@peptidosysuplementos.mx`** sin tocar `admin_email` (recomendado; `admin_email` y las pasarelas siguen en @grupoptm.com por decisión previa); (b) cambiar `admin_email` completo.

**D6 — El agua bacteriostática incluida**, hoy solo en Semaglutida 5 mg: (a) texto de la variación de 5 mg; (b) extenderla a los 20 mg; (c) retirarla. Si nadie decide, se pierde en silencio al fusionar.

**D7 — COA:** ¿existen los certificados de los otros 21 productos? Si no existen para todos los lotes, ¿qué se muestra en las fichas que no lo tengan? Es el trabajo con más retorno del trimestre y es captura, no programación.

**D8 — Firma y fecha de revisión** de cada monografía: ¿Dr. Gavito, cédula 4606965, como en el bloque «Revisado por» de la ficha? ¿Con qué `lastReviewed`?

**D9 — ¿Gasto en textos completos de artículos de pago?** Sin eso, 3 de las 5 filas del ejemplo de BPC-157 salen con «no reportado en el resumen — pendiente de comprobar» (PMID 21030672, 25415472, 36588717). Es honesto, pero si se repite mucho la sección parece más pobre que la del competidor aunque sea más sólida.

**D10 — Encabezado:** (a) **«Protocolos de investigación publicados»** — recomendado, el adjetivo alinea la promesa con lo que hay dentro; (b) «Protocolos de investigación» a secas, como el competidor: capta igual pero promete lo que deliberadamente no damos, y eso dispara rebote.

**D11 — Reparto ficha / monografía:** (a) ficha con tabla corta (≤6 filas) + enlace, monografía con la versión larga; (b) ficha solo con resumen de dos líneas + enlace. (b) evita mantener el mismo dato en dos sitios pero deja la ficha más corta que la del competidor.

**D12 — Las 9 tablas ya publicadas** (19, 1128, 1131, 1525, 1699, 2230, 2231, 2232, 2240), hoy con 5 esquemas de columnas distintos y 2 encabezados distintos: (a) migrar todas a la plantilla de 5 columnas; (b) **dejarlas y aplicar la plantilla solo de aquí en adelante, arreglando únicamente la fila sin fuente de 1128 y los PMID sin ancla** — recomendado: migrar toca `_elementor_data` de 9 fichas que hoy funcionan, y el riesgo de la limpieza es mayor que el del contenido actual.

**D13 — Los 2 clientes de abril y junio de 2026:** recomiendo **no** mandarles el correo automático (han pasado meses y se lee como descuido). Si el dueño los conoce, un mensaje personal suyo funciona mejor que una plantilla.

---

## 5. LO QUE NO RECOMIENDO

- **Copiar la sección de protocolos del competidor.** Su factor alométrico 6.2 y su rango de 250–500 µg/día para 70 kg es exactamente lo que se acaba de retirar del sitio. Además sus 7 referencias, rotuladas «Estudios Clínicos», son 3 revisiones, 2 estudios in vitro y 2 en rata: ni uno clínico. Se pierde esa consulta y se gana la informativa.
- **Migrar `/product/` a `/producto/`.** El encargo lo da por hecho, pero la base real es `/product/`. Serían 22 fichas con 301 y todas las URLs internas y de `_elementor_data` (con barras escapadas) a revisar, a cambio de nada medible. Es un proyecto aparte y las monografías no dependen de él.
- **Normalizar los 9 slugs con gramaje de presentación única** (`cagrilintida-10mg`, `sermorelina-10mg`, `thymosin-alpha-1-10mg`, `selank-10-mg`, `cjc-1295-ipamorelina-5mg`, `igf-1-lr3-1mg`, `glutation-1500mg`, `agua-bacteriostatica-3ml`). 9 URLs huérfanas a cambio de cero ganancia. Se hace el día que entre el segundo gramaje de cada molécula.
- **Páginas hijas de una página madre, o una taxonomía, en vez del tipo de contenido propio.** Con páginas, las monografías caen en el mismo saco que las políticas y las landings: comparten sitemap, patrón de título, robots y familia de diseño, y separarlas exige listas de IDs a mano — que es justo lo que ya duele (el listado 1551 con URLs empotradas). Con taxonomía solo hay un campo de descripción, sin H2/H3/tablas, y su sitemap está apagado por defecto igual (`tax_product_cat_sitemap` ya está en `off`, con las 7 categorías indexables y fuera del sitemap: ese error ya se pagó una vez).
- **Elementor para las monografías.** Obliga a abrir el editor 14 veces y deja las páginas donde solo se pueden tocar title/meta/slug por API.
- **`has_archive => true`.** La plantilla #155 «Elementor Archive» (condición `include/archive`) se apoderaría de `/monografia/` y se pierde el control del hub.
- **Publicar las 22 de golpe.** Sin piloto medido no hay forma de atribuir nada.
- **Inyectar `AggregateRating` antes de tener reseñas reales.** Es fabricar una señal. Y con una sola reseña de 5 estrellas, el rich result es técnicamente válido pero se lee como manipulado y desaparece si esa reseña se borra.
- **Pedir reseñas antes de arreglar el buzón y de exigir compra verificada.** En ese orden se recogen reseñas que nadie aprueba y que nadie puede demostrar que sean de clientes.
- **Ofrecer descuento, cupón o regalo a cambio de una reseña.**
- **Tocar `wp_woocommerce_attribute_taxonomies` en la misma ventana que una fusión.**
- **`wp db query`** (proc_open deshabilitado) y **Rank Math Redirections** para los 301 de blog (deja 404 en este stack; van por mu-plugin en `init`). Para los 301 de producto sí sirve el plugin Redirection 5.7.5, como demuestran las reglas 16 y 17.
- **Usar `MedicalWebPage` en la monografía.** Lleva `medicalAudience: Patient`, el encuadre que el sitio evita. El que ya inyecta `pys-seo-tweaks.php` se queda en la ficha y no se toca.
- **Dar por buena cualquier fase sin `verificar.py` en 1440 y 390, en anónimo, con LiteSpeed y hcdn purgados, y re-verificada por el coordinador.**