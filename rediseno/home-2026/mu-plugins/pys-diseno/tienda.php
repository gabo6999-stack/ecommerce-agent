<?php
/**
 * Carrito y finalizar compra.
 *
 * SOLO CSS. Son las dos páginas donde se cierra la venta, así que aquí no se
 * mueve ni un nodo del marcado de WooCommerce: ni los campos, ni su orden, ni
 * los que añade el editor de campos del checkout, ni las pasarelas. Lo único
 * que no es CSS es la miniatura del carrito, que pasa a ser el render de vial
 * igual que en el catálogo — una sustitución de imagen por filtro, sin tocar
 * la estructura.
 *
 * El interior de las pasarelas (Mercado Pago, PayPal, CoinGate, Zeno) NO se
 * estiliza: pintan sus propios formularios y a veces iframes, y forzarles
 * estilos es la forma más fácil de romper un pago.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** ¿Carrito o finalizar compra? */
function pys_dis_es_tienda() {
	return function_exists( 'is_cart' ) && ( is_cart() || is_checkout() );
}

/**
 * Miniatura del carrito. WooCommerce la pinta con su tamaño de 150×150
 * recortado y el tema la encoge a un círculo de 32 px: se veía como un punto
 * blanco. Se usa el render de vial cuando existe, como en el catálogo.
 */
add_filter(
	'woocommerce_cart_item_thumbnail',
	function ( $html, $item ) {
		$id   = isset( $item['product_id'] ) ? (int) $item['product_id'] : 0;
		$vial = $id ? pys_dis_vial( $id ) : '';
		if ( ! $vial ) {
			return $html;
		}
		return sprintf(
			'<img class="pys-mini-vial" src="%s" width="540" height="1043" alt="%s" loading="lazy" decoding="async">',
			esc_url( pys_dis_uri( 'img/' . $vial ) ),
			esc_attr( 'Vial de ' . get_the_title( $id ) )
		);
	},
	10,
	2
);

/** Hoja de carrito y finalizar compra. */
function pys_dis_css_tienda() {
	$p = 'html body[class][class][class]';
	/* `.woocommerce-cart` y `.woocommerce-checkout` son clases del BODY, no de un
	   contenedor: escritas como descendiente (`… .woocommerce-cart .coupon`) no
	   casaban con nada, y el cupón y el título se quedaban con el estilo viejo. */
	$c = 'html body.woocommerce-cart[class][class]';
	$k = 'html body.woocommerce-checkout[class][class]';
	return '
/* ── base común ────────────────────────────────────────────────────── */
.pys-h26.woocommerce-cart .site-main,.pys-h26.woocommerce-checkout .site-main{
  width:min(1200px,100%);margin-inline:auto;padding-inline:var(--gutter);
  padding-block:clamp(26px,4vw,52px)}
' . $c . ' h1.entry-title,' . $k . ' h1.entry-title,
' . $p . ' .page-header .entry-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(32px,4vw,52px)!important;letter-spacing:-.012em!important;line-height:1.05!important;
  text-shadow:none!important;color:var(--tinta)!important;
  margin:0 0 clamp(18px,2.6vw,30px)!important;text-transform:none!important}

/* La hoja propia de la página del carrito (Elementor, post 28) pinta un panel
   «grafito» con resplandores turquesa y magenta detrás de todo, y redondea a
   28 px los avisos. Se apaga: el fondo es el del sitio. */
' . $c . ' .elementor,' . $c . ' .elementor-section,' . $c . ' .elementor-container,
' . $c . ' .elementor-widget-wrap,' . $c . ' #page,' . $c . ' .site{background:none!important;
  background-image:none!important}

/* avisos (carrito vacío, «carrito actualizado», el del cupón): los de la base,
   con sitio para el icono de WooCommerce, que iba encima de la primera letra */
' . $c . ' .woocommerce-info,' . $c . ' .woocommerce-message,' . $c . ' .woocommerce-error,
' . $k . ' .woocommerce-info,' . $k . ' .woocommerce-message,' . $k . ' .woocommerce-error{
  background:var(--carbon)!important;background-image:none!important;border:1px solid var(--linea-2)!important;
  border-top:2px solid var(--aqua)!important;border-radius:3px!important;box-shadow:none!important;
  color:var(--tinta-2)!important;font-family:var(--optima)!important;font-size:15px!important;
  line-height:1.55!important;padding:16px 20px 16px 50px!important;position:relative;overflow:visible!important}
