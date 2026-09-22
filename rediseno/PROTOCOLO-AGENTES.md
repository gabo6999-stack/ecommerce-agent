# Protocolo para agentes — rediseño de peptidosysuplementos.mx (PYS)

Eres uno de varios agentes que trabajan EN PARALELO sobre el mismo sitio vivo.
Cada uno tiene una familia de páginas y UN archivo propio. Léete esto entero antes
de tocar nada.

## 1. El encargo

**Respetar el contenido, cambiar solo el diseño.** Las páginas ya llevan la
cabecera, el pie, el fondo hexagonal y la base tipográfica nuevas (capa global).
Lo que falta es que el CUERPO de cada página se vea como el resto del rediseño:
el sistema «laboratorio oscuro» de la portada, el catálogo, la ficha y el blog.

- NO se cambia, añade ni quita texto, enlaces, imágenes ni orden del contenido.
  Nada de editar posts, `_elementor_data`, plantillas de Elementor ni la BD.
- Todo se hace con **CSS** servido desde tu archivo. Solo si el CSS no puede, un
  filtro PHP de presentación (p. ej. cambiar la clase de un contenedor), siempre
  dentro de tu predicado y sin alterar el texto. Si crees que hace falta tocar
  contenido: NO lo hagas, repórtalo.
- Ocultar algo con CSS SOLO si es un duplicado real del mismo contenido (como el
  listado repetido del blog). Si lo haces, explícalo en el reporte.
- Reglas de contenido absolutas del sitio (por si escribes algún `content:` en
  CSS): nunca la palabra «farmacia» (usar «Tienda en línea»); nunca hablar de
  refrigeración durante el transporte.

## 2. Dónde vive el código

