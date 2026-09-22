"""
Verificación visual y por código del rediseño de PYS — antes y después.

Nace de un error concreto: en /blog/ quedaron dos rejillas con las mismas
entradas y nadie lo vio porque solo se revisó la parte de arriba de la página.
Esta herramienta mira la página ENTERA, en escritorio y en teléfono, y además
de capturarla comprueba por código los fallos que ya aparecieron:

  - contenido DUPLICADO a la vista (el fallo del blog)
  - imágenes que se salen de su caja y quedan cortadas (el fallo del catálogo)
  - texto invisible por degradado recortado (el fallo del botón)
  - desborde horizontal (la página se puede arrastrar de lado)
  - restos del diseño viejo: radios grandes y texto con degradado
  - imágenes rotas y errores de consola
  - y una HUELLA del contenido, para demostrar que el rediseño no quitó ni
    cambió texto: el contenido del HTML debe salir idéntico antes y después.

Uso:
  py -3.11 verificar.py <etiqueta> <url> [<url> ...]
  py -3.11 verificar.py <etiqueta> --lista urls.txt
  py -3.11 verificar.py --comparar <etiqueta_antes> <etiqueta_despues>

Deja por página: <slug>__escritorio.jpg, <slug>__movil.jpg y <slug>.json en
rediseno/verificacion/<etiqueta>/, más un resumen.json.
"""

import hashlib
import json
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "verificacion"
BASE = "https://peptidosysuplementos.mx"

VISTAS = {
    "escritorio": {"viewport": {"width": 1440, "height": 900}, "is_mobile": False},
    "movil": {
        "viewport": {"width": 390, "height": 844}, "is_mobile": True, "has_touch": True,
        "user_agent": ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/128.0 Mobile Safari/537.36"),
    },
}

