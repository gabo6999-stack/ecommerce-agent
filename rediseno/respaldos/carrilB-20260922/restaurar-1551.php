<?php
/* ROLLBACK del carril B.
 *
 * Devuelve a la pagina 1551 su _elementor_data original (listado a mano).
 * Uso:
 *   scp -q -i ~/.ssh/cmlc -P 65002 1551-_elementor_data.raw.json \
 *       u303216082@145.79.4.65:/tmp/pys-carrilb/1551-original.json
 *   scp -q -i ~/.ssh/cmlc -P 65002 restaurar-1551.php \
 *       u303216082@145.79.4.65:/tmp/pys-carrilb/restaurar-1551.php
 *   ssh ... "cd <docroot> && wp eval-file /tmp/pys-carrilb/restaurar-1551.php && wp litespeed-purge all"
 *
 * Para desactivar solo el shortcode sin tocar la pagina:
 *   rm <docroot>/wp-content/mu-plugins/pys-catalogo-vivo.php
 * (entonces 1551 mostraria el texto literal [pys_catalogo tipo="peptidos"],
 *  asi que el rollback completo es este archivo.)
 */
$json = file_get_contents( '/tmp/pys-carrilb/1551-original.json' );
if ( false === $json ) {
	exit( "ERROR: falta /tmp/pys-carrilb/1551-original.json\n" );
}
$json  = trim( $json );
$datos = json_decode( $json, true );
if ( JSON_ERROR_NONE !== json_last_error() || empty( $datos[0]['elements'][0]['settings']['html'] ) ) {
	exit( "ERROR: el respaldo no parsea\n" );
}
if ( false === strpos( $datos[0]['elements'][0]['settings']['html'], 'pys-products-grid' ) ) {
	exit( "ERROR: el respaldo no trae el listado a mano; abortado\n" );
}
update_post_meta( 1551, '_elementor_data', wp_slash( wp_json_encode( $datos ) ) );
delete_post_meta( 1551, '_elementor_element_cache' );
delete_post_meta( 1551, '_elementor_css' );
$h = json_decode( get_post_meta( 1551, '_elementor_data', true ), true )[0]['elements'][0]['settings']['html'];
printf(
	"RESTAURADO  %d bytes | listado a mano:%s | shortcode:%s\n",
	strlen( $h ),
	false !== strpos( $h, 'pys-products-grid' ) ? 'si' : 'NO',
	false !== strpos( $h, '[pys_catalogo' ) ? 'QUEDA' : 'no'
);
