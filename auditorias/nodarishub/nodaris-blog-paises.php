<?php
/**
 * Plugin Name: Nodaris — blog por país (/mx/blog/ y /ec/blog/)
 * Description: Mueve las entradas del blog a /<pais>/blog/<slug>/ y redirige las URLs viejas de la raíz. Sustituye a nodaris-301-consolidacion-blog.php.
 * Version: 1.0
 *
 * El resto del sitio ya vivía en /mx/ y /ec/, pero el blog seguía en la raíz.
 * El país de cada entrada se guarda como categoría (`mx` o `ec`) y de ahí sale
 * su permalink, así que mover un artículo de mercado es cambiarle la categoría.
 *
 * Se hace con reglas de reescritura y no poniendo la categoría en la estructura
 * de enlaces permanentes porque una base de categoría `/mx/` chocaría con las
 * páginas /mx/ que ya existen, y WordPress resuelve mal ese conflicto.
 *
 * Los 301 del final incluyen tanto las URLs viejas de la raíz como las entradas
 * retiradas en la consolidación del 2026-08-12, y todos apuntan ya a la URL
 * final para no encadenar redirecciones.
 */

if (!defined('ABSPATH')) {
    exit;
}

const NODARIS_PAISES = array('mx', 'ec');
const NODARIS_RUTAS_VERSION = '1.0';

/** Devuelve 'mx' | 'ec' | '' según la categoría de país de la entrada. */
function nodaris_pais_de_post($post_id) {
    $cache = wp_cache_get($post_id, 'nodaris_pais');
    if ($cache !== false) {
        return $cache;
    }
    $pais = '';
    $terminos = get_the_terms($post_id, 'category');
    if (is_array($terminos)) {
        foreach ($terminos as $t) {
            if (in_array($t->slug, NODARIS_PAISES, true)) {
                $pais = $t->slug;
                break;
            }
        }
    }
    wp_cache_set($post_id, $pais, 'nodaris_pais');
    return $pais;
}

/* ── El permalink que WordPress genera en todos lados ───────────────────────
   Al filtrar post_link, la URL nueva sale sola en el menú, el sitemap de Rank
   Math, el canonical, los enlaces del tema y el campo `link` de la REST API,
   que es de donde lee el buscador de guías. */
add_filter('post_link', function ($url, $post) {
    if (empty($post->ID) || $post->post_type !== 'post') {
        return $url;
    }
    $pais = nodaris_pais_de_post($post->ID);
    if (!$pais) {
        return $url;
    }
    return home_url('/' . $pais . '/blog/' . $post->post_name . '/');
}, 10, 2);

/* ── Que esas URLs resuelvan ─────────────────────────────────────────────── */
add_action('init', function () {
    // El lookahead evita que /mx/blog/page/2/ se interprete como una entrada
    // cuyo slug fuese "page".
    add_rewrite_rule('^(mx|ec)/blog/(?!page/)([^/]+)/?$', 'index.php?name=$matches[2]', 'top');
    add_rewrite_rule('^(mx|ec)/blog/page/([0-9]{1,})/?$',
                     'index.php?pagename=$matches[1]/blog&paged=$matches[2]', 'top');

    // Un mu-plugin no tiene hook de activación: se refrescan las reglas una
    // sola vez por versión, no en cada carga (flush en cada request es caro).
    if (get_option('nodaris_rutas_version') !== NODARIS_RUTAS_VERSION) {
        flush_rewrite_rules(false);
        update_option('nodaris_rutas_version', NODARIS_RUTAS_VERSION);
    }
});

/* ── El listado del shortcode también filtra por país ────────────────────────
   `[nodarishub_blog]` es un snippet de WPCode que vive en la base de datos y no
   acepta atributos. En vez de editarlo (WPCode a veces no regenera su archivo y
   quedaría desincronizado), se le acota la consulta desde aquí: `pre_get_posts`
   corre también para los `new WP_Query`, así que basta reconocer la suya. */
