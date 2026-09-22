<?php
/**
 * Plugin Name: PYS — Capa de diseño global
 * Description: Lleva el sistema visual de la portada al resto del sitio:
 *              cabecera, pie, fondo hexagonal y base tipográfica. Sustituye la
 *              cabecera y el pie de Elementor por los mismos que usa el home,
 *              de modo que no puedan acabar distintos. NO toca contenido: solo
 *              es diseño.
 * Version:     1.0.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

require_once __DIR__ . '/pys-diseno/partes.php';
require_once __DIR__ . '/pys-diseno/catalogo.php';
require_once __DIR__ . '/pys-diseno/ficha.php';
require_once __DIR__ . '/pys-diseno/blog.php';
require_once __DIR__ . '/pys-diseno/tienda.php';

/* ─── familias que rediseñan agentes en paralelo ──────────────────────
   Cada familia vive en SU archivo dentro de pys-diseno/ y define una sola
   función, pys_dis_css_<familia>(). Los ámbitos (qué página es de qué
   familia) se deciden AQUÍ y no en los archivos de los agentes, para que dos
   familias no puedan pisarse. Si un archivo todavía no existe, no pasa nada. */
foreach ( array( 'paginas-elementor', 'landings', 'paginas-planas', 'cuenta', 'utilitarias' ) as $pys_dis_f ) {
	if ( file_exists( __DIR__ . "/pys-diseno/{$pys_dis_f}.php" ) ) {
		require_once __DIR__ . "/pys-diseno/{$pys_dis_f}.php";
	}
}

/** Páginas que ya tienen su propia familia y NO son landings. */
function pys_dis_pagina_especial() {
	if ( is_front_page() || is_home() ) {
		return true;
	}
	return function_exists( 'is_cart' ) && ( is_shop() || is_cart() || is_checkout() || is_account_page() );
}

/** Página hecha con Elementor (con contenido real, no solo el modo marcado). */
function pys_dis_es_pagina_elementor() {
	if ( ! is_page() || pys_dis_pagina_especial() ) {
		return false;
	}
	$id = get_queried_object_id();
	return 'builder' === get_post_meta( $id, '_elementor_edit_mode', true )
		&& strlen( (string) get_post_meta( $id, '_elementor_data', true ) ) > 200;
}

/** Página normal de WordPress (Gutenberg o HTML). */
function pys_dis_es_pagina_plana() {
	return is_page() && ! pys_dis_pagina_especial() && ! pys_dis_es_pagina_elementor();
}

/** Mi cuenta (conectado o no). */
function pys_dis_es_cuenta() {
	return function_exists( 'is_account_page' ) && is_account_page();
}

/** Búsqueda y 404. */
function pys_dis_es_utilitaria() {
	return is_search() || is_404();
}

/**
 * La portada se pinta a sí misma con su propia plantilla —cabecera, pie y todo—
 * así que aquí se la salta para no duplicarle el marcado.
 */
function pys_dis_ajena() {
	return is_front_page();
}

/** Marca el <body> para que la base tipográfica y de color se aplique. */
add_filter(
	'body_class',
	function ( $clases ) {
		if ( ! pys_dis_ajena() ) {
			$clases[] = 'pys-h26';
		}
		return $clases;
	}
);

