"""Convierte un render de vial en foto de producto para WooCommerce.

El sitio tenía dos imágenes por producto que no coincidían: en las tarjetas y el
catálogo, el render 3D del vial; dentro de la ficha, la etiqueta tipográfica
plana (`*-v4.png`). Este script compone la versión que faltaba: el mismo render,
en el formato cuadrado de 1080x1080 que usan las fotos de producto.

El fondo se toma del propio render (esquina superior izquierda) para que el
recuadro no se note, y el vial ocupa el 90 % de la altura, que es la proporción
con la que se compusieron las 18 del 2026-09-23.

    python vial-a-foto-de-producto.py vial-bpc-157.jpg [salida.jpg]

Los renders viven en wp-content/uploads/home-2026/img/ y el mapa de qué render
le toca a cada producto está en mu-plugins/pys-diseno/partes.php, en
`pys_dis_vial()`: ese mapa manda, para que la ficha y la tarjeta no diverjan.

Aviso: el render del agua bacteriostática tiene la etiqueta cortada de origen
(«AGUA» y «BACTERIOSTÁTICA» pierden su primera letra). Esa ficha se dejó con su
imagen anterior a propósito hasta que el render se regenere.
"""
import sys
from pathlib import Path

from PIL import Image

LADO = 1080
OCUPACION = 0.90


def componer(origen: Path, destino: Path) -> None:
    v = Image.open(origen).convert("RGB")
    lienzo = Image.new("RGB", (LADO, LADO), v.getpixel((4, 4)))
    alto = int(LADO * OCUPACION)
    ancho = max(1, round(v.width * alto / v.height))
    lienzo.paste(v.resize((ancho, alto), Image.LANCZOS), ((LADO - ancho) // 2, (LADO - alto) // 2))
    lienzo.save(destino, quality=90, optimize=True)
    print(f"{origen.name} {v.size} -> {destino.name} {lienzo.size} {destino.stat().st_size // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ent = Path(sys.argv[1])
    sal = Path(sys.argv[2]) if len(sys.argv) > 2 else ent.with_name(ent.stem + "-1080.jpg")
    componer(ent, sal)
