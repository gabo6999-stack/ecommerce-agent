#!/usr/bin/env python3
"""FASE 2 · BLOQUES A y B — correcciones de contenido en las 14 fichas.

BLOQUE A — año de publicación. Reemplaza el año citado por el año real
(convención Vancouver: impreso/`pubdate`, o `epubdate` si no hay impreso). Las
39 discrepancias detectadas se dividen en:
  · 33 que coinciden con `History[medline]` (fecha de INDEXACIÓN, no de
    publicación) → corrección en lote, mecánica, al año real.
  · 5 sin explicación en ningún campo de PubMed → corregidas a mano una por
    una, con el año verificado contra el registro completo.

BLOQUE B — ficha 1128 (IGF-1 LR3): elimina las 3 citas que NO son de
long(R3)-IGF-1 (33938236, 36499281, 36091374 — todas de IGF-1 nativo o
recombinante). Conserva 10370861 y 9488001 (sí son de LR3). Reporta, sin
reescribir, cualquier afirmación del cuerpo que quede sin la cita que la
sostenía.

Respeta el mecanismo de publicación de cada ficha (Elementor vs plano) descrito
en docs/playbook-fichas-pys.md: en Elementor, el HTML corregido se escribe en
el widget text-editor de `_elementor_data` (vaciando `_elementor_element_cache`)
Y se sincroniza `description`; en plano, solo `description`.

    py -3 scripts/fase2_corrige_fichas.py            # dry-run + diffs
    py -3 scripts/fase2_corrige_fichas.py --apply
"""
from __future__ import annotations

import difflib
import html as H
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
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")
SALIDA = REPO / "docs" / "data"
DIFFS = REPO / "docs" / "data" / "fase2-diffs"
BACKUPS = REPO / "backups"

FICHAS = [795, 1699, 2240, 19, 799, 790, 793, 2232, 1128, 2231, 2230, 1525, 1531, 1131]

# ── Bloque A: los 5 sin explicación en ningún campo de PubMed ────────────────
# Verificados a mano contra el historial completo de eutils (received/accepted/
# revised/pubmed/medline/entrez + JournalIssue PubDate). Ninguno coincide con
# el año citado por la ficha; el año real es el que declara la propia revista.
ANIO_MANUAL = {
    "36091374": "2022",   # IGF-1 LR3 — todos los campos de PubMed dicen 2022
    "18031173": "1999",   # Sermorelina — JournalIssue=1999; indexado a MEDLINE en 2007
    "1481803":  "1992",   # Agua bacteriostática — todos los campos dicen 1992
    "39676787": "2024",   # Cagrilintida — todos los campos dicen 2024
    "40094000": "2025",   # Retatrutida — todos los campos dicen 2025
}

# ── Bloque B: citas de IGF-1 LR3 que en realidad son de IGF-1 nativo ─────────
# CORREGIDO tras leer el ABSTRACT completo (no solo el título) de las 3
# candidatas de la resolución médica original:
#   · 33938236 — el título dice "IGF-1 infusion", pero el abstract especifica
#     que el compuesto infundido fue "IGF-1 LR3 (IGF-1, n=8), an analog of
#     IGF-1 with low affinity for IGF binding proteins". SÍ es LR3.
#   · 36499281 — el título es de glicosilación en células CHO, pero el
#     abstract dice "upon IGF-1R ligand (IGF-1 LR3) stimulation". SÍ es LR3.
#   · 36091374 — el abstract dice explícitamente que desarrollaron un IGF-1
#     recombinante OVINO como ALTERNATIVA a LR3 porque "the peptide sequences
#     for LR3 IGF-1 and sheep IGF-1 also differ". Esta SÍ es otra molécula.
# Solo 36091374 se elimina. 33938236 y 36499281 se conservan — el título por
# sí solo no basta para juzgar identidad molecular; hace falta el abstract.
IGF1_A_QUITAR = {"36091374"}
IGF1_A_CONSERVAR = {"10370861", "9488001", "33938236", "36499281"}

