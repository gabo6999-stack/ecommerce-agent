<?php
/**
 * Catálogo: archivo de la tienda y archivos de categoría.
 *
 * Solo diseño. El contenido —qué productos salen, en qué orden, con qué precio
 * y existencia— lo sigue decidiendo WooCommerce; aquí se reordena el marcado de
 * la tarjeta y se le pone el lenguaje visual de la portada.
 *
 * La tarjeta NO se redefine: al <li> de WooCommerce se le añade la clase
 * `tarjeta` y hereda la misma hoja que usa la retícula de la portada.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * ¿Hay un bucle de productos en esta vista?
 *
 * Incluye la ficha de producto a propósito: ahí abajo viven los relacionados,
 * que usan el mismo marcado `ul.products > li.product`. Si no se contara, los
 * relacionados se quedarían con el estilo viejo justo debajo de una ficha ya
 * rediseñada.
 */
function pys_dis_es_catalogo() {
	if ( ! function_exists( 'is_shop' ) ) {
		return false;
	}
	return is_shop() || is_product_taxonomy() || is_product();
}

/**
 * El <li> de WooCommerce pasa a ser una tarjeta del sistema.
 *
 * El mismo filtro pinta la clase del <div> principal de la ficha, así que ahí
 * se salta el producto que se está viendo: con `tarjeta` la ficha entera se
 * volvía una tarjeta —borde, halo al pasar el ratón, `.tarjeta h3` encogiendo
 * los ladillos de la descripción— y su `overflow:hidden` recortaba el texto en
 * el teléfono y anulaba el `position:sticky` de la galería.
 */
add_filter(
	'woocommerce_post_class',
	function ( $clases, $producto = null ) {
		if ( ! pys_dis_es_catalogo() ) {
			return $clases;
		}
		if ( is_product() && $producto && (int) $producto->get_id() === (int) get_queried_object_id() ) {
			return $clases;
		}
		$clases[] = 'tarjeta';
		return $clases;
	},
	10,
	2
);

/**
 * Imagen de la tarjeta.
 *
 * Se sustituye la de WooCommerce por dos motivos: el tamaño `woocommerce_thumbnail`
 * de esta tienda es de 150×150 CON recorte cuadrado —a un bote alto le corta una
 * tira del centro y la estira—, y además los péptidos tienen render de vial, que
 * es lo que se enseña en la portada. Un producto no puede salir con vial en un
 * sitio y con su tarjeta tipográfica en otro.
 */
function pys_dis_loop_foto() {
	global $product;
	if ( ! $product ) {
		return;
	}
	$id    = $product->get_id();
	$vial  = pys_dis_vial( $id );
	$corta = pys_dis_cat_corta( $id );

	echo '<div class="foto' . ( $vial ? ' vial' : '' ) . '">';
	if ( $corta ) {
		echo '<span class="eti">' . esc_html( $corta ) . '</span>';
	}
	if ( $vial ) {
		printf(
			'<img src="%s" width="540" height="1043" loading="lazy" decoding="async" alt="%s">',
			esc_url( pys_dis_uri( 'img/' . $vial ) ),
			esc_attr( 'Vial de ' . $product->get_name() )
		);
	} elseif ( $product->get_image_id() ) {
		echo wp_kses_post( $product->get_image( 'large', array( 'loading' => 'lazy' ) ) );
	} else {
		echo '<span class="sinfoto">SIN IMAGEN</span>';
	}
	if ( ! $product->is_in_stock() ) {
		echo '<span class="agotado"><span>Agotado</span></span>';
	}
	echo '</div>';
}

/** SKU bajo el nombre, como en la portada. */
function pys_dis_loop_sku() {
	global $product;
	if ( $product && $product->get_sku() ) {
		echo '<div class="sku">SKU ' . esc_html( $product->get_sku() ) . '</div>';
	}
}

/** Franja de categoría y existencia. */
function pys_dis_loop_specs() {
	global $product;
	if ( ! $product ) {
		return;
	}
	$corta = pys_dis_cat_corta( $product->get_id() );
	echo '<div class="specs"><span>' . esc_html( $corta ? $corta : 'Catálogo' ) . '</span>'
		. '<span>·</span><span>' . ( $product->is_in_stock() ? 'en existencia' : 'sin existencia' )
		. '</span></div>';
}

