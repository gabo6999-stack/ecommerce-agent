<?php
/**
 * Blog: listado (/blog/, /category/blog/) y entradas.
 *
 * Solo diseño. El listado lo pinta la plantilla de archivo #155 de Elementor
 * —bloque de título en un widget HTML más el buscador de guías `.pg-*`— y las
 * entradas la plantilla #159 con el shortcode del plugin «single-posts». No se
 * toca ninguna de las dos plantillas ni el marcado que generan: se re-estiliza
 * encima.
 *
 * Las reglas llevan `html body[class][class][class]` porque el Customizer del
 * sitio ya estiliza estos mismos bloques con `html body[class] …!important`.
 * Las del buscador llevan además `#pys-guias`: su propia hoja usa ese id con
 * `!important`, y un id gana a cualquier número de clases.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** ¿Vista de blog? Listado, categoría o entrada. */
function pys_dis_es_blog() {
	return is_home() || is_category() || is_tag() || is_singular( 'post' );
}

/** Hoja del blog. */
function pys_dis_css_blog() {
	$p = 'html body[class][class][class]';
	$g = $p . ' #pys-guias';
	return '
/* ════════════════════════════════════════════════════════════════════
   LISTADO
   ════════════════════════════════════════════════════════════════════ */
' . $p . ' .pys-blog-title-block{background:none!important;border:0!important;
  box-shadow:none!important;padding:clamp(34px,5vw,64px) 0 clamp(20px,3vw,34px)!important}
' . $p . ' .pys-blog-title-inner{max-width:760px;margin-inline:auto;text-align:center}
/* el antiguo «píldora» pasa a ser un ladillo como el de la portada */
' . $p . ' .pys-blog-kicker{display:inline-block;background:none!important;border:0!important;
  box-shadow:none!important;padding:0!important;font-family:var(--optima)!important;
  font-size:11px!important;letter-spacing:.22em!important;text-transform:uppercase;
  color:var(--tinta-3)!important;margin-bottom:14px}
' . $p . ' .pys-blog-kicker::before{display:none!important}
' . $p . ' .pys-blog-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(34px,5vw,64px)!important;line-height:1.05!important;letter-spacing:-.012em;
  color:var(--tinta)!important;margin:0 0 18px!important;text-transform:none!important}
/* La palabra resaltada es un span SIN clase dentro del h1, pintado con un
   degradado recortado sobre el texto. Se queda en magenta sólido, que es como
   la portada resalta sus titulares. (`.pys-blog-accent` NO es ese texto: es el
   div vacío de debajo, la rayita decorativa.) */
' . $p . ' .pys-blog-title span{background:none!important;background-image:none!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important;
  -webkit-text-fill-color:var(--magenta)!important;color:var(--magenta)!important}
' . $p . ' .pys-blog-accent{width:56px!important;height:1px!important;margin:0 auto 20px!important;
  background:var(--magenta)!important;background-image:none!important;border:0!important;
  box-shadow:none!important;border-radius:0!important;opacity:.8}
/* el widget traía Inter: se queda en la Optima del resto del sitio */
' . $p . ' .pys-blog-copy,' . $p . ' .pys-blog-copy p{font-family:var(--optima)!important;
  color:var(--tinta-2)!important;font-size:17px!important;line-height:1.6!important}
' . $p . ' .pys-blog-copy{max-width:56ch;margin-inline:auto}
' . $p . ' .pys-blog-copy p{margin:0 0 8px}

/* DOS REJILLAS CON LAS MISMAS ENTRADAS. La plantilla de archivo #155 trae,
   desde el 26 de julio, el buscador de guías (widget HTML, pinta las 19 por
   JavaScript) Y el widget «archive-posts» de Elementor (10 por página, en el
   HTML), que nunca estuvo oculto. Antes las dos se veían iguales y pasaban
   por una; con el rediseño una quedó nueva y la otra vieja, y saltó a la vista.
   Se oculta la de Elementor SOLO en /blog/ (`body.blog`) y solo si el buscador
   está en la página (`:has`). Lo de `body.blog` no es opcional: el propio
   script del buscador se esconde a sí mismo cuando el body NO tiene esa
   clase —en /category/blog/, por ejemplo— y ahí, si también se ocultara esta
   rejilla, la página se quedaba sin una sola entrada. Sigue en el HTML, así
   que sus enlaces siguen siendo rastreables. */
