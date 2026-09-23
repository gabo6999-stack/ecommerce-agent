<?php
/**
 * Plugin Name: PYS — Catálogo en vivo
 * Description: Shortcode [pys_catalogo] que pinta las tarjetas de producto leyendo
 *              WooCommerce en vivo —render de vial, nombre, categoría corta, precio
 *              real, existencia y enlace a la ficha—, con el MISMO componente
 *              `.tarjeta` que usan la portada y el archivo de la tienda. Sustituye
 *              los listados escritos a mano de las landings, que se desincronizan
 *              del catálogo sin que nadie se entere.
 * Version:     1.0.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Por qué existe este archivo.
 *
 * /peptidos-mexico/ (página 1551) tenía el catálogo escrito a mano dentro de un
 * widget HTML de Elementor: 18 tarjetas con la imagen tipográfica «-v4.png» y el
 * precio tecleado. Ya se había desincronizado —anunciaba MOTS-c 40 mg a $3,200
 * cuando la tienda cobra $2,800—, y nada avisa cuando eso pasa: el precio de la
 * landing y el del carrito solo los compara el cliente.
 *
 * Aquí no se define ningún diseño nuevo. La tarjeta es `.tarjeta`, que vive una
 * sola vez en `pys-diseno/partes.php` y ya se sirve en todas las páginas que no
 * son la portada; lo único propio de este archivo es la retícula que la envuelve.
 * El render de vial sale de `pys_dis_vial()` y la etiqueta de categoría de
 * `pys_dis_cat_corta()`, las mismas funciones que usan la portada y el archivo
 * de la tienda, así que un producto no puede salir con una cara aquí y con otra
 * allá.
 */

/** Nombre de la tarjeta: el catálogo mete la promesa de venta tras un «|». */
function pys_cv_nombre( $nombre ) {
	$partes = explode( '|', (string) $nombre );
	return trim( $partes[0] );
}

/**
 * Productos del listado.
 *
 * `tipo` es un atajo sobre la categoría `suplementos`, que es la única frontera
 * real del catálogo: 18 péptidos y 4 suplementos Nutricost. Se resuelve por
 * taxonomía y no por una lista de IDs a propósito — una lista de IDs es
 * exactamente el problema que este archivo viene a quitar.
 *
 * @param string $tipo  peptidos | suplementos | todo.
 * @param string $cat   Slug de product_cat. Si viene, manda sobre $tipo.
 * @param int    $limite Máximo de productos, -1 para todos.
 * @return WC_Product[]
 */
function pys_cv_productos( $tipo = 'peptidos', $cat = '', $limite = -1 ) {
	if ( ! function_exists( 'wc_get_products' ) ) {
		return array();
	}

	$ids = wc_get_products(
		array(
			'status'  => 'publish',
			'limit'   => -1,
			'orderby' => 'title',
			'order'   => 'ASC',
			'return'  => 'ids',
		)
	);
	if ( is_wp_error( $ids ) || ! is_array( $ids ) ) {
		return array();
	}

	$productos = array();
	foreach ( $ids as $id ) {
		$p = wc_get_product( $id );
		if ( ! $p ) {
			continue;
		}
		/* Lo que el dueño esconde del catálogo no puede reaparecer en una landing. */
		if ( 'hidden' === $p->get_catalog_visibility() ) {
			continue;
		}

		if ( $cat ) {
			if ( ! has_term( $cat, 'product_cat', $id ) ) {
				continue;
			}
		} else {
			$es_suplemento = has_term( 'suplementos', 'product_cat', $id );
			if ( 'peptidos' === $tipo && $es_suplemento ) {
				continue;
			}
			if ( 'suplementos' === $tipo && ! $es_suplemento ) {
				continue;
			}
		}

		$productos[] = $p;
		if ( $limite > 0 && count( $productos ) >= $limite ) {
			break;
		}
	}

	return $productos;
}

/**
 * Precio de la tarjeta.
 *
 * En los variables WooCommerce pinta el rango («$1,900.00 – $3,200.00»), que en
 * una tarjeta de 290 px parte en dos líneas y se lee como si costara las dos
 * cosas. Se usa «Desde $X», que es además lo que decía la página a mano.
 */
function pys_cv_precio( $producto ) {
	if ( $producto->is_type( 'variable' ) ) {
		$min = $producto->get_variation_price( 'min', true );
		$max = $producto->get_variation_price( 'max', true );
		if ( '' !== $min && $min !== $max ) {
			/* translators: %s: importe ya formateado. */
			return sprintf( esc_html__( 'Desde %s', 'pys' ), wc_price( $min ) );
		}
	}
	return $producto->get_price_html();
}

