<?php
/**
 * PYS — rediseño de las páginas Elementor: políticas e informativas.
 * Solo diseño: no toca contenido.
 *
 * Ocho páginas, todas hechas con un único widget «HTML» de Elementor que trae
 * su propio marcado y su propia hoja en línea (degradados, vidrio, radios de
 * 24-42 px, texto con degradado recortado):
 *
 *   3    /politica-de-privacidad/             ┐ políticas: prosa larga
 *   10   /politica-de-envios-y-devoluciones/  ┘
 *   24   /recuperacion-muscular/              ┐ misma plantilla, prefijos
 *   26   /envejecimiento-saludable/           │ pys-, pys-longevity- y
 *   643  /rendimiento-deportivo/              ┘ pys-performance-
 *   23   /como-acelerar-el-metabolismo/       — plantilla propia (pys-metabolismo-page)
 *   1166 /suplementos-deportivos/             — plantilla propia (pys-supp-redesign)
 *   29   /pedido/                             — página vieja con [woocommerce_checkout]
 *                                                (noindex; la de verdad es la 777)
 *
 * 23, 24 y 643 llevan además el mismo aviso emergente (#pys-urgent-popup) y
 * casi todas, prosa suelta antes o después del bloque principal (h2/p/ul
 * sueltos dentro del widget, añadidos después para SEO).
 *
 * TODAS las reglas van acotadas por la clase `page-id-*` del body: las
 * landings de otra familia comparten el mismo predicado del cargador. Los
 * ámbitos se escriben como fichas (@@P, @@POL…) y se sustituyen al final.
 *
 * Como las hojas de los widgets usan `!important` a discreción, aquí TODAS las
 * declaraciones salen con `!important` (lo añade pys_dis_pe_importante()); la
 * cascada entre reglas propias se decide solo por especificidad y orden.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Añade `!important` a cada declaración que no lo lleve. Opera solo sobre los
 * bloques más internos `{…}` —las declaraciones—, así que los `@media` quedan
 * intactos. El CSS de aquí no lleva `;` dentro de valores (ni data: URIs).
 */
function pys_dis_pe_importante( $css ) {
	return preg_replace_callback(
		'/\{([^{}]*)\}/',
		function ( $m ) {
			$decl = array();
			foreach ( explode( ';', $m[1] ) as $d ) {
				$d = trim( $d );
				if ( '' === $d ) {
					continue;
				}
				if ( false === stripos( $d, '!important' ) ) {
					$d .= '!important';
				}
				$decl[] = $d;
			}
			return '{' . implode( ';', $decl ) . '}';
		},
		$css
	);
}

