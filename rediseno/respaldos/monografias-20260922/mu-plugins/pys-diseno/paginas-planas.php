<?php
/**
 * PYS — rediseño de las páginas planas (Gutenberg/HTML, sin Elementor en el
 * cuerpo): /glp-1/, las comparativas, las guías de péptidos inyectables y de
 * masa muscular, NAD+, contacto y términos. Solo diseño: no toca contenido.
 *
 * Estas páginas las sirve la plantilla de página de hello-elementor:
 *   main#content.site-main > .page-header > h1.entry-title
 *                          > .page-content > (prosa, figuras, avisos, tablas, FAQ)
 * El contenido trae cajas con estilo EN LÍNEA (avisos azul/ámbar claros, el
 * «Revisado por» dorado) y el Customizer le pinta a cinco de ellas (2102,
 * 2117-2119) un panel de radio 20 px, píldoras con degradado, tablas de radio
 * 12 px y titulares en aqua. Todo se re-estiliza encima.
 *
 * Especificidad: el Customizer ya tiene una regla de (1,5,2) con !important
 * sobre `#content.site-main` —`html body[class]:not(…):not(…):not(…)
 * #content.site-main`— que le fuerza el fondo transparente. Por eso aquí el
 * contenedor se escribe `#content#content.site-main` (repetir el id es válido
 * y cuenta dos veces): todas las reglas quedan en (2,4,2) o más y ganan por
 * especificidad, no por orden de carga. Los `style="…"` solo se vencen con
 * !important.
 *
 * Todo va colgado de `#content.site-main` para no alcanzar nada fuera del
 * cuerpo de estas páginas (p. ej. /home-2026/, que el cargador también
 * considera «plana» pero se pinta con su propia plantilla sin ese contenedor).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Hoja de las páginas planas. */
function pys_dis_css_paginas_planas() {
	$css = <<<'CSS'
/* ════════════════════════════════════════════════════════════════════
   CONTENEDOR: un solo panel de lectura con el título dentro
   (así ya se veían cinco de estas páginas; ahora todas por igual)
   ════════════════════════════════════════════════════════════════════ */
/* el panel mide lo que la columna de lectura (68ch del cuerpo) más su relleno:
   así el título, la prosa, los avisos y las tablas comparten un mismo borde */
%M{--pad:clamp(24px,5vw,64px);position:relative;z-index:1;box-sizing:border-box;
  width:min(calc(68ch + 2 * var(--pad) + 2px),calc(100% - 2 * var(--gutter)))!important;
  max-width:none!important;margin:clamp(22px,3.5vw,48px) auto clamp(48px,6vw,96px)!important;
  padding:var(--pad) var(--pad) calc(var(--pad) + 6px)!important;
  background:var(--carbon)!important;background-image:none!important;
  border:1px solid var(--linea)!important;border-radius:3px!important;box-shadow:none!important;
  color:var(--tinta-2);font-family:var(--optima);font-size:17.5px;line-height:1.7}
/* página sin contenido (términos, hoy vacía): sin panel vacío, y el pie abajo */
%M:not(:has(.page-header)):not(:has(.page-content > *)){background:none!important;
  border:0!important;padding:0!important;min-height:52vh}

/* ── cabecera ─────────────────────────────────────────────────────── */
%M .page-header{max-width:68ch;margin:0 auto clamp(26px,3.4vw,40px)!important;padding:0!important;
  width:auto!important}
%M .page-header .entry-title,
%M .page-content h1.glp1-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(30px,3.7vw,46px)!important;line-height:1.08!important;letter-spacing:-.014em!important;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;background:none!important;
  text-transform:none!important;max-width:none!important;width:auto!important;
  margin:0!important;padding:0!important;text-wrap:pretty}
/* la rayita magenta bajo el título, la misma del listado del blog */
%M .page-header::after,
%M .page-content h1.glp1-title::after{content:"";display:block;width:56px;height:1px;
  background:var(--magenta);opacity:.85;margin-top:clamp(18px,2.2vw,24px)}
