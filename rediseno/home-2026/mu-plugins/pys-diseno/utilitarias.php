<?php
/**
 * PYS — rediseño de búsqueda y 404. Solo diseño: no toca contenido.
 *
 * BÚSQUEDA GENERAL (/?s=…). La pinta la misma plantilla de archivo #155 de
 * Elementor que el listado del blog: bloque de título en un widget HTML, el
 * buscador de guías `#pys-guias` (que su propio JS oculta fuera de body.blog)
 * y el widget «archive-posts», que aquí SÍ trae los resultados —productos y
 * entradas mezclados—. Por eso NO se reutiliza la hoja del blog: esa oculta
 * el widget archive-posts cuando existe `.pg-grid` (el duplicado del blog), y
 * aquí se llevaría por delante los resultados.
 *
 * BÚSQUEDA DE PRODUCTOS (/?s=…&post_type=product). Es a la vez búsqueda y
 * archivo de la tienda, y ya la estiliza catalogo.php. El predicado de esta
 * familia (is_search) también la incluye, así que TODA regla de búsqueda va
 * acotada con `body.search:not(.post-type-archive-product)`: aquí no se toca.
 *
 * 404. La plantilla del tema: un titular y un párrafo. Se les da el aire y la
 * tipografía del sistema, sin añadir texto.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function pys_dis_css_utilitarias() {
	$css = <<<'CSS'
/* ════════════════════════════════════════════════════════════════════
   BÚSQUEDA — bloque de título (mismo lenguaje que el listado del blog)
   ════════════════════════════════════════════════════════════════════ */
@@S .pys-blog-title-block{background:none!important;background-image:none!important;border:0!important;
  border-radius:0!important;box-shadow:none!important;
  padding:clamp(34px,5vw,64px) 0 clamp(20px,3vw,34px)!important;font-family:var(--optima)!important}
@@S .pys-blog-title-block::before,@@S .pys-blog-title-block::after{display:none!important}
@@S .pys-blog-title-inner{max-width:760px;margin-inline:auto;text-align:center}
@@S .pys-blog-kicker{display:inline-block;background:none!important;border:0!important;
  box-shadow:none!important;padding:0!important;font-family:var(--optima)!important;
  font-size:11px!important;font-weight:400!important;letter-spacing:.22em!important;
  text-transform:uppercase;color:var(--tinta-3)!important;margin-bottom:14px}
@@S .pys-blog-kicker::before{display:none!important}
@@S .pys-blog-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(34px,5vw,64px)!important;line-height:1.05!important;letter-spacing:-.012em!important;
  color:var(--tinta)!important;margin:0 0 18px!important;text-transform:none!important}
/* la palabra resaltada venía con degradado recortado: magenta sólido */
@@S .pys-blog-title span{background:none!important;background-image:none!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important;
  -webkit-text-fill-color:var(--magenta)!important;color:var(--magenta)!important}
@@S .pys-blog-accent{width:56px!important;height:1px!important;margin:0 auto 20px!important;
  background:var(--magenta)!important;background-image:none!important;border:0!important;
  box-shadow:none!important;border-radius:0!important;opacity:.8}
@@S .pys-blog-copy{max-width:56ch;margin-inline:auto}
@@S .pys-blog-copy p{font-family:var(--optima)!important;color:var(--tinta-2)!important;
  font-size:17px!important;font-weight:400!important;line-height:1.6!important;margin:0 0 8px!important}

/* ════════════════════════════════════════════════════════════════════
   BÚSQUEDA — resultados (tarjeta = la de guía del blog)
   ════════════════════════════════════════════════════════════════════ */
@@S .elementor-widget-archive-posts{margin-top:clamp(8px,1.6vw,20px)!important}
@@S .elementor-posts-container{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:clamp(12px,1.4vw,18px)!important}
@media (max-width:920px){ @@S .elementor-posts-container{grid-template-columns:repeat(2,minmax(0,1fr))!important} }
@media (max-width:560px){ @@S .elementor-posts-container{grid-template-columns:1fr!important} }
/* el article y la tarjeta traían los dos marco de 28 px, degradado y sombra */
@@S article.elementor-post{background:none!important;background-image:none!important;border:0!important;
  border-radius:0!important;box-shadow:none!important;padding:0!important;margin:0!important}
@@S .elementor-post__card{background:var(--carbon)!important;background-image:none!important;
  border:1px solid var(--linea)!important;border-radius:3px!important;box-shadow:none!important;
  backdrop-filter:none!important;overflow:hidden;transform:none!important;
  transition:border-color .22s,background .22s}
@@S .elementor-post__card:hover{border-color:color-mix(in srgb,var(--magenta) 55%,transparent)!important;
  background:var(--carbon-2)!important;transform:none!important}
@@S .elementor-post__card::before,@@S .elementor-post__card::after{background:none!important;
  box-shadow:none!important}
/* miniatura: a sangre, sin esquinas redondas ni velo oscuro encima */
@@S .elementor-post__thumbnail__link,@@S .elementor-post__thumbnail{border-radius:0!important;
  background:var(--panel)!important;margin:0!important}
@@S .elementor-post__thumbnail__link::after,@@S .elementor-post__thumbnail::after{
  background:none!important;background-image:none!important;opacity:0!important}
/* Los PRODUCTOS traen su tarjeta tipográfica cuadrada, que el recorte 3:2 de
   Elementor decapitaba (en el teléfono se perdía el nombre del producto). Va
   completa sobre la misma luz de vitrina que la tarjeta del catálogo. */
