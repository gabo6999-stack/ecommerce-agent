<?php
/**
 * PYS — Home 2026.
 *
 * El diseño (retícula, tipografías, color, visor de 360°, animaciones) viene
 * del prototipo. El contenido NO: cada texto, precio, existencia, categoría,
 * guía, enlace de menú y dato de envío se lee aquí de WordPress/WooCommerce,
 * de modo que el home no pueda desincronizarse de la tienda ni afirmar nada
 * que el sitio no sostenga ya.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/* ─── estáticos ──────────────────────────────────────────────────────── */
wp_enqueue_script( 'pys-h26-motion', pys_h26_uri( 'js/motion.js' ), array(), PYS_H26_VER, true );
wp_enqueue_script( 'pys-h26-giro', pys_h26_uri( 'js/giro360.js' ), array(), PYS_H26_VER, true );
if ( function_exists( 'WC' ) ) {
	wp_enqueue_script( 'wc-add-to-cart' );   // «Agregar» sin recargar
	wp_enqueue_script( 'wc-cart-fragments' ); // contador del carrito en vivo
}

/* ─── enlaces reales del sitio ───────────────────────────────────────── */
$pys_url = array(
	'inicio'      => home_url( '/' ),
	'peptidos'    => home_url( '/peptidos-mexico/' ),
	'glp1'        => home_url( '/glp-1/' ),
	'suplementos' => home_url( '/suplementos-deportivos/' ),
	'productos'   => function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/comprar-peptidos-en-mexico/' ),
	'metabolismo' => home_url( '/como-acelerar-el-metabolismo/' ),
	'reparacion'  => home_url( '/recuperacion-muscular/' ),
	'longevidad'  => home_url( '/envejecimiento-saludable/' ),
	'performance' => home_url( '/rendimiento-deportivo/' ),
	'calculadora' => home_url( '/calculadora-de-dosis-de-peptidos/' ),
	'blog'        => home_url( '/blog/' ),
	'contacto'    => home_url( '/contacto/' ),
	'envios'      => home_url( '/politica-de-envios-y-devoluciones/' ),
	'privacidad'  => home_url( '/politica-de-privacidad/' ),
	'terminos'    => home_url( '/terminos-y-condiciones/' ),
	'carrito'     => function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : home_url( '/carrito/' ),
	'cuenta'      => function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'myaccount' ) : home_url( '/mi-cuenta/' ),
);

/* ─── catálogo en vivo ───────────────────────────────────────────────── */
$pys_cortos = pys_dis_cats_cortas();


/** Los nombres de algunos productos llevan la cola del título SEO tras «|». */
function pys_h26_nombre( $nombre ) {
	$partes = explode( '|', $nombre );
	return trim( $partes[0] );
}

$pys_cats = array();
if ( taxonomy_exists( 'product_cat' ) ) {
	$terminos = get_terms(
		array(
			'taxonomy'   => 'product_cat',
			'hide_empty' => true,
			'exclude'    => array( get_option( 'default_product_cat' ) ),
		)
	);
	if ( ! is_wp_error( $terminos ) ) {
		foreach ( $terminos as $t ) {
			if ( 'uncategorized' === $t->slug ) {
				continue;
			}
			$pys_cats[] = array(
				'slug'  => $t->slug,
				'largo' => $t->name,
				'corto' => isset( $pys_cortos[ $t->slug ] ) ? $pys_cortos[ $t->slug ] : $t->name,
				'n'     => (int) $t->count,
				'url'   => get_term_link( $t ),
			);
		}
		usort( $pys_cats, function ( $a, $b ) { return $b['n'] - $a['n']; } );
	}
}

$pys_productos = array();
$pys_q = new WP_Query(
	array(
		'post_type'           => 'product',
		'post_status'         => 'publish',
		'posts_per_page'      => -1,
		'orderby'             => 'menu_order title',
		'order'               => 'ASC',
		'ignore_sticky_posts' => true,
		'no_found_rows'       => true,
	)
);
foreach ( $pys_q->posts as $pys_post ) {
	$pr = function_exists( 'wc_get_product' ) ? wc_get_product( $pys_post->ID ) : null;
	if ( ! $pr || ! $pr->is_visible() ) {
		continue;
	}
	$slugs = wp_get_post_terms( $pys_post->ID, 'product_cat', array( 'fields' => 'slugs' ) );
	$slugs = is_wp_error( $slugs ) ? array() : $slugs;
	$primera = '';
	foreach ( $slugs as $s ) {
		if ( isset( $pys_cortos[ $s ] ) ) {
			$primera = $pys_cortos[ $s ];
			break;
		}
	}
	$vial = pys_dis_vial( $pys_post->ID );
	if ( $vial ) {
		$medio = '<img src="' . esc_url( pys_h26_uri( 'img/' . $vial ) ) . '" width="540" height="1043"'
			. ' loading="lazy" decoding="async" alt="' . esc_attr( 'Vial de ' . pys_h26_nombre( $pr->get_name() ) ) . '">';
	} elseif ( $pr->get_image_id() ) {
		/* `large` y no `woocommerce_thumbnail`: ese tamaño es de 150×150 CON
		   recorte cuadrado, así que a los botes altos (800×1600) les cortaba
		   una tira del centro y la estiraba a lo ancho de la tarjeta — se veían
		   ampliados y borrosos. Solo Zinc se salvaba, por ser casi cuadrado.
		   `large` respeta la proporción y el `object-fit:contain` lo encaja. */
		$medio = wp_get_attachment_image(
			$pr->get_image_id(),
			'large',
			false,
			array( 'loading' => 'lazy', 'alt' => $pr->get_name() )
		);
	} else {
		$medio = '';
	}

	$pys_productos[] = array(
		'id'        => $pys_post->ID,
		'nombre'    => pys_h26_nombre( $pr->get_name() ),
		'url'       => $pr->get_permalink(),
		'sku'       => $pr->get_sku(),
		'tipo'      => $pr->get_type(),
		'stock'     => $pr->is_in_stock(),
		'comprable' => $pr->is_purchasable(),
		'precio'    => $pr->get_price_html(),
		'img'       => $medio,
		'vial'      => $vial,
		'cats'      => $slugs,
		'cat'       => $primera,
		'ventas'    => (int) $pr->get_total_sales(),
		'importe'   => (float) $pr->get_price(),
	);
}
wp_reset_postdata();

$pys_en_stock = count( array_filter( $pys_productos, function ( $p ) { return $p['stock']; } ) );

/**
 * Viales del carrusel del héroe.
 *
 * Solo entran los que están EN EXISTENCIA y tienen render de vial —anunciar en
 * portada algo agotado es la mejor forma de perder a alguien—. Retatrutida va
 * primero por decisión del usuario; el resto se ordena por unidades vendidas y,
 * como empate, por precio. Hoy las ventas casi no dan señal (dos productos con
 * una unidad), así que en la práctica manda el ticket. Se recalcula en cada
 * carga: si algo se agota, sale solo del carrusel.
 */
/* Orden fijado por el usuario, por demanda del mercado (no por las ventas de
   la tienda, que hoy son dos unidades y no dicen nada). De Semaglutida va la
   de 5 mg porque la de 20 está agotada, y de MOTS-c la de 40 mg por ticket;
   sus hermanas caen en el resto. */
$pys_orden = array(
	'retatrutida',
	'tirzepatida',
	'semaglutida-5-mg',
	'mots-c-40mg',
	'cjc-1295-ipamorelina-5mg',
);

$pys_carrusel = array_values( array_filter( $pys_productos, function ( $p ) {
	return $p['vial'] && $p['stock'];
} ) );
usort( $pys_carrusel, function ( $a, $b ) use ( $pys_orden ) {
	$pa = array_search( get_post_field( 'post_name', $a['id'] ), $pys_orden, true );
	$pb = array_search( get_post_field( 'post_name', $b['id'] ), $pys_orden, true );
	if ( false !== $pa || false !== $pb ) {
		if ( false === $pa ) { return 1; }
		if ( false === $pb ) { return -1; }
		return $pa - $pb;
	}
	return $b['importe'] <=> $a['importe'];   // el resto, por ticket
} );
$pys_carrusel = array_slice( $pys_carrusel, 0, 8 );

/* ─── datos de envío, leídos de la configuración real de WooCommerce ─── */
$pys_envio_fijo  = null;
$pys_envio_gratis = null;
if ( class_exists( 'WC_Shipping_Zones' ) ) {
	foreach ( WC_Shipping_Zones::get_zones() as $zona ) {
		foreach ( $zona['shipping_methods'] as $metodo ) {
			if ( ! $metodo->is_enabled() ) {
				continue;
			}
			if ( 'flat_rate' === $metodo->id && null === $pys_envio_fijo ) {
				$pys_envio_fijo = $metodo->get_option( 'cost' );
			}
			if ( 'free_shipping' === $metodo->id && null === $pys_envio_gratis ) {
				$pys_envio_gratis = $metodo->get_option( 'min_amount' );
			}
		}
	}
}
$pys_moneda = function ( $n ) {
	return function_exists( 'wc_price' ) ? wp_strip_all_tags( wc_price( $n, array( 'decimals' => 0 ) ) ) : '$' . number_format( (float) $n );
};

/* ─── guías reales del blog ──────────────────────────────────────────── */
$pys_guias = get_posts(
	array(
		'post_type'        => 'post',
		'post_status'      => 'publish',
		'numberposts'      => 6,
		'orderby'          => 'date',
		'order'            => 'DESC',
		'suppress_filters' => false,
	)
);
$pys_total_guias = (int) wp_count_posts( 'post' )->publish;
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
<style data-no-optimize="1">
/* ════════════════════════════════════════════════════════════════════
   Home 2026 — dirección «laboratorio oscuro».
   Hoja del prototipo, con las tipografías servidas desde uploads y los
   añadidos que el prototipo no traía porque no era una tienda de verdad:
   desplegable del menú, contador del carrito, buscador y los botones
   nativos de WooCommerce.
   ════════════════════════════════════════════════════════════════════ */

/* IBM Plex Mono — SIL Open Font License 1.1, © IBM Corp. */
@font-face{font-family:"Plex Mono";src:url(<?php echo esc_url( pys_h26_uri( 'fonts/plex-mono-400.woff2' ) ); ?>) format("woff2");
           font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Plex Mono";src:url(<?php echo esc_url( pys_h26_uri( 'fonts/plex-mono-500.woff2' ) ); ?>) format("woff2");
           font-weight:500;font-style:normal;font-display:swap}
@font-face{font-family:"Plex Mono";src:url(<?php echo esc_url( pys_h26_uri( 'fonts/plex-mono-600.woff2' ) ); ?>) format("woff2");
           font-weight:600;font-style:normal;font-display:swap}
@font-face{font-family:"Optima PYS";src:url(<?php echo esc_url( pys_h26_uri( 'fonts/optima-500.woff2' ) ); ?>) format("woff2");
           font-weight:400 700;font-style:normal;font-display:swap}
@font-face{font-family:"Optima PYS";src:url(<?php echo esc_url( pys_h26_uri( 'fonts/optima-400-italic.woff2' ) ); ?>) format("woff2");
           font-weight:400 700;font-style:italic;font-display:swap}

