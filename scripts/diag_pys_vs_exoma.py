#!/usr/bin/env python3
"""DIAGNÓSTICO: por qué exoma rankea 2-10 y PYS 47-100+ con la misma autoridad.

Compara lo que Googlebot realmente recibe en la ficha de PYS contra la página
equivalente de exoma. Sin costo de API (solo HTTP).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from urllib.parse import urlparse

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "docs" / "data"
OUT = DATA / "diag-pys-vs-exoma.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}

serps = json.load(open(DATA / "cluster-pys-serps.json", encoding="utf-8"))

# URLs ganadoras de exoma por keyword (de los SERPs ya cacheados)
exoma_urls = {}
for kw, rows in serps.items():
    for r in rows:
        if "exomapeptides" in (r.get("dominio") or "") and kw not in exoma_urls:
            exoma_urls[kw] = (r["pos"], r["url"])

PAREJAS = [
    ("cjc-1295 / ipamorelina",
     "https://peptidosysuplementos.mx/product/cjc-1295-ipamorelina-5mg/",
     exoma_urls.get("cjc-1295", (None, None))[1]),
    ("glutatión",
     "https://peptidosysuplementos.mx/product/glutation-1500mg/", None),
    ("retatrutida",
     "https://peptidosysuplementos.mx/product/retatrutida-30mg/",
     exoma_urls.get("retatrutida", (None, None))[1]),
    ("mots-c",
     "https://peptidosysuplementos.mx/product/mots-c-10mg/",
     exoma_urls.get("mots-c", (None, None))[1]),
]


def texto_visible(html: str) -> str:
    h = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", html)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return re.sub(r"\s+", " ", h).strip()


def analizar(url: str) -> dict:
    if not url:
        return {"error": "sin URL"}
    try:
        r = requests.get(url, headers=UA, timeout=40)
    except Exception as e:
        return {"error": str(e)}
    html = r.text
    vis = texto_visible(html)
    titulo = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    canon = re.search(r'(?is)<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html)
    robots = re.findall(r'(?is)<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)', html)
    h1 = re.findall(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    h2 = re.findall(r"(?is)<h2[^>]*>(.*?)</h2>", html)
    desc = re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', html)
    dominio = urlparse(url).netloc.replace("www.", "")
    enlaces = re.findall(r'(?is)<a[^>]+href=["\']([^"\']+)', html)
    internos = [e for e in enlaces if dominio in e or e.startswith("/")]
    schemas = re.findall(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html)
    tipos = []
    for s in schemas:
        try:
            d = json.loads(s.strip())
        except Exception:
            continue
        for x in (d.get("@graph") or [d]):
            t = x.get("@type")
            tipos.extend(t if isinstance(t, list) else [t])
    limpio = lambda s: re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", "", s)).strip()
    return {
        "url": url, "http": r.status_code,
        "bytes_html": len(html),
        "palabras_visibles": len(vis.split()),
        "titulo": limpio(titulo.group(1)) if titulo else None,
        "meta_desc_len": len(desc.group(1)) if desc else 0,
        "canonical": canon.group(1) if canon else None,
        "meta_robots": robots,
        "h1": [limpio(x) for x in h1],
        "n_h2": len(h2),
        "h2_muestra": [limpio(x) for x in h2[:6]],
        "enlaces_internos": len(internos),
        "schema_tipos": sorted(set(t for t in tipos if t)),
    }


salida = {}
for nombre, u_pys, u_exo in PAREJAS:
    print("=" * 78)
    print(f"=== {nombre}")
    print("=" * 78)
    a, b = analizar(u_pys), analizar(u_exo)
    salida[nombre] = {"pys": a, "exoma": b}
    campos = ["http", "bytes_html", "palabras_visibles", "titulo", "meta_desc_len",
              "canonical", "meta_robots", "h1", "n_h2", "enlaces_internos", "schema_tipos"]
    for c in campos:
        va, vb = a.get(c), b.get(c)
        marca = ""
        if c == "palabras_visibles" and isinstance(va, int) and isinstance(vb, int):
            marca = f"   <<< exoma {vb/max(va,1):.1f}x" if vb > va * 1.3 else ""
        print(f"  {c:<20} PYS: {str(va)[:72]}")
        print(f"  {'':<20} EXO: {str(vb)[:72]}{marca}")
    print()

json.dump(salida, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"Guardado en {OUT}")
