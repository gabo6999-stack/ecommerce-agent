"""Ida y vuelta entre la pantalla y la etiqueta plana del vial."""
from PIL import Image
import numpy as np

CX, R, A = 269.5, 180.0, 34.5
TH0, TH1 = np.radians(-72.0), np.radians(80.0)     # arco visible de la etiqueta
V0, V1   = 380, 980                                 # franja vertical (sin bombeo)
ANCHO    = int(round(R*(TH1-TH0)))                  # longitud de arco -> 1:1 en el centro
ALTO     = V1 - V0

def _muestrea(a, xs, ys):
    """bilineal; a es HxWxC float"""
    h, w = a.shape[:2]
    xs = np.clip(xs, 0, w-1.001); ys = np.clip(ys, 0, h-1.001)
    x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
    fx, fy = (xs-x0)[...,None], (ys-y0)[...,None]
    return (a[y0,x0]*(1-fx)*(1-fy) + a[y0,x0+1]*fx*(1-fy)
          + a[y0+1,x0]*(1-fx)*fy + a[y0+1,x0+1]*fx*fy)

def desenvolver(img):
    a = np.asarray(img.convert("RGB")).astype(float)
    u = (np.arange(ANCHO)+0.5)/ANCHO
    th = TH0 + u*(TH1-TH0)
    xs = CX + R*np.sin(th)
    dy = A*np.cos(th)
    v  = V0 + np.arange(ALTO)
    XS = np.broadcast_to(xs, (ALTO, ANCHO))
    YS = v[:,None] + dy[None,:]
    return Image.fromarray(_muestrea(a, XS, YS).clip(0,255).astype(np.uint8))

def envolver(plano, destino):
    """pega `plano` (la etiqueta plana ya editada) de vuelta sobre `destino`."""
    p = np.asarray(plano.convert("RGB")).astype(float)
    d = np.asarray(destino.convert("RGB")).astype(float).copy()
    h, w = d.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    sen = (xs - CX)/R
    dentro = np.abs(sen) < 1.0
    th = np.arcsin(np.clip(sen, -1, 1))
    u  = (th - TH0)/(TH1 - TH0)
    v  = ys - A*np.cos(th) - V0
    ok = dentro & (u >= 0) & (u < 1) & (v >= 0) & (v < ALTO-1)
    pu, pv = u*ANCHO, v
    vals = _muestrea(p, np.where(ok, pu, 0), np.where(ok, pv, 0))
    d[ok] = vals[ok]
    return Image.fromarray(d.clip(0,255).astype(np.uint8))

if __name__ == "__main__":
    SRC = r"C:/Users/gabom/Proyectos/ecommerce-agent/rediseno/home-2026/assets/img"
    src = Image.open(f"{SRC}/vial-sermorelin-10-mg.jpg")
    plano = desenvolver(src)
    plano.save("vial/plano-sermorelin.png")
    print("plano:", plano.size)
    # prueba de ida y vuelta: re-envolver sin tocar nada debe dar casi lo mismo
    rt = envolver(plano, src)
    dif = np.abs(np.asarray(rt).astype(int) - np.asarray(src.convert("RGB")).astype(int))
    print(f"ida y vuelta -> error medio {dif.mean():.2f}, maximo {dif.max()}")
    rt.save("vial/roundtrip.png")
