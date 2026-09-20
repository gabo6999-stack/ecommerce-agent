#!/usr/bin/env python3
"""SERP de glutatión: ¿el top-10 es informativo o transaccional?

Es la keyword con mejor relación esfuerzo/retorno del estudio (6,600/mes en
'glutation' + 6,600 en 'glutathione', nadie rankea, PYS ya tiene el producto
2234). Antes de decidir el tipo de página hay que ver quién ocupa el top-10.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from collections import Counter
from urllib.parse import urlparse

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
DATA = REPO / "docs" / "data"

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

from dataforseo_client import DataForSEOClient  # noqa: E402

KEYWORDS = ["glutation", "glutathione", "glutation precio", "glutation inyectable"]

INFORMATIVO = ("/compendio/", "/blog/", "wikipedia", "/guia", "/articulo", "reddit",
               "youtube", "quora", "medlineplus", "/que-es", "mayoclinic", "healthline",
               "webmd", "medlineplus", "scielo", "nih.gov", "msdmanuals", "/salud")
TRANSACCIONAL = ("/producto/", "/product/", "/shop/", "/tienda/", "/comprar", "/p/",
                 "mercadolibre", "amazon.", "walmart", "farmacia", "fahorro", "chedraui",
                 "sears", "liverpool", "costco", "iherb", "linio")


def tipo(u: str) -> str:
    s = (u or "").lower()
    if any(t in s for t in TRANSACCIONAL):
        return "TRANSACCIONAL"
    if any(t in s for t in INFORMATIVO):
        return "informativo"
    return "otro"


c = DataForSEOClient()
salida = {}
for kw in KEYWORDS:
    try:
        items = c._post("/v3/serp/google/organic/live/advanced", {
            "keyword": kw, "location_code": 2484, "language_code": "es",
            "device": "desktop", "depth": 10})
    except Exception as e:
        print(f"{kw!r}: ERROR {e}")
        continue
    org = [it for it in items if it.get("type") == "organic"][:10]
    print("=" * 84)
    print(f"=== {kw!r}  ({len(org)} orgánicos)")
    print("=" * 84)
    conteo = Counter()
    filas = []
    for it in org:
        u = it.get("url") or ""
        t = tipo(u)
        conteo[t] += 1
        dom = (urlparse(u).netloc or "").replace("www.", "")
        path = urlparse(u).path[:44]
        filas.append({"pos": it.get("rank_absolute"), "dominio": dom,
                      "path": path, "tipo": t, "titulo": it.get("title")})
        print(f"  {it.get('rank_absolute'):>2}. [{t:<13}] {dom:<28} {path}")
        print(f"      {(it.get('title') or '')[:76]}")
    print(f"\n  composición: {dict(conteo)}")
    salida[kw] = {"composicion": dict(conteo), "resultados": filas}
    print()

json.dump(salida, open(DATA / "diag-serp-glutation.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"COSTO: ${c.total_cost:.4f}")
