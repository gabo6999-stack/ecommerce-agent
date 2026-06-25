<?php
/**
 * WPCode snippet — "Favicon.ico redirect Raditech"
 * Tipo: PHP Snippet  ·  Auto Insert / Run Everywhere  ·  Activo
 *
 * Arregla /favicon.ico → 404 redirigiéndolo al favicon que ya existe.
 * Snippet NUEVO e independiente: NO toca el snippet 932 (los 8 redirects 301).
 *
 * Gotchas WPCode (de memoria del proyecto):
 *   1) Debe ser tipo "PHP Snippet" (NUNCA "HTML Snippet").
 *   2) Guardar DOS veces (Update) — el primer guardado a veces no reconstruye su caché.
 *   3) Tras activar, purgar LiteSpeed "Vaciar todo".
 *
 * NOTA: no incluyas la etiqueta <?php de arriba al pegar en WPCode (WPCode ya la pone);
 * pega solo desde 'add_action' hasta el final.
 */
add_action('template_redirect', function () {
    $uri = isset($_SERVER['REQUEST_URI']) ? strtok($_SERVER['REQUEST_URI'], '?') : '';
    if ($uri === '/favicon.ico') {
        wp_redirect('https://raditech.mx/wp-content/uploads/2024/11/favicon-raditech-1-svg-1.webp');
        exit;
    }
});
