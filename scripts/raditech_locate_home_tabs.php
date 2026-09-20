<?php
/** Read-only locator for the rendered home solution-tabs source. */
global $wpdb;
$needle = 'rt-tab-panel';
$posts = $wpdb->get_results($wpdb->prepare(
    "SELECT ID, post_parent, post_type, post_status, post_title FROM {$wpdb->posts} WHERE post_content LIKE %s ORDER BY ID",
    '%' . $wpdb->esc_like($needle) . '%'
), ARRAY_A);
$options = $wpdb->get_results($wpdb->prepare(
    "SELECT option_id, option_name, autoload FROM {$wpdb->options} WHERE option_value LIKE %s ORDER BY option_id",
    '%' . $wpdb->esc_like($needle) . '%'
), ARRAY_A);
echo wp_json_encode(['status' => 'PASS', 'posts' => $posts, 'options' => $options], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
