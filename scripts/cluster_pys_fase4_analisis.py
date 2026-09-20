#!/usr/bin/env python3
"""Fase 2 — paso 4: clustering por solapamiento de SERP + lectura de viabilidad.

Sin costo de API (lee el caché del paso 3).

Dos keywords van al mismo cluster si comparten >= UMBRAL URLs en el top-10.
Eso es clustering real (mismo SERP = misma página debe atacarlas), no lexical.
La composición del SERP dice si PYS puede entrar o si el nicho está tomado por
farmacias/PLM/autoridad médica.
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
vol = {v["keyword"]: v.get("volume") or 0 for v in temas["limpio"]}

UMBRAL = 3          # URLs compartidas en top-10 para unir dos keywords
PYS = "peptidosysuplementos.mx"

GRUPOS = {
    "farmacia_retail": (
        "farmaciasimilares", "farmaciasguadalajara", "farmaciasanpablo", "fahorro",
        "farmaciadelahorro", "benavides", "chedraui", "walmart", "soriana",
        "farmalisto", "farmaciasyza", "sanborns", "cofarmex", "farmacias"),
    "marketplace": ("amazon.", "mercadolibre", "ebay", "aliexpress", "shopee", "linio"),
    "autoridad_medica": (
        "plm.com", "medlineplus", "mayoclinic", "nih.gov", "niddk", "msdmanuals",
        "drugs.com", "who.int", "gob.mx", "cofepris", "fda.gov", "ema.europa",
        "medicamentosplm", "vademecum", "elsevier", "scielo", "nejm", "healthline",
        "webmd", "clinicbarcelona", "cun.es", "topdoctors", "sanitas", "medicalnewstoday",
        "kickpharma", "imss", "issste", "clinicalatinoamericana", "hospital",
        "salud.", "medlineplus", "cochrane", "nlm.nih"),
    "marca_pharma": ("novonordisk", "ozempic", "mounjaro", "lilly", "wegovy", "saxenda",
                     "zepbound", "trulicity"),
    "ugc_foro": ("reddit", "quora", "youtube", "facebook", "tiktok", "instagram",
                 "x.com", "twitter", "pinterest"),
    "ecommerce_peptidos": (
        "exomapeptides", "peptide.com.mx", "peptidosysuplementos", "biotechpeptides",
        "corepeptides", "peptidesciences", "swisschems", "nootropicsdepot",
        "peptidos", "sarms", "musculo", "suplement"),
}


def clasificar(url: str) -> str:
    host = (urlparse(url or "").netloc or "").lower().replace("www.", "")
    for grupo, marcas in GRUPOS.items():
        if any(m in host for m in marcas):
            return grupo
    return "otro"


urls_de = {kw: {r["url"] for r in rows if r.get("url")} for kw, rows in serps.items()}
kws = [k for k in serps if urls_de.get(k)]

# ---- clustering por solapamiento (componentes conexas) ----
padre = {k: k for k in kws}


def find(x):
    while padre[x] != x:
        padre[x] = padre[padre[x]]
        x = padre[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        padre[rb] = ra


pares = []
for i, a in enumerate(kws):
    for b in kws[i + 1:]:
        comp = len(urls_de[a] & urls_de[b])
        if comp >= UMBRAL:
            union(a, b)
            pares.append((a, b, comp))

clusters = defaultdict(list)
for k in kws:
    clusters[find(k)].append(k)

# ---- reporte ----
print("=" * 78)
print(f"CLUSTERS POR SOLAPAMIENTO DE SERP (>= {UMBRAL} URLs compartidas en top-10)")
print("=" * 78)

orden = sorted(clusters.values(), key=lambda g: -sum(vol.get(k, 0) for k in g))
resumen = []
for grupo in orden:
    grupo.sort(key=lambda k: -vol.get(k, 0))
    v = sum(vol.get(k, 0) for k in grupo)
    comp = Counter()
    pys_pos = {}
    for k in grupo:
        for r in serps[k]:
            comp[clasificar(r["url"])] += 1
            if PYS in (r.get("dominio") or ""):
                pys_pos[k] = r["pos"]
    total = sum(comp.values()) or 1
    # viabilidad: cuánto del SERP es alcanzable (ecommerce/foro/otro) vs bloqueado
    bloqueado = comp["farmacia_retail"] + comp["autoridad_medica"] + comp["marca_pharma"]
    abierto = comp["ecommerce_peptidos"] + comp["ugc_foro"] + comp["otro"] + comp["marketplace"]
    pct_bloq = 100 * bloqueado // total
    etiqueta = ("BLOQUEADO" if pct_bloq >= 60 else
                "MIXTO" if pct_bloq >= 30 else "ABIERTO")
    print(f"\n── [{etiqueta}] {v:,}/mes · {len(grupo)} kw · SERP bloqueado {pct_bloq}%")
    print(f"   composición: {dict(comp.most_common())}")
    if pys_pos:
        print(f"   *** PYS ya rankea: {pys_pos}")
    for k in grupo[:10]:
        print(f"     {vol.get(k,0):>7}  {k}")
    if len(grupo) > 10:
        print(f"     ... +{len(grupo)-10} más")
    resumen.append({"keywords": grupo, "volumen": v, "pct_bloqueado": pct_bloq,
                    "etiqueta": etiqueta, "composicion": dict(comp),
                    "pys_posiciones": pys_pos})

# ---- quién domina el bucket "otro" (para afinar la clasificación) ----
otros = Counter()
for kw, rows in serps.items():
    for r in rows:
        if clasificar(r["url"]) == "otro":
            otros[r.get("dominio") or "?"] += 1
print("\n" + "=" * 78)
print("TOP DOMINIOS EN 'otro' (revisar si merecen su propia categoría)")
print("=" * 78)
for dom, n in otros.most_common(25):
    print(f"  {n:>3}  {dom}")

json.dump(resumen, open(DATA / "cluster-pys-clusters.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\nGuardado en {DATA / 'cluster-pys-clusters.json'}")