/** Hoja de la familia. */
function pys_dis_css_paginas_elementor() {
	/* `:is()` con una lista de clases pesa lo que una clase: todos los ámbitos
	   quedan en 0,3,2, igual que el `html body[class][class][class]` del resto
	   del rediseño. */
	$ambitos = array(
		'@@POL' => 'html body:is(.page-id-3,.page-id-10)[class][class]',
		'@@INF' => 'html body:is(.page-id-23,.page-id-24,.page-id-26,.page-id-643,.page-id-1166)[class][class]',
		'@@TRI' => 'html body:is(.page-id-24,.page-id-26,.page-id-643)[class][class]',
		'@@POP' => 'html body:is(.page-id-23,.page-id-24,.page-id-643)[class][class]',
		'@@MET' => 'html body:is(.page-id-23)[class][class]',
		'@@SUP' => 'html body:is(.page-id-1166)[class][class]',
		'@@PED' => 'html body:is(.page-id-29)[class][class]',
		'@@P'   => 'html body:is(.page-id-3,.page-id-10,.page-id-23,.page-id-24,.page-id-26,.page-id-643,.page-id-1166,.page-id-29)[class][class]',
	);

	$css = <<<'CSS'
/* ════════════════════════════════════════════════════════════════════
   0 · BASE COMÚN (las 8)
   ════════════════════════════════════════════════════════════════════ */

/* Todo el contenido por encima del panal y del halo fijos (z-index 0): sin
   esto el halo tiñe lo que no va dentro de un section. Posicionado pero SIN
   z-index, para no abrir un contexto de apilamiento: así la capa fija del
   aviso emergente sigue pudiendo tapar la cabecera. Queda encima del panal
   por orden en el documento. */
@@P .elementor{position:relative;z-index:auto}

/* El contenedor «boxed» de Elementor (1140 px) se alinea con la cabecera:
   la misma caja de 1320 px con el mismo margen lateral que `.wrap`. */
@@P .elementor > .e-con.e-parent{padding-inline:0;background:none;border:0}
@@P .elementor > .e-con.e-parent > .e-con-inner{width:100%;max-width:1320px;margin-inline:auto;
  padding-inline:var(--gutter);padding-block:0}
@@P .elementor > .e-con.e-parent:first-child > .e-con-inner{padding-top:clamp(26px,4vw,56px)}
@@P .elementor > .e-con.e-parent:last-child > .e-con-inner{padding-bottom:clamp(44px,6vw,96px)}
@@P .elementor-widget-html{width:100%}

/* Tipografía del sistema para todo el widget (las hojas en línea piden Inter) */
@@P .elementor-widget-html > .elementor-widget-container{font-family:var(--optima);color:var(--tinta);
  font-size:17px;line-height:1.6}
@@P :where(.elementor-widget-html) *{font-family:inherit;text-shadow:none;box-shadow:none;
  backdrop-filter:none;-webkit-backdrop-filter:none;animation:none;transform:none;filter:none}
/* Adornos de las hojas viejas: rejillas, halos, «P&S» de marca de agua,
   rayitas con degradado, anillos giratorios. Todos son pseudoelementos sin
   texto real; las viñetas de las listas y los +/− de los desplegables (li y
   summary) no entran aquí y se re-estilizan aparte. */
@@P :where(.elementor-widget-html) :is(main,section,div,article,a,h1,h2,h3,span,details,p)::before,
@@P :where(.elementor-widget-html) :is(main,section,div,article,a,h1,h2,h3,span,details,p)::after{
  display:none;content:none}
/* la base da 48-104 px de relleno a cada section: los widgets usan
   section también para tarjetas, así que se anula y cada bloque pone el suyo */
@@P :where(.elementor-widget-html) section{padding-block:0;z-index:auto}

@@P :where(.elementor-widget-html) :is(h1,h2,h3,h4){font-family:var(--optima);font-weight:400;
  color:var(--tinta);-webkit-text-fill-color:currentColor;text-transform:none;letter-spacing:-.01em;
  background:none}
@@P :where(.elementor-widget-html) :is(p,li){color:var(--tinta-2)}
@@P :where(.elementor-widget-html) :is(p,li) :is(strong,b){color:var(--tinta);font-weight:600}
@@P :where(.elementor-widget-html) :is(p,li) a{color:var(--magenta);background:none;border:0;padding:0;
  -webkit-text-fill-color:currentColor;text-decoration:underline;text-underline-offset:3px;
  text-decoration-color:color-mix(in srgb,var(--magenta) 40%,transparent);font-weight:inherit}
@@P :where(.elementor-widget-html) :is(p,li) a:hover{text-decoration-color:var(--magenta)}
/* palabra resaltada: magenta sólido, como en los titulares de la portada.
   Devuelve el relleno del texto (si no, al quitar el degradado se vuelve
   invisible). */
@@P :where(.elementor-widget-html) :is(h1,h2) :is(strong,.pys-gradient-text,.pys-gradient){
  font-weight:400;color:var(--magenta);-webkit-text-fill-color:currentColor;background:none;
  background-image:none;-webkit-background-clip:border-box;background-clip:border-box}
@@P :where(.elementor-widget-html) img{border-radius:0}

/* ── prosa suelta dentro del widget (h2/p/ul fuera de los bloques) ─── */
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(h2,h3,p,ul,ol){max-width:68ch}
@@P :where(.elementor-widget-html > .elementor-widget-container) > p{font-size:17px;line-height:1.7;
  margin:0 0 .85em;color:var(--tinta-2)}
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(p:first-child,.pys-urgent-popup:first-child + p){font-size:clamp(17.5px,1.4vw,19.5px);
  line-height:1.6;color:var(--tinta)}
@@P :where(.elementor-widget-html > .elementor-widget-container) > h2{font-size:clamp(24px,2.5vw,32px);
  line-height:1.15;letter-spacing:-.01em;margin:1.6em 0 .55em;padding-top:.85em;
  border-top:1px solid var(--linea)}
/* LiteSpeed saca las hojas y los scripts en línea del widget: tras el aviso emergente
   (oculto) el primer h2 es de hecho el primero de la página */
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(h2:first-child,.pys-urgent-popup:first-child + h2){margin-top:0;
  padding-top:0;border-top:0}
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(section,main) + h2{
  margin-top:clamp(44px,5vw,80px)}
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(ul,ol){padding-left:1.35em;
  margin:0 0 1em}
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(ul,ol) li{margin-bottom:.45em;
  font-size:17px;line-height:1.6}
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(ul,ol) li::marker{color:var(--magenta)}
@@P :where(.elementor-widget-html > .elementor-widget-container) > :is(ul,ol) li a{color:var(--tinta);
  text-decoration-color:color-mix(in srgb,var(--magenta) 55%,transparent)}
/* entre la prosa de arriba (widget 1) y el bloque principal (widget 2) */
@@P .elementor > .e-con.e-parent:first-child:not(:last-child) > .e-con-inner{padding-bottom:clamp(12px,2vw,24px)}

/* ════════════════════════════════════════════════════════════════════
   1 · POLÍTICAS (3 privacidad · 10 envíos y devoluciones)
   Columna de lectura de ~68ch, jerarquía clara, secciones separadas por
   una línea en vez de cajas dentro de cajas.
   ════════════════════════════════════════════════════════════════════ */
/* toda la página en una columna de 980 px: así la prosa suelta de arriba y
   de abajo arranca en el mismo borde que el título */
@@POL .elementor-widget-html > .elementor-widget-container{max-width:980px;margin-inline:auto}
@@POL :is(.pys-privacy-page,.pys-merchant-policy){background:none;color:var(--tinta);overflow:visible;
  padding:clamp(8px,2vw,24px) 0 0}
@@POL :is(.pys-privacy-wrap,.pys-policy-wrap){width:100%;max-width:none;margin:0}
@@POL .pys-merchant-policy + h2{margin-top:clamp(44px,5vw,72px)}

/* el documento de privacidad es un panel con la columna de lectura
   centrada: el relleno lateral se calcula para que el texto mida 680 px */
@@POL .pys-privacy-card{background:color-mix(in srgb,var(--carbon) 94%,transparent);border:1px solid var(--linea);
  border-radius:3px;padding-block:clamp(28px,5vw,64px);
  padding-inline:max(clamp(20px,4.5vw,56px),calc((100% - 680px) / 2));color:var(--tinta-2)}

/* cabecera: ladillo en mono, titular Optima, entradilla */
@@POL :is(.pys-privacy-badge,.pys-policy-badge){display:block;width:auto;padding:0;margin-top:0;margin-bottom:16px;
  background:none;border:0;border-radius:0;font-family:var(--mono);font-size:11px;font-weight:500;
  letter-spacing:.14em;line-height:1.5;text-transform:uppercase;color:var(--aqua)}
@@POL :is(.pys-privacy-title,.pys-policy-title){font-family:var(--optima);font-size:clamp(36px,5vw,62px);
  line-height:1.03;letter-spacing:-.018em;font-weight:400;color:var(--tinta);margin-top:0;margin-bottom:18px}
@@POL .pys-policy-title{max-width:20ch}
@@POL :is(.pys-privacy-intro,.pys-policy-copy){font-size:clamp(17px,1.35vw,19px);line-height:1.65;
  color:var(--tinta-2);margin-top:0;margin-bottom:24px}
@@POL .pys-policy-copy{max-width:60ch;margin-bottom:0}
@@POL .pys-policy-hero{max-width:none;margin:0}
@@POL .pys-privacy-line{width:56px;height:1px;margin-top:0;margin-bottom:6px;background:var(--magenta);
  background-image:none;border-radius:0;opacity:.85}

/* secciones numeradas: separadas por una línea, sin caja */
@@POL .pys-privacy-section{margin:1.7em 0 0;padding:1.5em 0 0;background:none;border:0;
  border-top:1px solid var(--linea);border-radius:0}
@@POL .pys-privacy-line + .pys-privacy-section{margin-top:1.4em;padding-top:0;border-top:0}
@@POL :is(.pys-privacy-card,.pys-policy-card) h2{font-size:clamp(22px,2.3vw,28px);line-height:1.18;
  letter-spacing:-.01em;margin:0 0 .6em;color:var(--tinta)}
@@POL .pys-privacy-card > h2{margin-top:1.9em}
@@POL :is(.pys-privacy-card,.pys-policy-card) h3{font-size:19.5px;line-height:1.3;letter-spacing:0;
  margin:1.6em 0 .45em;color:var(--tinta)}
@@POL :is(.pys-privacy-card,.pys-policy-card) :is(p,li){font-size:16.5px;line-height:1.72;color:var(--tinta-2)}
@@POL :is(.pys-privacy-card,.pys-policy-card) p{margin:0 0 .9em}
@@POL :is(.pys-privacy-card,.pys-policy-card) :is(strong,b){color:var(--tinta);font-weight:600}
@@POL :is(.pys-privacy-card,.pys-policy-card) em{color:var(--tinta-3);font-style:italic}
@@POL :is(.pys-privacy-card,.pys-policy-card) ul{display:block;list-style:disc;padding:0 0 0 1.25em;
  margin:.4em 0 1.1em;gap:0}
@@POL :is(.pys-privacy-card,.pys-policy-card) li{position:static;padding:0;margin:0 0 .42em}
@@POL :is(.pys-privacy-card,.pys-policy-card) li::before{display:none;content:none}
@@POL :is(.pys-privacy-card,.pys-policy-card) li::marker{color:var(--magenta)}
/* listas de enlaces: texto claro con el subrayado magenta, más calmado que
   una columna entera en magenta */
@@POL :is(.pys-privacy-card,.pys-policy-card) li a{color:var(--tinta);
  text-decoration-color:color-mix(in srgb,var(--magenta) 55%,transparent)}
@@POL :is(.pys-privacy-card,.pys-policy-card) li a:hover{color:var(--magenta)}
@@POL :is(.pys-privacy-card,.pys-policy-card) hr{height:0;margin:2.2em 0 1.8em;border:0;
  border-top:1px solid var(--linea);background:none;color:transparent}
@@POL .pys-privacy-card > hr + h2{margin-top:0}
/* HTML mal cerrado en el documento: dos listas ul sin cerrar, así que lo que va
   detrás queda DENTRO de la lista y cada bloque se sangraba un nivel más
   (en el teléfono dejaba una columna de tres palabras). Se anula la sangría
   de esas listas «rotas» y solo sus li conservan viñeta y sangría. */
@@POL :is(.pys-privacy-card,.pys-policy-card) ul:has(> :not(li)){padding-left:0;list-style:none}
@@POL :is(.pys-privacy-card,.pys-policy-card) ul:has(> :not(li)) > li{margin-left:1.25em;list-style:disc}
@@POL :is(.pys-privacy-card,.pys-policy-card) p:empty{display:none}

/* contacto de privacidad: el recuadro de estado de la portada */
@@POL .pys-privacy-contact{margin:2.4em 0 0;padding:clamp(22px,3.5vw,34px);background:var(--carbon-2);
  border:1px solid var(--linea-2);border-top:2px solid var(--aqua);border-radius:3px;text-align:left}
@@POL .pys-privacy-contact h2{font-size:clamp(24px,2.6vw,32px);margin:0 0 10px}
@@POL .pys-privacy-contact p{max-width:none;margin:0 0 20px;font-size:16px}

/* envíos: rejilla de 2 + 1. La tercera tarjeta trae casi toda la prosa de
   la página; en tres columnas medía 290 px de ancho y 30 000 de alto, y
   estiraba las otras dos hasta ese alto vacías. Va a lo ancho, con la misma
   columna de lectura que la política de privacidad. */
@@POL .pys-policy-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;
  margin-top:clamp(28px,4vw,44px)}
