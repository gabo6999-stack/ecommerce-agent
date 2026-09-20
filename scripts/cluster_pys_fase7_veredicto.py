#!/usr/bin/env python3
"""Fase 2 — paso 7: veredicto por keyword ganable.

Cruza posición real de PYS (SERP en vivo, profundidad 100) con volumen y con
la posición de exoma, para separar 'empujable' de 'desde cero'. Sin costo API.
"""
from __future__ import annotations

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
DATA = REPO / "docs" / "data"

pos = json.load(open(DATA / "cluster-pys-posiciones.json", encoding="utf-8"))
temas = json.load(open(DATA / "cluster-pys-temas.json", encoding="utf-8"))
extra = json.load(open(DATA / "cluster-pys-volumenes.json", encoding="utf-8"))
graf = json.load(open(DATA / "cluster-pys-grafias.json", encoding="utf-8")) \
    if (DATA / "cluster-pys-grafias.json").exists() else {}

vol = {v["keyword"]: v.get("volume") or 0 for v in temas["limpio"]}
vol.update({k: d["volume"] for k, d in extra.items()})
vol.update(graf)

# ficha de PYS por keyword (catálogo real verificado en la Fase 1)
FICHA = {
    "ipamorelina": "solo dentro del combo 2232", "cjc-1295": "2232",
    "cjc 1295 ipamorelin": "2232",
    "retatrutida": "19", "retatrutida precio": "19", "retatrutide precio": "19",
    "agua bacteriostatica": "799", "mots-c": "790 / 793", "tb-500": "combo 795",
    "bpc 157 precio": "combo 795", "bpc-157 y tb-500": "combo 795", "bpc 157": "combo 795",
    "cagrilintida": "2240", "selank": "1699", "sermorelina": "2231", "sermorelin": "2231",
    "glutation": "2234", "glutathione": "2234", "glutation liofilizado": "2234",
    "thymosin alpha 1": "2230", "igf-1 lr3": "1128", "nad+ inyectable": "1131",
    "tesamorelina": "— NO lo vende", "kisspeptina": "— NO lo vende",
    "pt-141": "— NO lo vende",
}


def tramo(p):
    if p is None:
        return "desde cero"
    if p <= 10:
        return "top-10"
    if p <= 20:
        return "EMPUJABLE (11-20)"
    if p <= 30:
        return "EMPUJABLE (21-30)"
    if p <= 50:
        return "lejos (31-50)"
    return "muy lejos (51+)"


filas = []
for kw, d in pos.items():
    filas.append({
        "keyword": kw, "volumen": vol.get(kw, 0), "pys": d.get("pys_pos"),
        "tramo": tramo(d.get("pys_pos")),
        "exoma": d.get("competidores", {}).get("exomapeptides.mx"),
        "peptide": d.get("competidores", {}).get("peptide.com.mx"),
        "ficha": FICHA.get(kw, "?"),
    })
filas.sort(key=lambda f: -f["volumen"])

print("=" * 96)
print("¿DÓNDE ESTÁ PYS REALMENTE? (SERP en vivo, profundidad 100, México)")
print("=" * 96)
print(f"{'vol/mes':>8} {'PYS':>6} {'exoma':>6} {'peptide':>7}  {'situación':<20} keyword / ficha")
print("-" * 96)
for f in filas:
    print(f"{f['volumen']:>8} {str(f['pys'] or '—'):>6} {str(f['exoma'] or '—'):>6} "
          f"{str(f['peptide'] or '—'):>7}  {f['tramo']:<20} {f['keyword']}  [{f['ficha']}]")

print("\n" + "=" * 96)
resumen = {}
for f in filas:
    resumen.setdefault(f["tramo"], []).append(f)
for t in ("top-10", "EMPUJABLE (11-20)", "EMPUJABLE (21-30)", "lejos (31-50)",
          "muy lejos (51+)", "desde cero"):
    g = resumen.get(t) or []
    if g:
        print(f"{t:<22} {len(g):>2} keywords · {sum(x['volumen'] for x in g):>7,}/mes")

empujable = [f for f in filas if "EMPUJABLE" in f["tramo"]]
print(f"\nEmpujable (11-30): {len(empujable)} keywords, "
      f"{sum(f['volumen'] for f in empujable):,}/mes")
sin_ficha = [f for f in filas if f["ficha"].startswith("—")]
if sin_ficha:
    print(f"\nHuecos de catálogo (volumen sin producto que vender):")
    for f in sorted(sin_ficha, key=lambda x: -x["volumen"]):
        print(f"   {f['volumen']:>7}/mes  {f['keyword']}")

json.dump(filas, open(DATA / "cluster-pys-veredicto.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