:root{
  color-scheme:dark;
  --negro:#050908; --carbon:#0A1210; --carbon-2:#0F1A17; --panel:#132420;
  --linea:#16241F; --linea-2:#22362F;
  --tinta:#EEF6F3; --tinta-2:#93AAA3; --tinta-3:#718C84;
  --magenta:#FF047E; --aqua:#02F6C8; --vitrina:#EEF3F1;
  --optima:Optima,"Optima nova LT Pro","Optima PYS",Candara,"Gill Sans",sans-serif;
  --mono:"Plex Mono",ui-monospace,Consolas,monospace;
  --gutter:clamp(18px,4vw,56px);
  /* Panal que teja sin costura: mosaico de 66 × 38.11 con los cuatro medios
     hexágonos de los bordes, de modo que al repetirse encajan. Va como SVG en
     línea para no pedir un archivo más. */
  --hex:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='66' height='38.11' viewBox='0 0 66 38.11'%3E%3Cpath d='M22.00,19.05L11.00,38.11L-11.00,38.11L-22.00,19.05L-11.00,0.00L11.00,0.00Z M55.00,0.00L44.00,19.05L22.00,19.05L11.00,0.00L22.00,-19.05L44.00,-19.05Z M55.00,38.11L44.00,57.16L22.00,57.16L11.00,38.11L22.00,19.05L44.00,19.05Z M88.00,19.05L77.00,38.11L55.00,38.11L44.00,19.05L55.00,0.00L77.00,0.00Z' fill='none' stroke='%23EEF6F3' stroke-width='1'/%3E%3C/svg%3E");
  --hex-viva:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='66' height='38.11' viewBox='0 0 66 38.11'%3E%3Cpath d='M22.00,19.05L11.00,38.11L-11.00,38.11L-22.00,19.05L-11.00,0.00L11.00,0.00Z M55.00,0.00L44.00,19.05L22.00,19.05L11.00,0.00L22.00,-19.05L44.00,-19.05Z M55.00,38.11L44.00,57.16L22.00,57.16L11.00,38.11L22.00,19.05L44.00,19.05Z M88.00,19.05L77.00,38.11L55.00,38.11L44.00,19.05L55.00,0.00L77.00,0.00Z' fill='none' stroke='%2302F6C8' stroke-width='1'/%3E%3C/svg%3E");
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
section[id],div[id]{scroll-margin-top:clamp(78px,11vh,104px)}
/* Ojo: el fondo del `body` NO se apaga desde aquí. El kit de Elementor le
   pinta el hexagonal del sitio y le gana a esta hoja incluso con
   `!important` —LiteSpeed reordena e inyecta CSS crítico, así que el orden
   de la cascada no es de fiar—. Se apaga en el atributo `style` del propio
   `<body>`, más abajo, que no puede perder. */
body.pys-h26{margin:0;color:var(--tinta);font-family:var(--optima);
  font-size:17px;line-height:1.55;-webkit-font-smoothing:antialiased;overflow-x:hidden}
.pys-h26 h1,.pys-h26 h2,.pys-h26 h3,.pys-h26 h4{margin:0;font-weight:400;line-height:1.05;
  letter-spacing:-.012em}
.pys-h26 p{margin:0}
.pys-h26 a{color:inherit;text-decoration:none}
.pys-h26 img{max-width:100%;height:auto}
.pys-h26 :focus-visible{outline:2px solid var(--magenta);outline-offset:4px}
.wrap{width:min(1320px,100%);margin-inline:auto;padding-inline:var(--gutter)}
.vs{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--tinta-3)}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* El halo ya no lleva `transition`: ahora el JS lo refresca en cada fotograma
   con requestAnimationFrame, y transicionar un degradado 60 veces por segundo
   es justo lo que no hay que hacer. */
#halo{position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(760px 620px at var(--mx,64%) var(--my,30%),
    rgba(2,246,200,.10) 0%, rgba(255,4,126,.055) 38%, transparent 72%)}

/* ── retícula hexagonal viva ─────────────────────────────────────────
   El hexágono es la forma de la marca: está en el logo y en la etiqueta de
   todos los viales. La capa de base es casi invisible y deriva muy despacio;
   encima va la misma retícula en aqua, recortada por una máscara que sigue al
   cursor, así solo se enciende el panal que tienes alrededor del puntero.
   Todo el efecto es CSS —el JS solo escribe dos variables— y ni la deriva ni
   la máscara repintan nada: una va por `transform` y la otra por composición.
   Sustituye a la textura hexagonal estática del sitio, que aquí ensuciaba. */
