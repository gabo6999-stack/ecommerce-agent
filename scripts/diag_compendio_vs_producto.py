#!/usr/bin/env python3
"""¿Conviene doblar (compendio + producto) en TODOS los péptidos, o solo en algunos?

La evidencia: con qué tipo de URL rankea exoma en cada keyword. Si en una query
gana con /producto/, esa query es transaccional y una segunda página propia
canibaliza. Si gana con /compendio/, ahí sí falta la capa informativa.

Sin costo de API (usa los SERPs ya cacheados).
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter
from urllib.parse import urlparse

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "docs" / "data"

serps = json.load(open(DATA / "cluster-pys-serps.json", encoding="utf-8"))
pos = json.load(open(DATA / "cluster-pys-posiciones.json", encoding="utf-8"))
temas = json.load(open(DATA / "cluster-pys-temas.json", encoding="utf-8"))
extra = json.load(open(DATA / "cluster-pys-volumenes.json", encoding="utf-8"))
graf = json.load(open(DATA / "cluster-pys-grafias.json", encoding="utf-8"))

vol = {v["keyword"]: v.get("volume") or 0 for v in temas["limpio"]}
vol.update({k: d["volume"] for k, d in extra.items()})
vol.update(graf)

# ¿PYS tiene el producto? (catálogo verificado en Fase 1)
CATALOGO = {
    "ipamorelina": "combo 2232", "cjc-1295": "combo 2232",
    "cjc 1295 ipamorelin": "combo 2232", "retatrutida": "19",
    "retatrutide precio": "19", "retatrutida precio": "19",
    "agua bacteriostatica": "799", "mots-c": "790/793", "tb-500": "combo 795",
    "bpc 157 precio": "combo 795", "bpc-157 y tb-500": "combo 795",
    "cagrilintida": "2240", "selank": "1699", "sermorelina": "2231",
    "sermorelin": "2231", "glutation": "2234", "glutathione": "2234",
    "thymosin alpha 1": "2230", "igf-1 lr3": "1128", "nad+ inyectable": "1131",
}

INFORMATIVO = ("/compendio/", "/blog/", "wikipedia", "/guia", "/articulo",
               "reddit", "youtube", "quora", "medlineplus", "/que-es")
TRANSACCIONAL = ("/producto/", "/product/", "/shop/", "/tienda/", "/comprar",
                 "mercadolibre", "amazon.")


def tipo_url(u: str) -> str:
    s = (u or "").lower()
    if any(t in s for t in INFORMATIVO):
        return "informativo"
    if any(t in s for t in TRANSACCIONAL):
        return "transaccional"
    return "otro"


print("=" * 100)
print("¿DOBLAR O NO? — evidencia por keyword del catálogo de PYS")
print("=" * 100)
print(f"{'vol/mes':>8}  {'top-10: inf/trans':>18}  {'exoma rankea con':<34} veredicto   keyword")
print("-" * 100)

filas = []
for kw in sorted(set(serps) | set(pos), key=lambda k: -vol.get(k, 0)):
    if kw not in CATALOGO:
        continue
    rows = serps.get(kw) or []
    tipos = Counter(tipo_url(r.get("url")) for r in rows)
    # con qué URL rankea exoma
    exo = None
    for r in rows:
        if "exomapeptides" in (r.get("dominio") or ""):
            path = urlparse(r["url"]).path
            exo = f"{path[:30]} (pos {r['pos']})"
            break
    inf, tra = tipos.get("informativo", 0), tipos.get("transaccional", 0)
    v = vol.get(kw, 0)

    if v < 200:
        vered = "NO doblar"      # no hay volumen que justifique 2 páginas
    elif inf >= tra and inf >= 3:
        vered = "SÍ doblar"      # el SERP premia contenido informativo
    elif tra > inf * 2:
        vered = "solo ficha"     # SERP puramente transaccional -> canibalizaría
    else:
        vered = "mixto"
    filas.append((v, kw, inf, tra, exo, vered))
    print(f"{v:>8}  {inf:>8} / {tra:<7}  {str(exo or '—'):<34} {vered:<11} {kw}  [{CATALOGO[kw]}]")

print("\n" + "=" * 100)
res = Counter(f[5] for f in filas)
print("RESUMEN:", dict(res))
for etiqueta in ("SÍ doblar", "mixto", "solo ficha", "NO doblar"):
    g = [f for f in filas if f[5] == etiqueta]
    if g:
        print(f"\n  {etiqueta} ({len(g)}, {sum(f[0] for f in g):,}/mes):")
        for v, kw, *_ in sorted(g, key=lambda x: -x[0]):
            print(f"     {v:>7}/mes  {kw}")
