<?php
/**
 * Plugin Name: PYS — Home 2026
 * Description: Registra la plantilla de página del home rediseñado (dirección
 *              "laboratorio oscuro"). El diseño sale del prototipo; TODO el
 *              contenido —productos, precios, existencias, categorías, guías,
 *              menú, políticas— se lee en vivo de WordPress y WooCommerce.
 * Version:     1.0.0
 *
 * Va como mu-plugin y no dentro del tema porque hello-elementor se actualiza
 * solo y se llevaría la plantilla por delante.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'PYS_H26_SLUG', 'pys-home-2026' );
define( 'PYS_H26_DIR', __DIR__ . '/pys-home-2026' );
define( 'PYS_H26_VER', '1.0.0' );

/**
 * URL base de los estáticos. Viven en uploads y no junto al mu-plugin porque
 * uploads está garantizado como servible; wp-content/mu-plugins/ depende de
 * que el servidor no lo tenga bloqueado.
 */
function pys_h26_uri( $ruta = '' ) {
	$subida = wp_upload_dir();
	return trailingslashit( $subida['baseurl'] ) . 'home-2026' . ( $ruta ? '/' . ltrim( $ruta, '/' ) : '' );
}

/** La plantilla aparece en el desplegable «Atributos de página». */
add_filter(
	'theme_page_templates',
	function ( $plantillas ) {
		$plantillas[ PYS_H26_SLUG ] = 'PYS — Home 2026';
		return $plantillas;
	}
);

add_filter(
	'template_include',
	function ( $plantilla ) {
		if ( ! is_page() ) {
			return $plantilla;
		}
		if ( get_page_template_slug( get_queried_object_id() ) !== PYS_H26_SLUG ) {
			return $plantilla;
		}
		$propia = PYS_H26_DIR . '/template.php';
		return file_exists( $propia ) ? $propia : $plantilla;
	},
	99
);

/** ¿La petición en curso usa esta plantilla? */
function pys_h26_es_nuestra() {
	return is_page() && get_page_template_slug( get_queried_object_id() ) === PYS_H26_SLUG;
}

/**
 * La plantilla no pinta ni un solo widget de Elementor, así que Elementor no
 * imprime `elementorFrontendConfig`… pero sus scripts sí se encolan igual y
 * revientan con un ReferenceError. Como LiteSpeed los combina en un único
 * archivo, ese error corta la ejecución de todo lo que va detrás en el mismo
 * bundle —incluido el «agregar al carrito» de WooCommerce—, así que aquí se
 * quitan de esta página.
 */
add_action(
	'wp_enqueue_scripts',
	function () {
		if ( ! pys_h26_es_nuestra() ) {
			return;
		}
		foreach ( array( 'elementor-frontend', 'elementor-pro-frontend', 'elementor-webpack-runtime', 'elementor-frontend-modules', 'preloaded-modules' ) as $handle ) {
			wp_dequeue_script( $handle );
		}
	},
	9999
);

/**
 * Al cambiar la portada, la página 21 —la portada anterior, en /inicio/— pasó a
 * borrador. Su URL seguía viva en enlaces antiguos y en el índice de Google, así
 * que en vez de dejarla en 404 se manda a la raíz con un 301, que es donde está
 * ahora ese contenido.
 */
add_action(
	'template_redirect',
	function () {
		if ( ! is_404() ) {
			return;
		}
		$ruta = wp_parse_url( isset( $_SERVER['REQUEST_URI'] ) ? esc_url_raw( wp_unslash( $_SERVER['REQUEST_URI'] ) ) : '', PHP_URL_PATH );
		if ( 'inicio' === trim( (string) $ruta, '/' ) ) {
			wp_safe_redirect( home_url( '/' ), 301 );
			exit;
		}
	}
);

/**
 * El contador del carrito del encabezado se refresca con los fragmentos de
 * WooCommerce, igual que el del tema, para que agregar sin recargar se note.
 */
add_filter(
	'woocommerce_add_to_cart_fragments',
	function ( $fragmentos ) {
		if ( ! function_exists( 'WC' ) || ! WC()->cart ) {
			return $fragmentos;
		}
		$n = WC()->cart->get_cart_contents_count();
		$fragmentos['#pys-cart-n'] = '<span class="pys-cart-n" id="pys-cart-n"'
			. ( $n ? '' : ' hidden' ) . '>' . esc_html( $n ) . '</span>';
		return $fragmentos;
	}
);
