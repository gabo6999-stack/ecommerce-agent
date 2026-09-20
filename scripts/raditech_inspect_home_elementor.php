<?php
$id = 862;
$content = (string) get_post_field('post_content', $id);
$data = (string) get_post_meta($id, '_elementor_data', true);
$needles = ['pacs-ris', 'teleradiologia', 'sistema-de-informacion-hospitalaria-his', 'monitores-grado-medico'];
$out = ['id' => $id, 'post_content_bytes' => strlen($content), 'elementor_bytes' => strlen($data), 'json_valid' => json_decode($data, true) !== null, 'needles' => []];
foreach ($needles as $needle) {
    $content_pos = strpos($content, $needle);
    $elementor_pos = strpos($data, $needle);
    $out['needles'][$needle] = [
        'post_content_count' => substr_count($content, $needle),
        'post_content_snippet' => $content_pos === false ? null : substr($content, max(0, $content_pos - 100), 260),
        'elementor_count' => substr_count($data, $needle),
        'elementor_snippet' => $elementor_pos === false ? null : substr($data, max(0, $elementor_pos - 100), 260),
    ];
}
echo wp_json_encode($out, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
