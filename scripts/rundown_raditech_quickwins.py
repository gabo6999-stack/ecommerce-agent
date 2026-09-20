#!/usr/bin/env python
"""Barrido reproducible de quick wins SEO de Raditech.

DataForSEO SERP live advanced, Google México, español, desktop, depth 20.
Una tarea por POST: el endpoint live ignora silenciosamente lotes múltiples.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

import requests

SKILL = Path(r"C:\Users\gabom\AppData\Local\hermes\skills\seo\ficha-vs-competidor\scripts")
sys.path.insert(0, str(SKILL))
from _config import auth_dataforseo, cargar  # noqa: E402

KEYWORDS = [
    "pacs", "sistema pacs", "sistema pacs ris", "pacs ris", "que es pacs",
    "pacs mexico", "software pacs", "visor dicom", "servidor pacs",
    "teleradiologia", "servicio de teleradiologia", "teleradiologia mexico",
    "empresas de teleradiologia", "interpretacion de estudios radiologicos",
    "monitores medicos", "monitor grado medico", "monitores para radiologia",
    "sistema his", "software hospitalario", "sistema ris",
    "expediente clinico electronico",
]
API = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
OUT_DIR = Path(r"C:\Users\gabom\Proyectos\ecommerce-agent\docs\data")
STAMP = "2026-08-05"

site = cargar("raditech")
auth = auth_dataforseo(site)


def fetch(keyword: str) -> dict:
    payload = [{
        "keyword": keyword,
        "location_code": 2484,
        "language_code": "es",
        "device": "desktop",
        "depth": 20,
    }]
    response = requests.post(API, auth=auth, json=payload, timeout=180)
    response.raise_for_status()
    body = response.json()
    return {"requested_keyword": keyword, "response": body}


OUT_DIR.mkdir(parents=True, exist_ok=True)
raw_path = OUT_DIR / f"raditech-serps-live-{STAMP}.json"
if "--reuse-raw" in sys.argv:
    if not raw_path.exists():
        raise RuntimeError(f"No existe el crudo para reutilizar: {raw_path}")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
else:
    with ThreadPoolExecutor(max_workers=4) as pool:
        raw = list(pool.map(fetch, KEYWORDS))
    raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

rows = []
usable_tasks = 0
cost = 0.0
for envelope in raw:
    requested = envelope["requested_keyword"]
    body = envelope["response"]
    cost += float(body.get("cost") or 0)
    tasks = body.get("tasks") or []
    if len(tasks) != 1:
        raise RuntimeError(f"{requested}: se esperaba 1 tarea, llegaron {len(tasks)}")
    task = tasks[0]
    results = task.get("result") or []
    if not results:
        raise RuntimeError(f"{requested}: sin resultado útil ({task.get('status_message')})")
    usable_tasks += 1
    result = results[0]
    organic = [item for item in (result.get("items") or []) if item.get("type") == "organic"]
    raditech = [item for item in organic if "raditech.mx" in (item.get("domain") or "").lower()]
    hit = min(raditech, key=lambda x: x.get("rank_absolute") or 999) if raditech else None
    rows.append({
        "keyword_requested": requested,
        "keyword_returned": result.get("keyword"),
        "raditech_position": hit.get("rank_absolute") if hit else None,
        "raditech_url": hit.get("url") if hit else None,
        "raditech_title": hit.get("title") if hit else None,
        "top_organic": [
            {
                "position": item.get("rank_absolute"),
                "domain": item.get("domain"),
                "url": item.get("url"),
                "title": item.get("title"),
            }
            for item in organic[:10]
        ],
    })

if usable_tasks != len(KEYWORDS):
    raise RuntimeError(f"Cardinalidad inválida: {usable_tasks}/{len(KEYWORDS)} tareas útiles")

ranked_any = [row for row in rows if row["raditech_position"] is not None]
ranked = [row for row in ranked_any if row["raditech_position"] <= 20]
top10 = [row for row in ranked if row["raditech_position"] <= 10]
quickwins = [row for row in ranked if 4 <= row["raditech_position"] <= 20]
summary = {
    "method": "DataForSEO SERP live advanced",
    "market": {"location_code": 2484, "language_code": "es", "device": "desktop", "depth": 20},
    "measured_at_utc": datetime.now(timezone.utc).isoformat(),
    "keywords_sent": len(KEYWORDS),
    "usable_results": usable_tasks,
    "cost_usd": round(cost, 4),
    "ranked_any_returned": len(ranked_any),
    "ranked_top20": len(ranked),
    "outside_top20_returned": [row for row in ranked_any if row["raditech_position"] > 20],
    "top10": len(top10),
    "best_position": min((row["raditech_position"] for row in ranked), default=None),
    "quickwins_4_20": quickwins,
    "rows": rows,
}
summary_path = OUT_DIR / f"raditech-quickwins-{STAMP}.json"
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "status": "PASS",
    "keywords_sent": len(KEYWORDS),
    "usable_results": usable_tasks,
    "cost_usd": round(cost, 4),
    "ranked_any_returned": len(ranked_any),
    "ranked_top20": len(ranked),
    "top10": len(top10),
    "best_position": summary["best_position"],
    "quickwins": [{"keyword": r["keyword_requested"], "position": r["raditech_position"], "url": r["raditech_url"]} for r in quickwins],
    "raw_path": str(raw_path),
    "summary_path": str(summary_path),
}, ensure_ascii=False, indent=2))
