<?php
/**
 * Piezas de diseño compartidas por TODO el sitio.
 *
 * Aquí viven los tokens, la base tipográfica, el fondo hexagonal, el cintillo,
 * la cabecera y el pie. La portada y el resto de las plantillas usan estas
 * mismas funciones, de modo que el encabezado no puede acabar distinto en una
 * página que en otra.
 *
 * No contiene NADA específico del home.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * URL de una categoría de producto por su slug.
 *
 * Se resuelve con `get_term_link()` y no a mano, porque la ruta de una
 * categoría depende de si cuelga de otra: `bienestar-general` estuvo bajo
 * `suplementos` y su URL llevaba las dos. Si el término no existe, se devuelve
 * la ruta canónica para que el enlace no acabe en `home_url('')`.
 */
function pys_dis_cat_url( $slug ) {
	if ( taxonomy_exists( 'product_cat' ) ) {
		$termino = get_term_by( 'slug', $slug, 'product_cat' );
		if ( $termino && ! is_wp_error( $termino ) ) {
			$url = get_term_link( $termino );
			if ( ! is_wp_error( $url ) ) {
				return $url;
			}
		}
	}
	return home_url( '/product-category/' . $slug . '/' );
}

/**
 * Mapa de enlaces reales del sitio.
 *
 * Las claves `cat_*` son las SIETE categorías de producto de WooCommerce, que
 * es donde vive el catálogo de verdad; las landings por objetivo
 * (`metabolismo`, `reparacion`, `longevidad`, `performance`) siguen aquí
 * porque el pie las enlaza y son guías, pero ya no son la navegación del
 * catálogo: entre las cuatro solo enseñaban 5 productos distintos.
 */
function pys_dis_enlaces() {
	static $u = null;
	if ( null !== $u ) {
		return $u;
	}
	$u = array(
		'inicio'       => home_url( '/' ),
		'coa'          => home_url( '/certificados-de-analisis/' ),
		'peptidos'     => home_url( '/peptidos-mexico/' ),
		'glp1'         => home_url( '/glp-1/' ),
		'comparativas' => home_url( '/comparativas-de-peptidos/' ),
		'suplementos'  => home_url( '/suplementos-deportivos/' ),
		'productos'    => function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/comprar-peptidos-en-mexico/' ),
		'metabolismo'  => home_url( '/como-acelerar-el-metabolismo/' ),
		'reparacion'   => home_url( '/recuperacion-muscular/' ),
		'longevidad'   => home_url( '/envejecimiento-saludable/' ),
		'performance'  => home_url( '/rendimiento-deportivo/' ),
		'calculadora'  => home_url( '/calculadora-de-dosis-de-peptidos/' ),
		'blog'         => home_url( '/blog/' ),
		'contacto'     => home_url( '/contacto/' ),
		'envios'       => home_url( '/politica-de-envios-y-devoluciones/' ),
		'privacidad'   => home_url( '/politica-de-privacidad/' ),
		'terminos'     => home_url( '/terminos-y-condiciones/' ),
		'carrito'      => function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : home_url( '/carrito/' ),
		'cuenta'       => function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'myaccount' ) : home_url( '/mi-cuenta/' ),

		/* categorías reales de WooCommerce */
		'cat_metabolico'  => pys_dis_cat_url( 'metabolismo-activo' ),
		'cat_reparacion'  => pys_dis_cat_url( 'recuperacion-rapida' ),
		'cat_crecimiento' => pys_dis_cat_url( 'reparacion-celular' ),
		'cat_longevidad'  => pys_dis_cat_url( 'bienestar-general' ),
		'cat_cognitivo'   => pys_dis_cat_url( 'peptidos-para-rendimiento-cognitivo' ),
		'cat_suplementos' => pys_dis_cat_url( 'suplementos' ),
	);
	return $u;
}

/**
 * Las cinco familias de péptidos del menú, en el orden en que se enseñan.
 * Una sola lista para la cabecera, el menú de teléfono y la portada, para que
 * no puedan acabar distintas.
 */
