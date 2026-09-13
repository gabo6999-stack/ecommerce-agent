// Mock de vial 2R (ISO 8362-1): D 16 mm, altura 35 mm, etiqueta 43 x 22 mm.
// La etiqueta se envuelve con la proyección cilíndrica real: x = R·sin(phi).
const fs = require('fs');
const { chromium } = require('./node_modules/playwright-core');

const b64 = fs.readFileSync('label_b64.txt', 'utf8');
const html = `<canvas id="c" width="880" height="1290"></canvas>
<img id="lab" src="data:image/png;base64,${b64}">
<style>body{margin:0;background:#000}#lab{display:none}</style>
<script>
window.render = () => new Promise(res => {
  const img = document.getElementById('lab');
  const go = () => {
    const c = document.getElementById('c'), g = c.getContext('2d');
    g.imageSmoothingQuality = 'high';
    const W = c.width, H = c.height;
    const S = 27;                 // px por mm
    const D = 15, R = D * S / 2;  // diámetro del vial
    const CIRC = Math.PI * D;     // 50.27 mm
    const LW = 43, LH = 22;       // etiqueta
    const cx = W / 2, base = 1180;
    const mm = v => v * S;
    const yAt = v => base - mm(v);

    // ── fondo
    const bg = g.createRadialGradient(cx, 560, 60, cx, 620, 900);
    bg.addColorStop(0, '#16302A'); bg.addColorStop(1, '#060C0A');
    g.fillStyle = bg; g.fillRect(0, 0, W, H);

    // ── sombra proyectada
    g.save();
    g.translate(cx, base + 14); g.scale(1, 0.17);
    const sh = g.createRadialGradient(0, 0, 10, 0, 0, R * 2.6);
    sh.addColorStop(0, 'rgba(0,0,0,.72)'); sh.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = sh; g.beginPath(); g.arc(0, 0, R * 2.6, 0, 7); g.fill();
    g.restore();

    // ── silueta del vidrio: cuerpo 26 mm, hombro 4 mm, cuello 3.5 mm, pestaña 1.5 mm
    const rNeck = mm(4.6), yBody = yAt(29), yNeck = yAt(33), yFlan = yAt(36.4), yTop = yAt(38);
    const cuerpo = new Path2D();
    cuerpo.moveTo(cx - R, base); cuerpo.lineTo(cx - R, yBody);
    cuerpo.bezierCurveTo(cx - R, yNeck + mm(1.4), cx - rNeck, yBody - mm(1.4), cx - rNeck, yNeck);
    cuerpo.lineTo(cx - rNeck, yFlan);
    cuerpo.lineTo(cx - rNeck - mm(.6), yFlan); cuerpo.lineTo(cx - rNeck - mm(.6), yTop);
    cuerpo.lineTo(cx + rNeck + mm(.6), yTop); cuerpo.lineTo(cx + rNeck + mm(.6), yFlan);
    cuerpo.lineTo(cx + rNeck, yFlan); cuerpo.lineTo(cx + rNeck, yNeck);
    cuerpo.bezierCurveTo(cx + rNeck, yBody - mm(1.4), cx + R, yNeck + mm(1.4), cx + R, yBody);
    cuerpo.lineTo(cx + R, base); cuerpo.closePath();

    g.save(); g.clip(cuerpo);
    const vidrio = g.createLinearGradient(cx - R, 0, cx + R, 0);
    vidrio.addColorStop(0, '#93B2AB'); vidrio.addColorStop(.05, '#2C433D');
    vidrio.addColorStop(.16, '#101C19'); vidrio.addColorStop(.5, '#0A1412');
    vidrio.addColorStop(.84, '#13201C'); vidrio.addColorStop(.95, '#3A534C');
    vidrio.addColorStop(1, '#8AA9A2');
    g.fillStyle = vidrio; g.fill(cuerpo);

    // torta liofilizada en el fondo
    const yCake = yAt(6.2);
    const cake = g.createLinearGradient(cx - R, 0, cx + R, 0);
    cake.addColorStop(0, '#8E9B96'); cake.addColorStop(.22, '#EDF1EC');
    cake.addColorStop(.55, '#FBFCF9'); cake.addColorStop(.82, '#D2D9D3'); cake.addColorStop(1, '#7F8C87');
    g.fillStyle = cake;
    g.beginPath();
    g.moveTo(cx - R + 3, base - 4);
    g.lineTo(cx - R + 3, yCake + 6);
    g.bezierCurveTo(cx - R * .4, yCake - 7, cx + R * .35, yCake + 9, cx + R - 3, yCake + 2);
    g.lineTo(cx + R - 3, base - 4); g.closePath(); g.fill();
    g.fillStyle = 'rgba(0,0,0,.12)';
    g.fillRect(cx - R, base - 10, R * 2, 10);
    // pared trasera vista a través del vidrio
    g.strokeStyle = 'rgba(190,220,212,.22)'; g.lineWidth = 2;
    g.beginPath(); g.ellipse(cx, base - mm(1.2), R * .88, mm(1.6), 0, 0, Math.PI); g.stroke();
    g.restore();

    // ── etiqueta envuelta: para cada columna, phi = asin(x/R) y u = 0.5 + phi·CIRC/(2pi·LW)
    const yLab = yAt(27.5), hLab = mm(LH);
    const k = CIRC / (2 * Math.PI * LW);   // u0 = .30: centra el bloque de texto en la cara visible
    g.save();
    g.beginPath(); g.rect(cx - R, yLab, R * 2, hLab); g.clip();
    for (let i = 0; i < R * 2; i++) {
      const x = i - R + .5, t = Math.max(-.9995, Math.min(.9995, x / R));
      const phi = Math.asin(t);
      const u = .235 + phi * k;
      const du = k / (R * Math.sqrt(1 - t * t));      // ancho de fuente por px de destino
      const sx = u * img.naturalWidth;
      const sw = Math.max(.6, Math.min(du * img.naturalWidth, img.naturalWidth));
      if (u < 0 || u > 1) continue;
      g.drawImage(img, sx - sw / 2, 0, sw, img.naturalHeight, cx + x - .5, yLab, 1.6, hLab);
    }
    // luz cilíndrica sobre la etiqueta
    const luz = g.createLinearGradient(cx - R, 0, cx + R, 0);
    luz.addColorStop(0, 'rgba(0,0,0,.55)'); luz.addColorStop(.10, 'rgba(0,0,0,.28)');
    luz.addColorStop(.30, 'rgba(255,255,255,.10)'); luz.addColorStop(.42, 'rgba(255,255,255,.16)');
    luz.addColorStop(.62, 'rgba(0,0,0,.02)'); luz.addColorStop(.86, 'rgba(0,0,0,.30)');
    luz.addColorStop(1, 'rgba(0,0,0,.60)');
    g.fillStyle = luz; g.fillRect(cx - R, yLab, R * 2, hLab);
    const vert = g.createLinearGradient(0, yLab, 0, yLab + hLab);
    vert.addColorStop(0, 'rgba(0,0,0,.14)'); vert.addColorStop(.18, 'rgba(0,0,0,0)');
    vert.addColorStop(.86, 'rgba(0,0,0,0)'); vert.addColorStop(1, 'rgba(0,0,0,.16)');
    g.fillStyle = vert; g.fillRect(cx - R, yLab, R * 2, hLab);
    g.restore();

    // ── tapón de bromobutilo bajo el sello
    g.save(); g.clip(cuerpo);
    const tap = g.createLinearGradient(cx - rNeck, 0, cx + rNeck, 0);
    tap.addColorStop(0, '#2A2A2C'); tap.addColorStop(.35, '#55565A'); tap.addColorStop(1, '#232326');
    g.fillStyle = tap; g.fillRect(cx - rNeck, yAt(37.2), rNeck * 2, mm(4.4));
    g.restore();

    // ── sello de aluminio
    const ySeal = yAt(38.1), hSeal = mm(5.0), rSeal = rNeck + mm(.85);
    const alu = g.createLinearGradient(cx - rSeal, 0, cx + rSeal, 0);
    alu.addColorStop(0, '#6E7476'); alu.addColorStop(.16, '#C9D0D2'); alu.addColorStop(.34, '#F2F5F6');
    alu.addColorStop(.55, '#AEB6B8'); alu.addColorStop(.78, '#7C8386'); alu.addColorStop(1, '#565C5E');
    g.fillStyle = alu;
    g.beginPath(); g.roundRect(cx - rSeal, ySeal, rSeal * 2, hSeal, [mm(.8), mm(.8), mm(.5), mm(.5)]); g.fill();
    g.strokeStyle = 'rgba(0,0,0,.22)'; g.lineWidth = 1.3;
    for (let i = 1; i < 30; i++) {
      const px = cx - rSeal + (rSeal * 2) * (i / 30);
      g.beginPath(); g.moveTo(px, ySeal + hSeal * .52); g.lineTo(px, ySeal + hSeal * .97); g.stroke();
    }
    g.fillStyle = 'rgba(0,0,0,.18)';
    g.fillRect(cx - rSeal, ySeal + hSeal * .46, rSeal * 2, 2.4);

    // ── flip-off magenta de marca
    const rFlip = rNeck - mm(.75), yFlip = ySeal - mm(1.6);
    const fl = g.createLinearGradient(cx - rFlip, 0, cx + rFlip, 0);
    fl.addColorStop(0, '#8E0044'); fl.addColorStop(.2, '#FF047E');
    fl.addColorStop(.45, '#FF61A9'); fl.addColorStop(.75, '#E5006F'); fl.addColorStop(1, '#7C003C');
    g.fillStyle = fl;
    g.beginPath(); g.roundRect(cx - rFlip, yFlip, rFlip * 2, mm(2.0), [mm(.7), mm(.7), 0, 0]); g.fill();
    g.save(); g.translate(cx, yFlip + 2); g.scale(1, .22);
    g.fillStyle = '#FF6FB0'; g.beginPath(); g.arc(0, 0, rFlip, 0, 7); g.fill();
    g.fillStyle = 'rgba(255,255,255,.30)'; g.beginPath(); g.arc(-rFlip * .22, -rFlip * .1, rFlip * .52, 0, 7); g.fill();
    g.restore();

    // ── brillos del vidrio por encima de todo
    g.save(); g.clip(cuerpo);
    const b1 = g.createLinearGradient(cx - R * .82, 0, cx - R * .52, 0);
    b1.addColorStop(0, 'rgba(255,255,255,0)'); b1.addColorStop(.5, 'rgba(255,255,255,.30)');
    b1.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = b1; g.fillRect(cx - R * .82, yAt(37), R * .30, mm(37));
    const b2 = g.createLinearGradient(cx + R * .56, 0, cx + R * .82, 0);
    b2.addColorStop(0, 'rgba(255,255,255,0)'); b2.addColorStop(.5, 'rgba(255,255,255,.16)');
    b2.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = b2; g.fillRect(cx + R * .56, yAt(37), R * .26, mm(37));
    g.restore();
    g.strokeStyle = 'rgba(255,255,255,.16)'; g.lineWidth = 1.5; g.stroke(cuerpo);

    // ── reflejo en la superficie
    g.save();
    g.globalAlpha = .17; g.translate(0, base * 2 + 10); g.scale(1, -1);
    g.filter = 'blur(2px)'; g.drawImage(c, 0, 0);
    g.restore();
    const fade = g.createLinearGradient(0, base, 0, base + mm(11));
    fade.addColorStop(0, 'rgba(6,12,10,0)'); fade.addColorStop(1, '#060C0A');
    g.fillStyle = fade; g.fillRect(0, base, W, mm(13));
    res(true);
  };
  img.complete ? go() : img.onload = go;
});
</script>`;

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 880, height: 1290 }, deviceScaleFactor: 2 });
  p.on('pageerror', e => console.log('ERROR:', String(e).slice(0, 160)));
  await p.setContent(html);
  await p.evaluate(() => window.render());
  await p.locator('#c').screenshot({ path: 'vial-retatrutida.png' });
  console.log('vial-retatrutida.png listo');
  await b.close();
})();
