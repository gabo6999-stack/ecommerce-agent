<?php
/**
 * PYS — rediseño de las landings comerciales hechas con Elementor. Solo
 * diseño: no toca contenido.
 *
 *   1551 /peptidos-mexico/                     listado de péptidos (tarjetas a mano)
 *   1729 /tirzepatida-en-mexico/
 *   1750 /semaglutida-en-mexico/
 *   2040 /calculadora-de-dosis-de-peptidos/    calculadora en JS
 *
 * Las cuatro son UN widget HTML de Elementor con su propio marcado (`.pys-*`,
 * `.pys-tz-*`, `.pys-sema-*`, `.pys-calc`) y su hoja vieja —degradados,
 * radios de 24-42 px, vidrio con blur, píldoras con brillo—, más una regla del
 * Customizer que pinta la sección raíz con
 * `html body[class] #content.site-main .elementor-widget-html > … > section`
 * (1,4,3) !important. Aquí se re-estiliza todo ese marcado con el sistema
 * «laboratorio oscuro» sin cambiar una sola etiqueta.
 *
 * ÁMBITO: el cargador aplica esta hoja con el mismo predicado que la de las
 * páginas Elementor informativas, así que NINGUNA regla va sin acotar: todas
 * empiezan por la clase `page-id-<id>` del <body> (fichas {A}, {P}, {T}, {S},
 * {C}, que se sustituyen al final). Con `[class][class]` quedan en 0,3,2.
 *
 * Lo único que se oculta:
 *   - las capas decorativas vacías del widget viejo (retícula, orbes y
 *     resplandores animados): son <div> sin contenido; el fondo ya lo pone la
 *     capa global.
 *   - el <h2> «Calculadora de Dosis de Péptidos» dentro de la calculadora: es
 *     el mismo texto que el <h1> de la página, justo encima (duplicado real).
 * Las animaciones de aparición (`*-reveal`) se dejan visibles de entrada: el
 * contenido no depende de que un script llegue a añadir `is-visible`.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function pys_dis_css_landings() {
	$css = <<<'CSS'
/* ═════════════════════════════════════════════════════════════════════
   BASE COMÚN
   ═════════════════════════════════════════════════════════════════════ */

/* La columna es la misma de la cabecera (1320 px con el gutter del sitio), no
   la caja de 1140 px de Elementor: así el contenido arranca a plomo con el
   logo. */
{A} .elementor > .e-con.e-parent{padding:0!important;min-height:0!important;
  --padding-top:0px;--padding-bottom:0px;--padding-left:0px;--padding-right:0px}
{A} .elementor > .e-con.e-parent > .e-con-inner{width:min(1320px,100%)!important;max-width:none!important;
  padding:0 var(--gutter)!important;margin-inline:auto!important}

/* Sección raíz de cada widget: fuera el panel oscuro con degradados (el del
   Customizer lleva un id y !important, de ahí `#content.site-main`), fuera su
   `overflow:hidden` (recortaba las bandas a sangre) y la tipografía Inter. */
{A} #content.site-main .elementor-widget-html > .elementor-widget-container > section,
{A} .pys-section-root,{A} .pys-sema-root{background:none!important;background-image:none!important;
  padding:0!important;overflow:visible!important;font-family:var(--optima)!important;color:var(--tinta)!important}
/* `body.elementor-page-ID … .elementor-widget-container{background:#17191B}`
   (y un degradado en la de semaglutida): era la caja gris de 1140 px */
{A} .elementor-widget-html > .elementor-widget-container{background:none!important;background-image:none!important}
{P} .pys-bg-grid,{T} .pys-tz-grid-bg,{T} .pys-tz-glow,{S} .pys-sema-bgline,{S} .pys-sema-orb{display:none!important}
{P} .pys-wrap,{T} .pys-tz-wrap,{S} .pys-sema-wrap{width:100%!important;max-width:none!important;margin:0!important}
{T} .pys-tz-reveal,{S} .pys-sema-reveal{opacity:1!important;transform:none!important}

/* ritmo vertical: la base le pone relleno a TODA sección, anidadas incluidas */
{P} .pys-section,{T} .pys-tz-section,{T} .pys-tz-final,{S} .pys-sema-section,{S} .pys-sema-final{
  padding:clamp(44px,6vw,96px) 0!important;background:none!important;background-image:none!important}
{P} .pys-hero,{T} .pys-tz-hero,{S} .pys-sema-hero{padding:clamp(26px,4vw,56px) 0 clamp(16px,2.5vw,36px)!important;
  background:none!important}
/* Las secciones «suaves» pasan a banda de carbón a sangre con filete arriba y
   abajo, como la franja de confianza de la portada. Va con border-image, que
   pinta fuera de la caja sin crear desborde horizontal. */
{T} .pys-tz-section-soft,{S} .pys-sema-section-soft{background:none!important;
  border-image:linear-gradient(to bottom,var(--linea) 1px,var(--carbon) 1px,var(--carbon) calc(100% - 1px),var(--linea) calc(100% - 1px)) 0 fill / 0 / 0 100vmax}

/* ── ladillos (la antigua píldora con punto brillante) ─────────────── */
{P} .pys-badge,{P} .pys-tag,{T} .pys-tz-badge,{T} .pys-tz-tag,{S} .pys-sema-badge,{S} .pys-sema-tag{
  display:inline-flex!important;align-items:center;gap:9px!important;padding:0!important;margin:0 0 14px!important;
  border:0!important;border-radius:0!important;background:none!important;box-shadow:none!important;
  backdrop-filter:none!important;-webkit-backdrop-filter:none!important;font-family:var(--optima)!important;
  font-size:11px!important;font-weight:400!important;letter-spacing:.22em!important;text-transform:uppercase;
  line-height:1.4!important;color:var(--tinta-3)!important}
{P} .pys-badge::before,{P} .pys-tag::before,{T} .pys-tz-badge::before,{T} .pys-tz-tag::before,
{S} .pys-sema-badge::before,{S} .pys-sema-tag::before{width:6px!important;height:6px!important;flex:none;
  border-radius:50%!important;background:var(--aqua)!important;box-shadow:none!important}

/* ── titulares ─────────────────────────────────────────────────────── */
{P} .pys-title,{T} .pys-tz-title,{S} .pys-sema-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(34px,4.6vw,64px)!important;line-height:1.04!important;letter-spacing:-.014em!important;
  color:var(--tinta)!important;max-width:16ch;margin:0 0 20px!important}
