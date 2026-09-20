"""
Crea renders de vial para productos que no lo tienen.

No dibuja un vial nuevo: toma uno existente, DESENVUELVE su etiqueta del
cilindro a un plano, sustituye ahí el nombre y el gramaje, y la vuelve a
envolver. Así el frasco, el tapón, la luz, la sombra, el hexágono y todo el
bloque legal son literalmente los del original — lo único nuevo son dos
líneas de texto.
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, sys
sys.path.insert(0, "vial")
from warp import desenvolver, envolver

SRC   = r"C:/Users/gabom/Proyectos/ecommerce-agent/rediseno/home-2026/assets/img"
BASE  = f"{SRC}/vial-sermorelin-10-mg.jpg"      # nombre corto: poco que borrar
FUENTE = "C:/Windows/Fonts/ARIALNB.TTF"   # Arial Narrow Bold: a igual altura da 270 px
                                          # contra los 266 del original

# medidas tomadas del plano del original
X_TEXTO   = 36
BASE_NOM  = 117        # línea base del nombre
BASE_DOS  = 154        # línea base del gramaje
ANCHO_MAX = 330        # hasta donde se puede escribir sin tocar el hexágono        # hasta donde llega "RETATRUTIDA" sin comerse el hexágono
BORRA     = (58, 166)  # franja a reconstruir
X_BORRA   = (18, 370)  # el hexágono empieza en 377 y su parte sombreada
                       # no se detecta por color: mejor no tocar esa mitad
LIMPIO_A  = (38, 57)   # filas limpias encima
LIMPIO_B  = (168, 190) # filas limpias debajo

def _tam_para_alto(alto_obj, ref="Hl"):
    """Tamaño cuya altura de ascendente sea `alto_obj`.

    Se mide sobre una referencia fija y NO sobre el texto real: si el nombre
    lleva 'g' o 'y', su caja de tinta incluye el descendente y la letra saldría
    mucho más chica que en los demás viales."""
    lo, hi = 10, 200
    while lo < hi:
        m = (lo+hi+1)//2
        b = ImageFont.truetype(FUENTE, m).getbbox(ref)
        if (b[3]-b[1]) <= alto_obj: lo = m
        else: hi = m-1
    return lo

def _ancho(f, t):
    b = f.getbbox(t); return b[2]-b[0]

def _placa(plano):
    """Reconstruye el fondo blanco de la etiqueta en la franja del nombre.

    Interpola entre las filas limpias de encima y las de debajo, así conserva
    el sombreado del cilindro, que no es plano. El hexágono magenta cruza esa
    misma franja por la derecha, de modo que la reconstrucción se aplica solo
    donde NO hay magenta: si no, se le come el trazo."""
    a = np.asarray(plano).astype(float).copy()
    arriba = np.median(a[LIMPIO_A[0]:LIMPIO_A[1]], axis=0)
    abajo  = np.median(a[LIMPIO_B[0]:LIMPIO_B[1]], axis=0)
    y0, y1 = BORRA
    t = np.linspace(0, 1, y1-y0)[:, None, None]
    fondo = arriba[None]*(1-t) + abajo[None]*t

    tira = a[y0:y1]
    r, g, b = tira[...,0], tira[...,1], tira[...,2]
    magenta = (r > 150) & ((r-g) > 35)
    # ensancha 2 px para no dejar el borde antialiaseado del trazo
    m = magenta.copy()
    for dx in (-2,-1,1,2):
        m |= np.roll(magenta, dx, axis=1)
    for dy in (-2,-1,1,2):
        m |= np.roll(magenta, dy, axis=0)

    x0, x1 = X_BORRA
    zona = np.zeros(tira.shape[:2], bool); zona[:, x0:x1] = True
    a[y0:y1] = np.where((m | ~zona)[...,None], tira, fondo)
    return Image.fromarray(a.clip(0,255).astype(np.uint8))

def genera(nombre, dosis, salida, base=BASE):
    src = Image.open(base)
    plano = _placa(desenvolver(src))
    d = ImageDraw.Draw(plano)

    # nombre: misma altura que en los demás viales, encogido solo si no cabe
    tam = _tam_para_alto(45)   # 45 -> 63 px, el ancho que da el original
    f = ImageFont.truetype(FUENTE, tam)
    while _ancho(f, nombre) > ANCHO_MAX and tam > 24:
        tam -= 1; f = ImageFont.truetype(FUENTE, tam)
    d.text((X_TEXTO, BASE_NOM), nombre, font=f, fill=(33,33,33), anchor="ls")

    if dosis:
        fd = ImageFont.truetype(FUENTE, _tam_para_alto(24, "H"))
        d.text((X_TEXTO, BASE_DOS), dosis, font=fd, fill=(33,33,33), anchor="ls")

    envolver(plano, src).save(salida, quality=92)
    print(f"  {salida} <- {nombre!r} tam {tam} ancho {_ancho(f, nombre)} / {dosis or chr(8212)}")

if __name__ == "__main__":
    genera("Sermorelin", "10 MG", "vial/prueba-sermorelin.jpg")   # control
    for n, dz, f in [("Glutatión","1500 MG","vial/vial-glutation-1500-mg.jpg"),
                     ("Cagrilintida","10 MG","vial/vial-cagrilintida-10-mg.jpg"),
                     ("Thymosin Alpha-1","10 MG","vial/vial-thymosin-alpha-1-10-mg.jpg"),
                     ("BPC-157", None, "vial/vial-bpc-157.jpg")]:
        genera(n, dz, f)
