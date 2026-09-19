(function(){
  /* Los datos los imprime el plugin desde WooCommerce: productos, precios,
     existencias, categorías y entradas del blog. El prototipo los traía en
     un archivo escrito a mano; aquí eso sería publicar precios falsos. */
  const D = window.PYS_DATOS || {};
  const PYS_SITIO     = D.sitio     || location.origin;
  const PYS_CATS      = D.cats      || [];
  const PYS_PRODUCTOS = D.productos || [];
  const PYS_BLOG      = D.blog      || [];
  const PYS_LANDINGS  = D.landings  || [];
  const ASSETS        = D.assets    || "";

  const { animate, inView, stagger, scroll } = window.Motion || {};
  const quieto = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const suave = [0.22, 0.61, 0.36, 1];
  const $ = (s) => document.querySelector(s);

  /* ── cuántos productos hay de verdad en cada categoría ──────────── */
  const cuentaCat = (largo) => PYS_PRODUCTOS.filter(p => p.cats.includes(largo)).length;

  /* ── navegación, armada desde las categorías y landings reales ──── */
  const menu = $("#menu");
  [["Catálogo","#catalogo"],["El vial","#vial"],["COA","#coa"],["Guías","#guias"],
   ["Preguntas","#faq"]].forEach(([t,u]) => {
    const a = document.createElement("a"); a.href = u; a.textContent = t; menu.appendChild(a);
  });

  const mcuerpo = $("#mnav-cuerpo");
  function et(txt){ const s=document.createElement("span"); s.className="et"; s.textContent=txt;
                    mcuerpo.appendChild(s); }
  function enlace(t,u,k){ const a=document.createElement("a"); a.href=u;
    a.innerHTML = t + (k ? '<span class="k">'+k+'</span>' : ''); mcuerpo.appendChild(a); }
  et("Catálogo");
  PYS_CATS.forEach(c => enlace(c.corto, "#catalogo", cuentaCat(c.largo) + " REF."));
  et("Calidad");
  enlace("Certificados de análisis", "#coa");
  enlace("Cómo es nuestro vial", "#vial");
  et("Contenido");
  enlace("Guías", "#guias", PYS_BLOG.length + "");
  enlace("Preguntas frecuentes", "#faq");

  const burger = $("#burger"), mnav = $("#mnav");
  function abrirNav(abre){
    mnav.hidden = !abre;
    burger.setAttribute("aria-expanded", abre ? "true" : "false");
    burger.setAttribute("aria-label", abre ? "Cerrar menú" : "Abrir menú");
    if (abre && animate && !quieto)
      animate(mnav.querySelectorAll(".et, a"), { opacity:[0,1], y:[-8,0] },
              { duration:.3, delay: stagger(0.03), ease: suave });
  }
  burger.addEventListener("click", () => abrirNav(mnav.hidden));
  mnav.addEventListener("click", (e) => { if (e.target.closest("a")) abrirNav(false); });
  addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !mnav.hidden){ abrirNav(false); burger.focus(); }
  });

  /* ── el resplandor sigue al cursor ──────────────────────────────── */
  const halo = $("#halo");
  if (!quieto && matchMedia("(hover:hover)").matches){
    let t = 0;
    addEventListener("pointermove", (e) => {
      const ahora = performance.now();
      if (ahora - t < 60) return;
      t = ahora;
      halo.style.setProperty("--mx", (e.clientX / innerWidth * 100).toFixed(1) + "%");
      halo.style.setProperty("--my", (e.clientY / innerHeight * 100).toFixed(1) + "%");
    }, { passive:true });
  }

  /* ── los dos visores de 360 ─────────────────────────────────────── */
  const ruta = (i) => ASSETS + "img/giro/g" + String(i).padStart(2,"0") + ".jpg";
  const visorHero = PYS.giro360($("#vitrina"),  { cuadros:36, ruta, grados:$("#grados") });
  const visorDet  = PYS.giro360($("#vitrina2"), { cuadros:36, ruta, grados:$("#grados2") });
  if (!quieto && scroll)
    scroll((p) => visorDet.aProgreso(p),
           { target: $("#notas"), offset: ["start 80%", "end 60%"] });

  const notas = [...document.querySelectorAll(".nota")];
  if (inView) notas.forEach((n) => inView(n, () => {
    notas.forEach(o => o.classList.toggle("viva", o === n));
    return () => {};
  }, { amount: 0.55 }));

  /* ── categorías reales ──────────────────────────────────────────── */
  const cats = $("#cats");
  PYS_CATS.forEach((c) => {
    const n = cuentaCat(c.largo);
    const a = document.createElement("a");
    a.className = "cat"; a.href = "#catalogo"; a.dataset.filtro = c.corto;
    a.innerHTML = '<span class="c">' + n + (n === 1 ? " referencia" : " referencias") + '</span>' +
                  '<span class="n">' + c.largo + '</span>' +
                  '<span class="flecha">Ver →</span>';
    a.addEventListener("click", () => aplicaFiltro(c.corto));
    cats.appendChild(a);
  });

  /* ── catálogo real ──────────────────────────────────────────────── */
  const rejilla = $("#rejilla"), filtros = $("#filtros"), cuenta = $("#cuenta");
  const esc = (t) => String(t == null ? "" : t)
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");

  function pinta(lista){
    rejilla.innerHTML = "";
    lista.forEach((p) => {
      const art = document.createElement("article");
      art.className = "tarjeta";
      const agotado = p.existencia !== "instock";
      const medio = p.frasco
        ? '<div class="frasco" role="img" aria-label="Frasco de ' + p.nombre + '">' +
            '<span class="tapa"></span>' +
            '<span class="rotulo"><b>P&amp;S</b><i>suplemento</i></span></div>'
        : '<img src="' + esc(p.img) + '" alt="' + esc(p.nombre) + '" loading="lazy">';
      art.innerHTML =
        '<div class="foto">' +
          '<span class="eti">' + p.cat + '</span>' +
          (agotado ? '' : '<span class="coa-sello">COA</span>') +
          medio +
          (agotado ? '<div class="agotado"><span>Agotado</span></div>' : '') +
        '</div>' +
        '<div class="cuerpo"><h3><a href="' + esc(p.url) + '">' + esc(p.nombre) + '</a></h3>' +
          '<div class="sku">' + (p.sku ? "SKU " + esc(p.sku) : "&nbsp;") + '</div></div>' +
        /* `specs` lo arma PHP desde el atributo del producto o su
           categoría. Si viene vacío solo se dice la existencia, que es lo
           único que se sabe seguro de cualquier producto. */
        '<div class="specs">' +
          (p.specs || []).map(t => '<span>' + esc(t) + '</span><span>·</span>').join('') +
          '<span>' + (agotado ? "sin existencia" : "en existencia") + '</span></div>' +
        /* El precio lo pinta WooCommerce: ya resuelve moneda, rangos de
           producto variable y el tachado de oferta. Y el botón es el suyo,
           con las clases que engancha wc-add-to-cart, no un botón de
           mentira: `ajax_add_to_cart` solo va en productos simples, que son
           los únicos que se añaden sin pasar por la ficha. */
        '<div class="compra"><span class="precio">' + (p.precioHtml || "") + '</span>' +
          (p.comprable
            ? '<a class="add add_to_cart_button' +
              (p.tipo === "simple" ? ' ajax_add_to_cart' : '') + '"' +
              ' href="' + esc(p.addUrl) + '"' +
              ' data-product_id="' + esc(p.id) + '" data-quantity="1" rel="nofollow">' +
              esc(p.addTexto || "Agregar") + '</a>'
            : '<a class="add" href="' + esc(p.url) + '">Ver ficha</a>') +
        '</div>';
      rejilla.appendChild(art);
    });
    cuenta.textContent = lista.length + (lista.length === 1 ? " REFERENCIA" : " REFERENCIAS");
    if (animate && !quieto)
      animate(rejilla.querySelectorAll(".tarjeta"), { opacity:[0,1], y:[16,0] },
              { duration:.45, delay: stagger(0.028), ease: suave });
  }

  function aplicaFiltro(corto){
    filtros.querySelectorAll(".filtro").forEach(b =>
      b.setAttribute("aria-pressed", b.dataset.f === corto ? "true" : "false"));
    const cat = PYS_CATS.find(c => c.corto === corto);
    pinta(corto === "todo" ? PYS_PRODUCTOS
                           : PYS_PRODUCTOS.filter(p => p.cats.includes(cat.largo)));
  }

  [{corto:"todo"}, ...PYS_CATS].forEach((c) => {
    const b = document.createElement("button");
    b.className = "filtro"; b.type = "button"; b.dataset.f = c.corto;
    b.textContent = c.corto === "todo" ? "Todo" : c.corto;
    b.setAttribute("aria-pressed", c.corto === "todo" ? "true" : "false");
    b.addEventListener("click", () => aplicaFiltro(c.corto));
    filtros.appendChild(b);
  });
  pinta(PYS_PRODUCTOS);

  /* ── el cromatograma del COA ────────────────────────────────────── */
  const picos = [[760,20,232],[250,10,17],[980,14,13],[400,9,9],[600,8,6]];
  const senal = (x) => picos.reduce((a,[c,s,h]) => a + h*Math.exp(-((x-c)**2)/(2*s*s)), 0);
  let d = "";
  for (let x = 0; x <= 1200; x += 2) d += (x ? "L" : "M") + x + "," + (268 - senal(x)).toFixed(2);
  $("#traza").setAttribute("d", d);
  $("#areag").setAttribute("d", d + "L1200,268L0,268Z");

  if (animate && inView && !quieto){
    /* Se dibuja con `pathLength` y no con `strokeDashoffset`: motion no
       reconoce esa segunda clave y la animación se quedaba sin correr —la
       traza no aparecía nunca, solo el área rellena de abajo. Con
       pathLength=1 el recorrido se mide de 0 a 1 y da igual lo que mida
       el trazo de verdad. */
    const traza = $("#traza");
    traza.setAttribute("pathLength", "1");
    /* como atributo y no como estilo en línea: motion escribe el
       stroke-dasharray de pathLength en el atributo, y un estilo en línea
       le gana siempre —la traza se quedaba congelada en «0 1». */
    traza.setAttribute("stroke-dasharray", "0 1");
    $("#areag").style.opacity = "0";
    inView($(".grafica"), () => {
      animate(traza, { pathLength:[0, 1] }, { duration:2.2, ease:"easeInOut" });
      animate($("#areag"), { opacity:[0,1] }, { duration:.9, delay:1.5 });
      animate($("#pico"), { opacity:[0,1] }, { duration:.6, delay:1.7 });
    }, { amount:.35 });
  } else {
    $("#pico").style.opacity = "1";
  }

  /* ── guías reales ───────────────────────────────────────────────── */
  const guias = $("#guias");
  const MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
  PYS_BLOG.slice(0, 6).forEach((g) => {
    const [a, m, dia] = g.fecha.split("-");
    const el = document.createElement("a");
    el.className = "guia"; el.href = g.url;
    el.innerHTML = '<h3>' + g.titulo + '</h3>' +
      '<div class="meta"><span>' + dia + " " + MESES[+m - 1] + " " + a + '</span>' +
      '<span>' + Math.max(1, Math.round(g.palabras / 220)) + ' min</span></div>';
    guias.appendChild(el);
  });

  /* ── pie ────────────────────────────────────────────────────────── */
  const pc = $("#pie-cats");
  PYS_CATS.slice(0, 5).forEach((c) => {
    const li = document.createElement("li");
    li.innerHTML = '<a href="#catalogo">' + c.corto + '</a>';
    li.querySelector("a").addEventListener("click", () => aplicaFiltro(c.corto));
    pc.appendChild(li);
  });
  const pg = $("#pie-guias");
  PYS_BLOG.slice(0, 4).forEach((g) => {
    const li = document.createElement("li");
    li.innerHTML = '<a href="' + g.url + '">' + g.titulo.split(":")[0].split("|")[0].trim() + '</a>';
    pg.appendChild(li);
  });

  /* ── datos estructurados ────────────────────────────────────────────
     Apagado por defecto: el sitio ya emite schema por su plugin de SEO y
     duplicar Organization, WebSite o FAQPage no suma, confunde. Se
     enciende con el filtro `pys_portada_schema` si se comprueba que no hay
     solapamiento. Aun encendido no se declara `offers`: los precios los
     declara la ficha de cada producto, que es donde corresponde. */
  if (D.schema) {
  const faqs = [...document.querySelectorAll(".faq details")].map((d) => ({
    "@type":"Question", name: d.querySelector("summary").textContent.trim(),
    acceptedAnswer:{ "@type":"Answer", text: d.querySelector("p").textContent.trim() }
  }));
  $("#ld").textContent = JSON.stringify([
    { "@context":"https://schema.org", "@type":"Organization",
      name:"Péptidos y Suplementos", url:PYS_SITIO, areaServed:"MX" },
    { "@context":"https://schema.org", "@type":"WebSite",
      name:"Péptidos y Suplementos", url:PYS_SITIO, inLanguage:"es-MX" },
    { "@context":"https://schema.org", "@type":"ItemList",
      name:"Catálogo de péptidos de investigación",
      numberOfItems: PYS_PRODUCTOS.length,
      itemListElement: PYS_PRODUCTOS.map((p, i) => ({
        "@type":"ListItem", position:i+1, name:p.nombreSeo, url:p.url })) },
    { "@context":"https://schema.org", "@type":"FAQPage", mainEntity:faqs }
  ]);
  }

  /* ── entradas ───────────────────────────────────────────────────── */
  if (animate && !quieto){
    animate("[data-rev]", { opacity:[0,1], y:[20,0] },
            { duration:.8, delay: stagger(0.08, { startDelay:.1 }), ease: suave });
    animate("#vitrina", { opacity:[0,1], scale:[.965,1] }, { duration:1, delay:.25, ease: suave });
    animate(".banda div", { opacity:[0,1] }, { duration:.6, delay: stagger(0.05, { startDelay:.5 }) });
    if (inView){
      [".cat", ".guia", ".pasos li"].forEach((sel) => {
        const els = document.querySelectorAll(sel);
        if (!els.length) return;
        els.forEach(e => e.style.opacity = "0");
        inView(els[0].parentElement, () => animate(els, { opacity:[0,1], y:[14,0] },
               { duration:.5, delay: stagger(0.05), ease: suave }), { amount:.15 });
      });
    }
  }

  /* ── el carrito, ya de verdad ───────────────────────────────────────
     WooCommerce dispara `added_to_cart` cuando su AJAX termina; ahí se
     actualiza la cuenta y se sacude el icono. Sin jQuery no hay evento, y
     entonces el enlace funciona igual pero recargando, que es el
     comportamiento correcto de reserva. */
  const icono = $("#carrito"), cuentaCarrito = $("#cuenta-carrito");

  function pintaCuenta(n) {
    if (!cuentaCarrito) return;
    cuentaCarrito.textContent = n;
    cuentaCarrito.hidden = !n;
  }
  pintaCuenta(Number(D.enCarrito || 0));

  if (window.jQuery) {
    window.jQuery(document.body).on("added_to_cart", (_e, fragmentos, _hash, boton) => {
      const n = Number(cuentaCarrito && cuentaCarrito.textContent || 0) + 1;
      pintaCuenta(n);
      if (animate && !quieto) animate(icono, { scale:[1,1.18,1] }, { duration:.4 });
      if (boton && boton[0]) boton[0].textContent = "Agregado";
    });
  }
})();
