#!/usr/bin/env python3
"""Fase 2 — paso 5: clasificación refinada + volúmenes del catálogo + veredicto.

Refina los grupos con los dominios que aparecieron de verdad en los SERPs
(zelara/clivi = telemedicina GLP-1; Vichy/Lancôme = cosmética, que delata que
la keyword NO es de péptido de investigación) y trae el volumen de las
keywords del catálogo que no venían en el pool.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from collections import Counter, defaultdict
from urllib.parse import urlparse

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
DATA = REPO / "docs" / "data"
VOLCACHE = DATA / "cluster-pys-volumenes.json"

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

serps = json.load(open(DATA / "cluster-pys-serps.json", encoding="utf-8"))
temas = json.load(open(DATA / "cluster-pys-temas.json", encoding="utf-8"))
vol = {v["keyword"]: v.get("volume") or 0 for v in temas["limpio"]}

# --- volúmenes faltantes (catálogo) vía Google Ads search_volume ---
faltan = [k for k in serps if k not in vol]
if faltan:
    cache = json.load(open(VOLCACHE, encoding="utf-8")) if VOLCACHE.exists() else {}
    nuevos = [k for k in faltan if k not in cache]
    if nuevos:
        from dataforseo_client import DataForSEOClient
        c = DataForSEOClient()
        items = c._post("/v3/keywords_data/google_ads/search_volume/live", {
            "keywords": nuevos, "location_code": 2484, "language_code": "es"})
        for it in items:
            cache[it.get("keyword")] = it.get("search_volume") or 0
        json.dump(cache, open(VOLCACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[volúmenes] {len(nuevos)} keywords consultadas | costo ${c.total_cost:.4f}\n")
    vol.update({k: v for k, v in cache.items()})

GRUPOS = {
    "telemedicina_glp1": ("zelara", "clivi", "zavamed", "goutogo", "enfaf",
                          "elipse", "nutriologo", "obesidad"),
    "cosmetica": ("vichy", "lancome", "esteelauder", "mesoestetic", "sesderma",
                  "loreal", "clinique", "sephora", "shiseido", "eucerin",
                  "isdin", "cerave", "theordinary", "paulaschoice", "skin"),
    "farmacia_retail": (
        "farmaciasimilares", "farmaciasguadalajara", "farmaciasanpablo", "fahorro",
        "farmaciadelahorro", "benavides", "chedraui", "walmart", "soriana",
        "farmalisto", "farmaciasyza", "sanborns", "farmacias", "sears.com",
        "olympiapharmacy"),
    "marketplace": ("amazon.", "mercadolibre", "ebay", "aliexpress", "shopee",
                    "linio", "iherb"),
    "autoridad_medica": (
        "plm.com", "medlineplus", "mayoclinic", "nih.gov", "niddk", "msdmanuals",
        "drugs.com", "who.int", "gob.mx", "cofepris", "fda.gov", "ema.europa",
        "vademecum", "elsevier", "scielo", "nejm", "healthline", "webmd",
        "medscape", "cima.aemps", "revespcardiol", "secardiologia", "genome.gov",
        "clinicamarcorived", "topdoctors", "sanitas", "imss", "cochrane",
        "clinicbarcelona", "cun.es", "medicalnewstoday", "wikipedia"),
    "marca_pharma": ("novonordisk", "ozempic", "mounjaro", "lilly", "wegovy",
                     "saxenda", "zepbound", "trulicity"),
    "ugc_foro": ("reddit", "quora", "youtube", "facebook", "tiktok", "instagram",
                 "x.com", "twitter", "pinterest"),
    "ecommerce_peptidos": (
        "exomapeptides", "peptide.com.mx", "peptidosysuplementos", "biotechpeptides",
        "corepeptides", "peptidesciences", "swisschems", "onyxgenlabz",
        "fit-peptides", "my-peptides", "cymitquimica", "peptidos", "sarms",
        "thefitweekend", "musculo", "suplement"),
}
# grupos que significan "este SERP no es para una tienda de péptidos"
BLOQUEANTES = ("autoridad_medica", "farmacia_retail", "marca_pharma", "cosmetica")


def clasificar(url: str) -> str:
    host = (urlparse(url or "").netloc or "").lower().replace("www.", "")
    for grupo, marcas in GRUPOS.items():
        if any(m in host for m in marcas):
            return grupo
    return "otro"


urls_de = {kw: {r["url"] for r in rows if r.get("url")} for kw, rows in serps.items()}
kws = [k for k in serps if urls_de.get(k)]
padre = {k: k for k in kws}


def find(x):
    while padre[x] != x:
        padre[x] = padre[padre[x]]; x = padre[x]
    return x


for i, a in enumerate(kws):
    for b in kws[i + 1:]:
        if len(urls_de[a] & urls_de[b]) >= 3:
            ra, rb = find(a), find(b)
            if ra != rb:
                padre[rb] = ra

clusters = defaultdict(list)
for k in kws:
    clusters[find(k)].append(k)

print("=" * 80)
print("CLUSTERS PYS — clasificación refinada")
print("=" * 80)

filas = []
for grupo in sorted(clusters.values(), key=lambda g: -sum(vol.get(k, 0) for k in g)):
    grupo.sort(key=lambda k: -vol.get(k, 0))
    v = sum(vol.get(k, 0) for k in grupo)
    comp = Counter()
    for k in grupo:
        for r in serps[k]:
            comp[clasificar(r["url"])] += 1
    total = sum(comp.values()) or 1
    bloq = sum(comp[g] for g in BLOQUEANTES)
    pct = 100 * bloq // total
    etiqueta = "BLOQUEADO" if pct >= 60 else "MIXTO" if pct >= 30 else "ABIERTO"
    filas.append({"cluster": grupo[0], "keywords": grupo, "volumen": v,
                  "pct_bloqueado": pct, "etiqueta": etiqueta,
                  "composicion": dict(comp.most_common())})
    print(f"\n── [{etiqueta} {pct}%] {v:,}/mes · {len(grupo)} kw")
    print(f"   {dict(comp.most_common())}")
    for k in grupo[:6]:
        print(f"     {vol.get(k,0):>7}  {k}")
    if len(grupo) > 6:
        print(f"     ... +{len(grupo)-6}")

json.dump(filas, open(DATA / "cluster-pys-clusters.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ¿PYS aparece en algún top-10?
print("\n" + "=" * 80)
apariciones = {k: [r["pos"] for r in rows if "peptidosysuplementos" in (r.get("dominio") or "")]
               for k, rows in serps.items()}
apariciones = {k: v for k, v in apariciones.items() if v}
print(f"PYS en top-10: {apariciones if apariciones else 'NINGUNA de las 39 keywords'}")

# ¿quién sí gana? dominios más frecuentes en todo el set
print("\nDOMINIOS MÁS PRESENTES EN LOS 39 SERPs:")
dom = Counter(r["dominio"] for rows in serps.values() for r in rows if r.get("dominio"))
for d, n in dom.most_common(18):
    print(f"  {n:>3}  {d:<34} [{clasificar('https://' + d)}]")
