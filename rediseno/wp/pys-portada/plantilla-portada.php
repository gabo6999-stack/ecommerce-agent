<?php
/**
 * Plantilla: PYS — Portada
 *
 * Sale del prototipo `rediseno/home.html`, con los datos de ejemplo
 * sustituidos por los de la tienda. Lo que no tiene dato real no se
 * imprime: es preferible una sección de menos que un número inventado.
 *
 * No usa get_header()/get_footer() porque el diseño trae su propia
 * navegación y su propio pie; wp_head() y wp_footer() sí se llaman, que es
 * lo que necesitan WooCommerce y el resto de plugins.
 */

if (!defined('ABSPATH')) exit;

$lote        = pys_portada_lote();
$n_prod      = count(pys_portada_productos());
$url_carrito = function_exists('wc_get_cart_url') ? wc_get_cart_url() : home_url('/');

$alt_svg = $lote
    ? sprintf('Cromatograma del lote %s con pico principal de %s %% a %s minutos',
              $lote['lote'], $lote['pureza'], $lote['tr'])
    : 'Cromatograma de ejemplo: pico principal único y línea base limpia';

$rotulo_pico = $lote ? $lote['pureza'] . ' % · tR ' . $lote['tr'] . ' min' : 'pico principal';
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class('pys-portada'); ?>>
<div id="halo" aria-hidden="true"></div>

<div class="cintillo">
  <div class="wrap">
    <span class="coa">◆ <b>COA por lote</b> — cada vial con su cromatograma</span>
    <span>Envío <b>24–48 h</b> a todo México</span>
    <span>SPEI · tarjeta · OXXO</span>
    <span>Pureza verificada por <b>HPLC</b></span>
  </div>
</div>

<header class="top">
  <div class="wrap">
    <a class="marca" href="#top"><span class="mb">P&amp;S</span>
      <span class="nom">Péptidos y Suplementos</span></a>
    <nav class="menu" id="menu"></nav>
    <button class="icob burger" id="burger" aria-label="Abrir menú" aria-expanded="false"
            aria-controls="mnav">
      <svg class="abre" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="1.9"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      <svg class="cierra" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="1.9"><path d="M6 6l12 12M18 6L6 18"/></svg>
    </button>
    <a class="icob" id="carrito" href="<?php echo esc_url($url_carrito); ?>" aria-label="Carrito">
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           stroke-width="1.8"><path d="M3 4h2l2.6 11.4a2 2 0 0 0 2 1.6h7.7a2 2 0 0 0 2-1.5L21 8H6"/>
        <circle cx="10" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/></svg>
      <span class="cuenta-carrito" id="cuenta-carrito" hidden></span>
    </a>
  </div>
  <div id="mnav" hidden><div class="wrap" id="mnav-cuerpo"></div></div>
</header>

<div class="hero" id="top">
  <div class="wrap">
    <div>
      <span class="vs" data-rev>Péptidos de investigación · México</span>
      <h1 data-rev>Péptidos con <em>certificado de análisis</em> por lote.</h1>
      <p class="lede" data-rev>Pureza verificada por HPLC, masa confirmada por espectrometría y
        ficha técnica con referencias comprobables en PubMed. Si no lo podemos enseñar,
        no lo vendemos.</p>
      <div class="cta" data-rev>
        <a class="btn pri" href="#catalogo">Ver catálogo</a>
        <a class="btn" href="#coa">Cómo se lee un COA</a>
      </div>
      <div class="sellos" data-rev>
<?php if ($lote && $lote['pureza']) : ?>
        <span class="sello ok"><?php echo esc_html($lote['pureza']); ?> % HPLC · lote en curso</span>
<?php endif; ?>
        <span class="sello"><?php echo esc_html($n_prod); ?> <?php echo $n_prod === 1 ? 'referencia' : 'referencias'; ?></span>
        <span class="sello">Envío 24–48 h</span>
      </div>
    </div>
    <div>
      <div class="vitrina" id="vitrina" role="img"
           aria-label="Vial de Retatrutida 30 mg; se puede girar para verlo por todos lados">
        <div class="lienzo"></div>
        <span class="marco" aria-hidden="true"></span>
        <span class="grados mono" id="grados">0°</span>
        <span class="pista">Arrastra para girar</span>
      </div>
    </div>
  </div>
</div>

<?php /* Sin lote configurado no se imprime nada: un número de lote
          inventado sobre una tienda real no es una opción. */ ?>
<?php if ($lote) : ?>
<div class="banda">
  <dl class="wrap">
    <div><dt>Lote en curso</dt><dd><?php echo esc_html($lote['lote']); ?></dd></div>
<?php if ($lote['producto']) : ?>
    <div><dt>Producto</dt><dd style="font-family:var(--optima);font-size:19px"><?php echo esc_html($lote['producto']); ?></dd></div>
<?php endif; ?>
<?php if ($lote['pureza']) : ?>
    <div class="ok"><dt>Pureza</dt><dd><?php echo esc_html($lote['pureza']); ?> %</dd></div>
