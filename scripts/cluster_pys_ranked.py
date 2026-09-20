#!/usr/bin/env python3
"""¿Para qué rankea PYS hoy, en cualquier posición? Y comparación con exoma.

OJO (ver memoria pys-capa-necesidad-filtro-serp): ranked_keywords es una
instantánea del índice histórico de DataForSEO, no un SERP en vivo. Sirve para
dimensionar tracción, no para confirmar una posición puntual.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
DATA = REPO / "docs" / "data"

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

from dataforseo_client import DataForSEOClient  # noqa: E402

c = DataForSEOClient()
salida = {}

for dominio in ("peptidosysuplementos.mx", "exomapeptides.mx"):
    try:
        # max_position por default es 20; queremos ver hasta la 100
        kws = c.ranked_keywords("pys", target=dominio, limit=1000, max_position=100)
    except Exception as e:
        print(f"{dominio}: ERROR {e}")
        continue

    con_vol = [k for k in kws if (k.get("volume") or 0) > 0]
    tramos = Counter()
    for k in kws:
        p = k.get("position")
        if not p:
            continue
        tramos["1-3" if p <= 3 else "4-10" if p <= 10 else
               "11-20" if p <= 20 else "21-50" if p <= 50 else "51+"] += 1
    etv = sum((k.get("volume") or 0) for k in kws if (k.get("position") or 999) <= 10)
    print(f"\n=== {dominio} ===")
    print(f"  keywords rankeadas: {len(kws)} ({len(con_vol)} con volumen)")
    print(f"  distribución: {dict(sorted(tramos.items()))}")
    print(f"  volumen en top-10: {etv:,}/mes")
    top = sorted([k for k in kws if (k.get("position") or 999) <= 10],
                 key=lambda k: -(k.get("volume") or 0))[:15]
    print("  mejores posiciones por volumen:")
    for k in top:
        print(f"     pos {str(k.get('position')):>3}  {k.get('volume') or 0:>6}/mes  "
              f"{k.get('keyword')}")
    salida[dominio] = {"n": len(kws), "tramos": dict(tramos), "vol_top10": etv,
                       "keywords": kws}

json.dump(salida, open(DATA / "cluster-pys-ranked.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\nCOSTO: ${c.total_cost:.4f}")
