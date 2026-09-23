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

/* -- Por qué la ficha ya NO emite MedicalWebPage -----------------------
   Emitía MedicalWebPage con medicalAudience: Patient en cada ficha. Dos
   problemas, y el primero no es de posicionamiento: la propia ficha dice
   «material destinado exclusivamente a investigación de laboratorio, no para
   consumo humano», así que declararle a Google una audiencia de PACIENTES la
   contradice de frente. El segundo es el reparto: MedicalWebPage empuja la
   ficha a territorio informacional, que es el de /monografia/<slug>/, y las
   dos páginas acaban peleándose la misma consulta.
   El revisor médico no se pierde: sigue visible en la ficha (pys_revisado_por)
   y sigue emitiéndose como reviewedBy en el schema de la monografía, que es la
   página cuya entidad sí es científica. */

/* -- Migas de pan en el schema de las fichas ---------------------------
   Rank Math emite su @graph sin BreadcrumbList (comprobado: Organization,
   WebSite, ImageObject, ItemPage y Product, y nada más). Se añade aquí, con el
   mismo hook que usa el resto del sitio, para que la ruta Inicio › Categoría ›
   Producto quede declarada a máquina igual que la de las monografías. */
add_filter(
    'rank_math/json_ld',
    function ( $datos, $jsonld ) {
        if ( ! function_exists( 'is_product' ) || ! is_product() ) {
            return $datos;
        }
        $id = get_queried_object_id();
        $ruta = array( array( 'nombre' => 'Inicio', 'url' => home_url( '/' ) ) );
        $terminos = get_the_terms( $id, 'product_cat' );
        if ( $terminos && ! is_wp_error( $terminos ) ) {
            $t = reset( $terminos );
            $enlace = get_term_link( $t );
            if ( ! is_wp_error( $enlace ) ) {
                $ruta[] = array( 'nombre' => $t->name, 'url' => $enlace );
            }
        }
        $ruta[] = array( 'nombre' => get_the_title( $id ), 'url' => get_permalink( $id ) );

        $elementos = array();
        foreach ( $ruta as $i => $paso ) {
            $elementos[] = array(
                '@type'    => 'ListItem',
                'position' => $i + 1,
                'name'     => $paso['nombre'],
                'item'     => $paso['url'],
            );
        }
        $datos['pysMigas'] = array(
            '@type'           => 'BreadcrumbList',
            '@id'             => get_permalink( $id ) . '#breadcrumb',
            'itemListElement' => $elementos,
        );
        return $datos;
    },
    20,
    2
);

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
