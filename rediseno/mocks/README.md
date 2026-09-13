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
va **a ras del engaste**: radio 6.55 sobre un sello de 6.72, apoyado sobre la
corona, dejando solo un filo de aluminio a la vista. A 5.6 se veía notoriamente
más angosto que el aluminio, que es el fallo que delataba el render. Comprobado
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

## `etiqueta_reta_corregida.pdf`
La etiqueta original de Retatrutida con la errata corregida:
decía **"*Vial lofolizado"**, debe decir **"*Vial liofilizado"**. La palabra se
recompuso con la propia Optima-Regular incrustada en el PDF original, al mismo
cuerpo (4 pt) y en el mismo origen (6.83, 38.95), así que es indistinguible
del resto de la etiqueta.

**La errata está en las 15 etiquetas de los dos PDF**, no solo en esta.

## Colores de marca, tomados de los PDF de imprenta
No son aproximación: son los valores vectoriales del archivo.

| Color | Hex | Uso en la etiqueta |
|---|---|---|
| Magenta | `#FF047E` | Nombre, chip de pureza, hexágono, monograma |
| Aqua | `#02F6C8` | Banda de "Solo para investigación" |
| Negro | `#161616` | Texto |

Tipografía: **Optima** (Regular, Bold, Italic).

## Hallazgo de diseño
El monograma P&S vive en el extremo derecho de una etiqueta de 43 mm sobre un
vial de 47 mm de perímetro: al envolverse queda en la cara oculta. Si el logo
debe verse de frente junto al nombre del producto, hay que moverlo al bloque
de texto o repetirlo en el otro extremo.
