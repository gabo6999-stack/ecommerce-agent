#!/usr/bin/env python3
"""Pasada retroactiva de enlaces internos del blog de PYS — Tiers 1 y 2.

DETERMINISTA: no interviene ningún LLM. Solo dos operaciones, ambas
verificables por diff:

  Tier 1 — remapear los <a href> que apuntan a URLs muertas (404) hacia el
           equivalente vivo. Si el destino es el propio post, o si el remapeo
           duplicaría un enlace ya presente, se DESENLAZA (se quita el <a> y se
           conserva el texto).
  Tier 2 — envolver la primera mención libre de un compuesto en un enlace a su
           ficha. "Libre" = fuera de <a>, de <h1..h6> y de <script>/<style>,
           dentro de <p>/<li>/<td>, y fuera del extracto inicial.

Invariante que se verifica siempre: **el texto visible no cambia**. Ninguna de
las dos operaciones altera una sola palabra de lo que lee el usuario; solo el
marcado. Si el conteo o el texto visible cambia, el post se descarta.

    py -3 scripts/retro_interlinks_blog.py            # dry-run + diffs
    py -3 scripts/retro_interlinks_blog.py --apply    # escribe en WordPress
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
UA = {"User-Agent": "Mozilla/5.0 (compatible; audit/1.0)"}
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")

SALIDA = REPO / "docs" / "data" / "blog-interlinks"
DIFFS = SALIDA / "diffs"
BACKUPS = REPO / "backups"

# ─── Tier 1: URL muerta -> destino vivo ──────────────────────────────────────
# post_id del destino cuando es un post (para detectar autoenlace).
MUERTAS = {
    f"{SITE}/composicion-corporal-guia-completa-transformacion/": (
        2075, f"{SITE}/perdida-de-grasa-peptidos-suplementos-guia-cientifica/"),
    f"{SITE}/masa-muscular-guia-completa-peptidos-suplementos/": (
        1926, f"{SITE}/optimizar-rendimiento-deportivo-suplementos-peptidos/"),
    f"{SITE}/guia-completa-suplementos-deportivos-evidencia-cientifica/": (
        1926, f"{SITE}/optimizar-rendimiento-deportivo-suplementos-peptidos/"),
    f"{SITE}/ghk-cu-peptido-de-cobre-beneficios/": (
        1913, f"{SITE}/ghk-cu-peptido-cobre-regeneracion-antienvejecimiento/"),
    # el compuesto SÍ tiene ficha: 5 enlaces muertos se vuelven blog -> ficha
    f"{SITE}/mots-c-peptido-mitocondrial-rendimiento-deportivo/": (
        None, f"{SITE}/product/mots-c-10mg/"),
}

# ─── Tier 2: (post, ficha) -> alias por orden de preferencia como ancla ──────
# Alias del PRODUCTO, no del compuesto genérico: `IGF-1 LR3` sí, `IGF-1` no
# (en el texto `IGF-1` casi siempre es la hormona endógena, no el producto).
TIER2 = [
    (2075, 2232, "product/cjc-1295-ipamorelina-5mg", ["CJC-1295 + Ipamorelin"]),
    (2096, 2232, "product/cjc-1295-ipamorelina-5mg", ["Ipamorelin + CJC-1295"]),
    (2201, 2232, "product/cjc-1295-ipamorelina-5mg", ["Ipamorelin/CJC-1295"]),
    (2201, 2231, "product/sermorelina-10mg", ["Sermorelin"]),
    (2094, 2232, "product/cjc-1295-ipamorelina-5mg", ["CJC-1295 / Ipamorelin"]),
    (2092, 2240, "product/cagrilintida-10mg", ["Cagrilintide"]),
    (1675, 2232, "product/cjc-1295-ipamorelina-5mg", ["CJC-1295"]),
    (1647, 799, "product/agua-bacteriostatica-3ml", ["agua bacteriostática"]),
]
EXCERPT_CHARS = 400          # el arranque suele ser el extracto: mal sitio para el ancla

BLOQUE = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style"}
CUERPO = {"p", "li", "td", "th"}
TAG = re.compile(r"(<[^>]+>)")
VACIOS = {"br", "img", "hr", "meta", "input", "source"}


# ─── utilidades ──────────────────────────────────────────────────────────────
def visible(html: str) -> str:
    """Texto que lee el usuario, sin scripts ni marcado."""
    sin = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"(?s)<[^>]+>", " ", sin))).strip()


def huella(html: str) -> str:
    """Texto visible SIN espacios, para comparar antes/después.

    Quitar o añadir un <a> cambia el espaciado del texto extraído (cada etiqueta
    se sustituye por un espacio), así que comparar `visible()` daría un falso
    positivo en cada operación. Sin espacios, la huella solo cambia si de verdad
    se ganó o se perdió un carácter de contenido.
    """
    return re.sub(r"\s+", "", visible(html))


def nodos_texto(html: str):
    """(offset, texto, stack_de_tags) por cada nodo de texto."""
    stack, pos = [], 0
    for t in TAG.split(html):
        if not t:
            continue
        if t.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", t)
            name = m.group(1).lower() if m else ""
            if not (t.endswith("/>") or name in VACIOS):
                if t.startswith("</"):
                    for i in range(len(stack) - 1, -1, -1):
                        if stack[i] == name:
                            del stack[i:]
                            break
                else:
                    stack.append(name)
        else:
            yield pos, t, list(stack)
        pos += len(t)


def primera_mencion(html: str, alias: list[str]):
    """(offset, largo, texto) de la primera mención enlazable, o None."""
    cands = []
    for pos, txt, stack in nodos_texto(html):
        s = set(stack)
        if BLOQUE & s or not (CUERPO & s):
            continue
        for rank, a in enumerate(alias):
            for m in re.finditer(re.escape(a), txt, re.I):
                ini, fin = m.start(), m.end()
                if ini > 0 and txt[ini - 1].isalnum():
                    continue
                if fin < len(txt) and txt[fin].isalnum():
                    continue
                off = pos + ini
                cands.append((rank, 0 if off > EXCERPT_CHARS else 1, off,
                              fin - ini, txt[ini:fin]))
    if not cands:
        return None
    cands.sort()
    _, _, off, largo, texto = cands[0]
    return off, largo, texto


def remapea(html: str, muerta: str, viva: str, n_max: int = 999):
    """Cambia el href de hasta n_max enlaces a `muerta`. Devuelve (html, n)."""
    pat = re.compile(r'(<a\b[^>]*?href=")' + re.escape(muerta) + r'("[^>]*>)', re.I)
    hechos = 0

    def rep(m):
        nonlocal hechos
        if hechos >= n_max:
            return m.group(0)
        hechos += 1
        return m.group(1) + viva + m.group(2)

    return pat.sub(rep, html), hechos


def desenlaza(html: str, url: str):
    """Quita el <a> conservando el texto interno. Devuelve (html, n)."""
    pat = re.compile(r'<a\b[^>]*?href="' + re.escape(url) + r'"[^>]*>(.*?)</a>',
                     re.I | re.S)
    n = len(pat.findall(html))
    return pat.sub(lambda m: m.group(1), html), n


# ─── carga de datos ──────────────────────────────────────────────────────────
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


def posts_publicados():
    out, page = {}, 1
    while True:
        r = requests.get(f"{SITE}/wp-json/wp/v2/posts",
                         params={"per_page": 100, "page": page, "status": "publish",
                                 "_fields": "id,title,link,content"},
                         headers=UA, timeout=60)
        r.raise_for_status()
        lote = r.json()
        if not lote:
            break
        for p in lote:
            out[p["id"]] = {
                "title": H.unescape(re.sub("<[^>]+>", "", p["title"]["rendered"])),
                "link": p["link"], "content": p["content"]["rendered"]}
        if len(lote) < 100:
            break
        page += 1
    return out


# ─── plan por post ───────────────────────────────────────────────────────────
def construye(posts):
    plan = {}
    for pid, post in posts.items():
        html = post["content"]
        nuevo = html
        acciones = []

        # --- Tier 1
        for muerta, (destino_id, viva) in MUERTAS.items():
            if muerta not in nuevo:
                continue
            n_total = len(re.findall(
                r'<a\b[^>]*?href="' + re.escape(muerta) + r'"', nuevo, re.I))
            autoenlace = destino_id == pid
            # ya existe un enlace vivo a ese destino? entonces el remapeo duplica
            ya = viva in nuevo
            if autoenlace or ya:
                nuevo, n = desenlaza(nuevo, muerta)
                acciones.append({
                    "tier": 1, "op": "desenlaza", "n": n, "de": muerta,
                    "motivo": "autoenlace" if autoenlace else "duplicaría un enlace existente"})
                continue
            # remapea la primera, desenlaza las repeticiones
            nuevo, n = remapea(nuevo, muerta, viva, n_max=1)
            acciones.append({"tier": 1, "op": "remapea", "n": n,
                             "de": muerta, "a": viva})
            if n_total > 1:
                nuevo, n2 = desenlaza(nuevo, muerta)
                acciones.append({"tier": 1, "op": "desenlaza", "n": n2, "de": muerta,
                                 "motivo": "repetición del mismo enlace en el post"})

        # --- Tier 2
        for post_id, ficha, ruta, alias in TIER2:
            if post_id != pid:
                continue
            url = f"{SITE}/{ruta}/"
            if f"/{ruta}/" in nuevo:
                acciones.append({"tier": 2, "op": "omitido", "ficha": ficha,
                                 "motivo": "ya enlazado"})
                continue
            hit = primera_mencion(nuevo, alias)
            if not hit:
                acciones.append({"tier": 2, "op": "omitido", "ficha": ficha,
                                 "motivo": "sin mención libre"})
                continue
            off, largo, texto = hit
            nuevo = (nuevo[:off] + f'<a href="{url}">' + texto + "</a>"
                     + nuevo[off + largo:])
            acciones.append({"tier": 2, "op": "envuelve", "ficha": ficha,
                             "ancla": texto, "a": url})

        if nuevo != html:
            plan[pid] = {"antes": html, "despues": nuevo, "acciones": acciones,
                         "title": post["title"], "link": post["link"]}
    return plan


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    DIFFS.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)

    posts = posts_publicados()
    print(f"posts publicados: {len(posts)}")
    plan = construye(posts)

    reporte = {"fecha": HOY, "aplicado": APPLY, "posts": []}
    abortados = []

    for pid, p in sorted(plan.items()):
        # INVARIANTE: el texto visible no puede cambiar
        v1, v2 = huella(p["antes"]), huella(p["despues"])
        if v1 != v2:
            abortados.append(pid)
            print(f"  ✗ {pid} ABORTADO: el texto visible cambió")
            continue

        d = "\n".join(difflib.unified_diff(
            p["antes"].splitlines(), p["despues"].splitlines(),
            fromfile=f"{pid}-antes", tofile=f"{pid}-despues", lineterm="", n=1))
        (DIFFS / f"{pid}.diff").write_text(d, encoding="utf-8")

        remaps = sum(a.get("n", 0) for a in p["acciones"]
                     if a["op"] == "remapea")
        desen = sum(a.get("n", 0) for a in p["acciones"] if a["op"] == "desenlaza")
        nuevos = sum(1 for a in p["acciones"] if a["op"] == "envuelve")
        print(f"  {pid}  {p['title'][:46]:<46} remap:{remaps} desenlaza:{desen} nuevo:{nuevos}")
        for a in p["acciones"]:
            if a["op"] == "envuelve":
                print(f"        + <a> {a['ancla']!r} -> {a['a'].split('.mx/')[1]}")
            elif a["op"] == "remapea":
                print(f"        ~ {a['de'].split('.mx/')[1]}  ->  {a['a'].split('.mx/')[1]}")
            elif a["op"] == "desenlaza":
                print(f"        - {a['de'].split('.mx/')[1]}  ({a['motivo']})")
            elif a["op"] == "omitido":
                print(f"        · ficha {a['ficha']} omitida: {a['motivo']}")

        reporte["posts"].append({
            "id": pid, "title": p["title"], "link": p["link"],
            "acciones": p["acciones"], "diff": f"diffs/{pid}.diff"})

        if APPLY:
            (BACKUPS / f"blog-{pid}-antes-{HOY}.json").write_text(
                json.dumps({"id": pid, "title": p["title"], "link": p["link"],
                            "content": p["antes"]}, ensure_ascii=False, indent=1),
                encoding="utf-8")
            r = requests.post(f"{SITE}/wp-json/wp/v2/posts/{pid}",
                              headers=jwt(), json={"content": p["despues"]}, timeout=60)
            ok = r.status_code == 200 and "id" in r.json()
            print(f"        WP -> HTTP {r.status_code} {'OK' if ok else r.text[:160]}")
            reporte["posts"][-1]["http"] = r.status_code

    reporte["abortados"] = abortados
    (SALIDA / "reporte-tier1-tier2.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nposts con cambios: {len(reporte['posts'])}  abortados: {len(abortados)}")
    print(f"diffs -> {DIFFS}")
    if not APPLY:
        print("\n(dry-run: no se escribió nada. Usa --apply para publicar)")


if __name__ == "__main__":
    main()
