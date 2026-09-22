"""
Revisión VISUAL de las capturas de verificar.py.

Una captura de página entera mide 5.000-9.000 px de alto; al abrirla de golpe se
reduce tanto que no se ve nada (así se escapó el listado duplicado del blog).
Esto la corta en tiras legibles y arma el antes/después lado a lado.

Uso:
  py -3.11 revisar.py tiras <etiqueta> [<slug>] [--alto 1400]
      -> verificacion/<etiqueta>/tiras/<slug>__<vista>__01.jpg ...
  py -3.11 revisar.py lado <etiqueta_antes> <etiqueta_despues> <slug> [escritorio|movil]
      -> verificacion/<slug>__<vista>__antes-vs-despues__NN.jpg (en tiras)
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent / "verificacion"


def tiras(img, alto):
    for i, y in enumerate(range(0, img.height, alto), 1):
        yield i, img.crop((0, y, img.width, min(y + alto, img.height)))


def cmd_tiras(etiqueta, slug=None, alto=1400):
    d = RAIZ / etiqueta
    out = d / "tiras"
    out.mkdir(exist_ok=True)
    n = 0
    for jpg in sorted(d.glob("*__*.jpg")):
        if slug and not jpg.name.startswith(slug + "__"):
            continue
        img = Image.open(jpg).convert("RGB")
        h = alto
        for i, t in tiras(img, h):
            t.save(out / f"{jpg.stem}__{i:02d}.jpg", quality=80)
            n += 1
    print(f"{n} tiras en {out}")


def cmd_lado(antes, despues, slug, vista="escritorio", alto=1400):
    a = Image.open(RAIZ / antes / f"{slug}__{vista}.jpg").convert("RGB")
    b = Image.open(RAIZ / despues / f"{slug}__{vista}.jpg").convert("RGB")
    if vista != "movil":
        # a media escala para que quepan los dos lado a lado y se sigan leyendo
        a = a.resize((a.width // 2, a.height // 2))
        b = b.resize((b.width // 2, b.height // 2))
        alto //= 2
        alto *= 2
    sep = 16
    lienzo = Image.new("RGB", (a.width + b.width + sep, max(a.height, b.height) + 40), "#ff00aa")
    lienzo.paste(a, (0, 40))
    lienzo.paste(b, (a.width + sep, 40))
    dib = ImageDraw.Draw(lienzo)
    dib.text((10, 12), f"ANTES  {a.height * (2 if vista != 'movil' else 1)} px", fill="white")
    dib.text((a.width + sep + 10, 12), f"DESPUES  {b.height * (2 if vista != 'movil' else 1)} px", fill="white")
    out = RAIZ / "lado-a-lado"
    out.mkdir(exist_ok=True)
    n = 0
    for i, t in tiras(lienzo, alto):
        t.save(out / f"{slug}__{vista}__{i:02d}.jpg", quality=80)
        n += 1
    print(f"{n} tiras en {out} ({slug}__{vista}__NN.jpg)")


if __name__ == "__main__":
    args = sys.argv[1:]
    alto = 1400
    if "--alto" in args:
        k = args.index("--alto")
        alto = int(args[k + 1])
        del args[k:k + 2]
    if not args:
        print(__doc__)
        sys.exit(1)
    if args[0] == "tiras":
        cmd_tiras(args[1], args[2] if len(args) > 2 else None, alto)
    elif args[0] == "lado":
        cmd_lado(args[1], args[2], args[3], args[4] if len(args) > 4 else "escritorio", alto)
    else:
        print(__doc__)
        sys.exit(1)
