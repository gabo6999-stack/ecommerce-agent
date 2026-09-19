# PYS — Portada

La portada rediseñada de `peptidosysuplementos.mx`, empaquetada como plugin de
WordPress. Los productos, los precios, las existencias y los enlaces salen de
WooCommerce; el diseño es el del prototipo `rediseno/home.html`.

## Por qué plugin y no tema hijo

- No hay que saber qué tema usa el sitio, y no se toca el tema en producción.
- Se desactiva con un clic. Un tema hijo mal puesto se arregla por FTP.
- Convive con el tema actual: la tienda, las fichas y el carrito siguen igual.

## Instalación

1. **Escritorio de WordPress → Plugins → Añadir nuevo → Subir plugin**, y
   sueltas `pys-portada.zip`. Actívalo.
2. **Páginas → Añadir nueva.** Ponle el título que quieras (no se ve) y, en el
   panel lateral, **Plantilla → «PYS — Portada»**. Publícala.
3. Ábrela en su propia URL y revísala con calma. **Todavía no es la portada.**
4. Cuando te convenza: **Ajustes → Lectura → Tu página de inicio muestra → Una
   página estática**, y eliges la que creaste.
5. Purga la caché. Con LiteSpeed, «Vaciar todo».

Para deshacer, en cualquier punto: vuelve a poner la portada anterior en
Ajustes → Lectura, o desactiva el plugin.

## Lo que tienes que configurar

### La tipografía

**Optima no viaja en el plugin.** La licencia de escritorio no cubre uso web —
Monotype vende la de webfont aparte— y este repositorio es público. Sin ella la
página cae a Candara / Gill Sans y no se rompe, pero no es la misma página.

Cuando tengas la licencia, deja los dos archivos en `assets/fonts/` con estos
nombres exactos y se enganchan solos:

```
assets/fonts/optima-500.woff2
assets/fonts/optima-400-italic.woff2
```

IBM Plex Mono sí viaja incluido: es OFL y se puede redistribuir.

### El lote en curso

La banda bajo el hero y los rótulos del cromatograma anuncian un lote con su
pureza, su masa y sus endotoxinas. **Si no lo configuras, la banda no se
imprime y el cromatograma se marca como ejemplo.** Es deliberado: publicar un
número de lote inventado sobre una tienda real no es una opción.

Para activarlo, en un snippet de WPCode (tipo PHP) o en el `functions.php` del
tema:

```php
add_filter('pys_portada_lote', function () {
    return [
        'lote'        => 'PYS-2609-RT',
        'producto'    => 'Retatrutida 30 mg',
        'pureza'      => '99.24',
        'masa'        => '4731.3',
        'endotoxinas' => '<0.5 EU',
        'tr'          => '8.42',
    ];
});
```

### Lo que dice cada tarjeta del producto

El prototipo ponía «liofilizado · 99 % HPLC» en todas. Eso es cierto de los
péptidos y falso de los suplementos y del agua bacteriostática, así que el
plugin lo resuelve por producto, en este orden:

1. El atributo **`presentación`** del producto, separado por comas
   (`liofilizado, 99 % HPLC`). Es el que manda, y el único sitio donde debe
   aparecer una pureza: la que esté medida.
2. Si no lo tiene, se deduce de la categoría: «suplemento · cápsulas» para
   Suplementos, «solución estéril» si el nombre lleva «agua», «liofilizado»
   para el resto de péptidos.
3. Si no se puede deducir, la tarjeta solo dice la existencia. Antes callar que
   afirmar de más.

### Las etiquetas cortas de las categorías

Los filtros y el menú usan una etiqueta corta («Metabolismo») en vez del nombre
completo de la categoría. Las siete actuales vienen mapeadas; una categoría
nueva se deduce sola quitándole el arranque repetido. Para ajustarlo:

```php
add_filter('pys_portada_cats_cortas', function ($mapa) {
    $mapa['slug-de-la-categoria'] = 'Etiqueta';
    return $mapa;
});
```

### Datos estructurados

Apagados por defecto. El sitio ya emite schema por su plugin de SEO y duplicar
`Organization`, `WebSite` o `FAQPage` no suma. Si compruebas que no hay
solapamiento:

```php
add_filter('pys_portada_schema', '__return_true');
```

Aun encendido no se declara `offers`: los precios los declara la ficha de cada
producto, que es donde corresponde.

## Qué sale de dónde

| En la página | De dónde |
|---|---|
| Rejilla del catálogo | `wc_get_products()` — publicados y visibles |
| Precio | `get_price_html()`, con moneda, rangos y ofertas ya resueltos |
| «Agotado» | `is_in_stock()` |
| Botón de compra | `add_to_cart_url()` + las clases de `wc-add-to-cart` |
| Imagen del producto | Imagen destacada; si no tiene, un vial sin etiqueta |
| Filtros y menú | `product_cat` con productos |
| Guías | Las 6 entradas publicadas más recientes |
| Carrito y su cuenta | `WC()->cart` |
| Lote, pureza, masa | El filtro `pys_portada_lote` — si no, no se imprime |

## Cómo se probó

Sin acceso al sitio, con un banco que simula las funciones de WordPress y
WooCommerce y renderiza la plantilla de verdad. Eso comprobó que:

- Sin lote configurado no aparece ningún número inventado y la banda no se
  imprime.
- Con lote, los valores interpolan en la banda, en la cabecera del
  cromatograma y en su pie.
- Las categorías no mapeadas caen en la etiqueta deducida.
- Un producto variable sale con «Seleccionar opciones» y sin `ajax_add_to_cart`,
  que es lo correcto: una variable no se añade sin elegir antes.
- Un producto sin imagen destacada cae en el vial de respaldo.

Y después, el HTML resultante en Chromium a 1440 px y 390 px: sin scroll
horizontal, sin errores de JS, con los precios de WooCommerce pintados y el
visor de 360° cargando sus 36 cuadros.

**Lo que esto no cubre**: el tema del sitio, su caché, y cómo se lleve con los
demás plugins. Por eso el paso 3 de la instalación es mirarla en su propia URL
antes de tocar Ajustes → Lectura.

## Peso

Unos 1.2 MB, casi todo los 36 cuadros del visor de 360° (`assets/img/giro/`) y
`motion.js`. Se cargan **solo en esta plantilla**: el resto de la tienda no
arrastra nada.
