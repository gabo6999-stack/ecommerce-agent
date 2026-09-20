<?php
/**
 * Corrige los destinos internos restantes detectados en el crawl público:
 * tres enlaces vía 301 y un destino 404.
 * Crea respaldo y revierte todos los objetos si falla la validación.
 */
$map = [
    'https://raditech.mx/pacs-vira-ris/' => 'https://raditech.mx/vira-pacs-sistema-radiologia-digital-hospitales-mexico/',
    'https://raditech.mx/resonancia-magnetica-cardiovascular/' => 'https://raditech.mx/teleradiologia-resonancia-cardiovascular/',
    'https://raditech.mx/tomografia-cardiaca-y-angiotomografia-coronaria/' => 'https://raditech.mx/teleradiologia-tomografia-cardiaca/',
    'https://raditech.mx/x-card/' => 'https://raditech.mx/portal-x-card/',
    '/pacs-vira-ris/' => '/vira-pacs-sistema-radiologia-digital-hospitales-mexico/',
    '/resonancia-magnetica-cardiovascular/' => '/teleradiologia-resonancia-cardiovascular/',
    '/tomografia-cardiaca-y-angiotomografia-coronaria/' => '/teleradiologia-tomografia-cardiaca/',
    '/x-card/' => '/portal-x-card/',
];
$ids = [10, 879, 871];
$backup_path = '/tmp/raditech-remaining-internal-destinations-2026-08-05.json';
$backup = [];
$changes = [];

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
    throw new Exception('No se pudo crear respaldo');
}

try {
    foreach ($ids as $id) {
        $before_content = $backup[(string) $id]['post_content'];
        $before_elementor = $backup[(string) $id]['elementor_data'];
        $after_content = $before_content;
        $after_elementor = $before_elementor;
        $content_count = 0;
        $elementor_count = 0;

        foreach ($map as $old => $new) {
            $local = 0;
            $after_content = str_replace($old, $new, $after_content, $local);
            $content_count += $local;

            $local = 0;
            $after_elementor = str_replace($old, $new, $after_elementor, $local);
            $elementor_count += $local;

            $old_escaped = str_replace('/', '\\/', $old);
            $new_escaped = str_replace('/', '\\/', $new);
            $local = 0;
            $after_elementor = str_replace($old_escaped, $new_escaped, $after_elementor, $local);
            $elementor_count += $local;
        }

        if ($after_content !== $before_content) {
            $result = wp_update_post(['ID' => $id, 'post_content' => $after_content], true);
            if (is_wp_error($result)) {
                throw new Exception("Falló post_content {$id}: " . $result->get_error_message());
            }
        }
        if ($after_elementor !== $before_elementor) {
            json_decode($after_elementor, true);
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception("JSON Elementor inválido en {$id}: " . json_last_error_msg());
            }
            if (!update_post_meta($id, '_elementor_data', wp_slash($after_elementor))) {
                throw new Exception("Falló _elementor_data {$id}");
            }
            delete_post_meta($id, '_elementor_element_cache');
        }
        if ($content_count || $elementor_count) {
            $changes[] = [
                'id' => $id,
                'post_content_replacements' => $content_count,
                'elementor_replacements' => $elementor_count,
            ];
        }
    }

    foreach ($ids as $id) {
        $content = (string) get_post_field('post_content', $id);
        $elementor = (string) get_post_meta($id, '_elementor_data', true);
        foreach ($map as $old => $new) {
            $old_escaped = str_replace('/', '\\/', $old);
            if (strpos($content, $old) !== false || strpos($elementor, $old) !== false || strpos($elementor, $old_escaped) !== false) {
                throw new Exception("Persistió destino antiguo en {$id}: {$old}");
            }
        }
    }
} catch (Throwable $error) {
    foreach ($backup as $id_string => $state) {
        $id = (int) $id_string;
        wp_update_post(['ID' => $id, 'post_content' => $state['post_content']]);
        update_post_meta($id, '_elementor_data', wp_slash($state['elementor_data']));
        delete_post_meta($id, '_elementor_element_cache');
    }
    throw $error;
}

echo wp_json_encode([
    'status' => 'PASS',
    'backup_path' => $backup_path,
    'objects_changed' => count($changes),
    'changes' => $changes,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
