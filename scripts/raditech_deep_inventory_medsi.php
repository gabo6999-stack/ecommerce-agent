<?php
/** Inventario profundo de Medsi/Medisi en tablas y cachés generadas. Solo lectura. */
global $wpdb;
$db_hits = [];
$db_name = DB_NAME;
$columns = $wpdb->get_results($wpdb->prepare(
    "SELECT TABLE_NAME,COLUMN_NAME,DATA_TYPE FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA=%s AND DATA_TYPE IN ('char','varchar','tinytext','text','mediumtext','longtext')
     ORDER BY TABLE_NAME,ORDINAL_POSITION",
    $db_name
), ARRAY_A);
foreach ($columns as $c) {
    $table = $c['TABLE_NAME']; $col = $c['COLUMN_NAME'];
    // Quote identifiers discovered from information_schema.
    $sql = "SELECT `{$col}` value FROM `{$table}` WHERE LOWER(`{$col}`) LIKE '%medsi%' OR LOWER(`{$col}`) LIKE '%medisi%' LIMIT 3";
    $vals = $wpdb->get_col($sql);
    foreach ($vals as $v) {
        $pos = stripos($v,'medsi'); if ($pos === false) $pos = stripos($v,'medisi');
        $db_hits[] = ['table'=>$table,'column'=>$col,'length'=>strlen($v),'context'=>substr($v,max(0,$pos-120),300)];
    }
}
$file_hits = [];
$roots = [WP_CONTENT_DIR];
foreach ($roots as $root) {
    if (!is_dir($root)) continue;
    $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
    foreach ($it as $f) {
        if (!$f->isFile() || $f->getSize() > 5*1024*1024) continue;
        if (!preg_match('/\.(?:html?|json|css|js|php|txt)$/i', $f->getFilename())) continue;
        $v = @file_get_contents($f->getPathname());
        if (!is_string($v)) continue;
        $pos = stripos($v,'medsi'); if ($pos === false) $pos = stripos($v,'medisi');
        if ($pos !== false) $file_hits[] = ['path'=>$f->getPathname(),'bytes'=>$f->getSize(),'context'=>substr($v,max(0,$pos-120),300)];
    }
}
echo wp_json_encode(['status'=>'PASS','db_hits'=>$db_hits,'file_hits'=>$file_hits], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n";
