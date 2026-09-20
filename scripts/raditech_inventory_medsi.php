<?php
/** Inventario de solo lectura de referencias Medsi en WordPress. */
global $wpdb;
$needle = '%medsi%';
$posts = $wpdb->get_results($wpdb->prepare(
    "SELECT ID, post_type, post_status, post_name, post_title,
     (post_title LIKE %s) AS in_title,
     (post_content LIKE %s) AS in_content,
     (post_excerpt LIKE %s) AS in_excerpt,
     (post_name LIKE %s) AS in_slug,
     (guid LIKE %s) AS in_guid
     FROM {$wpdb->posts}
     WHERE post_title LIKE %s OR post_content LIKE %s OR post_excerpt LIKE %s OR post_name LIKE %s OR guid LIKE %s
     ORDER BY post_type, ID",
    $needle,$needle,$needle,$needle,$needle,$needle,$needle,$needle,$needle,$needle
), ARRAY_A);
$meta = $wpdb->get_results($wpdb->prepare(
    "SELECT pm.post_id, p.post_type, p.post_status, p.post_name, pm.meta_key,
     (LENGTH(pm.meta_value)-LENGTH(REPLACE(LOWER(pm.meta_value),'medsi','')))/5 AS mentions
     FROM {$wpdb->postmeta} pm LEFT JOIN {$wpdb->posts} p ON p.ID=pm.post_id
     WHERE LOWER(pm.meta_value) LIKE %s
     ORDER BY pm.post_id, pm.meta_key",
    $needle
), ARRAY_A);
$terms = $wpdb->get_results($wpdb->prepare(
    "SELECT t.term_id, t.name, t.slug, tt.taxonomy
     FROM {$wpdb->terms} t JOIN {$wpdb->term_taxonomy} tt ON tt.term_id=t.term_id
     WHERE LOWER(t.name) LIKE %s OR LOWER(t.slug) LIKE %s OR LOWER(tt.description) LIKE %s",
    $needle,$needle,$needle
), ARRAY_A);
$options = $wpdb->get_results($wpdb->prepare(
    "SELECT option_name,
     (LENGTH(option_value)-LENGTH(REPLACE(LOWER(option_value),'medsi','')))/5 AS mentions,
     LENGTH(option_value) AS value_length
     FROM {$wpdb->options}
     WHERE LOWER(option_value) LIKE %s OR LOWER(option_name) LIKE %s
     ORDER BY option_name",
    $needle,$needle
), ARRAY_A);
echo wp_json_encode([
    'status'=>'PASS',
    'posts'=>$posts,
    'postmeta'=>$meta,
    'terms'=>$terms,
    'options'=>$options,
], JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE);
