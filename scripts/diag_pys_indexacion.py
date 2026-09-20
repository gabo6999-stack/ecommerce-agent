#!/usr/bin/env python3
"""¿Están indexadas las fichas de PYS? ¿Y cuántas páginas tiene cada sitio?

Test de indexación: se busca en Google una frase larga y única tomada del
cuerpo de la ficha. Si Google la devuelve, la página está indexada.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

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


# ---------- 1. tamaño de cada sitio vía sitemap ----------
def contar_sitemap(base: str) -> dict:
    vistos, urls, pendientes = set(), [], []
    for p in ("/sitemap_index.xml", "/sitemap.xml", "/wp-sitemap.xml"):
        try:
            r = requests.get(base + p, headers=UA, timeout=25)
            if r.status_code == 200 and "<" in r.text:
                pendientes.append((base + p, r.text))
                break
        except Exception:
            continue
    while pendientes:
        url, xml = pendientes.pop()
        if url in vistos:
            continue
        vistos.add(url)
        try:
            root = ET.fromstring(xml.encode("utf-8"))
        except Exception:
            continue
        tag = root.tag.split("}")[-1]
        locs = [e.text for e in root.iter() if e.tag.split("}")[-1] == "loc" and e.text]
        if tag == "sitemapindex":
            for l in locs[:25]:
                try:
                    rr = requests.get(l, headers=UA, timeout=25)
                    if rr.status_code == 200:
                        pendientes.append((l, rr.text))
                except Exception:
                    pass
        else:
            urls.extend(locs)
    tipos = {}
    for u in urls:
        seg = [s for s in u.replace("https://", "").split("/")[1:] if s]
        tipos[seg[0] if seg else "(raíz)"] = tipos.get(seg[0] if seg else "(raíz)", 0) + 1
    return {"total": len(urls), "por_tipo": dict(sorted(tipos.items(), key=lambda x: -x[1])[:8])}


print("=" * 74)
print("TAMAÑO DE CADA SITIO (sitemap)")
print("=" * 74)
tam = {}
for base in ("https://peptidosysuplementos.mx", "https://exomapeptides.mx"):
    tam[base] = contar_sitemap(base)
    print(f"  {base}")
    print(f"     URLs en sitemap: {tam[base]['total']}")
    print(f"     por sección: {tam[base]['por_tipo']}")

# ---------- 2. indexación por frase exacta ----------
FICHAS = [
    "https://peptidosysuplementos.mx/product/glutation-1500mg/",
    "https://peptidosysuplementos.mx/product/mots-c-10mg/",
    "https://peptidosysuplementos.mx/product/cjc-1295-ipamorelina-5mg/",
]


def frase_unica(url: str) -> str | None:
    try:
        html = requests.get(url, headers=UA, timeout=30).text
    except Exception:
        return None
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    txt = re.sub(r"\s+", " ", h)
    # frases largas del cuerpo, evitando boilerplate de navegación
    for m in re.finditer(r"[A-ZÁÉÍÓÚÑ][^.!?]{80,160}[.!?]", txt):
        f = m.group(0).strip()
        if not any(x in f.lower() for x in ("carrito", "menú", "cookies", "sesión",
                                            "iniciar", "buscar", "categoría")):
            return f
    return None


c = DataForSEOClient()
print("\n" + "=" * 74)
print("TEST DE INDEXACIÓN (frase exacta del cuerpo)")
print("=" * 74)
resultados = {}
for u in FICHAS:
    f = frase_unica(u)
    if not f:
        print(f"  {u}: no se pudo extraer frase")
        continue
    consulta = f'"{f[:110]}"'
    try:
        items = c._post("/v3/serp/google/organic/live/advanced", {
            "keyword": consulta, "location_code": 2484, "language_code": "es",
            "device": "desktop", "depth": 20})
    except Exception as e:
        print(f"  {u}: ERROR {e}")
        continue
    org = [it for it in items if it.get("type") == "organic"]
    encontrado = [it.get("url") for it in org if "peptidosysuplementos" in (it.get("url") or "")]
    estado = "INDEXADA" if encontrado else ("NO INDEXADA" if not org
                                            else "otra URL responde")
    print(f"\n  {u.split('/product/')[1]}")
    print(f"     frase: {f[:90]}...")
    print(f"     resultados totales: {len(org)} | ESTADO: {estado}")
    if encontrado:
        print(f"     -> {encontrado[0]}")
    resultados[u] = {"estado": estado, "n_resultados": len(org), "frase": f}

json.dump({"tamano": tam, "indexacion": resultados},
          open(DATA / "diag-pys-indexacion.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\nCOSTO: ${c.total_cost:.4f}")