' . $c . ' .woocommerce-error,' . $k . ' .woocommerce-error{border-top-color:var(--magenta)!important}
' . $c . ' .woocommerce-info::before,' . $c . ' .woocommerce-message::before,' . $c . ' .woocommerce-error::before,
' . $k . ' .woocommerce-info::before,' . $k . ' .woocommerce-message::before,' . $k . ' .woocommerce-error::before{
  color:var(--aqua)!important;left:20px!important;top:17px!important}
' . $c . ' .woocommerce-error::before,' . $k . ' .woocommerce-error::before{color:var(--magenta)!important}
' . $c . ' .woocommerce-info a,' . $k . ' .woocommerce-info a,' . $c . ' .woocommerce-message a{color:var(--magenta)!important}

/* campos: mismos que el buscador de la cabecera */
' . $p . ' .woocommerce form .form-row label,' . $c . ' .coupon label{
  font-family:var(--mono)!important;font-size:10.5px!important;letter-spacing:.12em;
  text-transform:uppercase;color:var(--tinta-3)!important;font-weight:400!important;margin-bottom:6px}
' . $p . ' .woocommerce form .form-row .required{color:var(--magenta);text-decoration:none}
' . $p . ' .woocommerce form .form-row input.input-text,
' . $p . ' .woocommerce form .form-row textarea,
' . $p . ' .woocommerce form .form-row select,
' . $c . ' .coupon input.input-text{background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta)!important;
  font-family:var(--optima)!important;font-size:16px!important;padding:12px 14px!important;
  box-shadow:none!important;line-height:1.4;min-height:48px}
' . $p . ' .woocommerce form .form-row textarea{min-height:110px}
' . $p . ' .woocommerce form .form-row input.input-text:focus,
' . $p . ' .woocommerce form .form-row textarea:focus,
' . $p . ' .woocommerce form .form-row select:focus{border-color:var(--magenta)!important;outline:none}
' . $p . ' .woocommerce form .form-row input::placeholder,' . $p . ' .woocommerce form .form-row textarea::placeholder{
  color:var(--tinta-3)}
/* el país y el estado van con selectWoo: es un desplegable propio, no el select nativo */
' . $p . ' .select2-container--default .select2-selection--single{background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;height:48px!important}
/* el texto elegido llevaba 8 px arriba y abajo con 46 px de interlínea: 62 px
   dentro de una caja de 48, y se veía caído contra el borde inferior */
' . $p . ' .select2-container--default .select2-selection--single .select2-selection__rendered{
  color:var(--tinta)!important;line-height:46px!important;padding:0 34px 0 14px!important;
  height:46px!important;font-family:var(--optima)!important;font-size:16px}
' . $p . ' .select2-container--default .select2-selection--single .select2-selection__arrow{height:46px!important}
' . $p . ' .select2-container--default .select2-selection--single .select2-selection__arrow b{
  border-color:var(--tinta-3) transparent transparent transparent!important}
' . $p . ' .select2-dropdown{background:var(--carbon)!important;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;color:var(--tinta)!important}
' . $p . ' .select2-search--dropdown .select2-search__field{background:var(--negro)!important;
  border:1px solid var(--linea-2)!important;color:var(--tinta)!important;border-radius:2px}
' . $p . ' .select2-results__option{color:var(--tinta-2)!important;font-size:15px}
' . $p . ' .select2-results__option--highlighted[aria-selected],
' . $p . ' .select2-results__option--highlighted[data-selected]{background:var(--panel)!important;
  color:var(--tinta)!important}
' . $p . ' .woocommerce form .form-row input[type=checkbox],' . $p . ' #ship-to-different-address input[type=checkbox],
' . $p . ' .woocommerce form .form-row input[type=radio],' . $p . ' #payment input[type=radio]{
  accent-color:var(--magenta);width:17px;height:17px;vertical-align:-3px;margin-right:8px}
/* las casillas llevan su texto al lado: la etiqueta ya no va en versalitas */
' . $p . ' .woocommerce form .form-row label.checkbox,' . $p . ' .woocommerce form .form-row .woocommerce-form__label-for-checkbox,
' . $p . ' .woocommerce form .form-row label.checkbox span,
' . $p . ' .woocommerce form .form-row label:has(> input[type=checkbox]),
' . $p . ' .woocommerce form .form-row label:has(> input[type=radio]){font-family:var(--optima)!important;
  font-size:15.5px!important;letter-spacing:0!important;text-transform:none!important;
  color:var(--tinta-2)!important}
/* las opciones del grupo «¿por qué decidiste comprar?» (editor de campos) son
   casillas dentro de su etiqueta: salían en versalitas mono de 10 px */
' . $p . ' .woocommerce form .form-row label:has(> input[type=checkbox]){display:flex!important;
  align-items:center;margin:0 0 6px!important;line-height:1.35}

