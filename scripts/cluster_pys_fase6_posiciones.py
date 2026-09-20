#!/usr/bin/env python3
"""Fase 2 — paso 6: ¿dónde está PYS realmente en las keywords ganables?

SERP en vivo a profundidad 100 (no solo top-10) para saber si PYS está en
11-30 (empujable) o fuera de las 100 (entrar desde cero).

Cachea por keyword. Uso: py -3 cluster_pys_fase6_posiciones.py [n_max]
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
from urllib.parse import urlparse

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
DATA = REPO / "docs" / "data"
CACHE = DATA / "cluster-pys-posiciones.json"

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

from dataforseo_client import DataForSEOClient  # noqa: E402

PYS = "peptidosysuplementos"
# los 15 clusters ganables + los 4 que quedaron al borde
KEYWORDS = [
    "ipamorelina", "retatrutida", "retatrutida precio", "agua bacteriostatica",
    "péptidos para bajar de peso", "cjc-1295", "péptidos gym",
    "péptidos para masa muscular", "mots-c", "tb-500", "péptidos inyectables",
    "péptidos mexico", "péptidos precio", "donde comprar péptidos en méxico",
    "comprar péptidos", "cagrilintida", "selank", "bpc 157 precio",
    "sermorelina", "bpc-157 y tb-500",
    # al borde (MIXTO 33%) — vale saber si ya rankea
    "igf-1 lr3", "thymosin alpha 1", "glutation liofilizado", "nad+ inyectable",
    # descubiertas tarde (paso de grafías): volumen alto que la muestra original
    # se perdió por elegir la variante equivocada de la keyword
    "glutation",            # 6,600/mes — PYS tiene el producto (2234)
    "glutathione",          # 6,600/mes
    "retatrutide precio",   # 4,400/mes — exoma está en pos 2
    "tesamorelina",         # 3,600/mes — PYS NO lo vende (hueco de catálogo)
    "sermorelin",           # 880/mes — gana a 'sermorelina' (210)
    "cjc 1295 ipamorelin",  # 590/mes — exoma en pos 4
    "kisspeptina",          # 720/mes — PYS NO lo vende
    "pt-141",               # 590/mes — PYS NO lo vende
]

cache = json.load(open(CACHE, encoding="utf-8")) if CACHE.exists() else {}
n_max = int(sys.argv[1]) if len(sys.argv) > 1 else len(KEYWORDS)
pendientes = [k for k in KEYWORDS if k not in cache][:n_max]
print(f"=== {len(cache)} en caché | {len(pendientes)} a consultar (profundidad 100) ===\n")

c = DataForSEOClient()
for i, kw in enumerate(pendientes, 1):
    try:
        items = c._post("/v3/serp/google/organic/live/advanced", {
            "keyword": kw, "location_code": 2484, "language_code": "es",
            "device": "desktop", "depth": 100,
        })
    except Exception as e:
        print(f"  [{i}/{len(pendientes)}] {kw!r}: ERROR {e}")
        continue
    org = [it for it in items if it.get("type") == "organic"]
    pos_pys, url_pys = None, None
    competidores = {}
    for it in org:
        host = (urlparse(it.get("url") or "").netloc or "").replace("www.", "")
        p = it.get("rank_absolute")
        if PYS in host and pos_pys is None:
            pos_pys, url_pys = p, it.get("url")
        for comp in ("exomapeptides.mx", "peptide.com.mx"):
            if comp in host and comp not in competidores:
                competidores[comp] = p
    cache[kw] = {"profundidad": len(org), "pys_pos": pos_pys, "pys_url": url_pys,
                 "competidores": competidores}
    estado = f"pos {pos_pys}" if pos_pys else f"FUERA del top-{len(org)}"
    print(f"  [{i}/{len(pendientes)}] {kw!r}: PYS {estado} | "
          f"exoma={competidores.get('exomapeptides.mx','—')} "
          f"peptide={competidores.get('peptide.com.mx','—')} | ${c.total_cost:.4f}")
    time.sleep(0.3)

json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nCOSTO DE ESTA CORRIDA: ${c.total_cost:.4f}")
