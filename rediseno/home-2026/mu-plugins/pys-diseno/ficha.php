<?php
/**
 * Ficha de producto.
 *
 * Solo diseño. No se toca la galería ni su orden —son imágenes del producto, y
 * en los variables hay una por variación—, ni los textos, ni las pestañas.
 * Lo que cambia es la retícula, la tipografía y los controles de compra.
 *
 * El panel de certificado de análisis lo pinta `pys-coa.php` y trae su propia
 * hoja; aquí solo se le da su sitio en la retícula.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Hoja de la ficha. */
function pys_dis_css_ficha() {
	return '
/* ── ficha de producto ─────────────────────────────────────────────── */
/* WooCommerce maqueta la ficha con floats al 48 %. Se pasa a retícula: con
   floats, cualquier bloque que se añada después (el panel de COA, por ejemplo)
   se cuela en la columna equivocada. */
.pys-h26.single-product div.product{display:grid;
  grid-template-columns:minmax(0,1.02fr) minmax(0,.98fr);
  gap:clamp(24px,4vw,56px);align-items:start}
.pys-h26.single-product div.product::before,
.pys-h26.single-product div.product::after{display:none}
.pys-h26.single-product div.product > .woocommerce-product-gallery{grid-column:1;
  width:auto!important;float:none!important;margin:0!important;position:sticky;top:104px}
.pys-h26.single-product div.product > .summary{grid-column:2;width:auto!important;
  float:none!important;margin:0!important;padding:0}
/* todo lo que va debajo ocupa el ancho completo */
.pys-h26.single-product div.product > .woocommerce-tabs,
.pys-h26.single-product div.product > .related,
.pys-h26.single-product div.product > .up-sells,
.pys-h26.single-product div.product > .pys-coa,
.pys-h26.single-product div.product > .woocommerce-product-gallery + .pys-coa{
  grid-column:1 / -1}
@media (max-width:860px){
  .pys-h26.single-product div.product{grid-template-columns:1fr}
  .pys-h26.single-product div.product > .woocommerce-product-gallery{position:static}
  .pys-h26.single-product div.product > .summary{grid-column:1}
}

/* galería: el mismo cristal de vitrina que las tarjetas */
.pys-h26 .woocommerce-product-gallery{padding:0}
.pys-h26 .woocommerce-product-gallery__wrapper{margin:0;border:1px solid var(--linea-2);
  border-radius:3px;overflow:hidden;
  background:radial-gradient(120% 86% at 50% 10%, #FFF 0%, var(--vitrina) 58%, #DDE5E2 100%)}
.pys-h26 .woocommerce-product-gallery__image{margin:0}
.pys-h26 .woocommerce-product-gallery__image img{display:block;width:100%;height:auto;
  border-radius:0}
.pys-h26 .woocommerce-product-gallery .flex-control-thumbs{display:flex;gap:8px;margin:10px 0 0;
  padding:0;list-style:none;flex-wrap:wrap}
.pys-h26 .woocommerce-product-gallery .flex-control-thumbs li{width:auto;margin:0;float:none}
.pys-h26 .woocommerce-product-gallery .flex-control-thumbs img{width:62px;height:62px;
  object-fit:contain;border:1px solid var(--linea-2);border-radius:2px;opacity:.65;
  background:var(--vitrina);cursor:pointer;transition:opacity .2s,border-color .2s}
.pys-h26 .woocommerce-product-gallery .flex-control-thumbs img:hover,
.pys-h26 .woocommerce-product-gallery .flex-control-thumbs .flex-active{opacity:1;
  border-color:var(--magenta)}
.pys-h26 .woocommerce-product-gallery__trigger{background:var(--carbon);border:1px solid var(--linea-2);
  border-radius:2px;color:var(--tinta-2);top:12px;right:12px;text-indent:0;line-height:1}

/* columna de compra */
html body[class][class][class] .product_title{font-family:var(--optima)!important;
  font-size:clamp(30px,3.4vw,46px)!important;font-weight:400!important;line-height:1.08;
  letter-spacing:-.012em;color:var(--tinta)!important;margin:0 0 16px;text-transform:none!important}
html body[class][class][class] .summary .price,
html body[class][class][class] .summary .price .woocommerce-Price-amount,
html body[class][class][class] .summary .price bdi,
html body[class][class][class] .summary .price span{font-family:var(--mono)!important;
  font-size:26px!important;font-weight:400!important;color:var(--tinta)!important;
  background:none!important;border:0!important;padding:0!important;box-shadow:none!important;
  -webkit-text-fill-color:currentColor!important}
html body[class][class][class] .summary .price{margin:0 0 20px;display:block}
html body[class][class][class] .summary .price .woocommerce-Price-currencySymbol{
  font-size:15px!important;vertical-align:top}
html body[class][class][class] .summary .price del{opacity:.5}
html body[class][class][class] .summary .price ins{text-decoration:none}
.pys-h26 .woocommerce-product-details__short-description{color:var(--tinta-2);font-size:16.5px;
  line-height:1.6;max-width:56ch;margin-bottom:22px}
.pys-h26 .woocommerce-product-details__short-description p{margin:0 0 10px}
.pys-h26 .summary .stock{font-family:var(--mono);font-size:11px;letter-spacing:.09em;
  text-transform:uppercase;margin:0 0 16px}
.pys-h26 .summary .stock.in-stock{color:var(--aqua)}
.pys-h26 .summary .stock.out-of-stock{color:var(--tinta-3)}

/* cantidad y botón */
.pys-h26 form.cart{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:0 0 22px}
.pys-h26 .quantity{margin:0}
html body[class][class][class] .quantity input.qty{background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta)!important;
  font-family:var(--mono)!important;font-size:15px!important;width:78px!important;
  height:50px!important;padding:0 10px!important;text-align:center;box-shadow:none!important}
html body[class][class][class] .single_add_to_cart_button{background:var(--magenta)!important;
  background-image:none!important;border:1px solid var(--magenta)!important;
  border-radius:2px!important;color:#fff!important;-webkit-text-fill-color:#fff!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important;
  font-family:var(--optima)!important;font-size:16px!important;font-weight:400!important;
  letter-spacing:0;padding:0 30px!important;height:50px!important;min-height:0!important;
  line-height:50px!important;box-shadow:none!important;text-transform:none!important;
  width:auto;flex:1 1 auto;max-width:320px}
html body[class][class][class] .single_add_to_cart_button:hover{background:#FF3D97!important;
  border-color:#FF3D97!important}

/* variaciones */
.pys-h26 .variations{width:100%;margin:0 0 18px;border:0}
.pys-h26 .variations th,.pys-h26 .variations td{border:0;padding:0 0 10px;background:none}
.pys-h26 .variations th.label{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--tinta-3);font-weight:400;padding-right:14px;
  vertical-align:middle;white-space:nowrap}
html body[class][class][class] .variations select{appearance:none;-webkit-appearance:none;
  background:var(--carbon) url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'12\' height=\'12\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%23718C84\' stroke-width=\'2.4\'%3E%3Cpath d=\'M5 9l7 7 7-7\'/%3E%3C/svg%3E") no-repeat right 14px center!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta)!important;
  font-family:var(--mono)!important;font-size:13px!important;padding:12px 38px 12px 14px!important;
  min-width:190px;height:auto!important}
/* el desplegable nativo se pinta sobre blanco: sin esto las opciones heredan
   el blanco del texto y quedan ilegibles */
.pys-h26 .variations select option{color:#111;background:#fff}
.pys-h26 .reset_variations{font-family:var(--mono);font-size:11px;color:var(--tinta-3);
  letter-spacing:.05em}
.pys-h26 .woocommerce-variation-price{margin-bottom:14px}

/* metadatos */
.pys-h26 .product_meta{border-top:1px solid var(--linea);padding-top:18px;margin-top:4px;
  font-family:var(--mono);font-size:11px;letter-spacing:.05em;color:var(--tinta-3);
  display:flex;flex-direction:column;gap:8px;line-height:1.7}
.pys-h26 .product_meta > span{display:block}
.pys-h26 .product_meta a{color:var(--tinta-2)}
.pys-h26 .product_meta a:hover{color:var(--magenta)}
/* las etiquetas son muchas y en magenta se comían la columna */
.pys-h26 .product_meta .tagged_as a{color:var(--tinta-3)}

/* pestañas */
.pys-h26 .woocommerce-tabs{margin-top:clamp(34px,5vw,64px)}
.pys-h26 .woocommerce-tabs ul.tabs{display:flex;gap:4px;list-style:none;margin:0 0 26px;padding:0;
  border-bottom:1px solid var(--linea);flex-wrap:wrap}
.pys-h26 .woocommerce-tabs ul.tabs::before,.pys-h26 .woocommerce-tabs ul.tabs::after{display:none}
.pys-h26 .woocommerce-tabs ul.tabs li{background:none;border:0;border-radius:0;margin:0;padding:0;
  box-shadow:none}
.pys-h26 .woocommerce-tabs ul.tabs li::before,.pys-h26 .woocommerce-tabs ul.tabs li::after{
  display:none}
html body[class][class][class] .woocommerce-tabs ul.tabs li a{display:block;padding:13px 20px;
  font-family:var(--mono)!important;font-size:11.5px!important;letter-spacing:.09em;
  text-transform:uppercase;color:var(--tinta-3)!important;font-weight:400!important;
  border-bottom:2px solid transparent;margin-bottom:-1px;background:none!important}
html body[class][class][class] .woocommerce-tabs ul.tabs li.active a{color:var(--tinta)!important;
  border-bottom-color:var(--magenta)}
.pys-h26 .woocommerce-Tabs-panel{color:var(--tinta-2);font-size:16.5px;line-height:1.65}
.pys-h26 .woocommerce-Tabs-panel > h2:first-child{display:none}

/* relacionados */
.pys-h26 .related,.pys-h26 .up-sells{margin-top:clamp(40px,6vw,80px)}
.pys-h26 .related > h2,.pys-h26 .up-sells > h2{font-family:var(--optima);
  font-size:clamp(24px,3vw,38px);font-weight:400;letter-spacing:-.012em;color:var(--tinta);
  margin:0 0 clamp(18px,2.4vw,28px)}
' . pys_dis_css_ficha_auditoria();
}

/**
 * La imagen principal de la galería se pide al tamaño de 768 px.
 *
 * `woocommerce_single` está configurado a 300 px, así que la foto que se
 * enseña en una columna de ~590 px salía estirada o, con el tope de 420 px del
 * Customizer, como un sello pequeño en medio de una caja gris. Es la MISMA
 * imagen (mismo adjunto, mismo texto alternativo), solo otro archivo de su
 * `srcset`; las miniaturas y la ampliación no cambian.
 */
add_filter(
	'woocommerce_gallery_image_size',
	function ( $tam ) {
		return ( function_exists( 'is_product' ) && is_product() ) ? 'medium_large' : $tam;
	}
);

/**
 * La imagen principal (la que se ve al cargar, y la candidata a LCP) se
 * decodifica en síncrono. Con el archivo de 768 px y `decoding="async"`, la
 * captura de página entera la pintaba en blanco hasta el segundo intento; en
 * la imagen que se ve primero, la decodificación asíncrona no aporta nada.
 * Solo cambia ese atributo; las demás imágenes de la galería no se tocan.
 */
add_filter(
	'woocommerce_gallery_image_html_attachment_image_params',
	function ( $params, $attachment_id = 0, $image_size = '', $main_image = false ) {
		if ( $main_image ) {
			$params['decoding'] = 'sync';
		}
		return $params;
	},
	10,
	4
);

/**
 * Segunda reconquista de la ficha (auditoría del 21-sep).
 *
 * Cada ficha trae en su documento de Elementor una hoja propia con reglas
 * `body.elementor-page-N …` —la misma en las 22, con alguna variante—, que
 * convierte la ficha en tres paneles de vidrio (radios de 32-34 px, degradados,
 * halos de neón), las pestañas en píldoras con degradado, el precio en aqua a
 * 900 y las etiquetas en magenta negrita. Esas reglas pisaban las de arriba.
 * En algunas fichas trae además `body.elementor-page-N a{color:#00E5C4}`, que
 * pintaba de aqua la cabecera y el pie compartidos.
 *
 * El cuerpo de la descripción es un solo widget de texto de Elementor con HTML
 * limpio (h2, h3, p, ul, ol, table, figure); salía en Arial gris sobre panel
 * gris, con los h3 y las celdas en #7A7A7A (el gris por defecto de Elementor) y
 * tablas con rejilla completa. Aquí pasa a ser prosa del sistema, como el blog.
 *
 * Dos fugas de la base también se corrigen aquí, solo en la ficha:
 *  - `.pys-h26 section{padding-block:48-104px}` (pensada para las secciones de
 *    la portada) inflaba el panel de COA, el bloque de relacionados y el
 *    `<section>` que algunas descripciones llevan dentro (BPC-157: huecos de
 *    100 px en blanco);
 *  - en el teléfono la columna única era `1fr` y no `minmax(0,1fr)`: una tabla
 *    ancha la ensanchaba por encima de la pantalla y el texto salía cortado.
 */
function pys_dis_css_ficha_auditoria() {
	return <<<'CSS'
/* ── la ficha no es un panel ─────────────────────────────────────────── */
html body[class][class][class] div.product.type-product{background:none!important;
  background-image:none!important;border:0!important;border-radius:0!important;box-shadow:none!important;
  padding:0!important;overflow:visible!important;-webkit-backdrop-filter:none!important;
  backdrop-filter:none!important}
html body[class][class][class] div.product.type-product > .pys-revisado-por,
html body[class][class][class] div.product.type-product > section{grid-column:1 / -1}
@media (max-width:860px){
  html body[class][class][class].single-product div.product.type-product{
    grid-template-columns:minmax(0,1fr)!important}
  html body[class][class][class] div.product.type-product > *{grid-column:1!important;min-width:0}
}
/* la base da 48-104 px de alto a todo elemento section: aquí no */
html body[class][class][class] div.product.type-product section{padding-block:0!important}
html body[class][class][class] div.product.type-product section.pys-coa{padding:26px 28px!important;
  margin:0!important}
@media (max-width:560px){
  html body[class][class][class] div.product.type-product section.pys-coa{padding:20px 18px!important}
}

/* ── galería ──────────────────────────────────────────────────────────── */
/* El `position:sticky` de arriba perdía contra `position:relative` de
   WooCommerce, pero su `top:104px` sí se aplicaba: la galería bajaba 104 px y
   se montaba encima del panel de COA. Tampoco puede ser sticky: en una
   retícula el límite del sticky es el contenedor entero (div.product, que
   incluye pestañas y relacionados), no la fila, así que la foto se quedaba
   pegada encima de la descripción al desplazarse. Va quieta. */
html body[class][class][class].single-product div.product > .woocommerce-product-gallery{
  position:relative!important;top:auto!important;align-self:start}
html body[class][class][class] div.product .woocommerce-product-gallery{background:none!important;
  background-image:none!important;border:0!important;border-radius:0!important;box-shadow:none!important;
  padding:0!important;overflow:visible!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
html body[class][class][class] div.product .woocommerce-product-gallery .flex-viewport,
html body[class][class][class] div.product .woocommerce-product-gallery > .woocommerce-product-gallery__wrapper{
  border:1px solid var(--linea-2);border-radius:3px;overflow:hidden;
  background:radial-gradient(120% 86% at 50% 10%, #FFF 0%, var(--vitrina) 58%, #DDE5E2 100%)}
html body[class][class][class] div.product .woocommerce-product-gallery .flex-viewport
  .woocommerce-product-gallery__wrapper{border:0;border-radius:0;background:none}
html body[class][class][class] div.product .woocommerce-product-gallery__image img,
html body[class][class][class] div.product .woocommerce-product-gallery__image a img{width:100%!important;
  height:auto!important;max-height:600px!important;max-width:100%!important;margin:0!important;
  object-fit:contain;border-radius:0!important;border:0!important;box-shadow:none!important;
  filter:none!important;background:none!important;display:block}
html body[class][class][class] div.product .woocommerce-product-gallery__image img.zoomImg{
  width:auto!important;max-width:none!important;border-radius:0!important;filter:none!important}
html body[class][class][class] div.product .woocommerce-product-gallery ol.flex-control-thumbs{
  display:flex!important;gap:8px;margin:10px 0 0!important;padding:0!important;list-style:none;flex-wrap:wrap}
html body[class][class][class] div.product .woocommerce-product-gallery ol.flex-control-thumbs li{
  width:auto!important;margin:0!important;float:none!important;padding:0!important}
html body[class][class][class] div.product .woocommerce-product-gallery ol.flex-control-thumbs li img{
  width:62px!important;height:62px!important;object-fit:contain;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;background:var(--vitrina)!important;filter:none!important;box-shadow:none!important;
  opacity:.6;cursor:pointer;transition:opacity .2s,border-color .2s}
html body[class][class][class] div.product .woocommerce-product-gallery ol.flex-control-thumbs li img:hover,
html body[class][class][class] div.product .woocommerce-product-gallery ol.flex-control-thumbs li img.flex-active{
  opacity:1;border-color:var(--magenta)!important}
html body[class][class][class] div.product .woocommerce-product-gallery__trigger{width:36px!important;
  height:36px!important;background:var(--carbon)!important;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;box-shadow:none!important;color:var(--tinta-2)!important;top:12px!important;
  right:12px!important;display:grid!important;place-items:center;z-index:3}

/* ── columna de compra ────────────────────────────────────────────────── */
html body[class][class][class] div.product .summary{background:none!important;background-image:none!important;
  border:0!important;border-radius:0!important;box-shadow:none!important;padding:0!important;
  -webkit-backdrop-filter:none!important;backdrop-filter:none!important;text-align:left!important}
html body[class][class][class] div.product .summary .product_title{text-align:left!important;
  letter-spacing:-.012em!important}
html body[class][class][class] div.product .summary .price{text-align:left!important;letter-spacing:0!important}
html body[class][class][class] div.product .summary p.stock{display:inline-block;background:none!important;
  border:0!important;border-radius:0!important;padding:0!important;box-shadow:none!important;
  font-family:var(--mono)!important;font-size:11px!important;font-weight:400!important;letter-spacing:.09em!important;
  text-transform:uppercase;margin:0 0 16px!important}
html body[class][class][class] div.product .summary p.stock.in-stock{color:var(--aqua)!important}
html body[class][class][class] div.product .summary p.stock.out-of-stock{color:var(--tinta-3)!important}
html body[class][class][class] div.product .summary .woocommerce-product-details__short-description,
html body[class][class][class] div.product .summary .woocommerce-product-details__short-description p{
  color:var(--tinta-2)!important;font-family:var(--optima)!important;font-size:16.5px!important;line-height:1.6!important}
html body[class][class][class] div.product form.cart{display:flex!important;flex-direction:row!important;
  flex-wrap:wrap;align-items:center!important;gap:12px;margin:0 0 22px!important}
html body[class][class][class] div.product form.variations_form{display:block!important}
html body[class][class][class] div.product form.cart .woocommerce-variation-add-to-cart{display:flex;
  flex-wrap:wrap;align-items:center;gap:12px}
html body[class][class][class] div.product form.cart .quantity{margin:0!important;float:none!important}
html body[class][class][class] div.product .single_add_to_cart_button{flex:1 1 auto!important;
  width:auto!important;max-width:320px!important;transform:none!important;filter:none!important;
  float:none!important;margin:0!important}
html body[class][class][class] div.product .single_add_to_cart_button.disabled,
html body[class][class][class] div.product .single_add_to_cart_button:disabled{opacity:.45!important;cursor:not-allowed}
html body[class][class][class] div.product .variations select{box-shadow:none!important;width:100%;max-width:320px}
html body[class][class][class] div.product .variations th,
html body[class][class][class] div.product .variations td{vertical-align:middle!important;
  padding:0 0 10px!important;line-height:1.3!important;border:0!important;background:none!important}
html body[class][class][class] div.product .variations th.label{padding-right:14px!important}
html body[class][class][class] div.product .variations th.label label{margin:0!important;color:var(--tinta-3)!important;
  font-family:var(--mono)!important;font-size:10.5px!important;font-weight:400!important;letter-spacing:.14em}
html body[class][class][class] div.product .woocommerce-variation-availability p.stock{margin:0 0 12px!important}
html body[class][class][class] div.product .pys-coa-aviso{margin:0 0 20px!important;font-size:14px!important}
html body[class][class][class] div.product .pys-coa-aviso a{color:var(--aqua)!important;font-weight:400!important;
  text-decoration:underline!important;text-underline-offset:3px;font-family:var(--optima)!important}
html body[class][class][class] div.product .product_meta{text-align:left!important;margin-top:4px!important;
  padding-top:18px!important;border-top:1px solid var(--linea)!important;color:var(--tinta-3)!important;
  font-family:var(--mono)!important;font-size:11px!important;line-height:1.7!important}
html body[class][class][class] div.product .product_meta span{color:var(--tinta-3)!important;
  font-family:var(--mono)!important;font-weight:400!important}
html body[class][class][class] div.product .product_meta a{color:var(--tinta-2)!important;font-weight:400!important;
  text-decoration:none!important}
html body[class][class][class] div.product .product_meta .tagged_as a{color:var(--tinta-3)!important}
html body[class][class][class] div.product .product_meta a:hover{color:var(--magenta)!important}
@media (max-width:560px){
  html body[class][class][class] div.product .single_add_to_cart_button{max-width:none!important}
}

/* ── pestañas ─────────────────────────────────────────────────────────── */
html body[class][class][class] div.product .woocommerce-tabs{background:none!important;
  background-image:none!important;border:0!important;border-radius:0!important;box-shadow:none!important;
  padding:0!important;margin-top:clamp(34px,5vw,64px)!important;-webkit-backdrop-filter:none!important;
  backdrop-filter:none!important;max-width:880px;width:100%;justify-self:center}
html body[class][class][class] div.product .woocommerce-tabs ul.tabs{border:0!important;
  border-bottom:1px solid var(--linea)!important;padding:0!important;margin:0 0 30px!important;
  display:flex!important;gap:4px;flex-wrap:wrap;overflow:visible}
html body[class][class][class] div.product .woocommerce-tabs ul.tabs li{background:none!important;
  background-image:none!important;border:0!important;border-radius:0!important;box-shadow:none!important;
  margin:0!important;padding:0!important}
html body[class][class][class] div.product .woocommerce-tabs ul.tabs li a{padding:13px 18px!important;
  line-height:1.3!important;-webkit-text-fill-color:currentColor!important}
html body[class][class][class] div.product .woocommerce-tabs ul.tabs li a:hover{color:var(--tinta)!important}
html body[class][class][class] div.product .woocommerce-Tabs-panel{background:none!important;border:0!important;
  border-radius:0!important;box-shadow:none!important;padding:0!important;margin:0!important;
  color:var(--tinta-2)!important;font-family:var(--optima)!important}
/* en el teléfono la hoja de Elementor de cada ficha las apila en columna, a
   todo el ancho y centradas; aquí siguen siendo una fila de pestañas */
@media (max-width:768px){
  html body[class][class][class] div.product .woocommerce-tabs ul.tabs{flex-direction:row!important;
    gap:0!important;align-items:flex-end}
  html body[class][class][class] div.product .woocommerce-tabs ul.tabs li{width:auto!important;
    text-align:left!important}
}
@media (max-width:560px){
  html body[class][class][class] div.product .woocommerce-tabs ul.tabs li a{padding:12px 11px!important;
    font-size:10.5px!important;letter-spacing:.06em!important}
}

/* ── descripción: el widget de Elementor como prosa ──────────────────── */
html body[class][class][class] .woocommerce-Tabs-panel--description .elementor,
html body[class][class][class] .woocommerce-Tabs-panel--description .e-con,
html body[class][class][class] .woocommerce-Tabs-panel--description .e-con-inner,
html body[class][class][class] .woocommerce-Tabs-panel--description .elementor-widget,
html body[class][class][class] .woocommerce-Tabs-panel--description .elementor-widget-container{
  background:none!important;background-image:none!important;border:0!important;border-radius:0!important;
  box-shadow:none!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important}
html body[class][class][class] .woocommerce-Tabs-panel--description .e-con{--padding-top:0px;
  --padding-bottom:0px;--padding-left:0px;--padding-right:0px;padding:0!important;min-height:0!important}
html body[class][class][class] .woocommerce-Tabs-panel--description .e-con-inner{max-width:none!important;
  padding:0!important}
html body[class][class][class] .woocommerce-Tabs-panel--description .elementor-widget-container{
  font-family:var(--optima)!important;font-size:17px!important;line-height:1.72!important;
  color:var(--tinta-2)!important}
html body[class][class][class] .woocommerce-Tabs-panel--description p,
html body[class][class][class] .woocommerce-Tabs-panel--description li,
html body[class][class][class] .woocommerce-Tabs-panel--description dd,
html body[class][class][class] .woocommerce-Tabs-panel--description dt{font-family:var(--optima)!important;
  font-size:17px!important;line-height:1.72!important;color:var(--tinta-2)!important}
html body[class][class][class] .woocommerce-Tabs-panel--description p{margin:0 0 1.05em!important}
html body[class][class][class] .woocommerce-Tabs-panel--description strong,
html body[class][class][class] .woocommerce-Tabs-panel--description b{color:var(--tinta)!important;font-weight:600}
html body[class][class][class] .woocommerce-Tabs-panel--description em{color:inherit}
html body[class][class][class] .woocommerce-Tabs-panel--description h2{font-family:var(--optima)!important;
  font-weight:400!important;font-size:clamp(24px,2.6vw,32px)!important;line-height:1.15!important;
  letter-spacing:-.01em!important;color:var(--tinta)!important;margin:1.6em 0 .55em!important;
  padding-top:.8em!important;border-top:1px solid var(--linea)!important;text-transform:none!important;
  -webkit-text-fill-color:currentColor!important;background:none!important}
html body[class][class][class] .woocommerce-Tabs-panel--description .elementor-widget-container > h2:first-child,
html body[class][class][class] .woocommerce-Tabs-panel--description .elementor-widget-container > section:first-child + h2{
  margin-top:0!important;padding-top:0!important;border-top:0!important}
html body[class][class][class] .woocommerce-Tabs-panel--description .elementor-widget-container > section:first-child + h2{
  margin-top:1.4em!important}
/* si el texto ya trae una raya antes del ladillo, no se dibujan dos */
html body[class][class][class] .woocommerce-Tabs-panel--description hr + h2{border-top:0!important;
  padding-top:0!important;margin-top:0!important}
html body[class][class][class] .woocommerce-Tabs-panel--description h3{font-family:var(--optima)!important;
  font-weight:400!important;font-size:21px!important;line-height:1.28!important;letter-spacing:0!important;
  color:var(--tinta)!important;margin:1.55em 0 .45em!important;text-transform:none!important;
  -webkit-text-fill-color:currentColor!important;background:none!important;overflow-wrap:normal}
html body[class][class][class] .woocommerce-Tabs-panel--description h4{font-family:var(--mono)!important;
  font-weight:500!important;font-size:12px!important;letter-spacing:.12em;text-transform:uppercase;
  color:var(--tinta-3)!important;margin:1.5em 0 .5em!important}
html body[class][class][class] .woocommerce-Tabs-panel--description a{color:var(--magenta)!important;
  text-decoration:underline!important;text-decoration-color:color-mix(in srgb,var(--magenta) 40%,transparent)!important;
  text-underline-offset:3px;-webkit-text-fill-color:currentColor!important;background:none!important;
  font-weight:inherit}
html body[class][class][class] .woocommerce-Tabs-panel--description a:hover{
  text-decoration-color:var(--magenta)!important}
html body[class][class][class] .woocommerce-Tabs-panel--description ul,
html body[class][class][class] .woocommerce-Tabs-panel--description ol{padding-left:1.35em!important;
  margin:0 0 1.2em!important}
html body[class][class][class] .woocommerce-Tabs-panel--description li{margin:0 0 .45em!important}
html body[class][class][class] .woocommerce-Tabs-panel--description ul li::marker{color:var(--magenta)}
html body[class][class][class] .woocommerce-Tabs-panel--description ol li::marker{color:var(--magenta);
  font-family:var(--mono);font-size:.85em}
/* tablas: cabecera en monoespaciada y solo líneas horizontales */
html body[class][class][class] .woocommerce-Tabs-panel--description table{width:100%!important;
  border-collapse:collapse!important;border-spacing:0;margin:1.3em 0 1.6em!important;background:none!important;
  border:0!important;font-size:15.5px}
html body[class][class][class] .woocommerce-Tabs-panel--description th{font-family:var(--mono)!important;
  font-size:10.5px!important;letter-spacing:.12em!important;text-transform:uppercase;font-weight:500!important;
  color:var(--tinta-3)!important;text-align:left!important;padding:10px 12px!important;border:0!important;
  border-bottom:1px solid var(--linea-2)!important;background:none!important;vertical-align:bottom;line-height:1.45!important}
html body[class][class][class] .woocommerce-Tabs-panel--description td{font-family:var(--optima)!important;
  font-size:15.5px!important;line-height:1.55!important;color:var(--tinta-2)!important;padding:11px 12px!important;
  border:0!important;border-bottom:1px solid var(--linea)!important;background:none!important;vertical-align:top}
html body[class][class][class] .woocommerce-Tabs-panel--description tr > td:first-child strong{
  font-weight:500}
html body[class][class][class] .woocommerce-Tabs-panel--description tbody tr:hover > td{
  background:var(--carbon-2)!important}
html body[class][class][class] .woocommerce-Tabs-panel--description figure{margin:1.4em 0!important}
html body[class][class][class] .woocommerce-Tabs-panel--description img{border-radius:3px!important;
  border:1px solid var(--linea)!important;box-shadow:none!important;filter:none!important}
html body[class][class][class] .woocommerce-Tabs-panel--description hr{border:0!important;
  border-top:1px solid var(--linea)!important;background:none!important;height:0!important;margin:2em 0!important}
html body[class][class][class] .woocommerce-Tabs-panel--description blockquote{border-left:2px solid var(--magenta)!important;
  margin:1.5em 0!important;padding:.2em 0 .2em 1.2em!important;background:none!important;color:var(--tinta)!important;
  font-style:italic}
html body[class][class][class] .woocommerce-Tabs-panel--description code{font-family:var(--mono);font-size:.88em;
  background:var(--panel);padding:.1em .4em;border-radius:2px;color:var(--tinta)}
/* preguntas frecuentes con marcado propio (omega-3 y hermanas) */
html body[class][class][class] .woocommerce-Tabs-panel--description .faq-item{background:none!important;
  border:0!important;border-top:1px solid var(--linea)!important;border-radius:0!important;box-shadow:none!important;
  padding:6px 0 2px!important;margin:0!important}
html body[class][class][class] .woocommerce-Tabs-panel--description .faq-item h3{margin-top:.6em!important}
@media (max-width:640px){
  html body[class][class][class] .woocommerce-Tabs-panel--description table{display:block!important;
    overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%}
  html body[class][class][class] .woocommerce-Tabs-panel--description p,
  html body[class][class][class] .woocommerce-Tabs-panel--description li{font-size:16.5px!important}
  html body[class][class][class] .woocommerce-Tabs-panel--description h3{font-size:19.5px!important}
}

/* ── información adicional ───────────────────────────────────────────── */
html body[class][class][class] .woocommerce-Tabs-panel--additional_information table.shop_attributes{
  border:0!important;border-collapse:collapse;width:100%;margin:0!important;background:none!important}
html body[class][class][class] table.shop_attributes th{font-family:var(--mono)!important;font-size:10.5px!important;
  letter-spacing:.12em;text-transform:uppercase;font-weight:500!important;color:var(--tinta-3)!important;
  text-align:left!important;padding:12px 16px 12px 0!important;border:0!important;
  border-bottom:1px solid var(--linea)!important;background:none!important;width:180px}
html body[class][class][class] table.shop_attributes td{font-family:var(--optima)!important;font-style:normal!important;
  color:var(--tinta-2)!important;padding:12px 0!important;border:0!important;border-bottom:1px solid var(--linea)!important;
  background:none!important}
html body[class][class][class] table.shop_attributes td p{margin:0!important;padding:0!important;font-style:normal}
html body[class][class][class] table.shop_attributes tr:nth-child(even) th,
html body[class][class][class] table.shop_attributes tr:nth-child(even) td{background:none!important}

/* ── valoraciones ─────────────────────────────────────────────────────── */
html body[class][class][class] #reviews h2,
html body[class][class][class] #reviews .comment-reply-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(22px,2.4vw,28px)!important;color:var(--tinta)!important;margin:0 0 12px!important;display:block}
html body[class][class][class] #reviews p,
html body[class][class][class] #reviews label{color:var(--tinta-2)!important;font-family:var(--optima)!important;
  font-size:15.5px!important}
html body[class][class][class] #reviews label{font-family:var(--mono)!important;font-size:10.5px!important;
  letter-spacing:.12em;text-transform:uppercase;color:var(--tinta-3)!important;display:block;margin:0 0 7px}
html body[class][class][class] #reviews .comment-form-cookies-consent label{display:inline;text-transform:none;
  letter-spacing:0;font-family:var(--optima)!important;font-size:14px!important;color:var(--tinta-2)!important}
html body[class][class][class] #reviews input[type=text],
html body[class][class][class] #reviews input[type=email],
html body[class][class][class] #reviews input[type=url],
html body[class][class][class] #reviews textarea{width:100%;background:var(--carbon)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta)!important;
  font-family:var(--optima)!important;font-size:16px!important;padding:12px 14px!important;box-shadow:none!important}
html body[class][class][class] #reviews input:focus,
html body[class][class][class] #reviews textarea:focus{border-color:var(--magenta)!important;outline:none}
html body[class][class][class] #reviews input[type=checkbox]{accent-color:var(--magenta)}
html body[class][class][class] #reviews p.stars a{color:var(--magenta)!important}
html body[class][class][class] #reviews .form-submit input[type=submit],
html body[class][class][class] #reviews #submit{background:var(--magenta)!important;border:1px solid var(--magenta)!important;
  border-radius:2px!important;color:#fff!important;-webkit-text-fill-color:#fff!important;
  font-family:var(--optima)!important;font-size:16px!important;padding:13px 26px!important;box-shadow:none!important;
  cursor:pointer;background-image:none!important;text-transform:none!important;letter-spacing:0!important}
html body[class][class][class] #reviews #submit:hover{background:#FF3D97!important;border-color:#FF3D97!important}

/* ── «Revisado por» (lo pinta pys-seo-tweaks.php con estilos en línea) ─── */
html body[class][class][class] div.product .pys-revisado-por{margin:clamp(34px,5vw,56px) auto 0!important;
  padding:18px 22px!important;background:var(--carbon)!important;border:1px solid var(--linea)!important;
  border-left:2px solid var(--aqua)!important;border-radius:2px!important;max-width:880px;width:100%;
  justify-self:center;box-shadow:none!important}
html body[class][class][class] div.product .pys-revisado-por p{margin:0!important;color:var(--tinta-2)!important;
  font-family:var(--optima)!important;font-size:15px!important;font-weight:400!important;line-height:1.6}
html body[class][class][class] div.product .pys-revisado-por p:first-child{font-family:var(--mono)!important;
  font-size:10.5px!important;letter-spacing:.14em;text-transform:uppercase;color:var(--tinta-3)!important;
  margin:0 0 8px!important}
html body[class][class][class] div.product .pys-revisado-por p:nth-child(2){color:var(--tinta)!important;
  font-size:17px!important}

/* ── relacionados ─────────────────────────────────────────────────────── */
html body[class][class][class] div.product section.related,
html body[class][class][class] div.product section.up-sells{margin-top:clamp(48px,6vw,88px)!important;
  background:none!important;padding:0!important}
html body[class][class][class] div.product section.related > h2,
html body[class][class][class] div.product section.up-sells > h2{font-family:var(--optima)!important;
  font-weight:400!important;font-size:clamp(24px,3vw,38px)!important;letter-spacing:-.012em!important;
  color:var(--tinta)!important;margin:0 0 clamp(18px,2.4vw,28px)!important;text-align:left!important}

/* ── la cabecera y el pie compartidos ────────────────────────────────── */
/* Algunas fichas traen `body.elementor-page-N a{color:#00E5C4}` y ponían en
   aqua el menú, la marca y los enlaces del pie. Se les devuelve su color. */
html body[class][class][class] header.top .marca{color:var(--tinta)!important}
html body[class][class][class] header.top .menu > a{color:var(--tinta-2)!important}
html body[class][class][class] header.top .menu > a:hover{color:var(--tinta)!important}
html body[class][class][class] header.top .desp li a,
html body[class][class][class] header.top a.icob,
html body[class][class][class] #mnav a{color:var(--tinta-2)!important}
html body[class][class][class] header.top .desp li a:hover,
html body[class][class][class] header.top a.icob:hover{color:var(--tinta)!important}
html body[class][class][class] footer.pie-h26 a{color:var(--tinta-2)!important}
html body[class][class][class] footer.pie-h26 a:hover{color:var(--tinta)!important}
html body[class][class][class] footer.pie-h26 .marca{color:var(--tinta)!important}
CSS;
}