# Todo lo que corre dentro de la página. Devuelve un diccionario de hallazgos.
SONDA = r"""
() => {
  const visible = e => {
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' &&
           s.display !== 'none' && parseFloat(s.opacity) > 0.05;
  };
  const ruta = e => {
    const p = [];
    while (e && e.nodeType === 1 && p.length < 4) {
      let x = e.tagName.toLowerCase();
      if (e.id) { x += '#' + e.id; p.unshift(x); break; }
      const c = (typeof e.className === 'string' ? e.className : '').trim().split(/\s+/).filter(Boolean);
      if (c.length) x += '.' + c.slice(0, 2).join('.');
      p.unshift(x); e = e.parentElement;
    }
    return p.join(' > ');
  };
  const norm = t => (t || '').replace(/\s+/g, ' ').trim();

  // la cabecera, el pie, el cintillo y el fondo son comunes a todo el sitio:
  // se excluyen para que la huella mida SOLO el contenido de la página
  const CROMO = 'header.top, .cintillo, footer.pie-h26, #mnav, #busca, .hexes, #halo, script, style, noscript';
  const cuerpo = document.body.cloneNode(true);
  cuerpo.querySelectorAll(CROMO).forEach(n => n.remove());
  const textoHTML = norm(cuerpo.textContent);

  // 1. duplicados visibles: el mismo titular dos o más veces
  const SEL_TIT = 'h1, h2, h3, h4, .pg-cardtitle, .elementor-post__title, ' +
                  '.woocommerce-loop-product__title, .tarjeta h3';
  const cuenta = {};
  document.querySelectorAll(SEL_TIT).forEach(e => {
    if (!visible(e) || e.closest(CROMO)) return;
    const t = norm(e.textContent);
    if (t.length < 12) return;
    cuenta[t] = (cuenta[t] || 0) + 1;
  });
  const duplicados = Object.entries(cuenta).filter(([, n]) => n > 1)
                           .map(([t, n]) => ({ texto: t.slice(0, 90), veces: n }));

  // 2. imágenes que se salen de una caja con overflow oculto (quedan cortadas)
  const cortadas = [];
  document.querySelectorAll('img').forEach(im => {
    if (!visible(im) || im.closest(CROMO)) return;
    let a = im.parentElement;
    let desplazable = false;
    while (a && a !== document.body) {
      const s = getComputedStyle(a);
      // una tabla que se desplaza de lado NO corta: lo que no cabe se alcanza
      // deslizando (los emoji de las tablas del blog en móvil daban falso aviso)
      if (/(auto|scroll)/.test(s.overflowX + s.overflowY)) { desplazable = true; break; }
      if (s.overflow === 'hidden' || s.overflowY === 'hidden' || s.overflowX === 'hidden') break;
      a = a.parentElement;
    }
    if (desplazable || !a || a === document.body) return;
    const ri = im.getBoundingClientRect(), ra = a.getBoundingClientRect();
    const sobra = Math.max(ra.top - ri.top, ri.bottom - ra.bottom, ra.left - ri.left, ri.right - ra.right);
    // Lo que importa es si la CAJA de la imagen se sale de su contenedor, no su
    // object-fit: el fallo del catálogo tenía `contain` y aun así el <img>
    // medía 250 px dentro de una caja de 187 y se comía 63. El umbral deja
    // pasar el par de píxeles que Elementor desborda a propósito para que no
    // queden rendijas en sus miniaturas.
    if (sobra > Math.max(12, ri.height * 0.06))
      cortadas.push({ img: (im.currentSrc || im.src).split('/').pop().slice(0, 60),
                      sobra_px: Math.round(sobra), caja: ruta(a) });
  });

  // 3. texto invisible por relleno transparente
  const invisibles = [];
  document.querySelectorAll('a, button, span, h1, h2, h3, p, label').forEach(e => {
    if (!visible(e) || e.closest(CROMO)) return;
    if (!norm(e.textContent)) return;
    const s = getComputedStyle(e);
    const fill = s.webkitTextFillColor || '';
    const transp = fill === 'rgba(0, 0, 0, 0)' || fill === 'transparent';
    const clipTexto = (s.webkitBackgroundClip || s.backgroundClip) === 'text';
    if (transp && !(clipTexto && s.backgroundImage !== 'none'))
      invisibles.push({ texto: norm(e.textContent).slice(0, 50), donde: ruta(e) });
  });

  // 4. restos del diseño viejo
  const radios = [], degradados = [];
  document.querySelectorAll('body *').forEach(e => {
    if (e.closest(CROMO)) return;
    const s = getComputedStyle(e);
    if (s.display === 'none') return;
    const r = e.getBoundingClientRect();
    if (r.width < 60 || r.height < 30) return;
    const rad = parseFloat(s.borderTopLeftRadius) || 0;
    // un radio solo se ve si el elemento tiene fondo, borde o sombra: sin eso
    // es invisible y no cuenta como resto del diseño viejo
    const pinta = (s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent') ||
                  s.backgroundImage !== 'none' || parseFloat(s.borderTopWidth) > 0 || s.boxShadow !== 'none';
    // se ignoran los círculos a propósito (botones redondos, avatares) y el
    // chat de Tanus (#cw-*), que es otro producto y no entra en el rediseño
    if (rad > 10 && pinta && !(Math.abs(r.width - r.height) < 4 && rad >= r.width / 2 - 2) &&
        !e.closest('[class*=chat], [id*=chat], [class*=tanus], [id^=cw-], [class^=cw-]'))
      radios.push({ radio: Math.round(rad), donde: ruta(e) });
    const clip = (s.webkitBackgroundClip || s.backgroundClip) === 'text';
    if (clip && s.backgroundImage.includes('gradient') && norm(e.textContent))
      degradados.push({ texto: norm(e.textContent).slice(0, 50), donde: ruta(e) });
  });

  // 5. imágenes rotas
  const rotas = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && visible(i))
                  .map(i => (i.currentSrc || i.src).split('/').pop().slice(0, 60));

  const titulos = [...document.querySelectorAll('h1, h2')].filter(e => !e.closest(CROMO))
                   .map(e => norm(e.textContent).slice(0, 80)).filter(Boolean);

  return {
    titulo_pagina: document.title,
    cromo_nuevo: !!document.querySelector('header.top'),
    cromo_viejo: !!document.querySelector('[data-elementor-type=header], [data-elementor-type=footer]'),
    // en teléfono `innerWidth` crece CON el desborde (el navegador ensancha la página
    // y la muestra alejada), así que compararlo consigo mismo nunca daba desborde:
    // así se escapó la cabecera de 461 px. Se compara contra el ancho del aparato.
    desborde_horizontal: document.documentElement.scrollWidth > Math.min(innerWidth, screen.width) + 1,
    ancho_pagina: document.documentElement.scrollWidth,
    alto_pagina: document.documentElement.scrollHeight,
    duplicados, imagenes_cortadas: cortadas.slice(0, 12), texto_invisible: invisibles.slice(0, 12),
    radios_viejos: radios.slice(0, 12), n_radios_viejos: radios.length,
    texto_degradado: degradados.slice(0, 8), imagenes_rotas: rotas.slice(0, 12),
    huella: {
      palabras_html: textoHTML ? textoHTML.split(' ').length : 0,
      palabras_visibles: norm(document.body.innerText).split(' ').length,
      titulos,
      _texto: textoHTML,
    },
  };
}
"""


