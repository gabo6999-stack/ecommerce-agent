<?php
/**
 * Plugin Name: PYS — Monografías científicas
 * Description: Crea el tipo de contenido «monografia» y todo lo que cuelga de
 *              él: el espacio de nombres /monografia/, las migas de pan, el
 *              JSON-LD de la molécula y el enlace de ida y vuelta con la ficha
 *              de producto.
 * Version:     1.0.0
 *
 * ⚠️ AVISO — ESTE ARCHIVO SOSTIENE URLS PÚBLICAS.
 * El tipo de contenido «monografia» se registra AQUÍ y en ningún otro sitio.
 * Si se borra o se renombra este mu-plugin, TODAS las URLs /monografia/<slug>/
 * devuelven 404 de golpe: las entradas siguen en la base de datos, pero
 * WordPress deja de saber servirlas y deja de generar sus reglas de reescritura.
 * Antes de tocarlo: respaldo en
 * rediseno/respaldos/monografias-20260922/mu-plugins/ y `wp rewrite flush --hard`
 * después de cualquier cambio en el bloque de `rewrite`.
 *
 * Qué hace, por partes:
 *
 * 1. Registra «monografia» con has_archive = FALSE a propósito. Con archivo, la
 *    plantilla #155 «Elementor Archive» (condición include/archive) se apodera
 *    de /monografia/ y se pierde el control del hub, que es una página normal.
 * 2. Neutraliza el adivinador de 404 de WordPress dentro de /monografia/.
 *    Medido el 2026-09-22, antes de este archivo:
 *      /monografia/bpc-157/     -> 301 a /product/bpc-157/
 *      /monografia/semaglutida/ -> 301 a /product/semaglutida-20mg/
 *    Es `redirect_guess_404_permalink()`, que resuelve el slug contra el
 *    producto (cabecera `x-redirect-by: WordPress`). Un slug sin monografía
 *    tiene que dar 404 limpio, no mandar al robot a una ficha que además puede
 *    pasar a borrador en una fusión.
 * 3. Migas de pan propias y su BreadcrumbList: Rank Math las tiene apagadas
 *    ("breadcrumbs":"off") y aquí sí hacen falta, porque la monografía cuelga
 *    de un hub.
 * 4. JSON-LD de la monografía: WebPage + about → MolecularEntity. NO se usa
 *    MedicalWebPage: arrastra medicalAudience: Patient, que es justo el
 *    encuadre que el sitio evita. El MedicalWebPage que inyecta
 *    pys-seo-tweaks.php se queda donde está, en la ficha de producto.
 * 5. Los datos químicos salen de campos personalizados de la entrada. Ninguno
 *    es obligatorio: lo que falta, sencillamente no se emite.
 *
 * Solo hay UN dato que une monografía y ficha: el campo `_pys_producto_id` de
 * la monografía. De ahí salen los dos sentidos del enlace, así que no puede
 * haber dos verdades.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Campos personalizados de la monografía y su tipo. */
function pys_mono_campos() {
	return array(
		'_pys_producto_id'    => 'integer', // ID de la ficha de producto asociada.
		'_pys_molecula'       => 'string',  // Nombre de la molécula (si no, el título).
		'_pys_alterno'        => 'string',  // Otros nombres, separados por «;».
		'_pys_cas'            => 'string',  // Número CAS.
		'_pys_formula'        => 'string',  // Fórmula molecular.
		'_pys_peso_molecular' => 'string',  // Peso molecular en Da.
		'_pys_secuencia'      => 'string',  // Secuencia de aminoácidos.
		'_pys_pubchem'        => 'string',  // URL de PubChem para sameAs.
		'_pys_citas'          => 'string',  // Una referencia por línea (URL o PMID).
	);
}

/* ─────────────────────────────────────────────────────────────────────
   1. EL TIPO DE CONTENIDO
   ───────────────────────────────────────────────────────────────────── */

