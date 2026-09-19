<?php
/**
 * Plugin Name:  PYS — Portada
 * Description:  La portada rediseñada de Péptidos y Suplementos, como plantilla de página. Lee productos, precios y existencias de WooCommerce.
 * Version:      1.0.0
 * Requires PHP: 7.4
 * License:      GPL-2.0-or-later
 *
 * Va como plugin y no como tema hijo a propósito: así no hay que saber qué
 * tema usa el sitio, no se toca el tema en producción, y si algo sale mal se
 * desactiva con un clic en vez de tener que restaurar archivos por FTP.
 */

if (!defined('ABSPATH')) exit;

define('PYS_PORTADA_VER', '1.0.0');
define('PYS_PORTADA_URL', plugin_dir_url(__FILE__));
define('PYS_PORTADA_DIR', plugin_dir_path(__FILE__));

/* ── La plantilla ──────────────────────────────────────────────────────
   Se ofrece como plantilla de página para cualquier tema. Creas una página,
   le asignas «PYS — Portada», la revisas en su propia URL, y solo cuando te
   convenza la marcas como portada en Ajustes → Lectura. Nunca al revés. */

add_filter('theme_page_templates', function ($plantillas) {
    $plantillas['pys-portada'] = __('PYS — Portada', 'pys-portada');
    return $plantillas;
});

function pys_portada_es_esta_pagina() {
    return is_page() && get_page_template_slug(get_queried_object_id()) === 'pys-portada';
}

add_filter('template_include', function ($plantilla) {
    return pys_portada_es_esta_pagina() ? PYS_PORTADA_DIR . 'plantilla-portada.php' : $plantilla;
});

/* ── Tipografía ────────────────────────────────────────────────────────
   Optima NO viaja en el plugin: la licencia de escritorio no cubre uso web
   y este código es público. Si compras la licencia de webfont, deja los
   .woff2 en assets/fonts/ con estos nombres y se enganchan solos; si no
   están, la página cae al respaldo del sistema sin romperse. */

function pys_portada_hay_optima() {
    return file_exists(PYS_PORTADA_DIR . 'assets/fonts/optima-500.woff2');
}

/* ── Los datos de la tienda ────────────────────────────────────────────
   Esto es lo que separa la portada real del prototipo: los precios, las
   existencias y los enlaces salen de WooCommerce, no de un archivo escrito
   a mano. */

function pys_portada_cats() {
    /* El diseño usa una etiqueta corta para los filtros y el menú, y el
       nombre largo de la categoría para todo lo demás. El mapa se puede
       cambiar sin tocar el plugin con el filtro de abajo. */
    $cortas = apply_filters('pys_portada_cats_cortas', [
        'peptidos-para-metabolismo-y-perdida-de-peso' => 'Metabolismo',
        'peptidos-bienestar-general'                  => 'Bienestar',
        'peptidos-reparacion-celular-anti-aging'      => 'Reparación',
        'peptidos-para-rendimiento-cognitivo'         => 'Cognitivo',
        'suplementos-deportivos-premium'              => 'Suplementos',
        'peptidos-recuperacion-y-crecimiento-muscular'=> 'Muscular',
        'peptidos-para-rendimiento-deportivo'         => 'Deportivo',
    ]);

    $terminos = get_terms([
        'taxonomy'   => 'product_cat',
        'hide_empty' => true,
        'orderby'    => 'count',
        'order'      => 'DESC',
    ]);
    if (is_wp_error($terminos)) return [];

    $salida = [];
    foreach ($terminos as $t) {
        if ($t->slug === 'uncategorized' || $t->slug === 'sin-categorizar') continue;
        $salida[] = [
            'corto' => $cortas[$t->slug] ?? pys_portada_acorta($t->name),
            'largo' => $t->name,
            'url'   => get_term_link($t),
        ];
    }
    return $salida;
}

function pys_portada_acorta($nombre) {
    /* Para una categoría que no esté en el mapa: se le quitan los arranques
       repetidos («Péptidos para…») y se deja la primera palabra con peso. */
    $limpio = preg_replace('/^(Péptidos|Peptidos|Suplementos)\s+(para|de|y)?\s*/iu', '', $nombre);
    $palabras = preg_split('/\s+/u', trim($limpio ?: $nombre));
    return $palabras[0] ?? $nombre;
}