/* botones: el secundario perfilado, el principal en magenta */
' . $p . ' .woocommerce button.button,' . $p . ' .woocommerce a.button,' . $p . ' .woocommerce input.button{
  background:transparent!important;background-image:none!important;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;color:var(--tinta-2)!important;-webkit-text-fill-color:currentColor!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important;
  font-family:var(--mono)!important;font-size:11.5px!important;font-weight:400!important;
  letter-spacing:.07em;text-transform:none!important;padding:13px 18px!important;
  box-shadow:none!important;line-height:1.3!important;min-height:0!important;height:auto!important}
' . $p . ' .woocommerce button.button:hover,' . $p . ' .woocommerce a.button:hover{border-color:var(--tinta-3)!important;
  color:var(--tinta)!important}
' . $p . ' .woocommerce button.button:disabled,' . $p . ' .woocommerce button.button[disabled]{opacity:.45!important}
' . $p . ' .woocommerce a.checkout-button,' . $p . ' #place_order{background:var(--magenta)!important;
  border-color:var(--magenta)!important;color:#fff!important;-webkit-text-fill-color:#fff!important;
  font-family:var(--optima)!important;font-size:17px!important;letter-spacing:0!important;
  padding:17px 24px!important;width:100%;text-align:center;display:block}
' . $p . ' .woocommerce a.checkout-button:hover,' . $p . ' #place_order:hover{background:#FF3D97!important;
  border-color:#FF3D97!important;color:#fff!important}

/* ── carrito ───────────────────────────────────────────────────────── */
/* el tema envolvía el formulario del carrito en un panel vidrioso de 28 px de
   radio; aquí va con las mismas esquinas y el mismo fondo que el resto */
' . $p . ' form.woocommerce-cart-form{border-radius:3px!important;border:1px solid var(--linea)!important;
  background:var(--carbon)!important;background-image:none!important;box-shadow:none!important;
  backdrop-filter:none!important;padding:6px clamp(10px,1.6vw,20px) clamp(14px,2vw,20px)!important;
  margin-bottom:clamp(20px,3vw,32px)}
' . $p . ' table.shop_table{background:none!important;border:0!important;border-radius:0!important;
  box-shadow:none!important;border-collapse:collapse;width:100%;margin:0 0 24px!important}
' . $p . ' table.shop_table th{font-family:var(--mono)!important;font-size:10.5px!important;
  letter-spacing:.12em;text-transform:uppercase;font-weight:400!important;color:var(--tinta-3)!important;
  background:none!important;border:0!important;border-bottom:1px solid var(--linea-2)!important;
  padding:12px 14px!important}
' . $p . ' table.shop_table td{background:none!important;border:0!important;
  border-bottom:1px solid var(--linea)!important;padding:16px 14px!important;color:var(--tinta-2)!important;
  vertical-align:middle}
' . $p . ' table.shop_table .product-name a{color:var(--tinta)!important;font-size:17px;
  -webkit-text-fill-color:currentColor!important}
' . $p . ' table.shop_table .product-name a:hover{color:var(--magenta)!important}
/* solo las celdas: con `.product-price` a secas también cogía el th de la
   cabecera, y «PRECIO» y «SUBTOTAL» salían en 15 px claros junto a los demás en 10 */
' . $p . ' table.shop_table td.product-price,' . $p . ' table.shop_table td.product-subtotal,
' . $p . ' table.shop_table .woocommerce-Price-amount,' . $p . ' table.shop_table bdi{
  font-family:var(--mono)!important;color:var(--tinta)!important;font-size:15px!important;
  -webkit-text-fill-color:currentColor!important;background:none!important}
' . $p . ' table.shop_table .product-thumbnail{width:84px}
/* la hoja del carrito les ponía fondo blanco, 8 px de relleno y sombra, con
   !important: el vial quedaba diminuto en un cuadro blanco */
