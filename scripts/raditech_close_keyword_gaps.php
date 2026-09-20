<?php
/**
 * Cierra gaps SEO acotados de Raditech sin crear URLs ni canibalizar.
 * Uso: wp eval-file /tmp/raditech_close_keyword_gaps.php
 */
if (PHP_SAPI !== 'cli') {
    exit(1);
}

$ids = [1039, 871, 883];
$meta_keys = [
    'rank_math_title',
    'rank_math_description',
    '_elementor_data',
    '_elementor_element_cache',
];
$backup = [
    'created_at_utc' => gmdate('c'),
    'posts' => [],
    'meta' => [],
];

foreach ($ids as $id) {
    $post = get_post($id, ARRAY_A);
    if (!$post) {
        throw new RuntimeException("No existe el objeto {$id}");
    }
    $backup['posts'][(string) $id] = $post;
    foreach ($meta_keys as $key) {
        $exists = metadata_exists('post', $id, $key);
        $backup['meta'][(string) $id][$key] = [
            'exists' => $exists,
            'value' => $exists ? get_post_meta($id, $key, true) : null,
        ];
    }
}

$backup_path = '/tmp/raditech-coverage-gaps-backup-' . gmdate('Ymd-His') . '.json';
if (file_put_contents($backup_path, wp_json_encode($backup, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT)) === false) {
    throw new RuntimeException('No se pudo escribir el respaldo');
}

function restore_coverage_backup(array $backup): void {
    foreach ($backup['posts'] as $id => $post) {
        wp_update_post([
            'ID' => (int) $id,
            'post_title' => $post['post_title'],
            'post_content' => $post['post_content'],
            'post_excerpt' => $post['post_excerpt'],
            'post_status' => $post['post_status'],
            'post_name' => $post['post_name'],
        ]);
    }
    foreach ($backup['meta'] as $id => $rows) {
        foreach ($rows as $key => $state) {
            if ($state['exists']) {
                update_post_meta((int) $id, $key, wp_slash($state['value']));
            } else {
                delete_post_meta((int) $id, $key);
            }
        }
    }
}

function replace_recursive(&$value, string $search, string $replace, int &$count): void {
    if (is_string($value)) {
        $value = str_replace($search, $replace, $value, $local);
        $count += $local;
        return;
    }
    if (is_array($value)) {
        foreach ($value as &$child) {
            replace_recursive($child, $search, $replace, $count);
        }
        unset($child);
    }
}

function replace_in_post_and_elementor(int $id, string $search, string $replace): array {
    $counts = ['post_content' => 0, '_elementor_data' => 0];
    $content = get_post_field('post_content', $id, 'raw');
    $new_content = str_replace($search, $replace, $content, $counts['post_content']);
    if ($counts['post_content'] > 0) {
        $result = wp_update_post(['ID' => $id, 'post_content' => $new_content], true);
        if (is_wp_error($result)) {
            throw new RuntimeException($result->get_error_message());
        }
    }

    if (metadata_exists('post', $id, '_elementor_data')) {
        $raw = get_post_meta($id, '_elementor_data', true);
        $data = json_decode($raw, true);
        if (!is_array($data)) {
            throw new RuntimeException("_elementor_data inválido en {$id}");
        }
        replace_recursive($data, $search, $replace, $counts['_elementor_data']);
        if ($counts['_elementor_data'] > 0) {
            $json = wp_json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if ($json === false || !update_post_meta($id, '_elementor_data', wp_slash($json))) {
                throw new RuntimeException("No se pudo actualizar Elementor en {$id}");
            }
        }
    }

    if (array_sum($counts) < 1) {
        throw new RuntimeException("No se encontró el marcador esperado en {$id}");
    }
    delete_post_meta($id, '_elementor_element_cache');
    return $counts;
}

try {
    $ris_title = '¿Qué es un sistema RIS y cómo funciona en radiología?';
    $ris_seo_title = 'Sistema RIS: qué es y cómo funciona en radiología | Raditech';
    $ris_description = 'Conoce qué es un sistema RIS, sus funciones y cómo se integra con PACS para gestionar citas, flujo de trabajo e informes radiológicos en hospitales.';

    $result = wp_update_post(['ID' => 1039, 'post_title' => $ris_title], true);
    if (is_wp_error($result)) {
        throw new RuntimeException($result->get_error_message());
    }
    update_post_meta(1039, 'rank_math_title', $ris_seo_title);
    update_post_meta(1039, 'rank_math_description', $ris_description);

    $old_h2 = 'Interpretación DICOM remota con especialistas certificados';
    $new_h2 = 'Interpretación de estudios radiológicos DICOM con especialistas certificados';
    $counts_871 = replace_in_post_and_elementor(871, $old_h2, $new_h2);
    update_post_meta(
        871,
        'rank_math_description',
        'Servicio de teleradiología para interpretación de estudios radiológicos DICOM por especialistas certificados, con cobertura 24/7 para hospitales y clínicas.'
    );

    $pacs_sentence = 'Para comprender la base técnica, consulta <a href="https://raditech.mx/sistema-pacs-hospital-guia-completa-digitalizacion/">qué es un sistema PACS y cómo funciona</a>.';
    $ris_sentence = ' Para conocer cómo se gestiona el flujo operativo, consulta <a href="https://raditech.mx/ris-radiologia-sistema-informacion-radiologica/">qué es un sistema RIS y cómo funciona</a>.';
    $counts_883 = replace_in_post_and_elementor(883, $pacs_sentence, $pacs_sentence . $ris_sentence);

    $stored_1039 = get_post(1039);
    $stored_871 = get_post_meta(871, '_elementor_data', true);
    $stored_883 = get_post_meta(883, '_elementor_data', true);
    $checks = [
        'ris_post_title' => $stored_1039 && $stored_1039->post_title === $ris_title,
        'ris_seo_title' => get_post_meta(1039, 'rank_math_title', true) === $ris_seo_title,
        'ris_description' => get_post_meta(1039, 'rank_math_description', true) === $ris_description,
        'telerad_h2' => strpos($stored_871, $new_h2) !== false,
        'telerad_old_h2_absent' => strpos($stored_871, $old_h2) === false,
        'telerad_description' => strpos(get_post_meta(871, 'rank_math_description', true), 'interpretación de estudios radiológicos') !== false,
        'pillar_ris_link' => strpos($stored_883, 'https://raditech.mx/ris-radiologia-sistema-informacion-radiologica/') !== false,
    ];
    if (in_array(false, $checks, true)) {
        throw new RuntimeException('Falló la validación almacenada: ' . wp_json_encode($checks));
    }

    echo wp_json_encode([
        'status' => 'PASS',
        'backup_path' => $backup_path,
        'counts_871' => $counts_871,
        'counts_883' => $counts_883,
        'checks' => $checks,
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . PHP_EOL;
} catch (Throwable $e) {
    restore_coverage_backup($backup);
    fwrite(STDERR, wp_json_encode([
        'status' => 'ROLLBACK',
        'backup_path' => $backup_path,
        'error' => $e->getMessage(),
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . PHP_EOL);
    exit(1);
}