@@POL .pys-policy-card{position:relative;min-height:0;overflow:visible;padding:clamp(22px,3vw,34px);
  background:var(--carbon);border:1px solid var(--linea);border-radius:3px}
@@POL .pys-policy-card:nth-child(3){grid-column:1 / -1;padding:clamp(26px,4vw,48px) clamp(22px,3vw,34px)}
@@POL .pys-policy-card:nth-child(3) > *{max-width:680px}
@@POL .pys-policy-card h2{font-size:clamp(23px,2.3vw,29px)}
@@POL .pys-policy-card > ul:first-of-type{margin-bottom:0}

@@POL .pys-policy-highlight{grid-column:1 / -1;display:grid;grid-template-columns:minmax(0,1fr) auto;
  gap:20px 32px;align-items:center;margin:0;padding:clamp(22px,3.5vw,40px);background:var(--carbon-2);
  border:1px solid var(--linea-2);border-top:2px solid var(--aqua);border-radius:3px;color:var(--tinta)}
@@POL .pys-policy-highlight h2{font-size:clamp(24px,2.8vw,34px);line-height:1.1;margin:0 0 10px;color:var(--tinta)}
@@POL .pys-policy-highlight p{font-size:16px;line-height:1.65;color:var(--tinta-2);margin:0}
@@POL .pys-policy-actions{display:flex;flex-wrap:wrap;gap:12px;justify-content:flex-end}
@@POL .pys-policy-note{margin:18px 0 0;padding:16px 0 0;background:none;border:0;border-top:1px solid var(--linea);
  border-radius:0;color:var(--tinta-3);font-size:13.5px;line-height:1.6;max-width:78ch}

/* botones: los de la base (.btn / .btn.pri) */
@@POL :is(.pys-privacy-btn,.pys-policy-btn){display:inline-flex;align-items:center;justify-content:center;
  gap:9px;width:auto;min-height:0;padding:14px 26px;border:1px solid var(--linea-2);border-radius:2px;
  background:transparent;color:var(--tinta);-webkit-text-fill-color:currentColor;font-family:var(--optima);
  font-size:16px;font-weight:400;line-height:1.2;letter-spacing:0;text-transform:none;text-decoration:none;
  transition:border-color .2s,background .2s}
@@POL :is(.pys-privacy-btn,.pys-policy-btn):hover{border-color:var(--tinta)}
@@POL :is(.pys-privacy-btn,.pys-policy-btn-primary){background:var(--magenta);border-color:var(--magenta);color:#fff}
@@POL :is(.pys-privacy-btn,.pys-policy-btn-primary):hover{background:#FF3D97;border-color:#FF3D97;color:#fff}

@media (max-width:760px){
  @@POL .pys-policy-grid{grid-template-columns:1fr}
  @@POL .pys-policy-highlight{grid-template-columns:1fr}
  @@POL .pys-policy-actions{justify-content:flex-start}
}
@media (max-width:480px){
  @@POL :is(.pys-privacy-btn,.pys-policy-btn){width:100%}
}

/* ════════════════════════════════════════════════════════════════════
   2 · AVISO EMERGENTE (23, 24, 643) — #pys-urgent-popup
   Se abre solo a los 4 s. No se toca su `display` (lo gobierna su JS).
   ════════════════════════════════════════════════════════════════════ */
@@POP #pys-urgent-popup.pys-urgent-popup{background:rgba(5,9,8,.84);padding:20px}
@@POP #pys-urgent-popup .pys-urgent-card{max-width:520px;padding:clamp(28px,4vw,40px) clamp(22px,4vw,36px) clamp(24px,3.5vw,32px);
  background:var(--carbon);border:1px solid var(--linea-2);border-radius:3px;
  box-shadow:0 40px 90px -40px rgba(0,0,0,.9);color:var(--tinta);font-family:var(--optima);text-align:left}
@@POP #pys-urgent-popup .pys-urgent-close{top:12px;right:12px;width:34px;height:34px;padding:0;display:grid;
  place-items:center;background:transparent;border:1px solid var(--linea-2);border-radius:2px;color:var(--tinta-2);
  font-family:var(--mono);font-size:18px;line-height:1;transition:border-color .2s,color .2s}
@@POP #pys-urgent-popup .pys-urgent-close:hover{background:transparent;border-color:var(--tinta);color:var(--tinta)}
@@POP #pys-urgent-popup .pys-urgent-topline{display:flex;align-items:center;gap:9px;max-width:calc(100% - 44px);
  margin:0 0 18px;padding:0;background:none;border:0;border-radius:0;font-family:var(--mono);font-size:11px;
  font-weight:500;letter-spacing:.12em;line-height:1.5;text-transform:uppercase;color:var(--aqua);justify-content:flex-start}
@@POP #pys-urgent-popup .pys-urgent-dot{width:7px;height:7px;flex:none;border-radius:50%;background:var(--magenta)}
@@POP #pys-urgent-popup .pys-urgent-title{max-width:none;margin:0 0 16px;font-family:var(--optima);
  font-size:clamp(27px,4vw,38px);line-height:1.08;letter-spacing:-.012em;font-weight:400;color:var(--tinta)}
@@POP #pys-urgent-popup .pys-urgent-title::after{display:block;content:"";width:56px;height:1px;margin:18px 0 0;
  border-radius:0;background:var(--magenta)}
@@POP #pys-urgent-popup .pys-urgent-text{max-width:none;margin:0 0 18px;font-size:16.5px;line-height:1.6;
  font-weight:400;color:var(--tinta-2)}
@@POP #pys-urgent-popup .pys-urgent-text strong{color:var(--tinta);font-weight:600}
@@POP #pys-urgent-popup .pys-urgent-highlight{max-width:none;margin:0 0 12px;padding:13px 16px;background:var(--carbon-2);
  border:1px solid var(--linea-2);border-left:2px solid var(--aqua);border-radius:2px;color:var(--tinta);
  font-size:15px;font-weight:400;line-height:1.45}
@@POP #pys-urgent-popup .pys-urgent-subnote{margin:0 0 22px;font-family:var(--mono);font-size:11px;font-weight:400;
  letter-spacing:.05em;color:var(--tinta-3)}
@@POP #pys-urgent-popup .pys-urgent-btn{display:flex;align-items:center;justify-content:center;width:100%;max-width:none;
  min-height:0;padding:14px 22px;background:var(--magenta);border:1px solid var(--magenta);border-radius:2px;
  color:#fff;-webkit-text-fill-color:#fff;font-family:var(--optima);font-size:16px;font-weight:400;
  letter-spacing:0;text-transform:none;text-decoration:none}
@@POP #pys-urgent-popup .pys-urgent-btn:hover{background:#FF3D97;border-color:#FF3D97}

/* ════════════════════════════════════════════════════════════════════
   3 · PIEZAS COMUNES DE LAS INFORMATIVAS (23, 24, 26, 643, 1166)
   ════════════════════════════════════════════════════════════════════ */
@@INF :is(.pys-metabolismo-page,.pys-recovery-page,.pys-longevity-page,.pys-performance-page,.pys-supp-redesign){
  background:none;color:var(--tinta);padding:0;margin:0}
@@INF :is(.pys-bg,.pys-longevity-bg,.pys-performance-bg){background:none;opacity:1}
@@INF :is(.pys-container,.pys-longevity-container,.pys-performance-container,.pys-wrap){width:100%;max-width:none;
  margin-inline:0;padding-inline:0}
