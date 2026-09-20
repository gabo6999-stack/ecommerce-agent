<?php
/** Retira HIS de la enumeración comercial rápida de la portada. */
global $wpdb;
$post_id = 10;
$backup_dir = '/tmp/raditech-medsi-backup-20260806-065438';
$old = 'PACS-RIS, teleradiología, HIS, X-Card';
$new = 'PACS-RIS, teleradiología, X-Card';
$post = $wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d", $post_id), ARRAY_A);
$meta = $wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d", $post_id), ARRAY_A);
file_put_contents($backup_dir . '/phase3-home-his-listing-backup.json', wp_json_encode(['post'=>$post,'meta'=>$meta], JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE));
$changed = 0;
$content = str_replace($old, $new, $post['post_content'], $count);
if ($count) { $wpdb->update($wpdb->posts, ['post_content'=>$content], ['ID'=>$post_id], ['%s'], ['%d']); $changed += $count; }
$rows = $wpdb->get_results($wpdb->prepare("SELECT meta_id,meta_key,meta_value FROM {$wpdb->postmeta} WHERE post_id=%d", $post_id), ARRAY_A);
foreach ($rows as $row) {
    if ($row['meta_key'] === '_elementor_element_cache') continue;
    $value = str_replace($old, $new, $row['meta_value'], $count);
    if ($count) { $wpdb->update($wpdb->postmeta, ['meta_value'=>$value], ['meta_id'=>$row['meta_id']], ['%s'], ['%d']); $changed += $count; }
}
delete_post_meta($post_id, '_elementor_element_cache');
clean_post_cache($post_id);
$remaining = (int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->posts} WHERE ID=%d AND post_content LIKE %s", $post_id, '%' . $wpdb->esc_like($old) . '%'));
$remaining += (int)$wpdb->get_var($wpdb->prepare("SELECT COUNT(*) FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_value LIKE %s", $post_id, '%' . $wpdb->esc_like($old) . '%'));
if ($remaining) WP_CLI::error('La enumeración HIS sigue almacenada.');
WP_CLI::log(wp_json_encode(['status'=>'PASS','changed'=>$changed,'backup'=>$backup_dir . '/phase3-home-his-listing-backup.json'], JSON_UNESCAPED_SLASHES));
