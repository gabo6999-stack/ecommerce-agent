<?php
/**
 * PYS — rediseño de las monografías científicas. Solo diseño: no toca contenido.
 *
 * Familia: el singular del tipo de contenido «monografia» y la página hub
 * /monografia/. El ámbito lo decide el cargador (pys-diseno.php), aquí no.
 *
 * El tema hello-elementor 3.4.7 no tiene single.php ni singular.php y la
 * plantilla #159 de Elementor está acotada a `include/singular/post`, así que
 * la monografía la pinta template-parts/single.php, con este marcado:
 *
 *   main#content.site-main > .page-header > h1.entry-title
 *                          > .page-content > nav.pys-mono-migas
 *                                            (prosa: h2/h3/p/tablas/listas)
 *                                            aside.pys-mono-ficha
 *
 * Es el mismo esqueleto de las páginas planas, así que la hoja parte de la
 * prosa de blog.php / paginas-planas.php: una sola columna de lectura de 68ch
 * dentro de un panel, titulares en Optima, tablas con solo líneas horizontales.
 * Lo propio de la monografía son tres cosas: las migas, la tabla de identidad
 * química (que llega como una tabla normal y se lee mejor con la primera
 * columna en monoespaciada) y el bloque final que lleva a la ficha.
 *
 * Especificidad: el Customizer del sitio ya tiene una regla con !important
 * sobre `#content.site-main`. Por eso el contenedor se escribe
 * `#content#content.site-main` —repetir el id es válido y cuenta dos veces— y
 * todas las reglas ganan por especificidad, no por orden de carga, que con
 * LiteSpeed reordenando e inyectando CSS crítico no es de fiar.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Hoja de las monografías. */
function pys_dis_css_monografias() {
	$css = <<<'CSS'
/* ════════════════════════════════════════════════════════════════════
   CONTENEDOR: un panel de lectura con el título dentro
   ════════════════════════════════════════════════════════════════════ */
%M{--pad:clamp(24px,5vw,64px);position:relative;z-index:1;box-sizing:border-box;
  width:min(calc(72ch + 2 * var(--pad) + 2px),calc(100% - 2 * var(--gutter)))!important;
  max-width:none!important;margin:clamp(22px,3.5vw,48px) auto clamp(48px,6vw,96px)!important;
  padding:var(--pad) var(--pad) calc(var(--pad) + 6px)!important;
  background:var(--carbon)!important;background-image:none!important;
  border:1px solid var(--linea)!important;border-radius:3px!important;box-shadow:none!important;
  color:var(--tinta-2);font-family:var(--optima);font-size:17.5px;line-height:1.7}

/* ── cabecera ─────────────────────────────────────────────────────── */
%M .page-header{max-width:72ch;margin:0 auto clamp(18px,2.4vw,26px)!important;padding:0!important;
  width:auto!important}
%M .page-header .entry-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(30px,3.7vw,46px)!important;line-height:1.08!important;letter-spacing:-.014em!important;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;background:none!important;
  text-transform:none!important;max-width:none!important;width:auto!important;
  margin:0!important;padding:0!important;text-wrap:pretty}

/* ── migas: la línea de servicio del sistema, en monoespaciada ────── */
%C .pys-mono-migas{max-width:72ch;margin:0 auto clamp(26px,3.4vw,38px)!important;
  padding:0 0 clamp(16px,2.2vw,22px)!important;border-bottom:1px solid var(--linea)!important;
  font-family:var(--mono)!important;font-size:11px!important;letter-spacing:.09em!important;
  text-transform:uppercase;color:var(--tinta-3)!important;line-height:1.5;
  display:flex;flex-wrap:wrap;align-items:baseline;gap:8px}
%C .pys-mono-migas a{color:var(--tinta-3)!important;text-decoration:none!important;
  border-bottom:1px solid transparent;transition:color .2s,border-color .2s}
