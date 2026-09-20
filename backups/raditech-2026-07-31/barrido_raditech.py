#!/usr/bin/env python3
"""Barrido de competidores de raditech: quien aparece de verdad en los SERPs
del nicho, medido, no supuesto. SERP live advanced depth 20, MX/es."""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import defaultdict

import requests

sys.path.insert(0, r"C:\Users\gabom\.claude\skills\ficha-vs-competidor\scripts")
from _config import cargar, auth_dataforseo  # noqa: E402

s = cargar("raditech")
AUTH = auth_dataforseo(s)

KW = [
    # nucleo PACS
    "pacs", "sistema pacs", "sistema pacs ris", "pacs ris", "que es pacs",
    "pacs mexico", "software pacs", "visor dicom", "servidor pacs",
    # teleradiologia
    "teleradiologia", "servicio de teleradiologia", "teleradiologia mexico",
    "empresas de teleradiologia", "interpretacion de estudios radiologicos",
    # monitores
    "monitores medicos", "monitor grado medico", "monitores para radiologia",
    # HIS / software hospitalario
    "sistema his", "software hospitalario", "sistema ris",
    "expediente clinico electronico",
]

URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"


def pedir(k):
    """OJO: los endpoints `live` aceptan UNA tarea por POST. Mandar un lote
    devuelve 200 y procesa solo la primera — silenciosamente."""
    r = requests.post(URL, auth=AUTH, json=[{
        "keyword": k, "location_code": 2484, "language_code": "es",
        "device": "desktop", "depth": 20}], timeout=180)
    return r.json()


from concurrent.futures import ThreadPoolExecutor  # noqa: E402

with ThreadPoolExecutor(max_workers=6) as ex:
    respuestas = list(ex.map(pedir, KW))

costo = sum(x.get("cost", 0) or 0 for x in respuestas)
tareas = [t for x in respuestas for t in x.get("tasks", [])]
print(f"costo ${costo:.4f}  tareas {len(tareas)}  "
      f"con datos {sum(1 for t in tareas if t.get('result'))}")

dominios = defaultdict(lambda: {"apar": 0, "kw": [], "mejor": 99})
por_kw = {}
crudo = {}

for t in tareas:
    if not t.get("result"):
        print(f"  sin datos: {t.get('data', {}).get('keyword')!r} "
              f"-> {t.get('status_message')}")
        continue
    res = t["result"][0]
    kw = res.get("keyword")
    filas = []
    for it in res.get("items", []) or []:
        if it.get("type") != "organic":
            continue
        dom = (it.get("domain") or "").lower().replace("www.", "")
        pos = it.get("rank_absolute")
        filas.append((pos, dom, it.get("url"), (it.get("title") or "")[:70]))
    por_kw[kw] = filas
    crudo[kw] = [{"pos": p, "dom": dm, "url": u, "titulo": ti} for p, dm, u, ti in filas]
    for pos, dom, u, ti in filas:
        e = dominios[dom]
        e["apar"] += 1
        e["kw"].append(f"{kw}#{pos}")
        e["mejor"] = min(e["mejor"], pos)

RUIDO = re.compile(
    r"wikipedia|youtube|facebook|linkedin|instagram|reddit|amazon|mercadolibre|"
    r"gob\.mx|edu\.|scielo|researchgate|medigraphic|elsevier|slideshare|"
    r"indeed|occ\.com|computrabajo|glassdoor|x\.com|tiktok")

print("\n=== DOMINIOS POR PRESENCIA (filtrado ruido) ===")
print(f"{'dominio':<34} {'apar':>4} {'mejor':>5}   keywords")
orden = sorted(dominios.items(), key=lambda x: (-x[1]["apar"], x[1]["mejor"]))
for dom, e in orden:
    if RUIDO.search(dom) or e["apar"] < 2:
        continue
    print(f"{dom:<34} {e['apar']:>4} {e['mejor']:>5}   {', '.join(e['kw'][:7])}")

print("\n=== ¿DONDE ESTA RADITECH? ===")
hay = False
for kw, filas in por_kw.items():
    for pos, dom, u, ti in filas:
        if "raditech" in dom or "teleradiologos" in dom:
            print(f"  {kw:<38} #{pos}  {u}")
            hay = True
if not hay:
    print("  raditech.mx NO aparece en el top-20 de ninguna de las "
          f"{len(por_kw)} keywords barridas.")

pathlib.Path("serps-raditech.json").write_text(
    json.dumps(crudo, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\nSERPs crudos -> serps-raditech.json  ({len(por_kw)} keywords)")