function pys_dis_menu_peptidos() {
	$u = pys_dis_enlaces();
	return array(
		'Metabólico y GLP-1' => $u['cat_metabolico'],
		'Reparación'         => $u['cat_reparacion'],
		'Crecimiento'        => $u['cat_crecimiento'],
		'Longevidad'         => $u['cat_longevidad'],
		'Cognitivo'          => $u['cat_cognitivo'],
	);
}

/** Lo que hay que leer antes de comprar: guías, comparativas y herramientas. */
function pys_dis_menu_aprender() {
	$u = pys_dis_enlaces();
	return array(
		'Blog'                 => $u['blog'],
		'Comparativas'         => $u['comparativas'],
		'GLP-1'                => $u['glp1'],
		'Calculadora de dosis' => $u['calculadora'],
	);
}

/** Condiciones de envío, leídas de la configuración real de WooCommerce. */
function pys_dis_envio() {
	static $e = null;
	if ( null !== $e ) {
		return $e;
	}
	$e = array( 'fijo' => null, 'gratis' => null );
	if ( class_exists( 'WC_Shipping_Zones' ) ) {
		foreach ( WC_Shipping_Zones::get_zones() as $zona ) {
			foreach ( $zona['shipping_methods'] as $m ) {
				if ( ! $m->is_enabled() ) {
					continue;
				}
				if ( 'flat_rate' === $m->id && null === $e['fijo'] ) {
					$e['fijo'] = $m->get_option( 'cost' );
				}
				if ( 'free_shipping' === $m->id && null === $e['gratis'] ) {
					$e['gratis'] = $m->get_option( 'min_amount' );
				}
			}
		}
	}
	return $e;
}

/** Importe formateado sin decimales. */
function pys_dis_moneda( $n ) {
	return function_exists( 'wc_price' )
		? wp_strip_all_tags( wc_price( $n, array( 'decimals' => 0 ) ) )
		: '$' . number_format( (float) $n );
}

/** URL de un estático del rediseño (comparte carpeta con el home). */
function pys_dis_uri( $ruta = '' ) {
	$s = wp_upload_dir();
	return trailingslashit( $s['baseurl'] ) . 'home-2026' . ( $ruta ? '/' . ltrim( $ruta, '/' ) : '' );
}