/** Imagen de la tarjeta: render de vial si lo hay, si no la de WooCommerce. */
function pys_cv_imagen( $producto ) {
	$id   = $producto->get_id();
	$vial = function_exists( 'pys_dis_vial' ) ? pys_dis_vial( $id ) : '';

	if ( $vial && function_exists( 'pys_dis_uri' ) ) {
		return sprintf(
			'<img src="%s" width="540" height="1043" loading="lazy" decoding="async" alt="%s">',
			esc_url( pys_dis_uri( 'img/' . $vial ) ),
			esc_attr( 'Vial de ' . pys_cv_nombre( $producto->get_name() ) )
		);
	}

	if ( $producto->get_image_id() ) {
		/* `large` y no `woocommerce_thumbnail`: ese tamaño es 150×150 CON recorte
		   cuadrado y a los botes altos les corta una tira del centro. */
		return wp_get_attachment_image(
			$producto->get_image_id(),
			'large',
			false,
			array( 'loading' => 'lazy', 'alt' => pys_cv_nombre( $producto->get_name() ) )
		);
	}

	return '';
}

/**
 * Una tarjeta. Mismo marcado que la retícula de la portada, para que el CSS
 * compartido de `.tarjeta` la vista sin una sola regla nueva.
 */
function pys_cv_tarjeta( $producto ) {
	$id     = $producto->get_id();
	$nombre = pys_cv_nombre( $producto->get_name() );
	$url    = $producto->get_permalink();
	$sku    = $producto->get_sku();
	$stock  = $producto->is_in_stock();
	$vial   = function_exists( 'pys_dis_vial' ) ? pys_dis_vial( $id ) : '';
	$corta  = function_exists( 'pys_dis_cat_corta' ) ? pys_dis_cat_corta( $id ) : '';
	$imagen = pys_cv_imagen( $producto );

	$html  = '<article class="tarjeta">';
	$html .= '<a class="foto' . ( $vial ? ' vial' : '' ) . '" href="' . esc_url( $url ) . '"'
		. ' aria-label="' . esc_attr( 'Ver ' . $nombre ) . '">';
	if ( $corta ) {
		$html .= '<span class="eti">' . esc_html( $corta ) . '</span>';
	}
	$html .= $imagen ? $imagen : '<span class="sinfoto">SIN IMAGEN</span>';
	if ( ! $stock ) {
		$html .= '<span class="agotado"><span>Agotado</span></span>';
	}
	$html .= '</a>';

	$html .= '<div class="cuerpo">';
	$html .= '<h3><a href="' . esc_url( $url ) . '">' . esc_html( $nombre ) . '</a></h3>';
	if ( $sku ) {
		$html .= '<div class="sku">SKU ' . esc_html( $sku ) . '</div>';
	}
	$html .= '</div>';

	$html .= '<div class="specs"><span>' . esc_html( $corta ? $corta : 'Catálogo' ) . '</span>'
		. '<span>·</span><span>' . ( $stock ? 'en existencia' : 'sin existencia' ) . '</span></div>';

	$html .= '<div class="compra"><span class="precio">' . wp_kses_post( pys_cv_precio( $producto ) ) . '</span>';
	if ( ! $stock ) {
		$html .= '<span class="add agotado-b">Agotado</span>';
	} elseif ( $producto->is_type( 'simple' ) && $producto->is_purchasable() ) {
		$html .= '<a class="add add_to_cart_button ajax_add_to_cart" href="?add-to-cart=' . (int) $id . '"'
			. ' data-quantity="1" data-product_id="' . (int) $id . '"'
			. ' data-product_sku="' . esc_attr( $sku ) . '"'
			. ' aria-label="' . esc_attr( 'Agregar ' . $nombre . ' al carrito' ) . '"'
			. ' rel="nofollow">Agregar</a>';
	} else {
		$html .= '<a class="add" href="' . esc_url( $url ) . '">Elegir opciones</a>';
	}
	$html .= '</div></article>';

	return $html;
}

/**
 * [pys_catalogo tipo="peptidos"]
 *
 * Atributos: tipo (peptidos|suplementos|todo), cat (slug de product_cat),
 * limite (int) y clase (clase extra en la retícula).
 */