%M .page-content h1.glp1-title{margin:0 auto clamp(26px,3.4vw,40px)!important}

/* ════════════════════════════════════════════════════════════════════
   PROSA
   ════════════════════════════════════════════════════════════════════ */
%C{font-size:17.5px!important;line-height:1.7!important;color:var(--tinta-2)!important;
  max-width:68ch;margin-inline:auto!important;padding:0!important}
%C p{margin:0 auto 1.05em!important;color:var(--tinta-2)!important}
%C strong,%C b{color:var(--tinta)!important;font-weight:600}
%C em{color:var(--tinta)}
%C h2{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(25px,2.6vw,33px)!important;line-height:1.16!important;letter-spacing:-.01em;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;text-transform:none!important;
  margin:1.55em auto .55em!important;padding:.8em 0 0!important;
  border:0!important;border-top:1px solid var(--linea)!important}
%C > h2:first-child{border-top:0!important;padding-top:0!important;margin-top:0!important}
/* títulos seguidos sin texto entre medias, o tras una raya: una sola línea */
%C h2 + h2,%C hr + h2{border-top:0!important;padding-top:0!important;margin-top:.45em!important}
%C h3{font-family:var(--optima)!important;font-weight:400!important;font-size:21px!important;
  line-height:1.26!important;color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;
  text-transform:none!important;margin:1.6em auto .45em!important;padding:0!important;border:0!important}
%C h2 + h3{margin-top:.9em!important}
%C h4{font-family:var(--mono)!important;font-weight:500!important;font-size:12px!important;
  letter-spacing:.12em;text-transform:uppercase;color:var(--tinta-3)!important;margin:1.5em auto .5em!important}
/* un h1 dentro del cuerpo que no es el título de la página (NAD+) */
%C > h1:not(.glp1-title){font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(27px,3vw,38px)!important;line-height:1.12!important;letter-spacing:-.012em;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;
  margin:1.5em auto .6em!important;padding:0!important;border:0!important}

/* enlaces: aqua, subrayado fino */
%C a{color:var(--aqua)!important;-webkit-text-fill-color:currentColor!important;background:none!important;
  border:0!important;text-decoration:underline!important;
  text-decoration-color:color-mix(in srgb,var(--aqua) 38%,transparent)!important;
  text-decoration-thickness:1px!important;text-underline-offset:3px;transition:text-decoration-color .2s}
%C a:hover{text-decoration-color:var(--aqua)!important}
%C strong a,%C a strong{color:var(--aqua)!important}

/* listas: viñeta magenta, como en la entrada del blog */
%C ul,%C ol{padding-left:1.35em!important;margin:0 auto 1.25em!important}
%C li{margin:0 0 .5em!important;color:var(--tinta-2)!important;padding-left:.15em}
%C ul li::marker{color:var(--magenta)}
%C ol li::marker{color:var(--magenta);font-family:var(--mono);font-size:.82em}
%C li > strong:first-child{color:var(--tinta)!important}

/* nota final en cursiva («Última revisión…», avisos legales) */
%C p:has(> em:only-child){font-size:14.5px!important;line-height:1.6!important;color:var(--tinta-3)!important;
  border-top:1px solid var(--linea);padding-top:1em;margin-top:1.6em!important}
%C p:has(> em:only-child) em{color:var(--tinta-3)!important}

/* los párrafos que solo envuelven el JSON-LD del FAQ no llevan texto:
   se quita el hueco que dejaban (el JSON-LD sigue en el HTML). OJO: en esta hoja NO puede
   aparecer ninguna etiqueta escrita con sus picos, ni en comentarios: LiteSpeed
   la toma por etiqueta real, se lleva al paquete JS todo lo que hay hasta el
   siguiente cierre de script y rompe la página */
%C p:has(> script[type="application/ld+json"]:first-child){display:none!important}

