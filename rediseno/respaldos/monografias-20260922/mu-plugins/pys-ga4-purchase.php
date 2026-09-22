<?php
/**
 * Plugin Name: PYS — evento purchase de GA4
 * Description: Emite el evento `purchase` de GA4 en la pagina de pedido recibido.
 *
 *   POR QUE EXISTE ESTE ARCHIVO
 *   El plugin WooCommerce Google Analytics Integration engancha su purchase al hook
 *   `woocommerce_thankyou` (includes/class-wc-abstract-google-analytics-js.php).
 *   En PYS ese hook NUNCA dispara porque la pagina de pedido recibido la renderiza
 *   Elementor y no la plantilla clasica `thankyou.php`. Comprobado con un log temporal:
 *   el tracker SI se instancia y hay 23 callbacks registrados en el hook, pero el hook
 *   no se ejecuta, asi que `script_data` termina con `cart, list_name` y sin `order`.
 *   Resultado: 0 compras en GA4 con pedidos reales en Woo.
 *
 *   POR QUE NO USA EL PLUGIN
 *   Se emite el gtag propio con `send_to` explicito porque en el sitio hay DOS etiquetas
 *   apuntando a la misma propiedad (G-6WS0BBKFVN del plugin de Woo y GT-PLHFTMX3 de
 *   Site Kit con useSnippet=1). Un `gtag('event')` sin `send_to` llegaria a las dos y
 *   contaria la compra doble.
 *
 *   ANTI-DUPLICADO
 *   Marca el pedido con `_pys_ga4_purchase_sent` y tambien con `_ga_tracked` (la bandera
 *   del propio plugin), asi que si algun dia `woocommerce_thankyou` vuelve a disparar,
 *   el plugin se saltara el pedido y no habra dos compras.
 *
 *   LIMITE CONOCIDO
 *   Esto es medicion en el navegador: si el cliente paga en MercadoPago y cierra la
 *   pestana sin volver, la pagina de gracias no se carga y la compra no se registra.
 *   Para cubrir ese caso hace falta el Measurement Protocol (server-side), que necesita
 *   un API secret de GA4. El client_id se guarda ya en el pedido para poder hacerlo.
 *
 * Version: 1.0
 */

defined( 'ABSPATH' ) || exit;

const PYS_GA4_ID = 'G-6WS0BBKFVN';

/**
 * Guarda el client_id de GA4 (cookie _ga) en el pedido al crearlo.
 * Sin esto, una compra enviada mas tarde desde el servidor no se puede atribuir
 * a la sesion original y GA4 la marcaria como directa.
 */
add_action( 'woocommerce_checkout_update_order_meta', function ( $order_id ) {
	if ( empty( $_COOKIE['_ga'] ) ) {
		return;
	}
	// La cookie viene como GA1.1.<client_id>  ->  nos quedamos con los 2 ultimos campos.
	$partes = explode( '.', sanitize_text_field( wp_unslash( $_COOKIE['_ga'] ) ) );
	if ( count( $partes ) >= 4 ) {
		$cid = $partes[ count( $partes ) - 2 ] . '.' . $partes[ count( $partes ) - 1 ];
		$order = wc_get_order( $order_id );
		if ( $order ) {
			$order->update_meta_data( '_pys_ga4_client_id', $cid );
			$order->save();
		}
	}
}, 10, 1 );

/** Devuelve el pedido de la pagina de gracias, solo si la clave de la URL es valida. */
function pys_ga4_pedido_de_la_pagina() {
	if ( is_admin() || ! function_exists( 'is_order_received_page' ) || ! is_order_received_page() ) {
		return null;
	}

	global $wp;
	$order_id = 0;
	if ( isset( $wp->query_vars['order-received'] ) ) {
		$order_id = absint( $wp->query_vars['order-received'] );
	}
	if ( ! $order_id && isset( $_GET['order-received'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification.Recommended
		$order_id = absint( $_GET['order-received'] ); // phpcs:ignore WordPress.Security.NonceVerification.Recommended
	}
	if ( ! $order_id ) {
		return null;
	}

	$order = wc_get_order( $order_id );
	if ( ! $order ) {
		return null;
	}

	// phpcs:ignore WordPress.Security.NonceVerification.Recommended,WordPress.Security.ValidatedSanitizedInput.InputNotSanitized
	$key = empty( $_GET['key'] ) ? '' : wc_clean( wp_unslash( $_GET['key'] ) );
	if ( ! $order->key_is_valid( $key ) ) {
		return null;
	}

	return $order;
}

add_action( 'wp_footer', function () {

	// Mismo criterio que el plugin: a los administradores no se les mide.
	if ( current_user_can( 'manage_options' ) ) {
		return;
	}

	$order = pys_ga4_pedido_de_la_pagina();
	if ( ! $order ) {
		return;
	}

	// Una sola vez por pedido.
	if ( '1' === (string) $order->get_meta( '_pys_ga4_purchase_sent' ) ) {
		return;
	}

	$items = array();
	foreach ( $order->get_items() as $item ) {
		$producto = $item->get_product();
		$cats     = array();
		if ( $producto ) {
			$terminos = get_the_terms( $producto->get_id(), 'product_cat' );
			if ( $terminos && ! is_wp_error( $terminos ) ) {
				$cats = wp_list_pluck( $terminos, 'name' );
			}
		}
		$cantidad = max( 1, (int) $item->get_quantity() );
		$entrada  = array(
			// El plugin usa `product_id` como identificador (ga_product_identifier), se respeta.
			'item_id'   => (string) ( $producto ? $producto->get_id() : $item->get_product_id() ),
			'item_name' => $item->get_name(),
			'quantity'  => $cantidad,
			'price'     => round( (float) $order->get_line_subtotal( $item, false, false ) / $cantidad, 2 ),
		);
		if ( ! empty( $cats[0] ) ) {
			$entrada['item_category'] = $cats[0];
		}
		if ( $producto && $producto->get_sku() ) {
			$entrada['item_variant'] = $producto->get_sku();
		}
		$items[] = $entrada;
	}

	$payload = array(
		'send_to'        => PYS_GA4_ID,   // evita que la compra llegue tambien a GT-PLHFTMX3
		'transaction_id' => (string) $order->get_order_number(),
		'value'          => round( (float) $order->get_total(), 2 ),
		'tax'            => round( (float) $order->get_total_tax(), 2 ),
		'shipping'       => round( (float) $order->get_shipping_total(), 2 ),
		'currency'       => $order->get_currency(),
		'items'          => $items,
	);

	$cupones = $order->get_coupon_codes();
	if ( ! empty( $cupones ) ) {
		$payload['coupon'] = implode( ',', $cupones );
	}

	// Marcar ANTES de imprimir: si algo falla despues, no se reintenta en bucle.
	// `_ga_tracked` es la bandera del plugin de Woo: evita una segunda compra
	// si algun dia `woocommerce_thankyou` vuelve a dispararse.
	$order->update_meta_data( '_pys_ga4_purchase_sent', 1 );
	$order->update_meta_data( '_ga_tracked', 1 );
	$order->save();

	?>
<script id="pys-ga4-purchase">
window.dataLayer = window.dataLayer || [];
function pysGtag(){ window.dataLayer.push(arguments); }
( function () {
	var enviar = function () {
		var g = ( typeof window.gtag === 'function' ) ? window.gtag : pysGtag;
		g( 'event', 'purchase', <?php echo wp_json_encode( $payload ); ?> );
	};
	if ( typeof window.gtag === 'function' ) { enviar(); }
	else { document.addEventListener( 'DOMContentLoaded', enviar ); }
} )();
</script>
	<?php
}, 20 );