function pys_cv_shortcode( $atts ) {
	$a = shortcode_atts(
		array(
			'tipo'   => 'peptidos',
			'cat'    => '',
			'limite' => -1,
			'clase'  => '',
		),
		$atts,
		'pys_catalogo'
	);

	$productos = pys_cv_productos( sanitize_key( $a['tipo'] ), sanitize_title( $a['cat'] ), (int) $a['limite'] );
	if ( ! $productos ) {
		return '';
	}

	$html = '<div class="pys-cv' . ( $a['clase'] ? ' ' . esc_attr( $a['clase'] ) : '' ) . '">';
	foreach ( $productos as $p ) {
		$html .= pys_cv_tarjeta( $p );
	}
	$html .= '</div>';

	return $html;
}
add_shortcode( 'pys_catalogo', 'pys_cv_shortcode' );

/**
 * `[pys_catalogo_cuenta tipo="peptidos"]` — cuántos productos hay, ahora mismo.
 *
 * La frase que presenta el catálogo llevaba el número escrito a mano. El
 * 2026-09-23 se fusionaron MOTS-c y semaglutida, el catálogo pasó de 18 a 16
 * péptidos y la página siguió diciendo 18: exactamente el mismo fallo que el
 * listado de tarjetas tenía antes de leer de WooCommerce. Un dato que se
 * escribe a mano se queda mintiendo el día que alguien toca el catálogo.
 */
function pys_cv_cuenta_shortcode( $atts ) {
	$a = shortcode_atts(
		array(
			'tipo' => 'peptidos',
			'cat'  => '',
		),
		$atts,
		'pys_catalogo_cuenta'
	);
	return (string) count( pys_cv_productos( sanitize_key( $a['tipo'] ), sanitize_title( $a['cat'] ), -1 ) );
}
add_shortcode( 'pys_catalogo_cuenta', 'pys_cv_cuenta_shortcode' );

/**
 * ¿La vista actual usa el shortcode?
 *
 * Se mira el contenido Y el documento de Elementor, porque en 1551 el shortcode
 * vive dentro de un widget HTML y nunca pasa por `post_content`.
 */
function pys_cv_en_uso() {
	static $uso = null;
	if ( null !== $uso ) {
		return $uso;
	}
	$uso = false;
	if ( is_singular() ) {
		$id = get_queried_object_id();
		if ( $id ) {
			$uso = false !== strpos( (string) get_post_field( 'post_content', $id ), '[pys_catalogo' )
				|| false !== strpos( (string) get_post_meta( $id, '_elementor_data', true ), '[pys_catalogo' );
		}
	}
	return $uso;
}

/**
 * El widget HTML de Elementor imprime su contenido tal cual: `render()` es un
 * `print_unescaped_setting('html')` y no pasa por `do_shortcode()`. Se le ejecuta
 * aquí, y SOLO si trae este shortcode, para no cambiar el comportamiento de
 * ningún otro widget del sitio.
 */
add_filter(
	'elementor/widget/render_content',
	function ( $contenido, $widget ) {
		if ( ! is_string( $contenido ) || false === strpos( $contenido, '[pys_catalogo' ) ) {
			return $contenido;
		}
		if ( ! $widget || ! method_exists( $widget, 'get_name' ) || 'html' !== $widget->get_name() ) {
			return $contenido;
		}
		return do_shortcode( $contenido );
	},
	10,
	2
);

/**
 * La caché de elementos de Elementor está encendida (`elementor_element_cache_ttl`
 * = 24 h) y guarda el HTML ya pintado en `_elementor_element_cache`. Un listado
 * de precios congelado 24 horas es el mismo fallo que este archivo viene a
 * arreglar, solo que más difícil de ver. Marcando el widget como contenido
 * dinámico, Elementor guarda en la caché un `[elementor-element …]` en vez del
 * HTML y lo vuelve a pintar en cada carga.
 */
add_filter(
	'elementor/element/is_dynamic_content',
	function ( $dinamico, $datos ) {
		if ( ! empty( $datos['settings']['html'] ) && is_string( $datos['settings']['html'] )
			&& false !== strpos( $datos['settings']['html'], '[pys_catalogo' ) ) {
			return true;
		}
		return $dinamico;
	},
	10,
	2
);

/**
 * Páginas que usan el shortcode. Se busca en el contenido Y en el documento de
 * Elementor, y se guarda 5 minutos: solo se consulta al guardar un producto.
 */