/**
 * Reordena el marcado del bucle.
 *
 * WooCommerce mete el precio DENTRO del enlace del producto y deja el botón
 * fuera, así que no se pueden poner uno al lado del otro solo con CSS. Se saca
 * el precio del enlace y se envuelven los dos en la misma fila `.compra`, que
 * es la que ya estiliza la tarjeta compartida.
 *
 * Orden en `woocommerce_after_shop_loop_item`: 5 cierra el enlace, 6 abre la
 * fila, 7 el precio, 10 el botón, 11 cierra.
 */
add_action(
	'wp',
	function () {
		if ( ! pys_dis_es_catalogo() ) {
			return;
		}
		remove_action( 'woocommerce_before_shop_loop_item_title', 'woocommerce_template_loop_product_thumbnail', 10 );
		add_action( 'woocommerce_before_shop_loop_item_title', 'pys_dis_loop_foto', 10 );

		add_action( 'woocommerce_shop_loop_item_title', 'pys_dis_loop_sku', 11 );

		remove_action( 'woocommerce_after_shop_loop_item_title', 'woocommerce_template_loop_price', 10 );
		add_action( 'woocommerce_after_shop_loop_item_title', 'pys_dis_loop_specs', 11 );

		add_action( 'woocommerce_after_shop_loop_item', function () { echo '<div class="compra">'; }, 6 );
		add_action( 'woocommerce_after_shop_loop_item', 'woocommerce_template_loop_price', 7 );
		add_action( 'woocommerce_after_shop_loop_item', function () { echo '</div>'; }, 11 );
	}
);

/** Hoja del archivo. La tarjeta ya viene de las piezas compartidas. */
function pys_dis_css_catalogo() {
	return '
/* ── archivo de la tienda ──────────────────────────────────────────── */
.pys-h26 .site-main{width:min(1320px,100%);margin-inline:auto;
  padding-inline:var(--gutter);padding-block:clamp(26px,4vw,52px)}
.pys-h26 .woocommerce-breadcrumb{font-family:var(--mono);font-size:11px;letter-spacing:.07em;
  color:var(--tinta-3);margin-bottom:clamp(18px,2.5vw,30px)}
.pys-h26 .woocommerce-breadcrumb a{color:var(--tinta-3)}
.pys-h26 .woocommerce-breadcrumb a:hover{color:var(--magenta)}
.pys-h26 .woocommerce-products-header{margin-bottom:clamp(20px,3vw,34px)}
.pys-h26 .woocommerce-products-header__title{font-size:clamp(30px,4vw,54px);line-height:1.05;
  letter-spacing:-.012em;font-weight:400;margin:0 0 14px;max-width:20ch}
.pys-h26 .term-description,.pys-h26 .woocommerce-product-details__short-description,
.pys-h26 .page-description{color:var(--tinta-2);font-size:16.5px;max-width:62ch}
.pys-h26 .term-description p{margin:0 0 10px}

/* barra de resultados y orden */
.pys-h26 .woocommerce-result-count{font-family:var(--mono);font-size:11px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--tinta-3);margin:0;float:none;text-align:left}
.pys-h26 .woocommerce-ordering{margin:0;float:none}
.pys-h26 .woocommerce-ordering select{appearance:none;-webkit-appearance:none;
  background:var(--carbon) url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'12\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23718C84\' stroke-width=\'2.4\'%3E%3Cpath d=\'M5 9l7 7 7-7\'/%3E%3C/svg%3E") no-repeat right 14px center;
  border:1px solid var(--linea-2);border-radius:2px;color:var(--tinta);
  font-family:var(--mono);font-size:11.5px;letter-spacing:.05em;padding:10px 38px 10px 14px;
  cursor:pointer}
.pys-h26 .woocommerce-ordering select:hover{border-color:var(--tinta-3)}
.pys-h26 .pys-barra{display:flex;align-items:center;justify-content:space-between;gap:16px;
  flex-wrap:wrap;padding-bottom:18px;margin-bottom:clamp(18px,2.4vw,26px);
  border-bottom:1px solid var(--linea)}

/* retícula: la misma que la portada */
.pys-h26 ul.products{display:grid;grid-template-columns:repeat(4,1fr);
  gap:clamp(12px,1.4vw,20px);list-style:none;margin:0;padding:0}
