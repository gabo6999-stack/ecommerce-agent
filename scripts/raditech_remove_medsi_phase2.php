<?php
/** Retiro definitivo de residuos Medsi/Medisi después de verificar la capa pública. */
global $wpdb;
$backup_dir = '/tmp/raditech-medsi-backup-20260806-065438';
$phase2_file = $backup_dir . '/phase2-deep-cleanup-backup.json';
$media_ids = [17,250,264,385,400];
$dedicated_ids = [19,402,890];

$revision_ids = array_map('intval', $wpdb->get_col(
    "SELECT DISTINCT p.ID FROM {$wpdb->posts} p
     LEFT JOIN {$wpdb->postmeta} pm ON pm.post_id=p.ID
     WHERE p.post_type='revision' AND (
       LOWER(CONCAT_WS(' ',p.post_title,p.post_name,p.post_content,p.post_excerpt,p.guid)) LIKE '%medsi%'
       OR LOWER(CONCAT_WS(' ',p.post_title,p.post_name,p.post_content,p.post_excerpt,p.guid)) LIKE '%medisi%'
       OR LOWER(pm.meta_value) LIKE '%medsi%' OR LOWER(pm.meta_value) LIKE '%medisi%'
     )"
));
$post_ids = array_values(array_unique(array_merge($media_ids, $dedicated_ids, $revision_ids)));
$id_csv = implode(',', array_map('intval', $post_ids));
$comment_ids = array_map('intval', $wpdb->get_col(
    "SELECT comment_ID FROM {$wpdb->comments} WHERE LOWER(comment_content) LIKE '%medsi%' OR LOWER(comment_content) LIKE '%medisi%'"
));
$comment_csv = $comment_ids ? implode(',', $comment_ids) : '0';

$has_wpr = $wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s', $wpdb->prefix.'wpr_above_the_fold')) === $wpdb->prefix.'wpr_above_the_fold';
$has_rm_links = $wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s', $wpdb->prefix.'rank_math_internal_links')) === $wpdb->prefix.'rank_math_internal_links';
$has_rm_404 = $wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s', $wpdb->prefix.'rank_math_404_logs')) === $wpdb->prefix.'rank_math_404_logs';