%C .pys-mono-migas a:hover{color:var(--tinta)!important;
  border-bottom-color:color-mix(in srgb,var(--magenta) 60%,transparent)}
%C .pys-mono-migas .pys-mono-sep{color:var(--linea-2)!important}
%C .pys-mono-migas [aria-current]{color:var(--tinta-2)!important}

/* ════════════════════════════════════════════════════════════════════
   PROSA
   ════════════════════════════════════════════════════════════════════ */
%C{font-size:17.5px!important;line-height:1.72!important;color:var(--tinta-2)!important;
  max-width:none!important;margin-inline:auto!important;padding:0!important}
%C > *{max-width:72ch;margin-inline:auto}
%C p{margin:0 auto 1.05em!important;color:var(--tinta-2)!important}
%C strong,%C b{color:var(--tinta)!important;font-weight:600}
%C em{color:var(--tinta)}
%C h2{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(25px,2.6vw,33px)!important;line-height:1.16!important;letter-spacing:-.01em;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;text-transform:none!important;
  margin:1.85em auto .55em!important;padding:.85em 0 0!important;
  border:0!important;border-top:1px solid var(--linea)!important}
%C > h2:first-child{border-top:0!important;padding-top:0!important;margin-top:0!important}
%C h2 + h2,%C hr + h2{border-top:0!important;padding-top:0!important;margin-top:.45em!important}
%C h3{font-family:var(--optima)!important;font-weight:400!important;font-size:21px!important;
  line-height:1.26!important;color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;
  text-transform:none!important;margin:1.6em auto .45em!important;padding:0!important;border:0!important}
%C h2 + h3{margin-top:.9em!important}
%C h4{font-family:var(--mono)!important;font-weight:500!important;font-size:12px!important;
  letter-spacing:.12em;text-transform:uppercase;color:var(--tinta-3)!important;
  margin:1.5em auto .5em!important}
%C a{color:var(--magenta)!important;-webkit-text-fill-color:currentColor!important;
  background:none!important;text-decoration:underline;
  text-decoration-color:color-mix(in srgb,var(--magenta) 40%,transparent);text-underline-offset:3px}
%C a:hover{text-decoration-color:var(--magenta)!important}
%C ul,%C ol{padding-left:1.35em;margin:0 auto 1.2em!important}
%C li{margin-bottom:.45em}
%C ul li::marker{color:var(--magenta)}
%C ol li::marker{color:var(--magenta);font-family:var(--mono);font-size:.85em}
%C blockquote{border-left:2px solid var(--magenta)!important;margin:1.5em auto!important;
  padding:.2em 0 .2em 1.2em!important;color:var(--tinta)!important;font-style:italic;
  background:none!important;border-radius:0!important}
%C hr{border:0!important;border-top:1px solid var(--linea)!important;margin:2.2em auto!important}
%C code{font-family:var(--mono)!important;font-size:.88em;background:var(--panel)!important;
  padding:.1em .4em;border-radius:2px;color:var(--tinta)!important}
%C figure{margin:1.6em auto!important}
%C img:not(.emoji){max-width:100%;height:auto;border-radius:3px!important;
  border:1px solid var(--linea);box-shadow:none!important}
%C figcaption{font-family:var(--mono)!important;font-size:11px;letter-spacing:.05em;
  color:var(--tinta-3)!important;margin-top:8px;text-align:center}

/* ════════════════════════════════════════════════════════════════════
   TABLAS — la de identidad química es la pieza central de la monografía
   ════════════════════════════════════════════════════════════════════ */
%C table{width:100%!important;max-width:72ch;border-collapse:collapse!important;border-spacing:0;
  margin:1.5em auto 1.8em!important;font-size:15.5px!important;background:none!important;
  border:0!important;border-radius:0!important;box-shadow:none!important}
%C tr,%C thead,%C tbody{background:none!important;background-color:transparent!important;
  color:inherit!important;border-radius:0!important}
