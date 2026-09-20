<?php
/** Corrige URLs escapadas dentro del JSON de Elementor, sin reserializarlo. */
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
$backup_path = '/tmp/raditech-elementor-links-backup-2026-08-05-landing-high-specialty.json';
$backup = [];
$changed = [];

foreach ($ids as $id) {
    $raw = (string) get_post_meta($id, '_elementor_data', true);
    $backup[(string) $id] = $raw;
}
$encoded = wp_json_encode($backup, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if (!$encoded || file_put_contents($backup_path, $encoded) === false) {
    throw new Exception('No se pudo crear respaldo de Elementor');
}

try {
    foreach ($ids as $id) {
        $before = $backup[(string) $id];
        if ($before === '') {
            continue;
        }
        $after = $before;
        $count = 0;
        foreach ($map as $old => $new) {
            $escaped_old = str_replace('/', '\\/', $old);
            $escaped_new = str_replace('/', '\\/', $new);
            $after = str_replace([$old, $escaped_old], [$new, $escaped_new], $after, $one_count);
            $count += $one_count;
        }
        if ($count === 0) {
            continue;
        }
        if (json_decode($after, true) === null) {
            throw new Exception("JSON Elementor inválido tras reemplazo en {$id}");
        }
        update_post_meta($id, '_elementor_data', wp_slash($after));
        delete_post_meta($id, '_elementor_element_cache');
        clean_post_cache($id);
        $readback = (string) get_post_meta($id, '_elementor_data', true);
        foreach ($map as $old => $new) {
            $escaped_old = str_replace('/', '\\/', $old);
            if (strpos($readback, $old) !== false || strpos($readback, $escaped_old) !== false) {
                throw new Exception("Persistió URL Elementor obsoleta en {$id}: {$old}");
            }
        }
        $changed[] = ['id' => $id, 'replacements' => $count];
    }
} catch (Throwable $error) {
    foreach ($backup as $id_string => $raw) {
        $id = (int) $id_string;
        if ($raw === '') {
            delete_post_meta($id, '_elementor_data');
        } else {
            update_post_meta($id, '_elementor_data', wp_slash($raw));
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
