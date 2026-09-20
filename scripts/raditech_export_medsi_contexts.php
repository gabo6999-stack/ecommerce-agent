<?php
/** Exporta fragmentos acotados alrededor de Medsi sin modificar WordPress. */
global $wpdb;
$ids = [10, 19, 111, 278, 281, 358, 402, 636, 842, 862, 867, 870, 890, 894, 932, 937, 945, 949, 1015, 1023, 1031, 1068, 1072, 1076, 1087];

function medsi_contexts($value, $radius = 420, $limit = 12) {
    $out = [];
    $offset = 0;
    $lower = strtolower($value);
    while (count($out) < $limit && ($pos = strpos($lower, 'medsi', $offset)) !== false) {
        $start = max(0, $pos - $radius);
        $length = min(strlen($value) - $start, $radius * 2 + 5);
        $out[] = substr($value, $start, $length);
        $offset = $pos + 5;
    }
    return $out;
}

$result = [];
foreach ($ids as $id) {
    $post = get_post($id);
    if (!$post) continue;
    $entry = [
        'ID' => $id,
        'type' => $post->post_type,
        'status' => $post->post_status,
        'slug' => $post->post_name,
        'title' => $post->post_title,
        'post_content' => medsi_contexts((string) $post->post_content),
        'post_excerpt' => medsi_contexts((string) $post->post_excerpt),
        'meta' => [],
    ];
    $meta_rows = $wpdb->get_results($wpdb->prepare(
        "SELECT meta_key, meta_value FROM {$wpdb->postmeta} WHERE post_id=%d AND LOWER(meta_value) LIKE %s",
        $id,
        '%medsi%'
    ));
    foreach ($meta_rows as $row) {
        $entry['meta'][$row->meta_key] = medsi_contexts((string) $row->meta_value);
    }
    if ($entry['post_content'] || $entry['post_excerpt'] || $entry['meta'] || stripos($post->post_title, 'medsi') !== false || stripos($post->post_name, 'medsi') !== false) {
        $result[] = $entry;
    }
}

echo wp_json_encode(['status' => 'PASS', 'objects' => $result], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
