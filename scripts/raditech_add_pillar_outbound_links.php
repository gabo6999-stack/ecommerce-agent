<?php
/** Añade tres enlaces educativos salientes desde la landing PACS/RIS. */
$id = 883;
$backup_path = '/tmp/raditech-pillar-outbound-links-2026-08-05.json';
$target_links = [
    'https://raditech.mx/sistema-pacs-hospital-guia-completa-digitalizacion/',
    'https://raditech.mx/sistema-pacs-hospital-guia-completa-implementacion/',
];
$replacements = [
    'PACS-RIS Raditech es una solución confiable para almacenamiento, gestión, visualización y distribución de estudios dentro del área de radiología.'
        => 'PACS-RIS Raditech es una solución confiable para almacenamiento, gestión, visualización y distribución de estudios dentro del área de radiología. Para comprender la base técnica, consulta <a href="https://raditech.mx/sistema-pacs-hospital-guia-completa-digitalizacion/">qué es un sistema PACS y cómo funciona</a>.',

    'Solicita información para implementar PACS-RIS Raditech en tu unidad médica, clínica u hospital.'
        => 'Solicita información para implementar PACS-RIS Raditech en tu unidad médica, clínica u hospital. Antes de cotizar, revisa la <a href="https://raditech.mx/sistema-pacs-hospital-guia-completa-implementacion/">guía de implementación de un sistema PACS</a>.',
];

$post = get_post($id);
if (!$post) {
    throw new Exception("Objeto inexistente: {$id}");
}
$backup = [
    'post_content' => (string) $post->post_content,
    'elementor_data' => (string) get_post_meta($id, '_elementor_data', true),
];
$encoded = wp_json_encode($backup, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if (!$encoded || file_put_contents($backup_path, $encoded) === false) {
    throw new Exception('No se pudo crear respaldo');
}

function replace_recursive(&$value, $old, $new, &$count) {
    if (is_array($value)) {
        foreach ($value as &$child) {
            replace_recursive($child, $old, $new, $count);
        }
        unset($child);
    } elseif (is_string($value)) {
        $local = 0;
        $value = str_replace($old, $new, $value, $local);
        $count += $local;
    }
}

try {
    foreach ($target_links as $target) {
        if (strpos($backup['post_content'], $target) !== false || strpos($backup['elementor_data'], $target) !== false || strpos($backup['elementor_data'], str_replace('/', '\\/', $target)) !== false) {
            throw new Exception("El enlace ya existe: {$target}");
        }
    }

    $content = $backup['post_content'];
    $elementor = json_decode($backup['elementor_data'], true);
    if (!is_array($elementor)) {
        throw new Exception('Elementor JSON inválido antes de editar: ' . json_last_error_msg());
    }
    $counts = [];
    foreach ($replacements as $old => $new) {
        $content_count = 0;
        $content = str_replace($old, $new, $content, $content_count);
        $elementor_count = 0;
        replace_recursive($elementor, $old, $new, $elementor_count);
        if ($content_count < 1 || $elementor_count < 1) {
            throw new Exception("Coincidencia insuficiente: content={$content_count}, elementor={$elementor_count}, frase={$old}");
        }
        $counts[] = ['post_content' => $content_count, 'elementor' => $elementor_count];
    }

    $result = wp_update_post(['ID' => $id, 'post_content' => $content], true);
    if (is_wp_error($result)) {
        throw new Exception($result->get_error_message());
    }
    $new_elementor = wp_json_encode($elementor, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    if (!$new_elementor || !update_post_meta($id, '_elementor_data', wp_slash($new_elementor))) {
        throw new Exception('No se pudo guardar Elementor');
    }
    delete_post_meta($id, '_elementor_element_cache');

    $saved_content = (string) get_post_field('post_content', $id);
    $saved_elementor = (string) get_post_meta($id, '_elementor_data', true);
    foreach ($target_links as $target) {
        $elementor_has_target = strpos($saved_elementor, $target) !== false || strpos($saved_elementor, str_replace('/', '\\/', $target)) !== false;
        if (strpos($saved_content, $target) === false || !$elementor_has_target) {
            throw new Exception("Validación falló para {$target}");
        }
    }
} catch (Throwable $error) {
    wp_update_post(['ID' => $id, 'post_content' => $backup['post_content']]);
    update_post_meta($id, '_elementor_data', wp_slash($backup['elementor_data']));
    delete_post_meta($id, '_elementor_element_cache');
    throw $error;
}

echo wp_json_encode([
    'status' => 'PASS',
    'backup_path' => $backup_path,
    'links_added' => count($target_links),
    'counts' => $counts,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