' . $p . ' table.shop_table .product-thumbnail img{width:64px!important;height:64px!important;
  max-width:none;border-radius:2px!important;object-fit:contain;border:1px solid var(--linea-2)!important;
  padding:0!important;box-shadow:none!important;
  background:radial-gradient(120% 86% at 50% 10%, #FFF 0%, var(--vitrina) 58%, #DDE5E2 100%)!important}
/* el render del vial es alto: se enseña entero dentro del mismo cuadro */
' . $p . ' table.shop_table .product-thumbnail img.pys-mini-vial{
  background:linear-gradient(180deg,#FCFEFD 0%,#F5F7F6 50%,#D8E1DE 100%)!important}
' . $p . ' table.shop_table .product-remove a.remove{display:grid!important;place-items:center;
  width:30px;height:30px;border:1px solid var(--linea-2)!important;border-radius:2px!important;
  background:none!important;color:var(--tinta-3)!important;font-size:18px!important;line-height:1}
' . $p . ' table.shop_table .product-remove a.remove:hover{border-color:var(--magenta)!important;
  color:var(--magenta)!important}
' . $p . ' table.shop_table .quantity input.qty{background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta)!important;
  font-family:var(--mono)!important;width:70px!important;height:44px!important;text-align:center;
  box-shadow:none!important}
' . $p . ' table.shop_table td.actions{padding-top:20px!important}
' . $c . ' .coupon{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
' . $c . ' .coupon input.input-text{width:220px!important;min-height:44px!important;min-width:0!important}
@media (max-width:760px){ ' . $c . ' .coupon input.input-text{width:100%!important} }

' . $p . ' .cart-collaterals{display:flex;justify-content:flex-end}
' . $p . ' .cart_totals{width:min(440px,100%)!important;float:none!important;background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-radius:3px!important;box-shadow:none!important;
  padding:clamp(18px,2.4vw,28px)!important}
' . $p . ' .cart_totals h2{font-family:var(--optima)!important;font-weight:400!important;
  font-size:24px!important;color:var(--tinta)!important;margin:0 0 14px!important;text-transform:none!important}
' . $p . ' .cart_totals table.shop_table th{width:40%;vertical-align:top}
' . $p . ' .cart_totals .order-total .woocommerce-Price-amount,' . $p . ' .cart_totals .order-total bdi{
  font-size:20px!important;color:var(--tinta)!important}
' . $p . ' .cart_totals .shipping-calculator-button,' . $p . ' .cart_totals a{color:var(--magenta)!important;
  font-family:var(--mono);font-size:11.5px;-webkit-text-fill-color:currentColor!important}
' . $p . ' .cart_totals .woocommerce-shipping-destination{color:var(--tinta-3);font-size:14px}
' . $p . ' .wc-proceed-to-checkout{padding:18px 0 0!important}
' . $p . ' .cart-empty{font-family:var(--optima);font-size:18px;color:var(--tinta-2)}
@media (max-width:760px){
  ' . $p . ' .cart-collaterals{display:block}
  ' . $p . ' table.shop_table_responsive tr td::before{font-family:var(--mono);font-size:10px;
    letter-spacing:.1em;text-transform:uppercase;color:var(--tinta-3)}
}

/* ── finalizar compra ──────────────────────────────────────────────── */
/* Datos del cliente a la izquierda y resumen del pedido pegado a la derecha,
   para que el total y el botón estén siempre a la vista. WooCommerce los apila
   con floats; aquí va en retícula. Todo lo que no sea una de esas tres piezas
   —avisos de error que se inyectan arriba, por ejemplo— ocupa el ancho entero. */
' . $p . ' form.checkout{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,.95fr);
  column-gap:clamp(24px,4vw,56px);align-items:start}
' . $p . ' form.checkout > *{grid-column:1 / -1}
' . $p . ' form.checkout > #customer_details{grid-column:1;grid-row:span 2}
' . $p . ' form.checkout > #order_review_heading{grid-column:2;margin:0 0 12px!important}
' . $p . ' form.checkout > #order_review{grid-column:2;position:sticky;top:104px}
' . $p . ' #customer_details .col-1,' . $p . ' #customer_details .col-2{width:100%!important;float:none!important;
  max-width:none}
' . $p . ' #customer_details .col-2{margin-top:clamp(20px,3vw,34px)}
' . $p . ' .woocommerce-billing-fields h3,' . $p . ' .woocommerce-shipping-fields h3,
' . $p . ' .woocommerce-additional-fields h3,' . $p . ' #order_review_heading{
  font-family:var(--optima)!important;font-weight:400!important;font-size:24px!important;
  color:var(--tinta)!important;margin:0 0 16px!important;text-transform:none!important}
' . $p . ' #ship-to-different-address{font-size:18px!important}
' . $p . ' #ship-to-different-address label{font-family:var(--optima)!important;text-transform:none!important;
  letter-spacing:0!important;color:var(--tinta)!important;font-size:18px!important}
/* En teléfono, nombre y apellidos quedaban lado a lado a 135 px cada uno:
   demasiado estrecho para escribir con el pulgar. Se apilan. */
