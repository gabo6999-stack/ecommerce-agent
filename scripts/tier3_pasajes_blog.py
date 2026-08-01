#!/usr/bin/env python3
"""Tiers 3 y 4 — pasajes redactados para las fichas que no tenían mención.

A diferencia de `retro_interlinks_blog.py`, aquí el texto visible SÍ cambia: se
inserta un bloque nuevo. Por eso el invariante es otro: el contenido previo debe
sobrevivir intacto (el HTML anterior tiene que seguir siendo prefijo + sufijo
exactos alrededor del bloque insertado).

Compuertas antes de escribir (Fase 4 del playbook de fichas):
  · 6  — palabra prohibida y frase de refrigeración en transporte
  · 7  — ninguna afirmación clínica sin fuente enlazada
  · 1  — cada PMID citado existe y coincide autor/revista/año (verificado a mano
         contra eutils; los PMIDs usados van documentados abajo)
  · V2 — todo enlace nuevo, interno y externo, responde 200

    py -3 scripts/tier3_pasajes_blog.py            # dry-run
    py -3 scripts/tier3_pasajes_blog.py --apply
"""
from __future__ import annotations

import html as H
import json
import pathlib
import re
import sys
import time

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
UA = {"User-Agent": "Mozilla/5.0 (compatible; audit/1.0)"}
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")
SALIDA = REPO / "docs" / "data" / "blog-interlinks"
BACKUPS = REPO / "backups"

PROHIBIDAS = re.compile(r"farmacia|refrigeraci[oó]n.{0,40}transporte", re.I)

# Fuentes verificadas en PubMed el 2026-07-31 (esummary + abstract):
#   40544433  Garvey WT, Blüher M et al. N Engl J Med 2025 — REDEFINE 1.
#             CagriSema −20.4% vs placebo −3.0% a 68 sem; n=3417; GI 79.6/39.9%.
#   35975308  Kumar P, Liu C et al. J Gerontol A Biol Sci Med Sci 2023 — GlyNAC
#             en adultos mayores. OJO: suplementa PRECURSORES (glicina+NAC), no
#             glutatión; el texto lo dice así, no se le atribuye al producto.
#   25738459  Lee C, Zeng J et al. Cell Metab 2015 — MOTS-c en RATONES. El texto
#             marca explícitamente que la evidencia es preclínica.
F_CAGRI = "https://pubmed.ncbi.nlm.nih.gov/40544433/"
F_GSH = "https://pubmed.ncbi.nlm.nih.gov/35975308/"
F_MOTSC = "https://pubmed.ncbi.nlm.nih.gov/25738459/"
EXT = ' target="_blank" rel="noopener noreferrer"'

P_CAGRI = f'{SITE}/product/cagrilintida-10mg/'
P_GSH = f'{SITE}/product/glutation-1500mg/'
P_MOTSC = f'{SITE}/product/mots-c-10mg/'
P_BPC = f'{SITE}/product/bpc-157-tb-500-10-10mg/'

