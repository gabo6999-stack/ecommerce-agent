<?php
/** Hace visible el H1 editorial de la guía RIS sin tocar CSS global. */
if (PHP_SAPI !== 'cli') {
    exit(1);
}
$id = 1039;
$old = '<h2>¿Qué es un RIS en Radiología y Por Qué es Fundamental para tu Hospital?</h2>';
$new = '<h1>¿Qué es un sistema RIS y cómo funciona en radiología?</h1>';
$content = get_post_field('post_content', $id, 'raw');
if (substr_count($content, $old) !== 1 || strpos($content, $new) !== false) {
    fwrite(STDERR, "PRECONDITION_FAIL\n");
    exit(1);
}
$backup = [
    'created_at_utc' => gmdate('c'),
    'post_id' => $id,
    'post_content' => $content,
];
$backup_path = '/tmp/raditech-ris-visible-h1-backup-' . gmdate('Ymd-His') . '.json';
if (file_put_contents($backup_path, wp_json_encode($backup, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT)) === false) {
    fwrite(STDERR, "BACKUP_FAIL\n");
    exit(1);
}
$updated = str_replace($old, $new, $content, $count);
$result = wp_update_post(['ID' => $id, 'post_content' => $updated], true);
if (is_wp_error($result) || $count !== 1) {
    wp_update_post(['ID' => $id, 'post_content' => $content]);
    fwrite(STDERR, "ROLLBACK\n");
    exit(1);
}
$stored = get_post_field('post_content', $id, 'raw');
if (substr_count($stored, $new) !== 1 || strpos($stored, $old) !== false) {
    wp_update_post(['ID' => $id, 'post_content' => $content]);
    fwrite(STDERR, "ROLLBACK_VALIDATION\n");
    exit(1);
}
echo wp_json_encode([
    'status' => 'PASS',
    'backup_path' => $backup_path,
    'replacements' => $count,
    'visible_h1_count' => substr_count($stored, $new),
], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . PHP_EOL;
