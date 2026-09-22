<?php
/**
 * Plugin Name: PYS - Related products sin duplicar
 * Description: Quita el bloque nativo "Productos relacionados" de WooCommerce SOLO en las
 *              fichas que ya incluyen su propia seccion curada dentro de la descripcion,
 *              para evitar el encabezado duplicado. Las fichas que no la traen conservan
 *              el bloque nativo (siguen teniendo enlaces internos).
 * Author: Ecommerce Agent
 * Version: 1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_action(
	'wp',
	function () {
		if ( ! function_exists( 'is_product' ) || ! is_product() ) {
			return;
		}

		$post_id = get_queried_object_id();
		if ( ! $post_id ) {
			return;
		}

		$needle = 'Productos relacionados';

		$content = get_post_field( 'post_content', $post_id );
		$has_own = ( is_string( $content ) && stripos( $content, $needle ) !== false );

		// El cuerpo de las fichas puede vivir en la copia de Elementor.
		if ( ! $has_own ) {
			$elementor = get_post_meta( $post_id, '_elementor_data', true );
			if ( is_string( $elementor ) && stripos( $elementor, $needle ) !== false ) {
				$has_own = true;
			}
		}

		if ( $has_own ) {
			remove_action( 'woocommerce_after_single_product_summary', 'woocommerce_output_related_products', 20 );
		}
	},
	20
);
