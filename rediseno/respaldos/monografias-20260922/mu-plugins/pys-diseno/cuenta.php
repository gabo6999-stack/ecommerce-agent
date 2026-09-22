<?php
/**
 * PYS — rediseño de «mi cuenta». Solo diseño: no toca contenido.
 *
 * La página 30 es de Elementor, pero lo único que pinta es el shortcode
 * [woocommerce_my_account] entre dos separadores: acceder y registrarse (o el
 * formulario de «contraseña perdida» en ese endpoint). Aquí no se mueve ni un
 * nodo de esos formularios; solo se re-estilizan encima.
 *
 * Ojo, contenido: el `post_content` de la página 30 guarda pegado un formulario
 * de acceso estático (con un nonce caducado y sin campo de contraseña). NO se
 * ve: como la página está en modo Elementor, el frente pinta `_elementor_data`
 * y no `post_content`. Por eso aquí no hay nada que ocultar.
 *
 * Las reglas llevan `html body.woocommerce-account[class][class][class]`
 * porque el kit de Elementor (post-4.css) estiliza campos y botones de forma
 * global, y LiteSpeed reordena las hojas: se gana por especificidad.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function pys_dis_css_cuenta() {
	$css = <<<'CSS'
/* ── marco de la página ───────────────────────────────────────────── */
@@C #content.site-main{width:min(1200px,100%);max-width:none;margin-inline:auto;
  padding-inline:var(--gutter);padding-block:clamp(30px,4.5vw,64px) clamp(56px,7vw,112px)}
@@C .page-header{margin:0 0 clamp(26px,3.4vw,44px);padding:0;max-width:none}
@@C .page-header .entry-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(34px,4.6vw,58px)!important;line-height:1.04!important;letter-spacing:-.012em;
  color:var(--tinta)!important;margin:0!important;padding:0!important;max-width:none!important;
  text-transform:none!important}
/* rayita de acento bajo el titular, la misma del listado del blog */
@@C .page-header::after{content:"";display:block;width:56px;height:1px;
  background:var(--magenta);margin-top:20px;opacity:.85}
/* el contenedor de Elementor y sus dos separadores metían ~110 px de aire
   entre el titular y los formularios; el ritmo lo lleva ahora el titular */
@@C .page-content,@@C .elementor-30,@@C .elementor-30 .e-con,
@@C .elementor-30 .e-con-inner{padding:0!important;margin:0!important;max-width:none!important;
  gap:0!important;background:none!important}
@@C .elementor-30 .elementor-spacer-inner{height:0!important}

/* ── acceder | registrarse: dos paneles ───────────────────────────── */
@@C #customer_login{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
  gap:clamp(16px,2.4vw,28px);align-items:start;margin:0}
/* el clearfix de .col2-set serían dos celdas fantasma dentro de la retícula */
@@C #customer_login::before,@@C #customer_login::after{content:none!important;display:none!important}
@@C #customer_login > .u-column1,@@C #customer_login > .u-column2{width:auto!important;max-width:none!important;float:none!important;
  margin:0!important;background:var(--carbon);border:1px solid var(--linea);border-radius:3px;
  padding:clamp(22px,3vw,38px)}
@@C #customer_login h2{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(24px,2.4vw,30px)!important;line-height:1.15!important;letter-spacing:-.01em;
  color:var(--tinta)!important;margin:0 0 22px!important;padding:0 0 16px!important;
  border-bottom:1px solid var(--linea);text-transform:none!important}
@@C .woocommerce form.woocommerce-form-login,@@C .woocommerce form.woocommerce-form-register{
  border:0!important;border-radius:0!important;padding:0!important;margin:0!important;
  background:none!important;box-shadow:none!important}

/* contraseña perdida: el formulario solo, en un panel del mismo sistema */
@@C .woocommerce form.woocommerce-ResetPassword{max-width:640px;margin:0!important;
  background:var(--carbon)!important;border:1px solid var(--linea)!important;border-radius:3px!important;
  box-shadow:none!important;padding:clamp(22px,3vw,38px)!important}
@@C .woocommerce form.woocommerce-ResetPassword > p:first-child{color:var(--tinta-2)!important;
  font-size:16.5px!important;line-height:1.65!important;margin:0 0 24px!important;max-width:56ch}
@@C .woocommerce form.woocommerce-ResetPassword .form-row-first,
@@C .woocommerce form.woocommerce-ResetPassword .form-row-last{width:100%!important;float:none!important;
  margin-right:0!important}

/* ── campos: los del buscador de la cabecera y del finalizar compra ── */
@@C .woocommerce form .form-row{margin:0 0 18px!important;padding:0!important}
@@C .woocommerce form .form-row label:not(.woocommerce-form__label-for-checkbox):not(.checkbox){
  display:block;font-family:var(--mono)!important;font-size:10.5px!important;font-weight:400!important;
  letter-spacing:.12em!important;text-transform:uppercase;line-height:1.5!important;
  color:var(--tinta-3)!important;margin:0 0 8px!important}
@@C .woocommerce form .form-row .required{color:var(--magenta)!important;text-decoration:none;border:0}
@@C .woocommerce form .form-row input.input-text,@@C .woocommerce form .form-row textarea,
@@C .woocommerce form .form-row select{width:100%;background:var(--negro)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta)!important;
  -webkit-text-fill-color:var(--tinta)!important;font-family:var(--optima)!important;
  font-size:16px!important;line-height:1.4!important;padding:12px 14px!important;
  min-height:48px;height:auto!important;box-shadow:none!important;outline:none;
  transition:border-color .2s}
