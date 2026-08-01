#!/usr/bin/env python3
"""Barrido de IDENTIDAD MOLECULAR sobre las 14 fichas. SOLO DIAGNÓSTICO.

El patrón que busca: **el compuesto estudiado no es el compuesto vendido**.
Es la misma clase de error que Tβ4 ≠ TB-500 y Epitalon ≠ epitalamina, y la
verificación de PMID NO lo detecta: el PMID existe, los cuatro campos coinciden,
y aun así el estudio es de otra molécula de la misma familia.

Para cada cita marca:
  VARIANTE  — el título nombra una variante distinta de la misma familia
  GENERICO  — el título habla de la familia/clase, no de la molécula concreta

El veredicto final NO lo da el script: imprime el contexto de la frase que cita
para leerlo a mano. La ficha 795 fue falso positivo precisamente porque el texto
explicitaba la distinción; sin leer el encuadre no se puede concluir.

    py -3 scripts/barrido_identidad_molecular.py
"""
from __future__ import annotations

import html as H
import json
import pathlib
import re
import time

import requests
from requests.auth import HTTPBasicAuth

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# exacta  : términos que prueban que el estudio ES de la molécula vendida
# variante: términos de una molécula DISTINTA de la misma familia (sospechoso)
# generico: términos de clase — el estudio puede ser de cualquier miembro
FICHAS = {
    795: {"nombre": "BPC-157 + TB-500",
          "exacta": ["bpc-157", "bpc 157", "bpc157", "body protection compound",
                     "body-protective compound", "tb-500", "tb 500"],
          "variante": ["thymosin beta4", "thymosin beta-4", "thymosin beta 4",
                       "thymosin peptide", "tβ4"],
          "generico": []},
    1699: {"nombre": "Selank", "exacta": ["selank"],
           "variante": ["semax", "tuftsin", "noopept"], "generico": []},
    2240: {"nombre": "Cagrilintida", "exacta": ["cagrilintide", "cagrilintida"],
           "variante": ["pramlintide", "cagrisema"], "generico": ["amylin", "amilina"]},
    19: {"nombre": "Retatrutida", "exacta": ["retatrutide", "retatrutida", "ly3437943"],
         "variante": ["tirzepatide", "semaglutide", "survodutide", "mazdutide",
                      "liraglutide", "dulaglutide"],
         "generico": ["triple agonist", "incretin", "glp-1 receptor agonist"]},
    799: {"nombre": "Agua Bacteriostática",
          "exacta": ["bacteriostatic", "benzyl alcohol", "alcohol bencílico"],
          "variante": ["sterile water for injection", "sodium chloride"],
          "generico": ["excipient", "preservative", "diluent"]},
    790: {"nombre": "MOTS-c 10mg", "exacta": ["mots-c", "mots c", "motsc"],
          "variante": ["humanin", "shlp", "romo1"],
          "generico": ["mitochondrial-derived peptide", "mitochondrial derived peptide"]},
    793: {"nombre": "MOTS-c 40mg", "exacta": ["mots-c", "mots c", "motsc"],
          "variante": ["humanin", "shlp"], "generico": ["mitochondrial-derived peptide"]},
    2232: {"nombre": "CJC-1295 (no-DAC) + Ipamorelina",
           "exacta": ["cjc-1295", "cjc 1295", "ipamorelin", "mod grf", "grf(1-29)"],
           # CJC-1295 CON DAC es otra molécula (vida media de días vs minutos):
           # el playbook ya documenta esa confusión.
           "variante": ["dac", "drug affinity complex", "tesamorelin",
                        "ghrp-2", "ghrp-6", "hexarelin", "sermorelin", "macimorelin"],
           "generico": ["growth hormone-releasing hormone", "growth hormone releasing",
                        "ghrh", "secretagogue", "ghs-r"]},
    1128: {"nombre": "IGF-1 LR3", "exacta": ["lr3", "long r3"],
           "variante": ["mecasermin", "des(1-3)", "igf-2", "igf-ii"],
           "generico": ["igf-1", "igf-i", "insulin-like growth factor"]},
    2231: {"nombre": "Sermorelina", "exacta": ["sermorelin", "grf(1-29)", "gh-rh(1-29)",
                                               "ghrh(1-29)", "ghrh (1-29)"],
           "variante": ["tesamorelin", "cjc-1295", "ghrp"],
           "generico": ["growth hormone-releasing hormone", "growth hormone releasing hormone",
                        "gh-releasing hormone", "ghrh"]},
    2230: {"nombre": "Timosina Alfa-1",
           "exacta": ["thymosin alpha", "thymosin α", "thymalfasin", "talpha1", "ta1"],
           "variante": ["thymosin beta", "thymopentin", "thymulin"],
           "generico": ["thymic peptide", "thymosin"]},
    1525: {"nombre": "Tirzepatida 30mg", "exacta": ["tirzepatide", "tirzepatida", "ly3298176"],
           "variante": ["semaglutide", "dulaglutide", "retatrutide", "liraglutide"],
           "generico": ["gip", "dual agonist", "incretin", "glp-1"]},
    1531: {"nombre": "Tirzepatida 60mg", "exacta": ["tirzepatide", "tirzepatida", "ly3298176"],
           "variante": ["semaglutide", "dulaglutide", "retatrutide"],
           "generico": ["gip", "dual agonist", "incretin", "glp-1"]},
    1131: {"nombre": "NAD+", "exacta": ["nad+", "nad(+)", "nad⁺", "nad "],
           # NMN y NR son PRECURSORES, no NAD+: un ensayo de NR no es un ensayo de NAD+
           "variante": ["nicotinamide mononucleotide", "nmn",
                        "nicotinamide riboside", "niagen", "nicotinamide adenine dinucleotide phosphate"],
           "generico": ["sirtuin", "nicotinamide"]},
}


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
RE_CITA = re.compile(
    r"<li[^>]*>\s*(?P<autor>[^<]{2,90}?)\s*<em>(?P<titulo>[\s\S]*?)</em>\s*"
    r"(?P<revista>[^,<]{2,60}),\s*(?P<anio>\d{4})\.\s*PMID[:\s]*(?P<pmid>\d+)", re.I)


