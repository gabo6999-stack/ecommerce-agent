#!/usr/bin/env python3
"""Fase 2 — Clustering PYS, paso 1: construir el pool de keywords.

Barato (solo DataForSEO Labs). Guarda el pool crudo para que los pasos
siguientes (SERPs + clustering) no tengan que volver a pagar la expansión.

OJO: el _flatten del cliente devuelve la clave 'volume' (no 'search_volume'),
'difficulty' e 'intent' ya vienen incluidos -> no hace falta search_intent aparte.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
OUT_DIR = REPO / "docs" / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "cluster-pys-pool.json"

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

from dataforseo_client import DataForSEOClient  # noqa: E402

SEEDS = [
    "péptidos para qué sirven",
    "péptidos vs esteroides",
    "cómo se aplican los péptidos",
    "péptidos efectos secundarios",
    "suplementos para recuperación muscular",
    "bpc 157 para que sirve",
    "agua bacteriostática reconstituir péptidos",
    "péptidos antienvejecimiento",
]
SUGGEST_SEEDS = ["péptidos", "bpc 157", "retatrutida", "semaglutida", "tirzepatida"]

# Términos que hacen que una keyword sea RELEVANTE para el catálogo de PYS.
# Se usa para separar señal de ruido (keyword_ideas con semillas amplias trae
# "farmacias similares", "para que sirve el ibuprofeno", etc.).
RELEVANTE = re.compile(
    r"p[eé]ptid|bpc|tb-?500|semaglutid|tirzepatid|retatrutid|cagrilintid|"
    r"ipamorelin|sermorelin|cjc|mots-?c|igf-?1|selank|thymosin|timosin|"
    r"glutati[oó]n|nad\+?|bacteriost|liofiliz|hgh|ghrp|ghrh|hexarelin|"
    r"melanotan|epitalon|tesamorelin|aod|dsip|kisspeptin|amilina",
    re.IGNORECASE,
)

c = DataForSEOClient()
pool: dict[str, dict] = {}


def add(items, fuente):
    nuevos = 0
    for it in items:
        kw = (it.get("keyword") or "").strip().lower()
        if not kw:
            continue
        if kw in pool:
            pool[kw]["fuentes"].append(fuente)
            continue
        pool[kw] = {
            "keyword": kw,
            "volume": it.get("volume"),
            "difficulty": it.get("difficulty"),
            "intent": it.get("intent"),
            "cpc": it.get("cpc"),
            "competition": it.get("competition"),
            "relevante": bool(RELEVANTE.search(kw)),
            "fuentes": [fuente],
        }
        nuevos += 1
    return nuevos


print("=== 1. keyword_ideas (8 semillas de la auditoría) ===")
items = c.keyword_ideas("pys", SEEDS, limit=1000, min_volume=10)
print(f"   {len(items)} items -> {add(items, 'ideas')} nuevos | ${c.total_cost:.4f}")

print("\n=== 2. keyword_suggestions (long-tail por semilla) ===")
for s in SUGGEST_SEEDS:
    try:
        items = c.keyword_suggestions("pys", s, limit=300)
        print(f"   {s!r}: {len(items)} -> {add(items, f'sug:{s}')} nuevos | ${c.total_cost:.4f}")
    except Exception as e:
        print(f"   {s!r}: ERROR {e}")

todos = list(pool.values())
rel = [v for v in todos if v["relevante"] and (v.get("volume") or 0) > 0]
rel.sort(key=lambda v: -(v.get("volume") or 0))

json.dump(
    {"pool": todos, "costo_usd": round(c.total_cost, 5), "seeds": SEEDS},
    open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1,
)

print(f"\n=== POOL: {len(todos)} únicas | {len(rel)} relevantes con volumen ===")
print(f"\n=== TOP 40 RELEVANTES por volumen ===")
for v in rel[:40]:
    print(f"  {v['volume']:>6}  kd={str(v.get('difficulty')):>4}  "
          f"{str(v.get('intent')):<14} {v['keyword']}")

vol_total = sum(v["volume"] for v in rel)
print(f"\n  volumen relevante total: {vol_total:,}/mes")
print(f"Guardado en {OUT}")
print(f"COSTO TOTAL: ${c.total_cost:.4f}")