add_action(
	'init',
	function () {
		register_post_type(
			'monografia',
			array(
				'labels'             => array(
					'name'               => 'Monografías',
					'singular_name'      => 'Monografía',
					'menu_name'          => 'Monografías',
					'add_new'            => 'Añadir nueva',
					'add_new_item'       => 'Añadir nueva monografía',
					'edit_item'          => 'Editar monografía',
					'new_item'           => 'Nueva monografía',
					'view_item'          => 'Ver monografía',
					'view_items'         => 'Ver monografías',
					'search_items'       => 'Buscar monografías',
					'not_found'          => 'No hay monografías',
					'not_found_in_trash' => 'No hay monografías en la papelera',
					'all_items'          => 'Todas las monografías',
					'archives'           => 'Monografías',
				),
				'public'             => true,
				'publicly_queryable' => true,
				'show_ui'            => true,
				'show_in_menu'       => true,
				'show_in_nav_menus'  => true,
				'show_in_rest'       => true,
				'menu_position'      => 21,
				'menu_icon'          => 'dashicons-analytics',
				'hierarchical'       => false,
				'has_archive'        => false, // A propósito: ver la cabecera.
				'rewrite'            => array(
					'slug'       => 'monografia',
					'with_front' => false,
					'feeds'      => false,
					'pages'      => true,
				),
				'query_var'          => true,
				'capability_type'    => 'post',
				'map_meta_cap'       => true,
				'supports'           => array(
					'title',
					'editor',
					'excerpt',
					'thumbnail',
					'custom-fields',
					'revisions',
				),
			)
		);

		foreach ( pys_mono_campos() as $clave => $tipo ) {
			register_post_meta(
				'monografia',
				$clave,
				array(
					'type'          => $tipo,
					'single'        => true,
					'show_in_rest'  => true,
					'auth_callback' => function () {
						return current_user_can( 'edit_posts' );
					},
				)
			);
		}
	}
);

/* ─────────────────────────────────────────────────────────────────────
   2. EL ADIVINADOR DE 404, NEUTRALIZADO DENTRO DE /monografia/
   ───────────────────────────────────────────────────────────────────── */