%C hr{border:0!important;border-top:1px solid var(--linea)!important;height:0;background:none!important;
  margin:2.2em auto!important}
%C blockquote{border-left:2px solid var(--magenta);margin:1.5em auto!important;
  padding:.2em 0 .2em 1.2em;color:var(--tinta);font-style:italic;background:none!important}
%C code{font-family:var(--mono);font-size:.88em;background:var(--panel);padding:.1em .4em;
  border-radius:2px;color:var(--tinta)}

/* ── figuras ──────────────────────────────────────────────────────── */
%C figure{margin:1.7em auto!important;padding:0!important}
%C figure img,%C > p > img{display:block!important;width:auto!important;max-width:100%!important;
  height:auto!important;max-height:460px;margin:0 auto!important;
  border:1px solid var(--linea)!important;border-radius:3px!important;background:var(--carbon-2)}
%C figcaption{font-family:var(--mono);font-size:11px;letter-spacing:.05em;color:var(--tinta-3);
  margin-top:8px;text-align:center}

/* ════════════════════════════════════════════════════════════════════
   CAJAS
   ════════════════════════════════════════════════════════════════════ */
/* avisos con estilo en línea (azul claro «Nota», ámbar «Importante»):
   pasan a recuadro carbón con filete a la izquierda y la etiqueta en mono */
%C > div[style*="border-left"]{background:var(--carbon-2)!important;background-image:none!important;
  border:1px solid var(--linea-2)!important;border-left:2px solid var(--aqua)!important;
  border-radius:3px!important;box-shadow:none!important;color:var(--tinta-2)!important;
  padding:18px 22px!important;margin:1.7em auto!important;font-size:15.5px!important;line-height:1.65!important}
%C > div[style*="#d97706"]{border-left-color:var(--magenta)!important}
%C > div[style*="border-left"] strong{color:var(--tinta)!important;font-weight:600}
%C > div[style*="border-left"] > strong:first-child{display:block;font-family:var(--mono)!important;
  font-size:10.5px!important;font-weight:500!important;letter-spacing:.14em;text-transform:uppercase;
  color:var(--aqua)!important;margin-bottom:7px}
%C > div[style*="#d97706"] > strong:first-child{color:var(--magenta)!important}

/* «Revisado por» (NAD+): ficha del revisor */
%C .pys-revisado-por{background:var(--carbon-2)!important;border:1px solid var(--linea-2)!important;
  border-left:2px solid var(--aqua)!important;border-radius:3px!important;box-shadow:none!important;
  padding:18px 22px!important;margin:1.8em auto!important}
%C .pys-revisado-por p{margin:0!important;color:var(--tinta-2)!important;font-size:15px!important;
  line-height:1.55!important;font-weight:400!important}
%C .pys-revisado-por p:first-child{font-family:var(--mono)!important;font-size:10.5px!important;
  font-weight:500!important;letter-spacing:.14em;text-transform:uppercase;color:var(--tinta-3)!important;
  margin-bottom:9px!important}
%C .pys-revisado-por p:nth-child(2){font-size:19px!important;color:var(--tinta)!important;
  margin-bottom:3px!important}

/* el hallazgo clave resaltado (NAD+) */
%C p.aviso{border-left:2px solid var(--magenta);border-radius:0 3px 3px 0;
  background:color-mix(in srgb,var(--magenta) 6%,var(--carbon-2));
  padding:16px 20px!important;margin:1.5em auto 1.3em!important;color:var(--tinta)!important}

/* preguntas frecuentes */
%C .faq-item{background:var(--carbon-2)!important;border:1px solid var(--linea)!important;
  border-radius:3px!important;box-shadow:none!important;padding:17px 22px!important;
  margin:0 auto 10px!important}
%C .faq-item h3{font-size:18.5px!important;margin:0 0 7px!important;color:var(--tinta)!important}
%C .faq-item p{margin:0!important;font-size:16px!important;line-height:1.62!important}
%C h2 + .faq-item{margin-top:.9em!important}

