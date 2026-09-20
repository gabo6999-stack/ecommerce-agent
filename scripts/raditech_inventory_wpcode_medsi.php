<?php
/** Inventario de rutas internas con Medsi dentro de la opción WPCode. */
function rt_walk_medsi_option($value, $path, &$hits) {
    if (is_array($value)) {
        if (isset($value['code']) && is_string($value['code'])
            && (stripos($value['code'], 'medsi') !== false || stripos($value['code'], 'medisi') !== false)) {
            $pos = stripos($value['code'], 'medsi');
            if ($pos === false) $pos = stripos($value['code'], 'medisi');
            $hits[] = [
                'path' => $path,
                'keys' => array_keys($value),
                'id' => $value['id'] ?? null,
                'title' => $value['title'] ?? null,
                'location' => $value['location'] ?? null,
                'code_type' => $value['code_type'] ?? null,
                'length' => strlen($value['code']),
                'compiled_length' => isset($value['compiled_code']) && is_string($value['compiled_code']) ? strlen($value['compiled_code']) : null,
                'compiled_same' => isset($value['compiled_code']) ? $value['compiled_code'] === $value['code'] : null,
                'compiled_has_medsi' => isset($value['compiled_code']) && is_string($value['compiled_code']) ? (stripos($value['compiled_code'], 'medsi') !== false || stripos($value['compiled_code'], 'medisi') !== false) : null,
                'context' => substr($value['code'], max(0, $pos - 180), 420),
            ];
        }
        foreach ($value as $k => $v) {
            if ($k !== 'code') rt_walk_medsi_option($v, $path . '[' . $k . ']', $hits);
        }
    }
}
$hits = [];
$value = get_option('wpcode_snippets', null);
rt_walk_medsi_option($value, 'wpcode_snippets', $hits);
echo wp_json_encode(['status'=>'PASS','type'=>gettype($value),'hits'=>$hits], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
