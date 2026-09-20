<?php
/**
 * Retiro reversible de Medsi en Raditech (fase 1).
 * - Respalda todos los objetos y metadatos afectados.
 * - Retira la marca del contenido y Elementor.
 * - Pasa landing, plantillas y medios dedicados a estados no públicos.
 * - Conserva únicamente el slug antiguo como origen técnico de un 301.
 */
global $wpdb;

$stamp = gmdate('Ymd-His');
$backup_dir = '/tmp/raditech-medsi-backup-' . $stamp;
$media_dir = $backup_dir . '/media';
wp_mkdir_p($media_dir);

function rt_has_medsi($value) {
    return is_string($value) && (stripos($value, 'medsi') !== false || stripos($value, 'medisi') !== false);
}

function rt_remove_html_units($html) {
    if (!is_string($html) || $html === '') return $html;

    // Elementor stores media URLs and filenames as standalone strings.
    if (rt_has_medsi($html)
        && preg_match('~^(?:https?://|/|[^\s]+\.(?:jpe?g|png|webp|gif|svg))~iu', trim($html))) {
        return '';
    }

    // Preserve useful generic claims while removing the discontinued brand.
    $html = str_ireplace(
        ['(Medsi, SAP Healthcare, entre otros)', '¿VIRA PACS puede integrarse con el sistema HIS de nuestra institución si no es Medsi?'],
        ['(incluidos los sistemas existentes de la institución)', '¿VIRA PACS puede integrarse con el sistema HIS de nuestra institución?'],
        $html
    );
    $html = preg_replace('/Si bien la integración nativa con Medsi HIS está documentada y validada,\s*/iu', '', $html);

    // Remove complete Medsi FAQ entries, cards and paragraphs before touching links.
    do {
        $before = $html;
        $html = preg_replace('/<details\b[^>]*>.*?(?:medsi|medisi).*?<\/details>/isu', '', $html);
        $html = preg_replace('/<article\b[^>]*data-panel=["\']his["\'][^>]*>.*?<\/article>/isu', '', $html);
        $html = preg_replace('/<(p|li|h2|h3|h4)\b[^>]*>[^<]*(?:<[^>]+>[^<]*)*?(?:medsi|medisi)[^<]*(?:<[^>]+>[^<]*)*?<\/\1>/isu', '', $html);
    } while ($before !== $html);

    // Remove navigation/product links whose only destination was the retired landing.
    $html = preg_replace('/<li\b[^>]*>\s*<a\b[^>]*sistema-his-medsi[^>]*>.*?<\/a>\s*<\/li>/isu', '', $html);
    $html = preg_replace_callback('/<a\b[^>]*href=["\'][^"\']*sistema-his-medsi\/?[^"\']*["\'][^>]*>(.*?)<\/a>/isu', function($m) {
        $label = trim(wp_strip_all_tags($m[1]));
        if (preg_match('/^(HIS hospitalario|sistema de información hospitalaria(?: \(HIS\))?)$/iu', $label)) {
            return 'HIS institucional';
        }
        return '';
    }, $html);

    // Remove standalone controls/tabs and media whose identity is tied to Medsi.
    $html = preg_replace('/<(button|a|li)\b[^>]*(?:data-(?:tab|target|panel)=["\']#?his["\']|href=["\']#his["\'])[^>]*>.*?<\/\1>/isu', '', $html);
    $html = preg_replace('/<img\b[^>]*(?:medsi|medisi)[^>]*>/isu', '', $html);
    $html = str_ireplace(['https://raditech.mx/sistema-his-medsi/', '/sistema-his-medsi/'], '', $html);

    return $html;
}

function rt_transform_tree($value, $post_id = 0) {
    if (is_string($value)) return rt_remove_html_units($value);
    if (!is_array($value)) return $value;

    $was_list = array_is_list($value);
    $original = $value;

    // Clear Elementor media objects tied to the retired product.
    if (isset($value['url']) && rt_has_medsi((string) $value['url'])) {
        $value['url'] = '';
        if (array_key_exists('id', $value)) $value['id'] = '';
    }
    foreach ($value as $key => $child) {
        $value[$key] = rt_transform_tree($child, $post_id);
    }

    // Remove repeatable FAQ/tab items identified by their original content.
    foreach ($value as $key => $child) {
        $before = $original[$key] ?? null;
        if (is_array($before) && rt_has_medsi(wp_json_encode($before))) {
            if (isset($before['tab_title']) || isset($before['accordion_title']) || isset($before['item_title'])) {
                unset($value[$key]);
            }
        }
    }

    // On the Products page, remove the deepest native Elementor HIS card.
    // Use the original subtree so the marker is not lost after child cleanup.
    if ($post_id === 358) {
        foreach ($value as $key => $child) {
            $before = $original[$key] ?? null;
            if (!is_array($before)) continue;
            $encoded = wp_json_encode($before);
            if (($before['elType'] ?? '') === 'container'
                && rt_has_medsi($encoded)
                && (($before['id'] ?? '') === 'a2d8379'
                    || stripos($encoded, 'Sistema de Informaci') !== false)) {
                unset($value[$key]);
            }
        }
    }

    return $was_list ? array_values($value) : $value;
}