def texto(f):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", f or ""))).strip()


def usos(desc, pmid):
    """Frases del cuerpo (fuera de la lista de referencias) que citan ese PMID."""
    out = []
    for m in re.finditer(re.escape(pmid), desc):
        ini = max(desc.rfind("<p", 0, m.start()), desc.rfind("<td", 0, m.start()),
                  desc.rfind("<li", 0, m.start()))
        fin = min([x for x in (desc.find("</p>", m.start()), desc.find("</td>", m.start()),
                               desc.find("</li>", m.start())) if x > 0] or [m.start() + 300])
        t = texto(desc[ini:fin])
        if t.startswith(("Hsieh", "Philp", "He L", "Ruff", "Nguyen")) or " PMID " in t[:60]:
            continue                                   # es la propia lista de referencias
        if t and t not in out:
            out.append(t)
    return out


def esummary(pmids):
    out, pmids = {}, list(pmids)
    for i in range(0, len(pmids), 150):
        lote = pmids[i:i + 150]
        r = requests.get(f"{EUTILS}/esummary.fcgi",
                         params={"db": "pubmed", "id": ",".join(lote), "retmode": "json"},
                         timeout=60)
        res = (r.json() or {}).get("result") or {}
        out.update({p: res.get(p) or {} for p in lote})
        time.sleep(0.4)
    return out


datos, todos = {}, set()
for pid, cfg in FICHAS.items():
    r = requests.get(f"{SITE}/wp-json/wc/v3/products/{pid}", auth=AUTH, timeout=45)
    if r.status_code != 200:
        continue
    desc = (r.json() or {}).get("description") or ""
    refs = [{"pmid": m.group("pmid"), "titulo_ficha": texto(m.group("titulo")),
             "autor": texto(m.group("autor"))} for m in RE_CITA.finditer(desc)]
    for x in refs:
        todos.add(x["pmid"])
    datos[pid] = {"desc": desc, "refs": refs}

print(f"fichas: {len(datos)}   PMIDs: {len(todos)}\nconsultando PubMed...\n")
REG = esummary(todos)

informe, n_flags = [], 0
for pid, cfg in FICHAS.items():
    if pid not in datos:
        continue
    flags = []
    for ref in datos[pid]["refs"]:
        rec = REG.get(ref["pmid"]) or {}
        tl = (rec.get("title") or "").lower()
        if not tl:
            continue
        exacta = any(t in tl for t in cfg["exacta"])
        variante = [t for t in cfg["variante"] if t in tl]
        generico = any(t in tl for t in cfg["generico"])
        if exacta:
            continue                                   # es la molécula vendida
        tipo = "VARIANTE" if variante else ("GENERICO" if generico else "SIN_MOLECULA")
        flags.append({"pmid": ref["pmid"], "tipo": tipo,
                      "variante_detectada": variante,
                      "titulo": rec.get("title", ""),
                      "revista": rec.get("source", ""),
                      "anio": (rec.get("pubdate") or "")[:4],
                      "usos": usos(datos[pid]["desc"], ref["pmid"])})
    n_flags += len(flags)
    informe.append({"id": pid, "nombre": cfg["nombre"],
                    "n_refs": len(datos[pid]["refs"]), "flags": flags})

SAL = REPO / "docs" / "data" / "barrido-identidad-molecular.json"
SAL.write_text(json.dumps({"fecha": time.strftime("%Y-%m-%d"), "fichas": informe},
                          ensure_ascii=False, indent=1), encoding="utf-8")

print("=" * 96)
print(f"{n_flags} citas marcadas para lectura humana (NO son veredictos)")
print("=" * 96)
for f in informe:
    marca = "!" if f["flags"] else " "
    print(f"\n{marca} {f['id']:>5}  {f['nombre'][:34]:<36} {f['n_refs']:>3} refs · "
          f"{len(f['flags'])} marcadas")
    for fl in f["flags"]:
        var = f" [{', '.join(fl['variante_detectada'])}]" if fl["variante_detectada"] else ""
        print(f"      {fl['tipo']}{var}  PMID {fl['pmid']} · {fl['revista']} {fl['anio']}")
        print(f"         título: {fl['titulo'][:104]}")
        for u in fl["usos"][:2]:
            print(f"         se usa: {u[:190]}")
print(f"\n-> {SAL}")