.pys-h26 ul.products::before,.pys-h26 ul.products::after{display:none}
.pys-h26 ul.products li.product{width:auto;margin:0;float:none;text-align:left;padding:0}
/* el enlace envuelve foto, nombre, SKU y specs: tiene que comportarse como
   la columna de la tarjeta, no como un enlace suelto */
.pys-h26 li.product .woocommerce-loop-product__link{display:flex;flex-direction:column;
  height:100%;color:inherit;text-decoration:none}
.pys-h26 li.product .woocommerce-loop-product__title{font-size:17.5px;line-height:1.22;
  font-weight:400;overflow-wrap:anywhere;padding:15px 16px 0;margin:0}
.pys-h26 li.product .sku{padding-inline:16px}
.pys-h26 li.product .specs{margin-top:auto}
.pys-h26 li.product .onsale{position:absolute;top:10px;right:10px;z-index:2;
  font-family:var(--mono);font-size:9px;letter-spacing:.09em;padding:3px 7px;border-radius:2px;
  background:var(--magenta);color:#fff;min-height:0;min-width:0;line-height:1.6}
/* el botón de WooCommerce adopta el aspecto del de la portada */
.pys-h26 li.product .compra .button{font-family:var(--mono);font-size:11px;letter-spacing:.06em;
  padding:9px 13px;border:1px solid var(--magenta);background:transparent;color:var(--magenta);
  border-radius:2px;cursor:pointer;transition:background .18s,color .18s;white-space:nowrap;
  line-height:1.4;margin:0;font-weight:400}
.pys-h26 li.product .compra .button:hover{background:var(--magenta);color:#fff}
.pys-h26 li.product .compra .button.loading{opacity:.6;pointer-events:none}
.pys-h26 li.product .compra .button.added{background:var(--aqua);border-color:var(--aqua);
  color:var(--negro)}
.pys-h26 li.product .compra .added_to_cart{display:none}
.pys-h26 li.product.outofstock .compra .button{border-color:var(--linea-2);color:var(--tinta-3)}
.pys-h26 li.product.outofstock .compra .button:hover{background:transparent;color:var(--tinta-3)}
@media (max-width:1040px){ .pys-h26 ul.products{grid-template-columns:repeat(3,1fr)} }
@media (max-width:780px){ .pys-h26 ul.products{grid-template-columns:repeat(2,1fr)} }
@media (max-width:440px){
  .pys-h26 li.product .woocommerce-loop-product__title{font-size:15.5px;padding:12px 12px 0}
  .pys-h26 li.product .sku{padding-inline:12px}
}
@media (max-width:340px){ .pys-h26 ul.products{grid-template-columns:1fr} }

/* paginación */
.pys-h26 .woocommerce-pagination{margin-top:clamp(28px,4vw,48px)}
.pys-h26 .woocommerce-pagination ul{display:flex;gap:7px;list-style:none;margin:0;padding:0;
  border:0;justify-content:center;flex-wrap:wrap}
.pys-h26 .woocommerce-pagination li{border:0;margin:0}
.pys-h26 .woocommerce-pagination a,.pys-h26 .woocommerce-pagination span{display:grid;
  place-items:center;min-width:40px;height:40px;padding:0 12px;border-radius:2px;
  border:1px solid var(--linea-2);font-family:var(--mono);font-size:12px;color:var(--tinta-2);
  background:transparent;transition:border-color .2s,color .2s}
.pys-h26 .woocommerce-pagination a:hover{border-color:var(--tinta-3);color:var(--tinta)}
.pys-h26 .woocommerce-pagination .current{background:var(--tinta);border-color:var(--tinta);
  color:var(--negro)}

/* ── reconquista de la tarjeta ───────────────────────────────────────
   El sitio ya traía su propio estilo para las tarjetas de WooCommerce —marco
   redondeado con halo, precio en caja y botón de píldora con degradado— y esas
   reglas le ganan a las de arriba. No se pueden localizar buscando por valor,
   porque están escritas con variables CSS y el valor solo existe ya calculado.
   En lugar de perseguirlas una a una, aquí se gana por especificidad con
   `html body[class][class][class]`. La regla rival es
   `body.post-type-archive-product ul.products li.product .woocommerce-loop-product__title`
   —(0,4,3) y con !important—, que EMPATA con dos [class] y gana por ir después en
   el documento; con el tercero se decide por especificidad y no por orden, que
   es lo único estable aquí. El !important puntual es para las que sí lo llevan. */
html body[class][class][class] ul.products li.product{border:1px solid var(--linea);
  border-radius:3px;background:var(--carbon);box-shadow:none;overflow:hidden;
  padding:0!important}
/* El tema le pone `padding:22px` al elemento li y alto fijo a la imagen del bucle: la
   foto quedaba embutida dentro de la tarjeta y el vial, de 187×250 en una caja
   de 187×187, se comía 63 px por abajo con el `overflow:hidden`. Se le devuelve
   el control del tamaño a la caja. */
html body[class][class][class] li.product .foto img{width:100%!important;
  height:100%!important;max-width:100%!important;object-fit:contain!important;
  display:block;margin:0}
html body[class][class][class] li.product .foto.vial img{width:auto!important;
  height:100%!important;margin-inline:auto!important}
html body[class][class][class] li.product .foto .eti{white-space:nowrap}
html body[class][class][class] ul.products li.product:hover{border-color:var(--linea-2);
  box-shadow:0 22px 50px -26px rgba(0,0,0,.95), 0 0 60px -26px rgba(2,246,200,.3)}
html body[class][class][class] li.product .woocommerce-loop-product__title{
  font-family:var(--optima)!important;font-size:17.5px!important;font-weight:400!important;
  text-transform:none!important;letter-spacing:-.012em;color:var(--tinta)!important;
  background:none;border:0;line-height:1.22}
html body[class][class][class] li.product .compra{display:flex;align-items:center;
  justify-content:space-between;gap:10px;padding:13px 16px;border-top:1px solid var(--linea);
  background:var(--carbon-2);flex-wrap:wrap;margin:0}
html body[class][class][class] li.product .compra .price{font-family:var(--mono)!important;
  font-size:16px!important;font-weight:400!important;font-variant-numeric:tabular-nums;
  color:var(--tinta)!important;background:none!important;border:0!important;
  padding:0!important;margin:0;display:inline;box-shadow:none;line-height:1.4}
/* El importe vive en un span.woocommerce-Price-amount con un bdi dentro,… con regla
   propia, así que estilar solo el `.price` de fuera no le llega: hay que bajar
   hasta el hijo o el número sigue saliendo turquesa y enorme. */
html body[class][class][class] li.product .compra .price .woocommerce-Price-amount,
html body[class][class][class] li.product .compra .price bdi,
html body[class][class][class] li.product .compra .price span{
  color:var(--tinta)!important;font-family:var(--mono)!important;font-size:16px!important;
  font-weight:400!important;background:none!important;border:0!important;padding:0!important;
  margin:0!important;box-shadow:none!important;line-height:1.4!important}
html body[class][class][class] li.product .compra .price .woocommerce-Price-currencySymbol{
  font-size:11px!important;vertical-align:top}
html body[class][class][class] li.product .compra .price del{color:var(--tinta-3);font-size:12.5px}
html body[class][class][class] li.product .compra .price ins{text-decoration:none;background:none}
html body[class][class][class] li.product .compra .button{background:transparent!important;
  background-image:none!important;border:1px solid var(--magenta)!important;
  border-radius:2px!important;color:var(--magenta)!important;
  font-family:var(--mono)!important;font-size:11px!important;font-weight:400;
  letter-spacing:.06em;padding:9px 13px!important;box-shadow:none!important;
  min-width:0;width:auto;text-transform:none;height:auto!important;
  min-height:0!important;line-height:1.4!important;
  /* el botón del tema pinta su texto con un degradado recortado
     (`background-clip:text` + `-webkit-text-fill-color:transparent`): al
     quitarle el degradado la etiqueta se quedaba invisible */
  -webkit-text-fill-color:currentColor!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important}
html body[class][class][class] li.product .compra .button:hover{background:var(--magenta)!important;
  color:#fff!important}
html body[class][class][class] li.product .compra .button.added{background:var(--aqua)!important;
  border-color:var(--aqua)!important;color:var(--negro)!important}
html body[class][class][class] li.product.outofstock .compra .button{
  border-color:var(--linea-2)!important;color:var(--tinta-3)!important}
html body[class][class][class] li.product.outofstock .compra .button:hover{
  background:transparent!important;color:var(--tinta-3)!important}

' . pys_dis_css_catalogo_auditoria();
}

/**
 * Segunda reconquista (auditoría del 21-sep).
 *
 * Las reglas de arriba con `.pys-h26 …` pierden contra el «CSS adicional» del
 * Customizer (`body.post-type-archive-product ul.products li.product …`, con
 * !important en fondos, rellenos y márgenes) y, en las fichas, contra el CSS
 * propio de cada documento de Elementor (`body.elementor-page-N .product
 * {background:…!important}`, que también casa con cada <li class="product">
 * de los relacionados). Lo que se veía:
 *
 *  - la imagen del bucle con `padding:18px`, radio de 24 px, sombra y dos
 *    halos de color de fondo: el vial salía metido en una caja blanca con brillo
 *    rosa, y si la foto tardaba en pintarse solo se veía el halo difuminado;
 *  - la etiqueta de categoría tapada por esa misma imagen («Metaboli…»);
 *  - el nombre pegado al borde (`padding:0!important`) y un hueco de 48 px
 *    (`min-height`) hasta el SKU;
 *  - el fondo de la tarjeta con degradado y una raya de neón abajo (`::after`);
 *  - el botón con `margin-top:18px!important`, que partía la fila de compra en
 *    unas tarjetas sí y en otras no: precios a alturas distintas en la misma fila;
 *  - el desplegable de orden como píldora (999 px), la paginación en círculos
 *    con la página actual en degradado, el titular a 83 px con letras encimadas
 *    (-0.065em), y la miga de pan y el recuento con la letra del tema;
 *  - el contenedor a 1140 px en vez de los 1320 de la cabecera, y dos halos de
 *    color pintados en su fondo;
 *  - en el teléfono, una sola columna forzada con !important.
 *
 * Todo gana por especificidad con `html body[class][class][class]`.
 */
function pys_dis_css_catalogo_auditoria() {
	return <<<'CSS'
/* contenedor: el mismo ancho que la cabecera. El Customizer le pone además
   `padding:22px!important` (y 42-78 px arriba) al .content-area que lo envuelve:
   en el teléfono eso restaba 44 px a la retícula y las tarjetas no cabían. */
html body[class][class][class] .content-area{padding:0!important;margin:0!important;
  background:none!important;background-image:none!important}
html body[class][class][class] .site-main{width:min(1320px,100%)!important;max-width:none!important;
  margin-inline:auto!important;padding:clamp(26px,4vw,52px) var(--gutter)!important;
  background:none!important;background-image:none!important}
html body[class][class][class] .woocommerce-breadcrumb,
html body[class][class][class] .woocommerce-breadcrumb a{font-family:var(--mono)!important;
  font-size:11px!important;letter-spacing:.07em;color:var(--tinta-3)!important;
  text-decoration:none!important;line-height:1.7}
html body[class][class][class] .woocommerce-breadcrumb a:hover{color:var(--magenta)!important}
html body[class][class][class] .woocommerce-products-header__title{font-family:var(--optima)!important;
  font-size:clamp(30px,4vw,54px)!important;line-height:1.05!important;letter-spacing:-.012em!important;
  font-weight:400!important;color:var(--tinta)!important;margin:0 0 14px!important;max-width:24ch}

/* barra de recuento y orden */
html body[class][class][class] .woocommerce-result-count{font-family:var(--mono)!important;
  font-size:11px!important;letter-spacing:.09em;text-transform:uppercase;color:var(--tinta-3)!important;
  margin:0!important;float:none!important;width:auto!important;text-align:left!important}
html body[class][class][class] .woocommerce-ordering{margin:0!important;float:none!important}
html body[class][class][class] .woocommerce-ordering select{appearance:none;-webkit-appearance:none;
  background:var(--carbon) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23718C84' stroke-width='2.4'%3E%3Cpath d='M5 9l7 7 7-7'/%3E%3C/svg%3E") no-repeat right 14px center!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;box-shadow:none!important;
  color:var(--tinta)!important;font-family:var(--mono)!important;font-size:11.5px!important;
  letter-spacing:.05em;padding:10px 38px 10px 14px!important;min-height:0!important;height:auto!important;
  width:auto!important;max-width:100%;margin:0!important;cursor:pointer;line-height:1.4}
html body[class][class][class] .woocommerce-ordering select:hover{border-color:var(--tinta-3)!important}
html body[class][class][class] .woocommerce-ordering select option{color:#111;background:#fff}

/* retícula: la de la portada, también en el teléfono (dos columnas) */
html body[class][class][class] ul.products{display:grid!important;
  grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:clamp(12px,1.4vw,20px)!important;
  margin:0!important;padding:0!important;list-style:none}
@media (max-width:1040px){ html body[class][class][class] ul.products{
  grid-template-columns:repeat(3,minmax(0,1fr))!important} }
@media (max-width:780px){ html body[class][class][class] ul.products{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:12px!important} }
@media (max-width:340px){ html body[class][class][class] ul.products{
  grid-template-columns:minmax(0,1fr)!important} }

/* la tarjeta */
html body[class][class][class] ul.products li.product{display:flex!important;flex-direction:column;
  width:auto!important;float:none!important;clear:none!important;margin:0!important;padding:0!important;
  border:1px solid var(--linea)!important;border-radius:3px!important;background:var(--carbon)!important;
  box-shadow:none!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;
  transform:none!important;overflow:hidden;text-align:left;min-width:0}
html body[class][class][class] ul.products li.product::before,
html body[class][class][class] ul.products li.product::after{content:none!important;display:none!important}
html body[class][class][class] ul.products li.product:hover{border-color:var(--linea-2)!important;
  transform:none!important;
  box-shadow:0 22px 50px -26px rgba(0,0,0,.95),0 0 60px -26px rgba(2,246,200,.3)!important}
/* el enlace envuelve foto, nombre, SKU y franja: es la columna que crece, así
   la franja y la fila de compra quedan a la misma altura en toda la fila */
html body[class][class][class] ul.products li.product a.woocommerce-loop-product__link{
  display:flex!important;flex-direction:column;flex:1 1 auto;height:auto!important;
  color:inherit!important;text-decoration:none!important}
html body[class][class][class] ul.products li.product a.woocommerce-loop-product__link::after{
  content:"";order:3;flex:1 0 13px}
html body[class][class][class] ul.products li.product .foto{position:relative;aspect-ratio:1/1;
  overflow:hidden;margin:0!important;padding:0!important;border-radius:0!important;flex:none}
html body[class][class][class] ul.products li.product .foto img{width:100%!important;height:100%!important;
  max-width:100%!important;max-height:none!important;object-fit:contain!important;display:block;
  padding:0!important;margin:0!important;border:0!important;border-radius:0!important;
  background:none!important;box-shadow:none!important;filter:none!important}
html body[class][class][class] ul.products li.product .foto.vial img{width:auto!important;
  margin-inline:auto!important}
html body[class][class][class] ul.products li.product .foto .eti{z-index:2;white-space:nowrap}
html body[class][class][class] ul.products li.product .foto .agotado{z-index:1}
html body[class][class][class] ul.products li.product .woocommerce-loop-product__title{order:1;
  font-family:var(--optima)!important;font-size:17.5px!important;font-weight:400!important;
  line-height:1.22!important;letter-spacing:-.012em!important;color:var(--tinta)!important;
  text-transform:none!important;padding:15px 16px 0!important;margin:0!important;min-height:0!important;
  background:none!important;border:0!important;overflow-wrap:anywhere;transition:color .2s}
html body[class][class][class] ul.products li.product a.woocommerce-loop-product__link:hover
  .woocommerce-loop-product__title{color:var(--magenta)!important}
html body[class][class][class] ul.products li.product .sku{order:2;font-family:var(--mono)!important;
  font-size:10.5px!important;letter-spacing:.06em;color:var(--tinta-3)!important;
  margin:7px 0 0!important;padding:0 16px!important}
html body[class][class][class] ul.products li.product .specs{order:4;margin:0!important;
  padding:11px 16px!important;border-top:1px solid var(--linea)!important;font-family:var(--mono)!important;
  font-size:10.5px!important;color:var(--tinta-3)!important;display:flex;gap:7px;flex-wrap:wrap}
/* fila de compra: precio arriba y botón debajo en TODAS las tarjetas. Los
   rótulos de WooCommerce («Añadir al carrito», «Seleccionar opciones») no caben
   junto al precio en una tarjeta de 290 px; en una fila partían y en otra no. */
html body[class][class][class] ul.products li.product .compra{display:flex!important;
  flex-direction:column;align-items:flex-start;justify-content:flex-start;gap:10px;
  padding:13px 16px 15px!important;margin:0!important;border-top:1px solid var(--linea)!important;
  background:var(--carbon-2)!important;flex:none}
/* la hoja de Elementor de las fichas centra el precio en el teléfono */
html body[class][class][class] ul.products li.product .compra .price{text-align:left!important}
html body[class][class][class] ul.products li.product .compra .button{display:inline-flex!important;
  align-items:center;justify-content:center;margin:0!important;width:auto!important;max-width:100%;
  white-space:normal;text-align:center;transform:none!important;filter:none!important}
/* oferta */
html body[class][class][class] ul.products li.product .onsale{position:absolute!important;top:10px!important;
  right:10px!important;left:auto!important;z-index:3;margin:0!important;min-height:0!important;
  min-width:0!important;padding:3px 7px!important;border-radius:2px!important;border:0!important;
  background:var(--magenta)!important;color:#fff!important;font-family:var(--mono)!important;
  font-size:9px!important;font-weight:400!important;letter-spacing:.09em;line-height:1.6!important;
  box-shadow:none!important}
@media (max-width:440px){
  html body[class][class][class] ul.products li.product .woocommerce-loop-product__title{
    font-size:15.5px!important;padding:12px 12px 0!important}
  html body[class][class][class] ul.products li.product .sku{font-size:9.5px!important;padding:0 12px!important}
  /* como en la portada (`.tarjeta .specs` de la base): en dos columnas de
     teléfono la franja no cabe en una línea; la categoría ya va en la etiqueta
     de la foto y el agotado en su velo */
  html body[class][class][class] ul.products li.product .specs{display:none!important}
  html body[class][class][class] ul.products li.product .compra{padding:11px 12px 12px!important;gap:8px;
    align-items:stretch}
  html body[class][class][class] ul.products li.product .compra .price,
  html body[class][class][class] ul.products li.product .compra .price .woocommerce-Price-amount,
  html body[class][class][class] ul.products li.product .compra .price bdi,
  html body[class][class][class] ul.products li.product .compra .price span{font-size:14.5px!important}
  html body[class][class][class] ul.products li.product .compra .button{width:100%!important;
    font-size:10px!important;padding:9px 6px!important;letter-spacing:.02em!important}
  html body[class][class][class] ul.products li.product .foto .eti{font-size:8px;padding:2px 5px;top:8px;left:8px}
}

/* paginación */
html body[class][class][class] .woocommerce-pagination{margin-top:clamp(28px,4vw,48px)}
html body[class][class][class] .woocommerce-pagination ul{display:flex!important;gap:7px;border:0!important;
  justify-content:center;flex-wrap:wrap;margin:0!important;padding:0!important;list-style:none}
html body[class][class][class] .woocommerce-pagination ul li{border:0!important;margin:0!important;
  float:none!important;overflow:visible!important;background:none!important}
html body[class][class][class] .woocommerce-pagination ul li a,
html body[class][class][class] .woocommerce-pagination ul li span{display:grid!important;place-items:center;
  min-width:40px;height:40px;padding:0 12px!important;border-radius:2px!important;
  border:1px solid var(--linea-2)!important;background:transparent!important;background-image:none!important;
  color:var(--tinta-2)!important;font-family:var(--mono)!important;font-size:12px!important;line-height:1!important;
  box-shadow:none!important;transition:border-color .2s,color .2s}
html body[class][class][class] .woocommerce-pagination ul li a:hover{border-color:var(--tinta-3)!important;
  color:var(--tinta)!important}
html body[class][class][class] .woocommerce-pagination ul li span.current{background:var(--tinta)!important;
  border-color:var(--tinta)!important;color:var(--negro)!important}

/* avisos (p. ej. «añadido al carrito»): el Customizer los redondea a 22 px */
html body[class][class][class] .woocommerce-message,
html body[class][class][class] .woocommerce-info,
html body[class][class][class] .woocommerce-error{background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-top:2px solid var(--aqua)!important;border-radius:3px!important;
  box-shadow:none!important;color:var(--tinta-2)!important}
html body[class][class][class] .woocommerce-error{border-top-color:var(--magenta)!important}
CSS;
}

/**
 * La cuenta de resultados y el desplegable de orden se agrupan en una fila. En
 * el marcado de WooCommerce van sueltos y flotados, que aquí no encaja.
 */
add_action(
	'woocommerce_before_shop_loop',
	function () {
		if ( pys_dis_es_catalogo() ) {
			echo '<div class="pys-barra">';
		}
	},
	19
);
add_action(
	'woocommerce_before_shop_loop',
	function () {
		if ( pys_dis_es_catalogo() ) {
			echo '</div>';
		}
	},
	31
);