function pys_portada_productos() {
    if (!function_exists('wc_get_products')) return [];

    $productos = wc_get_products([
        'status'     => 'publish',
        'limit'      => -1,
        'orderby'    => 'menu_order',
        'order'      => 'ASC',
        'visibility' => 'visible',
    ]);

    $cats_cortas = [];
    foreach (pys_portada_cats() as $c) $cats_cortas[$c['largo']] = $c['corto'];

    $respaldo = PYS_PORTADA_URL . 'assets/img/vial-sin-etiqueta.jpg';
    $salida = [];

    foreach ($productos as $p) {
        $nombres_cat = wp_get_post_terms($p->get_id(), 'product_cat', ['fields' => 'names']);
        if (is_wp_error($nombres_cat)) $nombres_cat = [];

        $id_img = $p->get_image_id();
        $img = $id_img ? wp_get_attachment_image_url($id_img, 'woocommerce_single') : '';

        $salida[] = [
            'id'         => $p->get_id(),
            'nombre'     => $p->get_name(),
            'nombreSeo'  => $p->get_name(),
            'slug'       => $p->get_slug(),
            'url'        => get_permalink($p->get_id()),
            'sku'        => $p->get_sku(),
            'existencia' => $p->is_in_stock() ? 'instock' : 'outofstock',
            'cats'       => array_values($nombres_cat),
            'cat'        => $cats_cortas[$nombres_cat[0] ?? ''] ?? '',
            'img'        => $img ?: $respaldo,
            'frasco'     => false,
            'specs'      => pys_portada_specs($p, $nombres_cat),
            /* `precioHtml` es lo que se pinta: WooCommerce ya resuelve ahí la
               moneda, los rangos de variable y el precio tachado en oferta.
               `precio` queda como número por si hace falta ordenar. */
            'precio'     => (float) $p->get_price(),
            'precioHtml' => $p->get_price_html(),
            'comprable'  => $p->is_purchasable() && $p->is_in_stock(),
            'tipo'       => $p->get_type(),
            'addUrl'     => $p->add_to_cart_url(),
            'addTexto'   => $p->add_to_cart_text(),
        ];
    }
    return $salida;
}

function pys_portada_specs($p, $cats) {
    /* El prototipo ponía «liofilizado · 99 % HPLC» en todas las tarjetas.
       Eso es cierto de los péptidos y falso de los suplementos y del agua
       bacteriostática, y en una tienda real una afirmación falsa sobre el
       producto no es un detalle de maquetación.

       Orden: lo que declare el propio producto en un atributo
       «presentación» (separado por comas) manda; si no lo declara, se
       deduce de la categoría; y si no se puede deducir, no se dice nada.
       La pureza no se inventa nunca: si la quieres en la tarjeta, ponla en
       el atributo del producto que la tenga medida. */
    $attr = $p->get_attribute('presentacion');
    if (!$attr) $attr = $p->get_attribute('pa_presentacion');
    if ($attr) {
        $partes = array_filter(array_map('trim', preg_split('/[,|]/u', $attr)));
        if ($partes) return array_values($partes);
    }

    $cat = function_exists('mb_strtolower') ? mb_strtolower(implode(' ', $cats)) : strtolower(implode(' ', $cats));
    $nom = function_exists('mb_strtolower') ? mb_strtolower($p->get_name()) : strtolower($p->get_name());

    if (strpos($cat, 'suplemento') !== false)                 return ['suplemento', 'cápsulas'];
    if (strpos($nom, 'agua') !== false)                       return ['solución estéril'];
    if (strpos($cat, 'péptido') !== false || strpos($cat, 'peptido') !== false) return ['liofilizado'];
    return [];
}

function pys_portada_blog($cuantas = 6) {
    $entradas = get_posts(['numberposts' => $cuantas, 'post_status' => 'publish']);
    $salida = [];
    foreach ($entradas as $e) {
        $salida[] = [
            'titulo'   => get_the_title($e),
            'url'      => get_permalink($e),
            'fecha'    => get_the_date('Y-m-d', $e),
            'palabras' => str_word_count(wp_strip_all_tags($e->post_content)),
        ];
    }
    return $salida;
}

/* ── El lote en curso ──────────────────────────────────────────────────
   La banda del hero y los rótulos del cromatograma anuncian un lote con su
   pureza y su masa. Eso es un dato de laboratorio, no de la tienda: si no se
   configura, la banda NO se imprime y el cromatograma se marca como ejemplo.
   Publicar un número de lote inventado sobre una tienda real no es una
   opción.

   Para activarla, en el functions.php del tema o en un snippet:

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
*/
function pys_portada_lote() {
    $lote = apply_filters('pys_portada_lote', null);
    if (!is_array($lote) || empty($lote['lote'])) return null;
    return wp_parse_args($lote, [
        'producto' => '', 'pureza' => '', 'masa' => '',
        'endotoxinas' => '', 'tr' => '',
    ]);
}

