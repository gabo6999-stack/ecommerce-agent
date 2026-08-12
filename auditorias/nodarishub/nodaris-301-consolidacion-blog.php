<?php
/**
 * Plugin Name: Nodaris — 301 de consolidación del blog
 * Description: Redirige las entradas retiradas por canibalización hacia la que se conservó de cada grupo (2026-08-12).
 * Version: 1.0
 *
 * Se hace aquí y no con el módulo de redirecciones de Rank Math porque ese, al
 * crear la redirección y pasar la entrada a borrador, dejaba las URLs en 404 y
 * WordPress las "adivinaba" hacia el post equivocado. El mapa explícito engancha
 * en `init`, antes de que corra la lógica de 404 y su adivinanza de permalinks.
 */

if (!defined('ABSPATH')) {
    exit;
}

add_action('init', function () {
    if (is_admin() || (defined('DOING_AJAX') && DOING_AJAX) || (defined('REST_REQUEST') && REST_REQUEST)) {
        return;
    }

    $mapa = array(
        // Grupo "cómo crear una página web"
        '/como-crear-una-pagina-web/'               => '/como-crear-una-pagina-web-para-negocio-2/',
        '/como-crear-una-pagina-web-para-negocio/'  => '/como-crear-una-pagina-web-para-negocio-2/',
        // Grupo "velocidad de carga"
        '/velocidad-de-carga-web-ventas-seo-pymes/' => '/velocidad-de-carga-de-una-pagina-web/',
        // Grupo "automatización de procesos"
        '/automatizacion-de-procesos-para-pymes/'   => '/que-es-la-automatizacion-de-procesos/',
        // Grupo "google search console"
        '/google-search-console-para-que-sirve/'    => '/google-search-console-tools-guia-pymes-2026/',
        '/para-que-sirve-google-search-console/'    => '/google-search-console-tools-guia-pymes-2026/',
    );

    $ruta = parse_url(isset($_SERVER['REQUEST_URI']) ? $_SERVER['REQUEST_URI'] : '', PHP_URL_PATH);
    if (empty($ruta)) {
        return;
    }
    $ruta = '/' . trim($ruta, '/') . '/';

    if (isset($mapa[$ruta])) {
        wp_redirect(home_url($mapa[$ruta]), 301);
        exit;
    }
});