/* separadores con punto y halo → una línea de 1 px */
@@INF :is(.pys-divider,.pys-longevity-divider,.pys-performance-divider,.pys-section-divider){display:block;width:100%;
  max-width:none;height:1px;margin:0;padding:0;background:var(--linea);opacity:1}
@@INF :is(.pys-divider,.pys-longevity-divider,.pys-performance-divider) span{display:none}

/* ladillos y etiquetas: mono, pequeños, en mayúsculas */
@@INF :is(.pys-kicker,.pys-longevity-kicker,.pys-performance-kicker,.pys-eyebrow,.pys-product-tag,.pys-product-label,
  .pys-longevity-product-label,.pys-performance-product-label,.pys-metric-kicker){display:inline-flex;align-items:center;
  gap:9px;width:auto;max-width:100%;margin:0 0 14px;padding:0;background:none;border:0;border-radius:0;
  font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.12em;line-height:1.5;
  text-transform:uppercase;color:var(--aqua);-webkit-text-fill-color:currentColor}

/* cabeceras de sección */
@@INF :is(.pys-section-head,.pys-longevity-section-head,.pys-performance-section-head,.pys-heading){max-width:none;
  margin:0 0 clamp(24px,3vw,40px);padding:0;text-align:left}
@@INF :is(.pys-section-head,.pys-longevity-section-head,.pys-performance-section-head).center,
@@INF .pys-heading{text-align:center}
@@INF :is(.pys-section-head,.pys-longevity-section-head,.pys-performance-section-head,.pys-heading) h2{
  font-size:clamp(28px,3.6vw,48px);line-height:1.08;letter-spacing:-.015em;margin:0 0 14px;max-width:24ch}
@@INF :is(.pys-section-head,.pys-longevity-section-head,.pys-performance-section-head).center h2,
@@INF .pys-heading h2{margin-inline:auto}
@@INF :is(.pys-section-head,.pys-longevity-section-head,.pys-performance-section-head,.pys-heading) p{
  font-size:16.5px;line-height:1.65;color:var(--tinta-2);max-width:64ch;margin:0 0 10px}
@@INF :is(.pys-section-head,.pys-longevity-section-head,.pys-performance-section-head).center p,
@@INF .pys-heading p{margin-inline:auto}

/* botones: .btn / .btn.pri de la base */
@@INF :is(.pys-hero-actions,.pys-longevity-actions,.pys-performance-actions,.pys-actions){display:flex;flex-wrap:wrap;
  gap:12px;margin-top:26px;justify-content:flex-start}
@@INF .center-actions{justify-content:center}
@@INF :is(.pys-btn,.pys-btn-primary,.pys-btn-secondary,.pys-longevity-btn-primary,.pys-performance-btn-primary,
  .pys-product-btn,.pys-longevity-product-btn,.pys-performance-product-btn,.pys-product-link,.pys-product-wa){
  display:inline-flex;align-items:center;justify-content:center;gap:9px;width:auto;min-height:0;padding:14px 26px;
  border:1px solid var(--linea-2);border-radius:2px;background:transparent;color:var(--tinta);
  -webkit-text-fill-color:currentColor;font-family:var(--optima);font-size:16px;font-weight:400;line-height:1.2;
  letter-spacing:0;text-transform:none;text-decoration:none;text-align:center;
  transition:border-color .2s,background .2s,color .2s}
@@INF :is(.pys-btn,.pys-btn-primary,.pys-btn-secondary,.pys-longevity-btn-primary,.pys-performance-btn-primary,
  .pys-product-btn,.pys-longevity-product-btn,.pys-performance-product-btn,.pys-product-link,.pys-product-wa):hover{
  border-color:var(--tinta);color:var(--tinta)}
