#!/usr/bin/env python3
"""FASE 1 · BLOQUE B — auditoría de veracidad de las referencias de las 14 fichas.

SOLO DIAGNÓSTICO. No escribe nada en WordPress ni en WooCommerce.

Comprueba, por ficha:
  1. Cada PMID contra eutils/esummary: ¿existe?
  2. Autor, revista y año de eutils contra lo que dice el texto de la ficha.
  3. Enlaces externos con lógica 403-aware: solo 404/410 y fallos de red cuentan
     como roto; 403/5xx = no comprobable (bloqueo de bots de las revistas).
  4. PMID que existe pero cuyo estudio no nombra la molécula exacta que vende la
     ficha (el error Tβ4 completa de 43 aa vs TB-500, fragmento de 7 aa).

    py -3 scripts/audita_referencias_fichas.py
"""
from __future__ import annotations

import html as H
import json
import pathlib
import re
import time
from collections import Counter

import requests
from requests.auth import HTTPBasicAuth

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Las 14 fichas reescritas (docs/playbook-fichas-pys.md, orden de ejecución).
# molecula: términos que el estudio DEBE nombrar para considerarse de la
# molécula exacta. `evita`: términos que delatan la molécula equivocada.
FICHAS = {
    # TB-500 es un fragmento de 7 aminoácidos de la timosina beta-4 (43 aa).
    # Un estudio sobre Tβ4 COMPLETA no es un estudio sobre TB-500: por eso
    # `thymosin beta4` va en `evita`, no en `molecula` (error del playbook).
    795:  {"nombre": "BPC-157 + TB-500",
           "molecula": ["bpc-157", "bpc 157", "bpc157",
                        "body protection compound", "body-protective compound",
                        "tb-500", "tb 500"],
           "evita": ["thymosin beta4", "thymosin beta-4", "thymosin beta 4",
                     "thymosin peptide"]},
    1699: {"nombre": "Selank", "molecula": ["selank", "tuftsin"], "evita": []},
    2240: {"nombre": "Cagrilintida",
           "molecula": ["cagrilintide", "cagrilintida", "amylin", "cagrisema"],
           "evita": []},
    19:   {"nombre": "Retatrutida",
           "molecula": ["retatrutide", "retatrutida", "ly3437943",
                        "triple agonist"], "evita": []},
    799:  {"nombre": "Agua Bacteriostática",
           "molecula": ["bacteriostatic", "benzyl alcohol", "water for injection",
                        "sterile", "excipient", "preservative"], "evita": []},
    790:  {"nombre": "MOTS-c 10mg", "molecula": ["mots-c", "mots c",
                                                 "mitochondrial-derived peptide"],
           "evita": []},
    793:  {"nombre": "MOTS-c 40mg", "molecula": ["mots-c", "mots c",
                                                 "mitochondrial-derived peptide"],
           "evita": []},
    2232: {"nombre": "CJC-1295 + Ipamorelina",
           "molecula": ["cjc-1295", "cjc 1295", "ipamorelin", "ghrh",
                        "growth hormone-releasing", "growth hormone releasing",
                        "secretagogue"], "evita": []},
    1128: {"nombre": "IGF-1 LR3",
           "molecula": ["igf-1", "igf-i", "insulin-like growth factor",
                        "mecasermin"], "evita": []},
    2231: {"nombre": "Sermorelina", "molecula": ["sermorelin", "grf(1-29)", "ghrh",
                        # sermorelina ES el GHRH(1-29): los títulos lo escriben así
                        "growth hormone-releasing hormone", "gh-releasing hormone",
                        "growth hormone releasing hormone"], "evita": []},
    2230: {"nombre": "Timosina Alfa-1",
           "molecula": ["thymosin alpha", "thymalfasin", "talpha1", "ta1",
                        "thymosin α1", "thymosin α"],
           "evita": ["thymosin beta"]},
    1525: {"nombre": "Tirzepatida 30mg",
           "molecula": ["tirzepatide", "tirzepatida", "ly3298176",
                        "gip", "dual agonist"], "evita": []},
    1531: {"nombre": "Tirzepatida 60mg",
           "molecula": ["tirzepatide", "tirzepatida", "ly3298176",
                        "gip", "dual agonist"], "evita": []},
    1131: {"nombre": "NAD+",
           "molecula": ["nad+", "nad(+)", "nad⁺", "nicotinamide", "nmn",
                        "nicotinamide riboside", "sirtuin"], "evita": []},
}

REVISTAS = ["N Engl J Med", "NEJM", "Lancet", "JAMA", "Cell Metab", "Nature",
            "Science", "Diabetes", "J Clin Endocrinol", "Peptides", "Front",
            "Int J Mol Sci", "Br J Pharmacol", "Am J Physiol", "PLoS",
            "Obesity", "Endocrin", "Aging", "J Gerontol", "Antioxidants",
            "Nutrients", "Clin Pharmacol", "Eur J", "Mol Cell"]


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