/* accesos rápidos de /glp-1/: de píldoras con degradado a sellos del sistema */
%C .glp1-quicknav{display:flex!important;flex-wrap:wrap;gap:8px!important;margin:0 auto 26px!important}
%C .glp1-quicknav br{display:none}
%C a.glp1-pill{display:inline-flex!important;align-items:center;gap:9px;
  font-family:var(--mono)!important;font-size:11px!important;font-weight:500!important;
  letter-spacing:.1em!important;text-transform:uppercase!important;line-height:1.2!important;
  padding:9px 14px!important;border:1px solid var(--linea-2)!important;border-radius:2px!important;
  background:transparent!important;background-image:none!important;box-shadow:none!important;
  color:var(--tinta-2)!important;-webkit-text-fill-color:currentColor!important;
  text-decoration:none!important;transform:none!important;transition:border-color .2s,color .2s}
%C a.glp1-pill::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--tinta-3);flex:none}
%C a.glp1-pill-reta::before{background:var(--magenta)}
%C a.glp1-pill-tirze::before{background:var(--aqua)}
%C a.glp1-pill-sema::before{background:var(--tinta-2)}
%C a.glp1-pill:hover{border-color:var(--tinta)!important;color:var(--tinta)!important;transform:none!important}

/* ════════════════════════════════════════════════════════════════════
   TABLAS: cabecera en mono y solo líneas horizontales
   ════════════════════════════════════════════════════════════════════ */
%C table{width:100%!important;border-collapse:collapse!important;border-spacing:0;
  margin:1.5em auto 1.7em!important;font-size:15.5px!important;line-height:1.5!important;
  background:none!important;border:0!important;border-radius:0!important;overflow:visible!important;
  box-shadow:none!important}
%C th{font-family:var(--mono)!important;font-size:10.5px!important;font-weight:500!important;
  letter-spacing:.12em;text-transform:uppercase;color:var(--tinta-3)!important;text-align:left!important;
  padding:10px 12px!important;border:0!important;border-bottom:1px solid var(--linea-2)!important;
  background:none!important;vertical-align:bottom}
%C td{padding:11px 12px!important;border:0!important;border-bottom:1px solid var(--linea)!important;
  background:none!important;color:var(--tinta-2)!important;vertical-align:top;font-size:15.5px!important}
%C tbody tr > td:first-child{color:var(--tinta)!important}
%C tbody tr:hover > td{background:var(--carbon-2)!important}

/* ════════════════════════════════════════════════════════════════════
   TELÉFONO
   ════════════════════════════════════════════════════════════════════ */
@media (max-width:640px){
  /* en el teléfono el panel va de borde a borde: la columna gana el ancho
     que se comían el margen y el relleno, y las tablas caben */
  %M{--pad:var(--gutter);width:100%!important;margin:14px 0 40px!important;
    border-left:0!important;border-right:0!important;border-radius:0!important;
    padding:28px var(--gutter) 36px!important;font-size:16.5px}
  %C{font-size:16.5px!important;line-height:1.68!important}
  %C h2{font-size:24px!important}
  %C h3{font-size:19px!important}
  %C > div[style*="border-left"],%C .pys-revisado-por{padding:15px 16px!important}
  %C .faq-item{padding:15px 16px!important}
  %C .faq-item h3{font-size:17px!important}
  %C figure img,%C > p > img{max-height:340px}
  /* la tabla no empuja la página: se desplaza dentro de su columna */
  %C table{display:block!important;overflow-x:auto!important;-webkit-overflow-scrolling:touch;
    font-size:13.5px!important}
  %C th{padding:8px 7px!important;font-size:9px!important;letter-spacing:.08em}
  %C td{padding:9px 7px!important;font-size:13.5px!important;line-height:1.45}
  /* las palabras largas de las celdas de datos («Gastrointestinales») se
     parten con guion en vez de empujar la tabla fuera de la columna */
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
