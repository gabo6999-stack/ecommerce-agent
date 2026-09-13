# Mocks de producto

## `vial-retatrutida-3d.png` — el bueno

Render con three.js y material de vidrio físico (`MeshPhysicalMaterial` con
`transmission`, `ior` 1.52, atenuación). Se genera con `generar-vial-3d.html`
servido por HTTP y capturado con Chromium headless (SwiftShader, sin GPU:
tarda unos minutos).

Lo que hace que lea como vidrio y no como plástico:

- **Pared modelada de verdad.** El cuerpo es un `LatheGeometry` cuyo perfil sube
  por fuera, cruza el borde y baja por dentro: 1.1 mm de pared y 2.6 mm de fondo.
  Con un cilindro macizo no hay refracción que valga.
- **Entorno.** `RoomEnvironment` por PMREM. Sin algo que reflejar, el vidrio sale
  muerto por muy bueno que sea el material.
- **Cartulina de rebote** detrás del vial, con los cantos fundidos en alfa. Es lo
  que hace un fotógrafo: sin ella el hombro sale negro con brillos de plástico.
- **Tone mapping neutro de Khronos**, no ACES. ACES desatura y te cambia el
  magenta de marca; el neutro respeta el tono.
- Sin suelo: un plano iluminado por el entorno sale gris y parte el encuadre. En
  su lugar, charco de sombra con alfa.

Etiqueta envuelta con `thetaLength = 2pi·43/47.5` y `thetaStart = -0.25·arco`,
que deja el bloque de texto de frente.

### Tres fallos que costaron varias vueltas

1. **Costura vertical** partiendo la tapa y el hombro: la causaba llamar
   `computeVertexNormals()` sobre las geometrías torneadas. `LatheGeometry` ya
   resuelve el empalme y esa llamada lo rompe. Se quitó.
2. **Vial demasiado corto.** Con 35 mm de alto, una etiqueta de 22 mm se comía
   toda la pared recta y quedaba pegada a la base. El vial pasa a 39 mm (5 ml),
   con 27 mm de pared recta: sobran 3 mm de vidrio abajo y 2 arriba.
3. **Fondo oscuro.** El vidrio transparente sobre negro lee negro, por
   definición: no hay nada que transmitir. Las fotos de la competencia están
   sobre blanco, y por eso su vidrio se ve limpio. El estudio pasó a claro y con
   eso desapareció el aspecto de plástico negro.

### La tapa

Anatomía real de un sello flip-off, que la primera versión tenía mal: corona
plana de aluminio con hueco central, falda con estrías finas (por `roughnessMap`,
no por geometría) y rizo por debajo de la pestaña de vidrio. El botón de plástico es **ancho y de tapa plana**, no una cúpula estrecha:
**sobresale** sobre el engaste: radio 7.39, el 110 % del sello (6.72), apoyado
encima de la corona. Cualquier cosa por debajo del 100 % se lee como botón
hundido y delata el render.

El aluminio va **liso**, sin estrías verticales: el `roughnessMap` de estriado
se quitó y la falda se resuelve solo con el torneado y la rugosidad baja (0.19),
que da el degradado horizontal de metal pulido. Comprobado
contra foto de un flip-off real.

El canto del botón se redondea con **siete puntos de perfil**, no con dos: con
menos, la silueta se ve facetada al ampliar, que es lo que se lee como
«pixeleado». Los torneados del sello y del botón van a 320 segmentos radiales,
y el render sale a 2000 × 2880 para que aguante el zoom.

**La cámara tiene que ir por encima del sello** (y 43 contra los 37.3 de la tapa).
Por debajo se ve el engaste desde abajo y el botón desaparece tras el borde: eso,
y no el modelado, era lo que hacía que la tapa se viera rara.

### Lo que este render todavía no da

No hay cáusticas, ni profundidad de campo, ni polvo o microrrayas en el vidrio, y
la torta liofilizada lee como banda crema, no como polvo granular. **Para catálogo
conviene fotografiar los viales reales**: ya tienes producto y etiquetas impresas,
y es lo que hace la competencia.