RE_CITA = re.compile(
    r"<li[^>]*>\s*(?P<autor>[^<]{2,90}?)\s*<em>(?P<titulo>[\s\S]*?)</em>\s*"
    r"(?P<revista>[^,<]{2,60}),\s*(?P<anio>\d{4})\.\s*PMID[:\s]*(?P<pmid>\d+)\.?\s*</li>",
    re.I)


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


def texto(f):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", f or ""))).strip()


def get_producto(pid):
    r = requests.get(f"{WC}/{pid}", auth=AUTH, timeout=45)
    r.raise_for_status()
    return r.json()


def anio_real(pmids):
    """{pmid: año Vancouver} = pubdate (impreso) o epubdate si no hay impreso."""
    out = {}
    ids = [p for p in pmids if p not in ANIO_MANUAL]
    for i in range(0, len(ids), 150):
        lote = ids[i:i + 150]
        r = requests.get(f"{EUTILS}/esummary.fcgi",
                         params={"db": "pubmed", "id": ",".join(lote), "retmode": "json"},
                         timeout=60)
        res = (r.json() or {}).get("result") or {}
        for p in lote:
            rec = res.get(p) or {}
            y = (rec.get("pubdate") or "")[:4] or (rec.get("epubdate") or "")[:4]
            out[p] = y
        time.sleep(0.4)
    out.update(ANIO_MANUAL)
    return out


def actualiza_producto(pid, nuevo_html):
    """Respeta el mecanismo Elementor/plano del playbook."""
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
    return {"status": r.status_code, "elementor": es_elementor,
            "ok": r.status_code == 200}


def verifica_en_vivo(permalink, debe_contener, no_debe_contener):
    time.sleep(3)
    r = requests.get(f"{permalink}?nc={int(time.time())}", headers=UA, timeout=40)
    ok_si = all(s in r.text for s in debe_contener)
    ok_no = all(s not in r.text for s in no_debe_contener)
    return ok_si and ok_no, r.status_code


