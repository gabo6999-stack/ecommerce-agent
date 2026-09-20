#!/usr/bin/env python3
"""Qué contiene exactamente la página de exoma para BPC-157+TB-500, y qué le
falta a la de PYS (ficha 795). Solo HTTP, sin costo de API.
"""
from __future__ import annotations

import html as htmlmod
import json
import pathlib
import re
from collections import Counter

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "docs" / "data"
UA = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"}

PAGINAS = {
    "EXOMA bpc-157-tb-500": "https://exomapeptides.mx/producto/bpc-157-tb-500",
    "EXOMA tb-500 (solo)": "https://exomapeptides.mx/producto/tb-500",
    "EXOMA compendio bpc": "https://exomapeptides.mx/compendio/bpc-157",
    "PYS 795 (actual)": "https://peptidosysuplementos.mx/product/bpc-157-tb-500-10-10mg/",
}

VACIAS = set("""de la el en y a los las un una con por para que se del al es su sus o
como mas más este esta estos estas lo le ni pero si no ha han hay ser son fue era
cuando donde sobre entre desde hasta cada todo toda todos todas otro otra puede pueden
tiene tienen debe deben hace hacer muy también solo sólo ya sin tras ante bajo the and
of to in for is are it its this that with on as be by or from at we you your our""".split())


def analizar(nombre, url):
    try:
        r = requests.get(url, headers=UA, timeout=40)
    except Exception as e:
        return {"error": str(e)}
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}"}
    h = r.text
    cuerpo = re.sub(r"(?is)<(script|style|noscript|nav|header|footer|svg)[^>]*>.*?</\1>", " ", h)
    limpio = lambda s: re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"(?s)<[^>]+>", "", s))).strip()
    encabezados = []
    for nivel in ("h1", "h2", "h3"):
        for m in re.finditer(rf"(?is)<{nivel}[^>]*>(.*?)</{nivel}>", cuerpo):
            t = limpio(m.group(1))
            if t and len(t) < 130:
                encabezados.append((nivel.upper(), t, m.start()))
    encabezados.sort(key=lambda x: x[2])
    vis = limpio(cuerpo)
    palabras = re.findall(r"[a-záéíóúñü0-9\-]{3,}", vis.lower())
    frec = Counter(w for w in palabras if w not in VACIAS and not w.isdigit())
    return {"url": url, "palabras": len(vis.split()),
            "encabezados": [(n, t) for n, t, _ in encabezados],
            "top_terminos": frec.most_common(40), "texto": vis}


res = {}
for nombre, url in PAGINAS.items():
    res[nombre] = analizar(nombre, url)
    d = res[nombre]
    print("=" * 92)
    print(f"=== {nombre}  —  {d.get('palabras', d.get('error'))} palabras")
    print("=" * 92)
    if "error" in d:
        print(f"   {d['error']}\n")
        continue
    for n, t in d["encabezados"][:40]:
        print(f"   {n:<3} {t}")
    print()

# --- qué cubre exoma que PYS no ---
exo = res.get("EXOMA bpc-157-tb-500", {})
pys = res.get("PYS 795 (actual)", {})
if "texto" in exo and "texto" in pys:
    t_pys = pys["texto"].lower()
    print("=" * 92)
    print("TÉRMINOS FRECUENTES EN EXOMA QUE NO APARECEN (o casi) EN PYS")
    print("=" * 92)
    faltan = []
    for w, n in exo["top_terminos"]:
        if n >= 4 and t_pys.count(w) < max(1, n // 4):
            faltan.append((w, n, t_pys.count(w)))
    for w, n, m in faltan[:30]:
        print(f"   {w:<26} exoma×{n:<4} PYS×{m}")

    print("\n" + "=" * 92)
    print("SECCIONES DE EXOMA SIN EQUIVALENTE EN PYS")
    print("=" * 92)
    h_pys = " | ".join(t.lower() for _, t in pys["encabezados"])
    for n, t in exo["encabezados"]:
        if n in ("H2", "H3"):
            clave = [w for w in re.findall(r"[a-záéíóúñ]{5,}", t.lower()) if w not in VACIAS]
            if clave and not any(w in h_pys for w in clave):
                print(f"   [{n}] {t}")

json.dump({k: {kk: vv for kk, vv in v.items() if kk != "texto"} for k, v in res.items()},
          open(DATA / "analisis-bpc157.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