.hexes{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.hexes span{position:absolute;inset:-140px;background-image:var(--hex);
  background-size:66px 38.11px}
.hexes .base{opacity:.055;animation:deriva 150s linear infinite}
/* un mosaico justo en horizontal y dos en vertical: al llegar al final la
   retícula coincide consigo misma y el salto no se ve */
@keyframes deriva{from{transform:translate3d(0,0,0)}
  to{transform:translate3d(-66px,-76.22px,0)}}
/* Cerco más chico y que se apaga antes: la retícula se insinúa alrededor del
   cursor en vez de iluminar media pantalla. */
.hexes .viva{background-image:var(--hex-viva);opacity:.4;
  -webkit-mask-image:radial-gradient(280px 240px at calc(var(--hx,50vw) + 140px) calc(var(--hy,38vh) + 140px),
    #000 0%, rgba(0,0,0,.28) 40%, transparent 66%);
  mask-image:radial-gradient(280px 240px at calc(var(--hx,50vw) + 140px) calc(var(--hy,38vh) + 140px),
    #000 0%, rgba(0,0,0,.28) 40%, transparent 66%)}
/* sin cursor que seguir, la capa viva no aporta y solo cuesta */
@media (hover:none){ .hexes .viva{display:none} .hexes .base{opacity:.075} }

/* ── cintillo ────────────────────────────────────────────────────────
   Desfila en bucle: los avisos no caben de una vez en ningún ancho y
   dejarlos cortados escondía la mitad. El grupo va duplicado y la tira se
   corre justo un 50 %, así el salto del final coincide con el principio y
   no se ve el corte. Se para al pasar el ratón para poder leerlo. */
.cintillo{position:relative;z-index:2;background:var(--carbon);border-bottom:1px solid var(--linea);
  font-family:var(--mono);font-size:11px;letter-spacing:.06em;overflow:hidden}
.cintillo .tira{display:flex;width:max-content;animation:desfile 46s linear infinite}
.cintillo:hover .tira,.cintillo:focus-within .tira{animation-play-state:paused}
.cintillo .grupo{display:flex;align-items:center;gap:clamp(18px,2.6vw,34px);
  padding-block:9px;padding-inline:clamp(9px,1.3vw,17px);flex:none}
@keyframes desfile{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.cintillo span{white-space:nowrap;color:var(--tinta-3)}
.cintillo b{color:var(--tinta);font-weight:500}
.cintillo .promo{color:var(--aqua)}
.cintillo .sep{color:var(--linea-2)}
/* A propósito NO hay excepción por `prefers-reduced-motion`: se probó la
   variante quieta que envuelve en dos renglones y se descartó, el cintillo va
   siempre en una sola línea desfilando. Como contrapeso se para al pasar el
   ratón o al recibir el foco, y nada de lo que dice vive solo aquí —el envío
   y las formas de pago se repiten en las preguntas frecuentes y en el pie. */
.cintillo .grupo{flex-wrap:nowrap}

/* ── nav ───────────────────────────────────────────────────────────── */
header.top{position:sticky;top:0;z-index:30;
  background:color-mix(in srgb,var(--negro) 88%,transparent);backdrop-filter:blur(14px);
  border-bottom:1px solid var(--linea)}
header.top .wrap{display:flex;align-items:center;gap:clamp(12px,2vw,26px);padding-block:14px}
.marca{display:flex;align-items:center;gap:11px;flex:none}
.marca .logo{height:34px;width:auto;display:block;flex:none}
.marca .nom{font-size:18px;white-space:nowrap}
@media (max-width:420px){ .marca .nom{font-size:16px} .marca .logo{height:29px} }
.menu{display:flex;gap:clamp(11px,1.6vw,22px);margin-left:auto;font-size:15px;align-items:center}
.menu > a,.desp > button{color:var(--tinta-2);transition:color .2s;position:relative;
  padding-block:4px;background:none;border:0;font:inherit;cursor:pointer;display:inline-flex;
  align-items:center;gap:5px;white-space:nowrap}
.menu > a::after,.desp > button::after{content:"";position:absolute;left:0;right:100%;bottom:-2px;
  height:1px;background:var(--magenta);transition:right .3s cubic-bezier(.22,.61,.36,1)}
.menu > a:hover,.desp > button:hover{color:var(--tinta)}
.menu > a:hover::after,.desp > button:hover::after{right:0}
.desp{position:relative}
.desp > button svg{transition:transform .2s}
.desp[data-abierto="1"] > button svg{transform:rotate(180deg)}
.desp ul{position:absolute;top:calc(100% + 12px);left:-14px;margin:0;padding:6px;list-style:none;
  min-width:212px;background:var(--carbon);border:1px solid var(--linea-2);border-radius:3px;
  box-shadow:0 26px 54px -26px rgba(0,0,0,.95);opacity:0;visibility:hidden;transform:translateY(-6px);
  transition:opacity .2s,transform .2s,visibility .2s}
.desp[data-abierto="1"] ul{opacity:1;visibility:visible;transform:translateY(0)}
.desp li a{display:block;padding:9px 12px;border-radius:2px;font-size:15px;color:var(--tinta-2)}
.desp li a:hover{background:var(--panel);color:var(--tinta)}
.iconos{display:flex;gap:8px;flex:none;margin-left:4px}
.icob{width:38px;height:38px;border:1px solid var(--linea-2);background:transparent;border-radius:2px;
  color:var(--tinta-2);display:grid;place-items:center;cursor:pointer;flex:none;position:relative}
.icob:hover{border-color:var(--tinta-3);color:var(--tinta)}
.pys-cart-n{position:absolute;top:-7px;right:-7px;min-width:18px;height:18px;padding:0 4px;
  border-radius:9px;background:var(--magenta);color:#fff;font-family:var(--mono);font-size:9.5px;
  line-height:18px;text-align:center;font-variant-numeric:tabular-nums}
.pys-cart-n[hidden]{display:none}
.burger{display:none}
.burger svg{display:none}
.burger[aria-expanded="false"] .abre{display:block}
.burger[aria-expanded="true"] .cierra{display:block}

#busca{border-top:1px solid var(--linea);background:var(--carbon)}
#busca .wrap{display:flex;align-items:center;gap:12px;padding-block:16px}
#busca input[type="search"]{flex:1;min-width:0;background:var(--negro);
  border:1px solid var(--linea-2);border-radius:2px;color:var(--tinta);
  font-family:var(--optima);font-size:16px;padding:12px 14px}
#busca input[type="search"]::placeholder{color:var(--tinta-3)}
#busca button{font-family:var(--mono);font-size:12px;letter-spacing:.08em;padding:13px 18px;
  border:1px solid var(--magenta);background:var(--magenta);color:#fff;border-radius:2px;
  cursor:pointer;flex:none}

#mnav{border-top:1px solid var(--linea);background:var(--carbon)}
#mnav .wrap{display:flex;flex-direction:column;align-items:stretch;gap:0;padding-block:12px 20px}
#mnav .et{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--tinta-3);padding:14px 0 4px}
#mnav a{display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:46px;
  border-bottom:1px solid var(--linea);font-size:16px;color:var(--tinta-2)}
#mnav a .k{font-family:var(--mono);font-size:10.5px;color:var(--tinta-3)}
@media (min-width:1101px){ #mnav{display:none!important} }
@media (max-width:1100px){ .menu > a,.desp{display:none} .burger{display:grid} }
/* En teléfono no cabían en una fila la marca (≈245 px) y los cuatro iconos (176 px):
   el navegador ensanchaba la página a 461 px y la enseñaba alejada, con el carrito
   cortado. La marca pasa a dos líneas y los iconos se compactan. Es el mismo arreglo
   que lleva la cabecera compartida (pys-diseno/partes.php): si se cambia uno, el otro. */
@media (max-width:540px){
  header.top .wrap{gap:10px}
  header.top .menu{display:none}
  header.top .marca{gap:9px;min-width:0}
  header.top .marca .nom{white-space:normal;font-size:14.5px;line-height:1.1;max-width:8.4em}
  header.top .iconos{gap:6px;margin-left:auto}
  header.top .icob{width:36px;height:36px}
}
@media (max-width:380px){
  header.top .iconos{gap:4px}
  header.top .icob{width:34px;height:34px}
}
/* En los teléfonos más angostos se va el icono de la cuenta: sigue en el menú. */
@media (max-width:340px){
  header.top .marca .nom{font-size:13.5px}
  header.top .iconos a[aria-label="Mi cuenta"]{display:none}
}

/* ── hero ──────────────────────────────────────────────────────────── */
.hero{position:relative;z-index:1}
.hero .wrap{display:grid;grid-template-columns:1.06fr .94fr;gap:clamp(24px,5vw,72px);
  align-items:center;padding-block:clamp(34px,5vw,72px)}
.hero h1{font-size:clamp(33px,4.4vw,62px);margin-block:16px 18px;max-width:16ch}
.hero h1 em{font-style:normal;color:var(--magenta)}
.hero .lede{color:var(--tinta-2);font-size:clamp(16px,1.3vw,18.5px);max-width:46ch}
.hero .lede + .lede{margin-top:12px}
.cta{display:flex;gap:12px;margin-top:28px;flex-wrap:wrap}
.btn{font-family:var(--optima);font-size:16px;padding:14px 26px;border-radius:2px;
  border:1px solid var(--linea-2);background:transparent;color:inherit;
  display:inline-flex;align-items:center;gap:9px;cursor:pointer;
  transition:border-color .2s,background .2s}
.btn.pri{background:var(--magenta);border-color:var(--magenta);color:#fff}
.btn.pri:hover{background:#FF3D97;border-color:#FF3D97}
.btn:hover{border-color:var(--tinta)}
.sellos{display:flex;gap:9px;margin-top:24px;flex-wrap:wrap}
.sello{font-family:var(--mono);font-size:11px;letter-spacing:.05em;padding:7px 12px;
  border:1px solid var(--linea-2);border-radius:2px;color:var(--tinta-2)}
.sello.ok{border-color:color-mix(in srgb,var(--aqua) 42%,transparent);color:var(--aqua);
  background:color-mix(in srgb,var(--aqua) 7%,transparent)}
@media (max-width:900px){ .hero .wrap{grid-template-columns:1fr} }

.vitrina{position:relative;background:
   radial-gradient(120% 90% at 50% 12%, #FFFFFF 0%, var(--vitrina) 46%, #D7E1DE 100%);
  border:1px solid var(--linea-2);border-radius:3px;overflow:hidden;
  box-shadow:0 0 0 1px rgba(2,246,200,.07), 0 40px 90px -40px rgba(0,0,0,.9),
             0 0 120px -30px rgba(2,246,200,.16);
  touch-action:pan-y;cursor:grab;user-select:none;display:block}
.vitrina:active{cursor:grabbing}
.vitrina .lienzo{display:block;width:100%;aspect-ratio:640/877}
.hero .vitrina{max-width:min(100%,410px);margin-inline:auto}
.vitrina img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
  opacity:0;pointer-events:none}
.vitrina img.on{opacity:1}
.vitrina .pista{position:absolute;left:0;right:0;bottom:12px;text-align:center;
  font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:#5E7A74;transition:opacity .4s}
.vitrina.usada .pista{opacity:0}
.vitrina .marco{position:absolute;inset:10px;border:1px solid rgba(8,18,15,.10);
  pointer-events:none;border-radius:2px}
.vitrina .grados{position:absolute;top:12px;right:14px;font-family:var(--mono);
  font-size:10.5px;color:#5E7A74;letter-spacing:.08em}
.pie-vitrina{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;
  margin-top:11px;font-family:var(--mono);font-size:10.5px;letter-spacing:.07em;
  color:var(--tinta-3);max-width:410px;margin-inline:auto}
/* es un párrafo: `.pys-h26 p{margin:0}` le ganaba al `margin-inline:auto` y el
   pie quedaba 62 px a la izquierda del vial, descentrado respecto a la caja y
   a los puntos del carrusel */
.hero .pie-vitrina{margin-inline:auto}
.pie-vitrina a{color:var(--magenta)}
.pie-vitrina a:hover{text-decoration:underline}

/* ── carrusel del héroe ──────────────────────────────────────────────
   Sin movimiento propio: el vial solo se inclina hacia el cursor. El relevo
   entre uno y otro se hace por PROFUNDIDAD y no por un fundido plano: el que
   sale retrocede, se desenfoca y se apaga, mientras el que entra viene desde
   un punto por delante y aterriza nítido. Se cruzan con tiempos distintos
   —la opacidad va más rápida que la escala— que es lo que evita que parezca
   un simple cambio de diapositiva. Encima pasa un barrido de luz. */
.carrusel{cursor:default}
.carrusel .pila{position:absolute;inset:0;transition:transform .55s cubic-bezier(.22,.61,.36,1);
  transform:translate3d(calc(var(--px,0) * 11px), calc(var(--py,0) * 11px), 0)}
/* Solo `opacity` y `transform`, que el navegador resuelve en la GPU sin
   repintar. La versión anterior llevaba `filter:blur(12px)` y un `will-change`
   permanente en las ocho láminas: eso son ocho capas vivas y un desenfoque de
   540×1043 por fotograma, y en un equipo con los efectos del sistema apagados
   se desploma tanto que el relevo se ve como un corte seco. La profundidad se
   consigue igual con la escala, y ahora va fluido en cualquier máquina. */
.carrusel img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;
  opacity:0;transform:scale(1.07);
  transition:opacity 1.05s cubic-bezier(.4,0,.2,1),
             transform 1.45s cubic-bezier(.19,.72,.28,1)}
.carrusel img.on{opacity:1;transform:scale(1);will-change:opacity,transform}
/* el que se va no vuelve al punto de entrada: se aleja hacia atrás */
.carrusel img.sale{opacity:0;transform:scale(.93);will-change:opacity,transform}
.carrusel .brillo{position:absolute;inset:0;overflow:hidden;pointer-events:none;border-radius:3px}
.carrusel .brillo::after{content:"";position:absolute;top:-35%;bottom:-35%;width:32%;
  background:linear-gradient(100deg,transparent 0%,rgba(255,255,255,.62) 50%,transparent 100%);
  transform:translateX(-170%) rotate(9deg);animation:barrido 7.5s ease-in-out infinite}
@keyframes barrido{0%{transform:translateX(-170%) rotate(9deg)}
  60%,100%{transform:translateX(430%) rotate(9deg)}}
.carrusel:hover .brillo::after{animation-play-state:paused}
.puntos{display:flex;gap:7px;justify-content:center;margin-top:13px;max-width:410px;
  margin-inline:auto}
.puntos button{width:28px;height:3px;padding:0;border:0;border-radius:2px;cursor:pointer;
  background:var(--linea-2);transition:background .3s}
.puntos button:hover{background:var(--tinta-3)}
.puntos button[aria-current="true"]{background:var(--magenta)}

/* ── banda de cifras ───────────────────────────────────────────────── */
.banda{position:relative;z-index:1;border-block:1px solid var(--linea);
  background:color-mix(in srgb,var(--carbon) 72%,transparent)}
.banda .wrap{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;padding-inline:0}
.banda div{padding:20px clamp(14px,2vw,26px);border-left:1px solid var(--linea)}
.banda div:first-child{border-left:none}
.banda dt{font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--tinta-3);
  margin-bottom:7px}
.banda dd{margin:0;font-family:var(--mono);font-size:clamp(15px,1.5vw,20px);
  font-variant-numeric:tabular-nums}
.banda .ok dd{color:var(--aqua)}
@media (max-width:980px){ .banda .wrap{grid-template-columns:repeat(2,1fr)}
  .banda div:nth-child(odd){border-left:none}
  .banda div:nth-child(n+3){border-top:1px solid var(--linea)} }

/* ── secciones ─────────────────────────────────────────────────────── */
.pys-h26 section{position:relative;z-index:1;padding-block:clamp(48px,6.5vw,104px)}
.cab{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;
  flex-wrap:wrap;margin-bottom:clamp(22px,3vw,40px)}
.cab h2{font-size:clamp(28px,3.8vw,52px);max-width:22ch}
.cab .vs{display:block;margin-bottom:12px}
.cab p{color:var(--tinta-2);font-size:16px;max-width:52ch;margin-top:12px}
.link-mas{font-family:var(--mono);font-size:12px;color:var(--magenta);letter-spacing:.05em;
  white-space:nowrap}
.link-mas:hover{text-decoration:underline}

/* ── categorías ────────────────────────────────────────────────────── */
.cats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--linea);
  border:1px solid var(--linea);border-radius:3px;overflow:hidden}
.cat{background:var(--carbon);padding:22px 18px 18px;display:flex;flex-direction:column;
  gap:8px;min-height:150px;transition:background .22s}
.cat:hover{background:var(--panel)}
.cat .n{font-size:18px;line-height:1.25;margin-top:auto}
.cat .c{font-family:var(--mono);font-size:11px;color:var(--tinta-3)}
.cat .flecha{color:var(--magenta);font-family:var(--mono);font-size:13px;opacity:0;
  transform:translateX(-4px);transition:all .25s}
.cat:hover .flecha{opacity:1;transform:translateX(0)}
@media (max-width:980px){ .cats{grid-template-columns:repeat(2,1fr)} }
@media (max-width:520px){
  .cats{grid-template-columns:1fr}
  .cat{min-height:0;padding:16px 16px 15px}
  .cat .n{margin-top:2px}
}

/* ── catálogo ────────────────────────────────────────────────────────
   La tarjeta de producto se define DOS veces a propósito: aquí y en las piezas
   compartidas (pys-diseno/partes.php), que es la que usa el archivo de la
   tienda. La portada NO carga la hoja base del sitio —pys_dis_ajena() la
   salta—, así que cuando esta copia se quitó, el catálogo del home se quedó sin
   estilos: imágenes a tamaño natural, texto suelto y el «Agregar» sin botón.
   Las dos copias tienen que ser idénticas: si se cambia una, la otra. */
.filtros{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:24px}
.filtro{font-family:var(--mono);font-size:11.5px;letter-spacing:.05em;padding:8px 13px;
  border:1px solid var(--linea-2);background:transparent;color:var(--tinta-2);
  border-radius:2px;cursor:pointer;transition:all .18s}
.filtro:hover{border-color:var(--tinta-3);color:var(--tinta)}
.filtro[aria-pressed="true"]{background:var(--tinta);border-color:var(--tinta);color:var(--negro)}
.rejilla{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(12px,1.4vw,20px)}
@media (max-width:1040px){ .rejilla{grid-template-columns:repeat(3,1fr)} }
@media (max-width:780px){ .rejilla{grid-template-columns:repeat(2,1fr)} }

.tarjeta{border:1px solid var(--linea);border-radius:3px;overflow:hidden;background:var(--carbon);
  display:flex;flex-direction:column;transition:border-color .25s,box-shadow .25s}
.tarjeta[hidden]{display:none}
.tarjeta:hover{border-color:var(--linea-2);
  box-shadow:0 22px 50px -26px rgba(0,0,0,.95), 0 0 60px -26px rgba(2,246,200,.3)}
/* La imagen real de producto es una tarjeta tipográfica cuadrada sobre
   fondo casi blanco, no una foto recortada: va completa (`contain`) sobre
   la misma luz de vitrina para que no se le vea el borde. */
.tarjeta .foto{position:relative;aspect-ratio:1/1;overflow:hidden;display:block;
  background:radial-gradient(120% 86% at 50% 10%, #FFFFFF 0%, var(--vitrina) 58%, #DDE5E2 100%)}
.tarjeta .foto img{width:100%;height:100%;object-fit:contain;display:block;
  transition:transform .5s cubic-bezier(.22,.61,.36,1)}
.tarjeta:hover .foto img{transform:scale(1.045)}
/* Los renders 3D del vial traen su propio fondo cocido en el JPG: un degradado
   vertical #FCFEFD → #F5F7F6 → #D8E1DE (muestreado del archivo). La tarjeta usa
   exactamente ese degradado en lugar del radial de vitrina, así el recuadro de
   la imagen no se ve y el vial parece apoyado sobre la tarjeta. Va a sangre de
   arriba abajo, que es como luce el frasco. */
.tarjeta .foto.vial{background:linear-gradient(180deg,#FCFEFD 0%,#F5F7F6 50%,#D8E1DE 100%)}
.tarjeta .foto.vial img{width:auto;height:100%;margin-inline:auto}
.tarjeta:hover .foto.vial img{transform:scale(1.035) translateY(-4px)}
.tarjeta .sinfoto{width:100%;height:100%;display:grid;place-items:center;
  font-family:var(--mono);font-size:11px;letter-spacing:.14em;color:#8CA199}
.tarjeta .eti{position:absolute;top:10px;left:10px;font-family:var(--mono);font-size:9px;
  letter-spacing:.09em;padding:3px 7px;border:1px solid rgba(8,18,15,.2);color:#3E534E;
  border-radius:2px;background:rgba(255,255,255,.62)}
.tarjeta .agotado{position:absolute;inset:0;display:grid;place-items:center;
  background:rgba(8,16,14,.62);backdrop-filter:blur(1.5px)}
.tarjeta .agotado span{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--tinta);border:1px solid var(--tinta-3);padding:7px 12px;
  border-radius:2px;background:rgba(5,9,8,.75)}
.tarjeta .cuerpo{padding:15px 16px 0;flex:1}
.tarjeta h3{font-size:17.5px;line-height:1.22;overflow-wrap:anywhere}
.tarjeta h3 a:hover{color:var(--magenta)}
.tarjeta .sku{font-family:var(--mono);font-size:10.5px;color:var(--tinta-3);margin-top:7px;
  letter-spacing:.06em}
.tarjeta .specs{padding:11px 16px;margin-top:13px;border-top:1px solid var(--linea);
  font-family:var(--mono);font-size:10.5px;color:var(--tinta-3);display:flex;gap:7px;flex-wrap:wrap}
.tarjeta .compra{display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:13px 16px;border-top:1px solid var(--linea);background:var(--carbon-2);flex-wrap:wrap}
.tarjeta .precio{font-family:var(--mono);font-size:16px;font-variant-numeric:tabular-nums;
  color:var(--tinta)}
.tarjeta .precio del{color:var(--tinta-3);font-size:12.5px;margin-right:5px}
.tarjeta .precio ins{text-decoration:none}
.tarjeta .precio .woocommerce-Price-currencySymbol{font-size:11px;vertical-align:top}
/* El botón es el de WooCommerce (`add_to_cart_button ajax_add_to_cart`), para
   que agregue de verdad y dispare los fragmentos del carrito. */
.tarjeta .add{font-family:var(--mono);font-size:11px;letter-spacing:.06em;padding:9px 13px;
  border:1px solid var(--magenta);background:transparent;color:var(--magenta);border-radius:2px;
  cursor:pointer;transition:background .18s,color .18s;white-space:nowrap;display:inline-block}
.tarjeta .add:hover{background:var(--magenta);color:#fff}
.tarjeta .add.loading{opacity:.6;pointer-events:none}
.tarjeta .add.added{background:var(--aqua);border-color:var(--aqua);color:var(--negro)}
.tarjeta .add.agotado-b{border-color:var(--linea-2);color:var(--tinta-3);cursor:not-allowed}
.tarjeta .added_to_cart{display:none}


/* ── enfoque (visor + notas al desplazar) ──────────────────────────── */
.detalle .wrap{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,5vw,80px);
  align-items:start}
.detalle .pegado{position:sticky;top:104px}
.detalle .vitrina{max-width:430px;margin-inline:auto}
.notas{display:flex;flex-direction:column;gap:clamp(40px,13vh,130px);padding-block:10vh 20vh}
.nota{opacity:.28;transition:opacity .45s}
.nota.viva{opacity:1}
.nota .ord{font-family:var(--mono);font-size:11px;letter-spacing:.16em;color:var(--magenta)}
.nota h3{font-size:clamp(23px,2.7vw,36px);margin-block:12px 14px}
.nota p{color:var(--tinta-2);font-size:16.5px;max-width:44ch}
.nota .mas{display:inline-block;margin-top:14px;font-family:var(--mono);font-size:11.5px;
  letter-spacing:.06em;color:var(--magenta)}
.nota .mas:hover{text-decoration:underline}
@media (max-width:900px){ .detalle .wrap{grid-template-columns:1fr}
  .detalle .pegado{position:relative;top:0}
  .notas{padding-block:28px 0;gap:36px} .nota{opacity:1} }

/* ── certificados de análisis ──────────────────────────────────────── */
.coa .wrap{display:grid;grid-template-columns:.95fr 1.05fr;gap:clamp(24px,4.5vw,70px);
  align-items:center}
.coa h2{font-size:clamp(28px,3.8vw,50px);margin-block:12px 16px;max-width:17ch}
.coa .lede{color:var(--tinta-2);max-width:46ch}
.coa .estado{margin-top:26px;padding:16px 18px;border:1px solid var(--linea-2);border-radius:3px;
  background:var(--carbon);display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap}
.coa .estado .pt{width:7px;height:7px;border-radius:50%;background:var(--aqua);flex:none;
  margin-top:8px;box-shadow:0 0 0 4px color-mix(in srgb,var(--aqua) 16%,transparent)}
.coa .estado p{color:var(--tinta-2);font-size:15px;flex:1;min-width:230px}
.coa .estado a{color:var(--magenta);font-family:var(--mono);font-size:12px;letter-spacing:.05em;
  white-space:nowrap;align-self:center}
.coa .estado a:hover{text-decoration:underline}

/* El cromatograma es un DIBUJO EXPLICATIVO, no la medición de ningún lote: no
   lleva producto, ni número de lote, ni cifra de pureza. Solo enseña qué se
   está mirando cuando abres un certificado. */
.grafica{border:1px solid var(--linea-2);border-radius:3px;background:var(--carbon-2);
  overflow:hidden}
.grafica .cabg{padding:11px 15px;border-bottom:1px solid var(--linea);font-family:var(--mono);
  font-size:10.5px;letter-spacing:.07em;color:var(--tinta-3);display:flex;gap:12px;
  justify-content:space-between;flex-wrap:wrap}
.grafica .cabg b{color:var(--ambar);font-weight:500}
.grafica svg{display:block;width:100%;height:clamp(160px,20vw,240px)}
#traza{fill:none;stroke:var(--aqua);stroke-width:1.6;stroke-linejoin:round;
  filter:drop-shadow(0 0 6px rgba(2,246,200,.45))}
#areag{fill:rgba(2,246,200,.10);stroke:none}
.malla{stroke:var(--linea);stroke-width:1}
.ejeg{fill:var(--tinta-3);font-family:var(--mono);font-size:10px;letter-spacing:.07em}
.anot{fill:var(--tinta);font-family:var(--mono);font-size:11px;letter-spacing:.04em}
.anot.tenue{fill:var(--tinta-3)}
.guia-anot{stroke:var(--tinta-3);stroke-width:1;stroke-dasharray:2 3}
.grafica .pieg{padding:12px 15px;border-top:1px solid var(--linea);font-family:var(--mono);
  font-size:10px;letter-spacing:.06em;color:var(--tinta-3);line-height:1.5}
@media (max-width:900px){ .coa .wrap{grid-template-columns:1fr} }

/* ── confianza + producto destacado ────────────────────────────────── */
.confianza{background:var(--carbon);border-block:1px solid var(--linea)}
.confianza .wrap{display:grid;grid-template-columns:1.02fr .98fr;gap:clamp(24px,4.5vw,70px);
  align-items:center}
.confianza h2{font-size:clamp(28px,3.8vw,50px);margin-block:12px 16px;max-width:18ch}
.confianza .lede{color:var(--tinta-2);max-width:46ch}
.confianza .lede + .lede{margin-top:12px}
.pasos{list-style:none;margin:26px 0 0;padding:0;display:flex;flex-direction:column;gap:16px}
.pasos li{display:grid;grid-template-columns:30px 1fr;gap:14px;align-items:start}
.pasos .n{font-family:var(--mono);font-size:11px;color:var(--magenta);letter-spacing:.1em;
  padding-top:4px}
.pasos b{font-weight:400;display:block;font-size:17px;margin-bottom:3px}
.pasos p{color:var(--tinta-2);font-size:15px}
.destacado{border:1px solid var(--linea-2);border-radius:3px;background:var(--carbon-2);
  overflow:hidden}
.destacado .cabd{padding:11px 15px;border-bottom:1px solid var(--linea);font-family:var(--mono);
  font-size:10.5px;letter-spacing:.07em;color:var(--tinta-3);display:flex;gap:12px;
  justify-content:space-between;flex-wrap:wrap}
.destacado .cabd b{color:var(--aqua);font-weight:500}
.destacado .imgd{background:radial-gradient(120% 86% at 50% 10%, #FFF 0%, var(--vitrina) 58%,
  #DDE5E2 100%);aspect-ratio:16/10;display:block;overflow:hidden}
.destacado .imgd img{width:100%;height:100%;object-fit:contain;display:block}
/* con el render del vial la caja se hace cuadrada: en 16/10 el frasco, que es
   más alto que ancho, quedaba diminuto */
.destacado .imgd.vial{aspect-ratio:1/1;
  background:linear-gradient(180deg,#FCFEFD 0%,#F5F7F6 50%,#D8E1DE 100%)}
.destacado .imgd.vial img{width:auto;margin-inline:auto}
.destacado .cuerpod{padding:18px 18px 4px}
.destacado h3{font-size:22px;margin-bottom:10px}
.destacado ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:7px}
.destacado li{color:var(--tinta-2);font-size:15px;display:flex;gap:9px;align-items:baseline}
.destacado li::before{content:"—";color:var(--magenta);font-family:var(--mono);font-size:11px;
  flex:none}
.destacado .comprad{display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:16px 18px;margin-top:16px;border-top:1px solid var(--linea);flex-wrap:wrap}
.destacado .precio{font-family:var(--mono);font-size:19px;font-variant-numeric:tabular-nums}
.destacado .precio .woocommerce-Price-currencySymbol{font-size:12px;vertical-align:top}
@media (max-width:900px){ .confianza .wrap{grid-template-columns:1fr} }

/* ── guías ─────────────────────────────────────────────────────────── */
.guias{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(12px,1.4vw,18px)}
.guia{border:1px solid var(--linea);border-radius:3px;background:var(--carbon);padding:20px;
  display:flex;flex-direction:column;gap:10px;transition:border-color .22s,background .22s}
.guia:hover{border-color:color-mix(in srgb,var(--magenta) 55%,transparent);background:var(--carbon-2)}
.guia h3{font-size:17px;line-height:1.28}
.guia .meta{font-family:var(--mono);font-size:10.5px;color:var(--tinta-3);letter-spacing:.06em;
  margin-top:auto;padding-top:10px;display:flex;justify-content:space-between;gap:10px}
@media (max-width:920px){ .guias{grid-template-columns:repeat(2,1fr)} }
@media (max-width:560px){ .guias{grid-template-columns:1fr} }

/* ── preguntas ─────────────────────────────────────────────────────── */
.faq{border-top:1px solid var(--linea)}
.faq .wrap{display:grid;grid-template-columns:.8fr 1.2fr;gap:clamp(24px,4vw,64px);align-items:start}
.faq details{border-bottom:1px solid var(--linea)}
.faq summary{padding:18px 0;cursor:pointer;list-style:none;display:flex;gap:14px;
  align-items:baseline;font-size:18px;transition:color .2s}
.faq summary::-webkit-details-marker{display:none}
.faq summary::before{content:"+";font-family:var(--mono);color:var(--magenta);font-size:15px;flex:none}
.faq details[open] summary::before{content:"−"}
.faq summary:hover{color:var(--magenta)}
.faq details .r{padding:0 0 18px 28px;color:var(--tinta-2);font-size:16px;max-width:64ch}
.faq details .r a{color:var(--magenta)}
.faq details .r a:hover{text-decoration:underline}
.faq details .r ul{margin:10px 0 0;padding-left:18px;display:flex;flex-direction:column;gap:6px}
@media (max-width:860px){ .faq .wrap{grid-template-columns:1fr} }

/* ── pie ───────────────────────────────────────────────────────────── */
.pys-h26 footer.pie-h26{border-top:1px solid var(--linea-2);background:var(--carbon);
  padding-block:44px 28px;position:relative;z-index:1}
.pie{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:28px}
.pie p{color:var(--tinta-2);font-size:14px;max-width:46ch;line-height:1.6}
.pie .marca{margin-bottom:14px}
.pie h4{margin:0 0 12px;font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--tinta-3)}
.pie ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px;font-size:15px}
.pie a{color:var(--tinta-2)}
.pie a:hover{color:var(--tinta)}
.aviso-inv{margin-top:32px;padding-top:16px;border-top:1px solid var(--linea);
  color:var(--tinta-3);font-size:13.5px;max-width:78ch;line-height:1.6}
.fin{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:18px;
  padding-top:16px;border-top:1px solid var(--linea);font-family:var(--mono);font-size:10.5px;
  color:var(--tinta-3);letter-spacing:.06em}
@media (max-width:820px){ .pie{grid-template-columns:1fr 1fr} }
@media (max-width:520px){ .pie{grid-template-columns:1fr} }

/* ── teléfono ──────────────────────────────────────────────────────── */
@media (max-width:440px){
  .rejilla{gap:10px}
  .tarjeta .cuerpo{padding:12px 12px 0}
  .tarjeta h3{font-size:15.5px}
  .tarjeta .sku{font-size:9.5px}
  .tarjeta .specs{display:none}
  .tarjeta .compra{padding:11px 12px;gap:8px}
  .tarjeta .precio{font-size:14.5px}
  .tarjeta .add{padding:8px 10px;font-size:10px}
  .tarjeta .eti{font-size:8px;padding:2px 5px;top:8px;left:8px}
}
@media (max-width:340px){ .rejilla{grid-template-columns:1fr} }
</style>
</head>
<?php
/* El hexagonal global del sitio se apaga aquí y no en la hoja: en el atributo
   `style` ninguna regla externa puede ganarle. El diseño se apoya en el negro
   plano más el halo que sigue al cursor; las dos texturas juntas ensucian. */
?>
<body <?php body_class( 'pys-h26' ); ?> style="background-image:none!important;background-color:#050908!important">
<?php wp_body_open(); ?>
<div class="hexes" aria-hidden="true"><span class="base"></span><span class="viva"></span></div>
<div id="halo" aria-hidden="true"></div>

<?php
/* Promoción vigente y condiciones de envío, tomadas de la configuración real
   de WooCommerce y de la Política de Envíos y Devoluciones del sitio. */
?>
<?php
/* Avisos del cintillo. Las formas de pago son las pasarelas realmente activas
   en la tienda: transferencia (bacs), tarjeta y Mercado Pago, el efectivo de
   Mercado Pago —que es el depósito en OXXO— y el módulo de criptomonedas. */
$pys_avisos = array(
	'<span class="promo">◆ <b>3 ml de solución bacteriostática</b> incluidos con cada péptido</span>',
	'<span>Envío nacional · <b>2 a 5 días hábiles</b></span>',
);
if ( $pys_envio_gratis ) {
	$pys_avisos[] = '<span>Envío gratuito desde <b>' . esc_html( $pys_moneda( $pys_envio_gratis ) ) . ' MXN</b></span>';
}
if ( $pys_envio_fijo ) {
	$pys_avisos[] = '<span>Tarifa fija <b>' . esc_html( $pys_moneda( $pys_envio_fijo ) ) . ' MXN</b></span>';
}
$pys_avisos[] = '<span>Transferencia · tarjeta · Mercado Pago · <b>depósito en OXXO</b> · cripto</span>';
?>
<div class="cintillo">
  <div class="tira">
    <?php
    /* El grupo va dos veces: el segundo es solo relleno para que el bucle no
       enseñe el hueco, así que se esconde de los lectores de pantalla. */
    for ( $pys_i = 0; $pys_i < 2; $pys_i++ ) :
      ?>
      <div class="grupo"<?php echo $pys_i ? ' aria-hidden="true"' : ''; ?>>
        <?php foreach ( $pys_avisos as $pys_j => $pys_aviso ) : ?>
          <?php if ( $pys_j ) : ?><span class="sep" aria-hidden="true">◆</span><?php endif; ?>
          <?php echo wp_kses_post( $pys_aviso ); ?>
        <?php endforeach; ?>
        <span class="sep" aria-hidden="true">◆</span>
      </div>
    <?php endfor; ?>
  </div>
</div>

<header class="top">
  <div class="wrap">
    <a class="marca" href="<?php echo esc_url( $pys_url['inicio'] ); ?>">
      <img class="logo" src="<?php echo esc_url( pys_h26_uri( 'img/logo-pys.png' ) ); ?>"
           width="75" height="96" alt="" decoding="async">
      <span class="nom">Péptidos y Suplementos MX</span>
    </a>

    <nav class="menu" aria-label="Principal">
      <a href="<?php echo esc_url( $pys_url['peptidos'] ); ?>">Péptidos</a>
      <a href="<?php echo esc_url( $pys_url['glp1'] ); ?>">GLP-1</a>
      <a href="<?php echo esc_url( $pys_url['suplementos'] ); ?>">Suplementos</a>
      <a href="<?php echo esc_url( $pys_url['productos'] ); ?>">Productos</a>
      <div class="desp" data-abierto="0">
        <button type="button" aria-expanded="false" aria-controls="desp-obj">Por objetivo
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.4" aria-hidden="true"><path d="M5 9l7 7 7-7"/></svg>
        </button>
        <ul id="desp-obj">
          <li><a href="<?php echo esc_url( $pys_url['metabolismo'] ); ?>">Metabolismo</a></li>
          <li><a href="<?php echo esc_url( $pys_url['reparacion'] ); ?>">Reparación celular</a></li>
          <li><a href="<?php echo esc_url( $pys_url['longevidad'] ); ?>">Longevidad</a></li>
          <li><a href="<?php echo esc_url( $pys_url['performance'] ); ?>">Performance</a></li>
        </ul>
      </div>
      <a href="#coa">COA</a>
      <a href="<?php echo esc_url( $pys_url['calculadora'] ); ?>">Calculadora</a>
      <a href="<?php echo esc_url( $pys_url['blog'] ); ?>">Blog</a>
    </nav>

    <div class="iconos">
      <button class="icob burger" id="burger" aria-label="Abrir menú" aria-expanded="false"
              aria-controls="mnav">
        <svg class="abre" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="1.9" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        <svg class="cierra" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="1.9" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>
      <button class="icob" id="lupa" aria-label="Buscar productos" aria-expanded="false"
              aria-controls="busca">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="1.9" aria-hidden="true"><circle cx="11" cy="11" r="7"/>
          <path d="M20 20l-3.6-3.6"/></svg>
      </button>
      <a class="icob" href="<?php echo esc_url( $pys_url['cuenta'] ); ?>" aria-label="Mi cuenta">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="8" r="3.6"/>
          <path d="M4.5 20c.9-3.8 3.9-5.8 7.5-5.8s6.6 2 7.5 5.8"/></svg>
      </a>
      <a class="icob" href="<?php echo esc_url( $pys_url['carrito'] ); ?>" aria-label="Ver carrito">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="1.8" aria-hidden="true">
          <path d="M3 4h2l2.6 11.4a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 8H6"/>
          <circle cx="10" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/></svg>
        <?php
        $pys_n_cart = ( function_exists( 'WC' ) && WC()->cart ) ? WC()->cart->get_cart_contents_count() : 0;
        ?>
        <span class="pys-cart-n" id="pys-cart-n"<?php echo $pys_n_cart ? '' : ' hidden'; ?>><?php echo esc_html( $pys_n_cart ); ?></span>
      </a>
    </div>
  </div>

  <div id="busca" hidden>
    <form class="wrap" role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>">
      <label class="sr" for="q-h26">Buscar productos</label>
      <input type="search" id="q-h26" name="s" placeholder="Buscar un péptido o suplemento…" autocomplete="off">
      <input type="hidden" name="post_type" value="product">
      <button type="submit">BUSCAR</button>
    </form>
  </div>

  <div id="mnav" hidden><div class="wrap">
    <span class="et">Catálogo</span>
    <a href="<?php echo esc_url( $pys_url['peptidos'] ); ?>">Péptidos</a>
    <a href="<?php echo esc_url( $pys_url['glp1'] ); ?>">GLP-1</a>
    <a href="<?php echo esc_url( $pys_url['suplementos'] ); ?>">Suplementos</a>
    <a href="<?php echo esc_url( $pys_url['productos'] ); ?>">Productos<span class="k"><?php echo count( $pys_productos ); ?> REF.</span></a>
    <span class="et">Por objetivo</span>
    <a href="<?php echo esc_url( $pys_url['metabolismo'] ); ?>">Metabolismo</a>
    <a href="<?php echo esc_url( $pys_url['reparacion'] ); ?>">Reparación celular</a>
    <a href="<?php echo esc_url( $pys_url['longevidad'] ); ?>">Longevidad</a>
    <a href="<?php echo esc_url( $pys_url['performance'] ); ?>">Performance</a>
    <span class="et">Calidad</span>
    <a href="#coa">Certificados de análisis</a>
    <span class="et">Recursos</span>
    <a href="<?php echo esc_url( $pys_url['calculadora'] ); ?>">Calculadora de dosis</a>
    <a href="<?php echo esc_url( $pys_url['blog'] ); ?>">Blog<span class="k"><?php echo (int) $pys_total_guias; ?></span></a>
    <a href="<?php echo esc_url( $pys_url['contacto'] ); ?>">Contacto</a>
    <span class="et">Cuenta</span>
    <a href="<?php echo esc_url( $pys_url['cuenta'] ); ?>">Mi cuenta</a>
    <a href="<?php echo esc_url( $pys_url['carrito'] ); ?>">Carrito</a>
  </div></div>
</header>

<div class="hero" id="top">
  <div class="wrap">
    <div>
      <span class="vs" data-rev>Péptidos y Suplementos de Alta Pureza en México</span>
      <h1 data-rev>Comprar Péptidos en México <em>para Salud, Biohacking y Alto rendimiento</em></h1>
      <p class="lede" data-rev>En PyS reunimos una selección especializada de péptidos y suplementos
        en México para personas que buscan optimizar su bienestar, metabolismo, recuperación física,
        longevidad y rendimiento.</p>
      <p class="lede" data-rev>Nuestro enfoque combina productos de alta pureza, información clara,
        atención personalizada y envío nacional para quienes desean integrar herramientas avanzadas
        de biohacking y suplementación especializada.</p>
      <div class="cta" data-rev>
        <a class="btn pri" href="#catalogo">Ver productos</a>
        <a class="btn" href="<?php echo esc_url( $pys_url['calculadora'] ); ?>">Calculadora de dosis</a>
      </div>
      <div class="sellos" data-rev>
        <span class="sello ok">Pureza 99% HPLC</span>
        <span class="sello"><?php echo count( $pys_productos ); ?> referencias</span>
        <span class="sello">Envío nacional</span>
        <span class="sello">Atención personalizada</span>
      </div>
    </div>
    <div>
      <?php
      /* El visor muestra la etiqueta real del vial de Retatrutida 30 mg: es un
         render, igual que las imágenes del catálogo, no una fotografía. */
      $pys_reta = get_page_by_path( 'retatrutida', OBJECT, 'product' );
      $pys_reta_url = $pys_reta ? get_permalink( $pys_reta ) : $pys_url['productos'];
      ?>
      <div class="vitrina carrusel" id="carrusel">
        <div class="lienzo"></div>
        <div class="pila">
          <?php foreach ( $pys_carrusel as $pys_k => $pys_c ) : ?>
            <img<?php echo $pys_k ? '' : ' class="on"'; ?>
                 src="<?php echo esc_url( pys_h26_uri( 'img/' . $pys_c['vial'] ) ); ?>"
                 width="540" height="1043"
                 <?php
                 /* `eager` explícito en la primera: es la imagen grande del
                    héroe y algo del stack le estaba metiendo `lazy`, que la
                    retrasa justo cuando es lo que mide el LCP. */
                 echo $pys_k ? 'loading="lazy"' : 'loading="eager" fetchpriority="high"';
                 ?> decoding="async"
                 alt="<?php echo esc_attr( 'Vial de ' . $pys_c['nombre'] ); ?>">
          <?php endforeach; ?>
        </div>
        <span class="brillo" aria-hidden="true"></span>
        <span class="marco" aria-hidden="true"></span>
      </div>
      <p class="pie-vitrina">
        <span class="mono" id="car-eti">RENDER · <?php echo esc_html( mb_strtoupper( $pys_carrusel[0]['nombre'] ) ); ?></span>
        <a id="car-link" href="<?php echo esc_url( $pys_carrusel[0]['url'] ); ?>"
           aria-label="Ver <?php echo esc_attr( $pys_carrusel[0]['nombre'] ); ?>">Ver el producto →</a>
      </p>
      <div class="puntos" id="car-puntos" role="tablist" aria-label="Productos destacados">
        <?php foreach ( $pys_carrusel as $pys_k => $pys_c ) : ?>
          <button type="button" role="tab" data-i="<?php echo (int) $pys_k; ?>"
                  aria-current="<?php echo $pys_k ? 'false' : 'true'; ?>"
                  aria-label="<?php echo esc_attr( $pys_c['nombre'] ); ?>"></button>
        <?php endforeach; ?>
      </div>
      <script type="application/json" id="car-datos"><?php
        echo wp_json_encode( array_map( function ( $p ) {
          return array( 'n' => $p['nombre'], 'u' => $p['url'] );
        }, $pys_carrusel ), JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES );
      ?></script>
    </div>
  </div>
</div>

<div class="banda">
  <dl class="wrap">
    <div><dt>Referencias</dt><dd><?php echo count( $pys_productos ); ?></dd></div>
    <div class="ok"><dt>En existencia</dt><dd><?php echo (int) $pys_en_stock; ?></dd></div>
    <div><dt>Categorías</dt><dd><?php echo count( $pys_cats ); ?></dd></div>
    <div><dt>Guías publicadas</dt><dd><?php echo (int) $pys_total_guias; ?></dd></div>
    <div><dt>Envío</dt><dd style="font-family:var(--optima);font-size:18px">Nacional · 2 a 5 días</dd></div>
  </dl>
</div>

<section id="categorias">
  <div class="wrap">
    <div class="cab">
      <div><span class="vs">Áreas de enfoque</span>
        <h2>Soluciones para recuperación, metabolismo y performance</h2></div>
      <a class="link-mas" href="#catalogo">Ver las <?php echo count( $pys_productos ); ?> referencias →</a>
    </div>
    <div class="cats">
      <?php foreach ( $pys_cats as $c ) : ?>
        <a class="cat" href="<?php echo esc_url( is_wp_error( $c['url'] ) ? $pys_url['productos'] : $c['url'] ); ?>">
          <span class="c"><?php echo (int) $c['n']; ?> <?php echo 1 === $c['n'] ? 'referencia' : 'referencias'; ?></span>
          <span class="n"><?php echo esc_html( $c['largo'] ); ?></span>
          <span class="flecha">Ver →</span>
        </a>
      <?php endforeach; ?>
      <?php
      /* Las categorías rara vez son múltiplo de 4 y la retícula se queda con
         un hueco. Esta última tarjeta lo llena con algo que sirve. */
      ?>
      <a class="cat" href="<?php echo esc_url( $pys_url['productos'] ); ?>">
        <span class="c"><?php echo count( $pys_productos ); ?> referencias</span>
        <span class="n">Ver todo el catálogo</span>
        <span class="flecha">Ver →</span>
      </a>
    </div>
  </div>
</section>

<section id="catalogo">
  <div class="wrap">
    <div class="cab">
      <div><span class="vs">Catálogo especializado en México</span>
        <h2>Catálogo</h2>
        <p>Explora el catálogo de PyS: péptidos y suplementos en México para investigación,
          metabolismo, recuperación física, biohacking y alto rendimiento. Precios y existencias
          se leen directamente de la tienda.</p></div>
      <span class="vs mono" id="cuenta"><?php echo count( $pys_productos ); ?> REFERENCIAS</span>
    </div>

    <div class="filtros" id="filtros" role="group" aria-label="Filtrar catálogo">
      <button class="filtro" type="button" data-f="todo" aria-pressed="true">Todo</button>
      <?php foreach ( $pys_cats as $c ) : ?>
        <button class="filtro" type="button" data-f="<?php echo esc_attr( $c['slug'] ); ?>"
                aria-pressed="false"><?php echo esc_html( $c['corto'] ); ?></button>
      <?php endforeach; ?>
    </div>

    <div class="rejilla" id="rejilla">
      <?php foreach ( $pys_productos as $p ) : ?>
        <article class="tarjeta" data-cats="<?php echo esc_attr( implode( ' ', $p['cats'] ) ); ?>">
          <a class="foto<?php echo $p['vial'] ? ' vial' : ''; ?>" href="<?php echo esc_url( $p['url'] ); ?>"
             aria-label="Ver <?php echo esc_attr( $p['nombre'] ); ?>">
            <?php if ( $p['cat'] ) : ?>
              <span class="eti"><?php echo esc_html( $p['cat'] ); ?></span>
            <?php endif; ?>
            <?php
            echo $p['img'] // phpcs:ignore WordPress.Security.EscapeOutput — wp_get_attachment_image ya escapa.
                ? $p['img']
                : '<span class="sinfoto">SIN IMAGEN</span>';
            ?>
            <?php if ( ! $p['stock'] ) : ?>
              <span class="agotado"><span>Agotado</span></span>
            <?php endif; ?>
          </a>
          <div class="cuerpo">
            <h3><a href="<?php echo esc_url( $p['url'] ); ?>"><?php echo esc_html( $p['nombre'] ); ?></a></h3>
            <?php if ( $p['sku'] ) : ?>
              <div class="sku">SKU <?php echo esc_html( $p['sku'] ); ?></div>
            <?php endif; ?>
          </div>
          <div class="specs">
            <span><?php echo esc_html( $p['cat'] ? $p['cat'] : 'Catálogo' ); ?></span>
            <span>·</span>
            <span><?php echo $p['stock'] ? 'en existencia' : 'sin existencia'; ?></span>
          </div>
          <div class="compra">
            <span class="precio"><?php echo wp_kses_post( $p['precio'] ); ?></span>
            <?php if ( ! $p['stock'] ) : ?>
              <span class="add agotado-b">Agotado</span>
            <?php elseif ( 'simple' === $p['tipo'] && $p['comprable'] ) : ?>
              <a class="add add_to_cart_button ajax_add_to_cart"
                 href="?add-to-cart=<?php echo (int) $p['id']; ?>"
                 data-quantity="1"
                 data-product_id="<?php echo (int) $p['id']; ?>"
                 data-product_sku="<?php echo esc_attr( $p['sku'] ); ?>"
                 aria-label="Agregar <?php echo esc_attr( $p['nombre'] ); ?> al carrito"
                 rel="nofollow">Agregar</a>
            <?php else : ?>
              <a class="add" href="<?php echo esc_url( $p['url'] ); ?>">Elegir opciones</a>
            <?php endif; ?>
          </div>
        </article>
      <?php endforeach; ?>
    </div>
  </div>
</section>

<section class="detalle" id="enfoque">
  <div class="wrap">
    <div class="pegado">
      <div class="vitrina" id="vitrina2" role="img"
           aria-label="El mismo vial girando conforme lees">
        <div class="lienzo"></div>
        <span class="marco" aria-hidden="true"></span>
        <span class="grados mono" id="grados2">0°</span>
      </div>
    </div>
    <div class="notas" id="notas">
      <div class="nota">
        <span class="ord">01 · RECUPERACIÓN</span>
        <h3>Recuperación física y reparación muscular</h3>
        <p>La recuperación es parte esencial del progreso. Por eso, nuestra línea incluye productos
          orientados a personas activas, deportistas y perfiles que buscan cuidar su rendimiento,
          mejorar su constancia y mantener una rutina física más eficiente.</p>
        <a class="mas" href="<?php echo esc_url( $pys_url['reparacion'] ); ?>">Ver recuperación muscular →</a>
      </div>
      <div class="nota">
        <span class="ord">02 · METABOLISMO</span>
        <h3>Optimización metabólica y energía celular</h3>
        <p>El rendimiento físico, la energía diaria y el bienestar metabólico dependen de múltiples
          factores: descanso, nutrición, entrenamiento, hábitos y suplementación inteligente. En PyS
          ofrecemos una línea especializada orientada a quienes buscan un enfoque más avanzado.</p>
        <a class="mas" href="<?php echo esc_url( $pys_url['metabolismo'] ); ?>">Ver metabolismo →</a>
      </div>
      <div class="nota">
        <span class="ord">03 · PERFORMANCE</span>
        <h3>Performance física y enfoque mental</h3>
        <p>Desbloquea tu máximo output físico y mental. Supera cualquier estancamiento optimizando
          la producción de energía a nivel mitocondrial. Nuestra línea para rendimiento está pensada
          para quienes buscan fuerza, claridad mental, resistencia y mayor constancia en su rutina.</p>
        <a class="mas" href="<?php echo esc_url( $pys_url['performance'] ); ?>">Ver performance →</a>
      </div>
    </div>
  </div>
</section>

<?php
/* Trazo del cromatograma de ejemplo: suma de gaussianas, calculada aquí y no
   en JavaScript para que el dibujo exista aunque el script no corra. Las
   cifras son de forma, no de medición: describen una curva bonita, no un lote. */
$pys_picos = array( array( 760, 20, 232 ), array( 250, 10, 17 ), array( 980, 14, 13 ),
	array( 400, 9, 9 ), array( 600, 8, 6 ) );
$pys_d = '';
for ( $x = 0; $x <= 1200; $x += 2 ) {
	$y = 0.0;
	foreach ( $pys_picos as $p ) {
		$y += $p[2] * exp( - ( ( $x - $p[0] ) ** 2 ) / ( 2 * $p[1] ** 2 ) );
	}
	$pys_d .= ( $x ? 'L' : 'M' ) . $x . ',' . number_format( 268 - $y, 2, '.', '' );
}
?>
<section class="coa" id="coa">
  <div class="wrap">
    <div>
      <span class="vs">Certificados de análisis</span>
      <h2>Qué es un COA y cómo se lee</h2>
      <p class="lede">Un certificado de análisis es el reporte que el laboratorio emite para un
        lote concreto. No es un sello ni un logotipo: es una medición, y por eso se puede
        comprobar. Estos son los tres datos que hay que saber mirar.</p>
      <ol class="pasos">
        <li><span class="n">01</span><div><b>Pureza, por HPLC</b>
          <p>La cromatografía líquida separa el compuesto de todo lo que no lo es. El área del
            pico principal, comparada con la de los demás, es el porcentaje de pureza.</p></div></li>
        <li><span class="n">02</span><div><b>Identidad, por espectrometría de masas</b>
          <p>Confirma que la molécula pesa lo que debería pesar. Una pureza alta con la masa
            equivocada no es un buen producto: es otro compuesto.</p></div></li>
        <li><span class="n">03</span><div><b>Número de lote</b>
          <p>Es lo que ata el certificado a tu vial. Un COA sin lote, o con un lote que no
            coincide con el impreso en la etiqueta, no prueba nada.</p></div></li>
      </ol>
      <?php
      /* Se lee del propio catálogo: conforme se le cargue el COA a un producto,
         este recuadro se actualiza solo y deja de mandar a contacto a secas. */
      $pys_coas   = function_exists( 'pys_coa_productos' ) ? pys_coa_productos() : array();
      $pys_n_coa  = count( $pys_coas );
      $pys_coa_id = $pys_n_coa ? array_key_first( $pys_coas ) : 0;
      ?>
      <div class="estado">
        <span class="pt" aria-hidden="true"></span>
        <?php if ( $pys_n_coa ) : ?>
          <p><?php echo 1 === $pys_n_coa ? 'Ya hay un certificado publicado' : 'Ya hay ' . (int) $pys_n_coa . ' certificados publicados'; ?>
            en la ficha de su producto, y seguimos subiendo el resto conforme el laboratorio nos
            los entrega. Si necesitas el de un lote en concreto,
            <a href="<?php echo esc_url( $pys_url['contacto'] ); ?>" style="color:inherit;text-decoration:underline">escríbenos</a>.</p>
          <a href="<?php echo esc_url( get_permalink( $pys_coa_id ) ); ?>#pys-coa">Ver un certificado →</a>
        <?php else : ?>
          <p>Estamos incorporando el certificado de cada lote en la ficha de su producto, conforme
            el laboratorio nos lo entrega. Si necesitas el de un lote en concreto, escríbenos.</p>
          <a href="<?php echo esc_url( $pys_url['contacto'] ); ?>">Solicitar un COA →</a>
        <?php endif; ?>
      </div>
    </div>

    <figure class="grafica" style="margin:0">
      <div class="cabg">
        <span>CÓMO SE LEE UN CROMATOGRAMA</span>
        <span><b>EJEMPLO ILUSTRATIVO</b></span>
      </div>
      <svg viewBox="0 0 1200 300" preserveAspectRatio="none" role="img"
           aria-label="Dibujo de un cromatograma: un pico principal alto y varios picos pequeños
                       de impurezas sobre un eje de tiempo en minutos. Es un ejemplo explicativo,
                       no la medición de un lote.">
        <g class="malla">
          <line x1="0" y1="268" x2="1200" y2="268"/>
          <line x1="0" y1="201" x2="1200" y2="201" opacity=".5"/>
          <line x1="0" y1="134" x2="1200" y2="134" opacity=".5"/>
          <line x1="0" y1="67" x2="1200" y2="67" opacity=".5"/>
        </g>
        <path id="areag" d="<?php echo esc_attr( $pys_d . 'L1200,268L0,268Z' ); ?>"></path>
        <path id="traza" d="<?php echo esc_attr( $pys_d ); ?>"></path>
        <line class="guia-anot" x1="760" y1="30" x2="760" y2="40"/>
        <text class="anot" x="760" y="22" text-anchor="middle">PICO PRINCIPAL → PUREZA</text>
        <line class="guia-anot" x1="250" y1="236" x2="250" y2="248"/>
        <text class="anot tenue" x="250" y="228" text-anchor="middle">IMPUREZAS</text>
        <g class="ejeg">
          <text x="4" y="290">0</text><text x="296" y="290">4</text>
          <text x="596" y="290">8</text><text x="896" y="290">12</text>
          <text x="1150" y="290">16 min</text>
        </g>
      </svg>
      <figcaption class="pieg">Eje horizontal, el tiempo que tarda cada componente en salir de la
        columna; eje vertical, la respuesta del detector. Dibujo explicativo: no corresponde a
        ningún lote ni producto.</figcaption>
    </figure>
  </div>
</section>

<section class="confianza" id="confianza">
  <div class="wrap">
    <div>
      <span class="vs">Confianza y claridad</span>
      <h2>Calidad, pureza y trazabilidad</h2>
      <p class="lede">Al comprar péptidos en México, la confianza es fundamental. En PyS buscamos
        ofrecer información clara sobre cada producto: presentación, concentración, manejo,
        disponibilidad y características generales.</p>
      <p class="lede">Nuestro objetivo es que puedas elegir con mayor claridad dentro de un catálogo
        especializado de péptidos y suplementos.</p>
      <ol class="pasos">
        <li><span class="n">01</span><div><b>Envío nacional</b>
          <p>Cobertura principal en México, con un tiempo estimado de 2 a 5 días hábiles.
            Tarifa fija de <?php echo esc_html( $pys_moneda( $pys_envio_fijo ? $pys_envio_fijo : 250 ) ); ?> MXN
            <?php if ( $pys_envio_gratis ) : ?>
              y envío gratuito en pedidos superiores a <?php echo esc_html( $pys_moneda( $pys_envio_gratis ) ); ?> MXN
            <?php endif; ?>.</p></div></li>
        <li><span class="n">02</span><div><b>Devoluciones con plazo claro</b>
          <p>14 días naturales a partir de la entrega, con el producto en su empaque original y
            sellado. El reembolso se procesa en un máximo de 7 días hábiles tras recibirlo.</p></div></li>
        <li><span class="n">03</span><div><b>Uso de investigación</b>
          <p>Los productos se presentan para uso de investigación. La información del catálogo busca
            facilitar una navegación clara y responsable.</p></div></li>
      </ol>
    </div>

    <?php
    /* Producto destacado: el mismo que ya destaca el home actual, pero con su
       precio, existencia e imagen leídos en vivo. */
    $pys_d = $pys_reta && function_exists( 'wc_get_product' ) ? wc_get_product( $pys_reta->ID ) : null;
    ?>
    <?php if ( $pys_d ) : ?>
      <div class="destacado">
        <div class="cabd">
          <span>PRODUCTO DESTACADO</span>
          <span><?php echo $pys_d->is_in_stock() ? '<b>EN EXISTENCIA</b>' : 'AGOTADO'; ?></span>
        </div>
        <?php $pys_vd = pys_dis_vial( $pys_reta->ID ); ?>
        <a class="imgd<?php echo $pys_vd ? ' vial' : ''; ?>" href="<?php echo esc_url( get_permalink( $pys_reta ) ); ?>">
          <?php if ( $pys_vd ) : ?>
            <img src="<?php echo esc_url( pys_h26_uri( 'img/' . $pys_vd ) ); ?>" width="540" height="1043"
                 loading="lazy" decoding="async"
                 alt="Vial de <?php echo esc_attr( pys_h26_nombre( $pys_d->get_name() ) ); ?>">
          <?php else : ?>
            <?php echo wp_kses_post( $pys_d->get_image( 'large', array( 'alt' => $pys_d->get_name() ) ) ); ?>
          <?php endif; ?>
        </a>
        <div class="cuerpod">
          <h3><?php echo esc_html( pys_h26_nombre( $pys_d->get_name() ) ); ?></h3>
          <ul>
            <li>Regulación del apetito</li>
            <li>Mejora de la sensibilidad metabólica</li>
            <li>Apoyo en pérdida de grasa</li>
          </ul>
        </div>
        <div class="comprad">
          <span class="precio"><?php echo wp_kses_post( $pys_d->get_price_html() ); ?></span>
          <a class="btn pri" href="<?php echo esc_url( get_permalink( $pys_reta ) ); ?>">Ver producto</a>
        </div>
      </div>
    <?php endif; ?>
  </div>
</section>

<section id="guias">
  <div class="wrap">
    <div class="cab">
      <div><span class="vs">Blog</span>
        <h2>Información clara antes de comprar</h2>
        <p>Información especializada en péptidos, suplementos, biohacking y bienestar avanzado.
          Contenido claro para rendimiento, metabolismo, recuperación y longevidad.</p></div>
      <a class="link-mas" href="<?php echo esc_url( $pys_url['blog'] ); ?>">Ver el blog →</a>
    </div>
    <div class="guias">
      <?php foreach ( $pys_guias as $g ) : ?>
        <a class="guia" href="<?php echo esc_url( get_permalink( $g ) ); ?>">
          <h3><?php echo esc_html( get_the_title( $g ) ); ?></h3>
          <div class="meta">
            <span><?php echo esc_html( get_the_date( 'j M Y', $g ) ); ?></span>
            <span><?php echo max( 1, (int) round( preg_match_all( "/\S+/u", wp_strip_all_tags( $g->post_content ) ) / 220 ) ); ?> min</span>
          </div>
        </a>
      <?php endforeach; ?>
    </div>
  </div>
</section>

<section class="faq" id="faq">
  <div class="wrap">
    <div><span class="vs">Preguntas</span>
      <h2 style="font-size:clamp(26px,3.4vw,44px);margin-top:12px">Información de compra</h2></div>
    <div>
      <details open>
        <summary>¿Cuánto tarda y cuánto cuesta el envío?</summary>
        <div class="r">Realizamos envíos nacionales dentro de México, sujetos a disponibilidad del
          producto, confirmación del pedido y cobertura logística. El tiempo estimado es de
          <strong>2 a 5 días hábiles</strong>, con un costo de
          <?php echo esc_html( $pys_moneda( $pys_envio_fijo ? $pys_envio_fijo : 250 ) ); ?> MXN de tarifa fija
          <?php if ( $pys_envio_gratis ) : ?>
            y <strong>envío gratuito en pedidos superiores a <?php echo esc_html( $pys_moneda( $pys_envio_gratis ) ); ?> MXN</strong>
          <?php endif; ?>. La información final se confirma antes de completar la compra.
          <a href="<?php echo esc_url( $pys_url['envios'] ); ?>">Ver la política completa</a>.</div>
      </details>
      <details>
        <summary>¿Qué formas de pago aceptan?</summary>
        <div class="r">Transferencia bancaria directa, tarjeta de crédito o débito, Mercado Pago,
          <strong>pago en efectivo con depósito en OXXO</strong> y criptomonedas (USDT, USDC y
          Binance Pay). Las opciones disponibles se muestran al finalizar la compra.</div>
      </details>
      <details>
        <summary>¿Puedo ver el certificado de análisis de mi lote?</summary>
        <div class="r">Estamos incorporando el certificado de cada lote en la ficha de su producto,
          conforme el laboratorio nos lo entrega, así que todavía no están todos publicados. Si
          necesitas el de un lote en concreto, pídelo por
          <a href="<?php echo esc_url( $pys_url['contacto'] ); ?>">contacto</a> con el número
          impreso en la etiqueta de tu vial. Arriba explicamos
          <a href="#coa">qué trae un COA y cómo se lee</a>.</div>
      </details>
      <details>
        <summary>¿Incluyen la solución para reconstituir?</summary>
        <div class="r">Por cada péptido que compres incluimos <strong>3 ml de solución bacteriostática
          para reconstitución, sin costo adicional</strong>. Disponible por tiempo limitado o hasta
          agotar existencias, y sujeto a disponibilidad.</div>
      </details>
      <details>
        <summary>¿Puedo devolver un producto?</summary>
        <div class="r">Por tratarse de productos sellados y de manejo especializado, las devoluciones
          se revisan caso por caso.
          <ul>
            <li>Plazo para solicitarla: 14 días naturales a partir de la entrega.</li>
            <li>El producto debe conservar su empaque original y sellado.</li>
            <li>No se aceptan devoluciones de productos abiertos, manipulados o usados.</li>
            <li>Los gastos de envío de la devolución corren por cuenta del cliente.</li>
            <li>El reembolso se procesa en un máximo de 7 días hábiles tras recibir el producto.</li>
            <li>No realizamos cambios de producto.</li>
          </ul>
          <a href="<?php echo esc_url( $pys_url['envios'] ); ?>">Ver la política completa</a>.</div>
      </details>
      <details>
        <summary>¿Para qué uso se venden estos productos?</summary>
        <div class="r">Los productos se presentan para <strong>uso de investigación</strong>; así va
          indicado en la etiqueta de cada vial. La información del catálogo busca facilitar una
          navegación clara y responsable, y no sustituye la consulta con un profesional de la
          salud.</div>
      </details>
    </div>
  </div>
</section>

<footer class="pie-h26">
  <div class="wrap">
    <div class="pie">
      <div>
        <span class="marca">
          <img class="logo" src="<?php echo esc_url( pys_h26_uri( 'img/logo-pys.png' ) ); ?>"
               width="75" height="96" alt="" loading="lazy" decoding="async">
          <span class="nom">Péptidos y Suplementos MX</span>
        </span>
        <p>Biohacking · Investigación · Suplementación avanzada</p>
        <p style="margin-top:10px">Información especializada en péptidos, suplementos, biohacking y
          bienestar avanzado. Contenido claro para rendimiento, metabolismo, recuperación y
          longevidad.</p>
      </div>
      <div><h4>Principales</h4><ul>
        <li><a href="<?php echo esc_url( $pys_url['peptidos'] ); ?>">Péptidos</a></li>
        <li><a href="<?php echo esc_url( $pys_url['suplementos'] ); ?>">Suplementos</a></li>
        <li><a href="<?php echo esc_url( $pys_url['productos'] ); ?>">Productos</a></li>
        <li><a href="<?php echo esc_url( $pys_reta_url ); ?>">Retatrutida</a></li>
        <li><a href="<?php echo esc_url( home_url( '/tirzepatida-en-mexico/' ) ); ?>">Tirzepatida</a></li>
        <li><a href="<?php echo esc_url( home_url( '/semaglutida-en-mexico/' ) ); ?>">Semaglutida</a></li>
      </ul></div>
      <div><h4>Explorar</h4><ul>
        <li><a href="<?php echo esc_url( $pys_url['metabolismo'] ); ?>">Metabolismo</a></li>
        <li><a href="<?php echo esc_url( $pys_url['reparacion'] ); ?>">Reparación celular</a></li>
        <li><a href="<?php echo esc_url( $pys_url['longevidad'] ); ?>">Longevidad</a></li>
        <li><a href="<?php echo esc_url( $pys_url['performance'] ); ?>">Performance</a></li>
        <li><a href="<?php echo esc_url( $pys_url['calculadora'] ); ?>">Calculadora de dosis</a></li>
        <li><a href="<?php echo esc_url( $pys_url['blog'] ); ?>">Blog</a></li>
      </ul></div>
      <div><h4>Compra</h4><ul>
        <li><a href="#coa">Certificados de análisis</a></li>
        <li><a href="<?php echo esc_url( $pys_url['envios'] ); ?>">Envíos y devoluciones</a></li>
        <li><a href="<?php echo esc_url( $pys_url['privacidad'] ); ?>">Política de privacidad</a></li>
        <li><a href="<?php echo esc_url( $pys_url['terminos'] ); ?>">Términos y condiciones</a></li>
        <li><a href="<?php echo esc_url( $pys_url['contacto'] ); ?>">Contacto</a></li>
        <li><a href="<?php echo esc_url( $pys_url['carrito'] ); ?>">Carrito</a></li>
        <li><a href="<?php echo esc_url( $pys_url['cuenta'] ); ?>">Mi cuenta</a></li>
        <li><a href="mailto:ventas@peptidosysuplementos.mx">ventas@peptidosysuplementos.mx</a></li>
      </ul></div>
    </div>
    <p class="aviso-inv">Productos presentados para uso de investigación. La información del catálogo
      busca facilitar una navegación clara y responsable.</p>
    <div class="fin">
      <span>© <?php echo esc_html( gmdate( 'Y' ) ); ?> PyS Péptidos y Suplementos. Todos los derechos reservados.</span>
      <span>PEPTIDOSYSUPLEMENTOS.MX</span>
    </div>
  </div>
</footer>

<?php
/* Datos estructurados: solo la lista del catálogo, con nombres y URLs reales.
   Rank Math ya emite Organization/WebSite, así que no se duplican; y no se
   declara FAQPage porque Google retiró ese resultado enriquecido. */
$pys_ld = array(
	'@context'        => 'https://schema.org',
	'@type'           => 'ItemList',
	'name'            => 'Catálogo de péptidos y suplementos',
	'numberOfItems'   => count( $pys_productos ),
	'itemListElement' => array(),
);
foreach ( $pys_productos as $i => $p ) {
	$pys_ld['itemListElement'][] = array(
		'@type'    => 'ListItem',
		'position' => $i + 1,
		'name'     => $p['nombre'],
		'url'      => $p['url'],
	);
}
?>
<script type="application/ld+json"><?php echo wp_json_encode( $pys_ld, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ); ?></script>

<script data-no-optimize="1">
(function(){
  var animate, inView, stagger, scroll;
  /* Decisión del usuario: las animaciones corren siempre, también para quien
     tenga «reducir movimiento» en el sistema. Su equipo lo tiene activado y eso
     le apagaba el halo del cursor, el giro del vial ligado al scroll y todas
     las entradas, así que veía una versión mutilada del diseño. Se deja la
     variable en su sitio —y no se borran los `if`— para poder revertirlo
     cambiando solo esta línea. */
  var quieto = false;
  var suave = [0.22, 0.61, 0.36, 1];
  var $ = function (s) { return document.querySelector(s); };
  var BASE = <?php echo wp_json_encode( pys_h26_uri( 'img/giro' ) ); ?>;

  /* Este bloque va en línea (LiteSpeed no lo toca) mientras que motion.js y
     giro360.js van encolados, así que LiteSpeed los combina y los aplaza: no
     se puede dar por hecho que ya estén cuando esto corre. Lo que no depende
     de la librería se conecta de inmediato; lo demás espera a que aparezca.  */
  function cuandoListo(cb){
    function hay(){ return window.Motion && window.PYS && window.PYS.giro360; }
    if (hay()) return cb();
    var n = 0, t = setInterval(function(){
      if (hay() || ++n > 120){ clearInterval(t); if (hay()) cb(); }
    }, 50);
  }

  /* ── menú de teléfono ───────────────────────────────────────────── */
  var burger = $("#burger"), mnav = $("#mnav");
  function abrirNav(abre){
    mnav.hidden = !abre;
    burger.setAttribute("aria-expanded", abre ? "true" : "false");
    burger.setAttribute("aria-label", abre ? "Cerrar menú" : "Abrir menú");
    if (abre && animate && !quieto)
      animate(mnav.querySelectorAll(".et, a"), { opacity:[0,1], y:[-8,0] },
              { duration:.3, delay: stagger(0.03), ease: suave });
  }
  burger.addEventListener("click", function(){ abrirNav(mnav.hidden); });
  mnav.addEventListener("click", function(e){ if (e.target.closest("a")) abrirNav(false); });

  /* ── buscador ───────────────────────────────────────────────────── */
  var lupa = $("#lupa"), busca = $("#busca");
  lupa.addEventListener("click", function(){
    var abre = busca.hidden;
    busca.hidden = !abre;
    lupa.setAttribute("aria-expanded", abre ? "true" : "false");
    if (abre) busca.querySelector("input[type=search]").focus();
  });

  /* ── «Por objetivo» ─────────────────────────────────────────────── */
  var desp = document.querySelector(".desp");
  if (desp){
    var bot = desp.querySelector("button");
    function abrirDesp(v){
      desp.dataset.abierto = v ? "1" : "0";
      bot.setAttribute("aria-expanded", v ? "true" : "false");
    }
    bot.addEventListener("click", function(){ abrirDesp(desp.dataset.abierto !== "1"); });
    desp.addEventListener("mouseenter", function(){ abrirDesp(true); });
    desp.addEventListener("mouseleave", function(){ abrirDesp(false); });
    desp.addEventListener("focusout", function(e){
      if (!desp.contains(e.relatedTarget)) abrirDesp(false);
    });
    document.addEventListener("click", function(e){
      if (!desp.contains(e.target)) abrirDesp(false);
    });
  }

  addEventListener("keydown", function(e){
    if (e.key !== "Escape") return;
    if (!mnav.hidden){ abrirNav(false); burger.focus(); }
    if (!busca.hidden){ busca.hidden = true; lupa.setAttribute("aria-expanded","false"); lupa.focus(); }
    if (desp) desp.dataset.abierto = "0";
  });

  /* ── el resplandor y el panal siguen al cursor ──────────────────────
     Un solo escuchador alimenta los dos, y la escritura se hace dentro de un
     requestAnimationFrame: antes iba con un temporizador de 60 ms, que para
     una máscara pegada al puntero se nota a saltos. */
  var halo = $("#halo"), hexes = document.querySelector(".hexes");
  if (!quieto && matchMedia("(hover:hover)").matches){
    var cx = 0, cy = 0, encolado = false;
    addEventListener("pointermove", function(e){
      cx = e.clientX; cy = e.clientY;
      if (encolado) return;
      encolado = true;
      requestAnimationFrame(function(){
        encolado = false;
        if (halo){
          halo.style.setProperty("--mx", (cx / innerWidth  * 100).toFixed(1) + "%");
          halo.style.setProperty("--my", (cy / innerHeight * 100).toFixed(1) + "%");
        }
        if (hexes){
          hexes.style.setProperty("--hx", cx + "px");
          hexes.style.setProperty("--hy", cy + "px");
        }
      });
    }, { passive:true });
  }

  /* ── los dos visores de 360° y las notas al desplazar ───────────── */
  cuandoListo(function(){
    var M = window.Motion || {};
    animate = M.animate; inView = M.inView; stagger = M.stagger; scroll = M.scroll;

    /* el visor de 36 cuadros se queda solo en la sección de enfoque: el héroe
       pasó a ser el carrusel, que se monta más abajo y sin librería */
    var ruta = function(i){ return BASE + "/g" + String(i).padStart(2,"0") + ".jpg"; };
    var visorDet = PYS.giro360($("#vitrina2"), { cuadros:36, ruta:ruta, grados:$("#grados2") });
    if (!quieto && scroll)
      scroll(function(p){ visorDet.aProgreso(p); },
             { target: $("#notas"), offset: ["start 80%", "end 60%"] });

    var notas = [].slice.call(document.querySelectorAll(".nota"));
    if (inView) notas.forEach(function(n){
      inView(n, function(){
        notas.forEach(function(o){ o.classList.toggle("viva", o === n); });
        return function(){};
      }, { amount: 0.55 });
    });

    /* El cromatograma ya viene dibujado desde PHP; aquí solo se le hace
       trazarse al entrar en pantalla. Se anima `pathLength` y no
       `strokeDashoffset`: motion no reconoce esa segunda clave y la traza se
       quedaba sin aparecer. Y el dasharray va como ATRIBUTO, porque motion
       escribe ahí y un estilo en línea le ganaría. */
    var graf = document.querySelector(".grafica");
    var traza = document.getElementById("traza");
    var area = document.getElementById("areag");
    if (graf && traza && area && animate && inView){
      traza.setAttribute("pathLength", "1");
      traza.setAttribute("stroke-dasharray", "0 1");
      area.style.opacity = "0";
      inView(graf, function(){
        animate(traza, { pathLength:[0,1] }, { duration:2.2, ease:"easeInOut" });
        animate(area, { opacity:[0,1] }, { duration:.9, delay:1.5 });
      }, { amount:.35 });
    }

    entradas();
  });

  /* ── carrusel del héroe ─────────────────────────────────────────────
     No depende de la librería de animación —todo es CSS— así que se monta
     de inmediato y no espera a nada. */
  var carr = $("#carrusel");
  if (carr){
    var datos   = JSON.parse($("#car-datos").textContent);
    var laminas = [].slice.call(carr.querySelectorAll("img"));
    var puntos  = [].slice.call(document.querySelectorAll("#car-puntos button"));
    var eti = $("#car-eti"), enl = $("#car-link");
    var ahora = 0, reloj = 0;

    function muestra(n){
      var antes = ahora;
      ahora = ((n % laminas.length) + laminas.length) % laminas.length;
      /* El que se va lleva su propia clase para que retroceda en vez de
         devolverse al punto por el que entró; los demás vuelven al reposo.
         Sin esto, el saliente y el entrante se cruzan en la misma dirección
         y el relevo se ve plano. */
      laminas.forEach(function(im, k){
        if (k === ahora) { im.classList.remove("sale"); im.classList.add("on"); }
        else if (k === antes) { im.classList.remove("on"); im.classList.add("sale"); }
        else { im.classList.remove("on", "sale"); }
      });
      puntos.forEach(function(b, k){ b.setAttribute("aria-current", k === ahora ? "true" : "false"); });
      var d = datos[ahora];
      eti.textContent = "RENDER · " + d.n.toUpperCase();
      enl.href = d.u;
      enl.setAttribute("aria-label", "Ver " + d.n);
    }
    function corre(){ clearInterval(reloj); reloj = setInterval(function(){ muestra(ahora + 1); }, 4200); }
    function para(){ clearInterval(reloj); }

    puntos.forEach(function(b){
      b.addEventListener("click", function(){ muestra(+b.dataset.i); corre(); });
    });
    carr.addEventListener("pointerenter", para);
    carr.addEventListener("pointerleave", corre);
    /* en una pestaña de fondo no tiene sentido seguir consumiendo */
    document.addEventListener("visibilitychange", function(){
      if (document.hidden) { para(); } else { corre(); }
    });

    /* el vial se recuesta hacia donde está el cursor */
    if (matchMedia("(hover:hover)").matches){
      carr.addEventListener("pointermove", function(e){
        var r = carr.getBoundingClientRect();
        carr.style.setProperty("--px", ((e.clientX - r.left) / r.width  - .5).toFixed(3));
        carr.style.setProperty("--py", ((e.clientY - r.top)  / r.height - .5).toFixed(3));
      }, { passive:true });
      carr.addEventListener("pointerleave", function(){
        carr.style.setProperty("--px", "0");
        carr.style.setProperty("--py", "0");
      });
    }
    /* Las láminas 2ª en adelante van en `lazy`, así que podrían llegar sin
       descodificar justo cuando les toca entrar y aparecer de golpe a mitad del
       fundido. Se fuerza su descodificación en segundo plano en cuanto el
       carrusel arranca, sin bloquear nada. */
    laminas.forEach(function(im){
      if (im.decode) { im.decode().catch(function(){}); }
    });

    if (laminas.length > 1) corre();
  }

  /* ── filtro del catálogo ────────────────────────────────────────────
     Las tarjetas se pintan en PHP para que existan en el HTML aunque el
     JS no corra; aquí solo se ocultan las que no tocan. */
  var rejilla = $("#rejilla"), filtros = $("#filtros"), cuenta = $("#cuenta");
  var tarjetas = [].slice.call(rejilla.querySelectorAll(".tarjeta"));

  function aplicaFiltro(slug){
    var n = 0;
    filtros.querySelectorAll(".filtro").forEach(function(b){
      b.setAttribute("aria-pressed", b.dataset.f === slug ? "true" : "false");
    });
    tarjetas.forEach(function(t){
      var toca = slug === "todo" || (" " + t.dataset.cats + " ").indexOf(" " + slug + " ") > -1;
      t.hidden = !toca;
      if (toca) n++;
    });
    cuenta.textContent = n + (n === 1 ? " REFERENCIA" : " REFERENCIAS");
    if (animate && !quieto)
      animate(tarjetas.filter(function(t){ return !t.hidden; }), { opacity:[0,1], y:[12,0] },
              { duration:.38, delay: stagger(0.022), ease: suave });
  }
  filtros.addEventListener("click", function(e){
    var b = e.target.closest(".filtro");
    if (b) aplicaFiltro(b.dataset.f);
  });

  /* ── entradas ───────────────────────────────────────────────────── */
  function entradas(){
    if (!animate || quieto) return;
    animate("[data-rev]", { opacity:[0,1], y:[20,0] },
            { duration:.8, delay: stagger(0.08, { startDelay:.1 }), ease: suave });
    animate("#carrusel", { opacity:[0,1], scale:[.965,1] }, { duration:1, delay:.25, ease: suave });
    animate(".banda div", { opacity:[0,1] }, { duration:.6, delay: stagger(0.05, { startDelay:.5 }) });
    if (inView){
      [".cat", ".guia", ".pasos li", ".tarjeta"].forEach(function(sel){
        var els = document.querySelectorAll(sel);
        if (!els.length) return;
        els.forEach(function(e){ e.style.opacity = "0"; });
        inView(els[0].parentElement, function(){
          animate(els, { opacity:[0,1], y:[14,0] },
                  { duration:.5, delay: stagger(0.04), ease: suave });
        }, { amount:.08 });
      });
    }
  }
})();
</script>

<?php wp_footer(); ?>
</body>
</html>