$backup = [
    'created_utc'=>gmdate('c'),
    'post_ids'=>$post_ids,
    'revision_ids'=>$revision_ids,
    'media_ids'=>$media_ids,
    'dedicated_ids'=>$dedicated_ids,
    'posts'=>$id_csv ? $wpdb->get_results("SELECT * FROM {$wpdb->posts} WHERE ID IN ({$id_csv})", ARRAY_A) : [],
    'postmeta'=>$id_csv ? $wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id IN ({$id_csv})", ARRAY_A) : [],
    'comments'=>$comment_ids ? $wpdb->get_results("SELECT * FROM {$wpdb->comments} WHERE comment_ID IN ({$comment_csv})", ARRAY_A) : [],
    'commentmeta'=>$comment_ids ? $wpdb->get_results("SELECT * FROM {$wpdb->commentmeta} WHERE comment_id IN ({$comment_csv})", ARRAY_A) : [],
    'rank_math_internal_links'=>$has_rm_links ? $wpdb->get_results("SELECT * FROM {$wpdb->prefix}rank_math_internal_links WHERE LOWER(url) LIKE '%medsi%' OR LOWER(url) LIKE '%medisi%'", ARRAY_A) : [],
    'rank_math_404_logs'=>$has_rm_404 ? $wpdb->get_results("SELECT * FROM {$wpdb->prefix}rank_math_404_logs WHERE LOWER(uri) LIKE '%medsi%' OR LOWER(uri) LIKE '%medisi%'", ARRAY_A) : [],
    'wpr_above_the_fold'=>$has_wpr ? $wpdb->get_results("SELECT * FROM {$wpdb->prefix}wpr_above_the_fold WHERE LOWER(lcp) LIKE '%medsi%' OR LOWER(lcp) LIKE '%medisi%' OR LOWER(viewport) LIKE '%medsi%' OR LOWER(viewport) LIKE '%medisi%'", ARRAY_A) : [],
];
if (file_put_contents($phase2_file, wp_json_encode($backup, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) === false) {
    throw new RuntimeException('No se pudo guardar el respaldo de fase 2.');
}

$deleted = [];
foreach ($comment_ids as $id) {
    if (wp_delete_comment($id, true)) $deleted[] = "comment:{$id}";
}
foreach ($revision_ids as $id) {
    if (wp_delete_post($id, true)) $deleted[] = "revision:{$id}";
}
foreach ($dedicated_ids as $id) {
    if (get_post($id) && wp_delete_post($id, true)) $deleted[] = "post:{$id}";
}
foreach ($media_ids as $id) {
    if (get_post($id) && wp_delete_attachment($id, true)) $deleted[] = "attachment:{$id}";
}
if ($has_rm_links) {
    $n = $wpdb->query("DELETE FROM {$wpdb->prefix}rank_math_internal_links WHERE LOWER(url) LIKE '%medsi%' OR LOWER(url) LIKE '%medisi%'");
    $deleted[] = "rank_math_internal_links:".(int)$n;
}
if ($has_rm_404) {
    $n = $wpdb->query("DELETE FROM {$wpdb->prefix}rank_math_404_logs WHERE LOWER(uri) LIKE '%medsi%' OR LOWER(uri) LIKE '%medisi%'");
    $deleted[] = "rank_math_404_logs:".(int)$n;
}
if ($has_wpr) {
    $n = $wpdb->query("DELETE FROM {$wpdb->prefix}wpr_above_the_fold WHERE LOWER(lcp) LIKE '%medsi%' OR LOWER(lcp) LIKE '%medisi%' OR LOWER(viewport) LIKE '%medsi%' OR LOWER(viewport) LIKE '%medisi%'");
    $deleted[] = "wpr_above_the_fold:".(int)$n;
}
wp_cache_flush();

$remaining = [
    'posts'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE ID<>932 AND (LOWER(CONCAT_WS(' ',post_title,post_name,post_content,post_excerpt,guid)) LIKE '%medsi%' OR LOWER(CONCAT_WS(' ',post_title,post_name,post_content,post_excerpt,guid)) LIKE '%medisi%')"),
    'postmeta'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->postmeta} WHERE LOWER(meta_value) LIKE '%medsi%' OR LOWER(meta_value) LIKE '%medisi%'"),
    'comments'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->comments} WHERE LOWER(comment_content) LIKE '%medsi%' OR LOWER(comment_content) LIKE '%medisi%'"),
    'rank_math_internal_links'=>$has_rm_links ? (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}rank_math_internal_links WHERE LOWER(url) LIKE '%medsi%' OR LOWER(url) LIKE '%medisi%'") : 0,
    'rank_math_404_logs'=>$has_rm_404 ? (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}rank_math_404_logs WHERE LOWER(uri) LIKE '%medsi%' OR LOWER(uri) LIKE '%medisi%'") : 0,
    'wpr_above_the_fold'=>$has_wpr ? (int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}wpr_above_the_fold WHERE LOWER(lcp) LIKE '%medsi%' OR LOWER(lcp) LIKE '%medisi%' OR LOWER(viewport) LIKE '%medsi%' OR LOWER(viewport) LIKE '%medisi%'") : 0,
];
if (array_sum($remaining) !== 0) {
    echo wp_json_encode(['status'=>'FAIL','backup_file'=>$phase2_file,'remaining'=>$remaining,'deleted'=>$deleted], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
    exit(1);
}
$redirect = (string)$wpdb->get_var($wpdb->prepare("SELECT post_content FROM {$wpdb->posts} WHERE ID=%d",932));
if (stripos($redirect,"'sistema-his-medsi'") === false || stripos($redirect,'/sistema-informacion-hospitalaria-his-guia-completa-mexico/') === false) {
    echo wp_json_encode(['status'=>'FAIL','backup_file'=>$phase2_file,'error'=>'Se perdió el 301 técnico','deleted'=>$deleted], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
    exit(1);
}
echo wp_json_encode(['status'=>'PASS','backup_file'=>$phase2_file,'deleted'=>$deleted,'remaining'=>$remaining,'technical_exception'=>'wpcode:932 source slug only'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
