<?php
/**
 * Reemplaza destinos internos obsoletos en objetos conocidos.
 * Crea respaldo JSON remoto antes de escribir y revierte en memoria si falla la validación.
 */
$map = [
    'https://raditech.mx/pacs-ris/' => 'https://raditech.mx/sistema-pacs-ris/',
    'https://raditech.mx/teleradiologia/' => 'https://raditech.mx/servicio-teleradiologia/',
    'https://raditech.mx/teleradiologia-de-alta-especialidad/' => 'https://raditech.mx/teleradiologia-alta-especialidad/',
    'https://raditech.mx/sistema-de-informacion-hospitalaria-his/' => 'https://raditech.mx/sistema-informacion-hospitalaria-his-guia-completa-mexico/',
    'https://raditech.mx/monitores-grado-medico/' => 'https://raditech.mx/monitores-medicos-radiologia/',
    '/pacs-ris/' => '/sistema-pacs-ris/',
    '/teleradiologia-de-alta-especialidad/' => '/teleradiologia-alta-especialidad/',
    '/sistema-de-informacion-hospitalaria-his/' => '/sistema-informacion-hospitalaria-his-guia-completa-mexico/',
    '/monitores-grado-medico/' => '/monitores-medicos-radiologia/',
];
$ids = [883];
$backup_path = '/tmp/raditech-links-backup-2026-08-05-landing-high-specialty.json';
$backup = [];

foreach ($ids as $id) {
    $post = get_post($id);
    if (!$post) {
        throw new Exception("Objeto inexistente: {$id}");
    }
    $backup[(string) $id] = [
        'post_content' => (string) $post->post_content,
        'elementor_data' => (string) get_post_meta($id, '_elementor_data', true),
    ];
}

$encoded = wp_json_encode($backup, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if (!$encoded || file_put_contents($backup_path, $encoded) === false) {
    throw new Exception('No se pudo crear el respaldo remoto');
}

$changed = [];
try {
    foreach ($ids as $id) {
        $before_content = $backup[(string) $id]['post_content'];
        $before_elementor = $backup[(string) $id]['elementor_data'];
        $after_content = str_replace(array_keys($map), array_values($map), $before_content, $count_content);
        $after_elementor = str_replace(array_keys($map), array_values($map), $before_elementor, $count_elementor);

        if ($count_content > 0) {
            $result = wp_update_post(['ID' => $id, 'post_content' => $after_content], true);
            if (is_wp_error($result)) {
                throw new Exception("wp_update_post {$id}: " . $result->get_error_message());
            }
        }
        if ($count_elementor > 0) {
            if (json_decode($after_elementor, true) === null) {
                throw new Exception("Elementor JSON inválido tras reemplazo en {$id}");
            }
            update_post_meta($id, '_elementor_data', wp_slash($after_elementor));
            delete_post_meta($id, '_elementor_element_cache');
        }
        if ($count_content || $count_elementor) {
            clean_post_cache($id);
            $changed[] = [
                'id' => $id,
                'post_content_replacements' => $count_content,
                'elementor_replacements' => $count_elementor,
            ];
        }
    }

    foreach ($ids as $id) {
        $content = (string) get_post_field('post_content', $id);
        $elementor = (string) get_post_meta($id, '_elementor_data', true);
        foreach ($map as $old => $new) {
            if (strpos($content, $old) !== false || strpos($elementor, $old) !== false) {
                throw new Exception("Persistió URL obsoleta en {$id}: {$old}");
            }
        }
    }
} catch (Throwable $error) {
    foreach ($backup as $id_string => $state) {
        $id = (int) $id_string;
        wp_update_post(['ID' => $id, 'post_content' => $state['post_content']]);
        if ($state['elementor_data'] !== '') {
            update_post_meta($id, '_elementor_data', wp_slash($state['elementor_data']));
        } else {
            delete_post_meta($id, '_elementor_data');
        }
        delete_post_meta($id, '_elementor_element_cache');
        clean_post_cache($id);
    }
    throw $error;
}

echo wp_json_encode([
    'status' => 'PASS',
    'backup_path' => $backup_path,
    'objects_changed' => count($changed),
    'changes' => $changed,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