html body.blog[class][class]:has(.pg-grid) .elementor-widget-archive-posts{display:none!important}

/* buscador de guías */
' . $g . '{color:var(--tinta)!important;font-family:var(--optima)!important}
' . $g . ' .pg-head{margin-bottom:18px}
' . $g . ' .pg-eyebrow,' . $g . ' .pg-total,' . $g . ' .pg-count,' . $g . ' .pg-hint{
  font-family:var(--mono)!important;font-size:11px!important;letter-spacing:.09em!important;
  text-transform:uppercase;color:var(--tinta-3)!important;font-weight:400!important}
' . $g . ' .pg-count b,' . $g . ' .pg-eyebrow b{color:var(--tinta)!important;font-weight:500!important}
' . $g . ' .pg-hint{text-transform:none;letter-spacing:.03em!important}
' . $g . ' .pg-hint kbd{font-family:var(--mono)!important;background:var(--panel)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta-2)!important;
  padding:0 6px!important;font-size:11px!important}
' . $g . ' .pg-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(26px,3.2vw,40px)!important;letter-spacing:-.012em;color:var(--tinta)!important;
  margin:8px 0 16px!important}
/* la barra es la caja del campo, con la lupa dentro, como el buscador de la cabecera */
' . $g . ' .pg-bar{background:var(--carbon)!important;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;box-shadow:none!important;padding:0 12px 0 14px!important;
  display:flex!important;align-items:center;gap:11px;max-width:620px}
' . $g . ' .pg-bar:focus-within{border-color:var(--magenta)!important;box-shadow:none!important}
' . $g . ' .pg-bar svg{color:var(--tinta-3)!important}
' . $g . ' .pg-bar:focus-within svg{color:var(--magenta)!important}
/* el texto que se escribe venía en #12211f —casi negro sobre negro—: invisible */
' . $g . ' .pg-input{flex:1;min-width:0;background:none!important;border:0!important;
  border-radius:0!important;color:var(--tinta)!important;-webkit-text-fill-color:var(--tinta)!important;
  caret-color:var(--magenta)!important;font-family:var(--optima)!important;font-size:16px!important;
  padding:13px 0!important;box-shadow:none!important;outline:none!important}
' . $g . ' .pg-input::placeholder{color:var(--tinta-3)!important;-webkit-text-fill-color:var(--tinta-3)!important}
/* la «×» de limpiar se veía siempre —su hoja le forzaba display:grid por encima
   del atributo hidden— y en círculo blanco */
' . $g . ' .pg-clear{background:transparent!important;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;color:var(--tinta-3)!important;box-shadow:none!important}
' . $g . ' .pg-clear:hover{border-color:var(--magenta)!important;color:var(--magenta)!important;
  background:transparent!important}
' . $g . ' .pg-clear[hidden]{display:none!important}
' . $g . ' .pg-grid{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:clamp(12px,1.4vw,18px)!important}
@media (max-width:920px){ ' . $g . ' .pg-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important} }
@media (max-width:560px){ ' . $g . ' .pg-grid{grid-template-columns:1fr!important} }
/* la tarjeta de guía es la misma que la de la portada */
' . $g . ' .pg-card,' . $g . ' .pg-skel{background:var(--carbon)!important;border:1px solid var(--linea)!important;
  border-radius:3px!important;box-shadow:none!important;overflow:hidden;
  transition:border-color .22s,background .22s;padding:0!important}
' . $g . ' .pg-card:hover{border-color:color-mix(in srgb,var(--magenta) 55%,transparent)!important;
  background:var(--carbon-2)!important;transform:none!important;box-shadow:none!important}