## `vial-retatrutida.png` — primera versión, en canvas 2D
Render de vial 2R (ISO 8362-1, 15 × 38 mm) con la etiqueta de 43 × 22 mm
envuelta por proyección cilíndrica real: cada columna de píxeles se muestrea
en `u = u0 + asin(x/R) · C/(2π·Lw)`, no con una deformación aproximada.

Se genera con `node generar-vial.js` (necesita `playwright-core` y el
`label_hi.png` renderizado del PDF de etiquetas a 900 dpi).

Parámetro a tocar: `u0 = .235` decide qué tramo de la etiqueta queda al frente.

## `etiquetas/` — los dos PDF con la errata corregida
Decían **"*Vial lofolizado"**; debe decir **"*Vial liofilizado"**. Afectaba a
**14 de las 15 etiquetas** (la de agua bacteriostática no lleva esa línea).

La palabra se recompone con la propia Optima-Regular incrustada en el PDF
original, al mismo cuerpo y en el mismo origen, así que es indistinguible del
resto de la etiqueta.

**Importante:** no basta con tapar la errata con un rectángulo blanco — así el
texto viejo sigue en la capa de texto del PDF y aparece en cualquier búsqueda o
preflight. Aquí se elimina de verdad con `apply_redactions`, conservando el
dibujo vectorial (`PDF_REDACT_LINE_ART_NONE`). Verificado: cero apariciones de
"lofolizado" en los dos archivos.

## `viales/` — los 15 renders

Uno por etiqueta. Se generan en lote con `generar-vial-3d.html` más `lote.js`:
la escena se construye una sola vez (PMREM y torneados son lo caro) y cada
producto solo cambia la textura de la etiqueta vía `window.__vial(url, conTorta)`.

El agua bacteriostática se renderiza **sin torta liofilizada**: es una solución,
no un liofilizado, y dibujarle polvo blanco sería un error de producto.

Cada etiqueta se gira lo que le toca. El título no está en el mismo sitio en
todas: va de u = 0.136 (Selank) a u = 0.340 (agua bacteriostática). `catalogo.json`
guarda ese `u0` por producto, calculado del centro del bloque en negrita, con un
suelo de 0.25 porque por debajo se asoma la costura por el canto izquierdo.

## Tres hallazgos de los archivos de imprenta

1. **La errata `lofolizado`** en 14 de las 15 etiquetas. Corregida.
2. **Las bandas de "Solo para investigación" usan 13 tonos distintos** entre los
   15 archivos: `#02f6c8`, `#bdfff2`, `#04bc99`, `#ff6ea9`, `#ffb6de`, `#ffdef1`,
   `#c40062`, `#ff8fca`, `#5fedd2`, `#008e73`, `#9cdbcf`, `#d8efea`, `#ff50ac`.
   Para una línea de producto es mucha variación; conviene decidir si es
   deliberado (código por familia) o deriva de archivo en archivo.
3. **Tres etiquetas tienen el bloque de texto demasiado ancho para el vial**:
   agua bacteriostática, CJC-1295 NO DAC + IPAMORELIN y BPC-157 + TB500. Su
   texto ocupa más de 150° de arco sobre un perímetro de 50 mm, así que los
   extremos caen en el canto y no se leen de frente. No es fallo del render: en
   el vial físico pasa igual. Se arregla con tipografía más chica, bloque más
   estrecho, o vial de mayor diámetro — el agua bacteriostática de hecho suele
   ir en vial de 10 ml, donde el mismo texto sí entraría holgado.

## Colores de marca, tomados de los PDF de imprenta
No son aproximación: son los valores vectoriales del archivo.

| Color | Hex | Uso en la etiqueta |
|---|---|---|
| Magenta | `#FF047E` | Nombre, chip de pureza, hexágono, monograma. **Solo en la etiqueta**: el flip-off va blanco satinado, como el de la competencia |
| Aqua | `#02F6C8` | Banda de "Solo para investigación" |
| Negro | `#161616` | Texto |

Tipografía: **Optima** (Regular, Bold, Italic).

## Hallazgo de diseño
El monograma P&S vive en el extremo derecho de una etiqueta de 43 mm sobre un
vial de 47 mm de perímetro: al envolverse queda en la cara oculta. Si el logo
debe verse de frente junto al nombre del producto, hay que moverlo al bloque
de texto o repetirlo en el otro extremo.