<?php endif; ?>
<?php if ($lote['masa']) : ?>
    <div><dt>Masa (MS)</dt><dd><?php echo esc_html($lote['masa']); ?></dd></div>
<?php endif; ?>
<?php if ($lote['endotoxinas']) : ?>
    <div><dt>Endotoxinas</dt><dd><?php echo esc_html($lote['endotoxinas']); ?></dd></div>
<?php endif; ?>
  </dl>
</div>
<?php endif; ?>

<section id="categorias">
  <div class="wrap">
    <div class="cab">
      <div><span class="vs">Catálogo por función</span>
        <h2>Qué buscas resolver</h2></div>
      <a class="link-mas" href="#catalogo">Ver las <?php echo esc_html($n_prod); ?> referencias →</a>
    </div>
    <div class="cats" id="cats"></div>
  </div>
</section>

<section id="catalogo">
  <div class="wrap">
    <div class="cab">
      <div><span class="vs">Existencias verificadas</span>
        <h2>Catálogo</h2>
        <p>Todos los péptidos se entregan liofilizados y sellados al vacío, con su certificado
          de análisis descargable por número de lote.</p></div>
      <span class="vs mono" id="cuenta"></span>
    </div>
    <div class="filtros" id="filtros" role="group" aria-label="Filtrar catálogo"></div>
    <div class="rejilla" id="rejilla"></div>
  </div>
</section>

<section class="detalle" id="vial">
  <div class="wrap">
    <div class="pegado">
      <div class="vitrina" id="vitrina2" role="img" aria-label="El mismo vial girando conforme lees">
        <div class="lienzo"></div>
        <span class="marco" aria-hidden="true"></span>
        <span class="grados mono" id="grados2">0°</span>
      </div>
    </div>
    <div class="notas" id="notas">
      <div class="nota">
        <span class="ord">01 · EL SELLO</span>
        <h3>Flip-off blanco sobre engaste de aluminio</h3>
        <p>La tapa de seguridad sobresale un 110 % del engaste y va lisa, sin estrías. Si el
          flip-off ya está levantado cuando te llega, el vial no se usa.</p>
      </div>
      <div class="nota">
        <span class="ord">02 · LA ETIQUETA</span>
        <h3>Impresa con el lote, no con una pegatina</h3>
        <p>Nombre, dosis, pureza, método y la leyenda de uso de investigación. Al reverso va el
          monograma; gíralo y lo ves aparecer.</p>
      </div>
      <div class="nota">
        <span class="ord">03 · LA TORTA</span>
        <h3>Liofilizada, no en polvo suelto</h3>
        <p>El péptido viene en torta compacta al fondo. Una torta rota o pegada a la pared
          significa que el vial viajó mal, y eso se reclama.</p>
      </div>
      <div class="nota">
        <span class="ord">04 · EL VIDRIO</span>
        <h3>Tipo I, pared de 1.1 mm</h3>
        <p>Borosilicato neutro. No cede iones al contenido ni cuando el vial pasa semanas
          reconstituido en refrigeración.</p>
      </div>
    </div>
  </div>
</section>

<section class="coa" id="coa">
  <div class="wrap">
    <div>
      <span class="vs">Certificado de análisis</span>
      <h2 style="font-size:clamp(28px,3.8vw,50px);margin-block:12px 16px">El COA no es un adorno:
        es el producto</h2>
      <p style="color:var(--tinta-2);max-width:44ch">Un certificado sin número de lote y sin
        método no se puede comprobar. El nuestro trae los dos, y el cromatograma del que sale
        el número.</p>
      <ol class="pasos">
        <li><span class="n">01</span><div><b>Se corre el HPLC</b>
          <p>El detector UV a 214 nm separa el péptido de lo que no lo es. El área bajo el pico
            principal es la pureza.</p></div></li>
        <li><span class="n">02</span><div><b>Se confirma la masa</b>
          <p>La espectrometría dice si la molécula pesa lo que debe. Pureza correcta con masa
            equivocada es otro compuesto.</p></div></li>
        <li><span class="n">03</span><div><b>Se publica con su lote</b>
          <p>El certificado se sube con el número que está impreso en tu vial. No es un PDF
            genérico de proveedor.</p></div></li>
      </ol>
    </div>

    <div class="grafica">
      <div class="cabg">
<?php if ($lote) : ?>
        <span>MUESTRA <b><?php echo esc_html($lote['producto']); ?></b></span>
        <span>LOTE <b><?php echo esc_html($lote['lote']); ?></b></span>
<?php else : ?>
        <span class="ejemplo">Trazo de ejemplo — no es un lote real</span>