@media (max-width:560px){
  ' . $p . ' .woocommerce form .form-row-first,' . $p . ' .woocommerce form .form-row-last{
    width:100%!important;float:none!important;margin-right:0!important}
}
@media (max-width:900px){
  ' . $p . ' form.checkout{grid-template-columns:1fr}
  ' . $p . ' form.checkout > #customer_details,' . $p . ' form.checkout > #order_review_heading,
  ' . $p . ' form.checkout > #order_review{grid-column:1;grid-row:auto;position:static}
}

/* resumen del pedido */
' . $p . ' #order_review{background:var(--carbon)!important;border:1px solid var(--linea-2)!important;
  border-radius:3px!important;box-shadow:none!important;padding:clamp(18px,2.4vw,26px)!important}
' . $p . ' .woocommerce-checkout-review-order-table{margin-bottom:18px!important}
' . $p . ' .woocommerce-checkout-review-order-table .order-total .woocommerce-Price-amount,
' . $p . ' .woocommerce-checkout-review-order-table .order-total bdi{font-size:20px!important}

/* pasarelas: se estiliza la lista y el recuadro, nunca lo que hay dentro */
' . $p . ' #payment{background:none!important;border:0!important;border-radius:0!important;padding:0!important}
' . $p . ' #payment ul.payment_methods{border:0!important;padding:0!important;margin:0 0 16px!important;
  list-style:none;display:flex;flex-direction:column;gap:8px}
' . $p . ' #payment ul.payment_methods li.wc_payment_method{background:var(--carbon-2)!important;
  border:1px solid var(--linea)!important;border-radius:2px!important;padding:13px 14px!important;
  margin:0!important;transition:border-color .2s}
/* Radio y nombre en la misma fila. Con los dos en línea, cuando el nombre y
   sus logotipos no cabían detrás del radio, el nombre bajaba entero a la fila
   de abajo y el radio se quedaba solo (Tarjeta, USDT, Transferencia en el
   teléfono). El recuadro de la pasarela ocupa la fila completa debajo. */
' . $p . ' #payment ul.payment_methods li.wc_payment_method{display:grid!important;
  grid-template-columns:auto minmax(0,1fr);column-gap:10px;align-items:center}
/* el «clearfix» de WooCommerce (::before y ::after con display:table) se
   volvía una celda más de la retícula y echaba el radio a la derecha */
' . $p . ' #payment ul.payment_methods li.wc_payment_method::before,
' . $p . ' #payment ul.payment_methods li.wc_payment_method::after,
' . $p . ' #payment ul.payment_methods::before,' . $p . ' #payment ul.payment_methods::after{
  content:none!important;display:none!important}
' . $p . ' #payment ul.payment_methods li.wc_payment_method > input[type=radio]{margin:0!important}
' . $p . ' #payment ul.payment_methods li.wc_payment_method > label{margin:0!important;line-height:1.35!important}
' . $p . ' #payment ul.payment_methods li.wc_payment_method > :not(input):not(label){grid-column:1 / -1}
' . $p . ' #payment ul.payment_methods li.wc_payment_method:has(input:checked){
  border-color:color-mix(in srgb,var(--magenta) 60%,transparent)!important}
' . $p . ' #payment ul.payment_methods li > label{font-family:var(--optima)!important;font-size:16px!important;
  color:var(--tinta)!important;text-transform:none!important;letter-spacing:0!important;cursor:pointer}
' . $p . ' #payment ul.payment_methods li img{max-height:22px;width:auto;vertical-align:middle;margin-left:6px}
' . $p . ' #payment div.payment_box{background:var(--negro)!important;border:1px solid var(--linea)!important;
  border-radius:2px!important;color:var(--tinta-2)!important;font-size:14.5px!important;
  margin:12px 0 0!important;padding:14px 16px!important}
' . $p . ' #payment div.payment_box::before{display:none!important}
' . $p . ' #payment div.form-row.place-order{padding:0!important;margin:0!important;background:none!important}
' . $p . ' .woocommerce-terms-and-conditions-wrapper,' . $p . ' .woocommerce-privacy-policy-text{
  color:var(--tinta-3)!important;font-size:13.5px!important;line-height:1.55;margin-bottom:16px}
' . $p . ' .woocommerce-privacy-policy-text a,' . $p . ' .woocommerce-terms-and-conditions-wrapper a{
  color:var(--magenta)!important}

/* cupón e inicio de sesión desplegables */
' . $p . ' .woocommerce-form-coupon-toggle .woocommerce-info,' . $p . ' .woocommerce-form-login-toggle .woocommerce-info{
  border-top-color:var(--linea-2)!important}
' . $p . ' .woocommerce-form-coupon,' . $p . ' .woocommerce-form-login{background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-radius:3px!important;padding:18px!important}
';
}