function pys_cv_paginas_con_shortcode() {
	$ids = get_transient( 'pys_cv_paginas' );
	if ( false !== $ids ) {
		return $ids;
	}
	global $wpdb;
	$en_contenido = $wpdb->get_col(
		"SELECT ID FROM {$wpdb->posts}
		 WHERE post_status = 'publish' AND post_content LIKE '%[pys_catalogo%'"
	);
	$en_elementor = $wpdb->get_col(
		"SELECT m.post_id FROM {$wpdb->postmeta} m
		 INNER JOIN {$wpdb->posts} p ON p.ID = m.post_id AND p.post_status = 'publish'
		 WHERE m.meta_key = '_elementor_data' AND m.meta_value LIKE '%[pys_catalogo%'"
	);
	$ids = array_values( array_unique( array_map( 'intval', array_merge( (array) $en_contenido, (array) $en_elementor ) ) ) );
	set_transient( 'pys_cv_paginas', $ids, 5 * MINUTE_IN_SECONDS );
	return $ids;
}

/**
 * El precio que ve el cliente lo sirve la caché de página de LiteSpeed, que
 * purga la ficha del producto al guardarlo pero no sabe que este listado
 * también lo muestra. Sin esto, la landing seguiría anunciando el precio viejo
 * hasta que caducara la caché: el mismo fallo de antes, solo que con menos
 * horas de vida. Se purga también al cambiar existencias, que es lo que más se
 * mueve.
 */
function pys_cv_purgar() {
	delete_transient( 'pys_cv_paginas' );
	foreach ( pys_cv_paginas_con_shortcode() as $id ) {
		delete_post_meta( $id, '_elementor_element_cache' );
		do_action( 'litespeed_purge_post', $id );
	}
}
foreach ( array( 'woocommerce_update_product', 'woocommerce_new_product', 'woocommerce_delete_product',
	'woocommerce_trash_product', 'woocommerce_product_set_stock', 'woocommerce_variation_set_stock',
	'woocommerce_product_set_stock_status', 'woocommerce_variation_set_stock_status' ) as $pys_cv_hook ) {
	add_action( $pys_cv_hook, 'pys_cv_purgar', 20 );
}
unset( $pys_cv_hook );

/** «Agregar» sin recargar y contador del carrito, como en la portada. */
add_action(
	'wp_enqueue_scripts',
	function () {
		if ( pys_cv_en_uso() && function_exists( 'WC' ) ) {
			wp_enqueue_script( 'wc-add-to-cart' );
			wp_enqueue_script( 'wc-cart-fragments' );
		}
	}
);

/**
 * Lo único propio: la retícula. La tarjeta entera viene de `.tarjeta`, que la
 * capa de diseño global ya sirve en esta página. Mismos cortes y mismo hueco
 * que `ul.products` en el archivo de la tienda, para que las dos retículas
 * respiren igual.
 */
add_action(
	'wp_head',
	function () {
		if ( ! pys_cv_en_uso() ) {
			return;
		}
		echo '<style data-no-optimize="1">'
			. 'html body[class][class][class] .pys-cv{display:grid!important;'
			. 'grid-template-columns:repeat(4,minmax(0,1fr))!important;'
			. 'gap:clamp(12px,1.4vw,20px)!important;margin:0!important;padding:0!important;list-style:none}'
			. 'html body[class][class][class] .pys-cv .tarjeta{margin:0;min-width:0;text-align:left}'
			. 'html body[class][class][class] .pys-cv .tarjeta h3{margin:0;font-family:var(--optima);'
			. 'font-weight:400;letter-spacing:-.012em;color:var(--tinta);text-transform:none}'
			. 'html body[class][class][class] .pys-cv .tarjeta h3 a{color:inherit;text-decoration:none}'
			. 'html body[class][class][class] .pys-cv .tarjeta .foto{margin:0;padding:0;border-radius:0}'
			. 'html body[class][class][class] .pys-cv .tarjeta .precio{color:var(--tinta)}'
			. 'html body[class][class][class] .pys-cv .tarjeta .add{text-decoration:none}'
			. '@media (max-width:1040px){html body[class][class][class] .pys-cv{'
			. 'grid-template-columns:repeat(3,minmax(0,1fr))!important}}'
			. '@media (max-width:780px){html body[class][class][class] .pys-cv{'
			. 'grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important}}'
			. '@media (max-width:340px){html body[class][class][class] .pys-cv{'
			. 'grid-template-columns:minmax(0,1fr)!important}}'
			. '</style>';
	},
	100
);