def slug(url):
    ruta, _, consulta = url.replace(BASE, "").partition("?")
    ruta = ruta.strip("/") or "portada"
    if consulta:
        # sin esto /?s=bpc y /?s=bpc&post_type=product caían las dos en «portada»
        ruta += "-" + consulta
    return re.sub(r"[^a-z0-9]+", "-", ruta.lower()).strip("-")[:80]


def capturar(etiqueta, urls):
    from playwright.sync_api import sync_playwright
    salida = RAIZ / etiqueta
    salida.mkdir(parents=True, exist_ok=True)
    resumen = {}
    with sync_playwright() as p:
        nav = p.chromium.launch()
        for url in urls:
            if not url.startswith("http"):
                url = BASE + "/" + url.lstrip("/")
            s = slug(url)
            resumen[s] = {"url": url}
            for vista, conf in VISTAS.items():
                ctx = nav.new_context(**conf, device_scale_factor=1)
                pag = ctx.new_page()
                errores = []
                pag.on("pageerror", lambda e: errores.append(str(e)[:200]))
                pag.on("console", lambda m: m.type == "error" and errores.append(m.text[:200]))
                sep = "&" if "?" in url else "?"
                try:
                    resp = pag.goto(f"{url}{sep}pysv={int(time.time())}", wait_until="networkidle",
                                    timeout=60000)
                    estado = resp.status if resp else 0
                except Exception as e:  # noqa: BLE001
                    resumen[s][vista] = {"error": str(e)[:200]}
                    ctx.close()
                    continue
                # carga todo lo diferido y deja terminar las animaciones de entrada:
                # si no, la captura sale con tarjetas a medio aparecer
                pag.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
                alto = pag.evaluate("document.documentElement.scrollHeight")
                paso = conf["viewport"]["height"]
                for y in range(0, alto, paso):
                    pag.evaluate(f"window.scrollTo(0, {y})")
                    pag.wait_for_timeout(180)
                # y espera a que TODAS las imágenes terminen: con las PNG de 1080 px de
                # /peptidos-mexico/ la captura salía con 14 de 18 tarjetas en blanco y
                # parecía un fallo del CSS. Una imagen a medio cargar tapa fallos reales.
                try:
                    pag.wait_for_function("[...document.images].every(i => i.complete)", timeout=25000)
                except Exception:  # noqa: BLE001
                    pass
                pag.evaluate("window.scrollTo(0, 0)")
                pag.wait_for_timeout(1800)
                datos = pag.evaluate(SONDA)
                datos["http"] = estado
                datos["errores_consola"] = errores[:10]
                texto = datos["huella"].pop("_texto")
                datos["huella"]["hash_contenido"] = hashlib.sha1(texto.encode()).hexdigest()[:12]
                (salida / f"{s}__{vista}.txt").write_text(texto, encoding="utf-8")
                pag.screenshot(path=str(salida / f"{s}__{vista}.jpg"), full_page=True,
                               type="jpeg", quality=68)
                resumen[s][vista] = datos
                ctx.close()
        nav.close()
    (salida / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    imprimir(resumen)
    return resumen


def problemas(d):
    """Lista legible de lo que está mal en una vista."""
    out = []
    if "error" in d:
        return [f"no cargó: {d['error']}"]
    if d.get("http") != 200:
        out.append(f"HTTP {d.get('http')}")
    if not d.get("cromo_nuevo"):
        out.append("sin cabecera nueva")
    if d.get("cromo_viejo"):
        out.append("sigue la cabecera/pie de Elementor")
    if d.get("desborde_horizontal"):
        out.append(f"desborde horizontal ({d['ancho_pagina']}px)")
    for x in d.get("duplicados", []):
        out.append(f"DUPLICADO ×{x['veces']}: «{x['texto']}»")
    for x in d.get("imagenes_cortadas", []):
        out.append(f"imagen cortada {x['sobra_px']}px: {x['img']}")
    for x in d.get("texto_invisible", []):
        out.append(f"texto invisible: «{x['texto']}»")
    for x in d.get("texto_degradado", []):
        out.append(f"texto con degradado viejo: «{x['texto']}»")
    if d.get("n_radios_viejos"):
        out.append(f"{d['n_radios_viejos']} elementos con radio grande del diseño viejo")
    for x in d.get("imagenes_rotas", []):
        out.append(f"imagen rota: {x}")
    for x in d.get("errores_consola", []):
        out.append(f"error de consola: {x[:110]}")
    return out


def imprimir(resumen):
    for s, v in resumen.items():
        for vista in VISTAS:
            d = v.get(vista, {})
            pr = problemas(d)
            marca = "OK " if not pr else "!! "
            print(f"{marca}{s} [{vista}]" + ("" if not pr else ""))
            for x in pr:
                print(f"      - {x}")


def comparar(antes, despues):
    """Antes vs después: el contenido debe seguir ahí y no debe haber fallos nuevos."""
    a = json.loads((RAIZ / antes / "resumen.json").read_text(encoding="utf-8"))
    d = json.loads((RAIZ / despues / "resumen.json").read_text(encoding="utf-8"))
    for s in d:
        if s not in a:
            print(f"?? {s}: no hay captura de antes")
            continue
        for vista in VISTAS:
            va, vd = a[s].get(vista, {}), d[s].get(vista, {})
            if "huella" not in va or "huella" not in vd:
                continue
            ha, hd = va["huella"], vd["huella"]
            mismo = ha["hash_contenido"] == hd["hash_contenido"]
            # el recuento de radios viejos se compara como número, no como texto:
            # «48 elementos…» y «10 elementos…» son una mejora, no un fallo nuevo
            ra, rd = va.get("n_radios_viejos", 0), vd.get("n_radios_viejos", 0)
            if ra or rd:
                tend = "bajó" if rd < ra else ("subió" if rd > ra else "igual")
                print(f"   radios del diseño viejo: {ra} → {rd} ({tend})" + ("  !!" if rd > ra else ""))
            sin_r = lambda v: {x for x in problemas(v) if "radio grande" not in x}
            pa, pd = sin_r(va), sin_r(vd)
            print(f"\n== {s} [{vista}] ==")
            print(f"   contenido del HTML: {'IDÉNTICO' if mismo else 'CAMBIÓ'} "
                  f"({ha['palabras_html']} → {hd['palabras_html']} palabras)")
            print(f"   palabras a la vista: {ha['palabras_visibles']} → {hd['palabras_visibles']}")
            if ha["titulos"] != hd["titulos"]:
                faltan = [t for t in ha["titulos"] if t not in hd["titulos"]]
                if faltan:
                    print(f"   !! titulares que ya no están: {faltan[:6]}")
            for x in sorted(pa - pd):
                print(f"   arreglado: {x}")
            for x in sorted(pd - pa):
                print(f"   !! NUEVO: {x}")
            for x in sorted(pa & pd):
                print(f"   sigue: {x}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    if args[0] == "--comparar":
        comparar(args[1], args[2])
    else:
        etiqueta, resto = args[0], args[1:]
        if resto and resto[0] == "--lista":
            resto = [l.strip() for l in Path(resto[1]).read_text(encoding="utf-8").splitlines() if l.strip()]
        capturar(etiqueta, resto)
