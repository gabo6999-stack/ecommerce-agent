#!/usr/bin/env python3
"""RUNDOWN PYS — marcador único para medir si la optimización funciona.

Un solo comando: mide la posición actual de cada ficha optimizada contra su
línea base y dice si el plan va bien, va mal o aún no se puede saber.

    py -3 scripts/rundown_pys.py           # mide y compara
    py -3 scripts/rundown_pys.py --seco    # solo muestra el estado, sin gastar API

Costo: ~$0.02 por ficha (SERP en vivo, profundidad 100).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import sys
from urllib.parse import urlparse

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
DATA = REPO / "docs" / "data"
BASE = DATA / "rundown-pys-baseline.json"
HIST = DATA / "rundown-pys-historial.json"

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

base = json.load(open(BASE, encoding="utf-8"))
hist = json.load(open(HIST, encoding="utf-8")) if HIST.exists() else []
seco = "--seco" in sys.argv
hoy = dt.date.today()


def semanas(desde: str) -> int:
    d = dt.date.fromisoformat(desde)
    return (hoy - d).days // 7


def medir(kw):
    from dataforseo_client import DataForSEOClient
    c = medir.cliente
    items = c._post("/v3/serp/google/organic/live/advanced", {
        "keyword": kw, "location_code": 2484, "language_code": "es",
        "device": "desktop", "depth": 100})
    org = [i for i in items if i.get("type") == "organic"]
    pys = exo = None
    for i in org:
        host = (urlparse(i.get("url") or "").netloc or "").replace("www.", "")
        if "peptidosysuplementos" in host and pys is None:
            pys = i.get("rank_absolute")
        if "exomapeptides" in host and exo is None:
            exo = i.get("rank_absolute")
    return pys, exo, len(org)


if not seco:
    from dataforseo_client import DataForSEOClient
    medir.cliente = DataForSEOClient()

print("=" * 92)
print(f"RUNDOWN PYS — {hoy}")
print("=" * 92)

filas = []
for f in base["fichas"]:
    sem = semanas(f["optimizada_el"])
    antes = f["antes"]["posicion"]
    if seco:
        ahora = exo = None
    else:
        ahora, exo, prof = medir(f["keyword"])

    # regla de lectura
    if sem < 4:
        lectura = "MUY PRONTO (Google no ha reprocesado)"
    elif ahora is None:
        lectura = "sin entrar al top-100"
    elif antes is None:
        lectura = f"entró en {ahora}"
    elif ahora < antes - 10:
        lectura = f"MEJORA +{antes - ahora} posiciones"
    elif ahora > antes + 10:
        lectura = f"EMPEORA -{ahora - antes} posiciones"
    else:
        lectura = "sin cambio significativo"

    filas.append({"id": f["id"], "keyword": f["keyword"], "semanas": sem,
                  "antes": antes, "ahora": ahora, "exoma": exo, "lectura": lectura})
    print(f"\n[{f['id']}] '{f['keyword']}'  ({f['volumen']}/mes)   optimizada hace {sem} semana(s)")
    print(f"   palabras: {f['antes']['palabras']} -> {f['despues']['palabras']}"
          f"   (exoma {f['competidor']['palabras']})")
    print(f"   posición: {antes} -> {ahora if ahora else 'fuera del top-100'}"
          f"   | exoma: {exo if exo else f['competidor']['posicion']}")
    print(f"   >>> {lectura}")

print("\n" + "=" * 92)
en_top10 = sum(1 for f in filas if f["ahora"] and f["ahora"] <= 10)
en_top20 = sum(1 for f in filas if f["ahora"] and f["ahora"] <= 20)
g = base["medicion_global_inicial"]
print(f"MARCADOR:  top-10 {en_top10}  (inicial {g['top10']})   |   "
      f"top-20 {en_top20}  (inicial {g['top20']})")

maduras = [f for f in filas if f["semanas"] >= 8]
if maduras:
    mejoraron = [f for f in maduras if "MEJORA" in f["lectura"]]
    print(f"\nFichas con 8+ semanas: {len(maduras)} | mejoraron: {len(mejoraron)}")
    if len(mejoraron) >= len(maduras) * 0.5:
        print("VEREDICTO: el diagnóstico (contenido + H1) se confirma. Seguir con el resto.")
    else:
        print("VEREDICTO: on-page NO alcanza. El cuello de botella es autoridad de dominio")
        print("           -> pasar a la estrategia de enlaces antes de seguir reescribiendo.")
else:
    print("\nAún no hay fichas con 8 semanas. Volver a correr entonces; antes no decide nada.")

if not seco:
    hist.append({"fecha": str(hoy), "filas": filas})
    json.dump(hist, open(HIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\ncosto de esta corrida: ${medir.cliente.total_cost:.4f}")
    print(f"historial -> {HIST}")