function rt_transform_elementor($raw, $post_id) {
    $decoded = json_decode($raw, true);
    if (!is_array($decoded)) return rt_remove_html_units($raw);
    $decoded = rt_transform_tree($decoded, $post_id);
    return wp_json_encode($decoded, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
}

function rt_transform_wpcode($content, $post_id) {
    if ($post_id === 932 || stripos($content, 'sistema-de-informacion-hospitalaria-his') !== false) {
        $target = '/sistema-informacion-hospitalaria-his-guia-completa-mexico/';
        $content = preg_replace(
            "/'sistema-de-informacion-hospitalaria-his'\s*=>\s*'\/sistema-his-medsi\/',/i",
            "'sistema-de-informacion-hospitalaria-his'         => '{$target}',\n        'sistema-his-medsi'                                => '{$target}',",
            $content
        );
        return $content;
    }
    // Header, footer and breadcrumb snippets: one entry per line.
    $content = preg_replace('/^[^\r\n]*(?:medsi|sistema-his-medsi)[^\r\n]*(?:\r\n|\r|\n)?/im', '', $content);
    return $content;
}

function rt_transform_option($value) {
    if (is_string($value)) {
        if (stripos($value, 'sistema-de-informacion-hospitalaria-his') !== false) {
            return rt_transform_wpcode($value, 932);
        }
        return preg_replace('/^[^\r\n]*(?:medsi|sistema-his-medsi)[^\r\n]*(?:\r\n|\r|\n)?/im', '', $value);
    }
    if (is_array($value)) {
        foreach ($value as $k => $v) $value[$k] = rt_transform_option($v);
    }
    return $value;
}

// Identify every non-revision object containing Medsi/Medisi in post fields or metadata.
$affected_ids = $wpdb->get_col(
    "SELECT DISTINCT p.ID
     FROM {$wpdb->posts} p
     LEFT JOIN {$wpdb->postmeta} pm ON pm.post_id=p.ID
     WHERE p.post_type <> 'revision' AND (
       LOWER(CONCAT_WS(' ',p.post_title,p.post_name,p.post_content,p.post_excerpt,p.guid)) LIKE '%medsi%'
       OR LOWER(CONCAT_WS(' ',p.post_title,p.post_name,p.post_content,p.post_excerpt,p.guid)) LIKE '%medisi%'
       OR LOWER(pm.meta_value) LIKE '%medsi%'
       OR LOWER(pm.meta_value) LIKE '%medisi%'
     )"
);
$affected_ids = array_values(array_unique(array_map('intval', array_merge($affected_ids, [10,19,111,358,402,867,870,890,932,949]))));
$id_csv = implode(',', $affected_ids);

$backup = [
    'created_utc' => gmdate('c'),
    'affected_ids' => $affected_ids,
    'posts' => $wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID IN ({$id_csv})", ARRAY_A),
    'postmeta' => $wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id IN ({$id_csv})", ARRAY_A),
    'options' => $wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name='wpcode_snippets'", ARRAY_A),
    'media_files' => [],
];

// Copy dedicated media outside the document root before changing statuses.
$media_ids = [];
foreach ($backup['posts'] as $row) {
    if ($row['post_type'] !== 'attachment') continue;
    $joined = strtolower($row['post_title'].' '.$row['post_name'].' '.$row['guid']);
    if (strpos($joined, 'medsi') === false && strpos($joined, 'medisi') === false) continue;
    $aid = (int) $row['ID'];
    $media_ids[] = $aid;
    $file = get_attached_file($aid);
    $meta = wp_get_attachment_metadata($aid);
    $files = [];
    if ($file && is_file($file)) $files[] = $file;
    if ($file && is_array($meta) && !empty($meta['sizes'])) {
        $dir = dirname($file);
        foreach ($meta['sizes'] as $size) {
            if (!empty($size['file']) && is_file($dir.'/'.$size['file'])) $files[] = $dir.'/'.$size['file'];
        }
    }
    foreach (array_unique($files) as $src) {
        $dest = $media_dir.'/'.$aid.'-'.basename($src);
        if (!copy($src, $dest)) throw new RuntimeException('No se pudo respaldar medio: '.$src);
        $backup['media_files'][] = ['attachment_id'=>$aid,'source'=>$src,'backup'=>$dest];
    }
}

$backup_file = $backup_dir.'/wordpress-backup.json';
if (file_put_contents($backup_file, wp_json_encode($backup, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) === false) {
    throw new RuntimeException('No se pudo escribir el respaldo JSON.');
}

$changed = [];
try {
    foreach ($backup['posts'] as $row) {
        $id = (int) $row['ID'];
        $type = $row['post_type'];

        if (in_array($id, [19,402,890], true)) {
            $wpdb->update($wpdb->posts, ['post_status'=>'draft'], ['ID'=>$id]);
            $changed[] = "draft:{$id}";
            continue;
        }
        if ($type === 'attachment' && in_array($id, $media_ids, true)) {
            $wpdb->update($wpdb->posts, ['post_status'=>'trash'], ['ID'=>$id]);
            $changed[] = "media-trash:{$id}";
            continue;
        }

        $content = $row['post_content'];
        if ($type === 'wpcode') $content = rt_transform_wpcode($content, $id);
        else $content = rt_remove_html_units($content);
        $excerpt = rt_remove_html_units($row['post_excerpt']);
        if ($content !== $row['post_content'] || $excerpt !== $row['post_excerpt']) {
            $wpdb->update($wpdb->posts, [
                'post_content'=>$content,
                'post_excerpt'=>$excerpt,
                'post_modified'=>current_time('mysql'),
                'post_modified_gmt'=>current_time('mysql', true),
            ], ['ID'=>$id]);
            clean_post_cache($id);
            $changed[] = "post:{$id}";
        }
    }

    foreach ($backup['postmeta'] as $meta) {
        $id = (int) $meta['post_id'];
        if (in_array($id, [19,402,890], true) || in_array($id, $media_ids, true)) continue;
        $new = $meta['meta_value'];
        if ($meta['meta_key'] === '_elementor_data' && rt_has_medsi($new)) {
            $new = rt_transform_elementor($new, $id);
        } elseif (rt_has_medsi($new)) {
            $new = rt_remove_html_units($new);
        }
        if ($new !== $meta['meta_value']) {
            $wpdb->update($wpdb->postmeta, ['meta_value'=>$new], ['meta_id'=>(int)$meta['meta_id']]);
            $changed[] = "meta:{$meta['meta_id']}";
        }
    }

    // Clear rendered Elementor caches for affected public objects.
    if ($id_csv) {
        $wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE post_id IN ({$id_csv}) AND meta_key='_elementor_element_cache'");
    }

    $option = get_option('wpcode_snippets', null);
    if ($option !== null && rt_has_medsi(wp_json_encode($option))) {
        update_option('wpcode_snippets', rt_transform_option($option), false);
        $changed[] = 'option:wpcode_snippets';
    }

    // Validate: one literal is intentionally retained as the source of a 301.
    $remaining = $wpdb->get_results(
        "SELECT p.ID,p.post_type,p.post_status,p.post_name
         FROM {$wpdb->posts} p
         LEFT JOIN {$wpdb->postmeta} pm ON pm.post_id=p.ID
         WHERE p.post_type <> 'revision'
           AND p.post_status NOT IN ('draft','trash','auto-draft','inherit')
           AND p.ID <> 932
           AND (
             LOWER(CONCAT_WS(' ',p.post_title,p.post_name,p.post_content,p.post_excerpt)) LIKE '%medsi%'
             OR LOWER(CONCAT_WS(' ',p.post_title,p.post_name,p.post_content,p.post_excerpt)) LIKE '%medisi%'
             OR LOWER(pm.meta_value) LIKE '%medsi%'
             OR LOWER(pm.meta_value) LIKE '%medisi%'
           )
         GROUP BY p.ID,p.post_type,p.post_status,p.post_name",
        ARRAY_A
    );
    if ($remaining) throw new RuntimeException('Quedaron referencias activas: '.wp_json_encode($remaining));

    $redirect_content = (string) $wpdb->get_var($wpdb->prepare(
        "SELECT post_content FROM {$wpdb->posts} WHERE ID=%d",
        932
    ));
    if (stripos($redirect_content, "'sistema-his-medsi'") === false || stripos($redirect_content, '/sistema-informacion-hospitalaria-his-guia-completa-mexico/') === false) {
        throw new RuntimeException('No quedó configurada la redirección 301 de la ruta retirada.');
    }

    echo wp_json_encode([
        'status'=>'PASS',
        'backup_dir'=>$backup_dir,
        'backup_file'=>$backup_file,
        'affected_ids'=>$affected_ids,
        'media_ids'=>$media_ids,
        'changes'=>$changed,
        'remaining_active'=>0,
        'redirect_source_only'=>'/sistema-his-medsi/',
        'redirect_target'=>'/sistema-informacion-hospitalaria-his-guia-completa-mexico/',
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
} catch (Throwable $e) {
    // Restore posts, metadata and option rows atomically enough for this bounded change.
    foreach ($backup['posts'] as $row) $wpdb->replace($wpdb->posts, $row);
    $wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE post_id IN ({$id_csv})");
    foreach ($backup['postmeta'] as $row) $wpdb->insert($wpdb->postmeta, $row);
    $wpdb->delete($wpdb->options, ['option_name'=>'wpcode_snippets']);
    foreach ($backup['options'] as $row) $wpdb->insert($wpdb->options, $row);
    echo wp_json_encode(['status'=>'ROLLBACK','error'=>$e->getMessage(),'backup_dir'=>$backup_dir], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
    exit(1);
}
