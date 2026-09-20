<?php
/** Localiza fuentes activas de Medsi/Medisi sin modificar WordPress. */
global $wpdb;
$posts = $wpdb->get_results(
    "SELECT ID,post_type,post_status,post_name,
      (LOWER(CONCAT_WS(' ',post_title,post_name,post_content,post_excerpt)) LIKE '%medsi%' OR LOWER(CONCAT_WS(' ',post_title,post_name,post_content,post_excerpt)) LIKE '%medisi%') AS hit
     FROM {$wpdb->posts}
     WHERE post_status NOT IN ('draft','trash','auto-draft','inherit')
       AND post_type <> 'revision'
       AND (LOWER(CONCAT_WS(' ',post_title,post_name,post_content,post_excerpt)) LIKE '%medsi%'
         OR LOWER(CONCAT_WS(' ',post_title,post_name,post_content,post_excerpt)) LIKE '%medisi%')",
    ARRAY_A
);
$meta = $wpdb->get_results(
    "SELECT pm.meta_id,pm.post_id,pm.meta_key,LENGTH(pm.meta_value) bytes
     FROM {$wpdb->postmeta} pm JOIN {$wpdb->posts} p ON p.ID=pm.post_id
     WHERE p.post_status NOT IN ('draft','trash','auto-draft','inherit')
       AND p.post_type <> 'revision'
       AND (LOWER(pm.meta_value) LIKE '%medsi%' OR LOWER(pm.meta_value) LIKE '%medisi%')
     ORDER BY pm.post_id,pm.meta_key",
    ARRAY_A
);
$options = $wpdb->get_results(
    "SELECT option_name,LENGTH(option_value) bytes
     FROM {$wpdb->options}
     WHERE LOWER(option_value) LIKE '%medsi%' OR LOWER(option_value) LIKE '%medisi%'
     ORDER BY option_name",
    ARRAY_A
);
$faq_meta = [];
foreach (get_post_meta(111) as $key => $values) {
    foreach ($values as $value) {
        if (stripos($value, 'medsi') !== false || stripos($value, 'medisi') !== false) {
            $pos = stripos($value, 'medsi'); if ($pos === false) $pos = stripos($value, 'medisi');
            $faq_meta[] = ['key'=>$key,'length'=>strlen($value),'context'=>substr($value,max(0,$pos-220),520)];
        }
    }
}
echo wp_json_encode(['status'=>'PASS','posts'=>$posts,'meta'=>$meta,'options'=>$options,'faq_meta'=>$faq_meta], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
