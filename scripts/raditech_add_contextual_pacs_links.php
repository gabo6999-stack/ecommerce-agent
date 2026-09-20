<?php
/** Añade tres interlinks contextuales hacia la landing PACS/RIS con rollback. */
$target = 'https://raditech.mx/sistema-pacs-ris/';
$ids = [1015, 111, 1072];
$backup = [];
foreach ($ids as $id) {
    $backup[(string) $id] = [
        'post_content' => (string) get_post_field('post_content', $id),
        'elementor_data' => (string) get_post_meta($id, '_elementor_data', true),
    ];
}
$backup_path = '/tmp/raditech-contextual-interlinks-before-2026-08-05.json';
$json = wp_json_encode($backup, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
if (!$json || file_put_contents($backup_path, $json) === false) {
    throw new Exception('No se pudo crear respaldo');
}

function replace_once_or_fail($text, $old, $new, $label) {
    $count = substr_count($text, $old);
    if ($count !== 1) {
        throw new Exception("{$label}: se esperaba 1 coincidencia, llegaron {$count}");
    }
    return str_replace($old, $new, $text);
}

function replace_recursive(&$value, $old, $new, &$count) {
    if (is_array($value)) {
        foreach ($value as &$child) {
            replace_recursive($child, $old, $new, $count);
        }
        unset($child);
    } elseif (is_string($value) && strpos($value, $old) !== false) {
        $hits = substr_count($value, $old);
        $value = str_replace($old, $new, $value);
        $count += $hits;
    }
}

$old_1015 = 'el PACS y la plataforma de teleradiología';
$new_1015 = '<a href="https://raditech.mx/sistema-pacs-ris/">el sistema PACS-RIS</a> y la plataforma de teleradiología';
$old_111 = '<p>Si desea conocer nuestros servicios y algunas funcionalidades de nuestro sistema PACS, lo invitamos a ver a solicitar una asesoría gratuita.</p>';
$new_111 = '<p>Si desea conocer nuestros servicios y las funcionalidades de nuestro sistema PACS, consulte la <a href="https://raditech.mx/sistema-pacs-ris/">solución PACS-RIS de Raditech</a> o solicite una asesoría gratuita.</p>';
$old_1072 = 'Un sistema PACS (Picture Archiving and Communication System) robusto';
$new_1072 = 'Un <a href="https://raditech.mx/sistema-pacs-ris/">sistema PACS</a> (Picture Archiving and Communication System) robusto';

try {
    foreach ($ids as $id) {
        $combined = $backup[(string) $id]['post_content'] . $backup[(string) $id]['elementor_data'];
        if (strpos($combined, $target) !== false) {
            throw new Exception("{$id}: ya contiene enlace al destino; abortado para evitar duplicado");
        }
    }

    $content_1015 = replace_once_or_fail($backup['1015']['post_content'], $old_1015, $new_1015, '1015');
    $result = wp_update_post(['ID' => 1015, 'post_content' => $content_1015], true);
    if (is_wp_error($result)) throw new Exception($result->get_error_message());

    $content_1072 = replace_once_or_fail($backup['1072']['post_content'], $old_1072, $new_1072, '1072');
    $result = wp_update_post(['ID' => 1072, 'post_content' => $content_1072], true);
    if (is_wp_error($result)) throw new Exception($result->get_error_message());

    $content_111_count = substr_count($backup['111']['post_content'], $old_111);
    if ($content_111_count !== 2) throw new Exception("111 post_content: se esperaban 2 coincidencias, llegaron {$content_111_count}");
    $content_111 = str_replace($old_111, $new_111, $backup['111']['post_content']);
    $result = wp_update_post(['ID' => 111, 'post_content' => $content_111], true);
    if (is_wp_error($result)) throw new Exception($result->get_error_message());

    $elements = json_decode($backup['111']['elementor_data'], true);
    if (!is_array($elements)) throw new Exception('111: Elementor JSON inválido antes del cambio');
    $elementor_count = 0;
    replace_recursive($elements, $old_111, $new_111, $elementor_count);
    if ($elementor_count !== 1) throw new Exception("111 Elementor: se esperaba 1 coincidencia, llegaron {$elementor_count}");
    $new_elementor = wp_json_encode($elements, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    if (!$new_elementor || json_decode($new_elementor, true) === null) throw new Exception('111: JSON inválido después del cambio');
    update_post_meta(111, '_elementor_data', wp_slash($new_elementor));

    foreach ($ids as $id) {
        delete_post_meta($id, '_elementor_element_cache');
        clean_post_cache($id);
        $combined = (string) get_post_field('post_content', $id) . (string) get_post_meta($id, '_elementor_data', true);
        if (strpos($combined, $target) === false) throw new Exception("{$id}: el enlace no persistió");
    }
} catch (Throwable $error) {
    foreach ($backup as $id_string => $state) {
        $id = (int) $id_string;
        wp_update_post(['ID' => $id, 'post_content' => $state['post_content']]);
        if ($state['elementor_data'] === '') delete_post_meta($id, '_elementor_data');
        else update_post_meta($id, '_elementor_data', wp_slash($state['elementor_data']));
        delete_post_meta($id, '_elementor_element_cache');
        clean_post_cache($id);
    }
    throw $error;
}

echo wp_json_encode([
    'status' => 'PASS',
    'backup_path' => $backup_path,
    'objects_changed' => $ids,
    'target' => $target,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
