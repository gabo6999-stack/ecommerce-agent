#!/usr/bin/env python3
"""FASE 4b -- enlazado interno de la landing NAD+ (estaba huerfana): 3 posts
de longevidad/biohacking (insercion de texto plano, wp/v2/posts) + la landing
/longevidad/ (Elementor, _elementor_data + limpieza de _elementor_element_cache,
mismo mecanismo del playbook). Ancla variada, sin "clic aqui".

    py -3 scripts/fase4b_enlaza_landing_nad.py            # dry-run + diffs
    py -3 scripts/fase4b_enlaza_landing_nad.py --apply
"""
from __future__ import annotations

import difflib
import json
import pathlib
import sys
import time

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")
LANDING = f"{SITE}/nad-que-es-y-para-que-sirve/"
BACKUPS = REPO / "backups"
DIFFS = REPO / "docs" / "data" / "fase4c-diffs"

# --- posts: (id, ancla exacta a buscar, texto a insertar justo despues) ---
POSTS = [
    (1675,
     "para la correcta reconstitución de tus péptidos.",
     ' Si te interesa profundizar en la evidencia real detrás del NAD+ '
     '—incluyendo lo que todavía no está probado sobre su forma inyectable—, '
     f'esta guía explica <a href="{LANDING}">qué es el NAD+ y para qué '
     'sirve</a>.'),
    (2096,
     "es una coenzima fundamental en el metabolismo energético celular y la regulación epigenética.",
     f' <a href="{LANDING}">Esta guía revisa en detalle qué dice la '
     'evidencia clínica sobre el NAD+</a>, incluyendo la diferencia entre '
     'precursores orales y la vía parenteral.'),
    (1913,
     "un cofactor clave en los procesos de reparación del ADN y energía celular relacionados con el antienvejecimiento.",
     ' Puede leerse un repaso completo de la evidencia sobre '
     f'<a href="{LANDING}">qué es el NAD+ y cómo funciona</a> antes de '
     'considerar su uso en investigación.'),
]

PAGE_LONGEVIDAD = 26
WIDGET_ID = "96c40f4"
ANCLA_PAGINA = ("los péptidos necesarios para alcanzar una longevidad activa y "
                "saludable, transformando tu biología desde el interior.")
INSERCION_PAGINA = (' Una pieza central de esa energía celular es el NAD+: puede '
                    f'leerse <a href="{LANDING}">qué es el NAD+ y qué dice hoy la '
                    'evidencia real</a> antes de decidir cómo abordarlo.')


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


def buscar_widget(nodos, wid):
    for n in nodos:
        if n.get("id") == wid:
            return n
        r = buscar_widget(n.get("elements") or [], wid)
        if r:
            return r
    return None


def main():
    DIFFS.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(exist_ok=True)
    h = jwt()

    print("=== POSTS (3) ===")
    for pid, ancla, insercion in POSTS:
        r = requests.get(f"{SITE}/wp-json/wp/v2/posts/{pid}", headers=h,
                         params={"context": "edit"}, timeout=20)
        p = r.json()
        raw = p.get("content", {}).get("raw", "")
        if ancla not in raw:
            print(f"  {pid}: ⚠ ancla no encontrada, se omite")
            continue
        if LANDING in raw:
            print(f"  {pid}: ya enlaza a la landing, se omite")
            continue
        nuevo = raw.replace(ancla, ancla + insercion, 1)
        d = "\n".join(difflib.unified_diff(raw.splitlines(), nuevo.splitlines(),
                                           fromfile=f"{pid}-antes", tofile=f"{pid}-despues", lineterm="", n=1))
        (DIFFS / f"post-{pid}-nad-link.diff").write_text(d, encoding="utf-8")
        print(f"  {pid}: inserción lista ({len(insercion)} caracteres)")
        if APPLY:
            (BACKUPS / f"post-{pid}-antes-fase4b-enlaces-{HOY}.json").write_text(
                json.dumps({"id": pid, "content": raw}, ensure_ascii=False, indent=1), encoding="utf-8")
            rp = requests.post(f"{SITE}/wp-json/wp/v2/posts/{pid}", headers=h,
                               timeout=30, json={"content": nuevo})
            print(f"      -> HTTP {rp.status_code}")

    print("\n=== PÁGINA /longevidad/ (Elementor) ===")
    r = requests.get(f"{SITE}/wp-json/wp/v2/pages/{PAGE_LONGEVIDAD}", headers=h,
                     params={"context": "edit"}, timeout=20)
    p = r.json()
    meta = p.get("meta", {})
    ed = json.loads(meta.get("_elementor_data", "[]"))
    node = buscar_widget(ed, WIDGET_ID)
    if not node:
        print("  ⚠ widget no encontrado, se omite")
    else:
        html = node["settings"]["html"]
        if ANCLA_PAGINA not in html:
            print("  ⚠ ancla no encontrada en el widget, se omite")
        elif LANDING in html:
            print("  ya enlaza a la landing, se omite")
        else:
            nuevo_html = html.replace(ANCLA_PAGINA, ANCLA_PAGINA + INSERCION_PAGINA, 1)
            d = "\n".join(difflib.unified_diff(html.splitlines(), nuevo_html.splitlines(),
                                               fromfile="longevidad-antes", tofile="longevidad-despues", lineterm="", n=1))
            (DIFFS / "pagina-longevidad-nad-link.diff").write_text(d, encoding="utf-8")
            print(f"  inserción lista ({len(INSERCION_PAGINA)} caracteres)")
            if APPLY:
                (BACKUPS / f"pagina-26-antes-fase4b-enlaces-{HOY}.json").write_text(
                    json.dumps({"id": PAGE_LONGEVIDAD, "elementor_data": meta.get("_elementor_data", "")},
                              ensure_ascii=False, indent=1), encoding="utf-8")
                node["settings"]["html"] = nuevo_html
                rp = requests.post(f"{SITE}/wp-json/wp/v2/pages/{PAGE_LONGEVIDAD}", headers=h, timeout=30, json={
                    "meta": {
                        "_elementor_data": json.dumps(ed, ensure_ascii=False),
                        "_elementor_element_cache": "",
                    },
                })
                print(f"      -> HTTP {rp.status_code} {rp.text[:200] if rp.status_code!=200 else ''}")

    if not APPLY:
        print("\n(dry-run: nada aplicado. Usa --apply)")
        return

    print("\nverificación en vivo...")
    time.sleep(3)
    urls = [p[0] for p in POSTS]
    for pid in urls:
        r2 = requests.get(f"{SITE}/wp-json/wp/v2/posts/{pid}", headers=h,
                          params={"_fields": "link"}, timeout=20)
        link = r2.json().get("link", "")
        rlive = requests.get(f"{link}?nc={int(time.time())}", headers=UA, timeout=40)
        ok = "nad-que-es-y-para-que-sirve" in rlive.text
        print(f"  post {pid}: HTTP {rlive.status_code}  enlace presente: {'OK' if ok else 'FALTA'}")
    rlive2 = requests.get(f"{SITE}/longevidad/?nc={int(time.time())}", headers=UA, timeout=40)
    ok2 = "nad-que-es-y-para-que-sirve" in rlive2.text
    print(f"  /longevidad/: HTTP {rlive2.status_code}  enlace presente: {'OK' if ok2 else 'FALTA'}")


if __name__ == "__main__":
    main()
