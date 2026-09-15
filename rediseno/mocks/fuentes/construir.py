#!/usr/bin/env python3
"""Convierte los TTF de Optima a woff2 para el prototipo, validándolos antes.

De los cuatro archivos que llegaron, dos no sirven. El script los detecta solo
en lugar de dejar que el error salga en la página, que es como se encontró:

1. OPTIMA.TTF y OPTIMA_B.TTF son un repack cirílico. Los nombres de los glifos
   siguen siendo latinos (`aacute`, `ntilde`), pero el dibujo que traen dentro
   es otra letra: la `á` son dos contornos que llegan a la altura de mayúscula
   — es una «б» — y la `ñ` es un solo contorno con descendente, una «ц». En
   pantalla «¿Cuánto rinde un vial?» sale «¿Cuбnto rinde un vial?». Quince
   glifos acentuados están así, y `tilde` viene vacía. No hay reparación
   honesta: hay que conseguir la Regular y la Bold occidentales de verdad.

2. Optima_Italic.ttf la rechazaba el navegador entero. OTS, el sanitizador de
   Chrome, devolvía «cmap: language id should be zero: 1»: la subtabla Mac del
   cmap declara language=1. Se descartan las subtablas que no son Unicode, que
   en web no se usan, y con eso pasa. De paso traía usWeightClass=5 e
   italicAngle=23853, que también se normalizan.

Un tercer arreglo aplica a cualquier cara que lo necesite: si `¿` y `¡` están
mapeadas pero vacías —le pasa a la Regular y la Bold— se reconstruyen rotando
180° la `?` y la `!` de la misma fuente, que es como se dibujan de origen, y
poniendo el tope de la caja en la altura de x. La Medium, que sí las trae, da
la referencia: su `¿` va de -214 a 483 y su altura de x es 483.

Los TTF no se versionan: el repo es público y Optima es una tipografía con
licencia. Pon los archivos en este directorio y corre:

    python3 construir.py

Salida: ../../fonts/*.woff2
"""
import os
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.normpath(os.path.join(AQUI, '..', '..', 'fonts'))

# archivo de entrada -> (nombre de salida, itálica)
CARAS = [
    ('OPTIMA.TTF',        'optima-400.woff2',        False),
    ('Optima_Medium.ttf', 'optima-500.woff2',        False),
    ('OPTIMA_B.TTF',      'optima-700.woff2',        False),
    ('Optima_Italic.ttf', 'optima-400-italic.woff2', True),
]

# acentuado -> base. Un acentuado legítimo lleva el acento encima de la base,
# así que tiene más contornos que ella (o es un glifo compuesto).
ACENTUADOS = {
    'aacute': 'a', 'agrave': 'a', 'adieresis': 'a', 'atilde': 'a',
    'eacute': 'e', 'egrave': 'e', 'ecircumflex': 'e', 'edieresis': 'e',
    'oacute': 'o', 'uacute': 'u', 'udieresis': 'u', 'ntilde': 'n',
    'Aacute': 'A', 'Oacute': 'O', 'Ntilde': 'N', 'Udieresis': 'U',
}


def altura_x(fuente):
    return fuente['glyf'][fuente.getBestCmap()[ord('x')]].yMax


def glifos_suplantados(fuente):
    """Devuelve los acentuados cuyo dibujo no corresponde a la letra."""
    glyf = fuente['glyf']
    malos = []
    for acentuado, base in ACENTUADOS.items():
        try:
            g, b = glyf[acentuado], glyf[base]
        except KeyError:
            continue
        if g.isComposite():
            continue
        if g.numberOfContours <= b.numberOfContours:
            malos.append(acentuado)
    return malos


def limpiar_cmap(fuente):
    """Deja solo subtablas Unicode con language=0, que es lo que acepta OTS."""
    cmap = fuente['cmap']
    antes = len(cmap.tables)
    cmap.tables = [s for s in cmap.tables if s.platformID in (0, 3)]
    for s in cmap.tables:
        s.language = 0
    if not cmap.tables:
        raise SystemExit('cmap sin subtabla Unicode')
    return antes - len(cmap.tables)


