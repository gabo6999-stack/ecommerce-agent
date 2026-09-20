#!/usr/bin/env python3
"""Indexación de las fichas que NO aparecen ni en el top-100, y tamaño de exoma.

Las que rankean en 38-88 están indexadas por definición; solo hay duda en las
ausentes. Extracción de frase corregida (sin migas de pan ni entidades HTML).
"""
from __future__ import annotations

import html as htmlmod
import json
import os
import pathlib
import re
import sys

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
DATA = REPO / "docs" / "data"
UA = {"User-Agent": "Mozilla/5.0 (compatible; audit/1.0)"}

for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

from dataforseo_client import DataForSEOClient  # noqa: E402

# ---------- tamaño real de exoma ----------
print("=" * 74)
print("TAMAÑO DE EXOMA (robots.txt -> sitemaps)")
print("=" * 74)
try:
    rb = requests.get("https://exomapeptides.mx/robots.txt", headers=UA, timeout=25).text
    print(rb[:400])
    sitemaps = re.findall(r"(?im)^sitemap:\s*(\S+)", rb)
    print(f"\n  sitemaps declarados: {sitemaps}")
    total = 0
    for sm in sitemaps[:6]:
        try:
            t = requests.get(sm, headers=UA, timeout=25).text
            locs = re.findall(r"<loc>([^<]+)</loc>", t)
            hijos = [l for l in locs if l.endswith(".xml")]
            if hijos:
                for h in hijos[:20]:
                    tt = requests.get(h, headers=UA, timeout=25).text
                    n = len(re.findall(r"<loc>([^<]+)</loc>", tt))
                    total += n
                    print(f"     {h.split('/')[-1]:<40} {n:>5} URLs")
            else:
                total += len(locs)
                print(f"     {sm.split('/')[-1]:<40} {len(locs):>5} URLs")
        except Exception as e:
            print(f"     {sm}: {e}")
    print(f"\n  TOTAL exoma: {total} URLs   (PYS: 91)")
except Exception as e:
    print(f"  error: {e}")

# ---------- indexación de las ausentes ----------
AUSENTES = {
    "glutation-1500mg": "https://peptidosysuplementos.mx/product/glutation-1500mg/",
    "cjc-1295-ipamorelina-5mg": "https://peptidosysuplementos.mx/product/cjc-1295-ipamorelina-5mg/",
}


def frase(url):
    h = requests.get(url, headers=UA, timeout=30).text
    # quedarse solo con el cuerpo del producto, fuera nav/menu/footer
    h = re.sub(r"(?is)<(script|style|noscript|nav|header|footer)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    t = htmlmod.unescape(h)
    t = re.sub(r"\s+", " ", t)
    cands = re.findall(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ][^.!?|/]{70,150}[.!?]", t)
    for f in cands:
        f = f.strip()
        if not any(x in f.lower() for x in ("carrito", "menú", "cookies", "sesión",
                                            "buscar", "categoría", "pérdida de peso /")):
            return f
    return None


c = DataForSEOClient()
print("\n" + "=" * 74)
print("INDEXACIÓN DE LAS FICHAS AUSENTES DEL TOP-100")
print("=" * 74)
for nombre, u in AUSENTES.items():
    f = frase(u)
    if not f:
        print(f"  {nombre}: sin frase utilizable")
        continue
    try:
        items = c._post("/v3/serp/google/organic/live/advanced", {
            "keyword": f'"{f[:100]}"', "location_code": 2484,
            "language_code": "es", "device": "desktop", "depth": 20})
    except Exception as e:
        print(f"  {nombre}: ERROR {e}")
        continue
    org = [it for it in items if it.get("type") == "organic"]
    hit = [it.get("url") for it in org if "peptidosysuplementos" in (it.get("url") or "")]
    print(f"\n  {nombre}")
    print(f"     frase: {f[:95]}")
    print(f"     resultados: {len(org)} | {'INDEXADA ✓' if hit else 'NO APARECE ✗'}")
    if hit:
        print(f"     -> {hit[0]}")

print(f"\nCOSTO: ${c.total_cost:.4f}")
