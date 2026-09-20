#!/usr/bin/env python3
"""FASE 4b -- publica la landing NAD+ como pagina de WordPress EN BORRADOR
para revision del usuario. No la pasa a "publish". Meta SEO via el endpoint
propio de Rank Math (el campo `meta` del REST core no persiste rank_math_*).

    py -3 scripts/fase4b_publica_landing_nad.py            # dry-run
    py -3 scripts/fase4b_publica_landing_nad.py --apply
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import requests

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://peptidosysuplementos.mx"
APPLY = "--apply" in sys.argv
HOY = time.strftime("%Y-%m-%d")

TITULO = "NAD+: qué es y para qué sirve"
SLUG = "nad-que-es-y-para-que-sirve"
RANK_MATH_TITLE = "NAD+: qué es y para qué sirve | evidencia real"
RANK_MATH_DESC = ("Qué es el NAD+, cómo funciona y qué dice realmente la revisión "
                  "PRISMA de 2026 sobre NAD+ inyectable: ensayos, evidencia y lo "
                  "que aún falta por demostrar.")
FOCUS_KW = "nad para que sirve"
CONTENT_FILE = REPO / "docs" / "contenido" / "landing-nad-que-es-para-que-sirve.html"


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


def main():
    html = CONTENT_FILE.read_text(encoding="utf-8")
    print(f"contenido: {len(html)} caracteres, título {TITULO!r}, slug {SLUG!r}")
    print(f"rank_math_title: {RANK_MATH_TITLE!r} ({len(RANK_MATH_TITLE)} car.)")
    print(f"rank_math_description: {RANK_MATH_DESC!r} ({len(RANK_MATH_DESC)} car.)")

    if not APPLY:
        print("\n(dry-run: no se crea nada. Usa --apply)")
        return

    h = jwt()

    r = requests.post(f"{SITE}/wp-json/wp/v2/pages", headers=h, timeout=30, json={
        "title": TITULO, "slug": SLUG, "status": "draft", "content": html,
    })
    page = r.json()
    if "id" not in page:
        sys.exit(f"creación de página falló: {r.status_code} {r.text[:300]}")
    pid = page["id"]
    print(f"\npágina creada: id={pid}, status={page.get('status')}, link={page.get('link')}")

    r2 = requests.post(f"{SITE}/wp-json/rankmath/v1/updateMeta", headers=h, timeout=20, json={
        "objectID": pid, "objectType": "post",
        "meta": {"rank_math_title": RANK_MATH_TITLE,
                "rank_math_description": RANK_MATH_DESC,
                "rank_math_focus_keyword": FOCUS_KW},
    })
    print(f"rank_math meta: HTTP {r2.status_code} {r2.text[:200]}")

    # verificación: releer la página con JWT (context=edit) y confirmar borrador
    time.sleep(2)
    r3 = requests.get(f"{SITE}/wp-json/wp/v2/pages/{pid}", headers=h,
                      params={"context": "edit"}, timeout=20)
    chk = r3.json()
    print(f"\nverificación: status={chk.get('status')} (debe ser 'draft')")

    (REPO / "docs" / "data" / f"fase4b-landing-nad-publicada-{HOY}.json").write_text(
        json.dumps({"fecha": HOY, "id": pid, "slug": SLUG, "status": chk.get("status"),
                   "link": page.get("link"), "rank_math_title": RANK_MATH_TITLE,
                   "rank_math_description": RANK_MATH_DESC, "focus_keyword": FOCUS_KW},
                  ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nreporte -> docs/data/fase4b-landing-nad-publicada-{HOY}.json")


if __name__ == "__main__":
    main()
