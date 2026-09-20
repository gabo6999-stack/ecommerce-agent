#!/usr/bin/env python3
"""FASE 4c -- reauditoria en vivo del año citado (Vancouver: pubdate impreso,
o epubdate si no hay impreso) contra PMID, sobre las 14 fichas, en TODO el
HTML crudo -- no solo la lista de referencias en <li> (eso es lo que dejó
pasar los 4 años malos de la 1131: se citan tambien inline, en prosa, y el
Bloque A de Fase 2 solo tocaba el formato de lista). Patron: cualquier año de
4 digitos seguido (con · o . de separador) de "PMID NNNNN", en cualquier
parte del documento. Cada coincidencia se verifica contra eutils EN VIVO,
nunca contra un resultado guardado.

    py -3 scripts/fase4c_reaudita_corrige_anios.py            # dry-run + reporte
    py -3 scripts/fase4c_reaudita_corrige_anios.py --apply
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time

import requests
from requests.auth import HTTPBasicAuth

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
WC = f"{SITE}/wp-json/wc/v3/products"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")
BACKUPS = REPO / "backups"
DIFFS = REPO / "docs" / "data" / "fase4c-diffs"

FICHAS = [795, 1699, 2240, 19, 799, 790, 793, 2232, 1128, 2231, 2230, 1525, 1531, 1131]
_SOLO = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--solo=")), None)
FICHAS_APLICAR = {int(x) for x in _SOLO.split(",")} if _SOLO else set(FICHAS)

# año-de-4-dígitos, separador (·, punto, o nada), "PMID", opcional : o espacio, dígitos
RE_CITA_ANIO = re.compile(r"(?P<anio>(?:19|20)\d{2})\s*[·.]?\s*PMID[:\s]*(?P<pmid>\d+)", re.I)


def env():
    d = {}
    for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


ENV = env()
AUTH = HTTPBasicAuth(ENV["WC_CONSUMER_KEY"], ENV["WC_CONSUMER_SECRET"])


def get_producto(pid):
    r = requests.get(f"{WC}/{pid}", auth=AUTH, timeout=45)
    r.raise_for_status()
    return r.json()


def anios_reales(pmids):
    """{pmid: {'pubdate':Y,'epubdate':Y}} -- consulta EN VIVO, sin caché de resultado previo."""
    out = {}
    pmids = sorted(set(pmids))
    for i in range(0, len(pmids), 150):
        lote = pmids[i:i + 150]
        r = requests.get(f"{EUTILS}/esummary.fcgi",
                         params={"db": "pubmed", "id": ",".join(lote), "retmode": "json"},
                         timeout=60)
        res = (r.json() or {}).get("result") or {}
        for p in lote:
            rec = res.get(p) or {}
            out[p] = {"pubdate": (rec.get("pubdate") or "")[:4],
                      "epubdate": (rec.get("epubdate") or "")[:4]}
        time.sleep(0.4)
    return out


def actualiza_producto(pid, nuevo_html):
    p = get_producto(pid)
    meta = {m["key"]: m["value"] for m in p.get("meta_data", [])}
    es_elementor = "_elementor_data" in meta and meta.get("_elementor_edit_mode") == "builder"
    payload = {"description": nuevo_html}
    if es_elementor:
        ed = json.loads(meta["_elementor_data"]) if isinstance(meta["_elementor_data"], str) else meta["_elementor_data"]
        tocados = []

        def inyectar(nodos):
            for n in nodos:
                s = n.get("settings") or {}
                if n.get("widgetType") == "text-editor" and "editor" in s:
                    s["editor"] = nuevo_html
                    tocados.append(n.get("id"))
                inyectar(n.get("elements") or [])

        inyectar(ed)
        if len(tocados) != 1:
            return {"error": f"se esperaba 1 widget text-editor, hay {len(tocados)}"}
        payload["meta_data"] = [
            {"key": "_elementor_data", "value": json.dumps(ed, ensure_ascii=False)},
            {"key": "_elementor_element_cache", "value": ""},
        ]
    r = requests.put(f"{WC}/{pid}", auth=AUTH, timeout=60, json=payload)
    return {"status": r.status_code, "elementor": es_elementor, "ok": r.status_code == 200}


def main():
    DIFFS.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)

    fichas_data, todos_pmids = {}, set()
    for pid in FICHAS:
        p = get_producto(pid)
        desc = p.get("description") or ""
        matches = list(RE_CITA_ANIO.finditer(desc))
        fichas_data[pid] = {"nombre": p.get("name"), "permalink": p.get("permalink"), "desc": desc, "matches": matches}
        todos_pmids |= {m.group("pmid") for m in matches}
        print(f"  {pid:>5}  {p.get('name','')[:40]:<40}  {len(matches)} cita(s) año+PMID")

    print(f"\ntotal fichas: {len(fichas_data)}   citas con año detectadas: "
         f"{sum(len(f['matches']) for f in fichas_data.values())}   PMIDs distintos: {len(todos_pmids)}")
    print("consultando pubdate/epubdate EN VIVO contra eutils (sin caché)...")
    ANIOS = anios_reales(todos_pmids)

    reporte = {"fecha": HOY, "aplicado": APPLY, "discrepancias": [], "backup": {}}
    total_disc = 0

    for pid, f in fichas_data.items():
        desc = f["desc"]
        nuevo = desc
        cambios = []
        for m in sorted(f["matches"], key=lambda x: x.start(), reverse=True):
            pmid, actual = m.group("pmid"), m.group("anio")
            real = ANIOS.get(pmid, {})
            validos = {y for y in (real.get("pubdate"), real.get("epubdate")) if y}
            if not validos:
                cambios.append({"pmid": pmid, "declarado": actual, "error": "sin pubdate/epubdate en eutils"})
                continue
            if actual not in validos:
                ini, fin = m.span("anio")
                correcto = real.get("pubdate") or real.get("epubdate")
                nuevo = nuevo[:ini] + correcto + nuevo[fin:]
                cambios.append({"pmid": pmid, "declarado": actual, "correcto": correcto,
                               "validos": sorted(validos), "contexto": desc[max(0, m.start() - 60):m.end() + 10]})

        reales_cambios = [c for c in cambios if "correcto" in c]
        if reales_cambios:
            total_disc += len(reales_cambios)
            print(f"\n  FICHA {pid} — {f['nombre']}: {len(reales_cambios)} discrepancia(s)")
            for c in reales_cambios:
                print(f"      PMID {c['pmid']}: declara {c['declarado']} -> correcto {c['correcto']} (válidos: {c['validos']})")
            errores = [c for c in cambios if "error" in c]
            for c in errores:
                print(f"      ⚠ PMID {c['pmid']}: {c['error']}")

            if nuevo != desc:
                d_txt = "\n".join(__import__("difflib").unified_diff(
                    desc.splitlines(), nuevo.splitlines(), fromfile=f"{pid}-antes", tofile=f"{pid}-despues", lineterm="", n=1))
                (DIFFS / f"{pid}.diff").write_text(d_txt, encoding="utf-8")

                if APPLY and pid in FICHAS_APLICAR:
                    BACKUPS.mkdir(exist_ok=True)
                    (BACKUPS / f"ficha-{pid}-antes-fase4c-{HOY}.json").write_text(
                        json.dumps({"id": pid, "nombre": f["nombre"], "description": desc}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
                    res = actualiza_producto(pid, nuevo)
                    print(f"      -> aplicado: {res}")
                    reporte["backup"][str(pid)] = f"backups/ficha-{pid}-antes-fase4c-{HOY}.json"

            reporte["discrepancias"].append({"id": pid, "nombre": f["nombre"], "cambios": reales_cambios})

    print(f"\n=== TOTAL: {total_disc} discrepancia(s) de año encontradas en {len(reporte['discrepancias'])} ficha(s) de {len(FICHAS)} ===")

    if APPLY and reporte["discrepancias"]:
        print("\nverificación en vivo...")
        time.sleep(3)
        for item in reporte["discrepancias"]:
            pid = item["id"]
            if pid not in FICHAS_APLICAR:
                continue
            perma = fichas_data[pid]["permalink"]
            r = requests.get(f"{perma}?nc={int(time.time())}", headers=UA, timeout=40)
            ok = all(c["correcto"] in r.text for c in item["cambios"])
            print(f"  {pid}: HTTP {r.status_code}  años nuevos presentes: {'OK' if ok else 'FALTA VERIFICAR A MANO'}")

    (REPO / "docs" / "data" / f"fase4c-reauditoria-anios-{HOY}.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nreporte -> docs/data/fase4c-reauditoria-anios-{HOY}.json")


if __name__ == "__main__":
    main()
