# Calculadora de Dosis de Péptidos — PYS

Bloque HTML autocontenido para `peptidosysuplementos.mx`.

## Qué hace
Calcula la reconstitución de un péptido y cuántas **unidades** cargar en una
jeringa de insulina U-100:

- Entradas: contenido del vial (mg/mcg), agua bacteriostática (ml), dosis deseada (mcg/mg).
- Salidas: concentración (mg/ml), **unidades en jeringa U-100**, dosis por vial, volumen a extraer (ml).
- Selector de péptidos con valores típicos precargados (BPC-157, TB-500, Ipamorelin,
  CJC-1295, semaglutida, tirzepatida, etc.).
- Aviso médico incluido.

Fórmulas:
```
concentración (mg/ml) = vial_mg / agua_ml
volumen (ml)          = dosis_mg / concentración
unidades (UI)         = volumen × 100      (1 ml = 100 UI en jeringa U-100)
dosis por vial        = vial_mg / dosis_mg
```

## Cómo publicar (sesión LOCAL con Chrome, cuenta gabo6999)

> Regla del stack: el diseño va **solo en Elementor**. Por API solo title/meta/slug/rank_math.

1. `git pull` de la rama `claude/practical-edison-3qhcvw`.
2. En WordPress de PYS, crea/edita la página de la calculadora con Elementor.
3. Arrastra un widget **HTML** y pega TODO el contenido de
   `calculadora_dosis_pys.html`.
4. (Opcional) Ajusta SEO con Rank Math: `rank_math_title`, `rank_math_description`, slug.
5. Publica y verifica en móvil (el bloque es responsive).

## Personalización rápida
- Colores: variables CSS al inicio (`--pys-azul`, `--pys-verde`, etc.).
- Péptidos/rangos: array `PRESETS` en el `<script>` (`[nombre, vial_mg, agua_ml, dosis, "mcg"|"mg"]`).
- CTA: el `href` del botón (`/contacto/`).
