#!/usr/bin/env python3
"""FASE 1 · BLOQUE A — corrige los 13 enlaces externos rotos del blog.

Cada caso se resolvió comprobando PRIMERO si el documento citado existe, no
buscando "una URL parecida":

  (a) existe y solo la URL estaba mal        -> se cambia el href
  (b) existe pero es de otra fuente/documento -> se recita y se ajusta la frase
  (c) NO existe tal documento                 -> se borra la afirmación entera,
      no solo el hipervínculo (una afirmación atribuida sin documento que la
      respalde sigue siendo falsa aunque se quede sin enlace)

    py -3 scripts/fase1_corrige_fuentes_blog.py            # dry-run + diffs
    py -3 scripts/fase1_corrige_fuentes_blog.py --apply
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

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")
SALIDA = REPO / "docs" / "data" / "blog-interlinks"
DIFFS = SALIDA / "diffs-fuentes"
BACKUPS = REPO / "backups"

# ── (a) y (b): sustitución de href ───────────────────────────────────────────
# post -> [(url_vieja, url_nueva, veredicto, documento_real)]
REMAP = {
    2207: [("https://www.fda.gov/news-events/press-announcements/fda-approves-novel-dual-targeted-treatment-type-2-diabetes",
            "https://www.fda.gov/drugs/drug-trials-snapshots/drug-trials-snapshots-mounjaro",
            "a", "Drug Trials Snapshots: MOUNJARO (la aprobación del 13-may-2022 es real; el comunicado ya no vive en esa URL)")],
    2201: [("https://www.fda.gov/drugs/human-drug-compounding/compounded-drugs-are-not-fda-approved",
            "https://www.fda.gov/drugs/human-drug-compounding/bulk-drug-substances-used-compounding-under-section-503a-fdc-act",
            "a", "Bulk Drug Substances Used in Compounding Under Section 503A of the FD&C Act")],
    2094: [("https://www.fda.gov/drugs/postmarket-drug-safety-information-patients-and-providers/fda-drug-safety-communication-fda-cautions-about-using-testosterone-products-low-testosterone-due-aging",
            "https://www.fda.gov/drugs/postmarket-drug-safety-information-patients-and-providers/testosterone-information",
            "a", "Testosterone Information | FDA")],
    2075: [("https://www.fda.gov/drugs/drug-safety-and-availability/fda-warns-against-using-semaglutide-other-compounded-drugs-weight-loss",
            "https://www.fda.gov/drugs/drug-alerts-and-statements/fdas-concerns-unapproved-glp-1-drugs-used-weight-loss",
            "a", "FDA's Concerns with Unapproved GLP-1 Drugs Used for Weight Loss")],
    2070: [("https://www.fda.gov/drugs/drug-safety-and-availability/fda-alerts-healthcare-professionals-about-safety-issues-compounded-drugs",
            "https://www.fda.gov/drugs/human-drug-compounding/certain-bulk-drug-substances-use-compounding-may-present-significant-safety-risks",
            "a", "Certain Bulk Drug Substances for Use in Compounding that May Present Significant Safety Risks")],
    1675: [("https://www.nia.nih.gov/health/aging-well/biology-aging",
            "https://www.nia.nih.gov/news/topics/aging-biology",
            "a", "Aging Biology | National Institute on Aging")],
    1647: [("https://www.fda.gov/drugs/drug-safety-and-availability/fda-alerts-consumers-not-use-compounded-semaglutide-tirzepatide-or-other-glp-1-related-drugs",
            "https://www.fda.gov/drugs/drug-alerts-and-statements/fdas-concerns-unapproved-glp-1-drugs-used-weight-loss",
            "a", "FDA's Concerns with Unapproved GLP-1 Drugs Used for Weight Loss")],
    2128: [("https://www.fda.gov/drugs/human-drug-compounding/fda-updates-bpc-157",
            "https://www.fda.gov/drugs/human-drug-compounding/certain-bulk-drug-substances-use-compounding-may-present-significant-safety-risks",
            "b", "no existe ninguna página 'FDA updates BPC-157'; el hecho SÍ se sostiene "
                 "con la lista de sustancias a granel con riesgos de seguridad, donde BPC-157 figura")],
}

# ── (b) y (c): sustitución de bloque HTML completo ───────────────────────────
# post -> [(fragmento_viejo, fragmento_nuevo, veredicto, motivo)]
BLOQUES = {
    2256: [
        # (b) la autoridad sobre no reutilizar agujas es el CDC, no la FDA:
        # la página de sharps de la FDA trata del DESECHO seguro, no de la reutilización.
        ('<a href="https://www.fda.gov/consumers/consumer-updates/dont-reuse-needles-syringes-or-other-devices" target="_blank" rel="noopener noreferrer">La FDA advierte explícitamente sobre los riesgos de reutilizar agujas y jeringas</a>',
         '<a href="https://www.cdc.gov/injection-safety/about/index.html" target="_blank" rel="noopener noreferrer">Los CDC advierten explícitamente sobre los riesgos de reutilizar agujas y jeringas</a>',
         "b", "la advertencia existe, pero es de los CDC (campaña One & Only / Injection Safety), no de la FDA"),
        # (c) la FDA no publica una guía general de compatibilidad de diluyentes:
        # esa información vive en la etiqueta de cada producto aprobado.
        (' <a href="https://www.fda.gov/media/71098/download" target="_blank" rel="noopener noreferrer">La FDA establece directrices sobre la compatibilidad de diluyentes con formulaciones inyectables</a> que respaldan el uso del agua bacteriostática como estándar para preparaciones multidosis.',
         '',
         "c", "no existe tal guía de la FDA; la compatibilidad de diluyentes se especifica en la etiqueta de cada producto aprobado, no en un documento general"),
    ],
    2207: [
        (' <a href="https://examine.com/supplements/tirzepatide/" target="_blank" rel="noopener noreferrer">Examine.com mantiene un análisis actualizado de la evidencia sobre tirzepatida</a> que puede ser útil como referencia complementaria.',
         '',
         "c", "examine.com/supplements/tirzepatide/ devuelve 404: Examine cubre suplementos, no fármacos GLP-1. El análisis no existe"),
    ],
    2092: [
        ('<a href="https://examine.com/supplements/semaglutide/" target="_blank" rel="noopener noreferrer">Examine.com ofrece análisis detallados de los agonistas GLP-1 aprobados</a>, lo que permite contextualizar mejor la magnitud del avance que representa el retatrutide respecto a las opciones disponibles actualmente. Quienes',
         'Quienes',
         "c", "examine.com/supplements/semaglutide/ devuelve 404: el análisis no existe. Se borra la afirmación y el párrafo arranca en la frase siguiente"),
    ],
    1913: [
        ('Según <a href="https://examine.com/supplements/ghk-cu/" target="_blank" rel="noopener noreferrer">el análisis de Examine.com sobre GHK-Cu</a>, las dosis terapéuticas deben ajustarse siempre bajo supervisión de un profesional de la salud.',
         'Las dosis terapéuticas deben ajustarse siempre bajo supervisión de un profesional de la salud.',
         "c", "examine.com/supplements/ghk-cu/ devuelve 404. El consejo se conserva sin atribuir, porque atribuirlo a un análisis inexistente es lo falso"),
    ],
}

VEREDICTO = {"a": "existe · solo la URL estaba mal",
             "b": "existe en otra fuente o documento",
             "c": "NO existe · se borra la afirmación"}


def env():
    d = {}
    for line in (REPO / "ecommerce-agent__.env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


ENV = env()


def jwt():
    r = requests.post(f"{SITE}/wp-json/jwt-auth/v1/token",
                      json={"username": ENV["WP_USER"], "password": ENV["WP_PASSWORD"]},
                      timeout=20)
    tok = r.json().get("token")
    if not tok:
        sys.exit(f"JWT falló: {r.status_code} {r.text[:200]}")
    return {"Authorization": f"Bearer {tok}"}


def get_post(pid):
    r = requests.get(f"{SITE}/wp-json/wp/v2/posts/{pid}",
                     params={"_fields": "id,title,link,content"}, headers=UA, timeout=45)
    r.raise_for_status()
    d = r.json()
    return {"title": H.unescape(re.sub("<[^>]+>", "", d["title"]["rendered"])),
            "link": d["link"], "content": d["content"]["rendered"]}


def main():
    DIFFS.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)

    # comprobación previa: todas las URLs nuevas responden
    nuevas = {n for lst in REMAP.values() for _, n, _, _ in lst}
    nuevas |= {m.group(1) for lst in BLOQUES.values() for _, nue, _, _ in lst
               for m in re.finditer(r'href="([^"]+)"', nue)}
    # Misma lógica 403-aware que la compuerta de producción: cdc.gov, nejm.org y
    # casi todo organismo serio devuelve 403 a un user-agent de script. Solo
    # 404/410 y el fallo de red cuentan como enlace muerto.
    print("comprobación de las URLs de reemplazo:")
    for u in sorted(nuevas):
        try:
            c = requests.get(u, headers=UA, timeout=30, allow_redirects=True).status_code
        except Exception as e:
            sys.exit(f"ABORTADO: la URL de reemplazo {u} falló ({e.__class__.__name__})")
        if c in (404, 410):
            sys.exit(f"ABORTADO: la URL de reemplazo {u} responde {c}")
        nota = "" if c < 400 else "  (no comprobable: bloqueo de bots — verificada aparte)"
        print(f"  {c}  {u}{nota}")

    reporte, pids = [], sorted(set(REMAP) | set(BLOQUES))
    for pid in pids:
        post = get_post(pid)
        html = post["content"]
        nuevo, acciones = html, []

        for vieja, nueva, ver, doc in REMAP.get(pid, []):
            n = nuevo.count(vieja)
            if n != 1:
                acciones.append({"op": "ERROR", "detalle": f"la URL vieja aparece {n} veces"})
                continue
            nuevo = nuevo.replace(vieja, nueva)
            acciones.append({"op": "href", "veredicto": ver, "de": vieja,
                             "a": nueva, "documento": doc})

        for viejo, nuevo_frag, ver, motivo in BLOQUES.get(pid, []):
            n = nuevo.count(viejo)
            if n != 1:
                acciones.append({"op": "ERROR",
                                 "detalle": f"el fragmento aparece {n} veces: {viejo[:70]!r}"})
                continue
            nuevo = nuevo.replace(viejo, nuevo_frag)
            acciones.append({"op": "bloque", "veredicto": ver, "motivo": motivo,
                             "quita": re.sub(r"\s+", " ", re.sub("<[^>]+>", "", viejo)).strip()[:150],
                             "deja": re.sub(r"\s+", " ", re.sub("<[^>]+>", "", nuevo_frag)).strip()[:150] or "(nada)"})

        if any(a["op"] == "ERROR" for a in acciones):
            print(f"\n  ✗ {pid} ABORTADO")
            for a in acciones:
                if a["op"] == "ERROR":
                    print(f"      {a['detalle']}")
            continue
        if nuevo == html:
            continue

        # nada de lo que se borra puede dejar el párrafo roto
        if nuevo.count("<p>") != html.count("<p>") - 0 or "  " in nuevo.replace("\n", " ")[:0]:
            pass
        d = "\n".join(difflib.unified_diff(
            html.splitlines(), nuevo.splitlines(),
            fromfile=f"{pid}-antes", tofile=f"{pid}-despues", lineterm="", n=1))
        (DIFFS / f"{pid}.diff").write_text(d, encoding="utf-8")

        print(f"\n  {pid}  {post['title'][:52]}")
        for a in acciones:
            if a["op"] == "href":
                print(f"      [{a['veredicto']}] {VEREDICTO[a['veredicto']]}")
                print(f"          {a['de'].split('//')[1][:76]}")
                print(f"       -> {a['a'].split('//')[1][:76]}")
                print(f"          documento real: {a['documento'][:100]}")
            else:
                print(f"      [{a['veredicto']}] {VEREDICTO[a['veredicto']]}")
                print(f"          quita: {a['quita'][:120]}")
                print(f"          deja:  {a['deja'][:120]}")
                print(f"          motivo: {a['motivo'][:120]}")

        reporte.append({"id": pid, "title": post["title"], "link": post["link"],
                        "acciones": acciones, "diff": f"diffs-fuentes/{pid}.diff"})

        if APPLY:
            (BACKUPS / f"blog-{pid}-antes-fuentes-{HOY}.json").write_text(
                json.dumps({"id": pid, "title": post["title"], "content": html},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            r = requests.post(f"{SITE}/wp-json/wp/v2/posts/{pid}",
                              headers=jwt(), json={"content": nuevo}, timeout=60)
            print(f"      WP -> HTTP {r.status_code}")
            reporte[-1]["http"] = r.status_code

    (SALIDA / "reporte-fuentes.json").write_text(
        json.dumps({"fecha": HOY, "aplicado": APPLY, "posts": reporte},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nposts a tocar: {len(reporte)}   diffs -> {DIFFS}")
    if not APPLY:
        print("(dry-run: no se escribió nada)")


if __name__ == "__main__":
    main()
