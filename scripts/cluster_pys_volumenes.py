#!/usr/bin/env python3
"""Volúmenes exactos del catálogo PYS vía Google Ads.

El endpoint keywords_data/google_ads/search_volume/live devuelve la lista en
tasks[0].result (NO en result[0].items como los endpoints de Labs), por eso el
_post genérico del cliente la descarta. Aquí se parsea directo.
"""
from __future__ import annotations

import json
import os
import pathlib
import requests
from requests.auth import HTTPBasicAuth

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "docs" / "data"
OUT = DATA / "cluster-pys-volumenes.json"

env = {}
for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

serps = json.load(open(DATA / "cluster-pys-serps.json", encoding="utf-8"))
temas = json.load(open(DATA / "cluster-pys-temas.json", encoding="utf-8"))
ya = {v["keyword"] for v in temas["limpio"]}
faltan = sorted(k for k in serps if k not in ya)
print(f"{len(faltan)} keywords sin volumen: {faltan}\n")

r = requests.post(
    "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
    auth=HTTPBasicAuth(env["DATAFORSEO_USERNAME"], env["DATAFORSEO_PASSWORD"]),
    json=[{"keywords": faltan, "location_code": 2484, "language_code": "es"}],
    timeout=120,
)
payload = r.json()
print(f"status {payload.get('status_code')} | costo ${payload.get('cost')}")
task = (payload.get("tasks") or [{}])[0]
result = task.get("result") or []

vols = {}
for it in result:
    kw = it.get("keyword")
    if kw:
        vols[kw] = {
            "volume": it.get("search_volume") or 0,
            "cpc": it.get("cpc"),
            "competition": it.get("competition"),
        }

json.dump(vols, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n{len(vols)} volúmenes obtenidos:\n")
for kw, d in sorted(vols.items(), key=lambda x: -x[1]["volume"]):
    print(f"  {d['volume']:>7}/mes   cpc={str(d['cpc']):<6}  {kw}")
print(f"\nGuardado en {OUT}")
