<?php
/**
 * Plugin Name: PYS — Certificados de análisis (COA)
 * Description: Guarda el certificado de análisis de cada producto (lote, pureza,
 *              masa, identidad, laboratorio y PDF) y lo pinta en su ficha. Los
 *              datos viven en un meta del producto, así que añadir el siguiente
 *              COA es rellenar la caja del editor y subir el PDF, sin tocar código.
 *              El listado `pys_coa_productos()` es el que alimentará la futura
 *              página índice de certificados.
 * Version:     1.0.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const PYS_COA_META = '_pys_coa';

/** Campos del certificado. La clave es la del meta; el valor, su etiqueta. */
function pys_coa_campos() {
	return array(
		'lote'           => 'Número de lote',
		'pureza'         => 'Pureza cromatográfica (%)',
		'masa'           => 'Masa total de péptido (mg)',
		'pct_etiqueta'   => '% de la cantidad declarada',
		'identidad'      => 'Identidad por espectrometría',
		'metodo'         => 'Método',
		'laboratorio'    => 'Laboratorio',
		'lab_num'        => 'Referencia del laboratorio',
		'fecha_analisis' => 'Fecha de análisis (AAAA-MM-DD)',
		'fecha_emision'  => 'Fecha de emisión (AAAA-MM-DD)',
		'pdf'            => 'ID del PDF en la mediateca',
	);
}

/**
 * Devuelve el COA de un producto, o array vacío si no tiene.
 * Se considera que NO hay certificado mientras falte el lote o el PDF: media
 * ficha rellenada no es un certificado y no debe pintar nada en la tienda.
 */
function pys_coa_get( $post_id ) {
	$coa = get_post_meta( $post_id, PYS_COA_META, true );
	if ( ! is_array( $coa ) || empty( $coa['lote'] ) || empty( $coa['pdf'] ) ) {
		return array();
	}
	$coa['pdf_url'] = wp_get_attachment_url( (int) $coa['pdf'] );
	return $coa['pdf_url'] ? $coa : array();
}

/** Productos publicados que ya tienen certificado. Para la página índice. */
function pys_coa_productos() {
	$ids = get_posts(
		array(
			'post_type'      => 'product',
			'post_status'    => 'publish',
			'posts_per_page' => -1,
			'fields'         => 'ids',
			'meta_key'       => PYS_COA_META,
			'orderby'        => 'title',
			'order'          => 'ASC',
		)
	);
	$out = array();
	foreach ( $ids as $id ) {
		$coa = pys_coa_get( $id );
		if ( $coa ) {
			$out[ $id ] = $coa;
		}
	}
	return $out;
}

/* ─── caja en el editor del producto ─────────────────────────────────── */

add_action(
	'add_meta_boxes',
	function () {
		add_meta_box(
			'pys-coa',
			'Certificado de análisis (COA)',
			'pys_coa_caja',
			'product',
			'normal',
			'default'
		);
	}
);

function pys_coa_caja( $post ) {
	$coa = get_post_meta( $post->ID, PYS_COA_META, true );
	$coa = is_array( $coa ) ? $coa : array();
	wp_nonce_field( 'pys_coa_guardar', 'pys_coa_nonce' );
	echo '<p style="margin:0 0 12px;color:#666">Se publica en la ficha solo cuando estén el '
		. '<strong>número de lote</strong> y el <strong>ID del PDF</strong>. El PDF se sube antes a '
		. 'Medios y aquí se pone su ID.</p><table class="form-table"><tbody>';
	foreach ( pys_coa_campos() as $clave => $etiqueta ) {
		$val = isset( $coa[ $clave ] ) ? $coa[ $clave ] : '';
		printf(
			'<tr><th style="width:220px"><label for="pys_coa_%1$s">%2$s</label></th>'
			. '<td><input type="text" id="pys_coa_%1$s" name="pys_coa[%1$s]" value="%3$s" class="regular-text"></td></tr>',
			esc_attr( $clave ),
			esc_html( $etiqueta ),
			esc_attr( $val )
		);
	}
	echo '</tbody></table>';
}

add_action(
	'save_post_product',
	function ( $post_id ) {
		if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
			return;
		}
		if ( ! isset( $_POST['pys_coa_nonce'] )
			|| ! wp_verify_nonce( sanitize_key( wp_unslash( $_POST['pys_coa_nonce'] ) ), 'pys_coa_guardar' ) ) {
			return;
		}
		if ( ! current_user_can( 'edit_post', $post_id ) || ! isset( $_POST['pys_coa'] ) ) {
			return;
		}
		$sucio = wp_unslash( $_POST['pys_coa'] ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
		$limpio = array();
		foreach ( array_keys( pys_coa_campos() ) as $clave ) {
			if ( isset( $sucio[ $clave ] ) && '' !== trim( $sucio[ $clave ] ) ) {
				$limpio[ $clave ] = sanitize_text_field( $sucio[ $clave ] );
			}
		}
		if ( $limpio ) {
			update_post_meta( $post_id, PYS_COA_META, $limpio );
		} else {
			delete_post_meta( $post_id, PYS_COA_META );
		}
	}
);

/* ─── ficha de producto ──────────────────────────────────────────────── */