/** ¿La petición cae dentro del espacio de nombres /monografia/? */
function pys_mono_en_namespace() {
	if ( empty( $_SERVER['REQUEST_URI'] ) ) {
		return false;
	}
	$ruta = wp_parse_url( wp_unslash( $_SERVER['REQUEST_URI'] ), PHP_URL_PATH ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
	if ( ! is_string( $ruta ) ) {
		return false;
	}
	$ruta = '/' . ltrim( $ruta, '/' );
	return 0 === strpos( $ruta, '/monografia/' ) || '/monografia' === rtrim( $ruta, '/' );
}

/**
 * WordPress 5.5+ consulta este filtro antes de intentar adivinar a qué se
 * parece una URL que dio 404. Dentro de /monografia/ no se adivina nada.
 */
add_filter(
	'do_redirect_guess_404_permalink',
	function ( $adivinar ) {
		return pys_mono_en_namespace() ? false : $adivinar;
	}
);

/**
 * Cinturón y tirantes: si alguna versión futura, o un plugin, vuelve a producir
 * un destino para un 404 de este espacio de nombres, aquí se tira. Solo actúa
 * sobre 404: las canonicalizaciones normales (barra final, mayúsculas) siguen
 * funcionando dentro de /monografia/.
 */
add_filter(
	'redirect_canonical',
	function ( $destino ) {
		if ( is_404() && pys_mono_en_namespace() ) {
			return false;
		}
		return $destino;
	},
	99
);

/* ─────────────────────────────────────────────────────────────────────
   3. MIGAS DE PAN Y ENLACE A LA FICHA, DENTRO DEL CONTENIDO
   ───────────────────────────────────────────────────────────────────── */

/** La página hub /monografia/, si existe y está publicada. */
function pys_mono_hub() {
	static $hub = null;
	if ( null === $hub ) {
		$p   = get_page_by_path( 'monografia', OBJECT, 'page' );
		$hub = ( $p && 'publish' === $p->post_status ) ? $p : false;
	}
	return $hub;
}

/** Nombre de la molécula de una monografía (campo propio o, si no, el título). */
function pys_mono_molecula( $id ) {
	$m = trim( (string) get_post_meta( $id, '_pys_molecula', true ) );
	return '' !== $m ? $m : get_the_title( $id );
}

/** La ficha de producto asociada a una monografía, si sigue publicada. */
function pys_mono_producto( $id ) {
	$pid = (int) get_post_meta( $id, '_pys_producto_id', true );
	if ( $pid <= 0 ) {
		return false;
	}
	$p = get_post( $pid );
	return ( $p && 'product' === $p->post_type && 'publish' === $p->post_status ) ? $p : false;
}

/** ¿Estamos pintando el cuerpo de una monografía en su propia página? */
function pys_mono_en_singular() {
	return is_singular( 'monografia' ) && in_the_loop() && is_main_query();
}

/**
 * Migas arriba y bloque «Disponible para investigación» abajo.
 *
 * Van por el filtro del contenido porque la plantilla del tema
 * (hello-elementor/template-parts/single.php) no ofrece ningún gancho entre el
 * H1 y el cuerpo. Las migas quedan justo debajo del título.
 */
add_filter(
	'the_content',
	function ( $contenido ) {
		if ( ! pys_mono_en_singular() ) {
			return $contenido;
		}
		return pys_mono_migas() . $contenido . pys_mono_bloque_ficha();
	}
);

/** Migas visibles «Inicio › Monografías › <molécula>». */
function pys_mono_migas() {
	$id  = get_queried_object_id();
	$hub = pys_mono_hub();

	$medio = $hub
		? '<a href="' . esc_url( get_permalink( $hub ) ) . '">Monografías</a>'
		: '<span>Monografías</span>';

	return '<nav class="pys-mono-migas" aria-label="Migas de pan">'
		. '<a href="' . esc_url( home_url( '/' ) ) . '">Inicio</a>'
		. '<span class="pys-mono-sep" aria-hidden="true">›</span>'
		. $medio
		. '<span class="pys-mono-sep" aria-hidden="true">›</span>'
		. '<span aria-current="page">' . esc_html( pys_mono_molecula( $id ) ) . '</span>'
		. '</nav>';
}

/** Bloque final con el enlace a la ficha, solo si hay ficha viva. */
function pys_mono_bloque_ficha() {
	$id       = get_queried_object_id();
	$producto = pys_mono_producto( $id );
	if ( ! $producto ) {
		return '';
	}
	$molecula = pys_mono_molecula( $id );

	return '<aside class="pys-mono-ficha">'
		. '<p class="pys-mono-ficha-et">Disponible para investigación</p>'
		. '<p class="pys-mono-ficha-tx">'
		. esc_html( $molecula ) . ' con certificado de análisis por lote, para uso exclusivo '
		. 'en investigación.</p>'
		. '<p class="pys-mono-ficha-cta"><a href="' . esc_url( get_permalink( $producto ) ) . '">'
		. 'Ver la ficha de ' . esc_html( $molecula ) . '</a></p>'
		. '</aside>';
}

/* ─────────────────────────────────────────────────────────────────────
   4. EL ENLACE INVERSO, EN LA FICHA DE PRODUCTO
   ───────────────────────────────────────────────────────────────────── */

/** La monografía publicada que apunta a este producto, si la hay. */
function pys_mono_de_producto( $producto_id ) {
	static $cache = array();
	$producto_id  = (int) $producto_id;
	if ( isset( $cache[ $producto_id ] ) ) {
		return $cache[ $producto_id ];
	}
	$encontradas = get_posts(
		array(
			'post_type'              => 'monografia',
			'post_status'            => 'publish',
			'posts_per_page'         => 1,
			'ignore_sticky_posts'    => true,
			'no_found_rows'          => true,
			'update_post_term_cache' => false,
			'meta_key'               => '_pys_producto_id', // phpcs:ignore WordPress.DB.SlowDBQuery
			'meta_value'             => $producto_id,       // phpcs:ignore WordPress.DB.SlowDBQuery
		)
	);
	$cache[ $producto_id ] = $encontradas ? $encontradas[0] : false;
	return $cache[ $producto_id ];
}

/**
 * Prioridad 45: después del botón de compra (30) y del meta (40), antes de las
 * pestañas. No se pisa con pys-seo-tweaks.php, que cuelga de
 * woocommerce_after_single_product_summary en 11.
 */
add_action(
	'woocommerce_single_product_summary',
	function () {
		if ( ! is_singular( 'product' ) ) {
			return;
		}
		$mono = pys_mono_de_producto( get_queried_object_id() );
		if ( ! $mono ) {
			return;
		}
		$molecula = pys_mono_molecula( $mono->ID );
		/* El estilo va EN LÍNEA a propósito. Este párrafo se pinta dentro de la
		   ficha de producto, cuya hoja de diseño (pys-diseno/ficha.php) es de
		   otro agente y no se toca. Mismo criterio que el bloque «Revisado por»
		   de pys-seo-tweaks.php. Los tokens (--mono, --magenta, --linea-2) los
		   define la capa global en todas las vistas menos la portada. */
		echo '<p class="pys-mono-enlace" style="margin:1.1rem 0 0;padding-top:1rem;'
			. 'border-top:1px solid var(--linea-2,#22362F);font-family:var(--mono,ui-monospace,monospace);'
			. 'font-size:12px;letter-spacing:.06em">'
			. '<a href="' . esc_url( get_permalink( $mono ) ) . '" '
			. 'style="color:var(--magenta,#FF047E);text-decoration:underline;text-underline-offset:3px">'
			. 'Monografía científica de ' . esc_html( $molecula ) . '</a></p>';
	},
	45
);

/* ─────────────────────────────────────────────────────────────────────
   5. EL JSON-LD DE LA MONOGRAFÍA
   ───────────────────────────────────────────────────────────────────── */

add_action(
	'wp_head',
	function () {
		if ( ! is_singular( 'monografia' ) ) {
			return;
		}
		$id  = get_queried_object_id();
		$url = get_permalink( $id );

		/* ── migas ── */
		$items = array(
			array(
				'@type'    => 'ListItem',
				'position' => 1,
				'name'     => 'Inicio',
				'item'     => home_url( '/' ),
			),
		);
		$hub = pys_mono_hub();
		if ( $hub ) {
			$items[] = array(
				'@type'    => 'ListItem',
				'position' => 2,
				'name'     => 'Monografías',
				'item'     => get_permalink( $hub ),
			);
		}
		/* El último eslabón no lleva `item`: es la página actual. Y si el hub
		   todavía no existe como página, no se inventa: se emiten dos eslabones
		   en vez de tres, para no declarar una URL que da 404. */
		$items[] = array(
			'@type'    => 'ListItem',
			'position' => count( $items ) + 1,
			'name'     => pys_mono_molecula( $id ),
		);

		$migas = array(
			'@context'        => 'https://schema.org',
			'@type'           => 'BreadcrumbList',
			'@id'             => $url . '#migas',
			'itemListElement' => $items,
		);

		/* ── la molécula ── */
		$molecula = array(
			'@type' => 'MolecularEntity',
			'name'  => pys_mono_molecula( $id ),
		);

		$alterno = array_filter( array_map( 'trim', explode( ';', (string) get_post_meta( $id, '_pys_alterno', true ) ) ) );
		if ( $alterno ) {
			$molecula['alternateName'] = array_values( $alterno );
		}

		$formula = trim( (string) get_post_meta( $id, '_pys_formula', true ) );
		if ( '' !== $formula ) {
			$molecula['molecularFormula'] = $formula;
		}

		$peso = trim( (string) get_post_meta( $id, '_pys_peso_molecular', true ) );
		if ( '' !== $peso ) {
			$molecula['molecularWeight'] = array(
				'@type'    => 'QuantitativeValue',
				'value'    => $peso,
				'unitText' => 'Da',
			);
		}

		$cas = trim( (string) get_post_meta( $id, '_pys_cas', true ) );
		if ( '' !== $cas ) {
			$molecula['identifier'] = array(
				'@type'      => 'PropertyValue',
				'propertyID' => 'CAS',
				'value'      => $cas,
			);
		}

		$secuencia = trim( (string) get_post_meta( $id, '_pys_secuencia', true ) );
		if ( '' !== $secuencia ) {
			$molecula['hasBioChemEntityPart'] = array(
				'@type'                  => 'Protein',
				'name'                   => pys_mono_molecula( $id ),
				'hasBioPolymerSequence'  => $secuencia,
			);
		}

		$pubchem = trim( (string) get_post_meta( $id, '_pys_pubchem', true ) );
		if ( '' !== $pubchem ) {
			$molecula['sameAs'] = $pubchem;
		}

		/* ── la página ── */
		$pagina = array(
			'@context'            => 'https://schema.org',
			'@type'               => 'WebPage',
			'@id'                 => $url . '#pagina',
			'url'                 => $url,
			'name'                => get_the_title( $id ),
			'inLanguage'          => 'es-MX',
			'isAccessibleForFree' => true,
			'datePublished'       => get_the_date( 'c', $id ),
			'dateModified'        => get_the_modified_date( 'c', $id ),
			'breadcrumb'          => array( '@id' => $url . '#migas' ),
			'about'               => $molecula,
		);

		$resumen = trim( (string) get_the_excerpt( $id ) );
		if ( '' !== $resumen ) {
			$pagina['description'] = $resumen;
		}

		$citas = array_filter( array_map( 'trim', preg_split( '/\r\n|\r|\n/', (string) get_post_meta( $id, '_pys_citas', true ) ) ) );
		if ( $citas ) {
			$pagina['citation'] = array_values(
				array_map(
					function ( $c ) {
						return array(
							'@type' => 'CreativeWork',
							'url'   => $c,
						);
					},
					$citas
				)
			);
		}

		/* El revisor es el mismo de las fichas y vive en pys-seo-tweaks.php.
		   Se reutiliza si está; no se copia, para que no puedan divergir. */
		if ( function_exists( 'pys_medical_reviewer' ) ) {
			$pagina['reviewedBy']   = pys_medical_reviewer();
			$pagina['lastReviewed'] = get_the_modified_date( 'Y-m-d', $id );
		}

		$bandera = JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES;
		echo '<script type="application/ld+json">' . wp_json_encode( $migas, $bandera ) . '</' . 'script>' . "\n";
		echo '<script type="application/ld+json">' . wp_json_encode( $pagina, $bandera ) . '</' . 'script>' . "\n";
	},
	21
);