add_action('pre_get_posts', function ($q) {
    if (is_admin() || $q->is_main_query()) {
        return;
    }
    if ($q->get('post_type') !== 'post' || (int) $q->get('posts_per_page') !== 9) {
        return;   // no es la consulta del listado del blog
    }
    $pagina = get_queried_object();
    if (!($pagina instanceof WP_Post) || $pagina->post_type !== 'page') {
        return;
    }
    foreach (NODARIS_PAISES as $p) {
        if (get_page_uri($pagina->ID) === $p . '/blog') {
            $q->set('category_name', $p);
            return;
        }
    }
});

/* ── Redirecciones de las URLs viejas ────────────────────────────────────────
   Engancha en `init`, antes de que corra la lógica de 404 y su adivinanza de
   permalinks, que mandaba las URLs retiradas al artículo equivocado. */
add_action('init', function () {
    if (is_admin() || (defined('DOING_AJAX') && DOING_AJAX) || (defined('REST_REQUEST') && REST_REQUEST)) {
        return;
    }

    // Entradas retiradas en la consolidación por canibalización (2026-08-12).
    // El valor es el SLUG de la que se conservó; el país se resuelve abajo.
    $consolidadas = array(
        'como-crear-una-pagina-web'               => 'como-crear-una-pagina-web-para-negocio-2',
        'como-crear-una-pagina-web-para-negocio'  => 'como-crear-una-pagina-web-para-negocio-2',
        'velocidad-de-carga-web-ventas-seo-pymes' => 'velocidad-de-carga-de-una-pagina-web',
        'automatizacion-de-procesos-para-pymes'   => 'que-es-la-automatizacion-de-procesos',
        'google-search-console-para-que-sirve'    => 'google-search-console-tools-guia-pymes-2026',
        'para-que-sirve-google-search-console'    => 'google-search-console-tools-guia-pymes-2026',
    );

    $ruta = parse_url(isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '', PHP_URL_PATH);
    if (empty($ruta)) {
        return;
    }
    $slug = trim($ruta, '/');

    // Solo interesan las rutas de un nivel: las viejas del blog vivían en la raíz.
    if ($slug === '' || strpos($slug, '/') !== false) {
        return;
    }

    if (isset($consolidadas[$slug])) {
        $slug = $consolidadas[$slug];
    }

    $entrada = get_page_by_path($slug, OBJECT, 'post');
    if (!$entrada) {
        return;   // no es una entrada: que WordPress siga su curso normal
    }

    $destino = get_permalink($entrada->ID);
    if ($destino && untrailingslashit($destino) !== untrailingslashit(home_url($ruta))) {
        wp_redirect($destino, 301);
        exit;
    }
}, 11);

/* ── hreflang de los tres índices del blog ───────────────────────────────────
   Los artículos NO llevan hreflang entre sí: son temas distintos por mercado,
   no traducciones. Los listados sí son equivalentes. El snippet de WPCode que
   maneja el hreflang del resto del sitio no cubre estas páginas. */
add_action('wp_head', function () {
    if (!is_page()) {
        return;
    }
    $actual = get_queried_object_id();
    $indices = array();
    foreach (array('mx', 'ec') as $p) {
        $pagina = get_page_by_path($p . '/blog');
        if ($pagina) {
            $indices[$p] = $pagina->ID;
        }
    }
    $blog_raiz = get_page_by_path('blog');
    $raiz_id = $blog_raiz ? $blog_raiz->ID : 0;

    if ($actual !== $raiz_id && !in_array($actual, $indices, true)) {
        return;
    }
    foreach ($indices as $p => $id) {
        printf('<link rel="alternate" hreflang="es-%s" href="%s" />' . "\n",
               esc_attr(strtoupper($p)), esc_url(get_permalink($id)));
    }
    if ($raiz_id) {
        printf('<link rel="alternate" hreflang="x-default" href="%s" />' . "\n",
               esc_url(get_permalink($raiz_id)));
    }
}, 20);
