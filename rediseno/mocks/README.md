# Mocks de producto

## `vial-retatrutida.png`
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