/* ── Carga de estilos y scripts ────────────────────────────────────────
   Solo en esta plantilla: no tiene sentido que el resto de la tienda
   arrastre 140 KB de librería de animación. */

add_action('wp_enqueue_scripts', function () {
    if (!pys_portada_es_esta_pagina()) return;

    wp_enqueue_style('pys-portada', PYS_PORTADA_URL . 'assets/portada.css', [], PYS_PORTADA_VER);

    if (pys_portada_hay_optima()) {
        wp_add_inline_style('pys-portada', pys_portada_css_fuentes());
    }

    wp_enqueue_script('pys-motion',  PYS_PORTADA_URL . 'assets/motion.js',  [], PYS_PORTADA_VER, true);
    wp_enqueue_script('pys-giro360', PYS_PORTADA_URL . 'assets/giro360.js', [], PYS_PORTADA_VER, true);
    wp_enqueue_script('pys-portada', PYS_PORTADA_URL . 'assets/portada.js',
                      ['pys-motion', 'pys-giro360'], PYS_PORTADA_VER, true);

    /* El carrito por AJAX de WooCommerce: sin esto el botón «Agregar»
       recarga la página en vez de añadir en sitio. */
    if (function_exists('WC')) wp_enqueue_script('wc-add-to-cart');

    $datos = [
        'sitio'     => home_url('/'),
        'assets'    => PYS_PORTADA_URL . 'assets/',
        'cats'      => pys_portada_cats(),
        'productos' => pys_portada_productos(),
        'blog'      => pys_portada_blog(),
        'landings'  => apply_filters('pys_portada_landings', []),
        'carrito'   => function_exists('wc_get_cart_url') ? wc_get_cart_url() : home_url('/'),
        'lote'      => pys_portada_lote(),
        /* Apagado por defecto: el sitio ya emite schema por su plugin de SEO
           y duplicar Organization o FAQPage no suma. Se enciende con
           add_filter('pys_portada_schema', '__return_true') si se comprueba
           que no hay solapamiento. */
        'schema'    => (bool) apply_filters('pys_portada_schema', false),
        /* WC() puede devolver null, y el carrito no existe hasta que
           WooCommerce termina de arrancar: sin las dos comprobaciones
           esto suelta un aviso en cada carga. */
        'enCarrito' => pys_portada_en_carrito(),
        'nonce'     => wp_create_nonce('pys_portada'),
    ];
    wp_add_inline_script('pys-portada', 'window.PYS_DATOS = ' . wp_json_encode($datos) . ';', 'before');
}, 20);

function pys_portada_en_carrito() {
    if (!function_exists('WC')) return 0;
    $wc = WC();
    if (!$wc || empty($wc->cart)) return 0;
    return (int) $wc->cart->get_cart_contents_count();
}

function pys_portada_css_fuentes() {
    $f = PYS_PORTADA_URL . 'assets/fonts/';
    return "
@font-face{font-family:'Optima PYS';src:url({$f}optima-500.woff2) format('woff2');
           font-weight:400 700;font-style:normal;font-display:swap}
@font-face{font-family:'Optima PYS';src:url({$f}optima-400-italic.woff2) format('woff2');
           font-weight:400 700;font-style:italic;font-display:swap}";
}

/* ── Aviso en el escritorio ────────────────────────────────────────────
   Dos cosas que se olvidan y se descubren en producción. */

add_action('admin_notices', function () {
    if (!current_user_can('manage_options')) return;
    $pantalla = get_current_screen();
    if (!$pantalla || !in_array($pantalla->id, ['plugins', 'dashboard'], true)) return;

    $faltan = [];
    if (!function_exists('wc_get_products')) {
        $faltan[] = 'WooCommerce no está activo: la rejilla de productos saldrá vacía.';
    }
    if (!pys_portada_hay_optima()) {
        $faltan[] = 'Optima no está en <code>assets/fonts/</code>: la portada usará la tipografía de respaldo. '
                  . 'La licencia de escritorio no cubre uso web; la de webfont se compra aparte.';
    }
    if (!pys_portada_lote()) {
        $faltan[] = 'No hay lote configurado (filtro <code>pys_portada_lote</code>): la banda de lote no se imprime '
                  . 'y el cromatograma se marca como ejemplo, que es lo correcto mientras no haya datos reales.';
    }
    if (!$faltan) return;

    echo '<div class="notice notice-warning"><p><strong>PYS — Portada</strong></p><ul style="list-style:disc;margin-left:20px">';
    foreach ($faltan as $f) echo '<li>' . wp_kses($f, ['code' => []]) . '</li>';
    echo '</ul></div>';
});