def texto(frag):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", frag or ""))).strip()


def contexto_de(html, pos, ancho=340):
    """Bloque <li>/<p> que contiene la referencia — ahí van autor, revista y año."""
    ini = max(html.rfind("<li", 0, pos), html.rfind("<p", 0, pos))
    if ini < 0:
        ini = max(0, pos - ancho)
    fin = min([x for x in (html.find("</li>", pos), html.find("</p>", pos)) if x > 0]
              or [pos + ancho])
    return texto(html[ini:fin])


def esummary(pmids):
    """{pmid: registro} en lotes de 150."""
    out = {}
    pmids = list(pmids)
    for i in range(0, len(pmids), 150):
        lote = pmids[i:i + 150]
        r = requests.get(f"{EUTILS}/esummary.fcgi",
                         params={"db": "pubmed", "id": ",".join(lote),
                                 "retmode": "json"}, timeout=60)
        res = (r.json() or {}).get("result") or {}
        for p in lote:
            out[p] = res.get(p) or {}
        time.sleep(0.4)
    return out


def check_url(u):
    if "pubmed.ncbi.nlm.nih.gov" in u:
        return "pubmed", ""
    try:
        r = requests.get(u, headers=UA, timeout=25, allow_redirects=True)
        if r.status_code in (404, 410):
            return "ROTO", f"HTTP {r.status_code}"
        if r.status_code < 400:
            return "ok", f"HTTP {r.status_code}"
        return "no comprobable", f"HTTP {r.status_code}"
    except Exception as e:
        return "ROTO", f"red: {e.__class__.__name__}"


# ── recolecta ────────────────────────────────────────────────────────────────
# Las fichas NO enlazan a PubMed: citan en texto plano dentro de <li>, con el
# formato «Autor et al. <em>Título.</em> Revista, año. PMID NNNNNNNN.». Eso
# permite contrastar los CUATRO campos contra eutils, no solo la existencia.
RE_CITA = re.compile(
    r"<li[^>]*>\s*(?P<autor>[^<]{2,90}?)\s*<em>(?P<titulo>[\s\S]*?)</em>\s*"
    r"(?P<revista>[^,<]{2,60}),\s*(?P<anio>\d{4})\.\s*PMID[:\s]*(?P<pmid>\d+)",
    re.I)

fichas, todos_pmids = {}, set()
for pid, meta in FICHAS.items():
    r = requests.get(f"{SITE}/wp-json/wc/v3/products/{pid}", auth=AUTH, timeout=45)
    if r.status_code != 200:
        print(f"  ! {pid}: HTTP {r.status_code}")
        continue
    p = r.json()
    desc = p.get("description") or ""
    refs, vistos = [], set()
    for m in RE_CITA.finditer(desc):
        refs.append({"pmid": m.group("pmid"),
                     "autor": texto(m.group("autor")),
                     "titulo": texto(m.group("titulo")),
                     "revista": texto(m.group("revista")),
                     "anio": m.group("anio"),
                     "ctx": texto(m.group(0))})
        vistos.add(m.group("pmid"))
        todos_pmids.add(m.group("pmid"))
    # PMIDs citados en el cuerpo pero fuera de la lista de referencias
    for m in re.finditer(r"PMID[:\s]*(\d+)", desc):
        if m.group(1) not in vistos:
            vistos.add(m.group(1))
            todos_pmids.add(m.group(1))
            refs.append({"pmid": m.group(1), "autor": "", "titulo": "",
                         "revista": "", "anio": "",
                         "ctx": contexto_de(desc, m.start())})
    externos = sorted({u.split("?")[0] for u in
                       re.findall(r'href="(https?://[^"]+)"', desc)
                       if "peptidosysuplementos.mx" not in u})
    fichas[pid] = {"nombre": p.get("name"), "url": p.get("permalink"),
                   "palabras": len(texto(desc).split()), "refs": refs,
                   "externos": externos, "meta": meta}

print(f"fichas leídas: {len(fichas)}   PMIDs distintos: {len(todos_pmids)}   "
      f"citas totales: {sum(len(f['refs']) for f in fichas.values())}")
print("consultando PubMed...")
REG = esummary(todos_pmids)