<?php endif; ?>
        <span>HPLC-UV <b>214 nm</b></span>
      </div>
      <svg id="svg" viewBox="0 0 1200 300" preserveAspectRatio="none" role="img"
           aria-label="<?php echo esc_attr($alt_svg); ?>">
        <g class="malla">
          <line x1="0" y1="268" x2="1200" y2="268"/>
          <line x1="0" y1="201" x2="1200" y2="201" opacity=".5"/>
          <line x1="0" y1="134" x2="1200" y2="134" opacity=".5"/>
          <line x1="0" y1="67" x2="1200" y2="67" opacity=".5"/>
        </g>
        <path id="areag"></path>
        <path id="traza"></path>
        <text id="pico" x="760" y="30" text-anchor="middle" fill="#EEF6F3"
              style="font-family:var(--mono);font-size:10px;letter-spacing:.06em;opacity:0"><?php echo esc_html($rotulo_pico); ?></text>
        <g class="ejeg">
          <text x="4" y="290">0</text><text x="296" y="290">4</text>
          <text x="596" y="290">8</text><text x="896" y="290">12</text>
          <text x="1158" y="290">16 min</text>
        </g>
      </svg>
<?php if ($lote) : ?>
      <dl class="pie">
        <div><dt>Pureza</dt><dd style="color:var(--aqua)"><?php echo esc_html($lote['pureza']); ?> %</dd></div>
        <div><dt>tR</dt><dd><?php echo esc_html($lote['tr']); ?> min</dd></div>
        <div><dt>Masa</dt><dd><?php echo esc_html($lote['masa']); ?></dd></div>
        <div><dt>Endotox.</dt><dd><?php echo esc_html($lote['endotoxinas']); ?></dd></div>
      </dl>
<?php endif; ?>
    </div>
  </div>
</section>

<section id="guias">
  <div class="wrap">
    <div class="cab">
      <div><span class="vs">Guías</span>
        <h2>Lo que hay que saber antes de comprar</h2>
        <p>Dieciocho guías escritas con referencias verificables. Reconstitución, dosis,
          diferencias entre compuestos y qué dice la evidencia.</p></div>
      <a class="link-mas" href="https://peptidosysuplementos.mx/category/blog/">Ver el blog →</a>
    </div>
    <div class="guias" id="guias"></div>
  </div>
</section>

<section class="faq" id="faq">
  <div class="wrap">
    <div><span class="vs">Preguntas</span>
      <h2 style="font-size:clamp(26px,3.4vw,44px);margin-top:12px">Lo que más nos preguntan</h2></div>
    <div>
      <details open>
        <summary>¿Qué es el COA por lote y dónde lo veo?</summary>
        <p>El certificado de análisis es el reporte del laboratorio para ese lote concreto: trae
          la pureza medida por HPLC, la masa confirmada por espectrometría y el método completo
          con el que se corrió. El número de lote está impreso en la etiqueta de tu vial y es el
          mismo con el que se publica el certificado, así que puedes cotejarlo.</p>
      </details>
      <details>
        <summary>¿Cómo se reconstituye un vial liofilizado?</summary>
        <p>Con agua bacteriostática, dejándola escurrir por la pared del vial y sin agitar: se
          gira despacio hasta disolver. La cantidad de agua define la concentración y por lo
          tanto cuántas unidades marcas en la jeringa de insulina. La guía de reconstitución
          tiene la tabla de volúmenes paso a paso.</p>
      </details>
      <details>
        <summary>¿Por qué dice «solo para investigación»?</summary>
        <p>Porque es lo que son. Estos compuestos no están aprobados por COFEPRIS para uso
          humano, no son medicamentos y no sustituyen una consulta médica. Se venden para uso
          de investigación y así va impreso en cada etiqueta.</p>
      </details>
      <details>
        <summary>¿Cuánto tarda el envío y cómo puedo pagar?</summary>
        <p>El envío es de 24 a 48 horas a todo México. Se puede pagar por transferencia SPEI,
          con tarjeta o en efectivo en OXXO.</p>
      </details>
      <details>
        <summary>¿Cómo se guarda un péptido?</summary>
        <p>Liofilizado y sellado aguanta a temperatura ambiente el traslado, pero se conserva
          mejor refrigerado y al abrigo de la luz. Una vez reconstituido va siempre en
          refrigeración, y el tiempo que dura en buen estado depende del compuesto: viene en
          la ficha de cada producto.</p>
      </details>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="pie">
      <div>
        <h4>Aviso</h4>
        <p>Los péptidos de este catálogo se comercializan para uso exclusivo de investigación.
          No son medicamentos, no están aprobados por COFEPRIS para uso humano y no sustituyen
          la consulta médica.</p>
      </div>
      <div><h4>Catálogo</h4><ul id="pie-cats"></ul></div>
      <div><h4>Guías</h4><ul id="pie-guias"></ul></div>
      <div><h4>Tienda</h4><ul>
        <li><a href="#coa">Certificados de análisis</a></li>
        <li><a href="#faq">Envíos y pagos</a></li>
        <li><a href="#faq">Preguntas frecuentes</a></li>
        <li><a href="#vial">Cómo es nuestro vial</a></li>
      </ul></div>
    </div>
    <div class="fin">
      <span>© 2026 PEPTIDOSYSUPLEMENTOS.MX</span>
      <span>SOLO USO DE INVESTIGACIÓN · NO PARA CONSUMO HUMANO</span>
    </div>
  </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