/* la palabra resaltada llevaba degradado recortado: magenta sólido, como la
   portada, devolviendo el relleno del texto para que no quede invisible */
{P} .pys-title span,{T} .pys-tz-title span,{S} .pys-sema-title span{background:none!important;
  background-image:none!important;-webkit-background-clip:border-box!important;background-clip:border-box!important;
  -webkit-text-fill-color:var(--magenta)!important;color:var(--magenta)!important}
{P} .pys-section-title,{P} .pys-editorial h2,{T} .pys-tz-section-title,{T} .pys-tz-editorial h2,{T} .pys-tz-final h2,
{S} .pys-sema-section-title,{S} .pys-sema-final h2{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(28px,3.6vw,48px)!important;line-height:1.08!important;letter-spacing:-.012em!important;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;max-width:24ch;margin:0!important}
{P} .pys-head,{T} .pys-tz-head,{S} .pys-sema-head{max-width:860px!important;margin-bottom:clamp(24px,3.2vw,44px)!important}

/* ── prosa de los bloques ──────────────────────────────────────────── */
{P} .pys-copy,{P} .pys-section-copy,{P} .pys-editorial p,{T} .pys-tz-copy,{T} .pys-tz-section-copy,
{T} .pys-tz-editorial p,{T} .pys-tz-final p,{S} .pys-sema-copy,{S} .pys-sema-section-copy,{S} .pys-sema-final p{
  font-family:var(--optima)!important;font-size:17px!important;line-height:1.68!important;color:var(--tinta-2)!important;
  max-width:62ch;margin:14px 0 0!important}
{P} .pys-copy,{T} .pys-tz-copy,{S} .pys-sema-copy{font-size:clamp(16.5px,1.3vw,18.5px)!important;max-width:50ch}
{P} .pys-copy strong,{P} .pys-section-copy strong,{T} .pys-tz-copy strong,{T} .pys-tz-section-copy strong,
{S} .pys-sema-copy strong,{S} .pys-sema-section-copy strong{color:var(--tinta)!important;font-weight:600}