@@C .woocommerce form .form-row input.input-text:hover{border-color:var(--tinta-3)!important}
@@C .woocommerce form .form-row input.input-text:focus,@@C .woocommerce form .form-row textarea:focus,
@@C .woocommerce form .form-row select:focus{border-color:var(--magenta)!important}
@@C .woocommerce form .form-row input::placeholder{color:var(--tinta-3)}
/* el autocompletado de Chrome pinta los campos de azul claro */
@@C .woocommerce form .form-row input.input-text:-webkit-autofill{
  -webkit-box-shadow:0 0 0 60px var(--negro) inset!important;-webkit-text-fill-color:var(--tinta)!important;
  caret-color:var(--tinta)}
@@C .woocommerce form .form-row select option{color:#111;background:#fff}
/* ver contraseña: el ojo es un SVG negro de WooCommerce; sobre el campo oscuro
   se invierte en lugar de redibujarlo */
@@C .woocommerce form .password-input input.input-text{padding-right:48px!important}
@@C .woocommerce form .show-password-input{right:14px!important;background:none!important;
  border:0!important;box-shadow:none!important;opacity:.6;transition:opacity .2s}
@@C .woocommerce form .show-password-input:hover{opacity:1}
@@C .woocommerce form .show-password-input::before,
@@C .woocommerce form .show-password-input::after{filter:invert(1)}

/* casilla «Recuérdame»: lleva su texto al lado, sin versalitas */
@@C .woocommerce form .woocommerce-form__label-for-checkbox{display:inline-flex!important;
  align-items:center;gap:9px;font-family:var(--optima)!important;font-size:15.5px!important;
  letter-spacing:0!important;text-transform:none!important;line-height:1.4!important;
  color:var(--tinta-2)!important;margin:0!important;cursor:pointer}
@@C .woocommerce form .woocommerce-form__label-for-checkbox span{color:inherit!important;font:inherit!important}
@@C .woocommerce form input[type=checkbox]{accent-color:var(--magenta);width:17px;height:17px;margin:0!important}
/* fila de acceso: casilla arriba, botón a todo lo ancho debajo */
@@C .woocommerce form.woocommerce-form-login > p.form-row:not(.woocommerce-form-row){display:flex;
  flex-direction:column;align-items:flex-start;gap:18px;margin:4px 0 0!important}

/* textos de ayuda y aviso de privacidad */
@@C .woocommerce form.woocommerce-form-register > p:not(.form-row){color:var(--tinta-2)!important;
  font-size:15px!important;line-height:1.6!important;margin:0 0 14px!important}
@@C .woocommerce .woocommerce-privacy-policy-text,@@C .woocommerce .woocommerce-privacy-policy-text p{
  color:var(--tinta-3)!important;font-size:13.5px!important;line-height:1.6!important}
@@C .woocommerce .woocommerce-privacy-policy-text p{margin:0 0 20px!important}
@@C .woocommerce .woocommerce-privacy-policy-text a{color:var(--magenta)!important}

/* ── botones: el de enviar, primario magenta como .btn.pri ──────────── */
@@C .woocommerce form button[type=submit].button,@@C .woocommerce form button[type=submit].woocommerce-button,
@@C .woocommerce form button[type=submit].woocommerce-Button{display:inline-flex!important;
  align-items:center;justify-content:center;width:100%;float:none!important;margin:0!important;
  background:var(--magenta)!important;background-image:none!important;border:1px solid var(--magenta)!important;
  border-radius:2px!important;color:#fff!important;-webkit-text-fill-color:#fff!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important;
  font-family:var(--optima)!important;font-size:16px!important;font-weight:400!important;
  letter-spacing:0!important;text-transform:none!important;line-height:1.3!important;
  padding:14px 26px!important;height:auto!important;min-height:0!important;box-shadow:none!important;
  cursor:pointer;transition:background .2s,border-color .2s}
@@C .woocommerce form button[type=submit].button:hover,@@C .woocommerce form button[type=submit].woocommerce-button:hover,
@@C .woocommerce form button[type=submit].woocommerce-Button:hover{background:#FF3D97!important;
  border-color:#FF3D97!important;color:#fff!important}
/* el resto de botones de la cuenta (con sesión) va perfilado, como en el carrito */
@@C .woocommerce a.button,@@C .woocommerce button.button:not([type=submit]),@@C .woocommerce input.button{
  background:transparent!important;background-image:none!important;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;color:var(--tinta-2)!important;-webkit-text-fill-color:currentColor!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important;
  font-family:var(--mono)!important;font-size:11.5px!important;font-weight:400!important;
  letter-spacing:.07em;text-transform:none!important;padding:12px 16px!important;box-shadow:none!important;
  line-height:1.3!important;height:auto!important;min-height:0!important}
@@C .woocommerce a.button:hover,@@C .woocommerce input.button:hover{border-color:var(--tinta-3)!important;
  color:var(--tinta)!important}

/* ¿olvidaste la contraseña? */
@@C .woocommerce .woocommerce-LostPassword{margin:22px 0 0!important;padding:16px 0 0!important;
  border-top:1px solid var(--linea)}
@@C .woocommerce .woocommerce-LostPassword a{font-family:var(--mono)!important;font-size:12px!important;
  letter-spacing:.05em;color:var(--magenta)!important;-webkit-text-fill-color:currentColor!important;
  text-decoration:none}
@@C .woocommerce .woocommerce-LostPassword a:hover{text-decoration:underline;text-underline-offset:3px}

@media (max-width:760px){
  @@C #customer_login{grid-template-columns:1fr}
}
CSS;
	return str_replace( '@@C', 'html body.woocommerce-account[class][class][class]', $css );
}