/** Una línea junto al precio, para que se vea sin bajar hasta el panel. */
add_action(
	'woocommerce_single_product_summary',
	function () {
		$coa = pys_coa_get( get_the_ID() );
		if ( ! $coa ) {
			return;
		}
		printf(
			'<p class="pys-coa-aviso"><a href="#pys-coa">Certificado de análisis del lote %s · pureza %s %%</a></p>',
			esc_html( $coa['lote'] ),
			esc_html( $coa['pureza'] )
		);
	},
	35
);

/** El panel completo, justo antes de las pestañas. */
add_action(
	'woocommerce_after_single_product_summary',
	function () {
		$coa = pys_coa_get( get_the_ID() );
		if ( ! $coa ) {
			return;
		}
		$fecha = static function ( $iso ) {
			$t = $iso ? strtotime( $iso ) : false;
			return $t ? date_i18n( 'j \d\e F \d\e Y', $t ) : '';
		};
		$filas = array();
		if ( ! empty( $coa['pureza'] ) ) {
			$filas[] = array( 'Pureza cromatográfica', $coa['pureza'] . ' %' );
		}
		if ( ! empty( $coa['masa'] ) ) {
			$masa = $coa['masa'] . ' mg';
			if ( ! empty( $coa['pct_etiqueta'] ) ) {
				$masa .= ' (' . $coa['pct_etiqueta'] . ' % de lo declarado)';
			}
			$filas[] = array( 'Masa total de péptido', $masa );
		}
		if ( ! empty( $coa['identidad'] ) ) {
			$filas[] = array( 'Identidad por espectrometría', $coa['identidad'] );
		}
		if ( ! empty( $coa['metodo'] ) ) {
			$filas[] = array( 'Método', $coa['metodo'] );
		}
		?>
		<section class="pys-coa" id="pys-coa">
			<div class="pys-coa-cab">
				<span class="et">Certificado de análisis</span>
				<h2>Lote <?php echo esc_html( $coa['lote'] ); ?></h2>
			</div>
			<dl class="pys-coa-datos">
				<?php foreach ( $filas as $f ) : ?>
					<div><dt><?php echo esc_html( $f[0] ); ?></dt><dd><?php echo esc_html( $f[1] ); ?></dd></div>
				<?php endforeach; ?>
			</dl>
			<p class="pys-coa-pie">
				<?php
				$partes = array();
				if ( ! empty( $coa['laboratorio'] ) ) {
					$partes[] = 'Analizado por ' . $coa['laboratorio'];
				}
				if ( ! empty( $coa['lab_num'] ) ) {
					$partes[] = 'referencia ' . $coa['lab_num'];
				}
				if ( ! empty( $coa['fecha_emision'] ) ) {
					$partes[] = 'emitido el ' . $fecha( $coa['fecha_emision'] );
				}
				echo esc_html( implode( ' · ', $partes ) );
				?>
			</p>
			<p class="pys-coa-ojo">Este certificado corresponde al lote
				<strong><?php echo esc_html( $coa['lote'] ); ?></strong>. Comprueba que coincida con el
				impreso en la etiqueta de tu vial: un COA de otro lote no dice nada del tuyo.</p>
			<a class="pys-coa-btn" href="<?php echo esc_url( $coa['pdf_url'] ); ?>" target="_blank" rel="noopener">
				Ver el certificado completo (PDF)
			</a>
		</section>
		<?php
	},
	9
);

add_action(
	'wp_enqueue_scripts',
	function () {
		if ( ! function_exists( 'is_product' ) || ! is_product() || ! pys_coa_get( get_queried_object_id() ) ) {
			return;
		}
		$css = '
.pys-coa{margin:38px 0;padding:26px 28px;border:1px solid rgba(238,246,243,.16);border-radius:4px;
  background:rgba(10,18,16,.72);color:#EEF6F3}
.pys-coa .et{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#718C84;display:block}
.pys-coa h2{margin:8px 0 0;font-size:26px;line-height:1.15;color:#EEF6F3}
.pys-coa-datos{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1px;
  margin:22px 0 0;padding:0;background:rgba(238,246,243,.12);border:1px solid rgba(238,246,243,.12);
  border-radius:3px;overflow:hidden}
.pys-coa-datos > div{background:#0A1210;padding:14px 16px;margin:0}
.pys-coa-datos dt{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:#718C84;
  margin:0 0 6px}
.pys-coa-datos dd{margin:0;font-family:ui-monospace,Consolas,monospace;font-size:15px;color:#02F6C8;
  font-variant-numeric:tabular-nums}
.pys-coa-pie{margin:16px 0 0;font-size:13px;color:#93AAA3}
.pys-coa-ojo{margin:14px 0 0;font-size:13.5px;color:#93AAA3;max-width:70ch}
.pys-coa-ojo strong{color:#EEF6F3}
.pys-coa-btn{display:inline-block;margin-top:20px;padding:13px 24px;border-radius:2px;
  background:#FF047E;color:#fff;font-size:15px;text-decoration:none}
.pys-coa-btn:hover{background:#FF3D97;color:#fff}
.pys-coa-aviso{margin:10px 0 0;font-size:14px}
.pys-coa-aviso a{color:#02F6C8;text-decoration:underline}
';
		wp_register_style( 'pys-coa', false, array(), '1.0.0' );
		wp_enqueue_style( 'pys-coa' );
		wp_add_inline_style( 'pys-coa', $css );
	}
);