Repo local: `C:\Users\gabom\Proyectos\ecommerce-agent\rediseno\home-2026\mu-plugins\`
Servidor (docroot): `/home/u303216082/domains/peptidosysuplementos.mx/public_html`,
mu-plugins en `wp-content/mu-plugins/`.

- `pys-diseno.php` — **cargador. NO LO TOQUES.** Decide qué familia aplica a cada
  página y, si tu archivo existe, lo carga y llama a tu función de CSS:

  | Familia | Tu archivo | Tu función (devuelve un string de CSS) | Predicado (ya hecho) |
  |---|---|---|---|
  | páginas Elementor: políticas e informativas | `pys-diseno/paginas-elementor.php` | `pys_dis_css_paginas_elementor()` | `pys_dis_es_pagina_elementor()` |
  | páginas Elementor: landings comerciales | `pys-diseno/landings.php` | `pys_dis_css_landings()` | `pys_dis_es_pagina_elementor()` |
  | páginas planas | `pys-diseno/paginas-planas.php` | `pys_dis_css_paginas_planas()` | `pys_dis_es_pagina_plana()` |
  | mi cuenta | `pys-diseno/cuenta.php` | `pys_dis_css_cuenta()` | `pys_dis_es_cuenta()` |
  | búsqueda y 404 | `pys-diseno/utilitarias.php` | `pys_dis_css_utilitarias()` | `pys_dis_es_utilitaria()` |

  Tu CSS se imprime en `<style data-no-optimize="1">` al final del `<head>`
  (prioridad 99), después de la base compartida, SOLO en las páginas de tu familia.
  Si necesitas un selector por página, usa la clase `page-id-<id>` del `<body>`.

  ⚠️ **Las dos familias Elementor comparten predicado**, así que en
  `paginas-elementor.php` y `landings.php` **TODA regla debe ir acotada a tus
  páginas** por la clase del body, p. ej.
  `html body:is(.page-id-3,.page-id-10)[class][class] .elementor-widget-heading{…}`
  (`:is()` aporta la especificidad de una clase: queda en 0,3,2). Una regla sin
  acotar pisaría las páginas del otro agente y le arruinaría su «antes».
- `pys-diseno/partes.php` — base compartida: tokens, fuentes, cabecera, pie,
  `.btn`, `.tarjeta`, avisos de WooCommerce. **NO LO TOQUES.** Si ves un fallo
  de la base, repórtalo.
- Archivos de otras familias ya hechas, para inspirarte y copiar patrones:
  `pys-diseno/blog.php` (el más parecido a una página de prosa), `catalogo.php`,
  `ficha.php`, `tienda.php`. Solo el agente de auditoría puede editarlos.
- La portada: `pys-home-2026/template.php` (plantilla propia). Es la referencia
  visual principal. Solo el agente de auditoría puede tocarla.

Plantilla de tu archivo:

```php
<?php
/**
 * PYS — rediseño de <familia>. Solo diseño: no toca contenido.
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

function pys_dis_css_<familia>() {
	return <<<'CSS'
html body[class][class][class] .tu-selector{...}
CSS;
}
```

## 3. El sistema visual (tokens ya definidos en `:root` por la base)

```
--negro:#050908  --carbon:#0A1210  --carbon-2:#0F1A17  --panel:#132420
--linea:#16241F  --linea-2:#22362F
--tinta:#EEF6F3  --tinta-2:#93AAA3  --tinta-3:#718C84
--magenta:#FF047E  --aqua:#02F6C8  --vitrina:#EEF3F1
--optima (titulares, peso normal, NUNCA negrita 900)
--mono   (etiquetas, cifras, SKU; pequeño, mayúsculas con tracking)
--gutter:clamp(18px,4vw,56px)
```

Rasgos del sistema: fondo negro plano (el hexagonal ya lo pone la base), paneles
`--carbon`/`--carbon-2` con borde 1px `--linea`, **radios pequeños (0–6 px; nada
de 20–30 px ni «vidrio» con blur)**, titulares Optima claros y grandes, etiquetas
en mono pequeñas en mayúsculas, acentos magenta (botón primario, palabra
resaltada) y aqua (datos, enlaces, estados), sin degradados en texto, sin sombras
de colores ni brillos neón. Botones: imita `.btn` de la base (míralo en
`partes.php`). Prosa: columna ~68ch, interlineado 1.7, `h2/h3` en Optima, tablas
con filas `--linea` y cabecera en mono.

## 4. Pelear contra el CSS viejo — las trampas conocidas

1. **Especificidad:** el Customizer y hojas en línea del sitio usan reglas como
   `html body.archive[class]` o
   `body.post-type-archive-product ul.products li.product ...!important`
   (hasta 0,4,3). Empieza tus selectores con **`html body[class][class][class]`**
   y usa `!important` cuando haga falta. No confíes en el orden de carga:
   LiteSpeed combina y reordena.
2. **Texto con degradado recortado:** muchos titulares y botones viejos usan
   `background-clip:text` + `-webkit-text-fill-color:transparent`. Si quitas el
   degradado sin devolver `-webkit-text-fill-color:currentColor` (o un color), el
   texto queda INVISIBLE. `verificar.py` lo detecta.
3. **Elementor mete estilos por widget** en
   `/wp-content/uploads/elementor/css/post-<id>.css` y en atributos: colores,
   fondos, radios, paddings. Hay que ganarles con especificidad, sin tocar el
   documento de Elementor.
4. **Widgets HTML con `<style>` en línea** dentro de la página (landings): traen
   sus propias clases y colores. Re-estilízalas; no borres su marcado.
5. **Imágenes cortadas:** un contenedor con `overflow:hidden` + alto fijo corta
   la foto. `verificar.py` lo mide. Arréglalo sin deformar.
6. **Márgenes:** la base NO resetea márgenes de `h1-h6`/`p` a propósito; la prosa
   necesita aire.
7. **`<option>` nativas** heredan texto claro sobre popup blanco: dar
   `color:#111;background:#fff`.
8. **Depurar CSSOM:** al recorrer `document.styleSheets`, filtra por
   `r.type === CSSRule.STYLE_RULE`; `if (r.cssRules)` es cierto también en
   reglas de estilo (lista vacía) y te hace creer que una regla no existe.
9. **Caché:** tras desplegar, SIEMPRE `wp litespeed-purge all`. Mira el HTML
   anónimo (curl o Playwright sin sesión), nunca como admin. hcdn suele
   refrescarse solo; verificar.py ya añade `?pysv=<timestamp>`.

## 5. Desplegar (tu carpeta temporal es propia)

```bash
S="ssh -i ~/.ssh/cmlc -p 65002 u303216082@145.79.4.65"
R=/home/u303216082/domains/peptidosysuplementos.mx/public_html
$S "mkdir -p /tmp/pys-<familia>"                      # la primera vez
scp -q -i ~/.ssh/cmlc -P 65002 <archivo-local> u303216082@145.79.4.65:/tmp/pys-<familia>/<archivo>.php
$S "php -l /tmp/pys-<familia>/<archivo>.php"          # OBLIGATORIO: un error de sintaxis TUMBA EL SITIO
$S "cp /tmp/pys-<familia>/<archivo>.php $R/wp-content/mu-plugins/pys-diseno/<archivo>.php && cd $R && wp litespeed-purge all"
curl -s -o /dev/null -w '%{http_code}\n' https://peptidosysuplementos.mx/   # la portada debe seguir en 200
```

- Solo copias TU archivo. Nunca `pys-diseno.php`, `partes.php` ni archivos ajenos.
- Si tras copiar la portada o tu página no dan 200: borra tu archivo del
  servidor al instante (`rm $R/wp-content/mu-plugins/pys-diseno/<archivo>.php`),
  purga, y arregla en local.
- wp-cli existe en el servidor; `wp db query` NO funciona (usa `wp eval` con
  `$wpdb`). No hay python en el servidor.
- Para inspeccionar el HTML: `curl -s "https://peptidosysuplementos.mx/<ruta>/?pysv=$(date +%s)"`.

## 6. Verificación — antes y después, por código Y visual (obligatoria)

Python con Playwright: `"C:/Users/gabom/AppData/Local/Programs/Python/Python311/python.exe"`
(el `python` por defecto NO tiene Playwright). Siempre con `PYTHONIOENCODING=utf-8`.
Herramientas en `C:\Users\gabom\Proyectos\ecommerce-agent\rediseno\herramientas\`.

1. **ANTES de escribir una sola línea de CSS**, captura tu familia:
   `verificar.py <familia>-antes <url1> <url2> ...` (o `--lista archivo.txt`).
   Deja en `rediseno/verificacion/<familia>-antes/` una captura de página ENTERA
   en escritorio (1440) y móvil (390), el texto, y un diagnóstico: duplicados,
   imágenes cortadas, texto invisible, desborde horizontal, radios/degradados
   viejos, imágenes rotas, errores de consola, y una huella del contenido.
2. Mira las capturas DE VERDAD, completas: `revisar.py tiras <familia>-antes`
   las corta en tiras legibles en `verificacion/<familia>-antes/tiras/`; ábrelas
   con la herramienta Read (ve imágenes). La página entera, no solo el primer
   pantallazo: el listado duplicado del blog estaba a media página y se escapó
   por mirar solo la parte de arriba.
3. Diseña, despliega, purga.
4. Captura el después: `verificar.py <familia>-despues <mismas urls>`.
5. Compara: `verificar.py --comparar <familia>-antes <familia>-despues`.
   Criterios para dar una página por buena:
   - «contenido del HTML: **IDÉNTICO**» en las dos vistas. Si sale CAMBIÓ,
     compara los `.txt` de antes y después (`diff`) y explica la causa (p. ej. un
     nonce o una fecha dinámica). Si falta texto real, es un fallo tuyo.
   - Ningún «!! NUEVO».
   - Ningún titular que «ya no está».
   - `OK` en las dos vistas, o solo avisos que justifiques (p. ej. radios en un
     widget de terceros como el chat).
6. Revisión visual del después:
   `revisar.py lado <familia>-antes <familia>-despues <slug> escritorio` y lo
   mismo con `movil`; abre TODAS las tiras de `verificacion/lado-a-lado/` de tus
   slugs. Busca: contraste, texto ilegible, cosas encimadas, huecos raros,
   bloques con el estilo viejo (blanco, radios grandes, degradados, neón), tablas
   desbordadas en móvil, botones sin texto, y cualquier cosa repetida. Que quede
   **bien y bonito**, coherente con la portada y el blog.
7. Repite 3–6 hasta que todo pase. Tu última captura `-despues` debe ser la del
   estado final desplegado (si iteras, puedes usar `<familia>-despues2`, etc.,
   pero compara siempre contra el `-antes` original).

## 7. Prohibido

- Hacer pedidos, pagos, registros de cuenta o enviar formularios en el sitio vivo
  (única excepción: el agente de auditoría de tienda puede AÑADIR AL CARRITO en su
  propia sesión headless para ver el carrito lleno; nunca pulsar «Realizar el
  pedido» ni escribir datos personales reales).
- Iniciar sesión en el sitio.
- `git commit`/`push` (el usuario decide cuándo).
- Usar el navegador integrado de Claude (Claude Browser) o Chrome: lo comparten
  todos. Usa Playwright headless vía las herramientas (puedes escribir scripts
  propios de Playwright en tu carpeta de trabajo si necesitas inspeccionar el DOM).
- Tocar archivos que no sean el tuyo (y tus capturas en `verificacion/`).
- Editar contenido: posts, páginas, `_elementor_data`, plantillas, menús, opciones.

## 8. Reporte final (lo que devuelves)

Breve y concreto:
- Archivo(s) que creaste/cambiaste y desplegaste.
- Por página: resultado de `--comparar` (IDÉNTICO sí/no, problemas arreglados,
  los que siguen y por qué).
- Rutas de las tiras lado-a-lado más representativas (2–4 por página difícil)
  para que el coordinador las revise.
- Lo que NO pudiste resolver sin tocar contenido o la base compartida.
- Hallazgos de contenido/SEO que veas de paso (no los arregles).