/* ── botones: los de la base (.btn / .btn.pri) ─────────────────────── */
{P} .pys-actions,{T} .pys-tz-actions,{S} .pys-sema-actions{gap:12px!important;margin-top:28px!important}
{P} .pys-btn,{T} .pys-tz-btn,{S} .pys-sema-btn{display:inline-flex!important;align-items:center;justify-content:center;
  gap:9px!important;min-height:0!important;padding:14px 26px!important;border-radius:2px!important;
  border:1px solid var(--linea-2)!important;background:transparent!important;background-image:none!important;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;font-family:var(--optima)!important;
  font-size:16px!important;font-weight:400!important;letter-spacing:0!important;text-transform:none!important;
  line-height:1.2!important;box-shadow:none!important;backdrop-filter:none!important;filter:none!important;
  transform:none!important;transition:border-color .2s,background .2s!important;cursor:pointer}
{P} .pys-btn:hover,{T} .pys-tz-btn:hover,{S} .pys-sema-btn:hover{border-color:var(--tinta)!important;
  transform:none!important;filter:none!important}
{P} .pys-btn-primary,{T} .pys-tz-btn-primary,{S} .pys-sema-btn-primary{background:var(--magenta)!important;
  border-color:var(--magenta)!important;color:#fff!important}
{P} .pys-btn-primary:hover,{T} .pys-tz-btn-primary:hover,{S} .pys-sema-btn-primary:hover{background:#FF3D97!important;
  border-color:#FF3D97!important}
{T} .pys-tz-btn svg,{S} .pys-sema-btn svg{width:17px!important;height:17px!important;flex:0 0 17px!important}
{T} .pys-tz-btn-wa svg,{S} .pys-sema-btn-wa svg{color:var(--aqua)}

/* ── sellos (puntos clave del héroe) ───────────────────────────────── */
{T} .pys-tz-keypoints,{S} .pys-sema-quick{display:flex!important;flex-wrap:wrap;gap:9px!important;margin-top:24px!important;
  max-width:none!important}
{T} .pys-tz-keypoint,{S} .pys-sema-quick span{display:inline-flex!important;align-items:center;gap:8px!important;
  min-height:0!important;padding:7px 12px!important;border:1px solid var(--linea-2)!important;border-radius:2px!important;
  background:transparent!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;
  font-family:var(--mono)!important;font-size:11px!important;font-weight:400!important;letter-spacing:.05em!important;
  line-height:1.35!important;color:var(--tinta-2)!important}
{T} .pys-tz-keypoint i,{S} .pys-sema-quick i{width:6px!important;height:6px!important;flex:0 0 6px!important;
  border-radius:50%!important;background:var(--aqua)!important;box-shadow:none!important}

/* ── visor del héroe ───────────────────────────────────────────────── */
{P} .pys-hero-grid,{T} .pys-tz-hero-grid,{S} .pys-sema-hero-grid{gap:clamp(24px,5vw,72px)!important}
{P} .pys-visual,{T} .pys-tz-visual,{S} .pys-sema-visual{border-radius:3px!important;background:var(--carbon-2)!important;
  background-image:none!important;border:1px solid var(--linea-2)!important;
  box-shadow:0 40px 90px -40px rgba(0,0,0,.9)!important;min-height:clamp(440px,44vw,600px)!important}
/* el marco interior se queda, como el de la vitrina de la portada */
{P} .pys-visual::before,{T} .pys-tz-visual::before,{S} .pys-sema-visual::before{inset:10px!important;
  border-radius:2px!important;border:1px solid var(--linea)!important;background:none!important}
{S} .pys-sema-visual::after{display:none!important}
{S} .pys-sema-visual::before{border-color:rgba(8,18,15,.14)!important}
/* la imagen de tirzepatida iba en su proporción anclada abajo: con el visor
   más bajo se salía por arriba. Ahora ocupa el visor y se ve entera. */
{T} .pys-tz-hero-img{animation:none!important;width:100%!important;max-width:none!important;height:100%!important;
  object-fit:contain;object-position:50% 100%}
/* la foto de semaglutida debía cubrir el visor (`inset:0` + `cover`) pero el
   `height:auto` de la base la dejaba en su proporción, con medio visor vacío */
{S} .pys-sema-hero-img{animation:none!important;height:100%!important;transform:none!important;filter:none!important}
{P} .pys-watermark,{T} .pys-tz-watermark{font-family:var(--optima)!important;color:rgba(238,246,243,.05)!important;
  letter-spacing:-.04em!important}
{P} .pys-floating,{T} .pys-tz-floating,{S} .pys-sema-visual-card{border-radius:3px!important;
  background:rgba(10,18,16,.92)!important;border:1px solid var(--linea-2)!important;box-shadow:none!important;
  backdrop-filter:none!important;-webkit-backdrop-filter:none!important;padding:18px 20px!important}
{P} .pys-floating h3,{T} .pys-tz-floating h3,{S} .pys-sema-visual-card h3{font-family:var(--mono)!important;
  font-size:11px!important;font-weight:500!important;letter-spacing:.12em!important;text-transform:uppercase;
  line-height:1.45!important;color:var(--aqua)!important;margin:0 0 10px!important}
{P} .pys-floating p,{T} .pys-tz-floating p,{S} .pys-sema-visual-card p{font-family:var(--optima)!important;
  font-size:15px!important;line-height:1.6!important;color:var(--tinta-2)!important;margin:0!important}
{T} .pys-tz-floating a,{S} .pys-sema-visual-card a{color:var(--magenta)!important;text-decoration:underline!important;
  text-underline-offset:3px;text-decoration-color:color-mix(in srgb,var(--magenta) 45%,transparent)!important}
{P} .pys-visual .pys-pill,{T} .pys-tz-pill{display:inline-flex!important;align-items:center;justify-content:center;
  gap:8px!important;padding:8px 12px!important;border-radius:2px!important;background:rgba(5,9,8,.86)!important;
  border:1px solid var(--linea-2)!important;box-shadow:none!important;font-family:var(--mono)!important;
  font-size:10.5px!important;font-weight:500!important;letter-spacing:.12em!important;color:var(--aqua)!important}
{T} .pys-tz-pill::before{width:6px!important;height:6px!important;background:var(--aqua)!important;box-shadow:none!important}

/* ── celdas: rejilla de filetes, como las categorías de la portada ─── */
{P} .pys-grid-cards,{T} .pys-tz-two,{T} .pys-tz-grid-3,{T} .pys-tz-grid-4,{S} .pys-sema-compact-grid,{S} .pys-sema-props{
  gap:1px!important;background:var(--linea)!important;border:1px solid var(--linea)!important;border-radius:3px!important;
  overflow:hidden}
{P} .pys-card,{T} .pys-tz-card,{T} .pys-tz-info-card,{T} .pys-tz-metric,{S} .pys-sema-panel,{S} .pys-sema-prop{
  background:var(--carbon)!important;background-image:none!important;border:0!important;border-radius:0!important;
  box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;
  padding:clamp(20px,2.4vw,30px)!important;min-height:0!important;transform:none!important;
  transition:background .22s!important}
{T} .pys-tz-section-soft .pys-tz-metric,{T} .pys-tz-section-soft .pys-tz-info-card{background:var(--carbon-2)!important}
{P} .pys-card:hover,{T} .pys-tz-card:hover,{T} .pys-tz-info-card:hover,{T} .pys-tz-metric:hover,
{S} .pys-sema-panel:hover,{S} .pys-sema-prop:hover{background:var(--panel)!important;transform:none!important;
  box-shadow:none!important}
{T} .pys-tz-card::before,{T} .pys-tz-card::after,{T} .pys-tz-info-card::before,{T} .pys-tz-info-card::after,
{T} .pys-tz-metric::before,{T} .pys-tz-metric::after,{S} .pys-sema-panel::before,{S} .pys-sema-panel::after,
{S} .pys-sema-prop::before,{S} .pys-sema-prop::after{display:none!important}
{P} .pys-card h3,{T} .pys-tz-card h3,{T} .pys-tz-info-card h3,{T} .pys-tz-path-item h3,{S} .pys-sema-panel h3{
  font-family:var(--optima)!important;font-weight:400!important;font-size:21px!important;line-height:1.25!important;
  letter-spacing:-.01em!important;color:var(--tinta)!important;margin:0 0 10px!important}
{P} .pys-card p,{T} .pys-tz-card p,{T} .pys-tz-info-card p,{T} .pys-tz-path-item p,{S} .pys-sema-panel p{
  font-family:var(--optima)!important;font-size:16px!important;line-height:1.62!important;color:var(--tinta-2)!important;
  margin:0!important}
{S} .pys-sema-prop strong{font-family:var(--mono)!important;font-size:11px!important;font-weight:500!important;
  letter-spacing:.1em!important;text-transform:uppercase;line-height:1.45!important;color:var(--aqua)!important;
  margin:0 0 10px!important}
{S} .pys-sema-prop span{font-family:var(--optima)!important;font-size:16px!important;line-height:1.6!important;
  color:var(--tinta-2)!important}

/* números de orden: mono magenta, como los pasos de la portada */
{P} .pys-number,{T} .pys-tz-path-num{display:block!important;width:auto!important;height:auto!important;
  border-radius:0!important;background:none!important;box-shadow:none!important;font-family:var(--mono)!important;
  font-size:11.5px!important;font-weight:500!important;letter-spacing:.16em!important;line-height:1.4!important;
  color:var(--magenta)!important;margin:0 0 14px!important}
{T} .pys-tz-metric strong{font-family:var(--mono)!important;font-size:11.5px!important;font-weight:500!important;
  letter-spacing:.16em!important;line-height:1.4!important;color:var(--magenta)!important;margin:0 0 12px!important}
{T} .pys-tz-metric span{font-family:var(--optima)!important;font-size:16.5px!important;line-height:1.55!important;
  color:var(--tinta)!important}

/* iconos: la baldosa con degradado y brillo pasa a casilla con trazo aqua */
{T} .pys-tz-icon,{S} .pys-sema-icon{width:44px!important;height:44px!important;border-radius:2px!important;
  background:transparent!important;background-image:none!important;border:1px solid var(--linea-2)!important;
  box-shadow:none!important;color:var(--aqua)!important;margin-bottom:18px!important}
{T} .pys-tz-icon::after,{S} .pys-sema-icon::after{display:none!important;animation:none!important}
{T} .pys-tz-icon svg,{S} .pys-sema-icon svg{width:21px!important;height:21px!important;stroke-width:1.6!important}

/* ── recuadros editorial y de cierre ───────────────────────────────── */
{P} .pys-editorial,{T} .pys-tz-editorial,{T} .pys-tz-final-box,{S} .pys-sema-final-box{border-radius:3px!important;
  background:var(--carbon)!important;background-image:none!important;border:1px solid var(--linea-2)!important;
  box-shadow:none!important;padding:clamp(26px,5vw,64px)!important}
{T} .pys-tz-editorial::before,{T} .pys-tz-editorial::after,{T} .pys-tz-final-box::before,{T} .pys-tz-final-box::after,
{S} .pys-sema-final-box::before,{S} .pys-sema-final-box::after{display:none!important}
{T} .pys-tz-final-grid,{S} .pys-sema-final-grid{gap:clamp(24px,4vw,56px)!important}
{T} .pys-tz-contact-card,{S} .pys-sema-mini-card{border-radius:3px!important;background:var(--carbon-2)!important;
  border:1px solid var(--linea)!important;box-shadow:none!important;backdrop-filter:none!important;
  -webkit-backdrop-filter:none!important;padding:16px 18px!important}
{T} .pys-tz-contact-card strong,{S} .pys-sema-mini-card strong{font-family:var(--mono)!important;font-size:10.5px!important;
  font-weight:500!important;letter-spacing:.12em!important;text-transform:uppercase;color:var(--tinta-3)!important;
  margin:0 0 7px!important}
{T} .pys-tz-contact-card span,{S} .pys-sema-mini-card span{font-family:var(--optima)!important;font-size:16px!important;
  line-height:1.55!important;color:var(--tinta)!important}
/* el primero es el teléfono: cifra, así que mono aqua */
{T} .pys-tz-contact-card:first-child span,{S} .pys-sema-mini-card:first-child span{font-family:var(--mono)!important;
  font-size:15px!important;color:var(--aqua)!important;font-variant-numeric:tabular-nums}
{T} .pys-tz-note{font-family:var(--mono)!important;font-size:11px!important;letter-spacing:.04em!important;
  line-height:1.6!important;color:var(--tinta-3)!important}

/* ── producto destacado: como el «destacado» de la portada ─────────── */
{T} .pys-tz-product-wrap,{S} .pys-sema-product-row{gap:clamp(24px,4.5vw,70px)!important}
{T} .pys-tz-product-card,{S} .pys-sema-product-card{gap:0!important;border-radius:3px!important;background:var(--carbon-2)!important;
  color:var(--tinta)!important;border:1px solid var(--linea-2)!important;box-shadow:none!important;transform:none!important;
  transition:border-color .22s!important}
{T} .pys-tz-product-card:hover,{S} .pys-sema-product-card:hover{border-color:color-mix(in srgb,var(--magenta) 55%,transparent)!important;
  transform:none!important;box-shadow:none!important}
/* las dos fotos de producto son cuadradas sobre blanco: caja blanca, sin la
   luz de colores de antes, para que no se le vea el borde a la imagen */
{T} .pys-tz-product-image,{S} .pys-sema-product-img{background:#fff!important;background-image:none!important;
  padding:18px!important;min-height:250px!important;border-right:1px solid var(--linea)}
{T} .pys-tz-product-image img,{S} .pys-sema-product-img img{filter:none!important;
  transition:transform .5s cubic-bezier(.22,.61,.36,1)!important}
{T} .pys-tz-product-card:hover img,{S} .pys-sema-product-card:hover img{transform:scale(1.035)!important}
{T} .pys-tz-product-body,{S} .pys-sema-product-body{padding:24px 26px!important}
{T} .pys-tz-product-label,{S} .pys-sema-product-label{padding:0!important;border-radius:0!important;background:none!important;
  font-family:var(--mono)!important;font-size:10.5px!important;font-weight:500!important;letter-spacing:.1em!important;
  color:var(--aqua)!important;margin-bottom:12px!important}
{T} .pys-tz-product-body h3,{S} .pys-sema-product-body h3{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(24px,2.2vw,30px)!important;line-height:1.1!important;letter-spacing:-.012em!important;
  color:var(--tinta)!important;margin:0 0 10px!important}
{T} .pys-tz-product-body p,{S} .pys-sema-product-body p{font-family:var(--optima)!important;font-size:15.5px!important;
  line-height:1.6!important;color:var(--tinta-2)!important;margin:0 0 18px!important}
{T} .pys-tz-product-link,{S} .pys-sema-product-link{font-family:var(--mono)!important;font-size:12px!important;
  font-weight:400!important;letter-spacing:.05em!important;text-transform:none!important;color:var(--magenta)!important}
{T} .pys-tz-product-link::after,{S} .pys-sema-product-link::after{color:var(--magenta)!important;font-size:13px!important}

/* ── preguntas frecuentes: como las de la portada ──────────────────── */
{T} .pys-tz-faq,{S} .pys-sema-accordion{gap:0!important;border-top:1px solid var(--linea)}
{T} .pys-tz-faq-item,{S} .pys-sema-faq-item{border-radius:0!important;background:none!important;background-image:none!important;
  border:0!important;border-bottom:1px solid var(--linea)!important;box-shadow:none!important}
{T} .pys-tz-faq-btn,{S} .pys-sema-faq-btn{white-space:normal!important;text-align:left!important;justify-content:flex-start!important;align-items:baseline!important;gap:14px!important;
  padding:18px 0!important;background:none!important;font-family:var(--optima)!important;font-size:18px!important;
  font-weight:400!important;letter-spacing:0!important;line-height:1.35!important;color:var(--tinta)!important;
  transition:color .2s}
{T} .pys-tz-faq-btn:hover,{S} .pys-sema-faq-btn:hover{color:var(--magenta)!important}
{T} .pys-tz-faq-icon,{S} .pys-sema-faq-plus{order:-1;display:inline-block!important;width:auto!important;height:auto!important;
  flex:none!important;border-radius:0!important;background:none!important;color:var(--magenta)!important;
  transform:none!important}
{T} .pys-tz-faq-icon::before,{S} .pys-sema-faq-plus::before{content:"+"!important;font-family:var(--mono)!important;
  font-size:15px!important;font-weight:400!important;line-height:1!important}
{T} .pys-tz-faq-item.is-open .pys-tz-faq-icon,{S} .pys-sema-faq-item.is-open .pys-sema-faq-plus{transform:none!important;
  background:none!important;color:var(--magenta)!important}
{T} .pys-tz-faq-item.is-open .pys-tz-faq-icon::before,{S} .pys-sema-faq-item.is-open .pys-sema-faq-plus::before{
  content:"\2212"!important}
{T} .pys-tz-faq-panel-inner,{S} .pys-sema-faq-inner{padding:0 0 18px 28px!important;font-family:var(--optima)!important;
  font-size:16px!important;line-height:1.65!important;color:var(--tinta-2)!important;max-width:66ch}
@media (min-width:861px){
  {T} .pys-tz-wrap:has(> .pys-tz-faq),{S} .pys-sema-wrap:has(> .pys-sema-accordion){display:grid;
    grid-template-columns:.8fr 1.2fr;gap:clamp(24px,4vw,64px);align-items:start}
  {T} .pys-tz-wrap:has(> .pys-tz-faq) > .pys-tz-head,{S} .pys-sema-wrap:has(> .pys-sema-accordion) > .pys-sema-head{
    margin-bottom:0!important}
}

/* ═════════════════════════════════════════════════════════════════════
   1551 · /peptidos-mexico/
   ═════════════════════════════════════════════════════════════════════ */
/* la línea suelta de arriba del héroe */
{P} .elementor-widget-container > p:first-child{margin:0!important;padding-top:clamp(22px,3vw,34px);
  max-width:70ch;font-size:15.5px;line-height:1.6;color:var(--tinta-3)}
{P} .elementor-widget-container > p:first-child strong{color:var(--tinta-2);font-weight:400}
{P} .pys-featured-image{filter:drop-shadow(0 30px 50px rgba(0,0,0,.5))!important}

/* Listado: la tarjeta del catálogo y de la portada (`.tarjeta`), solo con CSS.
   Las imágenes son las del documento de Elementor: cuadradas sobre #EDEDEA,
   así que la caja lleva ese mismo fondo y la imagen entera (`contain`). */
{P} .pys-products-grid{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:clamp(12px,1.4vw,20px)!important}
{P} .pys-product-card{position:relative;display:flex!important;flex-direction:column!important;min-height:100%;
  border:1px solid var(--linea)!important;border-radius:3px!important;overflow:hidden;background:var(--carbon)!important;
  color:var(--tinta)!important;box-shadow:none!important;transform:none!important;
  transition:border-color .25s,box-shadow .25s!important}
{P} .pys-product-card:hover{border-color:var(--linea-2)!important;box-shadow:0 22px 50px -26px rgba(0,0,0,.95)!important;
  transform:none!important}
{P} .pys-product-image{display:block!important;aspect-ratio:1/1;height:auto!important;min-height:0!important;padding:0!important;
  overflow:hidden;background:#EDEDEA!important;background-image:none!important}
{P} .pys-product-image img{display:block;width:100%!important;height:100%!important;max-width:none!important;
  max-height:none!important;object-fit:contain;filter:none!important;
  transition:transform .5s cubic-bezier(.22,.61,.36,1)!important}
{P} .pys-product-card:hover .pys-product-image img{transform:scale(1.045)!important}
{P} .pys-product-body{display:flex!important;flex-direction:column;flex:1;padding:15px 16px 0!important}
/* la categoría va encima del nombre, en mono como el SKU de la tarjeta: sobre
   la foto tapaba el nombre que la propia imagen lleva impreso */
{P} .pys-product-label{position:static!important;display:block!important;width:auto!important;max-width:none!important;
  margin:0 0 7px!important;padding:0!important;border:0!important;border-radius:0!important;background:none!important;
  color:var(--tinta-3)!important;font-family:var(--mono)!important;font-size:10px!important;font-weight:400!important;
  letter-spacing:.09em!important;line-height:1.4!important}
{P} .pys-product-card h3{font-family:var(--optima)!important;font-size:17.5px!important;font-weight:400!important;
  line-height:1.22!important;letter-spacing:-.012em!important;color:var(--tinta)!important;margin:0 0 14px!important;
  overflow-wrap:anywhere;transition:color .2s}
{P} .pys-product-card:hover h3{color:var(--magenta)!important}
/* el precio hace de fila `.compra` */
{P} .pys-product-price{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:auto -16px 0!important;
  padding:13px 16px!important;border-top:1px solid var(--linea);background:var(--carbon-2);font-family:var(--mono)!important;
  font-size:15px!important;font-weight:400!important;color:var(--tinta)!important;font-variant-numeric:tabular-nums}
{P} .pys-product-price::after{content:"\2192";font-size:14px;color:var(--magenta);transition:transform .2s}
{P} .pys-product-card:hover .pys-product-price::after{transform:translateX(3px)}

/* prosa suelta de después del widget */
{P} .elementor-widget-container > h2,{C} .elementor-widget-container > h2{font-family:var(--optima)!important;
  font-weight:400!important;font-size:clamp(24px,2.6vw,32px)!important;line-height:1.15!important;letter-spacing:-.01em;
  color:var(--tinta)!important;max-width:68ch;margin:1.6em 0 .6em!important;padding-top:.9em;border-top:1px solid var(--linea)}
{P} .elementor-widget-container > p:not(:first-child),{C} .elementor-widget-container > p{font-size:17px!important;
  line-height:1.7!important;color:var(--tinta-2)!important;max-width:68ch;margin:0 0 1em!important}
{P} .elementor-widget-container > p strong,{C} .elementor-widget-container > p strong{color:var(--tinta)!important;font-weight:600}
{P} .elementor-widget-container > ul{max-width:68ch;margin:0 0 1.2em!important;padding-left:1.35em!important;
  font-size:17px;line-height:1.7;color:var(--tinta-2)}
{P} .elementor-widget-container > ul li{margin-bottom:.35em}
{P} .elementor-widget-container > ul li::marker{color:var(--magenta)}
{P} .elementor-widget-container > p a,{P} .elementor-widget-container > ul a,{C} .elementor-widget-container > p a{
  color:var(--magenta)!important;text-decoration:underline;text-underline-offset:3px;
  text-decoration-color:color-mix(in srgb,var(--magenta) 40%,transparent)}
{P} .elementor-widget-container > p a:hover,{P} .elementor-widget-container > ul a:hover,
{C} .elementor-widget-container > p a:hover{text-decoration-color:var(--magenta)}
{P} .elementor-widget-html > .elementor-widget-container,{C} .elementor-widget-html > .elementor-widget-container{
  padding-bottom:clamp(40px,5vw,80px)!important}
{P} .elementor-widget-container > :last-child,{C} .elementor-widget-container > :last-child{margin-bottom:0!important}

/* ═════════════════════════════════════════════════════════════════════
   1729 · /tirzepatida-en-mexico/  (lo propio; lo común ya está arriba)
   ═════════════════════════════════════════════════════════════════════ */
/* mecanismo: lista numerada con filetes, no cuatro tarjetas flotantes */
{T} .pys-tz-path{gap:0!important;border-top:1px solid var(--linea)}
{T} .pys-tz-path-item{grid-template-columns:72px 1fr!important;gap:18px!important;padding:24px 0!important;border:0!important;
  border-bottom:1px solid var(--linea)!important;border-radius:0!important;background:none!important;box-shadow:none!important;
  transform:none!important}
{T} .pys-tz-path-item:hover{transform:none!important;border-color:var(--linea)!important}
{T} .pys-tz-path-num{padding-top:7px;margin:0!important}
{T} .pys-tz-path-item p{max-width:72ch;font-size:16.5px!important}
/* propiedades: tabla con cabecera en mono y solo filetes */
{T} .pys-tz-properties{border-radius:3px!important;border:1px solid var(--linea-2)!important;background:var(--carbon-2)!important;
  background-image:none!important;box-shadow:none!important}
{T} .pys-tz-properties-row{grid-template-columns:.72fr 1.28fr!important;border-bottom:1px solid var(--linea)!important}
{T} .pys-tz-properties-row:last-child{border-bottom:0!important}
{T} .pys-tz-properties-cell{padding:15px 20px!important;border-right:1px solid var(--linea)!important;font-family:var(--optima)!important;
  font-size:16px!important;line-height:1.6!important;color:var(--tinta-2)!important;transition:background .2s}
{T} .pys-tz-properties-cell:last-child{border-right:0!important}
{T} .pys-tz-properties-head .pys-tz-properties-cell{padding-block:12px!important;background:var(--carbon)!important;
  font-family:var(--mono)!important;font-size:10.5px!important;font-weight:500!important;letter-spacing:.12em!important;
  color:var(--tinta-3)!important}
{T} .pys-tz-properties-cell strong{color:var(--tinta)!important;font-weight:400!important}
{T} .pys-tz-properties-row:not(.pys-tz-properties-head):hover .pys-tz-properties-cell{background:var(--panel)}

/* ═════════════════════════════════════════════════════════════════════
   1750 · /semaglutida-en-mexico/  (lo propio)
   ═════════════════════════════════════════════════════════════════════ */
{S} .pys-sema-tabs{border-radius:3px!important;background:var(--carbon-2)!important;background-image:none!important;
  border:1px solid var(--linea-2)!important;box-shadow:none!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
/* pestañas separadas por filetes con `gap`, así vale igual en 4, 2 o 1 columnas */
{S} .pys-sema-tab-nav{gap:1px!important;background:var(--linea)!important;border-bottom:1px solid var(--linea-2)!important}
{S} .pys-sema-tab-btn{border:0!important;background:var(--carbon)!important;box-shadow:none!important;padding:16px 12px!important;
  font-family:var(--mono)!important;font-size:11.5px!important;font-weight:500!important;letter-spacing:.1em!important;
  color:var(--tinta-3)!important;transition:color .2s,background .2s!important}
{S} .pys-sema-tab-btn:hover{color:var(--tinta)!important}
{S} .pys-sema-tab-btn.is-active{background:var(--carbon-2)!important;color:var(--tinta)!important;
  box-shadow:inset 0 -2px 0 var(--magenta)!important}
{S} .pys-sema-tab-content{padding:clamp(22px,3vw,36px)!important}
{S} .pys-sema-tab-content h3{font-family:var(--optima)!important;font-weight:400!important;font-size:clamp(22px,2.2vw,28px)!important;
  line-height:1.2!important;letter-spacing:-.01em!important;color:var(--tinta)!important;margin:0 0 14px!important}
{S} .pys-sema-tab-content p{font-family:var(--optima)!important;font-size:16.5px!important;line-height:1.7!important;
  color:var(--tinta-2)!important;max-width:72ch;margin:0 0 14px!important}
{S} .pys-sema-tab-content p strong{color:var(--tinta)!important;font-weight:600}
{S} .pys-sema-list{gap:1px!important;background:var(--linea)!important;border:1px solid var(--linea)!important;border-radius:3px;
  overflow:hidden;margin-top:22px!important}
{S} .pys-sema-list span{min-height:0!important;gap:10px!important;padding:13px 16px!important;border:0!important;border-radius:0!important;
  background:var(--carbon)!important;font-family:var(--optima)!important;font-size:15.5px!important;font-weight:400!important;
  line-height:1.4!important;color:var(--tinta)!important}
{S} .pys-sema-list span::before{width:6px!important;height:6px!important;flex:0 0 6px!important;background:var(--aqua)!important;
  box-shadow:none!important}

/* ═════════════════════════════════════════════════════════════════════
   2040 · /calculadora-de-dosis-de-peptidos/
   La calculadora la pinta un script (`data-no-optimize`) que busca `.pys-calc`
   y sus ids: aquí no se toca nada de lo que lee o escribe (ni `display` de
   `.pys-otro` ni de `.pys-warn`, que el script conmuta con `hidden`/`.show`).
   ═════════════════════════════════════════════════════════════════════ */
{C} .page-header{width:min(1320px,100%)!important;max-width:none!important;margin-inline:auto!important;
  padding:clamp(26px,4vw,52px) var(--gutter) 0!important}
{C} .page-header h1.entry-title{width:auto!important;max-width:20ch!important;margin:0 0 clamp(18px,2.4vw,28px)!important;
  padding:0!important;font-family:var(--optima)!important;font-weight:400!important;font-size:clamp(34px,4.6vw,62px)!important;
  line-height:1.04!important;letter-spacing:-.014em!important;color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important}

/* sus variables pasan a la paleta del sistema: lo que no se sobrescriba abajo
   hereda ya el color correcto */
{C} .pys-calc{--pys-azul:var(--aqua);--pys-azul-osc:var(--tinta);--pys-verde:var(--aqua);--pys-bg:var(--carbon);
  --pys-card:var(--carbon-2);--pys-borde:var(--linea-2);--pys-texto:var(--tinta);--pys-suave:var(--tinta-3);
  --pys-marker:var(--aqua);max-width:none!important;margin:0!important;padding:clamp(20px,3vw,40px)!important;
  border:1px solid var(--linea-2)!important;border-radius:3px!important;background:var(--carbon)!important;box-shadow:none!important;
  font-family:var(--optima)!important;line-height:1.5!important;color:var(--tinta)!important}
/* mismo texto que el h1 de la página, justo encima */
{C} .pys-calc > h2{display:none!important}
{C} .pys-calc .pys-sub{max-width:60ch;margin:0 0 clamp(20px,2.6vw,30px)!important;font-size:17px!important;color:var(--tinta-2)!important}
{C} .pys-calc .pys-sub strong{color:var(--tinta)!important;font-weight:600}
{C} .pys-calc .pys-cols{gap:clamp(20px,3vw,44px)!important}
{C} .pys-calc .pys-step{margin:4px 0 12px!important;font-family:var(--optima)!important;font-size:16.5px!important;
  font-weight:400!important;color:var(--tinta)!important}

/* jeringas */
{C} .pys-calc .pys-spick{padding:10px 14px!important;border:1px solid var(--linea-2)!important;border-radius:3px!important;
  background:var(--carbon-2)!important;box-shadow:none!important;transition:border-color .18s,background .18s!important}
{C} .pys-calc .pys-spick:hover{border-color:var(--tinta-3)!important}
{C} .pys-calc .pys-spick.activo{border-color:var(--aqua)!important;box-shadow:inset 0 0 0 1px var(--aqua)!important;
  background:color-mix(in srgb,var(--aqua) 6%,var(--carbon-2))!important}
{C} .pys-calc .pys-spick .ml{flex:0 0 60px!important;font-family:var(--mono)!important;font-size:13px!important;
  font-weight:500!important;color:var(--tinta)!important}
{C} .pys-calc .pys-spick.activo .ml{color:var(--aqua)!important}
/* el dibujo es SVG hecho por el script con colores en atributos: el CSS les
   gana. Cifras de la escala claras (estaban en gris oscuro fuera del cañón),
   émbolo y capuchón en magenta en vez de naranja. */
{C} .pys-calc .pys-spick svg text{fill:var(--tinta-2);font-family:var(--mono)}
{C} .pys-calc .pys-spick svg rect[fill="#f08a3c"]{fill:var(--magenta)}
{C} .pys-calc .pys-spick svg rect[fill="#f4ad6e"]{fill:#FF6FB0}
{C} .pys-calc .pys-spick svg rect[fill="#ffffff"]{fill:var(--vitrina)}

/* opciones */
{C} .pys-calc .pys-pills{gap:8px!important}
{C} .pys-calc .pys-pill{padding:9px 14px!important;border:1px solid var(--linea-2)!important;border-radius:2px!important;
  background:transparent!important;box-shadow:none!important;font-family:var(--mono)!important;font-size:12px!important;
  font-weight:500!important;letter-spacing:.04em!important;line-height:1.2!important;color:var(--tinta-2)!important;
  transition:border-color .18s,color .18s,background .18s!important}
{C} .pys-calc .pys-pill:hover{border-color:var(--tinta-3)!important;color:var(--tinta)!important}
{C} .pys-calc .pys-pill.activo{border-color:color-mix(in srgb,var(--aqua) 60%,transparent)!important;color:var(--aqua)!important;
  background:color-mix(in srgb,var(--aqua) 9%,transparent)!important}
{C} .pys-calc .pys-units{margin-bottom:12px!important;border:1px solid var(--linea-2)!important;border-radius:2px!important;
  background:transparent!important}
{C} .pys-calc .pys-upill{padding:8px 18px!important;background:transparent!important;font-family:var(--mono)!important;
  font-size:12px!important;font-weight:500!important;letter-spacing:.06em!important;color:var(--tinta-3)!important}
{C} .pys-calc .pys-upill.activo{background:var(--tinta)!important;color:var(--negro)!important}
{C} .pys-calc .pys-otro input{padding:11px 13px!important;border:1px solid var(--linea-2)!important;border-radius:2px!important;
  background:var(--negro)!important;color:var(--tinta)!important;font-family:var(--mono)!important;font-size:15px!important;
  outline:none!important;box-shadow:none!important}
{C} .pys-calc .pys-otro input:focus{border-color:var(--magenta)!important}
{C} .pys-calc .pys-otro input::placeholder{color:var(--tinta-3);opacity:1}
{C} .pys-calc option{color:#111!important;background:#fff!important}

/* resultado: cifras en mono aqua */
{C} .pys-calc .pys-result{margin-top:clamp(22px,3vw,32px)!important;padding:clamp(18px,2.4vw,28px)!important;
  border:1px solid var(--linea-2)!important;border-radius:3px!important;background:var(--carbon-2)!important;box-shadow:none!important}
{C} .pys-calc .pys-frase{font-family:var(--optima)!important;font-size:clamp(17px,1.5vw,20px)!important;line-height:1.45!important;
  color:var(--tinta)!important}
{C} .pys-calc .pys-frase b{font-family:var(--mono)!important;font-weight:500!important;color:var(--tinta)!important}
{C} .pys-calc .pys-frase b.res{font-size:1.45em!important;color:var(--aqua)!important}
{C} .pys-calc .pys-frase span{font-family:var(--mono)!important;font-size:12px!important;letter-spacing:.06em;
  color:var(--tinta-3)!important}
{C} .pys-calc .pys-ruler .track{border-top:2px solid var(--tinta-3)!important}
{C} .pys-calc .pys-ruler .mark{background:var(--aqua)!important;border-radius:1px!important}
{C} .pys-calc .pys-ruler .tk{background:var(--tinta-3)!important}
{C} .pys-calc .pys-ruler .tk.major{background:var(--tinta-2)!important}
{C} .pys-calc .pys-ruler .tk .lab{font-family:var(--mono)!important;font-size:10.5px!important;font-weight:400!important;
  color:var(--tinta-3)!important}
{C} .pys-calc .pys-ruler .cap{font-family:var(--mono)!important;font-size:10.5px!important;letter-spacing:.06em;
  color:var(--tinta-3)!important}
{C} .pys-calc .pys-res-grid{grid-template-columns:repeat(2,1fr)!important;gap:1px!important;margin-top:18px!important;
  background:var(--linea)!important;border:1px solid var(--linea)!important;border-radius:3px;overflow:hidden}
{C} .pys-calc .pys-res{padding:16px 18px!important;border:0!important;border-radius:0!important;background:var(--carbon)!important;
  text-align:left!important}
{C} .pys-calc .pys-res .v{font-family:var(--mono)!important;font-size:clamp(22px,2.2vw,28px)!important;font-weight:500!important;
  color:var(--aqua)!important;font-variant-numeric:tabular-nums}
{C} .pys-calc .pys-res .u{margin-top:6px!important;font-family:var(--mono)!important;font-size:10.5px!important;
  letter-spacing:.1em!important;text-transform:uppercase;color:var(--tinta-3)!important}
{C} .pys-calc .pys-vial-total{margin-top:12px!important;padding:14px 18px!important;border:1px solid var(--linea)!important;
  border-radius:3px!important;background:var(--carbon)!important;text-align:left!important;font-family:var(--optima)!important;
  font-size:16.5px!important;font-weight:400!important;color:var(--tinta-2)!important}
{C} .pys-calc .pys-vial-total b{margin:0 4px!important;font-family:var(--mono)!important;font-size:22px!important;
  font-weight:500!important;color:var(--aqua)!important}
{C} .pys-calc .pys-warn{padding:13px 16px!important;border:1px solid color-mix(in srgb,var(--magenta) 50%,transparent)!important;
  border-radius:3px!important;background:color-mix(in srgb,var(--magenta) 8%,transparent)!important;font-size:14.5px!important;
  line-height:1.55!important;color:var(--tinta)!important}
{C} .pys-calc .pys-warn strong{color:var(--magenta)!important;font-weight:600}

/* reconstitución: desplegable como las preguntas de la portada */
{C} .pys-calc details.pys-info{margin-top:clamp(20px,2.6vw,30px)!important;padding:0!important;border:0!important;
  border-top:1px solid var(--linea)!important;border-bottom:1px solid var(--linea)!important;border-radius:0!important;
  background:none!important}
{C} .pys-calc details.pys-info summary{display:flex;align-items:baseline;gap:14px;padding:16px 0!important;
  font-family:var(--optima)!important;font-size:17.5px!important;font-weight:400!important;color:var(--tinta)!important;
  transition:color .2s}
{C} .pys-calc details.pys-info summary:hover{color:var(--magenta)!important}
{C} .pys-calc details.pys-info summary::before{content:"+"!important;margin:0!important;font-family:var(--mono);font-size:15px;
  color:var(--magenta)!important}
{C} .pys-calc details.pys-info[open] summary::before{content:"\2212"!important}
{C} .pys-calc details.pys-info ol{max-width:74ch;margin:0 0 18px!important;padding-left:48px!important;font-size:16px!important;
  line-height:1.6;color:var(--tinta-2)!important}
{C} .pys-calc details.pys-info li{margin-bottom:8px!important}
{C} .pys-calc details.pys-info li::marker{color:var(--magenta);font-family:var(--mono);font-size:.85em}
{C} .pys-calc details.pys-info strong{color:var(--tinta)!important;font-weight:600}
/* aviso: como los avisos de WooCommerce de la base */
{C} .pys-calc .pys-aviso{margin-top:clamp(18px,2.4vw,26px)!important;padding:14px 18px!important;border:1px solid var(--linea-2)!important;
  border-top:2px solid var(--aqua)!important;border-radius:3px!important;background:var(--carbon-2)!important;
  font-size:14.5px!important;line-height:1.6!important;color:var(--tinta-2)!important}
{C} .pys-calc .pys-aviso strong{color:var(--tinta)!important;font-weight:600}
{C} .pys-calc .pys-cta{display:inline-flex!important;align-items:center;margin-top:22px!important;padding:14px 26px!important;
  border:1px solid var(--magenta)!important;border-radius:2px!important;background:var(--magenta)!important;color:#fff!important;
  font-family:var(--optima)!important;font-size:16px!important;font-weight:400!important;text-decoration:none!important;
  transition:background .2s,border-color .2s}
{C} .pys-calc .pys-cta:hover{background:#FF3D97!important;border-color:#FF3D97!important}

/* ═════════════════════════════════════════════════════════════════════
   PANTALLAS
   ═════════════════════════════════════════════════════════════════════ */
@media (max-width:1040px){
  {P} .pys-products-grid{grid-template-columns:repeat(3,minmax(0,1fr))!important}
}
@media (max-width:780px){
  {P} .pys-products-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important}
  {S} .pys-sema-product-img{border-right:0;border-bottom:1px solid var(--linea)}
}
@media (max-width:720px){
  {T} .pys-tz-path-item{grid-template-columns:40px 1fr!important;gap:12px!important;padding:20px 0!important}
  /* la hoja vieja apilaba cada celda con su rótulo («PROPIEDAD», «DESCRIPCIÓN»)
     repetido 12 veces; a 390 px cabe una tabla de verdad con su cabecera */
  {T} .pys-tz-properties-head{display:grid!important}
  {T} .pys-tz-properties-row{grid-template-columns:minmax(0,.8fr) minmax(0,1.5fr)!important}
  {T} .pys-tz-properties-cell{padding:12px 13px!important;font-size:15px!important;border-bottom:0!important;
    border-right:1px solid var(--linea)!important}
  {T} .pys-tz-properties-cell:last-child{border-right:0!important}
  {T} .pys-tz-properties-cell[data-label]::before{display:none!important}
  {T} .pys-tz-properties-head .pys-tz-properties-cell{font-size:9.5px!important;letter-spacing:.1em!important}
}
@media (max-width:540px){
  {T} .pys-tz-product-image{border-right:0;border-bottom:1px solid var(--linea)}
}
@media (max-width:440px){
  {P} .pys-product-body{padding:12px 12px 0!important}
  {P} .pys-product-card h3{font-size:15px!important}
  {P} .pys-product-price{margin:auto -12px 0!important;padding:11px 12px!important;font-size:13px!important}
  {P} .pys-product-price{font-size:12px!important}
  {P} .pys-product-price::after{display:none}
  {P} .pys-product-label{font-size:9px!important}
  {S} .pys-sema-tab-nav{grid-template-columns:1fr 1fr!important}
  {T} .pys-tz-faq-btn,{S} .pys-sema-faq-btn{font-size:17px!important}
  {T} .pys-tz-faq-panel-inner,{S} .pys-sema-faq-inner{padding-left:24px!important}
}
CSS;

	$todas = 'html body:is(.page-id-1551,.page-id-1729,.page-id-1750,.page-id-2040)[class][class]';
	return strtr(
		$css,
		array(
			'{A}' => $todas,
			'{P}' => 'html body.page-id-1551[class][class]',
			'{T}' => 'html body.page-id-1729[class][class]',
			'{S}' => 'html body.page-id-1750[class][class]',
			'{C}' => 'html body.page-id-2040[class][class]',
		)
	);
}
