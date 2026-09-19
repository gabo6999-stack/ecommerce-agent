const fs = require('fs');
const { chromium } = require('./node_modules/playwright-core');
const catalogo = JSON.parse(fs.readFileSync('catalogo.json', 'utf8'));

(async () => {
  const b = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const p = await b.newPage({ viewport: { width: 1000, height: 1440 } });
  p.on('pageerror', e => console.log('ERROR:', String(e).slice(0, 160)));
  await p.goto('http://localhost:8731/vial3d.html', { waitUntil: 'load', timeout: 90000 });
  await p.waitForFunction(() => window.__listo === true, { timeout: 300000, polling: 500 });
  console.log('escena lista, arrancando lote de ' + catalogo.length);

  for (let i = 0; i < catalogo.length; i++) {
    const c = catalogo[i];
    const t0 = Date.now();
    await p.evaluate(([u, t, r, e, m]) => window.__vial(u, t, r, e, m),
                     [c.archivo, !c.agua, c.u0, c.escala, c.ml]);
    const salida = 'vial-' + c.archivo.replace(/^label_/, '').replace(/\.png$/, '') + '.png';
    await p.locator('#c').screenshot({ path: salida });
    console.log(`[${i + 1}/${catalogo.length}] ${salida}  (${Math.round((Date.now() - t0) / 1000)}s)`);
  }
  await b.close();
  console.log('LOTE COMPLETO');
})();