# ── analiza ──────────────────────────────────────────────────────────────────
informe, resumen = [], Counter()
for pid, f in fichas.items():
    hallazgos = []
    for ref in f["refs"]:
        rec = REG.get(ref["pmid"]) or {}
        titulo = rec.get("title") or ""
        if not titulo:
            hallazgos.append({"pmid": ref["pmid"], "tipo": "PMID_INEXISTENTE",
                              "detalle": "eutils no devuelve registro",
                              "ctx": ref["ctx"][:200]})
            resumen["PMID_INEXISTENTE"] += 1
            continue
        autores = [a.get("name", "") for a in (rec.get("authors") or [])]
        ap1 = autores[0].split()[0] if autores else ""
        revista = rec.get("source") or ""
        anio = (rec.get("pubdate") or "")[:4]
        # PubMed trae dos fechas: la del número impreso (pubdate) y la
        # electrónica adelantada (epubdate). Citar cualquiera de las dos es
        # legítimo, así que solo se marca cuando la ficha no coincide con NINGUNA.
        anios_ok = {anio, (rec.get("epubdate") or "")[:4]} - {""}

        def norm(s):
            return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())

        # 1) autor: el apellido que cita la ficha vs el primer autor real
        if ref["autor"] and ap1:
            cit = re.sub(r"\s*(et al\.?|y col\.?)\s*$", "", ref["autor"]).strip()
            ap_cit = cit.split()[0] if cit else ""
            if ap_cit and ap_cit.lower() != ap1.lower():
                hallazgos.append({"pmid": ref["pmid"], "tipo": "AUTOR_DISCREPA",
                                  "detalle": f"ficha cita {ap_cit!r}; PubMed: {ap1!r}",
                                  "ctx": ref["ctx"][:200]})
                resumen["AUTOR_DISCREPA"] += 1
        # 2) año
        if ref["anio"] and anios_ok and ref["anio"] not in anios_ok:
            hallazgos.append({"pmid": ref["pmid"], "tipo": "ANIO_DISCREPA",
                              "detalle": f"ficha dice {ref['anio']}; PubMed: "
                                         f"{'/'.join(sorted(anios_ok))}",
                              "ctx": ref["ctx"][:200]})
            resumen["ANIO_DISCREPA"] += 1
        # 3) revista (comparación laxa: abreviaturas varían)
        if ref["revista"] and revista:
            a, b = norm(ref["revista"]), norm(revista)
            tok_a = [t for t in a.split() if len(t) > 2]
            if tok_a and not any(t in b for t in tok_a) and not a.split()[0] in b:
                hallazgos.append({"pmid": ref["pmid"], "tipo": "REVISTA_DISCREPA",
                                  "detalle": f"ficha dice {ref['revista']!r}; PubMed: {revista!r}",
                                  "ctx": ref["ctx"][:200]})
                resumen["REVISTA_DISCREPA"] += 1
        # 4) título
        if ref["titulo"] and titulo:
            ta = set(norm(ref["titulo"]).split()) - {"the", "of", "and", "in", "a", "for", "on"}
            tb = set(norm(titulo).split())
            if ta and len(ta & tb) / len(ta) < 0.6:
                hallazgos.append({"pmid": ref["pmid"], "tipo": "TITULO_DISCREPA",
                                  "detalle": f"ficha: {ref['titulo'][:70]!r} | PubMed: {titulo[:70]!r}",
                                  "ctx": ""})
                resumen["TITULO_DISCREPA"] += 1

        # 5) molécula exacta
        tl = titulo.lower()
        if not any(m in tl for m in f["meta"]["molecula"]):
            hallazgos.append({"pmid": ref["pmid"], "tipo": "MOLECULA_REVISAR",
                              "detalle": f"el título no nombra la molécula: {titulo[:110]!r}",
                              "ctx": ""})
            resumen["MOLECULA_REVISAR"] += 1
        for mala in f["meta"]["evita"]:
            if mala in tl:
                hallazgos.append({"pmid": ref["pmid"], "tipo": "MOLECULA_EQUIVOCADA",
                                  "detalle": f"el título nombra {mala!r}: {titulo[:110]!r}",
                                  "ctx": ""})
                resumen["MOLECULA_EQUIVOCADA"] += 1

    enlaces = []
    for u in f["externos"]:
        est, det = check_url(u)
        if est in ("ROTO", "no comprobable"):
            enlaces.append({"url": u, "estado": est, "detalle": det})
            resumen[f"ENLACE_{est.replace(' ', '_')}"] += 1

    informe.append({"id": pid, "nombre": f["nombre"], "url": f["url"],
                    "palabras": f["palabras"], "n_refs": len(f["refs"]),
                    "hallazgos": hallazgos, "enlaces": enlaces})

SAL = REPO / "docs" / "data" / "auditoria-referencias-fichas.json"
SAL.write_text(json.dumps({"fecha": time.strftime("%Y-%m-%d"),
                           "resumen": dict(resumen), "fichas": informe},
                          ensure_ascii=False, indent=1), encoding="utf-8")

print("\n" + "=" * 78)
print("RESUMEN:", dict(resumen) or "sin hallazgos")
print("=" * 78)
for f in informe:
    marca = "!" if (f["hallazgos"] or f["enlaces"]) else " "
    print(f"\n{marca} {f['id']:>5}  {f['nombre'][:36]:<38} {f['n_refs']:>3} refs "
          f"· {f['palabras']} palabras")
    for h in f["hallazgos"]:
        print(f"      [{h['tipo']}] PMID {h['pmid']} — {h['detalle']}")
    for e in f["enlaces"]:
        print(f"      [{e['estado']}] {e['detalle']}  {e['url'][:78]}")
print(f"\n-> {SAL}")