def main():
    DIFFS.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)

    # ── recolecta todas las citas de las 14 fichas ───────────────────────────
    fichas_data, todos_pmids = {}, set()
    for pid in FICHAS:
        p = get_producto(pid)
        desc = p.get("description") or ""
        matches = list(RE_CITA.finditer(desc))
        fichas_data[pid] = {"nombre": p.get("name"), "permalink": p.get("permalink"),
                            "desc": desc, "matches": matches}
        todos_pmids |= {m.group("pmid") for m in matches}

    print(f"fichas: {len(fichas_data)}   citas parseadas: "
          f"{sum(len(f['matches']) for f in fichas_data.values())}   "
          f"PMIDs distintos: {len(todos_pmids)}")
    print("consultando pubdate/epubdate en eutils...")
    ANIOS = anio_real(todos_pmids)

    reporte = {"fecha": HOY, "aplicado": APPLY, "bloqueA": [], "bloqueB": []}

    for pid, f in fichas_data.items():
        desc = f["desc"]
        nuevo = desc
        cambios_a, quitar_b, huerfanas_b = [], [], []

        # ── BLOQUE A: corrige año, de atrás hacia adelante para no mover offsets
        for m in sorted(f["matches"], key=lambda x: x.start(), reverse=True):
            pmid = m.group("pmid")
            actual = m.group("anio")
            correcto = ANIOS.get(pmid)
            if not correcto:
                cambios_a.append({"pmid": pmid, "error": "sin año verificable en eutils"})
                continue
            if actual != correcto:
                ini, fin = m.span("anio")
                nuevo = nuevo[:ini] + correcto + nuevo[fin:]
                cambios_a.append({"pmid": pmid, "de": actual, "a": correcto,
                                  "medline_match": pmid not in ANIO_MANUAL})

        # ── BLOQUE B: solo ficha 1128 — quita las 3 citas de IGF-1 nativo
        if pid == 1128:
            texto_sin_citas = texto(nuevo)
            for m in sorted(RE_CITA.finditer(nuevo), key=lambda x: x.start(), reverse=True):
                if m.group("pmid") in IGF1_A_QUITAR:
                    quitar_b.append({"pmid": m.group("pmid"),
                                     "cita": texto(m.group(0))})
                    nuevo = nuevo[:m.start()] + nuevo[m.end():]
            # ¿alguna frase del CUERPO (fuera de la lista de referencias) sigue
            # citando esos PMID? Si sí, queda huérfana: se reporta, no se toca.
            for pmid in IGF1_A_QUITAR:
                for mm in re.finditer(re.escape(pmid), nuevo):
                    ini = max(nuevo.rfind("<p", 0, mm.start()), nuevo.rfind("<li", 0, mm.start()))
                    fin = min([x for x in (nuevo.find("</p>", mm.start()),
                                          nuevo.find("</li>", mm.start())) if x > 0] or [mm.start() + 200])
                    frag = texto(nuevo[ini:fin])
                    huerfanas_b.append({"pmid": pmid, "frase": frag})

        if nuevo == desc:
            continue

        d = "\n".join(difflib.unified_diff(
            desc.splitlines(), nuevo.splitlines(),
            fromfile=f"{pid}-antes", tofile=f"{pid}-despues", lineterm="", n=1))
        (DIFFS / f"{pid}.diff").write_text(d, encoding="utf-8")

        print(f"\n  {pid}  {f['nombre'][:44]}")
        if cambios_a:
            hechos = [c for c in cambios_a if "de" in c]
            errores = [c for c in cambios_a if "error" in c]
            print(f"      Bloque A: {len(hechos)} año(s) corregido(s)"
                 + (f", {len(errores)} error(es)" if errores else ""))
            for c in hechos:
                tipo = "lote(medline)" if c["medline_match"] and c["pmid"] not in ANIO_MANUAL else "manual"
                print(f"        PMID {c['pmid']}  {c['de']} -> {c['a']}  [{tipo}]")
            for c in errores:
                print(f"        ✗ PMID {c['pmid']}: {c['error']}")
        if quitar_b:
            print(f"      Bloque B: {len(quitar_b)} cita(s) de IGF-1 nativo eliminada(s)")
            for c in quitar_b:
                print(f"        - PMID {c['pmid']}: {c['cita'][:110]}")
        if huerfanas_b:
            print(f"      ⚠ {len(huerfanas_b)} mención(es) en el CUERPO siguen citando un PMID eliminado:")
            for h in huerfanas_b:
                print(f"        ! PMID {h['pmid']}: {h['frase'][:180]}")

        reporte["bloqueA"].append({"id": pid, "cambios": cambios_a})
        if pid == 1128:
            reporte["bloqueB"].append({"id": pid, "quitados": quitar_b,
                                       "huerfanas": huerfanas_b})

        if APPLY:
            (BACKUPS / f"ficha-{pid}-antes-fase2-{HOY}.json").write_text(
                json.dumps({"id": pid, "nombre": f["nombre"], "description": desc},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            res = actualiza_producto(pid, nuevo)
            print(f"      WP -> HTTP {res.get('status')} "
                 f"({'Elementor' if res.get('elementor') else 'plano'})")
            if not res.get("ok"):
                print(f"        ERROR: {res}")
                continue
            marcadores = [c["a"] for c in cambios_a if "a" in c][:2]
            ok, http = verifica_en_vivo(f["permalink"], marcadores, [])
            print(f"      verificación en vivo: HTTP {http}  marcadores presentes={ok}")

    (SALIDA / "reporte-fase2.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── reverificación final de las 129 citas ────────────────────────────────
    if APPLY:
        print("\n" + "=" * 78)
        print("reverificación final de las 129 citas...")
        total, mal = 0, 0
        for pid in FICHAS:
            p = get_producto(pid)
            for m in RE_CITA.finditer(p.get("description") or ""):
                total += 1
                pmid = m.group("pmid")
                correcto = ANIOS.get(pmid)
                if correcto and m.group("anio") != correcto:
                    mal += 1
                    print(f"  ✗ ficha {pid}  PMID {pmid}  sigue en {m.group('anio')}, debía {correcto}")
        print(f"total citas: {total}   con año incorrecto: {mal}")

    print(f"\ndiffs -> {DIFFS}")
    if not APPLY:
        print("(dry-run: no se escribió nada. Usa --apply para publicar)")


if __name__ == "__main__":
    main()
