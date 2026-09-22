<?php
if (!defined('ABSPATH')) { exit; }
function pys_add_lazy($html) {
if (stripos($html, '</html>') === false) { return $html; }
$n = 0;
return preg_replace_callback('/<img\b(?![^>]*\sloading=)[^>]*>/i', function ($m) use (&$n) {
$n++;
if ($n <= 1) { return $m[0]; }
return preg_replace('/<img\b/i', '<img loading="lazy"', $m[0], 1);
}, $html);
}
add_filter('litespeed_buffer_before', 'pys_add_lazy', 10);
add_action('template_redirect', function () {
if (is_admin() || is_feed()) { return; }
ob_start('pys_add_lazy');
}, 99);
add_action('template_redirect', function () {
if (is_admin() || is_user_logged_in()) { return; }
if (function_exists('is_cart') && (is_cart() || is_checkout() || is_account_page())) { return; }
header('Cache-Control: public, max-age=300, stale-while-revalidate=600', true);
}, 99);

/* -- PYS Medical Schema (E-E-A-T) - revisor medico fijo ----------------- */
/* Movido desde hello-elementor/functions.php el 2026-07-30: el theme padre
   se sobreescribe en cada actualizacion. Acotado a fichas de producto. */
if (!function_exists('pys_medical_reviewer')) {
function pys_medical_reviewer() {
    return array(
        '@type'           => 'Person',
        'name'            => 'Antonio Gavito Hernández',
        'honorificPrefix' => 'Dr.',
        'jobTitle'        => 'Médico cirujano',
        'identifier'      => array(
            '@type'      => 'PropertyValue',
            'propertyID' => 'Cédula profesional (México)',
            'value'      => '4606965',
        ),
        'description'     => 'Práctica enfocada en medicina de longevidad y terapias con péptidos',
    );
}
}

if (!function_exists('pys_medical_schema')) {
function pys_medical_schema() {
    if (!is_singular('product')) { return; }
    global $post;
    $schema = array(
        '@context'            => 'https://schema.org',
        '@type'               => 'MedicalWebPage',
        'name'                => get_the_title($post->ID),
        'url'                 => get_permalink($post->ID),
        'lastReviewed'        => get_the_modified_date('Y-m-d', $post->ID),
        'reviewedBy'          => pys_medical_reviewer(),
        'medicalAudience'     => array('@type' => 'Patient'),
        'isAccessibleForFree' => true,
        'inLanguage'          => 'es-MX',
    );
    echo '<script type="application/ld+json">' . wp_json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</' . 'script>';
}
add_action('wp_head', 'pys_medical_schema');
}

/* -- Bloque visible "Revisado por" en fichas de producto ---------------- */
if (!function_exists('pys_revisado_por')) {
function pys_revisado_por() {
    if (!function_exists('is_product') || !is_product()) { return; }
    echo '<div class="pys-revisado-por" style="margin:2rem 0;padding:1.25rem 1.5rem;border-left:3px solid #b8860b;background:rgba(17,17,17,.58);border-radius:4px;">'
       . '<p style="margin:0 0 .4rem;font-weight:600;">Revisado por:</p>'
       . '<p style="margin:0;font-weight:600;">Dr. Antonio Gavito Hernández</p>'
       . '<p style="margin:.2rem 0 0;">Médico cirujano — Cédula profesional 4606965</p>'
       . '<p style="margin:.2rem 0 0;">Práctica enfocada en medicina de longevidad y terapias con péptidos.</p>'
       . '</div>';
}
add_action('woocommerce_after_single_product_summary', 'pys_revisado_por', 11);
}

/* -- Una sola meta descripción por página -------------------------------
   hello-elementor imprime en wp_head su propia <meta name="description">
   sacada del post_excerpt, que en las fichas es la descripción corta. Eso
   deja DOS metas en 44 páginas publicadas: la de Rank Math (la que se
   quiere) y esa. Google elige una de las dos y no avisa cuál. El tema
   ofrece este filtro justo para apagarla; se apaga aquí y no en su
   functions.php para que una actualización del tema no lo revierta. */
add_filter( 'hello_elementor_description_meta_tag', '__return_false' );
