<?php
/** Sincroniza la caché de snippets WPCode con los posts ya depurados. */
global $wpdb;
$backup_dir = '/tmp/raditech-medsi-backup-20260806-065438';
$option = get_option('wpcode_snippets', null);
if (!is_array($option)) throw new RuntimeException('wpcode_snippets no es un array.');
$backup_file = $backup_dir . '/wpcode-option-before-sync.json';
if (file_put_contents($backup_file, wp_json_encode($option, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) === false) {
    throw new RuntimeException('No se pudo respaldar la opción WPCode.');
}
$ids = [867, 870, 932, 949];
$codes = [];
foreach ($ids as $id) {
    $codes[$id] = (string) $wpdb->get_var($wpdb->prepare("SELECT post_content FROM {$wpdb->posts} WHERE ID=%d", $id));
    if ($codes[$id] === '') throw new RuntimeException("Snippet {$id} vacío o inexistente.");
}
$updated = [];
function rt_sync_wpcode_items(&$value, $codes, &$updated) {
    if (!is_array($value)) return;
    if (isset($value['id'], $value['code']) && isset($codes[(int)$value['id']])) {
        $id = (int) $value['id'];
        $value['code'] = $codes[$id];
        $value['compiled_code'] = '';
        $value['modified'] = time();
        $updated[] = $id;
    }
    foreach ($value as &$child) rt_sync_wpcode_items($child, $codes, $updated);
    unset($child);
}
rt_sync_wpcode_items($option, $codes, $updated);
$updated = array_values(array_unique($updated));
sort($updated);
if ($updated !== $ids) throw new RuntimeException('No se localizaron exactamente los cuatro snippets: '.wp_json_encode($updated));
if (!update_option('wpcode_snippets', $option, false)) {
    // update_option devuelve false si no cambia; aquí debe cambiar porque la caché estaba obsoleta.
    throw new RuntimeException('WordPress no guardó la opción WPCode actualizada.');
}
wp_cache_flush();
$stored = get_option('wpcode_snippets', null);
$verified = [];
function rt_verify_wpcode_items($value, $codes, &$verified) {
    if (!is_array($value)) return;
    if (isset($value['id'], $value['code']) && isset($codes[(int)$value['id']])) {
        $id = (int)$value['id'];
        if ($value['code'] !== $codes[$id]) throw new RuntimeException("La caché WPCode {$id} no coincide con el post.");
        $verified[] = $id;
    }
    foreach ($value as $child) rt_verify_wpcode_items($child, $codes, $verified);
}
rt_verify_wpcode_items($stored, $codes, $verified);
$verified = array_values(array_unique($verified)); sort($verified);
if ($verified !== $ids) throw new RuntimeException('Verificación WPCode incompleta.');
echo wp_json_encode(['status'=>'PASS','backup_file'=>$backup_file,'updated'=>$updated,'verified'=>$verified], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
