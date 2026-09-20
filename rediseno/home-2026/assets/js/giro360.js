/* ════════════════════════════════════════════════════════════════════
   Visor de 360° — PYS.giro360(elemento, opciones)

   Los 36 cuadros salen de la misma escena three.js con la que se hicieron
   los renders del catálogo (rediseno/mocks/generar-vial-3d.html), girando
   el vial 10° por cuadro. Se sirven como imágenes y no como WebGL a
   propósito: pesa 900 KB contra los ~600 KB de three.js más el modelo,
   corre en cualquier teléfono sin GPU y no hay nada que pueda fallar.

   Devuelve { aCuadro, aProgreso, cuadroActual }.
   ════════════════════════════════════════════════════════════════════ */
window.PYS = window.PYS || {};

window.PYS.giro360 = function (el, opc) {
  if (!el) return { aCuadro(){}, aProgreso(){}, cuadroActual(){ return 0; } };

  const N        = opc.cuadros || 36;
  const ruta     = opc.ruta;
  const etiqueta = opc.grados || null;
  /* Las animaciones corren siempre por decisión del usuario; ver la misma
     nota en la plantilla del home. Revertir = devolver el matchMedia. */
  const quieto   = false;

  const imgs    = new Array(N);
  const cargado = new Array(N).fill(false);
  let actual = 0;

  /* Un <img> por cuadro, apilados y conmutados por opacidad. Cambiar el
     src de uno solo parpadea la primera vez que toca cada cuadro. */
  for (let i = 0; i < N; i++) {
    const im = document.createElement("img");
    im.alt = "";
    im.decoding = "async";
    im.draggable = false;
    imgs[i] = im;
    el.appendChild(im);
  }

  function cargar(i, prioridad) {
    if (cargado[i]) return Promise.resolve();
    return new Promise((ok) => {
      const im = imgs[i];
      im.addEventListener("load", () => { cargado[i] = true; ok(); }, { once: true });
      im.addEventListener("error", () => { ok(); }, { once: true });
      if (prioridad) im.fetchPriority = "high";
      im.src = ruta(i);
    });
  }

  /* mientras un cuadro no esté, se enseña el cargado más cercano */
  function cercanoCargado(i) {
    for (let d = 0; d < N; d++) {
      const a = (i + d) % N, b = (i - d + N) % N;
      if (cargado[a]) return a;
      if (cargado[b]) return b;
    }
    return 0;
  }

  function mostrar(i) {
    actual = ((i % N) + N) % N;
    const k = cargado[actual] ? actual : cercanoCargado(actual);
    for (let j = 0; j < N; j++) imgs[j].classList.toggle("on", j === k);
    if (etiqueta) etiqueta.textContent = Math.round(actual * 360 / N) + "°";
  }

  /* el cuadro frontal primero; el resto en abanico, para que un giro
     parcial ya tenga con qué dibujarse antes de que acabe la descarga */
  (async function precargar() {
    await cargar(0, true);
    mostrar(0);
    const orden = [];
    for (let paso = N >> 1; paso >= 1; paso >>= 1)
      for (let i = paso; i < N; i += paso) if (orden.indexOf(i) < 0) orden.push(i);
    for (const i of orden) { await cargar(i); if (i === actual) mostrar(actual); }
    el.dataset.listo = "1";
  })();

  /* ── arrastre ─────────────────────────────────────────────────────── */
  if (opc.arrastrable !== false) {
    let arrastrando = false, x0 = 0, cuadro0 = 0, vel = 0, ultimoX = 0, ultimoT = 0, raf = 0;

    const sensibilidad = () => Math.max(el.clientWidth, 260) * 1.15 / N; // px por cuadro

    el.addEventListener("pointerdown", (e) => {
      arrastrando = true; x0 = ultimoX = e.clientX; cuadro0 = actual;
      ultimoT = performance.now(); vel = 0;
      if (raf) { cancelAnimationFrame(raf); raf = 0; }
      el.setPointerCapture(e.pointerId);
      el.classList.add("usada");
    });

    el.addEventListener("pointermove", (e) => {
      if (!arrastrando) return;
      // arrastrar a la derecha gira el vial como si lo empujaras con el pulgar
      mostrar(cuadro0 - Math.round((e.clientX - x0) / sensibilidad()));
      const ahora = performance.now(), dt = ahora - ultimoT;
      if (dt > 8) { vel = (e.clientX - ultimoX) / dt; ultimoX = e.clientX; ultimoT = ahora; }
    });

    function soltar() {
      if (!arrastrando) return;
      arrastrando = false;
      if (quieto || Math.abs(vel) < 0.12) return;
      // inercia: sigue girando y se frena, como un objeto real
      let v = vel;
      const s = sensibilidad();
      let resto = 0;
      (function frenar() {
        resto += v * 16;
        const saltos = Math.trunc(resto / s);
        if (saltos) { mostrar(actual - saltos); resto -= saltos * s; }
        v *= 0.94;
        raf = Math.abs(v) > 0.02 ? requestAnimationFrame(frenar) : 0;
      })();
    }
    el.addEventListener("pointerup", soltar);
    el.addEventListener("pointercancel", soltar);

    /* teclado: el visor es una imagen que se explora, debe poder recorrerse */
    el.tabIndex = 0;
    el.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { mostrar(actual + 1); e.preventDefault(); }
      if (e.key === "ArrowLeft")  { mostrar(actual - 1); e.preventDefault(); }
    });
  }

  return {
    aCuadro: mostrar,
    aProgreso(p) { mostrar(Math.round(p * (N - 1))); },
    cuadroActual() { return actual; },
  };
};