%C th{font-family:var(--mono)!important;font-size:10.5px!important;font-weight:500!important;
  letter-spacing:.12em;text-transform:uppercase;color:var(--tinta-3)!important;text-align:left;
  padding:10px 12px!important;border:0!important;
  border-bottom:1px solid var(--linea-2)!important;background:none!important}
%C td{padding:11px 12px!important;border:0!important;border-bottom:1px solid var(--linea)!important;
  background:none!important;color:var(--tinta-2)!important;vertical-align:top}
/* la primera columna es el rótulo del dato (CAS, fórmula, peso molecular) */
%C tbody tr > td:first-child{color:var(--tinta)!important}
%C tbody tr:hover > td{background:var(--carbon-2)!important}
/* fórmulas, secuencias y números: cifras de ancho fijo, que es como se leen */
%C table td:last-child{font-variant-numeric:tabular-nums}
%C th:first-child,%C td:first-child{padding-left:0!important}
%C th:last-child,%C td:last-child{padding-right:0!important}

/* ════════════════════════════════════════════════════════════════════
   BLOQUE FINAL: de la monografía a la ficha
   ════════════════════════════════════════════════════════════════════ */
%C .pys-mono-ficha{max-width:72ch;margin:clamp(30px,4vw,48px) auto 0!important;
  padding:clamp(18px,2.4vw,24px) clamp(18px,2.4vw,26px)!important;
  background:var(--carbon-2)!important;border:1px solid var(--linea-2)!important;
  border-left:2px solid var(--aqua)!important;border-radius:2px!important;box-shadow:none!important}
%C .pys-mono-ficha-et{font-family:var(--mono)!important;font-size:10.5px!important;
  letter-spacing:.14em!important;text-transform:uppercase;color:var(--aqua)!important;
  margin:0 0 .5em!important}
%C .pys-mono-ficha-tx{color:var(--tinta-2)!important;font-size:16px!important;
  line-height:1.6!important;margin:0 0 .8em!important}
%C .pys-mono-ficha-cta{margin:0!important}
%C .pys-mono-ficha-cta a{display:inline-block;font-family:var(--optima)!important;font-size:16px;
  padding:12px 22px!important;border:1px solid var(--magenta)!important;background:var(--magenta)!important;
  color:#fff!important;-webkit-text-fill-color:#fff!important;border-radius:2px!important;
  text-decoration:none!important;transition:background .2s,border-color .2s}
%C .pys-mono-ficha-cta a:hover{background:#FF3D97!important;border-color:#FF3D97!important}

/* ════════════════════════════════════════════════════════════════════
   TELÉFONO
   ════════════════════════════════════════════════════════════════════ */
@media (max-width:640px){
  %M{--pad:var(--gutter);width:100%!important;margin:14px 0 40px!important;
    border-left:0!important;border-right:0!important;border-radius:0!important}
  %C{font-size:16.5px!important;line-height:1.68!important}
  %C h2{font-size:24px!important}
  %C h3{font-size:19px!important}
  %C .pys-mono-migas{font-size:10px!important;gap:6px}
  %C .pys-mono-ficha{padding:16px 17px!important}
  /* la tabla se desplaza dentro de su columna en vez de empujar la página */
  %C table{display:block!important;overflow-x:auto!important;-webkit-overflow-scrolling:touch;
    font-size:13.5px!important;white-space:normal}
  %C th{padding:8px 7px!important;font-size:9px!important;letter-spacing:.08em}
  %C td{padding:9px 7px!important;font-size:13.5px!important;line-height:1.45}
  %C td + td{-webkit-hyphens:auto;hyphens:auto}
  %C th:first-child,%C td:first-child{padding-left:0!important}
}
CSS;

	return str_replace(
		array( '%C', '%M' ),
		array(
			'html body[class][class][class] #content#content.site-main .page-content',
			'html body[class][class][class] #content#content.site-main',
		),
		$css
	);
}
