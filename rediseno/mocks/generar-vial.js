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
    g.translate(cx, base + 8); g.scale(1, 0.12);
    const sh = g.createRadialGradient(0, 0, 10, 0, 0, R * 2.6);
    sh.addColorStop(0, 'rgba(0,0,0,.85)'); sh.addColorStop(.45, 'rgba(0,0,0,.36)'); sh.addColorStop(1, 'rgba(0,0,0,0)');
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

    // ── vidrio: sombreado calculado por columna en vez de degradados a ojo.
    // cos(theta) da el grosor óptico (mas camino = mas tinte) y el Fresnel
    // (1-cos)^3 da el filo brillante del canto, que es lo que lee como vidrio.
    g.save(); g.clip(cuerpo);
    const bgCol = [10, 20, 17];         // el fondo que se ve a través del vial
    const tint = [22, 46, 40];          // vidrio tipo I con tinte verdoso
    const specAng = -0.62;              // llave a la izquierda
    for (let i = 0; i < R * 2; i++) {
      const x = i - R + .5, t = Math.max(-.999, Math.min(.999, x / R));
      const cosT = Math.sqrt(1 - t * t);
      const phi = Math.asin(t);
      const grosor = Math.min(1 / Math.max(cosT, .05), 9) / 9;      // 0..1
      const fres = Math.pow(1 - cosT, 3);
      const spec = Math.pow(Math.max(0, Math.cos((phi - specAng) * 2.6)), 22);
      const spec2 = Math.pow(Math.max(0, Math.cos((phi - 1.02) * 3.1)), 30);
      const c = [0, 1, 2].map(k => {
        let v = bgCol[k] + (tint[k] - bgCol[k]) * Math.pow(grosor, .8);
        v += fres * 190;
        v += spec * 150 + spec2 * 90;
        return Math.round(Math.max(0, Math.min(255, v)));
      });
      g.fillStyle = 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')';
      g.fillRect(cx + x - .5, yAt(38), 1.6, mm(38));
    }

    // torta liofilizada: masa opaca, mate, con el borde superior irregular
    const yCake = yAt(4.6);
    for (let i = 0; i < R * 2; i++) {
      const x = i - R + .5, t = Math.max(-.999, Math.min(.999, x / R));
      const cosT = Math.sqrt(1 - t * t);
      const lam = .16 + .84 * Math.pow(Math.max(0, Math.cos(Math.asin(t) + .42)), 1.8);
      const velo = Math.pow(cosT, .55);                    // el vidrio la apaga en los cantos
      const v = Math.round(Math.max(0, Math.min(255, (196 * lam + 14) * velo + 10)));
      g.fillStyle = 'rgb(' + v + ',' + v + ',' + Math.round(v * .97) + ')';
      g.fillRect(cx + x - .5, yCake, 1.6, base - yCake);
    }
    // canto superior de la torta
    const canto = g.createLinearGradient(0, yCake - mm(.5), 0, yCake + mm(1.1));
    canto.addColorStop(0, 'rgba(0,0,0,.34)'); canto.addColorStop(.45, 'rgba(0,0,0,.16)');
    canto.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = canto; g.fillRect(cx - R, yCake - mm(.5), R * 2, mm(1.6));

    // sombra de contacto de la torta contra el vidrio
    const bajo = g.createLinearGradient(0, base - mm(2), 0, base);
    bajo.addColorStop(0, 'rgba(0,0,0,0)'); bajo.addColorStop(1, 'rgba(0,0,0,.30)');
    g.fillStyle = bajo; g.fillRect(cx - R, base - mm(2), R * 2, mm(2));

    // fondo grueso del vial: concentra luz justo sobre la base
    const fondo = g.createLinearGradient(0, base - mm(3.4), 0, base);
    fondo.addColorStop(0, 'rgba(214,240,234,0)'); fondo.addColorStop(.6, 'rgba(214,240,234,.22)');
    fondo.addColorStop(1, 'rgba(214,240,234,.52)');
    g.fillStyle = fondo; g.fillRect(cx - R, base - mm(3.4), R * 2, mm(3.4));
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
    luz.addColorStop(0, 'rgba(18,26,24,.62)'); luz.addColorStop(.045, 'rgba(18,26,24,.34)');
    luz.addColorStop(.12, 'rgba(0,0,0,.10)'); luz.addColorStop(.30, 'rgba(255,255,255,.05)');
    luz.addColorStop(.46, 'rgba(255,255,255,.07)'); luz.addColorStop(.70, 'rgba(0,0,0,.05)');
    luz.addColorStop(.88, 'rgba(16,24,22,.26)'); luz.addColorStop(1, 'rgba(16,24,22,.58)');
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
    g.beginPath(); g.roundRect(cx - rSeal, ySeal, rSeal * 2, hSeal, [mm(.5), mm(.5), mm(1.1), mm(1.1)]); g.fill();
    // reborde superior del engaste
    g.fillStyle = 'rgba(255,255,255,.30)';
    g.fillRect(cx - rSeal, ySeal, rSeal * 2, mm(.35));
    g.fillStyle = 'rgba(0,0,0,.22)';
    g.fillRect(cx - rSeal, ySeal + mm(.35), rSeal * 2, mm(.18));
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

    g.strokeStyle = 'rgba(226,244,240,.28)'; g.lineWidth = 1.6; g.stroke(cuerpo);

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