# (post_id, ancla_unica_donde_insertar_ANTES, bloque_html, fichas_enlazadas)
PASAJES = [
    (2211,
     "<h2>Uso como péptidos de investigación en México: contexto regulatorio</h2>",
     f"""<h2>Cagrilintida: el otro camino, sumar amilina en vez de otro receptor</h2>
<p>No toda la investigación avanza añadiendo receptores de incretina. La <a href="{P_CAGRI}">cagrilintida</a> es un análogo de amilina de acción prolongada —una hormona distinta, que el páncreas secreta junto con la insulina— y se administra combinada con semaglutida; a esa combinación se le conoce como CagriSema. En <a href="{F_CAGRI}"{EXT}>REDEFINE 1</a>, un ensayo fase 3a de 68 semanas con 3,417 adultos con sobrepeso u obesidad, el cambio medio de peso fue de <strong>−20.4% frente a −3.0% con placebo</strong>. Los eventos gastrointestinales fueron bastante más frecuentes que con placebo (79.6% contra 39.9%), en su mayoría transitorios y de intensidad leve a moderada. Es la vía que compite de frente con el triple agonismo, y lo hace por un mecanismo completamente distinto.</p>
""",
     [P_CAGRI, F_CAGRI]),

    (1727,
     "<h2>Preguntas Frecuentes sobre Semaglutida 2026</h2>",
     f"""<p><strong>Fuera de la tabla, por mecanismo distinto:</strong> la <a href="{P_CAGRI}">cagrilintida</a> no es un agonista GLP-1 sino un análogo de amilina de acción prolongada, y se investiga combinada con semaglutida bajo el nombre de CagriSema. En el ensayo fase 3a <a href="{F_CAGRI}"{EXT}>REDEFINE 1</a> (68 semanas, 3,417 participantes), esa combinación alcanzó un cambio medio de peso de −20.4% frente a −3.0% con placebo. Por eso aparece cada vez más en las conversaciones sobre semaglutida: no la sustituye, se le suma.</p>
""",
     [P_CAGRI, F_CAGRI]),

    (2096,
     "<h3>Ashwagandha,",
     f"""<h3>Glutatión: el antioxidante que fabrica tu propia célula</h3>
<p>El <strong>glutatión</strong> (GSH) es un tripéptido —glutamato, cisteína y glicina— y el principal antioxidante intracelular: no solo neutraliza radicales libres, también recicla otros antioxidantes y participa en la detoxificación hepática. Su concentración cae con la edad: un <a href="{F_GSH}"{EXT}>ensayo aleatorizado en adultos mayores</a> documentó déficit de glutatión, estrés oxidativo y disfunción mitocondrial frente a adultos jóvenes, y mejoría de esos marcadores al reponer sus precursores (glicina y N-acetilcisteína). Conviene ser preciso con el encuadre: ese ensayo suplementó los precursores, no glutatión directo. En la tienda en línea está disponible el <a href="{P_GSH}">Glutatión 1500mg</a> para quien ya cubre lo básico y quiere trabajar sobre la defensa antioxidante celular.</p>
""",
     [P_GSH, F_GSH]),

    (1675,
     "<h2>Conclusión: Construye tu protocolo de longevidad basado en ciencia</h2>",
     f"""<h3>Glutatión: el péptido de longevidad que casi nunca se nombra como tal</h3>
<p>Cierra bien esta lista un compuesto que rara vez entra en ella pese a serlo de pleno derecho: el <strong>glutatión</strong> es literalmente un tripéptido (glutamato-cisteína-glicina) y el principal antioxidante que la célula produce por su cuenta. Su concentración disminuye con la edad —un <a href="{F_GSH}"{EXT}>ensayo aleatorizado en adultos mayores</a> encontró déficit de glutatión, estrés oxidativo y disfunción mitocondrial frente a adultos jóvenes—, lo que lo coloca de lleno en la conversación del envejecimiento celular. Si quieres incorporarlo al protocolo, la ficha del <a href="{P_GSH}">Glutatión 1500mg</a> reúne la información de presentación y uso.</p>
""",
     [P_GSH, F_GSH]),

    (2190,
     "<p>Puedes consultar y descargar el <a",
     f"""<p>Varios de los compuestos catalogados corresponden a péptidos que documentamos en detalle en el catálogo: por ejemplo el <a href="{P_BPC}">combo BPC-157 + TB-500</a> entre los regenerativos, o el <a href="{P_MOTSC}">MOTS-c</a> entre los metabólicos. Contrastar la ficha con la entrada del dataset permite verificar nombre, alias y estructura molecular contra una referencia normalizada.</p>
""",
     [P_BPC, P_MOTSC]),

    (2075,
     "<h2>Suplementos Deportivos que Potencian la Pérdida de Grasa</h2>",
     f"""<h3>MOTS-c: la vía mitocondrial</h3>
<p>El <strong>MOTS-c</strong> no trabaja sobre el eje de la hormona de crecimiento, sino sobre el metabolismo mitocondrial: es un péptido codificado en el propio ADN de la mitocondria. En el trabajo original publicado en <a href="{F_MOTSC}"{EXT}>Cell Metabolism</a>, su administración en ratones mejoró la homeostasis metabólica y redujo la obesidad y la resistencia a la insulina inducidas por dieta. <strong>Vale la pena ser explícito con el encuadre: esa evidencia es preclínica</strong>, en animales, y no existen ensayos clínicos de pérdida de grasa en humanos que la repliquen. Con esa salvedad sobre la mesa, la ficha del <a href="{P_MOTSC}">MOTS-c 10mg</a> reúne el detalle de presentación y reconstitución.</p>
""",
     [P_MOTSC, F_MOTSC]),
]


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


