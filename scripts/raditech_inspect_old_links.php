<?php
/** Read-only inventory of legacy internal links in Raditech content. */
$map = [
    'https://raditech.mx/pacs-ris/' => 'https://raditech.mx/sistema-pacs-ris/',
    'https://raditech.mx/teleradiologia/' => 'https://raditech.mx/servicio-teleradiologia/',
    'https://raditech.mx/sistema-de-informacion-hospitalaria-his/' => 'https://raditech.mx/sistema-informacion-hospitalaria-his-guia-completa-mexico/',
    'https://raditech.mx/monitores-grado-medico/' => 'https://raditech.mx/monitores-medicos-radiologia/',
];
$objects = [];
foreach (get_posts(['post_type' => ['post','page'], 'post_status' => 'any', 'numberposts' => -1]) as $post) {
    $content = (string) $post->post_content;
    $elementor = (string) get_post_meta($post->ID, '_elementor_data', true);
    $hits = [];
    foreach ($map as $old => $new) {
        $content_count = substr_count($content, $old);
        $elementor_count = substr_count($elementor, $old);
        if ($content_count || $elementor_count) {
            $hits[] = [
                'old' => $old,
                'new' => $new,
                'post_content' => $content_count,
                'elementor_data' => $elementor_count,
            ];
        }
    }
    if ($hits) {
        $objects[] = [
            'id' => $post->ID,
            'type' => $post->post_type,
            'status' => $post->post_status,
            'slug' => $post->post_name,
            'title' => get_the_title($post),
            'hits' => $hits,
        ];
    }
}
echo wp_json_encode(['status' => 'PASS', 'objects' => $objects], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
