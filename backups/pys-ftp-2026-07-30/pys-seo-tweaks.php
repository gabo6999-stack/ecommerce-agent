<?php
if (!defined('ABSPATH')) { exit; }
function pys_add_lazy($html) {
if (stripos($html, '</html>') === false) { return $html; }
$n = 0;
return preg_replace_callback('/<img\b(?![^>]*\sloading=)[^>]*>/i', function ($m) use (&$n) {
$n++;
if ($n <= 1) { return $m[0]; }
return preg_replace('/<img\b/i', '<img loading="lazy"', $m[0], 1);
}, $html);
}
add_filter('litespeed_buffer_before', 'pys_add_lazy', 10);
add_action('template_redirect', function () {
if (is_admin() || is_feed()) { return; }
ob_start('pys_add_lazy');
}, 99);
add_action('template_redirect', function () {
if (is_admin() || is_user_logged_in()) { return; }
if (function_exists('is_cart') && (is_cart() || is_checkout() || is_account_page())) { return; }
header('Cache-Control: public, max-age=300, stale-while-revalidate=600', true);
}, 99);