def palabras(html):
    sin = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    return len(re.sub(r"\s+", " ", H.unescape(re.sub(r"(?s)<[^>]+>", " ", sin))).split())


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)
    reporte, fallos = [], []

    # --- compuerta V2: todos los enlaces nuevos son válidos (una sola vez).
    # PubMed devuelve 403 a un user-agent de script: es bloqueo de bots, no un
    # enlace muerto. Para esas URLs la comprobación correcta es preguntarle a
    # eutils si el PMID existe, que además es la fuente de la compuerta 1.
    urls = sorted({u for *_, us in PASAJES for u in us})
    print("compuerta V2 — enlaces nuevos:")
    for u in urls:
        pm = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", u)
        if pm:
            r = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "pubmed", "id": pm.group(1), "retmode": "json"},
                timeout=30)
            rec = (r.json().get("result") or {}).get(pm.group(1), {})
            ok = bool(rec.get("title"))
            print(f"  {'PMID OK' if ok else 'PMID ??'}  {u}")
            if ok:
                au = (rec.get("authors") or [{}])[0].get("name", "?")
                print(f"           {au} et al. · {rec.get('source','')} "
                      f"{rec.get('pubdate','')[:4]} · {rec.get('title','')[:66]}")
            else:
                fallos.append(f"PMID inexistente en {u}")
            continue
        c = requests.get(u, headers=UA, timeout=30, allow_redirects=True).status_code
        print(f"  {c}  {u}")
        if c != 200:
            fallos.append(f"enlace {u} -> {c}")
    if fallos:
        sys.exit(f"ABORTADO: {fallos}")

    for pid, ancla, bloque, _ in PASAJES:
        post = get_post(pid)
        html = post["content"]

        # --- compuerta 6: palabra prohibida en el bloque nuevo
        mal = PROHIBIDAS.findall(re.sub("<[^>]+>", " ", bloque))
        if mal:
            fallos.append(f"{pid}: palabra prohibida {mal}")
            print(f"  ✗ {pid} palabra prohibida: {mal}")
            continue

        # --- compuerta 7: toda cifra/afirmación clínica lleva fuente en el bloque
        if re.search(r"\d+(\.\d+)?%", bloque) and "pubmed.ncbi.nlm.nih.gov" not in bloque:
            fallos.append(f"{pid}: cifra clínica sin fuente")
            print(f"  ✗ {pid} cifra sin fuente")
            continue

        n = html.count(ancla)
        if n != 1:
            fallos.append(f"{pid}: el ancla aparece {n} veces (debe ser 1)")
            print(f"  ✗ {pid} ancla ambigua ({n} coincidencias): {ancla[:50]!r}")
            continue

        i = html.index(ancla)
        nuevo = html[:i] + bloque + html[i:]

        # --- invariante: el contenido previo sobrevive intacto alrededor del bloque
        if not (nuevo.startswith(html[:i]) and nuevo.endswith(html[i:])):
            fallos.append(f"{pid}: el contenido previo no sobrevivió")
            continue
        if nuevo.replace(bloque, "", 1) != html:
            fallos.append(f"{pid}: la inserción alteró el HTML original")
            print(f"  ✗ {pid} la inserción alteró el original")
            continue

        antes, despues = palabras(html), palabras(nuevo)
        print(f"  {pid}  {post['title'][:44]:<44} {antes} -> {despues} palabras (+{despues-antes})")
        for m in re.finditer(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', bloque):
            print(f"        + {m.group(2)[:38]!r} -> {m.group(1)}")

        item = {"id": pid, "title": post["title"], "link": post["link"],
                "palabras_antes": antes, "palabras_despues": despues}

        if APPLY:
            (BACKUPS / f"blog-{pid}-antes-tier3-{HOY}.json").write_text(
                json.dumps({"id": pid, "title": post["title"], "content": html},
                           ensure_ascii=False, indent=1), encoding="utf-8")
            r = requests.post(f"{SITE}/wp-json/wp/v2/posts/{pid}",
                              headers=jwt(), json={"content": nuevo}, timeout=60)
            ok = r.status_code == 200 and "id" in r.json()
            print(f"        WP -> HTTP {r.status_code} {'OK' if ok else r.text[:160]}")
            item["http"] = r.status_code
        reporte.append(item)

    (SALIDA / "reporte-tier3-tier4.json").write_text(
        json.dumps({"fecha": HOY, "aplicado": APPLY, "posts": reporte,
                    "fallos": fallos}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nposts con pasaje: {len(reporte)}   fallos: {len(fallos)}")
    for f in fallos:
        print(f"  ! {f}")
    if not APPLY:
        print("\n(dry-run: no se escribió nada. Usa --apply para publicar)")


if __name__ == "__main__":
    main()