/* esqueleto de carga: eran ocho cajas blancas con destello */
' . $g . ' .pg-skel .pg-sk{background:linear-gradient(100deg,var(--carbon-2) 30%,var(--panel) 50%,var(--carbon-2) 70%)!important;
  background-size:200% 100%!important}
' . $g . ' .pg-thumb{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;
  border-radius:0!important;border:0!important;margin:0!important}
/* guía sin foto: era un recuadro casi blanco con un resplandor turquesa */
' . $g . ' .pg-thumb--ph{background:var(--panel)!important;background-image:none!important}
' . $g . ' .pg-thumb--ph span{font-family:var(--mono)!important;color:var(--tinta-3)!important;
  font-weight:400!important;letter-spacing:.14em;font-size:13px!important;opacity:1!important}
' . $g . ' .pg-body{padding:16px 18px 18px!important}
' . $g . ' .pg-tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:11px}
/* etiquetas: eran fichas turquesa con texto #067169 casi ilegible sobre negro */
' . $g . ' .pg-tag{font-family:var(--mono)!important;font-size:9.5px!important;letter-spacing:.06em!important;
  font-weight:400!important;text-transform:uppercase!important;padding:4px 8px!important;border-radius:2px!important;
  border:1px solid var(--linea-2)!important;background:transparent!important;
  color:var(--tinta-3)!important;box-shadow:none!important;cursor:pointer}
' . $g . ' .pg-tag:hover{border-color:var(--tinta-3)!important;color:var(--tinta)!important;
  background:transparent!important}
' . $g . ' .pg-cardtitle{font-family:var(--optima)!important;font-weight:400!important;
  font-size:18px!important;line-height:1.28!important;color:var(--tinta)!important;
  margin:0 0 8px!important;text-transform:none!important}
' . $g . ' .pg-ex{font-family:var(--optima)!important;color:var(--tinta-2)!important;
  font-size:14.5px!important;line-height:1.55}
' . $g . ' .pg-foot{border-top:1px solid var(--linea);margin-top:14px;padding-top:12px}
' . $g . ' .pg-foot time{font-family:var(--mono)!important;color:var(--tinta-3)!important}
' . $g . ' .pg-go{font-family:var(--mono)!important;font-size:11.5px!important;letter-spacing:.05em;
  color:var(--magenta)!important;background:none!important;border:0!important;padding:0!important;
  font-weight:400!important;-webkit-text-fill-color:currentColor!important}
/* resaltado de la búsqueda */
' . $g . ' mark{background:color-mix(in srgb,var(--magenta) 22%,transparent)!important;
  color:var(--tinta)!important;box-shadow:none!important;border-radius:1px!important;font-weight:inherit!important}
' . $g . ' .pg-state{color:var(--tinta-2)!important}
' . $g . ' .pg-state strong{color:var(--tinta)!important}
' . $g . ' .pg-state svg{color:var(--tinta-3)!important}
' . $g . ' .pg-link{color:var(--magenta)!important;font-family:var(--optima)!important;font-weight:400!important}
' . $g . ' .pg-empty{color:var(--tinta-3);font-family:var(--mono);font-size:12px}

/* ── rejilla de Elementor: la que queda en /category/blog/ ─────────────
   Ahí el buscador no aparece, así que las entradas las enseña el widget de
   archivo (piel «tarjetas»). Se viste igual que la tarjeta del buscador. */
' . $p . ' .elementor-widget-archive-posts{--grid-column-gap:clamp(12px,1.4vw,18px);--grid-row-gap:clamp(12px,1.4vw,18px)}
/* el Customizer redondea el artículo a 28 px y el enlace de la foto a 26 px */
' . $p . ' .elementor-widget-archive-posts article.elementor-post{border-radius:3px!important;
  border:0!important;background:none!important;box-shadow:none!important;overflow:hidden}
