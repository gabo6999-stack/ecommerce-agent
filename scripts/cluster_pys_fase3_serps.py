#!/usr/bin/env python3
"""Fase 2 — paso 3: SERPs en vivo para clustering por solapamiento y para
medir la COMPOSICIÓN real del SERP (la metodología que pedía la auditoría:
el KD miente, lo que decide es quién ocupa el top-10).

Cachea cada SERP en disco: re-correr NO vuelve a pagar.
Uso:  py -3 cluster_pys_fase3_serps.py [n_max]
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
CACHE = DATA / "cluster-pys-serps.json"

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

from dataforseo_client import DataForSEOClient  # noqa: E402

# Muestra representativa: cabezas de cada tema + todo el catálogo real de PYS.
KEYWORDS = [
    # --- GLP-1 cabezas (el 88% del volumen; hay que probar si es alcanzable) ---
    "semaglutida", "tirzepatida", "semaglutida precio", "tirzepatida precio",
    "semaglutida para que sirve", "semaglutida similares", "tirzepatida plm",
    # --- catálogo PYS: producto por producto ---
    "retatrutida", "retatrutida precio", "cagrilintida",
    "bpc 157", "bpc 157 precio", "bpc-157 y tb-500", "tb-500",
    "ipamorelina", "sermorelina", "cjc-1295", "mots-c", "igf-1 lr3",
    "selank", "thymosin alpha 1", "glutation liofilizado", "nad+ inyectable",
    "agua bacteriostatica",
    # --- educacional / categoría (top-of-funnel natural de PYS) ---
    "péptidos", "que son los péptidos", "para qué sirven los péptidos",
    "péptidos inyectables", "péptidos para masa muscular",
    "péptidos para bajar de peso", "péptidos antienvejecimiento",
    # --- comercial / compra ---
    "péptidos precio", "comprar péptidos", "donde comprar péptidos en méxico",
    "péptidos mexico", "péptidos gym",
    # --- protocolo / seguridad ---
    "como reconstituir peptidos", "péptidos efectos secundarios",
    "péptidos vs esteroides",
]

# --- clasificación de dominios para leer la composición del SERP ---
GRUPOS = {
    "farmacia_retail": (
        "farmaciasimilares", "farmaciasguadalajara", "farmaciasanpablo",
        "fahorro", "farmaciadelahorro", "benavides", "chedraui", "walmart",
        "soriana", "superama", "farmalisto", "farmaciasyza", "sanborns"),
    "marketplace": ("amazon.", "mercadolibre", "ebay", "aliexpress", "shopee"),
    "autoridad_medica": (
        "plm.com", "medlineplus", "mayoclinic", "nih.gov", "niddk", "msdmanuals",
        "drugs.com", "who.int", "gob.mx", "cofepris", "fda.gov", "ema.europa",
        "medicamentosplm", "vademecum", "elsevier", "scielo", "nejm", "healthline",
        "webmd", "clinicbarcelona", "cun.es", "topdoctors", "sanitas"),
    "marca_pharma": ("novonordisk", "ozempic", "mounjaro", "lilly", "wegovy", "saxenda"),
    "ugc_foro": ("reddit", "quora", "youtube", "facebook", "tiktok", "instagram",
                 "forocoches", "x.com", "twitter"),
    "ecommerce_peptidos": (
        "exomapeptides", "peptide.com.mx", "peptidosysuplementos", "peptidos",
        "biotechpeptides", "corepeptides", "limitlesslifenootropics",
        "peptidesciences", "swisschems"),
}


def clasificar(url: str) -> str:
    host = (urlparse(url).netloc or url).lower().replace("www.", "")
    for grupo, marcas in GRUPOS.items():
        if any(m in host for m in marcas):
            return grupo
    return "otro"


cache = json.load(open(CACHE, encoding="utf-8")) if CACHE.exists() else {}
n_max = int(sys.argv[1]) if len(sys.argv) > 1 else len(KEYWORDS)
pendientes = [k for k in KEYWORDS if k not in cache][:n_max]

print(f"=== {len(cache)} en caché | {len(pendientes)} a consultar ahora ===\n")
c = DataForSEOClient()

for i, kw in enumerate(pendientes, 1):
    try:
        items = c._post("/v3/serp/google/organic/live/advanced", {
            "keyword": kw,
            "location_code": 2484,      # México
            "language_code": "es",
            "device": "desktop",
            "depth": 10,
        })
    except Exception as e:
        print(f"  [{i}/{len(pendientes)}] {kw!r}: ERROR {e}")
        continue
    organicos = [it for it in items if it.get("type") == "organic"][:10]
    cache[kw] = [{"pos": it.get("rank_absolute"), "url": it.get("url"),
                  "dominio": (urlparse(it.get("url") or "").netloc or "").replace("www.", ""),
                  "titulo": it.get("title")} for it in organicos]
    comp = {}
    for r in cache[kw]:
        g = clasificar(r["url"] or "")
        comp[g] = comp.get(g, 0) + 1
    mix = " ".join(f"{k}:{v}" for k, v in sorted(comp.items(), key=lambda x: -x[1]))
    print(f"  [{i}/{len(pendientes)}] {kw!r}: {len(organicos)} orgánicos | {mix} | ${c.total_cost:.4f}")
    time.sleep(0.3)

json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n=== {len(cache)} SERPs en caché -> {CACHE} ===")
print(f"COSTO DE ESTA CORRIDA: ${c.total_cost:.4f}")