/** Hoja base, al final del <head> para ganarle al CSS del tema. */
add_action(
	'wp_head',
	function () {
		if ( pys_dis_ajena() ) {
			return;
		}
		$css = pys_dis_css();
		if ( pys_dis_es_catalogo() ) {
			$css .= pys_dis_css_catalogo();
		}
		if ( function_exists( 'is_product' ) && is_product() ) {
			$css .= pys_dis_css_ficha();
		}
		if ( pys_dis_es_blog() ) {
			$css .= pys_dis_css_blog();
		}
		if ( pys_dis_es_tienda() ) {
			$css .= pys_dis_css_tienda();
		}
		$familias = array(
			'pys_dis_css_paginas_elementor' => pys_dis_es_pagina_elementor(),
			'pys_dis_css_landings'          => pys_dis_es_pagina_elementor(),
			'pys_dis_css_paginas_planas'    => pys_dis_es_pagina_plana(),
			'pys_dis_css_cuenta'            => pys_dis_es_cuenta(),
			'pys_dis_css_utilitarias'       => pys_dis_es_utilitaria(),
		);
		foreach ( $familias as $funcion => $aplica ) {
			if ( $aplica && function_exists( $funcion ) ) {
				$css .= call_user_func( $funcion );
			}
		}
		echo '<style data-no-optimize="1">' . $css . '</style>'; // phpcs:ignore WordPress.Security.EscapeOutput
	},
	99
);

/**
 * Fondo, y apagado del hexagonal viejo que el kit de Elementor le pinta al
 * `body`. La regla del sitio es `html body.archive[class]` y hermanas —dos
 * elementos, una clase y un atributo—, así que repetir aquí el atributo tres
 * veces gana por especificidad y no por orden de carga, que con LiteSpeed
 * reordenando e inyectando CSS crítico no es de fiar.
 */
add_action(
	'wp_body_open',
	function () {
		if ( pys_dis_ajena() ) {
			return;
		}
		echo '<style data-no-optimize="1">html body[class][class][class]{background-image:none!important;'
			. 'background-color:#050908!important}</style>';
		pys_dis_fondo();
	}
);

/* ─── sustitución de la cabecera y el pie de Elementor ────────────────
   Elementor imprime sus plantillas de ubicación entre `before_do_{sitio}` y
   `after_do_{sitio}`. Se captura lo que suelta y se tira, y en su lugar va la
   nuestra. Así no hay que desregistrar nada ni tocar las condiciones del Theme
   Builder: si algún día se quiere volver atrás, basta desactivar este plugin. */

$GLOBALS['pys_dis_pintado'] = array( 'header' => false, 'footer' => false );

foreach ( array( 'header', 'footer' ) as $pys_dis_sitio ) {
	add_action(
		"elementor/theme/before_do_{$pys_dis_sitio}",
		function () {
			if ( ! pys_dis_ajena() ) {
				ob_start();
			}
		}
	);
	add_action(
		"elementor/theme/after_do_{$pys_dis_sitio}",
		function () use ( $pys_dis_sitio ) {
			if ( pys_dis_ajena() ) {
				return;
			}
			ob_end_clean();
			if ( 'header' === $pys_dis_sitio ) {
				pys_dis_cabecera();
			} else {
				pys_dis_pie();
			}
			$GLOBALS['pys_dis_pintado'][ $pys_dis_sitio ] = true;
		}
	);
}

/** Si Elementor no tenía plantilla para una ubicación, tampoco la pinta el tema. */
add_filter(
	'hello_elementor_header_footer',
	function ( $valor ) {
		return pys_dis_ajena() ? $valor : false;
	}
);

/**
 * Red de seguridad: si la ubicación de Elementor no llegó a dispararse —no hay
 * plantilla, o sus condiciones no aplican a esta vista— el pie no se habría
 * pintado nunca. Aquí se pinta antes de cerrar.
 */
add_action(
	'wp_footer',
	function () {
		if ( pys_dis_ajena() ) {
			return;
		}
		if ( empty( $GLOBALS['pys_dis_pintado']['footer'] ) ) {
			pys_dis_pie();
			$GLOBALS['pys_dis_pintado']['footer'] = true;
		}
		echo pys_dis_js(); // phpcs:ignore WordPress.Security.EscapeOutput
	},
	5
);

/**
 * Elementor se queda sin su `elementorFrontendConfig` en vistas donde no pinta
 * widgets y revienta dentro del bundle que combina LiteSpeed, arrastrando lo
 * que venga detrás. En la portada ya se desencolaba; aquí NO se toca, porque el
 * resto del sitio sí usa widgets de Elementor en landings y fichas.
 */