/** Hoja de estilo base: tokens, reset, fondo, cintillo, nav, botones y pie. */
function pys_dis_css() {
	ob_start();
	?>
/* IBM Plex Mono — SIL Open Font License 1.1, © IBM Corp.
   Optima: licencia del sitio. Se sirven desde uploads/home-2026/fonts. */
/* IBM Plex Mono — SIL Open Font License 1.1, © IBM Corp. */
@font-face{font-family:"Plex Mono";src:url(<?php echo esc_url( pys_dis_uri( 'fonts/plex-mono-400.woff2' ) ); ?>) format("woff2");
           font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Plex Mono";src:url(<?php echo esc_url( pys_dis_uri( 'fonts/plex-mono-500.woff2' ) ); ?>) format("woff2");
           font-weight:500;font-style:normal;font-display:swap}
@font-face{font-family:"Plex Mono";src:url(<?php echo esc_url( pys_dis_uri( 'fonts/plex-mono-600.woff2' ) ); ?>) format("woff2");
           font-weight:600;font-style:normal;font-display:swap}
@font-face{font-family:"Optima PYS";src:url(<?php echo esc_url( pys_dis_uri( 'fonts/optima-500.woff2' ) ); ?>) format("woff2");
           font-weight:400 700;font-style:normal;font-display:swap}
@font-face{font-family:"Optima PYS";src:url(<?php echo esc_url( pys_dis_uri( 'fonts/optima-400-italic.woff2' ) ); ?>) format("woff2");
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
/* El fondo hexagonal viejo que el kit de Elementor le pinta al body NO se
   apaga desde aquí: le gana a esta hoja incluso con !important, porque
   LiteSpeed reordena e inyecta CSS crítico y el orden de la cascada no es de
   fiar. Se apaga con una regla de especificidad doble que el cargador inyecta
   al abrir el body (y en la portada, con el atributo style de su plantilla). */
/* Ojo: los reset agresivos de titulares y párrafos (`margin:0`) NO viven aquí.
   Son del home, que arma su propio marcado; aplicados a todo el sitio dejarían
   sin aire la prosa del blog y de las políticas. Cada plantilla trae el suyo. */
body.pys-h26{margin:0;color:var(--tinta);font-family:var(--optima);
  font-size:17px;line-height:1.55;-webkit-font-smoothing:antialiased;overflow-x:hidden}
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
/* En teléfono no cabían en una fila la marca (≈245 px) y los cuatro iconos (176 px):
   el navegador ensanchaba la página a 461 px y la enseñaba alejada, con el carrito
   cortado. La marca pasa a dos líneas y los iconos se compactan. */
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
/* el último desplegable («Aprender») cae pegado al borde derecho del menú:
   si se abriera hacia la derecha se saldría de la ventana a 1100-1280 px */
.menu .desp:last-of-type ul{left:auto;right:-14px}
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

/* ── secciones ─────────────────────────────────────────────────────── */
.pys-h26 section{position:relative;z-index:1}
/* El `padding-block` de secciones es de la portada, que arma sus propias section; aquí
   solo caía sobre el contenido (las landings usan section hasta para tarjetas) y cada
   familia lo tenía anulado. Simulado en las 67 URL: quitarlo no mueve ninguna. */
.cab{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;
  flex-wrap:wrap;margin-bottom:clamp(22px,3vw,40px)}
.cab h2{font-size:clamp(28px,3.8vw,52px);max-width:22ch}
.cab .vs{display:block;margin-bottom:12px}
.cab p{color:var(--tinta-2);font-size:16px;max-width:52ch;margin-top:12px}
.link-mas{font-family:var(--mono);font-size:12px;color:var(--magenta);letter-spacing:.05em;
  white-space:nowrap}
.link-mas:hover{text-decoration:underline}

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


/* ── tarjeta de producto ─────────────────────────────────────────────
   Una sola definición para la portada y para el archivo de la tienda. En
   el archivo, la clase `tarjeta` se le añade al <li> de WooCommerce con un
   filtro, de modo que las dos retículas comparten pieza. */
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

@media (max-width:440px){
  .tarjeta .cuerpo{padding:12px 12px 0}
  .tarjeta h3{font-size:15.5px}
  .tarjeta .sku{font-size:9.5px}
  .tarjeta .specs{display:none}
  .tarjeta .compra{padding:11px 12px;gap:8px}
  .tarjeta .precio{font-size:14.5px}
  .tarjeta .add{padding:8px 10px;font-size:10px}
  .tarjeta .eti{font-size:8px;padding:2px 5px;top:8px;left:8px}
}

/* ── avisos de WooCommerce ──────────────────────────────────────────
   Salen en catálogo, ficha, carrito y finalizar compra, así que viven en la
   base y no en el módulo de una sola vista. */
.pys-h26 .woocommerce-message,.pys-h26 .woocommerce-info,.pys-h26 .woocommerce-error{
  background:var(--carbon);border:1px solid var(--linea-2);border-top:2px solid var(--aqua);
  border-radius:3px;color:var(--tinta-2);font-size:15px;padding:16px 20px;margin-bottom:22px}
.pys-h26 .woocommerce-error{border-top-color:var(--magenta)}
.pys-h26 .woocommerce-message a,.pys-h26 .woocommerce-info a{color:var(--magenta)}
/* WooCommerce pone su icono en absoluto a 1.5em del borde y la base solo dejaba 20 px:
   se montaba encima de la primera letra («✓elank se ha añadido…»). Y el botón «Ver
   carrito» del aviso seguía siendo la píldora con degradado del tema. Carrito y
   checkout los resuelve tienda.php. */
html body.pys-h26:not(.woocommerce-cart):not(.woocommerce-checkout)[class] :is(.woocommerce-message,.woocommerce-info,.woocommerce-error){
  position:relative;padding:16px 20px 16px 50px!important}
html body.pys-h26:not(.woocommerce-cart):not(.woocommerce-checkout)[class] :is(.woocommerce-message,.woocommerce-info,.woocommerce-error)::before{
  left:20px!important;top:17px!important;color:var(--aqua)!important}
html body.pys-h26:not(.woocommerce-cart):not(.woocommerce-checkout)[class] .woocommerce-error::before{color:var(--magenta)!important}
html body.pys-h26:not(.woocommerce-cart):not(.woocommerce-checkout)[class] :is(.woocommerce-message,.woocommerce-info) .button{
  float:right;margin:-5px 0 -5px 18px!important;padding:8px 16px!important;border-radius:2px!important;
  background:transparent!important;background-image:none!important;border:1px solid var(--linea-2)!important;
  box-shadow:none!important;color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;
  font-family:var(--mono)!important;font-size:11px!important;font-weight:400!important;letter-spacing:.12em!important;
  text-transform:uppercase!important;line-height:1.4!important;height:auto!important;min-height:0!important;
  display:inline-block!important;vertical-align:middle;transition:border-color .2s,color .2s}
html body.pys-h26:not(.woocommerce-cart):not(.woocommerce-checkout)[class] :is(.woocommerce-message,.woocommerce-info) .button:hover{
  border-color:var(--magenta)!important;color:var(--magenta)!important}

	<?php
	return ob_get_clean();
}

/** Fondo: retícula hexagonal + halo que siguen al cursor. */
function pys_dis_fondo() {
	?>
<div class="hexes" aria-hidden="true"><span class="base"></span><span class="viva"></span></div>
<div id="halo" aria-hidden="true"></div>
	<?php
}

/** Cintillo + cabecera. */
function pys_dis_cabecera() {
	$pys_url = pys_dis_enlaces();
	$envio   = pys_dis_envio();
	$pys_envio_fijo   = $envio['fijo'];
	$pys_envio_gratis = $envio['gratis'];
	$pys_moneda = 'pys_dis_moneda';
	$n_ref   = (int) wp_count_posts( 'product' )->publish;
	$n_guias = (int) wp_count_posts( 'post' )->publish;
	?>
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
      <img class="logo" src="<?php echo esc_url( pys_dis_uri( 'img/logo-pys.png' ) ); ?>"
           width="75" height="96" alt="" decoding="async">
      <span class="nom">Péptidos y Suplementos MX</span>
    </a>

    <nav class="menu" aria-label="Principal">
      <div class="desp" data-abierto="0">
        <button type="button" aria-expanded="false" aria-controls="desp-pep">Péptidos
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.4" aria-hidden="true"><path d="M5 9l7 7 7-7"/></svg>
        </button>
        <ul id="desp-pep">
          <?php foreach ( pys_dis_menu_peptidos() as $pys_et => $pys_href ) : ?>
            <li><a href="<?php echo esc_url( $pys_href ); ?>"><?php echo esc_html( $pys_et ); ?></a></li>
          <?php endforeach; ?>
        </ul>
      </div>
      <a href="<?php echo esc_url( $pys_url['cat_suplementos'] ); ?>">Suplementos</a>
      <a href="<?php echo esc_url( $pys_url['productos'] ); ?>">Tienda</a>
      <div class="desp" data-abierto="0">
        <button type="button" aria-expanded="false" aria-controls="desp-apr">Aprender
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.4" aria-hidden="true"><path d="M5 9l7 7 7-7"/></svg>
        </button>
        <ul id="desp-apr">
          <?php foreach ( pys_dis_menu_aprender() as $pys_et => $pys_href ) : ?>
            <li><a href="<?php echo esc_url( $pys_href ); ?>"><?php echo esc_html( $pys_et ); ?></a></li>
          <?php endforeach; ?>
        </ul>
      </div>
      <a href="<?php echo esc_url( $pys_url['coa'] ); ?>">COA</a>
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
    <span class="et">Péptidos</span>
    <?php foreach ( pys_dis_menu_peptidos() as $pys_et => $pys_href ) : ?>
      <a href="<?php echo esc_url( $pys_href ); ?>"><?php echo esc_html( $pys_et ); ?></a>
    <?php endforeach; ?>
    <span class="et">Catálogo</span>
    <a href="<?php echo esc_url( $pys_url['cat_suplementos'] ); ?>">Suplementos</a>
    <a href="<?php echo esc_url( $pys_url['productos'] ); ?>">Tienda<span class="k"><?php echo (int) $n_ref; ?> REF.</span></a>
    <span class="et">Calidad</span>
    <a href="<?php echo esc_url( $pys_url['coa'] ); ?>">Certificados de análisis</a>
    <span class="et">Aprender</span>
    <?php foreach ( pys_dis_menu_aprender() as $pys_et => $pys_href ) : ?>
      <a href="<?php echo esc_url( $pys_href ); ?>"><?php echo esc_html( $pys_et ); ?><?php
        echo 'Blog' === $pys_et ? '<span class="k">' . (int) $n_guias . '</span>' : '';
      ?></a>
    <?php endforeach; ?>
    <a href="<?php echo esc_url( $pys_url['contacto'] ); ?>">Contacto</a>
    <span class="et">Cuenta</span>
    <a href="<?php echo esc_url( $pys_url['cuenta'] ); ?>">Mi cuenta</a>
    <a href="<?php echo esc_url( $pys_url['carrito'] ); ?>">Carrito</a>
  </div></div>
</header>
	<?php
}

/** Pie. */
function pys_dis_pie() {
	$pys_url = pys_dis_enlaces();
	$reta = get_page_by_path( 'retatrutida', OBJECT, 'product' );
	$pys_reta_url = $reta ? get_permalink( $reta ) : $pys_url['productos'];
	?>
<footer class="pie-h26">
  <div class="wrap">
    <div class="pie">
      <div>
        <span class="marca">
          <img class="logo" src="<?php echo esc_url( pys_dis_uri( 'img/logo-pys.png' ) ); ?>"
               width="75" height="96" alt="" loading="lazy" decoding="async">
          <span class="nom">Péptidos y Suplementos MX</span>
        </span>
        <p>Biohacking · Investigación · Suplementación avanzada</p>
        <p style="margin-top:10px">Información especializada en péptidos, suplementos, biohacking y
          bienestar avanzado. Contenido claro para rendimiento, metabolismo, recuperación y
          longevidad.</p>
      </div>
      <div><h4>Principales</h4><ul>
        <li><a href="<?php echo esc_url( $pys_url['productos'] ); ?>">Tienda</a></li>
        <li><a href="<?php echo esc_url( $pys_url['peptidos'] ); ?>">Péptidos en México</a></li>
        <li><a href="<?php echo esc_url( $pys_url['suplementos'] ); ?>">Suplementos deportivos</a></li>
        <li><a href="<?php echo esc_url( $pys_reta_url ); ?>">Retatrutida</a></li>
        <li><a href="<?php echo esc_url( home_url( '/tirzepatida-en-mexico/' ) ); ?>">Tirzepatida</a></li>
        <li><a href="<?php echo esc_url( home_url( '/semaglutida-en-mexico/' ) ); ?>">Semaglutida</a></li>
      </ul></div>
      <?php
      /* Las cuatro landings por objetivo salieron del menú —entre las cuatro
         solo enseñaban 5 productos distintos— pero siguen enlazadas aquí, con
         el nombre de la guía que son. Antes se llamaban «Metabolismo»,
         «Reparación celular», «Longevidad» y «Performance», que es como se
         llaman ahora las CATEGORÍAS del menú: el mismo rótulo llevaba a dos
         sitios distintos. */
      ?>
      <div><h4>Guías</h4><ul>
        <li><a href="<?php echo esc_url( $pys_url['metabolismo'] ); ?>">Cómo acelerar el metabolismo</a></li>
        <li><a href="<?php echo esc_url( $pys_url['reparacion'] ); ?>">Recuperación muscular</a></li>
        <li><a href="<?php echo esc_url( $pys_url['longevidad'] ); ?>">Envejecimiento saludable</a></li>
        <li><a href="<?php echo esc_url( $pys_url['performance'] ); ?>">Rendimiento deportivo</a></li>
        <li><a href="<?php echo esc_url( $pys_url['comparativas'] ); ?>">Comparativas de péptidos</a></li>
        <li><a href="<?php echo esc_url( $pys_url['calculadora'] ); ?>">Calculadora de dosis</a></li>
        <li><a href="<?php echo esc_url( $pys_url['blog'] ); ?>">Blog</a></li>
      </ul></div>
      <div><h4>Compra</h4><ul>
        <li><a href="<?php echo esc_url( $pys_url['coa'] ); ?>">Certificados de análisis</a></li>
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
}

/**
 * JavaScript de la cabecera: menú de teléfono, buscador, desplegable «Por
 * objetivo» y el seguimiento del cursor para el halo y el panal. No depende de
 * ninguna librería, así que va en línea y corre de inmediato.
 */
function pys_dis_js() {
	ob_start();
	?>
<script data-no-optimize="1">
(function(){
  var quieto = false;
  var $ = function (s) { return document.querySelector(s); };
  var animate = null, stagger = null;   /* el menú se anima solo en la portada */
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

  /* ── desplegables del menú («Péptidos», «Aprender») ─────────────────
     Son dos, así que se recorren todos: con querySelector solo respondía el
     primero y el segundo se quedaba muerto. Abrir uno cierra el otro. */
  var desps = [].slice.call(document.querySelectorAll(".desp"));
  desps.forEach(function(desp){
    var bot = desp.querySelector("button");
    if (!bot) return;
    function abrirDesp(v){
      if (v) desps.forEach(function(o){
        if (o !== desp){ o.dataset.abierto = "0";
          var b = o.querySelector("button"); if (b) b.setAttribute("aria-expanded","false"); }
      });
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
  });

  addEventListener("keydown", function(e){
    if (e.key !== "Escape") return;
    if (!mnav.hidden){ abrirNav(false); burger.focus(); }
    if (!busca.hidden){ busca.hidden = true; lupa.setAttribute("aria-expanded","false"); lupa.focus(); }
    desps.forEach(function(o){
      o.dataset.abierto = "0";
      var b = o.querySelector("button"); if (b) b.setAttribute("aria-expanded","false");
    });
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

})();
</script>
	<?php
	return ob_get_clean();
}

/**
 * Devuelve el nombre del archivo del render de vial de un producto, o cadena
 * vacía si no tiene. Lo usan la portada y el catálogo, para que un producto no
 * salga con vial en un sitio y con su tarjeta tipográfica en otro.
 */
function pys_dis_vial( $post_id ) {
	/**
	 * Renders 3D del vial por producto, indexados por slug.
	 *
	 * Son los del prototipo: misma etiqueta que la imagen oficial del producto
	 * (nombre, gramaje, «99% HPLC», leyenda de investigación) pero sobre el vial
	 * en tres dimensiones en vez de la tarjeta tipográfica plana.
	 *
	 * Los cuatro últimos no venían en el prototipo: se generaron con
	 * `herramientas/generar-vial.py`, que desenvuelve la etiqueta de un render
	 * existente, le cambia nombre y gramaje, y la vuelve a envolver. El frasco,
	 * la luz y el bloque legal son por tanto los mismos bits que en los demás.
	 *
	 * Los cuatro suplementos Nutricost (cápsulas y softgels) NO están en la lista
	 * a propósito: su foto real de bote es correcta y un vial sería mentira.
	 * Un slug que no esté aquí se queda con su imagen de WooCommerce.
	 */
	static $viales = array(
	'retatrutida'              => 'vial-retatrutida-30-mg.jpg',
	'mots-c-10mg'              => 'vial-mots-c-10-mg.jpg',
	'mots-c-40mg'              => 'vial-mots-c-40-mg.jpg',
	'bpc-157-tb-500'           => 'vial-bpc-157-tb500-5-5mg.jpg',
	'agua-bacteriostatica-3ml' => 'vial-agua-bacteriostatica-0-9-alcohol-bencilico.jpg',
	'igf-1-lr3-1mg'            => 'vial-igf-1-lr3-1-mg.jpg',
	'nad'                      => 'vial-nad-500-mg.jpg',
	'semaglutida-20mg'         => 'vial-semaglutida-20-mg.jpg',
	'semaglutida-5-mg'         => 'vial-semaglutida-5-mg.jpg',
	'tirzepatida'              => 'vial-tirzepatida-30-mg.jpg',
	'selank-10-mg'             => 'vial-selank-10-mg.jpg',
	'sermorelina-10mg'         => 'vial-sermorelin-10-mg.jpg',
	'cjc-1295-ipamorelina-5mg' => 'vial-cjc-1295-ipamorelin-no-dac-5-5mg.jpg',
	'ghk-cu'                   => 'vial-ghk-cu-100-mg.jpg',
	/* generados a partir de los anteriores */
	'thymosin-alpha-1-10mg'    => 'vial-thymosin-alpha-1-10-mg.jpg',
	'cagrilintida-10mg'        => 'vial-cagrilintida-10-mg.jpg',
	'bpc-157'                  => 'vial-bpc-157.jpg',
	'glutation-1500mg'         => 'vial-glutation-1500-mg.jpg',
	);

	$slug = get_post_field( 'post_name', $post_id );
	return isset( $viales[ $slug ] ) ? $viales[ $slug ] : '';
}

/**
 * Nombre corto de cada categoría, para las etiquetas de las tarjetas y los
 * filtros. El nombre largo de WooCommerce no cabe en una tarjeta.
 *
 * Son los MISMOS rótulos que el menú «Péptidos», a propósito: antes la tarjeta
 * decía «Reparación» para `reparacion-celular` y el menú llamaba «Reparación»
 * a otra cosa. Cada valor tiene que seguir siendo único: la portada arma con
 * ellos los filtros del catálogo.
 */
function pys_dis_cats_cortas() {
	static $c = array(
	'metabolismo-activo'                  => 'Metabólico',
	'bienestar-general'                   => 'Longevidad',
	'reparacion-celular'                  => 'Crecimiento',
	'peptidos-para-rendimiento-cognitivo' => 'Cognitivo',
	'suplementos'                         => 'Suplementos',
	'recuperacion-rapida'                 => 'Reparación',
	'performance-top'                     => 'Deportivo',
	);
	return $c;
}

/** Nombre corto de la primera categoría del producto, o cadena vacía. */
function pys_dis_cat_corta( $post_id ) {
	$cortas = pys_dis_cats_cortas();
	$slugs  = wp_get_post_terms( $post_id, 'product_cat', array( 'fields' => 'slugs' ) );
	if ( is_wp_error( $slugs ) ) {
		return '';
	}
	foreach ( $slugs as $s ) {
		if ( isset( $cortas[ $s ] ) ) {
			return $cortas[ $s ];
		}
	}
	return '';
}

/* ─── listado de certificados de análisis ─────────────────────────────
   Alimenta la página /certificados-de-analisis/. El contenido sale del meta
   `_pys_coa` de cada producto (mu-plugin pys-coa.php), NO de la página: para
   publicar el certificado de un lote nuevo se rellena la caja «Certificado de
   análisis (COA)» en el editor de ese producto y se sube el PDF a Medios. La
   página se actualiza sola; aquí no hay nada que tocar.
   Se escribe con etiquetas normales (h3, table, p) para que herede el diseño
   de las páginas planas sin CSS propio. */

/** Una fila de la tabla del lote, solo si el dato existe. */
function pys_dis_coa_fila( $etiqueta, $valor ) {
	if ( '' === trim( (string) $valor ) ) {
		return '';
	}
	return '<tr><th scope="row">' . esc_html( $etiqueta ) . '</th><td>' . wp_kses_post( $valor ) . '</td></tr>';
}

/** [pys_coa_lotes] — los lotes con certificado publicado, uno por bloque. */
function pys_dis_coa_lotes() {
	if ( ! function_exists( 'pys_coa_productos' ) ) {
		return '';
	}
	$coas = pys_coa_productos();
	$n    = count( $coas );

	$total = function_exists( 'wp_count_posts' ) ? (int) wp_count_posts( 'product' )->publish : 0;

	if ( ! $n ) {
		return '<p>Todavía no hay ningún certificado publicado en esta página. Si necesitas el de un '
			. 'lote concreto, pídelo por <a href="' . esc_url( home_url( '/contacto/' ) ) . '">contacto</a> '
			. 'con el número impreso en la etiqueta de tu vial.</p>';
	}

	$out = '<p>Hay <strong>' . (int) $n . '</strong> ';
	$out .= ( 1 === $n ? 'certificado publicado' : 'certificados publicados' );
	if ( $total ) {
		$out .= ' de ' . (int) $total . ' referencias del catálogo';
	}
	$out .= '. Los demás se publican conforme el laboratorio nos los entrega; mientras tanto, se '
		. 'piden por <a href="' . esc_url( home_url( '/contacto/' ) ) . '">contacto</a> indicando el '
		. 'lote impreso en la etiqueta del vial.</p>';

	foreach ( $coas as $id => $coa ) {
		$lote = $coa['lote'];
		/* el ancla conserva el lote TAL CUAL va impreso en la etiqueta —los
		   identificadores HTML distinguen mayúsculas—, solo se le quita lo que
		   no sirva en un id: así /certificados-de-analisis/#lote-AA54YCH se
		   escribe leyendo el vial y no hay que adivinar la forma del ancla. */
		$ancla = 'lote-' . preg_replace( '/[^A-Za-z0-9_-]/', '', $lote );

		$out .= '<h3 id="' . esc_attr( $ancla ) . '">' . esc_html( get_the_title( $id ) )
			. ' &mdash; lote ' . esc_html( $lote ) . '</h3>';
		$out .= '<table><tbody>';
		$out .= pys_dis_coa_fila(
			'Producto',
			'<a href="' . esc_url( get_permalink( $id ) ) . '">' . esc_html( get_the_title( $id ) ) . '</a>'
		);
		$out .= pys_dis_coa_fila( 'Número de lote', esc_html( $lote ) );
		if ( ! empty( $coa['pureza'] ) ) {
			$out .= pys_dis_coa_fila( 'Pureza cromatográfica', esc_html( $coa['pureza'] ) . ' %' );
		}
		if ( ! empty( $coa['masa'] ) ) {
			$masa = esc_html( $coa['masa'] ) . ' mg';
			if ( ! empty( $coa['pct_etiqueta'] ) ) {
				$masa .= ' (' . esc_html( $coa['pct_etiqueta'] ) . ' % de la cantidad declarada)';
			}
			$out .= pys_dis_coa_fila( 'Masa total de péptido', $masa );
		}
		if ( ! empty( $coa['identidad'] ) ) {
			$out .= pys_dis_coa_fila( 'Identidad por espectrometría', esc_html( $coa['identidad'] ) );
		}
		if ( ! empty( $coa['metodo'] ) ) {
			$out .= pys_dis_coa_fila( 'Método', esc_html( $coa['metodo'] ) );
		}
		if ( ! empty( $coa['laboratorio'] ) ) {
			$out .= pys_dis_coa_fila( 'Laboratorio', esc_html( $coa['laboratorio'] ) );
		}
		if ( ! empty( $coa['lab_num'] ) ) {
			$out .= pys_dis_coa_fila( 'Referencia del laboratorio', esc_html( $coa['lab_num'] ) );
		}
		/* Ni la fecha de análisis ni la de emisión salen a la página: siguen
		   en el meta y dentro del PDF. Un lote analizado hace un año sigue
		   siendo bueno —liofilizado y congelado aguanta más de dos—, pero el
		   público no lo sabe y la fecha se lee como producto viejo. Regla del
		   dueño, 2026-09-23. */
		$out .= '</tbody></table>';
		$out .= '<p><a href="' . esc_url( $coa['pdf_url'] ) . '" target="_blank" rel="noopener">'
			. 'Ver el certificado completo del lote ' . esc_html( $lote ) . ' (PDF)</a> &middot; '
			. '<a href="' . esc_url( get_permalink( $id ) ) . '#pys-coa">ver en la ficha del producto</a></p>';
	}

	return $out;
}
add_shortcode( 'pys_coa_lotes', 'pys_dis_coa_lotes' );
