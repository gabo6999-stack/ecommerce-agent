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