' . $p . ' .elementor-widget-archive-posts .elementor-post__thumbnail__link{border-radius:0!important;
  box-shadow:none!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__card{background:var(--carbon)!important;
  border:1px solid var(--linea)!important;border-radius:3px!important;box-shadow:none!important;
  overflow:hidden;transition:border-color .22s,background .22s}
' . $p . ' .elementor-widget-archive-posts .elementor-post__card:hover{
  border-color:color-mix(in srgb,var(--magenta) 55%,transparent)!important;background:var(--carbon-2)!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__thumbnail{border-radius:0!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__thumbnail img{border-radius:0!important;
  filter:none!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__badge{background:var(--negro)!important;
  border:1px solid var(--linea-2)!important;border-radius:2px!important;color:var(--tinta-2)!important;
  font-family:var(--mono)!important;font-size:9.5px!important;font-weight:400!important;
  letter-spacing:.08em!important;text-transform:uppercase!important;padding:4px 8px!important;
  box-shadow:none!important;line-height:1.3!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__avatar img{border:1px solid var(--linea-2)!important;
  box-shadow:none!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__text{padding:16px 18px 0!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__title,
' . $p . ' .elementor-widget-archive-posts .elementor-post__title a{font-family:var(--optima)!important;
  font-weight:400!important;font-size:18px!important;line-height:1.28!important;color:var(--tinta)!important;
  -webkit-text-fill-color:currentColor!important;text-transform:none!important;letter-spacing:0!important;
  background:none!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__title a:hover{color:var(--magenta)!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__excerpt,
' . $p . ' .elementor-widget-archive-posts .elementor-post__excerpt p{font-family:var(--optima)!important;
  color:var(--tinta-2)!important;font-size:14.5px!important;line-height:1.55!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__read-more{font-family:var(--mono)!important;
  font-size:11.5px!important;letter-spacing:.05em!important;font-weight:400!important;
  text-transform:none!important;color:var(--magenta)!important;-webkit-text-fill-color:currentColor!important}
' . $p . ' .elementor-widget-archive-posts .elementor-post__meta-data{border-top:1px solid var(--linea)!important;
  padding:12px 18px!important;margin-top:14px;font-family:var(--mono)!important;font-size:10.5px!important;
  letter-spacing:.06em;color:var(--tinta-3)!important;text-transform:uppercase}
' . $p . ' .elementor-widget-archive-posts .elementor-post__meta-data span{color:var(--tinta-3)!important}
' . $p . ' .elementor-widget-archive-posts .elementor-pagination{font-family:var(--mono)!important;
  font-size:12px!important;margin-top:clamp(22px,3vw,34px)!important;display:flex;gap:6px;justify-content:center}
' . $p . ' .elementor-widget-archive-posts .elementor-pagination .page-numbers{display:inline-grid;
  place-items:center;min-width:38px;height:38px;padding:0 10px;border:1px solid var(--linea-2)!important;
  border-radius:2px!important;color:var(--tinta-2)!important;background:transparent!important;margin:0!important}
' . $p . ' .elementor-widget-archive-posts .elementor-pagination a.page-numbers:hover{border-color:var(--tinta-3)!important;
  color:var(--tinta)!important}
' . $p . ' .elementor-widget-archive-posts .elementor-pagination .page-numbers.current{
  border-color:var(--magenta)!important;color:var(--tinta)!important}

/* ════════════════════════════════════════════════════════════════════
   ENTRADA
   ════════════════════════════════════════════════════════════════════ */
' . $p . ' .single-posts-root,' . $p . ' .single-posts-hero,' . $p . ' .single-posts-content-section,
' . $p . ' .single-posts-cta-section{background:none!important;background-image:none!important}
/* La hoja del plugin pone Inter en toda la raíz con !important: la entradilla
   de la cabecera y el texto de la llamada final salían en otra letra. */
' . $p . ' .single-posts-root{font-family:var(--optima)!important}
/* Decoración vieja: una cuadrícula de líneas por encima del hexagonal, una
   mancha borrosa magenta/turquesa al pie (se veía como un borrón bajo la
   llamada final) y las marcas de agua «P&S» —la de la llamada, dos veces
   desplazadas y cortadas por el borde—. Son pseudoelementos sin contenido. */
' . $p . ' .single-posts-root::before,' . $p . ' .single-posts-root::after,
' . $p . ' .single-posts-hero::before,' . $p . ' .single-posts-hero::after,
' . $p . ' .single-posts-cta::before,' . $p . ' .single-posts-cta::after{display:none!important}
/* La caja del plugin iba a 1380 px pegada al borde izquierdo: el titular de la
   entrada empezaba 86 px antes que el logo. Ahora comparte la retícula de la
   cabecera (1320 px menos el margen del sitio). */
' . $p . ' .single-posts-wrap{width:calc(min(1320px,100%) - 2 * var(--gutter))!important;
  max-width:none!important;margin-inline:auto!important;padding-inline:0!important}
' . $p . ' .single-posts-hero{padding:clamp(28px,4.5vw,64px) 0 clamp(20px,3vw,36px)!important}
' . $p . ' .single-posts-hero-grid{gap:clamp(24px,4vw,56px)!important;align-items:center}
' . $p . ' .single-posts-eyebrow{background:none!important;border:0!important;box-shadow:none!important;
  padding:0!important;font-family:var(--optima)!important;font-size:11px!important;
  letter-spacing:.22em!important;text-transform:uppercase;color:var(--tinta-3)!important;
  display:inline-block;margin-bottom:14px}
' . $p . ' .single-posts-eyebrow::before{display:none!important}
' . $p . ' .single-posts-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(32px,4.2vw,58px)!important;line-height:1.06!important;letter-spacing:-.012em;
  color:var(--tinta)!important;margin:0 0 18px!important;text-transform:none!important;max-width:18ch}
' . $p . ' .single-posts-meta{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:16px}
' . $p . ' .single-posts-meta *{background:none!important;border:0!important;box-shadow:none!important;
  padding:0!important;font-family:var(--mono)!important;font-size:11px!important;
  letter-spacing:.08em;text-transform:uppercase;color:var(--tinta-3)!important;border-radius:0!important}
' . $p . ' .single-posts-intro{font-family:var(--optima)!important;color:var(--tinta-2)!important;
  font-size:17.5px!important;line-height:1.6;max-width:52ch}
' . $p . ' .single-posts-btn{background:var(--magenta)!important;background-image:none!important;
  -webkit-background-clip:border-box!important;background-clip:border-box!important;
  -webkit-text-fill-color:#fff!important;color:#fff!important;border:1px solid var(--magenta)!important;
  border-radius:2px!important;box-shadow:none!important;font-family:var(--optima)!important;
  font-size:16px!important;font-weight:400!important;letter-spacing:0!important;
  text-transform:none!important;padding:14px 26px!important;margin-top:24px!important}
' . $p . ' .single-posts-btn:hover{background:#FF3D97!important;border-color:#FF3D97!important}
' . $p . ' .single-posts-image-card{border:1px solid var(--linea-2)!important;border-radius:3px!important;
  box-shadow:0 40px 90px -40px rgba(0,0,0,.9)!important;background:var(--carbon)!important;
  padding:0!important;overflow:hidden}
' . $p . ' .single-posts-image-card::before,' . $p . ' .single-posts-image-card::after{border-radius:0!important}
' . $p . ' .single-posts-image{display:block;width:100%;height:auto;border-radius:0!important;margin:0!important}
/* La hoja del plugin fija la foto a 390 px de alto con !important dentro de una
   caja 4:3: si la caja mide menos de 390 de alto, la foto se sale y se corta
   por abajo. Se le da la misma proporción que a la caja y la llena entera. */
' . $p . ' .single-posts-image-card img{width:100%!important;height:auto!important;aspect-ratio:4/3;
  object-fit:cover!important;max-height:none!important}
/* entrada sin imagen destacada: el plugin deja un aviso en un recuadro redondo */
' . $p . ' .single-posts-image-fallback{border:1px dashed var(--linea-2)!important;border-radius:2px!important;
  background:var(--carbon-2)!important;box-shadow:none!important;color:var(--tinta-3)!important;
  font-family:var(--mono)!important;font-size:11px!important;font-weight:400!important;letter-spacing:.06em}

/* cuerpo: una columna de lectura, no un panel ancho */
' . $p . ' .single-posts-content-card{background:var(--carbon)!important;
  border:1px solid var(--linea)!important;border-radius:3px!important;box-shadow:none!important;
  backdrop-filter:none!important;padding:clamp(24px,4vw,56px)!important;color:var(--tinta-2)!important;
  font-family:var(--optima)!important;font-size:17.5px!important;line-height:1.72!important}
' . $p . ' .single-posts-content-card > *{max-width:68ch;margin-inline:auto}
' . $p . ' .single-posts-content-card h2{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(25px,2.6vw,34px)!important;line-height:1.15!important;letter-spacing:-.01em;
  color:var(--tinta)!important;margin:1.9em auto .6em!important;padding-top:.9em;
  border-top:1px solid var(--linea);text-transform:none!important}
' . $p . ' .single-posts-content-card > h2:first-child{border-top:0;padding-top:0;margin-top:0!important}
' . $p . ' .single-posts-content-card h3{font-family:var(--optima)!important;font-weight:400!important;
  font-size:21px!important;line-height:1.25!important;color:var(--tinta)!important;
  margin:1.6em auto .45em!important;text-transform:none!important}
' . $p . ' .single-posts-content-card h4{font-family:var(--mono)!important;font-weight:500!important;
  font-size:12px!important;letter-spacing:.12em;text-transform:uppercase;color:var(--tinta-3)!important;
  margin:1.5em auto .5em!important}
' . $p . ' .single-posts-content-card p{margin:0 auto 1.05em!important}
' . $p . ' .single-posts-content-card strong{color:var(--tinta)!important;font-weight:600}
' . $p . ' .single-posts-content-card em{color:var(--tinta)}
' . $p . ' .single-posts-content-card a{color:var(--magenta)!important;text-decoration:underline;
  text-decoration-color:color-mix(in srgb,var(--magenta) 40%,transparent);text-underline-offset:3px;
  -webkit-text-fill-color:currentColor!important;background:none!important}
' . $p . ' .single-posts-content-card a:hover{text-decoration-color:var(--magenta)}
/* listas: viñeta en magenta, como los guiones del producto destacado */
' . $p . ' .single-posts-content-card ul,' . $p . ' .single-posts-content-card ol{
  padding-left:1.35em;margin:0 auto 1.2em!important}
' . $p . ' .single-posts-content-card li{margin-bottom:.45em}
' . $p . ' .single-posts-content-card ul li::marker{color:var(--magenta)}
' . $p . ' .single-posts-content-card ol li::marker{color:var(--magenta);font-family:var(--mono);
  font-size:.85em}
/* BPC-157 (#2128): tres li sueltos, fuera de cualquier lista, que repiten
   palabra por palabra la lista de prohibiciones que va justo encima (WADA,
   NCAA, agencias). Es un duplicado real del contenido; se ocultan solo en esa
   entrada. Siguen en el HTML: el arreglo de fondo es quitarlos del post. */
html body.postid-2128[class][class] .single-posts-content-card > li{display:none!important}
/* tablas: cabecera en monoespaciada y solo líneas horizontales */
' . $p . ' .single-posts-content-card table{width:100%;max-width:68ch;border-collapse:collapse;
  margin:1.4em auto 1.6em!important;font-size:15.5px;background:none!important;border:0!important}
/* Varias entradas pintan filas alternas en línea (un tr con style
   background-color #f9f9f9, #f2f2f2, #fafafa, #f4f4f4) y una cabecera #2c3e50: en el tema
   oscuro eran franjas blancas con el texto claro encima, ilegible. */
' . $p . ' .single-posts-content-card tr,' . $p . ' .single-posts-content-card thead,
' . $p . ' .single-posts-content-card tbody{background:none!important;background-color:transparent!important;
  color:inherit!important}
' . $p . ' .single-posts-content-card th{font-family:var(--mono)!important;font-size:10.5px!important;
  letter-spacing:.12em;text-transform:uppercase;font-weight:500;color:var(--tinta-3)!important;
  text-align:left;padding:10px 12px!important;border:0!important;border-bottom:1px solid var(--linea-2)!important;
  background:none!important}
' . $p . ' .single-posts-content-card td{padding:11px 12px!important;border:0!important;
  border-bottom:1px solid var(--linea)!important;background:none!important;color:var(--tinta-2)!important;
  vertical-align:top}
' . $p . ' .single-posts-content-card tr:hover td{background:var(--carbon-2)!important}
@media (max-width:640px){
  ' . $p . ' .single-posts-content-card table{display:block;overflow-x:auto;white-space:nowrap}
}
' . $p . ' .single-posts-content-card figure{margin:1.6em auto!important}
/* la hoja del plugin les pone 22–24 px de radio con !important y sombra */
' . $p . ' .single-posts-content-card img:not(.emoji){max-width:100%;height:auto;border-radius:3px!important;
  border:1px solid var(--linea);box-shadow:none!important}
' . $p . ' .single-posts-content-card figcaption{font-family:var(--mono);font-size:11px;
  letter-spacing:.05em;color:var(--tinta-3);margin-top:8px;text-align:center}
' . $p . ' .single-posts-content-card blockquote{border-left:2px solid var(--magenta);margin:1.5em auto!important;
  padding:.2em 0 .2em 1.2em;color:var(--tinta);font-style:italic;background:none!important}
' . $p . ' .single-posts-content-card hr{border:0;border-top:1px solid var(--linea);margin:2em auto}
' . $p . ' .single-posts-content-card code{font-family:var(--mono);font-size:.88em;
  background:var(--panel);padding:.1em .4em;border-radius:2px;color:var(--tinta)}
/* «Revisado y aprobado por»: un div con estilo en línea (fondo #f0f7ff, borde
   azul, texto #1a1a1a) en cinco entradas. Era un recuadro blanco en medio de la
   lectura, y encima corrido a la izquierda de la columna por su `margin` en
   línea. Pasa a ser una ficha de datos del sistema. Los strong traen
   `color:#1a1a1a !important` en línea, que ninguna hoja puede vencer: se pintan
   con -webkit-text-fill-color, que manda sobre `color` al dibujar el texto. */
' . $p . ' .single-posts-content-card div[style*="f0f7ff"]{background:var(--carbon-2)!important;
  border:1px solid var(--linea-2)!important;border-left:2px solid var(--aqua)!important;
  border-radius:2px!important;color:var(--tinta-2)!important;box-shadow:none!important;
  margin:1.6em auto!important;padding:14px 18px!important;font-size:15.5px;line-height:1.6;
  -webkit-text-fill-color:var(--tinta-2)!important}
' . $p . ' .single-posts-content-card [style*="1a1a1a"]{-webkit-text-fill-color:var(--tinta)!important}

/* llamada final: el recuadro de estado de la sección de COA */
' . $p . ' .single-posts-cta-section{padding:clamp(28px,4vw,56px) 0!important;font-family:var(--optima)!important}
' . $p . ' .single-posts-cta{background:var(--carbon)!important;border:1px solid var(--linea-2)!important;
  border-radius:3px!important;box-shadow:none!important;padding:clamp(22px,3vw,36px)!important;
  text-align:left!important;max-width:820px!important;margin-inline:auto!important}
' . $p . ' .single-posts-cta-title{font-family:var(--optima)!important;font-weight:400!important;
  font-size:clamp(22px,2.6vw,30px)!important;color:var(--tinta)!important;margin:0 0 10px!important;
  text-transform:none!important;-webkit-text-fill-color:currentColor!important;background:none!important}
' . $p . ' .single-posts-cta-text{font-family:var(--optima)!important;color:var(--tinta-2)!important;
  font-size:16px!important;line-height:1.6}
';
}