@@S article.type-product .elementor-post__thumbnail__link,
@@S article.type-product .elementor-post__thumbnail{
  background:radial-gradient(120% 86% at 50% 10%, #FFFFFF 0%, var(--vitrina) 58%, #DDE5E2 100%)!important}
@@S article.type-product .elementor-post__thumbnail img{object-fit:contain!important;
  width:100%!important;height:100%!important;max-width:none!important;top:0!important;left:0!important;
  transform:none!important}
@@S article.type-product .elementor-post__card:hover .elementor-post__thumbnail img{transform:none!important}

@@S .elementor-post__text{padding:16px 18px 18px!important;margin:0!important}
@@S .elementor-post__title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:18px!important;line-height:1.28!important;letter-spacing:0!important;
  color:var(--tinta)!important;margin:0 0 8px!important;text-transform:none!important}
@@S .elementor-post__title a{font:inherit!important;letter-spacing:inherit!important;
  color:var(--tinta)!important;-webkit-text-fill-color:currentColor!important;background:none!important;
  transition:color .2s}
@@S .elementor-post__card:hover .elementor-post__title a,@@S .elementor-post__title a:hover{
  color:var(--magenta)!important}
@@S .elementor-post__excerpt p{font-family:var(--optima)!important;color:var(--tinta-2)!important;
  -webkit-text-fill-color:currentColor!important;font-size:14.5px!important;font-weight:400!important;
  line-height:1.55!important;margin:0 0 12px!important}
@@S .elementor-post__excerpt strong{color:var(--tinta)!important;font-weight:600!important}
@@S .elementor-post__read-more{font-family:var(--mono)!important;font-size:11.5px!important;
  font-weight:400!important;letter-spacing:.05em!important;text-transform:none!important;
  color:var(--magenta)!important;-webkit-text-fill-color:currentColor!important;
  background:none!important;margin:2px 0 0!important;padding:0!important}
@@S .elementor-post__read-more:hover{text-decoration:underline;text-underline-offset:3px}
/* pie de la tarjeta: la fecha, en monoespaciada, como en las guías */
@@S .elementor-post__meta-data{border-top:1px solid var(--linea)!important;background:none!important;
  padding:12px 18px!important;margin:0!important;font-family:var(--mono)!important;
  font-size:10.5px!important;font-weight:400!important;letter-spacing:.08em!important;
  text-transform:uppercase;color:var(--tinta-3)!important;-webkit-text-fill-color:currentColor!important}
@@S .elementor-post__meta-data span{font-family:inherit!important;font-size:inherit!important;
  font-weight:inherit!important;letter-spacing:inherit!important;color:inherit!important}

/* paginación: la del catálogo */
@@S .elementor-pagination{display:flex!important;justify-content:center;gap:7px;flex-wrap:wrap;
  margin-top:clamp(28px,4vw,48px)!important}
@@S .elementor-pagination .page-numbers{display:inline-grid!important;place-items:center;
  min-width:40px;width:auto!important;height:40px!important;padding:0 12px!important;margin:0!important;
  border-radius:2px!important;border:1px solid var(--linea-2)!important;background:transparent!important;
  background-image:none!important;box-shadow:none!important;font-family:var(--mono)!important;
  font-size:12px!important;font-weight:400!important;line-height:1!important;color:var(--tinta-2)!important;
  -webkit-text-fill-color:currentColor!important;transition:border-color .2s,color .2s}
@@S .elementor-pagination a.page-numbers:hover{border-color:var(--tinta-3)!important;color:var(--tinta)!important}
@@S .elementor-pagination .page-numbers.current{background:var(--tinta)!important;
  border-color:var(--tinta)!important;color:var(--negro)!important}

/* sin resultados: el aviso de WooCommerce de la base, centrado y a buen tamaño */
@@S .elementor-posts-nothing-found{grid-column:1 / -1;justify-self:center;width:min(640px,100%);
  margin:clamp(4px,1.4vw,16px) auto 0;background:var(--carbon);border:1px solid var(--linea-2);
  border-top:2px solid var(--aqua);border-radius:3px;
  padding:clamp(24px,3.4vw,40px) clamp(20px,3vw,40px);font-family:var(--optima)!important;
  font-size:clamp(17px,1.5vw,19px)!important;line-height:1.55;color:var(--tinta-2)!important;
  text-align:center}
@@S.search-no-results .elementor-location-archive{padding-bottom:clamp(64px,9vw,128px)!important}

/* ════════════════════════════════════════════════════════════════════
   404
   ════════════════════════════════════════════════════════════════════ */
@@E #content.site-main{width:min(1200px,100%);max-width:none!important;margin-inline:auto;
  padding-inline:var(--gutter);padding-block:clamp(64px,11vw,150px);
  min-height:clamp(440px,64vh,720px);display:flex;flex-direction:column;justify-content:center;
  align-items:center;text-align:center}
@@E .page-header,@@E .page-content{margin:0!important;padding:0!important;max-width:none!important;
  width:100%}
@@E .page-header .entry-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(38px,6vw,82px)!important;line-height:1.02!important;letter-spacing:-.016em;
  color:var(--tinta)!important;margin:0 auto!important;padding:0!important;max-width:16ch!important;
  text-transform:none!important;text-wrap:balance}
@@E .page-header::after{content:"";display:block;width:56px;height:1px;background:var(--magenta);
  margin:28px auto 24px;opacity:.85}
@@E .page-content p{color:var(--tinta-2)!important;font-size:clamp(17px,1.5vw,19px)!important;
  line-height:1.6!important;margin:0 auto!important;max-width:52ch}
CSS;
	return str_replace(
		array( '@@S', '@@E' ),
		array(
			'html body.search:not(.post-type-archive-product)[class][class]',
			'html body.error404[class][class][class]',
		),
		$css
	);
}