@@INF :is(.pys-btn-primary,.pys-longevity-btn-primary,.pys-performance-btn-primary,.pys-product-btn,
  .pys-longevity-product-btn,.pys-performance-product-btn,.pys-product-link){background:var(--magenta);
  border-color:var(--magenta);color:#fff}
@@INF :is(.pys-btn-primary,.pys-longevity-btn-primary,.pys-performance-btn-primary,.pys-product-btn,
  .pys-longevity-product-btn,.pys-performance-product-btn,.pys-product-link):hover{background:#FF3D97;
  border-color:#FF3D97;color:#fff}

/* iconos: cuadro de 44 px con borde fino y trazo aqua */
@@INF :is(.pys-icon,.pys-longevity-icon,.pys-performance-icon,.pys-mini-icon,.pys-benefit-icon){position:relative;
  display:grid;place-items:center;width:44px;height:44px;margin:0 0 20px;padding:0;background:transparent;
  border:1px solid var(--linea-2);border-radius:2px;color:var(--aqua);-webkit-text-fill-color:currentColor;
  font-size:19px;line-height:1;z-index:auto}
@@INF :is(.pys-icon,.pys-longevity-icon,.pys-performance-icon,.pys-mini-icon,.pys-benefit-icon) svg{display:block;
  width:22px;height:22px}

/* rejillas de ventajas: celdas unidas por una línea de 1 px, como las
   categorías de la portada */
@@INF :is(.pys-benefit-grid,.pys-longevity-benefit-grid,.pys-performance-benefit-grid,.pys-benefits-grid,
  .pys-faq-grid,.pys-longevity-faq-grid,.pys-mini-grid),@@SUP .pys-benefits{display:grid;gap:1px;background:var(--linea);
  border:1px solid var(--linea);border-radius:3px;overflow:hidden}
@@INF :is(.pys-benefit-card,.pys-longevity-benefit-card,.pys-performance-benefit-card,.pys-benefit,.pys-faq-card,
  .pys-longevity-faq-card,.pys-mini-card){position:relative;min-height:0;margin:0;padding:clamp(22px,2.4vw,30px);
  background:var(--carbon);border:0;border-radius:0;overflow:visible;transition:background .22s}
@@INF :is(.pys-benefit-card,.pys-longevity-benefit-card,.pys-performance-benefit-card,.pys-benefit):hover{
  background:var(--carbon-2)}
@@INF :is(.pys-benefit-card,.pys-longevity-benefit-card,.pys-performance-benefit-card).featured{
  box-shadow:inset 0 2px 0 var(--magenta)}
@@INF :is(.pys-benefit-card,.pys-longevity-benefit-card,.pys-performance-benefit-card,.pys-benefit) h3{
  position:relative;font-size:20px;line-height:1.22;letter-spacing:-.005em;margin:0 0 8px;color:var(--tinta)}
@@INF :is(.pys-benefit-card,.pys-longevity-benefit-card,.pys-performance-benefit-card,.pys-benefit) p{
  position:relative;font-size:15px;line-height:1.62;margin:0;color:var(--tinta-2)}
@@INF :is(.pys-faq-card,.pys-longevity-faq-card) h3{font-size:19px;line-height:1.28;margin:0 0 8px;color:var(--tinta)}
@@INF :is(.pys-faq-card,.pys-longevity-faq-card) p{font-size:15.5px;line-height:1.65;margin:0;color:var(--tinta-2)}

/* desplegables de preguntas: los de la portada */
@@INF :is(.pys-faq-list,.pys-faq){display:block;max-width:none;margin:0;padding:0;border-top:1px solid var(--linea)}
@@INF :is(.pys-faq-item,.pys-faq details){margin:0;padding:0;background:none;border:0;border-bottom:1px solid var(--linea);
  border-radius:0;overflow:visible}
@@INF :is(.pys-faq-item,.pys-faq details) summary{display:flex;align-items:baseline;justify-content:flex-start;gap:14px;
  padding:18px 0;margin:0;list-style:none;cursor:pointer;font-family:var(--optima);font-size:18px;font-weight:400;
  line-height:1.4;letter-spacing:0;text-align:left;color:var(--tinta);background:none;transition:color .2s}
@@INF :is(.pys-faq-item,.pys-faq details) summary::-webkit-details-marker{display:none}
@@INF :is(.pys-faq-item,.pys-faq details) summary:hover{color:var(--magenta)}
@@INF :is(.pys-faq-item,.pys-faq details) summary::after{order:-1;flex:none;display:inline;width:auto;height:auto;
  margin:0;padding:0;background:none;border:0;border-radius:0;font-family:var(--mono);font-size:15px;
  font-weight:400;line-height:1;color:var(--magenta)}
@@INF :is(.pys-faq-content,.pys-faq details > p){padding:0 0 18px 28px;margin:0;max-width:66ch}
@@INF :is(.pys-faq-content p,.pys-faq details > p){font-size:16px;line-height:1.65;color:var(--tinta-2);margin:0}

/* vitrina de producto: el fondo claro de la portada para las fotos de
   producto, que vienen sobre blanco. Si una imagen no carga, el texto
   alternativo sale en mono oscuro dentro de la vitrina. */
@@INF :is(.pys-product-img,.pys-longevity-product-img,.pys-performance-product-img,.pys-product-media){position:relative;
  display:flex;align-items:center;justify-content:center;min-height:0;margin:0;overflow:hidden;
  background:radial-gradient(120% 86% at 50% 10%,#FFFFFF 0%,var(--vitrina) 58%,#DDE5E2 100%);border:0;border-radius:0;
  color:#5E7A74;text-decoration:none}
@@INF :is(.pys-product-img,.pys-longevity-product-img,.pys-performance-product-img,.pys-product-media) img{position:relative;
  z-index:1;display:block;width:auto;max-width:100%;height:auto;max-height:100%;object-fit:contain;margin:0 auto;
  font-family:var(--mono);font-size:11px;letter-spacing:.04em;line-height:1.5;color:#5E7A74;text-align:center}

/* tarjeta final */
@@INF :is(.pys-final-card,.pys-longevity-final-card,.pys-performance-final-card){position:relative;max-width:none;margin:0;
  padding:clamp(30px,5vw,64px) clamp(22px,4vw,56px);background:var(--carbon-2);border:1px solid var(--linea-2);
  border-radius:3px;overflow:hidden;text-align:center}
@@INF :is(.pys-final-card,.pys-longevity-final-card,.pys-performance-final-card) h2{font-size:clamp(28px,3.6vw,48px);
  line-height:1.08;letter-spacing:-.015em;margin:0 auto 14px;max-width:22ch;color:var(--tinta)}
@@INF :is(.pys-final-card,.pys-longevity-final-card,.pys-performance-final-card) p{font-size:16.5px;line-height:1.65;
  color:var(--tinta-2);margin:0 auto;max-width:62ch}
@@INF :is(.pys-final-card,.pys-longevity-final-card,.pys-performance-final-card)
  :is(.pys-hero-actions,.pys-longevity-actions,.pys-performance-actions,.pys-actions){justify-content:center}

/* ════════════════════════════════════════════════════════════════════
   4 · PLANTILLA COMPARTIDA 24 / 26 / 643
   ════════════════════════════════════════════════════════════════════ */
@@TRI :is(.pys-hero,.pys-longevity-hero,.pys-performance-hero){position:relative;padding-block:clamp(36px,5.5vw,84px)}
@@TRI :is(.pys-hero-grid,.pys-longevity-hero-grid,.pys-performance-hero-grid){display:grid;
  grid-template-columns:minmax(0,1.06fr) minmax(0,.94fr);gap:clamp(24px,5vw,72px);align-items:center}
@@TRI :is(.pys-hero,.pys-longevity-hero,.pys-performance-hero) h1{font-size:clamp(38px,5.2vw,70px);line-height:1.02;
  letter-spacing:-.02em;margin:0 0 20px;max-width:15ch;color:var(--tinta)}
@@TRI :is(.pys-hero,.pys-longevity-hero,.pys-performance-hero) h1 strong{display:block;margin-top:.24em;font-size:.56em;
  line-height:1.12;letter-spacing:-.01em}
@@TRI :is(.pys-hero-copy,.pys-longevity-copy,.pys-performance-copy){position:relative;padding:0;background:none}
@@TRI :is(.pys-hero-copy,.pys-longevity-copy,.pys-performance-copy) > p{font-size:clamp(16px,1.3vw,18.5px);line-height:1.65;
  color:var(--tinta-2);max-width:50ch;margin:0 0 12px}

/* El visual del héroe: tres tarjetas flotantes encima de un orbe animado,
   posicionadas a mano (en rendimiento deportivo una tapaba el texto de
   otra). Pasa a ser un panel con las tres como filas numeradas, igual que
   los pasos de la portada. */
@@TRI :is(.pys-hero-visual,.pys-longevity-visual,.pys-performance-visual){position:relative;display:block;min-height:0;
  height:auto;padding:0;margin:0;overflow:hidden;background:var(--carbon);border:1px solid var(--linea-2);
  border-radius:3px;box-shadow:0 40px 90px -40px rgba(0,0,0,.9)}
@@TRI :is(.pys-orb,.pys-longevity-orb,.pys-performance-orb){position:static;display:block;inset:auto;width:auto;
  height:auto;margin:0;padding:0;background:none;border:0;border-radius:0;opacity:1}
@@TRI :is(.pys-floating-card,.pys-longevity-floating,.pys-performance-floating){position:relative;inset:auto;top:auto;
  right:auto;bottom:auto;left:auto;z-index:auto;display:grid;grid-template-columns:44px minmax(0,1fr);column-gap:14px;
  align-items:baseline;width:auto;max-width:none;min-height:0;margin:0;padding:22px clamp(18px,2.2vw,26px);
  background:none;border:0;border-bottom:1px solid var(--linea);border-radius:0}
@@TRI :is(.pys-floating-card,.pys-longevity-floating,.pys-performance-floating):last-child{border-bottom:0}
@@TRI :is(.pys-floating-card,.pys-longevity-floating,.pys-performance-floating) > span{grid-row:1 / span 2;display:block;
  width:auto;height:auto;margin:0;padding:0;background:none;border:0;font-family:var(--mono);font-size:11.5px;
  font-weight:500;letter-spacing:.1em;color:var(--magenta);-webkit-text-fill-color:currentColor}
@@TRI :is(.pys-floating-card,.pys-longevity-floating,.pys-performance-floating) > strong{display:block;margin:0 0 4px;
  font-size:21px;line-height:1.2;font-weight:400;color:var(--tinta)}
@@TRI :is(.pys-floating-card,.pys-longevity-floating,.pys-performance-floating) > p{grid-column:2;margin:0;font-size:15px;
  line-height:1.55;color:var(--tinta-2)}

@@TRI :is(.pys-section,.pys-longevity-section,.pys-performance-section,.pys-final-section,.pys-longevity-final-section,
  .pys-performance-final-section){position:relative;padding-block:clamp(48px,6vw,96px);background:none;overflow:visible}
@@TRI .pys-benefit-grid,@@TRI .pys-performance-benefit-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
@@TRI .pys-longevity-benefit-grid{grid-template-columns:repeat(4,minmax(0,1fr))}
@@TRI :is(.pys-faq-grid,.pys-longevity-faq-grid){grid-template-columns:repeat(2,minmax(0,1fr))}
@@TRI .pys-longevity-faq-card.wide{grid-column:1 / -1}

/* ciencia aplicada (24, 643): texto + pasos numerados */
@@TRI :is(.pys-science-grid,.pys-performance-science-grid){display:grid;grid-template-columns:minmax(0,.95fr) minmax(0,1.05fr);
  gap:clamp(24px,4.5vw,70px);align-items:start}
@@TRI :is(.pys-science-copy,.pys-performance-science-copy){padding:0;background:none;border:0;border-radius:0}
@@TRI :is(.pys-science-copy,.pys-performance-science-copy) h2{font-size:clamp(28px,3.4vw,46px);line-height:1.08;
  letter-spacing:-.015em;margin:0 0 16px;max-width:18ch}
@@TRI :is(.pys-science-copy,.pys-performance-science-copy) p{font-size:16.5px;line-height:1.7;margin:0 0 12px;
  max-width:52ch;color:var(--tinta-2)}
@@TRI :is(.pys-science-panel,.pys-performance-science-panel){display:block;padding:0;margin:0;background:none;border:0;
  border-top:1px solid var(--linea)}
@@TRI :is(.pys-step,.pys-performance-step){display:grid;grid-template-columns:44px minmax(0,1fr);gap:14px;
  align-items:baseline;margin:0;padding:20px 0;background:none;border:0;border-bottom:1px solid var(--linea);border-radius:0}
@@TRI :is(.pys-step,.pys-performance-step) > span{display:block;width:auto;height:auto;min-width:0;margin:0;padding:0;
  background:none;border:0;border-radius:0;font-family:var(--mono);font-size:11.5px;font-weight:500;letter-spacing:.1em;
  line-height:1.6;color:var(--magenta);-webkit-text-fill-color:currentColor}
@@TRI :is(.pys-step,.pys-performance-step) h3{font-size:19.5px;line-height:1.25;margin:0 0 5px;color:var(--tinta)}
@@TRI :is(.pys-step,.pys-performance-step) p{font-size:15px;line-height:1.6;margin:0;color:var(--tinta-2)}

/* recuperación muscular + péptidos (solo 24) */
@@TRI .pys-peptide-recovery-grid{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);
  gap:clamp(24px,4.5vw,70px);align-items:start}
@@TRI .pys-peptide-media{position:relative;align-self:stretch;min-height:440px;margin:0;padding:0;overflow:hidden;
  background:var(--carbon);border:1px solid var(--linea-2);border-radius:3px;box-shadow:0 40px 90px -40px rgba(0,0,0,.9)}
@@TRI .pys-peptide-media img{position:absolute;inset:0;display:block;width:100%;height:100%;min-height:0;max-height:none;
  object-fit:cover;object-position:50% 40%}
@@TRI .pys-media-badge{position:absolute;left:14px;right:14px;bottom:14px;top:auto;z-index:2;padding:12px 14px;
  background:color-mix(in srgb,var(--negro) 86%,transparent);border:1px solid var(--linea-2);border-radius:2px}
@@TRI .pys-media-badge span{display:block;margin:0 0 4px;font-family:var(--mono);font-size:10.5px;font-weight:500;
  letter-spacing:.12em;text-transform:uppercase;color:var(--aqua)}
@@TRI .pys-media-badge strong{display:block;font-size:20px;line-height:1.2;font-weight:400;color:var(--tinta)}
@@TRI .pys-peptide-copy{position:relative;padding:0;background:none;border:0;border-radius:0}
@@TRI .pys-peptide-copy h2{font-size:clamp(26px,3vw,40px);line-height:1.1;letter-spacing:-.015em;margin:0 0 16px;max-width:24ch}
@@TRI .pys-peptide-copy > p{font-size:16.5px;line-height:1.7;margin:0 0 12px;max-width:62ch;color:var(--tinta-2)}
@@TRI .pys-mini-grid{grid-template-columns:repeat(3,minmax(0,1fr));margin:24px 0 4px}
@@TRI .pys-mini-card{padding:18px 16px}
@@TRI .pys-mini-icon{width:36px;height:36px;margin-bottom:14px}
@@TRI .pys-mini-icon svg{width:18px;height:18px}
@@TRI .pys-mini-card strong{display:block;margin:0 0 6px;font-size:17px;line-height:1.25;font-weight:400;color:var(--tinta)}
@@TRI .pys-mini-card p{font-size:14px;line-height:1.55;margin:0;color:var(--tinta-2)}

/* productos: tarjeta ancha, vitrina + ficha, alternando lado */
@@TRI :is(.pys-product-grid,.pys-longevity-product-grid,.pys-performance-product-grid){display:grid;
  grid-template-columns:1fr;gap:16px}
@@TRI :is(.pys-product-card,.pys-longevity-product-card,.pys-performance-product-card){position:relative;display:grid;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr);min-height:0;margin:0;padding:0;overflow:hidden;
  background:var(--carbon);border:1px solid var(--linea-2);border-radius:3px;transition:border-color .22s}
@@TRI :is(.pys-product-card,.pys-longevity-product-card,.pys-performance-product-card):nth-child(even){
  grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
@@TRI :is(.pys-product-card,.pys-longevity-product-card,.pys-performance-product-card):hover{
  border-color:color-mix(in srgb,var(--magenta) 55%,transparent)}
@@TRI :is(.pys-product-img,.pys-longevity-product-img,.pys-performance-product-img){aspect-ratio:3 / 2;
  padding:clamp(20px,3vw,40px)}
@@TRI :is(.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content){position:relative;
  display:flex;flex-direction:column;justify-content:center;align-items:flex-start;padding:clamp(24px,3.5vw,48px);
  background:none;border:0}
@@TRI :is(.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content) h3{
  font-size:clamp(26px,3vw,38px);line-height:1.08;letter-spacing:-.015em;margin:0 0 12px;color:var(--tinta)}
@@TRI :is(.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content) > p{font-size:16px;
  line-height:1.65;margin:0 0 14px;max-width:52ch;color:var(--tinta-2)}
@@TRI :is(.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content) ul{display:flex;
  flex-direction:column;gap:7px;list-style:none;margin:4px 0 24px;padding:0}

/* ════════════════════════════════════════════════════════════════════
   5 · CÓMO ACELERAR EL METABOLISMO (23)
   ════════════════════════════════════════════════════════════════════ */
@@MET .pys-hero{position:relative;padding-block:clamp(36px,5.5vw,84px);background:none;overflow:visible}
@@MET .pys-hero-grid{display:grid;grid-template-columns:minmax(0,1.06fr) minmax(0,.94fr);gap:clamp(24px,5vw,72px);
  align-items:center}
@@MET .pys-hero-copy{padding:0;background:none}
@@MET .pys-hero h1{font-size:clamp(36px,4.6vw,62px);line-height:1.04;letter-spacing:-.02em;margin:0 0 20px;max-width:17ch}
@@MET .pys-hero-copy > p{font-size:clamp(16px,1.3vw,18px);line-height:1.65;color:var(--tinta-2);max-width:52ch;margin:0 0 12px}
@@MET .pys-trust-row{display:flex;flex-wrap:wrap;justify-content:flex-start;gap:9px;margin-top:24px}
@@MET .pys-trust-chip{display:inline-block;padding:7px 12px;background:none;border:1px solid var(--linea-2);
  border-radius:2px;font-family:var(--mono);font-size:11px;font-weight:400;letter-spacing:.05em;line-height:1.4;
  text-transform:none;color:var(--tinta-2)}
@@MET .pys-hero-panel{position:relative;display:block;padding:0;margin:0;overflow:hidden;background:var(--carbon);
  border:1px solid var(--linea-2);border-radius:3px;box-shadow:0 40px 90px -40px rgba(0,0,0,.9)}
@@MET .pys-metric-card{margin:0;padding:22px clamp(18px,2.2vw,26px);background:none;border:0;
  border-bottom:1px solid var(--linea);border-radius:0}
@@MET .pys-metric-card:last-child{border-bottom:0}
@@MET .pys-metric-kicker{margin-bottom:8px}
@@MET .pys-metric-title{font-size:21px;line-height:1.22;font-weight:400;letter-spacing:-.005em;margin:0 0 6px;color:var(--tinta)}
@@MET .pys-metric-text{font-size:15px;line-height:1.6;color:var(--tinta-2)}
@@MET .pys-section{position:relative;padding-block:clamp(48px,6vw,96px);background:none;overflow:visible}
@@MET .pys-benefits-grid{grid-template-columns:repeat(4,minmax(0,1fr))}
@@MET .pys-benefit-card h3{margin-top:0}

@@MET .pys-faq-wrap{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:clamp(24px,4vw,64px);align-items:start}
@@MET .pys-faq-intro{position:relative;padding:0;margin:0;background:none;border:0;border-radius:0}
@@MET .pys-faq-intro h2{font-size:clamp(28px,3.2vw,42px);line-height:1.08;letter-spacing:-.015em;margin:0 0 14px;max-width:none}
@@MET .pys-faq-intro p{font-size:16.5px;line-height:1.65;color:var(--tinta-2);margin:0;max-width:44ch}

@@MET .pys-products-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
@@MET .pys-product-card{position:relative;display:flex;flex-direction:column;align-items:stretch;gap:0;min-height:0;margin:0;
  padding:0;overflow:hidden;
  background:var(--carbon);border:1px solid var(--linea-2);border-radius:3px;transition:border-color .22s}
@@MET .pys-product-card:hover{border-color:color-mix(in srgb,var(--magenta) 55%,transparent)}
@@MET .pys-product-media{width:100%;aspect-ratio:16 / 10;padding:clamp(18px,2.6vw,30px);border-bottom:1px solid var(--linea-2)}
@@MET .pys-product-card:nth-child(2) .pys-product-media{background:radial-gradient(120% 86% at 50% 10%,#FFFFFF 0%,var(--vitrina) 58%,#DDE5E2 100%)}
@@MET .pys-product-content{display:flex;flex-direction:column;align-items:flex-start;flex:1;padding:clamp(20px,2.6vw,32px);
  background:none}
@@MET .pys-product-content h3{font-size:clamp(24px,2.4vw,30px);line-height:1.1;letter-spacing:-.012em;margin:0 0 8px}
@@MET .pys-product-subtitle{font-size:16px;line-height:1.45;font-weight:400;color:var(--tinta);margin:0 0 12px;
  -webkit-text-fill-color:currentColor;background:none}
@@MET .pys-product-content > p{font-size:15.5px;line-height:1.65;color:var(--tinta-2);margin:0 0 12px}
@@MET .pys-product-points{display:flex;flex-direction:column;gap:7px;list-style:none;margin:2px 0 0;padding:0}
@@MET .pys-product-meta{display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:10px 14px;width:100%;
  margin:18px 0 20px;
  padding:14px 0 0;border-top:1px solid var(--linea)}
@@MET .pys-price{padding:0;background:none;border:0;border-radius:0;font-family:var(--mono);font-size:18px;font-weight:400;
  letter-spacing:0;font-variant-numeric:tabular-nums;color:var(--tinta);-webkit-text-fill-color:currentColor}
@@MET .pys-mini-note{display:inline-block;padding:6px 10px;background:color-mix(in srgb,var(--aqua) 7%,transparent);
  border:1px solid color-mix(in srgb,var(--aqua) 42%,transparent);border-radius:2px;font-family:var(--mono);font-size:11px;
  font-weight:400;letter-spacing:.04em;line-height:1.4;color:var(--aqua)}
@@MET .pys-product-content .pys-btn{margin-top:auto}
@@MET .pys-disclaimer{max-width:none;margin:16px 0 0;padding:14px 16px;background:none;border:1px solid var(--linea);
  border-radius:3px;font-size:13.5px;font-weight:400;line-height:1.6;text-align:left;color:var(--tinta-3)}

/* viñetas de las fichas de producto: la raya magenta de la portada */
@@INF :is(.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content,.pys-product-points) li{
  position:relative;display:flex;gap:10px;align-items:baseline;margin:0;padding:0;font-size:15.5px;line-height:1.5;
  color:var(--tinta-2)}
@@INF :is(.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content,.pys-product-points) li::before{
  content:"—";position:static;display:inline;flex:none;width:auto;height:auto;margin:0;padding:0;background:none;
  border:0;border-radius:0;font-family:var(--mono);font-size:11px;font-weight:400;line-height:1;color:var(--magenta);
  -webkit-text-fill-color:currentColor}

/* ════════════════════════════════════════════════════════════════════
   6 · SUPLEMENTOS DEPORTIVOS (1166)
   ════════════════════════════════════════════════════════════════════ */
/* las piezas entran con un fundido al hacer scroll (JS propio): se dejan
   siempre visibles para que nada dependa de ese script */
@@SUP .pys-reveal{opacity:1;transform:none;transition:none}
@@SUP .pys-hero{padding-block:clamp(36px,5.5vw,84px);background:none}
@@SUP .pys-hero-card{position:relative;padding:0;margin:0;background:none;border:0;border-radius:0;overflow:visible}
@@SUP .pys-kicker i{display:inline-block;width:7px;height:7px;flex:none;border-radius:50%;background:var(--aqua)}
@@SUP .pys-hero-title{font-size:clamp(38px,5.2vw,70px);line-height:1.03;letter-spacing:-.02em;margin:0 0 20px;max-width:17ch}
@@SUP .pys-hero-copy{font-size:clamp(16px,1.35vw,18.5px);line-height:1.65;color:var(--tinta-2);max-width:56ch;margin:0}
@@SUP .pys-hero-badges{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;max-width:1000px;margin-top:36px;
  background:var(--linea);border:1px solid var(--linea);border-radius:3px;overflow:hidden}
@@SUP .pys-mini-stat{display:block;margin:0;padding:18px 20px;background:var(--carbon);border:0;border-radius:0}
@@SUP .pys-mini-stat strong{display:block;margin:0 0 5px;font-size:17px;line-height:1.25;font-weight:400;color:var(--tinta)}
@@SUP .pys-mini-stat span{display:block;font-size:14.5px;line-height:1.55;color:var(--tinta-2)}
@@SUP .pys-section{position:relative;padding-block:clamp(48px,6vw,96px);background:none;border:0;
  border-top:1px solid var(--linea);overflow:visible}
@@SUP .pys-heading{max-width:780px;margin-inline:auto}
@@SUP .pys-accent-line{width:56px;height:1px;margin:0 auto 18px;background:var(--magenta);background-image:none;
  border-radius:0;opacity:.85}
@@SUP .pys-section-title{font-size:clamp(28px,3.6vw,48px);line-height:1.08}
@@SUP .pys-benefits{grid-template-columns:repeat(4,minmax(0,1fr))}

@@SUP .pys-products{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
@@SUP .pys-product{position:relative;display:flex;flex-direction:column;min-height:0;margin:0;padding:0;overflow:hidden;
  background:var(--carbon);border:1px solid var(--linea-2);border-radius:3px;transition:border-color .22s}
@@SUP .pys-product:hover{border-color:color-mix(in srgb,var(--magenta) 55%,transparent)}
@@SUP .pys-product-media{aspect-ratio:1 / 1;padding:22px;border-bottom:1px solid var(--linea-2)}
@@SUP .pys-product-body{position:relative;display:flex;flex-direction:column;align-items:flex-start;flex:1;padding:18px;
  background:none}
@@SUP .pys-product-tag{margin-bottom:10px}
@@SUP .pys-product-body h3{font-size:20px;line-height:1.22;letter-spacing:-.005em;margin:0 0 8px;color:var(--tinta)}
@@SUP .pys-product-body > p{font-size:14.5px;line-height:1.6;margin:0;color:var(--tinta-2)}
@@SUP .pys-product-specs{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 18px}
@@SUP .pys-product-specs span{display:inline-block;padding:5px 8px;background:none;border:1px solid var(--linea-2);
  border-radius:2px;font-family:var(--mono);font-size:10.5px;font-weight:400;letter-spacing:.04em;line-height:1.4;
  color:var(--tinta-2)}
@@SUP .pys-product-links{display:flex;flex-direction:column;gap:8px;width:100%;margin-top:auto}
@@SUP :is(.pys-product-link,.pys-product-wa){width:100%;padding:12px 16px;font-size:15px}

@@SUP .pys-two-col{display:grid;grid-template-columns:minmax(0,.94fr) minmax(0,1.06fr);gap:clamp(24px,4vw,56px);align-items:start}
@@SUP .pys-info-stack{display:block;border-top:0}
@@SUP .pys-info-card{margin:0;padding:0 0 20px;background:none;border:0;border-bottom:1px solid var(--linea);border-radius:0}
@@SUP .pys-info-card + .pys-info-card{padding-top:20px}
@@SUP .pys-info-card strong{display:block;margin:0 0 6px;font-size:19px;line-height:1.25;font-weight:400;color:var(--tinta)}
@@SUP .pys-info-card p{font-size:15.5px;line-height:1.65;margin:0;color:var(--tinta-2)}
@@SUP .pys-panel{position:relative;margin:0;padding:clamp(22px,3.5vw,40px);background:var(--carbon);
  border:1px solid var(--linea-2);border-radius:3px;overflow:visible}
@@SUP .pys-panel-title{font-size:clamp(26px,3vw,38px);line-height:1.1;letter-spacing:-.015em;margin:0 0 14px}
@@SUP .pys-panel > p{font-size:16px;line-height:1.7;margin:0 0 6px;color:var(--tinta-2)}
@@SUP .pys-checklist{display:block;margin:18px 0 0;border-top:1px solid var(--linea)}
@@SUP .pys-check{display:grid;grid-template-columns:22px minmax(0,1fr);gap:10px;align-items:baseline;margin:0;
  padding:14px 0;background:none;border:0;border-bottom:1px solid var(--linea);border-radius:0}
@@SUP .pys-check > span{display:block;width:auto;height:auto;margin:0;padding:0;background:none;border:0;border-radius:0;
  font-family:var(--mono);font-size:13px;line-height:1.5;color:var(--aqua);-webkit-text-fill-color:currentColor}
@@SUP .pys-check > div{font-size:15.5px;line-height:1.6;color:var(--tinta-2)}
@@SUP .pys-check b{color:var(--tinta);font-weight:600}
@@SUP .pys-external{margin:20px 0 0;padding:16px 0 0;border-top:0;font-size:14.5px;line-height:1.6;color:var(--tinta-3)}
@@SUP .pys-reading-card{max-width:820px;margin:0 auto;padding:clamp(22px,3.5vw,40px);background:var(--carbon);
  border:1px solid var(--linea);border-radius:3px;color:var(--tinta-2)}
@@SUP .pys-reading-card p{font-size:16.5px;line-height:1.72;margin:0 0 .9em;color:var(--tinta-2)}
@@SUP .pys-reading-card p:last-child{margin-bottom:0}
@@SUP .pys-faq{max-width:900px;margin-inline:auto}
@@SUP .pys-final-cta{position:relative;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:22px 40px;align-items:center;
  margin:0;padding:clamp(26px,4vw,48px);background:var(--carbon-2);border:1px solid var(--linea-2);border-radius:3px;
  overflow:hidden;text-align:left}
@@SUP .pys-cta-title{font-size:clamp(26px,3vw,40px);line-height:1.1;letter-spacing:-.015em;margin:0 0 10px}
@@SUP .pys-final-cta p{font-size:16px;line-height:1.65;margin:0;color:var(--tinta-2);max-width:58ch}

/* ════════════════════════════════════════════════════════════════════
   7 · /pedido/ (29) — página vieja con el shortcode de finalizar compra;
   con el carrito vacío no pinta nada. Solo se le da la cabecera del sistema.
   ════════════════════════════════════════════════════════════════════ */
@@PED .page-header{position:relative;z-index:auto;width:100%;max-width:1320px;margin-inline:auto;
  padding:clamp(28px,4vw,56px) var(--gutter) 0}
@@PED .page-header .entry-title{max-width:none;margin:0;padding:0;font-family:var(--optima);font-weight:400;
  font-size:clamp(34px,4.4vw,56px);line-height:1.04;letter-spacing:-.015em;color:var(--tinta)}
@@PED .page-header::after{content:"";display:block;width:56px;height:1px;margin-top:20px;background:var(--magenta);opacity:.85}
@@PED .page-content{min-height:clamp(160px,32vh,420px)}
@@PED .elementor > .e-con.e-parent{padding-block:clamp(20px,3vw,40px)}

/* las hojas viejas centran casi todo por debajo de 640-767 px; el sistema
   compone a la izquierda (solo las cabeceras marcadas .center y las
   tarjetas finales van centradas) */
@@INF :is(.pys-hero-copy,.pys-longevity-copy,.pys-performance-copy,.pys-science-copy,.pys-performance-science-copy,
  .pys-peptide-copy,.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content,.pys-product-card,
  .pys-benefit-card,.pys-longevity-benefit-card,.pys-performance-benefit-card,.pys-benefit,.pys-faq-card,
  .pys-longevity-faq-card,.pys-mini-card,.pys-step,.pys-performance-step,.pys-floating-card,.pys-longevity-floating,
  .pys-performance-floating,.pys-metric-card,.pys-faq-intro,.pys-hero-card,.pys-product,.pys-product-body,
  .pys-info-card,.pys-panel,.pys-two-col,.pys-final-cta){text-align:left}
@@INF :is(.pys-product-content,.pys-longevity-product-content,.pys-performance-product-content,.pys-product-body,
  .pys-hero-copy,.pys-longevity-copy,.pys-performance-copy) :is(h1,h2,h3,p,ul){margin-inline:0}

/* ════════════════════════════════════════════════════════════════════
   8 · RESPONSIVO
   ════════════════════════════════════════════════════════════════════ */
@media (max-width:1100px){
  @@INF :is(.pys-longevity-benefit-grid,.pys-benefits-grid),@@SUP .pys-benefits{grid-template-columns:repeat(2,minmax(0,1fr))}
  @@SUP .pys-products{grid-template-columns:repeat(2,minmax(0,1fr))}
  @@SUP .pys-two-col{grid-template-columns:1fr}
}
@media (max-width:900px){
  @@TRI :is(.pys-hero-grid,.pys-longevity-hero-grid,.pys-performance-hero-grid,.pys-science-grid,
    .pys-performance-science-grid,.pys-peptide-recovery-grid){grid-template-columns:1fr}
  @@MET :is(.pys-hero-grid,.pys-faq-wrap){grid-template-columns:1fr}
  @@TRI :is(.pys-product-card,.pys-longevity-product-card,.pys-performance-product-card),
  @@TRI :is(.pys-product-card,.pys-longevity-product-card,.pys-performance-product-card):nth-child(even){grid-template-columns:1fr}
  @@TRI :is(.pys-product-card,.pys-longevity-product-card,.pys-performance-product-card):nth-child(even)
    :is(.pys-product-img,.pys-longevity-product-img,.pys-performance-product-img){order:0}
  @@TRI .pys-benefit-grid,@@TRI .pys-performance-benefit-grid{grid-template-columns:1fr}
  @@TRI .pys-peptide-media{align-self:auto;min-height:0;aspect-ratio:16 / 10}
  @@SUP .pys-final-cta{grid-template-columns:1fr}
}
@media (max-width:760px){
  @@MET .pys-products-grid{grid-template-columns:1fr}
  @@TRI :is(.pys-faq-grid,.pys-longevity-faq-grid,.pys-mini-grid){grid-template-columns:1fr}
  @@SUP .pys-hero-badges{grid-template-columns:1fr}
}
@media (max-width:560px){
  @@INF :is(.pys-longevity-benefit-grid,.pys-benefits-grid),@@SUP .pys-benefits{grid-template-columns:1fr}
  @@SUP .pys-products{grid-template-columns:1fr}
  @@SUP .pys-product-media{aspect-ratio:4 / 3}
  @@INF :is(.pys-hero-actions,.pys-longevity-actions,.pys-performance-actions,.pys-actions) > a{flex:1 1 auto}
  @@INF :is(.pys-faq-content,.pys-faq details > p){padding-left:0}
}
CSS;

	$css = preg_replace( '#/\*.*?\*/#s', '', $css );
	$css = strtr( $css, $ambitos );
	$css = pys_dis_pe_importante( $css );
	return trim( preg_replace( '/\s+/', ' ', $css ) );
}
