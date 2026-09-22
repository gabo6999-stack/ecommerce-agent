<?php
/**
 * Plugin Name: PYS - Schema para Merchant Center
 * Description: Completa el schema Product que genera Rank Math con los campos que exige
 *              Google Merchant Center: identificador de producto (mpn = SKU, ya que la
 *              marca es propia y no hay GTIN) y datos de envio reales tomados de la
 *              configuracion de WooCommerce.
 * Author: Ecommerce Agent
 * Version: 1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_filter(
	'rank_math/snippet/rich_snippet_product_entity',
	function ( $entity ) {

		if ( ! function_exists( 'wc_get_product' ) ) {
			return $entity;
		}

		$product = wc_get_product( get_the_ID() );
		if ( ! $product ) {
			return $entity;
		}

		// --- Nombre del producto ---------------------------------------------
		// Rank Math mete el TITULO SEO en `name` (p.ej. "Comprar Retatrutida 30
		// mg en Mexico | COA por Lote | PyS"). Eso es un titulo, no un nombre de
		// producto: se lo come Merchant Center y los rich results, y ahi se ve
		// como spam. Se fuerza el nombre real del producto de WooCommerce.
		$real_name = $product->get_name();
		if ( $real_name ) {
			// Algunos nombres del catalogo traen su propio "| descriptor";
			// quedarse con la parte anterior a la primera barra vertical.
			$parts = explode( '|', $real_name );
			$clean = trim( $parts[0] );
			$entity['name'] = ( '' !== $clean ) ? $clean : $real_name;
		}

		// --- Identificador de producto ---------------------------------------
		// Marca propia sin GTIN: Google acepta la combinacion marca + MPN.
		// Se usa el SKU como MPN, que es el identificador real del catalogo.
		$sku = $product->get_sku();
		if ( $sku && empty( $entity['mpn'] ) ) {
			$entity['mpn'] = $sku;
		}

		// Producto variable: el SKU puede vivir en las variaciones.
		if ( empty( $entity['mpn'] ) && $product->is_type( 'variable' ) ) {
			foreach ( $product->get_children() as $child_id ) {
				$child = wc_get_product( $child_id );
				if ( $child && $child->get_sku() ) {
					$entity['mpn'] = $child->get_sku();
					break;
				}
			}
		}

		// --- Datos de envio ---------------------------------------------------
		// Tomados de la zona real de WooCommerce; si no se puede leer, no se inventa.
		$rate = null;
		if ( class_exists( 'WC_Shipping_Zones' ) ) {
			foreach ( WC_Shipping_Zones::get_zones() as $zone ) {
				foreach ( $zone['shipping_methods'] as $method ) {
					if ( 'flat_rate' === $method->id && 'yes' === $method->enabled ) {
						$cost = isset( $method->instance_settings['cost'] ) ? $method->instance_settings['cost'] : null;
						if ( is_numeric( $cost ) ) {
							$rate = (float) $cost;
							break 2;
						}
					}
				}
			}
		}

		if ( null !== $rate && ! empty( $entity['offers'] ) && is_array( $entity['offers'] ) ) {
			$shipping = array(
				'@type'               => 'OfferShippingDetails',
				'shippingRate'        => array(
					'@type'    => 'MonetaryAmount',
					'value'    => $rate,
					'currency' => get_woocommerce_currency(),
				),
				'shippingDestination' => array(
					'@type'          => 'DefinedRegion',
					'addressCountry' => 'MX',
				),
				// Politica publicada: "Tiempo estimado: 2 a 5 dias habiles".
				'deliveryTime'        => array(
					'@type'       => 'ShippingDeliveryTime',
					'transitTime' => array(
						'@type'    => 'QuantitativeValue',
						'minValue' => 2,
						'maxValue' => 5,
						'unitCode' => 'DAY',
					),
				),
			);

			if ( isset( $entity['offers']['@type'] ) ) {
				$entity['offers']['shippingDetails'] = $shipping;
			} else {
				foreach ( $entity['offers'] as $i => $offer ) {
					if ( is_array( $offer ) ) {
						$entity['offers'][ $i ]['shippingDetails'] = $shipping;
					}
				}
			}
		}

		return $entity;
	},
	20
);