def reconstruir_invertidos(fuente):
    """Dibuja ¿ y ¡ girando ? y ! 180°, con el tope en la altura de x."""
    cmap = fuente.getBestCmap()
    glyf, hmtx = fuente['glyf'], fuente['hmtx']
    gs = fuente.getGlyphSet()
    xh = altura_x(fuente)
    hechos = []

    for origen_cp, destino_cp in ((ord('?'), ord('¿')), (ord('!'), ord('¡'))):
        g_origen, g_destino = cmap.get(origen_cp), cmap.get(destino_cp)
        if not g_origen or not g_destino:
            continue
        if glyf[g_destino].numberOfContours:      # ya tiene dibujo, no tocar
            continue
        src = glyf[g_origen]
        # girar 180° = escalar por -1 en ambos ejes; luego recolocar.
        # dx devuelve la caja a su sitio conservando los costados;
        # dy pone el tope del glifo girado en la altura de x.
        dx = src.xMin + src.xMax
        dy = xh + src.yMin
        pluma = TTGlyphPen(gs)
        # el giro invierte el sentido de los contornos: se revierte para
        # dejarlos como espera TrueType.
        src.draw(TransformPen(ReverseContourPen(pluma), (-1, 0, 0, -1, dx, dy)), glyf)
        glyf[g_destino] = pluma.glyph()
        hmtx[g_destino] = hmtx[g_origen]          # mismo avance que ? y !
        hechos.append(chr(destino_cp))
    return hechos


def normalizar_italica(fuente):
    os2, post, head = fuente['OS/2'], fuente['post'], fuente['head']
    arreglos = []
    if not 100 <= os2.usWeightClass <= 1000:
        os2.usWeightClass = 400
        arreglos.append('usWeightClass=400')
    if not -90 < post.italicAngle < 90:
        post.italicAngle = -12.0
        arreglos.append('italicAngle=-12')
    if not head.macStyle & 0b10:
        head.macStyle |= 0b10
        arreglos.append('macStyle italic')
    return arreglos


def main():
    os.makedirs(SALIDA, exist_ok=True)
    construidas, rechazadas = [], []

    for entrada, salida, es_italica in CARAS:
        origen = os.path.join(AQUI, entrada)
        if not os.path.exists(origen):
            print('%-22s ausente, se omite' % entrada)
            continue

        f = TTFont(origen)

        malos = glifos_suplantados(f)
        if malos:
            rechazadas.append((entrada, malos))
            print('%-22s RECHAZADA — %d acentuados suplantados: %s'
                  % (entrada, len(malos), ' '.join(malos[:6]) + ('…' if len(malos) > 6 else '')))
            continue

        notas = []
        quitadas = limpiar_cmap(f)
        if quitadas:
            notas.append('%d subtabla(s) cmap no Unicode fuera' % quitadas)
        arreglados = reconstruir_invertidos(f)
        if arreglados:
            notas.append('reconstruidos ' + ' '.join(arreglados))
        if es_italica:
            notas += normalizar_italica(f)
        for tabla in ('cvt ', 'fpgm', 'prep', 'kern'):   # hinting y kern viejos
            if tabla in f:
                del f[tabla]

        f.flavor = 'woff2'
        destino = os.path.join(SALIDA, salida)
        f.save(destino)
        construidas.append(salida)
        print('%-22s -> %-24s %5.1f KB  %s'
              % (entrada, salida, os.path.getsize(destino) / 1024,
                 '; '.join(notas) or 'sin cambios'))

    print()
    print('%d cara(s) construida(s): %s' % (len(construidas), ', '.join(construidas)))
    if rechazadas:
        print()
        print('Hay que pedirle al diseñador la Optima occidental de estas caras.')
        print('La que mandó tiene los huecos de los acentuados ocupados por')
        print('cirílico, así que el español sale roto:')
        for entrada, malos in rechazadas:
            print('  - %s (%d glifos)' % (entrada, len(malos)))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
