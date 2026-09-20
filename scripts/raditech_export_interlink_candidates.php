<?php
/** Exporta estado completo de tres candidatos antes de añadir interlinks. */
$ids = [1015, 111, 1072];
$out = [];
foreach ($ids as $id) {
    $post = get_post($id);
    if (!$post) {
        throw new Exception("Objeto inexistente: {$id}");
    }
    $out[(string) $id] = [
        'id' => $id,
        'type' => $post->post_type,
        'status' => $post->post_status,
        'slug' => $post->post_name,
        'title' => $post->post_title,
        'post_content' => (string) $post->post_content,
        'elementor_edit_mode' => (string) get_post_meta($id, '_elementor_edit_mode', true),
        'elementor_data' => (string) get_post_meta($id, '_elementor_data', true),
    ];
}
$path = '/tmp/raditech-interlink-candidates-before-2026-08-05.json';
$json = wp_json_encode($out, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if (!$json || file_put_contents($path, $json) === false) {
    throw new Exception('No se pudo escribir el respaldo');
}
echo wp_json_encode([
    'status' => 'PASS',
    'path' => $path,
    'objects' => array_map(function($row) {
        return [
            'id' => $row['id'],
            'type' => $row['type'],
            'slug' => $row['slug'],
            'elementor_edit_mode' => $row['elementor_edit_mode'],
            'post_content_bytes' => strlen($row['post_content']),
            'elementor_bytes' => strlen($row['elementor_data']),
        ];
    }, array_values($out)),
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
