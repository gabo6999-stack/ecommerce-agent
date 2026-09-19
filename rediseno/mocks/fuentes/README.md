# Optima para el prototipo

Los `.ttf` y los `.woff2` **no se versionan**: este repo es público y Optima es
una tipografía con licencia. Aquí queda el script que los procesa y el registro
de en qué estado llegaron los archivos.

## Uso

Pon los TTF en este directorio y corre:

```bash
pip install fonttools brotli
python3 construir.py
```

Salida en `rediseno/fonts/`, que es de donde los lee `index.html`.

## Estado de las cuatro caras que llegaron

| Archivo | Estado |
|---|---|
| `Optima_Medium.ttf` | **Buena.** Occidental completa, 233 glifos con contornos, `¿` y `¡` incluidas |
| `Optima_Italic.ttf` | **Buena** tras normalizar. Ver abajo |
| `OPTIMA.TTF` (Regular) | **Inservible.** Repack cirílico |
| `OPTIMA_B.TTF` (Bold) | **Inservible.** Repack cirílico |

### El repack cirílico

La Regular y la Bold conservan los nombres latinos de los glifos —`aacute`,
`ntilde`— pero el dibujo que traen dentro es otra letra:

| Glifo | Debería ser | Lo que trae |
|---|---|---|
| `aacute` | `a` + acento = 3 contornos | 2 contornos hasta la altura de mayúscula: una «б» |
| `ntilde` | `n` + tilde = 2 contornos | 1 contorno con descendente: una «ц» |
| `tilde` | la tilde suelta | vacío, 0 contornos |
| `questiondown` | `¿` | vacío, con avance de 1000 |

En pantalla, «¿Cuánto rinde un vial?» sale «¿Cuбnto rinde un vial?». Son 13
glifos acentuados así en cada una de las dos caras. No hay reparación honesta:
hay que conseguir la Regular y la Bold occidentales.

`construir.py` las detecta y las rechaza en lugar de dejar pasar el error.

### La itálica

Chrome la rechazaba entera. OTS, su sanitizador, devolvía:

```
OTS parsing error: cmap: language id should be zero: 1
```

La subtabla Mac del cmap declara `language=1`. El script descarta las subtablas
que no son Unicode —en web no se usan— y con eso pasa. De paso traía
`usWeightClass=5` e `italicAngle=23853`, que también se normalizan.

### `¿` y `¡` reconstruidas

Para cualquier cara que las tenga mapeadas pero vacías, el script las dibuja
girando 180° la `?` y la `!` de la misma fuente, que es como se dibujan de
origen, y poniendo el tope de la caja en la altura de x. La Medium da la
referencia: su `¿` va de -214 a 483 y su altura de x es 483.

## Lo que falta pedirle al diseñador

1. **Optima Regular y Bold occidentales**, en `.otf`, `.ttf` o `.woff2`. Las
   tiene: los PDF de las etiquetas llevan incrustado un subset occidental de
   Optima con `é` y `ó` bien dibujadas.
2. **La licencia de webfont.** La de escritorio, que es la que se usa en
   Illustrator, no cubre servir la fuente desde un sitio. Monotype la vende
   aparte. Aplica igual para la Medium y la Itálica que ya están montadas.

Mientras tanto la Medium cubre sola el rango 400-700 en `index.html`: un solo
peso para todo, pero limpio, en vez de dejar que el navegador engorde las
negritas por su cuenta.
