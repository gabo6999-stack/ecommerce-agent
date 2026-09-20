#!/usr/bin/env python3
"""Fase 2 — reporte final: clusters ordenados por oportunidad real.

Oportunidad = volumen que además es (a) alcanzable según composición de SERP
y (b) del negocio correcto (péptido de investigación, no cosmética ni fármaco
de farmacia). Sin costo de API.
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter, defaultdict
from urllib.parse import urlparse

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "docs" / "data"
serps = json.load(open(DATA / "cluster-pys-serps.json", encoding="utf-8"))
temas = json.load(open(DATA / "cluster-pys-temas.json", encoding="utf-8"))
extra = json.load(open(DATA / "cluster-pys-volumenes.json", encoding="utf-8"))

vol = {v["keyword"]: v.get("volume") or 0 for v in temas["limpio"]}
cpc = {v["keyword"]: v.get("cpc") for v in temas["limpio"]}
for k, d in extra.items():
    vol[k] = d["volume"]
    cpc[k] = d.get("cpc")

GRUPOS = {
    "telemedicina_glp1": ("zelara", "clivi", "zavamed", "goutogo", "enfaf"),
    "cosmetica": ("vichy", "lancome", "esteelauder", "mesoestetic", "sesderma",
                  "loreal", "clinique", "sephora", "eucerin", "isdin", "cerave"),
    "farmacia_retail": ("farmaciasimilares", "farmaciasdesimilares", "farmaciasguadalajara",
                        "farmaciasanpablo", "fahorro", "benavides", "chedraui", "walmart",
                        "soriana", "farmalisto", "sanborns", "sears.com", "olympiapharmacy"),
    "marketplace": ("amazon.", "mercadolibre", "ebay", "aliexpress", "linio", "iherb"),
    "autoridad_medica": ("plm.com", "medlineplus", "mayoclinic", "nih.gov", "niddk",
                         "msdmanuals", "drugs.com", "who.int", "gob.mx", "cofepris",
                         "fda.gov", "vademecum", "elsevier", "scielo", "healthline",
                         "webmd", "medscape", "cima.aemps", "revespcardiol",
                         "secardiologia", "genome.gov", "wikipedia", "clinicamarcorived"),
    "marca_pharma": ("novonordisk", "ozempic", "mounjaro", "lilly", "wegovy", "saxenda"),
    "ugc_foro": ("reddit", "quora", "youtube", "facebook", "tiktok", "instagram", "x.com"),
    "ecommerce_peptidos": ("exomapeptides", "peptide.com.mx", "peptidosysuplementos",
                           "biotechpeptides", "corepeptides", "peptidesciences",
                           "swisschems", "onyxgenlabz", "fit-peptides", "my-peptides",
                           "cymitquimica", "thefitweekend"),
}
BLOQUEANTES = ("autoridad_medica", "farmacia_retail", "marca_pharma", "cosmetica")


def clasificar(url):
    host = (urlparse(url or "").netloc or "").lower().replace("www.", "")
    for g, marcas in GRUPOS.items():
        if any(m in host for m in marcas):
            return g
    return "otro"


urls_de = {k: {r["url"] for r in rows if r.get("url")} for k, rows in serps.items()}
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

grupos = defaultdict(list)
for k in kws:
    grupos[find(k)].append(k)

filas = []
for g in grupos.values():
    g.sort(key=lambda k: -vol.get(k, 0))
    v = sum(vol.get(k, 0) for k in g)
    comp = Counter()
    for k in g:
        for r in serps[k]:
            comp[clasificar(r["url"])] += 1
    total = sum(comp.values()) or 1
    pct = 100 * sum(comp[x] for x in BLOQUEANTES) // total
    cpcs = [cpc.get(k) for k in g if cpc.get(k)]
    filas.append({
        "nombre": g[0], "keywords": g, "n": len(g), "volumen": v,
        "pct_bloqueado": pct,
        "etiqueta": "BLOQUEADO" if pct >= 60 else "MIXTO" if pct >= 30 else "ABIERTO",
        "cpc_medio": round(sum(cpcs) / len(cpcs), 2) if cpcs else None,
        "competidor_top": (Counter(
            r["dominio"] for k in g for r in serps[k]
            if clasificar(r["url"]) == "ecommerce_peptidos").most_common(1) or [("—", 0)])[0][0],
    })

abiertos = sorted([f for f in filas if f["etiqueta"] == "ABIERTO"],
                  key=lambda f: -f["volumen"])
otros = sorted([f for f in filas if f["etiqueta"] != "ABIERTO"],
               key=lambda f: -f["volumen"])

print("=" * 86)
print("OPORTUNIDAD REAL — clusters ABIERTOS (SERP contestable)")
print("=" * 86)
print(f"{'vol/mes':>8} {'bloq':>5} {'cpc':>6}  {'kw':>3}  cluster")
print("-" * 86)
for f in abiertos:
    print(f"{f['volumen']:>8} {str(f['pct_bloqueado'])+'%':>5} "
          f"{str(f['cpc_medio'] or '—'):>6}  {f['n']:>3}  {f['nombre']}")
    if f["n"] > 1:
        print(f"{'':>23}   └ {', '.join(f['keywords'][1:6])}")
tot_abierto = sum(f["volumen"] for f in abiertos)

print("\n" + "=" * 86)
print("DESCARTADOS — SERP bloqueado o intención equivocada")
print("=" * 86)
for f in otros:
    razon = []
    comp = Counter()
    for k in f["keywords"]:
        for r in serps[k]:
            comp[clasificar(r["url"])] += 1
    for g in BLOQUEANTES:
        if comp[g] >= 3:
            razon.append(f"{g}×{comp[g]}")
    print(f"{f['volumen']:>8} {str(f['pct_bloqueado'])+'%':>5}  {f['nombre']:<28} "
          f"{' '.join(razon)}")
tot_bloq = sum(f["volumen"] for f in otros)

print("\n" + "=" * 86)
print(f"Volumen ALCANZABLE: {tot_abierto:,}/mes   |   descartado: {tot_bloq:,}/mes "
      f"({100*tot_bloq//(tot_abierto+tot_bloq)}% del total medido)")
dom = Counter(r["dominio"] for rows in serps.values() for r in rows if r.get("dominio"))
print(f"PYS en top-10 de las 39 keywords: "
      f"{sum(1 for rows in serps.values() for r in rows if 'peptidosysuplementos' in (r.get('dominio') or ''))}")
print(f"exomapeptides.mx en top-10: {dom.get('exomapeptides.mx', 0)}")

json.dump({"abiertos": abiertos, "descartados": otros},
          open(DATA / "cluster-pys-reporte.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
